# website/anim/b04_how_training_works.py — B04 "Rolling downhill" (how training works)
#
# Carries the dial-box from b03 (what-is-a-net): a layered function whose guess
# starts garbled because its dials are random. This clip teaches the ONE loop:
#   guess  ->  measure how wrong (the error)  ->  step downhill  ->  repeat.
# Gradient descent without the jargon — the error is the HEIGHT of a hill, the
# dials are the POSITION on it, and a single ball rolls to the valley floor while
# the guessed letter sharpens toward the true answer over millions of passes.
#
# Locked 7-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 pose (~2.01s)   garbled guess beside the KNOWN answer 'A'; dial-box dim anchor
#   2 error (~1.49s)  a small bracket links guess<->answer; the word "error" appears
#                     once as the measured gap — NO hill yet
#   3 hill (~2.23s)   the 1-D curve draws: y = "error" (height), x = "the dials"
#                     (position); the ball appears high on the left slope
#   4 downhill (~1.83s) a short downhill arrow flicks on at the ball; spotlight the
#                     ball, dim the dial-box + answer card
#   5 step (~1.31s)   ball rolls ONE notch; error bracket shrinks; guess sharpens a
#                     touch toward 'A'; pass counter ticks up
#   6 free-run (~1.73s) ball free-runs to the valley; counter races to millions;
#                     dials rotate to settled angles
#   7 name (~1.37s)   ball nestles (settle flash); sharp 'A' matches; serif #fff
#                     payoff "shrink the error"; brief poster hold
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

TOP_Y = 3.1
CENTER_Y = 0.25
BOT_Y = -3.05
X_L = -6.6
X_R = 6.6


def tri(angle, c, op=1.0, s=0.08):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def flat_arrow(start, end, c=INK_FAINT, w=2.0):
    """Thin shaft + triangular head — avoids the Arrow tip glitch."""
    shaft = Line(start, end, stroke_color=c, stroke_width=w)
    head = tri(shaft.get_angle() - PI / 2, c, 1.0, 0.085).move_to(shaft.get_end())
    return VGroup(shaft, head)


def dial(r=0.12, angle=0.0, op=1.0, sw=1.6):
    """A small knob: a ring with a pointer line at `angle` (radians, 0 = right)."""
    ring = Circle(radius=r, color=INK, stroke_color=INK, stroke_width=sw,
                  fill_opacity=0)
    pt = Line(ORIGIN, r * np.array([np.cos(angle), np.sin(angle), 0]),
              color=INK, stroke_color=INK, stroke_width=sw)
    return VGroup(ring, pt).set_stroke(INK).set_opacity(op)


