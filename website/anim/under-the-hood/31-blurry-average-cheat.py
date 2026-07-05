# website/anim/b14_blurry_average_cheat.py  —  B14 "The lazy shortcut"
#
# Pure "just be close" distillation has a cheat: if a point only has to land
# CLOSE to two distinct teacher targets, the laziest answer is to sit dead in
# the middle — equidistant from both, scoring great, yet being NEITHER sound.
#
# Locked 7-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 pose      TOP context + feature frame + lone faint student point.       2.57
#   2 targets   two ringed targets fade in well-separated + dashed span.      1.74
#   3 puzzle    two pull-lines tug toward BOTH; student still OFF-centre.     1.39
#   4 midpoint  student slides to exact middle; '=' marks; meter pegs full.   1.94
#   5 loupe     magnifier drops; targets + student drift inward, lose crisp.  0.97
#   6 smudge    they collapse to one grey blob; meter still high (irony).     1.57
#   7 name      serif #fff "close is not correct" + sub; final soft pulse.    1.78
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

TOP_Y = 3.25
PLANE_C = np.array([-0.6, 0.15, 0])   # centre of the feature-plane band
BOT_Y = -3.35


def target_dot(label, at, sub):
    """A bright distinct sound target: a ringed dot + name + sub-label."""
    ring = Circle(radius=0.20, stroke_color=INK, stroke_width=2.2, fill_opacity=0)
    core = Dot(radius=0.085, color=INK).set_fill(INK, 1.0)
    g = VGroup(ring, core).move_to(at)
    name = serif(label, 24, INK).next_to(g, UP, buff=0.18)
    tag = mono(sub, 13, INK_FAINT).next_to(g, DOWN, buff=0.16)
    return VGroup(g, name, tag), g


