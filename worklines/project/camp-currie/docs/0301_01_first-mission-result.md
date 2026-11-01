# Camp Currie — the simulated first mission (Step 3)

> **Freshness:** 🟢 current · **Written:** 2026-11-02 · **Checked:** 2026-11-02 · **Step:** Camp Currie 3

"Meet the Crew" can be played from start to end with the keys alone. No speech is involved: a labelled, deterministic evaluator decides each transmission. The shell itself is in [0201_01](0201_01_shell-result.md).

## The mission

| Contact | Says first | Target | Hint |
|---|---|---|---|
| Mannie (key-art portrait) | "Mannie here, on the comm. Say my name, recruit." | Mannie | MAN-ee |
| Wyoh (key-art portrait) | "This is Wyoh. Call me by my name." | Wyoh | WHY-oh |
| Mycroft (drawn microphone) | "Mycroft listening. Who am I?" | Mycroft | MY-kroft |
| Mike (key-art portrait) | "Mike online. Your turn: my name." | Mike | MIKE |
| Luna (drawn Moon) | "Luna control. Name the station." | Luna | LOO-nah |

Wolfenstein, the sixth Level 1 name, comes with the full Level 1 in Step 5.

**Each contact runs the same loop:** the call comes in (portrait, signal bars, typed line, target and hint) → Your turn (TRANSMIT or LISTEN AGAIN) → a result stamp → the next contact or the debrief.

- **CLEAR!** lights one of the five signal lights.
- **TRY AGAIN** and **NOT SURE** send the learner back to Your turn.
  - *Not sure* never counts as a retry, and the relay says "That says nothing about your accent".

**The debrief shows:**
- a rank: S for no retry and at most one *not sure*; A for up to two retries; B beyond that;
- contacts, transmissions, retries and *not sure*;
- "Simulated results, not a pronunciation score".

## Evidence

- The core tests cover each outcome, listen again, Back at every level, and a whole mission with the default script: 7 transmissions, 1 retry, 1 *not sure*, rank A, all five lights lit.
- The rendered run saves each outcome's screen and the debrief (sheet in [0201_01](0201_01_shell-result.md)), all inspected.
- On `luna-pi`'s real Sway, the full mission reached the debrief (`results/camp-currie/luna-pi/20261102/cc.log`).

## Not done (later steps)

- Speech: the evaluator is replaced in Step 4, behind the same `evaluate(target, attempt)`.
- Luna: no run yet (needs Mannie's agreement and a slot), and no Wyoh launch entry yet.
