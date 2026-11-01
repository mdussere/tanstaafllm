Feature: Mike 12.1, small talk with LFM2.5-350M raw
  Mike's chosen model, untrained, as a chat partner: a short system prompt,
  a few short conversations in French and English on subjects that are
  surely in its training corpus. No action runs; the answers are read by
  the user, not scored. What is measured is time: the tokens read before
  each answer, the tokens written, and Luna's time estimated from its
  measured speeds (6.5 tokens/s read, 3.6 tokens/s written, docs/0405_01).
  Executed by test/mike/test_chat_baseline.py (marker integration).
  Evidence: results/mike/chat-baseline/<timestamp>/<config>/ (llama-server.log,
  turns.jsonl, result.json) and answers.md for reading.

  Scenario Outline: Conversations through llama-server's chat endpoint
    Given llama-server with LFM2.5-350M Q4_0 in the "<config>" setting
    And a system prompt of a few tens of tokens asking for short answers
    When each conversation is played turn by turn, the history sent each time
    Then each turn records the tokens read, the tokens written and the answer
    And a follow-up turn reads only its own new tokens when the server reuses the conversation
    And Luna's time to the first word and to the last word is estimated from the token counts

    Examples:
      | config    |
      | lean      |
      | lean-ckpt |
