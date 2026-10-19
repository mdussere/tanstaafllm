# Mike's harness and a zero-shot decider — cleaned discussion record

**Source:** ChatGPT shared conversation <https://chatgpt.com/share/6ace95fc-0800-83eb-bd5f-9d86b7257744>, captured on 2026-10-13. The raw export is [`0700_01_harness-and-decider-discussion-raw.md`](0700_01_harness-and-decider-discussion-raw.md) (77 messages); it is the primary reference. **Owner:** workline `mike`. **Plan step:** Step 7 (and an amended Step 3b).

## Summary

The user wants Mike to be a bounded local controller rather than a miniature Claude: one action per order, chosen from closed sets. The conversation explores two things:
- a real but tiny agent harness (PicoClaw or ZeroClaw);
- zero-shot, promptable classifiers ("JEV-like") that pick the target, the tool or a predefined plan faster than LFM2.5-350M.

It sets firm constraints: no training or fine-tuning, no translation, English allowed, GPU/OpenCL not a priority, and a latency budget per decision.

## Detailed summary

**User decisions (binding for Mike)**
- **Mike does one action at a time.** No autonomous planning or composition of operations. It either performs one order, or converts an order into text sent to the input.
- **Predefined plans are allowed.** The use case is narrow, so a decider may *select* a pre-written plan by case (command line or not, dictated or hand-corrected text…). Selecting a plan is not planning.
- **No training, no fine-tuning, no training dataset.** The user has neither the compute, the data nor the wish. Option B (LoRA fine-tuning, `0302_03`) is therefore **dropped**. Candidates must work as pre-trained models, zero-shot.
- **Embedding-similarity "classifiers" are rejected as deciders.** They are not calibrated and give poor results. They may at most pre-select candidates.
- **Latency budget per decision:** under 1 s is tolerable, 500 ms acceptable, 200 ms "super". The latency must be measured per number of classes.
- **Low latency, low compute, low memory**; nothing fancy is needed. The user accepts a limited capability.
- **French may be dropped for English** if the English speech-to-text understands the user's accent. **Translation is excluded**: it costs like everything else.
- **New action for Mycroft:** evaluate English speech-to-text quality on the user's accent ("if it passes, it passes").
- **GPU/OpenCL is not a preferred hypothesis.** With four cores, multithreading closes part of the gap. Only latency matters, not CPU load.
- **The Slate and Mike:** the Slate's outputs are roughly *send to the input* and *send to Mike*. "Send to the command line" may simply mean "send to Mike". Mannie is a heavy application: sending to Mannie means sending to its input. A Slate opened from Mannie must not offer Mike. A Slate opened from a command line must let Mike translate the request into a real command, check its syntax and its coherence, and possibly say no or ask for confirmation. Example: "ls of the home dir" must become `ls ~` and nothing else.
- **Keep verbatims in the repository** so that agents can go to the finest detail. Issues may point to them.

**Assistant proposals (not decisions; to be checked)**
- **Three architectures** for Mike: deterministic rules plus LFM (the current path); a JEV-like decider plus deterministic resolvers; or a hybrid with progressive intelligence. The proposal is to start from the first and move towards the hybrid.
- **A five-module micro-harness:**
  1. context (window, capabilities, focus);
  2. router (rules / decider / LFM);
  3. resolver (arguments, commands);
  4. policy (validation, refusal, confirmation);
  5. executor (Sway IPC / Wyoh MCP / text injection).

  The executor does not feed results back for a next step: no ReAct loop.
- **Harness candidates:**
  - **PicoClaw** (Go, Sipeed; 10–20 MB announced; MCP; `SKILL.md` skills; file/JSONL memory; young security hardening);
  - **ZeroClaw** (Rust; a few MB announced; a native llama.cpp provider; a `local_small` profile; readonly/supervised/full modes; risk of skill injection inflating the prompt);
  - NanoBot (Python, functional reference);
  - MicroClaw;
  - PocketFlow.

  ZeroClaw is first to try; PicoClaw stays a close second.
