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

  # Step 13.8: every session can be read back.
  Scenario: A session leaves a readable trace
    Given Mike starts, answers questions and ends
    Then chat.jsonl holds the session's start, turns, notices and end, each with the session id
    And conversations/<session>.md holds each question and answer with its timings, and why the session ended

  # Step 13.9: Mike and Mannie never run together, and the user switches between them.
  Scenario: Mike starts while Mannie holds Luna
    Given the brain lock is held by a live "mannie"
    When Mike's window opens
    Then its title starts with "Mike — asks" and it asks to stop Mannie: A (Return) yes, B (Escape) no
    When the user answers no
    Then Mannie keeps the lock and Mike's window closes
    When the user answers yes
    Then the title starts with "Mike — waiting", "mannie stop --save" runs, and Mike starts once the lock is free
    And if Mannie does not stop, Mike does not start

  Scenario: The user hands Luna back to Mannie
    Given Mike is ready
    When the user types "/mannie"
    Then Mike stops its server, frees the lock, starts "mannie start" detached, and its window closes
