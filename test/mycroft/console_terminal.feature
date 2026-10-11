Feature: Mycroft v0 console in a real terminal
  The console is a full-screen foreground view. It must stay readable, must
  not fill the terminal or its scrollback with repeated frames, and its keys
  must behave as documented. Executed by
  test/mycroft/test_console_terminal.py::test_console_in_a_real_terminal
  (marker: integration; needs MYCROFT_ASSET_ROOT). Every screen below is
  saved as text under results/mycroft/console-terminal/<timestamp>/.

  Background:
    Given the pinned Sherpa runtime and French model are installed
    And the console runs in an 80×24 pseudo-terminal replaying a public model test WAV

  Scenario: Compose, edit with the letter q, accept, then discard by Esc alone
    When the console has loaded the model
    Then the screen shows "Mycroft v0 — idle" on its first row and "Source:" on its second
    And nothing is written to the terminal while nothing changes
    When the user presses Space
    Then recognised lower-case text appears in the single text area before the replay ends
    And replay EOF leaves an editable "stopped-draft"
    When the user types " quoi"
    Then the draft ends with " quoi" and the console is still running
    When the user presses Enter
    Then the state is "accepted"
    When the user presses Space and then Esc with no following key
    Then the state becomes "discarded"
    When the user presses q
    Then the console exits with status 0 and restores the normal screen
    And the accepted draft is printed exactly once after the full-screen view closes
    And no frame line was ever started with a bare line feed
    And the console's peak RSS is saved as evidence
