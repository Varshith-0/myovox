# b12_copy_the_teacher.py — B12 "Tracing the master" (knowledge distillation)
#
# The third head exists for a trick: a STUDENT copies a TEACHER's rich internal
# PICTURE, not just the final right/wrong verdict. Metaphor: tracing paper laid
# over a master's brushstroke — you match the whole shape, point by point, not
# just where the line ends.
#
# Three-zone, scrubbable, monotonic composition (3b1b: pose -> build -> transform
# -> name):
#   TOP    (y ~ +2.6..+3.5) CONTEXT: where we are — "the third head: a 1024-num
#          projection" carried over from B11 'heads'; a quiet rail.
#   CENTER (-1.4..+2.2)     MECHANISM:
#          POSE: a faint confident MASTER curve (the teacher's internal picture).
#          BUILD: a crude wobbly STUDENT line, graded ONLY by its endpoint dot.
#          TRANSFORM: lay the master over as a guide; a shared ValueTracker pulls
#          the WHOLE student line onto the master's shape, point by point, while a
#          live distance readout via counter() free-falls toward 0.
#   BOTTOM (-3.6..-2.4)     CONTRAST -> NAME: "right / wrong only" vs "trace the
#          whole stroke" side by side; the traced student is far closer; resolve
#          to serif #fff 'distillation' + 'copy the rich picture, not just the
#          verdict'. Hands to the audio teacher next.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# ---- canvas zones ----------------------------------------------------------
TOP_Y = 3.18
RULE_Y = 2.58
PANEL_Y = 0.45        # centre of the tracing panel
BOT_Y = -3.0
X_L, X_R = -6.6, 6.6

# ---- the two shapes (x in panel coords; we map to screen) ------------------
PANEL_W = 6.6
PANEL_X = 0.0         # panel centre x


def master_y(t):
    """The teacher's confident curve — a smooth, distinctive S-stroke."""
    return 0.95 * np.sin(2.4 * t + 0.4) + 0.32 * np.sin(5.1 * t)


