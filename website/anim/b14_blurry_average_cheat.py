# website/anim/b14_blurry_average_cheat.py  —  B14 "The lazy shortcut"
#
# The HOOK question carried from S24 (the honesty lock): why bolt a LOCKED reader
# onto the copied feature? Because pure "just be close" distillation has a cheat.
#
# The idea, made visual on a feature plane (x in [-7,7], y in [-3.9,3.9]):
#   POSE   : two well-separated target points — "sound one" / "sound two" — the
#            continuous feature the student is told to copy.  A lone student point
#            sits off to the side.
#   BUILD  : a "be close" force (the downhill pull again) drags the student toward
#            BOTH targets at once; a distance meter improves; brightness/glow encode
#            the FALSE success — never colour.
#   TRANSFORM: across examples the student parks at the exact MIDPOINT, equidistant
#            from both. A magnifier shows the two sounds now overlap inside one grey
#            smudge — "difference erased".
#   WARN   : a stroke-width pulse (no colour, no alarm ring) flags the danger.
#   NAME   : serif #fff "close is not correct" + mono "a smooth blur scores well,
#            means nothing" — exactly the failure the honesty lock guards against.
#
# Persistent zones: TOP context line, CENTER feature-plane mechanism, BOTTOM meter
# + takeaway.  Built monotonically so it reads at any paused scroll frame.
from manim import *
from emg_style import *
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
    name = serif(label, 26, INK).next_to(g, UP, buff=0.18)
    tag = mono(sub, 14, INK_FAINT).next_to(g, DOWN, buff=0.16)
    return VGroup(g, name, tag), g


