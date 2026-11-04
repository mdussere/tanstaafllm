# Story 3 — modular asset production plan

> **Status:** ⚪ proposed, awaiting Adam/Hazel art-direction approval · **Written:** 2026-11-04 · **Step:** Hazel 3.3 · **From:** Adam / ChatGPT · **Scope:** planning only
>
> **Input:** [Story 3 editorial brief](0303_01_insert-coin-video-production-story-brief.md), [26 visual concepts](0303_02_story3-two-concepts-per-sequence.md), [existing series rules](0103_01_series-template.md), [Hazel renderer](../video/common/README.md).
>
> **Explicitly not done:** no generated images, no renderer/YAML edit, no finished asset pack, no upload or publishing. This document is the proposed contract for the next production step.

## 1. Design hypothesis: assets are not templates

The first cut looked like an animated software presentation because its reused templates tightly coupled dramaturgy, shape drawing and content. Introduce three independent layers:

1. **Asset** = a transparent sprite, an environment plate, a foreground occluder, or a nonvisual effect mask, with a stable origin/pivot and rights metadata.
2. **Composition template** = reusable arrangement of named slots, z-order, camera framing, staging and timing, with **no hard-coded plot-specific image or caption**.
3. **Scene script** = references to assets, template, text, data and music cues. The writing agent specifies *what happens*, the template specifies *how the shot is staged*, the CPU renders the frames.

An episode may add a new asset without needing new code. It should add a new template only if the **visual grammar/animation logic** is genuinely new. Keep the series' renewal rule (at least one new template or reviewed new variant per episode), but do not artificially invent one renderer function for each of the 13 Story 3 scenes.

**Visual protagonist:** the same Hazel sprite, projector, reel, editing desk and coin recur from the first through the last shot; this continuity should replace repeated generic HUDs as the series' identity.

## 2. Visual bible, version 0

| Property | Proposed constraint / reason |
|---|---|
| Frame | 1920×1080, 16:9; safe for final 640×360 phone preview |
| Visual language | Pixel-art/1990s point-and-click adventure meets arcade sci-fi; *consistent source pixel grid*, crisp hard edges, restrained CRT treatment |
| Pixel density | Choose **one master virtual stage**, e.g. 960×540 at 2× nearest-neighbor, and generate foreground cutouts at that logical scale. This is a **proposal** to test against Hazel's current 1920-native canvas; don't silently switch the global renderer |
| Palette | Reuse the engine palette tokens (ink, navy, violet, amber, cyan, green, red, chrome); sprite shadows must not turn into blurry painted gradients |
| Camera | 5 reusable setups: wide establishing, medium character+prop, overhead tabletop, macro object, screen-within-screen; vary by shot |
| Character | One stable Hazel **character sheet**, not fresh independent image generations per shot: same face, outfit, silhouette, handedness and outline widths |
| Background | 2–3 parallax planes, **no built-in titles**, leave distinct empty text zones; dark areas for contrast |
| Transparency | Straight alpha RGBA PNG (or lossless WebP only after compatibility test); no baked colored backgrounds, checkerboards, white halo or shadow halo on sprite edges |
| Overlap | Solid background; independently composited character, prop, emitted-light overlay, foreground occluder, titles and CRT/post FX |
| Type | Keep **all essential text in Hazel's renderer**, not ImageGen: Press Start 2P / VT323, with the existing phone read-audit and layout lint |
| Audio | Existing 2A03/120 BPM motifs; semantic cues attached to action/event markers, never baked into an asset |
| Target | Reusable for future episodes; final visuals must work with music muted and remain readable on a phone |

### Generation constraints for any future AI-produced image

Generate at most **one family at a time** from an approved reference sheet: first establish a single Hazel identity pose, then derive expressions/angles from that reference, not from independent descriptions. For transparent sprites, explicitly request isolated cutouts without backdrop, reflections or typography. For environments, request **clean plates** (no protagonist, signs with text or foreground objects that will need to move). Generate light cones, glow and smoke separately, **or procedurally** in the existing canvas, not painted onto the backgrounds.

Rendered generative pixel art is not guaranteed to have consistent pixel clusters or truly clean alpha. Inspect every asset at 100% and nearest-neighbor 400%; fix edges or reject the image. Do not equate “looks like pixel art” with a valid sprite. Prefer simple hand/procedural art for arrows, text, rectangles, coin counters and geometric FX.

## 3. Manifest format and asset contract

Recommended repo location (proposed, not created):

