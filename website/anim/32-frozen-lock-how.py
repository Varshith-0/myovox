# website/anim/b15_frozen_lock_how.py  —  B15 "A judge that cannot be bought"
#
# HOOK carried straight out of B14 (the lazy shortcut): "be close" distillation
# collapses two distinct sounds into ONE grey smudge that still scores well.
# THE FIX, discovered beat by beat:
#   1 POSE     the carried-forward smudge — the cheat that still scores well.
#   2 READER   draw an empty SOUND-READER that grades ONE question, not closeness.
#   3 LOCK     bolt it on and FREEZE it — the student can't soften its answer.
#   4 REJECT   feed it the blur -> it stalls, can't name a sound -> REJECTED.
#   5 SPLIT    the only way to pass: pull the blur into two crisp points S, Z.
#   6 ACCEPT   the reader names them -> ACCEPTED; #fff payoff "close AND decodable".
#
# Locked 6-beat sheet (one self.next_section per beat, timed to dur_sec):
#   b1 1.45  b2 2.79  b3 2.53  b4 1.68  b5 1.62  b6 1.92   (~12.0s)
#
# STRICT MONOCHROME on #050505. Emphasis = opacity / stroke / scale / glow only.
# Reject/accept encoded by stroke width + opacity, never colour.  The single pure
# #fff accent is reserved for the final "close to the voice AND decodable" payoff.
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

