# S07 — Windows (features, part 1).
# We slice the continuous EMG into tiny overlapping 25 ms windows, hopping every
# 20 ms (5 ms overlap), giving a steady 50 frames / second.
# Ground truth: 25 ms window (125 samples @ 5 kHz), 20 ms hop (100 samples),
# 5 ms overlap, 50 fps, 3 s sentence ~= 150 frames. (Explanation §4.1-4.2.)
#
# Full-canvas composition (x in [-7.1,7.1], y in [-4,4]):
#   TOP strip  (y +3.0..+3.6): persistent CONTEXT, ties back to S06.
#   CENTER     (y -1.6..+2.7): the star mechanism (normalize -> slide -> lens).
#   BOTTOM strip(y -2.6..-3.9): running TAKEAWAY (tally -> inequality -> 50 fps).
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
        top, bot = 2.7, 0.4         # trace stack spans top..bot
        ys = np.linspace(top, bot, N_TR)
        axis_y = -1.55              # full-width frame ruler

        # =================================================================
        # BEAT 1 — POSE / continuity: open on the S06 stack, write context.
        # =================================================================
        raw_amps = [0.27, 0.12, 0.31, 0.16, 0.23, 0.13, 0.28]
        traces = VGroup()
        for i, y in enumerate(ys):
            tr = trace(X0, X1, y, raw_amps[i], freq=1.6 + 0.5 * i,
                       phase=i * 1.3, jag=0.05)
            tr.set_stroke(INK, width=1.7, opacity=0.9)
            traces.add(tr)

        # --- persistent TOP context strip (stays up the whole clip) ------
        ctx_tag = mono("31 channels  —  5,000 readings / second", 22, INK_FAINT)
        ctx_tag.move_to([0, 3.42, 0]).align_to([X0, 0, 0], LEFT)
        ctx_cont = mono("↳ from the recording", 17, INK_GHOST)
        ctx_cont.next_to(ctx_tag, RIGHT, buff=0.4, aligned_edge=DOWN)
        cap_rule = Line([X0, 3.0, 0], [X1, 3.0, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2)

        # --- BOTTOM strip seed: empty progress underline at the very edge -
        prog_t = ValueTracker(0)
        prog_base = Line([X0, -3.86, 0], [X1, -3.86, 0],
                         stroke_color=INK_GHOST, stroke_width=1.4)
        prog_fill = always_redraw(lambda: Line(
            [X0, -3.86, 0],
            [X0 + (X1 - X0) * prog_t.get_value(), -3.86, 0],
            stroke_color=INK, stroke_width=3.0))

        self.play(
            LaggedStartMap(Create, traces, lag_ratio=0.06, run_time=0.85),
            FadeIn(cap_rule, run_time=0.6),
            Write(ctx_tag, run_time=0.7),
        )
        self.play(FadeIn(ctx_cont, shift=RIGHT * 0.08),
                  Create(prog_base), run_time=0.4)
        self.add(prog_fill)

        # =================================================================
        # BEAT 2 — NORMALIZE: every sensor onto one shared amplitude band.
        # =================================================================
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

        scale_note = mono("same scale", 18, INK_FAINT)
        scale_note.move_to([X1 - 0.95, top + 0.34, 0])

        self.play(FadeIn(band_top), FadeIn(band_bot), run_time=0.35)
        self.play(Transform(traces, norm), run_time=0.85)
        self.play(Indicate(VGroup(band_top, band_bot), color=INK,
                           scale_factor=1.0),
                  FadeIn(scale_note, shift=DOWN * 0.06), run_time=0.4)
        self.play(FadeOut(band_top), FadeOut(band_bot),
                  FadeOut(scale_note), run_time=0.3)

        # =================================================================
        # BEAT 3 — SLIDE & SNAP: the star transform (full-width ruler).
        # =================================================================
        axis = Line([X0, axis_y, 0], [X1, axis_y, 0],
                    stroke_color=INK_GHOST, stroke_width=2)
        self.play(Create(axis), run_time=0.4)

        # window (25 ms) and hop (20 ms) geometry, drawn to scale ----------
        win_w = 1.12                 # 25 ms wide
        hop = win_w * 20.0 / 25.0    # 20 ms hop -> overlap = 5 ms
        steps = 6                    # snapshots of the sliding window
        win_y = (top + bot) / 2
        win_h = (top - bot) + 2 * BAND + 0.4

        win = Rectangle(width=win_w, height=win_h)
        win.set_stroke("#ffffff", width=1.8, opacity=0.9)
        win.set_fill(INK, opacity=0.08)
        win.move_to([X0 + win_w / 2, win_y, 0])
        # "25 ms" rides in the gap BELOW the window box (between win bottom and
        # the ruler) so it can never climb into the top header band.
        win_lab = mono("25 ms", 20, INK).next_to(win, DOWN, buff=0.16)
        win_lab.add_updater(lambda m: m.next_to(win, DOWN, buff=0.16))

        # a live snapshot tally rises in the BOTTOM strip as the window snaps
        snaps = ValueTracker(0)
        snap_cnt = counter(snaps, fmt=lambda v: str(round(v)), s=52, c=INK,
                           at=[X1 - 0.7, -3.05, 0])
        snap_lab = mono("snapshots", 18, INK_FAINT)
        snap_lab.add_updater(lambda m: m.next_to(snap_cnt, LEFT, buff=0.28,
                                                 aligned_edge=DOWN))
        snap_lab.next_to(snap_cnt, LEFT, buff=0.28, aligned_edge=DOWN)
        self.add(snap_cnt, snap_lab)

        self.play(FadeIn(win), FadeIn(win_lab), run_time=0.45)

        # vertical drop-line from below the "25 ms" tag down to its tick (it
        # starts under the label so the connector never crosses the text) -----
        drop = always_redraw(lambda: DashedLine(
            [win.get_center()[0], -0.62, 0],
            [win.get_center()[0], axis_y + 0.22, 0],
            stroke_color=INK_FAINT, stroke_width=1.2, dash_length=0.1))
        self.add(drop)

        def mk_tick(cx):
            return Line([cx, axis_y - 0.2, 0], [cx, axis_y + 0.2, 0],
                        stroke_color=INK, stroke_width=2.6)

        ticks = VGroup()
        t0 = mk_tick(X0 + win_w / 2)
        self.play(Create(t0), snaps.animate.set_value(1),
                  prog_t.animate.set_value((win_w / 2) / (X1 - X0)),
                  Flash(t0.get_top(), color="#ffffff", line_length=0.1,
                        num_lines=8, flash_radius=0.22),
                  run_time=0.26)
        ticks.add(t0)
        for k in range(1, steps):
            cx = X0 + win_w / 2 + k * hop
            tick = mk_tick(cx)
            self.play(win.animate.move_to([cx, win_y, 0]),
                      Create(tick), snaps.animate.set_value(k + 1),
                      prog_t.animate.set_value((cx - X0) / (X1 - X0)),
                      Flash(tick.get_top(), color="#ffffff", line_length=0.1,
                            num_lines=8, flash_radius=0.22),
                      run_time=0.28, rate_func=smooth)
            ticks.add(tick)

        win_lab.clear_updaters()
        self.remove(drop)
        self.play(FadeOut(win), FadeOut(win_lab), run_time=0.3)

        # dim the context so the lens reads cleanly
        self.play(traces.animate.set_stroke(opacity=0.22),
                  ticks.animate.set_stroke(opacity=0.3),
                  axis.animate.set_stroke(opacity=0.5),
                  snap_cnt.animate.set_opacity(0.0),
                  snap_lab.animate.set_opacity(0.0), run_time=0.4)
        snap_cnt.clear_updaters()
        snap_lab.clear_updaters()
        self.remove(snap_cnt, snap_lab)

        # =================================================================
        # BEAT 4 — ZOOM: the lens proof of the 5 ms overlap (peak #fff).
        # =================================================================
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
        # thin pin-line from the lens back down to the ruler
        zoom_pin = DashedLine([cx0 - zw / 2 + 0.1, zy - zh / 2, 0],
                              [cx0 - zw / 2 + 0.1, axis_y + 0.2, 0],
                              stroke_color=INK_GHOST, stroke_width=1,
                              dash_length=0.08)

        a = zwin(cx0, 0.12, "#ffffff", 1.9)
        b = zwin(cx1, 0.05, INK_DIM, 1.6)
        a_lab = mono("window", 18, INK).next_to(a, UP, buff=0.14)
        b_lab = mono("next window", 18, INK_DIM).next_to(b, UP, buff=0.14)

        self.play(FadeIn(a, shift=UP * 0.1), FadeIn(a_lab),
                  FadeIn(zoom_tag), Create(zoom_pin), run_time=0.4)
        self.play(FadeIn(b, shift=RIGHT * 0.12), FadeIn(b_lab), run_time=0.32)

        # overlap region = 5 ms (intersection of a and b) — pure white sliver
        ov_l = cx1 - zw / 2
        ov_r = cx0 + zw / 2
        ov = Rectangle(width=ov_r - ov_l, height=zh)
        ov.move_to([(ov_l + ov_r) / 2, zy, 0])
        ov.set_stroke(width=0).set_fill("#ffffff", opacity=0.42)
        ov_lab = mono("overlap 5 ms", 19, INK)
        ov_lab.next_to(ov, DOWN, buff=0.18)
        ov_pin = Line(ov.get_bottom(), ov_lab.get_top(),
                      stroke_color=INK, stroke_width=1.2)

        # hop arrow between the two window LEFT edges (= 20 ms step)
        hy = zy + zh / 2 + 0.34
        hop_arrow = DoubleArrow([cx0 - zw / 2, hy, 0], [cx1 - zw / 2, hy, 0],
                                stroke_color=INK, buff=0,
                                tip_length=0.16, stroke_width=2.4)
        hop_brace = mono("hop 20 ms", 17, INK_DIM).next_to(hop_arrow, UP,
                                                           buff=0.06)

        # the BOTTOM strip writes the inequality EXACTLY as overlap flashes
        take = mono("25 ms wide   >   20 ms step    ⇒    slices overlap",
                    22, INK_DIM)
        take.move_to([0, -3.0, 0])

        self.play(GrowFromCenter(hop_arrow), FadeIn(hop_brace), run_time=0.4)
        # synchronized beat: overlap lights + inequality writes together
        self.play(FadeIn(ov),
                  Flash(ov.get_center(), color="#ffffff", line_length=0.2,
                        num_lines=14, flash_radius=0.55),
                  Write(take), run_time=0.6)
        self.play(Create(ov_pin), Write(ov_lab), run_time=0.42)
        self.wait(0.2)

        lens_grp = VGroup(a, b, a_lab, b_lab, ov, ov_lab, ov_pin,
                          hop_arrow, hop_brace, zoom_tag, zoom_pin)
        self.play(FadeOut(lens_grp),
                  FadeOut(take, shift=DOWN * 0.1),
                  traces.animate.set_stroke(opacity=0.9), run_time=0.45)

        # =================================================================
        # BEAT 5 — DENSIFY & NAME IT: sparse ticks -> full-width metronome.
        # =================================================================
        dense = VGroup()
        gx = X0 + win_w / 2
        while gx <= X1 - 0.02:
            dense.add(Line([gx, axis_y - 0.15, 0], [gx, axis_y + 0.15, 0],
                           stroke_color=INK, stroke_width=1.8))
            gx += hop
        self.play(FadeOut(ticks),
                  axis.animate.set_stroke(opacity=0.85),
                  LaggedStartMap(Create, dense, lag_ratio=0.025),
                  run_time=0.7)

        # bright #fff vertical sweep across the finished ruler -------------
        sweep_t = ValueTracker(0)
        sweep = always_redraw(lambda: Line(
            [X0 + (X1 - X0) * sweep_t.get_value(), axis_y - 0.24, 0],
            [X0 + (X1 - X0) * sweep_t.get_value(), axis_y + 0.24, 0],
            stroke_color="#ffffff", stroke_width=3.5))
        self.add(sweep)
        self.play(sweep_t.animate.set_value(1),
                  prog_t.animate.set_value(1.0),
                  run_time=0.6, rate_func=linear)
        self.remove(sweep)

        # top strip's right end gains the echo "→ 50 / second". The old recap
        # continuation must fully clear FIRST (staggered, never overlapping) so
        # the two right-aligned labels can't briefly stack into a mash.
        ctx_echo = mono("→ 50 / second", 19, INK_DIM)
        ctx_echo.move_to([0, 3.42, 0]).align_to([X1, 0, 0], RIGHT)
        self.play(FadeOut(ctx_cont, shift=LEFT * 0.06), run_time=0.28)
        self.remove(ctx_cont)          # ensure it can never re-render later
        self.play(FadeIn(ctx_echo, shift=LEFT * 0.1), run_time=0.32)

        # =================================================================
        # BEAT 6 — PUNCHLINE: bottom strip becomes the 50 fps headline.
        # =================================================================
        fps_t = ValueTracker(0)
        big = counter(fps_t, fmt=lambda v: str(round(v)), s=86, c=INK,
                      at=[-1.15, -3.0, 0])
        unit = mono("frames / second", 26, INK_DIM)
        unit.add_updater(lambda m: m.next_to(big, RIGHT, buff=0.3,
                                             aligned_edge=DOWN))
        unit.next_to(big, RIGHT, buff=0.3, aligned_edge=DOWN)
        self.add(big, unit)
        self.play(fps_t.animate.set_value(50), run_time=0.7,
                  rate_func=rush_into)
        big.clear_updaters()
        unit.clear_updaters()

        big_final = num("50", 86).move_to([-1.15, -3.0, 0])
        self.remove(big)
        self.add(glow(big_final))
        self.play(Flash(big_final.get_center(), color="#ffffff",
                        line_length=0.22, num_lines=16, flash_radius=1.0),
                  run_time=0.45)

        sub = mono("a 3-second sentence  ≈  150 frames", 23, INK_FAINT)
        sub.move_to([0, -3.62, 0])
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.55)

        self.wait(0.6)
