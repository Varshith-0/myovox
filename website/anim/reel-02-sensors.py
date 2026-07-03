# REEL 2 — SENSORS. "31 sensors catch those pulses, 5000 readings a second. No mic."
# OPENS ON: head + face + 31 grid sensors  (== scene 1 close).
# The sensors brighten; then EACH sensor unfurls into ONE line of the waterfall —
# the face-signal literally BECOMES the 31-channel recording — so the "5000
# readings/second" waterfall is the exact same signal, matched line-for-line.
# CLOSES ON: the 31-line waterfall  (== scene 3 open).
from manim import *
from style import *
from reel_common import (WHITE, head_outline, face_features, mouth_closed,
                         grid31_positions, sensor_array, waterfall, motes, drift)


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

        # ---- OPEN: head + face + sensors (matched from scene 1) --------
        self.next_section("open")
        head = head_outline(INK, 2.2)
        feats = face_features()
        mouth = mouth_closed()
        sensors = sensor_array(fill=0.5)
        self.add(head, feats, mouth, sensors)
        self.wait(0.1)

        # ---- BEAT 1: sensors brighten, count reads 31 ------------------
        self.next_section("brighten")
        count = mono("31 sensors", 24, INK_FAINT).to_edge(UP, buff=0.5)
        self.play(
            LaggedStart(*[Flash(d.get_center(), color=WHITE, num_lines=8,
                                flash_radius=0.16, line_length=0.07)
                          for d in sensors], lag_ratio=0.02),
            sensors.animate.set_fill(WHITE, 0.95),
            FadeIn(count, shift=DOWN * 0.1), run_time=1.0)
        self.play(sensors.animate.set_fill(WHITE, 0.6), run_time=0.3)
        self.wait(0.1)

        # ---- BEAT 2: each sensor unfurls into ITS waterfall line -------
        self.next_section("stream")
        pos = grid31_positions()
        wf = waterfall()  # the exact 31-line recording (== scene 3 open)
        # Each final line, collapsed to a bright point at its sensor. Transforming
        # seed[i] -> wf[i] makes the face-signal literally become the recording,
        # line-for-line, and lands on the exact waterfall geometry.
        seeds = VGroup()
        for i, line in enumerate(wf):
            s = line.copy().scale(0.04).move_to(pos[i]).set_stroke(INK, 1.3, opacity=0.0)
            seeds.add(s)
        self.add(seeds)

        rate = mono("5000 readings / second", 22, INK_FAINT).to_edge(UP, buff=0.5)
        self.play(
            FadeOut(VGroup(head, feats, mouth)),
            sensors.animate.set_fill(WHITE, 0.0).set_stroke(opacity=0.0),
            LaggedStart(*[Transform(seeds[i], wf[i]) for i in range(len(wf))],
                        lag_ratio=0.02),
            Transform(count, rate),
            run_time=1.7, rate_func=smooth)
        self.remove(sensors)
        self.wait(0.2)

        # ---- BEAT 3: no microphone -------------------------------------
        self.next_section("no-mic")
        m = mic([5.1, 2.3, 0])
        mlab = mono("no microphone", 18, INK_FAINT).next_to(m, DOWN, buff=0.12)
        self.play(FadeIn(m, scale=1.2), FadeIn(mlab), run_time=0.5)
        slash = Line([5.1 - 0.4, 2.3 - 0.45, 0], [5.1 + 0.4, 2.3 + 0.45, 0]).set_stroke(WHITE, 3.0)
        self.play(GrowFromCenter(slash), run_time=0.4)
        self.play(FadeOut(VGroup(m, mlab, slash), scale=0.6), run_time=0.5)
        self.wait(0.5)
