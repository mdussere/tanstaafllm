"""Reading-time audit of the video, and the holds that fix it.

Every screen ends at a cut: the moment its text starts to disappear (a dissolve,
a flash or a hard change). For each screen, this script lists the text that becomes
readable, then asks whether the viewer had time to read it before the cut.

Reading model (sources in NOTES.md, "Reading time"):
  - ORIENT: 0.4 s to notice that something new has appeared and look at it
    (conscious access takes about 0.3 s, plus one saccade);
  - then a word costs 0.25 s in VT323 mixed case (about 240 words per minute,
    the adult average for silent reading) and 0.30 s in Press Start 2P capitals
    (pixel capitals read about 20 % slower);
  - a screen stays readable for at least MIN_HOLD after its last text appears,
    even for a one-word stamp, so that it can land.

Two checks per screen (the default, --mode last, applies only the first):
  last  the last text needs ORIENT + its own reading time (at least MIN_HOLD)
        between the moment it is readable and the cut;
  total all the text of the screen needs ORIENT + the sum of the reading times,
        from the moment the first text is readable to the cut.
The missing time becomes a hold, rounded up to whole beats of the music (SNAP,
0.5 s at 120 BPM) so that every cut stays on the beat; a shortfall under TOLERANCE
is dropped. The hold: index.html freezes the choreography at the cut's
source time for that long, while the stars and blinks keep moving.

Usage:  python timing.py [--mode last|total] [--json F]
        prints the audit as a Markdown table; --json also writes the holds to F
"""
import json
import math
import sys

ORIENT, MIN_HOLD = 0.4, 1.0
PER_WORD = {"P": 0.30, "V": 0.25}
MODE = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "last"
EPS = 0.001
SNAP, TOLERANCE = 0.5, 0.1
BASE = 90.0   # the cut without holds (index.html BASE)   # holds sit just before the transition starts

# (scene, cut in source seconds, [(readable at, text, font), ...])
# Glance-only text (stat rows, tile captions, tree nodes, layer rows, CLEAR!) is left out.
SCREENS = [
    ("0 Title", 5.8, [
        (0.5, "TANSTAAFLLM STORY 2", "P"),
        (1.15, "ASK THE DESKTOP", "P"),
        (1.6, "How an agent learned to work a desktop without looking at it.", "V")]),
    ("1 Player 2", 13.75, [
        (6.45, "PLAYER 2 WYOH", "P"),
        (6.95, "THE DESKTOP LAYER OF LUNA", "P"),
        (8.4, "QUEST: \"Give consumers a structured, inspectable, synchronisable desktop they can observe and operate without pixels.\"", "V")]),
    ("2 Stage 1 screenshot trap", 20.0, [
        (14.3, "STAGE 1 THE SCREENSHOT TRAP", "P"),
        (15.1, "A BUTTON? A WINDOW? WHICH ONE?", "P"),
        (15.1, "Through screenshots, an agent guesses from pixels, and pays for every image, on a small handheld.", "V"),
        (17.15, "ON PAPER: A DOM FOR THE DESKTOP.", "P")]),
    ("3 Stage 2 HIOM", 28.0, [
        (20.3, "STAGE 2 ONE SCENE IS NOT A DESKTOP", "P"),
        (20.8, "First idea: one full-screen scene, with only the actions it advertises.", "V"),
        (22.65, "REOPENED", "P"),
        (23.0, "One scene could not hold a real desktop.", "V"),
        (23.65, "KEPT FROM IT: WAIT FOR A NAMED CONDITION, NEVER A FIXED DELAY.", "P")]),
    ("4 Stage 3 Sway", 36.0, [
        (28.3, "STAGE 3 ASK THE ONE THAT EXISTS", "P"),
        (28.6, "Don't build a compositor. Ask the one that exists.", "V"),
        (29.8, "SWAY UNMODIFIED NO FORK", "P"),
        (30.4, "MEASURED ON luna-pi", "P"),
        (30.7, "a Raspberry Pi, headless Sway 1.10.1, 2026-09-26", "V"),
        (32.6, "KILLED, BACK IN 7.5 ms luna-pi", "P")]),
    ("5 Stage 4 MCP", 44.0, [
        (36.3, "STAGE 4 HAND IT TO AGENTS", "P"),
        (36.7, "MCP OVER SSH DEVELOPMENT ONLY", "P"),
        (39.1, "1 QUERY THE WINDOW TREE 2 ACT 3 WAIT FOR THE CONFIRMING EVENT", "P"),
        (40.15, "26 TOOLS", "P"),
        (40.4, "luna-pi, THEN LUNA", "P"),
        (40.4, "Aside: without structured output, a one-item list read as the object itself.", "V")]),
    ("6 Boss: black panel", 52.0, [
        (44.3, "STAGE 5 BOSS: THE BLACK PANEL", "P"),
        (44.7, "LUNA 720 x 720 PANEL The same agent session, on the real panel:", "V"),
        (45.15, "BLACK.", "P"),
        (45.8, "Sway's own screenshots looked right.", "V"),
        (46.6, "MALI GPU DRIVER: NOT LOADED", "P"),
        (47.1, "Sway was rendering in software.", "V"),
        (48.6, "MALI GPU DRIVER: LOADED", "P"),
        (48.8, "1 passed", "V")]),
    ("7a Stage 6 buttons", 57.5, [
        (52.3, "STAGE 6 17 BUTTONS, NO KEYBOARD", "P"),
        (52.8, "A daemon turns the buttons into desktop actions:", "V"),
        (54.35, "FN+PAD FOCUS FN+A FULL SCREEN FN+B CLOSE FN+R1 WORKSPACE", "P"),
        (54.6, "BUTTONS ONLY, ON LUNA, 2026-10-07", "P"),
        (54.95, "THE SLATE TAKES THE TEXT.", "P"),
        (55.3, "A floating text zone, opened with L1.", "V")]),
    ("7b Stage 6 agent and Mike", 62.0, [
        (57.75, "THE AGENT PRESSES THE SAME BUTTONS", "P"),
        (58.05, "through a virtual gamepad, not by clicking pixels.", "V"),
        (58.5, "ON LUNA, IN THE SLATE: FN + B", "P"),
        (59.15, "MIKE ANSWERS IN 13 s", "P"),
        (59.55, "6.6 s if Mike is already open.", "V")]),
    ("8 Stage 7 seven layers", 72.0, [
        (62.3, "STAGE 7 SEVEN LAYERS", "P"),
        (62.6, "Luna, 2026-10-30, on the new system root: a game's buttons died.", "V"),
        (64.65, "FIX \"VERIFIED\": THE CODES WERE RIGHT.", "P"),
        (65.15, "THE GAME DID NOT MOVE.", "P"),
        (66.7, "Check each layer, in turn.", "V"),
        (68.65, "ONLY THE LAST ONE PROVES THE FIX.", "P")]),
    ("9 Payoff", 77.75, [
        (72.4, "sway_get_tree", "P"),
        (73.65, "ASK THE DESKTOP.", "P"),
        (74.8, "Screenshots stay, as evidence for humans.", "V")]),
    ("10 Story clear", 84.0, [
        (78.15, "STORY 2 CLEAR", "P"),
        (79.35, "DON'T LOOK AT THE DESKTOP, ASK IT.", "P"),
        (80.6, "The compositor already knows what a screenshot can only guess.", "V")]),
    ("11 End card", 89.5, [
        (84.5, "There Ain't No Such Thing As A Free LLM.", "V"),
        (84.8, "github.com/mdussere/tanstaafllm", "P"),
        (85.1, "A personal engineering project by Michael Dussere", "V")]),
]


