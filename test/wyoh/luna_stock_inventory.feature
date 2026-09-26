@live
Feature: Read-only preserved Luna stock-image inventory

  Scenario: Wyoh records the delivered EmuELEC baseline without modifying it
    Given Luna is reachable through the configured SSH key as root
    And its current microSD image is the preserved retrogaming baseline
    When the inventory reads identity, boot, mounts, memory, DRM, input, session processes, and SSH metadata
    Then it performs no target writes, package actions, service changes, or restarts
    And it persists complete stdout and stderr evidence under results/wyoh/luna-stock-inventory
    And its record distinguishes the stock image from the future experimental card
