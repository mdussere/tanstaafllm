# Mike v0 tool contract (Step 1.2–1.4)

> **Freshness:** 🟢 current · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** mike 1.2 ✅

**Question answered:** exactly which tools does the model see, with which allowed values, and how does Mike's adapter turn each call into Wyoh MCP requests?<br>
**Date:** 2026-10-09<br>
**Status:** 📋 draft written under Professor's decision D13 (delegated by the user). **Awaiting the user's approval** (Step 1 acceptance). Items marked **⚖️** need an explicit yes from the user.<br>
**Sources read (nothing changed in Wyoh):**
- `src/wyoh/wyoh_mcp_server.py`: tool names and arguments;
- `src/wyoh/deploy/luna/share/applications/*.desktop`, `src/wyoh/apps/calculator/wyoh-app.toml`, `src/wyoh/deploy/luna/menu.toml`, `src/wyoh/wyoh_apps.py`: the menu entries and the manifest schema;
- `src/wyoh/wyoh_layout.py`: the tile policy;
- `worklines/wyoh/docs/0900_01`: the planned Step 9 apps.

## 1. What the model sees

Seven tools. Every argument is either a closed list of values or a short free text. The model's output is never passed to Sway as is.

| Tool | Arguments | Meaning |
| --- | --- | --- |
| `list_windows` | — | say which windows are open and which has focus |
| `focus_window` | `app` ∈ open apps | bring an open window to the front |
| `launch_app` | `app` ∈ allowlist | start an application |
| `close_window` | `app` ∈ open apps | close a window |
| `move_window` | `app` ∈ open apps, `place` ∈ {`left`, `right`, `top`, `bottom`, `full`} | move a window or make it full screen |
| `type_text` | `text`: 1–200 characters, one line | type the text into the focused window |
| `none` | `reason`: 1–120 characters | nothing fits; say why |

The `app` list given to the model is the allowlist below. The prompt also says which apps are open and which one has focus; the adapter reads that from Wyoh just before each request.

## 2. The app allowlist

Mike's ids are short English words. They are not Wyoh's ids: one Mike id maps to one Wyoh menu entry. The French names are the words users are likely to say. They feed the prompt and the keyword baseline.

| Mike id | French names | Wyoh entry (source) | Sway `app_id` | Status |
| --- | --- | --- | --- | --- |
| `terminal` | terminal, console | `wyoh-terminal.desktop` (`Exec=foot`) | `foot` | available |
| `editor` | éditeur, éditeur de texte | `wyoh-editor.desktop` (`foot -a wyoh-editor vim`) | `wyoh-editor` | available |
| `images` | visionneuse, images, photos | `wyoh-imageviewer.desktop` (`swayimg …`) | `swayimg` (to confirm on `luna-pi`) | available |
| `tasks` | gestionnaire de tâches, tâches, processus | `wyoh-taskmanager.desktop` (`foot -a wyoh-htop htop`) | `wyoh-htop` | available |
| `calculator` | calculatrice, calculette | Wyoh app `calculator` (`wyoh-app.toml`) | `wyoh-calculator` | available (Wyoh 9.5) |
| `browser` | navigateur, internet, NetSurf | planned Wyoh app (NetSurf) | from its manifest | planned (Wyoh Step 9) |
| `files` | fichiers, gestionnaire de fichiers, Commander | planned Wyoh app (Commander) | from its manifest | planned |
| `chess` | échecs | planned Wyoh app (pygameUCI + Stockfish) | from its manifest | planned |
| `wolfenstein` | Wolfenstein, Wolf | planned Wyoh app (PortMaster) | from its manifest | planned |
| `dino` | dino, dinosaure, le jeu du dinosaure | planned Wyoh app (Dino, white on black) | from its manifest | planned |

Rules:

- **The allowlist is generated, not hand-written, once Wyoh's apps exist.** Mike reads Wyoh's generated `.desktop` entries and manifests, keeps those not hidden by `menu.toml`, and adds its own French names. Until then, the evaluation uses the table above.
- **A planned app the session does not have** is refused by the adapter ("calculator is not installed"). Nothing is launched.
- **Hidden entries** (`menu.toml`: htop, nvtop, cups, mpv, gmu, mupen64plus, the old bc calculator) are never in the allowlist.

