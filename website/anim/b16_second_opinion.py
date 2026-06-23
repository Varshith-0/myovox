# website/anim/b16_second_opinion.py — B16 "Ask twice" (ensembling intuition)
#
# THE IDEA: averaging two readers that fail DIFFERENTLY cancels their errors,
# while the truth they share survives. The tougher twin (from twin-warmstart)
# was trained to be different on PURPOSE — different mistakes are the asset.
# Two identical experts add nothing. The ensemble drops WER 26 -> ~20 by decode
# DIVERSITY, not by being a stronger single model.
#
# Three-zone full-canvas composition (pose -> build -> transform -> NAME):
#   TOP   (y ~ +2.6..+3.6)  CONTEXT: "the warm-start reader  +  its tougher twin"
#                  two reader chips carried over from twin-warmstart, + live WER.
#   CENTER(-2.4..+2.2)      MECHANISM: a faint dashed TRUTH line; reader A and
#                  reader B wobble around it with errors in DIFFERENT spots
#                  (A overshoots where B undershoots). A point-by-point AVERAGE
#                  curve is drawn — the opposite-sign wobble cancels toward truth.
#                  Then the counter-example: two IDENTICAL curves average to no
#                  improvement (struck with a Cross in INK).
#   BOTTOM(-3.6..-2.7)      TAKEAWAY: live WER counter falls 26 -> ~20 as the
#                  average forms; resolves to the named payoff.
#   final          a balanced poster holds ~0.6 s.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# ---- canvas zones ---------------------------------------------------------
TOP_Y = 3.18
CENTER_Y = -0.1
BOT_Y = -3.05
PLOT_X_L = -5.4
PLOT_X_R = 5.4
PLOT_HALF_H = 1.55          # vertical reach of the wobbles around truth


def wobble(xs, amps, phases, freqs):
    """A smooth deterministic wobble = sum of a few sines (an 'error pattern')."""
    y = np.zeros_like(xs)
    for a, p, f in zip(amps, phases, freqs):
        y = y + a * np.sin(f * xs + p)
    return y


def curve_from(xs, ys, c=INK, w=2.4, op=1.0):
    """A smooth open polyline through (x, y) samples, mapped into the plot band.
    fill_opacity=0 is essential — a crossing smooth VMobject will fill solid
    white lobes otherwise."""
    pts = [np.array([x, CENTER_Y + y, 0]) for x, y in zip(xs, ys)]
    m = VMobject(stroke_color=c, stroke_width=w, fill_opacity=0)
    m.set_points_smoothly(pts)
    m.set_stroke(opacity=op)
    m.set_fill(opacity=0)
    return m


