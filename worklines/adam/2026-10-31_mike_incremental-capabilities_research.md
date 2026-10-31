# Mike: Incremental Capabilities, Tool Routing, and Context-Aware PreStaC

**Adam workline — discussion notes, October 31, 2026**  
**Status:** exploratory input for Mike's workline; **not** an implementation request or a green light.  
**Related:** [ChatGBC / Rei analysis](2026-10-31_chatgbc_rei_analysis.md).

## 1. Product direction and non-regression principle

The starting point is **Mike as a small, fluent, friendly conversational companion on Luna**: pleasant small talk, useful to pass time on a train, without pretending to be a general knowledge engine. This baseline experience is intentional. **Add one capability at a time without degrading it**—especially conversational naturalness, responsiveness, resource consumption, and reliability.

Distinct lines of inquiry:
1. **Small talk:** better long conversations, history/context rollover, continuity, restart handling and graceful factual uncertainty.
2. **Information resources:** richer and more accurate answers using selected local knowledge, context banks, retrieval and perhaps later RAG; internet access is **not** the immediate objective.
3. **Tools:** accurate interpretation of Luna interface commands and safe mapping into one or **several** Wyoh/MCP operations, maintaining the existing user-confirmation contract.
4. **Inference economy:** exploit and extend PreStaC so the above remain practical on the hardware.

These are avenues, not an agreed implementation sequence.

## 2. Evidence: what exists today

- **Model:** pretrained LFM2.5-350M Q4_0, llama.cpp on Luna's RK3326, with approximately 1 GB RAM. Mike and Mannie run exclusively, not concurrently.
- **Small talk:** the Step 12 tests on Luna measured first visible output at **1.7–4.2 s**, typical medians **2.2–2.7 s**, about **4.6–5.0 tokens/s**, and approximately **300 MiB** server memory. The responses are conversational but sometimes confidently factually incorrect (e.g., misidentifying the author of *The Moon Is a Harsh Mistress* or Apollo 11 crew). Shorter output did not consistently improve accuracy.
- **PreStaC:** the Step 9 desk prototype implements a file-based **Prefetch Stack Cache**: hash-keyed layer-prefix inference frames, navigation-driven background prefill, push/pop/switch, restore on question, 64-token chunks, LRU disk budget. On Termidor, over **117 requests**, **98.3%** of prompt tokens were restored, median **18** new prompt tokens per question, and **28/28** sampled outputs matched uncached execution. The recorded median question-to-answer time was **0.32 s on Termidor**; this is **not** a Luna benchmark.
- **Crucial caveat:** cache correctness does not guarantee tool-selection accuracy. Reordering the tool definition and desktop layers lowered Mike's scores in the Step 9 evaluation. Prompt composition remains consequential.
- **Integration status:** the full `src/mike/prestac.py` stack prototype is not the current small-talk client's orchestration. Small talk already benefits from exact token-ID history and a saved/restored L0 prefix, but not the full navigation-triggered stack library.
- **Tool accuracy:** earlier closed-world tool routing scores were below the desired roughly **90%** reliability for actions; user approval remains mandatory.

Evidence: [Step 9 study](../mike/docs/0901_01_prestac-study.md), [Step 9 desk results](../mike/docs/0902_01_prestac-desk-result.md), [Step 12 desk](../mike/docs/1201_01_smalltalk-desk-result.md), [Step 12 Luna](../mike/docs/1205_01_smalltalk-on-luna.md), [harness and cache review](../../docs/16_mike-harness-and-caches.md).

## 3. The actual tool cost problem

Conventional LLM-driven tool use can involve:
1. an inference to decide **whether / which tool to call** and with what arguments;
2. external execution;
3. a second inference to **ingest the returned data** and formulate the response.

PreStaC efficiently eliminates repeat processing of *known prefixes*. It does **not** eliminate the live prefilling cost of newly returned tool content. A verbose tool result could erase much of the latency savings. The cost of the **decision** and the cost of **return ingestion** should therefore be studied independently.

For each tool, distinguish:
- raw output;
- task-relevant information;
- minimum representation passed to Mike.

A deterministic tool adapter may extract a tiny field (e.g. `available_ram_mb=550`) rather than passing full logs. For exact, safe queries, a direct deterministic answer might avoid a second LLM call altogether. For explanation or synthesis, the model still needs some fresh input. These are options, not a mandate to bypass Mike.

**Important limitation:** a newly generated tool result cannot in general be magically spliced into a previously computed recurrent/KV state. We can restore an exact *prefix* frame and process the new tail, or precompute a finite set of known alternatives; arbitrary state composition is not established.

