@live
Feature: At most four tiles per workspace, in a fixed order (user requirement 2026-10-08)

  Executed by `test_luna_layout.py`. The person (MCP virtual gamepad) opens
  terminals from the menu with the buttons; `wyoh-layout.service` places them.
  MCP reads the window geometry and saves a settled screenshot per step under
  `results/wyoh/luna-layout/<timestamp>/`; the agent inspects every one.

  Background:
    Given `wyoh-sway.service`, `wyoh-gamepad.service`, and `wyoh-layout.service` run on Luna
    And the workspace has no window

  Scenario: Fill the screen, then refuse a fifth tile
    When the person opens a terminal from the menu
    Then it fills the screen
    When the person opens a second terminal
    Then the screen is split vertically with the new terminal on top
    When the person opens a third terminal
    Then the top half is split and the new terminal is top-right
    When the person opens a fourth terminal
    Then the bottom half is split and the new terminal is bottom-right
    When the person opens a fifth terminal
    Then it is closed at once, four tiles remain, and "Too many tiles" pops up
    When the person presses B
    Then the pop-up is gone
    When the person holds FN and presses B until no window remains
    Then the desktop is empty
