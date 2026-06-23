# website/anim/b10_what_is_convolution.py — B10 "The other lens" (convolution)
#
# Earned right after what-is-attention: attention is the TELESCOPE (reaches far
# but smears the fine grain); convolution is the MAGNIFYING GLASS (a tiny window
# sliding along, reading only a frame and its close neighbours, catching the
# sharp local texture the wide view blurs flat). A reader that runs BOTH lenses
# at once is the Conformer, named next.
#
# Three persistent zones (3b1b: pose -> build -> transform -> NAME):
#   TOP  (y ~ +3.0):  context cap + the lingering attention fan, dimmed as "far".
#   CENTER(y ~ -1.3..+2.0): a row of frames; a small bracket WINDOW slides L->R,
#                  reading 3 local neighbours; at each stop it emits a sharpened
#                  local-feature mark; one frame holds a fine edge the broad view
#                  smeared flat — the magnifier catches it.
#   BOTTOM(y ~ -3.1): both lenses overlaid on one frame (far beam + near bracket)
#                  feeding one output; resolves to serif "two lenses".
from manim import *
from emg_style import *

WHITE = "#ffffff"

N_FRAMES = 9          # the sequence the lenses read
FRAME_X0 = -5.2       # leftmost frame centre x
FRAME_DX = 1.30       # spacing between frames
FRAME_Y = 0.55        # the frame-row baseline
FRAME_W = 0.46        # frame square size
WIN = 3               # convolution window width (a handful of neighbours)


def frame_x(i):
    return FRAME_X0 + i * FRAME_DX


