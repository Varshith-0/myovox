# S21 — Many guesses (ensemble + n-best + union)
# Average two readers, keep dozens of guesses each, pool them — until the right
# answer is almost always in the pool.  Oracle 9.30% WER vs ~20% 1-best.
#
# CANVAS-FILLING REBUILD — three persistent horizontal zones held the whole clip:
#   TOP strip (y~+3.2):    a left-anchored context breadcrumb carried from S18/S20
#                          ("two readers · sounds stuck at ~20.9%") + a twin-glyph,
#                          with an active stage label on the right that morphs
#                          ENSEMBLE -> N-BEST -> POOL -> ORACLE.
#   CENTER (y~-1.8..+2.2):  the star — four beats morph IN PLACE (average two
#                          ribbons -> fan an n-best list -> pool lists into a
#                          candidate cloud -> the oracle line).
#   BOTTOM ruler (y~-3.0):  one WER ruler that lives all clip (worse=left 26%,
#                          better=right). The live marker walks 26 -> ~20 across
#                          two beats; the oracle 9.30% tick snaps in far right with
#                          a shaded "prize" headroom band — the running takeaway.
# Strict monochrome (emg_style inks + pure #fff peak accent only). No LaTeX.
#
# Ground truth (§9, nbest.py / union.py):
#   ensemble = average per-frame log-probs of the two Conformers -> ~20.1% WER
#   PER unchanged (~20.9%);  n-best via k2;  multi-scale union -> oracle 9.30%
#   1-best stays ~20%.
from manim import *
from emg_style import *
import numpy as np


def reader_curve(x, peaks, base=0.10, jitter=0.0):
    """A smooth per-frame 'sound-probability' ribbon: bumps at `peaks`."""
    y = np.full_like(x, base)
    for cx, h, w in peaks:
        y = y + h * np.exp(-((x - cx) ** 2) / (2 * w * w))
    return y + jitter