```text
worklines/hazel/video/art/
  bible/
    hazel-reference.png
    palette.md
  characters/hazel/
    hazel-idle-3q.png
    hazel-profile-left.png
    hazel-working.png
    hazel-surprised.png
    hazel-holding-reel.png
  environments/
    workshop-back.png
    workshop-middle.png
    workshop-front.png
    screening-room.png
    arcade-nook.png
  props/
    projector-body.png
    projector-reel.png
    coin.png
    coin-purse.png
    editing-desk.png
    film-strip.png
    cartridge-base.png
    yaml-card-blank.png
    phone-shell.png
  fx/
    projection-beam.png
    dust-overlay.png
  manifest.yaml
```

Each entry in a later `manifest.yaml` should carry at least: `id`, `path`, `type`, `native_w`, `native_h`, `pivot: [x,y]`, optional `anchors: {hand:[x,y], reel_hub:[x,y], ...}`, `default_z`, `license/source`, `revision`. Dimensions and pivots are **designed after the first art samples**; do not invent precise coordinates before the art exists.

Suggested scene composition state:

```yaml
scene:
  composition: workbench_scene
  background: workshop_back
  camera: {shot: medium, target: hazel}
  layers:
    - {slot: main_actor, asset: hazel_working, anchor: desk_seat, opacity: 1}
    - {slot: primary_prop, asset: projector_body, anchor: workbench, opacity: 1}
    - {slot: moving_prop, asset: film_reel, parent: projector_body, anchor: reel_hub,
       animation: rotate_on_cue, cue: projector_start}
    - {slot: light, asset: projection_beam, opacity: 0.35, blend: screen}
  text: {key: "THE MACHINE BUILDS.", secondary: "HAZEL DIRECTS."}
```

This YAML is **conceptual schema only**, not valid input to the current Hazel build pipeline. All named anchors are future metadata, not implemented engine features.

**Core properties of a sprite instance:** `asset_id`, `parent`, `anchor/pivot`, `x/y`, `scale`, `rotation`, `opacity`, `tint`, `z`, `visibility`, `clip/mask`, optionally `blend` (normal/add/screen, after browser-canvas validation). **Animation primitives:** alpha keyframes, translate, scale, pan/zoom, sprite swap, rotation, mask reveal, simple parallax and hold. Ease curves and beat timing are renderer-owned. Animation is data, not per-scene JS.

**Risk:** layering a low-resolution image over a high-resolution canvas can cause halos and text clipping. Use `imageSmoothingEnabled=false` for sprite-scale nearest-neighbor. Prefer preprocessed transparent RGBA with straight alpha, no asset-baked shadow; draw contact shadows with a simple procedural ellipse.

## 4. Prioritized asset inventory

### P0 — pilot pack (create first; 15 unique visual sources)

These assets are sufficient to prove **three template families across at least four scenes**. Sizes are *logical approximations*, to be calibrated after the first composition study.

| ID | Asset | Kind | Suggested view / alpha | Used by |
|---|---|---|---|---|
| A01 | `hazel_identity_sheet` | reference | 3/4 hero reference, opaque reference sheet; **not** a movie layer | all Hazel poses |
| A02 | `hazel_idle_3q` | character | standing 3/4, RGBA | 01B, 02A, 07B, 12A |
| A03 | `hazel_working` | character | seated/leaning at desk, transparent | 03, 04, 08A, 09A |
| A04 | `hazel_holding_reel` | character | hands holding reel, transparent | 11A, 12B |
| A05 | `workshop_back` | environment | full 16:9 empty set, opaque | 01B, 02A, 04A, 07B, 08A, 09A, 11A, 12A |
| A06 | `workshop_foreground` | occluder | shelf/desk edge, transparent | same workshop shots / parallax |
| A07 | `projector_body` | prop | side-facing with empty reel hub, RGBA | 01A, 04A, 11A, 13A |
| A08 | `projector_reel` | prop | centered circular cutout, RGBA / rotational anchor | 01A, 04A, 11A |
| A09 | `coin` | prop | front face and flat profile, ideally two aligned variants | 01A, 02A, 11B, 13A |
| A10 | `coin_purse` | prop | empty-label pouch, RGBA | 02A, 07B |
| A11 | `film_strip` | prop/tile | seamless loopable strip with perforations, RGBA | 04A, 06A, 08A, 11A |
| A12 | `template_cartridge` | prop/tile | generic, blank insert and empty-label slot, RGBA | 08A, 09A |
| A13 | `yaml_card_blank` | prop | paper/card geometry; text rendered separately | 09A, 11A |
| A14 | `phone_shell` | prop/mask | isolated phone bezel + transparent viewport | 05A, 06A |
| A15 | `projection_beam` | effect | alpha or procedural cone, separate layer | 01A, 04A, 11A, 13A |

**Note:** A01 reference is a visual production source, not a composited render asset. Individual character poses must share geometry; `coin` and `template_cartridge` can be reused many times via transform and palette changes. Avoid 23 separately generated cartridge files.

