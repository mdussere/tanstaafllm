"""Deterministic tests for the Wyoh Slate core (Step 6.2).

Behaviour from worklines/wyoh/docs/0600_01_slate-and-keyboard-proposal.md and
the user's decisions of 2026-10-09: A Return, B Backspace, X Delete, Y Shift
for selection, R1/R2 word moves, the whole cross selecting the word (once) or
the line (twice). No terminal is touched.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh"))
import wyoh_slate as s  # noqa: E402


def typed(text: str) -> s.Slate:
    slate = s.Slate()
    slate.insert(text)
    return slate


# --- editing -----------------------------------------------------------------

def test_starts_empty_with_one_line():
    slate = s.Slate()
    assert slate.text() == "" and slate.lines == [""] and slate.cursor == (0, 0)


def test_return_splits_the_line_at_the_cursor():
    slate = typed("hello world")
    for _ in range(6):
        slate.move("left")
    slate.newline()
    assert slate.lines == ["hello", " world"] and slate.cursor == (1, 0)


def test_backspace_joins_lines_at_column_zero():
    slate = typed("ab\ncd")
    slate.move("home")
    slate.backspace()
    assert slate.text() == "abcd" and slate.cursor == (0, 2)


def test_delete_joins_with_the_next_line_at_line_end():
    slate = typed("ab\ncd")
    slate.move("up")
    slate.move("end")
    slate.delete()
    assert slate.text() == "abcd" and slate.cursor == (0, 2)


def test_backspace_and_delete_at_the_edges_do_nothing():
    slate = s.Slate()
    slate.backspace(); slate.delete()
    assert slate.text() == "" and slate.cursor == (0, 0)


def test_multi_line_insert_places_the_cursor_after_it():
    slate = typed("[]")
    slate.move("left")
    slate.insert("a\nbc")
    assert slate.lines == ["[a", "bc]"] and slate.cursor == (1, 2)


# --- movement ----------------------------------------------------------------

def test_left_and_right_cross_line_boundaries():
    slate = typed("ab\ncd")
    slate.move("home"); slate.move("left")
    assert slate.cursor == (0, 2)
    slate.move("right")
    assert slate.cursor == (1, 0)


def test_up_down_keep_the_goal_column():
    slate = typed("long line\nx\nanother line")
    slate.move("home")
    for _ in range(7):
        slate.move("right")
    slate.move("up")
    assert slate.cursor == (1, 1)
    slate.move("up")
    assert slate.cursor == (0, 7)


def test_up_on_the_first_line_goes_home_and_down_on_the_last_goes_end():
    slate = typed("abc")
    slate.move("up")
    assert slate.cursor == (0, 0)
    slate.move("down")
    assert slate.cursor == (0, 3)


def test_word_moves_skip_separators():
    slate = typed("cat dog, bird")
    slate.move("home")
    slate.word("right")
    assert slate.cursor == (0, 3)
    slate.word("right")
    assert slate.cursor == (0, 7)
    slate.word("left")
    assert slate.cursor == (0, 4)


def test_word_moves_cross_lines_at_the_edges():
    slate = typed("ab\ncd")
    slate.move("home")
    slate.word("left")
    assert slate.cursor == (0, 2)
    slate.word("right")
    assert slate.cursor == (1, 0)


# --- selection ---------------------------------------------------------------

def test_shift_arrows_extend_a_selection():
    slate = typed("hello")
    slate.move("left", select=True); slate.move("left", select=True)
    assert slate.selected_text() == "lo"


def test_shift_selection_across_lines():
    slate = typed("ab\ncd")
    slate.move("up", select=True)
    assert slate.selection() == ((0, 2), (1, 2)) and slate.selected_text() == "\ncd"


def test_moving_without_shift_collapses_the_selection_to_its_edge():
    slate = typed("hello")
    slate.move("left", select=True); slate.move("left", select=True)
    slate.move("right")
    assert slate.selection() is None and slate.cursor == (0, 5)
    slate.move("left", select=True)
    slate.move("left")
    assert slate.cursor == (0, 4)


def test_typing_replaces_the_selection():
    slate = typed("hello world")
    slate.word("left", select=True)
    slate.insert("there")
    assert slate.text() == "hello there"


@pytest.mark.parametrize("erase", ["backspace", "delete"])
def test_backspace_or_delete_removes_the_selection_only(erase):
    slate = typed("one two three")
    slate.word("left"); slate.move("left")
    slate.word("left", select=True)
    getattr(slate, erase)()
    assert slate.text() == "one  three"


def test_whole_cross_selects_the_word_under_the_cursor():
    slate = typed("say hello there")
    for _ in range(8):
        slate.move("left")
    assert slate.cursor == (0, 7)
    slate.toggle_word()
    assert slate.selected_text() == "hello"


def test_whole_cross_selects_the_word_just_before_the_cursor():
    slate = typed("say hello")
    slate.toggle_word()
    assert slate.selected_text() == "hello"


def test_whole_cross_again_deselects():
    slate = typed("say hello")
    slate.toggle_word()
    slate.toggle_word()
    assert slate.selection() is None


def test_whole_cross_between_spaces_selects_nothing():
    slate = typed("a   b")
    slate.move("left"); slate.move("left")
    slate.toggle_word()
    assert slate.selection() is None


def test_double_cross_selects_the_line():
    slate = typed("first\nsecond line\nthird")
    slate.move("up")
    slate.select_line()
    assert slate.selected_text() == "second line"
    slate.backspace()
    assert slate.lines == ["first", "", "third"]


# --- decoding what foot sends ------------------------------------------------

@pytest.mark.parametrize("data, event", [
    (b"\x1b[A", s.Event("key", "up")),
    (b"\x1b[D", s.Event("key", "left")),
    (b"\x1bOC", s.Event("key", "right")),
    (b"\x1b[1;2B", s.Event("key", "down", shift=True)),
    (b"\x1b[1;5C", s.Event("key", "right", ctrl=True)),
    (b"\x1b[1;6D", s.Event("key", "left", shift=True, ctrl=True)),
    (b"\x1b[3~", s.Event("key", "delete")),
    (b"\x1b[H", s.Event("key", "home")),
    (b"\x7f", s.Event("key", "backspace")),
    (b"\r", s.Event("key", "enter")),
    (b"\xc3\xa9", s.Event("text", "é")),
])
def test_decoder_maps_xterm_sequences(data, event):
    assert s.Decoder().feed(data) == [event]


def test_decoder_waits_for_split_sequences_and_utf8():
    decoder = s.Decoder()
    assert decoder.feed(b"\x1b[1;") == []
    assert decoder.feed(b"2A\xc3") == [s.Event("key", "up", shift=True)]
    assert decoder.feed(b"\xa0x") == [s.Event("text", "à"), s.Event("text", "x")]


def test_decoder_ignores_unknown_controls_and_alt_keys():
    assert s.Decoder().feed(b"\x01\x1bxa") == [s.Event("text", "a")]


def test_events_drive_the_editor():
    slate = s.Slate()
    for event in s.Decoder().feed(b"ab\rcd\x1b[D\x1b[1;2D\x7f"):
        s.apply(slate, event)
    assert slate.lines == ["ab", "d"]


# --- rendering ---------------------------------------------------------------

def _plain(frame: s.Frame) -> list[str]:
    return ["".join(text for text, _ in row) for row in frame.rows]


def test_render_wraps_long_lines_and_places_the_cursor():
    frame = s.render(typed("abcdefgh\nxy"), width=5, height=5)
    assert _plain(frame) == ["abcde", "fgh", "xy"]
    assert frame.cursor == (2, 2)


def test_render_scrolls_to_keep_the_cursor_visible():
    frame = s.render(typed("1\n2\n3\n4\n5"), width=10, height=3)  # 2 text rows + hint
    assert _plain(frame) == ["4", "5"] and frame.cursor == (1, 1)


def test_cursor_after_a_full_row_moves_to_the_next_row():
    frame = s.render(typed("abcde"), width=5, height=4)
    assert _plain(frame) == ["abcde", ""] and frame.cursor == (1, 0)


def test_render_marks_the_selection():
    slate = typed("say hello")
    slate.toggle_word()
    assert s.render(slate, 20, 3).rows[0] == [("say ", False), ("hello", True)]


def test_hint_shows_the_controls_and_line_count():
    assert s.render(typed("a\nb"), 60, 3).hint == "FN+A send · FN+X clear · L1 hide · 2 lines"


def test_ansi_uses_reverse_video_for_the_selection():
    slate = typed("say hello")
    slate.toggle_word()
    assert "\x1b[7mhello\x1b[27m" in s.to_ansi(s.render(slate, 20, 3))


# --- dictation (Step 12) -------------------------------------------------------

def test_dictated_text_is_inserted_at_the_cursor_with_a_space():
    slate = typed("echo")
    slate.insert_dictated("bonjour le monde ")
    assert slate.text() == "echo bonjour le monde"
    empty = s.Slate()
    empty.insert_dictated("salut")
    assert empty.text() == "salut"


def test_dictated_text_replaces_a_selection():
    slate = typed("say hello")
    slate.toggle_word()
    slate.insert_dictated("bonjour")
    assert slate.text() == "say bonjour"


def test_empty_dictation_changes_nothing():
    slate = typed("abc")
    slate.insert_dictated("   ")
    assert slate.text() == "abc"


def test_provisional_text_is_shown_underlined_but_not_in_the_text():
    slate = typed("echo")
    frame = s.render(slate, 40, 3, provisional="ce site", dictation="listening")
    assert frame.rows[0] == [("echo ", False), ("ce site", s.PROVISIONAL)]
    assert slate.text() == "echo"
    assert frame.hint.startswith("dictation: listening")
    assert "\x1b[4mce site\x1b[24m" in s.to_ansi(frame)


def test_provisional_text_inside_a_line_keeps_the_rest_after_it():
    slate = typed("ab cd")
    slate.move("left"); slate.move("left"); slate.move("left")  # after "ab"
    frame = s.render(slate, 40, 3, provisional="xy")
    assert frame.rows[0] == [("ab ", False), ("xy", s.PROVISIONAL), (" cd", False)]


def test_loading_state_hint():
    assert s.render(s.Slate(), 60, 3, dictation="loading").hint.startswith("dictation: loading")


# --- keys during dictation (user, 2026-10-15) ----------------------------------------

ENTER = s.Event("key", "enter")
BACK = s.Event("key", "backspace")


def test_a_key_while_listening_stops_and_waits_for_the_dictated_text():
    hold = s.KeyHold()
    assert hold.key(BACK, "listening", 0.0) == ([], True)
    assert hold.key(BACK, "stopping", 0.1) == ([], False)  # stop already asked
    slate = typed("Bonjour")
    slate.insert_dictated("Luna.")  # the final text arrives first
    for event in hold.release():
        s.apply(slate, event)
    assert slate.lines == ["Bonjour Lun"]  # Backspace erases the dictated end


def test_return_after_dictation_goes_after_the_spoken_words():
    hold, slate = s.KeyHold(), typed("Note :")
    now, stop = hold.key(ENTER, "listening", 0.0)
    assert now == [] and stop
    slate.insert_dictated("acheter du pain.")
    for event in hold.release():
        s.apply(slate, event)
    assert slate.lines == ["Note : acheter du pain.", ""] and slate.cursor == (1, 0)


def test_a_key_while_loading_cancels_the_start_and_acts_at_once():
    assert s.KeyHold().key(ENTER, "loading", 0.0) == ([ENTER], True)


def test_keys_act_at_once_without_dictation_or_after_an_error():
    hold = s.KeyHold()
    assert hold.key(ENTER, "", 0.0) == ([ENTER], False)
    assert hold.key(ENTER, "error: no capture device", 0.0) == ([ENTER], False)


def test_held_keys_are_released_after_the_limit():
    hold = s.KeyHold(limit=3.0)
    hold.key(ENTER, "listening", 10.0)
    assert not hold.expired(12.0) and hold.expired(13.5) and hold.release() == [ENTER] and hold.held == []



# --- history (FN+up / FN+down, user 2026-10-15) ----------------------------------------

def test_history_walks_back_newest_first_and_returns_to_the_draft():
    history = s.History(["first", "second"])
    assert history.next() is None  # nothing to go forward to yet
    assert history.previous("my draft") == "second"
    assert history.previous("second") == "first"
    assert history.previous("first") == "first"  # stays on the oldest
    assert history.next() == "second"
    assert history.next() == "my draft"
    assert history.next() is None


def test_empty_history_changes_nothing():
    assert s.History().previous("draft") is None



def test_send_while_listening_stops_dictation_and_waits_for_the_text():
    hold = s.KeyHold()
    assert hold.send_now("listening", 0.0) == (False, True)
    assert hold.waiting() and hold.send
    assert not hold.expired(2.0) and hold.expired(3.5)  # sent anyway if the text never comes


def test_send_without_dictation_goes_at_once():
    assert s.KeyHold().send_now("", 0.0) == (True, False)
    assert s.KeyHold().send_now("loading", 0.0) == (True, False)


def test_return_then_send_while_listening_keep_their_order():
    hold, slate = s.KeyHold(), typed("Note :")
    hold.key(ENTER, "listening", 0.0)
    assert hold.send_now("stopping", 0.5) == (False, False)
    slate.insert_dictated("du pain.")
    for event in hold.release():
        s.apply(slate, event)
    assert hold.send and slate.text() == "Note : du pain.\n"



# --- "/" commands for agents (user, 2026-10-15) ------------------------------------------

@pytest.mark.parametrize("before, dictated, after", [
    ("/", "Usage.", "/usage"),
    ("hello /", "Compact!", "hello /compact"),
    ("/", "Clear context.", "/clear context"),
    ("a/", "Usage.", "a/ Usage."),        # not a command: inside a word
    ("echo", "Usage.", "echo Usage."),
])
def test_dictation_after_a_slash_becomes_a_command(before, dictated, after):
    slate = typed(before)
    slate.insert_dictated(dictated)
    assert slate.text() == after
