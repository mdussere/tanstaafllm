Feature: Dictation into the Slate on Luna (Wyoh Step 12)
  L2 in the Slate starts Mycroft's dictation provider; its provisional text is
  shown underlined at the cursor, and its final text is inserted when L2 is
  pressed again. Executed by test_luna_slate_dictation.py with Mycroft's
  --fake mode in resident mode (no model, no microphone; Step 12.4); the
  real voice test with Kroko is the user's.
  The test switches the daemon to the fake command and restores the real one.

  Scenario: Dictated words go into the Slate and are sent with the rest
    Given the daemon's dictation command is Mycroft's resident fake mode saying "bonjour luna"
    And a terminal is open and the Slate is shown on it with "echo " typed
    Then the provider has been started by the Slate's opening and is idle
    When the person presses L2
    Then the Slate's hint reads "dictation: listening"
    And the words appear underlined at the cursor
    When the person presses L2 again
    Then "bonjour luna" is inserted after "echo " and the hint is back to normal
    When the person hides the Slate with L1, shows it again with L1, and presses L2
    Then dictation listens within 3 seconds, from the same provider process
    When the person presses L2 again, then L2 twice more
    Then "bonjour luna" is inserted twice more
    When the person types " > F" and presses FN+A
    Then the terminal writes "bonjour luna bonjour luna bonjour luna" into F
