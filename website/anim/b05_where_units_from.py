# website/anim/b05_where_units_from.py  —  B05 "Sounds nobody named"
#
# The "aha": the 100 finer sound-units were never handed to the machine. They
# fell out of SELF-SUPERVISED LEARNING — play a model thousands of hours of plain
# audio, hide a slice, make it guess the hidden piece. To do that well it has to
# quietly sort sounds into categories of its own. Those recurring shapes ARE the
# 100 units (HuBERT-style). Zero human labels.
#
# Metaphor: fill-in-the-blank — guessing the missing word teaches you the language.
#
# Three-zone full-canvas composition (pose -> build -> transform -> name):
#   LEFT rail  (x ~ -6.2): the 40 phonemes from the prior card, settled & dim —
#                  the labels a human DID supply. Stays as the anchor/contrast.
#   CENTER     (y ~ +0.2): a long waveform scrolls; a grey mask-box blanks a short
#                  segment; "?" + arrows from the visible sides point at the gap.
#                  The model proposes the missing slice; an error meter (reused
#                  downhill idiom) pulses and SHRINKS as the fill snaps in.
#   LOWER band (y ~ -1.9): tiny snippets fly in and settle into ~7 representative
#                  ghost bins, each tagged "one of 100"; a counter reads 100; a
#                  blank ∅ parks at the end as "nothing new yet".
#   NAME       serif #fff "it taught itself" + mono "no human labels"; the 100
#                  units take their place beside the 40 phonemes.
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


