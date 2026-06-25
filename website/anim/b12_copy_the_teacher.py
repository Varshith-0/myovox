# b12_copy_the_teacher.py — B12 "Tracing the master" (knowledge distillation)
#
# The third output (the projection that "refused to vote, and just glowed")
# exists for a trick: a STUDENT copies a TEACHER's rich internal PICTURE, not
# just the final right/wrong verdict. Metaphor: tracing paper laid over a
# master's brushstroke — match the whole shape, point by point, not just where
# the line ends.
#
# Locked 8-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 context (1.55) top rail "THE THIRD OUTPUT — a 1024-number projection",
#                    still glowing — echoes "the one that refused to vote".
#   2 open    (0.63) hairline rule seals the top; the panel opens empty, waiting.
#   3 student (1.95) crude wobbly STUDENT line draws; endpoint dot lights with
#                    'endpoint matches ✓' — graded only on where it ends.
#   4 master  (1.22) the faint confident MASTER curve fades in above/over it,
#                    'teacher's internal picture'.
#   5 gap     (1.87) hatched gap-lines shade between student and master;
#                    'shape is still wrong'.
#   6 trace   (2.21) endpoint tick + gap clear; master brightens into a
#                    tracing-paper guide; label -> 'trace the whole stroke'.
#   7 pull    (2.32) a pen sweeps L->R pulling the student onto the master while
#                    'distance to teacher' free-falls to 0; a flash marks match.
#   8 name    (1.83) panel clears to serif #fff 'distillation' + subtitle.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# ---- canvas zones ----------------------------------------------------------
TOP_Y = 3.18
RULE_Y = 2.5
PANEL_Y = 0.05        # centre of the tracing panel
X_L, X_R = -6.6, 6.6

# ---- the two shapes (x in panel param t; we map to screen) -----------------
PANEL_W = 6.6
PANEL_X = 0.0         # panel centre x


def master_y(t):
    """The teacher's confident curve — a smooth, distinctive S-stroke."""
    return 0.95 * np.sin(2.4 * t + 0.4) + 0.32 * np.sin(5.1 * t)


def student_y(t):
    """The student's crude first attempt — wobbly, wrong shape, but it happens
    to END near the master (so endpoint-only grading calls it 'good enough')."""
    crude = 0.45 * np.sin(1.1 * t - 1.2) - 0.30 * np.cos(3.3 * t) + 0.18
    edge = (t + 1.0) / 2.0                      # 0 at left, 1 at right
    blendL = np.exp(-((edge) ** 2) / 0.02)
    blendR = np.exp(-((edge - 1.0) ** 2) / 0.02)
    return crude * (1 - blendL - blendR) + master_y(t) * (blendL + blendR)


def screen_point(t, y, y_scale=1.0):
    """Map panel param t in [-1,1] + height y to a screen point in the panel."""
    return np.array([PANEL_X + t * (PANEL_W / 2.0),
                     PANEL_Y + y * y_scale,
                     0.0])


