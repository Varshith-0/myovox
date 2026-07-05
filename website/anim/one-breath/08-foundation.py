# ONE BREATH 8 — FOUNDATION. "None of this starts from zero. A lab at UC Davis built the
# sensors, the data, and the whole approach. I built upward from their foundation,
# using proven ideas from across the field — composition, not invention."
# OPENS ON: the small dim block sinking (== scene 7 close).
# It lands as a "this pipeline" block on two large foundation stones; a UC Davis
# nameplate etches in; borrowed-method tags orbit and tether briefly.
# CLOSES ON: the full glowing stack  (== scene 9 open).
from manim import *
from style import *
from one_breath_common import WHITE, motes, drift
import numpy as np

TAGS = ["Conformer", "WavLM", "HuBERT", "CTC", "k2 / icefall", "Qwen2.5", "QLoRA"]


class Foundation(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the sinking block (matched from scene 7) ------------
        self.next_section("open")
        block = mono("18.5", 30, INK_FAINT).move_to([0, -1.4, 0]).set_opacity(0.5)
        self.add(block)
        self.wait(0.1)

        # the block becomes the "this pipeline" tile
        self.next_section("pipeline-block")
        tile = RoundedRectangle(width=2.4, height=0.7, corner_radius=0.08,
                                stroke_color=INK, stroke_width=2.0,
                                fill_color=BG, fill_opacity=1.0).move_to([0, 0.55, 0])
        tlab = mono("this pipeline", 20, INK).move_to(tile.get_center())
        pipe = VGroup(tile, tlab)
        self.play(Transform(block, pipe.copy()), run_time=0.7, rate_func=smooth)
        self.remove(block)
        self.add(pipe)

        # ---- BEAT 1: two big foundation stones fade in beneath ---------
        self.next_section("stones")
        stone1 = RoundedRectangle(width=5.4, height=0.85, corner_radius=0.08,
                                  stroke_color=INK_DIM, stroke_width=2.0,
                                  fill_color=BG, fill_opacity=1.0).move_to([0, -0.5, 0])
        s1lab = mono("the corpus  ·  31-channel sEMG", 20, INK_DIM).move_to(stone1.get_center())
        stone2 = RoundedRectangle(width=6.6, height=0.85, corner_radius=0.08,
                                  stroke_color=INK_DIM, stroke_width=2.0,
                                  fill_color=BG, fill_opacity=1.0).move_to([0, -1.5, 0])
        s2lab = mono("the approach  ·  EMG → text decoding", 20, INK_DIM).move_to(stone2.get_center())
        self.play(FadeIn(VGroup(stone1, s1lab), shift=UP * 0.15),
                  FadeIn(VGroup(stone2, s2lab), shift=UP * 0.15),
                  pipe.animate.move_to([0, 0.55, 0]),
                  run_time=0.9, rate_func=smooth)

        # ---- BEAT 2: the UC Davis nameplate etches in ------------------
        self.next_section("nameplate")
        plate = VGroup(
            mono("UC Davis", 26, INK),
            mono("Gowda · McNaughton · Comstock · Miller", 16, INK_FAINT),
        ).arrange(DOWN, buff=0.12).move_to([0, -2.65, 0])
        underline = Line([-2.4, -2.98, 0], [2.4, -2.98, 0]).set_stroke(INK_GHOST, 1.2)
        self.play(Write(plate[0]), FadeIn(plate[1], shift=UP * 0.06),
                  Create(underline), run_time=0.9)

        # ---- BEAT 3: borrowed methods orbit and tether ----------------
        self.next_section("borrowed")
        rng = np.random.RandomState(6)
        tags = VGroup()
        anchors = []
        for i, name in enumerate(TAGS):
            ang = i / len(TAGS) * TAU
            r = 3.5
            p = [r * np.cos(ang) * 1.35, 0.55 + r * np.sin(ang) * 0.55, 0]
            anchors.append(p)
            t = mono(name, 15, INK_FAINT).move_to(p).set_opacity(0.0)
            tags.add(t)
        self.play(LaggedStart(*[FadeIn(t, scale=1.1) for t in tags], lag_ratio=0.06),
                  run_time=0.9)
        # a hairline tether flicks from each tag to the pipeline block, then releases
        tethers = VGroup(*[Line(anchors[i], pipe.get_center(), stroke_color=INK_GHOST,
                                stroke_width=0.8).set_opacity(0.0) for i in range(len(TAGS))])
        self.add(tethers)
        self.play(LaggedStart(*[t.animate.set_opacity(0.4) for t in tethers],
                              lag_ratio=0.05), run_time=0.6)
        note = mono("composition, not invention", 22, INK).move_to([0, 1.7, 0])
        self.play(FadeIn(note, shift=DOWN * 0.1),
                  tethers.animate.set_opacity(0.15), run_time=0.6)
        # gentle glow-breath on the box outlines (animate each individually so the
        # opaque fills never re-order above their labels), then restore label z-order.
        boxes = [tile, stone1, stone2]
        self.play(*[b.animate.set_stroke(WHITE, 2.2) for b in boxes], run_time=0.5)
        self.play(*[b.animate.set_stroke(INK, 2.0) for b in boxes], run_time=0.5)
        self.add(s1lab, s2lab, tlab)  # keep the labels above the box fills
        self.wait(0.3)
