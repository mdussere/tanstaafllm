Feature: Mike 8.0c, can a small model write a correct bash one-liner?
  Five everyday requests (disk usage, home files by size, recent .log files,
  line count, top memory processes), each with the commands accepted as right.
  Executed by test/mike/test_oneliner.py::test_oneliner (marker: integration;
  desk host). Evidence: results/mike/oneliner/<timestamp>/answers.jsonl.

  Scenario: One model, twenty answers
    Given a model in llama-server with its own chat template
    When each request is asked in French and in English, greedy and with Liquid AI's sampling
    Then the first command line of each answer is checked against the accepted commands
    And whether the answer is a single line is recorded
