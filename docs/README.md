# Welcome to Luna

> *"There ain't no such thing as a free lunch."*: Heinlein, *The Moon Is a Harsh Mistress*.
> Here: **there ain't no such thing as a free LLM.**

**Luna** is a 30-euro retro-gaming handheld, the R36 Ultra, that we are turning into a small AI-native computer. It has 4 slow ARM cores, 1 GiB of RAM, a square 720 × 720 screen, and a gamepad instead of a keyboard. The question behind the project: on a machine this small, **what is the least intelligence that does the job**, and what does each piece of it cost?

The names come from the novel. **Luna** is the machine. **Wyoh** is the desktop. **Mycroft** turns voice into text. **Mike** is the small local brain. **Mannie** is the large remote model, called on deliberately because he is expensive. AI agents build all this, one per part, organised in a **cell** as the revolutionaries are in the book. The user works with each of them directly, and the **Professor** steps in only to coordinate across agents or to supervise while the user is away.

## Read in this order

| Page | What you get | Time |
|---|---|---|
| [01 · Principles](01_principles.md) | The idea, the vocabulary, the rules of design | 10 min |
| [04 · Architecture](04_architecture.md) | The whole machine, how a request travels, where the memory goes, how the cell works | 10 min |
| [10 · Wyoh, the desktop](10_wyoh.md) | Sway, the gamepad daemon, the Slate, the apps | 5 min |
| [11 · Mycroft](11_mycroft.md) | Voice to text, models, what dictation costs on Luna | 5 min |
| [12 · Mike](12_mike.md) | The local brain: one request, one action | 5 min |
| [13 · Mannie](13_mannie.md) | The frontier model, and the price of a "pong" | 4 min |
| [14 · Luna](14_luna.md) | The device, its cards, what is still open | 4 min |
| [15 · The cell](15_the-cell.md) | How the agents build all this | 5 min |
| 20–30 · Operations, user guide, decisions | Running it, using it, and why it is like this | *to come* |
| [03 · The bring-up story](03_r36-ultra-bring-up-story.md) | How the handheld was brought up, card by card | 15 min |
| [05 · The text-to-shell story](05_text-to-shell-story.md) | Why a tiny model cannot turn a sentence into a shell command, measured | 6 min |
| [02 · Testing](02_testing.md) | How every test and experiment is written and run | for contributors |
| [How-to guides](howto/README.md) | Doing things on Luna yourself, step by step (first: fixing a game's buttons) | per guide |
| [LOGBOOK](LOGBOOK.md) | Every material change, by date | reference |

The project's manifesto is the repository's [`README.md`](../README.md). Diagrams live in [`img/`](img/), as SVG with a PNG render beside each one.

*Written by Professor, first edition, 2026-10-11. Every figure here comes from a measurement recorded in a workline. Each page names its sources.*
