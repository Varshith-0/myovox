# REEL 9 — SILENT. "What is it for? Silent speech. Mouth the words and they become
# text — in a crowd, in a meeting, anywhere a voice can't go."
# OPENS ON: the glowing stack expanding past the frame (== scene 8 close).
# A sweep reveals a triptych: a noisy cafe where a silent mouth types text; a
# private no-whisper dictation; a hands-free case. The panels compress to 3 lines.
# CLOSES ON: three lines of typed text drifting to centre  (== scene 10 open).
from manim import *
from style import *
from reel_common import WHITE, motes, drift, mouth_closed, mouth_open
import numpy as np


def panel(cx, title):
    box = RoundedRectangle(width=3.4, height=2.6, corner_radius=0.12,
                           stroke_color=INK_GHOST, stroke_width=1.4,
                           fill_color=BG, fill_opacity=1.0).move_to([cx, 0.3, 0])
    cap = mono(title, 17, INK_FAINT).next_to(box, DOWN, buff=0.2)
    return box, cap


class Silent(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: a wash of light from scene 8's glow -----------------
        self.next_section("open")
        wash = Circle(radius=0.4, stroke_width=0, fill_color=INK, fill_opacity=0.10
                      ).move_to([0, 0.4, 0])
        self.add(wash)
        self.play(wash.animate.scale(30).set_opacity(0.0), run_time=0.7,
                  rate_func=rate_functions.ease_out_sine)
        self.remove(wash)

        q = mono("what is it for?", 24, INK_FAINT).to_edge(UP, buff=0.5)
        self.play(FadeIn(q, shift=DOWN * 0.1), run_time=0.4)

        # ---- BEAT 1: three use-cases sweep in --------------------------
        self.next_section("triptych")
        cxs = [-3.8, 0.0, 3.8]
        titles = ["a loud cafe", "in private", "hands-free"]
        panels = []
        caps = VGroup()
        for cx, t in zip(cxs, titles):
            b, c = panel(cx, t)
            panels.append(b)
            caps.add(c)

        # panel 1: noise scribbles + a silent mouth -> text
        noise = VGroup(*[trace_line(cxs[0], k) for k in range(4)])
        mouth = mouth_closed().scale(0.9).move_to([cxs[0], 0.55, 0])
        typed1 = mono("\"meet me at eight\"", 15, INK).move_to([cxs[0], -0.5, 0])
        # panel 2: a struck-through speaker + text
        spk = speaker_glyph([cxs[1] - 0.7, 0.6, 0])
        spk_slash = Line([cxs[1] - 1.0, 0.35, 0], [cxs[1] - 0.4, 0.85, 0]).set_stroke(WHITE, 2.4)
        typed2 = mono("\"send the file\"", 15, INK).move_to([cxs[1], -0.5, 0])
        # panel 3: hands busy + text appears
        hands = mono("[ hands busy ]", 15, INK_FAINT).move_to([cxs[2], 0.6, 0])
        typed3 = mono("\"call me back\"", 15, INK).move_to([cxs[2], -0.5, 0])

        self.play(LaggedStart(Create(panels[0]), Create(panels[1]), Create(panels[2]),
                              lag_ratio=0.15),
                  LaggedStart(*[FadeIn(c) for c in caps], lag_ratio=0.15),
                  run_time=1.0)
        self.play(FadeIn(VGroup(*noise)), FadeIn(mouth), run_time=0.4)
        # silent articulation in panel 1
        self.play(Transform(mouth, mouth_open(0.28).scale(0.9).move_to([cxs[0], 0.55, 0])),
                  run_time=0.22)
        self.play(Transform(mouth, mouth_closed().scale(0.9).move_to([cxs[0], 0.55, 0])),
                  FadeIn(typed1, shift=UP * 0.06), run_time=0.3)
        self.play(FadeIn(spk), Create(spk_slash), FadeIn(typed2, shift=UP * 0.06),
                  run_time=0.5)
        self.play(FadeIn(hands), FadeIn(typed3, shift=UP * 0.06), run_time=0.5)
        self.wait(0.2)

        # ---- BEAT 2: compress to three lines of text -------------------
        self.next_section("compress")
        lines = VGroup(typed1.copy(), typed2.copy(), typed3.copy())
        target = VGroup(
            mono("\"meet me at eight\"", 22, INK),
            mono("\"send the file\"", 22, INK_DIM),
            mono("\"call me back\"", 22, INK_FAINT),
        ).arrange(DOWN, buff=0.4).move_to([0, 0.1, 0])
        everything = VGroup(*panels, caps, *noise, mouth, spk, spk_slash,
                            hands, typed1, typed2, typed3, q)
        self.play(FadeOut(everything), run_time=0.5)
        self.add(lines)
        self.play(Transform(lines[0], target[0]),
                  Transform(lines[1], target[1]),
                  Transform(lines[2], target[2]),
                  run_time=0.8, rate_func=smooth)
        self.play(lines.animate.move_to(ORIGIN), run_time=0.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)


def trace_line(cx, k=0):
    xs = np.linspace(cx - 1.3, cx + 1.3, 40)
    ph = np.random.RandomState(50 + k).uniform(0, 6)
    ys = 1.05 - 0.28 * k + 0.10 * np.sin(np.linspace(0, 8, 40) + ph)
    pts = [[xs[i], ys[i], 0] for i in range(40)]
    return VMobject().set_points_smoothly(pts).set_stroke(INK_GHOST, 1.0, opacity=0.4)


def speaker_glyph(at):
    cone = Polygon([-0.16, -0.14, 0], [-0.16, 0.14, 0], [0.04, 0.3, 0], [0.04, -0.3, 0],
                   color=INK, fill_opacity=0.9, stroke_width=0)
    a1 = Arc(0.18, -PI / 3, 2 * PI / 3, arc_center=[0.1, 0, 0]).set_stroke(INK, 2)
    return VGroup(cone, a1).move_to(at)