class CopyTheTeacher(Scene):
    def construct(self):
        seed()

        ts = np.linspace(-1.0, 1.0, 160)

        # ================================================================
        # BEAT 1 — CONTEXT (1.55s): inherit the third output, still glowing.
        # ================================================================
        self.next_section("context")

        top1 = mono("THE THIRD OUTPUT", 24, INK_DIM, w=BOLD).move_to([0, TOP_Y, 0])
        top2 = mono("a 1024-number projection — the one that just glowed",
                    17, INK_FAINT)
        top2.move_to([0, TOP_Y - 0.5, 0])
        top_glow = glow(top1.copy().set_color(WHITE))
        self.add(top_glow)
        self.play(FadeIn(top1, shift=DOWN * 0.12),
                  top_glow.animate.set_opacity(0.5), run_time=0.7)
        self.play(FadeIn(top2), run_time=0.5)
        self.play(top_glow.animate.set_opacity(0.0), run_time=0.3)
        self.remove(top_glow)
        self.wait(0.05)

        # ================================================================
        # BEAT 2 — OPEN (0.63s): seal the top, open the empty panel.
        # ================================================================
        self.next_section("open")

        rule = Line([X_L, RULE_Y, 0], [X_R, RULE_Y, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(Create(rule), run_time=0.45)
        self.wait(0.18)

        # ================================================================
        # BEAT 3 — STUDENT (1.95s): crude wobbly line, graded by endpoint only.
        # ================================================================
        self.next_section("student")

        student = VMobject(stroke_color=INK, stroke_width=3.0)
        student.set_points_smoothly([screen_point(t, student_y(t)) for t in ts])
        stu_lbl = mono("student's first attempt", 17, INK).move_to(
            [PANEL_X, PANEL_Y - 1.95, 0])
        self.play(FadeIn(stu_lbl, shift=UP * 0.08), run_time=0.35)
        self.play(Create(student), run_time=0.85)

        # endpoint-only verdict: the right end touches the master -> a tick.
        end_pt = screen_point(1.0, student_y(1.0))
        endpoint_dot = Dot(end_pt, radius=0.075, color=INK)
        endpoint_ring = Circle(radius=0.22, stroke_color=INK_FAINT,
                               stroke_width=1.6).move_to(end_pt)
        verdict = mono("endpoint matches  ✓", 16, INK_FAINT)
        verdict.next_to(endpoint_ring, UP, buff=0.16).shift(LEFT * 0.45)
        self.play(FadeIn(endpoint_dot, scale=0.5), Create(endpoint_ring),
                  run_time=0.35)
        self.play(FadeIn(verdict, shift=DOWN * 0.06), run_time=0.4)
        self.wait(0.05)

        # ================================================================
        # BEAT 4 — MASTER (1.22s): the faint confident teacher curve fades in.
        # ================================================================
        self.next_section("master")

        master = VMobject(stroke_color=INK_DIM, stroke_width=2.6)
        master.set_points_smoothly([screen_point(t, master_y(t)) for t in ts])
        master.set_opacity(0.55)
        master_lbl = mono("teacher's internal picture", 17, INK_DIM)
        master_lbl.move_to([PANEL_X, PANEL_Y + 1.85, 0])

        self.play(FadeIn(master_lbl, shift=DOWN * 0.08), run_time=0.35)
        self.play(Create(master), run_time=0.75)
        self.wait(0.12)

        # ================================================================
        # BEAT 5 — GAP (1.87s): shade the area between student & master.
        # ================================================================
        self.next_section("gap")

        # dim the endpoint framing so the gap is the focus.
        self.play(verdict.animate.set_opacity(0.35),
                  endpoint_ring.animate.set_stroke(opacity=0.4),
                  endpoint_dot.animate.set_opacity(0.4),
                  run_time=0.35)

        gap = VGroup(*[
            Line(screen_point(t, student_y(t)), screen_point(t, master_y(t)),
                 stroke_color=INK_GHOST, stroke_width=1.0)
            for t in np.linspace(-0.86, 0.86, 28)
        ])
        gap_lbl = mono("shape is still wrong", 16, INK_DIM).move_to(
            [PANEL_X, PANEL_Y - 2.45, 0])
        self.play(LaggedStart(*[Create(g) for g in gap], lag_ratio=0.025),
                  run_time=0.7)
        self.play(FadeIn(gap_lbl, shift=UP * 0.06), run_time=0.45)
        self.wait(0.2)

        # ================================================================
        # BEAT 6 — TRACE (2.21s): clear the endpoint/gap; master -> guide.
        # ================================================================
        self.next_section("trace")

        trace_lbl = mono("trace the whole stroke", 19, INK).move_to(stu_lbl)
        self.play(
            FadeOut(verdict), FadeOut(endpoint_ring), FadeOut(endpoint_dot),
            FadeOut(gap_lbl), FadeOut(gap),
            ReplacementTransform(stu_lbl, trace_lbl),
            run_time=0.6,
        )
        # brighten the master into a clear tracing-paper guide overlay.
        self.play(master.animate.set_stroke(INK_DIM, 2.6, opacity=0.85),
                  master_lbl.animate.set_color(INK),
                  run_time=0.7)
        self.wait(0.6)

        # ================================================================
        # BEAT 7 — PULL (2.32s): pen sweeps L->R pulling student onto master;
        #          'distance to teacher' free-falls to 0; flash on match.
        # ================================================================
        self.next_section("pull")

        pull = ValueTracker(0.0)

        def blended_points():
            a = pull.get_value()
            return [screen_point(t, (1 - a) * student_y(t) + a * master_y(t))
                    for t in ts]
        student.add_updater(lambda m: m.set_points_smoothly(blended_points()))

        def residual():
            a = pull.get_value()
            diffs = np.array([(1 - a) * student_y(t) + a * master_y(t)
                              - master_y(t) for t in ts])
            return float(np.mean(np.abs(diffs)) * 100.0)

        dist = ValueTracker(residual())
        dist_at = np.array([X_R - 1.5, PANEL_Y - 0.4, 0])
        dist_read = counter(dist, fmt=lambda v: f"{max(v, 0):4.1f}", s=40, c=INK,
                            at=dist_at)
        dist_tag = mono("distance to teacher", 13, INK_DIM)
        dist_tag.next_to(dist_read, UP, buff=0.16)
        # dim the trace label so the readout is the spotlight.
        self.play(FadeIn(dist_read), FadeIn(dist_tag),
                  trace_lbl.animate.set_opacity(0.45),
                  master_lbl.animate.set_opacity(0.45),
                  run_time=0.4)

        pen = Triangle(stroke_width=0, fill_color=WHITE, fill_opacity=0.95)
        pen.scale(0.085).rotate(PI)
        pen_t = ValueTracker(-1.0)

        def cur_y(t):
            a = pull.get_value()
            return (1 - a) * student_y(t) + a * master_y(t)
        pen.add_updater(lambda m: m.move_to(
            screen_point(pen_t.get_value(), cur_y(pen_t.get_value())) + UP * 0.16))
        self.add(pen)

        self.play(
            pull.animate.set_value(1.0),
            pen_t.animate.set_value(1.0),
            dist.animate.set_value(0.0),
            run_time=1.25, rate_func=smooth,
        )
        student.clear_updaters()
        student.set_points_smoothly([screen_point(t, master_y(t)) for t in ts])
        student.set_stroke(WHITE, 3.2)
        pen.clear_updaters()
        dist_read.clear_updaters()
        dist.set_value(0.0)

        self.play(FadeOut(pen, run_time=0.2),
                  Flash(screen_point(0.0, master_y(0.0)), color=WHITE,
                        flash_radius=1.2, line_length=0.14, num_lines=14,
                        run_time=0.5))
        self.wait(0.12)

        # ================================================================
        # BEAT 8 — NAME (1.83s): clear to serif #fff 'distillation' + sub.
        # ================================================================
        self.next_section("name")

        panel = VGroup(master, student, master_lbl, trace_lbl,
                       dist_read, dist_tag, rule)
        self.play(FadeOut(panel, shift=UP * 0.15),
                  FadeOut(top1), FadeOut(top2), run_time=0.5)
        self.remove(*panel)

        name = serif("distillation", 54, WHITE).move_to([0, 0.4, 0])
        name_g = glow(name)
        sub = mono("copy the rich picture, not just the verdict", 18, INK_DIM)
        sub.next_to(name, DOWN, buff=0.3)
        self.add(name_g)
        self.play(GrowFromCenter(name), FadeIn(sub, shift=UP * 0.08),
                  run_time=0.6)
        self.play(Indicate(name, scale_factor=1.06, color=WHITE), run_time=0.45)
        self.wait(0.5)
