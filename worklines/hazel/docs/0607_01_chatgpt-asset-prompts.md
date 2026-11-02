# Prompts for ChatGPT: the series' graphic assets

> **Freshness:** 🟢 current · **Written:** 2026-11-02 · **Checked:** 2026-11-02 · **Step:** hazel 6.7

**What this is:** prompts the user can paste into ChatGPT (image generation) to make the asset pack of Step 6.7, with the project's key art `worklines/hazel/video/common/art/wallpaper.png` attached as the reference image. The images come back to Hazel, which sorts them into `worklines/hazel/video/common/assets/`, checks them and writes the manifest.

## How to use

1. Start a ChatGPT conversation. **Attach `wallpaper.png`** and paste the **style block** below once.
2. Then paste the prompts **one at a time**, in the same conversation, so that the style stays consistent.
3. Save each image under the file name given in the prompt, as a PNG, and keep transparency where it is asked for.
4. If a character does not look like the key art, answer "closer to the reference: same face, hair and suit" and regenerate. Do not accept a different person.

## Style block (paste first, with the image attached)

```
This image is the key art of my project TANSTAAFLLM. Use it as the reference for every image I ask for in this conversation.
Keep the same four characters (same faces, hair, age, suits, and the robot's design), the same retro sci-fi mood (Heinlein's Moon, 1980s arcade), and this palette:
deep navy #070b24, navy #0f1645, violet #2b1660 and #4a2a8c, amber #ffb43c and #ff8a1e, cyan #3ee8ff, chrome white #eef3ff, soft lunar grey #a9b3d8, red #ff4d5e, green #57ff8f.
Unless I say otherwise, each image has:
- a transparent background (real alpha, no checkerboard drawn, no white box);
- one subject only, centred, with a little empty margin around it;
- no text, no logo and no watermark, unless I ask for them.
When I ask for "pixel art", I mean true pixel art: a visible pixel grid, a limited palette taken from the colours above, hard pixel edges with no anti-aliasing and no blur, a 1-pixel dark outline (#0a0420), simple 2–3-step shading, 1980s arcade or NES/SNES era.
Just reply "ready".
```

## A0. Recommended path for the characters: clean the crops, don't redraw (user, 2026-11-02)

To keep the characters undistorted, ChatGPT does not redraw them. Hazel crops each character out of `wallpaper.png` on the CPU, and ChatGPT only removes what is not the character and rebuilds what was hidden.

- **The crops,** in `worklines/hazel/video/common/assets/crops/`:
  - `crop-<name>-portrait.png`: chest-up, with neighbours and sky around;
  - `crop-<name>-face.png`: the face box used by the renderer.
- **Hazel then makes the sprites on the CPU** from the cleaned cut-outs: a 64 × 64 downscale, snapped to the series palette, with no dithering. A first CPU-only try, made straight from the uncleaned crops, is in `assets/sprites-cpu/`. It is recognisable, but the sky and the neighbours leak into it, which is why the crops are cleaned first.

**A0 prompt, for each character.** Attach `crop-<name>-portrait.png` and `wallpaper.png`.

```
The first image is a crop of the second (my project's key art). Keep the main character in the crop, <Mannie, the rugged man with brown hair / Wyoh, the blonde woman / Mike, the robot / the Professor, the man with glasses and a headset>, EXACTLY as painted: same face, same features, same proportions, same pose, same colours, same brush style. Do not redraw, beautify, restyle or re-light the face.
Only:
1. remove the background (sky, moon, stars), the title, and every part of the other characters that overlaps this one;
2. where the other characters or the frame hid parts of this character (shoulder, hair, suit, antenna…), rebuild those parts so that they match the visible ones;
3. give back a PNG with a real transparent background, at the same size as the crop, with the character in the same position.
```

Save the result as `char-<name>-cutout.png`. If the face changed at all, say "the face changed: keep it pixel-identical to the crop" and regenerate.

## A. The four characters, painted like the key art (transparent background)

These prompts are a fallback: use them only if A0 fails for a character.

These are portraits from the chest up, in the key art's painted style, facing three-quarters to the viewer's right as in the poster unless stated. They are used on the player cards and in dialogue.