def tri(angle, c, op=1.0, s=0.08):
    """A bare triangular arrowhead (no Arrow tip mobject => no tip bug)."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def twin_glyph(c=INK_FAINT):
    """Two overlapping rounded ticks — the 'two readers' motif carried from S18."""
    a = RoundedRectangle(width=0.42, height=0.20, corner_radius=0.09,
                         stroke_color=c, stroke_width=1.8, fill_opacity=0)
    b = a.copy().shift(RIGHT * 0.16 + DOWN * 0.10)
    return VGroup(b, a)


class ManyGuesses(Scene):
    def construct(self):
        seed()

        # ============================================================== #
        #  BEAT 0 — FRAME: fade in the three persistent zones            #
        # ============================================================== #
        self.next_section("frame")

        # ---- TOP strip: context breadcrumb (carried from S18 / S20) ----
        glyph = twin_glyph(INK_FAINT)
        crumb = mono("two readers · sounds stuck at ~20.9%", 19, INK_FAINT)
        crumb_grp = VGroup(glyph, crumb).arrange(RIGHT, buff=0.26)
        crumb_grp.to_edge(LEFT, buff=0.7).to_edge(UP, buff=0.55)

        stage = mono("ENSEMBLE", 24, INK_DIM, w=BOLD).to_edge(RIGHT, buff=0.8).set_y(crumb_grp.get_y())
        rule = Line(LEFT * 6.6, RIGHT * 6.6, stroke_color=LINE, stroke_width=1.2)
        rule.set_y(crumb_grp.get_y() - 0.42)

        self.play(
            FadeIn(crumb_grp, shift=DOWN * 0.18),
            FadeIn(stage, shift=DOWN * 0.18),
            Create(rule),
            run_time=0.5,
        )

        # ---- BOTTOM WER ruler (lives the WHOLE clip) ----
        rx = 4.3                  # half-width of the track
        ry = -3.0                 # ruler baseline y
        wmax = 26.0               # worst (left end) = 26% WER; right end = 0%

        def xpos(w):
            return -rx + (1.0 - w / wmax) * (2 * rx)

        track = Line([-rx, ry, 0], [rx, ry, 0], stroke_color=INK_GHOST, stroke_width=2.4)
        cap26 = num("26%", 22, INK_FAINT).move_to([xpos(26.0), ry - 0.42, 0])
        cap0 = num("0%", 18, INK_GHOST).move_to([xpos(0.0) + 0.18, ry - 0.42, 0])
        # ruler legend lives BELOW the % numbers (its own clear row) so it never
        # collides with the per-tick labels that appear ABOVE the track later.
        cap_lab = mono("word-error rate", 15, INK_FAINT)
        cap_lab.move_to([xpos(26.0) + cap_lab.width / 2 - 0.05, ry - 0.78, 0])
        cap_dir = mono("better →", 15, INK_GHOST)
        cap_dir.move_to([xpos(0.0) - cap_dir.width / 2 + 0.05, ry - 0.78, 0])

        # the live marker tick — starts at the 26% (worst) end
        live = Line([xpos(26.0), ry - 0.17, 0], [xpos(26.0), ry + 0.17, 0],
                    stroke_color=INK, stroke_width=3.2)

        self.play(
            Create(track),
            FadeIn(cap26), FadeIn(cap0), FadeIn(cap_lab), FadeIn(cap_dir),
            run_time=0.5,
        )
        self.play(GrowFromCenter(live), run_time=0.25)

        # the persistent center band centre and a generous frame for beats
        CY = 0.4   # vertical centre of the center zone

        # ============================================================== #
        #  BEAT 1 — AVERAGE two readers                                   #
        # ============================================================== #
        self.next_section("average")

        ax = Axes(
            x_range=[0, 10, 1], y_range=[0, 1.0, 1],
            x_length=9.0, y_length=2.6,
            axis_config={"stroke_color": INK_GHOST, "stroke_width": 1.6,
                         "include_ticks": False, "include_tip": False},
        ).move_to([0, CY, 0])

        xs = np.linspace(0, 10, 240)
        peaksA = [(2.0, 0.66, 0.5), (4.3, 0.78, 0.45), (6.6, 0.55, 0.6), (8.4, 0.70, 0.5)]
        peaksB = [(2.0, 0.80, 0.5), (4.3, 0.60, 0.5), (6.6, 0.74, 0.5), (8.4, 0.58, 0.55)]
        yA = reader_curve(xs, peaksA)
        yB = reader_curve(xs, peaksB)
        # one spurious wobble each, at different x — they cancel in the average
        yA = yA + 0.16 * np.exp(-((xs - 5.5) ** 2) / 0.5)
        yB = yB + 0.16 * np.exp(-((xs - 3.2) ** 2) / 0.5)
        yAvg = 0.5 * (yA + yB)

        def graph(y, color, sw, op):
            pts = [ax.c2p(x, min(v, 0.98)) for x, v in zip(xs, y)]
            return VMobject().set_points_smoothly(pts).set_stroke(color, sw, op)

        gA = graph(yA, INK_FAINT, 2.2, 0.7)
        gB = graph(yB, INK_DIM, 2.2, 0.72)
        labA = mono("reader A", 17, INK_FAINT).next_to(ax, LEFT, buff=0.2).align_to(ax, UP)
        labB = mono("reader B", 17, INK_DIM).next_to(labA, DOWN, buff=0.14)

        self.play(Create(ax), run_time=0.35)
        self.play(Create(gA), Create(gB), FadeIn(labA), FadeIn(labB), run_time=0.55)

        # a vertical sweep scans their disagreement (the two wobbles)
        sweep = Line(ax.c2p(0, 0), ax.c2p(0, 1.0), stroke_color=INK, stroke_width=2.6).set_opacity(0.75)
        self.add(sweep)
        self.play(sweep.animate.move_to(ax.c2p(10, 0.5)), run_time=0.5, rate_func=linear)
        self.play(FadeOut(sweep), run_time=0.12)

        # average -> one glowing, steadier ribbon
        gAvg = glow(graph(yAvg, INK, 3.6, 1.0))
        labAvg = mono("average", 19, INK).next_to(ax, LEFT, buff=0.2)
        labAvg.move_to((labA.get_center() + labB.get_center()) / 2)
        self.play(
            ReplacementTransform(VGroup(gA, gB), gAvg),
            ReplacementTransform(VGroup(labA, labB), labAvg),
            run_time=0.65,
        )

        foreshadow = mono("the sounds aren't read better — we just decode more cleverly",
                          16, INK_FAINT).move_to([0, CY - 1.7, 0])
        self.play(FadeIn(foreshadow), run_time=0.3)

        # --- ruler resolves: marker walks 26% -> ~20% ---
        m20 = Line([xpos(20.0), ry - 0.17, 0], [xpos(20.0), ry + 0.17, 0],
                   stroke_color=INK, stroke_width=3.2)
        cap20 = num("~20%", 22, INK).move_to([xpos(20.0), ry - 0.42, 0])
        cap20_t = mono("+ average", 15, INK_FAINT).move_to([xpos(20.0), ry + 0.42, 0])
        pulse = Dot(color=INK, radius=0.06).move_to([xpos(26.0), ry, 0])
        self.add(pulse)
        self.play(
            pulse.animate.move_to([xpos(20.0), ry, 0]),
            Transform(live, m20),
            cap26.animate.set_opacity(0.4),
            run_time=0.6, rate_func=smooth,
        )
        self.remove(pulse)
        self.play(FadeIn(cap20), FadeIn(cap20_t),
                  Indicate(cap20, scale_factor=1.12, color=INK), run_time=0.45)

        # ============================================================== #
        #  BEAT 2 — N-BEST: keep a ranked list                           #
        # ============================================================== #
        self.next_section("nbest")
        stage2 = mono("N-BEST", 24, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage2), run_time=0.4)
        stage = stage2

        # the average ribbon peels into a small stacked list-token, upper-left
        list_token = VGroup(*[
            RoundedRectangle(width=1.7, height=0.30, corner_radius=0.06,
                             stroke_color=INK_FAINT, stroke_width=1.4,
                             fill_color=INK_GHOST, fill_opacity=0.30 - 0.05 * k)
            .shift(DOWN * 0.10 * k + RIGHT * 0.09 * k)
            for k in range(4)
        ])
        list_token.move_to([-4.3, CY + 1.2, 0])
        tok_cap = mono("n-best", 15, INK_FAINT).next_to(list_token, DOWN, buff=0.16)
        self.play(
            ReplacementTransform(VGroup(ax, gAvg, labAvg, foreshadow), list_token),
            FadeIn(tok_cap),
            run_time=0.65,
        )

        # a ranked list of 5 candidates fans down (opacity gradient), true at rank 4
        cands = [
            ("the quick brown box", False),
            ("a quick brown fox", False),
            ("the quink brown fox", False),
            ("the quick brown fox", True),   # the true answer — buried but present
            ("the quick brow fox", False),
        ]
        rows = VGroup()
        for i, (c, _) in enumerate(cands):
            rank = mono(f"{i+1}.", 20, INK_FAINT)
            txt = mono(c, 23, INK)
            rows.add(VGroup(rank, txt).arrange(RIGHT, buff=0.30))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        rows.move_to([0.5, CY, 0])
        for i, row in enumerate(rows):
            row.set_opacity(1.0 - 0.13 * i)
        moredots = mono("...  (dozens more)", 18, INK_GHOST).next_to(rows, DOWN, buff=0.26, aligned_edge=LEFT)

        self.play(LaggedStartMap(FadeIn, rows, shift=RIGHT * 0.22, lag_ratio=0.13, run_time=0.7))
        self.play(FadeIn(moredots), run_time=0.2)

        true_idx = next(i for i, (_, t) in enumerate(cands) if t)
        true_row = rows[true_idx]
        marker = mono("← present, just not #1", 17, INK).next_to(true_row, RIGHT, buff=0.45)
        self.play(true_row.animate.set_opacity(1.0), FadeIn(marker, shift=LEFT * 0.2), run_time=0.45)
        self.play(Circumscribe(true_row, color=INK, stroke_width=2, buff=0.10, time_width=0.5), run_time=0.5)
        # ruler holds at ~20% — n-best alone doesn't move the 1-best (that's the point)
        self.wait(0.1)

        # ============================================================== #
        #  BEAT 3 — POOL: multi-scale union, dedupe                       #
        # ============================================================== #
        self.next_section("pool")
        stage3 = mono("POOL", 24, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage3), run_time=0.4)
        stage = stage3
        union_tag = mono("multi-scale union", 15, INK_FAINT).next_to(stage3, DOWN, buff=0.12).align_to(stage3, RIGHT)
        self.play(FadeIn(union_tag), run_time=0.25)

        # collapse the n-best list + token into three dial-labelled list-tokens, left
        dials = VGroup()
        dial_labels = ["scale ×1", "scale ×2", "scale ×4"]
        for lab in dial_labels:
            lst = VGroup(*[
                RoundedRectangle(width=1.6, height=0.26, corner_radius=0.05,
                                 stroke_color=INK_FAINT, stroke_width=1.2,
                                 fill_color=INK_GHOST, fill_opacity=0.26 - 0.05 * k)
                .shift(DOWN * 0.08 * k + RIGHT * 0.07 * k)
                for k in range(3)
            ])
            cap = mono(lab, 15, INK_FAINT).next_to(lst, DOWN, buff=0.14)
            dials.add(VGroup(lst, cap))
        dials.arrange(DOWN, buff=0.50, aligned_edge=LEFT)
        dials.move_to([-4.5, CY, 0])

        self.play(
            ReplacementTransform(VGroup(rows, moredots, marker, list_token, tok_cap), dials[0][0]),
            FadeIn(dials[0][1]),
            run_time=0.65,
        )
        self.play(LaggedStart(*[FadeIn(dials[k], shift=DOWN * 0.2) for k in (1, 2)],
                              lag_ratio=0.3, run_time=0.55))

        # the pooled-candidates cloud on the right
        pool = RoundedRectangle(width=3.4, height=2.9, corner_radius=0.14,
                                stroke_color=INK, stroke_width=2.0,
                                fill_color=INK_GHOST, fill_opacity=0.08)
        pool.move_to([3.3, CY, 0])
        pool_title = mono("pooled candidates", 19, INK, w=BOLD).next_to(pool, UP, buff=0.16)
        self.play(Create(pool), FadeIn(pool_title), run_time=0.5)

        count = ValueTracker(0)
        readout = counter(count, fmt=lambda v: str(round(v)), s=62, c=INK,
                          at=pool.get_center() + UP * 0.35)
        cap_count = mono("candidates", 16, INK_DIM).move_to(pool.get_center() + DOWN * 0.55)
        cap_dedup = mono("(deduped)", 14, INK_FAINT).next_to(cap_count, DOWN, buff=0.10)
        self.add(readout)

        arrows = VGroup(*[
            Line(dials[k][0].get_right() + RIGHT * 0.12, pool.get_left() + LEFT * 0.12,
                 stroke_width=1.8, color=INK_FAINT)
            for k in range(3)
        ])
        heads = VGroup(*[tri(-PI / 2, INK_FAINT, 1.0, 0.07).move_to(ln.get_end()) for ln in arrows])

        # small accumulating dots inside the box (deterministic placement)
        rng = np.random.default_rng(7)
        pc = pool.get_center()
        pw, ph = 3.4 - 0.5, 2.9 - 0.9
        all_dots = []
        for _ in range(30):
            dx = (rng.random() - 0.5) * pw
            dy = (rng.random() - 0.5) * ph + 0.05
            all_dots.append(Dot([pc[0] + dx, pc[1] + dy, 0], radius=0.035, color=INK).set_opacity(0.7))

        targets = [38, 71, 94]
        dot_cuts = [10, 21, 30]
        prev = 0
        for k in range(3):
            pulse = Dot(color=INK, radius=0.06).move_to(arrows[k].get_start())
            self.add(pulse)
            batch = VGroup(*all_dots[prev:dot_cuts[k]])
            # draw the arrow, send the pulse, bump the count and pour dots in one beat
            self.play(
                Create(arrows[k]), FadeIn(heads[k]),
                pulse.animate.move_to(arrows[k].get_end()),
                count.animate.set_value(targets[k]),
                LaggedStartMap(FadeIn, batch, lag_ratio=0.05, scale=0.6),
                run_time=0.5, rate_func=linear,
            )
            self.remove(pulse)
            prev = dot_cuts[k]
        readout.clear_updaters()
        self.play(FadeIn(cap_count), FadeIn(cap_dedup), run_time=0.3)

        # the TRUE answer dot travels in last and glows inside the cloud
        true_dot = Dot([pc[0] - 0.2, pc[1] - 0.15, 0], radius=0.06, color=WHITE)
        glow_dot = glow(true_dot.copy())
        in_caption = mono("the right answer is in the pool", 16, INK).next_to(pool, DOWN, buff=0.28)
        travel = Dot(color=WHITE, radius=0.06).move_to(dials[1][0].get_right())
        self.add(travel)
        self.play(travel.animate.move_to(true_dot.get_center()), run_time=0.45, rate_func=smooth)
        self.remove(travel)
        self.add(glow_dot)
        self.play(FadeIn(in_caption), Flash(true_dot, color=WHITE, line_length=0.12,
                                            num_lines=10, flash_radius=0.22), run_time=0.45)
        self.wait(0.1)
        # ruler still at ~20% — pooling fills the pool, doesn't choose yet

        # ============================================================== #
        #  BEAT 4 — ORACLE: the headroom, the prize                      #
        # ============================================================== #
        self.next_section("oracle")
        stage4 = mono("ORACLE", 24, INK, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        beat3 = VGroup(dials, arrows, heads, pool, pool_title, readout,
                       cap_count, cap_dedup, glow_dot, in_caption, *all_dots)
        self.play(FadeOut(beat3), FadeOut(union_tag),
                  ReplacementTransform(stage, stage4), run_time=0.6)
        stage = stage4

        line = mono("if a perfect chooser always picked the best candidate —",
                    20, INK_FAINT).move_to([0, CY + 1.2, 0])
        self.play(FadeIn(line), run_time=0.4)

        # --- the wow moment, on the ruler that has been there all along ---
        m_or = Line([xpos(9.30), ry - 0.20, 0], [xpos(9.30), ry + 0.20, 0],
                    stroke_color=INK, stroke_width=4.2)
        cap_or = num("9.30%", 24, INK).move_to([xpos(9.30), ry - 0.42, 0])
        cap_or_t = mono("perfect chooser", 15, INK).move_to([xpos(9.30), ry + 0.42, 0])

        mover = Dot(color=WHITE, radius=0.06).move_to([xpos(20.0), ry, 0])
        self.add(mover)
        self.play(GrowFromCenter(m_or), FadeIn(cap_or), FadeIn(cap_or_t),
                  mover.animate.move_to([xpos(9.30), ry, 0]),
                  run_time=0.65, rate_func=smooth)
        self.remove(mover)
        self.add(glow(m_or))

        # shaded headroom band ON the track, between ~20% and 9.30%
        band = Rectangle(width=abs(xpos(20.0) - xpos(9.30)), height=0.30,
                         stroke_width=0, fill_color=INK, fill_opacity=0.13)
        band.move_to([(xpos(20.0) + xpos(9.30)) / 2, ry, 0])

        # double-arrow ABOVE the track. Dashed drops start ABOVE the per-tick
        # labels (which sit at ry+0.42) so the thin lines never cut through text.
        gy = ry + 1.02
        dtop = gy - 0.10
        dbot = ry + 0.66   # clears the "+ average" / "perfect chooser" labels
        dl = DashedLine([xpos(20.0), dbot, 0], [xpos(20.0), dtop, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2, dash_length=0.06)
        dr = DashedLine([xpos(9.30), dbot, 0], [xpos(9.30), dtop, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2, dash_length=0.06)
        gspan = Line([xpos(9.30), gy, 0], [xpos(20.0), gy, 0], stroke_color=INK, stroke_width=2.2)
        gl = tri(PI / 2, INK, 1.0, 0.08).move_to([xpos(9.30), gy, 0])
        gr = tri(-PI / 2, INK, 1.0, 0.08).move_to([xpos(20.0), gy, 0])
        gap_lab = mono("the headroom — that gap is the prize", 18, INK).move_to([0, gy + 0.34, 0])

        # a second quiet line: the gap is reachable because the answer IS in the pool
        line2 = mono("— it's already in the pool; a smart chooser just has to find it",
                     18, INK_FAINT).move_to([0, CY + 0.55, 0])
        self.play(FadeIn(line2), run_time=0.35)

        self.play(FadeIn(band), Create(dl), Create(dr), run_time=0.4)
        self.play(GrowFromCenter(gspan), FadeIn(gl), FadeIn(gr), run_time=0.4)
        self.play(FadeIn(gap_lab), run_time=0.35)

        # compact recap of the three moves, low and dim, in the lower center band
        recap = VGroup(
            mono("average the two readers", 16, INK_FAINT),
            mono("·", 16, INK_GHOST),
            mono("keep dozens of guesses", 16, INK_FAINT),
            mono("·", 16, INK_GHOST),
            mono("pool across dial settings", 16, INK_FAINT),
        ).arrange(RIGHT, buff=0.24).move_to([0, CY - 0.7, 0])
        self.play(FadeIn(recap), run_time=0.45)

        # final poster hold — top breadcrumb + ORACLE, center recap, full ruler
        self.wait(0.6)


if __name__ == "__main__":
    pass
