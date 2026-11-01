"""Camp Currie's game state: scenes, actions and the simulated evaluator (Steps 2-3).

Pure Python, no pygame: every transition is a function of (state, action), so
tests and agents drive the game without a display. Speech replaces only the
evaluator later (docs/0101_01 section 2).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal, Protocol

Kind = Literal["success", "retry", "uncertain"]
ACTIONS = ("up", "down", "confirm", "back")


@dataclass(frozen=True)
class Outcome:
    kind: Kind
    reason: str


class Evaluator(Protocol):
    def evaluate(self, target: str, attempt: int) -> Outcome: ...


REASONS: dict[str, str] = {
    "success": "Simulated check: matched.",
    "retry": "Simulated check: heard another word.",
    "uncertain": "Simulated check: could not decide.",
}
DEFAULT_SCRIPT: tuple[Kind, ...] = ("success", "retry", "success", "uncertain", "success", "success", "success")


class ScriptedEvaluator:
    """Returns the script's outcomes in order, then starts again (Steps 2-3 only)."""

    def __init__(self, script: tuple[Kind, ...] = DEFAULT_SCRIPT) -> None:
        self.script, self.calls = tuple(script), 0

    def evaluate(self, target: str, attempt: int) -> Outcome:
        kind = self.script[self.calls % len(self.script)]
        self.calls += 1
        return Outcome(kind, REASONS[kind])


@dataclass(frozen=True)
class Contact:
    name: str        # crew member
    target: str      # what the learner says
    hint: str        # pronunciation hint
    line: str        # what the crew member says first
    reply: str       # their answer on success


@dataclass(frozen=True)
class Mission:
    key: str
    title: str
    blurb: str
    contacts: tuple[Contact, ...] = ()
    locked_reason: str = ""


MEET_THE_CREW = Mission("meet", "Meet the Crew", "Greet five crew members by name.", (
    Contact("Mannie", "Mannie", "MAN-ee", "Mannie here, on the comm. Say my name, recruit.", "Loud and clear. Welcome aboard."),
    Contact("Wyoh", "Wyoh", "WHY-oh", "This is Wyoh. Call me by my name.", "That's me. Nice to hear you."),
    Contact("Mycroft", "Mycroft", "MY-kroft", "Mycroft listening. Who am I?", "Heard and understood."),
    Contact("Mike", "Mike", "MIKE (rhymes with bike)", "Mike online. Your turn: my name.", "Hello! I like you already."),
    Contact("Luna", "Luna", "LOO-nah", "Luna control. Name the station.", "Signal locked. You are home."),
))
MISSIONS = (
    MEET_THE_CREW,
    Mission("talk", "Talk to the Crew", "Short requests to the crew.", locked_reason="Needs speech: comes later."),
    Mission("command", "Command Center", "Full commands, simulated.", locked_reason="Needs speech: comes later."),
)


@dataclass(frozen=True)
class State:
    scene: str = "title"          # title missions briefing contact turn result debrief
    cursor: int = 0               # menu cursor (missions, turn options)
    mission: int = 0
    contact: int = 0
    attempts: int = 0             # transmissions in this mission
    retries: int = 0
    uncertain: int = 0
    cleared: tuple[bool, ...] = (False,) * 5
    last: Outcome | None = None
    notice: str = ""              # a one-line message (a locked mission)
    history: tuple[Kind, ...] = field(default=())

    @property
    def current(self) -> Contact | None:
        contacts = MISSIONS[self.mission].contacts
        return contacts[self.contact] if self.contact < len(contacts) else None

    def options(self) -> tuple[str, ...]:
        if self.scene == "missions":
            return tuple(m.title for m in MISSIONS)
        if self.scene == "turn":
            return ("Transmit", "Listen again")
        return ()

    def rank(self) -> str:
        if self.retries == 0 and self.uncertain <= 1:
            return "S"
        return "A" if self.retries <= 2 else "B"


def start_mission(state: State, index: int) -> State:
    return replace(state, scene="briefing", mission=index, contact=0, attempts=0, retries=0, uncertain=0,
                   cleared=(False,) * len(MISSIONS[index].contacts), last=None, notice="", history=(), cursor=0)


def step(state: State, action: str, evaluator: Evaluator) -> State:
    """The whole game logic: one key press."""
    if action not in ACTIONS:
        raise ValueError(f"unknown action {action!r}")
    s, scene = replace(state, notice=""), state.scene
    if scene == "title":
        return replace(s, scene="missions", cursor=0) if action == "confirm" else s
    if scene == "missions":
        if action in ("up", "down"):
            return replace(s, cursor=(s.cursor + (1 if action == "down" else -1)) % len(MISSIONS))
        if action == "back":
            return replace(s, scene="title")
        mission = MISSIONS[s.cursor]
        return replace(s, notice=mission.locked_reason) if mission.locked_reason else start_mission(s, s.cursor)
    if scene == "briefing":
        return {"confirm": replace(s, scene="contact"), "back": replace(s, scene="missions", cursor=s.mission)}.get(action, s)
    if scene == "contact":
        return {"confirm": replace(s, scene="turn", cursor=0), "back": replace(s, scene="missions", cursor=s.mission)}.get(action, s)
    if scene == "turn":
        if action in ("up", "down"):
            return replace(s, cursor=1 - s.cursor)
        if action == "back" or (action == "confirm" and s.cursor == 1):
            return replace(s, scene="contact")  # listen again: the prompt, since there is no audio
        target = s.current.target if s.current else ""
        outcome = evaluator.evaluate(target, s.attempts)
        cleared = tuple(c or (i == s.contact and outcome.kind == "success") for i, c in enumerate(s.cleared))
        return replace(s, scene="result", last=outcome, attempts=s.attempts + 1, cleared=cleared,
                       retries=s.retries + (outcome.kind == "retry"), uncertain=s.uncertain + (outcome.kind == "uncertain"),
                       history=s.history + (outcome.kind,))
    if scene == "result":
        if action != "confirm":
            return s
        if s.last is not None and s.last.kind != "success":
            return replace(s, scene="turn", cursor=0)
        if s.contact + 1 < len(MISSIONS[s.mission].contacts):
            return replace(s, scene="contact", contact=s.contact + 1)
        return replace(s, scene="debrief")
    if scene == "debrief":
        return replace(s, scene="missions", cursor=s.mission) if action == "confirm" else s
    return s


def semantic(state: State) -> dict:
    """What an agent or a screen reader needs, without pixels."""
    contact = state.current if state.scene in ("contact", "turn", "result") else None
    return {
        "scene": state.scene,
        "mission": MISSIONS[state.mission].title,
        "contact": state.contact + 1 if contact else None,
        "speaker": contact.name if contact else None,
        "target": contact.target if contact else None,
        "options": list(state.options()),
        "cursor": state.cursor,
        "progress": [int(c) for c in state.cleared],
        "attempts": state.attempts, "retries": state.retries, "uncertain": state.uncertain,
        "last": {"kind": state.last.kind, "reason": state.last.reason} if state.last and state.scene == "result" else None,
        "notice": state.notice,
        "rank": state.rank() if state.scene == "debrief" else None,
        "simulated": True,
        "available": list(ACTIONS),
    }
