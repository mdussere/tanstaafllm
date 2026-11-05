# Story 3 — visual concept exploration: two new directions per sequence

> **Status:** ⚪ conceptual exploration — **not** a sub-agent execution result · **Written:** 2026-11-04 · **Workline:** Hazel 3.3 · **Review:** Hazel + Adam
>
> **Authoring note:** This first 26-concept brief was drafted by Adam's ChatGPT session. No autonomous sub-agent invocation is available from this session. A separate creative-review assignment for a Hazel sub-agent is needed before treating these as agent-selected concepts.
>
> **Scope:** Markdown only. No YAML changes, no template implementation, no rendering, no approval of the final edit.

## Why the first cut failed

The first rendered Story 3 is **too close to the generic Story 2 visual vocabulary**: comparison tables, flow diagrams, boxes, HUDs, stamps and metric tiles. Those are suitable for explaining software components, but Story 3 is an introspective film about *making a film*, and needs concrete mise-en-scène, artifacts of production, movement and visual irony. A recurring table is not a visual idea.

**Direction:** treat the story as a movie about a little arcade-game studio, not a slide deck about a build pipeline. Show the **same film-making protagonist and physical objects** across sequences: Hazel at her workstation, a stack of film reels, a storyboard wall, a game cabinet, a clock/coin counter, an editing table. The audience sees changes in the workshop. Abstract concepts should appear as events or objects with physical consequences.

## Creative boundaries

- 13 sequences in the present 112-second cut; proposals are **alternatives**, not 26 templates that must all be built. Pick one direction per sequence, then rationalize into a smaller family of reusable cinematic patterns.
- For each candidate give a **visual metaphor, staging/animation, text beat and sound cue**. A card should remain understandable with the audio muted, on a phone, without a voice-over.
- Avoid the current generic `compare_table`, `flow`, `two_boxes`, `metrics`, `template_wall`, `payback_meter` when they feel like dashboards. No mandatory HUD on every shot.
- Keep the NES pixel-art/CRT world and shared palette, but **vary camera language and framing**: extreme close-up, tracking shot, overhead editing desk, silhouette, split-screen, diegetic game screen, recursive zoom.
- One main phone-readable line; at most one secondary. Do not use tiny labels to carry essential facts.
- The underlying facts must be honest: €20 is a subscription budget, not per-token metered API billing; 290k handmade full-episode vs 54k scripted revision is **not a comparable benchmark**. The ~1.73-video payoff is a playful estimate, not yet measured.
- **Do not reveal that the viewer is watching the second compiled video until the final payoff.** The Story 3 working title and early cards must not telegraph it.

## 01 · Title — “Insert coin” (6 s)

**A — Coin into the film projector.** Macro pixel shot of a coin slowly turning: one side reads `INSERT COIN`, the other has a tiny movie-frame perforation. It falls into a battered arcade projector, which lights up a reel and begins to cast the Moon onto a wall. **Text:** “WHO MAKES THE FILM?” appears on the wall as part of the projection. **Sound:** one coin clink, motor spin-up, and theme emerging through a lo-fi filter. **Reusable pattern:** `object_wakes_world`.

**B — The camera leaves the game.** Begin inside familiar TANSTAAFLLM gameplay. The camera pulls back to reveal a CRT screen on Hazel's cluttered editing desk. A character is watching the same trailer the audience expected to watch. **Text:** “INSERT COIN” becomes a reflection in the glass rather than a title overlay. **Sound:** established series motif becomes thin CRT speaker audio, then a room-tone synth pulse. **Reusable pattern:** `screen_to_workshop`.

## 02 · Constraint — one €20 Claude Pro subscription (8 s)

**A — A single coin purse for the whole studio.** Overhead view: Hazel sits at a wooden/metal editing desk with *one* little purse labelled `€20 / MONTH`. Six agent hands reach for coins to power different projects, but the purse has only one clasp. Hazel closes it, choosing priorities. **Text:** “ONE SUBSCRIPTION. THE WHOLE CELL.” **Sound:** nervous alternating coin clicks, then a deliberate latch. **Reusable pattern:** `scarce_shared_resource`.

