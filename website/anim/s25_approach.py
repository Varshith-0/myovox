# S25 — What we changed (how we trained, and what is different)
# The closer opens by stating — plainly, no justification — the three changes we
# made on top of the published baseline, and how the system was trained.
#   move 1  decode:   scale-1.0 decode      -> tuned open-vocab decode   (51.17 -> 40.63)
#   move 2  encoder:  causal TDS            -> bidirectional Conformer + voice distillation (40.63 -> 26.14)
#   move 3  choosing: single 1-best         -> ensemble -> n-best union -> 7B LLM rerank (26.14 -> 18.53)
# A live WER readout ticks down as each change lands; a one-line training recipe
# runs along the bottom. Strict monochrome; the single pure-#fff accent is the
# final 18.53% result.
#
# ART DIRECTION — fill the canvas, three persistent horizontal zones:
#   TOP strip   (y ~ +3.0): cap line "WHAT WE CHANGED" + "built on a published 51% baseline"
#   CENTER      (y ~ -1.9..+2.2): three before->after rows, each "old" morphing into
#                                 the bright "new"; a WER counter rides top-right.
#   BOTTOM strip(y ~ -3.1): the running training recipe, filling in beat by beat.
from manim import *
from emg_style import *

WHITE = "#ffffff"


def tri(angle, c, op=1.0, s=0.08):
    """Bare triangular arrowhead (points up at angle=0; rotate to aim)."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def flat_arrow(start, end, c=INK_FAINT, w=2.0):
    """A thin shaft + triangular head — no Arrow tip mobject (avoids tip bugs)."""
    shaft = Line(start, end, stroke_color=c, stroke_width=w)
    head = tri(shaft.get_angle() - PI / 2, c, 1.0, 0.085).move_to(shaft.get_end())
    return VGroup(shaft, head)


class Approach(Scene):
    def construct(self):
        seed()

        # ============================================================== #
        #  PERSISTENT FRAME — top cap, WER readout, bottom recipe rail    #
        # ============================================================== #
        self.next_section("frame")

        top1 = mono("WHAT WE CHANGED", 26, INK_DIM, w=BOLD).move_to([0, 3.18, 0])
        top2 = mono("three changes on top of a published 51% baseline", 17, INK_FAINT).move_to(
            [0, 2.66, 0])
        rule = Line([-6.4, 2.34, 0], [6.4, 2.34, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.14), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)

        # live WER readout — parked in the top strip, right side (clear of the rows)
        wer = ValueTracker(51.17)
        read_at = np.array([5.35, 2.62, 0])
        readout = counter(wer, fmt=lambda v: f"{v:.2f}", s=26, c=INK, at=read_at)
        read_tag = mono("WER %", 13, INK_DIM)
        read_tag.add_updater(lambda m: m.next_to(readout, LEFT, buff=0.18))
        self.add(readout, read_tag)
        self.play(FadeIn(readout), FadeIn(read_tag), run_time=0.34)

        # ---- BOTTOM recipe rail skeleton -------------------------------
        LY = -3.18
        recipe_title = mono("how we trained", 14, INK_GHOST)
        recipe_title.move_to([-6.5, LY + 0.46, 0]).align_to(LEFT * 6.5, LEFT)
        led_rule = Line([-6.6, LY + 0.66, 0], [6.6, LY + 0.66, 0],
                        stroke_color=LINE, stroke_width=1.0)
        steps_txt = ["warm-start the front-end", "train the new encoder", "distil the voice",
                     "QLoRA-finetune the chooser"]
        steps = VGroup()
        for i, t in enumerate(steps_txt):
            chip = mono(t, 14, INK_GHOST)
            steps.add(chip)
            if i < len(steps_txt) - 1:
                steps.add(mono("·", 14, INK_GHOST))
        steps.arrange(RIGHT, buff=0.28).move_to([0, LY, 0])
        self.play(FadeIn(recipe_title), Create(led_rule),
                  LaggedStartMap(FadeIn, steps, lag_ratio=0.06), run_time=0.5)

        # ============================================================== #
        #  THE THREE CHANGES — before -> after rows                       #
        # ============================================================== #
        # geometry: three rows in the centre; "old" on the left, arrow, "new" right
        ROW_Y = [1.45, 0.15, -1.15]
        OLD_X, ARR_X, NEW_X = -4.35, -1.85, 0.95
        moves = [
            dict(tag="decode", old="scale-1.0 decode", new="tuned open-vocab decode",
                 detail="recover the missing scale + blank penalty", wer=40.63,
                 recipe_hi=0),
            dict(tag="encoder", old="causal TDS", new="bidirectional Conformer + distillation",
                 detail="reads both ways · voice-distilled in training",
                 wer=26.14, recipe_hi=1),
            dict(tag="choosing", old="single 1-best", new="ensemble → n-best union → 7B rerank",
                 detail="pool the guesses, then choose with a 7B model", wer=18.53,
                 recipe_hi=3),
        ]

        all_rows = VGroup()   # every row mobject, so resolve can clear them at once
        for k, mv in enumerate(moves):
            self.next_section(f"move{k+1}")
            y = ROW_Y[k]

            # row tag on the far left, ghost-tick anchored
            rtag = mono(mv["tag"], 14, INK_FAINT).move_to([-6.35, y, 0]).align_to(LEFT * 6.35, LEFT)
            # the "old" approach — faint
            old = mono(mv["old"], 18, INK_FAINT).move_to([OLD_X, y, 0])
            self.play(FadeIn(rtag, shift=RIGHT * 0.05), FadeIn(old), run_time=0.34)

            # arrow sweeps from old toward new; the new lands bright
            arr = flat_arrow([OLD_X + 1.35, y, 0], [NEW_X - 1.55, y, 0], INK_FAINT, 2.0)
            new = mono(mv["new"], 16, INK).move_to([NEW_X, y, 0], aligned_edge=LEFT)
            detail = mono(mv["detail"], 12, INK_FAINT).next_to(new, DOWN, buff=0.12,
                                                               aligned_edge=LEFT)
            all_rows.add(rtag, old, arr, new, detail)

            pulse = Dot(arr[0].get_start(), radius=0.05, color=INK)
            self.add(pulse)
            self.play(
                Create(arr),
                pulse.animate.move_to(arr[0].get_end()),
                TransformFromCopy(old, new),
                wer.animate.set_value(mv["wer"]),
                run_time=0.66, rate_func=smooth)
            self.remove(pulse)
            self.play(FadeIn(detail, shift=UP * 0.05),
                      Indicate(steps[mv["recipe_hi"] * 2], scale_factor=1.08, color=INK_DIM),
                      run_time=0.36)
            steps[mv["recipe_hi"] * 2].set_color(INK_DIM)

        wer.set_value(18.53)
        readout.clear_updaters()
        read_tag.clear_updaters()

        # ============================================================== #
        #  RESOLVE — the final result ignites (single white accent)       #
        # ============================================================== #
        self.next_section("resolve")
        # the rows have done their job — clear them so the result owns the frame.
        final = num("18.53%", 58, WHITE).move_to([0, 0.6, 0])
        final_tag = mono("word error rate", 16, INK_DIM).next_to(final, DOWN, buff=0.16)
        final_g = glow(final)
        self.play(FadeOut(all_rows), FadeOut(readout), FadeOut(read_tag), run_time=0.45)
        self.add(final_g)
        self.play(GrowFromCenter(final), FadeIn(final_tag),
                  Flash([0, 0.6, 0], color=WHITE, line_length=0.2, num_lines=14,
                        flash_radius=1.4, time_width=0.4), run_time=0.55)
        self.play(Circumscribe(VGroup(final, final_tag), color=WHITE, stroke_width=2.0,
                               buff=0.22, time_width=0.5), run_time=0.5)

        # name the spirit of the section — quietly, no justification
        closing = serif("we didn't start from zero — we built on top", 24, INK).move_to(
            [0, -1.4, 0])
        self.play(Write(closing), run_time=0.55)
        self.wait(0.6)


if __name__ == "__main__":
    pass