def words(s):
    return len([w for w in s.replace("/", " ").split() if any(c.isalnum() for c in w)])


def read_time(s, font):
    return words(s) * PER_WORD[font]


def audit():
    rows = []
    for name, cut, elems in SCREENS:
        first = min(e[0] for e in elems)
        last_t, last_s, last_f = max(elems, key=lambda e: e[0])
        need_last = max(MIN_HOLD, ORIENT + read_time(last_s, last_f))
        have_last = cut - last_t
        need_total = ORIENT + sum(read_time(s, f) for _, s, f in elems)
        have_total = cut - first
        hold = max(0.0, need_last - have_last, need_total - have_total if MODE == "total" else 0.0)
        hold = SNAP * math.ceil((hold - TOLERANCE) / SNAP) if hold > TOLERANCE else 0.0
        rows.append(dict(screen=name, cut=round(cut, 3), last=last_s, last_words=words(last_s),
                         have_last=round(have_last, 2), need_last=round(need_last, 2),
                         have_total=round(have_total, 2), need_total=round(need_total, 2),
                         hold=round(hold, 1)))
    return rows


def main():
    rows = audit()
    print("| Screen | Last text before the cut | Words | Last on screen | Needed | Whole screen | Needed | Hold added |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['screen']} | {r['last'][:48]} | {r['last_words']} | {r['have_last']:.2f} s | {r['need_last']:.2f} s "
              f"| {r['have_total']:.2f} s | {r['need_total']:.2f} s | {'+' + format(r['hold'], '.1f') + ' s' if r['hold'] else '—'} |")
    extra = sum(r["hold"] for r in rows)
    print(f"\nHolds: +{extra:.1f} s, so the video lasts {BASE + extra:.1f} s.")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        holds = [[r["cut"], r["hold"]] for r in rows if r["hold"] > 0]
        with open(out, "w") as f:
            json.dump({"holds": holds}, f, indent=1)
            f.write("\n")


if __name__ == "__main__":
    main()
