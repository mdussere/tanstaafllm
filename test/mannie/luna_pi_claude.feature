Feature: Claude Code on luna-pi and Luna (Mannie plan Step 2)
  Install, start and request figures for Claude Code on the arm64 reference board
  (Step 2.1–2.3) and on Luna itself (Step 2.4). Executed by
  test/mannie/test_luna_pi_claude.py (marker: live). MANNIE_LUNA_PI_LIVE=1 targets
  luna-pi; MANNIE_LUNA_LIVE=1 targets Luna, held through worklines/luna-access.md.
  Evidence goes to results/mannie/<host>-claude/<timestamp>/. Intent:
  worklines/mannie/docs/0101_01.

  Background:
    Given the target answers on "ssh luna-pi" (user michael) or "ssh luna" (root, HOME=/storage), through one multiplexed connection
    And nothing outside the target user's home is changed, and sudo is never used
    And on Luna everything but Claude Code's own ~/.claude lands under /storage/.local
    And the installer's temporary files stay on the card, not in Luna's RAM-backed /tmp
    And no saved output contains a credential-like string

  Scenario: Step 2.1 — read-only preflight
    When Mannie reads the target's architecture, glibc, free memory, free space and any existing Claude Code
    Then the target is aarch64 with glibc 2.26 or newer and room for about 0.5 GiB
    And the full preflight output is saved

  Scenario: Step 2.1 — install the pinned, verified version
    Given the release manifest of 2.1.287 has a good signature from Anthropic's release key
    And the linux-arm64 binary matches the manifest's SHA-256 on the desk
    When the binary is copied to the target, checked again there, and runs its own "install 2.1.287"
    Then "claude --version" on the target prints 2.1.287 and the installed binary matches the manifest
    And auto-update is off in ~/.claude/settings.json
    And the install's wall time, peak RSS and the disk use are saved

  Scenario: Step 2.3 — start figures without a session
    When "claude --version" and "claude --help" each run three times
    Then each run exits 0, and its wall time, CPU time and peak RSS are saved
    And the output of "claude doctor" is saved

  Scenario: Step 2.3 — interactive start
    When "claude" starts in a 100×30 pseudo-terminal in a scratch directory and idles for 20 s
    Then the time to first output, and the peak and settled RSS and PSS of its process tree, are saved
    And what Claude Code printed is not saved, only its size
    And whether the user had logged in is recorded

  Scenario: Step 2.2 — one model request after the user's login
    Given the user has logged in with /login in their own SSH terminal
    And ~/.claude/.credentials.json exists with mode 0600, and is never read by the test
    When "claude -p" asks for the single word "pong" with JSON output
    Then the reply contains "pong", and its wall time, peak RSS and token usage are saved

  Scenario: Step 2.4 — repeated requests
    Given the user has logged in on the target
    When "claude -p" asks for "pong" three more times
    Then each reply contains "pong", and the wall time, peak RSS, lowest MemAvailable, swap use and tokens of each are saved

  Scenario: Step 2.4 — one request that uses a tool
    Given the user has logged in on the target
    And the scratch directory holds note.txt with a code word
    When "claude -p" is asked for the code word, with only the Read tool allowed
    Then the reply contains the code word, and the same figures are saved
