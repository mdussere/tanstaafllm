"""Source time and output time around the reading holds.

A hold [cut, seconds] freezes the choreography at source time `cut` for `seconds` of output. Source time is the time
of the script (scene t0 / t1, element times); output time is the time of the video (frames, the score after the
holds). `renderFrame(T)` in runtime.js takes an output time and applies the same mapping as `source_time` below
(its `sourceTime`); keep the two in step (test/hazel/test_video_pipeline.py checks them against each other).
"""


def source_time(T, holds):
    """Output time T -> source time (inside a hold: the hold's cut)."""
    acc = 0.0
    for s, d in sorted(holds):
        if T < s + acc:
            break
        if T < s + acc + d:
            return s
        acc += d
    return T - acc


def output_time(t, holds):
    """Source time t -> the output time that shows it (a time exactly on a cut maps to the start of its hold)."""
    return t + sum(d for s, d in holds if s < t)
