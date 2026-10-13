# Step 2 result — evaluation sets, fake Wyoh, scoring, keyword baseline

**Question answered:** what do we measure a model against, and how well does a model-free keyword table already do?<br>
**Date:** 2026-10-09<br>
**Status:** done under Professor's decision D13 (delegated by the user). Deterministic; no model, no device.

## What exists

| Item | File | What it does |
| --- | --- | --- |
| Contract and adapter | `src/mike/mike_contract.py` | the 7 tools, the 10-app allowlist, `propose()` (checks a call against the desktop, plans its Wyoh MCP requests from templates), `run()` (sends them only after acceptance), `windows_from_tree()` |
| Fake Wyoh | `test/mike/fake_wyoh.py` | answers `sway_get_tree`, `sway_command` and `wyoh_dev_keyboard_type` with the real names; keeps a small desktop; **any other tool is an error** |
| Main set | `test/mike/eval_set.json` | **81** French requests, each with one of five scripted desktops and the expected call |
| Held-out set | `test/mike/eval_set_holdout.json` | **31** new phrasings, written *after* the baseline and prompt v3 and never used to tune them |
| Scoring and baseline | `test/mike/mike_eval.py` | scores each answer twice (the model's call; the adapter's proposal after its rewrite rule) and holds the keyword baseline |
| Tests | `test/mike/test_mike_contract.py`, `test/mike/test_eval_baseline.py` | adapter mapping and refusals against the fake Wyoh; validity of both sets; baseline score |

Main set by expected tool: 18 `launch_app`, 15 `none`, 12 `move_window`, 10 `focus_window`, 10 `close_window`, 10 `type_text`, 6 `list_windows`.

It includes:
- 2 typos;
- a bare noun ("calculatrice");
- a deictic ("ferme ça");
- 2 apps that are not on the allowlist (Spotify, Photoshop);
- 13 out-of-scope requests (weather, e-mail, shutdown, Wi-Fi…).

All requests are lower case with no final punctuation, as Mycroft emits them.

## Adapter checks (Step 2.2)

The tests check that:
- every tool maps to the exact Wyoh MCP requests of the contract;
- `top`/`bottom` become Sway's `up`/`down`;
- the adapter refuses, with a reason, an app off the allowlist, a planned app that is not installed, an app with no known launch command, a closed window, a bad place, multi-line or too long text, an unknown tool such as `sway_command`, and extra arguments;
- a "focus" on a closed app is proposed as a launch (the ⚖️ rule);
- closing asks twice;
- nothing is sent to Wyoh before acceptance;
- accepted actions change the fake desktop as expected.

Writing the tests found one contract error: Sway has no `move top`. The contract now says `top` → `up` and `bottom` → `down`.

## Keyword baseline (Step 2.4)

A table of French verbs and app names, about 60 lines, with no model.

| Set | Right call | Note |
| --- | --- | --- |
| Main (81) | **80** | **Optimistic:** the table was written while reading this set. |
| Held-out (31) | **14** (45 %) | The honest figure: new phrasings ("tu peux m'ouvrir l'éditeur", "colle le terminal sur la gauche", "je n'ai plus besoin de l'éditeur") defeat it. |

Evidence: `results/mike/eval-baseline/<timestamp>/keyword-baseline.{main,holdout}.json`.

**What it means:** a keyword table is perfect on what it was written for and fragile on anything else. A model is only worth its RAM if it does clearly better than 45 % on the held-out set. Both figures stay in the record.

## Commands

```bash
uv run --group mike pytest test/mike -m "not live and not integration"   # 53 passed
```

## Limits

- The sets were written by one author in one evening. The held-out set guards against overfitting by the baseline and prompt v3, not against the author's own phrasing habits. Real Mycroft transcripts would make a better third set.
- Planned apps (`browser`, `files`, `chess`, `wolfenstein`, `dino`) have no window id or launch command yet. The adapter refuses them as "not installed", so the adapter score for them measures the proposal, not a working launch.
