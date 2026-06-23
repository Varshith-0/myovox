# website/anim/b15_frozen_lock_how.py  —  B15 "A reader it can't change"
#
# HOOK carried straight out of B14 (the lazy shortcut): "be close" distillation
# collapses two distinct sounds into ONE grey smudge that still scores well.
# THE FIX, made visual: bolt a PADLOCKED sound-reader onto the student's copied
# features. Its dials are locked — the student cannot soften it. Its one job is to
# check that REAL, DISTINCT sounds can be read out. So the mushy blur now fails
# outright; to pass, the smudge must split back into two crisp, nameable points.
#
# Metaphor: a judge whose verdict you cannot edit.
#
# Three persistent zones, built monotonically so it reads at any paused frame:
#   TOP   (y ~ +3.0): context line carried from B14 + the locked-reader spec.
#   CENTER(-1.6..+2.2): the feature plane. The smudge -> reader -> rejection cross,
#                       then a splitting force -> two crisp points -> reader accepts.
#   BOTTOM(-3.6..-2.8): a verdict strip — REJECTED -> ACCEPTED, then the payoff.
#
# Reject/accept encoded with stroke width + opacity, never colour.  Single pure
# #fff accent reserved for the final "pushed back apart".
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

TOP_Y = 3.22
PLANE_C = np.array([-2.55, 0.25, 0])   # centre of the feature-plane (left of reader)
BOT_Y = -3.30


def padlock(c=INK, sw=2.6, scale=1.0):
    """A small closed padlock glyph: body + shackle + keyhole."""
    body = RoundedRectangle(corner_radius=0.05, width=0.46, height=0.36,
                            stroke_color=c, stroke_width=sw,
                            fill_color=BG, fill_opacity=1)
    shackle = Arc(radius=0.15, start_angle=0, angle=PI,
                  stroke_color=c, stroke_width=sw)
    shackle.next_to(body, UP, buff=-0.02)
    keyhole = Dot(radius=0.034, color=c).move_to(body.get_center())
    return VGroup(shackle, body, keyhole).scale(scale)


def smudge_blob(at, op_scale=1.0):
    """A soft grey smudge — layered translucent discs, no inner structure.
    Continues B14's 'difference erased, a mushy point between' visual."""
    return VGroup(*[
        Dot(radius=r, color=INK).set_fill(INK, op * op_scale).move_to(at)
        for r, op in [(0.42, 0.10), (0.31, 0.16), (0.21, 0.24), (0.12, 0.34)]
    ])


def crisp_point(at, label):
    """A bright, distinct, nameable sound point: ringed dot + serif name."""
    ring = Circle(radius=0.16, stroke_color=INK, stroke_width=2.2, fill_opacity=0)
    core = Dot(radius=0.07, color=INK).set_fill(INK, 1.0)
    dot = VGroup(ring, core).move_to(at)
    name = serif(label, 26, INK).next_to(dot, DOWN, buff=0.14)
    return VGroup(dot, name), dot


