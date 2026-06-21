# S27 — Borrowed light (where the novel methods came from, and who to credit)
# We invented none of the building blocks — we composed them. A clean two-column
# credit ledger, film-credits style: method on the left, the work it came from on
# the right, joined by a faint dotted leader. A light sweeps down each column as
# the names settle.
#
# ART DIRECTION — strict monochrome; the single pure-#fff accent is the closing
# line "composition, not invention".
#   TOP strip   (y ~ +3.0): cap "BORROWED LIGHT" + "the methods, and where they came from"
#   CENTER      : two columns of credits (method —⋯— source)
#   BOTTOM strip(y ~ -3.2): the closing line
from manim import *
from emg_style import *

WHITE = "#ffffff"

LEFT_COL = [
    ("Conformer encoder", "Gulati · 2020"),
    ("WavLM features", "Chen · 2022"),
    ("HuBERT units", "Hsu · 2021"),
    ("CTC alignment", "Graves · 2006"),
    ("TDS front-end", "Hannun · 2019"),
]
RIGHT_COL = [
    ("voice distill + rerank", "Benster · 2024"),
    ("WFST decode · k2/icefall", "Povey et al."),
    ("LibriSpeech LM", "Panayotov · 2015"),
    ("Qwen2.5-7B chooser", "Qwen Team"),
    ("QLoRA fine-tuning", "Dettmers · 2023"),
]


class Credits(Scene):
    def construct(self):
        seed()

        self.next_section("cap")
        top1 = mono("BORROWED LIGHT", 26, INK_DIM, w=BOLD).move_to([0, 3.16, 0])
        top2 = mono("the methods, and where they came from", 17, INK_FAINT).move_to([0, 2.64, 0])
        rule = Line([-6.4, 2.32, 0], [6.4, 2.32, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.14), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.32)

        # ---- column geometry -------------------------------------------
        ys = [1.55, 0.72, -0.11, -0.94, -1.77]
        # left column: method left edge .. source right edge
        Lm, Ls = -6.45, -0.55
        Rm, Rs = 0.55, 6.45

        def build_rows(spec, x_m, x_s):
            rows = VGroup()
            for (meth, src), y in zip(spec, ys):
                m = mono(meth, 15, INK).move_to([x_m, y, 0], aligned_edge=LEFT)
                s = mono(src, 12, INK_FAINT).move_to([x_s, y, 0], aligned_edge=RIGHT)
                leader = DashedLine(
                    [m.get_right()[0] + 0.18, y, 0], [s.get_left()[0] - 0.18, y, 0],
                    stroke_color=INK_GHOST, stroke_width=1.0, dash_length=0.06)
                rows.add(VGroup(m, leader, s))
            return rows

        left_rows = build_rows(LEFT_COL, Lm, Ls)
        right_rows = build_rows(RIGHT_COL, Rm, Rs)

        # a faint divider between the columns
        divider = Line([0, ys[-1] - 0.3, 0], [0, ys[0] + 0.3, 0],
                       stroke_color=LINE, stroke_width=1.0).set_opacity(0.5)
        self.play(Create(divider), run_time=0.3)

        # ---- credits roll in, column by column, with a light sweep ------
        self.next_section("roll")
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.10) for m in left_rows],
                              lag_ratio=0.16), run_time=1.1)
        sweepL = Line([Lm - 0.1, ys[0] + 0.35, 0], [Ls + 0.1, ys[0] + 0.35, 0],
                      stroke_color=WHITE, stroke_width=2.0).set_opacity(0.0)
        self.add(sweepL)
        self.play(sweepL.animate.move_to([(Lm + Ls) / 2, ys[-1] - 0.30, 0]).set_opacity(0.18),
                  run_time=0.55)
        self.remove(sweepL)

        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.10) for m in right_rows],
                              lag_ratio=0.16), run_time=1.1)
        sweepR = Line([Rm - 0.1, ys[0] + 0.35, 0], [Rs + 0.1, ys[0] + 0.35, 0],
                      stroke_color=WHITE, stroke_width=2.0).set_opacity(0.0)
        self.add(sweepR)
        self.play(sweepR.animate.move_to([(Rm + Rs) / 2, ys[-1] - 0.30, 0]).set_opacity(0.18),
                  run_time=0.55)
        self.remove(sweepR)

        # ---- BOTTOM line — the single white accent ----------------------
        self.next_section("closing")
        closing = serif("composition, not invention", 26, WHITE).move_to([0, -2.92, 0])
        closing_g = glow(closing)
        self.add(closing_g)
        self.play(Write(closing), run_time=0.55)
        self.play(Flash(closing.get_center(), color=WHITE, line_length=0.16, num_lines=14,
                        flash_radius=2.0, time_width=0.5), run_time=0.45)
        self.wait(0.6)


if __name__ == "__main__":
    pass
