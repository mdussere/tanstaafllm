Feature: Claude Code on luna-pi (Mannie plan Step 2)
  First install and start figures for Claude Code on the arm64 reference board.
  Executed by test/mannie/test_luna_pi_claude.py (marker: live; needs
  MANNIE_LUNA_PI_LIVE=1). luna-pi is reserved for Mannie. Evidence goes to
  results/mannie/luna-pi-claude/<timestamp>/. Intent: worklines/mannie/docs/0101_01.

  Background:
    Given luna-pi answers on "ssh luna-pi" as the user michael, through one multiplexed connection
    And nothing outside michael's home directory is changed, and sudo is never used
    And no saved output contains a credential-like string

  Scenario: Step 2.1 — read-only preflight
    When Mannie reads luna-pi's architecture, glibc, free memory, free space and any existing Claude Code
    Then luna-pi is aarch64 with glibc 2.26 or newer and room for about 0.5 GiB
    And the full preflight output is saved

  Scenario: Step 2.1 — install the pinned, verified version
    Given the release manifest of 2.1.287 has a good signature from Anthropic's release key
    And the linux-arm64 binary matches the manifest's SHA-256 on the desk
    When the binary is copied to luna-pi, checked again there, and runs its own "install 2.1.287"
    Then "claude --version" on luna-pi prints 2.1.287 and the installed binary matches the manifest
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
