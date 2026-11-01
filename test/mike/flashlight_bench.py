"""Mike Step 14.3: measure one "flashlight" candidate in a fresh process (`flashlight.feature`).

    python test/mike/flashlight_bench.py <candidate>   # prints one JSON line

Candidates: `bm25` and `tfidf` (lexical, standard library and numpy), and Model2Vec
static models by Hugging Face id (`minishlab/potion-base-2M`…). Run in its own process
so that its peak memory is its own. Measures:

* load time, memory (peak RSS before and after loading, then after indexing), disk;
* milliseconds per embedding, warm, one text at a time: a short sentence, a ~100-word block;
* zero-shot routing: each label as its description only, then as description + anchors
  (the nearest of those prototypes wins);
* retrieval over the guide's blocks: top-1 and top-3;
* the same routing and retrieval on ASR-like noisy variants (`noisy` in the data);
* the top-1 score of guide questions against questions outside the guide (AUC, and the
  best single threshold's accuracy): can a threshold tell "out of domain"?
"""

from __future__ import annotations

import json
import math
import re
import resource
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import flashlight_blocks as fb  # noqa: E402

DATA = json.loads((HERE / "flashlight_data.json").read_text())
SHORT = "How much memory does the desktop leave free?"
WORDS = re.compile(r"[a-z0-9]+")


def rss_peak_mib() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def rss_now_mib() -> float:
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return 0.0


class Lexical:
    """TF-IDF cosine or BM25 over lowercase word tokens, fitted on the texts it is asked to index."""

    def __init__(self, kind: str):
        self.kind = kind

    def fit(self, docs: list[str]) -> None:
        self.docs = [Counter(WORDS.findall(d.lower())) for d in docs]
        n = len(docs)
        df = Counter(w for d in self.docs for w in d)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
        self.avg = sum(sum(d.values()) for d in self.docs) / n
        self.norm = [math.sqrt(sum((tf * self.idf[w]) ** 2 for w, tf in d.items())) or 1 for d in self.docs]

    def scores(self, query: str) -> np.ndarray:
        q = Counter(WORDS.findall(query.lower()))
        out = np.zeros(len(self.docs))
        for i, d in enumerate(self.docs):
            if self.kind == "bm25":
                k1, b, length = 1.2, 0.75, sum(d.values())
                out[i] = sum(self.idf[w] * d[w] * (k1 + 1) / (d[w] + k1 * (1 - b + b * length / self.avg))
                             for w in q if w in d)
            else:
                dot = sum(qtf * self.idf[w] * d[w] * self.idf[w] for w, qtf in q.items() if w in d)
                qn = math.sqrt(sum((qtf * self.idf.get(w, 0)) ** 2 for w, qtf in q.items())) or 1
                out[i] = dot / (qn * self.norm[i])
        return out


class Static:
    """A Model2Vec static model: cosine between mean-pooled, normalised token vectors."""

    def __init__(self, name: str):
        from model2vec import StaticModel
        self.model = StaticModel.from_pretrained(name)

    def embed(self, texts: list[str]) -> np.ndarray:
        v = self.model.encode(texts)
        return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)

    def fit(self, docs: list[str]) -> None:
        self.index = self.embed(docs)

    def scores(self, query: str) -> np.ndarray:
        return self.index @ self.embed([query])[0]


def disk_mib(name: str) -> float | None:
    if "/" not in name:
        return 0.0
    from huggingface_hub.constants import HF_HUB_CACHE  # the files the model actually downloaded
    path = Path(HF_HUB_CACHE) / ("models--" + name.replace("/", "--")) / "blobs"
    return round(sum(f.stat().st_size for f in path.iterdir() if f.is_file()) / 2**20, 1)


