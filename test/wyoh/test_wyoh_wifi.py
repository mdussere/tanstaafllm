"""Deterministic tests for Wyoh's Wi-Fi panel core (Step 7.2).

The iwd objects mirror Luna's read-only inventory of 2026-10-15
(results/wyoh/wifi-inventory/20261015/managed-objects.json), trimmed. No
D-Bus, no fuzzel, no terminal.
"""

from __future__ import annotations

import json
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh"))
import wyoh_wifi as w  # noqa: E402

STATION = "/net/connman/iwd/0/2"
HOME = f"{STATION}/4d69636b207769666920686f6d65_psk"
BOX = f"{STATION}/46726565626f782d314532334236_psk"
CAFE = f"{STATION}/636166c3a9_open"
OFFICE = f"{STATION}/6f6666696365_8021x"
KNOWN_HOME = "/net/connman/iwd/4d69636b207769666920686f6d65_psk"


def _v(kind: str, value):
    return {"type": kind, "data": value}


def _network(name: str, kind: str, connected: bool = False, known: str = "") -> dict:
    props = {"Name": _v("s", name), "Connected": _v("b", connected), "Device": _v("o", STATION),
             "Type": _v("s", kind)}
    if known:
        props["KnownNetwork"] = _v("o", known)
    return {"net.connman.iwd.Network": props, "org.freedesktop.DBus.Properties": {}}


OBJECTS = {
    "/": {"org.freedesktop.DBus.ObjectManager": {}},
    "/net/connman/iwd/0": {"net.connman.iwd.Adapter": {"Powered": _v("b", True)}},
    STATION: {"net.connman.iwd.Device": {"Name": _v("s", "wlan0")},
              "net.connman.iwd.Station": {"State": _v("s", "connected"), "Scanning": _v("b", False),
                                          "ConnectedNetwork": _v("o", HOME)}},
    HOME: _network("Mick wifi home", "psk", connected=True, known=KNOWN_HOME),
    BOX: _network("Freebox-1E23B6", "psk"),
    CAFE: _network("café", "open"),
    OFFICE: _network("office", "8021x"),
    f"{STATION}/gone_psk": _network("gone", "psk"),  # not in GetOrderedNetworks: out of range
    KNOWN_HOME: {"net.connman.iwd.KnownNetwork": {"Name": _v("s", "Mick wifi home"), "Type": _v("s", "psk")}},
}
ORDERED = [[BOX, -5500], [HOME, -5700], [CAFE, -7000], [OFFICE, -8200]]


# --- reading iwd --------------------------------------------------------------------

def test_the_station_is_wlan0():
    assert w.station_path(OBJECTS) == STATION


def test_networks_in_range_connected_first_then_strongest():
    found = w.networks(OBJECTS, ORDERED)
    assert [n.ssid for n in found] == ["Mick wifi home", "Freebox-1E23B6", "café", "office"]
    assert found[0].connected and found[0].known == KNOWN_HOME and found[0].signal == -5700
    assert not found[1].known


def test_saved_networks():
    assert w.known_networks(OBJECTS) == [(KNOWN_HOME, "Mick wifi home")]


@pytest.mark.parametrize("signal, shown", [(-4500, "▮▮▮▮"), (-6500, "▮▮▮▯"), (-7000, "▮▮▯▯"), (-8800, "▮▯▯▯")])
def test_signal_bars(signal, shown):
    assert w.bars(signal) == shown


def test_menu_lines():
    assert w.menu_lines(w.networks(OBJECTS, ORDERED)) == [
        "✓ Mick wifi home  ▮▮▮▮",
        "  Freebox-1E23B6  ▮▮▮▮",
        "  café  ▮▮▯▯  Open",
        "  office  ▮▯▯▯  Enterprise (no)",
        "Rescan", "Forget a network…", "Disconnect"]


def test_a_saved_network_out_of_reach_is_starred_when_in_range():
    objects = {**OBJECTS, HOME: _network("Mick wifi home", "psk", known=KNOWN_HOME)}
    assert w.menu_lines(w.networks(objects, ORDERED))[1].startswith("★ Mick wifi home")


# --- profiles -----------------------------------------------------------------------

@pytest.mark.parametrize("ssid, name", [
    ("Mick wifi home", "Mick wifi home.psk"),       # as on Luna (/storage/.cache/iwd)
    ("Free_box-1", "Free_box-1.psk"),
    ("café", "=636166c3a9.psk"),
    ("a/b", "=612f62.psk"),
    ("Mick's", "=4d69636b2773.psk"),
])
def test_iwd_profile_names(ssid, name):
    assert w.profile_name(ssid, "psk") == name


