#!/usr/bin/env python3
"""Try a Mike model by hand: type a French request, see what it proposes.

Nothing is executed. For each line you type, the script shows:
- what the keyword table would do (option A);
- the model's raw answer, the call parsed from it, and the time it took;
- what the adapter would propose against the fake desktop.

It uses the same prompt (v4), tools, grammar and adapter as the Step 3
evaluation (`test/mike/`). `--chat` drops the tools to see the model as a
plain chat model.

    uv run --group mike worklines/mike/scripts/mike_chat.py
    uv run --group mike worklines/mike/scripts/mike_chat.py --model LFM2.5-230M-Q4_K_M.gguf
    uv run --group mike worklines/mike/scripts/mike_chat.py --open terminal,editor --focus editor
    uv run --group mike worklines/mike/scripts/mike_chat.py --chat
    uv run --group mike worklines/mike/scripts/mike_chat.py --model LFM2.5-230M-Q4_K_M.gguf --lean
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "test" / "mike"))

import mike_bench as bench  # noqa: E402
import mike_eval as ev  # noqa: E402
import mike_eval_model as em  # noqa: E402
from mike_eval import contract  # noqa: E402

MODES = {
    "outils": "the model must pick one of the 7 Wyoh actions (it cannot answer in words)",
    "libre": "same tools, no grammar: the model may call a tool or answer in words",
    "chat": "no tools: plain conversation",
}
HELP = ("Modes: " + "; ".join(f"/{k} = {v}" for k, v in MODES.items())
        + ".\nType a French request (empty line or Ctrl-D to quit). Nothing is executed.\n")
DEFAULT_ROOT = "/data/michael/tanstaafllm/mike-assets"
MODELS = ["LFM2.5-350M-Q4_K_M.gguf", "LFM2.5-230M-Q4_K_M.gguf", "functiongemma-270m-it-Q4_K_M.gguf"]


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default=MODELS[0], help=f"GGUF file name ({', '.join(MODELS)})")
    parser.add_argument("--root", default=os.environ.get("MIKE_ASSET_ROOT", DEFAULT_ROOT))
    parser.add_argument("--open", default="terminal,calculator", help="open apps (Mike ids), comma-separated")
    parser.add_argument("--focus", default="calculator")
    parser.add_argument("--free", action="store_true", help="no grammar: let the model write anything")
    parser.add_argument("--chat", action="store_true", help="no tools at all: plain chat")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--lean", action="store_true",
                        help="least RAM: no repacked weight copy, batch 16 (slower on x86)")
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    from llama_cpp import Llama, LlamaGrammar, llama_cpp

    path = Path(args.root) / args.model
    if not path.is_file():
        print(f"model not found: {path}", file=sys.stderr)
        return 2
    opened = tuple(a for a in args.open.split(",") if a)
    unknown = [a for a in opened + (args.focus,) if a and a not in contract.APP_IDS]
    if unknown:
        print(f"unknown app ids {unknown}; allowed: {contract.APP_IDS}", file=sys.stderr)
        return 2
    desktop = contract.Desktop(opened, args.focus or None)

    if args.lean:
        import llama_cpp as lc

        default = lc.llama_cpp.llama_model_default_params

        def no_repack():
            params = default()
            params.use_extra_bufts = False
            return params

        lc.llama.llama_cpp.llama_model_default_params = no_repack
    batch = 16 if args.lean else 64
    t0 = time.perf_counter()
    llm = Llama(model_path=str(path), n_ctx=2048, n_threads=args.threads, n_batch=batch, n_ubatch=batch,
                verbose=False)
    template = llm.metadata["tokenizer.chat_template"]
    vocab = llama_cpp.llama_model_get_vocab(llm.model)
    bos = llm.detokenize([llm.token_bos()], special=True).decode() if llm.token_bos() >= 0 else ""
    eos = llm.detokenize([llm.token_eos()], special=True).decode()
    fmt = bench.format_for(path.name)
    tool_grammar = LlamaGrammar.from_string(bench.grammar_for(fmt, contract.APP_IDS, contract.PLACES), verbose=False)
    mode = "chat" if args.chat else ("libre" if args.free else "outils")
    hwm = next(int(l.split()[1]) for l in Path("/proc/self/status").read_text().splitlines() if l.startswith("VmHWM"))
    print(f"{path.name} loaded in {time.perf_counter() - t0:.1f} s · peak RSS so far {hwm // 1024} MiB · "
          f"desktop {contract.desktop_line(desktop)}")
    print(HELP)

    while True:
        try:
            request = input(f"toi [{mode}]> ").strip()
        except EOFError:
            print()
            return 0
        if not request:
            return 0
        if request in ("/chat", "/outils", "/libre"):
            mode = request[1:]
            print(f"  → mode {mode}: {MODES[mode]}\n")
            continue
        if request.startswith("/"):
            print(HELP)
            continue
        grammar = tool_grammar if mode == "outils" else None
        if mode == "chat":
            prompt = bench.render_prompt_chat(template, bos, eos, request)
        else:
            bench.PROMPTS["v4"] = (em.system_v4(desktop), contract.TOOLS)
            prompt = bench.render_prompt(template, bos, eos, request, "v4")
            if grammar is not None:
                prompt += fmt.opener
            case = ev.EvalCase(request, desktop, contract.Call("none"), "manual")
            rule = ev.keyword_baseline(case)
            print(f"  mots-clés : {rule.tool}({rule.args})")
        tokens = llm.tokenize(prompt.encode(), add_bos=False, special=True)
        start = time.perf_counter()
        first = None
        out: list[int] = []
        text = ""
        for token in llm.generate(tokens, temp=0.0, top_k=1, repeat_penalty=1.0, grammar=grammar, reset=True):
            first = first or time.perf_counter() - start
            if llama_cpp.llama_vocab_is_eog(vocab, token):
                break
            out.append(token)
            text = llm.detokenize(out, special=True).decode(errors="replace")
            if len(out) >= (256 if mode == "chat" else 96) or (mode != "chat" and any(p in text for p in bench.STOP_PIECES)):
                break
            if grammar is not None and text.endswith(fmt.closer[0]) and \
                    bench.parse_call(fmt, fmt.opener + text + fmt.closer[1:]):
                break
        total = time.perf_counter() - start
        rate = len(out) / max(total - (first or 0), 1e-9)
        if mode == "chat":
            print(f"  mike    : {text.strip()}")
        else:
            print(f"  modèle    : {text!r}")
        print(f"  temps     : {len(tokens)} tokens lus, premier token {first or total:.2f} s, "
              f"{len(out)} tokens écrits, total {total:.2f} s ({rate:.0f} tokens/s)")
        if mode != "chat":
            full = (fmt.opener + text + fmt.closer[1:]) if grammar is not None else text
            parsed = bench.parse_call(fmt, full)
            if parsed is None:
                print("  appel     : aucun — le modèle a répondu en texte")
            else:
                call = contract.Call(parsed.tool, parsed.args)
                proposal = contract.propose(call, desktop)
                print(f"  appel     : {call.tool}({call.args})")
                print(f"  adaptateur: {proposal.kind} — {proposal.message}")
        print()

if __name__ == "__main__":
    sys.exit(main())
