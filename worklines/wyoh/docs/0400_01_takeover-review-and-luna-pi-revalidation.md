# Takeover review, uv environment, and `luna-pi` re-validation

**Date:** 2026-10-04
**Step:** Wyoh 4 (review and re-validation; no new step executed)
**Question answered:** Is the Wyoh record coherent and is its pre-hardware evidence still reproducible, and what does Step 4 need next?

## 1. Review

Every Wyoh record, the source, the tests, the logbook, and the overlapping Luna-workline records were reviewed when the workline changed owner. The substance holds: Steps 1–3.6 are done and their evidence is consistent with the plan. These incoherences were fixed in the same change:

| Where | Problem | Fix |
| --- | --- | --- |
| `plan_wyoh.md` banner | Still read "Step 1 is reopened" (2026-09-25), though Step 1 was ratified on 2026-09-26. | Replaced with a 2026-10-04 status. |
| `plan_wyoh.md` 4.4 | The pre-reachability "defer" acceptance stayed ticked as current after Step 4 was reopened. | Labelled historical. |
| `plan_wyoh.md` time tracking / artifacts | Stray Step 3.6 line; two artifact sections; `0306_02` unlisted. | Removed; merged into one grouped list. |
| `plan_wyoh.md` Mycroft amendment | Asked Step 1 to add a snapshot contract after Step 1 had closed. | Points to the ratified boundary in `0101_06`; detailed contract waits for Mycroft. |
| `0000_03` | Two contradictory banners (Sway is current vs. HIOM is the active product shape). | Old banner rewritten as dated history. |
| `0305_01` | `window` listed only as untriggerable, though Step 3.6 observed it. | Matrix and conclusion updated. |
| `0000_01` | Broken source link to `general/docs/`. | Now `professor/docs/`. |
| `0404_01` | Defer decision read as current. | Marked historical. |
| `docs/01_principles.md` | "Wyoh is deferred until the handheld is available." | Replaced with the actual state. |
| `AGENTS.md` | Active-workline table omitted `luna`. | Row added. |

Not changed: `worklines/luna/plan_luna.md` still shows items 2.6–2.8 (shared Sway + WayVNC on `luna-pi`) as open, although Wyoh 3.6 completed and validated that transition. The file carries uncommitted work from another agent, so the Luna owner should close those items.

## 2. Environment

The host previously had no single test environment: the project `.venv` (Python 3.14) held only Playwright, and pytest/MCP lived in an unrelated miniconda install. Bare `pytest` also collected third-party tests from the ignored `data/` link and failed with 24 collection errors.

Now:

- `pyproject.toml` (non-package) with dependency groups `dev` (pytest 9.1.1, pytest-timeout 2.4.0), `wyoh` (mcp 2.2.0, Pillow, vncdotool), and `scrape` (Playwright 1.63.0); `uv.lock` committed; `.python-version` 3.12, matching the host Python used for the 2026-09-28 evidence.
- `uv sync` rebuilt `.venv` on CPython 3.12.4. uv 0.12.23 was installed to `~/.local/bin` from PyPI.
- `pytest.ini` sets `testpaths = test`.
- The `luna-pi` bridge venv (`/home/michael/.local/opt/wyoh-mcp-2.2.0`, `mcp==2.2.0`) is unchanged and still pinned by `src/wyoh/requirements-mcp-over-ssh.txt`; the host group pins the same SDK version.

## 3. Re-validation

| Check | Command | Result |
| --- | --- | --- |
| Whole deterministic suite | `uv run pytest -m "not live and not integration" -q` | `43 passed, 9 deselected` |
| Deployed source drift | `rsync -ani --checksum` dry run of `src/wyoh/` and the unit | no differences; nothing redeployed |
| Wyoh live proofs on `luna-pi` | `WYOH_LIVE=1 WYOH_SHARED_VNC_LIVE=1 uv run pytest -m live test/wyoh --deselect test/wyoh/test_luna_stock_inventory.py -vv -rA --timeout=120` | `4 passed, 12 deselected in 19.21s` |

The Luna stock-inventory live test was deliberately not run: it targets the factory EmuELEC card, which is archived and set aside.

Log: `logs/wyoh/uv_live_rerun_20261004_003410.log`. Evidence (ignored):

