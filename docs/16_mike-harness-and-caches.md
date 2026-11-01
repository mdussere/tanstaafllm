# 16 · Mike's chat harness and its caches

> For a code review. This page describes the code that runs Mike's small talk on Luna (Step 12) and every cache it relies on: what each piece does, who calls whom, with links to the lines. It ends with the review's findings and what Step 13 changed for each (§ 9).

**State described:** after Step 13's fixes (2026-10-31). The first edition described commit `bb53c0c`; § 9 keeps its findings. Mike's side is [`src/mike/mike.py`](../src/mike/mike.py) (called `smalltalk.py` until 2026-10-31; 484 lines, standard library only, imports `prestac.py` from its own directory) and [`src/mike/prestac.py`](../src/mike/prestac.py) (336 lines). Wyoh's side is the launcher [`src/wyoh/apps/mike/run`](../src/wyoh/apps/mike/run) and FN+B in [`src/wyoh/wyoh_gamepad.py`](../src/wyoh/wyoh_gamepad.py#L885-L895). The model is LFM2.5-350M Q4_0 in llama.cpp's `llama-server` b11429.

**Measured so far:**
- Desk: [`worklines/mike/docs/1201_01`](../worklines/mike/docs/1201_01_smalltalk-desk-result.md).
- Luna: [`1205_01`](../worklines/mike/docs/1205_01_smalltalk-on-luna.md). First word after 2.2–2.7 s (median), last word after 9–14 s, about 300 MiB.
- PreStaC on the desk: [`0902_01`](../worklines/mike/docs/0902_01_prestac-desk-result.md).

---

## 1. The pieces

