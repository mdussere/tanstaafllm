Feature: Mike 13.5, graceful uncertainty
  Mike's model often invents facts (Step 12.5). A system-prompt variant that
  invites "I am not sure" is compared with the client's own prompt, on the
  desk, through the client's code. Executed by
  test/mike/test_mike_uncertainty.py (marker integration). Evidence:
  results/mike/uncertainty/<timestamp>/ (turns.jsonl, summary.json).

  Scenario: The humble prompt against the current one
    Given Step 12.1's conversations and six questions the model cannot know
    When each prompt plays them through the client
    Then each answer is recorded with its first-word time, length and whether it admits doubt
    And the variant is kept only if it admits doubt more on the unknowable questions,
      not more on the ordinary ones, with no slower first word and no longer answers