def ms_per_text(engine, text: str, n: int = 200) -> float:
    """Warm, one text at a time, as a resident process would see a sentence."""
    if isinstance(engine, Static):
        f = lambda: engine.embed([text])  # noqa: E731
    else:
        f = lambda: engine.scores(text)  # noqa: E731  (lexical: the whole query step)
    for _ in range(10):
        f()
    times = []
    for _ in range(n):
        t = time.perf_counter()
        f()
        times.append((time.perf_counter() - t) * 1000)
    return round(statistics.median(times), 3)


def auc(pos: list[float], neg: list[float]) -> float:
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 3)


def best_threshold(pos: list[float], neg: list[float]) -> dict:
    best = (0.0, 0.0)
    for t in sorted(set(pos + neg)):
        acc = (sum(p >= t for p in pos) + sum(n < t for n in neg)) / (len(pos) + len(neg))
        best = max(best, (acc, t))
    return {"accuracy": round(best[0], 3), "threshold": round(float(best[1]), 4)}


def route(make, labels: dict, tests: list, with_anchors: bool) -> dict:
    protos, owner = [], []
    for name, spec in labels.items():
        for text in [spec["description"]] + (spec["anchors"] if with_anchors else []):
            protos.append(text)
            owner.append(name)
    engine = make()
    engine.fit(protos)
    right, wrong = 0, []
    for text, want in tests:
        got = owner[int(np.argmax(engine.scores(text)))]
        right += got == want
        if got != want:
            wrong.append([text, want, got])
    return {"accuracy": round(right / len(tests), 3), "right": right, "of": len(tests), "wrong": wrong}


def main(name: str) -> dict:
    make = (lambda: Lexical(name)) if name in ("bm25", "tfidf") else (lambda: Static(name))
    base = rss_peak_mib()
    t = time.perf_counter()
    engine = make()
    load_s = time.perf_counter() - t
    loaded_rss = rss_now_mib()
    blocks = fb.blocks()
    texts = [b["text"] for b in blocks]
    ids = [b["id"] for b in blocks]
    t = time.perf_counter()
    engine.fit(texts)
    index_s = time.perf_counter() - t
    block100 = min(texts, key=lambda x: abs(len(x.split()) - 100))
    r = DATA["retrieval"]

    def retrieve(questions):
        top1 = top3 = 0
        best, misses = [], []
        for q, want in questions:
            s = engine.scores(q)
            order = [ids[i] for i in np.argsort(-s)[:3]]
            top1 += order[0] in want
            top3 += any(o in want for o in order)
            best.append(float(s.max()))
            if order[0] not in want:
                misses.append([q, order[0]])
        return {"questions": len(questions), "top1": top1, "top3": top3, "misses": misses}, best

    clean, pos = retrieve(r["questions"])
    noisy, _ = retrieve(DATA["noisy"]["retrieval"])
    neg = [float(engine.scores(q).max()) for q in r["outside"]]
    lab = DATA["routing"]
    return {
        "candidate": name, "load_s": round(load_s, 3), "index_s": round(index_s, 3),
        "rss_before_mib": round(base, 1), "rss_loaded_mib": round(loaded_rss, 1),
        "rss_peak_mib": round(rss_peak_mib(), 1), "disk_mib": disk_mib(name),
        "ms_short_sentence": ms_per_text(engine, SHORT),
        "ms_100_words": ms_per_text(engine, block100), "block_words": len(block100.split()),
        "routing_description_only": route(make, lab["labels"], lab["tests"], False),
        "routing_with_anchors": route(make, lab["labels"], lab["tests"], True),
        "routing_noisy_with_anchors": route(make, lab["labels"], DATA["noisy"]["routing"], True),
        "retrieval": {"blocks": len(blocks), **clean},
        "retrieval_noisy": noisy,
        "out_of_domain": {"auc": auc(pos, neg), "best_threshold": best_threshold(pos, neg),
                          "guide_top1_median": round(statistics.median(pos), 4),
                          "outside_top1_median": round(statistics.median(neg), 4)},
    }


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), ensure_ascii=False))