### P1 — needed to finish the likely workshop cut (13 assets)

| ID | Asset | Kind | Used by |
|---|---|---|---|
| A16 | `hazel_surprised` | character | trailer magic, phone critique |
| A17 | `hazel_profile_left` | character | projection / recursive shots |
| A18 | `workshop_desk` | prop/occluder | overhead desk and workbench shots |
| A19 | `storyboard_wall_blank` | environment | sequence 03B |
| A20 | `screening_room` | environment | sequence 05B |
| A21 | `arcade_cabinet_blank` | prop | opening / ending continuity |
| A22 | `movie_screen_mask` | prop/mask | film-within-film; reuse actual frame output as texture |
| A23 | `editing_splicer` | prop | manual template extraction 08A |
| A24 | `film_receipt_long` | prop | token invoice 07/10; draw all numeric labels in renderer |
| A25 | `magnifier` | prop/mask | reading audit 06A |
| A26 | `stopwatch` | prop | reading-time audit 06A |
| A27 | `factory_gear_kit` | modular props | YAML compilation 09A; 2–3 neutral gear silhouettes |
| A28 | `document_stack` | prop/tile | repeated manual work 07B |
| A29 | `studio_window_moon` | environment/overlay | scene 13B / workshop identity |

### P2 — optional variants, add only after the storyboard is approved

| ID | Optional addition | When justified |
|---|---|---|
| A30 | alternate hand gesture/pointing pose | hands must visibly indicate a small prop |
| A31 | projector smoke/glow sprite | procedural lighting is visually insufficient |
| A32 | 3-frame blinking animation | the hero feels lifeless in medium shots |
| A33 | printing rollers, paper stack animation | scene 07B copy machine is chosen |
| A34 | factory conveyor belt | scene 09A cannot be conveyed with existing props + moving masks |
| A35 | cabinet insert / pixel display texture | scene 01B or 13A requires a specific game-in-screen reveal |

**Minimum art spend:** P0 first. Do not commission all 35 at once. Composition decisions should determine the remaining art, not vice versa.

## 5. Three pilot composition templates

### C01 — `workbench_scene` (wide + medium set dressing)

**Slot contract:** `background` (required), `foreground` (optional), `actor` (required), `primary_prop` (0/1), `secondary_props` (0..3), `light` (optional), `key` (required), `secondary` (optional).

**Reusable staging:** static wide to medium push, actor idle/working sprite swaps, props reveal/enter on beats, optional `camera_x` pan and foreground occlusion. The background NEVER contains the key text. Opening composition 02A (coin budget), 03B (unexpected world), 07B (photocopy disaster), 12A (return to creative work) can use this without custom JS.

**Pilot:** a 6–8-second shot: Hazel turns toward the purse and projector, places a coin; “THE MOVIE COSTS TOO.” Fades to the next shot. The renderer positions all props through common anchors. Reject if any shot needs to embed a complete frame into a background plate.

### C02 — `projection_reveal` (screen-within-screen / recursive surface)

**Slot contract:** `environment`, `projector`, `reel`, `beam`, `screen_surface`, `on_screen` (an image, a short clip or *a live renderer frame texture*), optional `actor`, `key`.

**Reusable staging:** object starts idle, `projector_start` cue rotates reel and fades light cone, screen mask reveals image, camera may pull back; duration and moves depend on the scene. Can reveal a trailer, demonstrate phone-scale failure, or recurse into the current film.

**Pilot:** first show a static frame of Story 1 *inside* the screen, then camera pullback to Hazel's projector. **Recursion is not a built-in primitive yet**; run a safe nonrecursive nested snapshot before attempting an actual render-to-texture effect. The video itself is not an image asset copied into Git.

### C03 — `object_closeup` (one prop becomes the story)

**Slot contract:** `background_blur/flat`, `hero_prop`, optional `hand/actor`, `secondary_prop`, `key`, `focus_anchor`, `animation_preset`.

**Reusable staging:** extreme closeup → slow rotation/translate → dramatic stamp, match-cut on shape to the next scene. Same mechanics on a coin, cartridge, film reel, receipt or YAML card; the concept of the shot is the object transformation, not a table of numbers.

**Pilot:** macro coin falls into projector; the coin edge match-cuts to the rotating reel; text “INSERT COIN”. If this cannot be accomplished with two transparent sprites, a mask and motion curves, the composition layer is too rigid.

**Second wave (not implemented in pilot):** `inspection_station` (a visual test actually interacts with an object), `assembly_line` (prop moves between stations), `recursive_reveal` (screen output becomes input). They should first be variants using C01–C03, and only promoted to new families after visual evaluation.

## 6. Proposed scene-to-composition and asset matrix

