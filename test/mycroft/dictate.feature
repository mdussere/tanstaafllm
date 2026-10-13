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

  # Step 9.7: resident mode for the Slate (Wyoh's note 0903_03).

  Scenario: Resident provider serves several utterances with one load (deterministic)
    Given the provider runs with --resident and --fake "ouvre le terminal"
    Then it sends "ready" and nothing more while idle, and ignores a "stop" while idle
    When the host sends {"op": "start"}
    Then it sends "listening", then one "partial" per new word
    And a second "start" while listening is ignored
    When the host sends {"op": "stop"}
    Then it sends one "final", stays running and silent, and the next "start" begins from an empty text
    When the host closes stdin
    Then it exits with status 0, after a "final" if it was listening

  Scenario: Resident setup error (deterministic)
    Given the model files are missing
    Then the provider's only line is an "error", and it exits with status 2
