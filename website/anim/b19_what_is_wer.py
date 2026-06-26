# website/anim/b19_what_is_wer.py — B19 "Counting the misses" (word error rate)
#
# We keep quoting "percent wrong." This scene makes that yardstick concrete by
# grading a dictation, monochrome red-pen style. Nine beats, one per sentence:
#   1 puzzle    top cap "HOW WE COUNT THE MISSES" + subtitle + rule (rest empty)
#   2 line up    truth row, then guess row beneath, snapped by faint column guides
#   3 count      read-head at left edge + empty edit tally (swap/add/drop = 0)
#   4 swap       head on "ate"; ink cross + S tag; swap 0 -> 1
#   5 extra      head on "a";   box + I tag + ghost gap above; add 0 -> 1
#   6 missing    head on the gap; dashed slot + D tag; drop 0 -> 1; head exits
#   7 fraction   counts fly into 1+1+1 over 8 true words; readout sweeps to 37.5%
#   8 lower      numerator drops to 1+1; readout falls to 25%; "lower is the goal"
#   9 NAME       serif #fff "word error rate" with one flash; everything else dims
from manim import *
from emg_style import *

WHITE = "#ffffff"


def word_chip(t, s=22, c=INK):
    """A word as a mono Text — the unit we line up and count."""
    return mono(t, s, c)


def cross_mark(m, w=2.6):
    """An INK cross over a mobject — the monochrome 'red pen'."""
    return Cross(m, stroke_color=INK, stroke_width=w).scale(0.62)


