Feature: Blind Story 2 storyboard comprehension evidence
  A reviewer who has never seen the project must be able to inspect a one-second
  storyboard without receiving the episode brief, repository, video title or any
  other explanatory material.

  Scenario: Extract a neutral one-frame-per-second packet
    Given the current scripted Story 2 preview MP4 is supplied through HAZEL_STORY2_BLIND_VIDEO
    When the explicit integration test extracts the first 90 seconds at one frame per second
    Then results/hazel/video-pipeline contains 90 640×360 PNG stills
    And it contains ten 3×3 contact sheets and a frame-to-second manifest
    And the reviewer packet contains images only, with no project context
