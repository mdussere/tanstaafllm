#!/usr/bin/env python3
"""Wyoh applications: manifests, menu entries, Sway rules, gamepad profiles (Step 9.2, 9.4).

Each application Wyoh integrates lives in its own directory, normally
`/storage/.local/opt/<app>-<version>/`, holding:

* `wyoh-app.toml`: the manifest (schema below; agreed with Professor in
  worklines/wyoh/docs/0900_01_note-from-professor-graphical-apps.md, section 6);
* `run`: an executable launcher, the only thing the menu starts;
* the icon named by the manifest, and whatever the app needs.

From the manifests and `menu.toml` (the menu set: which ArchR entries to
hide), this module generates, in Wyoh's own data directory:

* one `.desktop` entry per app (`wyoh-app-<id>.desktop`);
* `Hidden=true` overrides with the same desktop-file IDs as the hidden ArchR
  entries (Wyoh's directory comes first in `XDG_DATA_DIRS`, so ArchR's files
  stay untouched);
* `sway-apps.conf`, the Sway rules (`window`), included by `sway.conf`;
* `app-profiles.toml`, the gamepad profiles by Wayland app_id, read by the
  gamepad daemon.

Standard library only; `generate()` is pure apart from writing its outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST = "wyoh-app.toml"
INPUTS = ("keys", "pointer", "gamepad-raw", "gamepad-virtual")
WINDOWS = ("tile", "floating", "fullscreen")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REQUIRED = ("id", "name", "version", "source", "licence", "wayland_app_id", "input", "window", "gpu", "quit")


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class App:
    id: str
    name: str
    version: str
    source: str
    licence: str
    wayland_app_id: str
    input: str
    window: str
    gpu: bool
    quit: str
    directory: Path
    comment: str = ""
    icon: str = ""
    categories: tuple[str, ...] = ("Utility",)
    rss_kb_at_rest: int | None = None
    sha256: dict[str, str] = field(default_factory=dict)
    keys: dict[str, str] = field(default_factory=dict)  # gamepad button -> key chord while focused
    pad: dict[str, int] = field(default_factory=dict)  # gamepad button -> virtual joystick button (gamepad-virtual)

    @property
    def launcher(self) -> Path:
        return self.directory / "run"


def load(directory: Path, check_files: bool = True) -> App:
    """Read and validate `<directory>/wyoh-app.toml`."""
    path = directory / MANIFEST
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ManifestError(f"{path}: {error}") from error
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        raise ManifestError(f"{path}: missing {missing}")
    known = set(REQUIRED) | {"comment", "icon", "categories", "rss_kb_at_rest", "sha256", "keys", "pad"}
    unknown = set(data) - known
    if unknown:
        raise ManifestError(f"{path}: unknown keys {sorted(unknown)}")
    if not ID_RE.match(str(data["id"])):
        raise ManifestError(f"{path}: id must be lower-case letters, digits and dashes")
    if data["input"] not in INPUTS:
        raise ManifestError(f"{path}: input must be one of {INPUTS}")
    if data["window"] not in WINDOWS:
        raise ManifestError(f"{path}: window must be one of {WINDOWS}")
    if not isinstance(data["gpu"], bool):
        raise ManifestError(f"{path}: gpu must be true or false")
    for key in ("name", "version", "source", "licence", "wayland_app_id", "quit"):
        if not isinstance(data[key], str) or not data[key].strip() or "\n" in data[key]:
            raise ManifestError(f"{path}: {key} must be a one-line string")
    rss = data.get("rss_kb_at_rest")
    if rss is not None and (not isinstance(rss, int) or rss <= 0):
        raise ManifestError(f"{path}: rss_kb_at_rest must be a positive integer")
    sha256 = data.get("sha256", {})
    if not isinstance(sha256, dict) or not all(re.fullmatch(r"[0-9a-f]{64}", str(v)) for v in sha256.values()):
        raise ManifestError(f"{path}: sha256 must map file names to 64 hex digits")
    keys = data.get("keys", {})
    if not isinstance(keys, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in keys.items()):
        raise ManifestError(f"{path}: keys must map gamepad buttons to key names")
    try:
        from wyoh_gamepad import BUTTONS, KEYS
    except ImportError:  # pragma: no cover - always beside wyoh_gamepad.py
        BUTTONS, KEYS = {}, {}
    for button, chord in keys.items():
        if BUTTONS and (button not in BUTTONS or any(k not in KEYS for k in chord.split("+"))):
            raise ManifestError(f"{path}: unknown button or key in keys: {button} = {chord}")
    if keys and data["input"] == "gamepad-raw":
        raise ManifestError(f"{path}: keys make no sense with input = gamepad-raw")
    pad = data.get("pad", {})
    if pad and data["input"] != "gamepad-virtual":
        raise ManifestError(f"{path}: pad needs input = gamepad-virtual")
    if data["input"] == "gamepad-virtual" and not pad:
        raise ManifestError(f"{path}: input = gamepad-virtual needs a [pad] table")
    if not isinstance(pad, dict) or not all(isinstance(v, int) and 0 <= v < 16 for v in pad.values()) or \
            (BUTTONS and any(b not in BUTTONS for b in pad)):
        raise ManifestError(f"{path}: pad must map gamepad buttons to virtual buttons 0-15")
    app = App(
        id=data["id"], name=data["name"], version=data["version"], source=data["source"],
        licence=data["licence"], wayland_app_id=data["wayland_app_id"], input=data["input"],
        window=data["window"], gpu=data["gpu"], quit=data["quit"], directory=directory,
        comment=data.get("comment", ""), icon=data.get("icon", ""),
        categories=tuple(data.get("categories", ["Utility"])), rss_kb_at_rest=rss, sha256=dict(sha256),
        keys=dict(keys), pad=dict(pad),
    )
    if check_files:
        if not os.access(app.launcher, os.X_OK):
            raise ManifestError(f"{path}: no executable `run` launcher")
        if app.icon and "/" in app.icon and not (directory / app.icon).is_file():
            raise ManifestError(f"{path}: icon {app.icon} not found")
        for name, digest in app.sha256.items():
            target = directory / name
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ManifestError(f"{path}: {name} is missing or does not match its SHA-256")
    return app


def desktop_entry(app: App) -> str:
    icon = str(app.directory / app.icon) if "/" in app.icon else app.icon
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={app.name}",
        *([f"Comment={app.comment}"] if app.comment else []),
        *([f"Icon={icon}"] if icon else []),
        f"Exec={app.launcher}",
        f"Categories={';'.join(app.categories)};",
        f"X-Wyoh-App={app.id} {app.version}",
    ]
    return "\n".join(lines) + "\n"


def sway_rules(apps: list[App]) -> str:
    rules = ["# Generated by wyoh_apps.py from the apps' wyoh-app.toml; do not edit."]
    for app in sorted(apps, key=lambda a: a.id):
        criteria = f'[app_id="{app.wayland_app_id}"]'
        if app.window == "fullscreen":
            rules.append(f"for_window {criteria} fullscreen enable")
        elif app.window == "floating":
            rules.append(f"for_window {criteria} floating enable")
    return "\n".join(rules) + "\n"


def app_profiles(apps: list[App]) -> dict[str, str]:
    return {app.wayland_app_id: app.input for app in apps if app.input != "keys"}


def hidden_entry(desktop_id: str) -> str:
    return f"[Desktop Entry]\nType=Application\nName={desktop_id}\nHidden=true\nNoDisplay=true\n"


@dataclass(frozen=True)
class MenuSet:
    hide: tuple[str, ...]


def load_menu(path: Path) -> MenuSet:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    hide = data.get("hide", [])
    if set(data) - {"hide"} or not all(isinstance(h, str) and h.endswith(".desktop") for h in hide):
        raise ManifestError(f"{path}: expected only `hide = [\"<id>.desktop\", ...]`")
    return MenuSet(tuple(hide))


def discover(globs: list[str], check_files: bool = True) -> tuple[list[App], list[str]]:
    """Load every manifest found; return the apps and the errors (one per bad app)."""
    apps: list[App] = []
    errors: list[str] = []
    seen: dict[str, Path] = {}
    for pattern in globs:
        root = Path(pattern).anchor or "."
        for manifest in sorted(Path(root).glob(str(Path(pattern).relative_to(root)))):
            try:
                app = load(manifest.parent, check_files=check_files)
            except ManifestError as error:
                errors.append(str(error))
                continue
            if app.id in seen:
                errors.append(f"{manifest}: id {app.id} already used by {seen[app.id]}")
                continue
            seen[app.id] = manifest
            apps.append(app)
    return apps, errors


def generate(apps: list[App], menu: MenuSet, applications_dir: Path, out_dir: Path,
             system_dirs: list[Path] | None = None) -> dict[str, list[str]]:
    """Write the generated files; return a report (written, hidden, not found on the system)."""
    applications_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in applications_dir.glob("wyoh-app-*.desktop"):
        old.unlink()
    written = []
    for app in apps:
        target = applications_dir / f"wyoh-app-{app.id}.desktop"
        target.write_text(desktop_entry(app), encoding="utf-8")
        written.append(target.name)
    hidden, absent = [], []
    for desktop_id in menu.hide:
        (applications_dir / desktop_id).write_text(hidden_entry(desktop_id), encoding="utf-8")
        hidden.append(desktop_id)
        if system_dirs is not None and not any((d / desktop_id).exists() for d in system_dirs):
            absent.append(desktop_id)
    (out_dir / "sway-apps.conf").write_text(sway_rules(apps), encoding="utf-8")
    profiles = app_profiles(apps)
    body = "".join(f'"{app_id}" = "{mode}"\n' for app_id, mode in sorted(profiles.items()))
    key_tables = "".join(
        f'\n[app_keys."{app.wayland_app_id}"]\n' + "".join(f'{b} = "{k}"\n' for b, k in sorted(app.keys.items()))
        for app in sorted(apps, key=lambda a: a.id) if app.keys)
    key_tables += "".join(
        f'\n[app_pad."{app.wayland_app_id}"]\n' + "".join(f"{b} = {i}\n" for b, i in sorted(app.pad.items()))
        for app in sorted(apps, key=lambda a: a.id) if app.pad)
    (out_dir / "app-profiles.toml").write_text(
        "# Generated by wyoh_apps.py; gamepad profiles by Wayland app_id.\n[app_profiles]\n" + body + key_tables,
        encoding="utf-8")
    return {"written": written, "hidden": hidden, "not_found_on_system": absent}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apps", action="append", default=[], help="manifest glob, e.g. /storage/.local/opt/*/wyoh-app.toml")
    parser.add_argument("--menu", type=Path, required=True, help="menu.toml (entries to hide)")
    parser.add_argument("--applications-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True, help="where sway-apps.conf and app-profiles.toml go")
    parser.add_argument("--system-dir", type=Path, action="append", default=[], help="system applications dirs to check")
    args = parser.parse_args()
    apps, errors = discover(args.apps)
    report = generate(apps, load_menu(args.menu), args.applications_dir, args.out_dir, args.system_dir or None)
    report["errors"] = errors
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
