"""Tests for Hazel's script-to-video pipeline (worklines/hazel/video/common/, Hazel Step 6).

What the pipeline promises, and what these tests hold it to
-----------------------------------------------------------
An episode script (YAML) is turned by `common/build.py` into a page that draws every frame (`runtime.js`,
`templates.js`), a chip score (`cues.py`), a reading audit (`audit.py`) and a layout lint (`lint.py`). The model
that writes the script only reads the audit, the lint and a contact sheet, so those reports must tell the truth:
a check that passes for the wrong reason is worse than no check. Every test below guards one rule of
`common/README.md`; most were written for a bug found in the code review of 2026-11-02 (pull request #4), named
in the test's docstring:

  R1  the documented build runs from the repository's uv environment (PyYAML declared)
  R2  the lint's CLEAR! zone is where the page draws the stage's end stamp, whatever its label
  R3  everything that renders a frame uses output time; script times are mapped through the reading holds
  R4  the tempo is 120 bpm, and a script asking for another one is refused
  R5  a scene too short for its template, or missing a slot, is refused with the scene's name
  R6  the lint reports texts narrowed to fit, and counts the metric tiles as one message, every tile read

Two clocks
----------
Source time is the script's: scene `t0` / `t1`, element times. Output time is the video's: frame numbers, the
score once the holds are inserted. A hold `[cut, seconds]` freezes the picture at source time `cut` for
`seconds` of output (`common/timemap.py`; `runtime.js` `sourceTime` does the same in the page).

How to run
----------
  uv run pytest -m "not live and not integration" test/hazel   # deterministic: no browser, no ffmpeg (~1 s)
  uv run pytest -m integration test/hazel                     # Chromium (Playwright) and ffmpeg (~15 s)
  uv run pytest test/hazel                                    # both

The deterministic tests resolve the committed Story 2 script (`episodes/story2-ask-the-desktop.yaml`) and change
it in memory; nothing is written. The integration tests are the scenarios of `video_pipeline.feature`; each
keeps its outputs (build log, lint.txt, audit.md, contact.png, stills, a screenshot) in
`results/hazel/video-pipeline/<timestamp>-<name>/`. Look at the stills before trusting a green run.

Not covered: the picture's look (only text boxes are measured), the score's content beyond its event times,
the MP4 encoding, and the hand-written stories (`story1-hello-luna/`, `story2-ask-the-desktop/`, `trailer/`).
"""
import datetime
import json
import pathlib
import subprocess
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
VIDEO = ROOT / 'worklines' / 'hazel' / 'video'
COMMON = VIDEO / 'common'
STORY2 = VIDEO / 'episodes' / 'story2-ask-the-desktop.yaml'
STORY3 = VIDEO / 'episodes' / 'story3-insert-coin-how-we-made-videos.yaml'
CINEMATIC = COMMON / 'cinematic.js'
SPRITES_V3 = COMMON / 'art' / 'sprites-v3'
sys.path.insert(0, str(COMMON))

import audit as AU      # noqa: E402
import build as B       # noqa: E402  (importing it is R1: build.py imports yaml at module level)
import layout as LY     # noqa: E402
import lint as LN       # noqa: E402
import slots as SL      # noqa: E402
import timemap as TM    # noqa: E402


@pytest.fixture
def ep():
    """The committed Story 2 script, freshly loaded: a test may change it in memory."""
    return yaml.safe_load(STORY2.read_text())


def scene_of(ep, template):
    """The first scene of the script that uses `template` (Story 2 uses each stage template once)."""
    return next(s for s in ep['scenes'] if s['template'] == template)


