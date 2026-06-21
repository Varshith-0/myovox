# website/anim/s20_knobs.py  — S20 "Two dials" (acoustic scale + blank penalty)
# Strict monochrome. Same sounds can be "ice cream" or "I scream"; two decode
# dials decide which words come out. Land scale near 0.25, blank penalty at 2.0.
#
# Ground truth (§8.3, decode.py):
#   untuned acoustic scale 1.0 -> ~75% WER;  tuned scale ~= 0.25 (Conformer)
#   CTC blank peaks ~0.92 (model is "blank-happy")
#   blank penalty 0 -> 2 moved WER 77.6 -> 60.6 on a slice (single biggest lever)
#
# Canvas: full-bleed.  x in [-7.1,7.1], y in [-4,4].
#   TOP    (y ~ +2.4..+3.6) : homophone context ledger (links to S19 word-map)
#   CENTER (y ~ -2.0..+2.0) : two ENORMOUS dials + a mid blank filmstrip
#   BOTTOM (y ~ -3.4..-2.6) : one full-width live WER meter + punchline
from manim import *
from emg_style import *
import numpy as np

A0, A1 = 210 * DEGREES, -30 * DEGREES  # needle sweep: left -> right
R = 1.25                                # big gauges
cL = LEFT * 3.7 + DOWN * 0.2            # left dial hub
cR = RIGHT * 3.7 + DOWN * 0.2           # right dial hub

# full-width WER meter geometry
WER_Y = -3.15
WER_X0, WER_X1 = -6.0, 6.0


def _ang(f):
    return A0 + float(np.clip(f, 0, 1)) * (A1 - A0)


def gauge_face(center):
    """Static parts of a dial (arc + ticks + hub), centred at `center`."""
    arc = Arc(radius=R, start_angle=A0, angle=(A1 - A0),
              arc_center=center, stroke_color=INK_GHOST, stroke_width=5)
    # faint inner shadow ring for depth
    inner = Arc(radius=R - 0.16, start_angle=A0, angle=(A1 - A0),
                arc_center=center, stroke_color=LINE, stroke_width=2)
    ticks = VGroup()
    for j, f in enumerate(np.linspace(0, 1, 9)):
        ang = _ang(f)
        u = np.array([np.cos(ang), np.sin(ang), 0])
        major = (j % 2 == 0)
        ticks.add(Line(center + R * u, center + (R + (0.16 if major else 0.09)) * u,
                       stroke_color=INK_FAINT if major else INK_GHOST,
                       stroke_width=2.5 if major else 1.5))
    hub = VGroup(
        Circle(radius=0.13, arc_center=center, stroke_color=INK_FAINT,
               stroke_width=2, fill_color=BG, fill_opacity=1),
        Dot(center, radius=0.055, color=INK),
    )
    return VGroup(arc, inner, ticks, hub)


def fill_arc_for(center, tracker, vmin, vmax):
    """A bright arc that fills from the left end up to the needle angle."""
    def make():
        f = (tracker.get_value() - vmin) / (vmax - vmin)
        f = float(np.clip(f, 0, 1))
        return Arc(radius=R, start_angle=A0, angle=f * (A1 - A0),
                   arc_center=center, stroke_color=INK, stroke_width=6)
    return always_redraw(make)


def needle_for(center, tracker, vmin, vmax):
    """A heavy needle that redraws from `center` as the tracker moves."""
    def make():
        f = (tracker.get_value() - vmin) / (vmax - vmin)
        ang = _ang(f)
        u = np.array([np.cos(ang), np.sin(ang), 0])
        tail = center - 0.18 * u
        tip = center + (R - 0.12) * u
        n = Line(tail, tip, stroke_color=INK, stroke_width=7)
        n.set_cap_style(CapStyleType.ROUND)
        return n
    return always_redraw(make)


def readout_for(center, tracker, fmt, s=46, c=INK):
    """A live numeric readout pinned just below `center`."""
    pos = center + DOWN * 0.62
    m = mono(fmt(tracker.get_value()), s, c).move_to(pos)
    m.add_updater(lambda x: x.become(mono(fmt(tracker.get_value()), s, c).move_to(pos)))
    return m


def wer_x(frac):
    """Map a 0..1 fraction to an x on the full-width WER track."""
    return WER_X0 + float(np.clip(frac, 0, 1)) * (WER_X1 - WER_X0)