class FrozenLockHow(Scene):
    def construct(self):
        seed()

        # ============================================================
        # B0 — POSE: carry B14's smudge forward onto the feature plane.
        # ============================================================
        self.next_section("pose")

        top1 = mono('"be close" let the student collapse two sounds into one blur',
                    19, INK_DIM).move_to([0, TOP_Y, 0])
        top2 = mono("the fix: a sound-reader bolted on that it cannot bend",
                    15, INK_FAINT).move_to([0, TOP_Y - 0.46, 0])
        rule = Line([-6.4, TOP_Y - 0.74, 0], [6.4, TOP_Y - 0.74, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)

        # the feature plane (same frame language as B14), sized to leave room for
        # the reader box on the right.
        plane = Rectangle(width=5.6, height=4.0, stroke_color=INK_GHOST,
                          stroke_width=1.2, fill_opacity=0).move_to(PLANE_C)
        plane_lbl = mono("the student's copied features", 13, INK_GHOST)
        plane_lbl.move_to(plane.get_top() + DOWN * 0.22).align_to(plane, LEFT)
        plane_lbl.shift(RIGHT * 0.18)
        self.play(Create(plane), FadeIn(plane_lbl), run_time=0.42)

        # the inherited smudge — sitting at the midpoint, the blurry "cheat".
        smudge_c = PLANE_C + np.array([0.0, 0.05, 0])
        smudge = smudge_blob(smudge_c)
        s_lbl = mono("one mushy point", 14, INK_FAINT).next_to(smudge, DOWN, buff=0.42)
        self.play(FadeIn(smudge), FadeIn(s_lbl), run_time=0.5)
        # a soft pulse: it still "scores well" on plain closeness.
        self.play(Indicate(smudge, scale_factor=1.12, color=INK), run_time=0.4)

        # ============================================================
        # B1 — BUILD: a padlocked sound-reader clamps onto the features.
        # ============================================================
        self.next_section("clamp")

        reader = RoundedRectangle(corner_radius=0.14, width=2.9, height=2.5,
                                  stroke_color=INK, stroke_width=2.2,
                                  fill_color=BG, fill_opacity=1).move_to([4.05, 0.25, 0])
        reader_lbl = mono("SOUND\nREADER", 20, INK).move_to(
            reader.get_center() + UP * 0.55)
        lock = padlock(INK, sw=2.6).move_to(reader.get_center() + DOWN * 0.30)
        lock_tag = mono("FROZEN · dials locked", 12, INK_FAINT).next_to(
            lock, DOWN, buff=0.16)

        # feed line: features -> reader (a clamp, drawn as a thin bracket arrow).
        feed = Line(plane.get_right() + RIGHT * 0.05, reader.get_left(),
                    stroke_color=INK_DIM, stroke_width=2.0)
        feed_head = Triangle(stroke_width=0, fill_color=INK_DIM, fill_opacity=1.0)
        feed_head.scale(0.07).rotate(-PI / 2).move_to(reader.get_left())

        self.play(Create(reader), FadeIn(reader_lbl), run_time=0.5)
        self.play(Create(feed), FadeIn(feed_head), run_time=0.34)
        self.play(FadeIn(lock, scale=0.6), FadeIn(lock_tag), run_time=0.4)
        # the lock clicks: a quiet flash, no colour.
        self.play(Flash(lock[2].get_center(), color=INK, line_length=0.12,
                        num_lines=10, flash_radius=0.34), run_time=0.4)

        # ============================================================
        # B2 — TRANSFORM A: the reader tries to read the smudge -> garbled.
        # ============================================================
        self.next_section("reject")

        # a pulse carries the smudge INTO the reader.
        carrier = smudge_blob(smudge_c, op_scale=0.9)
        self.add(carrier)
        self.play(carrier.animate.move_to(reader.get_center() + UP * 0.05),
                  run_time=0.55, rate_func=rate_functions.ease_in_sine)
        self.remove(carrier)

        # the reader's exit: it cannot name the blur — garbled, ambiguous output.
        out_anchor = reader.get_right() + RIGHT * 0.05
        garble = mono("? ?", 30, INK_FAINT).move_to(out_anchor + RIGHT * 0.7)
        out_arrow = Line(out_anchor, garble.get_left() + LEFT * 0.12,
                         stroke_color=INK_GHOST, stroke_width=1.8)
        amb_lbl = mono("can't tell which sound", 13, INK_FAINT).next_to(
            garble, DOWN, buff=0.18)
        self.play(Create(out_arrow), FadeIn(garble), FadeIn(amb_lbl), run_time=0.45)

        # REJECTION cross over the garbled output — heavy stroke, no colour.
        cross = Cross(garble, stroke_color=INK, stroke_width=4.0).scale(0.9)
        self.play(Create(cross), run_time=0.3)

        # ---- BOTTOM verdict strip: REJECTED (faint-but-thick, no colour) -------
        verdict_box = RoundedRectangle(corner_radius=0.08, width=3.6, height=0.62,
                                       stroke_color=INK, stroke_width=1.6,
                                       fill_opacity=0).move_to([0, BOT_Y + 0.1, 0])
        verdict = mono("REJECTED", 22, INK_DIM).move_to(verdict_box)
        why = mono("the locked reader can't be softened — the blur fails outright",
                   15, INK_FAINT).next_to(verdict_box, DOWN, buff=0.18)
        self.play(Create(verdict_box), FadeIn(verdict), run_time=0.4)
        self.play(FadeIn(why, shift=UP * 0.06), run_time=0.34)
        # a stroke-width pulse on the verdict box — the failure registers.
        for w in (3.4, 1.6):
            self.play(verdict_box.animate.set_stroke(width=w), run_time=0.16,
                      rate_func=linear)

        # ============================================================
        # B3 — TRANSFORM B: a force splits the smudge into two crisp points;
        #      the frozen reader now names them cleanly -> ACCEPTED.
        # ============================================================
        self.next_section("split")

        # clear the rejected output to make room for the clean read.
        self.play(FadeOut(VGroup(garble, cross, out_arrow, amb_lbl)),
                  FadeOut(s_lbl), run_time=0.34)

        # the splitting force: two opposed arrows pull the smudge apart.
        p_left = smudge_c + np.array([-1.45, 0.0, 0])
        p_right = smudge_c + np.array([1.45, 0.0, 0])
        force_l = Line(smudge_c + LEFT * 0.2, p_left + RIGHT * 0.2,
                       stroke_color=INK_DIM, stroke_width=2.4)
        force_r = Line(smudge_c + RIGHT * 0.2, p_right + LEFT * 0.2,
                       stroke_color=INK_DIM, stroke_width=2.4)
        head_l = Triangle(stroke_width=0, fill_color=INK_DIM, fill_opacity=1.0)
        head_l.scale(0.07).rotate(PI / 2).move_to(p_left + RIGHT * 0.18)
        head_r = Triangle(stroke_width=0, fill_color=INK_DIM, fill_opacity=1.0)
        head_r.scale(0.07).rotate(-PI / 2).move_to(p_right + LEFT * 0.18)
        force_cap = mono("to pass, it must pull the two sounds apart", 15, INK_FAINT)
        force_cap.move_to([PLANE_C[0], PLANE_C[1] + 1.35, 0])
        self.play(FadeIn(force_cap), run_time=0.3)
        self.play(GrowFromCenter(force_l), GrowFromCenter(force_r),
                  FadeIn(head_l), FadeIn(head_r), run_time=0.4)

        # the smudge splinters into two crisp, nameable points.
        pt1_grp, pt1 = crisp_point(p_left, "S")
        pt2_grp, pt2 = crisp_point(p_right, "Z")
        self.play(
            FadeOut(smudge),
            TransformFromCopy(smudge, pt1_grp),
            TransformFromCopy(smudge, pt2_grp),
            run_time=0.7,
        )
        self.play(FadeOut(VGroup(force_l, force_r, head_l, head_r)), run_time=0.25)

        # carry the two crisp points into the reader; it reads them cleanly.
        c1 = pt1.copy()
        c2 = pt2.copy()
        self.add(c1, c2)
        self.play(c1.animate.move_to(reader.get_center() + UP * 0.05),
                  c2.animate.move_to(reader.get_center() + UP * 0.05),
                  run_time=0.5, rate_func=rate_functions.ease_in_sine)
        self.remove(c1, c2)

        # clean named output: two distinct sounds, accepted.
        outS = serif("S", 34, INK).move_to(out_anchor + RIGHT * 0.7 + UP * 0.55)
        outZ = serif("Z", 34, INK).move_to(out_anchor + RIGHT * 0.7 + DOWN * 0.55)
        arrU = Line(out_anchor + UP * 0.25, outS.get_left() + LEFT * 0.12,
                    stroke_color=INK_DIM, stroke_width=2.0)
        arrD = Line(out_anchor + DOWN * 0.25, outZ.get_left() + LEFT * 0.12,
                    stroke_color=INK_DIM, stroke_width=2.0)
        check = mono("✓", 26, INK).next_to(VGroup(outS, outZ), RIGHT, buff=0.22)
        self.play(Create(arrU), Create(arrD), FadeIn(outS), FadeIn(outZ),
                  run_time=0.45)
        self.play(FadeIn(check, scale=0.6), run_time=0.3)

        # ---- BOTTOM verdict flips: REJECTED -> ACCEPTED (brighter, thicker) ----
        verdict_ok = mono("ACCEPTED", 22, INK).move_to(verdict_box)
        why_ok = mono("two real, distinct sounds read straight out of the copy",
                      15, INK_DIM).move_to(why)
        self.play(
            FadeOut(verdict, scale=0.9), FadeIn(verdict_ok, scale=1.05),
            verdict_box.animate.set_stroke(width=2.6),
            ReplacementTransform(why, why_ok),
            run_time=0.5,
        )

        # ============================================================
        # B4 — NAME IT + POSTER HOLD.  (single #fff accent)
        # ============================================================
        self.next_section("name")

        # clear the working output so the payoff owns center-right cleanly.
        self.play(FadeOut(VGroup(outS, outZ, arrU, arrD, check, force_cap)),
                  run_time=0.34)

        punch = serif("pushed back apart", 44, WHITE).move_to(
            [PLANE_C[0] + 1.2, PLANE_C[1] - 1.55, 0])
        sub = mono("close to the voice AND decodable as real sounds", 16, INK_DIM)
        sub.next_to(punch, DOWN, buff=0.18)
        glow_punch = glow(punch)
        self.add(glow_punch)
        self.play(GrowFromCenter(punch), FadeIn(sub, shift=UP * 0.08), run_time=0.6)
        # the two crisp points give one last confirming pulse.
        self.play(Indicate(VGroup(pt1, pt2), scale_factor=1.15, color=INK),
                  run_time=0.45)
        self.wait(0.6)