**B — The arcade's electricity meter.** A row of arcade cabinets comes to life; the camera pans across games for Luna, Mycroft and Wyoh. Every screen draws power from **one shared wall socket** marked `CLAUDE PRO / €20`. The last cabinet is the movie-making cabinet itself, whose plug unexpectedly joins the power strip. **Text:** “THE MOVIE COSTS TOO.” **Sound:** multiple game boots compete for one bass line; a breaker tick ends the shot. **Reusable pattern:** `shared_power_reveal`.

## 03 · First trailer — surprising creative leap (8 s)

**A — The brief becomes an arcade cabinet.** Hazel feeds a small folded `README + DOCS` envelope into a machine labelled `MAKE A TRAILER`; instead of sheets of instructions, a miniature arcade cabinet grows from it, speakers and all. **Text:** “WE ASKED FOR A TRAILER.” / “IT BUILT A GAME.” **Sound:** printer rattle → escalating arpeggio → coin chime. **Reusable pattern:** `brief_to_world`.

**B — Empty storyboard gains a mind.** A completely blank storyboard wall. Without an artist's hand, frames pop in one by one: moon, character silhouettes, coin slot, declaration of independence. The camera catches Hazel looking from blank clipboard to finished scene. **Text:** “NO STORYBOARD.” / “A WORLD APPEARED.” **Sound:** rhythmic pencil taps morph into 2A03 melody. **Reusable pattern:** `storyboard_materialization`.

## 04 · First toolchain — deterministic frames and NES audio (8 s)

**A — The clockwork projector.** Side cutaway of a clockwork machine: an advancing clock face labelled `t` drives a film strip on one axle and a little 2A03 sound chip on the other; two gears mesh precisely and a finished MP4 reel emerges. **Text:** “ONE CLOCK.” / “PICTURE + SOUND.” **Sound:** perfectly synchronized gear tick and notes on the same half-second pulse. **Reusable pattern:** `clockwork_cutaway`.

**B — Film-strip / piano-roll dance.** A tracking shot follows a film strip overhead while NES note blocks run beneath it like a player-piano roll. A glowing cursor crosses image and sound at the same instant; the strip turns into a playable CRT frame. **Text:** “EVERY FRAME HAS A TIME.” **Sound:** audible note at each alignment flash, no explanatory graph. **Reusable pattern:** `time_synchronized_tracks`.

## 05 · First self-criticism — readability, pacing, retro sound (10 s)

**A — Giant phone in the screening room.** Hazel's triumphant first cut is projected onto a towering phone. The tiny text collapses into illegible confetti; an impatient finger pauses the video; a cartoon ear recoils from a too-modern soundtrack. Then the phone is laid horizontally on the edit desk and a red pen circles the problems. **Text:** “IT LOOKED GOOD HERE.” / “NOT IN YOUR HAND.” **Sound:** chiptune stops mid-phrase and an uncomfortable tape squeal. **Reusable pattern:** `real_device_reality_check`.

**B — Audience of one, ruthless notes.** Dark miniature cinema, one viewer at the back holding a phone. The picture glows, but subtitles shrink and cuts arrive before the viewer finishes reading. Three sticky notes fly from the seat and land on Hazel's projector: `READ`, `WAIT`, `80s`. **Text:** “FEEDBACK BEATS APPLAUSE.” **Sound:** applause blip is abruptly replaced by a single pencil tap. **Reusable pattern:** `feedback_hits_workbench`.

## 06 · Measurement — learning to audit the film (10 s)

**A — Film inspection table.** Overhead film editor with a magnifying glass. Hazel slides the footage under three physical tools: a phone-size stencil, a stopwatch and a sound-wave strobe; each exposes an invisible defect. As adjustments are made, little red holes in the film become green registration marks. **Text:** “A MISTAKE BECOMES A TEST.” **Sound:** click / tick / tone, precisely timed to each tool. **Reusable pattern:** `inspection_station`.

**B — Rhythm game judges the video.** Turn footage into a rhythm-game lane: text blocks must survive long enough to cross the reading gate, visual cuts must land on a bar, and sound hits must overlap their marks. Missing a gate generates an unmistakable miss, not a badge. **Text:** “MAKE THE RULES EXECUTABLE.” **Sound:** timing-hit arpeggio for pass, muted thud for fail. **Reusable pattern:** `beat_audit_game`.

## 07 · Costly habit — hundreds of lines rewritten (10 s)

