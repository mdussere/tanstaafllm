Feature: The Slate and its on-screen keyboard on Luna (Wyoh Step 6)
  The person prepares several lines of text in the Slate with the gamepad,
  the on-screen keyboard (two selections: green on the left stick and L3, red
  on the right stick and R3), and a
  USB keyboard stand-in, then sends it once into the window that had focus
  or clears it. Controls (user, 2026-10-09, 6.9): L1 show/hide (text kept),
  FN+A send then clear and hide, FN+X clear, L2 dictation (Step 12),
  A Return, B Backspace, X Delete, Y Shift, R1/R2 next/previous word, the
  whole cross selects the word, twice the line. Executed by
  test_luna_slate.py through MCP development tools only; every step saves a
  settled screenshot of DSI-1.

  Background:
    Given the Wyoh session, the gamepad daemon and the layout service are running on Luna
    And the person has opened a terminal from the Start menu with the buttons

  Scenario: Open the Slate with its keyboard and look
    When the person presses L1
    Then a floating "wyoh-slate" window has the focus at the top of the panel
    And it is black with white text and a white 2 px border
    And the on-screen keyboard fills the bottom 240 px with black keys outlined in white

  Scenario: Two lines are sent once
    When the person types "echo first >> M", presses A, and types "echo second >> M"
    And presses FN+A
    Then the Slate and the keyboard disappear and the terminal's border is blue again
    And after A in the terminal, M holds "first" then "second", each once

  Scenario: L1 hides the Slate and keeps its text; FN+X clears it
    When the person opens the Slate, types two lines writing to D, and presses L1
    Then the Slate and the keyboard disappear and the daemon reports "hidden"
    When the person presses L1 again
    Then the same Slate is shown with its two lines
    When the person presses FN+X and then L1
    Then the Slate is empty and hidden, nothing reached the terminal, and D does not exist

  Scenario: The whole cross selects a word, B deletes it
    When the person types "echo hello brave world > W" and moves left into "brave"
    And presses the whole cross
    Then "brave" is shown selected
    When the person presses B and sends the Slate
    Then W holds "hello world"

  Scenario: Y with the arrows selects, R1 and R2 move by words
    When the person types "echo keep drop", holds Y and presses left four times, releases Y, and presses B
    And types "> S" and sends the Slate
    Then S holds "keep"
    When the person types "echo c", presses R2, types "b", presses R1, types "d" and " > R"
    And sends the Slate
    Then R holds "bcd"

  Scenario: The whole cross twice selects the line; the on-screen keyboard types
    When the person types "junk line" and presses the whole cross twice
    Then the line is shown selected
    When the person presses X
    And types "echo "
    Then the keyboard shows a pastel green selection on "f" and a pastel red one on "j"
    When the person steers green with the left stick to "a" and presses L3 twice
    And steers red with the right stick to Backspace, presses R3, steers red back to "é", presses R3
    And types " > K"
    And sends the Slate
    Then K holds "aé"
    And the gamepad status never contains the text, only its length
