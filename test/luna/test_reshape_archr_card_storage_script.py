"""Safety and geometry checks for the user-run Luna Step 6 storage reshape script."""

from pathlib import Path
import json
import re
import shutil
import subprocess

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "worklines/luna/scripts/reshape_archr_card_storage.sh"
SFDISK = shutil.which("sfdisk") or "/usr/sbin/sfdisk"
MIB = 2048  # sectors


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def constant(name: str) -> int:
    match = re.search(rf"\b{name}=(\d+)", script_text())
    assert match, name
    return int(match.group(1))


def old_geometry(n: int) -> tuple[int, int]:
    match = re.search(rf"readonly OLD_P{n}='(\d+) (\d+)'", script_text())
    assert match
    return int(match.group(1)), int(match.group(2))


def test_reshape_script_parses() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_reshape_script_has_identity_and_confirmation_gates() -> None:
    script = script_text()
    assert "readonly EXPECTED_BYTES=62534975488" in script
    assert "3cf95927-e0f1-4043-ad1d-fe04cae2f642" in script
    assert "a2bafe90-b2fb-47d9-91d8-f78c3090d63d" in script
    assert "2900-7A2B" in script
    assert "not removable" in script
    assert "refusing to touch the system disk" in script
    assert "a fourth partition already exists" in script
    assert "RESHAPE-LUNA-CARD" in script
    assert "UDISKS_IGNORE" in script


def test_checkpoint_and_backup_are_verified_before_any_write() -> None:
    script = script_text()
    checkpoint = script.index('dd if="$disk"')
    mismatch = script.index("checkpoint MISMATCH")
    backup_compare = script.index('-df "$storage_tar" -C "$work/old"')
    repartition = script.index("sfdisk --wipe never")
    first_mkfs = script.index("mkfs.ext4")
    first_resize = script.index('resize2fs "$p2"')
    assert checkpoint < mismatch < backup_compare < repartition < first_resize < first_mkfs


def test_existing_filesystems_are_never_wiped_by_sfdisk() -> None:
    script = script_text()
    assert "--wipe never --wipe-partitions never" in script
    assert 'label-id: $label_id' in script
    assert "boot partition changed" in script


def test_new_filesystems_match_archr_features_and_keep_storage_uuid() -> None:
    script = script_text()
    assert "readonly MKFS_EXT4_FEATURES='^orphan_file'" in script
    assert '-L LUNA_HOME "$p3"' in script
    assert '-m 0 -L STORAGE -U "$STORAGE_UUID" "$p4"' in script
    assert "restored STORAGE differs from the backup" in script


def test_card_is_only_written_by_sfdisk_resize2fs_and_mkfs() -> None:
    script = script_text()
    assert not re.search(r"\bdd\b[^\n]*\bof=\"?\$disk", script.split("Rollback:")[0])
    assert "rm -rf" not in script
    assert "wipefs" not in script


def test_home_mount_unit_lives_on_storage() -> None:
    script = script_text()
    assert 'unitdir="$work/storage/.config/system.d"' in script
    assert "What=/dev/disk/by-label/LUNA_HOME" in script
    assert "Where=/home" in script
    assert 'ln -s ../home.mount "$unitdir/multi-user.target.wants/home.mount"' in script


def test_home_mount_stays_out_of_local_fs_target() -> None:
    """On ArchR, udevd starts after local-fs.target; a device mount there deadlocks for 90 s."""
    script = script_text()
    unit = script[script.index('cat > "$unitdir/home.mount"'):script.index("ln -s ../home.mount")]
    assert "DefaultDependencies=no" in unit
    assert "After=local-fs.target systemd-udevd.service" in unit
    assert "WantedBy=multi-user.target" in unit
    assert "local-fs.target.wants" not in script


def test_target_geometry_is_contiguous_aligned_and_keeps_boot_and_root_starts() -> None:
    p = {n: (constant(f"P{n}_START"), constant(f"P{n}_SIZE")) for n in range(1, 5)}
    total = constant("EXPECTED_SECTORS")
    assert p[1] == old_geometry(1)
    assert p[2][0] == old_geometry(2)[0]
    assert p[2][0] + p[2][1] == p[3][0]
    assert p[3][0] + p[3][1] == p[4][0]
    assert p[4][0] + p[4][1] == total
    assert all(start % MIB == 0 and size % MIB == 0 for start, size in p.values())
    assert p[2][1] * 512 >= 20 * 10**9
    assert total * 512 == constant("EXPECTED_BYTES")


def test_sfdisk_applies_the_target_table_without_moving_p1_or_p2(tmp_path: Path) -> None:
    if not Path(SFDISK).exists():
        pytest.skip("sfdisk not available")
    image = tmp_path / "card.img"
    with image.open("wb") as handle:
        handle.truncate(constant("EXPECTED_BYTES"))

    old = "\n".join([
        "label: dos", "label-id: 0xfc3e6ee5", "unit: sectors", "",
        f"{image}1 : start={old_geometry(1)[0]}, size={old_geometry(1)[1]}, type=c, bootable",
        f"{image}2 : start={old_geometry(2)[0]}, size={old_geometry(2)[1]}, type=da",
        f"{image}3 : start={old_geometry(3)[0]}, size={old_geometry(3)[1]}, type=83",
    ]) + "\n"
    subprocess.run([SFDISK, "-q", str(image)], input=old, text=True, check=True)

    heredoc = re.search(r"sfdisk --wipe never.*?<<EOF\n(.*?)\nEOF", script_text(), re.S)
    assert heredoc
    table = heredoc.group(1).replace("$label_id", "0xfc3e6ee5").replace("${disk}", str(image))
    for name in ("P1_START", "P1_SIZE", "P2_START", "P2_SIZE", "P3_START", "P3_SIZE", "P4_START", "P4_SIZE"):
        table = table.replace(f"${name}", str(constant(name)))
    subprocess.run([SFDISK, "-q", "--wipe", "never", "--wipe-partitions", "never", str(image)],
                   input=table + "\n", text=True, check=True)

    dumped = json.loads(subprocess.run([SFDISK, "-J", str(image)], capture_output=True, text=True,
                                       check=True).stdout)["partitiontable"]
    parts = dumped["partitions"]
    assert dumped["id"] == "0xfc3e6ee5"
    assert [(q["start"], q["size"]) for q in parts] == [
        (constant(f"P{n}_START"), constant(f"P{n}_SIZE")) for n in range(1, 5)
    ]
    assert parts[0].get("bootable") is True
    assert [q["type"] for q in parts] == ["c", "da", "83", "83"]
