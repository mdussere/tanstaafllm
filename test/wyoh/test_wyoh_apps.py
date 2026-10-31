"""Deterministic tests for Wyoh's application manifests and menu set (Steps 9.2, 9.4)."""

from __future__ import annotations

import configparser
import hashlib
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh"))
import wyoh_apps as a  # noqa: E402
import wyoh_gamepad as g  # noqa: E402

GOOD = """
id = "chess"
name = "Chess"
version = "1.0"
source = "https://example.org/chess"
licence = "GPL-3.0"
wayland_app_id = "pygame-chess"
input = "pointer"
window = "fullscreen"
gpu = false
quit = "Escape"
icon = "chess.png"
"""


def make_app(root: Path, text: str = GOOD, run: bool = True, icon: bool = True) -> Path:
    directory = root / "chess-1.0"
    directory.mkdir(parents=True)
    (directory / a.MANIFEST).write_text(text, encoding="utf-8")
    if run:
        launcher = directory / "run"
        launcher.write_text("#!/bin/sh\n", encoding="utf-8")
        launcher.chmod(0o755)
    if icon:
        (directory / "chess.png").write_bytes(b"png")
    return directory


def test_a_valid_manifest_loads(tmp_path):
    app = a.load(make_app(tmp_path))
    assert (app.id, app.input, app.window, app.gpu) == ("chess", "pointer", "fullscreen", False)
    assert app.launcher.name == "run"


@pytest.mark.parametrize("change, message", [
    (lambda t: t.replace('input = "pointer"', 'input = "joystick"'), "input must be"),
    (lambda t: t.replace('window = "fullscreen"', 'window = "maximised"'), "window must be"),
    (lambda t: t.replace("gpu = false", 'gpu = "no"'), "gpu must be"),
    (lambda t: t.replace('id = "chess"', 'id = "Chess Game"'), "id must be"),
    (lambda t: t.replace('licence = "GPL-3.0"\n', ""), "missing"),
    (lambda t: t + 'colour = "red"\n', "unknown keys"),
    (lambda t: t + "rss_kb_at_rest = -3\n", "rss_kb_at_rest"),
    (lambda t: t + '[sha256]\n"run" = "abc"\n', "sha256"),
])
def test_invalid_manifests_are_refused(tmp_path, change, message):
    with pytest.raises(a.ManifestError, match=message):
        a.load(make_app(tmp_path, change(GOOD)))


def test_launcher_and_icon_must_exist(tmp_path):
    with pytest.raises(a.ManifestError, match="launcher"):
        a.load(make_app(tmp_path / "x", run=False))
    with pytest.raises(a.ManifestError, match="icon"):
        a.load(make_app(tmp_path / "y", GOOD.replace("chess.png", "img/chess.png")))


def test_checksums_are_verified(tmp_path):
    good = hashlib.sha256(b"#!/bin/sh\n").hexdigest()
    a.load(make_app(tmp_path / "ok", GOOD + f'[sha256]\n"run" = "{good}"\n'))
    with pytest.raises(a.ManifestError, match="SHA-256"):
        a.load(make_app(tmp_path / "bad", GOOD + f'[sha256]\n"run" = "{"0" * 64}"\n'))


def test_desktop_entry_launches_the_run_script(tmp_path):
    app = a.load(make_app(tmp_path))
    entry = configparser.ConfigParser(interpolation=None)
    entry.optionxform = str
    entry.read_string(a.desktop_entry(app))
    section = entry["Desktop Entry"]
    assert section["Exec"] == str(app.directory / "run")
    assert section["Name"] == "Chess" and section["Icon"] == "chess.png" and section["Type"] == "Application"


def test_sway_rules_and_profiles(tmp_path):
    chess = a.load(make_app(tmp_path / "c"))
    calc = a.load(ROOT / "src/wyoh/apps/calculator")
    assert a.sway_rules([chess, calc]).splitlines()[1:] == [
        'for_window [app_id="wyoh-calculator"] floating enable',
        'for_window [app_id="pygame-chess"] fullscreen enable',
    ]
    assert a.app_profiles([chess, calc]) == {"pygame-chess": "pointer"}  # "keys" is the default


def test_the_calculator_manifest_in_the_repository_is_valid():
    app = a.load(ROOT / "src/wyoh/apps/calculator")
    assert app.wayland_app_id == "wyoh-calculator" and app.input == "keys"
    assert "SDL_VIDEO_WAYLAND_WMCLASS=wyoh-calculator" in (app.directory / "run").read_text(encoding="utf-8")


def test_discovery_reports_bad_apps_and_duplicate_ids(tmp_path):
    make_app(tmp_path / "opt")
    shutil.copytree(tmp_path / "opt" / "chess-1.0", tmp_path / "opt" / "chess-2.0")
    broken = tmp_path / "opt" / "broken"
    broken.mkdir()
    (broken / a.MANIFEST).write_text("id = 1\n", encoding="utf-8")
    apps, errors = a.discover([str(tmp_path / "opt" / "*" / a.MANIFEST)])
    assert [app.id for app in apps] == ["chess"]
    assert len(errors) == 2 and any("already used" in e for e in errors)


