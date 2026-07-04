# REEL 9 — SILENT. "What is it for? Silent speech. Mouth the words and they become
# text — in a crowd, in a meeting, anywhere a voice can't go."
# OPENS ON: a wash of light from scene 8's glowing stack.
# Lead with the HERO mechanic: a face silently mouths a phrase (sound struck out)
# and the words type themselves out. Then the three use-cases stack as clean lines,
# each with its context — no cluttered boxes.
# CLOSES ON: three quoted lines at ORIGIN  (== scene 10 open, exact colours/sizes).
from manim import *
from style import *
from reel_common import WHITE, motes, drift

FACE_C = [0.0, 1.05, 0]


def make_face():
    head = Ellipse(width=2.0, height=2.6).set_stroke(INK, 2.0).move_to(FACE_C)
    eye_l = Arc(0.13, PI, PI, arc_center=[FACE_C[0] - 0.34, FACE_C[1] + 0.5, 0]).set_stroke(INK_DIM, 2)
    eye_r = Arc(0.13, PI, PI, arc_center=[FACE_C[0] + 0.34, FACE_C[1] + 0.5, 0]).set_stroke(INK_DIM, 2)
    nose = VMobject().set_points_as_corners(
        [[FACE_C[0], FACE_C[1] + 0.22, 0], [FACE_C[0] - 0.08, FACE_C[1] - 0.12, 0],
         [FACE_C[0] + 0.06, FACE_C[1] - 0.12, 0]]).set_stroke(INK_DIM, 2)
    return VGroup(head, eye_l, eye_r, nose)


MOUTH_Y = FACE_C[1] - 0.48


def mouth_closed_at():
    return Line([FACE_C[0] - 0.28, MOUTH_Y, 0], [FACE_C[0] + 0.28, MOUTH_Y, 0]).set_stroke(INK, 2.4)


def mouth_open_at(h):
    return Ellipse(width=0.42, height=h).set_stroke(INK, 2.4).set_fill(BG, 1.0).move_to([FACE_C[0], MOUTH_Y, 0])


def speaker_muted(at):
    cone = Polygon([-0.14, -0.12, 0], [-0.14, 0.12, 0], [0.04, 0.28, 0], [0.04, -0.28, 0],
                   color=INK_DIM, fill_opacity=0.9, stroke_width=0)
    a1 = Arc(0.16, -PI / 3, 2 * PI / 3, arc_center=[0.1, 0, 0]).set_stroke(INK_DIM, 2)
    grp = VGroup(cone, a1).move_to(at)
    slash = Line(at + LEFT * 0.28 + DOWN * 0.28, at + RIGHT * 0.28 + UP * 0.28).set_stroke(WHITE, 2.6)
    return grp, slash


# small context glyphs, left of each use-case line
def noise_glyph(at):
    xs = [-0.14, -0.05, 0.04, 0.13]
    hs = [0.07, 0.16, 0.1, 0.14]
    return VGroup(*[Line([x, -h, 0], [x, h, 0]) for x, h in zip(xs, hs)]
                  ).set_stroke(INK_FAINT, 2).move_to(at)


def lock_glyph(at):
    body = RoundedRectangle(width=0.24, height=0.18, corner_radius=0.03).set_stroke(INK_FAINT, 1.8)
    shackle = Arc(0.085, 0, PI).set_stroke(INK_FAINT, 1.8).move_to(body.get_top() + UP * 0.06)
    return VGroup(body, shackle).move_to(at)


def hands_glyph(at):
    grp, slash = speaker_muted([0, 0, 0])
    return VGroup(grp, slash).scale(0.7).move_to(at)


class Silent(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: a wash of light from scene 8's glow -----------------
        self.next_section("open")
        wash = Circle(radius=0.4, stroke_width=0, fill_color=INK, fill_opacity=0.1).move_to([0, 0.4, 0])
        self.add(wash)
        self.play(wash.animate.scale(30).set_opacity(0.0), run_time=0.7,
                  rate_func=rate_functions.ease_out_sine)
        self.remove(wash)
        title = mono("silent speech", 26, INK_FAINT).to_edge(UP, buff=0.5)
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.4)

        # ---- BEAT 1: the mechanic — mouth silently, words type out -----
        self.next_section("mechanic")
        face = make_face()
        mouth = mouth_closed_at()
        spk, slash = speaker_muted([FACE_C[0] + 1.65, FACE_C[1] + 0.25, 0])
        self.play(Create(face), Create(mouth), run_time=0.8)
        self.play(FadeIn(spk), Create(slash), run_time=0.4)

        typed = mono('"meet me at eight"', 26, INK).move_to([0, -1.35, 0])
        # a few silent articulations, then the words type out
        for h in (0.34, 0.18, 0.36, 0.2):
            self.play(Transform(mouth, mouth_open_at(h)), run_time=0.12)
        self.play(Transform(mouth, mouth_closed_at()),
                  AddTextLetterByLetter(typed), run_time=1.0)
        cap = mono("mouth the words — they become text", 18, INK_FAINT).move_to([0, -2.5, 0])
        self.play(FadeIn(cap, shift=UP * 0.08), run_time=0.4)
        self.wait(0.2)

        # ---- BEAT 2: the use-cases — where a voice can't go ------------
        self.next_section("contexts")
        USES = [('"meet me at eight"', "in a loud cafe", noise_glyph),
                ('"send the file"', "in a private meeting", lock_glyph),
                ('"call me back"', "hands full", hands_glyph)]
        rows = VGroup()
        for quote, ctx, _ in USES:
            q = mono(quote, 24, INK)
            t = mono("·  " + ctx, 16, INK_FAINT)
            rows.add(VGroup(q, t).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to([0.4, 0, 0])
        glyphs = VGroup(*[g(rows[i].get_left() + LEFT * 0.45).set_opacity(0)
                          for i, (_, _, g) in enumerate(USES)])

        # the hero phrase becomes the first use-case; face/speaker retire
        self.play(FadeOut(VGroup(face, mouth, spk, slash, cap)),
                  Transform(typed, rows[0][0]), run_time=0.55)
        self.remove(typed)
        self.add(rows[0][0])
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.06),
                  glyphs[0].animate.set_opacity(1.0), run_time=0.4)
        for i in (1, 2):
            self.play(FadeIn(rows[i], shift=UP * 0.06),
                      glyphs[i].animate.set_opacity(1.0), run_time=0.4)
        self.wait(0.3)

        # ---- BEAT 3: converge to the three quoted lines (== scene 10) --
        self.next_section("converge")
        final = VGroup(
            mono('"meet me at eight"', 22, INK),
            mono('"send the file"', 22, INK_DIM),
            mono('"call me back"', 22, INK_FAINT),
        ).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        quotes = [rows[0][0], rows[1][0], rows[2][0]]
        tags = VGroup(rows[0][1], rows[1][1], rows[2][1], glyphs, title)
        self.play(FadeOut(tags),
                  *[Transform(quotes[i], final[i]) for i in range(3)],
                  run_time=0.8, rate_func=smooth)
        self.wait(0.4)