@pytest.mark.parametrize("passphrase, ok", [
    ("short", False), ("12345678", True), ("x" * 63, True), ("x" * 64, False), ("a" * 64, True),
    ("mot de passe é", False), ("tab\there", False)])
def test_passphrase_rules(passphrase, ok):
    assert (w.check_passphrase(passphrase) == "") is ok


def test_profile_is_written_whole_with_mode_600(tmp_path):
    path = w.write_profile(tmp_path, "café", "psk", "secret-123")
    assert path.name == "=636166c3a9.psk"
    assert path.read_text(encoding="utf-8") == "[Security]\nPassphrase=secret-123\n"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert [p.name for p in tmp_path.iterdir()] == [path.name]  # no temporary file left


def test_a_64_hex_key_is_a_pre_shared_key():
    assert w.profile_text("ab" * 32).startswith("[Security]\nPreSharedKey=")


@pytest.mark.parametrize("error, start", [
    ("Call failed: Operation failed", "Connection failed: wrong password"),
    ("Call failed: Operation aborted", "The connection was interrupted"),
    ("Call failed: Object not found", "The network is out of range"),
    ("Call failed: Operation already in progress", "Wi-Fi is busy"),
])
def test_failure_messages(error, start):
    assert w.failure_message(error).startswith(start)


# --- busctl calls, and no secret anywhere -------------------------------------------

@pytest.fixture(autouse=True)
def _no_wait(monkeypatch):
    monkeypatch.setattr(w, "PROFILE_WAIT_S", 0.0)


class FakeBus:
    """busctl stand-in: answers from OBJECTS, records every command line."""

    def __init__(self, fail: dict[str, str] | None = None) -> None:
        self.commands: list[list[str]] = []
        self.fail = fail or {}

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        method = command[-1] if command[-1][0].isupper() else command[-2]
        if method in self.fail:
            return subprocess.CompletedProcess(command, 1, "", self.fail[method])
        if method == "GetManagedObjects":
            out = {"type": "a{oa{sa{sv}}}", "data": [OBJECTS]}
        elif method == "GetOrderedNetworks":
            out = {"type": "a(on)", "data": [ORDERED]}
        else:
            return subprocess.CompletedProcess(command, 0, "", "")
        return subprocess.CompletedProcess(command, 0, json.dumps(out), "")


def test_bar_shows_the_connected_network_and_its_signal():
    assert w.bar_text(w.Iwd(FakeBus())) == "Mick wifi home ▮▮▮▮"


def test_bar_without_iwd():
    assert w.bar_text(w.Iwd(FakeBus({"GetManagedObjects": "Unit not found"}))) == "Wi-Fi ?"


def test_a_failed_new_network_is_forgotten_and_its_file_removed(tmp_path, monkeypatch, capsys):
    bus = FakeBus({"Connect": "Call failed: Operation failed"})
    monkeypatch.setattr(w, "read_secret", lambda prompt: "wrong-password-1" if prompt else "")
    w.connect(w.Iwd(bus), BOX, tmp_path)
    assert list(tmp_path.iterdir()) == []
    out = capsys.readouterr().out
    assert "wrong password" in out and "The password was not saved." in out
    connect = [c for c in bus.commands if "Connect" in c]
    assert connect and connect[0][:2] == ["busctl", "--json=short"]
    everything = json.dumps(bus.commands) + out
    assert "wrong-password-1" not in everything  # never on a command line or the screen


def test_a_known_network_connects_without_a_password(tmp_path, monkeypatch, capsys):
    bus = FakeBus()
    asked = []
    monkeypatch.setattr(w, "read_secret", lambda prompt: asked.append(prompt) or "")
    assert w.connect(w.Iwd(bus), HOME, tmp_path) == 0
    assert asked == [""]  # only the closing key
    assert "Connected to Mick wifi home." in capsys.readouterr().out
    assert list(tmp_path.iterdir()) == []


def test_escape_at_the_password_cancels_without_a_profile(tmp_path, monkeypatch):
    bus = FakeBus()
    monkeypatch.setattr(w, "read_secret", lambda prompt: None)
    assert w.connect(w.Iwd(bus), BOX, tmp_path) == 1
    assert list(tmp_path.iterdir()) == [] and not any("Connect" in c for c in bus.commands)


def test_the_menu_offers_wifi():
    entry = (ROOT / "src/wyoh/deploy/luna/share/applications/wyoh-wifi.desktop").read_text(encoding="utf-8")
    assert "Name=Wi-Fi" in entry and "wyoh_wifi.py" in entry