class WhatIsWer(Scene):
    def construct(self):
        seed()

        # geometry shared across beats -------------------------------------
        truth_words = ["the", "quick", "brown", "fox", "jumps", "the", "lazy", "dog"]
        # aligned columns; the insertion column has no truth word above it.
        guess_cols = [
            ("the", None), ("quick", None), ("brown", None), ("fox", None),
            ("ate", "S"),   # substitution of "jumps"
            ("a", "I"),     # inserted word (nothing above it)
            (None, "D"),    # "the" deleted (gap in guess)
            ("lazy", None), ("dog", None),
        ]
        truth_for_col = ["the", "quick", "brown", "fox", "jumps", None,
                         "the", "lazy", "dog"]
        COL_W = 1.42
        n_cols = len(guess_cols)
        x0 = -(n_cols - 1) / 2 * COL_W
        TRUTH_Y = 1.55
        GUESS_Y = 0.05
        MID_Y = (TRUTH_Y + GUESS_Y) / 2

        def col_x(i):
            return x0 + i * COL_W

        # =================================================================
        # BEAT 1 — PUZZLE (~2.51s): just the framing; center + bottom empty.
        # =================================================================
        self.next_section("puzzle")

        cap = mono("HOW WE COUNT THE MISSES", 24, INK_DIM, w=BOLD).move_to([0, 3.32, 0])
        sub = mono("wrong measured how?", 17, INK_FAINT).move_to([0, 2.84, 0])
        rule = Line([-6.3, 2.52, 0], [6.3, 2.52, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(cap, shift=DOWN * 0.12), run_time=0.6)
        self.play(FadeIn(sub), Create(rule), run_time=0.6)
        self.wait(1.2)

        # =================================================================
        # BEAT 2 — LINE UP (~2.57s): truth row, then guess row, column guides.
        # =================================================================
        self.next_section("line_up")

        truth_lab = mono("truth", 14, INK_FAINT).move_to([x0 - COL_W * 0.62, TRUTH_Y, 0])
        guess_lab = mono("guess", 14, INK_FAINT).move_to([x0 - COL_W * 0.62, GUESS_Y, 0])

        truth_chips = VGroup()
        for i, w in enumerate(truth_for_col):
            if w is None:
                truth_chips.add(VGroup())  # placeholder for inserted column
            else:
                truth_chips.add(word_chip(w, 22, INK).move_to([col_x(i), TRUTH_Y, 0]))

        guess_chips = VGroup()
        for i, (w, _) in enumerate(guess_cols):
            if w is None:
                guess_chips.add(VGroup())  # placeholder for deleted column
            else:
                guess_chips.add(word_chip(w, 22, INK).move_to([col_x(i), GUESS_Y, 0]))

        truth_real = VGroup(*[c for c in truth_chips if len(c)])
        guess_real = VGroup(*[c for c in guess_chips if len(c)])
        self.play(FadeIn(truth_lab, shift=RIGHT * 0.06),
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.05) for c in truth_real],
                              lag_ratio=0.08), run_time=0.8)
        self.play(FadeIn(guess_lab, shift=RIGHT * 0.06),
                  LaggedStart(*[FadeIn(c, shift=UP * 0.05) for c in guess_real],
                              lag_ratio=0.08), run_time=0.8)

        guides = VGroup(*[
            Line([col_x(i), TRUTH_Y + 0.34, 0], [col_x(i), GUESS_Y - 0.34, 0],
                 stroke_color=INK_GHOST, stroke_width=1.0)
            for i in range(n_cols)
        ])
        self.play(LaggedStart(*[Create(g) for g in guides], lag_ratio=0.04),
                  run_time=0.6)
        self.wait(0.3)

        # =================================================================
        # BEAT 3 — COUNT (~0.91s): read-head at left + empty edit tally.
        # =================================================================
        self.next_section("count")

        EDIT_Y = -2.55
        tally_lab = mono("count the fixes", 16, INK_FAINT).move_to([-4.4, -1.55, 0])
        s_slot = mono("swap  0", 18, INK_DIM).move_to([-4.4, EDIT_Y + 0.62, 0])
        i_slot = mono("drop  0", 18, INK_DIM).move_to([-4.4, EDIT_Y + 0.10, 0])
        d_slot = mono("add   0", 18, INK_DIM).move_to([-4.4, EDIT_Y - 0.42, 0])

        head = Rectangle(width=COL_W * 0.92, height=2.0, stroke_color=INK_FAINT,
                         stroke_width=1.6, fill_opacity=0).move_to([col_x(0), MID_Y, 0])
        self.play(FadeIn(head),
                  FadeIn(tally_lab), FadeIn(s_slot), FadeIn(i_slot), FadeIn(d_slot),
                  run_time=0.7)
        self.wait(0.2)

        # rows dim while the head is parked, so each mark + tick is the lone change.
        rows_all = VGroup(truth_real, guess_real, truth_lab, guess_lab, guides)

        # =================================================================
        # BEAT 4 — SWAP (~1.06s): head on "ate"; cross + S tag; swap 0 -> 1.
        # =================================================================
        self.next_section("swap")

        self.play(head.animate.move_to([col_x(4), MID_Y, 0]),
                  rows_all.animate.set_opacity(0.45), run_time=0.4)
        sub_cross = cross_mark(guess_chips[4])
        s_tag = mono("S", 16, INK).next_to(guess_chips[4], DOWN, buff=0.46)
        new_s = mono("swap  1", 18, INK).move_to(s_slot)
        self.play(Create(sub_cross), FadeIn(s_tag, shift=UP * 0.06),
                  Transform(s_slot, new_s), run_time=0.66)

        # =================================================================
        # BEAT 5 — EXTRA (~1.12s): head on "a"; box + I tag + ghost gap; add 0 -> 1.
        # =================================================================
        self.next_section("extra")

        self.play(head.animate.move_to([col_x(5), MID_Y, 0]), run_time=0.4)
        ins_gap = Line([col_x(5) - 0.3, TRUTH_Y, 0], [col_x(5) + 0.3, TRUTH_Y, 0],
                       stroke_color=INK_GHOST, stroke_width=2.0)
        ins_mark = SurroundingRectangle(guess_chips[5], color=INK, buff=0.10,
                                        stroke_width=2.0)
        i_tag = mono("I", 16, INK).next_to(guess_chips[5], DOWN, buff=0.46)
        new_i = mono("drop  1", 18, INK).move_to(i_slot)
        self.play(Create(ins_gap), Create(ins_mark), FadeIn(i_tag, shift=UP * 0.06),
                  Transform(i_slot, new_i), run_time=0.72)

        # =================================================================
        # BEAT 6 — MISSING (~1.12s): head on the gap; dashed slot + D tag; drop -> 1.
        # =================================================================
        self.next_section("missing")

        self.play(head.animate.move_to([col_x(6), MID_Y, 0]), run_time=0.4)
        del_dash = DashedLine([col_x(6) - 0.34, GUESS_Y, 0],
                              [col_x(6) + 0.34, GUESS_Y, 0],
                              stroke_color=INK, stroke_width=2.0, dash_length=0.08)
        truth_emph = SurroundingRectangle(truth_chips[6], color=INK_FAINT, buff=0.10,
                                          stroke_width=1.6)
        d_tag = mono("D", 16, INK).next_to([col_x(6), GUESS_Y, 0], DOWN, buff=0.32)
        new_d = mono("add   1", 18, INK).move_to(d_slot)
        self.play(Create(del_dash), Create(truth_emph), FadeIn(d_tag, shift=UP * 0.06),
                  Transform(d_slot, new_d), run_time=0.55)
        self.play(head.animate.move_to([col_x(n_cols - 1) + 0.2, MID_Y, 0])
                  .set_opacity(0.0), run_time=0.3)

        # =================================================================
        # BEAT 7 — FRACTION (~2.44s): counts fly up; 1+1+1 / 8 -> 37% wrong.
        # =================================================================
        self.next_section("fraction")

        # re-brighten the graded rows now that we leave the per-column marking.
        self.play(rows_all.animate.set_opacity(0.7), run_time=0.3)

        FRAC_X = 4.2
        num_line = mono("1 + 1 + 1", 24, INK).move_to([FRAC_X, -1.92, 0])
        bar = Line([FRAC_X - 1.35, -2.4, 0], [FRAC_X + 1.35, -2.4, 0],
                   stroke_color=INK, stroke_width=2.2)
        den_line = mono("8 true words", 19, INK_DIM).move_to([FRAC_X, -2.84, 0])

        s_copy, i_copy, d_copy = s_slot.copy(), i_slot.copy(), d_slot.copy()
        self.add(s_copy, i_copy, d_copy)
        self.play(
            s_copy.animate.move_to(num_line).set_opacity(0.0),
            i_copy.animate.move_to(num_line).set_opacity(0.0),
            d_copy.animate.move_to(num_line).set_opacity(0.0),
            FadeIn(num_line, scale=1.1),
            run_time=0.8,
        )
        self.remove(s_copy, i_copy, d_copy)
        self.play(Create(bar), FadeIn(den_line, shift=UP * 0.06), run_time=0.5)

        eq = mono("=", 24, INK).move_to([FRAC_X - 2.05, -2.4, 0])
        wrong = ValueTracker(0.0)
        PCT_X = [FRAC_X - 3.45, -2.4, 0]
        pct = counter(wrong, fmt=lambda v: f"{v:.1f}%", s=42, c=INK, at=PCT_X)
        pct_tag = mono("wrong", 14, INK_FAINT).move_to([PCT_X[0], PCT_X[1] - 0.6, 0])
        self.add(pct)
        self.play(FadeIn(eq), FadeIn(pct_tag),
                  wrong.animate.set_value(100 * 3 / 8), run_time=0.84)
        wrong.set_value(100 * 3 / 8)

        # =================================================================
        # BEAT 8 — LOWER (~2.0s): numerator drops to 1+1; readout falls to 25%.
        # =================================================================
        self.next_section("lower")

        better = mono("fix one edit  ->  a lower score  ·  lower is the goal", 16,
                      INK_FAINT).move_to([0, -3.62, 0])
        self.play(FadeIn(better, shift=UP * 0.05), run_time=0.6)
        num_drop = mono("1 + 1", 24, INK).move_to(num_line)
        self.play(Transform(num_line, num_drop),
                  wrong.animate.set_value(100 * 2 / 8), run_time=0.9)
        wrong.set_value(100 * 2 / 8)
        quarter = mono("a quarter wrong", 15, INK_DIM).move_to([FRAC_X, -3.35, 0])
        self.play(FadeIn(quarter, shift=UP * 0.05), run_time=0.5)

        # =================================================================
        # BEAT 9 — NAME (~1.54s): serif #fff payoff + flash; everything else dims.
        # =================================================================
        self.next_section("name")

        pct.clear_updaters()
        left_tally = VGroup(tally_lab, s_slot, i_slot, d_slot)
        backdrop = VGroup(rows_all, sub_cross, s_tag, ins_gap, ins_mark, i_tag,
                          del_dash, truth_emph, d_tag, num_line, bar, den_line,
                          eq, pct, pct_tag, quarter, better, sub, rule, cap)
        PAY_AT = ORIGIN
        payoff = serif("word error rate", 48, WHITE).move_to(PAY_AT)
        payoff_g = glow(payoff)
        self.play(FadeOut(left_tally, shift=DOWN * 0.1),
                  backdrop.animate.set_opacity(0.12), run_time=0.5)
        self.add(payoff_g)
        self.play(
            GrowFromCenter(payoff),
            Flash(PAY_AT, color=WHITE, line_length=0.22, num_lines=14,
                  flash_radius=1.9, time_width=0.4),
            run_time=0.7,
        )
        self.wait(0.7)


if __name__ == "__main__":
    pass
