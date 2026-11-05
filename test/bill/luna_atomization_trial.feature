Feature: Local comparison of Luna sequence atoms

  The raw Luna session is private.  This experiment compares two models on the
  same bounded local source without publishing either the source or its derived
  atoms.

  Scenario: Two models atomize the first two Luna timestamp days
    Given the identified local Luna JSONL source
    And the source rows whose timestamps start with 2026-10-03 or 2026-10-04
    When GPT-6 Luna and GPT-6.1 Terra independently make concise Markdown sequence atoms
    Then each result remains in its dated ignored results directory
    And every atom names a beginning, an end, source references, a sequence and uncertainty
    And each run records model name, scope, start time and finish time
    And the validator reports whether each local result has the required observable shape
    And no raw or derived memory content is committed or written to Tinkstaff LLM Biverse