class BlurryAverageCheat(Scene):
    def construct(self):
        seed()

        # ============================================================
        # B0 — POSE: the feature plane + two distinct sound targets.
        # ============================================================
        self.next_section("pose")

        # TOP context — carries the hook straight out of the honesty lock (S24).
        top1 = mono("the student copies one long string of numbers", 20, INK_DIM)
        top1.move_to([0, TOP_Y, 0])
        top2 = mono('its only job: "be close" to the teacher', 15, INK_FAINT)
        top2.move_to([0, TOP_Y - 0.46, 0])
        rule = Line([-6.2, TOP_Y - 0.74, 0], [6.2, TOP_Y - 0.74, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)

        # A faint feature-space frame so "two points in a space" reads literally.
        plane_w, plane_h = 9.4, 4.3
        plane = Rectangle(width=plane_w, height=plane_h, stroke_color=INK_GHOST,
                          stroke_width=1.2, fill_opacity=0).move_to(PLANE_C)
        plane_lbl = mono("feature space", 13, INK_GHOST)
        plane_lbl.next_to(plane, UP, buff=0.10).align_to(plane, LEFT).shift(RIGHT * 0.1)
        self.play(Create(plane), FadeIn(plane_lbl), run_time=0.45)

        # the two targets, well separated on the plane.
        p1 = PLANE_C + np.array([-2.9, -0.15, 0])
        p2 = PLANE_C + np.array([2.9, -0.15, 0])
        t1_grp, t1 = target_dot("sound one", p1, "what the teacher hears  ·  A")
        t2_grp, t2 = target_dot("sound two", p2, "what the teacher hears  ·  B")
        self.play(LaggedStart(FadeIn(t1_grp, shift=RIGHT * 0.12),
                              FadeIn(t2_grp, shift=LEFT * 0.12),
                              lag_ratio=0.25), run_time=0.6)

        # a dashed "they must stay apart" span between the two true sounds.
        gap = DashedLine(t1.get_right() + RIGHT * 0.12, t2.get_left() + LEFT * 0.12,
                         dash_length=0.10, stroke_color=INK_GHOST, stroke_width=1.4)
        gap_lbl = mono("two sounds the words depend on", 14, INK_FAINT)
        gap_lbl.next_to(gap, UP, buff=0.12)
        self.play(Create(gap), FadeIn(gap_lbl, shift=UP * 0.06), run_time=0.45)

        # the lone STUDENT point — starts off to one side, faint.
        s_start = PLANE_C + np.array([-0.2, 1.45, 0])
        student = Dot(radius=0.10, color=INK).set_fill(INK, 0.45)
        student.move_to(s_start)
        s_lbl = mono("student", 15, INK_DIM).next_to(student, UP, buff=0.16)
        s_lbl.add_updater(lambda m: m.next_to(student, UP, buff=0.16))
        self.play(FadeIn(student, scale=0.5), FadeIn(s_lbl), run_time=0.4)

        # ============================================================
        # B1 — BUILD: the "be close" force drags the student toward BOTH.
        # ============================================================
        self.next_section("pull")

        # two pull-lines (the downhill gradient again) tug the student to each target.
        pull1 = always_redraw(lambda: Line(
            student.get_center(), t1.get_center(),
            stroke_color=INK_GHOST, stroke_width=1.6).set_opacity(0.55))
        pull2 = always_redraw(lambda: Line(
            student.get_center(), t2.get_center(),
            stroke_color=INK_GHOST, stroke_width=1.6).set_opacity(0.55))
        pull_cap = mono('"be close" pulls toward both at once', 15, INK_FAINT)
        pull_cap.move_to([PLANE_C[0], PLANE_C[1] + 1.05, 0])
        self.add(pull1, pull2)
        self.play(FadeIn(pull_cap), run_time=0.3)

        # ---- BOTTOM: a live distance meter (false success encoded as brightness) ----
        # avg distance from student to the two targets; lower = "looks better".
        def avg_dist():
            d1 = np.linalg.norm(student.get_center() - t1.get_center())
            d2 = np.linalg.norm(student.get_center() - t2.get_center())
            return (d1 + d2) / 2.0

        meter_w = 5.2
        meter_x = -0.6
        track = RoundedRectangle(width=meter_w, height=0.26, corner_radius=0.05,
                                 stroke_color=INK_GHOST, stroke_width=1.2,
                                 fill_opacity=0).move_to([meter_x, BOT_Y + 0.05, 0])
        d0 = avg_dist()  # starting average distance -> full bar

        def fill_width():
            # bar = how close we are; shrinks as distance grows, grows as it shrinks.
            frac = np.clip(1.0 - avg_dist() / d0, 0.02, 1.0)
            return meter_w * frac

        fill = always_redraw(lambda: RoundedRectangle(
            width=max(fill_width(), 0.06), height=0.26, corner_radius=0.05,
            stroke_width=0, fill_color=INK,
            fill_opacity=0.35 + 0.55 * np.clip(1.0 - avg_dist() / d0, 0, 1)
        ).align_to(track, LEFT).set_y(track.get_y()))
        meter_lbl = mono("copy-score  ·  closeness", 14, INK_FAINT)
        meter_lbl.next_to(track, LEFT, buff=0.3)
        if meter_lbl.get_left()[0] < -6.9:
            meter_lbl.next_to(track, DOWN, buff=0.14)
        good_lbl = mono("looks great", 14, INK_DIM).next_to(track, RIGHT, buff=0.3)
        self.play(Create(track), FadeIn(meter_lbl), run_time=0.4)
        self.add(fill)

        # the student slides DOWN toward the gap centre — meter brightens & fills.
        s_mid = PLANE_C + np.array([0.0, 0.05, 0])
        self.play(student.animate.move_to(s_mid + np.array([0.0, 0.55, 0])),
                  run_time=1.2, rate_func=smooth)
        self.play(FadeIn(good_lbl, shift=LEFT * 0.08), run_time=0.4)

        # ============================================================
        # B2 — TRANSFORM: across examples it parks at the exact MIDPOINT.
        # ============================================================
        self.next_section("midpoint")

        # a few faint "examples" nudge it; each settles it nearer dead-centre.
        examples = mono("across many examples …", 15, INK_GHOST)
        examples.move_to([PLANE_C[0], PLANE_C[1] - 1.55, 0])
        self.play(FadeIn(examples), run_time=0.3)
        for off in (0.22, -0.13, 0.06):
            self.play(student.animate.move_to(s_mid + np.array([off, 0.0, 0])),
                      run_time=0.42, rate_func=there_and_back_with_pause)
        self.play(student.animate.move_to(s_mid).set_fill(INK, 0.92), run_time=0.55)

        # equidistant braces: show the two equal distances meeting at the midpoint.
        eqL = mono("=", 18, INK_DIM).move_to(
            (student.get_center() + t1.get_center()) / 2 + UP * 0.28)
        eqR = mono("=", 18, INK_DIM).move_to(
            (student.get_center() + t2.get_center()) / 2 + UP * 0.28)
        mid_tag = mono("parks at the midpoint  ·  equidistant", 15, INK_DIM)
        mid_tag.move_to([PLANE_C[0], PLANE_C[1] - 1.55, 0])
        self.play(FadeIn(eqL, scale=0.6), FadeIn(eqR, scale=0.6),
                  ReplacementTransform(examples, mid_tag), run_time=0.45)

        # the meter pegs near full — the cheat "scores well".
        self.play(Indicate(VGroup(track, good_lbl), scale_factor=1.05, color=INK_DIM),
                  run_time=0.45)

        # ============================================================
        # B3 — MAGNIFIER: the two sounds melt into one grey smudge.
        # ============================================================
        self.next_section("smudge")

        # freeze the live pulls so we can morph the geometry cleanly.
        pull1.clear_updaters()
        pull2.clear_updaters()
        s_lbl.clear_updaters()

        # a magnifier circle over the midpoint; inside it the two true points and the
        # student all collapse into ONE blurry blob — the difference is erased.
        loupe_c = np.array([PLANE_C[0], PLANE_C[1] - 0.05, 0])
        magnify = mono("zoom in on what the student learned", 15, INK_FAINT)
        magnify.move_to([PLANE_C[0], PLANE_C[1] + 1.05, 0])
        self.play(ReplacementTransform(pull_cap, magnify), run_time=0.35)

        # collapse: both targets + student drift to the centre and dissolve into a
        # soft grey smudge (layered translucent discs = "smooth blur, no structure").
        smudge = VGroup(*[
            Dot(radius=r, color=INK).set_fill(INK, op).move_to(loupe_c)
            for r, op in [(0.46, 0.10), (0.34, 0.16), (0.24, 0.24), (0.14, 0.34)]
        ])
        loupe = Circle(radius=0.95, stroke_color=INK_FAINT, stroke_width=1.8,
                       fill_opacity=0).move_to(loupe_c)
        loupe_stem = Line(loupe.get_corner(DR) + np.array([-0.05, 0.05, 0]),
                          loupe.get_corner(DR) + np.array([0.35, -0.35, 0]),
                          stroke_color=INK_FAINT, stroke_width=3.0)

        # melt the distinct rings/cores + student into the smudge.
        movers = [t1, t2, student]
        self.play(
            *[m.animate.move_to(loupe_c).set_opacity(0.0) for m in movers],
            FadeOut(t1_grp[1]), FadeOut(t1_grp[2]),
            FadeOut(t2_grp[1]), FadeOut(t2_grp[2]),
            FadeOut(eqL), FadeOut(eqR),
            FadeOut(gap), FadeOut(gap_lbl),
            FadeOut(s_lbl),
            FadeIn(smudge),
            Create(loupe), Create(loupe_stem),
            run_time=1.1,
        )
        self.remove(*movers, pull1, pull2)

        erased = mono("difference erased  ·  neither sound, a mushy point between",
                      15, INK_DIM).move_to([PLANE_C[0], PLANE_C[1] - 1.55, 0])
        self.play(ReplacementTransform(mid_tag, erased), run_time=0.4)

        # ============================================================
        # B4 — WARNING: a stroke-width pulse (no colour, no ring-alarm).
        # ============================================================
        self.next_section("warn")
        # the loupe outline thickens & thins twice — a quiet danger pulse.
        for w in (4.0, 1.8, 4.0, 1.8):
            self.play(loupe.animate.set_stroke(width=w), run_time=0.22,
                      rate_func=linear)

        # the meter still reads "great" — drive the irony home.
        irony = mono("the copy-score is still high", 14, INK_FAINT)
        irony.next_to(track, DOWN, buff=0.14)
        self.play(FadeIn(irony, shift=UP * 0.06),
                  Indicate(good_lbl, scale_factor=1.1, color=INK_DIM), run_time=0.4)

        # ============================================================
        # B5 — NAME IT + POSTER HOLD.  (single #fff accent)
        # ============================================================
        self.next_section("name")

        # clear the meter so the payoff owns the bottom; keep the smudge as evidence.
        self.play(FadeOut(VGroup(track, fill, meter_lbl, good_lbl, irony)),
                  FadeOut(magnify),
                  run_time=0.4)

        punch = serif("close is not correct", 46, WHITE).move_to(
            [PLANE_C[0], BOT_Y + 0.5, 0])
        sub = mono("a smooth blur scores well — and means nothing", 17, INK_DIM)
        sub.next_to(punch, DOWN, buff=0.20)
        glow_punch = glow(punch)
        self.add(glow_punch)
        self.play(GrowFromCenter(punch), FadeIn(sub, shift=UP * 0.08),
                  ReplacementTransform(erased, sub.copy().set_opacity(0)),
                  run_time=0.6)

        # the smudge gives one last soft pulse — smooth, scoring, empty.
        self.play(Indicate(smudge, scale_factor=1.12, color=INK), run_time=0.45)
        self.wait(0.6)
