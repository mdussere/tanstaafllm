"""Hazel's script-to-video pipeline (worklines/hazel/video/common/): timing, layout lint, reading audit.

Deterministic tests run in the ordinary suite. The two integration tests (`video_pipeline.feature`) need
Playwright's Chromium and ffmpeg: `uv run pytest -m integration test/hazel`.
"""
import copy
import datetime
import pathlib
import subprocess
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
VIDEO = ROOT / 'worklines' / 'hazel' / 'video'
COMMON = VIDEO / 'common'
STORY2 = VIDEO / 'episodes' / 'story2-ask-the-desktop.yaml'
sys.path.insert(0, str(COMMON))

import audit as AU      # noqa: E402
import build as B       # noqa: E402
import layout as LY     # noqa: E402
import lint as LN       # noqa: E402
import slots as SL      # noqa: E402
import timemap as TM    # noqa: E402


@pytest.fixture
def ep():
    return yaml.safe_load(STORY2.read_text())


def scene_of(ep, template):
    return next(s for s in ep['scenes'] if s['template'] == template)


# ---------------------------------------------------------------- time around the holds
HOLDS = [[6.0, 1.5], [20.0, 0.5]]


@pytest.mark.parametrize('t', [0.0, 3.0, 5.99, 6.01, 12.0, 19.9, 20.5, 40.0])
def test_output_time_is_the_inverse_of_source_time(t):
    assert TM.source_time(TM.output_time(t, HOLDS), HOLDS) == pytest.approx(t)


def test_a_hold_freezes_source_time_on_its_cut():
    assert [TM.source_time(T, HOLDS) for T in (6.0, 6.7, 7.49)] == [6.0, 6.0, 6.0]
    assert TM.source_time(7.5, HOLDS) == pytest.approx(6.0)
    assert TM.output_time(10.0, HOLDS) == pytest.approx(11.5)


def test_contact_stills_move_with_the_holds(ep):
    scenes = LY.resolve(ep, B.timeline(ep))
    plain = B.contact_times(scenes, ep)
    cut = scenes[3]['t0']
    held = B.contact_times(scenes, ep, [[cut, 2.0]])
    for s, a, b in zip(scenes, plain, held):
        assert b == pytest.approx(a + (2.0 if s['t0'] >= cut else 0.0)), s['id']


# ---------------------------------------------------------------- the script
def test_timeline_refuses_a_tempo_the_pipeline_does_not_play(ep):
    assert B.timeline(ep)[-1]['t1'] == pytest.approx(90.0)
    ep['bpm'] = 100
    with pytest.raises(ValueError, match='120 bpm'):
        B.timeline(ep)


def test_story2_resolves_with_every_element_inside_its_scene(ep):
    for s in LY.resolve(ep, B.timeline(ep)):
        end = s['clear'] if s['template'] == 'T05' else s['t1'] - s['t0']
        assert all(0 <= m['at'] <= end for m in s['marks']), s['id']


@pytest.mark.parametrize('template', ['two_boxes', 'metrics', 'boss', 'handheld'])
def test_a_scene_too_short_for_its_template_is_refused(ep, template):
    scene_of(ep, template)['bars'] = 2
    with pytest.raises(ValueError, match='elements outside'):
        LY.resolve(ep, B.timeline(ep))


def test_a_missing_slot_names_the_scene_and_the_template(ep):
    sc = scene_of(ep, 'handheld')
    sc['parts'][0]['chips'] = []
    with pytest.raises(ValueError, match=f"scene {sc['id']}: template 'handheld'"):
        LY.resolve(ep, B.timeline(ep))


def test_every_metric_tile_is_read(ep):
    sc = scene_of(ep, 'metrics')
    r = next(s for s in LY.resolve(ep, B.timeline(ep)) if s['id'] == sc['id'])
    texts = [x[1] for x in SL.slots_of(r, ep)]
    for t in sc['tiles']:
        t = t if isinstance(t, dict) else dict(zip(('label', 'value'), t))
        assert f"{t['label']} {t['value']}" in texts


def test_story2_needs_no_reading_hold(ep):
    rows = AU.audit(LY.resolve(ep, B.timeline(ep)), ep)
    assert AU.table(rows)[1] == 0.0


# ---------------------------------------------------------------- the layout lint
def stamp_box(label):
    """The box runtime.js clearStamp() draws, at rest (scale 1, no shake, rotation ignored)."""
    w = LN.CLEAR_SIZE * len(label)
    x = min(LN.W - LN.M - 220, LN.W - LN.M - w * 0.55)
    return x - w / 2, x + w / 2


@pytest.mark.parametrize('label', ['CLEAR!', 'NO GO!', "LET'S DO IT!"])
def test_the_clear_zone_follows_the_label(label):
    x0, _, x1, _ = LN.clear_zone(label)
    a, b = stamp_box(label)
    assert x0 <= a and b <= x1
    assert x1 <= LN.W - LN.M + 8


def box(s, x0, y0, x1, y1, size=40, font='PS2P', **kw):
    return dict(dict(s=s, x0=x0, y0=y0, x1=x1, y1=y1, size=size, font=font, alpha=1.0, scale=1.0, glyph=40, squeeze=1), **kw)


def lint_one(boxes, scene=None):
    sc = scene or dict(id='s', t0=0, t1=10, template='T05')
    return LN.analyse({0.0: boxes}, [sc], [])


def test_tiles_drawn_as_one_group_are_one_secondary_message():
    tiles = [box('42 ms', 830, 560, 1030, 600, group='tiles'), box('0.6 ms', 1340, 560, 1580, 600, group='tiles')]
    assert lint_one(tiles)[2]['two_secondaries'] == 0
    loose = [dict(b, group=None) for b in tiles]
    assert lint_one(loose)[2]['two_secondaries'] == 1


def test_a_squeezed_text_is_reported_and_fails_strict_below_90_percent():
    text, _, problems = lint_one([box('A LONG TITLE', 200, 300, 900, 340, squeeze=0.95)])
    assert 'squeeze: text narrowed' in text and "'A LONG TITLE'" in text and problems['squeeze'] == 0
    assert lint_one([box('A LONG TITLE', 200, 300, 900, 340, squeeze=0.8)])[2]['squeeze'] == 1


def test_a_text_under_a_long_stamp_is_in_the_clear_zone():
    sc = dict(id='s', t0=0, t1=10, template='T05', clear=8.5, clear_text="LET'S DO IT!")
    under = box('a caption', 1000, 930, 1300, 970)          # under LET'S DO IT!, left of where CLEAR! would be
    assert lint_one([under], sc)[2]['clear'] == 1
    assert lint_one([under], dict(sc, clear_text='CLEAR!'))[2]['clear'] == 0


# ---------------------------------------------------------------- integration: Chromium + ffmpeg
def results_dir(name):
    d = ROOT / 'results' / 'hazel' / 'video-pipeline' / (datetime.datetime.now().strftime('%Y%m%dT%H%M%S') + '-' + name)
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.mark.integration
@pytest.mark.timeout(600)
def test_story2_builds_clean_under_strict():
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
                T = TM.output_time(s['t0'] + s['clear'] + 0.6, holds)       # the stamp at rest
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
    assert not errors
