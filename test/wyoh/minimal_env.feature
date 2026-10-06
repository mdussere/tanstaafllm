@live
Feature: The Wyoh luna-pi session is usable and operable through MCP (Step 3.7)

  Executed by `test_minimal_env.py`. Every action goes through a real MCP
  client attached to `wyoh-sway-vnc.service` with `--shared-vnc-session`.
  After each step the test saves an MCP server-side screenshot and an
  independent VNC frame under `results/wyoh/minimal-env/<timestamp>/`.
  The agent inspects those images before any success claim; the pixel
  assertions below are a guard, not a replacement for looking.

  Background:
    Given `wyoh-sway-vnc.service` runs the Step 3.7 config on luna-pi
    And `foot`, `wmenu-run`, and `wtype` are installed on luna-pi from Debian 13
    And the session has no application window
    And a VNC client is connected through a temporary SSH tunnel
    And the VNC client's first, placeholder frame has been discarded

  Scenario: Open, type into, rearrange, and close applications
    When MCP runs `exec foot` and observes the `window` `new` event
    And the terminal's rectangle no longer shows the background
    Then both screenshots show the terminal under the swaybar

    When MCP focuses that terminal by `con_id` and runs `exec wtype` with a marker command and Return
    Then the marker file appears on luna-pi with the expected content
    And both screenshots show the typed command in the terminal

    When MCP switches to workspace 2
    And a person at the VNC viewer presses Alt+d, types `mousepad`, and presses Return
    # Not `wtype`: wmenu 0.1.9 aborts on the keymap change a transient
    # virtual keyboard causes under Sway 1.10.1 (see the Step 3.7 result).
    Then a `mousepad` window appears on workspace 2 and renders
    And both screenshots show the editor alone on workspace 2

    When MCP moves the editor by `con_id` to workspace 1 and focuses workspace 1
    Then the tree shows two side-by-side windows on workspace 1
    And both screenshots show the terminal and the editor split

    When MCP makes the editor fullscreen by `con_id`
    Then the editor covers the output
    And both screenshots show only the editor

    When MCP leaves fullscreen
    And a person at the VNC viewer presses Alt+Enter
    Then a new terminal appears and renders
    And both screenshots show it
    When that person presses Alt+Shift+q
    Then that terminal is closed

    When MCP closes the remaining windows by `con_id`
    Then the tree has no application window
    And the marker file is removed
    And both screenshots show the empty desktop with the swaybar
