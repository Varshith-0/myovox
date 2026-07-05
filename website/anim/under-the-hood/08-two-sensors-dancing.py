# website/anim/b01_two_sensors_dancing.py  —  B01 "Two dancers"
#
# Bridges features-window (50 snapshots/sec) -> features-cov (31x31 grid).
# The "aha": covariance is ONE number for whether two signals rise and fall
# TOGETHER (positive, up-tilted cloud), AGAINST (negative, down-tilted), or
# with NO relationship (near zero, round blob) — and it has nothing to do with
# loudness.
#
# Locked 7-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 watch TWO   (1.37s) title "forget thirty-one — watch just TWO"; two traces
#                          pull out of the bundle (sensor A / sensor B).
#   2 ask one Q   (1.84s) scatter axes "plot B against A" fade in EMPTY, waiting;
#                          scrub line poised at the left edge.
#   3 TOGETHER    (1.30s) sweep -> up-diagonal cloud; cov ticks positive; sign
#                          marker slides RIGHT to "together".
#   4 AGAINST     (1.82s) B flips to its mirror; down-diagonal cloud; cov negative;
#                          sign marker slides LEFT to "against".
#   5 UNRELATED   (1.57s) B independent; round blob; cov ~zero; sign centres "none".
#   6 loudness    (1.83s) back to TOGETHER cloud; caption "B is half as loud — the
#                          SIGN is unchanged"; the cov number is spotlit.
#   7 covariance  (2.22s) traces+plot fade; the tilt collapses into the number,
#                          which grows into serif #fff "covariance" + one-line gloss.
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

# Zone geometry — keep everything inside x in [-7,7], y in [-3.9,3.9].
TRACE_X = -2.95         # centre x of the live trace pair (left mechanism)
TRACE_W = 4.5           # width of each trace
PLOT_C = np.array([3.7, 0.35, 0])   # scatter-plot centre (right mechanism)
PLOT_R = 1.35           # scatter-plot half-extent
SAMPLES = 64            # samples per regime sweep