class WhereUnitsFrom(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B0 — POSE: the 40 phonemes from the prior card, settled & dim on
        #      the LEFT as a column. These are the labels a human supplied.
        # =================================================================
        self.next_section("pose")

        title = mono("WHERE THE 100 UNITS CAME FROM", 24, INK_DIM, w=BOLD)
        title.move_to([0, 3.4, 0])
        sub = mono("nobody handed the machine a list", 16, INK_FAINT)
        sub.next_to(title, DOWN, buff=0.16)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.4)
        self.play(FadeIn(sub), run_time=0.3)

        # the prior card's 40 phonemes — a tidy dim grid hugging the left edge.
        phon_syms = ["AA", "AE", "AH", "B", "CH", "D", "EH", "ER", "F", "G",
                     "IH", "K", "L", "M", "N", "OW", "P", "R", "S", "T"]
        phon_cells = VGroup()
        for i, p in enumerate(phon_syms):
            r, c = i // 2, i % 2
            cell = mono(p, 13, INK_FAINT).move_to([X_L + 0.35 + c * 0.62,
                                                    1.55 - r * 0.32, 0])
            phon_cells.add(cell)
        phon_hdr = mono("40 phonemes", 15, INK_DIM)
        phon_hdr.next_to(phon_cells, UP, buff=0.22).set_x(phon_cells.get_x())
        phon_tag = mono("named by humans", 13, INK_GHOST)
        phon_tag.next_to(phon_cells, DOWN, buff=0.20).set_x(phon_cells.get_x())
        phon_box = SurroundingRectangle(VGroup(phon_cells, phon_hdr, phon_tag),
                                        color=INK_GHOST, stroke_width=1.0, buff=0.18)
        phon_grp = VGroup(phon_box, phon_hdr, phon_cells, phon_tag)

        self.play(FadeIn(phon_hdr),
                  LaggedStart(*[FadeIn(c) for c in phon_cells], lag_ratio=0.02),
                  run_time=0.6)
        self.play(Create(phon_box), FadeIn(phon_tag), run_time=0.35)

        # =================================================================
        # B1 — BUILD: a long waveform; a mask-box blanks a slice; "?" + arrows
        #      from the visible sides point at the gap. The fill-in-the-blank.
        # =================================================================
        self.next_section("mask")

        wx0, wx1, wy = -3.3, 6.3, 0.95
        n_pts = 220
        pts = wave_points(wx0, wx1, wy, n_pts, 0.62, 11)
        wave = VMobject(stroke_color=INK, stroke_width=2.0)
        wave.set_points_as_corners(pts)
        baseline = Line([wx0, wy, 0], [wx1, wy, 0], stroke_color=INK_GHOST,
                        stroke_width=1.0)
        audio_lbl = mono("thousands of hours of plain audio", 16, INK_FAINT)
        audio_lbl.next_to(VGroup(baseline), UP, buff=0.42).set_x((wx0 + wx1) / 2)

        self.play(FadeIn(audio_lbl), Create(baseline), run_time=0.35)
        self.play(Create(wave), run_time=0.9)

        # a faint read pulse sweeps the stream — audio arriving.
        pulse = Rectangle(width=0.16, height=1.4, stroke_width=0,
                          fill_color=INK, fill_opacity=0.16).move_to([wx0, wy, 0])
        self.add(pulse)
        self.play(pulse.animate.move_to([wx1, wy, 0]), run_time=0.5,
                  rate_func=linear)
        self.remove(pulse)

        # the mask box: blank a short central segment.
        mx0, mx1 = 0.9, 2.5
        mask = Rectangle(width=mx1 - mx0, height=1.7, stroke_color=INK_FAINT,
                         stroke_width=1.4, fill_color=BG, fill_opacity=1.0)
        mask.move_to([(mx0 + mx1) / 2, wy, 0])
        # hatch the mask so it reads as "hidden".
        hatch = VGroup()
        for hx in np.linspace(mx0 + 0.12, mx1 - 0.12, 7):
            hatch.add(Line([hx, wy - 0.75, 0], [hx - 0.34, wy + 0.75, 0],
                           stroke_color=INK_GHOST, stroke_width=1.0))
        qmark = serif("?", 40, INK_DIM).move_to([(mx0 + mx1) / 2, wy, 0])
        mask_grp = VGroup(mask, hatch, qmark)

        self.play(FadeIn(mask, scale=1.05),
                  LaggedStart(*[Create(h) for h in hatch], lag_ratio=0.06),
                  run_time=0.5)
        self.play(FadeIn(qmark, scale=0.7), run_time=0.3)

        # arrows from visible sides point INTO the gap — "guess from context".
        aL = flat_arrow([mx0 - 1.0, wy, 0], [mx0 - 0.16, wy, 0], INK_FAINT, 2.0)
        aR = flat_arrow([mx1 + 1.0, wy, 0], [mx1 + 0.16, wy, 0], INK_FAINT, 2.0)
        ctx_lbl = mono("predict the hidden slice from what surrounds it", 15, INK_DIM)
        ctx_lbl.next_to(mask_grp, DOWN, buff=0.55).set_x((mx0 + mx1) / 2)
        if ctx_lbl.get_left()[0] < -2.0:
            ctx_lbl.set_x(1.5)
        self.play(GrowArrow(aL[0]) if False else Create(aL),
                  Create(aR), FadeIn(ctx_lbl), run_time=0.45)

        # =================================================================
        # B2 — TRANSFORM: the model proposes the missing slice; an error meter
        #      pulses + SHRINKS (downhill idiom) as the fill snaps into place.
        # =================================================================
        self.next_section("predict")

        # error meter sits below-left of the wave, a shrinking bar.
        em_w = 2.4
        em_c = np.array([wx0 + 1.05, wy - 1.55, 0])
        em_track = RoundedRectangle(width=em_w, height=0.20, corner_radius=0.05,
                                    stroke_color=INK_GHOST, stroke_width=1.0,
                                    fill_opacity=0).move_to(em_c)
        em_fill = Rectangle(width=em_w * 0.92, height=0.20, stroke_width=0,
                            fill_color=INK, fill_opacity=0.7)
        em_fill.align_to(em_track, LEFT).set_y(em_c[1])
        em_lbl = mono("prediction error", 14, INK_FAINT)
        em_lbl.next_to(em_track, UP, buff=0.12).align_to(em_track, LEFT)
        self.play(FadeIn(em_track), FadeIn(em_fill), FadeIn(em_lbl), run_time=0.35)

        # the true hidden slice (what was behind the mask), drawn as the fill.
        seg_idx = [i for i, p in enumerate(pts) if mx0 <= p[0] <= mx1]
        fill_pts = [pts[i] for i in seg_idx]
        true_seg = VMobject(stroke_color=INK, stroke_width=2.0)
        true_seg.set_points_as_corners(fill_pts)

        # a couple of wrong-then-right guesses: meter shrinks each step.
        guess_a = VMobject(stroke_color=INK_FAINT, stroke_width=2.0)
        ga_pts = [p + np.array([0, 0.45 * np.sin(3 * k), 0])
                  for k, p in enumerate(fill_pts)]
        guess_a.set_points_as_corners(ga_pts)

        self.play(FadeOut(qmark), FadeIn(guess_a),
                  em_fill.animate.stretch_to_fit_width(em_w * 0.55).align_to(
                      em_track, LEFT),
                  run_time=0.45)
        self.play(Transform(guess_a, true_seg),
                  em_fill.animate.stretch_to_fit_width(em_w * 0.16).align_to(
                      em_track, LEFT),
                  run_time=0.55)
        em_fill.align_to(em_track, LEFT)

        # fade the mask away — the slice is recovered. One #fff flash to christen.
        flash_pt = np.array([(mx0 + mx1) / 2, wy, 0])
        self.play(FadeOut(mask), FadeOut(hatch), FadeOut(aL), FadeOut(aR),
                  run_time=0.3)
        self.play(Flash(flash_pt, color=WHITE, flash_radius=0.9,
                        line_length=0.16, num_lines=14), run_time=0.45)

        # =================================================================
        # B3 — DISCOVER: many tiny snippets fly in & settle into ~7 ghost bins,
        #      each tagged "one of 100"; a counter reads 100; a blank ∅ parks
        #      at the end as "nothing new yet".
        # =================================================================
        self.next_section("bins")

        # retire the error meter + ctx label, slide the recovered wave up to make
        # room for the lower discovery band.
        wave_full = VGroup(wave, guess_a)
        self.play(FadeOut(em_track), FadeOut(em_fill), FadeOut(em_lbl),
                  FadeOut(ctx_lbl), FadeOut(audio_lbl),
                  wave_full.animate.shift(UP * 0.55),
                  baseline.animate.shift(UP * 0.55),
                  run_time=0.45)

        band_lbl = mono("doing this well forces it to SORT sounds into its own bins",
                        16, INK_DIM).move_to([0, 0.45, 0])
        self.play(FadeIn(band_lbl, shift=UP * 0.08), run_time=0.35)

        # 7 representative ghost bins across the lower band, kept clear of the
        # left-hand phonemes panel (its right edge sits near x = -5.3).
        n_bins = 7
        bin_y = -2.0
        bins = VGroup()
        bin_glyphs = VGroup()
        rng = np.random.default_rng(5)
        bin_x0, bin_dx = -3.5, 1.42
        for b in range(n_bins):
            bx = bin_x0 + b * bin_dx
            card = RoundedRectangle(width=1.05, height=1.0, corner_radius=0.08,
                                    stroke_color=INK_FAINT, stroke_width=1.2,
                                    fill_color=BG, fill_opacity=1.0)
            card.move_to([bx, bin_y, 0])
            # a tiny representative wave-shape inside each bin.
            sp = wave_points(bx - 0.36, bx + 0.36, bin_y + 0.12, 26, 0.20,
                             100 + b)
            shape = VMobject(stroke_color=INK, stroke_width=1.6)
            shape.set_points_as_corners(sp)
            tag = mono("one of 100", 10, INK_GHOST).next_to(card, DOWN, buff=0.10)
            bins.add(VGroup(card, shape))
            bin_glyphs.add(tag)
        bins_grp = VGroup(bins, bin_glyphs)

        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in bins],
                              lag_ratio=0.08), run_time=0.7)

        # tiny snippets fly from along the wave DOWN into the nearest bins.
        snippets = VGroup()
        targets = []
        src_xs = np.linspace(wx0 + 0.4, wx1 - 0.4, 18)
        for sx in src_xs:
            # nearest point on the wave for the y
            yi = min(range(len(pts)), key=lambda i: abs(pts[i][0] - sx))
            d = Dot(radius=0.035, color=INK, fill_opacity=0.7)
            d.move_to(pts[yi] + UP * 0.55)
            snippets.add(d)
            tb = int(rng.integers(0, n_bins))
            targets.append(bins[tb].get_center() + np.array(
                [rng.uniform(-0.28, 0.28), rng.uniform(-0.1, 0.1), 0]))
        self.add(snippets)

        self.play(LaggedStart(*[d.animate.move_to(targets[i]).set_opacity(0.0)
                                for i, d in enumerate(snippets)],
                              lag_ratio=0.03), run_time=0.95)
        self.remove(*snippets)
        # brief pop on each bin's shape as the snippets land.
        self.play(LaggedStart(*[Indicate(bins[b][1], scale_factor=1.12, color=INK)
                                for b in range(n_bins)], lag_ratio=0.05),
                  run_time=0.5)

        # the counter reads 100 (these visible bins are a cap; "+ 93 more").
        cnt = ValueTracker(0)
        cnt_read = counter(cnt, fmt=lambda v: str(int(round(v))), s=64, c=INK,
                           at=[0, bin_y - 1.4, 0])
        cnt_word = mono("self-discovered units", 16, INK_DIM)
        self.add(cnt_read)
        self.play(cnt.animate.set_value(100), run_time=0.7)
        cnt_read.clear_updaters()
        cnt_word.next_to(cnt_read, RIGHT, buff=0.28)
        self.play(FadeIn(cnt_word, shift=RIGHT * 0.1), run_time=0.3)

        # a blank ∅ parks at the end of the row — "nothing new yet".
        blank = serif("∅", 30, INK_FAINT).move_to([X_R - 0.6, bin_y, 0])
        blank_tag = mono("blank", 11, INK_GHOST).next_to(blank, DOWN, buff=0.12)
        self.play(FadeIn(blank, scale=0.7), FadeIn(blank_tag), run_time=0.35)

        # =================================================================
        # B4 — NAME: serif #fff "it taught itself" + "no human labels"; the
        #      100 units take their place beside the 40 phonemes.
        # =================================================================
        self.next_section("name")

        # clear the upper mechanism + the big counter; the boxed bins below carry
        # the "100" message, leaving the centre free for the payoff word.
        self.play(FadeOut(wave_full), FadeOut(baseline), FadeOut(band_lbl),
                  FadeOut(sub),
                  FadeOut(cnt_read), FadeOut(cnt_word),
                  run_time=0.4)

        # the bins read as one boxed catalogue of self-discovered units.
        units_box = SurroundingRectangle(VGroup(bins, bin_glyphs, blank),
                                         color=INK_GHOST, stroke_width=1.0,
                                         buff=0.24)
        units_hdr = mono("100 self-discovered units", 15, INK_DIM)
        units_hdr.next_to(units_box, UP, buff=0.16).set_x(units_box.get_x())
        self.play(Create(units_box), FadeIn(units_hdr), run_time=0.4)

        # the payoff line, center, the single #fff accent.
        punch = serif("it taught itself", 50, WHITE).move_to([0, 1.7, 0])
        punch_sub = mono("no human labels", 20, INK_DIM)
        punch_sub.next_to(punch, DOWN, buff=0.22)
        self.play(Write(punch), run_time=0.6)
        self.play(FadeIn(punch_sub, shift=UP * 0.08), run_time=0.3)
        self.play(Indicate(punch, scale_factor=1.06, color=WHITE), run_time=0.45)

        # a quiet bridge: 40 named + 100 found = the targets, side by side.
        bridge = mono("40 named  +  100 found  →  the model's target sounds",
                      16, INK_FAINT).move_to([0, -3.62, 0])
        self.play(FadeIn(bridge, shift=UP * 0.08),
                  Indicate(phon_grp, scale_factor=1.03, color=INK_DIM),
                  run_time=0.5)

        self.wait(0.6)
