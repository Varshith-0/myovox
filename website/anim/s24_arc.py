# website/anim/s24_arc.py  — S24 "The climb (the arc)"
# Strict monochrome. The climb is really a FALL: a full-bleed stepped descent that
# walks DOWN-and-RIGHT across the whole canvas, each tread earned by one move:
#   51.17 -> 40.63 -> 26.14 -> 18.53   (WER, bold line)
# A fainter PER track runs in parallel beneath:
#   39.02 -> 39.02 -> 22.34 -> 20.90   (PER, dashed)
# The teaching contrast: PER fell HARD on move two (the model truly HEARD better)
# but barely moved on move three (only the decoding got smarter) — the wall ahead.
#
# CANVAS-FILLING REBUILD — three persistent horizontal zones held the whole clip:
#   TOP strip (y~+2.6..+3.5):  quiet context — a left-anchored recap linking back to
#                         S23 ("the whole climb, in one chart · from 51% wrong"), a
#                         thin LINE rule, and a right-anchored down-arrow "lower is
#                         better" cue. The INK_GHOST y-axis rises into this strip so
#                         the chart visibly owns the upper canvas.
#   CENTER (y~-2.3..+1.9): the star — a wide stepped WER descent sweeping the full
#                         width; a traveling pulse rides each segment as it's drawn,
#                         each new dot GrowsFromCenter with its value; the dashed PER
#                         track runs beneath; move captions hang on ghost ticks. The
#                         wow: copies of the two move-3 segments lift into a small
#                         "tilt comparator" — WER steep, PER near-flat.
#   BOTTOM band (y~-3.1..-3.7): the running takeaway — a 3-segment progress bar sized
#                         by the drops (-10.5 / -14.5 / -7.6, so move 2 is the widest
#                         win), the live WER counter ticking 51.17 -> 18.53, "WER %"
#                         tag. Final state freezes the bar full with widths labelled.
# Strict monochrome (emg_style inks + a single pure-#fff peak accent). No LaTeX.
#
# Ground truth (Technical report §1, §12):
#   WER 51.17 -> 40.63 -> 26.14 -> 18.53; PER 39.02 -> 22.34 -> 20.90; the EMG-only
#   full-context encoder (not the teacher) moved WER on move two; PER barely moved on
#   move three (only the word-chooser got smarter).
from manim import *
from emg_style import *
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
        # POSE (0-2.5s) — top context strip, y-axis, the two start dots,
        # bottom counter + empty progress track.
        # =================================================================

        # ----- TOP context strip -----
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

        # ----- value axis -----
        base = Line([X0, _y(0), 0], [X1, _y(0), 0],
                    stroke_color=INK_GHOST, stroke_width=2)
        yaxis = Line([X0, _y(0), 0], [X0, 2.40, 0],   # rises up INTO the top strip
                     stroke_color=INK_GHOST, stroke_width=1.4).set_opacity(0.55)
        axis_lbl = mono("0% wrong", 13, INK_FAINT).next_to([X0, _y(0), 0], DOWN, buff=0.12).shift(RIGHT * 0.05)

        self.play(
            FadeIn(recap_grp, shift=RIGHT * 0.06),
            FadeIn(better, shift=LEFT * 0.06),
            Create(top_rule),
            run_time=0.5,
        )
        self.play(Create(yaxis), Create(base), FadeIn(axis_lbl), run_time=0.42)

        # ----- BOTTOM band: live WER counter + empty progress track -----
        BAR_L, BAR_R = -3.55, 3.55
        BAR_Y = -3.62
        bar_track = RoundedRectangle(width=BAR_R - BAR_L, height=0.20, corner_radius=0.05,
                                     stroke_color=INK_GHOST, stroke_width=1.6,
                                     fill_opacity=0).move_to([(BAR_L + BAR_R) / 2, BAR_Y, 0])

        wer_t = ValueTracker(WER[0])
        readout_at = np.array([0, -3.10, 0])
        readout = counter(wer_t, fmt=lambda v: f"{v:.2f}", s=40, c=INK, at=readout_at)
        read_tag = mono("WER %", 13, INK_DIM)
        read_tag.add_updater(lambda m: m.next_to(readout, RIGHT, buff=0.20).align_to(readout, DOWN))
        self.add(readout, read_tag)
        self.play(Create(bar_track), FadeIn(readout), FadeIn(read_tag), run_time=0.42)

        # ----- WER start dot (51.17) -----
        dots = VGroup(*[Dot(p, radius=0.075, color=INK) for p in pts])
        start_lab = mono(f"{WER[0]:.2f}", 22, INK).next_to(pts[0], UP, buff=0.22).shift(RIGHT * 0.18)
        start_tag = mono("start", 13, INK_FAINT).next_to(start_lab, UP, buff=0.10)
        self.play(GrowFromCenter(dots[0]),
                  FadeIn(start_lab, shift=DOWN * 0.08),
                  FadeIn(start_tag), run_time=0.45)

        # ----- PER start dot (fainter, lower, dashed track to come) -----
        per_dots = VGroup(*[Dot(p, radius=0.05, color=INK_FAINT) for p in per_pts])
        per_tag = mono("PER", 13, INK_FAINT).next_to(per_pts[0], LEFT, buff=0.24)
        per_v0 = mono("39", 14, INK_FAINT).next_to(per_pts[0], DOWN, buff=0.13)
        self.play(GrowFromCenter(per_dots[0]), FadeIn(per_tag), FadeIn(per_v0), run_time=0.45)

        # =================================================================
        # THE THREE MOVES (2.5-9.5s)
        # Each: caption on a ghost tick, descending segment + traveling pulse,
        # counter ticks down, a progress-bar segment lights, new dot + value,
        # the PER dashed segment.
        # =================================================================
        move_anchor_x = [_x(0.5), _x(1.5), _x(2.5)]
        # progress-bar segment boundaries proportional to the WER drops
        total_drop = WER[0] - WER[-1]
        seg_frac = [d / total_drop for d in DROP]
        seg_x = [BAR_L]
        for f in seg_frac:
            seg_x.append(seg_x[-1] + f * (BAR_R - BAR_L))
        # seg_x = [BAR_L, b1, b2, BAR_R]
        bar_segs = []

        per_segments = []   # keep refs to PER dashed segments for the wow moment

        per_notes = [
            "PER unchanged",          # move 1
            "truly heard better",     # move 2
            "barely moved",           # move 3
        ]
        per_note_mobs = []   # keep refs (move-3 note gets retired during the WOW beat)

        for i in range(1, len(WER)):
            seg = Line(pts[i - 1], pts[i], stroke_color=INK, stroke_width=4)

            # move caption on a ghost tick, hung well above the higher endpoint
            mlbl = mono(MOVES[i - 1][0], 15, INK_DIM, w=BOLD)
            mtxt = mono(MOVES[i - 1][1], 14, INK_DIM).set_opacity(0.82)
            mgrp = VGroup(mlbl, mtxt).arrange(DOWN, buff=0.07)
            top_y = max(pts[i - 1][1], pts[i][1])
            mgrp.move_to([move_anchor_x[i - 1], top_y + 1.05, 0])
            tick = Line([move_anchor_x[i - 1], mgrp.get_bottom()[1] - 0.04, 0],
                        [move_anchor_x[i - 1], top_y + 0.16, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2)

            # WER value label at the new dot — above-right, clear of the line below
            vlab = mono(f"{WER[i]:.2f}", 22, INK)
            if i == len(WER) - 1:
                vlab.next_to(pts[i], RIGHT, buff=0.30)         # last: out to the right
            else:
                vlab.next_to(pts[i], UP, buff=0.18).shift(RIGHT * 0.42)

            # build the caption first (pose)
            self.play(FadeIn(mgrp, shift=DOWN * 0.06), Create(tick), run_time=0.32)

            # draw the segment while a pulse travels & counter ticks & bar lights
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
                run_time=0.72, rate_func=smooth,
            )
            self.remove(pulse)
            self.play(GrowFromCenter(dots[i]),
                      FadeIn(vlab, shift=UP * 0.06),
                      run_time=0.34)

            # PER dashed segment for this move
            pseg = DashedLine(per_pts[i - 1], per_pts[i], stroke_color=INK_FAINT,
                              stroke_width=2.6, dash_length=0.1)
            per_segments.append(pseg)
            note = mono(per_notes[i - 1], 13, INK_FAINT)
            per_note_mobs.append(note)
            note_mid = (per_pts[i - 1] + per_pts[i]) / 2

            if i == 2:
                # move 2: PER drops HARD — the single peak-white accent of the clip.
                note.set_color(INK).move_to(note_mid + DOWN * 0.32 + LEFT * 0.20)
                self.play(Create(pseg), GrowFromCenter(per_dots[i]), run_time=0.4)
                self.play(
                    Flash(per_dots[i], color=WHITE, line_length=0.16, num_lines=10,
                          flash_radius=0.26, run_time=0.5),
                    Indicate(pseg, color=WHITE, scale_factor=1.0),
                    FadeIn(note, shift=UP * 0.05),
                    run_time=0.5,
                )
            else:
                note.move_to(note_mid + DOWN * 0.30)
                self.play(Create(pseg), GrowFromCenter(per_dots[i]),
                          FadeIn(note, shift=UP * 0.05), run_time=0.42)

        wer_t.set_value(WER[-1])   # lock exact final value

        # PER value labels for the later points — BELOW their dots, nudged LEFT so
        # the final 20.90 never collides with the WER "18.53" hanging to the right.
        per_v2 = mono("22.34", 14, INK_FAINT).next_to(per_pts[2], DOWN, buff=0.16).shift(LEFT * 0.10)
        per_v3 = mono("20.90", 14, INK_FAINT).next_to(per_pts[3], DOWN, buff=0.18).shift(LEFT * 0.55)
        self.play(FadeIn(per_v2), FadeIn(per_v3), run_time=0.35)

        # collect the full WER polyline (drawn segments) + dots so we can re-emphasise
        wer_line_grp = VGroup(*[Line(pts[i - 1], pts[i], stroke_color=INK, stroke_width=4)
                                for i in range(1, len(WER))])
        early_dim = VGroup(start_lab, start_tag, per_v0, per_tag)

        # =================================================================
        # WOW / NAME IT (9.5-12s) — read the contrast OFF the chart itself.
        # Quiet everything but the move-3 pair, then drop two slope brackets right
        # on the two move-3 segments: WER falls STEEP (-7.6), PER lies near-FLAT
        # (-1.4). The single white accent rides the steep WER drop and stalls on the
        # flat PER drop. Punchline lands in the open lower-left, clear of all lines.
        # =================================================================
        # gentle pull-back: quiet moves 1-2 AND the move-3 caption + its redundant
        # "barely moved" note, so the right corner opens up for the slope read.
        dim_grp = VGroup(per_segments[0], per_segments[1])
        move3_caption = mgrp                      # last caption built in the loop
        retire = VGroup(per_note_mobs[2])         # move-3 "barely moved" — slope says it
        self.play(
            *[m.animate.set_opacity(0.30) for m in dim_grp],
            *[dots[k].animate.set_opacity(0.4) for k in (0, 1)],
            per_dots[0].animate.set_opacity(0.4),
            per_dots[1].animate.set_opacity(0.4),
            move3_caption.animate.set_opacity(0.35),
            FadeOut(retire),
            run_time=0.5,
        )

        # ---- slope read ON the chart (no floating inset, no clutter) ----
        # WER move-3 segment falls STEEP; sits above-right of the segment, in the
        # gap freed by dimming the caption.
        wmid = (pts[2] + pts[3]) / 2
        wer_slope = VGroup(
            mono("steep", 13, INK),
            mono(f"-{WER[2]-WER[3]:.1f} WER", 13, INK_DIM),
        ).arrange(DOWN, buff=0.05).move_to(wmid + RIGHT * 0.30 + UP * 0.50)

        # PER move-3 segment lies near-FLAT; label drops well below, clear of 20.90.
        pmid = (per_pts[2] + per_pts[3]) / 2
        per_slope = VGroup(
            mono("flat", 13, INK_FAINT),
            mono(f"-{PER[2]-PER[3]:.1f} PER", 13, INK_FAINT),
        ).arrange(DOWN, buff=0.05).move_to(pmid + DOWN * 0.72 + LEFT * 0.05)

        self.play(
            FadeIn(wer_slope, shift=UP * 0.05),
            FadeIn(per_slope, shift=DOWN * 0.05),
            run_time=0.45,
        )

        # white accent: ride the steep WER drop, then stall on the flat PER drop
        trace = Dot(pts[2], radius=0.05, color=WHITE)
        self.add(trace)
        self.play(MoveAlongPath(trace, wer_line_grp[2]), run_time=0.5, rate_func=smooth)
        self.play(trace.animate.move_to(per_pts[3]), run_time=0.45, rate_func=rush_into)
        self.add(glow(per_dots[3]))
        self.play(Flash(per_dots[3], color=INK, line_length=0.12, num_lines=8,
                        flash_radius=0.2, run_time=0.4),
                  FadeOut(trace), run_time=0.4)

        # name it — in the OPEN lower-left, clear of every line and label
        punch = VGroup(
            mono("smarter at choosing words,", 17, INK),
            mono("not at hearing sounds", 17, INK_DIM),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        punch.move_to([-2.55, -1.55, 0])
        self.play(FadeIn(punch, shift=UP * 0.06), run_time=0.42)

        # =================================================================
        # POSTER HOLD — restore the full chart, label the bar widths, glow the
        # endpoints. Stop the live counter. Everything balanced, nothing clipped.
        # =================================================================
        wer_t.set_value(WER[-1])
        readout.clear_updaters()
        read_tag.clear_updaters()

        # bring moves 1-2 + the move-3 caption back up so the chart reads whole
        self.play(
            *[m.animate.set_opacity(1.0) for m in dim_grp],
            *[dots[k].animate.set_opacity(1.0) for k in (0, 1)],
            per_dots[0].animate.set_opacity(1.0),
            per_dots[1].animate.set_opacity(1.0),
            move3_caption.animate.set_opacity(1.0),
            run_time=0.4,
        )

        # label each lit bar segment with its drop width
        width_lbls = VGroup()
        for k, seg_bar in enumerate(bar_segs):
            wl = mono(f"-{DROP[k]:.1f}", 12, INK_FAINT)
            wl.next_to(seg_bar, DOWN, buff=0.10)
            width_lbls.add(wl)
        self.play(LaggedStartMap(FadeIn, width_lbls, lag_ratio=0.22, run_time=0.4))

        # headline endpoints glow
        self.add(glow(dots[0]), glow(dots[-1]))
        self.play(
            Indicate(dots[-1], color=INK, scale_factor=1.4),
            run_time=0.4,
        )
        self.wait(0.6)


if __name__ == "__main__":
    pass