- `results/wyoh/sway-ipc/20261003T223428Z/` — Sway 1.10.1; socket ready 42.1 ms; workspace-focus event latency 0.57 ms; sampled RSS 20,148 KiB; 5 CPU ticks over 250.8 ms; recovery 7.6 ms. All within noise of the 2026-09-26 values.
- `results/wyoh/mcp-over-ssh/20261003T223411Z/` — MCP protocol 2026-07-28; 20 tools discovered; events observed `tick`, `workspace`, `shutdown`.
- `results/wyoh/shared-sway-vnc/20261003T223415Z/` — descriptor-bound attachment to the running service; `window` `new` event for `lxterminal`; server-side screenshot 10,392 bytes, SHA-256 `16faec2a…5b47`.
- `results/wyoh/shared-sway-vnc-vnc/20261003T223419Z/` — independent VNC frames, 1280×720.

**Corrected the same day:** a numerical check of the VNC frames (579 vs. 141,521 distinct colours; 910,266 of 921,600 pixels changed) was first read as supporting the rendered-client claim. Visual inspection, prompted by the user, proved the opposite: `before-terminal.png` (`a2ef…`) shows an `lxterminal` left by the preceding test, and `terminal-visible.png` (`b5fe…`) shows only the wallpaper, captured on the `window` event before the terminal drew. A colour count cannot tell a wallpaper from an application. See section 5.

`luna-pi` was not modified. `wyoh-sway-vnc.service` remained active with its loopback-only `127.0.0.1:5900` listener; `luna-vnc.service` remains installed and disabled.

## 4. Conclusions

1. **The IPC and MCP evidence is reproducible; the Step 3.6 VNC proof is not valid.** Steps 2, 3, and 3.5 and the service/descriptor/screenshot parts of 3.6 re-pass with the same figures. The 3.6 rendered-client test passes for the wrong reason (section 5).
2. **The MCP screenshot does show content.** Its bytes repeat across runs because the same terminal renders identically each time: a grim capture taken on 2026-10-04 with `lxterminal` open has the same 10,392-byte size and shows the terminal. An earlier version of this note wrongly said it showed only the background.
3. **Step 4's target has changed.** Its open items (4.2, 4.6) still describe inventorying the stock EmuELEC frontend. That card is archived and set aside. The relevant target is now the Luna workline's disposable ArchR card, which already boots Sway + EmulationStation on Luna's real RK3326/720×720 hardware: the most direct evidence yet that Sway runs there, but not yet Wyoh evidence.
4. **The blocker is Luna networking, owned by the Luna workline.** ArchR has no Wi-Fi until the RK915 overlay (Luna 5.8e) works. Without SSH, no Wyoh check can run on Luna.
5. **Proposed Step 4 re-scope (needs a decision, not applied):** once ArchR has SSH, a read-only inventory of ArchR's Sway (version, config, launch chain, IPC socket, input devices, outputs), a memory measurement of the full Sway + EmulationStation session against the 150/200 MiB Wyoh budget, and then the IPC proof against that live session. That last item attaches to a session Wyoh does not own, which the bridge currently refuses by design; it needs an explicit decision on read-only vs. one allowlisted action.
6. **Open version question:** whether "unmodified, version-pinned Sway" means ArchR's shipped Sway or our pinned 1.10.1. This decides Step 6.1 (formerly 5.1).

## 5. Correction after visual inspection (same day)

The user reported that the "terminal visible" image shows only the Sway background and that the VNC session cannot be used. Both are correct.

- **The VNC test is racy.** It captures `terminal-visible` as soon as Sway emits the `window` `new` event, before the client's first frame. Its `before` frame contained a terminal left by the preceding MCP test, whose cleanup `kill` acts on whatever is focused. "The frames differ" was true, but for the reverse reason.
- **Rendering itself works.** With one `lxterminal` opened for diagnosis (then closed by `app_id`), both a grim capture and a fresh VNC capture showed the terminal correctly. The VNC capture is byte-identical to the test's `before-terminal.png`.
- **The session is unusable by a person.** `sway-vnc.conf` replaces Sway's default config and keeps only a wallpaper, the descriptor writer, and WayVNC: no key bindings, no bar, no launcher. Over VNC there is nothing to click and no key does anything.
- **Lesson:** numerical image checks (colour counts, whole-frame differences) cannot replace looking at the image. Step 3.7 requires visual inspection by the agent.

Proposed fix: Wyoh Step 3.7 in the plan (a minimal workable environment, then an MCP scenario with per-step inspected screenshots). It awaits a green light. `luna-pi` configuration was not changed during this diagnosis.
