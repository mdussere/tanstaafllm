Feature: A very simple browser in the Wyoh session (Wyoh Step 9.10)
  NetSurf's framebuffer front end (PortMaster's nsfb) draws on an SDL
  surface in Sway, with images and JavaScript off. It is checked first on
  luna-pi's 720x720 headless Sway, while Luna is busy with Mannie. Executed by
  test_luna_pi_netsurf.py; every page is a grim screenshot kept in results/.

  Scenario Outline: NetSurf opens a page on luna-pi
    Given the bundle assembled by fetch_netsurf.py is copied to luna-pi
    And every library nsfb needs is found
    When nsfb opens "<url>" in luna-pi's Sway at 720x720
    Then after <seconds> seconds nsfb is still running
    And the screenshot is not blank, and is kept to be inspected for the page's text and "Done"

    Examples:
      | url                                             | seconds |
      | https://lite.duckduckgo.com/lite/               | 20      |
      | https://lite.duckduckgo.com/lite/?q=lune        | 20      |
      | https://fr.wikipedia.org/wiki/Lune              | 60      |
