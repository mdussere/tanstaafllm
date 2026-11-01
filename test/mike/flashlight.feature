Feature: Mike 14.1-14.3, the "flashlight embedding"
  The smallest, fastest embedding that serves both zero-shot routing of short
  user sentences and retrieval of short knowledge blocks (about 100 words) from
  Luna's guide. Termidor only; nothing goes into Mike's conversation yet.
  Data: test/mike/flashlight_data.json; blocks cut by test/mike/flashlight_blocks.py.
  Executed by test/mike/test_flashlight.py with flashlight_bench.py (marker
  integration). Evidence: results/mike/flashlight/<timestamp>/candidates.jsonl.

  Scenario Outline: One candidate measured in its own process
    Given the candidate <candidate>
    When it is loaded and the guide's blocks are indexed
    Then its disk size, memory, and milliseconds per sentence and per 100-word block are recorded
    And its zero-shot routing accuracy, by label description alone and with three anchors per label
    And its top-1 and top-3 retrieval on the guide questions
    And how well its best score separates guide questions from questions outside the guide

    Examples:
      | candidate                      |
      | bm25                           |
      | tfidf                          |
      | minishlab/potion-base-2M       |
      | minishlab/potion-base-4M       |
      | minishlab/potion-base-8M       |
      | minishlab/potion-retrieval-32M |
      | rrf (BM25 + POTION-4M fused)   |
