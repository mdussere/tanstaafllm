Feature: Dictation into the Slate on Luna (Wyoh Step 12)
  L2 in the Slate starts Mycroft's dictation provider; its provisional text is
  shown underlined at the cursor, and its final text is inserted when L2 is
  pressed again. Executed by test_luna_slate_dictation.py with Mycroft's
  --fake mode (no model, no microphone); the real voice test is the user's.
  The test switches the daemon to the fake command and restores the real one.

  Scenario: Dictated words go into the Slate and are sent with the rest
    Given the daemon's dictation command is Mycroft's fake mode saying "bonjour luna"
    And a terminal is open and the Slate is shown on it with "echo " typed
    When the person presses L2
    Then the Slate's hint reads "dictation: loading…" then "dictation: listening"
    And the words appear underlined at the cursor
    When the person presses L2 again
    Then "bonjour luna" is inserted after "echo " and the hint is back to normal
    When the person types " > F" and presses FN+A
    Then the terminal writes "bonjour luna" into F