class BlurryAverageCheat(Scene):
    def construct(self):
        seed()

        # ============================================================
        # BEAT 1 — POSE (2.57s): TOP context, feature frame, lone student.
        # ============================================================
        self.next_section("pose")

        top1 = mono("the student copies one long string of numbers", 20, INK_DIM)
        top1.move_to([0, TOP_Y, 0])
        top2 = mono('its only job: "be close" to the teacher', 15, INK_FAINT)
        top2.move_to([0, TOP_Y - 0.46, 0])
        rule = Line([-6.2, TOP_Y - 0.74, 0], [6.2, TOP_Y - 0.74, 0],
                    stroke_color=LINE, stroke_width=1.2)
        top_ctx = VGroup(top1, top2, rule)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.5)
        self.play(FadeIn(top2), Create(rule), run_time=0.45)

        # a faint feature-space frame so "two points in a space" reads literally.
        plane = Rectangle(width=9.4, height=4.0, stroke_color=INK_GHOST,
                          stroke_width=1.2, fill_opacity=0).move_to(PLANE_C)
        plane_lbl = mono("feature space", 13, INK_GHOST)
        plane_lbl.next_to(plane, UP, buff=0.10).align_to(plane, LEFT).shift(RIGHT * 0.1)
        self.play(Create(plane), FadeIn(plane_lbl), run_time=0.55)

        # the lone STUDENT point — off to one side, faint (no targets yet).
        s_start = PLANE_C + np.array([-0.2, 1.30, 0])
        student = Dot(radius=0.10, color=INK).set_fill(INK, 0.45)
        student.move_to(s_start)
        s_lbl = mono("student", 15, INK_DIM).next_to(student, UP, buff=0.16)
        s_lbl.add_updater(lambda m: m.next_to(student, UP, buff=0.16))
        self.play(FadeIn(student, scale=0.5), FadeIn(s_lbl), run_time=0.55)
        self.wait(0.45)

        # ============================================================
        # BEAT 2 — TARGETS (1.74s): two well-separated sounds + dashed span.
        # ============================================================
        self.next_section("targets")

        p1 = PLANE_C + np.array([-2.9, -0.30, 0])
        p2 = PLANE_C + np.array([2.9, -0.30, 0])
        t1_grp, t1 = target_dot("sound one", p1, "what the teacher hears · A")
        t2_grp, t2 = target_dot("sound two", p2, "what the teacher hears · B")
        self.play(LaggedStart(FadeIn(t1_grp, shift=RIGHT * 0.12),
                              FadeIn(t2_grp, shift=LEFT * 0.12),
                              lag_ratio=0.25), run_time=0.85)

        gap = DashedLine(t1.get_right() + RIGHT * 0.12, t2.get_left() + LEFT * 0.12,
                         dash_length=0.10, stroke_color=INK_GHOST, stroke_width=1.4)
        gap_lbl = mono("two sounds the words depend on", 14, INK_FAINT)
        gap_lbl.next_to(gap, DOWN, buff=0.14)
        self.play(Create(gap), FadeIn(gap_lbl, shift=UP * 0.06), run_time=0.55)
        self.wait(0.34)

        # ============================================================
        # BEAT 3 — PUZZLE (1.39s): pull toward BOTH; student still OFF-centre.
        # ============================================================
        self.next_section("puzzle")

        pull1 = always_redraw(lambda: Line(
            student.get_center(), t1.get_center(),
            stroke_color=INK, stroke_width=1.8).set_opacity(0.6))
        pull2 = always_redraw(lambda: Line(
            student.get_center(), t2.get_center(),
            stroke_color=INK, stroke_width=1.8).set_opacity(0.6))
        pull_cap = mono('"be close" pulls toward both at once', 16, INK_DIM)
        pull_cap.move_to([PLANE_C[0], PLANE_C[1] + 1.10, 0])

        # dim the context a touch so the gap + pulls own the focus.
        self.play(FadeIn(pull1), FadeIn(pull2), FadeIn(pull_cap),
                  top_ctx.animate.set_opacity(0.5), run_time=0.55)
        # a small hesitation in place — invite the prediction, stay off-centre.
        self.play(student.animate.shift(RIGHT * 0.35), run_time=0.42,
                  rate_func=there_and_back)
        self.wait(0.42)

        # ============================================================
        # BEAT 4 — MIDPOINT (1.94s): slide to exact middle; '=' marks; meter full.
        # ============================================================
        self.next_section("midpoint")

        s_mid = (t1.get_center() + t2.get_center()) / 2

        # BOTTOM meter — false success encoded as brightness (lower distance = fuller).
        def avg_dist():
            d1 = np.linalg.norm(student.get_center() - t1.get_center())
            d2 = np.linalg.norm(student.get_center() - t2.get_center())
            return (d1 + d2) / 2.0

        meter_w = 5.0
        meter_x = -0.6
        track = RoundedRectangle(width=meter_w, height=0.26, corner_radius=0.05,
                                 stroke_color=INK_GHOST, stroke_width=1.2,
                                 fill_opacity=0).move_to([meter_x, BOT_Y + 0.05, 0])
        d0 = avg_dist()  # starting (off-centre) distance -> baseline

        def fill_width():
            frac = np.clip(1.0 - avg_dist() / (d0 * 1.05), 0.05, 1.0)
            return meter_w * frac

        fill = always_redraw(lambda: RoundedRectangle(
            width=max(fill_width(), 0.06), height=0.26, corner_radius=0.05,
            stroke_width=0, fill_color=INK,
            fill_opacity=0.30 + 0.60 * np.clip(1.0 - avg_dist() / (d0 * 1.05), 0, 1)
        ).align_to(track, LEFT).set_y(track.get_y()))
        meter_lbl = mono("copy-score · closeness", 14, INK_FAINT)
        meter_lbl.next_to(track, DOWN, buff=0.14)
        good_lbl = mono("looks great", 15, INK_DIM).next_to(track, RIGHT, buff=0.3)
        self.play(Create(track), FadeIn(meter_lbl), run_time=0.35)
        self.add(fill)

        # the single settle: slide straight to the exact midpoint and brighten.
        self.play(student.animate.move_to(s_mid).set_fill(INK, 0.95),
                  run_time=0.9, rate_func=smooth)

        # equidistant marks — the two equal distances meeting at the midpoint.
        eqL = mono("=", 18, INK_DIM).move_to(
            (student.get_center() + t1.get_center()) / 2 + UP * 0.30)
        eqR = mono("=", 18, INK_DIM).move_to(
            (student.get_center() + t2.get_center()) / 2 + UP * 0.30)
        self.play(FadeIn(eqL, scale=0.6), FadeIn(eqR, scale=0.6),
                  FadeIn(good_lbl, shift=LEFT * 0.08), run_time=0.45)
        self.wait(0.24)

        # ============================================================
        # BEAT 5 — LOUPE (0.97s): magnifier drops; points drift inward, lose crisp.
        # ============================================================
        self.next_section("loupe")

        pull1.clear_updaters()
        pull2.clear_updaters()
        s_lbl.clear_updaters()

        loupe_c = np.array([s_mid[0], s_mid[1], 0])
        loupe = Circle(radius=0.95, stroke_color=INK_FAINT, stroke_width=1.8,
                       fill_opacity=0).move_to(loupe_c)
        loupe_stem = Line(loupe.get_corner(DR) + np.array([-0.05, 0.05, 0]),
                          loupe.get_corner(DR) + np.array([0.35, -0.35, 0]),
                          stroke_color=INK_FAINT, stroke_width=3.0)

        magnify = mono("zoom in on what the student learned", 15, INK_FAINT)
        magnify.move_to(pull_cap.get_center())

        # dim TOP context further; targets + student drift inward, blur their crispness.
        self.play(
            Create(loupe), Create(loupe_stem),
            ReplacementTransform(pull_cap, magnify),
            top_ctx.animate.set_opacity(0.28),
            t1.animate.move_to(loupe_c + LEFT * 0.30).set_stroke(width=1.2),
            t2.animate.move_to(loupe_c + RIGHT * 0.30).set_stroke(width=1.2),
            FadeOut(t1_grp[1]), FadeOut(t1_grp[2]),
            FadeOut(t2_grp[1]), FadeOut(t2_grp[2]),
            FadeOut(eqL), FadeOut(eqR), FadeOut(gap), FadeOut(gap_lbl),
            run_time=0.97,
        )

        # ============================================================
        # BEAT 6 — SMUDGE (1.57s): collapse to one grey blob; meter still high.
        # ============================================================
        self.next_section("smudge")

        smudge = VGroup(*[
            Dot(radius=r, color=INK).set_fill(INK, op).move_to(loupe_c)
            for r, op in [(0.46, 0.10), (0.34, 0.16), (0.24, 0.24), (0.14, 0.34)]
        ])
        movers = [t1, t2, student]
        self.play(
            *[m.animate.move_to(loupe_c).set_opacity(0.0) for m in movers],
            FadeOut(s_lbl),
            FadeIn(smudge),
            run_time=0.7,
        )
        self.remove(*movers, pull1, pull2)

        # quiet stroke-width pulse on the loupe flags the irony — meter stays lit.
        for w in (3.6, 1.8, 3.6, 1.8):
            self.play(loupe.animate.set_stroke(width=w), run_time=0.16,
                      rate_func=linear)
        self.wait(0.23)

        # ============================================================
        # BEAT 7 — NAME (1.78s): serif #fff payoff + sub; final soft pulse.
        # ============================================================
        self.next_section("name")

        self.play(
            FadeOut(VGroup(track, fill, meter_lbl, good_lbl)),
            FadeOut(magnify), FadeOut(plane_lbl),
            run_time=0.4,
        )

        punch = serif("close is not correct", 46, WHITE).move_to(
            [PLANE_C[0], BOT_Y + 0.55, 0])
        sub = mono("a smooth blur scores well — and means nothing", 17, INK_DIM)
        sub.next_to(punch, DOWN, buff=0.20)
        glow_punch = glow(punch)
        self.add(glow_punch)
        self.play(GrowFromCenter(punch), FadeIn(sub, shift=UP * 0.08), run_time=0.6)

        self.play(Indicate(smudge, scale_factor=1.14, color=INK), run_time=0.45)
        self.wait(0.3)
