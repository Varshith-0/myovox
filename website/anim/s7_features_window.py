# S07 — Windows (features, part 1).
# We slice the continuous EMG into tiny overlapping 25 ms windows, hopping every
# 20 ms (5 ms overlap), giving a steady 50 snapshots / second.
# Ground truth: 25 ms window (125 samples @ 5 kHz), 20 ms hop (100 samples),
# 5 ms overlap, 50 fps, 3 s sentence ~= 150 frames. (Explanation Section 4.1-4.2.)
#
# Beat sheet (clip_T ~= 12.0s): one self.next_section() per spoken sentence.
#   1 PUZZLE   endless stream of traces — you can't compare an endless stream.
#   2 NORMALIZE every trace onto one shared loudness band.
#   3 SLIDE     a 25 ms window slides + snapshots; tally climbs.
#   4 OVERLAP   lens proves 20 ms hop -> bright white 5 ms overlap sliver.
#   5 DENSIFY   sparse ticks -> full metronome; one white sweep; "50 / second".
#   6 PUNCHLINE bottom strip becomes the glowing 50 snapshots / second.
from manim import *
from emg_style import *
import numpy as np


def trace(x0, x1, y, amp, n=320, freq=2.0, phase=0.0, jag=0.0):
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


class Windows(Scene):
    def construct(self):
        seed()

        # ---- canvas geometry --------------------------------------------
        X0, X1 = -6.4, 6.4          # full-width signal span
        N_TR = 7                    # representative traces (subset of 31)
        BAND = 0.17                 # common amplitude band after normalization
        top, bot = 2.45, 0.25       # trace stack spans top..bot
        ys = np.linspace(top, bot, N_TR)
        axis_y = -1.55              # full-width frame ruler
        win_y = (top + bot) / 2

        # =================================================================
        # BEAT 1 — PUZZLE (~2.25s): the endless stream just sits there. No
        #          mechanism. Let the narration name the tension.
        # =================================================================
        self.next_section("puzzle")

        raw_amps = [0.27, 0.12, 0.31, 0.16, 0.23, 0.13, 0.28]
        traces = VGroup()
        for i, y in enumerate(ys):
            tr = trace(X0, X1, y, raw_amps[i], freq=1.6 + 0.5 * i,
                       phase=i * 1.3, jag=0.05)
            tr.set_stroke(INK, width=1.7, opacity=0.9)
            traces.add(tr)

        # persistent TOP context strip — ties back to S06.
        ctx_tag = mono("31 channels   ·   5,000 readings / second", 22, INK_FAINT)
        ctx_tag.move_to([0, 3.42, 0]).align_to([X0, 0, 0], LEFT)
        cap_rule = Line([X0, 3.0, 0], [X1, 3.0, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2)

        # the unsolved problem, named under the stream.
        puzzle = mono("an endless stream — you can't compare endlessness", 20,
                      INK_DIM)
        puzzle.move_to([0, -3.0, 0])

        self.play(LaggedStartMap(Create, traces, lag_ratio=0.06, run_time=0.95),
                  FadeIn(cap_rule, run_time=0.6),
                  Write(ctx_tag, run_time=0.8))
        self.play(FadeIn(puzzle, shift=UP * 0.08), run_time=0.45)
        self.wait(0.85)

        # =================================================================
        # BEAT 2 — NORMALIZE (~1.96s): every sensor onto one shared band.
        #          Dim the context tag so the band is the sole focus.
        # =================================================================
        self.next_section("normalize")

        band_top = VGroup()
        band_bot = VGroup()
        for y in ys:
            band_top.add(DashedLine([X0, y + BAND, 0], [X1, y + BAND, 0],
                                    stroke_color=INK_GHOST, stroke_width=1,
                                    dash_length=0.09))
            band_bot.add(DashedLine([X0, y - BAND, 0], [X1, y - BAND, 0],
                                    stroke_color=INK_GHOST, stroke_width=1,
                                    dash_length=0.09))
        norm = VGroup()
        for i, y in enumerate(ys):
            tr = trace(X0, X1, y, BAND, freq=1.6 + 0.5 * i,
                       phase=i * 1.3, jag=0.03)
            tr.set_stroke(INK, width=1.7, opacity=0.9)
            norm.add(tr)

        scale_note = mono("drawn at one scale, to compare", 19, INK).move_to([0, -3.0, 0])

        self.play(FadeOut(puzzle, shift=DOWN * 0.08),
                  ctx_tag.animate.set_opacity(0.35),
                  FadeIn(band_top), FadeIn(band_bot), run_time=0.55)
        self.play(Transform(traces, norm), run_time=0.75)
        self.play(Indicate(VGroup(band_top, band_bot), color=INK,
                           scale_factor=1.0),
                  FadeIn(scale_note, shift=UP * 0.06), run_time=0.35)
        self.play(FadeOut(band_top), FadeOut(band_bot),
                  FadeOut(scale_note), run_time=0.3)

        # =================================================================
        # BEAT 3 — SLIDE & SNAP (~1.93s): the 25 ms window slides; tally climbs.
        # =================================================================
        self.next_section("slide")

        axis = Line([X0, axis_y, 0], [X1, axis_y, 0],
                    stroke_color=INK_GHOST, stroke_width=2)

        win_w = 1.12                 # 25 ms wide
        hop = win_w * 20.0 / 25.0    # 20 ms hop -> overlap = 5 ms
        steps = 6                    # snapshots of the sliding window
        win_h = (top - bot) + 2 * BAND + 0.4

        win = Rectangle(width=win_w, height=win_h)
        win.set_stroke("#ffffff", width=1.8, opacity=0.9)
        win.set_fill(INK, opacity=0.08)
        win.move_to([X0 + win_w / 2, win_y, 0])
        win_lab = mono("25 ms", 20, INK).next_to(win, DOWN, buff=0.16)
        win_lab.add_updater(lambda m: m.next_to(win, DOWN, buff=0.16))

        # live snapshot tally in the BOTTOM strip (fades with the lens beat).
        snaps = ValueTracker(0)
        snap_cnt = counter(snaps, fmt=lambda v: str(round(v)), s=52, c=INK,
                           at=[1.0, -3.05, 0])
        snap_lab = mono("snapshots", 18, INK_FAINT)
        snap_lab.add_updater(lambda m: m.next_to(snap_cnt, LEFT, buff=0.28,
                                                 aligned_edge=DOWN))
        snap_lab.next_to(snap_cnt, LEFT, buff=0.28, aligned_edge=DOWN)

        self.play(Create(axis), FadeIn(win), FadeIn(win_lab), run_time=0.45)
        self.add(snap_cnt, snap_lab)

        drop = always_redraw(lambda: DashedLine(
            [win.get_center()[0], win_y - win_h / 2 - 0.46, 0],
            [win.get_center()[0], axis_y + 0.22, 0],
            stroke_color=INK_FAINT, stroke_width=1.2, dash_length=0.1))
        self.add(drop)

        def mk_tick(cx):
            return Line([cx, axis_y - 0.2, 0], [cx, axis_y + 0.2, 0],
                        stroke_color=INK, stroke_width=2.6)

        ticks = VGroup()
        t0 = mk_tick(X0 + win_w / 2)
        self.play(Create(t0), snaps.animate.set_value(1),
                  Flash(t0.get_top(), color="#ffffff", line_length=0.1,
                        num_lines=8, flash_radius=0.22),
                  run_time=0.22)
        ticks.add(t0)
        for k in range(1, steps):
            cx = X0 + win_w / 2 + k * hop
            tick = mk_tick(cx)
            self.play(win.animate.move_to([cx, win_y, 0]),
                      Create(tick), snaps.animate.set_value(k + 1),
                      Flash(tick.get_top(), color="#ffffff", line_length=0.1,
                            num_lines=8, flash_radius=0.22),
                      run_time=0.18, rate_func=smooth)
            ticks.add(tick)

        win_lab.clear_updaters()
        self.remove(drop)
        self.play(FadeOut(win), FadeOut(win_lab), run_time=0.25)

        # =================================================================
        # BEAT 4 — OVERLAP (~2.72s): the lens proof of the 5 ms overlap.
        #          Dim the stream + tally so the white sliver is the sole focus.
        # =================================================================
        self.next_section("overlap")

        self.play(traces.animate.set_stroke(opacity=0.22),
                  ticks.animate.set_stroke(opacity=0.3),
                  axis.animate.set_stroke(opacity=0.5),
                  snap_cnt.animate.set_opacity(0.0),
                  snap_lab.animate.set_opacity(0.0), run_time=0.32)
        snap_cnt.clear_updaters()
        snap_lab.clear_updaters()
        self.remove(snap_cnt, snap_lab)

        zy = -0.2                    # clean center-low lane for the lens
        zh = 1.0
        ZS = 3.0                     # zoom factor for the inset geometry
        zw = win_w * ZS              # window width in the inset
        zhop = hop * ZS              # hop in the inset
        cx0 = -zhop / 2
        cx1 = +zhop / 2

        def zwin(cx, fill, stroke, sw):
            r = Rectangle(width=zw, height=zh).move_to([cx, zy, 0])
            r.set_stroke(stroke, width=sw, opacity=0.95)
            r.set_fill(INK, opacity=fill)
            return r

        zoom_tag = mono("zoom in", 16, INK_FAINT)
        zoom_tag.move_to([cx0 - zw / 2 - 0.1, zy + zh / 2 + 0.62, 0])
        zoom_pin = DashedLine([cx0 - zw / 2 + 0.1, zy - zh / 2, 0],
                              [cx0 - zw / 2 + 0.1, axis_y + 0.2, 0],
                              stroke_color=INK_GHOST, stroke_width=1,
                              dash_length=0.08)

        a = zwin(cx0, 0.12, "#ffffff", 1.9)
        b = zwin(cx1, 0.05, INK_DIM, 1.6)
        a_lab = mono("window", 18, INK).next_to(a, UP, buff=0.14)
        b_lab = mono("next window", 18, INK_DIM).next_to(b, UP, buff=0.14)

        self.play(FadeIn(a, shift=UP * 0.1), FadeIn(a_lab),
                  FadeIn(zoom_tag), Create(zoom_pin), run_time=0.32)
        self.play(FadeIn(b, shift=RIGHT * 0.12), FadeIn(b_lab), run_time=0.3)

        # hop arrow between the two window LEFT edges (= 20 ms step)
        hy = zy + zh / 2 + 0.34
        hop_arrow = DoubleArrow([cx0 - zw / 2, hy, 0], [cx1 - zw / 2, hy, 0],
                                stroke_color=INK, buff=0,
                                tip_length=0.16, stroke_width=2.4)
        hop_brace = mono("hop 20 ms", 17, INK_DIM).next_to(hop_arrow, UP,
                                                           buff=0.06)
        self.play(GrowFromCenter(hop_arrow), FadeIn(hop_brace), run_time=0.35)

        # overlap region = 5 ms (intersection of a and b) — pure white sliver.
        ov_l = cx1 - zw / 2
        ov_r = cx0 + zw / 2
        ov = Rectangle(width=ov_r - ov_l, height=zh)
        ov.move_to([(ov_l + ov_r) / 2, zy, 0])
        ov.set_stroke(width=0).set_fill("#ffffff", opacity=0.42)
        ov_lab = mono("overlap 5 ms", 19, INK)
        ov_lab.next_to(ov, DOWN, buff=0.18)
        ov_pin = Line(ov.get_bottom(), ov_lab.get_top(),
                      stroke_color=INK, stroke_width=1.2)

        # the inequality writes in the BOTTOM strip EXACTLY as overlap flashes.
        take = mono("25 ms wide   >   20 ms step    →    snapshots overlap",
                    22, INK_DIM)
        take.move_to([0, -3.0, 0])

        self.play(FadeIn(ov),
                  Flash(ov.get_center(), color="#ffffff", line_length=0.2,
                        num_lines=14, flash_radius=0.55),
                  FadeIn(take, shift=UP * 0.06), run_time=0.7)
        self.play(Create(ov_pin), Write(ov_lab), run_time=0.35)
        self.wait(0.1)

        lens_grp = VGroup(a, b, a_lab, b_lab, ov, ov_lab, ov_pin,
                          hop_arrow, hop_brace, zoom_tag, zoom_pin)
        self.play(FadeOut(lens_grp),
                  FadeOut(take, shift=DOWN * 0.1),
                  traces.animate.set_stroke(opacity=0.6), run_time=0.4)

        # =================================================================
        # BEAT 5 — DENSIFY (~1.49s): sparse ticks -> full metronome; one white
        #          sweep; the "50 / second" echo lands in the top strip NOW.
        # =================================================================
        self.next_section("densify")

        dense = VGroup()
        gx = X0 + win_w / 2
        while gx <= X1 - 0.02:
            dense.add(Line([gx, axis_y - 0.15, 0], [gx, axis_y + 0.15, 0],
                           stroke_color=INK, stroke_width=1.8))
            gx += hop
        self.play(FadeOut(ticks),
                  axis.animate.set_stroke(opacity=0.85),
                  LaggedStart(*[Create(d) for d in dense], lag_ratio=0.02),
                  run_time=0.55)

        sweep_t = ValueTracker(0)
        sweep = always_redraw(lambda: Line(
            [X0 + (X1 - X0) * sweep_t.get_value(), axis_y - 0.24, 0],
            [X0 + (X1 - X0) * sweep_t.get_value(), axis_y + 0.24, 0],
            stroke_color="#ffffff", stroke_width=3.5))
        self.add(sweep)
        self.play(sweep_t.animate.set_value(1), run_time=0.5,
                  rate_func=linear)
        self.remove(sweep)

        # top strip's right end gains the echo "→ 50 / second" ON this beat.
        ctx_echo = mono("→ 50 / second", 19, INK_DIM)
        ctx_echo.move_to([0, 3.42, 0]).align_to([X1, 0, 0], RIGHT)
        self.play(FadeIn(ctx_echo, shift=LEFT * 0.1), run_time=0.32)
        self.wait(0.12)

        # =================================================================
        # BEAT 6 — PUNCHLINE (~1.63s): bottom strip becomes the glowing 50.
        # =================================================================
        self.next_section("punchline")

        fps_t = ValueTracker(0)
        big = counter(fps_t, fmt=lambda v: str(round(v)), s=86, c=INK,
                      at=[-1.4, -3.0, 0])
        unit = mono("snapshots / second", 26, INK_DIM)
        unit.add_updater(lambda m: m.next_to(big, RIGHT, buff=0.3,
                                             aligned_edge=DOWN))
        unit.next_to(big, RIGHT, buff=0.3, aligned_edge=DOWN)
        self.add(big, unit)
        self.play(fps_t.animate.set_value(50), run_time=0.6,
                  rate_func=rush_into)
        big.clear_updaters()
        unit.clear_updaters()

        big_final = num("50", 86).move_to([-1.4, -3.0, 0])
        self.remove(big)
        self.add(glow(big_final))
        self.play(Flash(big_final.get_center(), color="#ffffff",
                        line_length=0.22, num_lines=16, flash_radius=1.0),
                  Indicate(big_final, scale_factor=1.08, color=WHITE),
                  run_time=0.45)

        sub = mono("a 3-second sentence  ≈  150 snapshots", 23, INK_FAINT)
        sub.move_to([0, -3.62, 0])
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.38)

        self.wait(0.3)
