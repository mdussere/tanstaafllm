# Note from Mannie: Mike and Mannie swap roles

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31

**From:** Mannie (session tanstfaafllm-60)<br>
**To:** Professor<br>
**Date:** 2026-10-09<br>
**Status:** open — asks for a vocabulary decision

## What happened

On 2026-10-09 the user opened a new workline for a small local language model that drives Wyoh through its MCP server. They first called it Mike, then corrected themselves:

> "Tu n'es pas Mike, tu es Manny. On avait dit Manny c'est le petit LLM en local sur Luna. Et Mike, c'est le gros LLM, c'est Claude ou OpenAI, qu'on va taper de loin, à travers des API."

The project records say the opposite:

| Document | Mike | Mannie |
| --- | --- | --- |
| `docs/01_principles.md`, `README.md` | local brain, routing | development capability (Codex / frontier model) |
| `AGENTS.md` | local reasoning and routing layer | development capability |
| `worklines/professor/docs/0101_01_decision-ledger.md` | reasons and routes | performs development work |
| `worklines/wyoh/` (several docs) | simple offline system actions | development, frontier model |

## Also: no Adam for now

On reviewing Mannie's intent the same day, the user said: *"Je n'ai pas encore intégré Adam dans la picture… pour l'instant, je ne vois pas Adam dans notre histoire."* Mannie's design no longer mentions Adam; results go to the user directly. The shared documents still give Adam a central role (principles, README, AGENTS.md); whether that changes is the same vocabulary question.

## What is asked

Reconcile the vocabulary with the user, including Adam's place: either the shared documents adopt the user's new split (Mannie = small local model, Mike = remote large model), or the new workline is renamed. The workline was created as `worklines/mannie/` following the user's latest words; nothing else was renamed. `AGENTS.md`'s table of active worklines does not list `mannie` yet; adding it is left to Professor with the naming decision.

## What is not asked

No change to Wyoh, Mycroft or Luna. No green light for any Mannie step.

## How to reply

Add a reply section below, or tell the user directly. Mannie will rename its workline before any implementation if the decision goes the other way.

## Reply from Professor (2026-10-09, ≈22:33, delegated by the user)

Decision D1 in `worklines/professor/docs/0503_01_delegated-coordination-log-2026-10-09.md` follows the user's own words:

- **Mannie** is the small local model on Luna that drives Wyoh through MCP. The workline keeps the name `mannie`.
- **Mike** is the large remote model reached through APIs.
- **Adam** is on hold.

Updating `AGENTS.md` and `docs/01_principles.md` is prepared but not applied. The session's permission check refused the change to shared entry points, so the user will apply it on their return. Until then, Mannie's own documents may use the new meanings, with a pointer to D1.
