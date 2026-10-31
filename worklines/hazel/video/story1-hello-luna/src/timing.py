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
BASE = 94.0   # the cut without holds (index.html BASE)   # holds sit just before the transition starts

# (scene, cut in source seconds, [(readable at, text, font), ...])
# Glance-only text (stat rows, card details, tile captions, CLEAR!) is left out.
SCREENS = [
    ("0 Title", 4.8, [
        (0.5, "TANSTAAFLLM STORY 1", "P"),
        (1.15, "HELLO, LUNA", "P"),
        (1.6, "How a cheap game handheld became a Linux computer on Wi-Fi.", "V")]),
    ("1 Player 1", 11.75, [
        (5.45, "PLAYER 1 R36 ULTRA", "P"),
        (7.55, "QUEST: A LINUX COMPUTER WE CAN LOG INTO.", "P"),
        (8.2, "Not a game console: a computer to install things on and build upon.", "V")]),
    ("2 Stage 1 secure", 20.0, [
        (12.3, "STAGE 1 SECURE THE ORIGINAL CARD", "P"),
        (13.25, "FACTORY CARD 48.8 GiB", "P"),
        (13.6, "EXTRACT THE WHOLE CARD", "P"),
        (14.2, "Our reference, and our way back.", "V"),
        (15.3, "SAFE ON DISK 42 GB, COMPRESSED", "P"),
        (16.4, "VERIFY: IDENTICAL byte for byte", "P"),
        (17.1, "The original card goes into a drawer, untouched.", "V"),
        (17.45, "FIRST, SECURE THE ORIGINAL. THEN EXPLORE IT.", "P")]),
    ("2b Stage 2 choose", 26.0, [
        (20.7, "Several community Linux systems exist for these clones.", "V"),
        (21.75, "ANOTHER SYSTEM: ITS INTERFACE RESTARTS IN A LOOP.", "P"),
        (22.55, "SET ASIDE", "P"),
        (23.2, "ArchR based on Arch Linux", "V"),
        (23.9, "LOOKS THE MOST LIKE A NORMAL LINUX. ALREADY HAS A DRIVER FOR THE WI-FI CHIP.", "P"),
        (24.55, "WE CHOOSE ArchR.", "P")]),
    ("3 Stage 3 screen", 34, [
        (26.75, "FIRST BOOT: NOTHING AT ALL.", "P"),
        (27.8, "These clones use many different screens, and ArchR needs a description of the right one.", "V"),
        (30.55, "ARCH R FLASHER BUILDS IT", "P"),
        (31, "from the original card's hardware description file.", "V"),
        (31.55, "THE SCREEN COMES ALIVE.", "P")]),
    ("4 Stage 4 keyboard", 40, [
        (35.3, "MULTI-PORT USB-C HUB NOT EVEN CAPS LOCK.", "P"),
        (37.4, "PLAIN USB-C TO USB-A WORKS STRAIGHT AWAY.", "P")]),
    ("5 Stage 5 terminal", 48, [
        (41.5, "A black screen: no login waits on the other terminals.", "V"),
        (43.15, "ONE BOOT LINE: TEXT MODE.", "P"),
        (44, "An administrator shell, right on the screen.", "V"),
        (44.75, "QWERTY AZERTY", "P"),
        (45.1, "French layout, built on the PC.", "V")]),
    ("6a Boss: invisible", 53.25, [
        (48.9, "lo loopback wi-fi none", "V"),
        (49.8, "The driver is on the card, not running.", "V"),
        (50.8, "Linux sees the slot. Nothing is in it.", "V"),
        (51.55, "THE CHIP IS INVISIBLE.", "P")]),
    ("6b Boss: pin 2", 59, [
        (53.7, "HARDWARE DESCRIPTION, PIN 2: ORIGINAL CARD pin 2 switches the chip on.", "V"),
        (54.6, "ArchR (GENERIC) pin 2 says if a card is inserted.", "V"),
        (56.35, "LISTENING ON THE WIRE IT SHOULD BE DRIVING.", "P"),
        (56.8, "The chip was never switched on.", "V")]),
    ("6c Boss: patches", 66, [
        (59.12, "PATCH 1 SWITCH THE CHIP ON", "P"),
        (59.5, "Firmware uploads, then fails on some boots.", "V"),
        (60.92, "PATCH 2 KEEP THE CLOCK RUNNING", "P"),
        (61.3, "One missing marker. Now wlan0 appears.", "V"),
        (62.72, "PATCH 3 THE RIGHT DOORBELL WIRE", "P"),
        (63.1, "Another wake-up pin: it sees the home network.", "V")]),
    ("7 Stage 7 router", 74, [
        (67.4, "AP is in CSA process, reject auth", "V"),
        (68, "Linux thought the router was changing channels, and politely refused to connect. Indefinitely.", "V"),
        (70.55, "2.4 GHz CHANNEL: AUTO 11", "P"),
        (71.15, "CONNECTED. AN ADDRESS ON THE HOME NETWORK.", "P")]),
    ("8 Stage 8 ssh", 81.75, [
        (74.6, "The PC sends its public key over the network.", "V"),
        (75.6, "Then the SSH service is switched on.", "V"),
        (77.6, "$ ssh luna", "P"),
        (77.8, "a shell on the handheld:", "V"),
        (78.65, "HELLO, LUNA.", "P")]),
    ("9 Story clear", 88, [
        (82.15, "STORY 1 CLEAR", "P"),
        (83.35, "EVERY ERROR MESSAGE POINTED AT THE NEXT PROBLEM.", "P"),
        (84.8, "And not every problem is on the device.", "V")]),
    ("10 End card", 93.5, [
        (88.5, "There Ain't No Such Thing As A Free LLM.", "V"),
        (88.8, "github.com/mdussere/tanstaafllm", "P"),
        (89.1, "A personal engineering project by Michael Dussere", "V")]),
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
