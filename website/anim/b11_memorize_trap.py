# website/anim/b11_memorize_trap.py — B11 "The memorizing trap" (overfitting)
#
# Idea to land: with scarce single-subject data, a GIANT model just memorizes the
# exact examples (wild wiggly curve through every dot) and crumbles on anything
# new; a SMALL four-layer model is forced to learn the underlying pattern (smooth
# curve), missing some training dots but catching the new test dot. So we keep the
# reader deliberately small. Justifies the Conformer's four layers.
#
# Locked 7-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 pose     (1.54s) one person's data — solid dots drop onto faint axes
#   2 build    (2.47s) GIANT reader grows; a wild curve threads every dot exactly
#   3 genius   (0.64s) dots pulse in sequence; "memorized every example"
#   4 trap     (1.53s) a hollow WHITE test dot; dashed miss + error flash
#   5 crumble  (1.98s) the miss holds spotlit; everything else dims
#   6 shrink   (2.52s) GIANT -> 4 layers; wild curve relaxes to one smooth curve
#   7 name     (1.29s) smooth curve lands at the test dot; serif "small on purpose"
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# ---- plot geometry (keep inside frame) ------------------------------------
PX_L, PX_R = -3.0, 3.0          # plot x extent on screen
PY_B, PY_T = -1.05, 2.25        # plot y extent on screen
PLOT_CX = (PX_L + PX_R) / 2