**A1. `char-mannie-portrait.png`**
```
Mannie, the man on the far left of the reference: rugged, mid-thirties, tousled brown hair, stubble, determined look, worn grey-brown work suit with a harness and the wrench clipped on it. Chest-up portrait, same painted style and lighting as the reference (cool moonlight from the upper left, a warm amber rim light). Transparent background. 1024×1024.
```

**A2. `char-wyoh-portrait.png`**
```
Wyoh, the woman second from the left in the reference: short tousled blonde hair, confident gaze upward, grey space suit with the crescent-moon patch on the shoulder. Chest-up portrait, same painted style and lighting as the reference. Transparent background. 1024×1024.
```

**A3. `char-mike-portrait.png`**
```
Mike, the robot in the reference: boxy grey head that is a screen with two cyan smiling arc eyes, two antennas on top, segmented neck, armoured shoulders. Chest-up, same painted style and lighting. Transparent background. 1024×1024.
```

**A4. `char-prof-portrait.png`**
```
The Professor, the older man on the far right of the reference: curly greying hair, round glasses, headset with a boom microphone, calm and wise expression, dark suit with a chest control unit. Chest-up portrait, same painted style and lighting. Transparent background. 1024×1024.
```

**A5. `char-group.png`**
```
The four characters of the reference together, in the same arrangement (Mannie, Wyoh, Mike, the Professor from left to right), cut out from the background: no moon, no stars, no title. Transparent background. 1536×1024.
```

## B. The characters as pixel-art sprites (transparent background)

The preferred sprites come from the A0 cut-outs, through the CPU (64 × 64, palette snap). Use B1 and B2 when you want a hand-drawn pixel-art look, or the animation frames, which the CPU cannot make.

These are used in the stages: small, readable on a phone, and animated by swapping frames.

**B1. `sprite-<name>-bust.png`**, one prompt per character (mannie, wyoh, mike, prof)
```
Pixel-art bust of <Mannie / Wyoh / Mike / the Professor> from the reference, faithful to the face, hair and suit, 64×64 pixel grid shown at 16× (1024×1024 image), front three-quarter view. True pixel art, palette from the style block, 1-pixel dark outline. Transparent background.
```

**B2. `sprite-<name>-sheet.png`**, one prompt per character
```
Pixel-art sprite sheet of <character> from the reference, full body, 48×64 pixel grid per frame, shown at 8×. One horizontal row of 6 frames with equal spacing:
1 idle, 2 idle (breathing), 3 talking (mouth open), 4 pointing to the right, 5 thumbs up / victory, 6 surprised.
Same character in every frame, same size, feet on the same baseline. True pixel art, palette from the style block. Transparent background.
```
(For Mike, replace "mouth open" with "screen eyes change to a speech icon", and "surprised" with "screen shows a question mark".)

**B3. `sprite-agent-robot.png`**
```
A small, generic "AI agent" robot in pixel art, a simpler cousin of Mike: boxy head with a screen face and two cyan dot eyes, one antenna, a small body. 32×32 pixel grid shown at 16×. Two frames side by side: eyes open, eyes as two lines (thinking). True pixel art. Transparent background.
```

## C. Title and lockups (transparent background)

**C1. `logo-tanstaafllm.png`**
```
The chrome title "TANSTAAF LLM" from the reference, alone: same chrome lettering, same bevel and reflections, the thin line and the four-point star under it. Nothing else, no moon, no sky. Transparent background. 2048×640.
```

**C2. `logo-tanstaafllm-pixel.png`**
```
The same "TANSTAAF LLM" title redrawn as pixel art: chunky arcade letters with a chrome gradient (white #eef3ff to lunar grey #a9b3d8 to violet #4a2a8c), a 2-pixel dark outline and a hard drop shadow; the small star below. 256×64 pixel grid shown at 8×. Transparent background.
```

## D. Sky, moon, ground (backgrounds)

**D1. `moon.png`**
```
The full moon from the reference, alone: the same craters and the same lighting, as a perfect disc with a soft cool glow at its edge. Nothing else. Transparent background. 2048×2048.
```

**D2. `moon-pixel.png`**
```
The same moon as pixel art: 128×128 pixel grid shown at 8×, 6 shades of lunar grey and blue from the palette, craters readable, no anti-aliasing. Transparent background.
```

