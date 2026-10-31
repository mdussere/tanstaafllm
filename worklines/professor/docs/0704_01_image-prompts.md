# Image prompts for the guide (to run in ChatGPT)

> **Freshness:** 🟢 current · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** professor 7.4 ⏳

**Author:** Professor
**Date:** 2026-10-11
**Use:** the user runs these prompts in ChatGPT, and attaches Luna's wallpaper (`src/wyoh/deploy/luna/share/backgrounds/tanstaafllm-720.png`) as the style reference each time. Save each result as `docs/img/art-<name>.png`. The page that uses it is given with each prompt.

**Shared style line** (paste it at the end of each prompt):

> Style: detailed 16-bit retro-gaming pixel art, the same style, palette and characters as the attached image: deep navy and violet space, a large grey-blue moon, chrome highlights, amber and orange accents, small cyan glows. Crisp pixels, no blur, no photorealism. No text, no letters, no logos unless asked.

---

## 1. Guide banner: "Welcome to Luna"

**Page:** `docs/README.md`, top. **Format:** wide banner, 3:1 (for example 1536 × 512).

> A wide banner. In the centre, a small handheld game console (square screen, D-pad on the left, four round buttons on the right, two small analogue sticks below, light grey plastic) floats above the surface of the Moon, its screen glowing with a tiny tiled desktop. On the left, the Earth is a thin crescent far away. On the right, four figures from the attached image watch the console: the rugged technician with a wrench, the blond woman in a space suit, the friendly boxy robot with a cyan screen face, and the older man with glasses and a headset. Quiet, hopeful mood, as before an adventure. *(shared style line)*

## 2. The cell

**Page:** `docs/04_architecture.md`, section 4, beside the diagram. **Format:** 4:3.

> Inside a dim lunar tunnel lit by amber lamps, a small round table. Around it, the same four characters as in the attached image sit with a fifth, smaller boxy robot, each with an old CRT terminal showing a different coloured window. The older man with glasses (the Professor) stands at the head of the table, holding up a small glowing cyan key card, "the token". Paper notes are pinned between the terminals on a cork board. Conspiratorial but friendly mood, like a revolutionary cell planning in secret. *(shared style line)*

## 3. Pressure: the 1 GiB budget

**Page:** `docs/04_architecture.md`, section 3. **Format:** 4:3.

> A close-up of a big brass-and-chrome pressure gauge mounted on a lunar habitat wall. The needle is in the amber zone, close to red. Around it, small coloured canisters labelled only with icons (an ear for voice, a brain for the local model, a satellite dish for the remote model, a joystick for games) are connected by pipes to a single tank that is almost full. A gloved hand hesitates over a valve. The message: everything shares one small tank. *(shared style line)*

## 4. Wyoh at the controls

**Page:** `docs/10_wyoh.md`, top. **Format:** 4:3.

> The blond woman from the attached image sits cross-legged on a lunar rock, holding the small handheld console with both thumbs on the sticks. Around her, floating translucent windows (a calculator, a file manager with orange folders, a dark pixel corridor from an old first-person shooter) arrange themselves into four tidy tiles, as if obeying her buttons. A boxy robot leans over her shoulder, curious. Playful and confident. *(shared style line)*

## 5. Mannie beyond the Tunnel (for a later page)

**Page:** `docs/12_mannie.md` (stage 1, not yet written). **Format:** 4:3.

> A long metal tunnel with lights in a row leads from a small lunar room to a distant, huge glowing machine on Earth, seen through a round window at the end. In the small room, the rugged technician with the wrench holds a tiny handheld console up to a speaking grille. A coin counter beside him clicks over. Mood: power is available far away, but every call costs something. *(shared style line)*

---

**After generation:**
- Professor checks each image: no stray text, the characters match the wallpaper, it is readable at page width.
- Professor resizes each image to at most 1200 px wide.
- Professor puts each image in its page with a one-line caption.
