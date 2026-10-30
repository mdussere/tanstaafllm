Feature: Mike Step 4.5, first supervised run on Luna
  LFM2.5-350M Q4_0 runs in the official llama.cpp arm64 `llama-server`, lean,
  on Luna as `michael`, under the shared brain lock. The desk renders the
  prompts and scores the answers through an SSH tunnel; nothing is executed on
  Luna's desktop. Executed by test/mike/test_luna_first_run.py::test_luna_first_run
  (marker: live; needs Professor's go with Mannie on Luna stopped).
  Evidence: results/mike/luna-first-run/<timestamp>/ (run.log, server log,
  report.json with every memory sample, summary.json).

  Scenario: Six held-out requests, one per tool
    Given the release and the model under ~/.local/opt/mike with their checksums checked
    And /tmp/luna-brain.lock is free, then holds "mike <server pid>"
    When the shared prompt prefix is evaluated once and saved to a slot file
    And each request is sent after restoring that prefix
    Then each proposal is scored, and nothing runs on the desktop
    And MemAvailable is sampled before start, after load, every second, and after stop
    And the server stops if MemAvailable falls below 150 MiB
    And at the end the server is stopped and the lock is removed
