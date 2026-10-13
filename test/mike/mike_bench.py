"""Mike Step 3 model smoke bench (`worklines/mike/docs/0301_01`).

Gives a small local model the intent's task-level tool list and a dozen short
French requests, and records which call it proposes, how long it takes and how
much memory its process uses. Nothing is executed: the proposed call is only
scored against the expected one.

Each model is rendered with its own embedded chat template, so it sees tools in
the format it was trained on. Two modes are run:

- ``free``: the model writes whatever it wants after the generation prompt;
- ``constrained``: the assistant turn is prefilled with the model's call opener
  and a GBNF grammar allows only one well-formed call from the list.

The pure helpers (tools, cases, parsers, grammars, scoring) need no model and
are covered by ``test_mike_bench.py``. ``run_model`` needs ``llama_cpp``.
"""

from __future__ import annotations

import ast
import json
import re
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


APPS = ["calculator", "browser", "terminal", "files", "chess", "wolfenstein", "dino"]
PLACES = ["left", "right", "top", "bottom", "full"]
OPEN_APPS = ["terminal", "browser"]

SYSTEM_PROMPT = (
    "You are Mike, the assistant of a small handheld computer. "
    "The user speaks French. Choose exactly one tool for the request. "
    f"Open windows: {', '.join(OPEN_APPS)} (browser has focus). "
    "If no tool fits, call none with a short reason."
)


def _tool(name: str, description: str, properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(properties),
            },
        },
    }


_APP = {"type": "string", "enum": APPS}
TOOLS = [
    _tool("list_windows", "List the open windows.", {}),
    _tool("focus_window", "Bring an open window to the front.", {"app": _APP}),
    _tool("launch_app", "Start an application.", {"app": _APP}),
    _tool("close_window", "Close an open window.", {"app": _APP}),
    _tool("move_window", "Place a window on the screen.",
          {"app": _APP, "place": {"type": "string", "enum": PLACES}}),
    _tool("type_text", "Type text into the focused window.", {"text": {"type": "string"}}),
    _tool("none", "No tool fits the request.", {"reason": {"type": "string"}}),
]

# Prompt v2 (Step 3.2d): the French verbs that ask for each tool, the desktop
# state as a list, and examples that are deliberately not smoke requests.
SYSTEM_PROMPT_V2 = (
    "You are Mike, the assistant of a small handheld computer. The user speaks French. "
    "Answer every request with exactly one tool call.\n"
    f"Open windows: {', '.join(OPEN_APPS)}. Focused window: browser.\n"
    f"Applications that can be started: {', '.join(APPS)}.\n"
    "How French requests map to tools:\n"
    "- ouvre, lance, démarre, je veux jouer à X -> launch_app\n"
    "- passe sur, va sur, montre X (an open window) -> focus_window\n"
    "- ferme, quitte X -> close_window\n"
    "- mets, place X à gauche / à droite / en haut / en bas / en plein écran -> move_window\n"
    "- écris, tape, saisis TEXT -> type_text with TEXT exactly as said\n"
    "- quelles fenêtres, qu'est-ce qui est ouvert -> list_windows\n"
    "- anything else (questions, messages, the weather, the internet) -> none\n"
    "Examples:\n"
    'démarre le dino -> launch_app(app="dino")\n'
    'va sur le navigateur -> focus_window(app="browser")\n'
    'quitte le terminal -> close_window(app="terminal")\n'
    'place le terminal à droite -> move_window(app="terminal", place="right")\n'
    'saisis merci -> type_text(text="merci")\n'
    'raconte-moi une blague -> none(reason="no tool for jokes")'
)
TOOLS_V2 = [
    _tool("list_windows", "List the open windows (quelles fenêtres sont ouvertes).", {}),
    _tool("focus_window", "Bring an already open window to the front (passe sur, va sur).", {"app": _APP}),
    _tool("launch_app", "Start an application (ouvre, lance, démarre).", {"app": _APP}),
    _tool("close_window", "Close an open window (ferme, quitte).", {"app": _APP}),
    _tool("move_window", "Place a window: left, right, top, bottom or full screen (mets, place).",
          {"app": _APP, "place": {"type": "string", "enum": PLACES}}),
    _tool("type_text", "Type the given text into the focused window (écris, tape, saisis).",
          {"text": {"type": "string"}}),
    _tool("none", "Use when no other tool fits (questions, messages, weather).", {"reason": {"type": "string"}}),
]
PROMPTS = {"v1": (SYSTEM_PROMPT, TOOLS), "v2": (SYSTEM_PROMPT_V2, TOOLS_V2)}


