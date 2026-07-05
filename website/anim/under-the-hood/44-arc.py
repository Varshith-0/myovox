# website/anim/s24_arc.py  — S24 "The climb (the arc)"
# Strict monochrome. The climb is really a FALL: a full-bleed stepped descent that
# walks DOWN-and-RIGHT across the whole canvas, each tread earned by one move:
#   51.17 -> 40.63 -> 26.14 -> 18.53   (WER, bold line)
# A fainter PER track runs in parallel beneath:
#   39.02 -> 39.02 -> 22.34 -> 20.90   (PER, dashed)
# The teaching contrast: PER fell HARD on move two (the model truly HEARD better)
# but barely moved on move three (only the decoding got smarter).
#
# BEAT SHEET (one self.next_section per spoken sentence; total ~12.0s):
#   1  the whole climb, 51 wrong          — start dot + 51.17 spotlit, PER stays faint
#   2  move 1, 51 -> ~40                  — WER segment, pulse, counter, bar lights
#   3  move 2, 40 -> 26                   — steepest WER segment (PER only dotted)
#   4  move 3, 26 -> 18.5                 — final WER segment, endpoint glows
#   5  the faint line is sound error      — PER track fades up; WER dims slightly
#   6  on move two it plunges             — move-2 PER segment + single #fff accent
#   7  on move three it barely budges     — flat move-3 PER + slopes + punchline
# Strict monochrome (style inks + a single pure-#fff peak accent). No LaTeX.
#
# Ground truth (Technical report Section 1, Section 12):
#   WER 51.17 -> 40.63 -> 26.14 -> 18.53; PER 39.02 -> 22.34 -> 20.90; the EMG-only
#   full-context encoder (not the teacher) moved WER on move two; PER barely moved on
#   move three (only the word-chooser got smarter).
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

# --- data ---------------------------------------------------------------
WER = [51.17, 40.63, 26.14, 18.53]
PER = [39.02, 39.02, 22.34, 20.90]   # PER unchanged by move-1 decode fix
DROP = [WER[i] - WER[i + 1] for i in range(len(WER) - 1)]   # 10.54, 14.49, 7.61
MOVES = [
    ("move 1", "fix the decode"),
    ("move 2", "look both ways +\ncopy the teacher"),
    ("move 3", "combine readers,\npool + choose"),
]

# --- plot geometry (full-bleed: sweep most of the width & height) -------
X0, X1 = -5.4, 5.4                  # left .. right of the plot (near canvas edges)
YB, YT = -2.30, 1.85               # bottom (0%) .. top of value axis (tall)
VMAX = 56.0


def _x(i):
    return X0 + (X1 - X0) * i / (len(WER) - 1)


def _y(v):
    return YB + (YT - YB) * (v / VMAX)


