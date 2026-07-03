# REEL 1 — SPARK. "Every word begins as movement; a moving muscle leaks a pulse."
# The head draws on; the lips mouth a SILENT word; each articulation FLASHES the
# muscle sites white (monochrome — no fill discs); then the 31-sensor array (the
# hand-placed grid from 06-signal.py) grows onto the skin.
# CLOSES ON: head + face + 31 grid sensors  (== scene 2 open).
from manim import *
from style import *
from reel_common import (WHITE, head_outline, face_features, mouth_closed,
                         mouth_open, MUSCLE_SITES, sensor_array, motes, drift)


class Spark(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- BEAT 1: the head draws on --------------------------------
        self.next_section("draw")
        head = head_outline(INK, 2.2)
        feats = face_features()
        mouth = mouth_closed()
        spark0 = Dot([0, 0.6, 0], radius=0.05, color=WHITE)
        self.play(FadeIn(spark0, scale=2.0), run_time=0.4)
        self.play(Create(head, run_time=1.4, rate_func=smooth),
                  spark0.animate.move_to([0, -0.25, 0]).set_opacity(0.0))
        self.remove(spark0)
        self.play(Create(feats), Create(mouth), run_time=0.6)
        self.wait(0.1)

        # ---- BEAT 2: silent articulation, muscle sites flash white -----
        self.next_section("mouth")
        for k in range(2):
            self.play(Transform(mouth, mouth_open(h=0.28 + 0.08 * k)), run_time=0.26)
            self.play(
                LaggedStart(*[Flash(s, color=WHITE, num_lines=10, flash_radius=0.28,
                                    line_length=0.14) for s in MUSCLE_SITES],
                            lag_ratio=0.06),
                run_time=0.6)
            self.play(Transform(mouth, mouth_closed()), run_time=0.22)

        # ---- BEAT 3: the 31-sensor array grows onto the skin -----------
        self.next_section("sensors")
        sensors = sensor_array(fill=0.5)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in sensors],
                              lag_ratio=0.04),
                  run_time=1.4)
        self.wait(0.5)