@dataclass(frozen=True)
class Case:
    request: str
    tool: str
    args: dict[str, str] = field(default_factory=dict)


# Mycroft-style text: lower case, no final punctuation.
CASES = [
    Case("ouvre la calculatrice", "launch_app", {"app": "calculator"}),
    Case("lance les échecs", "launch_app", {"app": "chess"}),
    Case("je veux jouer à wolfenstein", "launch_app", {"app": "wolfenstein"}),
    Case("ouvre le gestionnaire de fichiers", "launch_app", {"app": "files"}),
    Case("quelles fenêtres sont ouvertes", "list_windows"),
    Case("passe sur le terminal", "focus_window", {"app": "terminal"}),
    Case("ferme le navigateur", "close_window", {"app": "browser"}),
    Case("mets le navigateur à gauche", "move_window", {"app": "browser", "place": "left"}),
    Case("mets le terminal en plein écran", "move_window", {"app": "terminal", "place": "full"}),
    Case("écris bonjour tout le monde", "type_text", {"text": "bonjour tout le monde"}),
    Case("tape ls -la", "type_text", {"text": "ls -la"}),
    Case("quel temps fera-t-il demain", "none"),
    Case("envoie un mail à paul", "none"),
]


@dataclass(frozen=True)
class Call:
    tool: str
    args: dict[str, str]


# --- call formats -----------------------------------------------------------

@dataclass(frozen=True)
class Format:
    """How one model family writes a tool call."""

    name: str
    opener: str  # prefilled in constrained mode
    closer: str


LFM = Format("lfm", "<|tool_call_start|>[", "]<|tool_call_end|>")
GEMMA = Format("functiongemma", "<start_function_call>call:", "}<end_function_call>")


def format_for(model_name: str) -> Format:
    return GEMMA if "gemma" in model_name.lower() else LFM


def parse_lfm(text: str) -> Call | None:
    """Parse ``[name(key="value", …)]`` (Pythonic call list); first call only."""
    match = re.search(r"\[\s*([a-z_]+)\s*\((.*?)\)\s*[\],]", text, re.S)
    if not match:
        return None
    try:
        node = ast.parse(f"f({match.group(2)})", mode="eval").body
    except SyntaxError:
        return None
    if not isinstance(node, ast.Call):
        return None
    args: dict[str, str] = {}
    for keyword in node.keywords:
        if keyword.arg is None or not isinstance(keyword.value, ast.Constant):
            return None
        args[keyword.arg] = str(keyword.value.value)
    return Call(match.group(1), args)


def parse_functiongemma(text: str) -> Call | None:
    """Parse ``call:name{key:<escape>value<escape>,…}``; first call only."""
    match = re.search(r"call:([a-z_]+)\{(.*?)\}", text, re.S)
    if not match:
        return None
    args = {key: value for key, value in re.findall(r"(\w+):<escape>(.*?)<escape>", match.group(2), re.S)}
    return Call(match.group(1), args)


def parse_call(fmt: Format, text: str) -> Call | None:
    return parse_functiongemma(text) if fmt is GEMMA else parse_lfm(text)


# --- grammars ---------------------------------------------------------------

def _alternatives(values: list[str], quote: str) -> str:
    return " | ".join(json.dumps(f"{quote}{value}{quote}") for value in values)


TOOL_NAMES = [tool["function"]["name"] for tool in TOOLS]


