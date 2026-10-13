"""Mike Step 2 evaluation: the set, the scoring, and the keyword baseline.

`eval_set.json` holds French requests, each with a scripted desktop and the
call the contract expects (`worklines/mike/docs/0102_01`). Two scores are
kept for every answer:

- **model**: the model's own call equals the expected call;
- **adapter**: the call the adapter would propose (after its rewrite rules)
  equals the expected call. Whether the adapter then refuses (for example a
  planned app that is not installed) is reported, not scored.

The keyword baseline is the least sufficient mechanism the model must beat:
verbs and app names, no model at all.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO / "src" / "mike"))
import mike_contract as contract  # noqa: E402

EVAL_SET = Path(__file__).with_name("eval_set.json")
HOLDOUT_SET = Path(__file__).with_name("eval_set_holdout.json")  # never used for tuning


@dataclass(frozen=True)
class EvalCase:
    request: str
    desktop: contract.Desktop
    expected: contract.Call
    tag: str


def load_cases(path: Path = EVAL_SET) -> list[EvalCase]:
    data = json.loads(path.read_text())
    desktops = {key: contract.Desktop(tuple(d["open"]), d["focus"]) for key, d in data["desktops"].items()}
    return [EvalCase(row["request"], desktops[row["desktop"]], contract.Call(row["tool"], row["args"]), row["tag"])
            for row in data["cases"]]


def _norm_text(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip().strip("\"'.!").casefold()


def same_call(expected: contract.Call, got: contract.Call | None) -> bool:
    """A missing call counts as `none`; `none`'s reason is not compared."""
    tool = got.tool if got else "none"
    if tool != expected.tool:
        return False
    if expected.tool == "none":
        return True
    args = got.args if got else {}
    if expected.tool == "type_text":
        return _norm_text(args.get("text", "")) == _norm_text(expected.args["text"])
    return all(args.get(k) == v for k, v in expected.args.items())


def score(case: EvalCase, got: contract.Call | None) -> dict[str, Any]:
    proposal = contract.propose(got or contract.Call("none", {"reason": "text answer"}), case.desktop)
    return {
        "model": same_call(case.expected, got),
        "adapter": same_call(case.expected, proposal.call),
        "proposal": proposal.kind,
        "rewritten": proposal.rewritten_from is not None,
    }


def tally(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_tool: dict[str, list[int]] = {}
    for row in rows:
        counts = by_tool.setdefault(row["expected"]["tool"], [0, 0, 0])
        counts[0] += row["model"]
        counts[1] += row["adapter"]
        counts[2] += 1
    return {
        "n": len(rows),
        "model": sum(r["model"] for r in rows),
        "adapter": sum(r["adapter"] for r in rows),
        "by_tool": {tool: {"model": m, "adapter": a, "n": n} for tool, (m, a, n) in sorted(by_tool.items())},
    }


def evaluate(predict: Callable[[EvalCase], contract.Call | None], cases: list[EvalCase] | None = None) -> dict[str, Any]:
    rows = []
    for case in cases or load_cases():
        got = predict(case)
        rows.append({"request": case.request, "tag": case.tag,
                     "expected": {"tool": case.expected.tool, "args": case.expected.args},
                     "got": None if got is None else {"tool": got.tool, "args": got.args},
                     **score(case, got)})
    return {"summary": tally(rows), "rows": rows}


# --- keyword baseline ---------------------------------------------------------

def _fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.casefold())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn").replace("’", "'")


_NAMES = sorted(((_fold(name), app.id) for app in contract.ALLOWLIST for name in app.names_fr + (app.id,)),
                key=lambda pair: -len(pair[0]))
_TYPE = re.compile(r"^(ecris|tape|saisis)\s+(?:le texte\s+)?(.+)$")
_LIST = re.compile(r"(quelles? (fenetres|applications)|qu'est-ce (qui est|que j'ai d')? ?ouvert|liste les fenetres|fenetres ouvertes)")
_CLOSE = re.compile(r"^(ferme|fermer|quitte|tue|arrete)\b")
_PLACES = [("plein ecran", "full"), ("gauche", "left"), ("droite", "right"), ("en haut", "top"),
           ("remonte", "top"), ("en bas", "bottom"), ("vers le bas", "bottom"), ("descends", "bottom")]
_MOVE = re.compile(r"^(mets?|place|deplace|passe|agrandis|plein ecran|descends|remonte)\b")
_FOCUS = re.compile(r"^(passe (sur|a)|va sur|reviens|bascule|montre|active|focus|remets|je veux voir)\b")
_LAUNCH = re.compile(r"^(ouvre|lance|demarre|affiche|je veux jouer|on fait|j'ai besoin)\b")


def _app_in(text: str) -> str | None:
    for name, app in _NAMES:
        if re.search(rf"\b{re.escape(name)}\b", text):
            return app
    return None


def keyword_baseline(case: EvalCase) -> contract.Call:
    text = _fold(case.request).strip()
    raw = case.request.strip()
    if match := _TYPE.match(text):
        # keep the user's own spelling of the text
        words = raw.split(maxsplit=1)[1]
        if words.casefold().startswith("le texte "):
            words = words[len("le texte "):]
        return contract.Call("type_text", {"text": words})
    if _LIST.search(text):
        return contract.Call("list_windows")
    app = _app_in(text)
    if app is None and re.search(r"\bca\b", text):
        app = case.desktop.focus
    if app is None:
        return contract.Call("none", {"reason": "no app or action recognised"})
    if _CLOSE.match(text):
        return contract.Call("close_window", {"app": app})
    place = next((p for word, p in _PLACES if word in text), None)
    if place and _MOVE.match(text):
        return contract.Call("move_window", {"app": app, "place": place})
    if _FOCUS.match(text):
        return contract.Call("focus_window", {"app": app})
    if _LAUNCH.match(text) or text == _fold(app) or len(text.split()) <= 2:
        return contract.Call("launch_app", {"app": app})
    return contract.Call("none", {"reason": "no action recognised"})


# --- option A: keyword table first, model second ------------------------------

NO_APP = "no app or action recognised"
NO_ACTION = "no action recognised"


def hybrid(case: EvalCase, model_call: contract.Call | None, variant: str) -> contract.Call | None:
    """Keyword table first; the model only where the table is unsure.

    ``model-on-any-miss``: the model answers whenever the table finds nothing.
    ``model-on-app-only``: the model answers only when the table found an app
    but no verb; with no app at all the answer stays ``none``.
    """
    rule = keyword_baseline(case)
    reason = rule.args.get("reason") if rule.tool == "none" else None
    if reason is None:
        return rule
    if variant == "model-on-any-miss" or reason == NO_ACTION:
        return model_call
    return rule


def hybrid_from_run(report: dict[str, Any], sets: dict[str, Path], variant: str) -> dict[str, Any]:
    """Re-score a saved model run (`test_model_eval.py` JSON) with the hybrid, no model needed."""
    out = {}
    for name, path in sets.items():
        cases = {c.request: c for c in load_cases(path)}
        for mode, result in report["sets"][name].items():
            got = {row["request"]: row["got"] for row in result["rows"]}

            def predict(case: EvalCase) -> contract.Call | None:
                g = got[case.request]
                return hybrid(case, contract.Call(g["tool"], g["args"]) if g else None, variant)

            out[f"{name}/{mode}"] = evaluate(predict, list(cases.values()))["summary"]
    return out
