# Audio jack and microphone — result (Step 8)

> **Freshness:** ⚪ draft · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** luna 8.2 ⏳

**Status:** draft. Updated 2026-10-11 after 8.2c: the codec-configuration hypothesis is ruled out (see the end). Still pending: the user's optional checks. Desk analysis done on 2026-10-09 (sub-step 8.1b, decided by Professor on the user's behalf, D2). Nothing on the card, overlays or boot partition was changed.

**Question:** Is Luna's 3.5 mm jack headphones only, or headphones + microphone (4-pole headset)? Is there a built-in microphone? Mycroft's speech input depends on the answer.

## Short answer so far

- The **factory hardware description points to a 4-pole headset jack**: the headset's microphone line is wired to the codec, and also to an ADC that reads the headset's button.
- Under ArchR, **recording with a headset plugged in gives pure noise, identical to recording with nothing**.
- That fits a **software configuration difference rather than missing hardware**. ArchR's mainline codec driver sets the microphone input differently from the factory driver and never touches a register the factory driver sets when recording starts (probably the microphone bias, unconfirmed).
- **Not yet proven.** The user's physical checks and a live register reading are still needed.

## What was measured (live, read-only, 2026-10-09)

Test: `test/luna/test_audio_jack_record.py` (Gherkin `test/luna/audio_jack_record.feature`), 5 s, `hw:0,0`, S16_LE, 48 kHz, stereo, mixer as ArchR left it (Master Capture 100 %, Mic Capture Gain 6 = 0 dB).

| Run | Plug | RMS L / R | Peak | DC offset |
|---|---|---|---|---|
| harness check | unknown | −61.1 / −60.3 dBFS | −39 dBFS | ≈ −340 |
| headset-speak (1) | 4-pole headset | −61.1 / −60.3 dBFS | −39 dBFS | ≈ −340 |
| headset-speak (2) | 4-pole headset, confirmed plugged | −61.1 / −60.3 dBFS | −39 dBFS | ≈ −340 |

Speech or tapping into a working microphone would add 20–30 dB or more. These runs show only converter noise. The timing of speech in runs 1–2 was not synchronised with the recording, which is why the tapping check is still needed.

Other live observations:

- **The capture chain is powered while recording.** ASoC DAPM debugfs shows `MIC Power On`, `MICL`, `MICR`, the boost stages, both PGAs and both ADCs `On` during capture, all `Off` at rest. ArchR doesn't leave the path switched off in DAPM.
- **Headphone detection always reads "inserted":** `Headphones Jack` = on; `evtest --query` exit 10; GPIO 86 (`GPIO2_C6`, "Headphone detection") reads high. This was before and after the headset was plugged, and whether the jack was empty during the first reading is unconfirmed.

## Factory versus ArchR

Sources:
- factory DTB: `worklines/luna/data/r36-ultra.dtb`;
- ArchR DTB: `rk3326-gameconsole-eeclone.dtb` from the ArchR image (kernel 6.12.94);
- drivers: mainline `sound/soc/codecs/rk817_codec.c` (torvalds master, 540 lines) and the Rockchip BSP `rk817_codec.c` (`rockchip-linux/kernel`, branch `develop-4.19`), the vendor driver family the factory image uses. ArchR's own kernel patches were not checked for changes to this driver.

| Aspect | Factory | ArchR |
|---|---|---|
| Sound card | `rockchip,multicodecs-card` | `simple-audio-card` `rk817-sound-amplified` |
| Headphone detect | `hp-det-gpio` GPIO2_C6, active-high | the same pin and polarity |
| Headset button | `io-channels` SARADC ch1 `adc-detect`; key-up 1.8 V; `play-pause-key` pressed below 2 mV | not described |
| Mic input mode | **single-ended** (no `rockchip,mic-in-differential`) | **differential** (`rockchip,mic-in-differential` on the codec node) |
| Mic routing in the card | the BSP driver's `Capture MIC Path` control: "Main Mic" or "Hands Free Mic" | no microphone widget or route; only Headphones and Speaker |
| On capture start | BSP writes `AMIC_CFG0 = 0x0a`, **`AMIC_CFG1 (0x28) = 0x30`**, `DMIC_PGA_GAIN = 0xaa` (+12 dB) | mainline sets only `AMIC_CFG0` bits through DAPM; **`AMIC_CFG1` is never written** (reset value 0x00); gain 0 dB |

