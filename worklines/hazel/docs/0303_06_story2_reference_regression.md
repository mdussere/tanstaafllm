# Story 2 regeneration audit — why Story 3 lost the series language

> **Date:** 2026-11-04 · **Workline:** Adam → Hazel · **Status:** 🟢 reference comparison performed; Story 3 redesign pending user approval · **No render of Story 3 requested here.**

## Reproducible experiment

A [dedicated GitHub Actions run #41869289272](https://github.com/mdussere/tanstaafllm/actions/runs/41869289272) succeeded on branch `cell/adam`, using independent builds of two representations **from the same current commit**:

1. **Reference:** `worklines/hazel/video/story2-ask-the-desktop/src/index.html` + **its own** `score.py`, a hand-directed 90-second film. The original was captured at 1920×1080 / 10 fps and downscaled to 640×360 for comparison; this is a regeneration, not the historical uploaded MP4 byte-for-byte.
2. **Generic rebuild:** `worklines/hazel/video/episodes/story2-ask-the-desktop.yaml` compiled with `video/common/build.py`, 640×360 / 10 fps, its **common** `cues.py` soundtrack. This is the current template implementation, **not** the hand-authored original.

[Download both MP4s, contact sheets and WAVs](https://github.com/mdussere/tanstaafllm/actions/runs/41869289272/artifacts/13342734940) (CI artifact retention seven days).

Both encode successfully, duration 90.0 s. Success means they are valid videos — **not that they represent the same composition**.

## Verified differences

### Story timeline and narrative

| Time (s) | Original hand-authored | Current generic YAML |
|---|---|---|
| 0–14 | Title + Wyoh player. Same core arcade identity, detailed actor portrait. | Recognizably similar title and player composition. |
| 14–20 | Stage 1 screenshot trap; first line and guesses. | Similar stage but generalized motion and cue timings. |
| **20–28** | **Stage 2 HIOM: “one scene is not a desktop”, reopened**, and the explicit wait-for-event lesson. | **“Like Playwright, for a desktop”** table inserted instead. |
| 28–44 | Stage 3 Sway and measured IPC, followed by Stage 4 MCP. | HIOM becomes Stage 3, Sway Stage 4, MCP Stage 5: **several stages shifted**. |
| 44–62 | Black GPU panel boss, then physical buttons / virtual gamepad. | Boss and handheld material shifted later. |
| **62–72** | **Seven layer trap**: green checks 1–6 are insufficient; only last layer proves repair. | This stage is **missing**; the recompilation moves directly to payoff. |
| 72–90 | Payoff, victory, end card. | Same broad payoff, victory and end-card beats and font/palette family. |

**Conclusion:** even the original Story 2 story is not faithfully reproduced by the common script. Its apparent 90-second duration can obscure dramatic omissions and a structural reorder. Making Story 3 from standard layouts cannot recover the source video's narrative craft automatically.

### Visual composition

- The titles, Press Start 2P/VT323, starfield/Moon, key-art portrait, violet/cyan/amber palette and `CLEAR!` stamps **are** recognizable between the versions. **Reuse these as identity, not as whole-story formula.**
- The original uses **scene-specific actions** (spilling windows, named waits, exact black-to-lit boss phase, virtual gamepad, seven-layer contradiction), not just a label and a template.
- A `--strict` or phone readability pass is **not a test of original timing, framing or story equivalence**.
- Restore the original T01 title/opening and T23 end-card, select the punchy arcade stage transitions, but keep the newer **small Hazel animated vignette** for explicitly physical actions.

### Sound / musical storytelling

The original `score.py` and modern `common/cues.py` share 2A03-inspired synthesis primitives, 120 BPM and some thematic vocabulary, **but are not the same score**.

Objective comparison of regenerated WAVs (90 s, decoded as mono in analysis):

- Original `hits.json`: **88** labeled events, often naming story beats (e.g. `window spills`, `STAMP ASK THE DESKTOP`, `guess (a coin)`, `ON PAPER: A DOM`, `CLEAR!`).
- Scripted `hits.json`: **93** events, many generic template markers (`enter`, `key`, `second`, `NO GO!`).
- Direct corresponding PCM sample correlation: **~0.017**. This shows that the waveform is *not the same music track*; it does not by itself measure artistic quality or rhythmic energy. Also sample timing, synthesis and scene reordering matter.
- Audio loudness is relatively close overall, so the complaint is better understood as **missing musical narrative orchestration and timed accents**, not simply volume or lack of drums.

**Recommendation:** use the actual original Story 2 / trailer score motifs, intro fanfare, syncopated drive, failure buzz, stamp and level-clear transitions as source vocabulary. Compose a **new story-specific score with event cues per shot** rather than a continuous underscoring loop or the default common T24 groove. A score that contains 90 seconds of music is not equivalent to 90 seconds of music-driven storytelling.

## Decision for Story 3 V3

1. Preserve the user-approved layout: Hazel within **≤50% of image area**, her feet anchored to the bottom of the vignette, explanatory board beside/below. This is a strong **partial** result and should not be discarded.
2. Allow **at least three types of camera framing**: close-ups on coin/film reel/cartridge, smaller Hazel/prop staged vignette, full-width retro title/reveal. One frame family everywhere makes another slide deck.
3. Rebuild the sequence transitions around **explicit named events**, with stage changes on bar boundaries, flash or block-dissolve, strong stinger / musical shift, not mere alpha fade.
4. Track the actual narrative through the shots: initial €20 monthly subscription, surprise first trailer, flawed phone viewing, repeated costly handmade production, **first** template rationalization, **then** YAML automation, and the self-referential estimated two-film payback.
5. **Stop at preview** pending user approval. No master Full HD, merging to main, or publication.

## Evidence versus limits

This audit compared newly built **original source vs modern YAML source**, not the original YouTube upload against a local video. The original `NOTES.md` confirms seven layers and exact event timing, and the regenerated pictures confirm their absence/reordering in the YAML. The difference was observed, not inferred from the file names.

The original and scripted videos, audio and contact sheets can be downloaded as a single GitHub artifact while retained. A local side-by-side contact sheet was also made in Adam's ChatGPT session.