**A — Sisyphus at a pixel editing desk.** Hazel is pushing a huge roll of handwritten frame code uphill to a projection booth. At the top, the reel plays six seconds; the cut reveals an identical mountain and another reel labelled `NEXT EPISODE`. **Text:** “SAME WORK. AGAIN.” **Sound:** laboured bass ascent; the riff loops exactly at the reset. **Reusable pattern:** `repetitive_labour_loop`.

**B — The copy machine grows teeth.** A small copier duplicates a scene. Every copy reproduces not only the frame but also the tiny unreadable text and wrong music hit. The copies become a marching, threatening parade toward Hazel's chair. She pulls the plug. **Text:** “COPYING KEEPS THE BUGS.” **Sound:** each copy adds an increasingly unpleasant dissonant note. **Reusable pattern:** `defect_replication`.

## 08 · Manual rationalization — library and renewal rule (10 s)

**A — Scene-pattern workshop.** Hazel cuts useful parts from discarded film reels with a splicer, lays them into reusable **physical cartridges**, and slots them into an organized wooden rack. When preparing the next film, she composes existing cartridges **but must forge one empty, glowing cartridge of her own**. **Text:** “REUSE THE PATTERN.” / “INVENT ONE NEW ONE.” **Sound:** clean splice snaps, then a fresh melodic phrase for the new cartridge. **Reusable pattern:** `pattern_cartridges` (new candidate).

**B — The arcade level editor.** Show a side-scrolling platform editor on a giant drafting monitor: previously hand-built platforms are replaced with reusable tiles. A new episode is rearranged freely, but its final slot is a question-mark tile that **must be designed before the level unlocks**. **Text:** “OLD TILES. NEW LEVEL.” **Sound:** satisfying placement blips, silence at the locked slot, new motif on unlock. **Reusable pattern:** `level_editor_with_novelty_gate` (new candidate).

## 09 · Instrumentation / automation — YAML compilation (8 s)

**A — The recipe becomes a factory.** A tiny **legible** YAML recipe card enters a film-making press. Distinct stations stamp scene timing, draw canvas frames, score NES notes, inspect readability and join audio to MP4. The machines are the previously built templates; Hazel only changes the recipe. **Text:** “THE SCRIPT CHOOSES.” / “THE MACHINE BUILDS.” **Sound:** five distinct mechanical beat-synced stations, then one final encoded chime. **Reusable pattern:** `recipe_to_artifact_factory` (new candidate).

**B — Conductor, not a typist.** The same Hazel who used to play every instrument and draw every frame now stands before a mini arcade orchestra. Her YAML sheet music makes the clock, editor, NES synth and encoder play together; she conducts **choices**, not individual notes. **Text:** “WE STOP REDRAWING.” / “WE START DIRECTING.” **Sound:** silence, then separate voices enter on each bar, resolving as one theme. **Reusable pattern:** `orchestrated_compilation`.

## 10 · Economics — compare work without pretending identical scopes (8 s)

**A — Two piles of receipts, not two identical products.** An edit desk holds an enormous invoice labelled `HANDMADE FULL EPISODE ~290K` and a smaller one labelled `SCRIPTED REVISION ~54K`. A magnifying glass enlarges the words **FULL EPISODE** and **REVISION** so the audience sees the caveat. Hazel moves both into a folder labelled `ESTIMATE`, rather than displaying a fake apples-to-apples win. **Text:** “LESS HANDWORK.” / “MEASURE THE NEXT FILM.” **Sound:** two register dings in distinct registers, followed by an unresolved chord. **Reusable pattern:** `honest_receipts`.

**B — A timer with different starting lines.** Two runners take off from different lines on a racetrack: one starts with blank code and must build a full movie; the other starts with existing templates and only revises scenes. The camera pulls up to reveal **different courses**. **Text:** “A PROMISING SIGNAL.” / “NOT YET THE SAME TEST.” **Sound:** two tempos, dissonant until the camera reveals the asymmetry. **Reusable pattern:** `comparison_caveat_reveal`.

## 11 · Payoff — the film catches itself (12 s)

**A — Recursive projector / second reel.** A projector shows the story we have just watched. The camera pulls behind the screen to reveal a second projector whose film reel is labelled `STORY 3`, **currently being assembled by the machines from sequence 09**. Only now does the viewer understand this is the second script-built movie. The image recursively contains itself for one beat, then the machine stamps `PAID BACK? ~1.73 USES*`. **Text:** “YOU JUST WATCHED IT HAPPEN.” **Sound:** theme turns inside out (countermelody in retrograde), then a satisfying stamp. **Reusable pattern:** `recursive_self_reveal` (new candidate).

