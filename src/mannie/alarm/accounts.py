"""Edit the account files of Luna's new root (plan_mannie.md Step 7), under fakeroot.

- removes Arch Linux ARM's default "alarm" account (uid 1000);
- adds michael as uid/gid 1000 (its files on LUNA_HOME are already 1000:1000),
  in wheel, video, audio, input and render;
- locks root's password (Arch Linux ARM ships root:root); root keeps SSH by key.
Files are rewritten in place, so their owner and mode are kept.
"""

import sys
import time
from pathlib import Path

etc = Path(sys.argv[1])
today = int(time.time() // 86400)
groups = {"wheel", "video", "audio", "input", "render"}


def rewrite(name: str, edit) -> None:
    path = etc / name
    lines = [edit(line) for line in path.read_text().splitlines()]
    path.write_text("".join(line + "\n" for line in lines if line is not None))


def members(line: str, last: int) -> str:
    fields = line.split(":")
    users = [u for u in fields[last].split(",") if u and u != "alarm"]
    if fields[0] in groups and "michael" not in users:
        users.append("michael")
    fields[last] = ",".join(users)
    return ":".join(fields)


rewrite("passwd", lambda l: None if l.startswith("alarm:") else l)
rewrite("shadow", lambda l: None if l.startswith("alarm:") else ("root:!*:" + l.split(":", 2)[2] if l.startswith("root:") else l))
rewrite("group", lambda l: None if l.startswith("alarm:") else members(l, 3))
rewrite("gshadow", lambda l: None if l.startswith("alarm:") else members(l, 3))
with open(etc / "passwd", "a") as f:
    f.write("michael:x:1000:1000:Michael:/home/michael:/bin/bash\n")
with open(etc / "shadow", "a") as f:
    f.write(f"michael:!*:{today}::::::\n")
with open(etc / "group", "a") as f:
    f.write("michael:x:1000:\n")
with open(etc / "gshadow", "a") as f:
    f.write("michael:!::\n")
