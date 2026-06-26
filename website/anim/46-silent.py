# S28 — What it's for (silent speech, for a healthy speaker)
# Closing scene. You mouth the words with no sound; it types them. Four use-cases,
# then honest framing: trained on ONE healthy speaker — a silent keyboard, not a
# medical device; cross-subject is the road still ahead.
#
# ART DIRECTION — strict monochrome on #050505. ONE pure-#fff accent: the typed
# TEXT igniting at beat 3. Eight beats, one self.next_section per spoken sentence;
# at every beat exactly one element is lit and everything else sits dim.
#   TOP strip   (y ~ +3.0): cap "WHAT IT'S FOR" + framing line + rule
#   CENTER      : the silent flow (head -> muted speaker -> text) and four cards
#   BOTTOM strip(y ~ -2.3): honesty note, then a forward-looking closing serif
from manim import *
from style import *
import os

WHITE = "#ffffff"
HEAD_IMG = os.path.join(os.path.dirname(__file__), "head_face.png")


def speaker_glyph(c=INK):
    """A small speaker silhouette (trapezoid)."""
    return Polygon(
        [-0.22, -0.12, 0], [-0.06, -0.12, 0], [0.16, -0.30, 0],
        [0.16, 0.30, 0], [-0.06, 0.12, 0], [-0.22, 0.12, 0],
        stroke_color=c, stroke_width=2.0, fill_color=c, fill_opacity=0.08)


def text_glyph(c=INK):
    """Three short bars reading as typed text lines."""
    return VGroup(*[
        RoundedRectangle(width=w, height=0.085, corner_radius=0.04, stroke_width=0,
                         fill_color=c, fill_opacity=0.9)
        for w in (0.62, 0.50, 0.40)
    ]).arrange(DOWN, buff=0.10, aligned_edge=LEFT)


def use_card(title, detail):
    box = RoundedRectangle(width=2.92, height=1.42, corner_radius=0.12,
                           stroke_color=INK_GHOST, stroke_width=1.6,
                           fill_color=BG, fill_opacity=1.0)
    t = mono(title, 15, INK, w=BOLD)
    d = mono(detail, 11, INK_FAINT)
    inner = VGroup(t, d).arrange(DOWN, buff=0.16).move_to(box.get_center())
    return VGroup(box, inner)


def flat_arrow(start, end, c=INK_FAINT, w=2.0):
    shaft = Line(start, end, stroke_color=c, stroke_width=w)
    head = Triangle(stroke_width=0, fill_color=c, fill_opacity=1.0).scale(
        0.085).rotate(shaft.get_angle() - PI / 2).move_to(shaft.get_end())
    return VGroup(shaft, head)


