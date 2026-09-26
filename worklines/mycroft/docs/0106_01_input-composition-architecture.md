# Mycroft input and composition architecture

**Status:** planning decision, 2026-09-25. No interface, context source, classifier, or command execution is authorised by this document.

Mycroft is Luna's input-and-composition capability. Its already-measured ASR slice remains deliberately narrow: recorded audio, Sherpa reference decoder, and context-free text. The broader product path is:

```text
capture -> ASR hypotheses -> editable composition buffer -> explicit acceptance -> destination
```

Input modes may eventually select an intended destination and a bounded optional context. The backend contract must allow `context = []` and `alternatives = []`; the baseline must behave correctly with both empty. Context is not execution authority, and an accepted transcript is still distinct from a requested action.

The next evidence work has two independent tracks: (1) compact, FOSS ASR candidates with exact contextual-vocabulary capabilities verified; (2) a later controlled experiment comparing no context, mode context, environment context, and structured-command context on the same utterances. The source decision is [the shared discussion record](../../professor/docs/0102_03_shared-chatgpt-options-decision.md).
