"""Mike Step 3.2c: run a model on the Step 2 evaluation sets with the contract (needs llama_cpp).

Prompt v3 is built from the contract: the system turn (fixed, cached once per
mode) lists the tools, the apps with their French names, the verbs and a few
examples that are in neither evaluation set; the user turn is the desktop line
followed by the request, so the shared prefix stays the same for every case.
"""

from __future__ import annotations

import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import mike_bench as bench
import mike_eval as ev
from mike_eval import contract


def _apps_line() -> str:
    return "; ".join(f"{app.id} ({', '.join(app.names_fr)})" for app in contract.ALLOWLIST)


SYSTEM_PROMPT_V3 = (
    "You are Mike, the assistant of a small handheld computer. The user speaks French. "
    "Each user message starts with the desktop state in brackets, then the request. "
    "Answer with exactly one tool call.\n"
    f"Applications (id and French names): {_apps_line()}.\n"
    "How French requests map to tools:\n"
    "- ouvre, lance, démarre, je veux X (X not open) -> launch_app\n"
    "- passe sur, va sur, reviens à, montre X (X open) -> focus_window\n"
    "- ferme, quitte, arrête X -> close_window (ça = the focused window)\n"
    "- mets, place, déplace X à gauche / à droite / en haut / en bas / en plein écran -> move_window\n"
    "- écris, tape, saisis TEXT -> type_text with TEXT exactly as said\n"
    "- quelles fenêtres, qu'est-ce qui est ouvert -> list_windows\n"
    "- anything else (questions, messages, settings, apps not in the list) -> none\n"
    "Examples:\n"
    '[open: terminal; focus: terminal] démarre le dino -> launch_app(app="dino")\n'
    '[open: editor, terminal; focus: editor] va sur la console -> focus_window(app="terminal")\n'
    '[open: images; focus: images] quitte la visionneuse -> close_window(app="images")\n'
    '[open: editor; focus: editor] place l\'éditeur à droite -> move_window(app="editor", place="right")\n'
    '[open: editor; focus: editor] saisis merci -> type_text(text="merci")\n'
    '[open: terminal; focus: terminal] chante une chanson -> none(reason="no tool for singing")'
)
bench.PROMPTS["v3"] = (SYSTEM_PROMPT_V3, contract.TOOLS)

# Prompt v4: the same rules, but the desktop goes at the end of the system turn,
# as in the smoke set's v2, and the user turn is the request alone.
SYSTEM_PROMPT_V4 = SYSTEM_PROMPT_V3.replace(
    "Each user message starts with the desktop state in brackets, then the request. ", "")
for _old, _new in (("[open: terminal; focus: terminal] ", ""), ("[open: editor, terminal; focus: editor] ", ""),
                   ("[open: images; focus: images] ", ""), ("[open: editor; focus: editor] ", "")):
    SYSTEM_PROMPT_V4 = SYSTEM_PROMPT_V4.replace(_old, _new)


def system_v4(desktop: contract.Desktop) -> str:
    opened = ", ".join(desktop.open) or "none"
    return f"{SYSTEM_PROMPT_V4}\nOpen windows now: {opened}. Focused window: {desktop.focus or 'none'}."


def user_turn(case: ev.EvalCase, prompt: str = "v3") -> str:
    if prompt == "v4":
        return case.request
    return f"{contract.desktop_line(case.desktop)} {case.request}"