## 4. Extend PreStaC: from a single navigation stack to context banks

The current PreStaC design follows a single evolving navigation stack. Explore **multiple prebuilt, switchable and reusable stacks**, not just a stack that grows and shrinks with the current window:

- thematic/domain stacks: **Wyoh internals**, Luna operations, project documentation, *The Moon Is a Harsh Mistress*, etc.;
- capability stacks: available MCP tools and their contracts;
- historical/session stacks: saved earlier contexts and the possibility of returning to them;
- static or slowly changing knowledge potentially prefetched outside the critical path;
- navigation-derived layers combined with a selected question-domain layer.

A question's subject—not merely Sway's focused application—could determine which complete prefix state Mike restores. **An inexpensive semantic router** selects a suitable bank/stack before Mike begins answering.

Key research questions: How to manage several frames within a disk budget? What is the real restore cost on Luna? Which prompt and state structures can be switched without losing necessary dialogue history? How to preserve correctness with hybrid recurrent state? How does the cost of reading a fresh suffix change with total context length? Is it better to cache one large knowledge prefix or several small domain-specific prefixes? Selection is not the same as merging independently computed states.

## 5. Before generation: micro decision models

Investigate whether a cheap **decision stage** can detect, before the main LLM:
- ordinary small talk vs local-knowledge question vs device/interface action;
- whether a tool or external lookup is needed;
- which knowledge stack(s) to restore or prepare;
- which tool or sequence of tools may be required.

A plain classifier solves only the first part. **A tool invocation is a function plus arguments**, possibly a sequence of MCP calls. For `ouvre le navigateur`, the pipeline is conceptually:

1. **Domain recognition:** Luna interface operation;
2. **Intent and slots:** `open` + `browser`;
3. **Grounding and planning:** resolve `browser` against available apps and map the intent to a validated Wyoh/MCP call or multi-call sequence;
4. **Safety:** preserve contractual user review/approval before applicable actions execute.

More difficult inputs include literal file paths, references to prior windows, ambiguity, and multi-step actions. The router should not be credited with full semantic parsing unless it actually handles these.

