Feature: Mike 11, a pre-trained model untrained on the NL2SH-ALFA test set
  The baseline for Step 11's trained models. LFM2.5-350M Q4_0 in llama-server,
  one-line system prompt asking for a single bash command, greedy. Executed by
  test/mike/test_nl2sh_baseline.py (marker integration). Evidence:
  results/mike/nl2sh-baseline/<timestamp>/<model>/ (llama-server.log,
  rows.jsonl, result.json).

  Scenario: The 300 test requests are answered once
    Given the 300 NL2SH-ALFA test requests, each with two accepted commands
    When each request is sent to the model's chat endpoint, greedy
    Then the first command line of each answer is saved with its raw answer
    And the result gives the exact matches against either command, the same first command and the character error rate
