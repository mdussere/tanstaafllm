# Sound output on Luna — result (Step 9)

> **Freshness:** 🟡 historical · **Written:** 2026-11-10 · **Checked:** 2026-11-10 · **Step:** luna 9.2 ✅

**Question (Adam, via Wyoh, 2026-11-10):** why is there no sound at all on Luna, neither Mike's voice (Piper, `mycroft_speak.py`) nor Wolfenstein 3D (ecwolf, SDL)?

**Short answer:** the hardware works. Card 0, the RK817 codec, routes playback to the headphone output (`Playback Mux = HP`) even with the jack empty, so the built-in speaker gets nothing. The master volume is also low (201/255, about −20 dB). With the mux on `SPK` and the volume at 255, Adam heard the speaker loud. The USB-C headset already plays, and very loudly.

## Setup found (read as `michael`, Arch Linux ARM root, kernel 6.12.94)

| Item | State |
|---|---|
| Sound server | none: no PipeWire, no PulseAudio; plain ALSA (`alsa-lib`/`alsa-utils` 1.2.16), `sdl2-compat` |
| ALSA config | no `/etc/asound.conf`, no `~/.asoundrc`; the ALSA default is card 0 |
| Card 0 `rk817ext` | `Playback Mux` = **HP**; `Headphones Jack` = off (jack empty); `Internal Speakers Switch` on; `Master Playback Volume` **201/255** (−95…0 dB scale) |
| Card 1 `Earphones` (USB-C headset) | `Headset Playback Switch` on, `Headset Playback Volume` **120/120 (0 dB)** |
| Access | `/dev/snd/*` is `root:audio`, and `michael` is in `audio` |

## Listening tests (Adam at the device)

Evidence is in `results/luna/sound-output/20261110T22*`. The mixer was changed only for each tone, then restored to `HP`/201.

| Tone | Output | Adam heard |
|---|---|---|
| 440 Hz | speaker, settings as found (`HP`, 201) | nothing |
| 660 Hz | speaker, `SPK`, 201 | yes, very quiet |
| 660 Hz | speaker, `SPK`, **255** | **yes, loud** |
| 880 Hz | USB headset, 120/120 | yes, very loud |

Only one ear on the first runs was an artefact: `speaker-test` plays the left, then the right channel (about 2.5 s each), and the first tones were cut off after 3 s.

## Fixes, for Mannie (system configuration is Mannie's)

1. **Speaker by default:** set `Playback Mux` to `SPK` and `Master Playback Volume` near the top (Adam found 255 loud), and persist the state (for example `alsactl store`, restored at boot by `alsa-restore.service`).
2. **Follow the jack:** switch `Playback Mux` to `HP` when `Headphones Jack` turns on, and back to `SPK` when it turns off. Nothing on the new root does this; the jack detection itself works (Step 8.2b).
3. **USB headset:** the ALSA default stays card 0, so Piper and ecwolf ignore a plugged headset. If Adam wants sound to follow the headset, an `/etc/asound.conf` (or a sound server) should select `CARD=Earphones` when it is present. Its volume at 0 dB is very loud, so start lower.