### What this means

1. **The headset button points to a headset microphone line.** A headset button works by shorting the microphone line to ground. The factory ADC sits at about 1.8 V when idle and calls anything under 2 mV a press. That is exactly how a microphone line pulled up by its bias behaves. So the jack's 4th contact is very probably wired, and a template copied from Rockchip's reference board is the less likely explanation.
2. **Which channel carries which mic (BSP, single-ended mode):**
   - "Main Mic" keeps the **left** ADC and mutes and powers down the right one;
   - "Hands Free Mic" (the headset) keeps the **right** ADC and mutes the left one.

   So on the factory board, the headset microphone very probably arrives on **MICR / the right channel**. Whether a built-in "main" microphone is fitted on the left is not shown: the BSP offers both paths on every board.
3. **ArchR forces differential mode.** In differential mode the codec measures the difference between a P and an N pin. A single-ended headset microphone wired as on the factory board may then cancel out or never reach the converter. `rockchip,mic-in-differential` comes from ArchR's generic "R36S clone" description and may simply be wrong for this board.
4. **ArchR probably never switches on the microphone bias.** The factory driver writes `AMIC_CFG1 = 0x30` when recording starts, and mainline never touches that register. Its bit meaning is not documented in either driver. If it holds the microphone bias enable (a common layout), a headset's electret microphone gets no power under ArchR and records exactly the flat noise we measured. **This is a hypothesis.** It can be checked by reading register 0x28 live, and by measuring DC on the jack's microphone contact during a recording.

Either 3 or 4 alone would explain the flat recordings. Neither has been tested on the device yet.

## Still to do

| Check | Who | What it settles |
|---|---|---|
| Unplug the headset and re-read GPIO 86 / `Headphones Jack` | user (physical) | whether detection works or is stuck |
| Tap or scratch the headset mic continuously while recording | user + agent | rules out speech timing |
| Read codec registers 0x27 and 0x28 (regmap debugfs) and SARADC ch1, at rest and during capture | agent, read-only, when Luna is back online | whether bias is set; the mic-line voltage seen by the button ADC |
| Multimeter between the jack sleeve and ring 2 during a recording | user, optional | whether bias reaches the jack |
| `none-speak` condition | user + agent | whether a built-in mic exists |

**A possible fix, needs a green light, not tonight:** a device-tree overlay that removes `rockchip,mic-in-differential` and adds a microphone widget and route for the right channel. If the bias register is confirmed, a one-line runtime write to `AMIC_CFG1` could be tried first (reversible at reboot) to prove the point before any driver or overlay work. Either way, this would be a new sub-step.

## Live register check (8.2b, 2026-10-11, read-only)

`test_codec_and_mic_line_snapshot`, evidence in `results/luna/audio-jack/20261011T224723_snapshot/` (`rest.txt`, `capture.txt`). Jack empty.

| Register / signal | At rest | During capture | Factory BSP during capture |
|---|---|---|---|
| `AMIC_CFG0` 0x27 | 0xf0 | **0x8c**: bit 7 differential on; mic and PGAs powered; boosts 1 and 2 | 0x0a (single-ended) |
| `AMIC_CFG1` 0x28 | 0x00 | **0x00** | **0x30** |
| `DMIC_PGA_GAIN` 0x29 | 0x66 | 0x66 (0 dB) | 0xaa (+12 dB) |
| `AADC_CFG0` 0x18 | 0xc8 | 0x08 | 0x08 |
| `Headphones Jack` / GPIO 86 | off / low | off / low | — |
| SARADC ch1 (headset-button line) | ≈ 508/1023 (≈ 0.89 V) | ≈ 502–517 | key-up threshold 1.8 V |

