Feature: Graphical applications from Luna's menu (Wyoh Step 9.11)
  The person launches the Wyoh calculator and Files (Commander) from the
  Start menu and uses them with the gamepad only. Both are SDL2 apps drawn
  by the Mali GPU; they display because the session sets
  MALI_WAYLAND_DMABUF_PROTOCOL=1 (9.1b). Executed by test_luna_apps.py
  through MCP development tools; every step saves a settled screenshot.

  Background:
    Given the Wyoh session, the gamepad daemon and the layout service are running on Luna
    And the workspace is empty

  Scenario: The calculator computes 3 × 7 with the cross and A
    When the person opens the Start menu and filters it with "calc", then presses A
    Then a floating "wyoh-calculator" window has the focus, drawn (not transparent)
    When the person presses A on 3, moves to × and presses A, moves to 7 and presses A, moves to = and presses A
    Then the display shows 21
    When the person presses FN+B
    Then the calculator is closed

  Scenario: Files opens full screen and its selection moves
    When the person opens the Start menu and filters it with "files", then presses A
    Then a full-screen "commander" window has the focus, drawn
    When the person presses the cross down twice
    Then the highlighted row has moved down
    When the person presses FN+B
    Then Files is closed and the workspace is empty

  Scenario: Wolfenstein 3D from the menu to Floor 1, played with the gamepad (remapped virtual joystick, 9.8b)
    When the person opens the Start menu and filters it with "wolf", then presses A
    Then a full-screen "ecwolf" window has the focus
    When the person presses A through the title, the main menu, the episode and the difficulty
    Then Floor 1 is shown with its blue status bar
    When the person pushes the left stick forward, presses R1 to fire and L1 to open
    Then the view has changed
    When the person presses FN+B
    Then Wolfenstein 3D is closed and the workspace is empty

  Scenario: Mannie (Claude Code) and the Terminal, with the larger terminal font
    When the person opens the Start menu and filters it with "mannie", then presses A
    Then a "mannie" window has the focus and shows Claude Code in foot at 12 pt (50 % above foot's 8 pt)
    When the person presses FN+B
    Then Mannie is closed
    When the person opens the Start menu and filters it with "terminal", then presses A
    Then a "foot" window has the focus, with the same font
    When the person presses FN+B
    Then the workspace is empty

  Scenario: The Wi-Fi panel lists networks and cancels a new password
    When the person opens the Start menu and filters it with "wi-fi", then presses A
    Then after a rescan the networks are listed, the connected one first with a check mark
    When the person moves down to a new network and presses A
    Then a "wyoh-wifi" window asks for its password
    When the person types a password
    Then it is shown masked
    When the person presses B
    Then the window closes and no profile is written for that network