def grammar_for(fmt: Format, apps: list[str] | None = None, places: list[str] | None = None) -> str:
    """GBNF for the text that follows ``fmt.opener`` in constrained mode.

    LFM:            ``name(app="calculator", place="left")]``
    FunctionGemma:  ``name{app:<escape>calculator<escape>,place:<escape>left<escape>}``
    """
    if fmt is GEMMA:
        open_, close, sep = "{", "}", ","
        quote = ""
        def arg(key: str, rule: str) -> str:
            return f'"{key}:<escape>" {rule} "<escape>"'
        text = "str ::= [^<{}\\n]{1,200}"
    else:
        open_, close, sep = "(", ")]", ", "
        quote = '"'
        def arg(key: str, rule: str) -> str:
            return f'"{key}=" {rule}'
        text = 'str ::= "\\"" [^"\\\\\\n]{1,200} "\\""'
    args = {
        "list_windows": [],
        "focus_window": [arg("app", "app")],
        "launch_app": [arg("app", "app")],
        "close_window": [arg("app", "app")],
        "move_window": [arg("app", "app"), arg("place", "place")],
        "type_text": [arg("text", "str")],
        "none": [arg("reason", "str")],
    }
    lines = ["root ::= " + " | ".join(f"c-{n.replace('_', '-')}" for n in TOOL_NAMES)]
    for name in TOOL_NAMES:
        body = f" {json.dumps(sep)} ".join(args[name])
        lines.append(f"c-{name.replace('_', '-')} ::= {json.dumps(name + open_)} {body} {json.dumps(close)}".replace("  ", " "))
    lines.append(f"app ::= {_alternatives(apps or APPS, quote)}")
    lines.append(f"place ::= {_alternatives(places or PLACES, quote)}")
    lines.append(text)
    return "\n".join(lines) + "\n"


# --- scoring ----------------------------------------------------------------

def _norm(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip().strip("\"'").casefold()


def score(case: Case, call: Call | None) -> dict[str, bool]:
    """``tool``: right tool (no call counts as ``none``); ``exact``: right args too."""
    tool = call.tool if call else "none"
    tool_ok = tool == case.tool
    if case.tool == "none":
        return {"tool": tool_ok, "exact": tool_ok}
    args = call.args if call else {}
    exact = tool_ok and all(_norm(args.get(k, "")) == _norm(v) for k, v in case.args.items())
    return {"tool": tool_ok, "exact": exact}


# --- prompt -----------------------------------------------------------------

def _template_env():
    import jinja2
    from jinja2.ext import Extension

    class Generation(Extension):
        """Hugging Face's ``{% generation %}`` training marker: render its body as is."""

        tags = {"generation"}

        def parse(self, parser):
            lineno = next(parser.stream).lineno
            body = parser.parse_statements(("name:endgeneration",), drop_needle=True)
            return jinja2.nodes.Scope(body, lineno=lineno)

    env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, loader=jinja2.BaseLoader(),
                             extensions=[Generation])

    def raise_exception(message: str) -> None:
        raise jinja2.TemplateError(message)

    env.globals["raise_exception"] = raise_exception
    env.globals["strftime_now"] = lambda fmt: datetime.now().strftime(fmt)
    env.filters["tojson"] = lambda value, indent=None, **_: json.dumps(value, indent=indent, ensure_ascii=False)
    return env


def render_prompt(chat_template: str, bos_token: str, eos_token: str, request: str,
                  prompt: str = "v1") -> str:
    """Render one request with the model's own template and the tool list."""
    system, tools = PROMPTS[prompt]
    messages = [{"role": "system", "content": system}, {"role": "user", "content": request}]
    return _template_env().from_string(chat_template).render(
        messages=messages, tools=tools, add_generation_prompt=True,
        bos_token=bos_token, eos_token=eos_token,
    )


def render_prompt_chat(chat_template: str, bos_token: str, eos_token: str, request: str) -> str:
    """Render one request as a plain chat turn: no system text, no tools."""
    return _template_env().from_string(chat_template).render(
        messages=[{"role": "user", "content": request}], add_generation_prompt=True,
        bos_token=bos_token, eos_token=eos_token,
    )


# --- model run (needs llama_cpp) ---------------------------------------------

def _vm_hwm_kib() -> int:
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmHWM:"):
            return int(line.split()[1])
    return -1


STOP_PIECES = ("<|im_end|>", "<end_of_turn>", "<|tool_call_end|>", "<end_function_call>")


