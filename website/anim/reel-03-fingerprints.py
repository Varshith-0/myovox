# REEL 3 — FINGERPRINTS. "Too much to read. 50 times a second we ask: which
# muscles move together? Each answer is a fingerprint of the face."
# OPENS ON: the 31-line waterfall  (== scene 2 close).
# A window sweeps the waterfall; each pass stamps a small symmetric grid below;
# the grids stack into a filmstrip that begins sliding right.
# CLOSES ON: the filmstrip sliding right  (== scene 4 open).
from manim import *
from style import *
from reel_common import (WHITE, waterfall, fingerprint_tile, filmstrip,
                         motes, drift)
import numpy as np


class Fingerprints(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the waterfall (matched) -----------------------------
        self.next_section("open")
        wf = waterfall()
        self.add(wf)
        # gentle life
        self.wait(0.1)

        # ---- BEAT 1: too much — compress the stack up top --------------
        self.next_section("compress")
        note = mono("which muscles move together?", 22, INK_FAINT).to_edge(UP, buff=0.45)
        self.play(wf.animate.scale(0.5).move_to([0, 1.75, 0]).set_stroke(opacity=0.4),
                  FadeIn(note, shift=DOWN * 0.1), run_time=0.9, rate_func=smooth)

        # ---- BEAT 2: a window sweeps; each pass stamps a fingerprint ----
        self.next_section("sweep")
        wf_left, wf_right = -3.0, 3.0
        wtop, wbot = 2.55, 0.95
        win = Rectangle(width=0.7, height=wtop - wbot, stroke_color=WHITE,
                        stroke_width=1.8, fill_opacity=0.0
                        ).move_to([wf_left, (wtop + wbot) / 2, 0])
        self.play(FadeIn(win), run_time=0.3)

        strip_y = -0.9
        n_stamps = 7
        xs = np.linspace(wf_left, wf_right, n_stamps)
        tiles = VGroup()
        step = 0.62 + 0.12
        strip_x0 = -(n_stamps / 2 - 0.5) * step
        for k in range(n_stamps):
            self.play(win.animate.move_to([xs[k], (wtop + wbot) / 2, 0]),
                      run_time=0.24, rate_func=linear)
            t = fingerprint_tile(k=8, size=0.62,
                                 at=[strip_x0 + k * step, strip_y, 0], seed_n=20 + k)
            frame = Square(side_length=0.62, stroke_color=INK_GHOST, stroke_width=1.0,
                           fill_opacity=0).move_to(t.get_center())
            drop = VGroup(t, frame)
            src = drop.copy().move_to([xs[k], (wtop + wbot) / 2, 0]).scale(0.4).set_opacity(0.0)
            self.add(src)
            self.play(Transform(src, drop), run_time=0.22)
            self.remove(src)
            tiles.add(drop)

        # ---- BEAT 3: 50 per second; the filmstrip glides ---------------
        self.next_section("filmstrip")
        rate = mono("50 fingerprints / second", 22, INK_FAINT).to_edge(DOWN, buff=0.6)
        self.play(FadeOut(win), FadeOut(wf, shift=UP * 0.3),
                  note.animate.set_opacity(0.0),
                  FadeIn(rate, shift=UP * 0.1),
                  tiles.animate.move_to([0, 0.0, 0]).scale(1.15),
                  run_time=0.8, rate_func=smooth)
        # a slow continuous rightward glide + a fresh tile easing in at the left
        self.play(tiles.animate.shift(RIGHT * 0.5), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)