Use this as a *draft visual direction*, not a final storyboard. A/B references are from the 26-concept note.

| Seq | Story beat | Concept to explore | Proposed composition | Key asset IDs | Needed motion |
|---|---|---|---|---|---|
| 01 | Title / insert coin | 01A | C03 object closeup → C02 projection | A07–A09,A15 | coin drop, reel rotates |
| 02 | One Claude Pro subscription, €20 | 02A | C01 workbench | A02,A05,A06,A09,A10 | hand / purse / coin emphasis |
| 03 | README becomes surprising trailer | 03B/03A | C01 + C02 | A03,A05,A07,A19,A22 | storyboard reveals into projected world |
| 04 | Time-driven image/audio toolchain | 04A | C03 + C02 | A07,A08,A11,A15 | synchronized clock and strip motion |
| 05 | Phone readability criticism | 05A | C02 with phone mask | A14,A16,A20,A22 | punch-in on shrinking text |
| 06 | Convert failure to executable tests | 06A | C01 overhead variant | A11,A18,A25,A26 | physical gauges inspect frames |
| 07 | Repeat code, repeat defects | 07B | C01 workshop | A05,A16,A24,A28 | accumulating stacks / loop |
| 08 | Extract 23 reusable patterns | 08A | C01 assembly variant | A03,A05,A11,A12,A23 | strip-cut → cartridge shelf |
| 09 | Instrument and compile from YAML | 09A | C01 assembly variant | A03,A05,A12,A13,A27 | card enters / stations animate |
| 10 | Promising but noncomparable costs | 10A | C03 tabletop | A18,A24,A25 | compare two receipts with scope caveat |
| 11 | Film is its own second build | 11A | C02 projection nested reveal | A04,A07,A08,A11,A15,A22 | real recursive pullback / safe fallback |
| 12 | Automate repetition, preserve choices | 12A | C01 workbench | A02,A05,A06,A18 | machinery stops; Hazel draws |
| 13 | Motto and coin returns | 13A | C03 macro + end-card typography | A07,A09,A21,A29 | quiet coin return; lights fade |

**Narrative discipline:** reveal the 23-template library in scene 08, and machine-readable YAML automation only in scene 09. Keep the two-film payoff hidden until 11. If sequence 12 weakens the surprise, compress it to a silent visual beat or integrate it into the last 2 seconds of 11.

## 7. Image-generation workflow (future user approval required)

1. **Reference sheet first:** 1 Hazel character identity image with fixed silhouette/clothes/colors and 3 poses; compare proportions, approve or regenerate.
2. **One environment keyframe:** wide empty workshop 16:9; test empty safe areas and separability into back/front/props.
3. **Pilot isolated cutouts:** projector, reel, coin, one Hazel pose, beam/mask. Export transparency, reject false-alpha backgrounds.
4. **One animated pilot in the actual Hazel canvas:** 6–8 seconds, using only C01–C03 composition data and existing beat-aligned cues. Confirm what is truly reusable before ordering additional images.
5. **Contact sheet and regression:** screenshot composition, alpha halos, scale/pixel alignment, ownership/accessibility; lint texts; inspect motion on actual 640×360 phone preview.
6. **Only then:** generate P1 assets and cover the 13 scenes. Preserve prompt, reference version, generator information and approval in an asset manifest.

### Asset acceptance checks

- Exact transparent alpha for foreground assets; transparent corners tested, no white/black/checkerboard baked in.
- No text, numbers or logos baked into imagery unless explicitly an art mark cleared by Hazel.
- No mismatched hands, body proportions, costumes, skin palette or perspective across Hazel poses.
- Assets must look like one game when layered, not like separately generated posters.
- The same prop can move, rotate, scale or be tinted independently without exposing missing pieces.
- Pixel edges survive nearest-neighbor scaling and a 640×360 reduction.
- The same shot can be configured with **two unrelated sets of props/messages without editing JS**: the actual reuse test.
- Repeated layers should not need 1920×1080 PNGs when a small sprite would do; use sized cutouts and shared plates.

## 8. Scope, priorities and next decision

**Now delivered:** this Markdown plan only, for Adam's review. Proposed minimal P0 pack: 15 unique sources (including 1 identity reference), 3 composition templates, and 1 playable pilot shot. **No images have yet been generated.**

**Next decision for Adam:** approve the overall art direction and choose which to prototype first: **(a) coin → projector** (C03/C02), or **(b) Hazel at the workbench** (C01). This choice defines the first reference images and tests consistency before a larger image-generation run.

**Guardrails:** Hazel owns its production engine; schedule changes through its workline, with no merge or public upload without user approval. Asset generation may use ChatGPT's image capabilities once the first visual subject/output is explicitly requested.