TOP_Y = 3.30
PLANE_C = np.array([-2.70, 0.10, 0])     # centre of the feature-plane (left)
READER_C = np.array([3.95, 0.10, 0])     # centre of the sound-reader (right)
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
        # BEAT 1 (~1.45s) — POSE the cheat: carry B14's smudge forward.
        #   recap line implies the open question "how do you catch it?";
        #   the spec/sub line stays INK_FAINT so it doesn't compete.
        # ============================================================
        self.next_section("pose")

        top1 = mono('"be close" let the blur score well — how do you catch it?',
                    19, INK_DIM).move_to([0, TOP_Y, 0])
        top2 = mono("add a judge that grades a different thing entirely",
                    14, INK_FAINT).move_to([0, TOP_Y - 0.44, 0])
        rule = Line([-6.4, TOP_Y - 0.72, 0], [6.4, TOP_Y - 0.72, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.3)

        plane = Rectangle(width=4.7, height=3.5, stroke_color=INK_GHOST,
                          stroke_width=1.2, fill_opacity=0).move_to(PLANE_C)
        plane_lbl = mono("the student's copied features", 13, INK_GHOST)
        plane_lbl.move_to(plane.get_top() + DOWN * 0.22).align_to(plane, LEFT)
        plane_lbl.shift(RIGHT * 0.18)
        self.play(Create(plane), FadeIn(plane_lbl), run_time=0.36)

        smudge_c = PLANE_C + np.array([0.0, 0.05, 0])
        smudge = smudge_blob(smudge_c)
        s_lbl = mono("one mushy point", 14, INK_FAINT).next_to(smudge, DOWN, buff=0.40)
        self.play(FadeIn(smudge), FadeIn(s_lbl), run_time=0.34)
        # one soft pulse: it still "scores well" on plain closeness.
        self.play(Indicate(smudge, scale_factor=1.12, color=INK), run_time=0.33)

        # ============================================================
        # BEAT 2 (~2.79s) — DRAW the reader: a judge that asks ONE question
        #   (can two distinct sounds be read out?), NOT closeness.  No lock yet.
        # ============================================================
        self.next_section("reader")

        reader = RoundedRectangle(corner_radius=0.14, width=2.7, height=2.4,
                                  stroke_color=INK, stroke_width=2.2,
                                  fill_color=BG, fill_opacity=1).move_to(READER_C)
        reader_lbl = mono("SOUND\nREADER", 20, INK).move_to(
            reader.get_center() + UP * 0.45)

        feed = Line(plane.get_right() + RIGHT * 0.05, reader.get_left(),
                    stroke_color=INK_DIM, stroke_width=2.0)
        feed_head = Triangle(stroke_width=0, fill_color=INK_DIM, fill_opacity=1.0)
        feed_head.scale(0.07).rotate(-PI / 2).move_to(reader.get_left())

        # spotlight the reader: dim the plane + smudge while the judge is named.
        # NOTE: set_opacity on a stroke-only Rect would fill it grey -> dim stroke only.
        self.play(plane.animate.set_stroke(opacity=0.4),
                  VGroup(plane_lbl, smudge, s_lbl).animate.set_opacity(0.4),
                  Create(reader), FadeIn(reader_lbl), run_time=0.7)
        self.play(Create(feed), FadeIn(feed_head), run_time=0.45)

        ask = mono("its one question:", 13, INK_FAINT).move_to(
            reader.get_center() + DOWN * 0.20)
        ask2 = mono("can two distinct\nsounds be read out?", 14, INK_DIM).move_to(
            reader.get_center() + DOWN * 0.62)
        self.play(FadeIn(ask), run_time=0.4)
        self.play(FadeIn(ask2, shift=UP * 0.06), run_time=0.55)
        self.wait(0.4)

        # ============================================================
        # BEAT 3 (~2.53s) — LOCK it: drop the padlock, freeze the dials.
        # ============================================================
        self.next_section("lock")

        # clear the question text so the lock owns the reader cleanly.
        self.play(FadeOut(VGroup(ask, ask2)), run_time=0.34)
        lock = padlock(INK, sw=2.6).move_to(reader.get_center() + DOWN * 0.32)
        lock_tag = mono("FROZEN · dials locked", 13, INK).next_to(
            lock, DOWN, buff=0.18)
        self.play(FadeIn(lock, scale=0.6, shift=DOWN * 0.3), run_time=0.5)
        # the lock clicks: a quiet flash, no colour.
        self.play(Flash(lock[2].get_center(), color=INK, line_length=0.14,
                        num_lines=10, flash_radius=0.36), run_time=0.45)
        self.play(FadeIn(lock_tag, shift=UP * 0.06), run_time=0.4)
        why_lock = mono("the student can't soften it or bend its answer",
                        14, INK_FAINT).move_to([0, BOT_Y + 0.05, 0])
        self.play(FadeIn(why_lock), run_time=0.4)
        self.wait(0.4)

        # ============================================================
        # BEAT 4 (~1.68s) — REJECT: feed the blur in, it stalls -> REJECTED.
        #   spotlight reader + verdict; dim the plane/smudge origin.
        # ============================================================
        self.next_section("reject")

        self.play(FadeOut(why_lock),
                  plane.animate.set_stroke(opacity=0.22),
                  plane_lbl.animate.set_opacity(0.22), run_time=0.3)

        carrier = smudge_blob(smudge_c, op_scale=0.9)
        self.add(carrier)
        self.play(carrier.animate.move_to(reader.get_center() + UP * 0.05),
                  run_time=0.45, rate_func=rate_functions.ease_in_sine)
        self.remove(carrier)

        out_anchor = reader.get_right() + RIGHT * 0.05
        garble = mono("? ?", 30, INK_FAINT).move_to(out_anchor + RIGHT * 0.62)
        out_arrow = Line(out_anchor, garble.get_left() + LEFT * 0.12,
                         stroke_color=INK_GHOST, stroke_width=1.8)
        amb_lbl = mono("can't tell\nwhich sound", 12, INK_FAINT).next_to(
            garble, DOWN, buff=0.16)
        cross = Cross(garble, stroke_color=INK, stroke_width=4.0).scale(0.9)
        self.play(Create(out_arrow), FadeIn(garble), FadeIn(amb_lbl), run_time=0.4)
        self.play(Create(cross), run_time=0.25)

        verdict_box = RoundedRectangle(corner_radius=0.08, width=3.4, height=0.6,
                                       stroke_color=INK, stroke_width=1.6,
                                       fill_opacity=0).move_to([0, BOT_Y + 0.1, 0])
        verdict = mono("REJECTED", 22, INK_DIM).move_to(verdict_box)
        self.play(Create(verdict_box), FadeIn(verdict), run_time=0.3)
        for w in (3.4, 1.6):
            self.play(verdict_box.animate.set_stroke(width=w), run_time=0.09,
                      rate_func=linear)

        # ============================================================
        # BEAT 5 (~1.62s) — SPLIT: pull the blur into two crisp points S, Z.
        #   spotlight the plane; dim the reader.  (force_cap CUT.)
        # ============================================================
        self.next_section("split")

        self.play(FadeOut(VGroup(garble, cross, out_arrow, amb_lbl)),
                  FadeOut(s_lbl),
                  VGroup(reader, reader_lbl, lock, lock_tag).animate.set_opacity(0.3),
                  plane.animate.set_stroke(opacity=0.55),
                  plane_lbl.animate.set_opacity(0.55),
                  smudge.animate.set_opacity(1.0),
                  run_time=0.34)

        p_left = smudge_c + np.array([-1.15, 0.0, 0])
        p_right = smudge_c + np.array([1.15, 0.0, 0])
        force_l = Line(smudge_c + LEFT * 0.2, p_left + RIGHT * 0.2,
                       stroke_color=INK_DIM, stroke_width=2.4)
        force_r = Line(smudge_c + RIGHT * 0.2, p_right + LEFT * 0.2,
                       stroke_color=INK_DIM, stroke_width=2.4)
        head_l = Triangle(stroke_width=0, fill_color=INK_DIM, fill_opacity=1.0)
        head_l.scale(0.07).rotate(PI / 2).move_to(p_left + RIGHT * 0.18)
        head_r = Triangle(stroke_width=0, fill_color=INK_DIM, fill_opacity=1.0)
        head_r.scale(0.07).rotate(-PI / 2).move_to(p_right + LEFT * 0.18)
        self.play(GrowFromCenter(force_l), GrowFromCenter(force_r),
                  FadeIn(head_l), FadeIn(head_r), run_time=0.4)

        pt1_grp, pt1 = crisp_point(p_left, "S")
        pt2_grp, pt2 = crisp_point(p_right, "Z")
        self.play(
            FadeOut(smudge),
            TransformFromCopy(smudge, pt1_grp),
            TransformFromCopy(smudge, pt2_grp),
            run_time=0.6,
        )
        self.play(FadeOut(VGroup(force_l, force_r, head_l, head_r)), run_time=0.25)
        self.wait(0.1)

        # ============================================================
        # BEAT 6 (~1.92s) — ACCEPT + NAME: the reader reads them cleanly,
        #   verdict flips to ACCEPTED, single #fff payoff.
        # ============================================================
        self.next_section("accept")

        # re-light the reader; carry the two crisp points into it.
        self.play(VGroup(reader, reader_lbl, lock, lock_tag).animate.set_opacity(1.0),
                  run_time=0.25)
        c1 = pt1.copy()
        c2 = pt2.copy()
        self.add(c1, c2)
        self.play(c1.animate.move_to(reader.get_center() + UP * 0.05),
                  c2.animate.move_to(reader.get_center() + UP * 0.05),
                  run_time=0.4, rate_func=rate_functions.ease_in_sine)
        self.remove(c1, c2)

        outS = serif("S", 32, INK).move_to(out_anchor + RIGHT * 0.62 + UP * 0.5)
        outZ = serif("Z", 32, INK).move_to(out_anchor + RIGHT * 0.62 + DOWN * 0.5)
        arrU = Line(out_anchor + UP * 0.22, outS.get_left() + LEFT * 0.12,
                    stroke_color=INK_DIM, stroke_width=2.0)
        arrD = Line(out_anchor + DOWN * 0.22, outZ.get_left() + LEFT * 0.12,
                    stroke_color=INK_DIM, stroke_width=2.0)
        check = mono("✓", 24, INK).next_to(VGroup(outS, outZ), RIGHT, buff=0.2)
        self.play(Create(arrU), Create(arrD), FadeIn(outS), FadeIn(outZ),
                  run_time=0.4)

        verdict_ok = mono("ACCEPTED", 22, INK).move_to(verdict_box)
        self.play(
            FadeOut(verdict, scale=0.9), FadeIn(verdict_ok, scale=1.05),
            verdict_box.animate.set_stroke(width=2.6),
            FadeIn(check, scale=0.6),
            run_time=0.4,
        )

        # dim the reader output so the #fff payoff + two crisp points own focus.
        self.play(VGroup(reader, reader_lbl, lock, lock_tag, feed, feed_head,
                         outS, outZ, arrU, arrD, check).animate.set_opacity(0.32),
                  run_time=0.25)
        punch = serif("close to the voice", 36, WHITE).move_to(
            [PLANE_C[0] + 0.95, PLANE_C[1] - 1.5, 0])
        sub = serif("AND decodable", 36, WHITE).next_to(punch, DOWN, buff=0.1)
        glow_punch = glow(VGroup(punch, sub))
        self.add(glow_punch)
        self.play(GrowFromCenter(punch), GrowFromCenter(sub), run_time=0.42)
        self.play(Indicate(VGroup(pt1, pt2), scale_factor=1.18, color=INK),
                  run_time=0.38)
        self.wait(0.45)
