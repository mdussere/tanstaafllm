# Note from Wyoh — the input zone is Wyoh's for now

**From:** Wyoh workline
**To:** Mycroft workline
**Date:** 2026-10-07
**Status:** coordination note; changes no Mycroft step

By user decision, the **input zone** on Luna (where text is prepared before the system receives it) is owned by **Wyoh for now**. It is opened and validated with the device's controls (L1 opens or closes, L2 validates), as part of Wyoh's proposed Step 5 (Device interactors). Its first version takes keyboard text only. The user's long-term intent is that this zone becomes where text is **dictated and corrected by voice** before validation, which is Mycroft's composition capability.

To keep the hand-over simple, Wyoh's zone follows Mycroft's composition rules (`0106_01_input-composition-architecture.md` and plan item 5.6): text can be edited before acceptance, validation emits exactly once, and closing discards with no side effect. The zone delivers text to the window that had focus. That delivery is Wyoh's; producing and correcting the text is the part Mycroft is expected to take over.

Nothing in Mycroft's plan, green lights, or context boundary changes. When Mycroft is ready to provide dictation into the zone, the ownership split should be revisited explicitly.
