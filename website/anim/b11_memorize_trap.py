# website/anim/b11_memorize_trap.py — B11 "The memorizing trap" (overfitting)
#
# Idea to land: with scarce single-subject data, a GIANT model just memorizes the
# exact examples (wild wiggly curve through every dot) and crumbles on anything
# new; a SMALL four-layer model is forced to learn the underlying pattern (smooth
# curve), missing some training dots but catching the new test dot. So we keep the
# reader deliberately small. Justifies the Conformer's four layers.
#
# Three persistent zones (3b1b: pose -> build -> transform -> name):
#   TOP   (y ~ +3.0): cap "THE MEMORIZING TRAP" + "one person's data — a lot, but finite"
#   CENTER(y ~ -1.4..+2.4): the plot — training dots, then the giant overfit curve,
#                 then a hollow TEST dot the giant misses (error flash), then the
#                 curve relaxes into the small smooth fit that lands near the test dot.
#   BOTTOM(y ~ -3.3): the model glyph + "size" readout flips GIANT -> 4 layers, with
#                 a one-line takeaway resolving to "learn the pattern, not the answers".
#   final a balanced poster holds ~0.6s.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# ---- plot geometry (keep inside frame) ------------------------------------
PX_L, PX_R = -3.0, 3.0          # plot x extent on screen
PY_B, PY_T = -1.35, 2.05        # plot y extent on screen
PLOT_CX = (PX_L + PX_R) / 2


def model_glyph(n_layers, w=2.0, c=INK, op=1.0, lab_w=1.9):
    """A stacked-layers glyph standing for the model: n horizontal bars."""
    bars = VGroup(*[
        RoundedRectangle(width=lab_w, height=0.14, corner_radius=0.06,
                         stroke_width=0, fill_color=c, fill_opacity=op)
        for _ in range(n_layers)
    ]).arrange(DOWN, buff=0.10)
    return bars


