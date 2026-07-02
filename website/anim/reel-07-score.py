# REEL 7 — SCORE. "Where the baseline got half the words wrong, this gets four of
# five right — 18.5% word error, from muscles alone."
# OPENS ON: the chosen sentence (== scene 6 close).
# Its words disband into particles that reform as 51; the number falls
# 51 -> 40 -> 26 -> 18.5 as a bar shrinks; five word-slots draw, four light.
# CLOSES ON: 18.5 small + dim, sinking toward the bottom  (== scene 8 open).
from manim import *
from style import *
from reel_common import WHITE, counter, motes, drift
import numpy as np

STEPS = [51.17, 40.63, 26.14, 18.53]
SENTENCE = "the cat sat by the door"


def outline_points(mob, n):
    subs = [m for m in mob.family_members_with_points() if len(m.points) >= 4]
    pts = []
    for m in subs:
        k = max(8, len(m.points) // 3)
        for t in np.linspace(0, 1, k, endpoint=False):
            pts.append(m.point_from_proportion(t))
    pts = np.array(pts)
    idx = np.random.RandomState(7).choice(len(pts), n, replace=len(pts) < n)
    return pts[idx]


class Score(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the chosen sentence (matched) -----------------------
        self.next_section("open")
        sent = mono(SENTENCE, 30, INK).move_to(ORIGIN)
        self.add(sent)
        self.wait(0.1)

        # ---- BEAT 1: sentence -> particles -> the number 51 ------------
        self.next_section("gather")
        N = 150
        big = num("51", 150, INK).move_to([0, 0.4, 0])
        targets = outline_points(big, N)
        src = outline_points(sent, N)
        parts = VGroup(*[Dot(src[i], radius=0.02, color=INK).set_opacity(0.8)
                         for i in range(N)])
        self.add(parts)
        self.play(FadeOut(sent), run_time=0.3)
        self.play(LaggedStart(*[parts[i].animate.move_to(targets[i])
                                for i in range(N)], lag_ratio=0.002),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)

        wer_t = ValueTracker(STEPS[0])
        readout = counter(wer_t, fmt=lambda v: f"{v:.1f}", s=150, c=INK, at=[0, 0.4, 0])
        self.add(readout)
        self.play(parts.animate.set_opacity(0.0), run_time=0.3)
        self.remove(parts)
        pct = mono("% of words wrong", 22, INK_FAINT).next_to(readout, DOWN, buff=0.5)
        pct.add_updater(lambda m: m.next_to(readout, DOWN, buff=0.5))
        self.add(pct)

        # ---- BEAT 2: the number falls; a bar shrinks -------------------
        self.next_section("fall")
        BAR_L, BAR_R, BAR_Y = -3.6, 3.6, -2.4
        track = RoundedRectangle(width=BAR_R - BAR_L, height=0.16, corner_radius=0.04,
                                 stroke_color=INK_GHOST, stroke_width=1.4,
                                 fill_opacity=0).move_to([(BAR_L + BAR_R) / 2, BAR_Y, 0])
        fill = RoundedRectangle(width=BAR_R - BAR_L, height=0.16, corner_radius=0.04,
                                stroke_width=0, fill_color=INK, fill_opacity=0.8)
        fill.move_to(track.get_center())

        def bar_for(v):
            frac = v / STEPS[0]
            w = (BAR_R - BAR_L) * frac
            r = RoundedRectangle(width=max(0.05, w), height=0.16, corner_radius=0.04,
                                 stroke_width=0, fill_color=INK, fill_opacity=0.8)
            r.move_to([BAR_L + w / 2, BAR_Y, 0])
            return r
        fill.add_updater(lambda m: m.become(bar_for(wer_t.get_value())))
        self.play(Create(track), FadeIn(fill), run_time=0.4)

        for v in STEPS[1:]:
            self.play(wer_t.animate.set_value(v), run_time=0.7,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(Flash(readout.get_center(), color=WHITE, num_lines=10,
                            flash_radius=1.4, line_length=0.12), run_time=0.25)
        fill.clear_updaters()
        wer_t.set_value(STEPS[-1])

        # ---- BEAT 3: four of five words correct ------------------------
        self.next_section("four-of-five")
        readout.clear_updaters()
        pct.clear_updaters()
        self.play(readout.animate.scale(0.42).move_to([0, 1.5, 0]),
                  pct.animate.scale(0.7).move_to([0, 0.95, 0]).set_opacity(0.6),
                  FadeOut(track), FadeOut(fill), run_time=0.6, rate_func=smooth)

        slots = VGroup(*[RoundedRectangle(width=1.5, height=0.7, corner_radius=0.08,
                                          stroke_color=INK_GHOST, stroke_width=1.6,
                                          fill_opacity=0) for _ in range(5)])
        slots.arrange(RIGHT, buff=0.28).move_to([0, -0.6, 0])
        self.play(LaggedStart(*[Create(s) for s in slots], lag_ratio=0.08), run_time=0.7)
        for i in range(5):
            if i < 4:
                self.play(slots[i].animate.set_fill(INK, 0.9), run_time=0.2)
            else:
                self.play(slots[i].animate.set_stroke(INK_GHOST, 1.6).set_fill(BG, 0),
                          run_time=0.2)
        cap = mono("four words in five, correct", 22, INK_DIM).move_to([0, -1.7, 0])
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=0.4)

        # settle the number toward the bottom (match cut into scene 8)
        self.next_section("settle")
        block = mono("18.5", 30, INK_FAINT)
        block.move_to([0, -0.6, 0])
        self.play(FadeOut(VGroup(readout, pct, slots, cap), run_time=0.5),
                  run_time=0.5)
        self.add(block)
        self.play(block.animate.move_to([0, -1.4, 0]).set_opacity(0.5),
                  run_time=0.6, rate_func=smooth)
        self.wait(0.4)
