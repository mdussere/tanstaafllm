Feature: Mike Step 3.2c, shortlisted models on the evaluation sets
  Each model proposes one contract call for every request of the main set
  (81 cases) and of the held-out set (31 cases, never used for tuning).
  Nothing is executed. Executed by test/mike/test_model_eval.py::test_model_eval
  (marker: integration; needs MIKE_ASSET_ROOT and the uv group `mike`).
  Evidence: results/mike/model-eval/<timestamp>/<model>.json and summary.md.

  Background:
    Given a shortlisted GGUF model under MIKE_ASSET_ROOT
    And prompt v3 built from the tool contract, with the desktop line in the user turn
    And the shared prompt prefix evaluated once per mode and restored before each request

  Scenario Outline: One model answers both sets in both modes
    When the model answers every request freely, then constrained by the contract grammar
    Then each answer is scored as the model's call and as the adapter's proposal
    And the median and worst time per request and the peak RSS are saved

    Examples:
      | model                   |
      | LFM2.5-350M-Q4_K_M.gguf |
      | LFM2.5-230M-Q4_K_M.gguf |