Possible model families (to compare, **not yet selected**):
- deterministic lexical rules, character n-gram **TF-IDF / linear classifiers**, weighted keywords;
- **fastText** or a very small discriminative classifier;
- compact character CNN, GRU/minGRU (inspired by Rudy's tightly constrained model, but for classification/slot tagging rather than story generation);
- cheap pretrained **sentence embeddings** for nearest-context matching, as a **zero-shot or few-shot semantic router**;
- slot tagging / span extraction plus deterministic argument resolution;
- Mike's own native function calling as a baseline, although this spends main-model inference on deciding.

**New point raised at the end of the discussion:** a zero-shot, embedding-based classifier may be particularly suitable for context selection. Compare an embedding for the question against embeddings of short domain descriptions, representative keywords, phrases or examples, using a similarity measure. Cheap lexical/semantic baselines—keyword overlap, character n-grams, TF-IDF, fuzzy or nearest-neighbor matching—should also be evaluated. An embedding-based router is a retrieval/semantic-similarity operation but **does not automatically imply deploying a full document RAG pipeline**.

Open questions: viable *micro* embedding model on Cortex-A35 and Termidor CPU; multilingual/French queries and ASR noise; memory footprint, embedding latency, thresholding, multi-label matches, out-of-domain rejection, and semantic mismatch between surface keywords and the needed tool. No measured winning model has been identified.

## 6. Two tool orchestration paths to compare

**Path A — native Mike decision:** Mike consumes the (possibly cached) tool contract, decides tool/function and arguments, receives a compact result and then answers. This is conceptually simpler but may require an expensive first and second LLM phase.

**Path B — early micro-route:** a very cheap classifier/semantic parser decides or proposes a tool and/or prefix context; a deterministic bridge validates arguments, resolves symbolic entities and constructs Wyoh/MCP operations; Mike only handles the conversational or interpretive portions. Error handling must include ambiguity, unknown requests and fallback.

Both should be measured end-to-end, and may coexist. **Accuracy of function and arguments, false actions, and user approval matter more than classification accuracy alone.**

## 7. Information-augmentation options (without assuming conventional RAG)

A knowledge-rich prefix can sometimes be preprocessed and cached, rather than retrieved at question time. Compare:
- a large prepared context containing relevant stable information;
- several narrower domain-specific PreStaC stacks selected semantically;
- targeted retrieval with very compact structured snippets or citations;
- small static lookup tables for exact facts;
- tools returning minimal fields or deterministic answers.

Large contexts have costs: initial prefill, persistent frame size, context-window limit and potential added latency on later tokens. A cache avoids repeat **prefill**, not every cost of long-context inference. On a hybrid recurrent model, exact sequencing and saved-state compatibility need particular care.

## 8. Research questions and evaluation criteria

Before selecting an architecture, establish a shared benchmark with representative utterances, ambiguous references, negations, compound commands, French ASR variants and out-of-scope inputs.

Measure **separately and end-to-end**:
- domain / stack routing correctness, including top-k and abstention;
- function selection **and exact arguments**, plus any correct MCP sequence;
- unsafe false positives and false negatives; confirmation and refusal;
- startup time, peak resident memory and disk footprint;
- router latency, frame restore, prompt prefill, tool time, result ingestion and generation time;
- conversational fluency and first-token latency **before and after every feature**;
- long-session correctness, rolling history behavior, restart behavior and cache compatibility.

Candidate experiments to discuss (not authorized here): lexical baseline vs tiny embedding model; micro-trained intent/slot tagger; prebuilt domain stacks; compact tool-response adapters; native LFM2.5 function calling vs micro-model dispatch; direct deterministic answers where appropriate.

## 10. October 31 follow-up — first concrete embedding use case: RAG over Luna's guide

**Adam's latest direction:** before using embeddings for generic zero-shot tool routing or semantic stack selection, **start with a simple, local RAG over Luna's existing guide / knowledge base**. The guide is the first corpus: bounded, available locally, project-specific, and straightforward to assess. **No internet retrieval is needed in this first stage.**

Conceptual flow:
1. Treat the Luna guide as the authoritative source material; identify its actual repository files and structure before designing ingestion.
2. Index meaningful, referenceable passages of that guide offline. Compare small embedding options, including the Model2Vec POTION family, against a cheap lexical baseline.
3. Embed the user's question; retrieve a small number of relevant passages and carry their source locations forward.
4. Give Mike **only the minimal relevant excerpts**, not a verbose search response; answer with appropriate uncertainty when the guide lacks an answer.
5. Measure factual grounding and end-to-end latency, especially **fresh passage prefill on Luna**. Fast embedding does not make a long retrieved chunk free to ingest.

**Performance goal discussed:** the *routing / embedding / retrieval decision* should ideally complete in **under 100 ms on Luna** (warm, resident process). This is a design target, not a demonstrated measurement, and is **distinct from** the time required for Mike to read the retrieved passage and generate a response.

**Candidate embedding models:** Model2Vec POTION-2M, 4M, and 8M; English-only use is acceptable if needed for accuracy or cost, because the user is willing to issue simple English commands. Do not assume a multilingual model is essential. Benchmark actual Luna CPU latency, RAM, indexing cost, and retrieval relevance before picking a model. Prior comparisons made during the discussion were estimates; MTEB aggregate and classification scores are **not zero-shot routing accuracy or Luna measurements**.

**Non-regression:** Mike remains a pleasant conversational companion; guide-based retrieval should be invoked where helpful, without turning every small-talk exchange into a search or slowing the baseline unnecessarily.

**Keep separate for later:** multi-stack semantic selection in PreStaC, micro-model tool/intent/argument parsing, and the two-pass speech-to-shell / MCP execution hypothesis remain valuable research directions, **not the immediate first embedding deliverable**.

This records Adam's requested priority and makes the note available for Mike's own discussion. It does **not** authorize autonomous implementation or deployments.

## 9. Boundaries and collaboration

This is **Adam's exploration for Mike to read and challenge**, not an instruction to change Mike's plan, start training, deploy on Luna, alter existing safety gates, or bypass Mannie ownership. Do not treat candidate architectures as established results.

The underlying direction is to **minimize what the larger model must calculate**, while protecting the baseline experience: Mike remains pleasant to talk to, and capabilities are added incrementally with measured non-regression.

Related project and research references:
- [Rudy's ChatGBC](https://github.com/crashtheuniverse/chatgbc) and [Adam's analysis](2026-10-31_chatgbc_rei_analysis.md)
- [PreStaC design](../mike/docs/0901_01_prestac-study.md) and [desk results](../mike/docs/0902_01_prestac-desk-result.md)
- [Mike harness / caches](../../docs/16_mike-harness-and-caches.md)
- [Mike small-talk on Luna](../mike/docs/1205_01_smalltalk-on-luna.md)
