Feature: Talking to Mike from the Slate on Luna (Wyoh Step 6.11)
  Mike's window is a foot terminal with app_id "mike" running Mike's client
  (mike.py) as michael; its title says "Mike — ready" once it takes a
  question. FN+B in the Slate starts it when needed, waits, types the text
  and Return. Mannie must be stopped (Mike and Mannie never run together).
  Executed by test_luna_mike_window.py through Wyoh's MCP server.

  Scenario: FN+B starts Mike and Mike answers
    Given Mannie is stopped and no Mike window is open
    When the Slate opens with L1 and a question is typed in it
    And FN+B is pressed
    Then Mike's window appears and its title becomes "Mike — ready"
    And the question is delivered once, Mike thinks, and is ready again
    And the screenshot shows the question and Mike's answer

  Scenario: FN+B with Mike already open
    Given Mike's window is open and ready
    When a second question is typed in the Slate and FN+B is pressed
    Then it is delivered at once and Mike answers it in the same window
    And closing Mike's window leaves no llama-server and no brain lock
