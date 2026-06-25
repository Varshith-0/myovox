# S25 — What we changed (the three changes on a published baseline)
# A calm closing recap: state — plainly, no justification — the three changes we
# made on top of the published 51% baseline, and watch the WER tick down.
#   move 1  decode:   scale-1.0 decode  -> tuned open-vocab decode               (51.17 -> 40.63)
#   move 2  encoder:  causal TDS        -> bidirectional Conformer + distillation (40.63 -> 26.14)
#   move 3  choosing: single 1-best     -> ensemble -> n-best union -> 7B rerank  (26.14 -> 18.53)
# A live WER readout ticks down as each change lands; a one-line training recipe
# sits at ghost opacity along the bottom, with only "distil the voice" brightening.
# Strict monochrome; the single pure-#fff accent is the final 18.53% result.
#
# Seven beats — one spoken sentence each:
#   1 cap + WER parks at 51.17        4 row 2 (encoder) -> 26.14, distil brightens
#   2 subtitle + rule                 5 row 3 (choosing) -> 18.53
#   3 row 1 (decode) -> 40.63         6 all three rows hold lit together
#                                     7 resolve: 18.53% ignites + closing line
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

        ROW_Y = [1.45, 0.15, -1.15]
        OLD_X, NEW_X = -4.35, 0.95
        read_at = np.array([5.35, 2.62, 0])
        LY = -3.18

        # ----- persistent frame mobjects (built up across beats 1-2) -----
        top1 = mono("WHAT WE CHANGED", 26, INK_DIM, w=BOLD).move_to([0, 3.18, 0])
        top2 = mono("three changes on a published 51% baseline", 17, INK_FAINT).move_to(
            [0, 2.66, 0])
        rule = Line([-6.4, 2.34, 0], [6.4, 2.34, 0], stroke_color=LINE, stroke_width=1.2)

        wer = ValueTracker(51.17)
        readout = counter(wer, fmt=lambda v: f"{v:.2f}", s=26, c=INK, at=read_at)
        read_tag = mono("WER %", 13, INK_DIM)
        read_tag.add_updater(lambda m: m.next_to(readout, LEFT, buff=0.18))

        # bottom recipe rail — held at ghost throughout
        recipe_title = mono("how we trained", 14, INK_GHOST).move_to([0, LY + 0.46, 0])
        recipe_title.align_to(LEFT * 6.5, LEFT)
        led_rule = Line([-6.6, LY + 0.66, 0], [6.6, LY + 0.66, 0],
                        stroke_color=LINE, stroke_width=1.0)
        steps_txt = ["warm-start the front-end", "train the new encoder", "distil the voice",
                     "QLoRA-finetune the chooser"]
        steps = VGroup()
        for i, t in enumerate(steps_txt):
            steps.add(mono(t, 14, INK_GHOST))
            if i < len(steps_txt) - 1:
                steps.add(mono("·", 14, INK_GHOST))
        steps.arrange(RIGHT, buff=0.28).move_to([0, LY, 0])

        # ============================================================== #
        #  BEAT 1 — "So what, exactly, is new here?"                       #
        #  cap fades in; WER readout parks at 51.17; rows empty.           #
        # ============================================================== #
        self.next_section("beat1")
        self.add(readout, read_tag)
        self.play(FadeIn(top1, shift=DOWN * 0.14),
                  FadeIn(readout), FadeIn(read_tag), run_time=0.5)
        self.wait(0.35)

        # ============================================================== #
        #  BEAT 2 — "We didn't start from scratch ... changed three       #
        #  things." subtitle + rule + ghost recipe rail come in.          #
        # ============================================================== #
        self.next_section("beat2")
        self.play(FadeIn(top2), Create(rule), run_time=0.45)
        self.play(FadeIn(recipe_title), Create(led_rule),
                  LaggedStart(*[FadeIn(c) for c in steps], lag_ratio=0.06), run_time=0.6)
        self.wait(1.2)

        # ============================================================== #
        #  BEATS 3-5 — the three before -> after rows                     #
        # ============================================================== #
        moves = [
            dict(beat="beat3", tag="decode", old="scale-1.0 decode",
                 new="tuned open-vocab decode", wer=40.63, distil=False),
            dict(beat="beat4", tag="encoder", old="causal TDS",
                 new="bidirectional Conformer + distillation", wer=26.14, distil=True),
            dict(beat="beat5", tag="choosing", old="single 1-best",
                 new="ensemble → n-best union → 7B rerank", wer=18.53, distil=False),
        ]
        rows = []  # one VGroup per row, so we can dim/spotlight by row
        for k, mv in enumerate(moves):
            self.next_section(mv["beat"])
            y = ROW_Y[k]

            rtag = mono(mv["tag"], 14, INK_FAINT).move_to([-6.35, y, 0])
            rtag.align_to(LEFT * 6.35, LEFT)
            old = mono(mv["old"], 18, INK_FAINT).move_to([OLD_X, y, 0])
            arr = flat_arrow([OLD_X + 1.35, y, 0], [NEW_X - 1.55, y, 0], INK_FAINT, 2.0)
            new = mono(mv["new"], 16, INK).move_to([NEW_X, y, 0], aligned_edge=LEFT)
            row = VGroup(rtag, old, arr, new)
            rows.append(row)

            # spotlight: dim every earlier row to faint
            dim_prev = [r.animate.set_opacity(0.34) for r in rows[:-1]]

            self.play(FadeIn(rtag, shift=RIGHT * 0.05), FadeIn(old),
                      *dim_prev, run_time=0.4)

            pulse = Dot(arr[0].get_start(), radius=0.05, color=INK)
            self.add(pulse)
            self.play(
                Create(arr),
                pulse.animate.move_to(arr[0].get_end()),
                TransformFromCopy(old, new),
                wer.animate.set_value(mv["wer"]),
                run_time=0.9, rate_func=smooth)
            self.remove(pulse)
            self.add(new)  # ensure the copy target persists in the row group

            if mv["distil"]:
                distil_chip = steps[2 * 2]  # "distil the voice"
                self.play(distil_chip.animate.set_color(INK_DIM),
                          Indicate(distil_chip, scale_factor=1.1, color=INK), run_time=0.4)
                distil_chip.set_color(INK_DIM)
            self.wait(0.4)

        # ============================================================== #
        #  BEAT 6 — "Three changes." all three rows hold lit together.    #
        # ============================================================== #
        self.next_section("beat6")
        self.play(*[r.animate.set_opacity(1.0) for r in rows], run_time=0.35)
        self.wait(0.4)

        # ============================================================== #
        #  BEAT 7 — "Fifty-one percent wrong, down to eighteen and a      #
        #  half." rows clear; 18.53% ignites; closing line writes.        #
        # ============================================================== #
        self.next_section("beat7")
        readout.clear_updaters()
        read_tag.clear_updaters()
        all_rows = VGroup(*rows)

        final = num("18.53%", 58, WHITE).move_to([0, 0.55, 0])
        final_tag = mono("word error rate", 16, INK_DIM).next_to(final, DOWN, buff=0.18)
        final_g = glow(final)

        self.play(FadeOut(all_rows), FadeOut(readout), FadeOut(read_tag), run_time=0.4)
        self.add(final_g)
        self.play(GrowFromCenter(final), FadeIn(final_tag),
                  Flash([0, 0.55, 0], color=WHITE, line_length=0.2, num_lines=14,
                        flash_radius=1.4, time_width=0.4), run_time=0.55)

        closing = serif("we built on top", 26, INK).move_to([0, -1.45, 0])
        self.play(Write(closing), run_time=0.5)
        self.wait(0.7)


if __name__ == "__main__":
    pass