- **Evidence cited:**
  - A Zenodo preprint, "Benchmarking Lightweight AI-Agent Frameworks on a 2 GB Raspberry Pi 4" (2026-06-08), comparing ZeroClaw, PicoClaw, NanoBot and smolagents. Peak RSS was about 31 MiB for PicoClaw, with a remote model. With local models, every framework failed the basic test: Qwen2.5-1.5B was too slow, and SmolLM2-360M could not call tools. Its code and data are said to be published.
  - No public test of LFM2.5 with PicoClaw or ZeroClaw was found.
- **LFM2.5 facts cited:** LFM stands for Liquid Foundation Model. The context window is 64K, but 2K–4K is advised on Luna. A QAD Q4_0 version (Liquid AI, 2026-08-19) is said to reach close to Q5_K_M quality at Q4_0 speed; it should be added to the benchmarks.
- **Zero-shot decider candidates:**
  - **GLiClass Edge v3.0 (32.7M):** many labels in one pass; ONNX INT8 and LiteRT exist; about 31 MiB of weights in INT8, an estimated 50–90 MiB resident.
  - **GLiClass Small/Instruct (144M):** an instruction prompt plus labels; a C/ONNX implementation exists (GLiClass.c).
  - **Multilingual MiniLMv2-L6 XNLI:** ONNX; one pass per class.
  - **Laya multilingual (322M, mmBERT):** choice / yes-no / score decisions; too large for this role.
  - JEV itself is remote, so it is excluded.

  GLiClass's inference takes text, labels, an optional prompt, a threshold, single- or multi-label, and examples. Successive decisions are possible: context, then plan, then operation. Each costs one pass.
- **Assistant-proposed targets:**
  - first version: < 50 ms and < 30 MiB;
  - revised after the user's answer: < 200 ms excellent, < 500 ms acceptable, 1 s maximum; < 50 MiB excellent, 100–150 MiB acceptable; 5–10 classes, up to 20.
