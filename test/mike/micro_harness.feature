Feature: Mike Step 3b.2, ready-made micro-harnesses on Mike's local model
  ZeroClaw and PicoClaw (official release binaries) drive LFM2.5-350M through
  llama-server, with Mike's six contract tools from a fake MCP server as their
  only tools. Nothing reaches a desktop. Executed by
  test/mike/test_micro_harness.py::test_micro_harness (marker: integration;
  needs MIKE_ASSET_ROOT and MIKE_TOOLS_ROOT).
  Evidence: results/mike/micro-harness/<timestamp>/ (every request the harness
  sent, every tool call, logs, summary.jsonl).

  Background:
    Given llama-server with LFM2.5-350M, --jinja and an 8,192-token context
    And a recording proxy between the harness and the server
    And a throw-away home where the harness has only Mike's instructions and Mike's six MCP tools

  Scenario Outline: One harness answers four French requests
    Given the harness "<harness>"
    When it is asked, one process per request: "ouvre l'éditeur", "mets le terminal à gauche", "écris bonjour", "quel temps fera-t-il demain"
    Then the first tool call of each answer is compared with the expected contract call (none for the weather)
    And the prompt it sent (system size, tools, tokens, cached tokens) is kept
    And its own peak RSS, without the fake MCP server, and its wall time are saved

    Examples:
      | harness  |
      | zeroclaw |
      | picoclaw |
