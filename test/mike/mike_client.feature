Feature: Mike 12.2, the small-talk client keeps the conversation as tokens
  src/mike/mike.py, Mike's chat client: one question per line, the
  answer streamed. The conversation is kept as the exact token ids the server
  read and generated; the system prompt (layer L0) is a PreStaC frame saved
  with the server's slot save. Executed by test/mike/test_mike_client.py
  (deterministic tests, and marker integration against llama-server).
  Evidence: results/mike/client-desk/<timestamp>/ (turns.jsonl,
  summary.json, server logs).

  Scenario: Follow-up turns read only themselves
    Given the client and llama-server with LFM2.5-350M Q4_0
    When Step 12.1's conversations are played through the client
    Then the streamed text equals the recorded answer
    And no follow-up turn reads more than 40 prompt tokens

  Scenario: A restarted client restores the system prompt
    Given the slot files saved by a first run
    When the server and the client start again and the conversations are played
    Then layer L0 is restored, not read
    And the first question of each conversation reads no more than 40 prompt tokens