def test_story3_v3b_uses_only_the_committed_bitmap_pack():
    """Hazel 3.3i: Story 3's compositor has no fallback to the artistically rejected SVG cut.

    The complete source pack is versioned under ``art/sprites-v3``; every file named by its manifest exists, and
    the 13-scene script makes its deliberately varied framing explicit. This is a fast guard before the rendered
    preview test below proves that Chromium can load the bytes.
    """
    manifest = json.loads((SPRITES_V3 / 'manifest.json').read_text())
    for spec in manifest['sprites'].values():
        assert (SPRITES_V3 / spec['file']).is_file(), spec['file']
    for spec in manifest['animations'].values():
        assert all((SPRITES_V3 / frame).is_file() for frame in spec['frames'])
    for spec in manifest['backgrounds'].values():
        assert (SPRITES_V3 / spec['file']).is_file(), spec['file']
    compositor = CINEMATIC.read_text()
    assert 'art/cinema/' not in compositor and '.svg' not in compositor
    assert "art/sprites-v3/" in compositor and 'imageSmoothingEnabled = false' in compositor
    scenes = yaml.safe_load(STORY3.read_text())['scenes']
    assert len(scenes) == 13
    assert {s['shot'] for s in scenes} >= {'title', 'wide', 'prop', 'close', 'vignette', 'reveal'}


# ================================================================ R3: two clocks, source and output
# Two holds: 1.5 s at source 6.0 (output 6.0..7.5 shows source 6.0), then 0.5 s at source 20.0 (output 21.5..22.0).
HOLDS = [[6.0, 1.5], [20.0, 0.5]]


@pytest.mark.parametrize('t', [0.0, 3.0, 5.99, 6.01, 12.0, 19.9, 20.5, 40.0])
def test_output_time_is_the_inverse_of_source_time(t):
    """Going from the script's time to the video's and back returns the same time, before, between and after the
    holds. Times exactly on a cut are left to the next test: there, many output times show one source time."""
    assert TM.source_time(TM.output_time(t, HOLDS), HOLDS) == pytest.approx(t)


def test_a_hold_freezes_source_time_on_its_cut():
    """During a hold the picture is frozen: every output time inside it maps to the cut. After it, output time runs
    ahead of source time by the hold's length (10.0 in the script is 11.5 in the video)."""
    assert [TM.source_time(T, HOLDS) for T in (6.0, 6.7, 7.49)] == [6.0, 6.0, 6.0]
    assert TM.source_time(7.5, HOLDS) == pytest.approx(6.0)
    assert TM.output_time(10.0, HOLDS) == pytest.approx(11.5)


def test_contact_stills_move_with_the_holds(ep):
    """Bug 3 of the review: `contact_times` chose each scene's still in source time and handed it to the page,
    which reads output time; after the first hold, every thumbnail showed the wrong moment. Story 2 has no hold,
    so the bug was invisible. With a 2 s hold at the start of scene 3, the stills of scenes 3 and later must move
    2 s later in the video, and the earlier ones must not move."""
    scenes = LY.resolve(ep, B.timeline(ep))
    plain = B.contact_times(scenes, ep)
    cut = scenes[3]['t0']
    held = B.contact_times(scenes, ep, [[cut, 2.0]])
    for s, a, b in zip(scenes, plain, held):
        assert b == pytest.approx(a + (2.0 if s['t0'] >= cut else 0.0)), s['id']


# ================================================================ R4, R5: the script
def test_timeline_refuses_a_tempo_the_pipeline_does_not_play(ep):
    """Bug 4: `bpm` was read by the timeline only. The layout (BEAT = 0.5), the page (BPM = 120) and the score's
    grooves are written for 120 bpm, so `bpm: 100` would have stretched the cuts but not the choreography or the
    music. Story 2 at 120 bpm lasts 90 s (45 bars of 2 s); any other tempo is refused, naming the only one."""
    assert B.timeline(ep)[-1]['t1'] == pytest.approx(90.0)
    ep['bpm'] = 100
    with pytest.raises(ValueError, match='120 bpm'):
        B.timeline(ep)


def test_story2_resolves_with_every_element_inside_its_scene(ep):
    """The committed script passes the new timing check: every cue mark falls between its scene's start and its
    CLEAR! stamp (a frame template: its end). If this fails after a template change, the template now places an
    element where it is never drawn or never heard."""
    for s in LY.resolve(ep, B.timeline(ep)):
        end = s['clear'] if s['template'] == 'T05' else s['t1'] - s['t0']
        assert all(0 <= m['at'] <= end for m in s['marks']), s['id']


