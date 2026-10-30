# Step 9.1 — PreStaC, the Prefetch Stack Cache: study

**Question answered:** what PreStaC is made of, how it fits with Mike's other layers and with Wyoh, Mycroft, Mannie and Luna, who calls whom, and how its asynchrony works.<br>
**Date:** 2026-10-26<br>
**Status:** design study, documentation only. Nothing is built.
- **Sources:**
  - the user's design (plan Step 9);
  - Luna measurements `docs/0405_01`;
  - prompt breakdown, this session (2026-10-26);
  - `llama-server` b11429;
  - Wyoh's Slate and gamepad daemon (`src/wyoh/wyoh_slate.py`, `src/wyoh/wyoh_gamepad.py`).
- **Status of claims:** points not yet verified are marked **(to check)** and gathered in § 11.

## 1. The idea in one paragraph

On Luna, Mike's model reads about 6.7 tokens per second. A 1,000-token context therefore takes about 2.5 minutes to read, while a question is only 2–14 tokens.

The user's observation: **the context is almost entirely built during navigation, and Mycroft adds the star at the top of the tree, the question.** So PreStaC:
1. reads the context **before** the question, layer by layer, while the user navigates;
2. keeps the model's state after each layer in a **file**;
3. organises those files as a **stack**: entering a context pushes a layer, leaving it pops one;
4. when the question comes, restores the top state and reads only the question.

The user ruled out a server-class cache such as Redis or LMCache: it is too heavy for Luna, and it does not need to be shared between machines.

## 2. Decisions already taken (user)

| Decision | Source |
| --- | --- |
| A very simple, **file-based** cache, organised as a **stack**, with **prefetch** layer by layer during navigation | user, 2026-10-26 |
| PreStaC first; the layers are **optimised afterwards** (order, the tool JSON, compact rules) | user, 2026-10-26 |
| PreStaC is a **step of its own** (Step 9) | user, 2026-10-26 |
| The limiting factors are **CPU and context loading, not memory** | user, 2026-10-26 |
| No training of any kind; one action per order; every action needs the user's acceptance | plan, key decisions |

## 3. What the runtime gives us (facts)

From the measurements in `docs/03b3_01` and `docs/0405_01`:

| Fact | Value | Where measured |
| --- | --- | --- |
| `llama-server` saves a slot's state to a named file and restores it (`POST /slots/0?action=save` / `restore`, `--slot-save-path`) | works | desk and Luna |
| After a restore, a request that starts with the restored tokens reads only the rest | yes: 400 restored, 682 read | Luna |
| Without an explicit save and restore, `llama-server` re-reads the whole prompt for LFM2.5, a hybrid model, even with context checkpoints | yes | desk |
| State file for 400 tokens | 4.8 MB | desk (same model) |
| Reading speed, 4 threads | 9.1 tokens/s for the first 400 tokens, 6.6–6.8 tokens/s after that | Luna |
| Writing speed | 2.8–3.6 tokens/s | Luna |
| Model load | 3.5 s | Luna |
| Mike's current prompt | 1,081 tokens: 1,053 fixed (97.4 %), 12 desktop state, 16 turn and question | prompt breakdown |
| A question | 2–14 tokens, median 6 | 112 evaluation requests |

**What follows from LFM2.5 being a hybrid model:**
- Its state is mostly fixed-size convolution state, plus a cache for a few attention layers that grows with the number of tokens. **(to check:** how many attention layers, and the state size at 1,000 tokens).
- The state **cannot be cut back** to an earlier token. It can only be extended, or replaced by a restore.
- A stack fits that exactly: pushing extends, and popping replaces the state with a saved one.

## 4. Vocabulary

- **Layer:** a piece of prompt text with a name and a role. Examples: "L0 instructions and tools", "L1 desktop", "L2 terminal in `~/git`", "Q question".
- **Stack:** an ordered list of layers, from L0 at the bottom to the top. The prompt is the concatenation of the stack plus the question.
- **Frame:** a stack prefix `L0…Lk` with its **state file**, the model's state after reading exactly those tokens.
- **Key:** the identifier of a frame. It is a hash of the model, the runtime build, the chat-template rendering version, and the **token ids** of `L0…Lk`.
- **Wanted stack:** the stack that navigation currently asks for.
- **Ready depth:** how many of the wanted stack's frames already have a state file.
- **Prefetch:** the background work that raises the ready depth to the wanted depth.

## 5. Primitives

Three levels, each using only the one below.

### 5.1 The engine (over `llama-server`)

