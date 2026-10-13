# Mannie on Luna — intent (Steps 1–2)

**Status:** draft, awaiting the user's approval (Step 1 acceptance)<br>
**Date:** 2026-10-11<br>
**Question answered:** What will Mannie install, where, and how, what will be measured, and when does the work stop?

## 1. Desk research results (Step 1)

### 1.1 Build, runtime and size

Official sources: [Advanced setup](https://code.claude.com/docs/en/setup), the official installer `https://claude.ai/install.sh` (read, not run), and the signed release manifests under `https://downloads.claude.ai/claude-code-releases/`.

- **Install method.** The recommended route is the native installer: one self-contained binary. The binary goes in `~/.local/share/claude/versions/<version>`, with a launcher at `~/.local/bin/claude`. The npm package installs the same binary, and Debian has a signed apt repository, but that needs root. Mannie uses the native binary.
- **No Node.js at runtime.** The documentation says the npm package "installs the same native binary … The installed `claude` binary does not itself invoke Node."
- **Platforms.** `linux-arm64` (glibc) and `linux-arm64-musl` are published. Luna (ArchR) and `luna-pi` (Debian) are both glibc, so `linux-arm64` applies.
- **glibc.** Mannie downloaded the arm64 binary of 2.1.287 to the desk and inspected it. Its highest versioned symbol is **`GLIBC_2.26`**, and it links only `libc`, `libm`, `libdl`, `libpthread`, `librt` and the aarch64 loader. Luna has glibc 2.40 and `luna-pi` has 2.41, so both qualify. ripgrep is bundled.
- **Size.** The `linux-arm64` binary of 2.1.287 is **243,720,184 bytes (≈232 MiB)**. The installer keeps up to three versions on disk, so plan for about 0.7 GiB with auto-update on and about 0.25 GiB with it off.
- **Integrity.** The 2.1.287 manifest has a **good GPG signature** from "Anthropic Claude Code Release Signing" (fingerprint `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`, as published). The downloaded binary's SHA-256 matches the manifest: `e4daf793d1e74fb0d9874dd09e98690bbfd7be515f78a87fd05b9e2b4bb33b03`.
- **Versions on 2026-10-11:** `stable` = 2.1.287 (built 2026-10-01), `latest` = 2.1.296.

### 1.2 Login with the Pro subscription, without a browser on the device

Official source: [Authentication](https://code.claude.com/docs/en/authentication).

- **`/login` over SSH (recommended).** Run `claude` on the device and choose the subscription login. Claude Code prints a URL. You open it in a browser on any other machine, and if the browser shows a code, you paste it at the `Paste code here if prompted` prompt. The documentation names SSH sessions as a case for this. The credential is stored in `~/.claude/.credentials.json`, mode `0600`, and renews itself. `/logout` removes it.
- **`claude setup-token` (alternative).** This prints a one-year OAuth token, which is then set as `CLAUDE_CODE_OAUTH_TOKEN`. The token can only make model requests, and Claude Code does not save it, so it would sit in a shell profile or a file. Mannie does not recommend it here: the token would pass through a clipboard, and possibly through an agent's transcript.
- **Either way, the user acts.** The browser approval is the user's step, done in their own SSH terminal. Mannie never sees, copies or logs the credential.

### 1.3 Expected memory

- **Documented minimum: "4 GB+ RAM".** Luna has 983 MiB, so it is **below the documented requirement**. Running there is outside what Anthropic supports, and the result must be read that way.
- **The installer itself** says: "Claude Code needs roughly 512MB of free memory to install." Luna leaves about 535–795 MiB available under Sway, so installing on Luna may only just fit.
- **Desk-host hint (x86-64, version 2.1.119, not the target).** `claude --version` peaked at about 208 MiB RSS and `claude --help` at about 260 MiB. An interactive session will be larger. The real arm64 figures come from `luna-pi` in Step 2.
- **What this means.** A first estimate puts an idle interactive session at 250–400 MiB. That would not fit alongside Mycroft's ~250 MiB provider in Luna's budget. Step 2 measures the real figure; nothing is assumed.

## 2. What Step 2 will do on `luna-pi`

`luna-pi` is a Raspberry Pi 4 with about 8 GiB of RAM, running Debian 13 trixie (glibc 2.41), with 6.2 GB free. As of 2026-10-11, Claude Code is not installed there. It is reserved for Mannie (user, 2026-10-11). Its figures are an arm64 reference, **not evidence that Claude Code fits on Luna**.

- **Where:** only the user `michael`'s home: `~/.local/share/claude/`, `~/.local/bin/claude` and `~/.claude/`. No `sudo`, no apt repository, no system change.
- **Which version:** pinned at **2.1.287** (stable). The test streams the GPG-verified, checksum-matched binary from the desk to the Pi, checks the SHA-256 again there, and runs the binary's own `install 2.1.287`, which is the last step of the official installer. Auto-update is turned off with `DISABLE_AUTOUPDATER=1` in `~/.claude/settings.json`, so the measured version doesn't change mid-series.
- **Login:** the user runs `/login` in their own SSH terminal (§1.2). Until then, the start measurements use the not-logged-in first screen.

### What is measured

| Measurement | How |
|---|---|
| Version and checksum | `claude --version`, SHA-256 of the installed binary |
| Disk use | `du` on `~/.local/share/claude` and `~/.claude` |
| `--version` and `--help` | wall time, peak RSS and CPU time, measured with `/usr/bin/time -v`, 3 runs each |
| Installation | wall time and peak RSS of `claude install` |
| `claude doctor` | full output saved |
| Interactive start | `claude` started in a pseudo-terminal: time to first output, then peak and settled RSS of the whole process tree over 20 s idle, sampled from `/proc`. It runs once before login and once after login. |
| One request, after login (only if the user has logged in) | `claude -p "Reply with the single word: pong" --output-format json`: wall time, peak RSS, and the reported token usage. This is the only model request in Step 2. |

### Tests and evidence

- `test/mannie/luna_pi_claude.feature` is the readable contract, run by `test/mannie/test_luna_pi_claude.py`.
- Every test is `@pytest.mark.live` and skipped unless `MANNIE_LUNA_PI_LIVE=1`. The default suite is unchanged.
- A small probe script, `test/mannie/claude_probe.py`, runs on the Pi with the system `python3` and samples memory from `/proc`.
- Evidence goes to `results/mannie/luna-pi-claude/<timestamp>/`: full command output and the probe's JSON.
- **No credential is ever written there.** The tests never read `~/.claude/.credentials.json`; they only check that it exists and has mode `0600`. Saved output is scanned for `sk-ant-` and similar token patterns, and the test fails if any is found.

### Cost record

The subscription has a flat rate, so Step 2 records requests, input and output tokens, and wall time, from the JSON output of `-p`. Step 2 sends at most **one** short model request.

## 3. Stop conditions

Mannie stops, records the state in the plan, and asks the user if:

- the binary's checksum or the manifest signature does not match;
- installing needs `sudo` or any change outside the home directory;
- login would require the credential to pass through Mannie, a log, or the repository;
- any saved output contains a credential-like string (the file is deleted before anything is committed, and the user is told);
- the Pi misbehaves (OOM, SSH lost). That is a finding, not something to work around.

## 4. Later (not part of this intent)

- **2.4 on Luna.** Repeat the measurements under `/storage/.local/`, once Luna is free and Professor gives a slot. Because 983 MiB is below the documented 4 GB, first check that the installer's ~512 MiB margin is available.
- **Proposal: a 1 GiB rehearsal on the Pi.** Run the same probe under a memory limit, for example `systemd-run --user -p MemoryMax=600M`, to see how Claude Code behaves under Luna's budget before taking a Luna slot. This would be a new sub-step, and it needs a green light.
