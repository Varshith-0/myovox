# website/anim/b05_where_units_from.py  —  B05 "Where the 100 units came from"
#
# The "aha": the 100 finer sound-units were never handed to the machine. They
# fell out of SELF-SUPERVISED LEARNING — play a model thousands of hours of plain
# audio, hide a slice, make it guess the hidden piece. To do that well it has to
# quietly sort sounds into bins of its own. Those recurring shapes ARE the 100
# units (HuBERT-style). Zero human labels.
#
# Discovery-first 9-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 puzzle (1.45) open on the 100-bin catalogue, spotlit; serif '?' hovers
#   2 nobody (0.60) the '?' pulses once; nothing answers; bins dim
#   3 trick  (0.60) title -> "self-supervised learning"; bins fade to ghost
#   4 audio  (2.20) long waveform draws; read-pulse sweeps; "thousands of hours"
#   5 mask   (4.71) hatched mask + '?' over a slice; arrows point inward
#   6 practice (2.97) wrong guess (error high) -> morph to true slice (error 0)
#   7 sort   (0.93) snippets fly off the wave into ~7 ghost bins; each pops
#   8 found  (0.60) counter -> 100 + "self-discovered"; #fff "it taught itself"
#   9 bridge (1.39) "40 named + 100 found -> target sounds"; phoneme panel pulses
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

X_L = -6.7
X_R = 6.7