def tri(angle, c, op=1.0, s=0.08):
    """A bare triangular arrowhead (no Arrow tip mobject => no tip bug)."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


class Climb(Scene):
    def construct(self):
        seed()

        pts = [np.array([_x(i), _y(WER[i]), 0]) for i in range(len(WER))]
        per_pts = [np.array([_x(i), _y(PER[i]), 0]) for i in range(len(WER))]

        # =================================================================
        # BEAT 1 (~2.01s) — "the whole climb, 51 wrong."
        # Top context strip, y-axis, the WER start dot + 51.17 spotlit.
        # PER start dot stays faint as a quiet promise of the lower track.
        # =================================================================
        self.next_section("beat1_pose")

        recap = mono("the whole climb, in one chart", 17, INK_FAINT)
        recap_b = mono("from 51% wrong", 14, INK_GHOST)
        recap_grp = VGroup(recap, recap_b).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        recap_grp.to_corner(UL, buff=0.55).shift(DOWN * 0.05)

        better = VGroup(
            tri(PI, INK_FAINT, 1.0, 0.075),
            mono("lower is better", 14, INK_FAINT),
        ).arrange(RIGHT, buff=0.14)
        better.to_corner(UR, buff=0.55).shift(DOWN * 0.05)

        top_rule = Line([-6.4, 2.42, 0], [6.4, 2.42, 0], stroke_color=LINE, stroke_width=1.2)

        base = Line([X0, _y(0), 0], [X1, _y(0), 0],
                    stroke_color=INK_GHOST, stroke_width=2)
        yaxis = Line([X0, _y(0), 0], [X0, 2.40, 0],
                     stroke_color=INK_GHOST, stroke_width=1.4).set_opacity(0.55)
        axis_lbl = mono("0% wrong", 13, INK_FAINT).next_to([X0, _y(0), 0], DOWN, buff=0.12).shift(RIGHT * 0.05)

        self.play(
            FadeIn(recap_grp, shift=RIGHT * 0.06),
            FadeIn(better, shift=LEFT * 0.06),
            Create(top_rule),
            run_time=0.5,
        )
        self.play(Create(yaxis), Create(base), FadeIn(axis_lbl), run_time=0.4)

        # bottom band: live WER counter + empty progress track
        BAR_L, BAR_R = -3.55, 3.55
        BAR_Y = -3.62
        bar_track = RoundedRectangle(width=BAR_R - BAR_L, height=0.20, corner_radius=0.05,
                                     stroke_color=INK_GHOST, stroke_width=1.6,
                                     fill_color=BG, fill_opacity=0).move_to([(BAR_L + BAR_R) / 2, BAR_Y, 0])

        wer_t = ValueTracker(WER[0])
        readout_at = np.array([0, -3.10, 0])
        readout = counter(wer_t, fmt=lambda v: f"{v:.2f}", s=40, c=INK, at=readout_at)
        read_tag = mono("WER %", 13, INK_DIM)
        read_tag.add_updater(lambda m: m.next_to(readout, RIGHT, buff=0.20).align_to(readout, DOWN))
        self.add(readout, read_tag)
        self.play(Create(bar_track), FadeIn(readout), FadeIn(read_tag), run_time=0.4)

        # WER start dot (51.17) — the single focus of beat 1
        dots = VGroup(*[Dot(p, radius=0.075, color=INK) for p in pts])
        start_lab = mono(f"{WER[0]:.2f}", 22, INK).next_to(pts[0], UP, buff=0.22).shift(RIGHT * 0.18)
        start_tag = mono("start", 13, INK_FAINT).next_to(start_lab, UP, buff=0.10)
        self.add(glow(dots[0]))
        self.play(GrowFromCenter(dots[0]),
                  FadeIn(start_lab, shift=DOWN * 0.08),
                  FadeIn(start_tag), run_time=0.5)

        # PER start dot — faint, lower; the dashed track is held for beat 5
        per_dots = VGroup(*[Dot(p, radius=0.05, color=INK_FAINT) for p in per_pts])
        per_dots[0].set_opacity(0.5)
        self.play(GrowFromCenter(per_dots[0]), run_time=0.3)
        self.wait(0.2)

        # =================================================================
        # BEATS 2-4 — THE THREE MOVES. One descending WER segment per beat:
        # caption on a ghost tick, traveling pulse, counter ticking, bar
        # segment lighting, new dot + value. The PER track is laid down ONLY
        # as dotted segments (no notes / no explanation) — that story waits.
        # =================================================================
        move_anchor_x = [_x(0.5), _x(1.5), _x(2.5)]
        total_drop = WER[0] - WER[-1]
        seg_frac = [d / total_drop for d in DROP]
        seg_x = [BAR_L]
        for f in seg_frac:
            seg_x.append(seg_x[-1] + f * (BAR_R - BAR_L))
        bar_segs = []
        per_segments = []
        move_captions = []

        for i in range(1, len(WER)):
            self.next_section(f"beat{i+1}_move{i}")
            seg = Line(pts[i - 1], pts[i], stroke_color=INK, stroke_width=4)

            # move caption on a ghost tick, hung well above the higher endpoint
            mlbl = mono(MOVES[i - 1][0], 15, INK_DIM, w=BOLD)
            mtxt = mono(MOVES[i - 1][1], 14, INK_DIM).set_opacity(0.82)
            mgrp = VGroup(mlbl, mtxt).arrange(DOWN, buff=0.07)
            top_y = max(pts[i - 1][1], pts[i][1])
            mgrp.move_to([move_anchor_x[i - 1], top_y + 1.05, 0])
            move_captions.append(mgrp)
            tick = Line([move_anchor_x[i - 1], mgrp.get_bottom()[1] - 0.04, 0],
                        [move_anchor_x[i - 1], top_y + 0.16, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2)

            vlab = mono(f"{WER[i]:.2f}", 22, INK)
            if i == len(WER) - 1:
                vlab.next_to(pts[i], RIGHT, buff=0.30)
            else:
                vlab.next_to(pts[i], UP, buff=0.18).shift(RIGHT * 0.42)

            self.play(FadeIn(mgrp, shift=DOWN * 0.06), Create(tick), run_time=0.32)

            pulse = Dot(color=INK, radius=0.06).move_to(pts[i - 1])
            self.add(pulse)
            seg_bar = RoundedRectangle(
                width=seg_x[i] - seg_x[i - 1], height=0.20, corner_radius=0.05,
                stroke_width=0, fill_color=INK, fill_opacity=0.0,
            ).move_to([(seg_x[i - 1] + seg_x[i]) / 2, BAR_Y, 0])
            self.add(seg_bar)
            bar_segs.append(seg_bar)
            self.play(
                Create(seg),
                pulse.animate.move_to(pts[i]),
                wer_t.animate.set_value(WER[i]),
                seg_bar.animate.set_fill(INK, opacity=0.85 - 0.10 * (i - 1)),
                run_time=0.78, rate_func=smooth,
            )
            self.remove(pulse)

            grow = [GrowFromCenter(dots[i]), FadeIn(vlab, shift=UP * 0.06)]
            if i == len(WER) - 1:
                self.add(glow(dots[i]))
            self.play(*grow, run_time=0.36)

            # PER dashed segment — dotted only, NO note (held for beats 5-7)
            pseg = DashedLine(per_pts[i - 1], per_pts[i], stroke_color=INK_GHOST,
                              stroke_width=2.2, dash_length=0.1)
            per_segments.append(pseg)
            per_dots[i].set_opacity(0.5)
            self.play(Create(pseg), GrowFromCenter(per_dots[i]), run_time=0.4)
            if i < len(WER) - 1:
                self.wait(0.15)

        wer_t.set_value(WER[-1])   # lock exact final value

        # the full WER polyline (for the white accent in beat 6/7)
        wer_line_grp = VGroup(*[Line(pts[i - 1], pts[i], stroke_color=INK, stroke_width=4)
                                for i in range(1, len(WER))])

        # =================================================================
        # BEAT 5 (~1.91s) — "the faint line underneath is the sound error."
        # Introduce the PER track as ONE connected object: fade it up from
        # ghost to faint; dim the WER line slightly to draw the eye DOWN.
        # =================================================================
        self.next_section("beat5_per_track")

        wer_dim_grp = VGroup(wer_line_grp, dots, start_lab, start_tag)
        per_track = VGroup(*per_segments, *per_dots)
        per_tag = mono("PER", 13, INK_FAINT).next_to(per_pts[0], LEFT, buff=0.24)
        per_sub = mono("sound error", 13, INK_FAINT).next_to(per_tag, DOWN, buff=0.08)

        self.add(wer_line_grp)   # static copy under the live segments
        self.play(
            wer_dim_grp.animate.set_opacity(0.4),
            *[s.animate.set_stroke(INK_FAINT, opacity=1.0) for s in per_segments],
            *[per_dots[k].animate.set_opacity(0.9) for k in range(len(per_dots))],
            FadeIn(per_tag), FadeIn(per_sub),
            run_time=0.7,
        )
        # PER value labels — below their dots, nudged clear of the WER labels
        per_v0 = mono("39", 13, INK_FAINT).next_to(per_pts[0], DOWN, buff=0.13).shift(RIGHT * 0.55)
        per_v2 = mono("22.34", 13, INK_FAINT).next_to(per_pts[2], DOWN, buff=0.16).shift(LEFT * 0.10)
        per_v3 = mono("20.90", 13, INK_FAINT).next_to(per_pts[3], DOWN, buff=0.18).shift(LEFT * 0.55)
        self.play(FadeIn(per_v0), FadeIn(per_v2), FadeIn(per_v3), run_time=0.5)
        self.wait(0.5)

        # =================================================================
        # BEAT 6 (~1.21s) — "on move two it plunges: truly heard better."
        # Spotlight ONLY the move-2 PER segment; dim the other PER segments.
        # The single pure-#fff accent rides this steep PER drop.
        # =================================================================
        self.next_section("beat6_per_plunge")

        note2 = mono("truly heard better", 13, INK).move_to(
            (per_pts[1] + per_pts[2]) / 2 + RIGHT * 0.55 + DOWN * 0.05)
        self.play(
            per_segments[0].animate.set_stroke(INK_GHOST, opacity=0.5),
            per_segments[2].animate.set_stroke(INK_GHOST, opacity=0.5),
            per_dots[1].animate.set_opacity(0.4),
            per_dots[3].animate.set_opacity(0.4),
            per_segments[1].animate.set_stroke(WHITE, opacity=1.0),
            run_time=0.45,
        )
        # plain (continuous) path for the white accent — DashedLine has no
        # single point-path, so MoveAlongPath needs a solid Line.
        accent_path = Line(per_pts[1], per_pts[2])
        trace = Dot(per_pts[1], radius=0.05, color=WHITE)
        self.add(trace)
        self.add(glow(per_dots[2]))
        self.play(
            MoveAlongPath(trace, accent_path),
            FadeIn(note2, shift=UP * 0.05),
            run_time=0.45, rate_func=smooth,
        )
        self.play(
            Flash(per_pts[2], color=WHITE, line_length=0.16, num_lines=10,
                  flash_radius=0.26),
            FadeOut(trace),
            run_time=0.4,
        )
        self.wait(0.1)

        # =================================================================
        # BEAT 7 (~1.56s) — "on move three it barely budges — smarter
        # word-picking, not better hearing." Spotlight the near-flat move-3
        # PER segment; drop slope labels (-7.6 WER steep vs -1.4 PER flat);
        # the punchline lands in the open lower-left.
        # =================================================================
        self.next_section("beat7_flat_payoff")

        self.play(
            per_segments[1].animate.set_stroke(INK_FAINT, opacity=1.0),
            per_dots[2].animate.set_opacity(0.9),
            per_segments[2].animate.set_stroke(INK_FAINT, opacity=1.0),
            per_dots[3].animate.set_opacity(0.9),
            note2.animate.set_opacity(0.4),
            run_time=0.4,
        )

        # slope read ON the chart: WER move-3 steep vs PER move-3 flat
        wmid = (pts[2] + pts[3]) / 2
        wer_slope = VGroup(
            mono("steep", 13, INK),
            mono(f"-{WER[2]-WER[3]:.1f} WER", 13, INK_DIM),
        ).arrange(DOWN, buff=0.05).move_to(wmid + RIGHT * 0.45 + UP * 0.55)

        pmid = (per_pts[2] + per_pts[3]) / 2
        per_slope = VGroup(
            mono("flat", 13, INK),
            mono(f"-{PER[2]-PER[3]:.1f} PER", 13, INK_DIM),
        ).arrange(DOWN, buff=0.05).move_to(pmid + DOWN * 0.72 + LEFT * 0.05)

        # spotlight the flat move-3 PER segment briefly
        self.play(
            FadeIn(wer_slope, shift=UP * 0.05),
            FadeIn(per_slope, shift=DOWN * 0.05),
            Indicate(per_segments[2], color=INK, scale_factor=1.0),
            run_time=0.55,
        )

        punch = VGroup(
            mono("smarter at choosing words,", 17, INK),
            mono("not at hearing sounds", 17, INK_DIM),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        punch.move_to([-2.55, -1.55, 0])
        self.play(FadeIn(punch, shift=UP * 0.06), run_time=0.45)

        # poster hold — stop the live counter, restore WER so the chart reads whole
        readout.clear_updaters()
        read_tag.clear_updaters()
        self.play(wer_dim_grp.animate.set_opacity(1.0), run_time=0.4)
        self.wait(0.45)


if __name__ == "__main__":
    pass
