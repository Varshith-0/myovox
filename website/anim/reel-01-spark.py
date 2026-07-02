# REEL 1 — SPARK. "Every word begins as movement; a moving muscle leaks a pulse."
# One continuous face draws on; the lips mouth a SILENT word; each articulation
# ripples faint pulses across jaw, cheek, throat; the pulses condense into the 31
# sensor points that rest on the skin.
# CLOSES ON: face_front + 31 settled sensor points  (== scene 2 open).
from manim import *
from style import *
from reel_common import (WHITE, face_front, mouth_closed, mouth_open,
                         sensor_positions, motes, drift)
import numpy as np


class Spark(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- BEAT 1: the face draws on, one continuous line -------------
        self.next_section("draw")
        fc = face_front()
        mouth = mouth_closed()
        spark0 = Dot(ORIGIN, radius=0.05, color=WHITE)
        self.play(FadeIn(spark0, scale=2.0), run_time=0.4)
        self.play(Create(fc, run_time=1.5, rate_func=smooth),
                  spark0.animate.move_to([0, -0.28, 0]).set_opacity(0.0))
        self.remove(spark0)
        self.play(Create(mouth), run_time=0.4)
        self.wait(0.15)

        # ---- BEAT 2: silent articulation + pulses ripple ---------------
        self.next_section("mouth")
        # muscle sites the pulses radiate from (cheek, jaw, throat)
        sites = [[-0.95, 0.05, 0], [0.95, 0.05, 0],
                 [-0.75, -0.55, 0], [0.75, -0.55, 0], [0.0, -1.9, 0]]

        def ripple(site, rmax=0.55, rt=0.7):
            ring = Circle(radius=0.05, stroke_color=WHITE, stroke_width=2.4
                          ).move_to(site).set_opacity(0.9)
            self.add(ring)
            return ring, AnimationGroup(
                ring.animate.scale(rmax / 0.05).set_stroke(opacity=0.0),
                run_time=rt, rate_func=rate_functions.ease_out_sine)

        # two silent syllables, each opening the mouth and firing pulses
        for k in range(2):
            mo = mouth_open(h=0.30 + 0.08 * k)
            self.play(Transform(mouth, mo), run_time=0.28)
            rings = []
            anims = []
            for s in sites:
                r, a = ripple(s, rmax=0.5 + 0.12 * k)
                rings.append(r)
                anims.append(a)
            self.play(*anims, run_time=0.7)
            for r in rings:
                self.remove(r)
            self.play(Transform(mouth, mouth_closed()), run_time=0.24)

        # ---- BEAT 3: pulses condense into 31 resting sensors -----------
        self.next_section("settle")
        pos = sensor_positions(31)
        # seed each sensor from a random muscle site so they "condense" inward
        rng = np.random.RandomState(7)
        seeds = [sites[rng.randint(len(sites))] for _ in range(len(pos))]
        sensors = VGroup(*[Dot(seeds[i], radius=0.045, color=WHITE).set_opacity(0.0)
                           for i in range(len(pos))])
        self.add(sensors)
        self.play(
            LaggedStart(*[
                s.animate.move_to(pos[i]).set_opacity(0.55).set_color(INK)
                for i, s in enumerate(sensors)],
                lag_ratio=0.02),
            run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)
