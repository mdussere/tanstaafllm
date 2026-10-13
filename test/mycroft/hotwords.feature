Feature: Known words (hotwords) on Mycroft's current model (plan step 9.1)
  The user wants a list of known words (their first name, component and game
  names) to be recognised without ambiguity. Executed by
  test/mycroft/test_hotwords.py (marker: integration; needs MYCROFT_ASSET_ROOT
  with bpe.vocab beside the model, MYCROFT_PIPER_VOICE pointing to a Piper French
  voice, and ffmpeg on the desk host).
  Evidence goes to results/mycroft/hotwords/<timestamp>/.

  Scenario: The same synthetic sentences decoded three ways
    Given French sentences containing Michael, Luna, Mycroft, Wyoh and Wolfenstein, spoken by Piper's French voice and converted to 16 kHz mono
    When each sentence is decoded with greedy search (today's setting)
    And with modified beam search alone
    And with modified beam search and the list of known words, at two boost scores
    Then every decoding finishes, and the transcripts and the count of known words found are saved per setting
    And the result shows whether the list helps, beyond the change of decoder
