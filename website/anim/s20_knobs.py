# website/anim/s20_knobs.py  — S20 "Two dials" (acoustic scale + blank penalty)
# Strict monochrome. The same sounds can be "ice cream" or "I scream"; the
# cheapest-path search must pick one, and two decode dials tip the scale.
# Land acoustic scale near 0.25, blank penalty at 2.0.
#
# Ground truth (Section 8.3, decode.py):
#   untuned acoustic scale 1.0 -> ~75% WER;  tuned scale ~= 0.25 (Conformer)
#   CTC blank peaks ~0.92 (model is "blank-happy")
#   blank penalty 0 -> 2 moved WER 77.6 -> 60.6 on a slice (single biggest lever)
#
# Locked 6-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 (1.48s) POSE   : one phoneme string -> two readings on a beam
#   2 (4.07s) BUILD  : two enormous dials rise, needles at high default; WER meter
#   3 (0.76s) DIAL 1 : acoustic scale 1.0 -> 0.25, WER 76% -> 64% (held slice)
#   4 (3.76s) BLANK  : per-frame filmstrip, tall blank bars dominate
#   5 (0.60s) DIAL 2 : blank penalty 0 -> 2.0, bars commit, WER 64% -> 48% (held slice)
#   NOTE: the meter is a held DECODE-TUNING slice and must only ever FALL; it is
#   NOT the final 18.5% (that is earned later by the encoder + ensemble + rerank).
#   6 (1.41s) NAME   : chips lock, "ice cream" -> white, punchline, poster hold
#
# Canvas: full-bleed.  x in [-7.1,7.1], y in [-4,4].
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
        if f < 1e-3:  # angle-0 Arc renders as a degenerate filled disc; skip it
            return VGroup()
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
        # BEAT 1 (1.48s) — POSE: identical sounds, two legal sentences.
        #   One homophone is enough to feel the tie. No sub-captions.
        # ================================================================
        self.next_section("pose")
        sounds = mono("AY   S   K   R   IY   M", 30, INK_DIM).move_to(UP * 2.7)
        brace = mono("identical sounds", 16, INK_FAINT).next_to(sounds, DOWN, buff=0.18)
        self.play(FadeIn(sounds, shift=DOWN * 0.15), run_time=0.45)
        self.play(FadeIn(brace), run_time=0.2)

        # two legal readings of the SAME phoneme string, on a balance beam
        opt_a = serif("ice cream", 40, INK)
        opt_b = serif("I scream", 40, INK)
        opt_a.move_to(LEFT * 2.7 + UP * 1.25)
        opt_b.move_to(RIGHT * 2.7 + UP * 1.25)
        beam_pivot = UP * 0.85
        beam = Line(LEFT * 3.4, RIGHT * 3.4, stroke_color=INK_FAINT, stroke_width=2.5)
        beam.move_to(beam_pivot)
        fulcrum = Triangle(color=INK_FAINT, fill_opacity=0.0).scale(0.16)
        fulcrum.next_to(beam, DOWN, buff=0.02)
        self.play(TransformFromCopy(sounds, opt_a),
                  TransformFromCopy(sounds, opt_b),
                  Create(beam), FadeIn(fulcrum), run_time=0.6)
        self.wait(0.13)

        # keep the chosen reading findable for the final brighten
        chosen = opt_a

        # ================================================================
        # BEAT 2 (4.07s) — BUILD: shrink the pose into the dim top strip,
        #   then raise the two enormous dials (needles parked HIGH) + WER meter.
        #   End labels are withheld until Beat 3 (they appear with the move).
        # ================================================================
        self.next_section("build")
        b1 = VGroup(sounds, brace, opt_a, opt_b, beam, fulcrum)
        self.play(
            b1.animate.scale(0.5).to_edge(UP, buff=0.18).set_opacity(0.40),
            run_time=0.7)

        scale_t = ValueTracker(1.0)   # acoustic scale, range [0, 1] on the face
        blank_t = ValueTracker(0.0)   # blank penalty, range [0, 3]

        face_L = gauge_face(cL)
        face_R = gauge_face(cR)
        name_L = mono("acoustic scale", 22, INK_DIM).next_to(face_L, UP, buff=0.30)
        name_R = mono("blank penalty", 22, INK_DIM).next_to(face_R, UP, buff=0.30)

        self.play(LaggedStart(
            FadeIn(face_L, scale=0.9), FadeIn(face_R, scale=0.9),
            FadeIn(name_L), FadeIn(name_R),
            lag_ratio=0.12), run_time=1.1)

        fill_L = fill_arc_for(cL, scale_t, 0.0, 1.0)
        fill_R = fill_arc_for(cR, blank_t, 0.0, 3.0)
        needle_L = needle_for(cL, scale_t, 0.0, 1.0)
        needle_R = needle_for(cR, blank_t, 0.0, 3.0)
        read_L = readout_for(cL, scale_t, lambda v: f"{v:.2f}")
        read_R = readout_for(cR, blank_t, lambda v: f"{v:.1f}")
        self.add(fill_L, fill_R, needle_L, needle_R, read_L, read_R)
        self.play(FadeIn(fill_L), FadeIn(fill_R), run_time=0.5)

        # ----- full-width WER meter (bottom zone) --------------------------
        wer_track = Line(LEFT * 6 + UP * WER_Y, RIGHT * 6 + UP * WER_Y,
                         stroke_color=INK_GHOST, stroke_width=4)
        wer_lbl = mono("words wrong", 14, INK_FAINT)
        wer_lbl.move_to(np.array([WER_X0 - 0.05, WER_Y + 0.34, 0]), aligned_edge=LEFT)
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

        self.play(FadeIn(wer_track), FadeIn(wer_lbl), run_time=0.45)
        self.add(wer_fill, wer_tip, wer_count)
        self.play(FadeIn(wer_fill), run_time=0.45)
        self.wait(0.87)

        # ================================================================
        # BEAT 3 (0.76s) — DIAL ONE: acoustic scale 1.0 -> 0.25, WER 76 -> 64
        #   on a held decode slice (scale only; NOT the final 18.5% pipeline result).
        #   Spotlight: left dial + WER meter only. Right dial dims to ghost.
        #   End labels fade in exactly as the needle moves.
        # ================================================================
        self.next_section("dial_one")
        endL_lo = mono("lean English", 14, INK_DIM).move_to(cL + LEFT * 1.55 + DOWN * 1.30)
        endL_hi = mono("trust muscle", 14, INK_FAINT).move_to(cL + RIGHT * 1.55 + DOWN * 1.30)
        # dim the right dial's LABELS only — never fill its stroke-only arc face
        self.play(
            scale_t.animate.set_value(0.25),
            wer_t.animate.set_value(0.64),
            FadeIn(endL_lo), FadeIn(endL_hi),
            face_R.animate.set_stroke(opacity=0.30),
            name_R.animate.set_opacity(0.30),
            read_R.animate.set_opacity(0.30),
            run_time=0.76, rate_func=smooth)

        # ================================================================
        # BEAT 4 (3.76s) — BLANK story: a mid filmstrip of blank-happy bars.
        #   Spotlight: filmstrip + right-dial name. Left dial dims to ghost.
        # ================================================================
        self.next_section("blank")
        fill_L.clear_updaters()
        needle_L.clear_updaters()
        read_L.clear_updaters()
        # restore the right dial to full WITHOUT closing the arc into a disc
        # (VGroup.set_opacity sets fill_opacity=1, which fills the stroke-only Arc)
        face_R.set_stroke(opacity=1.0)
        name_R.set_opacity(1.0)
        read_R.set_opacity(1.0)
        # Dim the LEFT dial the SAME way: stroke-only on the arcs/fill/needle (never
        # set_opacity, which would fill the stroke arcs into a solid grey disc);
        # set_opacity only on the text labels.
        left_text = VGroup(name_L, endL_lo, endL_hi, read_L)
        self.play(
            face_L.animate.set_stroke(opacity=0.30),
            fill_L.animate.set_stroke(opacity=0.30),
            needle_L.animate.set_stroke(opacity=0.30),
            left_text.animate.set_opacity(0.30),
            run_time=0.5)

        bx0 = LEFT * 0.95 + DOWN * 0.95
        heights = [0.62, 0.62, 0.56, 0.62, 0.22, 0.62, 0.62, 0.56]
        bars = VGroup()
        for i, h in enumerate(heights):
            blanky = h > 0.4
            bar = Rectangle(width=0.20, height=h, stroke_width=0, fill_color=INK,
                            fill_opacity=0.85 if blanky else 0.4)
            bar.move_to(bx0 + RIGHT * (i * 0.27) + UP * (h / 2))
            bars.add(bar)
        bars.move_to(np.array([0, -0.45, 0]), aligned_edge=DOWN)
        film_cap = VGroup(
            mono("most frames guess blank", 14, INK_FAINT),
            mono("(~0.92 sure)", 13, INK_GHOST),
        ).arrange(DOWN, buff=0.10)
        film_cap.move_to(np.array([0, -1.55, 0]))
        film_top = mono("per-frame readout", 13, INK_GHOST)
        film_top.move_to(bars.get_top() + UP * 0.22)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06),
                  FadeIn(film_cap), FadeIn(film_top), run_time=1.2)
        self.play(Indicate(name_R, color=INK, scale_factor=1.12), run_time=0.7)
        self.wait(1.36)

        # ================================================================
        # BEAT 5 (0.60s) — DIAL TWO: blank penalty 0.0 -> 2.0.
        #   needle (cause) -> bars commit -> WER's biggest leftward drop 64 -> 48.
        #   Same held-slice meter as Beat 3 — it only ever falls (no silent reset),
        #   and this is the single largest drop, matching the "biggest lever" line.
        # ================================================================
        self.next_section("dial_two")
        new_heights = [0.26, 0.62, 0.24, 0.62, 0.58, 0.26, 0.62, 0.22]
        bar_targets = []
        for i, h in enumerate(new_heights):
            blanky = h > 0.4
            t = Rectangle(width=0.20, height=h, stroke_width=0, fill_color=INK,
                          fill_opacity=0.85 if blanky else 0.62)
            t.move_to(np.array([bars[i].get_x(), bars.get_bottom()[1] + h / 2, 0]))
            bar_targets.append(t)

        self.play(
            blank_t.animate.set_value(2.0),
            wer_t.animate.set_value(0.48),
            *[Transform(bars[i], bar_targets[i]) for i in range(len(bars))],
            run_time=0.6, rate_func=smooth)

        # freeze updaters so the held end frame is stable
        for m in (fill_R, needle_R, read_R, wer_fill, wer_tip, wer_count):
            m.clear_updaters()

        # ================================================================
        # BEAT 6 (1.41s) — NAME IT + POSTER HOLD: landed chips, the chosen
        #   reading brightens to pure white, the single punchline underlines.
        # ================================================================
        self.next_section("name_it")
        chip_L = mono("0.25", 18, INK).next_to(name_L, RIGHT, buff=0.25)
        chip_R = mono("2.0", 18, INK).next_to(name_R, RIGHT, buff=0.25)
        boxL = SurroundingRectangle(chip_L, color=INK_FAINT, stroke_width=1.4, buff=0.08)
        boxR = SurroundingRectangle(chip_R, color=INK_FAINT, stroke_width=1.4, buff=0.08)
        chosen_bright = chosen.copy().set_opacity(1.0).set_color(WHITE)
        win = SurroundingRectangle(chosen, color=WHITE, stroke_width=2.2, buff=0.12)
        self.play(
            FadeIn(chip_L, shift=LEFT * 0.1), FadeIn(chip_R, shift=LEFT * 0.1),
            Create(boxL), Create(boxR),
            Transform(chosen, chosen_bright),
            Create(win),
            run_time=0.55)

        punch = mono("blank penalty  —  the single biggest lever", 21, INK_DIM)
        punch.move_to(np.array([0, WER_Y + 0.78, 0]))
        underline = Line(punch.get_left(), punch.get_right(),
                         stroke_color=INK_FAINT, stroke_width=1.5)
        underline.next_to(punch, DOWN, buff=0.08)
        self.play(FadeIn(punch, shift=UP * 0.08), Create(underline), run_time=0.45)
        self.wait(0.41)