def model_glyph(n_layers, c=INK, op=1.0, lab_w=1.9, bar_h=0.14, buff=0.10):
    """A stacked-layers glyph standing for the model: n horizontal bars."""
    return VGroup(*[
        RoundedRectangle(width=lab_w, height=bar_h, corner_radius=min(0.06, bar_h / 2),
                         stroke_width=0, fill_color=c, fill_opacity=op)
        for _ in range(n_layers)
    ]).arrange(DOWN, buff=buff)


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
        # a NEW test point the model has never seen — sits on the true pattern,
        # in a gap where the overfit curve overshoots far above it.
        test_x = -0.121
        test_y = true_y(test_x)

        glyph_at = np.array([-5.0, -2.45, 0])

        # ============================================================
        # BEAT 1 — POSE (1.54s): one person's data drops onto faint axes.
        # ============================================================
        self.next_section("pose")

        rule = Line([-6.4, 3.05, 0], [6.4, 3.05, 0],
                    stroke_color=LINE, stroke_width=1.2)
        cap = mono("one person's data — a lot, but finite", 18, INK_FAINT)
        cap.move_to([0, 3.5, 0])

        ax_x = Line(to_screen(-2.6, -1.05), to_screen(2.6, -1.05),
                    stroke_color=INK_GHOST, stroke_width=1.2)
        ax_y = Line(to_screen(-2.6, -1.05), to_screen(-2.6, 1.3),
                    stroke_color=INK_GHOST, stroke_width=1.2)

        dots = VGroup(*[
            Dot(to_screen(x, y), radius=0.075, color=INK)
            for x, y in zip(train_x, train_y)
        ])

        self.play(FadeIn(cap, shift=DOWN * 0.1), Create(rule), run_time=0.4)
        self.play(Create(ax_x), Create(ax_y), run_time=0.34)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.08), run_time=0.6)
        self.wait(0.2)

        # ============================================================
        # BEAT 2 — BUILD (2.47s): a GIANT reader threads a wild curve
        #          through EVERY dot exactly.
        # ============================================================
        self.next_section("build")

        giant = model_glyph(12, c=INK, op=0.9, lab_w=1.9,
                            bar_h=0.09, buff=0.06).move_to(glyph_at)
        giant_tag = mono("a giant reader", 15, INK).next_to(giant, DOWN, buff=0.16)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in giant],
                              lag_ratio=0.03),
                  FadeIn(giant_tag, shift=UP * 0.06), run_time=0.7)

        # a wild interpolating curve forced through every training dot, with
        # overshooting wiggles between them (visually "memorized every example").
        def overfit_point(t):
            x = -2.6 + t * 5.2
            xs, ys = train_x, train_y
            if x <= xs[0]:
                base = ys[0]
            elif x >= xs[-1]:
                base = ys[-1]
            else:
                i = max(0, min(len(xs) - 2, np.searchsorted(xs, x) - 1))
                u = (x - xs[i]) / (xs[i + 1] - xs[i])
                s = u * u * (3 - 2 * u)
                base = ys[i] * (1 - s) + ys[i + 1] * s
                base += 0.55 * np.sin(np.pi * u) * np.sin(6.0 * np.pi * u)
            return to_screen(x, base)

        giant_curve = VMobject(stroke_color=INK, stroke_width=2.6)
        giant_curve.set_points_smoothly(
            [overfit_point(t) for t in np.linspace(0, 1, 240)])
        self.play(Create(giant_curve), run_time=1.5)
        self.wait(0.27)

        # ============================================================
        # BEAT 3 — GENIUS (0.64s): dots pulse in sequence; "memorized".
        # ============================================================
        self.next_section("genius")

        mem_tag = mono("memorized every example", 16, INK).move_to([0, -3.0, 0])
        self.play(
            LaggedStart(*[Indicate(d, scale_factor=1.4, color=WHITE) for d in dots],
                        lag_ratio=0.05),
            FadeIn(mem_tag, shift=UP * 0.08),
            run_time=0.64,
        )

        # ============================================================
        # BEAT 4 — TRAP (1.53s): a NEW hollow test dot; the giant curve
        #          misses it badly; an error flashes.
        # ============================================================
        self.next_section("trap")

        test_dot = Circle(radius=0.10, stroke_color=WHITE, stroke_width=3.0,
                          fill_opacity=0).move_to(to_screen(test_x, test_y))
        test_tag = mono("one example it never saw", 14, INK_DIM)
        test_tag.next_to(test_dot, DOWN, buff=0.30)

        t_at = (test_x + 2.6) / 5.2
        giant_pred = overfit_point(t_at)
        err = DashedLine(giant_pred, to_screen(test_x, test_y),
                         dash_length=0.10, stroke_color=WHITE, stroke_width=2.6)
        miss_dot = Dot(giant_pred, radius=0.055, color=INK_DIM)
        err_tag = mono("wildly off", 15, WHITE).next_to(err, RIGHT, buff=0.22)

        self.play(FadeIn(test_dot, scale=0.4),
                  FadeIn(test_tag, shift=DOWN * 0.05), run_time=0.45)
        self.play(Create(err), FadeIn(miss_dot),
                  Flash(giant_pred, color=WHITE, line_length=0.16, num_lines=12,
                        flash_radius=0.5, time_width=0.4),
                  run_time=0.55)
        self.play(FadeIn(err_tag), run_time=0.4)
        self.wait(0.13)

        # ============================================================
        # BEAT 5 — CRUMBLE (1.98s): the miss holds spotlit; the rest dims.
        # ============================================================
        self.next_section("crumble")

        self.play(
            dots.animate.set_opacity(0.22),
            giant_curve.animate.set_stroke(opacity=0.28),
            rule.animate.set_stroke(opacity=0.3),
            cap.animate.set_opacity(0.2),
            run_time=0.6,
        )
        self.play(
            Indicate(err_tag, scale_factor=1.2, color=WHITE),
            Indicate(test_dot, scale_factor=1.3, color=WHITE),
            run_time=0.6,
        )
        self.wait(0.78)

        # ============================================================
        # BEAT 6 — SHRINK (2.52s): GIANT -> 4 layers; wild curve relaxes
        #          into one smooth curve through the cloud.
        # ============================================================
        self.next_section("shrink")

        small = model_glyph(4, c=INK, op=1.0, lab_w=2.1).move_to(glyph_at)
        small_tag = mono("four layers", 16, INK).next_to(small, DOWN, buff=0.18)

        # the smooth generalizing curve: a gentle cubic through the cloud.
        coeffs = np.polyfit(train_x, train_y, 3)

        def smooth_point(t):
            x = -2.6 + t * 5.2
            return to_screen(x, np.polyval(coeffs, x))

        small_curve = VMobject(stroke_color=INK, stroke_width=3.0)
        small_curve.set_points_smoothly(
            [smooth_point(t) for t in np.linspace(0, 1, 160)])

        self.play(
            ReplacementTransform(giant, small),
            ReplacementTransform(giant_tag, small_tag),
            ReplacementTransform(giant_curve, small_curve),
            FadeOut(err), FadeOut(err_tag), FadeOut(miss_dot),
            FadeOut(mem_tag), FadeOut(test_tag),
            dots.animate.set_opacity(0.5),
            run_time=1.6,
        )
        self.wait(0.92)

        # ============================================================
        # BEAT 7 — NAME (1.29s): smooth curve lands at the test dot;
        #          serif #fff "small on purpose" + poster hold.
        # ============================================================
        self.next_section("name")

        small_pred = smooth_point(t_at)
        hit = DashedLine(small_pred, to_screen(test_x, test_y),
                         dash_length=0.08, stroke_color=INK_DIM, stroke_width=2.0)

        name = serif("small on purpose", 44, WHITE).move_to([0, -2.85, 0])
        name_g = glow(name)
        punch = mono("learn the pattern — not the answer key", 17, INK_DIM)
        punch.next_to(name, DOWN, buff=0.18)

        self.play(Create(hit),
                  Indicate(test_dot, scale_factor=1.5, color=WHITE),
                  run_time=0.45)
        self.add(name_g)
        self.play(GrowFromCenter(name),
                  Flash([0, -2.85, 0], color=WHITE, line_length=0.18, num_lines=12,
                        flash_radius=1.6, time_width=0.4), run_time=0.45)
        self.play(FadeIn(punch, shift=UP * 0.08), run_time=0.3)
        self.wait(0.45)


if __name__ == "__main__":
    pass