## 3. How the adapter maps calls onto Wyoh MCP

Templates only. `{app_id}` and `{exec}` come from the allowlist, never from the model.

| Call | Wyoh MCP request(s) | Before running |
| --- | --- | --- |
| `list_windows()` | `sway_get_tree` → summary: app names, focused one | nothing; read-only, runs without asking |
| `focus_window(app)` | `sway_command('[app_id="{app_id}"] focus')` | app must be open |
| `launch_app(app)` | `sway_command('exec {exec}')`, where `{exec}` is the entry's `Exec=` line | app must be on the allowlist and installed |
| `close_window(app)` | `sway_command('[app_id="{app_id}"] kill')` | app must be open; **the console asks a second time** ("Close calculator? Unsaved work may be lost") |
| `move_window(app, left/right/top/bottom)` | `sway_command('[app_id="{app_id}"] focus')`, then `sway_command('move {direction}')` with `top` → `up`, `bottom` → `down` (Sway's names) | app must be open |
| `move_window(app, full)` | `sway_command('[app_id="{app_id}"] fullscreen toggle')` | app must be open |
| `type_text(text)` | `wyoh_dev_keyboard_type(text)` | a window must have focus; the text is shown in full before acceptance |
| `none(reason)` | nothing | — |

Everything except `list_windows` and `none` runs only after the user accepts the proposed action.

**Not exposed, ever:** raw `sway_command`, `exec` of anything not on the allowlist, `sway_get_config`, subscriptions, screenshots, the gamepad tools, `wyoh_stop_owned_child_for_test`.

### Adapter rules

1. **Refuse, never guess.** An `app` that is not on the allowlist, or not open when it must be, is refused with the reason. The model's call is shown next to the refusal.
2. **⚖️ "Focus a closed app" becomes "launch it".** If the model calls `focus_window(app)` and `app` is not open but is on the allowlist, the adapter proposes `launch_app(app)` instead and says so: "calculator is not open: launch it?". The user still accepts. On the smoke set this would fix two of LFM2.5-350M's three errors (`0302_02`). Professor marked it for the user's approval (D13).
3. **⚖️ `move_window` places are relative.** Wyoh's layout policy (`wyoh_layout.py`) fixes up to four tiles in a set order. `move left` in Sway moves the window one step in the tiling, not to an absolute half of the screen, and the policy may move it back. So in v0, `left`/`right`/`top`/`bottom` are relative moves, and only `full` is absolute. Whether Wyoh should offer absolute placement is a question for Wyoh (Step 6.2 note), not a change Mike makes.
4. **`type_text` uses a development-only tool.** `wyoh_dev_keyboard_type` is the virtual-keyboard stand-in. A production text-input path is Wyoh's to define (Step 6.2 note).
5. **One call per request.** No chaining, no retries by the model. If Wyoh's answer is an error, the console shows it as it is.

## 4. Inputs and outputs (1.4)

**From Mycroft (in):** one accepted UTF-8 line, exactly as Mycroft emits it, without changes. Today that is lower case, without punctuation (`docs/LOGBOOK.md`, Mycroft 2026-10-09). A source tag (`mycroft` or `typed`) goes with it, for the record only; it does not change what Mike may do. Mike never receives a draft or partial results. The hand-off itself is a later note to Mycroft (Step 6.1).

**To Mannie (out), later:** when the result is `none`, the console may offer "ask Mannie?". Only if the user says yes, Mike sends the request text, the model's reason and the desktop summary to Mannie, and shows the cost. Nothing is sent automatically. This is designed in Step 6.3, not built.

## 5. What the evaluation set uses

The Step 2 evaluation set is written against this contract: the ten Mike ids above, a scripted desktop state per case (open apps, focus), and the expected call. The **ten Mike ids replace the seven app names of the smoke set**, which were placeholders (the smoke set had no `editor`, `images` or `tasks`).
