# S28 — What it's for (silent speech, for a healthy speaker)
# Trained on ONE healthy subject — so this is a silent interface, a "silent
# keyboard", not a clinical device. You mouth the words with no sound; it types
# them. Honest framing: cross-subject is untested; no medical claim.
#
# ART DIRECTION — strict monochrome. A small flow (the talking head -> no sound -> text)
# across the top of the centre, four use-case cards beneath, an honesty note, and
# a closing line. The single pure-#fff accent is the typed TEXT payoff.
#   TOP strip   (y ~ +3.0): cap "WHAT IT'S FOR" + the framing line
#   CENTER      : the silent flow + four use-case cards + honesty note
#   BOTTOM strip(y ~ -3.2): "you mouth the words — it types them"
from manim import *
from emg_style import *
import os

WHITE = "#ffffff"
# The actual 3D talking head from the site's "Talking" stage (vignetted to fade
# into the black), used in place of a drawn mouth glyph.
HEAD_IMG = os.path.join(os.path.dirname(__file__), "head_face.png")


def speaker_glyph(c=INK):
    """A small speaker silhouette (trapezoid)."""
    return Polygon(
        [-0.22, -0.12, 0], [-0.06, -0.12, 0], [0.16, -0.30, 0],
        [0.16, 0.30, 0], [-0.06, 0.12, 0], [-0.22, 0.12, 0],
        stroke_color=c, stroke_width=2.0, fill_color=c, fill_opacity=0.08)


def text_glyph(c=INK):
    """Three short bars reading as typed text lines."""
    bars = VGroup(*[
        RoundedRectangle(width=w, height=0.085, corner_radius=0.04, stroke_width=0,
                         fill_color=c, fill_opacity=0.9)
        for w in (0.62, 0.50, 0.40)
    ]).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    return bars


def use_card(title, detail):
    box = RoundedRectangle(width=2.92, height=1.42, corner_radius=0.12,
                           stroke_color=INK_GHOST, stroke_width=1.6,
                           fill_color=INK, fill_opacity=0.03)
    t = mono(title, 15, INK, w=BOLD)
    d = mono(detail, 11, INK_FAINT)
    inner = VGroup(t, d).arrange(DOWN, buff=0.16)
    inner.move_to(box.get_center())
    return VGroup(box, inner)


class Silent(Scene):
    def construct(self):
        seed()

        self.next_section("cap")
        top1 = mono("WHAT IT'S FOR", 26, INK_DIM, w=BOLD).move_to([0, 3.16, 0])
        top2 = mono("trained on one healthy speaker — a silent interface, not a clinical tool",
                    16, INK_FAINT).move_to([0, 2.64, 0])
        rule = Line([-6.4, 2.32, 0], [6.4, 2.32, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.14), run_time=0.42)
        self.play(FadeIn(top2), Create(rule), run_time=0.32)

        # ============================================================== #
        #  THE SILENT FLOW — mouth -> no sound -> text                    #
        # ============================================================== #
        self.next_section("flow")
        FY = 1.30
        # the WHOLE 3D model (head + neck + shoulders), shown as-is and complete.
        # The image is centred on the FACE, and the face sits ON the arrow row at
        # x = -4.3 — so it lines up over its label and on the row like the other two
        # nodes; the body dissolves into black below.
        face = ImageMobject(HEAD_IMG).scale_to_fit_height(1.95).move_to([-4.3, 0.88, 0])
        face_lbl = mono("you mouth the words", 13, INK_FAINT).move_to([-4.3, 0.02, 0])

        spk = speaker_glyph(INK).move_to([0, FY, 0])
        slash = Line([-0.38, -0.36, 0], [0.38, 0.36, 0], stroke_color=WHITE,
                     stroke_width=3.0).move_to(spk.get_center())
        spk_lbl = mono("no sound leaves", 13, INK_FAINT).next_to(
            VGroup(spk, slash), DOWN, buff=0.20)

        txt = text_glyph(INK).move_to([4.3, FY, 0])
        txt_lbl = mono("it types them", 13, INK_FAINT).next_to(txt, DOWN, buff=0.22)

        def conn(a, b):
            s = Line(a.get_right() + RIGHT * 0.18, b.get_left() + LEFT * 0.18,
                     stroke_color=INK_FAINT, stroke_width=2.0)
            h = Triangle(stroke_width=0, fill_color=INK_FAINT, fill_opacity=1.0).scale(
                0.08).rotate(s.get_angle() - PI / 2).move_to(s.get_end())
            return VGroup(s, h)

        self.play(FadeIn(face, scale=1.04), FadeIn(face_lbl), run_time=0.5)
        # a subtle "speaking" breath so the model reads as alive / mouthing
        self.play(face.animate.scale(1.035), rate_func=there_and_back, run_time=0.7)
        # arrow from the model (at face/row height) to the muted speaker
        a1s = np.array([face.get_right()[0] + 0.18, FY, 0])
        a1l = Line(a1s, spk.get_left() + LEFT * 0.18, stroke_color=INK_FAINT, stroke_width=2.0)
        a1h = Triangle(stroke_width=0, fill_color=INK_FAINT, fill_opacity=1.0).scale(
            0.08).rotate(a1l.get_angle() - PI / 2).move_to(a1l.get_end())
        a1 = VGroup(a1l, a1h)
        self.play(Create(a1), run_time=0.3)
        # the muted speaker: draw it, then the white slash snaps across (the accent)
        self.play(DrawBorderThenFill(spk), run_time=0.4)
        self.play(Create(slash),
                  Flash(spk.get_center(), color=WHITE, line_length=0.12, num_lines=10,
                        flash_radius=0.5, time_width=0.4),
                  FadeIn(spk_lbl), run_time=0.42)
        a2 = conn(spk, txt)
        self.play(Create(a2), run_time=0.3)
        txt_g = glow(txt)
        self.add(txt_g)
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in txt],
                              lag_ratio=0.2), FadeIn(txt_lbl), run_time=0.45)

        # ============================================================== #
        #  USE-CASE CARDS                                                 #
        # ============================================================== #
        self.next_section("cards")
        cards_spec = [
            ("QUIET ROOM", "dictate without a sound"),
            ("PRIVATE", "no one can overhear"),
            ("NOISY PLACE", "the mic fails, you don't"),
            ("HANDS-FREE", "AR · VR · calls"),
        ]
        cards = VGroup(*[use_card(t, d) for t, d in cards_spec])
        cards.arrange(RIGHT, buff=0.20).move_to([0, -1.12, 0])
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.10) for m in cards],
                              lag_ratio=0.14), run_time=0.9)

        # ---- honesty note (quiet, dim — stated, not defended) ----------
        self.next_section("honesty")
        note = mono("one healthy speaker  ·  cross-subject is future work  ·  not a medical device",
                    14, INK_FAINT).move_to([0, -2.30, 0])
        self.play(FadeIn(note), run_time=0.4)

        # ---- BOTTOM line ----------------------------------------------
        closing = serif("you mouth the words — it types them", 24, INK).move_to([0, -3.08, 0])
        self.play(Write(closing), run_time=0.55)
        self.wait(0.6)


if __name__ == "__main__":
    pass