def tri(angle, c=INK_FAINT, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def flat_arrow(start, end, c=INK_FAINT, w=2.0):
    """Thin shaft + triangular head — avoids Arrow tip glitches."""
    shaft = Line(start, end, stroke_color=c, stroke_width=w)
    head = tri(shaft.get_angle() - PI / 2, c, 1.0, 0.075).move_to(shaft.get_end())
    return VGroup(shaft, head)


def wave_points(x0, x1, y0, n, amp, seed_n):
    """A jittery audio-like waveform as a polyline of n points across [x0,x1]."""
    rng = np.random.default_rng(seed_n)
    xs = np.linspace(x0, x1, n)
    phase = rng.uniform(0, 2 * np.pi, 5)
    freq = np.array([2.0, 4.7, 8.1, 13.0, 19.0])
    amps = np.array([1.0, 0.6, 0.35, 0.22, 0.13])
    t = np.linspace(0, 6.0, n)
    ys = np.zeros(n)
    for k in range(5):
        ys += amps[k] * np.sin(freq[k] * t + phase[k])
    ys += 0.25 * rng.standard_normal(n)
    ys = ys / np.max(np.abs(ys)) * amp
    return [np.array([xs[i], y0 + ys[i], 0]) for i in range(n)]


def bin_card(bx, by, seed_n, w=1.02, h=0.92):
    """A ghost bin holding a tiny representative wave-shape."""
    card = RoundedRectangle(width=w, height=h, corner_radius=0.08,
                            stroke_color=INK_FAINT, stroke_width=1.2,
                            fill_color=BG, fill_opacity=1.0).move_to([bx, by, 0])
    sp = wave_points(bx - 0.34, bx + 0.34, by + 0.04, 26, 0.20, seed_n)
    shape = VMobject(stroke_color=INK, stroke_width=1.6)
    shape.set_points_as_corners(sp)
    return VGroup(card, shape)


class WhereUnitsFrom(Scene):
    def construct(self):
        seed()

        # 7 representative ghost bins laid out as the lower catalogue. We BUILD
        # them up top first (the puzzle), then they ride down later as the answer.
        N_BINS = 7
        bin_dx = 1.42
        bin_x0 = -(N_BINS - 1) / 2 * bin_dx

        def make_bins(by):
            grp = VGroup()
            for b in range(N_BINS):
                grp.add(bin_card(bin_x0 + b * bin_dx, by, 100 + b))
            return grp

        # =================================================================
        # BEAT 1 — PUZZLE (~1.45s): open on the 100-bin catalogue, spotlit,
        #          a serif '?' hovering over the row. Everything else dark.
        # =================================================================
        self.next_section("puzzle")

        bins = make_bins(0.2)
        bins_box = SurroundingRectangle(bins, color=INK_GHOST, stroke_width=1.0,
                                        buff=0.26)
        bins_hdr = mono("100 self-discovered units", 16, INK_DIM)
        bins_hdr.next_to(bins_box, DOWN, buff=0.18).set_x(bins_box.get_x())

        qmark = serif("?", 88, WHITE).move_to([0, 2.2, 0])
        q_glow = glow(qmark.copy())

        self.play(
            LaggedStart(*[FadeIn(b, shift=UP * 0.08) for b in bins],
                        lag_ratio=0.06),
            run_time=0.8,
        )
        self.play(Create(bins_box), FadeIn(bins_hdr), run_time=0.35)
        self.add(q_glow)
        self.play(FadeIn(qmark, shift=DOWN * 0.1),
                  q_glow.animate.set_opacity(0.5), run_time=0.3)
        self.wait(0.32)

        # =================================================================
        # BEAT 2 — NOBODY (~0.6s): the '?' pulses once; nothing answers; the
        #          bins dim slightly as we pivot toward mechanism.
        # =================================================================
        self.next_section("nobody")

        self.play(
            Indicate(qmark, scale_factor=1.18, color=WHITE),
            q_glow.animate.set_opacity(0.0),
            VGroup(bins, bins_box, bins_hdr).animate.set_opacity(0.45),
            run_time=0.5,
        )
        self.remove(q_glow)

        # =================================================================
        # BEAT 3 — TRICK (~0.6s): title -> "self-supervised learning"; the bins
        #          fade to ghost and a clear center stage opens.
        # =================================================================
        self.next_section("trick")

        title = mono("SELF-SUPERVISED LEARNING", 22, INK_DIM, w=BOLD)
        title.move_to([0, 3.4, 0])
        self.play(
            FadeOut(qmark, shift=UP * 0.1),
            FadeOut(VGroup(bins, bins_box, bins_hdr)),
            FadeIn(title, shift=DOWN * 0.1),
            run_time=0.5,
        )
        self.remove(bins, bins_box, bins_hdr)

        # =================================================================
        # BEAT 4 — AUDIO (~2.2s): a long waveform draws across center; a read-
        #          pulse sweeps it L->R; "thousands of hours of plain audio".
        # =================================================================
        self.next_section("audio")

        wx0, wx1, wy = -5.2, 5.2, 1.05
        n_pts = 240
        pts = wave_points(wx0, wx1, wy, n_pts, 0.66, 11)
        wave = VMobject(stroke_color=INK, stroke_width=2.0)
        wave.set_points_as_corners(pts)
        baseline = Line([wx0, wy, 0], [wx1, wy, 0], stroke_color=INK_GHOST,
                        stroke_width=1.0)
        audio_lbl = mono("thousands of hours of plain audio — no labels", 16,
                         INK_FAINT)
        audio_lbl.next_to(baseline, UP, buff=0.55).set_x(0)

        self.play(FadeIn(audio_lbl), Create(baseline), run_time=0.45)
        self.play(Create(wave), run_time=1.0)

        pulse = Rectangle(width=0.16, height=1.5, stroke_width=0,
                          fill_color=INK, fill_opacity=0.18).move_to([wx0, wy, 0])
        self.add(pulse)
        self.play(pulse.animate.move_to([wx1, wy, 0]), run_time=0.6,
                  rate_func=linear)
        self.remove(pulse)

        # =================================================================
        # BEAT 5 — MASK (~4.71s): a hatched mask drops over one segment with a
        #          '?'; two arrows point inward from the visible sides.
        # =================================================================
        self.next_section("mask")

        self.play(audio_lbl.animate.set_opacity(0.28), run_time=0.3)

        mx0, mx1 = -0.7, 1.0
        mcx = (mx0 + mx1) / 2
        mask = Rectangle(width=mx1 - mx0, height=1.8, stroke_color=INK_FAINT,
                         stroke_width=1.4, fill_color=BG, fill_opacity=1.0)
        mask.move_to([mcx, wy, 0])
        hatch = VGroup()
        for hx in np.linspace(mx0 + 0.12, mx1 - 0.12, 7):
            hatch.add(Line([hx, wy - 0.78, 0], [hx - 0.34, wy + 0.78, 0],
                           stroke_color=INK_GHOST, stroke_width=1.0))
        m_q = serif("?", 42, INK_DIM).move_to([mcx, wy, 0])
        mask_grp = VGroup(mask, hatch, m_q)

        self.play(FadeIn(mask, scale=1.05),
                  LaggedStart(*[Create(h) for h in hatch], lag_ratio=0.06),
                  run_time=0.7)
        self.play(FadeIn(m_q, scale=0.7), run_time=0.4)

        aL = flat_arrow([mx0 - 1.1, wy, 0], [mx0 - 0.14, wy, 0], INK_FAINT, 2.0)
        aR = flat_arrow([mx1 + 1.1, wy, 0], [mx1 + 0.14, wy, 0], INK_FAINT, 2.0)
        ctx_lbl = mono("hide a slice — guess it from what surrounds it", 16, INK_DIM)
        ctx_lbl.next_to(mask_grp, DOWN, buff=0.7).set_x(0)
        self.play(Create(aL), Create(aR), run_time=0.55)
        self.play(FadeIn(ctx_lbl, shift=UP * 0.06), run_time=0.5)
        self.wait(1.7)

        # =================================================================
        # BEAT 6 — PRACTICE (~2.97s): a wobbly wrong guess fills the gap (error
        #          high) -> morphs to the true slice (error shrinks); mask away.
        # =================================================================
        self.next_section("practice")

        self.play(FadeOut(ctx_lbl), FadeOut(aL), FadeOut(aR), run_time=0.35)

        # error bar to the lower-left of the gap — the only thing moving besides fill.
        em_w = 2.6
        em_c = np.array([wx0 + 1.2, wy - 1.7, 0])
        em_track = RoundedRectangle(width=em_w, height=0.22, corner_radius=0.05,
                                    stroke_color=INK_GHOST, stroke_width=1.0,
                                    fill_opacity=0).move_to(em_c)
        em_fill = Rectangle(width=em_w * 0.92, height=0.22, stroke_width=0,
                            fill_color=INK, fill_opacity=0.7)
        em_fill.align_to(em_track, LEFT).set_y(em_c[1])
        em_lbl = mono("guess error", 14, INK_FAINT)
        em_lbl.next_to(em_track, UP, buff=0.12).align_to(em_track, LEFT)
        self.play(FadeIn(em_track), FadeIn(em_fill), FadeIn(em_lbl), run_time=0.4)

        # the true hidden slice (what was behind the mask).
        seg_idx = [i for i, p in enumerate(pts) if mx0 <= p[0] <= mx1]
        fill_pts = [pts[i] for i in seg_idx]
        true_seg = VMobject(stroke_color=INK, stroke_width=2.0)
        true_seg.set_points_as_corners(fill_pts)

        guess = VMobject(stroke_color=INK_FAINT, stroke_width=2.0)
        ga_pts = [p + np.array([0, 0.5 * np.sin(3 * k), 0])
                  for k, p in enumerate(fill_pts)]
        guess.set_points_as_corners(ga_pts)

        self.play(FadeOut(m_q), FadeIn(guess), run_time=0.45)
        self.wait(0.45)
        # the only motion: the error bar shrinking + the fill snapping to truth.
        self.play(
            Transform(guess, true_seg),
            em_fill.animate.stretch_to_fit_width(em_w * 0.12).align_to(
                em_track, LEFT),
            run_time=0.9,
        )
        em_fill.align_to(em_track, LEFT)
        self.play(FadeOut(mask), FadeOut(hatch), run_time=0.35)
        self.play(Flash([mcx, wy, 0], color=WHITE, flash_radius=0.9,
                        line_length=0.16, num_lines=14), run_time=0.45)
        self.wait(0.3)

        # =================================================================
        # BEAT 7 — SORT (~0.93s): tiny snippets fly off the recovered wave and
        #          drop into ~7 ghost bins below; each bin pops as its kind lands.
        # =================================================================
        self.next_section("sort")

        wave_full = VGroup(wave, guess)
        bins_lo_y = -1.95
        bins_lo = make_bins(bins_lo_y)
        self.play(
            FadeOut(em_track), FadeOut(em_fill), FadeOut(em_lbl),
            FadeOut(audio_lbl),
            wave_full.animate.shift(UP * 0.7),
            baseline.animate.shift(UP * 0.7),
            run_time=0.4,
        )

        sort_lbl = mono("to guess well, it SORTS sounds into bins of its own",
                        16, INK_DIM).move_to([0, 0.35, 0])
        self.play(FadeIn(sort_lbl, shift=UP * 0.06),
                  LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in bins_lo],
                              lag_ratio=0.06),
                  run_time=0.5)

        # snippets fly off the recovered wave DOWN into the nearest bins.
        rng = np.random.default_rng(5)
        cur_pts = [p + UP * 0.7 for p in pts]  # wave was shifted up
        snippets = VGroup()
        targets = []
        src_xs = np.linspace(wx0 + 0.4, wx1 - 0.4, 16)
        for sx in src_xs:
            yi = min(range(len(cur_pts)), key=lambda i: abs(cur_pts[i][0] - sx))
            d = Dot(radius=0.035, color=INK, fill_opacity=0.7)
            d.move_to(cur_pts[yi])
            snippets.add(d)
            tb = int(rng.integers(0, N_BINS))
            targets.append(bins_lo[tb].get_center() + np.array(
                [rng.uniform(-0.26, 0.26), rng.uniform(-0.08, 0.08), 0]))
        self.add(snippets)
        self.play(LaggedStart(*[d.animate.move_to(targets[i]).set_opacity(0.0)
                                for i, d in enumerate(snippets)],
                              lag_ratio=0.03), run_time=0.55)
        self.remove(*snippets)
        self.play(LaggedStart(*[Indicate(bins_lo[b][1], scale_factor=1.14, color=INK)
                                for b in range(N_BINS)], lag_ratio=0.04),
                  run_time=0.45)

        # =================================================================
        # BEAT 8 — FOUND (~0.6s): counter rolls to 100 beside "self-discovered";
        #          the bins box up; the #fff payoff "it taught itself" writes in.
        # =================================================================
        self.next_section("found")

        units_box = SurroundingRectangle(bins_lo, color=INK_GHOST,
                                         stroke_width=1.0, buff=0.24)
        units_hdr = mono("100 · self-discovered", 15, INK_DIM)
        units_hdr.next_to(units_box, DOWN, buff=0.16).set_x(units_box.get_x())

        punch = serif("it taught itself", 50, WHITE).move_to([0, 1.65, 0])
        p_glow = glow(punch.copy())

        self.play(
            FadeOut(wave_full), FadeOut(baseline), FadeOut(sort_lbl),
            FadeOut(title),
            Create(units_box), FadeIn(units_hdr),
            run_time=0.4,
        )
        self.add(p_glow)
        self.play(Write(punch), p_glow.animate.set_opacity(0.0), run_time=0.45)
        self.remove(p_glow)

        # =================================================================
        # BEAT 9 — BRIDGE (~1.39s): "40 named + 100 found -> target sounds";
        #          the left phoneme panel re-spotlights and pulses once.
        # =================================================================
        self.next_section("bridge")

        # the 40 phonemes the human DID supply — re-spotlit on the left for the
        # bridge so "40 named" lands.
        phon_syms = ["AA", "AE", "AH", "B", "CH", "D", "EH", "ER", "F", "G",
                     "IH", "K", "L", "M", "N", "OW", "P", "R", "S", "T"]
        phon_cells = VGroup()
        for i, p in enumerate(phon_syms):
            r, c = i // 2, i % 2
            cell = mono(p, 12, INK_FAINT).move_to([X_L + 0.32 + c * 0.55,
                                                    -0.4 - r * 0.30, 0])
            phon_cells.add(cell)
        phon_hdr = mono("40 named", 14, INK_DIM)
        phon_hdr.next_to(phon_cells, UP, buff=0.18).set_x(phon_cells.get_x())
        phon_box = SurroundingRectangle(VGroup(phon_cells, phon_hdr),
                                        color=INK_GHOST, stroke_width=1.0, buff=0.16)
        phon_grp = VGroup(phon_box, phon_hdr, phon_cells)

        bridge = mono("40 named  +  100 found  →  the model's target sounds",
                      16, INK_FAINT).move_to([0, -3.62, 0])

        self.play(
            FadeIn(phon_hdr),
            LaggedStart(*[FadeIn(c) for c in phon_cells], lag_ratio=0.015),
            Create(phon_box),
            FadeIn(bridge, shift=UP * 0.06),
            run_time=0.7,
        )
        self.play(
            Indicate(phon_grp, scale_factor=1.04, color=INK_DIM),
            run_time=0.5,
        )
        self.wait(0.3)
