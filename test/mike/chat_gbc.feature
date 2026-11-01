Feature: Mike 10.6, Chat-GBC's shipped models reproduced on the desk host
  Chat-GBC (github.com/rudydel/Chat-GBC, commit db83f9b) runs a 21k–138k
  parameter transformer on a Game Boy. On Termidor, without the ROM or an
  emulator, its own Python entry points run its shipped checkpoints. Its
  training is not run (Mike's non-goal). Executed by test/mike/test_chat_gbc.py
  (marker integration). Evidence: results/mike/chat-gbc/<timestamp>/ (every
  command's complete output, summary.jsonl, chat.jsonl).

  Scenario Outline: The project's evaluation gives the numbers of its training log
    Given the shipped checkpoint "<model>" and the project's data/gameboy questions
    And the held-out split of its training run (share 0.2, seed 0)
    When llm.evaluate runs with the "<mode>" model
    Then the exact-match shares on training and held-out questions, per source file,
      equal the final "[<mode>]" evaluation in models/<model>/train_log.txt

    Examples:
      | model | mode  |
      | tiny  | float |
      | tiny  | int   |
      | micro | float |
      | micro | int   |

  Scenario Outline: A few questions, timed
    Given the shipped checkpoint "<model>" in "<mode>" mode
    When it is asked two README questions, one off-topic question and two of Mike's requests
    Then each answer and its time, model load included, are saved

    Examples:
      | model | mode  |
      | tiny  | int   |
      | micro | int   |
