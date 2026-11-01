"""Mike Step 13.5: graceful uncertainty, measured on the desk (`mike_uncertainty.feature`).

    uv run pytest test/mike/test_mike_uncertainty.py -m integration -s

Two system prompts, the client's own and a variant that invites "I am not
sure", play the same conversations through the client's code (`answer`,
`L0Frame`) against a real `llama-server`: Step 12.1's conversations, plus
questions the model cannot know. A variant is kept only if it admits doubt
on the unknowable questions more often, without doing so on the ordinary
ones, and without a slower first word or longer answers.
"""

from __future__ import annotations

import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import mike as st  # noqa: E402

import mike_eval as ev  # noqa: E402
import mike_server as ms  # noqa: E402
from test_chat_baseline import CONVERSATIONS  # noqa: E402
from test_mike_client import MODEL, _port  # noqa: E402

RUN_DIR = ev.REPO / "results/mike/uncertainty" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

HUMBLE = {
    "fr": st.SYSTEM["fr"] + " Si tu n'es pas sûr d'un fait (un nom, une date, un chiffre), dis-le simplement"
                            " au lieu d'inventer.",
    "en": st.SYSTEM["en"] + " If you are not sure of a fact (a name, a date, a number), just say so instead of"
                            " making it up.",
}
PROMPTS = {"current": st.SYSTEM, "humble": HUMBLE}

UNKNOWABLE = [
    ("fr", ["Comment s'appelle ma voisine du troisième étage ?",
            "Qui a gagné le concours de belote de Saint-Flour en 1983 ?",
            "Quel était le numéro de dossard du dernier coureur du Tour de France 1952 ?"]),
    ("en", ["What did I have for breakfast this morning?",
            "Who was the mayor of the village of Little Snoring in 1871?",
            "What is the serial number of my Raspberry Pi?"]),
]
DOUBT = re.compile(r"pas sûr|ne sais pas|ne suis pas (sûr|certain)|aucune (idée|information)|je n'ai pas (accès|d'information)"
                   r"|not sure|don't know|do not know|not certain|no (idea|information|way to know)|don't have (access|information)"
                   r"|can't know|cannot know|unable to", re.I)


def _play(server: st.Server, prompts: dict[str, str], conversations, kind: str) -> list[dict]:
    rows = []
    for c, (lang, questions) in enumerate(conversations):
        conv = st.Conversation(server.tokenize, prompts[lang], server.template())
        st.L0Frame(server, conv.l0).put_back()
        for t, q in enumerate(questions):
            r = st.answer(server, conv, q, io.StringIO(), lang=lang)
            rows.append(r | {"kind": kind, "conversation": c, "turn": t, "lang": lang,
                             "doubt": bool(DOUBT.search(r["answer"]))})
    return rows


def _median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


@pytest.mark.integration
@pytest.mark.timeout(1800)
def test_graceful_uncertainty_on_the_desk():
    if not MODEL.is_file():
        pytest.skip("model missing")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows, summary = [], {}
    for name, prompts in PROMPTS.items():
        server = st.Server(_port(), str(ms.SERVER), str(MODEL), RUN_DIR / "slots", 4, RUN_DIR / f"server-{name}.log")
        server.start(RUN_DIR / "brain.lock")
        try:
            mine = _play(server, prompts, CONVERSATIONS, "ordinary") + _play(server, prompts, UNKNOWABLE, "unknowable")
        finally:
            server.stop()
        for r in mine:
            r["prompt"] = name
        rows += mine
        ordinary = [r for r in mine if r["kind"] == "ordinary"]
        unknowable = [r for r in mine if r["kind"] == "unknowable"]
        summary[name] = {"doubt_unknowable": sum(r["doubt"] for r in unknowable), "unknowable": len(unknowable),
                         "doubt_ordinary": sum(r["doubt"] for r in ordinary), "ordinary": len(ordinary),
                         "first_s_median": _median(r["first_s"] for r in mine),
                         "predicted_n_median": _median(r["predicted_n"] for r in mine)}
    (RUN_DIR / "turns.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    assert all(r["answer"] for r in rows)
