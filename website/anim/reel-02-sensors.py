# REEL 2 — SENSORS. "31 sensors catch those pulses, 5000 readings a second. No mic."
# OPENS ON: face_front + 31 settled sensor points  (== scene 1 close).
# The points brighten to sensors; a live trace unspools from each; the face slides
# away as a full 31-line waterfall fills the frame; a microphone is struck out.
# CLOSES ON: the 31-line waterfall  (== scene 3 open).
from manim import *
from style import *
from reel_common import (WHITE, face_front, sensor_positions, waterfall,
                         trace, motes, drift)
import numpy as np


def mic(at, c=INK):
    cap = RoundedRectangle(width=0.26, height=0.42, corner_radius=0.13,
                           stroke_color=c, stroke_width=2.4, fill_opacity=0).move_to(at)
    arc = Arc(0.22, PI + 0.5, PI - 1.0, arc_center=at + DOWN * 0.05).set_stroke(c, 2.2)
    stem = Line(at + DOWN * 0.27, at + DOWN * 0.5).set_stroke(c, 2.2)
    base = Line(at + DOWN * 0.5 + LEFT * 0.16, at + DOWN * 0.5 + RIGHT * 0.16).set_stroke(c, 2.2)
    return VGroup(cap, arc, stem, base)


class Sensors(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: re-materialise the face + settled sensors -----------
        self.next_section("open")
        fc = face_front()
        pos = sensor_positions(31)
        sensors = VGroup(*[Dot(pos[i], radius=0.045, color=INK).set_opacity(0.55)
                           for i in range(len(pos))])
        self.add(fc, sensors)
        self.wait(0.1)

        # ---- BEAT 1: sensors brighten, count reads 31 ------------------
        self.next_section("brighten")
        count = mono("31 sensors", 24, INK_FAINT).to_edge(UP, buff=0.5)
        self.play(sensors.animate.set_opacity(0.95).set_color(WHITE),
                  LaggedStart(*[Flash(p.get_center(), color=WHITE, num_lines=8,
                                      flash_radius=0.14, line_length=0.06)
                                for p in sensors], lag_ratio=0.02, run_time=0.9),
                  FadeIn(count, shift=DOWN * 0.1))
        self.play(sensors.animate.set_color(INK).set_opacity(0.8), run_time=0.3)
        self.wait(0.15)

        # ---- BEAT 2: traces unspool; face slides off; waterfall forms --
        self.next_section("stream")
        wf = waterfall()
        # each sensor emits a short trace that grows into a full channel line
        subset = list(range(0, 31, 1))
        stubs = VGroup()
        for i in subset:
            y = pos[i % len(pos)][1]
            st = trace(pos[i % len(pos)][0], pos[i % len(pos)][0] + 1.6, y, 0.09,
                       n=60, freq=2.0 + 0.1 * i, seed_n=200 + i)
            st.set_stroke(INK, 1.2, opacity=0.6)
            stubs.add(st)
        self.play(LaggedStart(*[Create(s) for s in stubs], lag_ratio=0.02, run_time=0.9))

        rate = mono("5000 readings / second", 22, INK_FAINT).to_edge(UP, buff=0.5)
        self.play(
            FadeOut(fc, shift=LEFT * 1.2),
            FadeOut(sensors, shift=LEFT * 1.2),
            FadeOut(stubs, shift=LEFT * 0.6),
            LaggedStart(*[Create(t) for t in wf], lag_ratio=0.02),
            Transform(count, rate),
            run_time=1.5, rate_func=smooth)
        self.wait(0.2)

        # ---- BEAT 3: no microphone -------------------------------------
        self.next_section("no-mic")
        m = mic([5.1, 2.3, 0])
        mlab = mono("no microphone", 18, INK_FAINT).next_to(m, DOWN, buff=0.12)
        self.play(FadeIn(m, scale=1.2), FadeIn(mlab), run_time=0.5)
        slash = Line([5.1 - 0.4, 2.3 - 0.45, 0], [5.1 + 0.4, 2.3 + 0.45, 0]).set_stroke(WHITE, 3.0)
        self.play(GrowFromCenter(slash), run_time=0.4)
        self.play(FadeOut(VGroup(m, mlab, slash), scale=0.6), run_time=0.5)
        # let the waterfall keep undulating a touch (never a dead frame)
        self.wait(0.5)
