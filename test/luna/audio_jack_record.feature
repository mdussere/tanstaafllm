Feature: Find where Luna's microphone input is wired
  The factory device tree describes a headset button on the jack, but ArchR only
  reports headphone insertion. Recording under controlled conditions shows whether
  the codec hears a built-in microphone, a headset microphone on the jack, or nothing.

  Background:
    Given Luna is reachable as "ssh luna"
    And the capture mixer is left as ArchR configured it (nothing is changed)

  Scenario Outline: Record one condition
    Given the jack holds <plug>
    When the test prints "RECORDING" and the person <voice> for 5 seconds
    Then a 5-second stereo WAV is fetched from "hw:0,0" on Luna (usb-* conditions: "hw:1,0", or LUNA_AUDIO_DEVICE)
    And the jack switch state, the mixer state and arecord's output are saved
    And per-channel RMS and peak levels are saved to stats.json
      under results/luna/audio-jack/<timestamp>_<id>/

    Examples:
      | id              | plug                                | voice                        |
      | none-silent     | nothing                             | stays quiet                  |
      | none-speak      | nothing                             | speaks at the handheld       |
      | headset-silent  | a 4-pole headset with a microphone  | stays quiet                  |
      | headset-speak   | a 4-pole headset with a microphone  | speaks into the headset mic  |
      | headphones-speak| 3-pole headphones without a mic     | speaks at the handheld       |
      | usb-silent      | a USB-C headset (records on hw:1,0) | stays quiet                  |
      | usb-speak       | a USB-C headset (records on hw:1,0) | speaks into its microphone   |

  # Reading: a condition "hears" speech when its RMS is clearly above the matching
  # silent baseline. Only headset-speak loud means a headset jack with no internal mic;
  # none-speak loud means a built-in microphone.
