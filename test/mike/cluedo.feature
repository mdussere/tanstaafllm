Feature: Mike 8.0, a trust check: does the model solve a simple Cluedo scene?
  A scene of about 1,000 tokens, in French and in English, with one answer:
  Professor Plum / le professeur Violet, the rope / la corde, the library / la
  bibliothèque. Executed by test/mike/test_cluedo.py::test_cluedo (marker:
  integration; desk host). Evidence: results/mike/cluedo/<timestamp>/answers.jsonl.

  Scenario Outline: One model, eight questions
    Given the model "<model>" in llama-server with its own chat template
    When it is asked in French and in English, for a short answer and for brief reasoning then the answer,
      with greedy and with Liquid AI's recommended sampling
    Then each answer is scored on the murderer, the weapon and the room

    Examples:
      | model                     |
      | LFM2.5-350M-Q4_K_M.gguf   |
      | LFM2.5-350M-Q4_0.gguf     |
      | LFM2.5-350M-QAD-Q4_0.gguf |
      | LFM2.5-230M-Q4_K_M.gguf   |
