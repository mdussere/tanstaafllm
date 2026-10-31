Feature: Mike 12.5, small talk on Luna
  The client src/mike/smalltalk.py on Luna (R36 Ultra), as michael, with
  LFM2.5-350M Q4_0 and llama-server b11429 arm64 in ~/.local/opt/mike.
  Only while Mannie on Luna is stopped and the brain lock is free; Kroko,
  Sway and the Wyoh services keep running. Executed by
  test/mike/test_smalltalk_luna.py (marker live). Evidence:
  results/mike/smalltalk-luna/<timestamp>/ (chat.jsonl, each run's output and
  server log, summary.json).

  Scenario: Four runs of Step 12.1's questions on stdin
    Given the client copied to Luna and checked by SHA-256
    When it answers the French questions cold, the English ones cold, the French ones warm, and the French ones with repacked weights
    Then each start records its time to ready and whether L0 was read or restored
    And each turn records the tokens read, the time to the first word and to the last, and the server's memory
    And the brain lock is released after each run
