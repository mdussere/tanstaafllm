Feature: Mike Step 3 model smoke test on the desk host
  A small local model receives Mike's task-level tool list and a dozen
  short French requests and proposes one call for each. Nothing is executed.
  Executed by test/mike/test_model_smoke.py::test_model_smoke
  (marker: integration; needs MIKE_ASSET_ROOT and the uv group `mike`).
  Evidence: results/mike/model-comparison/<timestamp>/<model>.json and summary.md.

  Background:
    Given a shortlisted GGUF model under MIKE_ASSET_ROOT
    And the model runs alone in a fresh process with a 2,048-token context and 4 threads

  Scenario Outline: One model answers every smoke request in both modes
    When the model is loaded
    Then its load time and peak RSS are recorded
    When each request is rendered with the model's own chat template and the tool list
    And the model answers freely, then with its call opener prefilled and a grammar
    Then every answer, its parsed call, its score, its prompt tokens and its timings are saved
    And the constrained answers are all well-formed calls from the list

    Examples:
      | model                              |
      | LFM2.5-350M-Q4_K_M.gguf            |
      | LFM2.5-230M-Q4_K_M.gguf            |
      | functiongemma-270m-it-Q4_K_M.gguf  |