class Silent(Scene):
    def construct(self):
        seed()

        # ============================================================== #
        #  BEAT 1 — "So what is all of this for?"            (1.10s)      #
        # ============================================================== #
        self.next_section("b1_cap")
        top1 = mono("WHAT IT'S FOR", 26, INK_DIM, w=BOLD).move_to([0, 3.16, 0])
        top2 = mono("you mouth the words — and it types them",
                    16, INK_FAINT).move_to([0, 2.64, 0])
        rule = Line([-6.4, 2.32, 0], [6.4, 2.32, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.14), run_time=0.45)
        self.play(FadeIn(top2), Create(rule), run_time=0.35)
        self.wait(0.30)

        # ============================================================== #
        #  BEAT 2 — "You mouth the words — no breath, no sound." (1.83s) #
        # ============================================================== #
        self.next_section("b2_head")
        FY = 0.95
        face = ImageMobject(HEAD_IMG).scale_to_fit_height(1.95).move_to([-4.3, 0.88, 0])
        face_lbl = mono("silent", 13, INK_FAINT).move_to([-4.3, 0.02, 0])
        self.play(FadeIn(face, scale=1.04), FadeIn(face_lbl), run_time=0.55)
        # one subtle silent-breath pulse
        self.play(face.animate.scale(1.035), rate_func=there_and_back, run_time=0.85)
        self.wait(0.40)

        # ============================================================== #
        #  BEAT 3 — "And it types them."   (0.70s)  THE WHITE ACCENT     #
        # ============================================================== #
        self.next_section("b3_types")
        spk = speaker_glyph(INK).move_to([0, FY, 0])
        slash = Line([-0.34, -0.32, 0], [0.34, 0.32, 0], stroke_color=INK,
                     stroke_width=2.6).move_to(spk.get_center())
        txt = text_glyph(INK).move_to([4.3, FY, 0])
        a1 = flat_arrow([face.get_right()[0] + 0.18, FY, 0], spk.get_left() + LEFT * 0.18)
        a2 = flat_arrow(spk.get_right() + RIGHT * 0.18, txt.get_left() + LEFT * 0.20)
        txt_g = glow(txt)
        self.add(spk, slash, a1, a2, txt_g)
        self.play(
            FadeIn(a1), FadeIn(spk), FadeIn(slash), FadeIn(a2),
            LaggedStart(*[FadeIn(m, shift=RIGHT * 0.08) for m in txt], lag_ratio=0.2),
            Flash([4.3, FY, 0], color=WHITE, line_length=0.16, num_lines=12,
                  flash_radius=0.7, time_width=0.4),
            run_time=0.70)

        flow = Group(face, face_lbl, spk, slash, a1, a2, txt_g)

        # ============================================================== #
        #  USE-CASE CARDS — revealed one at a time, beats 4-7            #
        # ============================================================== #
        cards_spec = [
            ("QUIET ROOM", "dictate without a sound"),
            ("PRIVATE", "no one can overhear"),
            ("NOISY PLACE", "the mic fails, you don't"),
            ("HANDS-FREE", "AR · VR · calls"),
        ]
        cards = VGroup(*[use_card(t, d) for t, d in cards_spec])
        cards.arrange(RIGHT, buff=0.20).move_to([0, -1.30, 0])

        def light_card(idx, rt):
            """Reveal card idx; dim the flow row + prior cards, spotlight this one."""
            anims = [FadeIn(cards[idx], shift=UP * 0.10)]
            if idx == 0:
                anims.append(flow.animate.set_opacity(0.30))
            for j in range(idx):
                anims.append(cards[j].animate.set_opacity(0.42))
            self.play(*anims, run_time=rt)

        # ---- BEAT 4 — "Dictate in a silent room."   (1.07s) ----------
        self.next_section("b4_quiet")
        light_card(0, 0.70)
        self.wait(0.37)

        # ---- BEAT 5 — "Say something private..."    (1.73s) ----------
        self.next_section("b5_private")
        light_card(1, 0.85)
        self.wait(0.88)

        # ---- BEAT 6 — "Get a message through..."    (2.08s) ----------
        self.next_section("b6_noisy")
        light_card(2, 0.90)
        self.wait(1.18)

        # ============================================================== #
        #  BEAT 7 — trained on one healthy speaker...  (3.21s)           #
        #  HANDS-FREE card co-reveals; honesty note "not a medical       #
        #  device"; cards held but dimmed under the note.                #
        # ============================================================== #
        self.next_section("b7_honesty")
        light_card(3, 0.85)
        note_a = mono("one healthy speaker", 14, INK_FAINT)
        note_b = mono("not a medical device", 14, INK_DIM)
        note = VGroup(note_a, mono("·", 14, INK_GHOST), note_b).arrange(
            RIGHT, buff=0.30).move_to([0, -2.42, 0])
        self.play(cards.animate.set_opacity(0.40), FadeIn(note_a), run_time=0.70)
        self.play(FadeIn(note[1]),
                  FadeIn(note_b),
                  Indicate(note_b, scale_factor=1.06, color=INK),
                  run_time=0.66)
        self.wait(1.00)

        # ============================================================== #
        #  BEAT 8 — "Making it work for many people..."  (1.84s)         #
        #  cross-subject brightens; closing serif resolves on the future #
        # ============================================================== #
        self.next_section("b8_road")
        cross = mono("cross-subject — not there yet", 14, INK)
        cross.move_to([0, -2.05, 0])
        # keep the "not a medical device" disclaimer persistent (dim) through the close
        self.play(FadeOut(note_a, shift=UP * 0.06), FadeOut(note[1]),
                  note_b.animate.set_opacity(0.55).move_to([0, -2.42, 0]),
                  FadeIn(cross, shift=UP * 0.06), run_time=0.45)
        closing = serif("the road still ahead", 26, INK).move_to([0, -3.18, 0])
        closing_g = glow(closing)
        self.add(closing_g)
        self.play(Write(closing), run_time=0.65)
        self.wait(0.74)


if __name__ == "__main__":
    pass
