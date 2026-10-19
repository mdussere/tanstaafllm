#!/usr/bin/env python3
"""Wyoh's Wi-Fi panel on Luna (Step 7): list, join, forget networks with the buttons.

Design: worklines/wyoh/docs/0700_01_wifi-settings-proposal.md; user decisions
of 2026-10-15 (fuzzel panel on iwd, Start menu entry, password networks only).
iwd owns Wi-Fi and its addresses on Luna (7.1); Wyoh only talks to it through
`busctl` (systemd's D-Bus tool), so no Python D-Bus library is needed.

- `wyoh_wifi.py` shows the list in fuzzel: networks (connected mark, SSID,
  security, signal), then Rescan, Forget a network…, Disconnect.
- `wyoh_wifi.py --connect PATH` runs in a foot window: it asks for the
  password of a new network (masked; type it with the Slate, FN+A sends it
  here, then A), writes iwd's profile (mode 600), connects and shows the
  result. A failed new profile is forgotten, so a wrong password is not kept.
- `wyoh_wifi.py --bar` prints the bar's Wi-Fi text.

Passwords never reach a command line, a log or the status: they go from the
terminal to iwd's profile file only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

IWD = "net.connman.iwd"
PROFILE_DIR = Path("/storage/.cache/iwd")  # Luna 5.8i: iwd's persistent state directory
FOOT_INI = "/storage/.local/share/tanstfaafllm/wyoh/deploy/luna/foot.ini"
FUZZEL_INI = "/storage/.local/share/tanstfaafllm/wyoh/deploy/luna/fuzzel.ini"
SECURITY = {"psk": "WPA", "open": "Open", "8021x": "Enterprise", "wep": "WEP"}
SUPPORTED = ("psk", "open")
RESCAN, FORGET, DISCONNECT = "Rescan", "Forget a network…", "Disconnect"
PROFILE_WAIT_S = 5.0  # how long iwd may take to notice a new profile file


# --- pure core -------------------------------------------------------------------

@dataclass(frozen=True)
class Network:
    path: str
    ssid: str
    kind: str  # psk | open | 8021x | wep
    connected: bool
    known: str  # KnownNetwork object path, "" if not saved
    signal: int  # dBm × 100 (iwd's unit); -10000 when not in range


def station_path(objects: dict[str, Any]) -> str | None:
    """The first station-mode device (wlan0)."""
    return next((path for path, interfaces in objects.items() if f"{IWD}.Station" in interfaces), None)


def networks(objects: dict[str, Any], ordered: list[list[Any]]) -> list[Network]:
    """Networks in range, strongest first (iwd's order), from GetManagedObjects and
    GetOrderedNetworks (both as busctl --json=short `data`)."""
    signal = {path: strength for path, strength in ordered}
    found = []
    for path, interfaces in objects.items():
        props = interfaces.get(f"{IWD}.Network")
        if props is None or path not in signal:
            continue
        value = {name: item["data"] for name, item in props.items()}
        found.append(Network(path, value.get("Name", ""), value.get("Type", ""), bool(value.get("Connected")),
                             value.get("KnownNetwork", ""), signal[path]))
    return sorted(found, key=lambda n: (not n.connected, -n.signal))


def known_networks(objects: dict[str, Any]) -> list[tuple[str, str]]:
    """Saved networks as (path, SSID), by name."""
    saved = []
    for path, interfaces in objects.items():
        props = interfaces.get(f"{IWD}.KnownNetwork")
        if props is not None:
            saved.append((path, props["Name"]["data"]))
    return sorted(saved, key=lambda item: item[1].lower())


def bars(signal: int) -> str:
    """Signal as four bars, filled from the left."""
    dbm = signal / 100
    filled = 4 if dbm >= -60 else 3 if dbm >= -67 else 2 if dbm >= -75 else 1
    return "▮" * filled + "▯" * (4 - filled)


def menu_lines(found: list[Network]) -> list[str]:
    lines = []
    for network in found:
        # Short enough for the Start menu's width on the 720 px panel: WPA is the
        # usual case and is not named; other kinds are.
        mark = "✓" if network.connected else "★" if network.known else " "
        note = "" if network.kind == "psk" else f"  {SECURITY.get(network.kind, network.kind)}"
        if network.kind not in SUPPORTED:
            note += " (no)"
        lines.append(f"{mark} {network.ssid}  {bars(network.signal)}{note}")
    return lines + [RESCAN, FORGET, DISCONNECT]


def profile_name(ssid: str, kind: str) -> str:
    """iwd's file name for a network: the SSID itself when it is only letters,
    digits, space, '-' and '_'; otherwise '=' and the SSID's bytes in hex."""
    if ssid and all(c.isascii() and (c.isalnum() or c in " -_") for c in ssid):
        return f"{ssid}.{kind}"
    return f"={ssid.encode().hex()}.{kind}"


def check_passphrase(passphrase: str) -> str:
    """'' if WPA accepts it, otherwise why not."""
    if len(passphrase) == 64 and all(c in "0123456789abcdefABCDEF" for c in passphrase):
        return ""
    if not 8 <= len(passphrase) <= 63:
        return "A WPA password has 8 to 63 characters."
    if not all(" " <= c <= "~" for c in passphrase):
        return "A WPA password uses printable ASCII characters only."
    return ""


def profile_text(passphrase: str) -> str:
    key = "PreSharedKey" if len(passphrase) == 64 else "Passphrase"
    return f"[Security]\n{key}={passphrase}\n"


def failure_message(error: str) -> str:
    """What busctl's error text means for the person."""
    text = error.lower()
    if "not found" in text or "not available" in text:
        return "The network is out of range."
    if "not supported" in text:
        return "This kind of network is not supported."
    if "busy" in text or "in progress" in text:
        return "Wi-Fi is busy; try again."
    if "aborted" in text:
        return "The connection was interrupted."
    if "timed out" in text or "timeout" in text:
        return "The network did not answer."
    return "Connection failed: wrong password, or the access point refused."


# --- iwd through busctl ----------------------------------------------------------

class Iwd:
    def __init__(self, run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run) -> None:
        self.run = run

    def _busctl(self, *args: str, timeout: float = 30) -> subprocess.CompletedProcess[str]:
        return self.run(["busctl", "--json=short", f"--timeout={int(timeout)}", *args],
                        capture_output=True, text=True, timeout=timeout + 5, check=False)

    def call(self, path: str, interface: str, method: str, *args: str, timeout: float = 30) -> Any:
        result = self._busctl("call", IWD, path, f"{IWD}.{interface}", method, *args, timeout=timeout)
        if result.returncode != 0:
            raise IwdError(result.stderr.strip() or f"{method} failed")
        return json.loads(result.stdout)["data"] if result.stdout.strip() else None

    def objects(self) -> dict[str, Any]:
        result = self._busctl("call", IWD, "/", "org.freedesktop.DBus.ObjectManager", "GetManagedObjects")
        if result.returncode != 0:
            raise IwdError(result.stderr.strip() or "iwd is not running")
        return json.loads(result.stdout)["data"][0]

    def scan(self, station: str, wait: float = 8.0) -> None:
        try:
            self.call(station, "Station", "Scan")
        except IwdError:
            return  # already scanning, or connecting: use what iwd has
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline:
            time.sleep(0.5)
            props = self.objects().get(station, {}).get(f"{IWD}.Station", {})
            if not props.get("Scanning", {}).get("data", False):
                return

    def ordered(self, station: str) -> list[list[Any]]:
        return self.call(station, "Station", "GetOrderedNetworks")[0]


class IwdError(RuntimeError):
    pass


def current(iwd: Iwd) -> tuple[str | None, list[Network], dict[str, Any]]:
    objects = iwd.objects()
    station = station_path(objects)
    if station is None:
        return None, [], objects
    return station, networks(objects, iwd.ordered(station)), objects


def bar_text(iwd: Iwd) -> str:
    try:
        station, found, _ = current(iwd)
    except (IwdError, OSError, ValueError, subprocess.SubprocessError):
        return "Wi-Fi ?"
    if station is None:
        return "Wi-Fi off"
    connected = next((n for n in found if n.connected), None)
    return f"{connected.ssid} {bars(connected.signal)}" if connected else "Wi-Fi: not connected"


# --- the list (fuzzel) -----------------------------------------------------------

def fuzzel(lines: list[str], prompt: str, placeholder: str = "") -> str | None:
    command = ["fuzzel", "--config", FUZZEL_INI, "--dmenu", "--prompt", prompt,
               "--lines", str(min(max(len(lines), 1), 10))]
    if placeholder:
        command += ["--placeholder", placeholder]
    result = subprocess.run(command, input="\n".join(lines) + "\n", capture_output=True, text=True, check=False)
    choice = result.stdout.rstrip("\n")
    return choice if result.returncode == 0 and choice else None


def connect_window(path: str) -> None:
    subprocess.run(["foot", f"--config={FOOT_INI}", "--app-id=wyoh-wifi", "--title=Wi-Fi",
                    sys.executable, os.path.abspath(__file__), "--connect", path], check=False)


def panel(iwd: Iwd) -> int:
    rescan = True
    while True:
        objects = iwd.objects()
        station = station_path(objects)
        if station is None:
            fuzzel(["Close"], "Wi-Fi: ", "no Wi-Fi device")
            return 1
        if rescan:
            iwd.scan(station)
        station, found, objects = current(iwd)
        lines = menu_lines(found)
        connected = next((n.ssid for n in found if n.connected), "")
        choice = fuzzel(lines, "Wi-Fi: ", "choose a network" if connected else "not connected")
        if choice is None:
            return 0
        rescan = choice == RESCAN
        if choice == RESCAN:
            continue
        if choice == DISCONNECT:
            if fuzzel(["No", "Yes, disconnect"], "Disconnect? ") == "Yes, disconnect":
                try:
                    iwd.call(station, "Station", "Disconnect")
                except IwdError:
                    pass
            continue
        if choice == FORGET:
            saved = known_networks(objects)
            pick = fuzzel([name for _, name in saved] or ["(no saved network)"], "Forget: ")
            target = next((path for path, name in saved if name == pick), None)
            if target and fuzzel(["No", f"Yes, forget {pick}"], "Forget? ") == f"Yes, forget {pick}":
                try:
                    iwd.call(target, "KnownNetwork", "Forget")
                except IwdError:
                    pass
            continue
        network = found[lines.index(choice)] if choice in lines[:len(found)] else None
        if network is None or network.connected:
            continue
        if network.kind not in SUPPORTED:
            fuzzel(["OK"], "Not supported: ", f"{SECURITY.get(network.kind, network.kind)} networks")
            continue
        connect_window(network.path)
        return 0


# --- the connect window (foot) ---------------------------------------------------

def read_secret(prompt: str) -> str | None:
    """A masked line from the terminal; None on Escape."""
    import termios
    import tty

    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    text = ""
    try:
        tty.setraw(fd)
        while True:
            sys.stdout.write(f"\r\x1b[K{prompt}{'•' * len(text)}")
            sys.stdout.flush()
            data = os.read(fd, 64).decode("utf-8", "replace")
            for char in data:
                if char in "\r\n":
                    return text
                if char == "\x1b":
                    return None
                if char in "\x7f\x08":
                    text = text[:-1]
                elif char >= " ":
                    text += char
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        sys.stdout.write("\r\n")


def wait_key(message: str) -> None:
    print(f"\n{message}")
    print("A or B: close")
    try:
        read_secret("")
    except Exception:  # noqa: BLE001 - the window closes either way
        pass


def write_profile(directory: Path, ssid: str, kind: str, passphrase: str) -> Path:
    """iwd's profile, mode 600, written beside and renamed so iwd never reads half of it."""
    target = directory / profile_name(ssid, kind)
    temporary = directory / f".wyoh-{os.getpid()}.tmp"
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(profile_text(passphrase))
    os.replace(temporary, target)
    return target


def connect(iwd: Iwd, path: str, profile_dir: Path = PROFILE_DIR) -> int:
    objects = iwd.objects()
    props = objects.get(path, {}).get(f"{IWD}.Network")
    if props is None:
        wait_key("The network is no longer in range.")
        return 1
    ssid, kind = props["Name"]["data"], props["Type"]["data"]
    new_profile = None
    print(f"Wi-Fi: {ssid}\n")
    if kind == "psk" and "KnownNetwork" not in props:
        print("Password: press L1 to open the Slate, type it, FN+A sends it here; then A.")
        print("B cancels.\n")
        while True:
            passphrase = read_secret("Password: ")
            if passphrase is None:
                return 1
            problem = check_passphrase(passphrase)
            if not problem:
                break
            print(problem)
        new_profile = write_profile(profile_dir, ssid, kind, passphrase)
        del passphrase
        deadline = time.monotonic() + PROFILE_WAIT_S  # iwd notices the new file
        while "KnownNetwork" not in iwd.objects().get(path, {}).get(f"{IWD}.Network", {}):
            if time.monotonic() > deadline:
                break
            time.sleep(0.25)
    print("Connecting…")
    try:
        iwd.call(path, "Network", "Connect", timeout=60)
    except IwdError as error:
        if new_profile is not None:
            forget_new(iwd, path, new_profile)
        wait_key(failure_message(str(error)) + (" The password was not saved." if new_profile else ""))
        return 1
    wait_key(f"Connected to {ssid}.")
    return 0


def forget_new(iwd: Iwd, path: str, profile: Path) -> None:
    known = iwd.objects().get(path, {}).get(f"{IWD}.Network", {}).get("KnownNetwork", {}).get("data")
    if known:
        try:
            iwd.call(known, "KnownNetwork", "Forget")
        except IwdError:
            pass
    profile.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wyoh's Wi-Fi panel (iwd)")
    parser.add_argument("--connect", metavar="PATH", help="join this iwd network (in a terminal)")
    parser.add_argument("--bar", action="store_true", help="print the bar's Wi-Fi text")
    args = parser.parse_args(argv)
    iwd = Iwd()
    if args.bar:
        print(bar_text(iwd))
        return 0
    try:
        if args.connect:
            return connect(iwd, args.connect)
        return panel(iwd)
    except IwdError as error:
        if args.connect:
            wait_key(f"Wi-Fi error: {error}")
        else:
            fuzzel(["Close"], "Wi-Fi: ", f"error: {error}"[:60])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