class SecondOpinion(Scene):
    def construct(self):
        seed()

        # sampled x positions across the plot band
        xs = np.linspace(PLOT_X_L, PLOT_X_R, 220)

        # =================================================================
        # B0 — CONTEXT: carry the two readers over from twin-warmstart,
        #      and a live WER readout that will fall as we average.
        # =================================================================
        self.next_section("context")

        title = mono("two readers that fail differently", 24, INK_DIM).move_to([0, TOP_Y, 0])

        def reader_chip(label, op=1.0):
            box = RoundedRectangle(width=1.95, height=0.62, corner_radius=0.1,
                                   stroke_color=INK_FAINT, stroke_width=1.6,
                                   fill_color=BG, fill_opacity=1.0)
            txt = mono(label, 17, INK).move_to(box)
            return VGroup(box, txt).set_opacity(op)

        chipA = reader_chip("reader A")
        chipB = reader_chip("twin B")
        chip_lblA = mono("warm-start", 13, INK_FAINT)
        chip_lblB = mono("tougher · augmented", 13, INK_FAINT)
        chipA.move_to([-3.1, TOP_Y - 0.62, 0])
        chipB.move_to([3.1, TOP_Y - 0.62, 0])
        chip_lblA.next_to(chipA, DOWN, buff=0.1)
        chip_lblB.next_to(chipB, DOWN, buff=0.1)

        # live WER readout, parked top-centre between the two chips
        wer = ValueTracker(26.0)
        wer_read = counter(wer, fmt=lambda v: f"{v:.0f}", s=40, c=INK, at=[0, TOP_Y - 0.55, 0])
        wer_tag = mono("WER %", 13, INK_DIM)
        wer_tag.add_updater(lambda m: m.next_to(wer_read, DOWN, buff=0.08))

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.4)
        self.play(
            FadeIn(chipA, shift=RIGHT * 0.12), FadeIn(chipB, shift=LEFT * 0.12),
            FadeIn(chip_lblA), FadeIn(chip_lblB),
            run_time=0.5,
        )
        self.add(wer_read, wer_tag)
        self.play(FadeIn(wer_read), run_time=0.34)

        # =================================================================
        # B1 — POSE: the hidden TRUTH line both readers aim at.
        # =================================================================
        self.next_section("truth")

        truth_y = 0.18 * np.sin(0.55 * xs + 0.4)          # gently undulating truth
        truth_curve = DashedVMobject(
            curve_from(xs, truth_y, c=INK_DIM, w=2.0, op=0.7),
            num_dashes=46, dashed_ratio=0.55,
        )
        truth_lbl = mono("the truth (what was really said)", 15, INK_FAINT)
        truth_lbl.move_to([PLOT_X_L + 2.4, CENTER_Y + 1.15, 0])

        self.play(Create(truth_curve), run_time=0.7)
        self.play(FadeIn(truth_lbl, shift=DOWN * 0.08), run_time=0.32)

        # =================================================================
        # B2 — BUILD: reader A and reader B wobble around truth in
        #      DIFFERENT places. A overshoots where B undershoots.
        # =================================================================
        self.next_section("two_readers")

        errA = wobble(xs, amps=[0.62, 0.30], phases=[0.0, 1.7], freqs=[0.9, 2.1])
        # B is the NEGATIVE-correlated partner: opposite-sign error in most spots
        errB = wobble(xs, amps=[0.60, 0.28], phases=[PI, 1.7 + PI], freqs=[0.9, 2.1])

        ysA = truth_y + errA
        ysB = truth_y + errB

        curveA = curve_from(xs, ysA, c=INK, w=2.4, op=0.62)
        curveB = curve_from(xs, ysB, c=INK, w=2.4, op=0.62)
        labA = mono("A", 20, INK).move_to([PLOT_X_L - 0.0, CENTER_Y + ysA[0], 0])
        labA.next_to([PLOT_X_L, CENTER_Y + ysA[0], 0], LEFT, buff=0.12)
        labB = mono("B", 20, INK).next_to([PLOT_X_L, CENTER_Y + ysB[0], 0], LEFT, buff=0.12)
        # keep the A/B tags from stacking on top of each other at the left edge
        if abs(labA.get_y() - labB.get_y()) < 0.42:
            labA.shift(UP * 0.24)
            labB.shift(DOWN * 0.24)

        self.play(Create(curveA), FadeIn(labA), run_time=0.85)
        self.play(Create(curveB), FadeIn(labB), run_time=0.85)

        # Highlight ONE spot where A overshoots (above truth) and B undershoots
        # (below truth): opposite-sign errors. Encode sign by POSITION + ticks,
        # never colour.
        # pick an x index where errA is clearly positive and errB clearly negative
        gap = errA - errB
        hi = int(np.argmax(gap))
        hx = xs[hi]
        pA = np.array([hx, CENTER_Y + ysA[hi], 0])
        pB = np.array([hx, CENTER_Y + ysB[hi], 0])
        pT = np.array([hx, CENTER_Y + truth_y[hi], 0])

        dotA = Dot(pA, radius=0.06, color=INK)
        dotB = Dot(pB, radius=0.06, color=INK)
        tickup = Triangle(stroke_width=0, fill_color=INK, fill_opacity=0.95).scale(0.08)
        tickup.next_to(dotA, UP, buff=0.06)
        tickdn = Triangle(stroke_width=0, fill_color=INK, fill_opacity=0.95).scale(0.08).rotate(PI)
        tickdn.next_to(dotB, DOWN, buff=0.06)
        # thin connectors from each dot down/up to the truth line
        connA = DashedLine(pA, pT, stroke_color=INK_GHOST, stroke_width=1.4, dash_length=0.06)
        connB = DashedLine(pB, pT, stroke_color=INK_GHOST, stroke_width=1.4, dash_length=0.06)
        spot_lbl = mono("A too high · B too low", 14, INK_DIM)
        spot_lbl.next_to(VGroup(dotA, dotB), RIGHT, buff=0.22)
        if spot_lbl.get_right()[0] > PLOT_X_R + 0.6:
            spot_lbl.next_to(VGroup(dotA, dotB), LEFT, buff=0.22)

        self.play(
            FadeIn(dotA, scale=0.5), FadeIn(dotB, scale=0.5),
            Create(connA), Create(connB),
            FadeIn(tickup, shift=UP * 0.06), FadeIn(tickdn, shift=DOWN * 0.06),
            run_time=0.5,
        )
        self.play(FadeIn(spot_lbl, shift=UP * 0.06), run_time=0.34)

        # =================================================================
        # B3 — TRANSFORM: the point-by-point AVERAGE hugs the truth line as
        #      opposite-sign wobble cancels. WER falls 26 -> ~20.
        # =================================================================
        self.next_section("average")

        ysAvg = (ysA + ysB) / 2.0
        avg_curve = curve_from(xs, ysAvg, c=WHITE, w=3.2, op=1.0)

        # the averaged point at the highlighted spot lands near truth
        pAvg = np.array([hx, CENTER_Y + ysAvg[hi], 0])
        dotAvg = Dot(pAvg, radius=0.07, color=WHITE)

        avg_lbl = mono("average of A and B", 17, INK).move_to([PLOT_X_L + 2.1, CENTER_Y - 1.2, 0])

        # dim the two reader curves so the average reads as the answer
        self.play(
            curveA.animate.set_stroke(opacity=0.30),
            curveB.animate.set_stroke(opacity=0.30),
            FadeOut(spot_lbl),
            run_time=0.4,
        )
        # draw the average; in lockstep the highlighted dots collapse toward truth
        self.play(
            Create(avg_curve),
            ReplacementTransform(VGroup(dotA.copy(), dotB.copy()), dotAvg),
            wer.animate.set_value(20.0),
            FadeIn(avg_lbl, shift=UP * 0.08),
            run_time=1.0,
        )
        # a small pull: the leftover ticks fade as the cancellation completes
        self.play(
            FadeOut(tickup), FadeOut(tickdn),
            FadeOut(connA), FadeOut(connB),
            FadeOut(dotA), FadeOut(dotB),
            Indicate(avg_curve, scale_factor=1.02, color=WHITE),
            run_time=0.55,
        )
        cancel_note = mono("opposite errors cancel · shared truth survives", 14, INK_FAINT)
        cancel_note.move_to([0, CENTER_Y - 1.95, 0])
        self.play(FadeIn(cancel_note, shift=UP * 0.06), run_time=0.4)
        self.wait(0.5)

        # =================================================================
        # B4 — COUNTER-EXAMPLE: two IDENTICAL readers average to no gain.
        #      A compact inset to the lower-right, struck with a Cross in INK.
        # =================================================================
        self.next_section("identical")

        # stash the main scene, slide it left a touch to make room for the inset
        main_plot = VGroup(truth_curve, curveA, curveB, avg_curve,
                           dotAvg, truth_lbl, labA, labB, avg_lbl, cancel_note)

        inset_w, inset_h = 3.4, 1.7
        inset_c = np.array([3.55, CENTER_Y - 0.05, 0])
        inset_box = RoundedRectangle(width=inset_w, height=inset_h, corner_radius=0.1,
                                     stroke_color=INK_GHOST, stroke_width=1.4,
                                     fill_color=BG, fill_opacity=1.0).move_to(inset_c)
        inset_cap = mono("two identical readers", 13, INK_FAINT)
        inset_cap.next_to(inset_box, UP, buff=0.12)

        # local x within the inset
        ix = np.linspace(inset_c[0] - inset_w / 2 + 0.22, inset_c[0] + inset_w / 2 - 0.22, 80)
        iwob = 0.34 * np.sin(2.2 * (ix - inset_c[0]) + 0.3)
        idtruth = DashedVMobject(
            VMobject(stroke_color=INK_DIM, stroke_width=1.4, stroke_opacity=0.6, fill_opacity=0)
            .set_points_smoothly([np.array([x, inset_c[1], 0]) for x in ix]),
            num_dashes=20, dashed_ratio=0.5,
        )
        # two IDENTICAL wobbly curves (same error) -> their average is the same
        idc1 = VMobject(stroke_color=INK, stroke_width=2.0, stroke_opacity=0.7, fill_opacity=0) \
            .set_points_smoothly([np.array([x, inset_c[1] + y, 0]) for x, y in zip(ix, iwob)])
        idc2 = VMobject(stroke_color=INK, stroke_width=2.0, stroke_opacity=0.7, fill_opacity=0) \
            .set_points_smoothly([np.array([x, inset_c[1] + y, 0]) for x, y in zip(ix, iwob)])

        # fade the main plot back so the inset reads, but keep it visible (dim).
        # NOTE: never set_opacity() on the group — that would re-enable the
        # curves' fill and bring back the white lobes. Dim STROKE only.
        wer_tag.clear_updaters()
        self.play(
            main_plot.animate.shift(LEFT * 1.7),
            truth_curve.animate.set_stroke(opacity=0.22),
            avg_curve.animate.set_stroke(opacity=0.5),
            dotAvg.animate.set_opacity(0.5),
            truth_lbl.animate.set_opacity(0.3),
            labA.animate.set_opacity(0.3), labB.animate.set_opacity(0.3),
            avg_lbl.animate.set_opacity(0.3), cancel_note.animate.set_opacity(0.3),
            FadeOut(wer_tag), run_time=0.5,
        )

        self.play(FadeIn(inset_box), FadeIn(inset_cap),
                  Create(idtruth), run_time=0.45)
        self.play(Create(idc1), run_time=0.4)
        self.play(Create(idc2), run_time=0.4)
        # the "average" is identical -> error unchanged; strike it through
        cross = Cross(inset_box, stroke_color=INK, stroke_width=3.0).scale(0.78)
        no_gain = mono("same mistakes → no gain", 13, INK_DIM)
        no_gain.next_to(inset_box, DOWN, buff=0.12)
        self.play(Create(cross), FadeIn(no_gain, shift=UP * 0.05), run_time=0.5)
        self.wait(0.35)

        # restore the main plot to full presence (the winning idea) — stroke only,
        # so the curves' fill stays 0 and the white lobes never return.
        self.play(
            truth_curve.animate.set_stroke(opacity=0.7),
            avg_curve.animate.set_stroke(opacity=1.0),
            dotAvg.animate.set_opacity(1.0),
            truth_lbl.animate.set_opacity(1.0),
            labA.animate.set_opacity(1.0), labB.animate.set_opacity(1.0),
            avg_lbl.animate.set_opacity(1.0), cancel_note.animate.set_opacity(0.7),
            run_time=0.4,
        )
        # reader curves stay dim — the average is the answer now.
        curveA.set_stroke(opacity=0.30)
        curveB.set_stroke(opacity=0.30)

        # =================================================================
        # B5 — NAME IT + POSTER HOLD.
        # =================================================================
        self.next_section("name")

        wer.clear_updaters()
        wer_read.clear_updaters()

        payoff = serif("mistakes cancel", 50, WHITE).move_to([0, BOT_Y + 0.32, 0])
        payoff_g = glow(payoff)
        sub = mono("the twin's value is being different, not being better", 16, INK_DIM)
        sub.next_to(payoff, DOWN, buff=0.16)

        self.add(payoff_g)
        self.play(
            FadeIn(payoff, shift=UP * 0.1),
            Flash([0, BOT_Y + 0.32, 0], color=WHITE, line_length=0.18, num_lines=14,
                  flash_radius=1.4, time_width=0.4),
            run_time=0.55,
        )
        self.play(FadeIn(sub, shift=UP * 0.06), run_time=0.4)

        self.wait(0.7)


if __name__ == "__main__":
    pass
