# Story 2 — blind one-second storyboard comprehension check

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** Hazel 3.2e

## Question

Can a reviewer with no project context infer Story 2's story from only one still per second of the current scripted preview?

## Method

The repeatable integration test `test_story2_blind_storyboard_extracts_one_still_per_second` extracted the 90-second, 640×360 scripted Story 2 preview at one frame per second. It produced 90 PNG stills, ten chronological 3×3 contact sheets, a frame-to-second manifest and the complete ffmpeg log under:

`results/hazel/video-pipeline/20261105T202749-story2-blind-storyboard/`

The blind reviewer was started with no inherited conversation context and was explicitly restricted to the ten contact-sheet images (individual stills only if necessary). They received no repository, episode brief, comparison page, source files, audio or explanatory text outside the text visibly present in the frames.

Command and result:

```text
HAZEL_STORY2_BLIND_VIDEO=/home/michael/git/tanstfaafllm-story2-comparison/dist/media/story2-scripted-reconstruction.mp4 \
  uv run pytest -m integration test/hazel/test_video_pipeline.py -k blind --timeout=120 --timeout-method=thread

1 passed, 29 deselected in 5.26s
```

The readable behavioural contract is `test/hazel/story2_blind_storyboard.feature`.

## Blind reviewer result

**Yes, the reviewer understood the central story.** Their independent reconstruction was:

> A desktop-automation quest rejects screenshot/pixel guessing in favour of querying the desktop's own window tree, using named actions and waiting for events. An existing compositor/system interface is exposed to an agent, and the film concludes: “don't look at the desktop; ask it.”

They identified Wyoh/the desktop layer, a development agent, Sway/window-tree imagery and Luna as the principal visual actors. They also recovered the main progression:

| Seconds | Inferred beat |
| --- | --- |
| 0–17 | The “ASK THE DESKTOP” mission and desktop-without-pixels premise. |
| 18–35 | Screenshot/pixel ambiguity contrasted with a DOM-like desktop model. |
| 36–53 | Window tree, named actions/buttons and event waiting replace visual guessing. |
| 54–71 | A failed single-scene approach gives way to using the existing compositor. |
| 72–80 | Development-only capability is handed to agents: query, act, wait. |
| 81–89 | Black-panel/input problems resolve; the thesis returns at the end. |

## What this proves—and does not

The visual narrative and on-screen copy communicate the intended high-level argument without an external brief. The reviewer still could not tell whether labels represent deployed capability or a conceptual illustration, what the agent may decide on its own, or how production-ready the timings/tool count are. Those are appropriate uncertainties: the film should not imply more than it demonstrates.

This is one vision-model reviewer, not a human audience study. The one-second still format removes motion and the event-driven soundtrack, while retaining the on-screen title and copy; it tests storyboard-level comprehension, not the complete audiovisual experience. No context-assisted second pass was run, per the user's instruction.
