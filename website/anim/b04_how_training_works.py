# website/anim/b04_how_training_works.py — B04 "Rolling downhill" (how training works)
#
# Carries the dial-box from b03 (what-is-a-net): a layered function whose guess
# starts garbled because its dials are random. This clip teaches the ONE loop:
#   guess  ->  measure how wrong (the error)  ->  step downhill  ->  repeat.
# Gradient descent without the jargon — the error is the HEIGHT of a hill, the
# dials are the POSITION on it, and a single ball rolls to the valley floor while
# the guessed letter sharpens toward the true answer over millions of passes.
#
# Three-zone full-canvas composition (3b1b: pose -> build -> transform -> name):
#   TOP    (y~+2.6..+3.6)  CONTEXT: the carried dial-box function — numbers in,
#                  a stack of dial-banks, a guess out — dimmed as the anchor.
#   CENTER (-1.6..+2.0)    MECHANISM: the error hill (a 1-D curve), a ball high on
#                  one slope, and the guessed/true letter pair. A shared
#                  ValueTracker rolls the ball downhill while the dials rotate a
#                  hair and the guess sharpens — one clean continuous descent.
#   BOTTOM (-3.7..-2.7)    TAKEAWAY: a live "x N" pass counter free-runs
#                  1 -> 1000 -> millions in lockstep with the descent, then the
#                  serif #fff payoff "shrink the error".
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

        # ================================================================
        # TOP — CONTEXT: the carried dial-box function (numbers -> guess).
        # ================================================================
        self.next_section("carryover")

        in_lbl = mono("numbers in", 16, INK_FAINT).move_to([X_L + 0.9, TOP_Y, 0])
        # a tiny fingerprint bar-row entering at left (echo of b03/features-embed).
        fp_hh = 0.08 + 0.26 * np.abs(np.random.randn(7))
        fp = VGroup()
        for k, h in enumerate(fp_hh):
            fp.add(Rectangle(width=0.05, height=float(h), stroke_width=0,
                             fill_color=INK, fill_opacity=0.7))
        fp.arrange(RIGHT, buff=0.03, aligned_edge=DOWN)
        fp.next_to(in_lbl, RIGHT, buff=0.28)

        # the layered dial-box: 3 banks of 3 dials each — random angles.
        box = RoundedRectangle(width=2.5, height=1.15, corner_radius=0.08,
                               stroke_color=INK_FAINT, stroke_width=1.4,
                               fill_color=BG, fill_opacity=1.0)
        box.move_to([0.1, TOP_Y, 0])
        rng = np.random.default_rng(11)
        dial_angles = rng.uniform(0, 2 * PI, 9)
        dials = VGroup()
        for di in range(9):
            d = dial(r=0.11, angle=float(dial_angles[di]), op=0.92, sw=1.6)
            col = di % 3
            row = di // 3
            d.move_to([box.get_x() + (col - 1) * 0.72,
                       box.get_y() + (row - 1) * 0.40, 0])
            dials.add(d)
        box_lbl = mono("a stack of dials", 13, INK_GHOST).next_to(box, DOWN, buff=0.10)

        # threads in and out of the box.
        thread_in = flat_arrow([fp.get_right()[0] + 0.12, TOP_Y, 0],
                               [box.get_left()[0] - 0.06, TOP_Y, 0], INK_GHOST, 1.6)
        out_lbl = mono("a guess", 16, INK_FAINT).move_to([X_R - 0.95, TOP_Y, 0])
        thread_out = flat_arrow([box.get_right()[0] + 0.06, TOP_Y, 0],
                                [out_lbl.get_left()[0] - 0.12, TOP_Y, 0],
                                INK_GHOST, 1.6)

        self.play(FadeIn(in_lbl), FadeIn(fp, shift=RIGHT * 0.1), run_time=0.4)
        self.play(FadeIn(box), LaggedStartMap(FadeIn, dials, lag_ratio=0.05),
                  FadeIn(box_lbl), run_time=0.55)
        self.play(Create(thread_in[0]), FadeIn(thread_in[1]),
                  Create(thread_out[0]), FadeIn(thread_out[1]),
                  FadeIn(out_lbl), run_time=0.4)

        top_grp = VGroup(in_lbl, fp, box, dials, box_lbl, thread_in,
                         thread_out, out_lbl)
        rule = Line([X_L, TOP_Y - 0.75, 0], [X_R, TOP_Y - 0.75, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(top_grp.animate.set_opacity(0.6), Create(rule), run_time=0.3)
        # restore each dial's pointer crispness (set_opacity dims the whole group);
        # we WANT them dim here, so leave as-is — this is the anchor state.

        # ================================================================
        # CENTER — POSE: the garbled guess beside the (known) true answer.
        # ================================================================
        self.next_section("pose")

        # the guess letter — starts garbled & dim; true answer docks beside it.
        guess_at = np.array([4.55, CENTER_Y + 1.15, 0])
        true_at = np.array([4.55, CENTER_Y - 0.55, 0])
        guess_box = RoundedRectangle(width=1.4, height=1.05, corner_radius=0.08,
                                     stroke_color=INK_GHOST, stroke_width=1.3,
                                     fill_opacity=0).move_to(guess_at)
        true_box = RoundedRectangle(width=1.4, height=1.05, corner_radius=0.08,
                                    stroke_color=INK_FAINT, stroke_width=1.3,
                                    fill_opacity=0).move_to(true_at)
        guess_cap = mono("its guess", 14, INK_FAINT).next_to(guess_box, UP, buff=0.12)
        true_cap = mono("known answer", 14, INK_DIM).next_to(true_box, DOWN, buff=0.12)

        # garbled glyph: overlapping faint strokes that read as illegible.
        garble = VGroup(
            serif("E", 46, INK_GHOST).rotate(0.18).shift([-0.06, 0.02, 0]),
            serif("Z", 46, INK_GHOST).rotate(-0.22).shift([0.07, -0.03, 0]),
            serif("S", 46, INK_FAINT).rotate(0.05),
        ).move_to(guess_box)
        true_glyph = serif("A", 46, INK_DIM).move_to(true_box)

        self.play(FadeIn(guess_box), FadeIn(guess_cap),
                  FadeIn(garble), run_time=0.45)
        self.play(FadeIn(true_box), FadeIn(true_cap),
                  FadeIn(true_glyph, shift=UP * 0.1), run_time=0.4)
        # hold on the nonsense first guess vs the known answer.
        self.play(Indicate(garble, scale_factor=1.06, color=INK_FAINT),
                  run_time=0.5)

        # ================================================================
        # BUILD — the error HILL: a 1-D curve, the dials are the position,
        #         the error is the height; a ball sits high up one slope.
        # ================================================================
        self.next_section("build")

        # the hill curve, drawn as a smooth parabola-ish valley on the left.
        hill_cx, hill_cy = -2.4, CENTER_Y - 0.25
        hill_w, hill_h = 5.4, 2.4
        x_axis = Line([hill_cx - hill_w / 2, hill_cy - hill_h / 2, 0],
                      [hill_cx + hill_w / 2, hill_cy - hill_h / 2, 0],
                      stroke_color=INK_GHOST, stroke_width=1.2)
        y_axis = Line([hill_cx - hill_w / 2, hill_cy - hill_h / 2, 0],
                      [hill_cx - hill_w / 2, hill_cy + hill_h / 2 + 0.1, 0],
                      stroke_color=INK_GHOST, stroke_width=1.2)
        err_lbl = mono("error", 15, INK_FAINT).rotate(PI / 2)
        err_lbl.next_to(y_axis, LEFT, buff=0.12)
        dials_lbl = mono("the dials", 14, INK_FAINT).next_to(x_axis, DOWN, buff=0.16)

        # curve y = valley(t), t in [0,1]; minimum near t=0.62.
        t_min = 0.62

        def curve_y(t):
            return hill_cy - hill_h / 2 + hill_h * (2.6 * (t - t_min) ** 2 + 0.04)

        def curve_x(t):
            return hill_cx - hill_w / 2 + 0.18 + t * (hill_w - 0.36)

        curve = VMobject(stroke_color=INK, stroke_width=2.2)
        pts = [[curve_x(t), curve_y(t), 0] for t in np.linspace(0, 1, 80)]
        curve.set_points_smoothly(pts)

        self.play(Create(x_axis), Create(y_axis),
                  FadeIn(err_lbl), FadeIn(dials_lbl), run_time=0.4)
        self.play(Create(curve), run_time=0.6)

        # the ball, high up the left slope. A shared tracker drives EVERYTHING.
        roll = ValueTracker(0.06)   # position along the hill, 0..1
        ball = Dot(radius=0.11, color=INK, fill_opacity=1.0)
        ball.move_to([curve_x(0.06), curve_y(0.06) + 0.11, 0])

        def update_ball(m):
            t = roll.get_value()
            m.move_to([curve_x(t), curve_y(t) + 0.11, 0])
        ball.add_updater(update_ball)

        # a dashed drop-line from the ball to the axis marks the current error.
        drop = always_redraw(lambda: DashedLine(
            ball.get_center() + DOWN * 0.11,
            [curve_x(roll.get_value()), hill_cy - hill_h / 2, 0],
            stroke_color=INK_GHOST, stroke_width=1.1, dash_length=0.06))

        self.add(drop, ball)
        self.play(FadeIn(ball, scale=0.5), run_time=0.3)

        # link ball <-> dial-box and guess: a faint guide from hill to the guess.
        link = flat_arrow([hill_cx + hill_w / 2 + 0.05, hill_cy + 0.2, 0],
                          [guess_box.get_left()[0] - 0.1, CENTER_Y + 0.3, 0],
                          INK_GHOST, 1.4)
        step_cap = mono("each step rolls a little downhill", 16, INK_FAINT)
        step_cap.move_to([hill_cx, hill_cy + hill_h / 2 + 0.55, 0])
        self.play(Create(link[0]), FadeIn(link[1]),
                  FadeIn(step_cap, shift=DOWN * 0.08), run_time=0.4)

        # ================================================================
        # BOTTOM — the live pass counter skeleton (one live counter only).
        # ================================================================
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

        # ================================================================
        # TRANSFORM — one clean continuous descent: ball rolls to the valley,
        #   dials rotate a hair, guess sharpens, counter free-runs.
        # ================================================================
        self.next_section("descend")

        # the guess will resolve to "A" — build the sharpened target now.
        sharp_guess = serif("A", 46, INK).move_to(guess_box)

        # the dials' settled angles (all converge toward a tidy, aligned set).
        settled_angles = np.full(9, PI / 2) + rng.uniform(-0.25, 0.25, 9)

        # restore dial crispness for the rotation (they were dimmed in anchor).
        # rotate each dial's pointer from its start angle to its settled angle in
        # lockstep with the roll tracker — a hair per step.
        start_angles = dial_angles.copy()
        for di, d in enumerate(dials):
            d.set_opacity(0.6)  # keep top anchor dim but visible

        def update_dials(m):
            f = (roll.get_value() - 0.06) / (t_min - 0.06)
            f = float(np.clip(f, 0, 1))
            for di, d in enumerate(m):
                a = start_angles[di] + f * (settled_angles[di] - start_angles[di])
                pointer = d[1]
                r = 0.11
                pointer.put_start_and_end_on(
                    d[0].get_center(),
                    d[0].get_center() + r * np.array([np.cos(a), np.sin(a), 0]))
        dials.add_updater(update_dials)

        # the guess crossfades garble -> sharp in lockstep via opacity on roll.
        def update_garble(m):
            f = (roll.get_value() - 0.06) / (t_min - 0.06)
            m.set_opacity(0.55 * (1 - float(np.clip(f, 0, 1))))
        garble.add_updater(update_garble)

        sharp_guess.set_opacity(0.0)
        self.add(sharp_guess)

        def update_sharp(m):
            f = (roll.get_value() - 0.06) / (t_min - 0.06)
            m.set_opacity(float(np.clip(f, 0, 1)))
        sharp_guess.add_updater(update_sharp)

        # The descent is shown as the LOOP it really is: a few discrete steps
        # (guess -> measure -> step downhill), each rolling the ball a notch and
        # ticking the pass counter, then a final settle into the valley. A label
        # names the current phase so the mechanism reads at any scrubbed frame.
        phase = mono("measure the miss", 17, INK_DIM)
        phase.move_to([hill_cx, hill_cy - hill_h / 2 - 0.55, 0])
        self.play(FadeIn(phase, shift=UP * 0.05), run_time=0.3)

        # an error-bracket on the curve that shrinks as the ball descends.
        err_bracket = always_redraw(lambda: Line(
            [curve_x(roll.get_value()), hill_cy - hill_h / 2, 0],
            ball.get_center() + DOWN * 0.11,
            stroke_color=INK_FAINT, stroke_width=3.0))
        self.add(err_bracket)

        # four notches: roll positions and the pass count at each.
        notches = [0.20, 0.36, 0.50, t_min]
        pass_marks = [12, 480, 50_000, 1_000_000]
        for k, (tgt, pm) in enumerate(zip(notches, pass_marks)):
            last = k == len(notches) - 1
            cap = ("step downhill" if k % 2 == 0 else "measure the miss")
            if last:
                cap = "the valley floor"
            new_phase = mono(cap, 17, INK_DIM).move_to(phase)
            self.play(
                roll.animate.set_value(tgt),
                passes.animate.set_value(pm),
                Transform(phase, new_phase),
                run_time=(1.15 if last else 0.95), rate_func=smooth,
            )
            if not last:
                self.wait(0.18)

        dials.clear_updaters()
        garble.clear_updaters()
        sharp_guess.clear_updaters()
        ball.clear_updaters()
        err_bracket.clear_updaters()
        sharp_guess.set_opacity(1.0)
        garble.set_opacity(0.0)
        self.remove(garble)
        # the error bracket has collapsed to ~nothing in the valley; retire it.
        self.play(FadeOut(err_bracket), run_time=0.25)

        # a small "match" tick between the now-sharp guess and the true answer.
        match = flat_arrow(guess_box.get_bottom() + DOWN * 0.02,
                           true_box.get_top() + UP * 0.02, INK_FAINT, 1.8)
        self.play(Create(match[0]), FadeIn(match[1]),
                  Indicate(sharp_guess, scale_factor=1.12, color=INK),
                  run_time=0.5)

        # the ball nestles in the valley — a small settle bounce.
        self.play(Flash(ball.get_center(), color=INK, flash_radius=0.5,
                        line_length=0.1, num_lines=12, run_time=0.5))

        # ================================================================
        # NAME — the #fff payoff: shrink the error.
        # ================================================================
        self.next_section("name")

        # retire the live counter into a quiet readout; the payoff owns the bottom.
        passes.clear_updaters()
        pass_read.clear_updaters()

        payoff = serif("shrink the error", 38, WHITE).move_to([0, BOT_Y + 0.12, 0])
        payoff_g = glow(payoff)
        sub = mono("guess · measure the miss · step downhill · repeat", 16, INK_DIM)
        sub.move_to([0, BOT_Y - 0.55, 0])

        self.play(FadeOut(pass_read, shift=DOWN * 0.1),
                  FadeOut(pass_cap, shift=DOWN * 0.1),
                  FadeOut(phase), FadeOut(step_cap), run_time=0.3)
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  FadeIn(sub, shift=UP * 0.08),
                  Flash([0, BOT_Y + 0.12, 0], color=WHITE, line_length=0.16,
                        num_lines=12, flash_radius=1.2, time_width=0.4),
                  run_time=0.6)

        # ================================================================
        # POSTER HOLD.
        # ================================================================
        self.wait(0.6)