| Primitive | What it does | Built on |
| --- | --- | --- |
| `restore(key)` | load a frame's state into the slot | `POST /slots/0?action=restore {filename}` |
| `extend(tokens)` | read more tokens on top of the slot's current state, writing nothing | `POST /completion {prompt: tokens of the whole frame, n_predict: 0, cache_prompt: true}` **(to check:** that it reads only the new tokens after a restore, and leaves the state at exactly the end of the prompt) |
| `save(key)` | write the slot's state to the frame's file | `POST /slots/0?action=save {filename}` |
| `answer(tokens, grammar)` | read the question and write the call | `POST /completion` with the grammar, as in Step 3 |
| `cancel()` | stop the current read | close the HTTP request **(to check:** whether the server stops reading at once, between batches of 16 tokens, which is about 2.4 s on Luna, or not at all; and what state the slot is left in) |

The engine is one process and **one slot**: it does one thing at a time.

### 5.2 The store (files)

| Primitive | What it does |
| --- | --- |
| `lookup(key) → path or none` | is this frame already on disk? |
| `commit(key, metadata)` | make a saved state visible: write to a temporary name, then rename it, so that a half-written file is never used |
| `touch(key)` | mark it as recently used |
| `evict(budget)` | delete the least recently used frames beyond a byte budget; L0 is never evicted |
| `invalidate(prefix)` | drop frames after a model, runtime or template change (their key no longer matches anyway) |

### 5.3 The stack (PreStaC's API, used by Mike)

| Primitive | Who calls it | What it does |
| --- | --- | --- |
| `push(layer)` | Mike's context builder, on a navigation event | the wanted stack gets one more layer; prefetch is scheduled |
| `pop()` | the same, on leaving a context | the wanted stack loses its top layer; nothing to compute, since the frame below already exists |
| `replace_top(layer)` | the same, on a change of the top context (for example, a new terminal output) | pop + push |
| `set_stack(layers)` | the same, after a jump (another app, a reboot) | the wanted stack is replaced wholesale; frames that still match are kept |
| `ready() → depth` | Mike, the console | how much is prefetched |
| `ask(question, grammar) → answer` | Mike, when a question arrives | restore the deepest ready frame, extend with what is missing, then answer |
| `pause()` / `resume()` | Mike, on Mycroft's dictation start and stop | hold the prefetch so that Kroko gets the cores |

**Why "wanted" and "ready" are separate:** navigation changes the wanted stack instantly. The prefetcher catches up in the background. `ask` always works: it uses whatever is ready and reads the rest itself.

## 6. Where PreStaC sits, and who calls whom

```
 user ──gamepad/keyboard──► Wyoh daemon (wyoh_gamepad.py) ──► Sway (focus, windows)
                              │  ▲                    │
              navigation      │  │ proposal shown,    │ Slate (wyoh_slate.py, Unix socket)
              events          │  │ accept / refuse    │   ▲ dictated text
                              ▼  │                    │   │
                    ┌───────── Mike (one process on Luna, as michael) ─────────┐
                    │  context builder ──push/pop/set──► PreStaC               │
                    │  (Wyoh facts → layer text)          │ stack, prefetcher  │
                    │                                     │ store (files)      │
                    │  question (FN+B) ──ask────────────► │                    │
                    │                                     ▼                    │
                    │  contract.propose ◄── call ── engine adapter             │
                    └─────────────────────────────────────┬────────────────────┘
                                                          │ HTTP, localhost
                                                          ▼
                                     llama-server (one slot, holds /tmp/luna-brain.lock)
                                                          │
                                         ~/.cache/mike/prestac/*.bin (state files)

 Mycroft (Kroko, resident in the Slate) ── writes the words into the Slate;
                                             its dictation start/stop → pause/resume
 Mannie ── never runs with Mike (brain lock); Mike's state files stay on disk
```

**Who calls whom:**

