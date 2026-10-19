Feature: Mike Step 3b.1, the model through llama.cpp's C++ server
  The same contract evaluation as Step 3 (prompt v4, constrained), but the
  model runs in `llama-server` from the official llama.cpp release, not in
  Python. Nothing is executed on the desktop. Executed by
  test/mike/test_server_runtime.py::test_server_runtime (marker: integration;
  needs MIKE_ASSET_ROOT and the unpacked release under MIKE_TOOLS_ROOT).
  Evidence: results/mike/server-runtime/<timestamp>/ (server logs, one JSON
  report per model and configuration, summary.jsonl).

  Background:
    Given a GGUF model under MIKE_ASSET_ROOT
    And llama-server started with one slot, a 2,048-token context and 4 threads

  Scenario Outline: One configuration answers both sets
    Given the server configuration "<config>"
    When every request of the main (81) and held-out (31) sets is sent with the contract grammar
    Then each answer is scored as the model's call and as the adapter's proposal
    And the server's peak, anonymous and file-backed RSS are read from /proc
    And the median and worst time per request and the prompt tokens evaluated are saved

    Examples:
      | config    |
      | default   |
      | lean      |
      | lean-ckpt |
      | lean-slot |
