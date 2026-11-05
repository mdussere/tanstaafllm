Feature: Complete first-pass segmentation of the Luna Claude session

  The complete raw JSONL is preserved in a private repository. A model may
  inspect bounded reading views, and its derived sequence index remains
  traceable to the immutable source.

  Scenario: Terra cuts and summarizes all source rows
    Given the byte-verified 3,714-row Luna session
    And bounded reading views retaining absolute source line numbers
    When GPT-6.1 Terra marks attempted-action sequences across every view
    Then each sequence has a title, source start and end, summary, observed state and uncertainty
    And every source line is assigned to a sequence or explicitly labelled context only
    And cross-view continuations are reconciled before the complete index is accepted
    And model usage or a clearly labelled cost estimate is recorded
    And the raw source and derived index are stored in the private repository

  Scenario: Adam browses Luna's source and provisional atoms
    Given the first-pass index was preserved in Git history
    When the current private tree is opened
    Then Luna has only raw and refined directories
    And raw contains exactly the byte-verified original JSONL
    And refined contains 79 date-and-sequence-sorted Markdown atom drafts
    And each draft links its source lines and says its verbatim is pending
    And the four context-only spans plus the drafts account for all 3,714 rows