class MemorizeTrap(Scene):
    def construct(self):
        seed()

        # the latent "true" pattern the data is drawn from (a gentle wave).
        def true_y(x):
            return 0.55 * np.sin(1.15 * x + 0.3) + 0.18 * x

        # screen-space mapping: data x in [-2.6, 2.6] -> PX; data y -> PY band.
        def to_screen(dx, dy):
            sx = PLOT_CX + dx / 2.6 * (PX_R - PLOT_CX)
            sy = (PY_B + PY_T) / 2 + dy * 0.85
            return np.array([sx, sy, 0])

        # training samples: true pattern + noise. ONE person -> a handful of dots.
        train_x = np.array([-2.4, -1.85, -1.2, -0.6, 0.05, 0.7, 1.3, 1.85, 2.4])
        noise = np.array([0.22, -0.30, 0.26, -0.20, 0.30, -0.26, 0.22, -0.32, 0.20])
        train_y = true_y(train_x) + noise
        # a NEW test point the model has never seen — sits on the true pattern.
        test_x = -0.95
        test_y = true_y(test_x)

        # ============================================================
        # B0 — TOP frame + POSE: the scatter of one person's dots.
        # ============================================================
        self.next_section("pose")

        top1 = mono("THE MEMORIZING TRAP", 26, INK_DIM, w=BOLD).move_to([0, 3.2, 0])
        top2 = mono("one person's data — a lot, but finite", 17, INK_FAINT).move_to(
            [0, 2.68, 0])
        rule = Line([-6.4, 2.36, 0], [6.4, 2.36, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)

        # faint plot axes (a frame for the data — no numbers, just a stage).
        ax_x = Line(to_screen(-2.6, -1.05), to_screen(2.6, -1.05),
                    stroke_color=INK_GHOST, stroke_width=1.2)
        ax_y = Line(to_screen(-2.6, -1.05), to_screen(-2.6, 1.05),
                    stroke_color=INK_GHOST, stroke_width=1.2)
        self.play(Create(ax_x), Create(ax_y), run_time=0.4)

        # the training dots drop in — solid INK dots = the answer key we hold.
        dots = VGroup(*[
            Dot(to_screen(x, y), radius=0.075, color=INK)
            for x, y in zip(train_x, train_y)
        ])
        dots_cap = mono("9 examples we measured", 15, INK_FAINT)
        dots_cap.next_to(ax_x, DOWN, buff=0.22).set_x(PLOT_CX)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.10, run_time=0.7))
        self.play(FadeIn(dots_cap), run_time=0.28)

        # ============================================================
        # BOTTOM skeleton: the model glyph + a "size" label that will flip.
        # ============================================================
        glyph_at = np.array([-4.9, -3.0, 0])
        size_lab = mono("model size", 14, INK_GHOST).move_to([-4.9, -2.0, 0])
        self.play(FadeIn(size_lab), run_time=0.25)

        # ============================================================
        # B1 — BUILD: a GIANT model threads a wild wiggly curve through
        #      EVERY dot exactly. "memorized."
        # ============================================================
        self.next_section("memorize")

        giant = model_glyph(12, c=INK, op=0.9, lab_w=2.1).move_to(glyph_at)
        giant_tag = mono("GIANT model", 16, INK).next_to(giant, DOWN, buff=0.18)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in giant],
                              lag_ratio=0.04, run_time=0.6),
                  FadeIn(giant_tag, shift=UP * 0.06), run_time=0.6)

        # a wild interpolating curve that passes through every training dot. We
        # build it as a smooth path forced through the dots with overshooting
        # control wiggles between them (visually "memorized every example").
        def overfit_point(t):
            # t in [0,1] across the x-range; piecewise through dots with wiggle.
            x = -2.6 + t * 5.2
            # base: pass near each dot via a high-frequency interpolation.
            # use a cubic-ish blend that hits each dot, plus a wiggle term.
            # find bracketing dots
            xs = train_x
            ys = train_y
            if x <= xs[0]:
                base = ys[0]
            elif x >= xs[-1]:
                base = ys[-1]
            else:
                i = np.searchsorted(xs, x) - 1
                i = max(0, min(len(xs) - 2, i))
                u = (x - xs[i]) / (xs[i + 1] - xs[i])
                # smoothstep between dots so it actually touches them
                s = u * u * (3 - 2 * u)
                base = ys[i] * (1 - s) + ys[i + 1] * s
                # add an overshoot wiggle that vanishes AT the dots (u=0,1)
                base += 0.55 * np.sin(np.pi * u) * np.sin(6.0 * np.pi * u)
            return to_screen(x, base)

        giant_curve = VMobject(stroke_color=INK, stroke_width=2.6)
        giant_curve.set_points_smoothly(
            [overfit_point(t) for t in np.linspace(0, 1, 240)])
        mem_tag = mono("memorized every example", 16, INK).move_to([0, -2.55, 0])
        self.play(Create(giant_curve), run_time=1.7)
        # emphasise that it nails every dot
        self.play(LaggedStart(*[Indicate(d, scale_factor=1.4, color=WHITE)
                                for d in dots], lag_ratio=0.08, run_time=0.9),
                  FadeIn(mem_tag, shift=UP * 0.08), run_time=0.9)
        self.wait(0.3)

        # ============================================================
        # B2 — TRANSFORM (the trap): a NEW hollow test dot appears — the
        #      giant curve misses it badly; an error flashes.
        # ============================================================
        self.next_section("trap")

        test_dot = Circle(radius=0.10, stroke_color=WHITE, stroke_width=3.0,
                          fill_opacity=0).move_to(to_screen(test_x, test_y))
        test_tag = mono("a new example", 14, INK_DIM)
        test_tag.next_to(test_dot, UP, buff=0.30).shift(LEFT * 0.55)
        self.play(FadeIn(test_dot, scale=0.4), FadeIn(test_tag, shift=DOWN * 0.05),
                  run_time=0.45)

        # where the giant curve actually is at test_x — far from the test dot.
        # sample the overfit curve at test_x:
        t_at = (test_x + 2.6) / 5.2
        giant_pred = overfit_point(t_at)
        err = DashedLine(giant_pred, to_screen(test_x, test_y),
                         dash_length=0.10, stroke_color=WHITE, stroke_width=2.6)
        miss_dot = Dot(giant_pred, radius=0.055, color=INK_DIM)
        err_tag = mono("way off", 15, WHITE).next_to(err, RIGHT, buff=0.18)
        self.play(Create(err), FadeIn(miss_dot), run_time=0.4)
        self.play(FadeIn(err_tag),
                  Flash(giant_pred, color=WHITE, line_length=0.16, num_lines=12,
                        flash_radius=0.5, time_width=0.4), run_time=0.5)
        self.play(Indicate(err_tag, scale_factor=1.2, color=WHITE), run_time=0.5)
        self.wait(0.45)

        # ============================================================
        # B3 — SHRINK: collapse the giant to a small four-layer model;
        #      the wild curve relaxes into a smooth fit that misses some
        #      training dots but LANDS NEAR the test dot.
        # ============================================================
        self.next_section("shrink")

        small = model_glyph(4, c=INK, op=1.0, lab_w=2.1).move_to(glyph_at)
        small_tag = mono("4 layers", 16, INK).next_to(small, DOWN, buff=0.18)

        # the smooth generalizing curve: the true pattern, lightly fit (a gentle
        # cubic through the cloud, NOT through every dot).
        coeffs = np.polyfit(train_x, train_y, 3)

        def smooth_point(t):
            x = -2.6 + t * 5.2
            y = np.polyval(coeffs, x)
            return to_screen(x, y)

        small_curve = VMobject(stroke_color=INK, stroke_width=3.0)
        small_curve.set_points_smoothly(
            [smooth_point(t) for t in np.linspace(0, 1, 160)])

        # smooth model's prediction at the test x — close to the test dot.
        small_pred = smooth_point(t_at)
        hit = DashedLine(small_pred, to_screen(test_x, test_y),
                         dash_length=0.08, stroke_color=INK_DIM, stroke_width=2.0)

        learn_tag = mono("learned the pattern", 16, INK).move_to([0, -2.55, 0])

        # the shrink: giant glyph -> small glyph, wild curve -> smooth curve.
        self.play(
            ReplacementTransform(giant, small),
            ReplacementTransform(giant_tag, small_tag),
            ReplacementTransform(giant_curve, small_curve),
            FadeOut(err), FadeOut(err_tag), FadeOut(miss_dot),
            FadeOut(mem_tag),
            run_time=1.4,
        )
        self.play(Create(hit), run_time=0.5)
        self.play(FadeIn(learn_tag, shift=UP * 0.08),
                  Indicate(test_dot, scale_factor=1.5, color=WHITE),
                  run_time=0.6)
        self.wait(0.35)

        # ============================================================
        # B4 — NAME IT + POSTER HOLD: serif #fff "small on purpose".
        # ============================================================
        self.next_section("name")

        # tidy the bottom for the punchline
        self.play(FadeOut(learn_tag), FadeOut(size_lab), run_time=0.3)

        name = serif("small on purpose", 46, WHITE).move_to([0, -2.7, 0])
        name_g = glow(name)
        punch = mono("learn the pattern — not the answer key", 18, INK_DIM)
        punch.next_to(name, DOWN, buff=0.20)
        self.add(name_g)
        self.play(GrowFromCenter(name),
                  Flash([0, -2.7, 0], color=WHITE, line_length=0.18, num_lines=12,
                        flash_radius=1.6, time_width=0.4), run_time=0.55)
        self.play(FadeIn(punch, shift=UP * 0.08), run_time=0.4)

        self.wait(0.6)


if __name__ == "__main__":
    pass
