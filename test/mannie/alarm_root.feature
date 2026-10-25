Feature: An Arch Linux ARM root for Luna, on ArchR's boot path (Mannie plan Step 7)
  The root is built on the desk host by src/mannie/alarm/build-luna-root.sh, without
  root privileges, from the signed Arch Linux ARM tarball and ArchR's kernel modules.
  Executed by test/mannie/test_alarm_root.py: the account and resolver checks run by
  default; the image check is an integration test (MANNIE_ALARM_IMAGE=<image>).
  Nothing here writes to a card.

  Scenario: the default account becomes michael's
    Given Arch Linux ARM's account files with the "alarm" user at uid 1000
    When accounts.py edits them
    Then "alarm" is gone, michael has uid 1000 and belongs to wheel, video, audio, input and render
    And root's password is locked

  Scenario: only missing packages are fetched for the first boot
    Given the base root's package database
    When the closure of the wanted packages is resolved
    Then packages and virtual provisions the base already has are left out

  Scenario: the built image fits ArchR's boot path
    Given a built image
    Then its label is ARCHR_ROOT
    And /flash and /storage exist, and the 6.12.94 modules are reachable at ArchR's kernel-overlays path
    And rk915's module and firmware are present
    And the owners and modes of the sensitive files are root's, as on a real install
    And pacman ignores Arch Linux ARM's kernel
    And SSH uses Luna's host keys on STORAGE, and /home is LUNA_HOME
    And the first-boot service is enabled, with every cached package beside its signature
