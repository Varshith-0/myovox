# website/anim/b10_what_is_convolution.py — B10 "The other lens" (convolution)
#
# Earned right after what-is-attention. Discovery arc puzzle->predict->reveal->NAME:
#   1 attention REACHED FAR — brighten the inherited fan as a fresh success.
#   2 but reaching far has a COST — dim the fan to faint "the far view".
#   3 the cost felt: one snapshot's crisp edge gets SMEARED flat.
#   4 so add a second lens — a small magnifier WINDOW of 3 that slides.
#   5 it reads each local patch; on the edge snapshot a loupe pops and the
#     smear snaps to a crisp tall tick — the detail the wide view missed.
#   6 NAME the sliding-window lens: convolution (serif #fff payoff).
#   7 both lenses on one output -> the Conformer.
#
# Layout (x[-7,7] y[-3.9,3.9], strict monochrome on #050505):
#   TOP  (fan above the row): the lingering attention arcs, "the far view".
#   CENTER (FRAME_Y): a row of frames the lenses read; one holds a fine edge.
#   BELOW (out_y): the sharpened local-detail output track + ticks.
#   BOTTOM: serif "convolution" payoff, then the Conformer hand-off.
from manim import *
from emg_style import *

WHITE = "#ffffff"

N_FRAMES = 9
FRAME_X0 = -5.2
FRAME_DX = 1.30
FRAME_Y = 0.55
FRAME_W = 0.46
WIN = 3


def frame_x(i):
    return FRAME_X0 + i * FRAME_DX