| Caller | Called | When | Message |
| --- | --- | --- | --- |
| Wyoh daemon | Mike | focus change; Slate opened, and from where; terminal output changed **(to check:** which events Wyoh can give; Sway gives focus and window events, but not a terminal's working directory) | `context` event: the facts, not text |
| Mike's context builder | PreStaC | on each `context` event | `push`, `pop`, `replace_top` or `set_stack`, with rendered layer text |
| PreStaC's prefetcher | engine | in the background, one job at a time | `restore`, `extend`, `save` |
| Wyoh daemon | Mike | FN+B in the Slate (user decision, 2026-10-15; reserved today) | `ask` with the Slate's text |
| Wyoh daemon | Mike | dictation starts or stops (L2) | `dictation on/off` → `pause`/`resume` |
| Mike | PreStaC | on `ask` | `ask(question)` → the model's call |
| Mike | `contract.propose` | after the answer | the checked proposal |
| Mike | Wyoh daemon | the proposal is ready | shown to the user; nothing runs before acceptance |
| Wyoh daemon | Wyoh (Sway) | the user accepts | the adapter's fixed-template requests |

**Ownership:**
- **Wyoh** owns the facts about the desktop.
- **Mike** owns turning facts into layer text, and the stack.
- **`llama-server`** owns the computation.
- **Mycroft** owns the words.
- **PreStaC never talks to Wyoh or Mycroft directly.** It is a library inside Mike, so the Mike–Wyoh interface stays one socket (plan 5.4).

**The Mike–Wyoh socket** (a proposal for 5.4, to agree with Wyoh through a note): JSON lines over a Unix socket.
- Wyoh → Mike: `context`, `ask`, `dictation`, `cancel`.
- Mike → Wyoh: `ready {depth}`, `working`, `proposal {…}`, `refused {…}`, `busy`.

## 7. Asynchrony

### 7.1 One worker, one queue, coalesced

- There is one slot and one set of 4 cores, so all engine work runs **in one worker, one job at a time**.
- Navigation events can come several per second; reading one layer takes seconds on Luna. So the queue is **coalesced**: only the latest wanted stack matters.
- A short debounce (about 0.3–0.5 s, to tune) after an event avoids starting work for a context the user only passes through.

### 7.2 Prefetch

The worker repeatedly:
1. finds the first wanted frame that is not ready;
2. restores the frame below it, unless the slot already holds exactly that state;
3. extends with the missing layer;
4. saves and commits the result.

It works **bottom-up**: a deep frame needs every frame under it.

**Skipping restores:** most of the time the slot already holds the frame just below, from the previous step, so no restore is needed.

### 7.3 Cancellation

A job becomes useless when the wanted stack no longer contains the frame it is computing. The prefetcher then:
- cancels it, if cancelling is cheap **(to check**, § 5.1);
- or lets it finish, if it is almost done or if its frame is still a prefix of the new wanted stack. The common case is going deeper: the work is not wasted.

**Long layers:** they can be read in **chunks**, for example 64 tokens, about 10 s on Luna. A chunk is never saved as a frame; the chunks only make the read interruptible.

### 7.4 The question arrives

| Situation when `ask` comes | What PreStaC does | Cost on Luna |
| --- | --- | --- |
| The top frame is ready | restore it (unless the slot already holds it), read the question, answer | about 16 tokens ≈ 2.5 s, plus the answer, about 10 tokens ≈ 3 s, plus the restore **(to check)** |
| The prefetch is computing a frame of the wanted stack | let it finish (that work is needed anyway), then as above | the rest of that layer, plus the above |
| The prefetch is on a stale frame | cancel it, restore the deepest ready frame, read the missing layers and the question | depends on the missing layers |
| Nothing is ready except L0 | restore L0, read every other layer and the question | everything above L0 |

**Priority:** `ask` always outranks prefetch. While Mike answers, prefetch is held.

**After the answer:** the slot holds the frame plus the question, which no frame matches, so the next job starts with a restore.

### 7.5 Sharing the CPU with Kroko and with the desktop

- **While the user dictates,** Kroko takes about 1.5 of the 4 cores (estimate from RTF 0.76–0.79 at 2 threads, Mycroft `0908_01`). Prefetch therefore **pauses during dictation**.
  - The question only comes at the end of the dictation, so pausing costs nothing.
  - **Lowering the thread count instead does not work:** `llama-server`'s thread count is fixed at start.
- **While the user navigates,** prefetch competes with Sway and the apps. The worker can run at low priority (`nice`), so that the desktop stays responsive. **(to check:** effect on prefetch speed).
- **Battery:** prefetch only what the wanted stack needs, no speculative layers beyond it at first.

### 7.6 Start, stop and the brain lock

- **The engine** starts under `/tmp/luna-brain.lock`. Mike stops when Mannie needs Luna.
- **The state files outlive the process:** after a restart or a reboot, frames whose key still matches are reused at once.
- **L0 is computed once per model and runtime version,** at install, about 2.5 minutes on Luna for the current 1,053 tokens. After that it is only restored, so Mike starts warm.

## 8. Files

```
~/.cache/mike/prestac/<model-id>/
    <key>.bin     the state, written by llama-server under --slot-save-path
    <key>.json    {layers: [names], tokens, parent, created, last_used, bytes,
                   model_sha256, runtime_build, template_version}
    index.json    optional cache of the metadata, rebuilt from *.json if missing
```

- **The key:** SHA-256 of `model_sha256 + runtime_build + template_version + token ids of L0…Lk`.
  - It uses token ids, not text: the same text can be split into tokens differently at a layer boundary.
  - Two navigation paths that reach the same context share one frame.
- **Budget:** the frames are a few MB each. With a budget of about 200 MB (to set), that is tens of frames, and the user's home has 7 GB free.
  - **Eviction:** least recently used first.
  - **Pinned:** L0, and the frames of the current wanted stack.
- **Writes:** `llama-server` writes the file, and PreStaC renames it into place only after the save has returned. A crash therefore leaves no half-written frame.
- **Durability:** none is needed. A lost or corrupt frame is simply recomputed.

## 9. Rules for layers (to optimise later, Step 9.4)

1. **From the most stable to the most variable.** The current prompt breaks this rule: the desktop state sits before the 657-token tool JSON, so only 37 % was restorable. Moved to the end, 97.4 % is.
2. **Deterministic rendering:** the same facts give the same text. No clock, no unstable ordering (sort windows by a fixed key).
3. **Tokenise each layer on its own, then join the token ids.** Otherwise two words at a boundary may merge into one token, and the frames no longer line up.
4. **Respect the chat template:**
   - Layers L0…Lk all belong to the system turn. Today, the tool JSON is added by LFM2.5's template after the system text.
   - The question is the user turn, followed by the assistant opener.
   - PreStaC renders the template in pieces, as Mike already does with the template it renders itself.
5. **Small layers near the top,** because they are the ones navigation changes. Large stable material belongs at the bottom.

## 10. Failure modes

| Failure | Effect | Handling |
| --- | --- | --- |
| A restore fails (missing, corrupt, or incompatible file) | frame unusable | drop it, recompute from the frame below |
| `llama-server` dies | slot lost; files intact | restart under the lock; the files are reused |
| Disk full | a save fails | evict, then retry once; otherwise run without the cache (slow but correct) |
| Model, runtime or template change | every key misses | recompute L0, delete old frames |
| Navigation thrashing | prefetch never catches up | debounce; `ask` still works, more slowly |
| The question arrives during a long read | waits | cancellation granularity **(to check)**, chunked reads |
| A cache bug would give a wrong context | wrong proposal | a frame is used only when its key, which covers the exact token ids, matches; nothing runs without the user's acceptance anyway |

## 11. What is not known yet (to check first, in 9.2)

1. **`extend` with `n_predict: 0`:** after a restore, does it read only the new tokens, and leave the slot at exactly the end of the prompt, so that `save` captures exactly frame k+1?
2. **Cancellation:** does closing the HTTP request stop the read, how soon, and is the slot then usable or does it need a restore?
3. **Restore time on Luna,** for frames of 400, 1,000 and 1,500 tokens, from the SD card.
4. **State size against tokens** for LFM2.5-350M, for the disk budget.
5. **Reading speed of a short question after a long restored context.** Measured: 9.1 tokens/s at the start and 6.7 later, so it may drop further with depth.
6. **What Wyoh can tell Mike:**
   - Sway focus and window events, already in Wyoh's development MCP server (`sway_subscribe`);
   - the Slate's origin (terminal or Mannie);
   - a terminal's working directory and last output, which Sway does not know, so a terminal adapter would be needed (`0700_02`).
7. **Writing the state file:** time and SD-card wear for frequent saves.

## 12. Alternatives considered

| Option | Why not now |
| --- | --- |
| Redis, LMCache, SGLang's radix tree | server-class, GPU-oriented, too heavy for Luna (user) |
| `llama-server`'s own cache (`cache_prompt`, `--cache-ram`, context checkpoints) | automatic but opaque; with LFM2.5 it reused nothing across different prompts in our test; kept as a complement |
| `llama-completion --prompt-cache FILE` per request | one process per question: 3.5 s of model load each time, and one cache file per process |
| Linking `libllama` directly (state get/set in memory, sequences copied in RAM) | the most efficient, and it could keep several frames in RAM; a later optimisation once the protocol is proven with `llama-server` |

## 13. What 9.2 would measure (proposal, needs a green light)

**On the desk host:**
- the primitives of § 5;
- the unknowns of § 11, items 1, 2 and 4;
- a simulated navigation path:
  1. L0;
  2. desktop;
  3. terminal;
  4. terminal after `ls`;
  5. back to the desktop;
  6. a question at each step.

**Reported for each question:**
- the share of prompt tokens restored, with **95 % or more** as the target;
- the tokens read;
- the time from question to answer;
- the background prefetch time;
- the state files' size.

**Then on Luna (9.3), through Professor and Mannie:** items 3 and 5 of § 11, and the same path.
