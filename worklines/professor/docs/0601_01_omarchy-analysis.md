# 0601 — Omarchy as an external reference for Luna

> **Freshness:** 🟡 historical · **Written:** 2026-10-09 · **Checked:** 2026-10-31 · **Step:** professor 6.1 ✅

**Question answered:** What is Omarchy, how does it relate to TANSTAAFLLM, and which of its ideas are worth taking to the low-end R36 Ultra (Luna)?

**Status:** review-ready, 2026-10-05 (Professor Step 6)<br>
**Sources:** [omarchy.org](https://omarchy.org/), its [manual](https://omarchy.org/manual/), and the [basecamp/omarchy](https://github.com/basecamp/omarchy) repository (`quattro` branch, version 4.0.x): `AGENTS.md`, manual chapters 04, 05, 06, 10, 11, 13, 14, 17, 30, 31, 47 and 49, and `agents/skills/{migrations,command-metadata,visual-verification,acceptance-tests}.md`, read on 2026-10-05. Nothing was installed or run. All Luna facts come from existing Luna and Wyoh records.

## 1. What Omarchy is

Omarchy is DHH's opinionated Arch Linux + Hyprland distribution for developer laptops ("the malleable OS for the age of agents"). It is MIT-licensed and delivered as an x86_64 ISO plus pacman packages from its own repository and Arch mirror. ARM, Apple Silicon and the Steam Deck are community ports only (manual ch. 49).

| Area | Omarchy's choice |
| --- | --- |
| Base / packaging | Arch Linux. Omarchy itself is a set of pacman packages. Its defaults live in `/usr/share/omarchy`, and the user's overrides in `~/.config`. |
| Session | Hyprland (tiling, animated) under uwsm. A single long-running **Quickshell (Qt Quick)** process draws the bar, menu, notifications, OSD and lock screen. |
| Interaction | Keyboard only ("you literally can't do a thing with the mouse alone"). `Super+Space` opens the Omarchy Menu, a dotted-id tree. Common apps have direct hotkeys. |
| Command surface | One `omarchy` CLI over `bin/omarchy-<group>-<name>` scripts. Each script declares its metadata in header comments (`summary`, `args`, `examples`, `hidden`, `requires-sudo`), and `omarchy commands --json` lists them. The menu is scriptable too (`omarchy menu summon style.theme`). |
| Updates | `omarchy update` takes a snapshot, upgrades packages, runs pending **migrations**, then fires `post-update` hooks. A guard blocks a direct `pacman -Syu`. There are four channels (stable, which lags the Arch mirror by a month; rc; edge; dev, which is a git checkout). |
| Migrations | Timestamped `migrations/<unix-ts>.sh` files, run in order with `bash -euo pipefail` and recorded per user in `~/.local/state/omarchy/migrations/`. They must be idempotent, and a failure stops the queue. They never run silently: a login notifier opens a terminal instead. |
| Recovery | Btrfs root snapshots, bootable from the Limine menu. They cover the root filesystem only, not `/home`. `omarchy reinstall [configs]` is the reset of last resort. |
| Extension | Event hooks under `~/.config/omarchy/hooks/<event>.d/` (`post-boot`, `post-update`, `theme-set`, `battery-low`, …). Menu entries can be added in JSONC. |
| Themes | One palette (`colors.toml`) rendered through templates into every app's config. |
| AI | Lazy mise stubs for 13 cloud coding-agent CLIs, plus a default-agent launcher. Agents launched by Omarchy run **unattended, in auto-approve modes**. An agents panel shows each subscription's usage and limits. An Omarchy skill is symlinked into every harness's skill directory, with the advice "plan mode first, be ready to roll back". Crashes from systemd-coredump go to the agent with a diagnose-crash skill. Local LLMs mean LM Studio or Ollama. Dictation uses Voxtype, holding F9 to type into the focused input. |
| Its own testing | Shell tests, plus a graphical acceptance suite in a disposable VM that saves a `success-<step>.png` per step. The rule is that visual changes must be inspected, not just produced. The docs warn that `wtype` does not prove a global compositor binding works. |

## 2. Where it diverges from TANSTAAFLLM

Omarchy and TANSTAAFLLM agree on several things: keyboard-first and terminal-first work, inspectable text configuration, agents as normal users of the system, and recovery as a feature. They disagree on the price of resources and the shape of authority.

| Axis | Omarchy | TANSTAAFLLM on Luna |
| --- | --- | --- |
| Resource assumption | Abundance: a modern laptop, a GPU-accelerated compositor, Chromium web apps, Docker, a Windows VM. | Scarcity: RK3326, about 1 GiB shared RAM, 720×720 panel. The ArchR card has **no GPU driver** and uses software compositing (Wyoh 4.7). |
| Where intelligence runs | Cloud agents by default, chosen by subscription. Local models through generic runners. | The least sufficient mechanism first. Local where it fits. Frontier models are a visible, deliberate escalation. |
| Agent authority | The agent edits the OS directly, unattended. Safety comes from snapshots and `reinstall`. | Finite, advertised actions (Wyoh). Proposal before acceptance (Mycroft). Ordinary developer permissions with review (Mannie). Safety comes **before** the action, not only through rollback. |
| Cost visibility | Subscription quotas (percentage of the 5-hour and weekly limits). | All costs: memory, CPU, heat, battery, latency, money, privacy. |
| Input model | Keyboard with `Super`. A mouse is optional. | Controller first. A USB keyboard is optional. Voice is a composition path. |
| Session shell | One rich Qt Quick process for every surface. | Unmodified Sway, `swaybar`, `foot`, `bemenu`. Wyoh measured a GTK editor at about 3× `foot`+`nano` and avoids GTK. |

## 3. Ideas, classified for Luna

**Owner** names the workline that would decide; this note opens no work there. **Fit** is judged against the R36 Ultra constraints above. No footprint figure is claimed for Omarchy components, because none was measured.

### Adopt or adapt

| # | Omarchy idea | Luna form | Why it fits the R36 | Owner |
| --- | --- | --- | --- | --- |
| A1 | **One self-describing command surface.** Header metadata on each script, `--json` listing, `requires-sudo` flag. | A single `luna` command whose scripts declare summary, args, **risk/confirmation** and **resource cost**. One catalogue generates the CLI help, the controller menu, and the Wyoh/MCP tool list. | Costs nothing at rest (scripts, no daemon). Puts "finite advertised actions" and "costs visible" into one artifact that Mike, Adam and the person all read. Closest match to Wyoh's HIOM action catalogue. | Wyoh (catalogue), Mike (consumer) |
| A2 | **Addressable menu tree** with dotted ids that can be summoned directly (`menu summon style.theme`) and extended in a user file. | The controller launcher is the same tree. Every node has a stable id, so "Adam, open network settings" resolves to `menu.system.network` instead of pixel navigation. | A d-pad needs a menu anyway. Stable ids are what HIOM already asks for. `bemenu`/`wmenu` can render it at almost no cost. | Wyoh |
| A3 | **Ordered, idempotent, never-silent migrations** with per-user markers, where a failure stops the queue. | Turn Luna's hand-run card scripts (textmode boot, Wi-Fi overlay, `/storage` drop-ins, keymap, `/home` mount) into numbered idempotent migrations with a marker directory. A fresh card can then be brought to the known state, and drift becomes visible. | Text files and markers. Directly answers the reproducibility problem raised by the many one-off ArchR fixes, and is relevant input to the pending **Luna Step 7** base-system decision. | Luna |
| A4 | **Defaults vs overrides layering**, with `refresh-config` taking automatic backups and `reinstall configs` as the reset. | Project-owned defaults in a read-only location, the person's overrides in `~/.config`, and a reset command. Luna already uses `/storage/.config/system.d` drop-ins on the same principle. | Free at runtime. It makes "Seal" (known-good state) concrete for configuration. | Luna (Step 7) |
| A5 | **Snapshot before every update** + an update guard that blocks raw `pacman -Syu`. | The R36 has no Limine or Btrfs snapshots; it boots through U-Boot `extlinux`. Options are (a) a fallback `extlinux` entry such as "Free Fall", (b) a pre-update root `tar`/`zstd` checkpoint to `/storage`, (c) the guard alone (a pacman hook or wrapper). Full-card zstd checkpoints already exist on the desktop side. | Recovery is a stated principle. An SD card is slow to snapshot, so evidence on cost is needed before choosing. | Luna (research) |
| A6 | **Event hook directories** (`post-boot`, `post-update`, `battery-low`). | `battery-low`, `thermal-high` and `memory-low` as **Pressure** events that run small scripts. They are fired by an existing cheap mechanism (udev/systemd path or timer), not a new resident monitor. | Gives "Pressure" an operational meaning with no new daemon. | Wyoh (events), Mike (reactions) |
| A7 | **On-demand notices** (a hotkey shows date, battery or weather once) instead of resident widgets. | A controller combo shows a one-shot Pressure/status card. | Avoids periodic redraws, which matter under software compositing: Wyoh measured about 80% of a core during full redraws on Luna. | Wyoh |
| A8 | **Agents panel showing usage and limits** for each subscription. | A short, plain-text cost line from Adam: last escalation, tokens and money, and local CPU/RAM spent. The desktop or the remote side computes it, and Luna only displays it. | The literal TANSTAAFLLM principle. Omarchy limits it to quotas; Luna should cover all costs. | Adam / Wyoh |
| A9 | **A repository skill for the system's own agent**, symlinked into every harness and paired with "plan first, roll back if needed". | A `luna` skill (or `AGENTS.md` section) for Mannie that documents the A1 catalogue, the migrations (A3) and the reset path. It is used from the desktop over SSH, where Mannie already works. | Costs nothing on Luna. Makes desktop-driven agent work on the card repeatable. | Mannie (no workline yet; Professor Step 3 candidate) |
| A10 | **Crash → coredump → agent with a diagnose skill**, and "mute hides, it does not fix". | Keep core dumps small or off on Luna. Pull them to the desktop over SSH for Mannie to analyse. Keep the honest wording. | Analysis stays off the 1 GiB device. The wording matches "degrade clearly". | Mannie / Luna |
| A11 | **Push-to-talk dictation into the focused input** (hold F9; Voxtype's English base model is 150 MB according to its docs). | Confirms Mycroft's composition UX shape: hold a controller button, record, then show a reviewable proposal. Unlike Omarchy, Mycroft does not type straight into the target. | Mycroft is already on-demand rather than resident, and Omarchy shows the same interaction is usable day to day. Voxtype could be a desk-research candidate only if Mycroft reopens its shortlist. | Mycroft |
| A12 | **Per-step screenshot acceptance** that is inspected, with the warning that `wtype` cannot prove global bindings. | Already Wyoh's practice. The Luna run uses a kernel **uinput** keyboard, which does reach compositor bindings. Record this as a confirmed difference in our favour. | Validates current practice; no change needed. | Wyoh (note only) |

### Lower priority

- **Release channels** (stable, which lags upstream by a month; edge; dev as a git checkout). Luna's "dev channel" is effectively the desktop deploy over SSH (Catapult). A lagging stable channel only matters once Luna has users other than its developer.
- **One palette rendered into every app's config at theme-set time.** Costs nothing at runtime. It could give Adam's states (completed, proposed, blocked, degraded) consistent colours across `foot`, `swaybar` and `bemenu`. This is cosmetic, so it waits until the state contract exists.

### Reject for Luna

| Omarchy element | Reason |
| --- | --- |
| Hyprland and its animations | Wyoh's Sway v0 is ratified. ArchR has no GPU driver, and animated compositing on the CPU spends battery and heat on decoration. |
| A single Qt Quick shell for every surface | A resident Qt Quick process under software rendering, within about 1 GiB, is the opposite of Wyoh's measured preference for small separate tools. Unmeasured, so rejected on principle; revisit only with Luna measurements. |
| Unattended, auto-approving agents as the default launch mode | Conflicts with principle 5 (human agency) and with the propose-then-accept contracts. Rollback afterwards does not replace review beforehand. |
| Chromium web apps, Docker, a Windows VM, Steam, LM Studio/Ollama, multi-account quota autoswitching | Out of budget or out of scope. Generic local-LLM runners also contradict "least sufficient intelligence". |
| `Super`-key-only navigation | Luna is controller-first. Only the menu-as-hub idea (A2) carries over. |
| Disk-encryption unlock themes, fwupd firmware | Not applicable to the R36 boot chain. |

## 4. Recommended for discussion

1. **A1 + A2 together:** one action catalogue that drives the CLI, the controller menu and the MCP tools. This is the highest-value idea. It is cheap and strengthens Wyoh's existing contract.
2. **A3 + A4 as inputs to Luna Step 7:** whichever base is chosen, card state should be reproducible from ordered migrations over a defaults/overrides split, not from a history of hand-run scripts.
3. **A6 + A7:** Pressure as events and one-shot notices, never as resident polling widgets.
4. **A8:** Adam's cost line should go beyond Omarchy's subscription-quota view.
5. Explicitly **do not** copy unattended agent authority (section 3, rejected).

## 5. Limits of this analysis

- Read from public documentation only, on 2026-10-05. Omarchy changes quickly (version 4.0.x on the `quattro` branch).
- No Omarchy component was measured. Footprint statements are about Luna's recorded evidence, not about Omarchy.
- Ownership in section 3 is a proposal. Each workline decides under its own plan and green light.
