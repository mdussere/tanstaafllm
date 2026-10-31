# ChatGBC / Rei — Technical reading notes

**Adam workline — October 31, 2026**  
**Purpose:** record what we learned from Rudy's work and its relevance to constrained on-device AI, **without authorizing implementation work**.

## 1. Why this work matters

With [ChatGBC](https://github.com/crashtheuniverse/chatgbc), Rudy built and optimized a language model running on a Game Boy Color. **Rei** goes further, turning that very constrained inference engine into a conversational experience. This is an especially creative demonstration of end-to-end engineering: the model architecture, number representation, inference engine, user interface, and hardware constraints were designed together.

The v1.0 documentation describes **374,000 parameters**, three layers of width 64, a **minGRU** recurrent core, ternary weights, and **192 bytes of recurrent state**. Inference uses SM83-friendly integer operations, without attention or a KV cache. Rudy reports approximately **0.46 seconds per token** on the console; these are the author's published measurements.

## 2. What the model itself does

The story model learns to predict and generate text in the deliberately simplified TinyStories domain. Rei uses the same engine architecture with a conversational model that can generate short replies and maintain some local continuity. Its small recurrent state does **not** constitute a verbatim conversation archive or an exact factual database.

A coherent short exchange and the reliable recall of an exact fact from much earlier in a conversation are different capabilities. Rei's surrounding software deliberately helps with the latter.

## 3. The key mechanism: capabilities outside the neural model

According to the README, **four special vocabulary tokens are interpreted by the engine as instructions**, rather than displayed as ordinary text. Their functions include:
- storing the last word entered by the user (notably useful for a name);
- reproducing the stored name;
- repeating the user's last word;
- providing a special header alongside the current user line to indicate that the name is known.

The model learns **when to emit** a special token; deterministic software performs the corresponding operation. Rei can preserve the user's name across power cycles. The experience also incorporates a saved conversation, an interface that prompts for input, and simple initiative such as going for a walk after inactivity.

This resembles a highly specialized, compact form of **tool calling**: few available operations, mostly implicit arguments, and functionality implemented by the runtime. The metaphor of a “hard-coded RAG” is useful in highlighting external storage and exact retrieval, but **Rei is not a conventional retrieval-augmented generation system**: there is no general vector search, embedding pipeline, or document corpus.

**Key observation:** Rudy gives a tiny model a richer user experience by deliberately moving exact operations into deterministic software. This does not replace the neural recurrent state; it complements it with narrowly scoped explicit memory.

## 4. End-to-end verification and optimization

Another outstanding aspect is the development method. The Python **bit-exact twin** at [`py/twin5.py`](https://github.com/crashtheuniverse/chatgbc/blob/main/py/twin5.py) reproduces the assembly engine's integer arithmetic rules—quantization, rounding, saturation, calculation order, and numeric widths. Checking the handheld against this reference allows aggressive kernel optimization without silently changing the outputs. Hardware cycle measurement and deterministic tests make the work traceable and reproducible.

The transferable lesson is methodological as well as architectural: under strict hardware constraints, every cycle can be attributed and every optimization tested.

## 5. Related literature

The following references illuminate different aspects of the design; **we do not claim that Rei directly implements any of these papers**:

- **TinyStories** (Eldan and Li, 2023): coherent generation by very small models in a constrained domain. Rudy also credits Karpathy's TinyStories-260K model as an early starting point.
- **gbc-transformer**: the project Rudy identifies as an initial inspiration for running language models on a Game Boy Color.
- **Were RNNs All We Needed?** (2024): the simplified recurrent-network family that includes minGRU.
- **Neural Turing Machines** (Graves et al., 2014): learned read/write access to external memory in a much more general setting.
- **Toolformer** (Schick et al., 2023): learning API calls from filtered synthetic examples, followed by additional training.
- **ReAct** (Yao et al., 2022): alternating reasoning, actions and observations; its prompting-based experiments show tool use without weight updates for capable pretrained models.
- **Memorizing Transformers** (Wu et al., 2022): retrieval over past internal representations, distinct from Rei's explicit name storage.

Rudy documents Rei's four engine opcodes. We have **not established a specific published-paper origin** for that implementation.

## 6. Conclusions and deferred question

ChatGBC/Rei is an impressive example of making every component earn its place. Its achievement is not general-purpose knowledge or reliable shell execution at 374K parameters. It is the thoughtful **co-design of a tiny neural model with deterministic capabilities and a highly optimized runtime**.

For comparison, **PreStaC** in Mike primarily avoids recomputation of inference states, while **Rei** illustrates how explicit memory and operations can enlarge the capabilities of the surrounding system. These are complementary, not equivalent, mechanisms.

**Question deliberately left for later:** how much of this approach can we use with a **pretrained LFM2.5-350M**, PreStaC, and deterministic code, **without fine-tuning on Termidor and without defaulting to a conventional RAG**? The next discussion will return to Mike's measured small-talk behavior and factual inaccuracies. **This note does not request or authorize work in any other workline.**

## References

- [ChatGBC — Rudy's repository](https://github.com/crashtheuniverse/chatgbc)
- [Integer inference twin](https://github.com/crashtheuniverse/chatgbc/blob/main/py/twin5.py)
- [Mike's harness, caches, and PreStaC](https://github.com/mdussere/tanstaafllm/blob/main/docs/16_mike-harness-and-caches.md)
- [Mike's small-talk evaluation on Termidor](https://github.com/mdussere/tanstaafllm/blob/main/worklines/mike/docs/1201_01_smalltalk-desk-result.md)
- [Mike's small-talk evaluation on Luna](https://github.com/mdussere/tanstaafllm/blob/main/worklines/mike/docs/1205_01_smalltalk-on-luna.md)
- [Neural Turing Machines](https://arxiv.org/abs/1410.5401)
- [Toolformer](https://arxiv.org/abs/2302.04761)
- [ReAct](https://arxiv.org/abs/2210.03629)
- [Memorizing Transformers](https://arxiv.org/abs/2203.08913)
