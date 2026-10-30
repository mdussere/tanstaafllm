Feature: Mike 4.6, the model's base speed without any harness
  `llama-completion` alone reads a fixed French Cluedo scene of about 1,050
  tokens and answers in a few tokens (who, with what, where). No tools, no
  grammar, no prefix cache. Executed by test/mike/test_raw_speed.py
  (desk: marker integration; Luna: marker live, under the brain lock).
  Evidence: results/mike/raw-speed/<timestamp>/ (full logs, summary.jsonl).

  Scenario Outline: One setting on one host
    Given LFM2.5-350M Q4_0, 4 threads, greedy decoding, at most 24 tokens
    And the weight-repacking setting "<setting>"
    When the Cluedo prompt is read and answered
    Then prompt tokens per second, generated tokens per second, load time and the answer are saved

    Examples:
      | setting |
      | lean    |
      | repack  |
