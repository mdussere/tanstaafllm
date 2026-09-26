@live
Feature: Wyoh validates a bounded Sway IPC operation

  Scenario: A trusted proof fixture focuses an allowlisted workspace in an isolated Sway session
    Given luna-pi has the pinned user-local Sway 1.10.1 proof prefix
    And the fixture has recorded its pre-operation Sway outputs, tree, workspaces, inputs, seats, and version
    When it asks the capability boundary to focus workspace "wyoh-proof" at the expected revision
    Then only the fixed "workspace wyoh-proof" command reaches Sway
    And the fixture waits for an observed workspace focus event rather than a fixed completion delay
    And the post-operation snapshot identifies "wyoh-proof" as focused
    And the result preserves IPC replies, event, process metrics, and recovery evidence

  Scenario: A stale, unauthorised, or ambiguous request cannot mutate Sway
    Given a consumer request is stale, not allowed, or names an ambiguous workspace
    When the capability boundary validates it
    Then the request is rejected before any Sway IPC command is sent
