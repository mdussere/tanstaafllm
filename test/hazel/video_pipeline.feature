Feature: The script-to-video pipeline builds Story 2 and checks it (Hazel Step 6)
  The generator turns an episode script into a page, a score, a reading
  audit, a layout lint and a contact sheet. The integration scenarios are
  executed by test_video_pipeline.py with Playwright's Chromium and ffmpeg;
  each saves the build's outputs (lint.txt, audit.md, contact.png, stills/)
  under results/hazel/video-pipeline/<timestamp>/.

  Scenario: Story 2 builds clean under --strict
    Given the committed script episodes/story2-ask-the-desktop.yaml
    When common/build.py builds it with --preview --no-video --strict
    Then the build exits 0
    And lint.txt reports no overflow, margin, overlap, CLEAR! zone or phone-rule problem
    And the contact sheet has one still per scene

  Scenario: The page and the generator agree on the end stamp and the holds
    Given a page built from Story 2, with reading holds added to its timeline
    When the page draws each stage's end stamp (CLEAR!, NO GO!, LET'S DO IT!)
    Then each stamp's recorded box lies inside the lint's CLEAR! zone for that label
    And for every sampled output time, runtime.js sourceTime equals timemap.source_time