![Mike's chat harness on Luna](img/mike-harness-architecture.png)

| Piece | Owner | Where | Role |
| --- | --- | --- | --- |
| Slate + FN+B | Wyoh | [`wyoh_gamepad.py` `mike_zone`](../src/wyoh/wyoh_gamepad.py#L1601-L1626), [`mike_wait`](../src/wyoh/wyoh_gamepad.py#L1628-L1646), [`mike_step`](../src/wyoh/wyoh_gamepad.py#L885-L895) | Starts Mike's window if absent, waits for the title "Mike — ready" (polls the Sway tree every 0.5 s, 90 s at most), then types the dictated text and Return. "Mike — busy" gives the notice "Mike cannot start while Mannie runs". |
| Window | Wyoh | [`apps/mike/run`](../src/wyoh/apps/mike/run), [`wyoh-app.toml`](../src/wyoh/apps/mike/wyoh-app.toml) | `foot -a mike`, then `runuser -l michael` and `python3 $MIKE_HOME/smalltalk.py`, which on Luna is now a link to `mike.py` until Wyoh's launcher names `mike.py`. Tiled, not fullscreen (the floating Slate must stay visible). |
| Client | Mike | [`mike.py`](../src/mike/mike.py) | The loop, the conversation as token ids, the L0 frame, the brain lock, the titles, the log. |
| Model server | llama.cpp | `~/.local/opt/mike/llama-b11429/llama-server` | One slot, context 2,048. Spawned by the client in its own process group, and dies with it ([`Server`](../src/mike/mike.py#L235-L334)). |
| PreStaC library | Mike | [`prestac.py`](../src/mike/prestac.py) | Stack of frames with prefetch (desk prototype of Step 9.2). The chat client uses its `Store`, `HttpEngine` and `frame_keys` for the L0 frame (§ 6). |

### What the client contains

| Function or class | Lines | Does |
| --- | --- | --- |
| [`Template`](../src/mike/mike.py#L74-L80) | 74–80 | The template's special ids, read from the server at start (`/props`): BOS, end of turn, `\n`. |
| [`Conversation`](../src/mike/mike.py#L83-L124) | 83–124 | The token tape: `l0`, `ids`, `turns`; `prompt_for()` (question capped at 600 characters), `finish()` (rolls over past `KEEP_CTX`), `reset()`. |
| [`sse_events`](../src/mike/mike.py#L127-L132) | 127–132 | Parses the server-sent-events stream of `/completion`. |
| [`take_lock`, `name_server_in_lock`, `release_lock`](../src/mike/mike.py#L169-L206) | 169–206 | `/tmp/luna-brain.lock` holds "mike <client pid> <server pid>". The client refuses while a live client holds it; a stale Mike lock has its orphan server stopped. |
| [`orphan_servers`, `stop_pid`, `_die_with_parent`](../src/mike/mike.py#L209-L231) | 153–231 | Finds a `llama-server` on Mike's port; stops a process group; makes the server receive SIGTERM when the client dies (`PR_SET_PDEATHSIG`). |
| [`Server`](../src/mike/mike.py#L235-L334) | 235–334 | Starts and owns `llama-server`, stops it. Also `post`, `get`, `tokenize`, `template`, `namespace`, `stream` and `rss_kib`. |
| [`L0Frame`](../src/mike/mike.py#L337-L363) | 337–363 | Layer L0 as a frame in PreStaC's `Store`: `put_back()` restores it, or reads L0 and saves it. |
| [`set_title`, `plain`](../src/mike/mike.py#L366-L373) | 366–373 | OSC 2 title for Sway; drops the model's `**` emphasis while printing. |
| [`answer`](../src/mike/mike.py#L376-L408) | 376–408 | One turn: stream, print, `finish`, and the turn's record. Ctrl+C stops the answer and keeps what was written. |
| [`main`](../src/mike/mike.py#L411-L480) | 411–480 | Arguments, `SIGHUP`/`SIGTERM` handlers, start, the L0 frame, the input loop, `/new`, `/quit`, rollover, the log. |

**Settings** ([lines 56–71](../src/mike/mike.py#L56-L71)):
- system prompt in French or English ("two or three short sentences");
- sampling from the model card: temperature 0.1, top-k 50, repeat penalty 1.05, no seed;
- `MAX_TOKENS` 120;
- `KEEP_CTX` 1,600, after which the conversation rolls over;
- `MAX_QUESTION_CHARS` 600;
- `FRAME_BUDGET` 20 MB for the frames.

**Environment:** `MIKE_HOME`, `MIKE_LANG`, `MIKE_PORT` (8091), `MIKE_SERVER`, `MIKE_MODEL`, `MIKE_LOCK`, `MIKE_REPACK`, `MIKE_THREADS` (4), `XDG_STATE_HOME`.

---

## 2. Start

```mermaid
sequenceDiagram
    autonumber
    participant W as Wyoh (FN+B)
    participant F as foot "mike"
    participant C as mike.py main()
    participant L as /tmp/luna-brain.lock
    participant S as llama-server
    participant D as slots/ (disk)
    W->>F: swaymsg exec apps/mike/run (if no "mike" window)
    F->>C: runuser -l michael python3 mike.py
    C->>F: title "Mike — starting"
    C->>L: take_lock(): O_EXCL create "mike <client pid>"
    alt another live client holds it (Mannie, another Mike)
        C->>F: title "Mike — busy", waits for Enter
    else a stale Mike lock
        C->>S: stop its orphan server, remove the lock, retry
    end
    C->>S: stop any llama-server already on the port (orphan)
    C->>S: spawn llama-server ... --slot-save-path slots/ (own group, dies with the client)
    C->>L: "mike <client pid> <server pid>"
    loop every 0.2 s, at most 300 s
        C->>S: GET /health
    end
    C->>S: GET /props, POST /tokenize (BOS, end of turn, \n, system turn) → Template, Conversation.l0
    C->>C: key = frame_keys(model name|size|mtime|build, [l0])
    alt Store has the frame
        C->>S: POST /slots/0?action=restore
        S->>D: read <key>.bin
    else first time, or the frame is unreadable
        C->>S: POST /completion {prompt: l0, n_predict: 0}
        C->>S: POST /slots/0?action=save (tmp-<key>.bin)
        S->>D: write tmp-<key>.bin
        C->>D: Store.commit: rename to <key>.bin, write <key>.json, evict
    end
    C->>F: "Prêt (x s)", title "Mike — ready"
    W->>F: types the text, Return
```

Measured on Luna ([`1205_01`](../worklines/mike/docs/1205_01_smalltalk-on-luna.md)):
- **3.7 s** to "ready" when the frame exists;
- **8.1 s** when L0 has to be read (the second start, with the model file probably still in memory);
- **11.0 s** the first time.

Wyoh measured FN+B with Mike closed: the question was delivered at 6.5 s and answered at 13 s.

---

## 3. One turn

```mermaid
sequenceDiagram
    autonumber
    participant U as user (stdin)
    participant C as mike.py
    participant S as llama-server slot 0
    participant J as chat.jsonl
    U->>C: input() → "Qui était Marie Curie ?"
    C->>C: title "Mike — thinking"
    C->>S: POST /tokenize "<|im_start|>user\n…<|im_end|>\n<|im_start|>assistant\n"
    C->>C: prompt = conv.ids + those ids   (prompt_for)
    C->>S: POST /completion {prompt: ids, stream, return_tokens, cache_prompt, n_predict 120, sampling}
    Note over S: common prefix with the slot kept,<br/>only the tail is read (prompt_n)
    loop one event per token
        S-->>C: data: {content, tokens:[id]}
        C-->>U: print(content) as it comes
    end
    S-->>C: data: {stop: true, timings}
    C->>C: conv.finish(prompt, answer ids)
    opt the history passed KEEP_CTX
        C->>S: L0Frame.put_back() (restore L0)
        C-->>U: "(long conversation: only the last exchange is kept)"
    end
    C->>J: question, answer, prompt_n, first_s, total_s, VmRSS/VmHWM
    C->>C: title "Mike — ready"
```

**Code path:** [`main` loop](../src/mike/mike.py#L454-L475) → [`answer`](../src/mike/mike.py#L376-L408) → [`Conversation.prompt_for`](../src/mike/mike.py#L102-L105) → [`Server.stream`](../src/mike/mike.py#L329-L334) → [`sse_events`](../src/mike/mike.py#L127-L132) → [`Conversation.finish`](../src/mike/mike.py#L107-L124).

**Each line of `chat.jsonl`** holds:
- the question and the answer;
- `prompt_tokens` (the size of the tape) and `prompt_n` (what the server really read);
- `predicted_n`, `first_s`, `total_s`, `prompt_ms`, `predicted_ms` and `stop`;
- `VmRSS` and `VmHWM` when the server belongs to the client.

---

## 4. The conversation as a token tape

![The conversation as a token tape](img/mike-token-tape.png)

The cache works only if what the client sends starts with **exactly** the tokens the slot holds. So the client never re-renders the history as text. It keeps the ids:

- **L0** ([line 95](../src/mike/mike.py#L95)) is `BOS` (id 1, read from the server) plus the tokenised system turn: 28–35 tokens.
- **The question** ([lines 104–105](../src/mike/mike.py#L104-L105), capped at 600 characters) is the user turn wrapped in LFM2's template, tokenised by the server with `parse_special`, so that `<|im_start|>` and `<|im_end|>` become single ids.
- **The answer** ([lines 113–117](../src/mike/mike.py#L113-L117)) is the ids exactly as generated. They end with `<|im_end|>` (id 7) when the model stops by itself; the client adds that id when the answer was cut at 120 tokens or stopped with Ctrl+C. Then comes `\n`, tokenised once at start.
- **The last generated token is not yet in the slot:** the model sampled it but never read it back. The next request therefore reads it, which is why a follow-up reads "the question + 2–3".
- **Why ids and not text:** in Step 12.1, sending the history as text once made the server read 59 tokens instead of about 16. A past answer, turned back into tokens, did not match the ids the model had generated.
- **LFM2 is a hybrid model** (attention plus convolution state). Its state can be extended, or replaced by a restore, but not cut back to an arbitrary earlier token. `/new` and a rollover therefore restore the L0 frame from disk ([lines 465 and 471](../src/mike/mike.py#L465-L471)) instead of asking the server to forget the turns.
- **Rollover** ([lines 118–124](../src/mike/mike.py#L118-L124)): past `KEEP_CTX`, only L0 and the last exchange are kept. Measured on the desk with the limit lowered to 260: the next question read 58 tokens (the kept exchange and itself), against 240 before the fix.
- **After Ctrl+C**, the server may have written a token or two that the client never received. The next prompt then differs from the slot's content near its end, and the hybrid model may read more than the question (not measured).

---

## 5. The four caches

![Mike's four caches](img/mike-cache-levels.png)

### 5.1 The slot (prompt cache)

- **Turned on per request** with `"cache_prompt": true` ([line 332](../src/mike/mike.py#L332)). The server compares the new prompt with what the slot holds, keeps the common prefix and reads the rest. `timings.prompt_n` says how many tokens it read.
- **One slot** (`-np 1`) and `--cache-ram 0`: no host-RAM cache of other prompts. Memory is the constraint on Luna.
- **For the hybrid model**, reuse works here because the client only ever extends the slot. The desk setting `lean-ckpt` (context checkpoints) gave the same results as `lean` in 12.1 (`results/mike/chat-baseline/20261031T110034Z/`), so the client does not use checkpoints.

### 5.2 Frames: the slot saved to a file

- **Saving and restoring:** [`L0Frame.put_back`](../src/mike/mike.py#L349-L363) uses `POST /slots/0?action=save|restore` with a file name. The server writes under `--slot-save-path` (`~/.local/state/mike/slots/`).
- **Size:** about 12.4 KB per token (`0902_01`). The chat L0 frame is 0.4–0.5 MB (`results/mike/smalltalk-desk/…/slots/`); the 1,053-token tool prompt of Step 9 made 13 MB.
- **The client saves one frame only, L0,** in PreStaC's `Store` ([`L0Frame`](../src/mike/mike.py#L337-L347)): key = `frame_keys(namespace, [L0])`, where the namespace is the model file's name, size and modification time plus the server's `build_info` ([`Server.namespace`](../src/mike/mike.py#L323-L327)). Commit is atomic (the server writes `tmp-<key>.bin`, renamed after the save returns), with a `.json` beside it, and eviction keeps 20 MB at most. The first client's `l0-*.bin` files are removed at start.

### 5.3 PreStaC (the library)

See § 6. The chat client does not use it.

### 5.4 The page cache

- **The model is memory-mapped.** About 230 MiB of the server's RSS is the file (`RssFile`), shared with the kernel's page cache.
- **On Luna, the first start took 11.0 s and the next 8.1 s.** Both read L0, so the 3 s difference is most likely the file already being in memory. Starting after a reboot has not been measured.

### 5.5 `llama-server` flags used by the client

From [`Server.__init__`](../src/mike/mike.py#L238-L250):

| Flag | Value | Why |
| --- | --- | --- |
| `-c` | 2048 | Context; `KEEP_CTX` 1,600 leaves room for a question and 120 tokens of answer |
| `-np` | 1 | One slot: one conversation |
| `-t` | 4 (`MIKE_THREADS`) | Luna's four cores; Kroko is idle while Mike answers |
| `--cache-ram` | 0 | No host copy of other prompts |
| `-b`, `-ub` | 16, 16 | "Lean": small batches, less memory (`0302_05`) |
| `--no-repack` | unless `MIKE_REPACK=1` | The repacked copy costs memory and was no faster on Luna (4.63 against 4.59–4.98 tokens/s) |
| `--slot-save-path` | `state/slots` | Allows the frames |
| `--no-webui` | | |

---

## 6. PreStaC, the library ([`prestac.py`](../src/mike/prestac.py))

PreStaC was designed for Mike's **tool** prompt (Step 9; study [`0901_01`](../worklines/mike/docs/0901_01_prestac-study.md)). That prompt has a fixed L0 of about 1,000 tokens, then a desktop layer, then app layers, and the question last. While the user navigates, a background worker reads each layer on top of the frame below and saves the result. A question then restores the deepest ready frame and reads only its own tokens.

```mermaid
classDiagram
    class Layer {
      name: str
      tokens: tuple[int]
    }
    class Store {
      root, budget = 200 MB
      lookup(key) bool
      commit(key, meta)  tmp-*.bin renamed, then .json
      touch(key)
      evict(pinned) LRU
    }
    class Engine {
      <<protocol>>
      restore(filename)
      save(filename)
      extend(tokens) timings
      answer(tokens, body) reply
    }
    class HttpEngine {
      url
      /slots/0?action=restore|save
      /completion n_predict 0 (extend)
      /completion (answer)
    }
    class PreStaC {
      wanted: list[Layer]
      slot_tokens
      set_stack / push / pop / replace_top
      pause / resume
      step()  one chunk of 64 tokens
      start() / stop()  worker thread
      ask(tail, body) AskResult
    }
    Engine <|.. HttpEngine
    PreStaC --> Store
    PreStaC --> Engine
    PreStaC --> Layer
```

| Part | Lines | Notes |
| --- | --- | --- |
| [`frame_keys`](../src/mike/prestac.py#L41-L48) | 41–48 | A chained SHA-256 of the namespace and each layer's ids. A frame's key covers every token below it. The namespace in the prototype: `model|b11429|prestac-l0-v1`. |
| [`Store`](../src/mike/prestac.py#L53-L109) | 53–109 | `<key>.bin` plus `<key>.json`. Commit renames the server's `tmp-<key>.bin`, so a crash never leaves a half-written frame. LRU eviction stays within the budget, and the wanted stack's frames are pinned. |
| [`HttpEngine`](../src/mike/prestac.py#L121-L145) | 121–145 | `extend` sends the whole frame so far with `n_predict: 0`; the prompt cache reads only the new chunk. |
| [`PreStaC.step`](../src/mike/prestac.py#L234-L276) | 234–276 | Finds the first missing frame. If the slot does not already hold a prefix of it, restores the frame below. Then reads up to 64 more tokens, and saves and commits when the frame is complete. A question waiting (`_asking`) or `pause()` (dictation) stops the worker between chunks. |
| [`PreStaC.ask`](../src/mike/prestac.py#L307-L336) | 307–336 | Waits at most for the chunk in progress (`_lock`), then uses the slot if it already holds the frame, otherwise restores the deepest ready frame, then answers. |

**Who uses it:**
- the desk prototype [`test/mike/test_prestac_desk.py`](../test/mike/test_prestac_desk.py#L70-L73), with the layers of [`test/mike/prestac_layers.py`](../test/mike/prestac_layers.py);
- the deterministic tests [`test/mike/test_prestac.py`](../test/mike/test_prestac.py), with a fake engine.

**Measured** (`0902_01`): 98.3 % of the prompt tokens restored over 117 questions, a median of 18 tokens read per question, the same answers with and without the cache (28/28).

**The chat client uses its lower levels only** (Step 13.3): `Store`, `HttpEngine` and `frame_keys` for the single L0 frame. It does not use the `PreStaC` class: one fixed layer and a history that grows by itself need no prefetch worker. Context banks (Step 16) would bring the class back.

---

## 7. Process lifetime and the brain lock

- **Luna runs one brain at a time** (user's rule): Mike's server and Mannie's Claude process need about 300 MiB each. About 400 MiB is available once Kroko and the desktop are loaded.
- **The lock holds "mike <client pid> <server pid>".** The client creates it with its own pid before spawning the server ([`take_lock`](../src/mike/mike.py#L169-L192)), then adds the server's pid ([`name_server_in_lock`](../src/mike/mike.py#L195-L198)). It removes the lock in [`Server.stop`](../src/mike/mike.py#L278-L287), which `main`'s `finally` calls ([line 479](../src/mike/mike.py#L479)).
- **The server dies with the client:**
  - `SIGHUP` (the window closing) and `SIGTERM` raise `SystemExit` in the client, so `finally` runs ([lines 425–428](../src/mike/mike.py#L425-L428));
  - the server runs in its own process group and is stopped as a group ([`stop_pid`](../src/mike/mike.py#L153-L166));
  - even after a `SIGKILL` of the client, the kernel sends `SIGTERM` to the server ([`_die_with_parent`](../src/mike/mike.py#L225-L231), `PR_SET_PDEATHSIG`).
  - Measured on the desk: after `SIGHUP`, `SIGTERM` or `SIGKILL` to the client, no server is left. After `SIGHUP` and `SIGTERM` the lock is gone too. After `SIGKILL` the lock stays, stale, and the next start removes it.
- **The client never adopts a running server:** a stale Mike lock has its orphan server stopped, and any `llama-server` still on Mike's port is stopped before the client spawns its own ([lines 261–263](../src/mike/mike.py#L261-L263)).

---

## 8. Tests

| Test | Kind | What it checks |
| --- | --- | --- |
| [`test_mike_client.py`](../test/mike/test_mike_client.py) | default | The tape (`prompt_for` and `finish`, the cut answer closed, the rollover, the capped question), SSE parsing, the brain lock with its orphan server, Ctrl+C during an answer, Markdown emphasis |
| same, `test_smalltalk_desk` | integration | 12.1's conversations through the client against a real server, cold then warm. Follow-ups read at most 40 tokens; after a restart, L0 is restored. |
| same, `test_client_signal_leaves_no_server_and_no_lock` | integration | `SIGHUP`, `SIGTERM`, `SIGKILL` to the client process: no server survives |
| same, `test_rollover_reads_only_the_kept_exchange` | integration | With `KEEP_CTX` at 260, the question after the rollover reads the kept exchange and itself |
| [`test_mike_client_luna.py`](../test/mike/test_mike_client_luna.py) | live | Four runs on Luna; timings and memory from `chat.jsonl` |
| [`test_chat_baseline.py`](../test/mike/test_chat_baseline.py) | integration | The OpenAI chat endpoint with the history as text (the comparison), and the answer length |
| [`test_prestac.py`](../test/mike/test_prestac.py), [`test_prestac_desk.py`](../test/mike/test_prestac_desk.py) | default, integration | The library with a fake engine and against `llama-server` |

---

## 9. The review's findings

The findings of the first edition (commit `bb53c0c`), ordered by impact. **Measured** means reproduced on Termidor; the others come from reading the code. What Step 13 did with each is in § 9.1; the line links in this table point to the first edition's code.

| # | Finding | Evidence | Effect | Options |
| --- | --- | --- | --- | --- |
| **F1** | **Dropping the oldest turn breaks the cache.** [`finish`](../src/mike/mike.py#L87-L90) cuts a turn out of the middle of the tape, so the next request matches only up to L0 and reads everything after it again. | **Measured:** with `KEEP_CTX` lowered to 260, the turn after the trim read 240 of 267 tokens. | At the real limit of 1,600 tokens: about 1,500 tokens read, **about 4 min on Luna** for one question, after 30–40 turns. | (a) At the limit, start a new conversation with a notice. (b) Keep the last turn or two and read them once, a few hundred tokens: about 30–60 s, announced. (c) A one-sentence summary as a new layer. (d) A larger context, at a memory cost. |
| **F2** | **The lock names the client, not the server.** If the client dies without running `finally`, the server keeps running and keeps its 300 MiB, while the lock points to a dead pid. The next lock check then treats the lock as stale. | **Measured:** a `SIGHUP` sent to the client alone left `llama-server` running, reparented, with the lock holding the dead client pid. On Luna, closing the window happened to stop both. | Mannie could start beside an orphan server: out of memory. A new client finds the orphan through `/health` and uses it with no lock. | Handle `SIGHUP` and `SIGTERM` in the client so that `finally` runs. Start the server in its own process group and stop the group. Write the server's pid into the lock. At start, treat a server that answers without a lock as an orphan and stop it. |
| **F3** | **A server found running is trusted blindly** ([line 124](../src/mike/mike.py#L124)): no lock, no ownership, and nobody stops it. | Code | Works with F2's orphans; two clients could share one slot and overwrite each other's state. | Refuse, or adopt the server only through the lock. |
| **F4** | **Two implementations of frames.** The client's [`restore_or_save`](../src/mike/mike.py#L178-L188) does not use `prestac.Store`. | Code | The client has no atomic save, no metadata, no eviction (one stale file per edited prompt), and keys the frame on the model's **file name** (F5). | Move the L0 frame onto `prestac.Store` + `HttpEngine`, which are stdlib-only and fit Luna. Or keep it tiny on purpose and say so. |
| **F5** | **The frame key ignores the model's content and the runtime build.** | Code | A model file replaced under the same name, or a new `llama-server`, could restore an incompatible state. Whether llama.cpp detects this is not checked. | Put the model's size and modification time (or its SHA-256, once) and the build number into the key, as PreStaC's namespace does. |
| **F6** | **The save is not atomic** (written straight to the final name). | Code | A crash during the save leaves a truncated file. The next restore probably fails with an HTTP error (not checked) and falls back to reading L0 again and overwriting the file. | `Store.commit`'s temporary name, then a rename. |
| **F7** | **Ctrl+C quits Mike entirely**, even in the middle of an answer. | Code | No way to stop a long answer and keep talking. | Catch the interrupt inside `answer`, close the stream, keep the ids generated so far (as for a cut answer). |
| **F8** | **The template is hard-coded for LFM2** (`BOS` 1, `IM_END` 7, the `<|im_start|>` strings). | [Lines 46, 68, 77](../src/mike/mike.py#L46) | Changing the model means changing the code. | Read the BOS from `/props` and tokenise `<|im_end|>` once at start. |
| **F9** | **Two `/tokenize` calls per turn**, one of them for the constant `"\n"`. | [Line 85](../src/mike/mike.py#L85) | Negligible (local HTTP). | Tokenise `"\n"` once at start. |
| **F10** | **No guard on a long question.** 1,600 + a 300-token dictation + 120 tokens of answer comes close to 2,048. | Code | Rare; the server would refuse or cut. | Cap the question, or trim before it is added. |
| **F11** | **The model's Markdown is printed raw** (`**deux**`). | 12.1 answers | Cosmetic, in a terminal. | Strip `**` and `#` while printing, or ask for plain text in the prompt. |
| **F12** | **`PreStaC.ask` forgets the slot after answering** ([line 329](../src/mike/prestac.py#L329)). The next prefetch always restores a frame, even when the slot already holds the prefix. | Code | One avoidable restore per question in the tool harness. | Keep `slot_tokens` = the prompt sent (without the answer) when it is useful. |

### 9.1 What Step 13 changed (user: "apply the fixes", 2026-10-31)

| # | Status | What changed | Evidence |
| --- | --- | --- | --- |
| F1 | ✅ fixed | Past `KEEP_CTX` the conversation rolls over: L0 restored, the last exchange kept, a one-line notice. | Desk, limit 260: 58 tokens read after the rollover, against 240 before |
| F2 | ✅ fixed | Signal handlers, the server in its own process group, `PR_SET_PDEATHSIG`; the lock names the client and the server. | Desk: no server left after `SIGHUP`, `SIGTERM` or `SIGKILL` |
| F3 | ✅ fixed | No adoption: orphans on the port are stopped, the client always owns its server. | Default test with a fake `llama-server` process |
| F4 | ✅ fixed | The L0 frame lives in PreStaC's `Store` through `HttpEngine`. | Desk integration test (cold, then warm: L0 restored) |
| F5 | ✅ fixed | The key's namespace holds the model file's name, size, modification time and the server build. | Code |
| F6 | ✅ fixed | Atomic commit: `tmp-<key>.bin` renamed after the save returns. | Code (PreStaC's `Store`) |
| F7 | ✅ fixed | Ctrl+C stops the answer; what was written is kept in the conversation. At the prompt, Ctrl+C still quits. | Default test with a fake stream |
| F8 | ✅ fixed | BOS and end-of-turn ids are read from the server. The `<|im_start|>` strings remain LFM2's (ChatML) template. | Code |
| F9 | ✅ fixed | `\n` is tokenised once. | Code |
| F10 | ✅ fixed | Questions are capped at 600 characters. | Default test |
| F11 | ✅ fixed | `**` and `__` are not printed (the log keeps the raw answer). | Default test |
| F12 | ⏸ kept | The slot then holds the question and the answer, which is never a prefix of a frame to compute, so remembering it would not save a restore. The finding was wrong. | Code reading |

**Still to do in Step 13:**
- 13.5: a system-prompt variant inviting "I am not sure", measured against Step 12's on the same questions.
- 13.6: Step 12.5's runs again on Luna, with Mannie stopped, to check that nothing got slower or bigger. `prestac.py` must now sit next to `mike.py` in `MIKE_HOME`.

*Written by Mike, 2026-10-31, for the user's code review; updated the same day after Step 13's fixes.*
