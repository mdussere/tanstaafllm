Feature: Mannie's persona and project snapshot on the device (Mannie plan 2.5)
  Claude Code on luna-pi or Luna knows it is Mannie, and knows where the project's
  documentation is, without loading it into every request. Executed by
  test/mannie/test_mannie_context.py. The bundle checks run by default; deployment
  and the request are live (MANNIE_LUNA_PI_LIVE=1 or MANNIE_LUNA_LIVE=1).

  Background:
    Given the bundle is built from the repository by src/mannie/build_context.py
    And it holds MANNIE.md, VERSION and repo/ (the repository's Markdown, same layout, with INDEX.md)

  Scenario: the bundle is complete and small where it matters
    Then repo/ holds README.md, AGENTS.md, docs/ and every workline plan and doc
    And INDEX.md lists every file with its size and first heading
    And MANNIE.md, which every session loads, stays under 4 KiB
    And no file contains a credential-like string

  Scenario: deploy without touching the user's own settings
    Given the target user's home is $HOME ("/storage" for root on Luna)
    When the bundle is unpacked beside ~/.local/share/tanstfaafllm/mannie/context and swapped in
    Then ~/.claude/CLAUDE.md contains the line "@~/.local/share/tanstfaafllm/mannie/context/MANNIE.md"
    And any other line already in ~/.claude/CLAUDE.md is kept
    And the credential file is never read

  Scenario: Claude answers as Mannie
    Given the user has logged in on the target
    When "claude -p" is asked who it is and where the project documentation is, without tools
    Then the answer names Mannie and the snapshot directory
    And its tokens, wall time and peak RSS are saved, to compare with a plain "pong"
