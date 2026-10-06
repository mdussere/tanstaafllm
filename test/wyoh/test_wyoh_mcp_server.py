from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


SCRIPTS = Path(__file__).parents[2] / "src" / "wyoh"
MAKEFILE = Path(__file__).parents[2] / "Makefile"
sys.path.insert(0, str(SCRIPTS))
import wyoh_mcp_server as server  # noqa: E402


class FakeIPC:
    def __init__(self, socket_path: str, *, events: list[tuple[int, Any]]) -> None:
        self.socket_path = socket_path
        self.events = events
        self.requests: list[tuple[int, str]] = []
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def request(self, message_type: int, payload: str = "") -> Any:
        self.requests.append((message_type, payload))
        if message_type == server.REQUEST_TYPES["sway_subscribe"]:
            return {"success": True}
        return {"message_type": message_type, "payload": payload, "nested": {"raw": True}}

    def receive(self, timeout_seconds: float | None = None) -> tuple[int, Any]:
        assert timeout_seconds is not None
        if not self.events:
            raise TimeoutError
        return self.events.pop(0)


class FakeSession:
    state = "running"
    process = SimpleNamespace(pid=4242)


class FakeFactory:
    def __init__(self) -> None:
        self.instances: list[FakeIPC] = []

    def __call__(self, socket_path: str) -> FakeIPC:
        ipc = FakeIPC(socket_path, events=[(server.EVENT_TYPES["tick"], {"payload": "proof"})])
        self.instances.append(ipc)
        return ipc


def test_every_documented_request_is_forwarded_with_its_exact_message_type() -> None:
    factory = FakeFactory()
    bridge = server.SwayBridge(FakeSession(), "/owned/socket", ipc_factory=factory)

    for tool_name, message_type in server.REQUEST_TYPES.items():
        if tool_name == "sway_subscribe":
            continue
        raw_reply = bridge.request(tool_name, "payload" if tool_name == "sway_command" else "")
        ipc = factory.instances[-1]
        assert ipc.socket_path == "/owned/socket"
        assert ipc.requests == [(message_type, "payload" if tool_name == "sway_command" else "")]
        assert ipc.closed
        assert raw_reply == {
            "message_type": message_type,
            "payload": "payload" if tool_name == "sway_command" else "",
            "nested": {"raw": True},
        }


def test_subscription_preserves_the_documented_event_type_and_cleans_up() -> None:
    factory = FakeFactory()
    bridge = server.SwayBridge(FakeSession(), "/owned/socket", ipc_factory=factory)

    created = bridge.subscribe(["workspace", "tick"])
    subscription_id = created["subscription_id"]
    assert created["events"] == ["workspace", "tick"]
    assert factory.instances[0].requests == [
        (server.REQUEST_TYPES["sway_subscribe"], '["workspace", "tick"]')
    ]

    event = bridge.next_event(subscription_id, timeout_seconds=1.0)
    assert event == {"event": "tick", "payload": {"payload": "proof"}}
    assert bridge.unsubscribe(subscription_id) == {"subscription_id": subscription_id, "closed": True}
    assert factory.instances[0].closed


def test_subscription_rejects_unknown_or_duplicate_events_without_opening_a_socket() -> None:
    factory = FakeFactory()
    bridge = server.SwayBridge(FakeSession(), "/owned/socket", ipc_factory=factory)
    with pytest.raises(ValueError, match="unsupported"):
        bridge.subscribe(["not-an-ipc-event"])
    with pytest.raises(ValueError, match="unique"):
        bridge.subscribe(["tick", "tick"])
    assert factory.instances == []


def test_subscription_timeout_is_a_normal_structured_wait_result() -> None:
    factory = FakeFactory()
    bridge = server.SwayBridge(FakeSession(), "/owned/socket", ipc_factory=factory)
    subscription_id = bridge.subscribe(["workspace"])["subscription_id"]
    factory.instances[0].events.clear()

    assert bridge.next_event(subscription_id, timeout_seconds=0.1) == {
        "timeout": True,
        "timeout_seconds": 0.1,
        "subscription_id": subscription_id,
    }


def test_all_documented_event_numbers_are_pinned() -> None:
    assert server.EVENT_TYPES == {
        "workspace": 0x80000000,
        "output": 0x80000001,
        "mode": 0x80000002,
        "window": 0x80000003,
        "barconfig_update": 0x80000004,
        "binding": 0x80000005,
        "shutdown": 0x80000006,
        "tick": 0x80000007,
        "bar_state_update": 0x80000014,
        "input": 0x80000015,
    }


def test_tool_discovery_exposes_every_request_and_subscription_operation() -> None:
    tools = asyncio.run(server.mcp.list_tools())
    names = {tool.name for tool in tools}
    assert names == set(server.REQUEST_TYPES) | {
        "sway_next_event",
        "sway_unsubscribe",
        "wyoh_server_status",
        "wyoh_capture_screenshot",
        "wyoh_stop_owned_child_for_test",
        # Step 5: development-only simulated person, and the gamepad daemon's status
        "wyoh_dev_gamepad_tap",
        "wyoh_dev_gamepad_buttons",
        "wyoh_dev_gamepad_stick",
        "wyoh_dev_keyboard_type",
        "wyoh_dev_keyboard_key",
        "wyoh_gamepad_status",
    }


def test_simulated_person_refuses_unknown_buttons_before_creating_a_device(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[str] = []
    monkeypatch.setattr(server, "_person", lambda kind: created.append(kind))
    with pytest.raises(ValueError, match="unknown gamepad buttons"):
        server.wyoh_dev_gamepad_tap(["BTN_EAST", "BTN_NOPE"])
    with pytest.raises(ValueError, match="hold_seconds"):
        server.wyoh_dev_gamepad_tap(["BTN_EAST"], hold_seconds=60)
    with pytest.raises(ValueError, match="stick"):
        server.wyoh_dev_gamepad_stick(100, 0, seconds=1, stick="middle")
    assert created == []


def test_main_refuses_an_ambient_sway_socket_before_starting_a_child(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWAYSOCK", "/forbidden/live/socket")
    monkeypatch.setattr(
        server,
        "_arguments",
        lambda: SimpleNamespace(
            full_ipc_development=True,
            shared_vnc_session=False,
            sway_binary="unused",
            library_path="unused",
        ),
    )
    with pytest.raises(SystemExit, match="ambient Sway socket"):
        server.main()


def test_shared_session_requires_the_fixed_owner_written_descriptor(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    session = server.SharedVncSwaySession(tmp_path / "missing.json")
    with pytest.raises(server.SwayIPCError, match="not ready"):
        session.start()


def test_deployment_preview_is_transport_only_and_cannot_manage_a_service() -> None:
    makefile = MAKEFILE.read_text(encoding="utf-8")
    target = makefile.split("wyoh-deploy-preview:\n", 1)[1].split("\nwyoh-deploy:\n", 1)[0]
    assert target.count("rsync ") == 2
    assert target.count("--dry-run") == 2
    assert "systemctl" not in target