class TwoSensorsDancing(Scene):
    def construct(self):
        seed()

        # ============================================================
        # SHARED DATA — three regimes share ONE underlying "A" wiggle.
        # B is built from A so the relationship is exact, not random-ish.
        # ============================================================
        t = np.linspace(0, 1, SAMPLES)
        a = (np.sin(2 * np.pi * 2.3 * t) + 0.6 * np.sin(2 * np.pi * 4.1 * t + 1.0)
             + 0.4 * np.sin(2 * np.pi * 6.7 * t + 2.0))
        a = a / np.max(np.abs(a))
        b_indep = (np.sin(2 * np.pi * 3.7 * t + 0.5) + 0.7 * np.sin(2 * np.pi * 5.9 * t)
                   + 0.5 * np.sin(2 * np.pi * 8.3 * t + 1.5))
        b_indep = b_indep / np.max(np.abs(b_indep))

        # Crucially DIFFERENT amplitudes: B is half as loud as A — yet the
        # covariance SIGN is identical, proving it is the DANCE not the loudness.
        AMP_A, AMP_B = 1.0, 0.5
        regimes = {
            "together": AMP_B * a,            # B = scaled copy of A  -> positive
            "against":  -AMP_B * a,           # B = mirror of A       -> negative
            "unrelated": AMP_B * b_indep,     # B independent          -> ~zero
        }

        def cov(b):
            ca = a - a.mean()
            cb = b - b.mean()
            return float(np.mean(ca * cb))

        # geometry of the left trace band
        yA, yB = 1.15, -0.55
        xs_trace = np.linspace(TRACE_X - TRACE_W / 2, TRACE_X + TRACE_W / 2, SAMPLES)
        VSCALE = 0.55

        def make_trace(vals, y0, amp=1.0, op=0.95, w=2.2):
            pts = [[xs_trace[i], y0 + amp * vals[i] * VSCALE, 0] for i in range(SAMPLES)]
            m = VMobject(stroke_color=INK, stroke_width=w, fill_opacity=0.0)
            m.set_points_smoothly(pts)
            m.set_stroke(INK, width=w, opacity=op)
            m.set_fill(opacity=0.0)
            return m

        def plot_point(av, bv):
            return PLOT_C + np.array([av * PLOT_R * 0.82, bv * PLOT_R * 0.82, 0])

        # ============================================================
        # BEAT 1 — WATCH TWO (1.37s): title + two traces pull out.
        # ============================================================
        self.next_section("watch_two")

        title = mono("forget 31", 22, INK_DIM)
        title.move_to([0, 3.5, 0])
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.4)

        baseA = Line([TRACE_X - TRACE_W / 2, yA, 0], [TRACE_X + TRACE_W / 2, yA, 0],
                     stroke_color=INK_GHOST, stroke_width=1.0)
        baseB = Line([TRACE_X - TRACE_W / 2, yB, 0], [TRACE_X + TRACE_W / 2, yB, 0],
                     stroke_color=INK_GHOST, stroke_width=1.0)
        labA = mono("sensor A", 17, INK_DIM).next_to(baseA, LEFT, buff=0.26)
        labB = mono("sensor B", 17, INK_DIM).next_to(baseB, LEFT, buff=0.26)

        traceA = make_trace(a, yA, AMP_A)
        traceB = make_trace(regimes["together"] / AMP_B, yB, AMP_B)

        self.play(Create(baseA), Create(baseB), FadeIn(labA), FadeIn(labB),
                  run_time=0.4)
        self.play(Create(traceA), Create(traceB), run_time=0.45)
        self.wait(0.12)

        # ============================================================
        # BEAT 2 — ASK ONE QUESTION (1.84s): empty scatter axes appear.
        # Dim title to ghost now that beat 1 is established.
        # ============================================================
        self.next_section("ask")

        ax_x = Line(PLOT_C + LEFT * PLOT_R, PLOT_C + RIGHT * PLOT_R,
                    stroke_color=INK_FAINT, stroke_width=1.4)
        ax_y = Line(PLOT_C + DOWN * PLOT_R, PLOT_C + UP * PLOT_R,
                    stroke_color=INK_FAINT, stroke_width=1.4)
        plot_box = Square(PLOT_R * 2 + 0.2, stroke_color=INK_GHOST,
                          stroke_width=1.0, fill_opacity=0).move_to(PLOT_C)
        ax_lbl_x = mono("A's height", 13, INK_FAINT).next_to(plot_box, DOWN, buff=0.14).set_x(PLOT_C[0])
        ax_lbl_y = mono("B's height", 13, INK_FAINT).rotate(PI / 2).next_to(plot_box, LEFT, buff=0.16).set_y(PLOT_C[1])
        plot_title = mono("plot B against A", 15, INK_FAINT).next_to(plot_box, UP, buff=0.16)

        # sign-track + live covariance readout
        track_y = -2.7
        track = Line([-2.6, track_y, 0], [2.6, track_y, 0],
                     stroke_color=INK_GHOST, stroke_width=1.4).set_x(0)
        tick_against = Line([-2.6, track_y - 0.1, 0], [-2.6, track_y + 0.1, 0],
                            stroke_color=INK_GHOST, stroke_width=1.4)
        tick_none = Line([0, track_y - 0.1, 0], [0, track_y + 0.1, 0],
                         stroke_color=INK_GHOST, stroke_width=1.4)
        tick_together = Line([2.6, track_y - 0.1, 0], [2.6, track_y + 0.1, 0],
                             stroke_color=INK_GHOST, stroke_width=1.4)
        lbl_against = mono("against", 14, INK_FAINT).next_to(tick_against, DOWN, buff=0.14)
        lbl_none = mono("none", 14, INK_FAINT).next_to(tick_none, DOWN, buff=0.14)
        lbl_together = mono("together", 14, INK_FAINT).next_to(tick_together, DOWN, buff=0.14)
        track_grp = VGroup(track, tick_against, tick_none, tick_together,
                           lbl_against, lbl_none, lbl_together)
        sign_dot = Dot(radius=0.07, color=INK).move_to([0, track_y, 0])

        covT = ValueTracker(0.0)
        cov_read = counter(covT, fmt=lambda v: f"{v:+.2f}", s=40, c=INK,
                           at=[0, -3.45, 0])
        cov_tag = mono("covariance", 15, INK_FAINT).next_to(cov_read, LEFT, buff=0.22)
        cov_tag.add_updater(lambda m: m.next_to(cov_read, LEFT, buff=0.22))

        scrub = Line([0, yA + 1.0, 0], [0, yB - 1.0, 0],
                     stroke_color=WHITE, stroke_width=2.0).set_opacity(0.7)
        scrub.move_to([xs_trace[0], (yA + yB) / 2, 0])

        self.play(title.animate.set_color(INK_GHOST),
                  Create(plot_box), Create(ax_x), Create(ax_y),
                  FadeIn(ax_lbl_x), FadeIn(ax_lbl_y), FadeIn(plot_title),
                  run_time=0.7)
        self.play(FadeIn(track_grp), FadeIn(sign_dot), run_time=0.45)
        self.add(cov_read)
        self.play(FadeIn(cov_read), FadeIn(cov_tag), FadeIn(scrub), run_time=0.35)
        self.wait(0.34)

        # ============================================================
        # A reusable sweep: scrub crosses both traces, drops a dot trail in the
        # plot, settles the cloud + sign marker + covariance number. Monotonic
        # L->R so it reads at any scrubbed frame.
        # ============================================================
        def run_sweep(b_vals, label_text, target_cov, sign_x, run_time=1.0):
            dots = VGroup()
            self.add(dots)
            cap = mono(label_text, 18, INK).move_to([PLOT_C[0], 2.55, 0])

            sweepT = ValueTracker(0.0)

            def upd_scrub(m):
                f = sweepT.get_value()
                x = xs_trace[0] + f * (xs_trace[-1] - xs_trace[0])
                m.move_to([x, (yA + yB) / 2, 0])
            scrub.add_updater(upd_scrub)

            pts = [plot_point(a[i], b_vals[i]) for i in range(SAMPLES)]
            for p in pts:
                d = Dot(radius=0.05, color=INK, fill_opacity=0.0).move_to(p)
                dots.add(d)

            def upd_dots(m):
                lit = sweepT.get_value() * (SAMPLES - 1)
                for i, d in enumerate(m):
                    d.set_opacity(0.85 if i <= lit else 0.0)
            dots.add_updater(upd_dots)

            self.play(FadeIn(cap, shift=DOWN * 0.06), run_time=0.22)
            self.play(sweepT.animate.set_value(1.0),
                      covT.animate.set_value(target_cov),
                      sign_dot.animate.move_to([sign_x, track_y, 0]),
                      run_time=run_time, rate_func=linear)
            scrub.clear_updaters()
            dots.clear_updaters()
            for d in dots:
                d.set_opacity(0.7)
            return dots, cap

        # ============================================================
        # BEAT 3 — TOGETHER (1.30s): up-diagonal cloud, sign RIGHT.
        # ============================================================
        self.next_section("together")

        c1 = cov(regimes["together"])
        dots1, cap1 = run_sweep(regimes["together"], "move TOGETHER",
                                c1, 2.6 * 0.85, run_time=0.85)
        self.play(Indicate(sign_dot, scale_factor=1.4, color=WHITE), run_time=0.23)

        # ============================================================
        # BEAT 4 — AGAINST (1.82s): B flips to its mirror; down-diagonal, sign LEFT.
        # ============================================================
        self.next_section("against")

        self.play(FadeOut(dots1), FadeOut(cap1), run_time=0.28)
        newB = make_trace(regimes["against"] / AMP_B, yB, AMP_B)
        self.play(Transform(traceB, newB), run_time=0.4)
        c2 = cov(regimes["against"])
        dots2, cap2 = run_sweep(regimes["against"], "move AGAINST",
                                c2, -2.6 * 0.85, run_time=0.7)
        self.play(Indicate(sign_dot, scale_factor=1.4, color=WHITE), run_time=0.22)

        # ============================================================
        # BEAT 5 — UNRELATED (1.57s): B independent; round blob; sign centres.
        # ============================================================
        self.next_section("unrelated")

        self.play(FadeOut(dots2), FadeOut(cap2), run_time=0.3)
        newB = make_trace(regimes["unrelated"] / AMP_B, yB, AMP_B)
        self.play(Transform(traceB, newB), run_time=0.45)
        c3 = cov(regimes["unrelated"])
        dots3, cap3 = run_sweep(regimes["unrelated"], "no relationship",
                                c3, 0.0, run_time=0.6)
        self.play(Indicate(sign_dot, scale_factor=1.4, color=WHITE), run_time=0.2)

        # ============================================================
        # BEAT 6 — LOUDNESS (1.83s): back to TOGETHER cloud; "half as loud — the
        # SIGN is unchanged"; spotlight the covariance number.
        # ============================================================
        self.next_section("loudness")

        self.play(FadeOut(dots3), FadeOut(cap3), run_time=0.25)
        newB = make_trace(regimes["together"] / AMP_B, yB, AMP_B)
        self.play(Transform(traceB, newB), run_time=0.35)
        c1b = cov(regimes["together"])
        dots4, cap4 = run_sweep(regimes["together"], "move TOGETHER",
                                c1b, 2.6 * 0.85, run_time=0.45)

        loud = mono("B is half as loud as A — the SIGN is unchanged", 15, INK_FAINT)
        loud.move_to([0, -1.55, 0])
        self.play(FadeIn(loud, shift=UP * 0.08), run_time=0.3)

        covT.clear_updaters()
        cov_read.clear_updaters()
        cov_tag.clear_updaters()
        self.play(Indicate(cov_read, scale_factor=1.25, color=WHITE), run_time=0.4)

        # ============================================================
        # BEAT 7 — COVARIANCE (2.22s): traces+plot fade; the tilt collapses into
        # the number, which grows into the serif #fff payoff.
        # ============================================================
        self.next_section("name")

        left_grp = VGroup(traceA, traceB, baseA, baseB, labA, labB,
                          dots4, cap4, scrub, loud, title)
        plot_grp = VGroup(plot_box, ax_x, ax_y, ax_lbl_x, ax_lbl_y, plot_title)
        self.play(FadeOut(left_grp, shift=LEFT * 0.2),
                  FadeOut(plot_grp),
                  FadeOut(track_grp), FadeOut(sign_dot),
                  FadeOut(cov_read),
                  cov_tag.animate.set_opacity(0.0),
                  run_time=0.5)

        payoff = serif("covariance", 54, WHITE).move_to([0, 0.5, 0])
        payoff_g = glow(payoff)
        sub = mono("one number for how two move together", 18, INK_DIM)
        sub.next_to(payoff, DOWN, buff=0.24)

        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  Flash([0, 0.5, 0], color=WHITE, line_length=0.2, num_lines=14,
                        flash_radius=1.5, time_width=0.4),
                  run_time=0.55)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.4)

        # poster hold
        self.wait(0.6)


if __name__ == "__main__":
    pass
