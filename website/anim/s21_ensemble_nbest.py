# S21 — Many guesses (ensemble + n-best + union)
# Two readers each get a sentence wrong ~1/5 of the time. Average them (26%->~20%),
# then stop demanding ONE answer: keep a shortlist, pool the lists across dial
# settings, and the truly-correct sentence is almost always in the pool. A perfect
# chooser would hit 9.30% — the gap to ~20% is the prize for a smarter chooser.
#
# LOCKED 8-BEAT SHEET (one self.next_section per beat, timed to dur_sec; ~13.6s):
#   1 puzzle   two reader ribbons "one wrong sentence" + WER marker stuck at 26%
#   2 average  vertical sweep; the two wobbles merge into one glowing ribbon
#   3 nudge    marker walks 26% -> ~20%; "+ average" tick snaps in and pulses
#   4 turn     averaged ribbon peels into ONE n-best list-token, spotlit; ruler holds
#   5 pool     candidates fan -> three dial-lists pour into the pooled cloud; counter
#   6 in-pool  the bright true-answer dot travels in last and flashes inside the cloud
#   7 oracle   the 9.30% "perfect chooser" tick grows far right; ~20% stays put
#   8 prize    headroom band + double-arrow fill the gap; serif #fff "the prize"
#
# Strict monochrome (emg_style inks + a single pure-#fff peak accent). No LaTeX.
# Ground truth (§9): ensemble averages per-frame log-probs -> ~20.1% WER; n-best via
# k2; multi-scale union -> oracle 9.30%; 1-best stays ~20%.
from manim import *
from emg_style import *
import numpy as np


def reader_curve(x, peaks, base=0.10):
    """A smooth per-frame 'sound-probability' ribbon: bumps at `peaks`."""
    y = np.full_like(x, base)
    for cx, h, w in peaks:
        y = y + h * np.exp(-((x - cx) ** 2) / (2 * w * w))
    return y


