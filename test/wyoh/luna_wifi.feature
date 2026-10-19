Feature: Choosing a Wi-Fi network on Luna (Wyoh Step 7)
  iwd owns Wi-Fi on Luna; Wyoh's panel (wyoh_wifi.py) lists networks in
  fuzzel and joins them through iwd's D-Bus interface. Leaving the home
  network cuts the desk's SSH, so the join runs on Luna, detached
  (luna_wifi_switch.py), and always returns home. Executed by
  test_luna_wifi.py. Passwords come from the environment and never reach
  results/.

  Scenario: Luna joins a second network with a new password and comes home
    Given Luna is connected to its home network
    When a new profile is written for the test network with a candidate password
    And Luna connects to it, trying the next candidate after a refusal
    Then one attempt succeeds, with an address and the test network in the bar text
    And Luna returns to the home network with its home address
    And no profile for the test network is left
