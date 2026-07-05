# S27 — Borrowed light (where the novel methods came from, and who to credit)
# We invented none of the building blocks — we composed them. A clean two-column
# credit ledger, film-credits style: method on the left, the work it came from on
# the right, joined by a faint dotted leader. The joins (leaders + divider) are the
# only thing WE added, so the coda spotlights them.
#
# ART DIRECTION — strict monochrome; the single pure-#fff accent is the closing
# line "composition, not invention".
#   TOP strip   (y ~ +3.1): cap "BORROWED LIGHT" + "the methods, and where they came from"
#   CENTER      : two columns of credits (method ⋯ source), joined by dotted leaders
#   BOTTOM      : the white serif closing line
#
# Beat sheet (s27 credits) — one self.next_section per spoken sentence:
#   1 look-back   : empty two-column frame + divider appear
#   2 left column : Conformer, WavLM, HuBERT units, CTC, front-end roll in, dim
#   3 right column: WFST decode, LibriSpeech LM, Qwen2.5, QLoRA roll in
#   4 borrowed    : the whole filled ledger dims to INK_FAINT in one breath
#   5 the joins   : leaders + divider brighten while names stay dim
#   6 coda        : ledger recedes; "composition, not invention" writes with a soft glow
from manim import *
from style import *

WHITE = "#ffffff"

LEFT_COL = [
    ("Conformer encoder", "Gulati · 2020"),
    ("WavLM features", "Chen · 2022"),
    ("HuBERT units", "Hsu · 2021"),
    ("CTC training", "Graves · 2006"),
    ("TDS front-end", "Hannun · 2019"),
]
RIGHT_COL = [
    ("WFST decode · k2", "Povey et al."),
    ("LibriSpeech LM", "Panayotov · 2015"),
    ("Qwen2.5 chooser", "Qwen Team"),
    ("QLoRA fine-tuning", "Dettmers · 2023"),
]


class Credits(Scene):
    def construct(self):
        seed()

        ys = [1.55, 0.72, -0.11, -0.94, -1.77]
        Lm, Ls = -6.45, -0.55
        Rm, Rs = 0.55, 6.45

        # ============================================================== #
        #  BEAT 1 — "Look back at every piece we just used."             #
        #  Empty two-column frame + divider appear.                       #
        # ============================================================== #
        self.next_section("look-back")
        top1 = mono("BORROWED LIGHT", 26, INK_DIM, w=BOLD).move_to([0, 3.16, 0])
        top2 = mono("the methods, and where they came from", 17, INK_FAINT).move_to(
            [0, 2.64, 0])
        rule = Line([-6.4, 2.32, 0], [6.4, 2.32, 0], stroke_color=LINE, stroke_width=1.2)
        divider = Line([0, ys[-1] - 0.3, 0], [0, ys[0] + 0.3, 0],
                       stroke_color=LINE, stroke_width=1.0).set_opacity(0.5)
        self.play(FadeIn(top1, shift=DOWN * 0.14), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)
        self.play(Create(divider), run_time=0.4)
        self.wait(0.25)

        # ---- column geometry: rows hold (method, leader, source) -------
        def build_rows(spec, x_m, x_s):
            rows = VGroup()
            leaders = VGroup()
            names = VGroup()
            for (meth, src), y in zip(spec, ys):
                m = mono(meth, 15, INK_DIM).move_to([x_m, y, 0], aligned_edge=LEFT)
                s = mono(src, 12, INK_FAINT).move_to([x_s, y, 0], aligned_edge=RIGHT)
                leader = DashedLine(
                    [m.get_right()[0] + 0.18, y, 0], [s.get_left()[0] - 0.18, y, 0],
                    stroke_color=INK_GHOST, stroke_width=1.0, dash_length=0.06)
                rows.add(VGroup(m, leader, s))
                leaders.add(leader)
                names.add(m, s)
            return rows, leaders, names

        left_rows, left_leaders, left_names = build_rows(LEFT_COL, Lm, Ls)
        right_rows, right_leaders, right_names = build_rows(RIGHT_COL, Rm, Rs)

        # ============================================================== #
        #  BEAT 2 — "The Conformer, WavLM, the HuBERT units, the CTC      #
        #  training — each one came from someone else's published work."  #
        #  Left column rolls in row by row, then settles dim.            #
        # ============================================================== #
        self.next_section("left-column")
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.10) for m in left_rows],
                              lag_ratio=0.22), run_time=2.0)
        # momentarily brighten the four named methods, then settle dim
        self.play(*[m.animate.set_color(INK) for m in left_names[::2]], run_time=0.7)
        self.play(*[m.animate.set_color(INK_DIM) for m in left_names[::2]], run_time=0.7)
        self.wait(0.4)

        # ============================================================== #
        #  BEAT 3 — "So did the decoder, the language model, Qwen, QLoRA."#
        #  Right column rolls in.                                         #
        # ============================================================== #
        self.next_section("right-column")
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.10) for m in right_rows],
                              lag_ratio=0.22), run_time=1.7)
        self.wait(0.5)

        all_names = VGroup(left_names, right_names)
        all_leaders = VGroup(left_leaders, right_leaders)

        # ============================================================== #
        #  BEAT 4 — "We invented none of them."                          #
        #  The whole filled ledger dims to INK_FAINT in one breath.      #
        # ============================================================== #
        self.next_section("borrowed")
        self.play(all_names.animate.set_color(INK_FAINT), run_time=0.7)
        self.wait(0.3)

        # ============================================================== #
        #  BEAT 5 — "What we did was choose them, and fit them together." #
        #  The joins (leaders + divider) brighten; names stay dim.        #
        # ============================================================== #
        self.next_section("the-joins")
        self.play(
            all_leaders.animate.set_stroke(color=INK, width=1.6),
            divider.animate.set_stroke(color=INK_DIM, width=1.4).set_opacity(1.0),
            run_time=1.1)
        self.wait(0.6)

        # ============================================================== #
        #  BEAT 6 — "This is composition, not invention."                #
        #  Ledger recedes; the white serif closing line writes in.       #
        # ============================================================== #
        self.next_section("coda")
        ledger = VGroup(left_rows, right_rows, divider, top1, top2, rule)
        closing = serif("composition, not invention", 30, WHITE).move_to([0, 0.25, 0])
        closing_g = glow(closing)
        self.play(ledger.animate.set_opacity(0.10), run_time=0.5)
        self.add(closing_g)
        self.play(Write(closing), run_time=0.7)
        # A quiet homage: the animation style itself is borrowed too.
        homage = mono("animation in the spirit of 3Blue1Brown", 16, INK_FAINT)
        homage.next_to(closing, DOWN, buff=0.55)
        self.play(FadeIn(homage, shift=UP * 0.08), run_time=0.5)
        self.wait(0.7)


if __name__ == "__main__":
    pass
