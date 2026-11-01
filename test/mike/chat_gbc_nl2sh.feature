Feature: Mike 11, Rudy's Chat-GBC models trained on natural language → shell
  Chat-GBC (github.com/rudydel/Chat-GBC, commit db83f9b) with a tokenizer that
  keeps case and every printable ASCII character (chat_gbc_nl2sh.patch). Trained
  from scratch on Termidor's CPU with Rudy's recipe and step counts, on the
  NL2SH-ALFA training pairs (MIT ALFA, NAACL 2025), without his question
  augmentation. Executed by test/mike/test_chat_gbc_nl2sh.py (marker
  integration). Evidence: results/mike/chat-gbc-nl2sh/<timestamp>/<model>/
  (train.log, eval.log, rows.jsonl, eval.json) and summary.jsonl.

  Scenario Outline: A tiny shell model is trained and measured
    Given the clone matches chat_gbc_nl2sh.patch
    And the NL2SH-ALFA training pairs that fit the context, the longer ones counted
    When the "<model>" configuration is trained for 12,000 pre-training and 8,000 fine-tuning steps
    And every one of the 300 test requests is asked once, greedy
    Then each answer is saved with its two accepted commands
    And the summary gives the exact matches against either command, the same first command, the character error rate and the training time

    Examples:
      | model |
      | tiny  |
      | micro |
