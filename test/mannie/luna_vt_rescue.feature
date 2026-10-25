Feature: A keyboard brings back Luna's console (Mannie plan 7.5)
  If SSH or the desktop fail, plugging a USB keyboard into Luna and pressing
  Ctrl+Alt+F1 shows tty1, where michael is logged in. Ctrl+Alt+F7 goes back to
  Wyoh's Sway session. luna-vt-rescue reads the keyboards directly, so this works
  even when Sway is stuck; the kernel has no SysRq. Executed by
  test/mannie/test_luna_vt_rescue.py (live part: MANNIE_LUNA_LIVE=1).

  Background:
    Given Wyoh's Sway session runs on tty7 and michael's autologin console on tty1
    And luna-vt-rescue is running

  Scenario: only Ctrl+Alt+F<n> switches
    Then Ctrl+Alt+F1 asks for VT 1 and Ctrl+Alt+F7 for VT 7
    And Ctrl or Alt alone, a key release, or another key ask for nothing

  Scenario: a keyboard plugged in while Luna runs
    Given a new keyboard appears (a uinput virtual keyboard in the test)
    When it presses Ctrl+Alt+F1, then Ctrl+Alt+F7
    Then the active VT is tty1, then tty7
    And luna-vt-rescue's journal shows it watched the keyboard and ran both chvt
    And Wyoh's Sway session is still active
