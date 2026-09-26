Feature: Luna Pi VNC desktop evidence

  @live
  Scenario: Capture the virtual Luna Pi desktop through the SSH tunnel
    Given the `luna-vnc.service` is active on luna-pi
    And an SSH tunnel forwards local port 5900 to Pi-local port 5900
    When I run `LUNA_VNC_LIVE=1 pytest -m live test/luna`
    Then the run saves `desktop.png` and capture logs under `results/luna/vnc/<timestamp>/`
    And the screenshot is inspected rather than judged by pytest exit status alone

  @live
  Scenario: Report a blank desktop honestly
    Given the captured image is substantially black
    Then the test still preserves the image and logs
    And the workline records the virtual session as blank rather than calling it a usable desktop
