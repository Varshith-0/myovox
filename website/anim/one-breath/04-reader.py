# ONE BREATH 4 — READER. "A small network learns to read the filmstrip. While training
# it listens to the real voice — a teacher it copies, then never needs again."
# OPENS ON: one_breath_filmstrip() (== scene 3 close).
# Left-to-right flow: filmstrip → the reader (a box of dials) → the sounds K AE T.
# The reader box sits left-of-centre so the sounds never collide with it. The
# teacher voice pours in from above, then evaporates for good.
# CLOSES ON: the phoneme row K AE T at [3.7, 0]  (== scene 5 open).
from manim import *
from style import *
from one_breath_common import (WHITE, one_breath_filmstrip, dial_box, phoneme_row, trace,
                         motes, drift)
import numpy as np

BOX_C = [-0.9, 0, 0]      # reader box: left of centre, clear of the sounds
STRIP_C = [-4.5, 0, 0]    # filmstrip: far left (the input)
ROW_C = [3.7, 0, 0]       # phoneme row: right (== scene 5 open)


class Reader(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the filmstrip (matched), slide left; reader appears ---
        self.next_section("open")
        strip = one_breath_filmstrip()
        self.add(strip)
        self.wait(0.1)

        box, dials = dial_box(at=BOX_C, w=2.6, h=2.0)
        self.play(strip.animate.scale(0.4).move_to(STRIP_C),
                  FadeIn(box), FadeIn(dials, lag_ratio=0.02), run_time=1.0, rate_func=smooth)
        net_lab = mono("a small network", 20, INK_FAINT).next_to(box, DOWN, buff=0.35)
        self.play(FadeIn(net_lab), run_time=0.3)

        # ---- BEAT 1: frames feed in; dials turn and settle -------------
        self.next_section("learn")
        feed = strip.copy()
        self.add(feed)
        rng = np.random.RandomState(5)
        self.play(
            feed.animate.move_to(box.get_left() + LEFT * 0.05).scale(0.45).set_opacity(0.0),
            LaggedStart(*[d[1].animate.rotate(rng.uniform(-PI, PI)) for d in dials],
                        lag_ratio=0.03),
            run_time=1.1, rate_func=smooth)
        self.remove(feed)

        # ---- BEAT 2: the teacher voice pours in, then evaporates -------
        self.next_section("teacher")
        wave = trace(-1.3, 1.3, 0.0, 0.32, n=180, freq=5.0, seed_n=9)
        wave.set_stroke(INK, 2.0, opacity=0.55).move_to([BOX_C[0], 2.5, 0])
        tlab = mono("real voice · training only", 17, INK_FAINT).next_to(wave, UP, buff=0.12)
        self.play(Create(wave), FadeIn(tlab), run_time=0.6)
        drips = VGroup(*[Dot(wave.point_from_proportion(p), radius=0.05, color=WHITE)
                         for p in np.linspace(0.15, 0.85, 6)])
        self.add(drips)
        self.play(LaggedStart(*[d.animate.move_to(box.get_center()).set_opacity(0.0)
                                for d in drips], lag_ratio=0.08),
                  box.animate.set_stroke(WHITE, 2.4), run_time=1.0)
        self.remove(drips)
        self.play(box.animate.set_stroke(INK, 2.0), run_time=0.3)
        gone = mono("gone at use time", 16, INK_GHOST).move_to(wave.get_center())
        self.play(FadeOut(wave, shift=UP * 0.3), FadeOut(tlab, shift=UP * 0.3), run_time=0.5)
        self.play(FadeIn(gone), run_time=0.25)
        self.play(FadeOut(gone), run_time=0.3)

        # ---- BEAT 3: sounds emerge from the box's right side -----------
        self.next_section("sounds")
        row = phoneme_row(("K", "AE", "T"), at=ROW_C, s=30)
        conduit = DashedLine(box.get_right() + RIGHT * 0.1, row.get_left() + LEFT * 0.2,
                             stroke_color=INK_GHOST, stroke_width=1.4, dash_length=0.12)
        self.play(Create(conduit), run_time=0.35)
        for sym in row:
            src = sym.copy().move_to(box.get_right()).scale(0.4).set_opacity(0.0)
            self.add(src)
            self.play(Transform(src, sym), run_time=0.3)
            self.remove(src)
            self.add(sym)

        # ---- CLOSE: clear the reader, leaving only K AE T (== scene 5) --
        self.next_section("handoff")
        self.play(FadeOut(VGroup(box, dials, net_lab, strip, conduit)), run_time=0.5)
        self.wait(0.4)