def student_y(t):
    """The student's crude first attempt — wobbly, wrong shape, but it happens
    to END near the master (so endpoint-only grading calls it 'good enough')."""
    crude = 0.45 * np.sin(1.1 * t - 1.2) - 0.30 * np.cos(3.3 * t) + 0.18
    # pin both ends to the master so the endpoint verdict is misleadingly happy
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
        # B0 — TOP CONTEXT: inherit the third head from B11 'heads'.
        # ================================================================
        self.next_section("context")

        top1 = mono("THE THIRD OUTPUT", 24, INK_DIM, w=BOLD).move_to([0, TOP_Y, 0])
        top2 = mono("a 1024-number projection — what is it for?", 17, INK_FAINT)
        top2.move_to([0, TOP_Y - 0.5, 0])
        rule = Line([X_L, RULE_Y, 0], [X_R, RULE_Y, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.4)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)

        # ================================================================
        # B1 — POSE: the MASTER's confident curve (the teacher's picture).
        #      Drawn faint — it is the thing to be copied, present from now.
        # ================================================================
        self.next_section("master")

        master = VMobject(stroke_color=INK_DIM, stroke_width=2.6)
        master.set_points_smoothly([screen_point(t, master_y(t)) for t in ts])
        master.set_opacity(0.55)
        master_lbl = mono("teacher's internal picture", 17, INK_DIM)
        master_lbl.move_to([PANEL_X, PANEL_Y + 1.9, 0])
        master_tag = mono("the whole detailed shape it forms", 14, INK_FAINT)
        master_tag.next_to(master_lbl, DOWN, buff=0.12)

        self.play(FadeIn(master_lbl, shift=DOWN * 0.08), run_time=0.3)
        self.play(Create(master), FadeIn(master_tag), run_time=0.95)

        # ================================================================
        # B2 — BUILD: the STUDENT's crude attempt, graded ONLY by endpoint.
        # ================================================================
        self.next_section("student")

        student = VMobject(stroke_color=INK, stroke_width=3.0)
        student.set_points_smoothly([screen_point(t, student_y(t)) for t in ts])
        stu_lbl = mono("student's first attempt", 17, INK).move_to(
            [PANEL_X, PANEL_Y - 2.0, 0])
        self.play(FadeIn(stu_lbl, shift=UP * 0.08), run_time=0.3)
        self.play(Create(student), run_time=0.85)

        # The endpoint-only verdict: both ends already touch the master -> a tick.
        end_pt = screen_point(1.0, student_y(1.0))
        endpoint_dot = Dot(end_pt, radius=0.075, color=INK)
        endpoint_ring = Circle(radius=0.22, stroke_color=INK_FAINT,
                               stroke_width=1.6).move_to(end_pt)
        verdict = mono("endpoint matches  ✓", 16, INK_FAINT)
        verdict.next_to(endpoint_ring, UP, buff=0.16).shift(LEFT * 0.2)
        if verdict.get_right()[0] > X_R:
            verdict.next_to(endpoint_ring, LEFT, buff=0.16)
        self.play(FadeIn(endpoint_dot, scale=0.5), Create(endpoint_ring),
                  run_time=0.3)
        self.play(FadeIn(verdict, shift=DOWN * 0.06), run_time=0.3)

        # but the SHAPE is wrong — shade the gap between the two lines.
        gap = VGroup(*[
            Line(screen_point(t, student_y(t)), screen_point(t, master_y(t)),
                 stroke_color=INK_GHOST, stroke_width=1.0)
            for t in np.linspace(-0.86, 0.86, 26)
        ])
        gap_lbl = mono("grade only right / wrong  →  shape is still wrong",
                       15, INK_FAINT).move_to([PANEL_X, PANEL_Y - 2.5, 0])
        self.play(LaggedStartMap(Create, gap, lag_ratio=0.02, run_time=0.5),
                  FadeIn(gap_lbl), run_time=0.5)
        self.wait(0.1)

        # ================================================================
        # B3 — TRANSFORM: trace the WHOLE stroke. One ValueTracker pulls the
        #      student's entire line onto the master, while a distance readout
        #      free-falls toward 0 (the 'pull downhill' idiom).
        # ================================================================
        self.next_section("trace")

        # retire the endpoint-only framing; bring up the tracing-paper guide.
        trace_lbl = mono("trace the whole stroke", 19, INK).move_to(stu_lbl)
        self.play(
            FadeOut(verdict), FadeOut(endpoint_ring), FadeOut(endpoint_dot),
            FadeOut(gap_lbl), FadeOut(gap),
            ReplacementTransform(stu_lbl, trace_lbl),
            run_time=0.45,
        )

        # brighten the master into a clear "tracing-paper" guide overlay.
        self.play(master.animate.set_stroke(INK_DIM, 2.6, opacity=0.8),
                  run_time=0.3)

        # the pull: blend student_y -> master_y by a shared tracker.
        pull = ValueTracker(0.0)

        def blended_points():
            a = pull.get_value()
            return [screen_point(t, (1 - a) * student_y(t) + a * master_y(t))
                    for t in ts]

        student.add_updater(lambda m: m.set_points_smoothly(blended_points()))

        # live residual-distance readout (mean |gap|), free-falling toward 0.
        def residual():
            a = pull.get_value()
            diffs = np.array([(1 - a) * student_y(t) + a * master_y(t) - master_y(t)
                              for t in ts])
            return float(np.mean(np.abs(diffs)) * 100.0)   # scaled "distance"

        dist = ValueTracker(residual())
        dist_at = np.array([X_R - 1.55, PANEL_Y + 0.0, 0])
        dist_read = counter(dist, fmt=lambda v: f"{max(v,0):4.1f}", s=40, c=INK,
                            at=dist_at)
        dist_tag = mono("distance to teacher", 13, INK_DIM)
        dist_tag.next_to(dist_read, UP, buff=0.16)
        self.add(dist_read)
        self.play(FadeIn(dist_read), FadeIn(dist_tag), run_time=0.3)

        # a moving "tracing pen" rides the student line as it is pulled over.
        pen = Triangle(stroke_width=0, fill_color=WHITE, fill_opacity=0.95)
        pen.scale(0.085).rotate(PI)
        pen_t = ValueTracker(-1.0)

        def cur_y(t):
            a = pull.get_value()
            return (1 - a) * student_y(t) + a * master_y(t)
        pen.add_updater(lambda m: m.move_to(
            screen_point(pen_t.get_value(), cur_y(pen_t.get_value())) + UP * 0.16))
        self.add(pen)

        # The trace: pull 0->1, pen sweeps L->R, distance falls — all locked.
        self.play(
            pull.animate.set_value(1.0),
            pen_t.animate.set_value(1.0),
            dist.animate.set_value(0.0),
            run_time=2.4, rate_func=smooth,
        )
        student.clear_updaters()
        student.set_points_smoothly([screen_point(t, master_y(t)) for t in ts])
        student.set_stroke(WHITE, 3.2)
        pen.clear_updaters()
        dist_read.clear_updaters()
        dist.set_value(0.0)

        # christen the match: the student line now lies ON the master.
        self.play(FadeOut(pen, run_time=0.2),
                  Flash(screen_point(0.0, master_y(0.0)), color=WHITE,
                        flash_radius=1.2, line_length=0.14, num_lines=14,
                        run_time=0.5))
        matched = mono("line now matches the master, point by point", 15, INK_DIM)
        matched.move_to([PANEL_X, PANEL_Y - 2.5, 0])
        self.play(FadeIn(matched, shift=UP * 0.06), run_time=0.3)
        self.wait(0.35)

        # ================================================================
        # B4 — CONTRAST: 'right/wrong only' vs 'trace the whole stroke'.
        #      Clear the panel, drop two tiny side-by-side sketches below.
        # ================================================================
        self.next_section("contrast")

        panel = VGroup(master, student, master_lbl, master_tag, trace_lbl,
                       dist_read, dist_tag, matched)
        self.play(FadeOut(panel, shift=UP * 0.15), run_time=0.45)
        self.remove(*panel)

        head = mono("two ways to grade the student", 20, INK_DIM)
        head.move_to([0, 1.95, 0])
        self.play(FadeIn(head, shift=DOWN * 0.08), run_time=0.3)

        def mini(student_fn, sw=2.4, sop=1.0, show_gap=False):
            """A small master(faint)+student sketch in panel-local coords.
            show_gap shades the residual between the two lines (= 'still wrong')."""
            mts = np.linspace(-1.0, 1.0, 90)
            m = VMobject(stroke_color=INK_DIM, stroke_width=1.8)
            m.set_points_smoothly([[t * 1.15, master_y(t) * 0.5, 0] for t in mts])
            m.set_opacity(0.5)
            s = VMobject(stroke_color=INK, stroke_width=sw)
            s.set_points_smoothly([[t * 1.15, student_fn(t) * 0.5, 0] for t in mts])
            s.set_stroke(opacity=sop)
            out = VGroup(m, s)
            if show_gap:
                gap = VGroup(*[
                    Line([t * 1.15, student_fn(t) * 0.5, 0],
                         [t * 1.15, master_y(t) * 0.5, 0],
                         stroke_color=INK_GHOST, stroke_width=1.0)
                    for t in np.linspace(-0.82, 0.82, 18)
                ])
                out.add(gap)
            return out

        # LEFT: endpoint-only -> crude student kept (far off); shade the gap.
        left = mini(student_y, sw=2.4, sop=0.85, show_gap=True)
        left_box = SurroundingRectangle(left, color=LINE, stroke_width=1.2,
                                        buff=0.3)
        left_grp = VGroup(left, left_box).move_to([-3.3, 0.05, 0])
        left_t1 = mono("grade right / wrong only", 15, INK_FAINT)
        left_t1.next_to(left_grp, UP, buff=0.16)
        left_t2 = mono("student stays crude", 14, INK_FAINT)
        left_t2.next_to(left_grp, DOWN, buff=0.16)

        # RIGHT: trace whole stroke -> student matches.
        right = mini(master_y, sw=2.8, sop=1.0)
        right[1].set_stroke(WHITE, 2.8)
        right_box = SurroundingRectangle(right, color=INK_FAINT, stroke_width=1.4,
                                         buff=0.3)
        right_grp = VGroup(right, right_box).move_to([3.3, 0.05, 0])
        right_t1 = mono("trace the whole stroke", 15, INK_DIM)
        right_t1.next_to(right_grp, UP, buff=0.16)
        right_t2 = mono("student matches the master", 14, INK_DIM)
        right_t2.next_to(right_grp, DOWN, buff=0.16)

        self.play(
            FadeIn(left_grp, shift=RIGHT * 0.1), FadeIn(left_t1), FadeIn(left_t2),
            run_time=0.45,
        )
        self.play(
            FadeIn(right_grp, shift=LEFT * 0.1), FadeIn(right_t1), FadeIn(right_t2),
            run_time=0.45,
        )
        self.play(Indicate(right[1], scale_factor=1.06, color=WHITE),
                  right_box.animate.set_stroke(WHITE, 1.8),
                  run_time=0.45)
        self.wait(0.3)

        # ================================================================
        # B5 — NAME IT + poster hold. Hands to the audio teacher next.
        # ================================================================
        self.next_section("name")

        name = serif("distillation", 50, WHITE).move_to([0, -2.45, 0])
        name_g = glow(name)
        sub = mono("copy the rich picture, not just the verdict", 17, INK_DIM)
        sub.next_to(name, DOWN, buff=0.2)
        self.add(name_g)
        self.play(GrowFromCenter(name), FadeIn(sub, shift=UP * 0.08),
                  run_time=0.55)
        self.wait(0.6)
