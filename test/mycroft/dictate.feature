Feature: Mycroft dictation provider protocol
  A host (Wyoh's gamepad daemon, for the Slate) starts mycroft_dictate.py,
  reads JSON lines from its stdout, and stops it by closing its stdin. The
  host owns the text. Protocol agreed in
  worklines/wyoh/docs/0600_02_note-from-mycroft-dictation-in-slate.md.
  Executed by test/mycroft/test_dictate.py.

  Scenario: Fake dictation, stopped by the host (deterministic)
    Given the provider runs with --fake "ouvre le terminal"
    Then its first line is {"op": "ready"}
    And it sends one "partial" per new word, each with the whole text so far
    And it sends no further "partial" while the text does not change
    When the host closes the provider's stdin
    Then the provider sends one "final" with "ouvre le terminal" and exits with status 0

  Scenario: Stop by SIGTERM (deterministic)
    Given the provider runs with --fake and has sent "ready"
    When the host sends SIGTERM
    Then the provider sends one "final" and exits with status 0

  Scenario: Setup error (deterministic)
    Given the input path does not exist
    Then the provider's only line is an "error" with a message, and it exits with status 2

  Scenario: Real model on a public French WAV (integration, needs MYCROFT_ASSET_ROOT)
    Given the pinned Sherpa runtime for this machine's architecture and the French model
    When the provider replays a public model test WAV with stdin kept open
    Then it sends "ready", then lower-case "partial" lines, then a non-empty "final" at the end of the file, and exits 0
    When the provider replays the same WAV and the host closes stdin after the first "partial"
    Then it sends "final" promptly and exits 0
    And model load time, first-partial latency, stop-to-final latency, and peak RSS are saved under results/mycroft/dictate/<timestamp>/