- **Machine speed ratios** (Mycroft's Zipformer, approximate): x86 → `luna-pi` ≈ 5.7× slower; `luna-pi` → Luna ≈ 3.6×; x86 → Luna ≈ 20×. Proposed as an order of magnitude for LFM, not a measured factor.
- **OpenCL:** an official llama.cpp OpenCL back end exists, validated on Adreno, not on Mali-G31. Earlier reports show OpenCL slower than the CPU on Mali/Adreno. Proposal: keep it as a watch item and reopen only on evidence of at least a 2× end-to-end speed-up.
- **Memory modes:** Mike and Mannie are alternative modes, not resident together. Composite estimate:
  - Mike mode: about 683 MiB used, about 300 MiB free;
  - Mannie mode: about 627 MiB used, about 356 MiB free.

  The figures come from several machines and were not validated together on Luna.
- **A terminal adapter is needed:** Sway knows the focused window but not the shell's working directory.
- **Proposed Mike output:**
  - for a terminal, a *proposal* (`terminal_command`, explanation, `requires_confirmation`), typed without Enter;
  - for the Wyoh desktop, an action after validation.
- **Open question raised:** should Mike work over several turns from the Slate? ("Find the last file I modified and open it" needs a query and then a second decision.)

**Unverified technical claims to check before relying on them:**
- the RAM and feature figures for PicoClaw and ZeroClaw;
- the Zenodo preprint's results;
- the QAD Q4_0 quality;
- GLiClass Edge's size, quality and ARM64 support;
- the existence of GLiClass-Instruct, GLiClass.c and Laya;
- the OpenCL statements;
- the composite memory budget;
- the GitHub star counts.

**Peripheral (no Mike action):** the ChatGPT GitHub connector created issue #2 on `mdussere/tanstaafllm`, "Evaluate English ASR on French-accented speech". Later edits were blocked by the tool. The user wants that issue's first step to be archiving another conversation (<https://chatgpt.com/share/6accd5f6-5c80-83ed-92f8-1c2d02d5cb40>); that is Mycroft's. The assistant also reread the repository after the user corrected the repository's name.

## Cleaned verbatim of the user's messages

> Translated from spoken French (voice dictation). French is kept in parentheses where the wording is ambiguous or was probably mistranscribed. Section headers are added by the cleaner. Assistant replies are summarised above and kept in full in the raw export. Message numbers refer to the order in the raw export. One user message (before message 63) was not captured, and the user does not remember it.

### § 1. JEV-like deciders for Mike (msg 1)

I also think that eventually, for Mike, we will need to look at JEV-like models — JEV, J-E-V — because they are closed decision models, zero-shot, promptable (*"one-shot… pas one-shot, zéro-shot, pardon"*). That could be very interesting. When I give a command like "open me…", "list the files in my dir", the first thing Mike has to work out is which application it is meant for: is it a command line, is it something else? So I potentially have a number of closed choices to make. I am not going to ask Mike to do what Claude does, that is, make a plan and compose operations. Mike must do one action at a time. I give it an order, it carries it out. Or I give an order, it converts it to text and sends it to the input. But Mike will not make a plan and run a set of complex operations. If I ask it to go and open an application, I don't know. I am still wondering about Mike's capabilities. In any case, we will need to find it a harness, and I would like proposals.

### § 2. A real small agent (msg 3)

Let's quickly separate JEV (*"GF"*, a mistranscription; the user confirmed JEV) from the harness. By harness, I mainly mean that tomorrow I want to build a small agent. A small agent has a lot of things: it is not just an LLM and not just a chat. It is being able to use skills, having a memory, taking actions, using tools, and so on. So I want to see what is available to build an agent with a small model. Have people started doing this — small agents on embedded hardware (*"en BD"*; the user confirmed "embedded")?

### § 3. PicoClaw or ZeroClaw (msgs 5, 7, 9, 11)

Between PicoClaw and ZeroClaw (*"PicoClos / ZeroClos"*), what would be the real difference, and what should guide the choice? In the end, if there is no difference, the choice is the project's momentum and its long-term future.

What is our context size on LFM2.5?

Are there blogs, publications, anything comparing the two?

I never asked before: what does LFM mean? And are there publications testing LFM with ZeroClaw or LFM with PicoClaw (*"zéro CLO / picoCLO"*)?

### § 4. No fine-tuning (msg 13)

My problem is that I will not be able to fine-tune LFM. I simply do not have the compute to fine-tune at home, so that is a problem. Nor do I have the data that would let me fine-tune for this.

### § 5. Speed across machines and OpenCL (msgs 15, 17, 19, 21)

What variations of LFM did we observe on `luna-pi` (*"LunaPay"*) and on Luna?

Our point of comparison is indeed the speech-to-text models. What speed-up did we have between Surcouf (*"Surf"*), `luna-pi` and Luna on equivalent tests? Take the most powerful models we tested.

And OpenCL in all this: could it be an acceleration factor?

With four cores and fairly sequential operations, CPU load is not really a problem. It is only the speed-up we are after. And parallelism and multithreading close part of the CPU's gap with the GPU. So it is really not a hypothesis we favour at the moment.

### § 6. Predefined plans chosen by a zero-shot classifier (msg 23)

And the JEV-like models (*"Jeff-like"*), because they could be a way to speed up part of the operations: choosing the tool, choosing which case we are in (are we on a command line or not), what to look for, predefined plans. Maybe that is it too. We said we do not want reflexivity, we do not want to make a plan. But we could very well have predefined plans, because our use case is very limited. When we pass a line of code, or a text that was dictated — possibly dictated, possibly corrected by hand, and we can know that — we could have different plans depending on the case. Choosing the plan, like choosing the tools, could make the agent semi-intelligent within our constrained frame. But that requires zero-shot classifiers à la JEV. So I would like you to survey what has come out in the last few weeks that competes with JEV-like models — a "poor man's JEV" based on BERT, things like that. I have seen things based on embeddings; I am not sure that is… well, to be seen. Does anything stand out?

### § 7. Constraints on the decider (msgs 25, 27, 29, 31, 33)

So all that excludes, for me, anything that needs retraining or fine-tuning. I don't have the means, I don't have the data, and I don't want to get into that.

On something like GLiClass (*"GLI Class"*), what is the inference function and what are its parameters? When we classify, we cross an input with a set of classes. But with something like JEV, we also give a strategy, a prompt that strongly steers the decisions. Is that the case with GLiClass, for example?

I can live with that constraint. I don't need anything crazy. All I want is very low latency, very low compute cost, and a very small memory footprint.

Yes, but a zero-shot classifier based on an embedding is not comparable (*"n'est pas comptable"* — probably "not calibrated" or "not comparable"). Only with great difficulty, and its results are not very good. So if I have classes, the latency of each class should be evaluated. If that latency is below a second — at 500 milliseconds it becomes acceptable. Your 50-millisecond target is great, but 200 milliseconds would already be great.

With 144 million parameters, what memory footprint should we expect?

### § 8. Language (msgs 35, 37, 39)

Once again — I must already have told Professor — if French becomes a brake, a bottleneck, we will give up French and go straight to English. If the speech-to-text is good enough to understand my lousy accent, there is no reason not to use English.

The problem is that translation is expensive, like everything else.

OK, so the action to add is: evaluate speech-to-text quality with an English model against my lousy accent. If it passes, it passes.

### § 9. GitHub issues and keeping verbatims (msgs 41–61, 72–76)

Can you post issues on GitHub? Wikis too? Can you get a link to this conversation to put it in the issue? I would rather we extract the whole conversation and keep verbatims in GitHub. The other agents can go down to the finest level of detail if they need to. Try to post an issue; there is no need to send it the verbatims, I will have them extracted. (After a permissions fix, issue #2 was created.) In the issue you don't refer to our discussion. The first thing the agent must do is access and dump this conversation: <https://chatgpt.com/share/6accd5f6-5c80-83ed-92f8-1c2d02d5cb40>. Can you delete the issue? If so, delete it and recreate it. (Several "Retry"s followed; the tool blocked the edits.)

### § 10. The Slate and Mike (msg 64)

There is a small distinction here. The Slate is designed to depend partly on Mike. If we dictate by voice, we end up with natural language, and what we want behind it is to turn that natural language into an operation — and that is Mike. Whatever we do, Mike does that. But either way: either we say Mike comes afterwards, so it is not part of the Slate, and that is "I send to Mike". We have already started talking about this: at the Slate's output I have roughly several buttons — one that sends to the input, one that sends to Mike, one that sends to the command line, I don't remember exactly, something like that. Sending to the command line may simply be sending to Mike. Or maybe a button that sends to Mannie (*"Mani"*), but I'm not sure, because for me Mannie is a heavy application, so it is the input: when I send to Mannie, I send to the input. So it is either "send to Mike" or "send to the input". That means that at times I have a Slate started with or without Mike, where Mike is just the Slate's output. Except that if I open the Slate from Mannie, I must not be able to send my input to Mike. If I open the Slate from the command line, I clearly want to be able to translate my input into a real command line, check its syntax, check that it is coherent with what is around it, and possibly be told no, or "is that really what you want to do?". So maybe there is a step like "an output validated by Mike". I said I wanted an `ls` of the home dir: when I say I want an `ls` of the home dir, Mike must translate it into `ls ~` and nothing else.

### § 11. Reloading the project (msgs 66, 68, 70)

Reload the project: I have just updated the documentation, which gives roughly the project's progress, and the logbook. Look at the project and we will discuss it afterwards. I corrected the typo in the project's name — there was an extra F — so correct it. Now that you are corrected, go and look at the repository and what is new.
