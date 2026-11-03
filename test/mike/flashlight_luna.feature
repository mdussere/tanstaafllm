Feature: Mike 14.4, the flashlight on Luna
  The flashlight chosen on the desk (POTION-4M for routing, BM25 and their
  reciprocal-rank fusion for retrieval) measured on Luna itself: load time,
  memory and milliseconds per sentence and per 100-word block, warm. Only in a
  slot agreed with Mannie on Luna. Executed by test/mike/test_flashlight_luna.py
  (marker live). Evidence: results/mike/flashlight-luna/<timestamp>/.

  Scenario: The desk bench, run on Luna
    Given a venv under ~/.local/opt/mike-embed with the desk's model2vec version
    And the bench, Luna's guide pages and POTION-4M's files copied from the desk
    When BM25, POTION-4M and their fusion are each measured in their own process
    Then each records its load time, memory, and milliseconds per sentence and per 100-word block
    And its routing and retrieval scores match the desk's, since the data and models are the same
