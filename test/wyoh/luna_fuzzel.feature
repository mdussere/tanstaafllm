@live
Feature: The fuzzel application menu on Luna's real panel (Step 4.8)

  Executed by `test_luna_fuzzel.py`. A person (kernel uinput keyboard and
  mouse, French layout) drives fuzzel as a user would; MCP observes Sway,
  opens a Wyoh-defined menu in fuzzel's dmenu mode, and cleans up. Each step
  saves the MCP screenshot of DSI-1 on a settled frame under
  `results/wyoh/luna-fuzzel/<timestamp>/`; the agent inspects every one.
  fuzzel is Debian's 1.12 (no GTK), with a Windows 3.x palette and a Papirus
  icon subset; the Mali GPU driver is loaded by the unit.

  Background:
    Given `wyoh-sway.service` runs on Luna with the Step 4.8 config and the Mali driver
    And the session has no application window

  Scenario: Open, filter, navigate, cancel, and launch by keyboard and mouse
    When the person presses Alt+d
    Then the menu shows entries with icons and a navy selection
    When the person types "ed"
    Then the list is filtered
    When the person clears the filter and presses Down three times
    Then the selection is three rows lower
    When the person presses Escape
    Then the menu closes and nothing was launched

    When the person opens the menu, types "term", and presses Return
    Then a terminal window appears
    When the person opens the menu, types "image", and clicks the selected row
    Then the image viewer appears with its picture
    When the person opens the menu, presses Down seven times and Up seven times
    Then the selection returns to the first row
    When the person presses Return
    Then the calculator appears

  Scenario: A Wyoh-defined menu through fuzzel's dmenu mode
    When MCP runs fuzzel --dmenu with "Cascade windows", "Tile windows", "Close all"
    Then the menu shows the three choices
    When the person presses Down and Return
    Then "Tile windows" is written to the choice file
    And the menu closes

  Scenario: Clean up
    When MCP closes every window by `con_id`
    Then the screenshot shows the empty desktop with the bar