**D3. `sky-stars-far.png`, `sky-stars-near.png`**
```
A starfield layer for a parallax background, 1920×1080, transparent background. <far layer: many tiny white and pale blue stars, 1 pixel, sparse, some faint violet nebula wisps at 20 % opacity> / <near layer: fewer, bigger stars, 2–3 pixels, a few amber and cyan ones, two four-point twinkles>. Pixel-crisp dots. The image must tile horizontally.
```

**D4. `sky-gradient.png`**
```
A plain night-sky gradient background, 1920×1080, opaque: deep navy #070b24 at the top to violet #2b1660 at the bottom, with a faint purple nebula band across the upper third like the reference. No stars, no moon.
```

**D5. `ground-lunar-horizon.png`**
```
A lunar surface horizon strip in pixel art, 1920×360, transparent above the horizon: grey regolith with small craters and rocks, a slight curve, cool light from the left, the palette of the style block. It must tile horizontally.
```

## E. Props, in pixel art (transparent background)

These are used in the stories, so they must be readable at small size. Each one is "true pixel art, palette from the style block, 1-pixel dark outline, transparent background".

**E1. `prop-luna-handheld.png`**: the Luna handheld.
```
A vertical game handheld (like an R36-style clone): a square screen at the top, a d-pad on the left, four round buttons A/B/X/Y on the right (yellow, red, cyan, green), two small analog sticks below, a speaker grille, shoulder buttons on top. Slate violet-grey shell. The screen is plain flat black (it will be filled in by code). 80×120 pixel grid shown at 8×. Transparent background.
```

**E2. `prop-microsd.png`**, `prop-hard-disk.png`, `prop-usb-adapter.png`, `prop-usb-hub.png`, `prop-keyboard.png`, `prop-wifi-chip.png`, `prop-router.png`, `prop-pc-monitor.png`, `prop-microphone.png`, `prop-coin.png`
```
<one of: a microSD card with a gold contact strip and an amber label / an external hard disk with a green activity LED / a small USB-C to USB-A adapter / a multi-port USB-C hub with five ports / a compact keyboard seen from above / a Wi-Fi chip, a square IC with pins on four sides and Wi-Fi arcs printed on it / a home Wi-Fi router with two antennas and five status LEDs / a desktop PC monitor on a stand, screen plain black / a retro microphone / a gold arcade coin with a star, seen face-on>, as pixel art, 32×32 pixel grid shown at 16×. True pixel art, palette from the style block. Transparent background.
```
(For the coin, add: "a 6-frame spin animation in one horizontal row".)

**E3. `prop-boss-frames.png`**
```
A set of four "boss" frames for a retro game, in pixel art, side by side: a red heart-container HP bar with 5 pips, a red "WARNING" hazard stripe band, a skull-and-crossed-wrenches badge, and a cracked-shield icon. 32×32 pixel grid each, shown at 16×. Transparent background.
```

## F. Hazel, Adam and Luna (optional, new characters)

These are not in the key art. Use them only if the user wants them on screen.

**F1. `char-hazel-portrait.png`**
```
A new character in the same painted style as the reference: Hazel, a sharp-eyed twelve-year-old girl with red hair in a messy ponytail, freckles, a too-big grey space suit with rolled-up sleeves, a courier satchel. She is the crew's creative director. Chest-up, same lighting as the reference. Transparent background. 1024×1024.
```

**F2. `char-adam-silhouette.png`**
```
"Adam", shown only as a silhouette: a human figure from the chest up, seen from behind, looking at a glowing amber screen. No face and no recognisable features. Painted style of the reference. Transparent background. 1024×1024.
```

## What Hazel does with the images

1. Checks each one: the transparency is real, and the character is faithful to the key art. For pixel art, it checks that the grid is clean, and snaps it to the grid if needed (downscale by the stated factor, nearest neighbour, then quantise to the palette, all on the CPU).
2. Saves the assets in `common/assets/` and writes `manifest.yaml` (name, size, anchor, source "ChatGPT from wallpaper.png, <date>", use).
3. Lets the templates call them by name (`sprite: wyoh`, `prop: router`). The sprites drawn in code stay as a fallback.
