# REEL 3 — FINGERPRINTS. "Too much to read. 50 times a second we ask: which
# muscles move together? Each answer is a fingerprint of the face."
# OPENS ON: the 31-line waterfall  (== scene 2 close).
# The signal compresses into a clean band; a window sweeps it EXACTLY from left
# edge to right edge, full height; each pass drops one fingerprint tile that STAYS,
# building a filmstrip; a scan then runs the finished sequence.
# CLOSES ON: reel_filmstrip()  (== scene 4 open).
from manim import *
from style import *
from reel_common import WHITE, waterfall, reel_filmstrip, motes, drift
import numpy as np

# Where the compressed signal band lives, and its exact extent.
SIG_CY = 1.75          # vertical centre of the band
SIG_L, SIG_R = -3.0, 3.0   # waterfall scaled 0.5 spans exactly [-3, 3]
SIG_H = 2.35           # its height after the 0.5 scale
HALF_W = 0.3           # half the sweep window's width


class Fingerprints(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the waterfall (matched) -----------------------------
        self.next_section("open")
        wf = waterfall()
        self.add(wf)
        self.wait(0.1)

        # ---- BEAT 1: compress the signal into a clean band up top ------
        self.next_section("compress")
        note = mono("which muscles move together?", 22, INK_FAINT).to_edge(UP, buff=0.4)
        self.play(wf.animate.scale(0.5).move_to([0, SIG_CY, 0]).set_stroke(opacity=0.55),
                  FadeIn(note, shift=DOWN * 0.1), run_time=0.9, rate_func=smooth)

        # ---- BEAT 2: a window sweeps the WHOLE signal; each pass drops a
        #      fingerprint tile that STAYS, filling the filmstrip below. ----
        self.next_section("sweep")
        win = Rectangle(width=2 * HALF_W, height=SIG_H, stroke_color=WHITE,
                        stroke_width=2.0, fill_color=WHITE, fill_opacity=0.05
                        ).move_to([SIG_L + HALF_W, SIG_CY, 0])
        self.play(FadeIn(win), run_time=0.3)

        target = reel_filmstrip()               # exact final strip (== scene 4 open)
        xs = np.linspace(SIG_L + HALF_W, SIG_R - HALF_W, 7)  # window centre per capture
        placed = VGroup()
        for k in range(7):
            self.play(win.animate.move_to([xs[k], SIG_CY, 0]),
                      run_time=0.2, rate_func=linear)
            tile = target[k]
            # a captured copy flies from the window down to its slot, then the REAL
            # tile is placed and kept (the earlier version never added it, so tiles
            # vanished the instant the transform ended).
            fly = tile.copy().scale(0.22).move_to([xs[k], SIG_CY, 0]).set_opacity(0.0)
            self.add(fly)
            self.play(Transform(fly, tile), run_time=0.24, rate_func=smooth)
            self.remove(fly)
            self.add(tile)
            placed.add(tile)

        # ---- BEAT 3: 50 / second; scan the finished sequence; settle ----
        self.next_section("filmstrip")
        rate = mono("50 fingerprints / second", 22, INK_FAINT).move_to([0, -2.35, 0])
        self.play(FadeOut(win), FadeOut(wf, shift=UP * 0.25), FadeOut(note),
                  FadeIn(rate, shift=UP * 0.1), run_time=0.7)
        # a bright scan runs left-to-right across the tiles — they are a sequence in
        # time, not a static row. Ends clean on the exact reel_filmstrip pose.
        for k in range(7):
            self.play(Indicate(placed[k], scale_factor=1.12, color=WHITE), run_time=0.12)
        self.wait(0.4)
