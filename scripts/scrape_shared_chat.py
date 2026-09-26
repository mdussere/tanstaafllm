#!/usr/bin/env python3
"""Export a public ChatGPT shared conversation to Markdown with Playwright.

The ChatGPT UI virtualizes old messages.  This scraper therefore visits every
window while scrolling upward, records the DOM ordering of each window, and
uses their overlap to reconstruct the complete conversation.

The browser is deliberately visible: do not change ``headless=False`` unless
you have a reason to debug the browser environment rather than the page.
"""

from __future__ import annotations

import argparse
import heapq
import json
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

from playwright.sync_api import Page, Locator, sync_playwright


DEFAULT_URL = "https://chatgpt.com/share/6ab592d0-65a8-83ed-a39d-a20f3cfec445"
DEFAULT_OUTPUT = Path("docs/2026_09_24_01_iniitial_discussion.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Public ChatGPT share URL")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Markdown destination (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--debug-json",
        type=Path,
        help="Optional path for collected messages and ordering edges",
    )
    return parser.parse_args()


def current_window(page: Page) -> list[dict[str, str]]:
    # ChatGPT collapses long messages behind a visible "Show more" control.
    # Expand the controls in every virtualized window before reading innerText;
    # otherwise the export is not a faithful source record.
    for _ in range(8):
        buttons = page.get_by_role("button", name="Show more", exact=True)
        count = buttons.count()
        if not count:
            break
        clicked = False
        for index in range(count):
            try:
                buttons.nth(index).click(timeout=1_000)
                clicked = True
            except Exception:
                # A virtualized node may disappear after an earlier click.
                # The next sampled window retries any remaining control.
                continue
        if not clicked:
            break
        time.sleep(0.1)

    raw = page.locator("[data-message-author-role]").evaluate_all(
        """nodes => nodes.map(node => ({
            role: node.dataset.messageAuthorRole,
            text: node.innerText,
            id: node.getAttribute('data-message-id') || ''
        }))"""
    )
    messages = []
    for message in raw:
        message_id = message["id"] or f"{message['role']}\x1f{message['text']}"
        messages.append({"id": message_id, "role": message["role"], "text": message["text"]})
    return messages


def collect_conversation(page: Page, root: Locator) -> tuple[dict[str, dict[str, str]], set[tuple[str, str]]]:
    """Scroll to the very top, sampling every virtualized message window."""

    messages: dict[str, dict[str, str]] = {}
    edges: set[tuple[str, str]] = set()
    stable_at_top = 0
    previous_count = 0

    while True:
        window = current_window(page)
        for message in window:
            messages.setdefault(message["id"], message)
        for before, after in zip(window, window[1:]):
            if before["id"] != after["id"]:
                edges.add((before["id"], after["id"]))

        if len(messages) != previous_count:
            if len(messages) % 25 == 0 or len(messages) - previous_count >= 10:
                print(f"Collected {len(messages)} messages", flush=True)
            previous_count = len(messages)

        if root.evaluate("node => node.scrollTop") > 0:
            root.evaluate("node => node.scrollBy(0, -500)")
            stable_at_top = 0
            time.sleep(0.1)
            continue

        # The top must stay stable for several fast polls: reaching scrollTop=0
        # can itself trigger one final batch of older messages.
        time.sleep(0.2)
        stable_at_top += 1
        if stable_at_top >= 8:
            return messages, edges


def chronological_order(messages: dict[str, dict[str, str]], edges: set[tuple[str, str]]) -> list[dict[str, str]]:
    """Topologically sort the per-window DOM order constraints.

    A normal run yields one chain.  The deterministic fallback retains all
    messages even if the UI failed to expose an overlap between two windows.
    """

    successors: dict[str, set[str]] = defaultdict(set)
    indegree = {message_id: 0 for message_id in messages}
    for before, after in edges:
        if before in messages and after in messages and after not in successors[before]:
            successors[before].add(after)
            indegree[after] += 1

    discovery_order = {message_id: index for index, message_id in enumerate(messages)}
    ready = [(discovery_order[message_id], message_id) for message_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    ordered_ids: list[str] = []

    while ready:
        _, message_id = heapq.heappop(ready)
        ordered_ids.append(message_id)
        for successor in sorted(successors[message_id], key=discovery_order.__getitem__):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                heapq.heappush(ready, (discovery_order[successor], successor))

    if len(ordered_ids) != len(messages):
        # Preserve data rather than discarding a cycle created by a transient
        # virtualized DOM state. The JSON debug output makes this diagnosable.
        ordered_ids.extend(message_id for message_id in messages if message_id not in set(ordered_ids))

    return [messages[message_id] for message_id in ordered_ids]


def render_markdown(url: str, messages: list[dict[str, str]]) -> str:
    chunks = [
        "# Activités LLM Raspberry Pi",
        "",
        f"> Source : {url}  ",
        f"> Export Playwright le {date.today().isoformat()} — {len(messages)} messages.",
    ]
    for message in messages:
        role = "Utilisateur" if message["role"] == "user" else "Assistant"
        chunks.extend(("", f"## {role}", "", message["text"].strip()))
    return "\n".join(chunks).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            args=["--disable-gpu"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(args.url, wait_until="networkidle", timeout=120_000)
        root = page.locator("[data-scroll-root]")
        root.wait_for(timeout=30_000)
        time.sleep(0.3)
        messages, edges = collect_conversation(page, root)
        final_scroll = root.evaluate("node => node.scrollTop")
        browser.close()

    ordered = chronological_order(messages, edges)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(args.url, ordered), encoding="utf-8")
    if args.debug_json:
        args.debug_json.parent.mkdir(parents=True, exist_ok=True)
        args.debug_json.write_text(
            json.dumps({"messages": messages, "edges": sorted(edges)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(
        f"Exported {len(ordered)} messages to {args.output} "
        f"({len(edges)} ordering edges; final scrollTop={final_scroll})."
    )


if __name__ == "__main__":
    main()
