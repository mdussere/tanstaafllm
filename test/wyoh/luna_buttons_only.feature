@live
Feature: Luna is operated with only its buttons and the input zone (Wyoh Step 5)

  Executed by `test_luna_buttons_only.py`. The person is simulated through MCP:
  the development tools create a virtual gamepad (the device's 17 buttons and
  4 axes) and a virtual keyboard (the USB keyboard that types into the input
  zone, until voice replaces it). Only gamepad buttons, the right stick (pointer), and
  typing inside the input zone are used; no Sway command operates the session
  on the person's behalf. MCP observes Sway, reads the gamepad daemon's
  status, and saves a settled screenshot of DSI-1 after each step under
  `results/wyoh/luna-buttons-only/<timestamp>/`; the agent inspects every one.

  Background:
    Given `wyoh-sway.service` and `wyoh-gamepad.service` run on Luna
    And the daemon has attached both the real and the virtual gamepad
    And the session has no application window

  Scenario: A day's work with the buttons
    # Launch from the menu with the D-pad
    When the person presses Start
    Then the application menu is shown
    When the person presses Down eight times and A
    Then a terminal opens

    # Input zone: prepare a command, send it, run it
    When the person presses L1
    Then the input zone is shown
    When the person types a marker command (`touch /tmp/…`) on the keyboard
    Then the zone shows the text
    When the person presses L2
    Then the text appears once in the terminal and the zone is gone
    When the person presses A
    Then the command runs and the marker file exists

    # Input zone: discard
    When the person presses L1, types a second command, and presses B
    Then nothing is delivered and the second marker file does not exist

    # Second window, focus, fullscreen, pointer
    When the person presses Start, Down three times, and A
    Then the image viewer opens above the terminal (layout policy: the second window goes on top)
    When the person presses Select
    Then the focus moves to the other window
    When the person holds FN and presses A, twice
    Then the focused window goes fullscreen and back
    When the person pushes the right stick to the top-left corner, then into the image viewer (top half), and clicks R3
    Then the image viewer has the focus
    When the person presses Select
    Then the terminal has the focus again

    # Quick linear navigation keys reach the application
    When the person sends `cat -A` through the zone and presses A
    And the person presses R1, R2, and A
    Then the terminal shows `^I` and `^[[Z` for Tab and Shift+Tab

    # Recovery
    When the person presses L1 and holds FN and Start for more than two seconds
    Then the zone is discarded and the daemon records one recovery

    # Close everything with FN+B
    When the person holds FN and presses B until no window remains
    Then the desktop is empty