class TwoDials(Scene):
    def construct(self):
        seed()

        # ================================================================
        # BEAT 1 — POSE: identical sounds, two legal sentences (top zone).
        #   The word-map's statistics break the tie (links back to S19).
        # ================================================================
        sounds = mono("AY   S   K   R   IY   M", 30, INK_DIM).move_to(UP * 2.7)
        brace = mono("identical sounds", 16, INK_FAINT).next_to(sounds, DOWN, buff=0.18)
        self.play(FadeIn(sounds, shift=DOWN * 0.15), run_time=0.55)
        self.play(FadeIn(brace), run_time=0.25)

        # two legal readings of the SAME phoneme string, on a balance beam
        opt_a = serif("ice cream", 40, INK)
        opt_b = serif("I scream", 40, INK)
        opt_a.move_to(LEFT * 2.7 + UP * 1.15)
        opt_b.move_to(RIGHT * 2.7 + UP * 1.15)
        beam_pivot = UP * 0.78
        beam = Line(LEFT * 3.4, RIGHT * 3.4, stroke_color=INK_FAINT, stroke_width=2.5)
        beam.move_to(beam_pivot)
        fulcrum = Triangle(color=INK_FAINT, fill_opacity=0.0).scale(0.16)
        fulcrum.next_to(beam, DOWN, buff=0.02)
        self.play(TransformFromCopy(sounds, opt_a),
                  TransformFromCopy(sounds, opt_b),
                  Create(beam), FadeIn(fulcrum), run_time=0.95)

        # a second homophone pair ghosts in — the problem is general
        pair2_a = serif("recognize speech", 19, INK_GHOST)
        pair2_b = serif("wreck a nice beach", 19, INK_GHOST)
        pair2 = VGroup(pair2_a, pair2_b).arrange(RIGHT, buff=0.9)
        pair2.move_to(UP * 0.3)
        self.play(LaggedStart(FadeIn(pair2_a), FadeIn(pair2_b),
                              lag_ratio=0.3), run_time=0.55)

        # word-statistics break the tie -> "ice cream" wins; beam tips toward it
        tie = mono("word-map breaks the tie", 15, INK_FAINT).move_to(DOWN * 0.45)
        self.play(FadeIn(tie, shift=UP * 0.08), run_time=0.3)
        win = SurroundingRectangle(opt_a, color=INK, stroke_width=2, buff=0.16)
        self.play(Create(win),
                  opt_b.animate.set_opacity(0.28),
                  pair2_b.animate.set_opacity(0.18),
                  Rotate(beam, 6 * DEGREES, about_point=beam_pivot),
                  run_time=0.6)
        self.play(Flash(opt_a, color=INK, line_length=0.14,
                        num_lines=12, flash_radius=1.1), run_time=0.4)

        cap1 = mono("sounds tie  ·  the dials break it", 15, INK_FAINT).move_to(DOWN * 0.95)
        self.play(FadeIn(cap1), run_time=0.3)

        # ----- collapse Beat 1 into the permanent TOP context strip --------
        b1 = VGroup(sounds, brace, opt_a, opt_b, beam, fulcrum,
                    pair2, tie, win, cap1)
        self.play(
            b1.animate.scale(0.5).to_edge(UP, buff=0.18).set_opacity(0.42),
            run_time=0.7)
        # keep the chosen reading findable for the final brighten
        chosen = opt_a

        # ================================================================
        # BEAT 2 — BUILD: raise the two enormous dials + the WER meter.
        # ================================================================
        scale_t = ValueTracker(1.0)   # acoustic scale, range [0, 1] on the face
        blank_t = ValueTracker(0.0)   # blank penalty, range [0, 3]

        face_L = gauge_face(cL)
        face_R = gauge_face(cR)
        name_L = mono("acoustic scale", 22, INK_DIM).next_to(face_L, UP, buff=0.30)
        name_R = mono("blank penalty", 22, INK_DIM).next_to(face_R, UP, buff=0.30)

        # end-of-range labels under each arc (kept tucked beside each gauge so
        # they never collide with the centre filmstrip band)
        endL_lo = mono("lean English", 14, INK_FAINT).move_to(cL + LEFT * 1.55 + DOWN * 1.30)
        endL_hi = mono("trust muscle", 14, INK_FAINT).move_to(cL + RIGHT * 1.55 + DOWN * 1.30)
        endR_lo = mono("0", 14, INK_FAINT).move_to(cR + LEFT * 1.45 + DOWN * 1.30)
        endR_hi = mono("3", 14, INK_FAINT).move_to(cR + RIGHT * 1.45 + DOWN * 1.30)

        self.play(LaggedStart(
            FadeIn(face_L, scale=0.9), FadeIn(face_R, scale=0.9),
            FadeIn(name_L), FadeIn(name_R),
            FadeIn(endL_lo), FadeIn(endL_hi), FadeIn(endR_lo), FadeIn(endR_hi),
            lag_ratio=0.10), run_time=1.0)

        fill_L = fill_arc_for(cL, scale_t, 0.0, 1.0)
        fill_R = fill_arc_for(cR, blank_t, 0.0, 3.0)
        needle_L = needle_for(cL, scale_t, 0.0, 1.0)
        needle_R = needle_for(cR, blank_t, 0.0, 3.0)
        read_L = readout_for(cL, scale_t, lambda v: f"{v:.2f}")
        read_R = readout_for(cR, blank_t, lambda v: f"{v:.1f}")
        self.add(fill_L, fill_R, needle_L, needle_R, read_L, read_R)

        # ----- full-width WER meter (bottom zone) --------------------------
        wer_track = Line(LEFT * 6 + UP * WER_Y, RIGHT * 6 + UP * WER_Y,
                         stroke_color=INK_GHOST, stroke_width=4)
        wer_lbl = mono("words wrong", 14, INK_FAINT)
        wer_lbl.move_to(np.array([WER_X0 - 0.05, WER_Y + 0.34, 0]), aligned_edge=LEFT)
        # fill + a live counter riding the tip, both ValueTracker-driven
        wer_t = ValueTracker(0.76)  # fraction wrong

        def make_wer_fill():
            x = wer_x(wer_t.get_value())
            return Line(LEFT * 6 + UP * WER_Y, np.array([x, WER_Y, 0]),
                        stroke_color=INK, stroke_width=8)
        wer_fill = always_redraw(make_wer_fill)

        def make_wer_tip():
            x = wer_x(wer_t.get_value())
            return Dot(np.array([x, WER_Y, 0]), radius=0.07, color=INK)
        wer_tip = always_redraw(make_wer_tip)

        def make_wer_count():
            pct = int(round(wer_t.get_value() * 100))
            x = wer_x(wer_t.get_value())
            m = mono(f"{pct}% wrong", 18, INK)
            m.move_to(np.array([x, WER_Y + 0.30, 0]), aligned_edge=LEFT)
            return m
        wer_count = always_redraw(make_wer_count)

        self.play(FadeIn(wer_track), FadeIn(wer_lbl), run_time=0.4)
        self.add(wer_fill, wer_tip, wer_count)
        self.play(FadeIn(wer_fill), run_time=0.4)

        # ================================================================
        # BEAT 3 — TRANSFORM dial one: acoustic scale 1.0 -> 0.25.
        #   WER fill retreats; scale alone fixes most words.
        # ================================================================
        self.play(scale_t.animate.set_value(0.25),
                  wer_t.animate.set_value(0.18),
                  endL_lo.animate.set_color(INK_DIM),
                  chosen.animate.set_opacity(0.62),  # one notch brighter
                  run_time=1.5, rate_func=smooth)
        self.play(Flash(read_L, color=INK, line_length=0.13,
                        num_lines=12, flash_radius=0.7), run_time=0.4)

        # ================================================================
        # BEAT 4 — BUILD the blank story: a mid filmstrip of blank-happy bars.
        #   centered at x=0, in a ~2-unit band, y ~ -0.5.
        # ================================================================
        bx0 = LEFT * 0.95 + DOWN * 0.95
        # tall = "blank" (model's lazy default), short = a real sound
        heights = [0.62, 0.62, 0.56, 0.62, 0.22, 0.62, 0.62, 0.56]
        bars = VGroup()
        for i, h in enumerate(heights):
            blanky = h > 0.4
            bar = Rectangle(width=0.20, height=h, stroke_width=0, fill_color=INK,
                            fill_opacity=0.85 if blanky else 0.4)
            bar.move_to(bx0 + RIGHT * (i * 0.27) + UP * (h / 2))
            bars.add(bar)
        bars.move_to(np.array([0, -0.45, 0]), aligned_edge=DOWN)
        # narrow two-line caption — stays in the centre band, clears end-labels
        film_cap = VGroup(
            mono("most frames guess blank", 14, INK_FAINT),
            mono("(~0.92 sure)", 13, INK_GHOST),
        ).arrange(DOWN, buff=0.10)
        film_cap.move_to(np.array([0, -1.55, 0]))
        film_top = mono("per-frame readout", 13, INK_GHOST)
        film_top.move_to(bars.get_top() + UP * 0.22)
        self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN, lag_ratio=0.06),
                  FadeIn(film_cap), FadeIn(film_top), run_time=0.8)
        # pulse the right dial's name — it is about to matter most
        self.play(Indicate(name_R, color=INK, scale_factor=1.12), run_time=0.5)

        # ================================================================
        # BEAT 5 — THE HERO MOVE: blank penalty 0.0 -> 2.0.
        #   needle (cause) -> bars commit to real sounds (mechanism)
        #   -> WER bar's biggest single leftward drop (payoff), L->R.
        # ================================================================
        # blanks shrink, 2-3 real-sound bars rise
        new_heights = [0.26, 0.62, 0.24, 0.62, 0.58, 0.26, 0.62, 0.22]
        bar_targets = []
        for i, h in enumerate(new_heights):
            blanky = h > 0.4
            t = Rectangle(width=0.20, height=h, stroke_width=0, fill_color=INK,
                          fill_opacity=0.85 if blanky else 0.62)
            t.move_to(np.array([bars[i].get_x(), 0, 0]))  # x fixed, set y below
            t.align_to(bars, DOWN)
            t.move_to(np.array([bars[i].get_x(), bars.get_bottom()[1] + h / 2, 0]))
            bar_targets.append(t)

        # WER's second, larger drop framed as 0.78 -> 0.61 (blank effect)
        self.play(
            blank_t.animate.set_value(2.0),
            wer_t.animate.set_value(0.61),
            *[Transform(bars[i], bar_targets[i]) for i in range(len(bars))],
            run_time=1.7, rate_func=smooth)
        self.play(Indicate(read_R, color=INK, scale_factor=1.25), run_time=0.55)

        # freeze updaters so the held end frame is stable
        for m in (fill_L, fill_R, needle_L, needle_R, read_L, read_R,
                  wer_fill, wer_tip, wer_count):
            m.clear_updaters()

        # ================================================================
        # BEAT 6 — NAME IT + POSTER HOLD: landed chips, brightened reading,
        #   the punchline, and a stable composed canvas.
        # ================================================================
        chip_L = mono("0.25", 18, INK).next_to(name_L, RIGHT, buff=0.25)
        chip_R = mono("2.0", 18, INK).next_to(name_R, RIGHT, buff=0.25)
        boxL = SurroundingRectangle(chip_L, color=INK_FAINT, stroke_width=1.4, buff=0.08)
        boxR = SurroundingRectangle(chip_R, color=INK_FAINT, stroke_width=1.4, buff=0.08)
        # brighten the chosen reading up top to pure #fff with a soft glow
        chosen_bright = chosen.copy().set_opacity(1.0).set_color(WHITE)
        win.set_color(INK)  # its box reads as the resolved answer
        self.play(
            FadeIn(chip_L, shift=LEFT * 0.1), FadeIn(chip_R, shift=LEFT * 0.1),
            Create(boxL), Create(boxR),
            Transform(chosen, chosen_bright),
            win.animate.set_stroke(color=WHITE, width=2.2, opacity=1.0),
            run_time=0.55)

        punch = mono("blank penalty  —  the single biggest lever", 21, INK_DIM)
        punch.move_to(np.array([0, WER_Y + 0.78, 0]))
        underline = Line(punch.get_left(), punch.get_right(),
                         stroke_color=INK_FAINT, stroke_width=1.5)
        underline.next_to(punch, DOWN, buff=0.08)
        self.play(FadeIn(punch, shift=UP * 0.08), run_time=0.45)
        self.play(Create(underline), run_time=0.3)
        self.wait(0.6)
