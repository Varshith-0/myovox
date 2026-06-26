# I1 — Hero. The claim: read speech from facial muscles, with the sound off.
# Beats (one per narration sentence):
#   1 SILENT    an audio waveform is muted to a dead flat line — "sound, off".
#   2 SIGNAL    31 faint EMG traces rise from the skin in its place.
#   3 RECOVER   the 31 collapse into one bright trace, which becomes the words.
#   4 PROMISE   "four words in five" + the title EMG -> TEXT.
from manim import *
from emg_style import *
import numpy as np

X0, X1 = -5.6, 5.6


def trace(x0, x1, y, amp, n=260, freq=2.0, phase=0.0, jag=0.0):
    """A wiggly EMG-like line from x0..x1 centred on y with peak amplitude `amp`."""
    xs = np.linspace(x0, x1, n)
    t = np.linspace(0, 1, n)
    w = (np.sin(2 * PI * freq * t + phase)
         + 0.5 * np.sin(2 * PI * freq * 2.3 * t + phase * 1.7)
         + 0.3 * np.sin(2 * PI * freq * 4.1 * t + phase * 0.6))
    if jag:
        w = w + jag * np.random.uniform(-1, 1, n)
    w = w / np.max(np.abs(w))
    pts = np.array([[xs[i], y + amp * w[i], 0] for i in range(n)])
    return VMobject().set_points_smoothly(pts)


def speaker(at, c=INK):
    cone = Polygon([-0.2, -0.18, 0], [-0.2, 0.18, 0], [0.05, 0.4, 0], [0.05, -0.4, 0],
                   color=c, fill_opacity=0.9, stroke_width=0)
    a1 = Arc(0.24, -PI / 3, 2 * PI / 3, arc_center=[0.14, 0, 0]).set_stroke(c, 2.5)
    a2 = Arc(0.42, -PI / 3, 2 * PI / 3, arc_center=[0.14, 0, 0]).set_stroke(c, 2.5)
    return VGroup(cone, a1, a2).move_to(at)


class Hero(Scene):
    def construct(self):
        seed()

        # ---- BEAT 1: SILENT ---------------------------------------------
        self.next_section("silent")
        spk = speaker([-4.9, 0, 0])
        wave = trace(-4.1, X1, 0.0, 0.7, n=360, freq=6.0, jag=0.04)
        wave.set_stroke(INK, width=2.2, opacity=0.95)
        self.play(FadeIn(spk, run_time=0.5), Create(wave, run_time=0.9))
        self.wait(0.25)

        slash = Line([-5.35, -0.5, 0], [-4.45, 0.5, 0]).set_stroke("#ffffff", 3.2)
        flat = Line([-4.1, 0, 0], [X1, 0, 0]).set_stroke(INK_FAINT, 2)
        off = mono("sound — off", 26, INK_DIM).move_to([0.7, -1.5, 0])
        self.play(Transform(wave, flat), GrowFromCenter(slash),
                  FadeIn(off, shift=UP * 0.1), run_time=0.7)
        self.wait(0.4)

        # ---- BEAT 2: SIGNAL ---------------------------------------------
        self.next_section("signal")
        N = 31
        ys = np.linspace(2.3, -2.3, N)
        bundle = VGroup()
        for i, y in enumerate(ys):
            tr = trace(X0, X1, y, 0.12, freq=1.4 + 0.12 * i, phase=i * 0.7, jag=0.05)
            tr.set_stroke(INK, width=1.3, opacity=0.55)
            bundle.add(tr)
        tag = mono("face & throat muscles  ·  tiny electrical pulses at the skin", 22, INK_FAINT)
        tag.move_to([0, -3.4, 0])
        self.play(FadeOut(VGroup(wave, spk, slash, off), run_time=0.4))
        self.play(LaggedStart(*[Create(t) for t in bundle], lag_ratio=0.03, run_time=1.4),
                  FadeIn(tag, run_time=0.6))
        self.wait(0.4)

        # ---- BEAT 3: RECOVER --------------------------------------------
        self.next_section("recover")
        one = trace(X0, X1, 0.0, 0.5, freq=2.0, phase=0.3, jag=0.02)
        one.set_stroke("#ffffff", width=2.4, opacity=1.0)
        self.play(Transform(bundle, VGroup(*[one.copy() for _ in range(N)])),
                  FadeOut(tag), run_time=0.9)
        self.remove(bundle)
        gone = glow(one)
        self.add(gone)
        phrase = serif("read speech from muscles", 56).move_to([0, 0.1, 0])
        self.play(FadeOut(gone, run_time=0.5), Write(phrase, run_time=1.0))
        self.wait(0.4)

        # ---- BEAT 4: PROMISE --------------------------------------------
        self.next_section("promise")
        self.play(phrase.animate.scale(0.5).move_to([0, 1.5, 0]).set_opacity(0.55),
                  run_time=0.55)
        title = VGroup(mono("EMG", 66, INK), mono("→", 66, INK_DIM), mono("TEXT", 66, INK))
        title.arrange(RIGHT, buff=0.42).move_to(ORIGIN)
        promise = mono("four words in five, correct", 30, INK_DIM).move_to([0, -1.7, 0])
        self.add(glow(title))
        self.play(FadeIn(title, shift=UP * 0.1, run_time=0.7),
                  Flash(title.get_center(), color="#ffffff", num_lines=16,
                        flash_radius=1.5, line_length=0.3))
        self.play(FadeIn(promise, shift=UP * 0.1), run_time=0.5)
        self.wait(0.6)
