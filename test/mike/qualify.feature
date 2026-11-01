Feature: Mike 10, qualify a model: 90 % stable on the evaluation cases
  A model is used, optimised or run on Luna only once it is qualified (user,
  2026-10-29). Executed by test/mike/test_qualify.py (marker integration,
  desk host Termidor). Evidence: results/mike/qualify/<timestamp>/<model>.<format>/
  (report.json, rows.jsonl with every answer, the server log), and summary.jsonl.

  Scenario Outline: One model in one prompt format
    Given the GGUF model "<model>" on llama-server, context 2,048, 4 threads
    And prompt v4's instructions, examples and desktop line in the "<format>" format
    And the answer constrained by the contract grammar
    When each of the 81 main and 31 held-out cases is asked twice greedily and 9 times sampled
      (temperature 0.5, top-p 0.95, seeds 1 to 9)
    Then every answer is scored after the adapter
    And the two greedy answers of each case are compared (determinism)
    And a case is stable-right when at least 9 of its 10 counted answers are right
    And the model is qualified when at least 90 % of the cases are stable-right on each set

    Examples:
      | model                            | format |
      | LFM2.5-350M-Q4_0.gguf            | native |
      | LFM2.5-350M-Q4_0.gguf            | plain  |
      | Qwen3-1.7B-Q4_K_M.gguf           | plain  |
      | bitnet-b1.58-2B-4T-i2_s.gguf     | plain  |
      | Qwen3-4B-Q4_K_M.gguf             | plain  |
      | gemma-3-4b-it-Q4_K_M.gguf        | plain  |
