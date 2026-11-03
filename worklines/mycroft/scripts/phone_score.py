"""Compare recognised phones with expected phones (plan step 11.5, offline scoring).

The expected phones come from eSpeak NG (`espeak-ng -q --ipa -v en-us`), the
recognised ones from ZIPA through Sherpa-ONNX. Both are normalised to one
coarse IPA alphabet, then aligned with a Levenshtein alignment, giving a phone
error rate and the most frequent confusions ("ɪ→i" is a short /ɪ/ heard as /i/).

Normalisation is deliberately coarse, so it does not count notation
differences as errors: stress marks, length marks and spaces are dropped, the
flap ɾ counts as t, ɐ as ə, and r-coloured vowels (ɚ, ɝ, ɜ) as ə˞.
"""

from __future__ import annotations

import subprocess
import unicodedata
from collections import Counter

_DROP = set("ˈˌː‿.,;:!?-_ \t\n'\"")
_REPLACE = {"ɚ": "ə˞", "ɝ": "ə˞", "ɜ": "ə˞", "ɾ": "t", "ɐ": "ə", "ᵻ": "ɪ", "g": "ɡ", "r": "ɹ"}
_ATTACH = {"˞", "ʰ", "ʲ", "ʷ"}  # modifiers that belong to the previous phone


def phones(ipa: str) -> list[str]:
    """Split an IPA string into normalised phones."""
    text = "".join(_REPLACE.get(ch, ch) for ch in unicodedata.normalize("NFD", ipa))
    out: list[str] = []
    for ch in text:
        if ch in _DROP or unicodedata.category(ch) == "Mn":
            continue
        if ch in _ATTACH:
            if out and ch == "˞" and not out[-1].endswith("˞"):
                out[-1] += ch
            continue  # aspiration and palatalisation are notation detail here
        out.append(ch)
    return out


def espeak_phones(text: str, voice: str = "en-us") -> list[str]:
    ipa = subprocess.run(["espeak-ng", "-q", "--ipa", "-v", voice, text], check=True,
                         capture_output=True, text=True).stdout
    return phones(ipa)


def align(expected: list[str], heard: list[str]) -> tuple[float, Counter]:
    """Phone error rate and confusions (`a→b`, `a→∅` deleted, `∅→b` inserted)."""
    n, m = len(expected), len(heard)
    cost = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        cost[i][0] = i
    for j in range(m + 1):
        cost[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost[i][j] = min(cost[i - 1][j] + 1, cost[i][j - 1] + 1,
                             cost[i - 1][j - 1] + (expected[i - 1] != heard[j - 1]))
    confusions: Counter = Counter()
    i, j = n, m
    while i or j:
        if i and j and cost[i][j] == cost[i - 1][j - 1] + (expected[i - 1] != heard[j - 1]):
            if expected[i - 1] != heard[j - 1]:
                confusions[f"{expected[i - 1]}→{heard[j - 1]}"] += 1
            i, j = i - 1, j - 1
        elif i and cost[i][j] == cost[i - 1][j] + 1:
            confusions[f"{expected[i - 1]}→∅"] += 1
            i -= 1
        else:
            confusions[f"∅→{heard[j - 1]}"] += 1
            j -= 1
    return (cost[n][m] / n if n else 0.0), confusions
