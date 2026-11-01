Feature: Camp Currie's first shell and simulated mission (Steps 2-3)
  The game runs without speech: a labelled, deterministic evaluator decides
  each attempt. Keys only: arrows, Return (A), Escape (B). Executed by
  test_camp_currie.py; the rendered run saves every screen under
  results/camp-currie/shell/<timestamp>/ for inspection.

  Scenario: From the title to the first contact
    Given the title screen
    When the learner presses A, then A on "Meet the Crew", then A on the briefing
    Then Mannie's call shows his name, the target "MANNIE" and the hint "MAN-ee"

  Scenario: Locked missions explain themselves
    Given the mission map
    When the learner moves to "Talk to the Crew" and presses A
    Then the mission stays closed and says it needs speech, later

  Scenario Outline: One transmission, three simulated outcomes
    Given a contact and the evaluator scripted to "<outcome>"
    When the learner transmits
    Then the result stamp reads "<stamp>" and the reason says it is simulated
    And A leads to "<next>"

    Examples:
      | outcome   | stamp     | next          |
      | success   | CLEAR!    | next contact  |
      | retry     | TRY AGAIN | your turn     |
      | uncertain | NOT SURE  | your turn     |

  Scenario: The whole mission
    Given the default script (success, retry, success, uncertain, success, success, success)
    When the learner clears all five contacts
    Then the debrief shows 5/5, 7 transmissions, 1 retry, 1 not sure, and rank A
    And "Simulated results, not a pronunciation score."