def tri(angle, c, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


class WhatIsConvolution(Scene):
    def construct(self):
        seed()

        # ============================================================
        # B0 — POSE: the frame row + the lingering attention fan (far).
        # ============================================================
        self.next_section("pose")

        cap = mono("ATTENTION REACHES FAR — BUT SMEARS THE FINE GRAIN", 22, INK_DIM,
                   w=BOLD).move_to([0, 3.30, 0])
        rule = Line([-6.4, 2.98, 0], [6.4, 2.98, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(cap, shift=DOWN * 0.12), Create(rule), run_time=0.45)

        # the row of frames — the sequence both lenses read.
        frames = VGroup()
        for i in range(N_FRAMES):
            sq = Square(FRAME_W, stroke_color=INK_GHOST, stroke_width=1.4,
                        fill_opacity=0).move_to([frame_x(i), FRAME_Y, 0])
            frames.add(sq)
        self.play(LaggedStartMap(Create, frames, lag_ratio=0.05, run_time=0.55))

        # the attention fan from the prior card, drawn faint then pushed to the
        # top as the dimmed "far view" — many thin arcs from one query frame
        # reaching every other frame (distance does not matter to it).
        q = 4  # the query frame
        top_edge = FRAME_Y + FRAME_W / 2
        fan = VGroup()
        for j in range(N_FRAMES):
            if j == q:
                continue
            start = np.array([frame_x(q), top_edge, 0])
            end = np.array([frame_x(j), top_edge, 0])
            arc = ArcBetweenPoints(start, end, angle=-PI / 2.6,
                                   stroke_color=INK_FAINT, stroke_width=1.4)
            arc.set_fill(opacity=0)
            fan.add(arc)
        far_lab = mono("the far view", 16, INK_FAINT).move_to([0, 2.20, 0])
        self.play(LaggedStartMap(Create, fan, lag_ratio=0.06, run_time=0.7),
                  FadeIn(far_lab), run_time=0.7)

        far_view = VGroup(fan, far_lab)
        self.play(far_view.animate.set_opacity(0.22), run_time=0.45)
        self.wait(0.3)

        # ============================================================
        # B1 — BUILD: a small bracket window appears + slides L->R,
        #      reading only its local neighbours.
        # ============================================================
        self.next_section("window")

        sub = mono("so the reader carries a second lens: a sliding magnifier",
                   18, INK_FAINT).move_to([0, -2.05, 0])
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)

        # the bracket = a window of WIN frames. Built from two corner brackets.
        def make_window(center_i, h=0.92, c=INK, w=2.6):
            lo = frame_x(center_i - 1) - FRAME_W * 0.62
            hi = frame_x(center_i + 1) + FRAME_W * 0.62
            top, bot = FRAME_Y + h / 2, FRAME_Y - h / 2
            ear = 0.16
            brk = VGroup(
                Line([lo, top, 0], [lo + ear, top, 0], stroke_color=c, stroke_width=w),
                Line([lo, top, 0], [lo, bot, 0], stroke_color=c, stroke_width=w),
                Line([lo, bot, 0], [lo + ear, bot, 0], stroke_color=c, stroke_width=w),
                Line([hi, top, 0], [hi - ear, top, 0], stroke_color=c, stroke_width=w),
                Line([hi, top, 0], [hi, bot, 0], stroke_color=c, stroke_width=w),
                Line([hi, bot, 0], [hi - ear, bot, 0], stroke_color=c, stroke_width=w),
            )
            return brk

        win_tag = mono("window of 3", 14, INK_DIM)

        # a ValueTracker drives the window centre i across the row (lockstep).
        winT = ValueTracker(1.0)   # centre index, valid range [1, N-2]
        window = make_window(1)
        window.add_updater(lambda m: m.become(
            make_window(int(round(winT.get_value())))))
        win_tag.add_updater(lambda m: m.next_to(window, DOWN, buff=0.14))

        self.add(window, win_tag)
        self.play(FadeIn(window), FadeIn(win_tag), run_time=0.3)

        # the local-feature output track, just below the frames — one sharpened
        # mark per stop. A static reveal (caps at N-2 stops), legible at any scrub.
        out_y = -1.05
        out_track = Line([frame_x(0), out_y, 0], [frame_x(N_FRAMES - 1), out_y, 0],
                         stroke_color=INK_GHOST, stroke_width=1.2)
        out_lab = mono("sharpened local detail", 14, INK_FAINT)
        out_lab.next_to(out_track, DOWN, buff=0.16).align_to(out_track, RIGHT)
        self.play(Create(out_track), FadeIn(out_lab), run_time=0.35)

        # ============================================================
        # B2 — TRANSFORM: slide the window, emit a sharp local mark at each
        #      stop; the magnifier catches a fine edge the far view blurred.
        # ============================================================
        self.next_section("slide")

        # one frame (index 6) carries a FINE EDGE: a tiny crisp notch the broad
        # attention smeared flat. Mark the smear faintly inside it now.
        edge_i = 6
        smear = Line([frame_x(edge_i) - 0.14, FRAME_Y, 0],
                     [frame_x(edge_i) + 0.14, FRAME_Y, 0],
                     stroke_color=INK_FAINT, stroke_width=2.0).set_opacity(0.4)
        self.play(Create(smear), run_time=0.25)

        out_marks = VGroup()
        # heights of the local-feature ticks; the edge frame yields a tall, sharp
        # one — the detail only the magnifier finds.
        heights = [0.30, 0.26, 0.34, 0.28, 0.30, 0.66, 0.30][:N_FRAMES - 2]

        def emit_at(stop_i, h, accent=False):
            x = frame_x(stop_i)
            c = WHITE if accent else INK
            w = 4.0 if accent else 2.6
            tick = Line([x, out_y, 0], [x, out_y - h, 0], stroke_color=c, stroke_width=w)
            dot = Dot([x, out_y - h, 0], radius=0.045, color=c)
            return VGroup(tick, dot)

        # slide stop by stop; at the edge frame the emitted mark is the tall #fff
        # accent and a magnifier loupe pops to show the caught detail.
        n_stops = N_FRAMES - 2
        for k in range(n_stops):
            stop_i = k + 1
            accent = (stop_i == edge_i)
            self.play(winT.animate.set_value(stop_i), run_time=0.40, rate_func=smooth)
            mark = emit_at(stop_i, heights[k], accent=accent)
            out_marks.add(mark)
            if accent:
                loupe = Circle(radius=0.34, stroke_color=WHITE, stroke_width=2.4)
                loupe.move_to([frame_x(edge_i), FRAME_Y, 0])
                sharp = Line([frame_x(edge_i) - 0.10, FRAME_Y - 0.10, 0],
                             [frame_x(edge_i) + 0.10, FRAME_Y + 0.10, 0],
                             stroke_color=WHITE, stroke_width=3.0)
                self.play(Create(mark), Create(loupe), run_time=0.4)
                self.play(smear.animate.set_opacity(0.0), Create(sharp), run_time=0.3)
                caught = mono("caught the fine edge the far view blurred", 14, INK_DIM)
                caught.next_to(loupe, UP, buff=0.40)
                self.play(FadeIn(caught, shift=UP * 0.08), run_time=0.35)
                self.wait(0.4)
            else:
                self.play(Create(mark), run_time=0.22)

        winT.set_value(edge_i)  # park the window on the showpiece frame
        self.add(out_marks)

        # ============================================================
        # B3 — OVERLAY both lenses on one frame: far beam + near bracket
        #      feeding the same output.
        # ============================================================
        self.next_section("overlay")

        window.clear_updaters()
        win_tag.clear_updaters()
        self.play(FadeOut(sub), FadeOut(caught), run_time=0.25)

        both = mono("on one frame, both lenses feed one output", 17, INK_FAINT)
        both.move_to([0, -2.05, 0])
        self.play(FadeIn(both, shift=UP * 0.08), run_time=0.3)

        # brighten the far beam reaching the query frame, alongside the near
        # bracket already there — both pointing at the edge frame's output.
        self.play(far_view.animate.set_opacity(0.6),
                  Indicate(window, scale_factor=1.05, color=INK), run_time=0.55)
        self.wait(0.4)

        # ============================================================
        # B4 — NAME IT + POSTER HOLD.
        # ============================================================
        self.next_section("name")

        payoff = serif("two lenses", 56, WHITE).move_to([0, -2.78, 0])
        payoff_g = glow(payoff)
        sub2 = mono("attention reaches  ·  convolution magnifies", 18, INK_DIM)
        sub2.next_to(payoff, DOWN, buff=0.20)
        self.play(FadeOut(both), run_time=0.2)
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  Flash([0, -2.78, 0], color=WHITE, line_length=0.18, num_lines=12,
                        flash_radius=1.2, time_width=0.4), run_time=0.5)
        self.play(FadeIn(sub2, shift=UP * 0.08), run_time=0.4)

        self.wait(0.7)