What this settles:
- **Jack detection works.** It reads off and low when the jack is empty; the earlier "always inserted" readings had a plug in.
- **ArchR records in differential mode and leaves `AMIC_CFG1` at 0.** Both differences from the factory driver are now register facts, not inferences.
- **Still unproven:** that either difference is what silences the headset microphone. That is the point of 8.2c, a runtime write reset at reboot, which needs the user's green light. The 0.89 V on SARADC ch1 with the jack empty is noted but not interpreted; it may be a divider or a floating input.

## Runtime register trial (8.2c, 2026-10-11, user-approved)

Luna was held exclusively (granted by Professor), with the user tapping the 4-pole headset microphone throughout. The codec registers were written over I2C (`i2cset -f -y 0 0x20 …`) during a 10 s recording, then restored, and Luna was rebooted.

| Trial | Phases (≈ 2.4 s each) | RMS L / R, all phases |
|---|---|---|
| 1 (`20261011T225901_trial-8.2c`) | as-is (0x27 = 0x8c); `AMIC_CFG1` = 0x30; plus single-ended (0x27 = 0x0c); single-ended alone | −73 to −79 dBFS |
| 2 (`20261011T230033_trial-8.2c-factory`) | as-is; **factory exact** (0x27 = 0x0a, 0x28 = 0x30, 0x29 = 0xaa); 0x27 = 0x0e; 0x27 = 0x02 | −72 to −78 dBFS |

Every write was read back. The noise floor moved by a few dB between phases, so the writes did reach the analogue front end. No phase showed the tapping, which would have been tens of dB above the floor.

Apart from playback-only registers, every capture register the factory BSP writes now matches either ArchR's own value (0x13, 0x17, 0x18, 0x1e, 0x30, 0x42, 0x49, 0x4a, 0x4c, 0x4f, compared during capture in 8.2b) or the trial's value (0x27, 0x28, 0x29).

**Conclusion for now:** with the RK817 codec set as the factory driver sets it, the jack's microphone still gives nothing. So **the codec configuration is not what silences it**, which rules out the 8.1b hypothesis. Two possibilities remain:

1. the jack's 4th contact doesn't reach the RK817 microphone inputs, which matches the user's reading that the jack is output only;
2. the headset's wiring standard (CTIA/OMTP) doesn't match the jack's. This is unlikely to explain everything, because the user's microphone-only plug failed too.

Supporting this, SARADC ch1 (the factory headset-button line) reads the same ≈ 508/1023 with the headset plugged and the jack empty. The factory button description may be leftover from the reference design.

Not tried, and not worth doing before a USB-C microphone is tested:
- a full factory EmuELEC capture test on a spare card;
- a multimeter check for microphone bias on the jack.

**Practical outcome:** use a **USB-C microphone** for Mycroft (8.2d).

## USB-C headset (8.2e, 2026-10-13): a working microphone

| Item | Value |
|---|---|
| Device | TTGK "LUDOS Earphones", USB 3302:3b77, plugged straight into Luna's USB-C port |
| ALSA | card 1 `Earphones`; capture `hw:1,0` = `/dev/snd/pcmC1D0c`; stable name `hw:CARD=Earphones,DEV=0` |
| Capture format | S16_LE, 2 identical channels (mono microphone), 48 kHz only |
| Mixer | `Headset` capture 120/120 (0 dB), on, as found |
| Silent | −65.6 dBFS RMS, peak −48.6 dBFS (`20261013T221752_usb-silent`) |
| Speaking | −43.5 dBFS RMS, peak −10.0 dBFS (`20261013T221801_usb-speak`): **+22 dB** |
| After a reboot | still card 1, enumerated at boot |

**Conclusion of Step 8:**
- **Luna's 3.5 mm jack gives no usable microphone under ArchR,** even with the codec set exactly as the factory driver sets it (8.2c).
- **A USB-C headset with its own converter works out of the box** (`snd-usb-audio`).
- **Mycroft's input on Luna should be a USB audio capture device**, chosen by name (`CARD=Earphones` for this headset) rather than by number, since the card index depends on what is plugged in.
- **The user's earlier USB-C-to-jack adapter** was passive or a hub, and showed no audio device (8.2d).
