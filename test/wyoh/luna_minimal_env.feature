@live
Feature: Luna's real panel reproduces the luna-pi Step 3.7 run (Step 4.7)

  Executed by `test_luna_minimal_env.py`; mirrors luna-pi run
  `results/wyoh/minimal-env/20261003T232433Z` step for step. MCP actions are
  MCP tool calls on `wyoh-sway.service` (ArchR's Sway 1.11 on DSI-1). The
  person at the keyboard is a kernel uinput keyboard (`uinput_keyboard.py`),
  handled by Sway like the USB keyboard with the French layout. Evidence is
  the MCP screenshot of DSI-1 for each step, taken on a settled frame, under
  `results/wyoh/luna-minimal-env/<timestamp>/`; the agent inspects every one.
  There is no VNC on Luna. The editor is `vim` in `foot`, not a GTK app
  (ArchR's `nano` 8.5 does not follow terminal resizes).

  Background:
    Given `wyoh-sway.service` runs on Luna with the Step 4.7 config
    And the MCP 2.2.0 venv, `wtype`, and `vim` are available
    And Sway lists the uinput keyboard among its inputs
    And the session has no application window

  Scenario: The nine steps of the luna-pi run, on the physical display
    # 00
    Then the screenshot shows the bar and the empty workspace 1

    # 01
    When MCP runs `exec foot` and the terminal has drawn
    Then the screenshot shows the terminal under the bar

    # 02
    When MCP focuses it by `con_id` and types a marker command with `wtype`
    Then the marker file appears on Luna with the expected content
    And the screenshot shows the typed command

    # 03a / 03b
    When MCP switches to workspace 2
    And the person presses Alt+d
    Then the screenshot shows the launcher
    When the person types `foot -a wyoh-editor vim` and presses Return
    Then a `wyoh-editor` window appears alone on workspace 2

    # 04
    When MCP moves the editor by `con_id` to workspace 1
    Then the screenshot shows the terminal and the editor side by side

    # 05
    When MCP makes the editor fullscreen by `con_id`
    Then the screenshot shows only the editor, without the bar

    # 06
    When MCP leaves fullscreen
    And the person presses Alt+Enter
    Then a third terminal appears beside the others
    When the person presses Alt+Shift+q
    Then that terminal is closed

    # 07
    When MCP closes the remaining windows by `con_id`
    Then the tree has no application window
    And the marker file is removed
    And the screenshot shows the empty desktop with the bar