class WhatIsConvolution(Scene):
    def construct(self):
        seed()

        edge_i = 6          # the snapshot that hides a fine edge
        q = 4               # the attention query snapshot

        # ============================================================
        # BEAT 1 — attention reached FAR (brighten the inherited fan).
        # ============================================================
        self.next_section("reach_far")

        frames = VGroup()
        for i in range(N_FRAMES):
            sq = Square(FRAME_W, stroke_color=INK_DIM, stroke_width=1.6,
                        fill_opacity=0).move_to([frame_x(i), FRAME_Y, 0])
            frames.add(sq)
        self.play(LaggedStart(*[Create(s) for s in frames], lag_ratio=0.05),
                  run_time=0.55)

        top_edge = FRAME_Y + FRAME_W / 2
        fan = VGroup()
        for j in range(N_FRAMES):
            if j == q:
                continue
            arc = ArcBetweenPoints(
                np.array([frame_x(q), top_edge, 0]),
                np.array([frame_x(j), top_edge, 0]),
                angle=-PI / 2.6, stroke_color=INK, stroke_width=2.0)
            arc.set_fill(opacity=0)
            fan.add(arc)
        q_box = Square(FRAME_W + 0.10, stroke_color=WHITE, stroke_width=2.2,
                       fill_opacity=0).move_to([frame_x(q), FRAME_Y, 0])
        self.play(FadeIn(q_box),
                  LaggedStart(*[Create(a) for a in fan], lag_ratio=0.06),
                  run_time=1.0)
        self.wait(0.35)

        # ============================================================
        # BEAT 2 — but reaching that far has a COST (dim the fan).
        # ============================================================
        self.next_section("cost")

        far_lab = mono("the far view", 16, INK_FAINT).move_to([0, 2.30, 0])
        far_view = VGroup(fan, far_lab)
        self.play(fan.animate.set_stroke(color=INK_FAINT, opacity=0.22),
                  FadeOut(q_box),
                  FadeIn(far_lab), run_time=0.55)
        self.wait(0.1)

        # ============================================================
        # BEAT 3 — the cost FELT: a crisp edge smeared flat.
        # ============================================================
        self.next_section("smear")

        # dim the rest of the row; spotlight only the edge snapshot.
        others = VGroup(*[frames[i] for i in range(N_FRAMES) if i != edge_i])
        self.play(others.animate.set_stroke(opacity=0.35),
                  frames[edge_i].animate.set_stroke(color=INK, width=2.0),
                  run_time=0.5)

        smear = Line([frame_x(edge_i) - 0.15, FRAME_Y, 0],
                     [frame_x(edge_i) + 0.15, FRAME_Y, 0],
                     stroke_color=INK_FAINT, stroke_width=2.4).set_opacity(0.5)
        smear_lab = mono("a sharp edge — smeared flat", 15, INK_DIM)
        smear_lab.next_to(frames[edge_i], UP, buff=0.40)
        self.play(Create(smear), FadeIn(smear_lab, shift=DOWN * 0.06),
                  run_time=0.7)
        self.wait(0.7)

        # ============================================================
        # BEAT 4 — a second lens: a small sliding magnifier window of 3.
        # ============================================================
        self.next_section("window")

        self.play(FadeOut(smear_lab),
                  others.animate.set_stroke(color=INK_DIM, opacity=1.0),
                  frames[edge_i].animate.set_stroke(color=INK_DIM, width=1.6),
                  run_time=0.45)

        def make_window(center_i, h=0.92, c=INK, w=2.8):
            lo = frame_x(center_i - 1) - FRAME_W * 0.62
            hi = frame_x(center_i + 1) + FRAME_W * 0.62
            top, bot = FRAME_Y + h / 2, FRAME_Y - h / 2
            ear = 0.16
            return VGroup(
                Line([lo, top, 0], [lo + ear, top, 0], stroke_color=c, stroke_width=w),
                Line([lo, top, 0], [lo, bot, 0], stroke_color=c, stroke_width=w),
                Line([lo, bot, 0], [lo + ear, bot, 0], stroke_color=c, stroke_width=w),
                Line([hi, top, 0], [hi - ear, top, 0], stroke_color=c, stroke_width=w),
                Line([hi, top, 0], [hi, bot, 0], stroke_color=c, stroke_width=w),
                Line([hi, bot, 0], [hi - ear, bot, 0], stroke_color=c, stroke_width=w),
            )

        winT = ValueTracker(1.0)
        window = make_window(1)
        window.add_updater(lambda m: m.become(make_window(int(round(winT.get_value())))))
        win_tag = mono("window of 3", 14, INK_DIM)
        win_tag.add_updater(lambda m: m.next_to(window, UP, buff=0.16))
        self.add(window, win_tag)
        self.play(FadeIn(window), FadeIn(win_tag), run_time=0.45)

        out_y = -1.15
        out_track = Line([frame_x(0), out_y, 0], [frame_x(N_FRAMES - 1), out_y, 0],
                         stroke_color=INK_GHOST, stroke_width=1.2)
        out_lab = mono("local detail", 14, INK_FAINT)
        out_lab.next_to(out_track, DOWN, buff=0.16).align_to(out_track, LEFT)
        self.play(Create(out_track), FadeIn(out_lab), run_time=0.55)
        self.wait(0.6)

        # ============================================================
        # BEAT 5 — slide; emit a tick per patch; loupe pops the sharp edge.
        # ============================================================
        self.next_section("slide")

        self.play(fan.animate.set_opacity(0.0), far_lab.animate.set_opacity(0.0),
                  run_time=0.25)

        heights = [0.30, 0.26, 0.34, 0.28, 0.30, 0.66, 0.30][:N_FRAMES - 2]
        out_marks = VGroup()

        def emit_at(stop_i, h, accent=False):
            x = frame_x(stop_i)
            c = WHITE if accent else INK
            w = 4.0 if accent else 2.6
            tick = Line([x, out_y, 0], [x, out_y - h, 0], stroke_color=c, stroke_width=w)
            dot = Dot([x, out_y - h, 0], radius=0.045, color=c)
            return VGroup(tick, dot)

        loupe = sharp = None
        for k in range(N_FRAMES - 2):
            stop_i = k + 1
            accent = (stop_i == edge_i)
            self.play(winT.animate.set_value(stop_i), run_time=0.16, rate_func=smooth)
            mark = emit_at(stop_i, heights[k], accent=accent)
            out_marks.add(mark)
            if accent:
                loupe = Circle(radius=0.34, stroke_color=WHITE, stroke_width=2.6)
                loupe.move_to([frame_x(edge_i), FRAME_Y, 0])
                sharp = Line([frame_x(edge_i), FRAME_Y - 0.13, 0],
                             [frame_x(edge_i), FRAME_Y + 0.13, 0],
                             stroke_color=WHITE, stroke_width=3.4)
                self.play(Create(mark), Create(loupe), run_time=0.30)
                self.play(smear.animate.set_opacity(0.0), Create(sharp), run_time=0.28)
            else:
                self.play(Create(mark), run_time=0.10)
        self.play(winT.animate.set_value(edge_i), run_time=0.2)
        self.add(out_marks)
        self.wait(0.15)

        # ============================================================
        # BEAT 6 — NAME IT: convolution (serif #fff payoff, single flash).
        # ============================================================
        self.next_section("name")

        window.clear_updaters()
        win_tag.clear_updaters()
        self.play(FadeOut(win_tag), FadeOut(out_lab), run_time=0.2)

        payoff = serif("convolution", 56, WHITE).move_to([0, -2.95, 0])
        payoff_g = glow(payoff)
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  Flash([0, -2.95, 0], color=WHITE, line_length=0.18, num_lines=12,
                        flash_radius=1.3, time_width=0.4), run_time=0.6)
        self.wait(0.25)

        # ============================================================
        # BEAT 7 — both lenses on one output -> the Conformer.
        # ============================================================
        self.next_section("conformer")

        self.play(fan.animate.set_stroke(color=INK, opacity=0.7),
                  FadeOut(far_lab),
                  Indicate(window, scale_factor=1.06, color=INK),
                  run_time=0.6)
        sub = mono("attention reaches  ·  convolution magnifies  →  Conformer",
                   18, INK_DIM).move_to([0, -3.55, 0])
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.6)
        self.wait(0.9)