def run_model_eval(model_path: str, sets: dict[str, Path], n_ctx: int = 2048, n_threads: int = 4,
                   n_batch: int = 64, max_tokens: int = 64, prompt: str = "v3", lean: bool = False) -> dict[str, Any]:
    """One model, both modes, every set; prefix state cached once per mode.

    ``lean`` (`docs/0302_05`): no repacked weight copy and a batch of 16.
    """
    from llama_cpp import Llama, LlamaGrammar, llama_cpp

    rss_before = bench._vm_hwm_kib()
    started = time.perf_counter()
    if lean:
        import llama_cpp as lc

        default = lc.llama_cpp.llama_model_default_params

        def no_repack():
            params = default()
            params.use_extra_bufts = False
            return params

        lc.llama.llama_cpp.llama_model_default_params = no_repack
        n_batch = 16
    llm = Llama(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, n_batch=n_batch, n_ubatch=n_batch,
                verbose=False)
    load_s = time.perf_counter() - started
    template = llm.metadata["tokenizer.chat_template"]
    vocab = llama_cpp.llama_model_get_vocab(llm.model)
    bos = llm.detokenize([llm.token_bos()], special=True).decode(errors="replace") if llm.token_bos() >= 0 else ""
    eos = llm.detokenize([llm.token_eos()], special=True).decode(errors="replace")
    fmt = bench.format_for(Path(model_path).name)
    grammar = LlamaGrammar.from_string(bench.grammar_for(fmt, contract.APP_IDS, contract.PLACES), verbose=False)
    cases = {name: ev.load_cases(path) for name, path in sets.items()}

    def tokens_for(case: ev.EvalCase, mode: str) -> list[int]:
        if prompt == "v4":
            bench.PROMPTS["v4"] = (system_v4(case.desktop), contract.TOOLS)
        text = bench.render_prompt(template, bos, eos, user_turn(case, prompt), prompt)
        if mode == "constrained":
            text += fmt.opener
        return llm.tokenize(text.encode(), add_bos=False, special=True)

    report: dict[str, Any] = {"model": Path(model_path).name, "prompt": prompt, "lean": lean, "n_ctx": n_ctx,
                              "n_threads": n_threads, "n_batch": n_batch, "load_s": round(load_s, 3),
                              "vm_hwm_kib_start": rss_before, "prefix": {}, "sets": {}}
    for mode in ("free", "constrained"):
        # The prefix shared by *every* case: two cases with the same desktop
        # would share the desktop too, and other desktops would miss the cache.
        everything = [c for group in cases.values() for c in group]
        first = tokens_for(everything[0], mode)
        shared = min(bench.common_prefix(first, tokens_for(c, mode)) for c in everything[1:])
        prefix = first[:shared]
        t0 = time.perf_counter()
        llm.reset()
        llm.eval(prefix)
        state = llm.save_state()
        report["prefix"][mode] = {"tokens": len(prefix), "eval_s": round(time.perf_counter() - t0, 3)}
        for name, group in cases.items():
            timings: list[float] = []
            raws: dict[str, str] = {}

            def predict(case: ev.EvalCase) -> contract.Call | None:
                tokens = tokens_for(case, mode)
                llm.load_state(state)
                t = time.perf_counter()
                out: list[int] = []
                text = ""
                for token in llm.generate(tokens, temp=0.0, top_k=1, repeat_penalty=1.0,
                                          grammar=grammar if mode == "constrained" else None):
                    if llama_cpp.llama_vocab_is_eog(vocab, token):
                        break
                    out.append(token)
                    text = llm.detokenize(out, special=True).decode(errors="replace")
                    if len(out) >= max_tokens or any(p in text for p in bench.STOP_PIECES):
                        break
                    if mode == "constrained" and text.endswith(fmt.closer[0]) and \
                            bench.parse_call(fmt, fmt.opener + text + fmt.closer[1:]):
                        break
                timings.append(time.perf_counter() - t)
                raws[case.request] = text
                full = (fmt.opener + text + fmt.closer[1:]) if mode == "constrained" else text
                parsed = bench.parse_call(fmt, full)
                return contract.Call(parsed.tool, parsed.args) if parsed else None

            result = ev.evaluate(predict, group)
            for row in result["rows"]:
                row["raw"] = raws[row["request"]]
            timings.sort()
            result["summary"]["median_s"] = round(timings[len(timings) // 2], 3)
            result["summary"]["max_s"] = round(timings[-1], 3)
            report["sets"].setdefault(name, {})[mode] = result
    report["vm_hwm_kib_peak"] = bench._vm_hwm_kib()
    return report


def summarise(report: dict[str, Any]) -> dict[str, Any]:
    out = {"model": report["model"], "peak_rss_mib": round(report["vm_hwm_kib_peak"] / 1024, 1),
           "prefix": report["prefix"]}
    for name, modes in report["sets"].items():
        for mode, result in modes.items():
            s = result["summary"]
            out[f"{name}/{mode}"] = {k: s[k] for k in ("n", "model", "adapter", "median_s", "max_s")}
    return out


__all__ = ["run_model_eval", "summarise", "SYSTEM_PROMPT_V3", "user_turn", "asdict"]