@pytest.mark.parametrize('template', ['two_boxes', 'metrics', 'boss', 'handheld'])
def test_a_scene_too_short_for_its_template_is_refused(ep, template):
    """Bug 5: templates place their elements at fixed offsets from the scene's end (and some from its start). At
    2 bars (4 s), `two_boxes` put its spill 2.5 s before the scene, `metrics` its tiles before it, `boss` its first
    hit before it, `handheld` its last presses after the stamp, all silently. `resolve` must now refuse such a
    scene and say what falls outside. The four templates are the ones that broke at 2 bars in the review."""
    scene_of(ep, template)['bars'] = 2
    with pytest.raises(ValueError, match='elements outside'):
        LY.resolve(ep, B.timeline(ep))


def test_a_missing_slot_names_the_scene_and_the_template(ep):
    """R5: a script error must read as a script error. An empty `chips` list used to crash `t_handheld` on
    `ct[-1]` with a bare IndexError; the model fixing the script needs the scene and the template instead."""
    sc = scene_of(ep, 'handheld')
    sc['parts'][0]['chips'] = []
    with pytest.raises(ValueError, match=f"scene {sc['id']}: template 'handheld'"):
        LY.resolve(ep, B.timeline(ep))


def test_every_metric_tile_is_read(ep):
    """R6: the reading audit only counted the last tile of a `metrics` scene, so the time to read the figures was
    underestimated. Every tile ("<label> <value>") must now be an audit slot of its scene."""
    sc = scene_of(ep, 'metrics')
    r = next(s for s in LY.resolve(ep, B.timeline(ep)) if s['id'] == sc['id'])
    texts = [x[1] for x in SL.slots_of(r, ep)]
    for t in sc['tiles']:
        t = t if isinstance(t, dict) else dict(zip(('label', 'value'), t))
        assert f"{t['label']} {t['value']}" in texts


def test_story2_needs_no_reading_hold(ep):
    """A regression guard on the committed script: Story 2 is cut so that its last text on every screen is on long
    enough to be read, and the audit adds no hold (+0.0 s). A change to a template's timing or to the audit's rules
    that makes it add one shows here first; check `audit.md` before accepting the new figure."""
    rows = AU.audit(LY.resolve(ep, B.timeline(ep)), ep)
    assert AU.table(rows)[1] == 0.0


# ================================================================ R2, R6: the layout lint, on hand-made text boxes
def stamp_box(label):
    """Horizontal extent of the end stamp at rest, recomputed here from `runtime.js` `clearStamp()` independently of
    `lint.clear_zone`: centred at W - M - 220 = 1580, moved left so that 55 % of its width stays inside W - M."""
    w = LN.CLEAR_SIZE * len(label)
    x = min(LN.W - LN.M - 220, LN.W - LN.M - w * 0.55)
    return x - w / 2, x + w / 2


@pytest.mark.parametrize('label', ['CLEAR!', 'NO GO!', "LET'S DO IT!"])
def test_the_clear_zone_follows_the_label(label):
    """Bug 2: the zone was computed once for "CLEAR!" (x 1356..1804), but `LET'S DO IT!` is drawn from x 887 to 1757,
    so most of it was never checked. The three labels Story 2 uses must each lie inside their zone, and the zone
    must not reach past the safe margin (plus its 8 px of slack)."""
    x0, _, x1, _ = LN.clear_zone(label)
    a, b = stamp_box(label)
    assert x0 <= a and b <= x1
    assert x1 <= LN.W - LN.M + 8


def box(s, x0, y0, x1, y1, size=40, font='PS2P', **kw):
    """One text box as `runtime.js` records it for the lint (`lintRecord`): fully visible (alpha 1), at rest
    (scale 1), not narrowed (squeeze 1), 40 px glyphs, the secondary-message size. `kw` overrides any field."""
    return dict(dict(s=s, x0=x0, y0=y0, x1=x1, y1=y1, size=size, font=font, alpha=1.0, scale=1.0, glyph=40, squeeze=1), **kw)