def tri(angle, c, op=1.0, s=0.08):
    """A bare triangular arrowhead (no Arrow tip mobject => no tip bug)."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def list_token(n=4, w=1.7, c=INK_FAINT, base_op=0.30):
    """A small stacked stack-of-cards glyph standing for one ranked shortlist."""
    return VGroup(*[
        RoundedRectangle(width=w, height=0.30, corner_radius=0.06,
                         stroke_color=c, stroke_width=1.4,
                         fill_color=INK_GHOST, fill_opacity=base_op - 0.05 * k)
        .shift(DOWN * 0.10 * k + RIGHT * 0.09 * k)
        for k in range(n)
    ])


class ManyGuesses(Scene):
    def construct(self):
        seed()

        # ---- the WER ruler lives the WHOLE clip (worst=left 26%, better=right) ----
        rx, ry, wmax = 4.3, -3.0, 26.0

        def xpos(w):
            return -rx + (1.0 - w / wmax) * (2 * rx)

        track = Line([-rx, ry, 0], [rx, ry, 0], stroke_color=INK_GHOST, stroke_width=2.4)
        cap26 = num("26%", 22, INK).move_to([xpos(26.0), ry - 0.42, 0])
        cap0 = num("0%", 18, INK_GHOST).move_to([xpos(0.0) + 0.18, ry - 0.42, 0])
        cap_lab = mono("word-error rate", 15, INK_FAINT)
        cap_lab.move_to([xpos(26.0) + cap_lab.width / 2 - 0.05, ry - 0.80, 0])
        cap_dir = mono("better →", 15, INK_GHOST)
        cap_dir.move_to([xpos(0.0) - cap_dir.width / 2 + 0.05, ry - 0.80, 0])

        CY = 0.55  # vertical centre of the working zone

        # ============================================================== #
        #  BEAT 1 — PUZZLE: two readers, each wrong ~1/5; marker stuck     #
        # ============================================================== #
        self.next_section("puzzle")

        ax = Axes(
            x_range=[0, 10, 1], y_range=[0, 1.0, 1],
            x_length=9.0, y_length=2.4,
            axis_config={"stroke_color": INK_GHOST, "stroke_width": 1.6,
                         "include_ticks": False, "include_tip": False},
        ).move_to([0, CY, 0])

        xs = np.linspace(0, 10, 240)
        peaksA = [(2.0, 0.66, 0.5), (4.3, 0.78, 0.45), (6.6, 0.55, 0.6), (8.4, 0.70, 0.5)]
        peaksB = [(2.0, 0.80, 0.5), (4.3, 0.60, 0.5), (6.6, 0.74, 0.5), (8.4, 0.58, 0.55)]
        yA = reader_curve(xs, peaksA) + 0.16 * np.exp(-((xs - 5.5) ** 2) / 0.5)
        yB = reader_curve(xs, peaksB) + 0.16 * np.exp(-((xs - 3.2) ** 2) / 0.5)
        yAvg = 0.5 * (yA + yB)

        def graph(y, color, sw, op):
            pts = [ax.c2p(x, min(v, 0.98)) for x, v in zip(xs, y)]
            return VMobject().set_points_smoothly(pts).set_stroke(color, sw, op)

        gA = graph(yA, INK_FAINT, 2.2, 0.7)
        gB = graph(yB, INK_DIM, 2.2, 0.72)
        labA = VGroup(mono("reader A", 17, INK_DIM),
                      mono("one wrong sentence", 14, INK_FAINT)).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        labB = VGroup(mono("reader B", 17, INK_DIM),
                      mono("one wrong sentence", 14, INK_FAINT)).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        labA.next_to(ax, LEFT, buff=0.18).align_to(ax, UP)
        labB.next_to(labA, DOWN, buff=0.26).align_to(labA, LEFT)

        # the live marker tick, parked at 26% (worst) end — the unsolved problem
        live = Line([xpos(26.0), ry - 0.17, 0], [xpos(26.0), ry + 0.17, 0],
                    stroke_color=INK, stroke_width=3.4)

        self.play(
            Create(track), FadeIn(cap26), FadeIn(cap0), FadeIn(cap_lab), FadeIn(cap_dir),
            Create(ax),
            run_time=0.55,
        )
        self.play(Create(gA), Create(gB), FadeIn(labA), FadeIn(labB), run_time=0.6)
        self.play(GrowFromCenter(live), Indicate(cap26, scale_factor=1.14, color=INK),
                  run_time=0.4)
        self.wait(0.13)

        # ============================================================== #
        #  BEAT 2 — AVERAGE: sweep, two wobbles merge into one ribbon     #
        # ============================================================== #
        self.next_section("average")

        sweep = Line(ax.c2p(0, 0), ax.c2p(0, 1.0), stroke_color=INK, stroke_width=2.6).set_opacity(0.75)
        self.add(sweep)
        self.play(sweep.animate.move_to(ax.c2p(10, 0.5)), run_time=0.8, rate_func=linear)
        self.play(FadeOut(sweep), run_time=0.15)

        gAvg = glow(graph(yAvg, INK, 3.6, 1.0))
        labAvg = mono("average", 19, INK)
        labAvg.next_to(ax, LEFT, buff=0.18).move_to((labA.get_center() + labB.get_center()) / 2)
        self.play(
            ReplacementTransform(VGroup(gA, gB), gAvg),
            ReplacementTransform(VGroup(labA, labB), labAvg),
            run_time=0.85,
        )
        self.wait(0.13)

        # ============================================================== #
        #  BEAT 3 — NUDGE: marker walks 26% -> ~20%; "+ average" pulses    #
        # ============================================================== #
        self.next_section("nudge")

        m20 = Line([xpos(20.0), ry - 0.17, 0], [xpos(20.0), ry + 0.17, 0],
                   stroke_color=INK, stroke_width=3.4)
        cap20 = mono("~20%", 22, INK).move_to([xpos(20.0), ry - 0.42, 0])
        cap20_t = mono("+ average", 15, INK_FAINT).move_to([xpos(20.0), ry + 0.40, 0])
        pulse = Dot(color=INK, radius=0.06).move_to([xpos(26.0), ry, 0])
        self.add(pulse)
        self.play(
            pulse.animate.move_to([xpos(20.0), ry, 0]),
            Transform(live, m20),
            cap26.animate.set_color(INK_FAINT),
            run_time=0.55, rate_func=smooth,
        )
        self.remove(pulse)
        # FadeIn first, THEN Indicate in a separate play — combining them lets
        # Indicate's there-and-back restore cap20 to its pre-FadeIn opacity (0).
        self.play(FadeIn(cap20), FadeIn(cap20_t), run_time=0.3)
        self.play(Indicate(cap20, scale_factor=1.12, color=INK), run_time=0.35)

        # ============================================================== #
        #  BEAT 4 — TURN: still demanding ONE answer; peel into n-best     #
        # ============================================================== #
        self.next_section("turn")

        token = list_token(4, 1.9, INK, 0.34).move_to([0, CY + 0.1, 0])
        token_glow = glow(token.copy())
        tok_cap = mono("still one answer — keep a list?", 16, INK).next_to(token, DOWN, buff=0.22)
        self.add(token_glow)
        self.play(
            ReplacementTransform(VGroup(ax, gAvg, labAvg), token),
            FadeIn(tok_cap),
            run_time=0.55,
        )
        token_glow.move_to(token).set_opacity(0.0)
        self.wait(0.14)

        # ============================================================== #
        #  BEAT 5 — POOL: candidates fan; dial-lists pour into the cloud   #
        # ============================================================== #
        self.next_section("pool")

        # the shortlist fans down (opacity gradient), true answer buried at rank 4
        cands = [
            ("the quick brown box", False),
            ("a quick brown fox", False),
            ("the quink brown fox", False),
            ("the quick brown fox", True),
            ("the quick brow fox", False),
        ]
        rows = VGroup()
        for i, (c, _) in enumerate(cands):
            rank = mono(f"{i+1}.", 18, INK_FAINT)
            txt = mono(c, 20, INK)
            rows.add(VGroup(rank, txt).arrange(RIGHT, buff=0.28))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-2.5, CY + 0.05, 0])
        for i, row in enumerate(rows):
            row.set_opacity(1.0 - 0.13 * i)
        moredots = mono("...  dozens more", 16, INK_GHOST).next_to(rows, DOWN, buff=0.18, aligned_edge=LEFT)

        self.play(
            FadeOut(VGroup(token, tok_cap)),
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.1),
            run_time=0.6,
        )
        self.play(FadeIn(moredots), run_time=0.2)

        # collapse the shortlist into three dial-labelled list-tokens at left
        dials = VGroup()
        for lab in ("dial ×1", "dial ×2", "dial ×4"):
            lst = list_token(3, 1.5, INK_FAINT, 0.26)
            cap = mono(lab, 14, INK_FAINT).next_to(lst, DOWN, buff=0.12)
            dials.add(VGroup(lst, cap))
        dials.arrange(DOWN, buff=0.42, aligned_edge=LEFT).move_to([-4.6, CY, 0])

        self.play(
            ReplacementTransform(VGroup(rows, moredots), dials[0][0]),
            FadeIn(dials[0][1]),
            run_time=0.5,
        )
        self.play(LaggedStart(*[FadeIn(dials[k], shift=DOWN * 0.18) for k in (1, 2)],
                              lag_ratio=0.3), run_time=0.45)

        pool = RoundedRectangle(width=3.6, height=2.9, corner_radius=0.14,
                                stroke_color=INK, stroke_width=2.0,
                                fill_color=INK_GHOST, fill_opacity=0.08).move_to([3.1, CY, 0])
        pool_title = mono("pooled candidates", 18, INK, w=BOLD).next_to(pool, UP, buff=0.14)
        self.play(Create(pool), FadeIn(pool_title), run_time=0.35)

        count = ValueTracker(0)
        readout = counter(count, fmt=lambda v: str(round(v)), s=60, c=INK,
                          at=pool.get_center() + UP * 0.30)
        cap_count = mono("candidates", 15, INK_DIM).move_to(pool.get_center() + DOWN * 0.55)
        self.add(readout)

        arrows = VGroup(*[
            Line(dials[k][0].get_right() + RIGHT * 0.12, pool.get_left() + LEFT * 0.12,
                 stroke_width=1.8, color=INK_FAINT)
            for k in range(3)
        ])
        heads = VGroup(*[tri(-PI / 2, INK_FAINT, 1.0, 0.07).move_to(ln.get_end()) for ln in arrows])

        rng = np.random.default_rng(7)
        pc = pool.get_center()
        pw, ph = 3.6 - 0.6, 2.9 - 0.9
        all_dots = [
            Dot([pc[0] + (rng.random() - 0.5) * pw, pc[1] + (rng.random() - 0.5) * ph + 0.05, 0],
                radius=0.035, color=INK).set_opacity(0.7)
            for _ in range(30)
        ]
        targets, dot_cuts, prev = [38, 71, 94], [10, 21, 30], 0
        for k in range(3):
            p = Dot(color=INK, radius=0.06).move_to(arrows[k].get_start())
            self.add(p)
            batch = VGroup(*all_dots[prev:dot_cuts[k]])
            self.play(
                Create(arrows[k]), FadeIn(heads[k]),
                p.animate.move_to(arrows[k].get_end()),
                count.animate.set_value(targets[k]),
                LaggedStartMap(FadeIn, batch, lag_ratio=0.05, scale=0.6),
                run_time=0.45, rate_func=linear,
            )
            self.remove(p)
            prev = dot_cuts[k]
        readout.clear_updaters()
        self.play(FadeIn(cap_count), run_time=0.2)

        # ============================================================== #
        #  BEAT 6 — IN-POOL: the true-answer dot travels in and flashes    #
        # ============================================================== #
        self.next_section("in_pool")

        # dim the dial-lists now the count has landed — focus shifts to the cloud
        self.play(VGroup(dials, arrows, heads).animate.set_opacity(0.30), run_time=0.3)

        true_dot = Dot([pc[0] - 0.2, pc[1] - 0.15, 0], radius=0.06, color=WHITE)
        glow_dot = glow(true_dot.copy())
        in_caption = mono("the right answer is in the pool", 16, INK).next_to(pool, DOWN, buff=0.28)
        travel = Dot(color=WHITE, radius=0.06).move_to(dials[1][0].get_right())
        self.add(travel)
        self.play(travel.animate.move_to(true_dot.get_center()), run_time=0.7, rate_func=smooth)
        self.remove(travel)
        self.add(glow_dot)
        self.play(FadeIn(in_caption),
                  Flash(true_dot, color=WHITE, line_length=0.12, num_lines=10, flash_radius=0.22),
                  run_time=0.6)
        self.wait(0.2)

        # ============================================================== #
        #  BEAT 7 — ORACLE: the 9.30% perfect-chooser tick grows far right #
        # ============================================================== #
        self.next_section("oracle")

        beat56 = VGroup(dials, arrows, heads, pool, pool_title, readout,
                        cap_count, glow_dot, in_caption, *all_dots)
        line = mono("if you could always grab the best candidate —", 19, INK_FAINT).move_to([0, CY + 0.2, 0])
        self.play(FadeOut(beat56), FadeIn(line), run_time=0.55)

        m_or = Line([xpos(9.30), ry - 0.20, 0], [xpos(9.30), ry + 0.20, 0],
                    stroke_color=INK, stroke_width=4.2)
        cap_or = num("9.30%", 24, INK).move_to([xpos(9.30), ry - 0.42, 0])
        cap_or_t = mono("perfect chooser", 15, INK).move_to([xpos(9.30), ry + 0.40, 0])
        mover = Dot(color=WHITE, radius=0.06).move_to([xpos(20.0), ry, 0])
        self.add(mover)
        self.play(GrowFromCenter(m_or), FadeIn(cap_or), FadeIn(cap_or_t),
                  mover.animate.move_to([xpos(9.30), ry, 0]),
                  run_time=0.85, rate_func=smooth)
        self.remove(mover)
        self.add(glow(m_or))
        self.wait(0.5)

        # ============================================================== #
        #  BEAT 8 — PRIZE: the headroom band fills the gap (#fff payoff)   #
        # ============================================================== #
        self.next_section("prize")

        band = Rectangle(width=abs(xpos(20.0) - xpos(9.30)), height=0.30,
                         stroke_width=0, fill_color=INK, fill_opacity=0.13)
        band.move_to([(xpos(20.0) + xpos(9.30)) / 2, ry, 0])

        gy = ry + 1.02
        dtop, dbot = gy - 0.10, ry + 0.66
        dl = DashedLine([xpos(20.0), dbot, 0], [xpos(20.0), dtop, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2, dash_length=0.06)
        dr = DashedLine([xpos(9.30), dbot, 0], [xpos(9.30), dtop, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2, dash_length=0.06)
        gspan = Line([xpos(9.30), gy, 0], [xpos(20.0), gy, 0], stroke_color=INK, stroke_width=2.2)
        gl = tri(PI / 2, INK, 1.0, 0.08).move_to([xpos(9.30), gy, 0])
        gr = tri(-PI / 2, INK, 1.0, 0.08).move_to([xpos(20.0), gy, 0])

        payoff = serif("that gap is the prize", 36, WHITE).move_to([0, CY + 0.1, 0])
        sub = mono("the right answer is already here — find it", 17, INK_FAINT).next_to(payoff, DOWN, buff=0.26)
        payoff_glow = glow(payoff.copy())
        self.add(payoff_glow)

        self.play(FadeOut(line), FadeIn(band), Create(dl), Create(dr), run_time=0.4)
        self.play(GrowFromCenter(gspan), FadeIn(gl), FadeIn(gr), run_time=0.4)
        self.play(FadeIn(payoff, shift=UP * 0.08), FadeIn(sub),
                  Indicate(payoff, scale_factor=1.08, color=WHITE),
                  payoff_glow.animate.set_opacity(0.0), run_time=0.5)
        self.remove(payoff_glow)

        # final poster hold
        self.wait(0.35)


if __name__ == "__main__":
    pass
