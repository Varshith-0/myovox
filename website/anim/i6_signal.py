# I6 — Signal. Why muscles make electricity, what EMG is, what "31 channels"
# means, and the dataset behind it all.
# Beats (roughly one per narration sentence; a couple span two):
#   1 VOLT     muscle fibres fire to contract -> a faint ~1 mV pulse at the skin.
#   2 READ     too faint to feel, but a skin sensor can read it.
#   3 EMG      that recording has a name: EMG = electro (electricity) + myo
#              (muscle) + graphy (recording).
#   4 GRID     31 sensors over the face/neck; each is one channel, 5,000 / s.
#   5 MIC      a microphone records the real voice alongside — training only.
#   6 TRACES   31 wiggly lines come back — overlapping, mostly noise.
#   7 DATA     one corpus, one speaker: 9,660 sentences, split, 34,546-word lexicon.
#   8 QUESTION every word is hidden in here — how do we pull it back out?
from manim import *
from emg_style import *
import numpy as np


def trace(x0, x1, y, amp, n=240, freq=2.0, phase=0.0, jag=0.0):
    xs = np.linspace(x0, x1, n)
    t = np.linspace(0, 1, n)
    w = (np.sin(2 * PI * freq * t + phase) + 0.5 * np.sin(2 * PI * freq * 2.3 * t + phase * 1.7)
         + 0.3 * np.sin(2 * PI * freq * 4.1 * t + phase * 0.6))
    if jag:
        w = w + jag * np.random.uniform(-1, 1, n)
    w = w / np.max(np.abs(w))
    return VMobject().set_points_smoothly([[xs[i], y + amp * w[i], 0] for i in range(n)])


def grid31():
    rows = [(0.4, np.linspace(-1.0, 1.0, 4)), (0.0, np.linspace(-1.3, 1.3, 5)),
            (-0.4, np.linspace(-1.3, 1.3, 5)), (-0.8, np.linspace(-1.2, 1.2, 5)),
            (-1.2, np.linspace(-0.95, 0.95, 4)), (-1.6, np.linspace(-0.8, 0.8, 4)),
            (-2.0, np.linspace(-0.4, 0.4, 2)), (-2.4, np.linspace(-0.4, 0.4, 2))]
    return [[x, y, 0] for y, xs in rows for x in xs]


def head_outline():
    head = Ellipse(width=3.2, height=4.2).set_stroke(INK_GHOST, 2).move_to([0, 0.6, 0])
    neck = VGroup(Line([-0.6, -1.4, 0], [-0.75, -2.7, 0]), Line([0.6, -1.4, 0], [0.75, -2.7, 0])).set_stroke(INK_GHOST, 2)
    return VGroup(head, neck)


def mic_icon(at):
    body = RoundedRectangle(width=0.34, height=0.7, corner_radius=0.17).set_stroke(INK, 2.4)
    stem = Line([0, -0.35, 0], [0, -0.62, 0]).set_stroke(INK, 2.4)
    base = Line([-0.18, -0.62, 0], [0.18, -0.62, 0]).set_stroke(INK, 2.4)
    arc = Arc(0.28, -PI, PI, arc_center=[0, 0, 0]).set_stroke(INK, 2)
    return VGroup(body, stem, base, arc).move_to(at)