def lint_one(boxes, scene=None):
    """Lint one frame at t = 0 of a single 10 s stage scene. Returns (lint.txt text, summary, problem counts)."""
    sc = scene or dict(id='s', t0=0, t1=10, template='T05')
    return LN.analyse({0.0: boxes}, [sc], [])


def test_tiles_drawn_as_one_group_are_one_secondary_message():
    """R6: the phone rule allows one secondary message on screen at a time. The four tiles of `metrics` sit in two
    columns, so the lint saw two messages and reported 8 frames of Story 2's stage 3. The template now draws the
    figures with `group: 'tiles'`, and grouped boxes count as one message; the same boxes without a group still
    count as two, so the rule itself is unchanged. (Treating the tiles as one block is a design choice, open for
    review in pull request #4.) The coordinates are two tile figures of Story 2's stage 3."""
    tiles = [box('42 ms', 830, 560, 1030, 600, group='tiles'), box('0.6 ms', 1340, 560, 1580, 600, group='tiles')]
    assert lint_one(tiles)[2]['two_secondaries'] == 0
    loose = [dict(b, group=None) for b in tiles]
    assert lint_one(loose)[2]['two_secondaries'] == 1


def test_a_squeezed_text_is_reported_and_fails_strict_below_90_percent():
    """R6: `txt()` narrows a text that is wider than its `maxW`, and the lint did not see it. A text at 95 % of its
    width is listed in lint.txt but does not fail `--strict` (Story 2's HUD title "LIKE PLAYWRIGHT, FOR A DESKTOP"
    is at 95 %); below 90 % (SQUEEZE_FAIL) the letters visibly thin and `--strict` fails."""
    text, _, problems = lint_one([box('A LONG TITLE', 200, 300, 900, 340, squeeze=0.95)])
    assert 'squeeze: text narrowed' in text and "'A LONG TITLE'" in text and problems['squeeze'] == 0
    assert lint_one([box('A LONG TITLE', 200, 300, 900, 340, squeeze=0.8)])[2]['squeeze'] == 1


def test_a_text_under_a_long_stamp_is_in_the_clear_zone():
    """Bug 2, seen from the lint's report: a caption at x 1000..1300, y 930..970 is under `LET'S DO IT!` (drawn from
    x 887) but left of where `CLEAR!` would be (from x 1356). It must be reported for the long label and only for it."""
    sc = dict(id='s', t0=0, t1=10, template='T05', clear=8.5, clear_text="LET'S DO IT!")
    under = box('a caption', 1000, 930, 1300, 970)
    assert lint_one([under], sc)[2]['clear'] == 1
    assert lint_one([under], dict(sc, clear_text='CLEAR!'))[2]['clear'] == 0


# ================================================================ integration: Chromium + ffmpeg (video_pipeline.feature)
def results_dir(name):
    """A new evidence folder, results/hazel/video-pipeline/<timestamp>-<name>/ (results/ is not versioned)."""
    d = ROOT / 'results' / 'hazel' / 'video-pipeline' / (datetime.datetime.now().strftime('%Y%m%dT%H%M%S') + '-' + name)
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.mark.integration
@pytest.mark.timeout(600)
def test_story2_builds_clean_under_strict():
    """Scenario "Story 2 builds clean under --strict". Runs the documented build as a subprocess (the CLI is the
    boundary under test: R1, and `--strict`'s exit code): page, score with ffmpeg's loudness pass, lint in
    Chromium, contact sheet; no MP4. Exit 0 under `--strict` means no lint problem and no reading hold. The
    summary line of lint.txt is checked as well, and there is one still per scene. Evidence: build.log and every
    build output in the results folder."""
    out = results_dir('story2-strict')
    run = subprocess.run([sys.executable, str(COMMON / 'build.py'), str(STORY2), '--preview', '--no-video', '--strict',
                          '--out', str(out)], cwd=VIDEO, capture_output=True, text=True)
    (out / 'build.log').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stdout + run.stderr
    summary = (out / 'lint.txt').read_text().strip().splitlines()[-1]
    for k in ('overflow 0', 'margin 0', 'overlap 0', 'clear-zone 0', 'frames with 2+ secondaries 0'):
        assert k in summary, summary
    assert len(list((out / 'stills').glob('*.png'))) == len(yaml.safe_load(STORY2.read_text())['scenes'])


