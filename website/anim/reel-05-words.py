# REEL 5 — WORDS. "It guesses sounds, not spelling. A map of 34,546 English words
# turns sounds into sentences — by finding the cheapest path through it."
# OPENS ON: the phoneme row K AE T (== scene 4 close).
# The sounds feed a LEGIBLE word lattice: 6 columns, each the right word plus a
# look-alike. A single cheapest path lights up left-to-right through the real
# words; those lit words then slide together INTO the finished sentence — so the
# viewer actually sees the sentence get produced.
# CLOSES ON: the sentence "the cat sat by the door".
from manim import *
from style import *
from reel_common import WHITE, phoneme_row, motes, drift
import numpy as np

CORRECT = ["the", "cat", "sat", "by", "the", "door"]
ALT = ["a", "cot", "sad", "buy", "an", "dock"]
ALT_SIDE = [+1, -1, +1, -1, +1, -1]      # which side the look-alike sits
COLS_X = np.linspace(-4.2, 4.2, 6)
Y_MID, Y_OFF = 0.0, 1.0
SENTENCE = "the cat sat by the door"


class Words(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the phoneme row (matched); lift it to feed the map ---
        self.next_section("open")
        row = phoneme_row(("K", "AE", "T"), at=[3.7, 0, 0], s=30)
        self.add(row)
        self.play(row.animate.scale(0.8).move_to([0, 3.05, 0]), run_time=0.7, rate_func=smooth)
        sub = mono("guesses sounds, not spelling", 16, INK_FAINT).next_to(row, DOWN, buff=0.18)
        self.play(FadeIn(sub), run_time=0.3)

        # ---- BEAT 1: build the word lattice — real words, look-alikes ---
        self.next_section("map")
        start = Circle(0.16, stroke_color=INK, stroke_width=2.4,
                       fill_color=BG, fill_opacity=1).move_to([-5.7, Y_MID, 0])
        end = Circle(0.16, stroke_color=INK, stroke_width=2.4,
                     fill_color=BG, fill_opacity=1).move_to([5.7, Y_MID, 0])

        correct, alts = [], []
        for i, x in enumerate(COLS_X):
            c = mono(CORRECT[i], 22, INK).move_to([x, Y_MID, 0])
            a = mono(ALT[i], 20, INK_GHOST).move_to([x, Y_MID + ALT_SIDE[i] * Y_OFF, 0])
            correct.append(c)
            alts.append(a)
        correct_g = VGroup(*correct)
        alts_g = VGroup(*alts)

        def link(p, q, gap=0.42):
            a = np.array(p, float)
            b = np.array(q, float)
            u = (b - a) / (np.linalg.norm(b - a) + 1e-9)
            return Line(a + u * gap, b - u * gap, stroke_color=INK_GHOST, stroke_width=1.2)

        spine = [link(start.get_center(), [COLS_X[0], Y_MID, 0], 0.22)]
        branches = []
        for i in range(5):
            spine.append(link([COLS_X[i], Y_MID, 0], [COLS_X[i + 1], Y_MID, 0]))
            branches.append(link([COLS_X[i], Y_MID, 0], alts[i + 1].get_center()))
            branches.append(link(alts[i].get_center(), [COLS_X[i + 1], Y_MID, 0]))
        spine.append(link([COLS_X[5], Y_MID, 0], end.get_center(), 0.22))
        # branches off the alts of the first / into the last, for a fuller web
        branches.append(link(start.get_center(), alts[0].get_center(), 0.22))
        branches.append(link(alts[5].get_center(), end.get_center(), 0.22))
        spine_g = VGroup(*spine)
        branch_g = VGroup(*branches)

        maplab = mono("34,546 words  ·  five times what it trained on", 18, INK_FAINT
                      ).move_to([0, -2.55, 0])

        self.play(GrowFromCenter(start), GrowFromCenter(end), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.05) for m in [*correct, *alts]],
                              lag_ratio=0.03),
                  FadeIn(maplab), run_time=1.0)
        self.play(LaggedStart(*[Create(e) for e in [*spine, *branches]], lag_ratio=0.02),
                  run_time=0.9)
        self.wait(0.2)

        # ---- BEAT 2: the cheapest path lights up, left to right --------
        self.next_section("path")
        cap = mono("find the cheapest path", 18, INK_DIM).move_to([0, -2.55, 0])
        self.play(ReplacementTransform(maplab, cap),
                  alts_g.animate.set_opacity(0.28),
                  branch_g.animate.set_stroke(opacity=0.1),
                  run_time=0.4)

        pulse = Dot(start.get_right(), radius=0.08, color=WHITE)
        self.add(pulse)
        self.play(start.animate.set_stroke(WHITE, 3.0), run_time=0.15)
        for i in range(6):
            self.play(
                pulse.animate.move_to(correct[i].get_center()),
                spine[i].animate.set_stroke(WHITE, 3.0, opacity=1.0),
                correct[i].animate.set_color(WHITE).scale(1.12),
                run_time=0.26, rate_func=smooth)
        self.play(pulse.animate.move_to(end.get_left()),
                  spine[6].animate.set_stroke(WHITE, 3.0, opacity=1.0),
                  end.animate.set_stroke(WHITE, 3.0), run_time=0.24)
        self.remove(pulse)

        # ---- BEAT 3: the lit words slide together INTO the sentence ----
        self.next_section("sentence")
        sent = VGroup(*[mono(w, 32, WHITE) for w in CORRECT]).arrange(RIGHT, buff=0.34)
        sent.move_to([0, 0.2, 0])
        clutter = VGroup(alts_g, spine_g, branch_g, start, end, cap, row, sub)
        self.play(
            *[Transform(correct[i], sent[i]) for i in range(6)],
            FadeOut(clutter),
            run_time=0.9, rate_func=smooth)
        self.add(glow(VGroup(*correct)))
        self.play(Flash([0, 0.2, 0], color=WHITE, num_lines=14, flash_radius=2.2,
                        line_length=0.18, time_width=0.4), run_time=0.5)
        self.wait(0.4)