class HowTrainingWorks(Scene):
    def construct(self):
        seed()

        # the carried dial-box anchor (TOP, permanently dim — never re-brightened).
        top_grp, dials, dial_angles, rng = self._build_dialbox_anchor()

        # CENTER pose: garbled guess vs the known answer.
        (guess_box, true_box, garble, true_glyph, sharp_guess,
         guess_at, true_at) = self._beat1_pose()

        # the word "error" as the measured gap between guess and answer.
        gap_bracket, err_word = self._beat2_error(guess_box, true_box)

        # the error hill + ball + drop-line; a shared tracker drives the descent.
        (roll, ball, curve, curve_x, curve_y, t_min, hill_cx, hill_cy, hill_h,
         hill_grp) = self._beat3_hill(gap_bracket, err_word)

        # spotlight the ball; the downhill direction arrow.
        downhill, phase = self._beat4_downhill(
            roll, ball, curve_x, curve_y, t_min,
            true_box, true_glyph, top_grp)

        # the live pass counter + the shrinking error bracket.
        passes, pass_read, pass_cap, err_bracket = self._build_descent_machinery(
            roll, ball, curve_x, hill_cy, hill_h)

        # one notch step: ball rolls a notch, guess sharpens, counter ticks.
        self._beat5_step(roll, passes, garble, sharp_guess, t_min, phase,
                         hill_cx, hill_cy, hill_h)

        # free-run to the valley; counter races; dials settle.
        self._beat6_freerun(roll, passes, dials, dial_angles, rng,
                            garble, sharp_guess, t_min, phase,
                            hill_cx, hill_cy, hill_h)

        # the payoff: ball nestles, 'A' matches, #fff "shrink the error".
        self._beat7_name(ball, err_bracket, sharp_guess, guess_box, true_box,
                        true_glyph, passes, pass_read, pass_cap, phase, downhill,
                        hill_grp, top_grp)

    # -----------------------------------------------------------------
    # TOP anchor — the carried dial-box (built once, dimmed, never re-lit).
    # -----------------------------------------------------------------
    def _build_dialbox_anchor(self):
        in_lbl = mono("numbers in", 16, INK_GHOST).move_to([X_L + 0.9, TOP_Y, 0])
        fp_hh = 0.08 + 0.26 * np.abs(np.random.randn(7))
        fp = VGroup()
        for h in fp_hh:
            fp.add(Rectangle(width=0.05, height=float(h), stroke_width=0,
                             fill_color=INK, fill_opacity=0.7))
        fp.arrange(RIGHT, buff=0.03, aligned_edge=DOWN)
        fp.next_to(in_lbl, RIGHT, buff=0.28)

        box = RoundedRectangle(width=2.5, height=1.15, corner_radius=0.08,
                               stroke_color=INK_FAINT, stroke_width=1.4,
                               fill_color=BG, fill_opacity=1.0)
        box.move_to([0.1, TOP_Y, 0])
        rng = np.random.default_rng(11)
        dial_angles = rng.uniform(0, 2 * PI, 9)
        dials = VGroup()
        for di in range(9):
            d = dial(r=0.11, angle=float(dial_angles[di]), op=0.92, sw=1.6)
            col, row = di % 3, di // 3
            d.move_to([box.get_x() + (col - 1) * 0.72,
                       box.get_y() + (row - 1) * 0.40, 0])
            dials.add(d)
        box_lbl = mono("the dials", 13, INK_GHOST).next_to(box, DOWN, buff=0.10)

        thread_in = flat_arrow([fp.get_right()[0] + 0.12, TOP_Y, 0],
                               [box.get_left()[0] - 0.06, TOP_Y, 0], INK_GHOST, 1.6)
        out_lbl = mono("a guess", 16, INK_GHOST).move_to([X_R - 0.95, TOP_Y, 0])
        thread_out = flat_arrow([box.get_right()[0] + 0.06, TOP_Y, 0],
                                [out_lbl.get_left()[0] - 0.12, TOP_Y, 0],
                                INK_GHOST, 1.6)

        top_grp = VGroup(in_lbl, fp, box, dials, box_lbl, thread_in,
                         thread_out, out_lbl)
        rule = Line([X_L, TOP_Y - 0.95, 0], [X_R, TOP_Y - 0.95, 0],
                    stroke_color=LINE, stroke_width=1.2)

        self.add(rule)
        self.play(FadeIn(top_grp, shift=DOWN * 0.06), run_time=0.45)
        top_grp.set_opacity(0.45)
        return top_grp, dials, dial_angles, rng

    # -----------------------------------------------------------------
    # BEAT 1 — POSE (~2.01s): garbled guess beside the KNOWN answer 'A'.
    # -----------------------------------------------------------------
    def _beat1_pose(self):
        self.next_section("pose")

        guess_at = np.array([4.55, CENTER_Y + 1.05, 0])
        true_at = np.array([4.55, CENTER_Y - 0.75, 0])
        guess_box = RoundedRectangle(width=1.4, height=1.05, corner_radius=0.08,
                                     stroke_color=INK_GHOST, stroke_width=1.3,
                                     fill_opacity=0).move_to(guess_at)
        true_box = RoundedRectangle(width=1.4, height=1.05, corner_radius=0.08,
                                    stroke_color=INK_FAINT, stroke_width=1.3,
                                    fill_opacity=0).move_to(true_at)
        guess_cap = mono("its guess", 14, INK_FAINT).next_to(guess_box, UP, buff=0.12)
        true_cap = mono("known answer", 14, INK_DIM).next_to(true_box, DOWN, buff=0.12)

        garble = VGroup(
            serif("E", 46, INK_GHOST).rotate(0.18).shift([-0.06, 0.02, 0]),
            serif("Z", 46, INK_GHOST).rotate(-0.22).shift([0.07, -0.03, 0]),
            serif("S", 46, INK_FAINT).rotate(0.05),
        ).move_to(guess_box)
        true_glyph = serif("A", 46, INK_DIM).move_to(true_box)

        # the sharpened guess target, hidden for now.
        sharp_guess = serif("A", 46, INK).move_to(guess_box).set_opacity(0.0)

        self.play(FadeIn(guess_box), FadeIn(guess_cap),
                  FadeIn(garble), run_time=0.55)
        self.play(FadeIn(true_box), FadeIn(true_cap),
                  FadeIn(true_glyph, shift=UP * 0.1), run_time=0.5)
        self.play(Indicate(garble, scale_factor=1.06, color=INK_FAINT),
                  run_time=0.55)
        self.wait(0.25)

        # keep caps grouped with their boxes for later dimming.
        guess_box.add(guess_cap)
        true_box.add(true_cap)
        self.add(sharp_guess)
        return (guess_box, true_box, garble, true_glyph, sharp_guess,
                guess_at, true_at)

    # -----------------------------------------------------------------
    # BEAT 2 — ERROR (~1.49s): bracket links guess<->answer; the word "error".
    # -----------------------------------------------------------------
    def _beat2_error(self, guess_box, true_box):
        self.next_section("error")

        gap_bracket = flat_arrow(guess_box.get_bottom() + DOWN * 0.04,
                                 true_box.get_top() + UP * 0.04,
                                 INK_FAINT, 2.4)
        err_word = mono("error", 18, INK).next_to(gap_bracket, LEFT, buff=0.18)

        self.play(Create(gap_bracket[0]), FadeIn(gap_bracket[1]), run_time=0.55)
        self.play(FadeIn(err_word, shift=RIGHT * 0.08),
                  Indicate(err_word, scale_factor=1.12, color=INK), run_time=0.6)
        self.wait(0.2)
        return gap_bracket, err_word

    # -----------------------------------------------------------------
    # BEAT 3 — HILL (~2.23s): the 1-D curve; error = height, dials = position.
    # -----------------------------------------------------------------
    def _beat3_hill(self, gap_bracket, err_word):
        self.next_section("hill")

        # the "error" gap migrates into the hill's y-axis meaning.
        self.play(FadeOut(gap_bracket), FadeOut(err_word, shift=LEFT * 0.1),
                  run_time=0.35)

        hill_cx, hill_cy = -2.4, CENTER_Y - 0.25
        hill_w, hill_h = 5.6, 2.5
        x_axis = Line([hill_cx - hill_w / 2, hill_cy - hill_h / 2, 0],
                      [hill_cx + hill_w / 2, hill_cy - hill_h / 2, 0],
                      stroke_color=INK_GHOST, stroke_width=1.2)
        y_axis = Line([hill_cx - hill_w / 2, hill_cy - hill_h / 2, 0],
                      [hill_cx - hill_w / 2, hill_cy + hill_h / 2 + 0.1, 0],
                      stroke_color=INK_GHOST, stroke_width=1.2)
        err_lbl = mono("error", 15, INK_FAINT).rotate(PI / 2)
        err_lbl.next_to(y_axis, LEFT, buff=0.12)
        dials_lbl = mono("the dials", 14, INK_FAINT).next_to(x_axis, DOWN, buff=0.16)

        t_min = 0.62

        def curve_y(t):
            return hill_cy - hill_h / 2 + hill_h * (2.6 * (t - t_min) ** 2 + 0.04)

        def curve_x(t):
            return hill_cx - hill_w / 2 + 0.18 + t * (hill_w - 0.36)

        curve = VMobject(stroke_color=INK, stroke_width=2.2)
        pts = [[curve_x(t), curve_y(t), 0] for t in np.linspace(0, 1, 80)]
        curve.set_points_smoothly(pts)

        self.play(Create(x_axis), Create(y_axis),
                  FadeIn(err_lbl), FadeIn(dials_lbl), run_time=0.55)
        self.play(Create(curve), run_time=0.7)

        # the ball, high up the left slope. The shared tracker drives everything.
        roll = ValueTracker(0.06)
        ball = Dot(radius=0.11, color=INK, fill_opacity=1.0)
        ball.move_to([curve_x(0.06), curve_y(0.06) + 0.11, 0])

        def update_ball(m):
            t = roll.get_value()
            m.move_to([curve_x(t), curve_y(t) + 0.11, 0])
        ball.add_updater(update_ball)
        self.add(ball)
        self.play(FadeIn(ball, scale=0.5), run_time=0.3)
        self.wait(0.2)

        hill_grp = VGroup(x_axis, y_axis, err_lbl, dials_lbl, curve)
        return (roll, ball, curve, curve_x, curve_y, t_min,
                hill_cx, hill_cy, hill_h, hill_grp)

    # -----------------------------------------------------------------
    # BEAT 4 — DOWNHILL (~1.83s): downhill arrow; spotlight ball, dim the rest.
    # -----------------------------------------------------------------
    def _beat4_downhill(self, roll, ball, curve_x, curve_y, t_min,
                        true_box, true_glyph, top_grp):
        self.next_section("downhill")

        # dim the answer card + dial-box anchor so the ball is the focal object.
        # true_box[0] is the rounded outline (stroke-only); true_box[1] its caption.
        self.play(true_box[0].animate.set_stroke(opacity=0.3),
                  true_box[1].animate.set_opacity(0.3),
                  true_glyph.animate.set_opacity(0.3),
                  top_grp.animate.set_opacity(0.3),
                  run_time=0.4)

        # a short downhill direction arrow at the ball, pointing toward the valley.
        t0 = roll.get_value()
        bx, by = curve_x(t0), curve_y(t0) + 0.11
        tip = curve_x(t0 + 0.16)
        downhill = flat_arrow([bx + 0.1, by + 0.04, 0],
                              [tip, curve_y(t0 + 0.16) + 0.18, 0],
                              INK, 2.6)
        phase = mono("which way is downhill", 17, INK_DIM)
        phase.move_to([-2.4, CENTER_Y + 1.55, 0])

        self.play(FadeIn(phase, shift=DOWN * 0.06), run_time=0.4)
        self.play(Create(downhill[0]), FadeIn(downhill[1]),
                  Flash(ball.get_center(), color=INK, flash_radius=0.34,
                        line_length=0.08, num_lines=10),
                  run_time=0.65)
        self.wait(0.25)
        return downhill, phase

    # -----------------------------------------------------------------
    # Descent machinery — the live pass counter + shrinking error bracket.
    # -----------------------------------------------------------------
    def _build_descent_machinery(self, roll, ball, curve_x, hill_cy, hill_h):
        passes = ValueTracker(1.0)

        def fmt_pass(v):
            v = int(round(v))
            if v >= 1_000_000:
                return "x millions"
            if v >= 1000:
                return "x " + f"{v:,}"
            return "x " + str(v)

        pass_read = counter(passes, fmt=fmt_pass, s=40, c=INK,
                            at=[0, BOT_Y + 0.12, 0])
        pass_cap = mono("examples seen", 14, INK_GHOST)
        pass_cap.move_to([0, BOT_Y - 0.5, 0])
        self.add(pass_read)
        self.play(FadeIn(pass_cap), run_time=0.3)

        err_bracket = always_redraw(lambda: Line(
            [curve_x(roll.get_value()), hill_cy - hill_h / 2, 0],
            ball.get_center() + DOWN * 0.11,
            stroke_color=INK_FAINT, stroke_width=3.0))
        self.add(err_bracket)
        return passes, pass_read, pass_cap, err_bracket

    # -----------------------------------------------------------------
    # BEAT 5 — STEP (~1.31s): one notch downhill; guess sharpens; counter ticks.
    # -----------------------------------------------------------------
    def _beat5_step(self, roll, passes, garble, sharp_guess, t_min, phase,
                    hill_cx, hill_cy, hill_h):
        self.next_section("step")

        # the guess crossfades garble -> sharp in lockstep with the roll.
        def frac(v):
            return float(np.clip((v - 0.06) / (t_min - 0.06), 0, 1))

        garble.add_updater(lambda m: m.set_opacity(0.55 * (1 - frac(roll.get_value()))))
        sharp_guess.add_updater(lambda m: m.set_opacity(frac(roll.get_value())))

        new_phase = mono("one step downhill", 17, INK_DIM).move_to(phase)
        self.play(
            roll.animate.set_value(0.24),
            passes.animate.set_value(12),
            Transform(phase, new_phase),
            run_time=0.95, rate_func=smooth,
        )
        self.wait(0.2)

    # -----------------------------------------------------------------
    # BEAT 6 — FREE-RUN (~1.73s): roll to the valley; counter races; dials settle.
    # -----------------------------------------------------------------
    def _beat6_freerun(self, roll, passes, dials, dial_angles, rng,
                       garble, sharp_guess, t_min, phase,
                       hill_cx, hill_cy, hill_h):
        self.next_section("freerun")

        # dials rotate from random to a settled, aligned set in lockstep with roll.
        settled_angles = np.full(9, PI / 2) + rng.uniform(-0.25, 0.25, 9)
        start_angles = dial_angles.copy()

        def update_dials(m):
            f = float(np.clip((roll.get_value() - 0.06) / (t_min - 0.06), 0, 1))
            for di, d in enumerate(m):
                a = start_angles[di] + f * (settled_angles[di] - start_angles[di])
                pointer = d[1]
                r = 0.11
                pointer.put_start_and_end_on(
                    d[0].get_center(),
                    d[0].get_center() + r * np.array([np.cos(a), np.sin(a), 0]))
        dials.add_updater(update_dials)

        new_phase = mono("roll to the valley floor", 17, INK_DIM).move_to(phase)
        self.play(
            roll.animate.set_value(t_min),
            passes.animate.set_value(1_000_000),
            Transform(phase, new_phase),
            run_time=1.2, rate_func=smooth,
        )

        dials.clear_updaters()
        garble.clear_updaters()
        sharp_guess.clear_updaters()
        sharp_guess.set_opacity(1.0)
        garble.set_opacity(0.0)
        self.remove(garble)
        self.wait(0.2)

    # -----------------------------------------------------------------
    # BEAT 7 — NAME (~1.37s): ball nestles, 'A' matches, #fff "shrink the error".
    # -----------------------------------------------------------------
    def _beat7_name(self, ball, err_bracket, sharp_guess, guess_box, true_box,
                    true_glyph, passes, pass_read, pass_cap, phase, downhill,
                    hill_grp, top_grp):
        self.next_section("name")

        ball.clear_updaters()
        err_bracket.clear_updaters()
        passes.clear_updaters()
        pass_read.clear_updaters()

        # dim everything except the valley ball, the matched 'A', and the payoff.
        # hill curve/axes are stroke-only — dim their stroke so they don't fill.
        self.play(
            FadeOut(err_bracket),
            FadeOut(phase),
            FadeOut(downhill),
            FadeOut(pass_read, shift=DOWN * 0.1),
            FadeOut(pass_cap, shift=DOWN * 0.1),
            *[m.animate.set_stroke(opacity=0.22) for m in hill_grp[:2] + hill_grp[4:]],
            *[m.animate.set_opacity(0.22) for m in hill_grp[2:4]],
            top_grp.animate.set_opacity(0.18),
            run_time=0.4,
        )

        # the sharp guess matches the (re-lit) known answer (stroke + glyph only).
        match = flat_arrow(guess_box.get_bottom() + DOWN * 0.02,
                           true_box.get_top() + UP * 0.02, INK_FAINT, 1.8)
        self.play(
            true_box[0].animate.set_stroke(opacity=1.0),
            true_box[1].animate.set_opacity(0.85),
            true_glyph.animate.set_opacity(1.0),
            Create(match[0]), FadeIn(match[1]),
            Indicate(sharp_guess, scale_factor=1.12, color=INK),
            Flash(ball.get_center(), color=INK, flash_radius=0.5,
                  line_length=0.1, num_lines=12),
            run_time=0.55,
        )

        # the #fff payoff owns the bottom strip.
        payoff = serif("shrink the error", 38, WHITE).move_to([0, BOT_Y + 0.12, 0])
        payoff_g = glow(payoff)
        sub = mono("guess · measure the error · step downhill · repeat", 16, INK_DIM)
        sub.move_to([0, BOT_Y - 0.55, 0])
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  FadeIn(sub, shift=UP * 0.08),
                  Flash([0, BOT_Y + 0.12, 0], color=WHITE, line_length=0.16,
                        num_lines=12, flash_radius=1.2, time_width=0.4),
                  run_time=0.55)

        self.wait(0.55)