@pytest.mark.integration
@pytest.mark.timeout(600)
def test_page_and_generator_agree_on_stamps_and_holds(ep):
    """Scenario "The page and the generator agree on the end stamp and the holds". The deterministic tests check
    the Python side against a model of the page; this one asks the page itself.

    1. Two holds are added to Story 2's timeline (1.5 s after scene 2, 0.5 s after scene 6), so the page's clock
       and the generator's differ from scene 3 on.
    2. For every stage, the frame 0.6 s after its stamp lands (the stamp at rest, scale 1, no shake) is drawn with
       the lint recorder on, and the stamp's recorded box must lie inside `lint.clear_zone` for its label. This is
       the test that found the rotation gap: the rotated stamp rose 19 px above the old zone.
    3. Every 0.25 s of output, `runtime.js` `sourceTime` must equal `timemap.source_time`: the two copies of the
       hold mapping (R3) cannot drift apart.

    Evidence: the generated page and a screenshot of the last stage's stamp in the results folder."""
    import capture as CAP
    from playwright.sync_api import sync_playwright

    out = results_dir('stamps-holds')
    scenes = LY.resolve(ep, B.timeline(ep))
    holds = [[scenes[2]['t1'], 1.5], [scenes[6]['t1'], 0.5]]
    B.make_page(ep, scenes, holds, out)
    stages = [s for s in scenes if s['template'] == 'T05']
    httpd, url = CAP.serve(out)
    try:
        with sync_playwright() as p:
            browser, page, errors, duration = CAP.open_page(p, url, 1920, 1080)
            for s in stages:
                T = TM.output_time(s['t0'] + s['clear'] + 0.6, holds)
                label = s['clear_text']
                rec = [r for r in page.evaluate('t => window.lintFrame(t)', T) if r['s'] == label]
                assert rec, (s['id'], label)
                x0, y0, x1, y1 = LN.clear_zone(label)
                r = rec[0]
                assert x0 <= r['x0'] and r['x1'] <= x1 and y0 <= r['y0'] and r['y1'] <= y1, (s['id'], label, r)
            for T in [i * 0.25 for i in range(int(duration / 0.25))]:
                js = page.evaluate('T => sourceTime(T)', T)
                assert js == pytest.approx(TM.source_time(T, holds)), T
            page.screenshot(path=str(out / 'last-stage-stamp.png'))
            browser.close()
    finally:
        httpd.shutdown()
    assert not errors, errors


@pytest.mark.integration
@pytest.mark.timeout(600)
def test_story3_bitmap_preview_builds_clean_under_strict():
    """Scenario "Story 3 V3b bitmap preview builds clean under --strict".

    This is the preflight for the GitHub workflow: it builds the exact 13-scene V3b page using Chromium, checks
    the lint and reading audit, and preserves its contact sheet and stills. The workflow performs the same build
    with MP4 encoding after the branch is pushed; this test intentionally stops before a video file.
    """
    out = results_dir('story3-bitmap-strict')
    run = subprocess.run([sys.executable, str(COMMON / 'build.py'), str(STORY3), '--preview', '--no-video', '--strict',
                          '--out', str(out)], cwd=VIDEO, capture_output=True, text=True)
    (out / 'build.log').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stdout + run.stderr
    assert (out / 'contact.png').is_file()
    assert len(list((out / 'stills').glob('*.png'))) == 13
    summary = (out / 'lint.txt').read_text().strip().splitlines()[-1]
    for key in ('overflow 0', 'margin 0', 'overlap 0', 'clear-zone 0', 'frames with 2+ secondaries 0'):
        assert key in summary, summary