def _menu(applications: Path, system: Path) -> list[str]:
    """What fuzzel would list: Wyoh's directory first, then the system's;
    the first file with a given ID wins, and Hidden/NoDisplay entries are skipped."""
    shown, seen = [], set()
    for directory in (applications, system):
        for path in sorted(directory.glob("*.desktop")):
            if path.name in seen:
                continue
            seen.add(path.name)
            entry = configparser.ConfigParser(interpolation=None)
            entry.optionxform = str
            entry.read(path, encoding="utf-8")
            section = entry["Desktop Entry"]
            if section.get("Hidden") == "true" or section.get("NoDisplay") == "true":
                continue
            shown.append(section["Name"])
    return sorted(shown)


def test_the_generated_menu_holds_exactly_the_intended_entries(tmp_path):
    """Step 9.4: Wyoh's entries plus the apps; ArchR's listed entries hidden."""
    applications = tmp_path / "share" / "applications"
    shutil.copytree(ROOT / "src/wyoh/deploy/luna/share/applications", applications)
    # the old bc calculator entry, still on Luna from an earlier deploy (rsync does not delete)
    (applications / "wyoh-calculator.desktop").write_text(
        "[Desktop Entry]\nType=Application\nName=Calculator (bc)\nExec=foot bc\n", encoding="utf-8")
    system = tmp_path / "usr-share-applications"
    system.mkdir()
    archr = {"htop.desktop": "Htop", "nvtop.desktop": "nvtop", "cups.desktop": "Manage Printing",
             "mpv.desktop": "mpv Media Player", "gmu.desktop": "Gmu Music Player", "vlc.desktop": "VLC",
             "mupen64plus.desktop": "Mupen64Plus"}
    for desktop_id, name in archr.items():
        (system / desktop_id).write_text(f"[Desktop Entry]\nType=Application\nName={name}\nExec=x\n", encoding="utf-8")
    apps = [a.load(ROOT / "src/wyoh/apps/calculator")]
    menu = a.load_menu(ROOT / "src/wyoh/deploy/luna/menu.toml")
    report = a.generate(apps, menu, applications, tmp_path / "generated", [system])
    # Wyoh's own, not ArchR's; and the new root's duplicates (Mannie, 2026-10-30), absent from this fake system
    assert sorted(report["not_found_on_system"]) == sorted(
        ["wyoh-calculator.desktop", "foot.desktop", "footclient.desktop", "foot-server.desktop", "vim.desktop"])
    assert _menu(applications, system) == sorted(
        ["Calculator", "Image Viewer", "Mannie", "Task Manager", "Terminal", "Text Editor", "VLC", "Wi-Fi"])


def test_generated_profiles_reach_the_gamepad_config(tmp_path):
    chess = a.load(make_app(tmp_path / "c", GOOD.replace('"pointer"', '"gamepad-raw"')))
    a.generate([chess], a.MenuSet(()), tmp_path / "apps", tmp_path / "gen")
    main = tmp_path / "gamepad.toml"
    main.write_text(f'app_profiles_file = "{tmp_path / "gen" / "app-profiles.toml"}"\n', encoding="utf-8")
    assert g.load_config(main).app_profiles == {"pygame-chess": "gamepad-raw"}


def test_a_missing_profiles_file_means_no_profiles(tmp_path):
    main = tmp_path / "gamepad.toml"
    main.write_text(f'app_profiles_file = "{tmp_path / "absent.toml"}"\n', encoding="utf-8")
    assert g.load_config(main).app_profiles == {}


def test_app_keys_are_validated_and_generated(tmp_path):
    keys = '\n[keys]\nBTN_TR = "KEY_LEFTCTRL"\nBTN_EAST = "KEY_SPACE"\n'
    app = a.load(make_app(tmp_path / "k", GOOD.replace('"pointer"', '"keys"') + keys))
    assert app.keys == {"BTN_TR": "KEY_LEFTCTRL", "BTN_EAST": "KEY_SPACE"}
    a.generate([app], a.MenuSet(()), tmp_path / "apps", tmp_path / "gen")
    main = tmp_path / "gamepad.toml"
    main.write_text(f'app_profiles_file = "{tmp_path / "gen" / "app-profiles.toml"}"\n', encoding="utf-8")
    assert g.load_config(main).app_keys == {"pygame-chess": {"BTN_EAST": "KEY_SPACE", "BTN_TR": "KEY_LEFTCTRL"}}


@pytest.mark.parametrize("keys, message", [
    ('\n[keys]\nBTN_NOPE = "KEY_SPACE"\n', "unknown button"),
    ('\n[keys]\nBTN_TR = "KEY_NOPE"\n', "unknown button or key"),
])
def test_bad_app_keys_are_refused(tmp_path, keys, message):
    with pytest.raises(a.ManifestError, match=message):
        a.load(make_app(tmp_path, GOOD.replace('"pointer"', '"keys"') + keys))


def test_keys_with_gamepad_raw_are_refused(tmp_path):
    text = GOOD.replace('"pointer"', '"gamepad-raw"') + '\n[keys]\nBTN_TR = "KEY_LEFTCTRL"\n'
    with pytest.raises(a.ManifestError, match="gamepad-raw"):
        a.load(make_app(tmp_path, text))


def test_mikes_window_manifest_matches_fn_b():
    app = a.load(ROOT / "src/wyoh/apps/mike")
    assert app.wayland_app_id == "mike" and app.name == "Mike" and app.input == "keys"
    run = (ROOT / "src/wyoh/apps/mike/run").read_text(encoding="utf-8")
    assert "-a mike" in run and "runuser -l michael" in run and "mike.py" in run
    assert g.MIKE_RUN == "/storage/.local/opt/wyoh-mike/run"  # where the menu and FN+B both start it
