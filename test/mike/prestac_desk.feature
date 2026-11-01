Feature: Mike 9.2, PreStaC on the desk host
  PreStaC keeps one model state file per context layer (instructions and tools,
  desktop, terminal), computed in the background as navigation changes the
  stack; a question restores the deepest ready frame and reads only the rest.
  Executed by test/mike/test_prestac_desk.py (marker: integration; llama-server,
  LFM2.5-350M Q4_0, lean). Evidence: results/mike/prestac-desk/<timestamp>/.

  Scenario: The cache does not change the answers
    Given a sample of the 112 evaluation requests
    When each is answered through PreStaC and again with no cache at all
    Then both answers are the same text

  Scenario: A navigation path
    Given the requests grouped by desktop
    When the path visits each desktop, opens and leaves the terminal, comes back to the first desktop,
      and on every other desktop asks the first question before the prefetch has finished
    Then at least 95 % of all prompt tokens are restored from frames
    And the time from question to answer, the background work and the frame sizes are saved
