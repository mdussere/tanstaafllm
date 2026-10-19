"""Build Mannie's context bundle for Claude Code on Luna (plan_mannie.md 2.5).

The bundle is a directory, deployed as ~/.local/share/tanstfaafllm/mannie/context/:

  MANNIE.md      the persona, imported by ~/.claude/CLAUDE.md (loaded every session)
  VERSION        repository commit and build time of the snapshot
  repo/          read-only snapshot of the repository's Markdown, same layout
  repo/INDEX.md  one line per file: path, size, first heading (read on demand)

Standard library only.

  python3 src/mannie/build_context.py <output directory>
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PERSONA = Path(__file__).with_name("context") / "MANNIE.md"
# Markdown shipped in the snapshot, relative to the repository root.
INCLUDE = ["README.md", "AGENTS.md", "docs/*.md", "worklines/*.md", "worklines/*/plan_*.md", "worklines/*/docs/*.md"]
# The line that ~/.claude/CLAUDE.md must contain; "~" is the device user's home.
IMPORT_LINE = "@~/.local/share/tanstfaafllm/mannie/context/MANNIE.md"


def sources(repo: Path = REPO) -> list[Path]:
    found = {path for pattern in INCLUDE for path in repo.glob(pattern) if path.is_file()}
    return sorted(path.relative_to(repo) for path in found)


def _title(path: Path) -> str:
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("#"):
                return line.lstrip("#").strip()
    return ""


def _version(repo: Path) -> str:
    def git(*args: str) -> str:
        done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
        return done.stdout.strip() if done.returncode == 0 else "unknown"

    dirty = "yes" if git("status", "--porcelain") not in ("", "unknown") else "no"
    built = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"commit: {git('rev-parse', '--short', 'HEAD')}\nuncommitted changes: {dirty}\nbuilt: {built}\n"


def build(output: Path, repo: Path = REPO) -> list[Path]:
    """Write the bundle into an empty or missing `output`; return the snapshot's files."""
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"{output} is not empty")
    files = sources(repo)
    lines = [
        "# Index of the project snapshot",
        "",
        "Read-only copy of the repository's Markdown. Open only the file you need.",
        "",
    ]
    for relative in files:
        target = output / "repo" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo / relative, target)
        size = (repo / relative).stat().st_size
        lines.append(f"- `{relative}` ({max(1, round(size / 1024))} KiB): {_title(repo / relative)}")
    (output / "repo" / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copyfile(PERSONA, output / "MANNIE.md")
    (output / "VERSION").write_text(_version(repo), encoding="utf-8")
    return files


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    print(f"{len(build(Path(sys.argv[1])))} files")
