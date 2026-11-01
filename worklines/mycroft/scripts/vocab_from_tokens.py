"""Build a `bpe.vocab` for Sherpa's hotwords from a model's own `tokens.txt` (plan step 9.10).

Sherpa splits each hotword into the model's tokens with a SentencePiece-style
vocabulary (`piece<TAB>score`). Kroko publishes no such file, so this one is
rebuilt from the tokens it does ship. Each piece costs about 1, so the split
with the fewest pieces wins, as BPE's own merges would give; among equal
splits, earlier (more frequent) tokens win. Special
symbols (`<blk>`, `<sos/eos>`, `<unk>`, `#0`, `#1`) are left out.

    python3 vocab_from_tokens.py MODEL_DIR    # writes MODEL_DIR/bpe.vocab
"""

from __future__ import annotations

import sys
from pathlib import Path


def vocab_lines(tokens: str) -> list[str]:
    lines = []
    for line in tokens.splitlines():
        piece, index = line.rsplit(maxsplit=1) if " " in line.strip() else (line, "0")
        if piece.startswith("<") and piece.endswith(">") or piece.startswith("#"):
            continue
        lines.append(f"{piece}\t{-(1 + int(index) / 10000):.4f}")
    return lines


def main(argv: list[str]) -> int:
    model_dir = Path(argv[1])
    lines = vocab_lines((model_dir / "tokens.txt").read_text(encoding="utf-8"))
    (model_dir / "bpe.vocab").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{model_dir / 'bpe.vocab'}: {len(lines)} pieces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
