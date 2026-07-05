# I4 — Roadmap. The whole journey as a timeline, lit in three groups.
# Beats (one per narration sentence):
#   1 TRACK    the empty journey line + all 7 stops + a start dot.
#   2 BODY     dot travels, lighting body -> signal -> fingerprint.
#   3 READER   reader -> sounds -> words light up.
#   4 CHOOSE   sentence lights, a score badge lands, "~50 scenes" caption.
from manim import *
from style import *
import numpy as np

STOPS = ["body", "signal", "fingerprint", "reader", "sounds", "words", "sentence"]
XS = np.linspace(-5.7, 5.7, 7)
YL = 0.5  # the track height


class Roadmap(Scene):
    def construct(self):
        seed()

        title = mono("the whole journey, before we begin", 26, INK_FAINT).to_edge(UP, buff=0.6)
        track = Line([XS[0], YL, 0], [XS[-1], YL, 0], stroke_color=INK_GHOST, stroke_width=2)

        nodes = VGroup(*[Circle(radius=0.14, stroke_color=INK_GHOST, stroke_width=2)
                         .set_fill(BG, 1).move_to([x, YL, 0]) for x in XS])
        # Alternate labels above/below the track so long names never collide.
        labels = VGroup()
        stems = VGroup()
        for i, (s, x) in enumerate(zip(STOPS, XS)):
            ly = YL + 0.85 if i % 2 == 0 else YL - 0.85
            lab = mono(s, 19, INK_FAINT).move_to([x, ly, 0])
            stem = Line([x, YL, 0], [x, ly + (-0.22 if i % 2 == 0 else 0.22), 0],
                        stroke_color=INK_GHOST, stroke_width=1)
            labels.add(lab)
            stems.add(stem)

        dot = Dot(radius=0.12, color="#ffffff").move_to([XS[0], YL, 0])

        def light(i):
            return AnimationGroup(
                nodes[i].animate.set_fill("#ffffff", 1).set_stroke("#ffffff", 2.5),
                labels[i].animate.set_color(INK),
                stems[i].animate.set_stroke(INK_FAINT, 1.2),
            )

        def travel(to_idx, group, rt):
            self.play(dot.animate.move_to([XS[to_idx], YL, 0]),
                      LaggedStart(*[light(i) for i in group], lag_ratio=0.5),
                      run_time=rt, rate_func=linear)

        # ---- BEAT 1: TRACK ----------------------------------------------
        self.next_section("track")
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.5)
        self.play(Create(track), LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.06),
                  LaggedStart(*[FadeIn(s) for s in stems], lag_ratio=0.06),
                  LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.06), run_time=1.2)
        self.play(FadeIn(dot, scale=1.5), run_time=0.3)
        self.wait(0.3)

        # ---- BEAT 2: BODY -> SIGNAL -> FINGERPRINT ----------------------
        self.next_section("body")
        travel(2, [0, 1, 2], 1.5)
        self.wait(0.2)

        # ---- BEAT 3: READER -> SOUNDS -> WORDS --------------------------
        self.next_section("reader")
        travel(5, [3, 4, 5], 1.6)
        self.wait(0.2)

        # ---- BEAT 4: CHOOSE + SCORE -------------------------------------
        self.next_section("choose")
        travel(6, [6], 0.7)
        btxt = mono("18.5% word error", 22, INK)
        bbox = RoundedRectangle(width=btxt.width + 0.7, height=0.9, corner_radius=0.1)
        bbox.set_stroke("#ffffff", 1.8).set_fill(INK, 0.05)
        btxt.move_to(bbox.get_center())
        badge = VGroup(bbox, btxt).move_to([3.7, YL - 1.85, 0])
        self.play(FadeIn(badge, shift=UP * 0.1),
                  Flash(nodes[6].get_center(), color="#ffffff", num_lines=12, flash_radius=0.5),
                  run_time=0.6)
        cap = mono("≈ 50 short scenes — one idea each", 26, INK).move_to([0, -3.2, 0])
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=0.6)
        self.wait(0.6)
