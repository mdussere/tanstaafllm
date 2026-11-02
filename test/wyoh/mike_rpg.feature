Feature: Mike's RPG dialogue window (Wyoh 6.13, look B)
  mike_rpg.py runs Mike's client unchanged in a pseudo-terminal and stages it:
  the question above, Mike's portrait, the answer typed in a dialogue box. It
  mirrors the client's titles, so FN+B and the Mike <-> Mannie switch keep
  working. Executed by test_mike_rpg.py with a fake client; screens saved
  under results/wyoh/mike-rpg/<timestamp>/ and inspected.

  Scenario: A question and its streamed answer
    Given the window has started the client and its title reads "Mike — ready"
    When "hello" is typed and Return pressed
    Then the question shows at the top, the title goes "thinking" then "ready"
    And the dialogue box holds Mike's whole answer, without the echoed question or the prompt

  Scenario: Mike asks to stop Mannie
    Given the client starts with "Mike — asks: stop Mannie?"
    When Return (A) is pressed
    Then the title becomes "Mike — waiting for Mannie", then "Mike — ready"