def common_prefix(a: list[int], b: list[int]) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def run_model(model_path: str, n_ctx: int = 2048, n_threads: int = 4, n_batch: int = 512,
              max_tokens: int = 64, prompt: str = "v1", prefix_cache: bool = False) -> dict[str, Any]:
    """Load one model in this process, run every case in both modes, return a report.

    Meant to run in a fresh child process so ``VmHWM`` is this model's peak.
    ``prefix_cache`` evaluates the part of the prompt shared by every request
    once, saves the model state, and restores it before each request: the only
    way to reuse the prefix of a hybrid (convolution + attention) model, whose
    state cannot be truncated.
    """
    from llama_cpp import Llama, LlamaGrammar, llama_cpp

    rss_before = _vm_hwm_kib()
    started = time.perf_counter()
    llm = Llama(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, n_batch=n_batch, verbose=False)
    load_s = time.perf_counter() - started
    rss_loaded = _vm_hwm_kib()

    meta = llm.metadata
    template = meta["tokenizer.chat_template"]
    vocab = llama_cpp.llama_model_get_vocab(llm.model)
    bos = llm.detokenize([llm.token_bos()], special=True).decode(errors="replace") if llm.token_bos() >= 0 else ""
    eos = llm.detokenize([llm.token_eos()], special=True).decode(errors="replace")
    fmt = format_for(Path(model_path).name)
    grammar = LlamaGrammar.from_string(grammar_for(fmt), verbose=False)

    def tokens_for(case: Case, mode: str) -> list[int]:
        text = render_prompt(template, bos, eos, case.request, prompt)
        if mode == "constrained":
            text += fmt.opener
        return llm.tokenize(text.encode(), add_bos=False, special=True)

    results = []
    prefix_states: dict[str, dict[str, Any]] = {}
    for mode in ("free", "constrained"):
        state = None
        if prefix_cache:
            first, second = tokens_for(CASES[0], mode), tokens_for(CASES[1], mode)
            prefix = first[:common_prefix(first, second)]
            t0 = time.perf_counter()
            llm.reset()
            llm.eval(prefix)
            state = llm.save_state()
            prefix_states[mode] = {"tokens": len(prefix), "eval_s": round(time.perf_counter() - t0, 3),
                                   "state_mib": round(state.llama_state_size / 2**20, 2)}
        for case in CASES:
            tokens = tokens_for(case, mode)
            if state is not None:
                llm.load_state(state)
            cached = 0
            for a, b in zip(llm._input_ids.tolist(), tokens):
                if a != b:
                    break
                cached += 1
            t0 = time.perf_counter()
            ttft = None
            out: list[int] = []
            text = ""
            for token in llm.generate(tokens, temp=0.0, top_k=1, repeat_penalty=1.0,
                                      grammar=grammar if mode == "constrained" else None):
                if ttft is None:
                    ttft = time.perf_counter() - t0
                if llama_cpp.llama_vocab_is_eog(vocab, token):
                    break
                out.append(token)
                text = llm.detokenize(out, special=True).decode(errors="replace")
                if len(out) >= max_tokens or any(p in text for p in STOP_PIECES):
                    break
                if mode == "constrained" and text.endswith(fmt.closer[0]) and parse_call(fmt, fmt.opener + text + fmt.closer[1:]):
                    break
            total = time.perf_counter() - t0
            full = (fmt.opener + text + fmt.closer[1:]) if mode == "constrained" else text
            call = parse_call(fmt, full)
            results.append({
                "mode": mode, "request": case.request,
                "expected": {"tool": case.tool, "args": case.args},
                "got": asdict(call) if call else None,
                "raw": text, **score(case, call),
                "prompt_tokens": len(tokens), "prompt_tokens_cached": cached,
                "output_tokens": len(out), "ttft_s": round(ttft or total, 3), "total_s": round(total, 3),
            })

    return {
        "model": Path(model_path).name, "format": fmt.name, "n_ctx": n_ctx, "n_threads": n_threads, "n_batch": n_batch,
        "prompt": prompt, "prefix_cache": prefix_states or None,
        "load_s": round(load_s, 3), "vm_hwm_kib_start": rss_before,
        "vm_hwm_kib_loaded": rss_loaded, "vm_hwm_kib_peak": _vm_hwm_kib(),
        "results": results,
    }


def summarise(report: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"model": report["model"], "n_batch": report.get("n_batch"),
                           "prompt": report.get("prompt", "v1"), "prefix_cache": report.get("prefix_cache"),
                           "load_s": report["load_s"],
                           "peak_rss_mib": round(report["vm_hwm_kib_peak"] / 1024, 1)}
    for mode in ("free", "constrained"):
        rows = [r for r in report["results"] if r["mode"] == mode]
        out[mode] = {
            "tool_ok": sum(r["tool"] for r in rows), "exact_ok": sum(r["exact"] for r in rows), "n": len(rows),
            "first_prompt_tokens": rows[0]["prompt_tokens"],
            "first_ttft_s": rows[0]["ttft_s"],
            "median_total_s": sorted(r["total_s"] for r in rows)[len(rows) // 2],
        }
    return out