**B — Arcade “second credit” secret ending.** A classic `CONTINUE? 1 CREDIT` screen appears. One credit is already spent on Story 2. A second coin drops; instead of launching another game, the camera zooms into the falling coin and reveals tiny frames of **this very video** being compiled inside it. `2 / 2` flashes, then `YOUR SCREEN IS THE PAYBACK`. **Text:** “SECOND FILM.” / “THIS FILM.” **Sound:** distinct second-coin motif resolves the previous unfinished melody. **Reusable pattern:** `second_credit_twist` (new candidate).

*Accounting rule for either variant:* the ~1.73 break-even comes from ~408k ÷ (~290k − ~54k), but **the 54k is a revision and the 290k a complete handmade production**. Until a complete scripted film is measured, avoid declaring a real measured repayment. If the humorous stamp uses `PAID BACK`, annotate it as a narrative projection, not audited accounting. This reveal should be the last major story beat, not followed by an explanatory conclusion that spoils its force.

## 12 · Result / synthesis (8 s)

**A — Hazel leaves the editing bench.** The workshop is now quieter: tools are in labeled places, a visible `TESTS` lamp glows, and the editing bench is empty of repetitive code sheets. Hazel picks up a pencil and moves to a **blank storyboard**: the human-facing creative work still needs decisions. **Text:** “AUTOMATE THE REPEATED.” / “KEEP THE CHOICE.” **Sound:** machinery fades, a single confident melody remains. **Reusable pattern:** `craft_returns_to_author`.

**B — A reel marked “LESSONS” becomes a tool.** Each earlier failure briefly flashes as a scar on a battered reel, then that scar turns into a calibration notch, template index or test ruler. Hazel winds the reel onto the projector; it runs smoothly this time. **Text:** “MEMORY IS WHAT WE CHANGE.” **Sound:** each converted failure resolves one note in a rising chord. **Reusable pattern:** `failure_to_instrument`.

## 13 · End card / return to motto (6 s)

**A — Credits on a resting arcade cabinet.** The game cabinet from 01 goes dark; under its glass, the Moon still glows faintly. The title appears not as a reused end card but as **engraving on the metal coin return**: `THERE AIN'T NO SUCH THING AS A FREE LLM`. One last coin remains in the tray. **Sound:** theme ends with an actual coin returning, not a victory fanfare. **Reusable pattern:** `quiet_coin_return`.

**B — The studio lights go out, one at a time.** Tracking shot across the now-idle tools: film splicer, phone stencil, clockwork projector, YAML card, second reel. Each switches off on a beat until only the Moon is illuminated through the window. The motto is revealed in silhouette. **Sound:** the five instrumental voices shut down one by one until one soft pulse remains. **Reusable pattern:** `closing_the_workshop`.

## Proposed selection strategy (not an approved edit)

The first cut wants a **new visual grammar**, not just new names for the old charts. Suggested coherent visual direction for creative review:

- **Workshop / physical movie-making:** 01A · 02A · 03B · 04A · 05B · 06A · 07B · 08A · 09A · 10A · 11A · 12A · 13A.
- **Arcade / meta-game:** 01B · 02B · 03A · 04B · 05A · 06B · 07A · 08B · 09B · 10B · 11B · 12B · 13B.

Neither should be used as an automatic all-A / all-B edit. Mix according to the actual film's visual arc and sound. The final cut should have **fewer** than 13 distinct template implementations: group related mechanics as reusable families. Two concepts per sequence is an exploration, not a requirement to implement 26 new assets.

## What a Hazel sub-agent should do next

1. Read Story 3's **editorial brief** and watch the first cut; **do not use its preexisting template choices as creative constraints**.
2. Challenge each pair above: keep, improve or replace concepts as necessary, and explain why it is a stronger *shot* rather than a diagram.
3. Check continuity of **Hazel's workshop and props**, the dramatic timing, legibility and NES musical architecture; protect the final reveal.
4. Return **only Markdown**, with per-sequence two concepts, a recommended direction, a minimal vocabulary of reusable template families and a list of needed art assets.
5. Do **not** modify generator code, YAML episode, existing template cards, or render video without Adam's subsequent go.
