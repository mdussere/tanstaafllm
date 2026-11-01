Feature: Mike 17, small-talk quality assessed, nothing changed
  The user finds talking to Mike "hallucination all the time". This step records
  reproducible transcripts of where Mike stands, on Termidor, and changes nothing:
  the same client code (src/mike/mike.py: Conversation, answer, L0Frame), the same
  system prompt, the same LFM2.5-350M Q4_0 and the same sampling. No reference
  model for now (the user, 2026-11-01).
  Scenarios: test/mike/assessment_scenarios.json (S1-S6, French and English).
  Executed by test/mike/test_mike_assessment.py (marker integration).
  Evidence: results/mike/assessment/<timestamp>/<model>/ (turns.jsonl and one
  Markdown transcript per scenario, language and run). Professor grades; the
  runner does not grade.

  Background:
    Given a llama-server started by Mike's client code on Termidor
    And Mike's own system prompt for the scenario's language

  Scenario Outline: One model plays every scenario
    Given the model <model>
    When each scenario is played in French and in English, once greedy and with seeds 1, 2 and 3
    Then every turn is recorded with its question, full answer, time to first token, total time and tokens
    And whether the client rolled the conversation over
    And a readable transcript exists per scenario, language and run

    Examples:
      | model        |
      | lfm2.5-350m  |
