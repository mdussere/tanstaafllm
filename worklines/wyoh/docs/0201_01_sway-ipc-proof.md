# Step 2 evidence — Sway IPC proof

> **Freshness:** 🟡 historical · **Written:** 2026-09-26 · **Checked:** 2026-10-31 · **Step:** wyoh 2.1 ✅

**Status:** passed on 2026-09-26
**Question answered:** Can the proposed Sway-v0 boundary read session state, perform one bounded operation, observe its completion, and reject unsafe requests without a side effect?

## Pinned substrate and protocol

The live proof used Sway **1.10.1** from Debian Trixie package `1.10.1-2+rpt1`. It was downloaded and extracted into a dedicated `luna-pi` user-local prefix; the system package database and the existing Labwc/WayVNC session were not changed. The matching downloaded wlroots package was `0.18.2-3+rpt4+b1`.

The fixture implements Sway's packaged `sway-ipc(7)` Unix-socket framing directly: `i3-ipc`, native-endian payload length and type, followed by JSON. It records `GET_VERSION` (7), `GET_OUTPUTS` (3), `GET_TREE` (4), `GET_WORKSPACES` (1), `GET_INPUTS` (100), and `GET_SEATS` (101). It subscribes with `SUBSCRIBE` (2) to `workspace` events and permits exactly one `RUN_COMMAND` (0): `workspace wyoh-proof`.

## Capability and synchronisation result

`FocusWorkspaceMediator` accepts only an explicitly granted, exact-revision, unambiguous workspace selector. It constructs the fixed workspace command itself; a consumer cannot supply an arbitrary Sway command. Asset-free pytest checks prove that unauthorised, stale, and malformed/ambiguous requests leave the recording transport empty.

The live test takes its pre-operation snapshot, subscribes, sends the allowed command, discards unrelated queued workspace events, waits specifically for a `workspace` event whose change is `focus` and current workspace is `wyoh-proof`, and then takes a post-operation snapshot. It uses no completion sleep. The first run exposed an initial queued `init` event; that evidence is retained and led to the predicate-specific wait used by the passing run.

## Passing live evidence

Command:

```bash
WYOH_LIVE=1 python3 -m pytest -m live test/wyoh -q
```

Passing result directory: `results/wyoh/sway-ipc/20260926T113413Z/`.

- Sway reported `1.10.1`; the headless output was `HEADLESS-1` at 1280×720.
- The post-operation workspace was `wyoh-proof`; the observed event change was `focus`.
- Startup to IPC socket: 42.106 ms; focus event latency: 0.612 ms; sampled RSS: 20,144 KiB; child recovery after termination: 7.521 ms.
- The 250.781 ms idle sample accumulated five CPU ticks. It is a short sample, not a power or thermal claim.
- The default test command passed two deterministic tests and deselected the live check. The final live command passed one test and deselected two.

No rendered-client or VNC assertion was made, so no screenshot is offered as UI-success evidence. This is an IPC/session proof only; display composition, physical inputs, graphics acceleration, and Luna fit remain separate evidence.

## Limits

The test uses a temporary headless Sway child on `luna-pi`, an empty input set, the Pixman renderer, and an ephemeral workspace. It demonstrates a portable Sway IPC contract and Pi-specific process behaviour, not an interactive Luna desktop, controller mapping, GPU capability, or target resource budget.
