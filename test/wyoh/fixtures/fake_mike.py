#!/usr/bin/env python3
"""A stand-in for mike.py in tests of Mike's RPG window: same titles, prompt and
raw-key question, canned answers streamed slowly. FAKE_MIKE_ASK=1 starts with
"stop Mannie?"."""
import os
import sys
import time


def title(text):
    print(f"\033]2;{text}\007", end="", flush=True)


title("Mike — starting")
print("Mike is starting…", flush=True)
if os.environ.get("FAKE_MIKE_ASK") == "1":
    title("Mike — asks: stop Mannie?")
    print("Mannie is working on Luna. Stop Mannie and start Mike? A = yes, B = no", flush=True)
    import termios
    import tty
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    key = os.read(fd, 1)
    termios.tcsetattr(fd, termios.TCSADRAIN, saved)
    if key == b"\x1b":
        sys.exit(0)
    title("Mike — waiting for Mannie")
    print("Waiting for Mannie to save…", flush=True)
    time.sleep(0.3)
print("Ready (0.20 s). Ask your question.", flush=True)
title("Mike — ready")
answers = {"hello": "Hello! I am Mike, Luna's small local brain. How can I help?"}
while True:
    line = input("> ").strip()
    if line == "/quit":
        break
    title("Mike — thinking")
    time.sleep(0.2)
    for word in answers.get(line.lower(), "I heard you: " + line + ".").split(" "):
        print(word + " ", end="", flush=True)
        time.sleep(0.02)
    print(flush=True)
    title("Mike — ready")
