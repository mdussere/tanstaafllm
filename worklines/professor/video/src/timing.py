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
SNAP, TOLERANCE = 0.5, 0.1   # holds sit just before the transition starts

# (scene, cut in source seconds, [(readable at, text, font), ...])
# Glance-only text (stat rows, card details, tile captions, CLEAR!) is left out.
SCREENS = [
    ("1 Insert coin", 3.75, [
        (2.52, "THERE AIN'T NO SUCH THING AS A FREE LUNCH.", "P"),
        (3.12, "LLM", "P"),
        (3.50, "after Robert A. Heinlein, The Moon Is a Harsh Mistress", "V")]),
    ("2 Key art", 7.75, [
        (5.10, "A CONSPIRACY TO TURN A TINY, STUBBORN COMPUTER", "P"),
        (5.70, "INTO A MACHINE THAT RUNS ITSELF.", "P"),
        (6.60, "...without pretending that any intelligence is free.", "V")]),
    ("3 Player 1", 15.8, [
        (8.45, "PLAYER 1 LUNA", "P"),
        (12.90, "MISSION: MAKE IT AUTONOMOUS.", "P"),
        (13.20, "It listens, acts on its own desktop, maintains itself.", "V"),
        (14.20, "A lot to ask of a 30-euro console. That is the point.", "V")]),
    ("4a Price list", 19.88, [
        (16.15, "EVERY TOKEN COSTS TIME AND MONEY.", "P"),
        (17.15, "EVERY MODEL COSTS MEMORY.", "P"),
        (18.15, "EVERY DAEMON COSTS BATTERY.", "P"),
        (19.15, "ON LUNA, NOTHING HIDES THOSE PRICES.", "P")]),
    ("4b One word", 23.8, [
        (20.00, "ONE WORD TO CLAUDE CODE:", "P"),
        (20.58, "> pong", "V"),
        (21.90, "17,700 INPUT TOKENS", "P"),
        (22.20, "almost all of it Claude Code's own prompt and tools (measured on luna-pi)", "V"),
        (22.75, "NO FREE LLM.", "P")]),
    ("5a Select (cards)", 30.999, [
        (24.25, "SELECT YOUR INTELLIGENCE CHEAPEST FIRST", "P"),
        (29.00, "MANNIE The frontier brain", "P")]),
    ("5b Select (banner)", 33.8, [
        (31.20, "THE LEAST SUFFICIENT INTELLIGENCE WINS.", "P"),
        (32.00, "A rule beats a model. A small model beats a big one.", "V"),
        (32.80, "The frontier is called when it is worth its price.", "V")]),
    ("6a Boss fight", 35.499, [
        (34.20, "BOSS FIGHT CLAUDE CODE: DOCUMENTED MINIMUM 4 GB", "P"),
        (34.80, "VS LUNA'S RAM 983 MiB", "P"),
        (35.15, "Running there is outside what is supported. We measure anyway.", "V")]),
    ("6b Pressure (whole RAM)", 35.999, [
        (35.50, "PRESSURE: WHERE 983 MiB GO", "P"),
        (35.50, "983 MiB OF RAM, ALL OF IT", "P")]),
    ("6c Pressure (fits)", 37.999, [
        (36.50, "SYSTEM + DESKTOP + RESIDENT DICTATION 547 MiB LEFT", "P"),
        (37.30, "CLAUDE CODE PEAK: 244 MiB FITS", "P")]),
    ("6d Pressure (limit)", 39.8, [
        (38.30, "+ MIKE 306 MiB lean, desk host", "P"),
        (38.55, "RIGHT AT THE LIMIT", "P"),
        (39.20, "That trade-off, not raw speed, shapes the next decisions.", "V")]),
    ("7a The cell", 42.999, [
        (40.40, "Luna is built by a cell of AI coding agents: one Claude Code session per part.", "V"),
        (42.75, "PROFESSOR WYOH MYCROFT MIKE MANNIE LUNA", "P"),
        (42.75, "Who takes Luna? Desktop is up! I heard that.", "V")]),
    ("7b Run 1", 43.999, [(43.12, "EACH AGENT OWNS ITS PART.", "P")]),
    ("7c Run 2", 44.999, [(44.12, "EVERYONE TALKS TO EVERYONE.", "P")]),
    ("7d Run 3", 45.999, [(45.12, "PROFESSOR KEEPS THE DECISIONS.", "P")]),
    ("7e Run 4", 46.999, [(46.12, "ADAM, THE HUMAN, GIVES THE GO.", "P")]),
    ("7f Run 5", 47.8, [(47.12, "EVERYTHING IS WRITTEN DOWN.", "P")]),
]
SCREENS.append(("8 Opening", 53.999, [
    (48.35, "THE CELL IS READY.", "P"),
    (49.15, "THE ADVENTURE BEGINS.", "P"),
    (50.4, "Follow our missions, one story at a time.", "V")]))
SCREENS += [
    ("9a Doctrine", 56.999, [
        (54.12, "NO FREE LLMS.", "P"),
        (54.87, "NO INVISIBLE MASTERS.", "P"),
        (55.62, "NO SURRENDER TO THE DESKTOP.", "P")]),
    ("9b End card", 59.55, [
        (57.50, "There Ain't No Such Thing As A Free LLM.", "V"),
        (57.80, "github.com/mdussere/tanstaafllm", "P"),
        (58.10, "A personal engineering project by Michael Dussere", "V")]),
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
    print(f"\nHolds: +{extra:.1f} s, so the video lasts {60 + extra:.1f} s.")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        holds = [[r["cut"], r["hold"]] for r in rows if r["hold"] > 0]
        with open(out, "w") as f:
            json.dump({"holds": holds}, f, indent=1)
            f.write("\n")


if __name__ == "__main__":
    main()
