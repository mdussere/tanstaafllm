Feature: Mycroft on Luna (plan Step 8)
  First memory and CPU figures for the dictation provider on the real device.
  Executed by test/mycroft/test_luna_footprint.py (marker: live; needs
  MYCROFT_LUNA_LIVE=1, MYCROFT_ASSET_ROOT, and a Luna slot arranged through
  Professor). Evidence goes to results/mycroft/luna-footprint/<timestamp>/.

  Background:
    Given Luna answers on "ssh luna" through one multiplexed connection
    And nothing outside /storage is changed and no package is installed

  Scenario: Step 8.1 — read-only preflight
    When Mycroft reads Luna's architecture, Python, glibc, libstdc++, free memory and free space on /storage
    Then Luna is aarch64 with python3, and /storage has room for the bundle
    And the full preflight output is saved

  Scenario: Step 8.1 — install the bundle
    Given the prebuilt aarch64 Sherpa libraries, the model's int8 files, tokens, one public WAV, and the scripts
    When files whose SHA-256 differs on Luna are streamed there
    Then every file on Luna matches its local SHA-256
    And the assets are under /storage/.local/opt/mycroft and the scripts under /storage/.local/share/tanstfaafllm/mycroft

  Scenario: Step 8.1 — measure the provider replaying a public WAV
    Given Luna was rebooted and its load has settled, when MYCROFT_LUNA_REBOOT=1
    When the probe runs mycroft_dictate.py three times on the public WAV
    Then every run ends with a non-empty "final" and exit status 0
    And each run's peak RSS, CPU time, model load time, first-partial time and lag after the audio are saved
    And Luna is rebooted again at the end when MYCROFT_LUNA_REBOOT=1

  # Steps 8.2–8.4 and 8.6 (user decisions of 2026-10-11, relayed by Professor).

  Scenario: Steps 8.2–8.6 — install the extra files
    Given Sherpa's prebuilt aarch64 C++ binary (same libraries as the installed ones), the "onnx-extended" pre-optimised model, and the probe scripts
    When files whose SHA-256 differs on Luna are streamed there
    Then every file matches, and the variant root links to the installed runtime

  Scenario: Steps 8.2–8.4 — threads, load time and pre-optimised model, compiled binary
    Given Luna was rebooted and its load has settled, when MYCROFT_LUNA_REBOOT=1
    When the Python load profile runs once with a dropped page cache, then twice each at 1, 2 and 4 threads
    And Sherpa's C++ binary decodes the same WAV twice each at 1, 2 and 4 threads
    And mycroft_dictate.py replays the WAV in real time twice each at 2 and 4 threads
    And the "onnx-extended" model is loaded twice at 1 thread
    Then the read, library-load, session-creation and decode times, the real-time factor, peak RSS and CPU time are saved for every run
    And Luna is rebooted at the end

  Scenario: Step 8.6 — resident provider under memory pressure, and swap support
    Given Luna was rebooted and its load has settled, when MYCROFT_LUNA_REBOOT=1
    When the swap and zram support of Luna's kernel is read without changing anything
    And a resident provider loads the model once, decodes, then decodes again while another process holds memory down to 150 MiB available, and once more after it is freed
    Then its anonymous and file-backed memory at each stage, and the three decode times, are saved
    And Luna is rebooted at the end

  Scenario: Step 9.3 — the Kroko French model on Luna
    Given Kroko's four model files and its public test clip are installed under /storage/.local/opt/mycroft, checked by SHA-256
    And Luna was rebooted and its load has settled, when MYCROFT_LUNA_REBOOT=1
    When Sherpa's C++ binary decodes the public clips twice each with Kroko at 1 and 2 threads, and with the current model at 2 threads
    Then load time, decoding time, real-time factor, peak RSS and CPU time are saved for every run
    And Luna is rebooted at the end

  Scenario: Step 9.8 — resident provider with the prepared Kroko
    Given the prepared Kroko files and the current scripts are installed under /storage/.local, checked by SHA-256
    And Luna was rebooted and its load has settled, when MYCROFT_LUNA_REBOOT=1
    When one resident provider (Kroko, 2 threads) loads once and serves three start/final cycles on the public clip
    Then its load time, idle and listening RSS, start-to-listening delay, first-partial time, lag after the audio, peak RSS and CPU time are saved
    And every cycle ends with a non-empty "final", and the provider exits with status 0
    And Luna is rebooted at the end
