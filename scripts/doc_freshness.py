"""Freshness banners for workline records (Professor Step 13).

Every record in worklines/<name>/docs/*.md carries one line under its title:

    > **Freshness:** 🟡 historical · **Written:** 2026-10-03 · **Checked:** 2026-10-31 · **Step:** luna 5.2 ✅

- 🟢 current: the reference for an open step, or a standing contract, runbook or protocol;
- 🟡 historical: the record of a finished step, true on its date, not updated;
- 🔴 superseded by [newer record](link): replaced; the link is mandatory;
- ⚪ draft: a proposal or note not yet acted on.

Usage:
    python scripts/doc_freshness.py --propose     # print the proposed banner of every record
    python scripts/doc_freshness.py --write       # write proposed banners; keep existing ones
    python scripts/doc_freshness.py --check       # exit 1 if a record lacks a valid banner

The proposal reads Git (first commit date), the record's step prefix (NNSS_ → step NN.SS)
and that step's checkbox in plan_<name>.md. Professor reviews 🟢 and 🔴 by hand.
"""
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANNER = re.compile(r"^> \*\*Freshness:\*\* (🟢 current|🟡 historical|🔴 superseded by \[[^\]]+\]\([^)]+\)|⚪ draft)"
                    r" · \*\*Written:\*\* \d{4}-\d{2}-\d{2} · \*\*Checked:\*\* \d{4}-\d{2}-\d{2}"
                    r"( · \*\*Step:\*\* .+)?$")
STANDING = re.compile(r"contract|runbook|protocol|reference|controls|cheat|conventions", re.I)


def records():
    out = subprocess.run(["git", "ls-files", "worklines/*/docs/*.md"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [ROOT / p for p in out.stdout.split()]


def written(path):
    out = subprocess.run(["git", "log", "--diff-filter=A", "--follow", "--format=%ad", "--date=short", "--", str(path)],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    return out[-1] if out else datetime.date.today().isoformat()


def step_state(workline, step, sub):
    plan = ROOT / "worklines" / workline / f"plan_{workline}.md"
    if not plan.exists():
        return None
    text = plan.read_text()
    if sub:
        m = re.search(rf"^\s*- \[([ xX])\] {step}\.{sub}[a-z]?\b", text, re.M)
        if m:
            return m.group(1).lower() == "x"
    m = re.search(rf"^### Step {step}\b.*?\n\*\*Status\*\*:?\s*([^\n]*)", text, re.M | re.S)
    if m:
        s = m.group(1).lower()
        return "✅" in s or "done" in s or "complete" in s or "closed" in s
    return None


def propose(path, today):
    workline = path.parts[-3]
    head = path.read_text()[:1500].lower()
    m = re.match(r"(\d{2})(\d{2})_", path.name)
    step = sub = None
    if m and m.group(1) != "00":
        step, sub = int(m.group(1)), int(m.group(2))
    done = step_state(workline, step, sub) if step else None
    if step is None:
        fresh, step_txt = "🟡 historical", ""
    else:
        label = f"{workline} {step}" + (f".{sub}" if sub else "")
        step_txt = f" · **Step:** {label} " + ("✅" if done else "⏳" if done is False else "?")
        fresh = "🟢 current" if done is False else "🟡 historical"
    if STANDING.search(path.name) and "supersed" not in head:
        fresh = "🟢 current"
    if "draft" in head[:400] and done is not True:
        fresh = "⚪ draft"
    return f"> **Freshness:** {fresh} · **Written:** {written(path)} · **Checked:** {today}{step_txt}"


def insert(path, banner):
    lines = path.read_text().split("\n")
    for i, l in enumerate(lines):
        if l.startswith("> **Freshness:**"):
            return False                                  # keep a banner someone already set
    for i, l in enumerate(lines):
        if l.startswith("# "):
            lines[i + 1:i + 1] = ["", banner]
            path.write_text("\n".join(lines))
            return True
    lines[0:0] = [banner, ""]
    path.write_text("\n".join(lines))
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--propose"
    today = datetime.date.today().isoformat()
    bad = []
    for p in records():
        rel = p.relative_to(ROOT)
        if mode == "--check":
            ok = any(BANNER.match(l) for l in p.read_text().split("\n")[:12])
            if not ok:
                bad.append(str(rel))
        elif mode == "--write":
            if insert(p, propose(p, today)):
                print(f"wrote  {rel}")
        else:
            print(f"{rel}\n  {propose(p, today)}")
    if bad:
        print("records without a valid freshness banner:", *bad, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()
