# website/anim/b19_what_is_wer.py — B19 "Counting the misses" (word error rate)
#
# We keep quoting "percent wrong." This scene makes that yardstick concrete by
# grading a dictation, monochrome-red-pen style.
#
# Three persistent zones (pose -> build -> transform -> NAME -> poster hold):
#   TOP    (y ~ +2.6..+3.4) CONTEXT: cap "HOW WE COUNT THE MISSES" + the formula
#                  skeleton "(swap + add + drop) / true words" filling in beat by beat.
#   CENTER (y ~ -0.6..+1.8) MECHANISM: a 'truth' sentence above a 'guess' sentence,
#                  word-aligned in columns; a read-head walks the columns and marks
#                  one substitution (S), one insertion (I), one deletion (D) — Crosses
#                  and a gap in INK, no colour.
#   BOTTOM (y ~ -3.3..-1.6) TAKEAWAY: the three edit-counts gather into S+I+D over
#                  true words; a division bar resolves to an ABSTRACT toy fraction
#                  2/8 = "a quarter"; a cleaner guess scores lower to ground
#                  "lower is better"; serif #fff payoff "word error rate".
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

        # ============================================================
        #  PERSISTENT FRAME — top cap + formula skeleton
        # ============================================================
        self.next_section("frame")

        cap = mono("HOW WE COUNT THE MISSES", 24, INK_DIM, w=BOLD).move_to([0, 3.32, 0])
        sub = mono("grade the guess against the truth, like a dictation", 16,
                   INK_FAINT).move_to([0, 2.84, 0])
        rule = Line([-6.3, 2.52, 0], [6.3, 2.52, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(cap, shift=DOWN * 0.12), run_time=0.42)
        self.play(FadeIn(sub), Create(rule), run_time=0.34)

        # ============================================================
        #  CENTER — two sentences, word-aligned in columns
        # ============================================================
        # The truth and the guess differ by exactly one swap, one extra, one drop.
        #   truth:  the  quick  brown  fox  jumps  the  lazy  dog
        #   guess:  the  quick  brown  fox  ate   a    the  lazy  dog
        # Aligned per column so each kind of edit reads at a glance:
        #   col4  jumps -> ate           SUBSTITUTION
        #   col5  (—)   -> a   inserted   INSERTION
        #   col6  the   -> (gap) dropped  DELETION
        truth_words = ["the", "quick", "brown", "fox", "jumps", "the", "lazy", "dog"]
        guess_cols = [
            ("the", None),       # match
            ("quick", None),     # match
            ("brown", None),     # match
            ("fox", None),       # match
            ("ate", "S"),        # substitution of "jumps"
            ("a", "I"),          # inserted word (no truth above it)
            (None, "D"),         # "the" deleted (gap in guess)
            ("lazy", None),      # match
            ("dog", None),       # match
        ]
        # truth above each column; insertion column has no truth word above it.
        truth_for_col = ["the", "quick", "brown", "fox", "jumps", None, "the", "lazy", "dog"]

        COL_W = 1.42
        n_cols = len(guess_cols)
        x0 = -(n_cols - 1) / 2 * COL_W
        TRUTH_Y = 1.55
        GUESS_Y = 0.05

        def col_x(i):
            return x0 + i * COL_W

        truth_lab = mono("truth", 14, INK_FAINT).move_to([x0 - COL_W * 0.62, TRUTH_Y, 0])
        guess_lab = mono("guess", 14, INK_FAINT).move_to([x0 - COL_W * 0.62, GUESS_Y, 0])

        truth_chips = VGroup()
        for i, w in enumerate(truth_for_col):
            if w is None:
                truth_chips.add(VGroup())  # placeholder for the inserted column
            else:
                truth_chips.add(word_chip(w, 22, INK).move_to([col_x(i), TRUTH_Y, 0]))

        guess_chips = VGroup()
        for i, (w, _) in enumerate(guess_cols):
            if w is None:
                guess_chips.add(VGroup())  # placeholder for the deleted column
            else:
                guess_chips.add(word_chip(w, 22, INK).move_to([col_x(i), GUESS_Y, 0]))

        # bring up the truth line, then the guess line below it.
        truth_real = VGroup(*[c for c in truth_chips if len(c)])
        guess_real = VGroup(*[c for c in guess_chips if len(c)])
        self.play(FadeIn(truth_lab, shift=RIGHT * 0.06),
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.05) for c in truth_real],
                              lag_ratio=0.08), run_time=0.7)
        self.play(FadeIn(guess_lab, shift=RIGHT * 0.06),
                  LaggedStart(*[FadeIn(c, shift=UP * 0.05) for c in guess_real],
                              lag_ratio=0.08), run_time=0.7)

        # faint column guides so the alignment is unmistakable.
        guides = VGroup(*[
            Line([col_x(i), TRUTH_Y + 0.34, 0], [col_x(i), GUESS_Y - 0.34, 0],
                 stroke_color=INK_GHOST, stroke_width=1.0)
            for i in range(n_cols)
        ])
        self.play(LaggedStartMap(Create, guides, lag_ratio=0.04, run_time=0.4))

        # ============================================================
        #  CENTER — a read-head walks the columns, marking edits
        # ============================================================
        self.next_section("mark")

        # the running edit tally, parked bottom-left, fills as marks land.
        EDIT_Y = -2.55
        tally_lab = mono("edits to fix the guess", 16, INK_FAINT).move_to([-4.4, -1.55, 0])

        s_slot = mono("swap  0", 18, INK_DIM).move_to([-4.4, EDIT_Y + 0.62, 0])
        i_slot = mono("add   0", 18, INK_DIM).move_to([-4.4, EDIT_Y + 0.10, 0])
        d_slot = mono("drop  0", 18, INK_DIM).move_to([-4.4, EDIT_Y - 0.42, 0])
        self.play(FadeIn(tally_lab),
                  FadeIn(s_slot), FadeIn(i_slot), FadeIn(d_slot), run_time=0.4)

        # read-head box that travels column to column.
        head = Rectangle(width=COL_W * 0.92, height=2.0, stroke_color=INK_FAINT,
                         stroke_width=1.6, fill_opacity=0)
        head.move_to([col_x(0), (TRUTH_Y + GUESS_Y) / 2, 0])
        self.play(FadeIn(head), run_time=0.25)

        # --- column 4: SUBSTITUTION  (jumps -> ate) ---
        self.play(head.animate.move_to([col_x(4), (TRUTH_Y + GUESS_Y) / 2, 0]),
                  run_time=0.5)
        sub_cross = cross_mark(guess_chips[4])
        s_tag = mono("S", 16, INK).next_to(guess_chips[4], DOWN, buff=0.46)
        new_s = mono("swap  1", 18, INK)
        new_s.move_to(s_slot)
        self.play(Create(sub_cross), FadeIn(s_tag, shift=UP * 0.06),
                  Transform(s_slot, new_s), run_time=0.5)

        # --- column 5: INSERTION  (extra "a", nothing above it) ---
        self.play(head.animate.move_to([col_x(5), (TRUTH_Y + GUESS_Y) / 2, 0]),
                  run_time=0.5)
        # empty truth slot drawn as a small ghost gap to show "nothing was said here"
        ins_gap = Line([col_x(5) - 0.3, TRUTH_Y, 0], [col_x(5) + 0.3, TRUTH_Y, 0],
                       stroke_color=INK_GHOST, stroke_width=2.0)
        ins_mark = SurroundingRectangle(guess_chips[5], color=INK, buff=0.10,
                                        stroke_width=2.0)
        i_tag = mono("I", 16, INK).next_to(guess_chips[5], DOWN, buff=0.46)
        new_i = mono("add   1", 18, INK)
        new_i.move_to(i_slot)
        self.play(Create(ins_gap), Create(ins_mark), FadeIn(i_tag, shift=UP * 0.06),
                  Transform(i_slot, new_i), run_time=0.55)

        # --- column 6: DELETION  ("the" missing from guess) ---
        self.play(head.animate.move_to([col_x(6), (TRUTH_Y + GUESS_Y) / 2, 0]),
                  run_time=0.5)
        # gap in the guess row where the truth word has no partner.
        del_gap = SurroundingRectangle(
            Rectangle(width=0.7, height=0.4).move_to([col_x(6), GUESS_Y, 0]),
            color=INK, buff=0.0, stroke_width=2.0).set_stroke(opacity=0.9)
        del_dash = DashedLine([col_x(6) - 0.34, GUESS_Y, 0],
                              [col_x(6) + 0.34, GUESS_Y, 0],
                              stroke_color=INK, stroke_width=2.0, dash_length=0.08)
        truth_emph = SurroundingRectangle(truth_chips[6], color=INK_FAINT, buff=0.10,
                                          stroke_width=1.6)
        d_tag = mono("D", 16, INK).next_to([col_x(6), GUESS_Y, 0], DOWN, buff=0.32)
        new_d = mono("drop  1", 18, INK)
        new_d.move_to(d_slot)
        self.play(Create(del_dash), Create(truth_emph), FadeIn(d_tag, shift=UP * 0.06),
                  Transform(d_slot, new_d), run_time=0.55)

        # park the read-head at the far right; the marking pass is done.
        self.play(head.animate.move_to([col_x(n_cols - 1) + 0.2,
                                        (TRUTH_Y + GUESS_Y) / 2, 0]).set_opacity(0.0),
                  run_time=0.4)

        # ============================================================
        #  TOP — fill in the formula skeleton as the counts settle
        # ============================================================
        self.next_section("formula")

        formula = mono("(swap + add + drop)  /  true words", 18, INK_FAINT)
        formula.move_to([0, 2.18, 0])
        self.play(FadeIn(formula, shift=DOWN * 0.06), run_time=0.5)
        self.wait(0.35)

        # ============================================================
        #  BOTTOM — gather the counts into S+I+D over true words
        # ============================================================
        self.next_section("fraction")

        # right side: the live fraction.  numerator = 1+1+1 = 3 edits,
        # denominator = 8 truly-spoken words.  -> an ABSTRACT toy fraction.
        FRAC_X = 4.2
        num_line = mono("1 + 1 + 1", 24, INK).move_to([FRAC_X, -1.92, 0])
        bar = Line([FRAC_X - 1.35, -2.4, 0], [FRAC_X + 1.35, -2.4, 0],
                   stroke_color=INK, stroke_width=2.2)
        den_line = mono("8 true words", 19, INK_DIM).move_to([FRAC_X, -2.84, 0])

        # gather the three tally rows into the single numerator: each slot sends
        # a travelling copy to the numerator's resting spot, then num_line appears.
        s_copy = s_slot.copy()
        i_copy = i_slot.copy()
        d_copy = d_slot.copy()
        self.add(s_copy, i_copy, d_copy)
        self.play(
            s_copy.animate.move_to(num_line).set_opacity(0.0),
            i_copy.animate.move_to(num_line).set_opacity(0.0),
            d_copy.animate.move_to(num_line).set_opacity(0.0),
            FadeIn(num_line, scale=1.1),
            run_time=0.55,
        )
        self.remove(s_copy, i_copy, d_copy)
        self.play(Create(bar), FadeIn(den_line, shift=UP * 0.06), run_time=0.45)

        # resolve the toy fraction with a live "% wrong" readout sweeping up.
        eq = mono("=", 24, INK).move_to([FRAC_X - 2.05, -2.4, 0])
        wrong = ValueTracker(0.0)
        PCT_X = [FRAC_X - 3.45, -2.4, 0]
        pct = counter(wrong, fmt=lambda v: f"{int(round(v))}%", s=42, c=INK, at=PCT_X)
        pct_tag = mono("wrong", 14, INK_FAINT).move_to([PCT_X[0], PCT_X[1] - 0.6, 0])
        self.add(pct)
        self.play(FadeIn(eq), FadeIn(pct_tag),
                  wrong.animate.set_value(100 * 3 / 8), run_time=0.7)
        wrong.set_value(100 * 3 / 8)

        # ============================================================
        #  TRANSFORM — a cleaner guess scores lower (lower is better)
        # ============================================================
        self.next_section("lower_is_better")

        # ground "lower is better": fixing one edit drops the numerator + the %.
        better = mono("fix one edit  ->  fewer wrong  ->  a lower score", 16, INK_FAINT)
        better.move_to([0, -3.62, 0])
        self.play(FadeIn(better, shift=UP * 0.05), run_time=0.5)
        # the numerator drops 3 -> 2, the readout falls in lockstep (2/8 = a quarter).
        num_drop = mono("1 + 1", 24, INK).move_to(num_line)
        self.play(Transform(num_line, num_drop),
                  wrong.animate.set_value(100 * 2 / 8), run_time=0.8)
        wrong.set_value(100 * 2 / 8)
        quarter = mono("a quarter wrong", 15, INK_DIM).move_to([FRAC_X, -3.35, 0])
        self.play(FadeIn(quarter, shift=UP * 0.05), run_time=0.45)

        # ============================================================
        #  NAME — the single #fff payoff + poster hold
        # ============================================================
        self.next_section("name")

        pct.clear_updaters()
        # clear the left tally column so the payoff owns the cleared left-centre.
        left_tally = VGroup(tally_lab, s_slot, i_slot, d_slot)
        PAY_AT = [-3.4, -2.4, 0]
        payoff = serif("word error rate", 40, WHITE).move_to(PAY_AT)
        payoff_g = glow(payoff)
        self.play(FadeOut(left_tally, shift=DOWN * 0.1), run_time=0.4)
        self.add(payoff_g)
        self.play(
            GrowFromCenter(payoff),
            Flash(PAY_AT, color=WHITE, line_length=0.18, num_lines=12,
                  flash_radius=1.6, time_width=0.4),
            run_time=0.6,
        )

        self.wait(0.6)


if __name__ == "__main__":
    pass
