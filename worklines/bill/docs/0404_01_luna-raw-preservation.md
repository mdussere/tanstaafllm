# Luna raw session preserved

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** 4.4

## What was preserved

Adam supplied the destination `mdussere/tanstaafllm-bobiverse`. SSH access to its `main` branch succeeded. An unauthenticated GitHub API request returned 404, consistent with a private repository; the connected GitHub app did not list it. Bill copied the identified Luna Claude Code project-session JSONL byte-for-byte, checked the source and copy SHA-256, then pushed [private raw commit `b2f4ad7`](https://github.com/mdussere/tanstaafllm-bobiverse/commit/b2f4ad7). The [raw file](https://github.com/mdussere/tanstaafllm-bobiverse/blob/b2f4ad7/raw/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/session.jsonl) and [manifest](https://github.com/mdussere/tanstaafllm-bobiverse/blob/b2f4ad7/raw/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/manifest.json) are accessible to authorized repository readers.

| Property | Observed value |
| --- | --- |
| Source | One local Claude Code project session for Luna, ID `08421a9a-b5dc-435e-a293-8497430d722a` |
| Capture | 2026-11-05 20:58:15 UTC |
| Size | 13,451,993 bytes; 3,714 JSONL records |
| Timestamp days | 13, from 2026-10-03 through 2026-11-01 |
| SHA-256, source and copy | `9c07746899fd3bba398d103af91f511e67d362a7c2312ea87b3d698093461af9` |

This is the complete accessible content of that one file at capture time. Other Claude Code sessions, global history, separate project-managed memory files and attachment content stored outside this JSONL were not copied. The snapshot does not prove that every interaction elsewhere was retained by Claude Code. No raw content was added to the public TANSTAAFLLM repository.

## Check

The two local files had matching byte counts and SHA-256 values before commit. The private commit was pushed to `main`; checking it out and hashing `session.jsonl` reproduces the manifest value. The follow-on [Step 5 index](0505_01_full-luna-session-pass.md) names this checksum as its source.
