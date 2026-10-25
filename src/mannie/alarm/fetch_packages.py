"""Fetch Arch Linux ARM packages for Luna's offline first boot (plan_mannie.md Step 7).

Resolves the dependency closure of the wanted packages against the sync databases,
leaves out what the base root already holds, then downloads each package with its
signature and checks both: the SHA-256 recorded in the database, and a good GPG
signature from the Arch Linux ARM Build System key. Standard library and `gpg` only.

  python3 fetch_packages.py --root <extracted root> --out <cache dir> [--gnupg <dir>] pkg…

Without --gnupg, a temporary keyring is made from archlinuxarm-builder.asc (beside
this file) and its fingerprint is checked.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

MIRROR = "http://mirror.archlinuxarm.org/aarch64"
REPOS = ["core", "extra", "alarm", "aur"]
FINGERPRINT = "68B3537F39A313B3E574D06777193F152BDBE6A6"
KEY_FILE = Path(__file__).with_name("archlinuxarm-builder.asc")


def keyring(home: Path) -> Path:
    subprocess.run(["gpg", "--homedir", str(home), "--batch", "--import", str(KEY_FILE)], capture_output=True, check=True)
    listing = subprocess.run(["gpg", "--homedir", str(home), "--batch", "--with-colons", "--fingerprint"], capture_output=True, text=True, check=True)
    if f"fpr:::::::::{FINGERPRINT}:" not in listing.stdout:
        raise SystemExit("archlinuxarm-builder.asc is not the published Arch Linux ARM Build System key")
    return home


def _fields(text: str) -> dict[str, list[str]]:
    fields, key = {}, None
    for line in text.splitlines():
        if line.startswith("%") and line.endswith("%"):
            key = line.strip("%")
            fields[key] = []
        elif line and key:
            fields[key].append(line)
    return fields


def load_sync(cache: Path) -> dict[str, dict]:
    packages: dict[str, dict] = {}
    for repo in REPOS:
        db = cache / f"{repo}.db"
        if not db.exists():
            with urllib.request.urlopen(f"{MIRROR}/{repo}/{repo}.db", timeout=120) as response:
                db.write_bytes(response.read())
        with tarfile.open(db) as archive:
            texts: dict[str, str] = {}
            for member in archive.getmembers():
                if member.isfile():
                    texts.setdefault(member.name.split("/")[0], "")
                    texts[member.name.split("/")[0]] += archive.extractfile(member).read().decode() + "\n"
        for text in texts.values():
            fields = _fields(text)
            if "NAME" not in fields:  # Arch Linux ARM's extra.db has a few broken entries
                continue
            name = fields["NAME"][0]
            packages.setdefault(name, {"repo": repo, **fields})
    return packages


def load_local(root: Path) -> dict[str, dict]:
    local = {}
    for desc in (root / "var/lib/pacman/local").glob("*/desc"):
        fields = _fields(desc.read_text())
        local[fields["NAME"][0]] = fields
    return local


def _bare(dep: str) -> str:
    return re.split(r"[<>=:]", dep, maxsplit=1)[0].strip()


def provider_index(packages: dict[str, dict]) -> dict[str, str]:
    index = {}
    for name, fields in packages.items():
        for provided in fields.get("PROVIDES", []):
            index.setdefault(_bare(provided), name)
    return index


def resolve(wanted: list[str], sync: dict[str, dict], local: dict[str, dict]) -> list[str]:
    providers, local_provides = provider_index(sync), set(local)
    for fields in local.values():
        local_provides.update(_bare(p) for p in fields.get("PROVIDES", []))
    chosen, todo = [], list(wanted)
    while todo:
        dep = _bare(todo.pop(0))
        if dep in local_provides or dep in chosen:
            continue
        name = dep if dep in sync else providers.get(dep)
        if name is None:
            raise SystemExit(f"no package provides {dep}")
        if name in chosen or name in local:
            continue
        chosen.append(name)
        todo.extend(sync[name].get("DEPENDS", []))
    return chosen


def fetch(names: list[str], sync: dict[str, dict], out: Path, gnupg: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name in names:
        fields = sync[name]
        filename = fields["FILENAME"][0]
        for suffix in ("", ".sig"):
            target = out / (filename + suffix)
            if not target.exists():
                url = f"{MIRROR}/{fields['repo']}/{filename}{suffix}"
                with urllib.request.urlopen(url, timeout=300) as response:
                    target.write_bytes(response.read())
        digest = hashlib.sha256((out / filename).read_bytes()).hexdigest()
        if digest != fields["SHA256SUM"][0]:
            raise SystemExit(f"{filename}: SHA-256 differs from the database")
        verify = subprocess.run(
            ["gpg", "--homedir", str(gnupg), "--batch", "--status-fd", "1", "--verify", str(out / (filename + ".sig")), str(out / filename)],
            capture_output=True, text=True,
        )
        if f"VALIDSIG {FINGERPRINT}" not in verify.stdout:
            raise SystemExit(f"{filename}: no good signature from {FINGERPRINT}")
        print(f"ok {filename}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--gnupg", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("packages", nargs="+")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sync = load_sync(args.out)
    names = resolve(args.packages, sync, load_local(args.root))
    total = sum(int(sync[n]["CSIZE"][0]) for n in names)
    print(f"{len(names)} packages, {total / 1e6:.1f} MB: {' '.join(names)}")
    if not args.dry_run:
        with tempfile.TemporaryDirectory() as home:
            fetch(names, sync, args.out, args.gnupg or keyring(Path(home)))
        # One file name per line, in dependency order; luna-firstboot installs exactly these.
        (args.out / "luna-firstboot-packages.txt").write_text("".join(sync[n]["FILENAME"][0] + "\n" for n in names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