class Signal(Scene):
    def construct(self):
        seed()

        # ---- BEAT 1: WHY ELECTRICITY ------------------------------------
        self.next_section("volt")
        fibers = VGroup(*[Line([x, -0.5, 0], [x, 0.5, 0], stroke_color=INK, stroke_width=3)
                          for x in np.linspace(-5.4, -4.4, 5)])
        fib_lab = mono("muscle fibres", 18, INK_FAINT).next_to(fibers, DOWN, buff=0.25)
        axis = VGroup(Line([-3.2, -1.2, 0], [5.4, -1.2, 0], stroke_color=INK_GHOST, stroke_width=1.6),
                      Line([-3.2, -1.2, 0], [-3.2, 1.4, 0], stroke_color=INK_GHOST, stroke_width=1.6))
        pulse = trace(-3.0, 5.2, 0.0, 1.3, n=300, freq=1.0, jag=0.02).set_stroke(INK, 2.2)
        why = mono("to contract, muscle fibres fire tiny electrical pulses", 22, INK_DIM).move_to([0, 2.7, 0])
        v_lab = mono("≈ 1 mV at the skin  (a thousandth of a volt)", 21, INK).next_to(axis, UP, buff=0.1).shift(RIGHT * 1.2)
        self.play(FadeIn(why, shift=DOWN * 0.1), Create(fibers), FadeIn(fib_lab), run_time=0.7)
        self.play(LaggedStart(*[Flash(f.get_center(), color="#ffffff", line_length=0.12, num_lines=6, flash_radius=0.2) for f in fibers], lag_ratio=0.1, run_time=0.7),
                  Create(axis))
        self.play(Create(pulse, run_time=0.8), FadeIn(v_lab, shift=DOWN * 0.1))
        self.wait(0.3)

        # ---- BEAT 2: READ -----------------------------------------------
        self.next_section("read")
        sensor = VGroup(Circle(0.22, stroke_color="#ffffff", stroke_width=2.5).set_fill(INK, 0.1),
                        Dot(radius=0.05, color="#ffffff")).move_to([1.0, 2.4, 0])
        read = mono("too faint to feel — but a sensor on the skin can read it", 22, INK_FAINT).move_to([0, -3.3, 0])
        self.play(FadeIn(read), sensor.animate.move_to([1.0, 0.2, 0]), run_time=0.7)
        self.play(Flash([1.0, 0.0, 0], color="#ffffff", num_lines=12, flash_radius=0.4), run_time=0.4)
        self.wait(0.25)

        # ---- BEAT 3: WHAT EMG IS ----------------------------------------
        self.next_section("emg")
        self.play(FadeOut(VGroup(fibers, fib_lab, axis, pulse, why, v_lab, read, sensor)), run_time=0.4)
        emg = mono("EMG", 84, INK)
        emg_g = glow(emg.move_to([0, 1.4, 0]))
        parts = VGroup(
            VGroup(mono("electro", 30, INK), mono("electricity", 18, INK_FAINT)).arrange(DOWN, buff=0.12),
            VGroup(mono("myo", 30, INK), mono("muscle", 18, INK_FAINT)).arrange(DOWN, buff=0.12),
            VGroup(mono("graphy", 30, INK), mono("recording", 18, INK_FAINT)).arrange(DOWN, buff=0.12),
        ).arrange(RIGHT, buff=1.1).move_to([0, -0.8, 0])
        plus = VGroup(mono("+", 30, INK_FAINT).move_to((parts[0].get_right() + parts[1].get_left()) / 2),
                      mono("+", 30, INK_FAINT).move_to((parts[1].get_right() + parts[2].get_left()) / 2))
        self.add(emg_g)
        self.play(FadeIn(emg, shift=UP * 0.06), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in parts], lag_ratio=0.25),
                  FadeIn(plus), run_time=1.1)
        self.wait(0.4)

        # ---- BEAT 4: 31 CHANNELS ----------------------------------------
        self.next_section("grid")
        self.play(FadeOut(VGroup(emg_g, emg, parts, plus)), run_time=0.4)
        head = head_outline()
        dots = VGroup(*[Circle(0.1, stroke_color=INK, stroke_width=1.8).set_fill("#ffffff", 0.5).move_to(p)
                        for p in grid31()])
        gtag = mono("31 sensors on the face & neck", 25, INK).move_to([0, 2.9, 0])
        chan = mono("each sensor = one channel  ·  5,000 readings / second", 21, INK_DIM).move_to([0, -3.35, 0])
        self.play(Create(head), FadeIn(gtag, shift=DOWN * 0.1), run_time=0.6)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.04, run_time=1.2))
        self.play(FadeIn(chan, shift=UP * 0.1), run_time=0.4)
        self.wait(0.3)

        # ---- BEAT 5: MIC ------------------------------------------------
        self.next_section("mic")
        mic = mic_icon([4.6, 0.2, 0])
        mtag = mono("training only", 18, INK_FAINT).next_to(mic, DOWN, buff=0.2)
        mlink = DashedLine([1.8, 0.0, 0], mic.get_left(), stroke_color=INK_GHOST, stroke_width=1.4)
        mnote = mono("a microphone records the real voice too — gone at real use", 21, INK_DIM).move_to([0, -3.35, 0])
        self.play(FadeOut(chan), FadeIn(mic, shift=LEFT * 0.1), Create(mlink), FadeIn(mtag), run_time=0.6)
        self.play(FadeIn(mnote, shift=UP * 0.1), run_time=0.4)
        slash = Line(mic.get_corner(DL) + DOWN * 0.1, mic.get_corner(UR) + UP * 0.1).set_stroke("#ffffff", 3)
        self.play(GrowFromCenter(slash), run_time=0.4)
        self.wait(0.25)

        # ---- BEAT 6: TRACES ---------------------------------------------
        self.next_section("traces")
        self.play(FadeOut(VGroup(head, dots, gtag, mic, mtag, mlink, mnote, slash)), run_time=0.4)
        ys = np.linspace(2.5, -2.5, 31)
        traces = VGroup(*[trace(-5.8, 5.8, y, 0.1, freq=1.3 + 0.1 * i, phase=i * 0.6, jag=0.06)
                          .set_stroke(INK, 1.2, opacity=0.6) for i, y in enumerate(ys)])
        ttag = mono("31 channels — overlapping, mostly noise", 22, INK_DIM).move_to([0, -3.4, 0])
        self.play(LaggedStart(*[Create(t) for t in traces], lag_ratio=0.02, run_time=1.4), FadeIn(ttag))
        self.wait(0.3)

        # ---- BEAT 7: DATA -----------------------------------------------
        self.next_section("data")
        self.play(traces.animate.set_stroke(opacity=0.12), FadeOut(ttag), run_time=0.4)
        ct = ValueTracker(0)
        big = counter(ct, fmt=lambda v: f"{int(v):,}", s=92, c=INK, at=[0, 1.7, 0])
        big_lab = mono("sentences  ·  one speaker", 24, INK_DIM)
        big_lab.add_updater(lambda m: m.next_to(big, DOWN, buff=0.25))
        self.add(big, big_lab)
        self.play(ct.animate.set_value(9660), run_time=1.0, rate_func=rush_into)
        big.clear_updaters(); big_lab.clear_updaters()
        total, W = 9660, 8.0
        segs = [("train", 8500), ("val", 760), ("test", 400)]
        bar = VGroup()
        x = -W / 2
        for i, (name, n) in enumerate(segs):
            w = n / total * W
            r = Rectangle(width=w, height=0.4).move_to([x + w / 2, -0.5, 0])
            r.set_stroke(INK_GHOST, 1.2).set_fill("#ffffff" if i == 0 else INK, 0.85 if i == 0 else 0.12)
            lab = mono(f"{n:,} {name}", 17, INK if i == 0 else INK_FAINT).next_to(r, DOWN, buff=0.12)
            bar.add(VGroup(r, lab))
            x += w
        bar[1][1].next_to(bar[1][0], UP, buff=0.12)
        lex = mono("decoded against a 34,546-word dictionary  ·  5× the training words", 22, INK).move_to([0, -2.7, 0])
        self.play(LaggedStart(*[GrowFromEdge(s[0], LEFT) for s in bar], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(s[1]) for s in bar], lag_ratio=0.1), run_time=0.9)
        self.play(FadeIn(lex, shift=UP * 0.1), run_time=0.5)
        self.wait(0.4)

        # ---- BEAT 8: QUESTION -------------------------------------------
        self.next_section("question")
        self.play(FadeOut(VGroup(big, big_lab, bar, lex)), traces.animate.set_stroke(opacity=0.5), run_time=0.35)
        q1 = serif("hidden in here is every word", 44).move_to([0, 0.5, 0])
        q2 = mono("how do we pull them back out?", 26, INK_DIM).move_to([0, -0.6, 0])
        self.play(FadeIn(q1, shift=UP * 0.08, run_time=0.7))
        self.play(FadeIn(q2, shift=UP * 0.1), run_time=0.5)
        self.wait(0.6)
