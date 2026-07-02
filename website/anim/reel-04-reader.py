# REEL 4 — READER. "A small network learns to read the filmstrip. While training
# it listens to the real voice — a teacher it copies, then never needs again."
# OPENS ON: the filmstrip (== scene 3 close).
# The strip feeds the left face of a box of dials; dials settle; a ghost voice
# waveform pours light into the box, then evaporates for good; sound symbols
# K AE T emerge from the right.
# CLOSES ON: the phoneme row K AE T  (== scene 5 open).
from manim import *
from style import *
from reel_common import (WHITE, filmstrip, dial_box, phoneme_row, trace,
                         motes, drift)
import numpy as np


class Reader(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the filmstrip, matched, then slide it left ----------
        self.next_section("open")
        strip = filmstrip(count=7, at=[0, 0, 0], tile_size=0.62 * 1.15)
        strip.scale(1.15).shift(RIGHT * 0.5)  # match scene 3's closing transform
        self.add(strip)
        self.wait(0.1)

        box, dials = dial_box(at=[1.4, 0, 0], w=2.8, h=2.2)
        self.play(strip.animate.scale(0.62).move_to([-3.4, 0, 0]),
                  FadeIn(box), FadeIn(dials, lag_ratio=0.02), run_time=1.0,
                  rate_func=smooth)
        net_lab = mono("a small network", 20, INK_FAINT).next_to(box, DOWN, buff=0.35)
        self.play(FadeIn(net_lab), run_time=0.3)

        # ---- BEAT 1: frames feed in; dials turn and settle -------------
        self.next_section("learn")
        feed = strip.copy()
        self.add(feed)
        rng = np.random.RandomState(5)
        self.play(
            feed.animate.move_to(box.get_left() + LEFT * 0.1).scale(0.4).set_opacity(0.0),
            LaggedStart(*[d[1].animate.rotate(rng.uniform(-PI, PI))
                          for d in dials], lag_ratio=0.03),
            run_time=1.1, rate_func=smooth)
        self.remove(feed)

        # ---- BEAT 2: the teacher voice pours in, then evaporates -------
        self.next_section("teacher")
        wave = trace(-2.4, 2.4, 2.55, 0.32, n=200, freq=5.0, seed_n=9)
        wave.set_stroke(INK, 2.0, opacity=0.5).move_to([1.4, 2.5, 0])
        tlab = mono("real voice · training only", 17, INK_FAINT).next_to(wave, UP, buff=0.12)
        self.play(Create(wave), FadeIn(tlab), run_time=0.6)
        # light drips from the waveform down into the box
        drips = VGroup(*[Dot(wave.point_from_proportion(p), radius=0.05, color=WHITE)
                         for p in np.linspace(0.15, 0.85, 6)])
        self.add(drips)
        self.play(LaggedStart(*[d.animate.move_to(box.get_center()).set_opacity(0.0)
                                for d in drips], lag_ratio=0.08),
                  box.animate.set_stroke(WHITE, 2.4), run_time=1.0)
        self.remove(drips)
        self.play(box.animate.set_stroke(INK, 2.0), run_time=0.3)
        # the teacher is gone for good
        gone = mono("teacher — gone at use time", 16, INK_GHOST).move_to(wave.get_center())
        self.play(FadeOut(wave, shift=UP * 0.3), FadeOut(tlab, shift=UP * 0.3),
                  run_time=0.5)
        self.play(FadeIn(gone), run_time=0.25)
        self.play(FadeOut(gone), run_time=0.3)

        # ---- BEAT 3: sounds emerge from the right ----------------------
        self.next_section("sounds")
        row = phoneme_row(("K", "AE", "T"), at=[3.7, 0, 0], s=30)
        # emerge one at a time from the box's right edge
        for i, sym in enumerate(row):
            src = sym.copy().move_to(box.get_right()).scale(0.4).set_opacity(0.0)
            self.add(src)
            self.play(Transform(src, sym), run_time=0.3)
            self.remove(src)
            self.add(sym)
        self.play(FadeOut(net_lab), run_time=0.3)
        self.wait(0.4)
