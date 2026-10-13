"""Deterministic checks of the Mike smoke bench helpers (no model needed)."""

from __future__ import annotations

import pytest

import mike_bench as bench


def test_every_case_uses_a_listed_tool_and_allowed_values():
    names = {tool["function"]["name"] for tool in bench.TOOLS}
    for case in bench.CASES:
        assert case.tool in names
        if "app" in case.args:
            assert case.args["app"] in bench.APPS
        if "place" in case.args:
            assert case.args["place"] in bench.PLACES


def test_no_raw_sway_or_exec_tool_is_offered():
    names = {tool["function"]["name"] for tool in bench.TOOLS}
    assert not any("sway" in name or "exec" in name for name in names)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ('[launch_app(app="calculator")]', bench.Call("launch_app", {"app": "calculator"})),
        ('<|tool_call_start|>[move_window(app="browser", place="left")]<|tool_call_end|>',
         bench.Call("move_window", {"app": "browser", "place": "left"})),
        ("[list_windows()]", bench.Call("list_windows", {})),
        ("Je ne peux pas faire ça.", None),
        ("[launch_app(app=calculator)]", None),
    ],
)
def test_parse_lfm(text, expected):
    assert bench.parse_lfm(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("<start_function_call>call:launch_app{app:<escape>chess<escape>}<end_function_call>",
         bench.Call("launch_app", {"app": "chess"})),
        ("call:move_window{app:<escape>terminal<escape>,place:<escape>full<escape>}",
         bench.Call("move_window", {"app": "terminal", "place": "full"})),
        ("call:list_windows{}", bench.Call("list_windows", {})),
        ("bonjour", None),
    ],
)
def test_parse_functiongemma(text, expected):
    assert bench.parse_functiongemma(text) == expected


def test_score_counts_a_text_answer_as_none():
    refuse = bench.Case("envoie un mail à paul", "none")
    assert bench.score(refuse, None) == {"tool": True, "exact": True}
    launch = bench.Case("ouvre la calculatrice", "launch_app", {"app": "calculator"})
    assert bench.score(launch, None) == {"tool": False, "exact": False}


def test_score_separates_tool_from_arguments():
    case = bench.Case("mets le navigateur à gauche", "move_window", {"app": "browser", "place": "left"})
    wrong_place = bench.Call("move_window", {"app": "browser", "place": "right"})
    assert bench.score(case, wrong_place) == {"tool": True, "exact": False}
    typed = bench.Case("tape ls -la", "type_text", {"text": "ls -la"})
    assert bench.score(typed, bench.Call("type_text", {"text": " LS -la "}))["exact"]


@pytest.mark.parametrize("fmt", [bench.LFM, bench.GEMMA])
def test_grammar_lists_every_tool_and_every_allowed_value(fmt):
    grammar = bench.grammar_for(fmt)
    for name in bench.TOOL_NAMES:
        assert name in grammar
    for value in bench.APPS + bench.PLACES:
        assert value in grammar
    assert grammar.startswith("root ::= ")


def test_lfm_grammar_output_parses_once_wrapped():
    produced = 'move_window(app="browser", place="left")]'
    assert bench.parse_lfm(bench.LFM.opener + produced) == bench.Call(
        "move_window", {"app": "browser", "place": "left"})


def test_render_prompt_passes_tools_and_request_to_the_template():
    jinja2 = pytest.importorskip("jinja2")
    del jinja2
    template = (
        "{{ bos_token }}{% for t in tools %}{{ t.function.name }};{% endfor %}"
        "{% for m in messages %}<{{ m.role }}>{{ m.content }}{% endfor %}"
        "{% if add_generation_prompt %}<assistant>{% endif %}"
    )
    prompt = bench.render_prompt(template, "<s>", "</s>", "ouvre la calculatrice")
    assert prompt.startswith("<s>list_windows;focus_window;")
    assert prompt.endswith("<user>ouvre la calculatrice<assistant>")


def test_render_prompt_accepts_the_hugging_face_generation_tag():
    pytest.importorskip("jinja2")
    template = "{% for m in messages %}{% generation %}{{ m.content }}{% endgeneration %}{% endfor %}"
    assert bench.render_prompt(template, "", "", "tape ls").endswith("tape ls")


def test_prompt_v2_keeps_the_same_tools_and_avoids_smoke_requests():
    assert [t["function"]["name"] for t in bench.TOOLS_V2] == bench.TOOL_NAMES
    for case in bench.CASES:
        assert case.request not in bench.SYSTEM_PROMPT_V2


def test_common_prefix():
    assert bench.common_prefix([1, 2, 3, 4], [1, 2, 5]) == 2
    assert bench.common_prefix([], [1]) == 0
