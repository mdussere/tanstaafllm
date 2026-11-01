"""Mike 9.2: PreStaC layers for LFM2.5 and the Step 2 evaluation cases.

L0 is the fixed part, rendered by the model's own chat template: the system
turn with prompt v4's instructions (no desktop) and the tool JSON that the
template appends. Then one layer per piece of context (the desktop, an app),
each a new line of the system turn. The tail closes the system turn, holds the
question and opens the tool call. Every piece is tokenised on its own and the
token ids are joined, so that no token straddles a layer boundary.
"""

from __future__ import annotations

from typing import Callable

import mike_bench as bench
import mike_eval_model as em
from mike_eval import contract

import prestac

SYSTEM_END = "<|im_end|>\n<|im_start|>user\n"


class LfmLayers:
    def __init__(self, chat_template: str, bos: str, eos: str, tokenize: Callable[[str], list[int]]):
        self.tokenize = tokenize
        bench.PROMPTS["prestac-l0"] = (em.SYSTEM_PROMPT_V4, contract.TOOLS)
        rendered = bench.render_prompt(chat_template, bos, eos, "Q", "prestac-l0")
        cut = rendered.index(SYSTEM_END)
        self.l0_text = rendered[:cut]
        self.l0 = prestac.Layer("L0 instructions+tools", tuple(tokenize(self.l0_text)))

    def desktop(self, desktop: contract.Desktop) -> prestac.Layer:
        opened = ", ".join(desktop.open) or "none"
        text = f"\nOpen windows now: {opened}. Focused window: {desktop.focus or 'none'}."
        return prestac.Layer(f"desktop {opened}/{desktop.focus}", tuple(self.tokenize(text)))

    def app(self, name: str, text: str) -> prestac.Layer:
        return prestac.Layer(name, tuple(self.tokenize("\n" + text)))

    def tail(self, question: str) -> prestac.Layer:
        text = SYSTEM_END + question + "<|im_end|>\n<|im_start|>assistant\n" + bench.LFM.opener
        return prestac.Layer("question", tuple(self.tokenize(text)))
