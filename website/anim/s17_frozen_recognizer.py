# S17 — The honesty lock (frozen recognizer). The load-bearing idea:
# matching "on average" isn't enough — a locked phoneme reader forces the copied
# features to be genuinely decodable into sounds. Strict monochrome.
#
# REBUILT to fill the whole canvas as an instrument panel:
#   TOP   strip  — quiet context: S16 recap chip + the reader's frozen spec +
#                  a "~10% PER, then FROZEN" tag that gets a snowflake/lock glyph.
#   CENTER       — a wide S-vs-Z duel pushed to the edges, a TALL vertical
#                  "phoneme distance" meter standing literally between them, and
#                  the locked PHONEME READER box; pulses feed THROUGH it.
#   BOTTOM strip — a running takeaway: a separation progress bar + live counter
#                  + a morphing verdict (DISTINCT→BLURRED→DECODABLE) and a
#                  word-by-word punchline that finally becomes the mechanism recap.
# The aha is the synchronized snap on Beat 4: the lock + CTC demand force the
# identical blurry bars to SPLINTER back apart, the central needle SURGES, the
# bottom counter races up, and one pure-#fff ✓ pops — one cause, one effect,
# across all three zones at once.
from manim import *
from emg_style import *

WHITE = "#ffffff"


def vec_bars(values, w=0.20, gap=0.07, unit=1.15, c=INK, op=1.0):
    """A little column-vector drawn as horizontal bars (no LaTeX)."""
    bars = VGroup()
    for v in values:
        b = Rectangle(
            width=max(0.05, abs(v) * unit), height=w,
            stroke_width=0, fill_color=c, fill_opacity=op,
        )
        bars.add(b)
    bars.arrange(DOWN, buff=gap, aligned_edge=LEFT)
    return bars


def sep_of(va, vb):
    """A simple 0..1 'separation' score: mean |a-b|, scaled to read nicely."""
    d = float(np.mean(np.abs(np.array(va) - np.array(vb))))
    return min(1.0, d / 0.55)


def snowflake(c=INK, r=0.12, sw=2.0):
    """A tiny 6-spoke snowflake glyph (lock/freeze cue) — no heavy asset."""
    g = VGroup()
    for k in range(6):
        a = k * PI / 3
        d = np.array([np.cos(a), np.sin(a), 0]) * r
        spoke = Line(-d, d, stroke_color=c, stroke_width=sw)
        # two little barbs near each tip
        for s in (0.55, 0.55):
            tip = d * s
            for sgn in (+1, -1):
                ba = a + sgn * PI / 4
                bd = np.array([np.cos(ba), np.sin(ba), 0]) * (r * 0.34)
                g.add(Line(tip, tip + bd, stroke_color=c, stroke_width=sw))
        g.add(spoke)
    return g


class HonestyLock(Scene):
    def construct(self):
        seed()

        # =================================================================
        # BEAT 1 — POSE / fill the canvas.  Three zones come up balanced.
        # =================================================================

        # ---- TOP strip: context (y ~ +2.55 .. +3.45) --------------------
        recap = mono("from S16: copy the teacher's voice  →", 14, INK_FAINT)
        recap.move_to([-4.35, 3.18, 0])

        spec = mono("WavLM→phonemes  ·  LayerNorm → 2×Conv1d(k5) → Linear(41)",
                    14, INK_FAINT).move_to([2.05, 3.18, 0])
        frozen_tag = mono("~10% PER, then FROZEN", 13, INK_FAINT)
        frozen_tag.next_to(spec, DOWN, buff=0.16).align_to(spec, RIGHT)
        flake = snowflake(INK, r=0.12).next_to(frozen_tag, LEFT, buff=0.16)
        flake.set_opacity(0.0)   # appears on the lock snap (Beat 3)

        top_rule = Line([-6.6, 2.78, 0], [6.6, 2.78, 0],
                        stroke_color=INK_GHOST, stroke_width=1.1)

        self.play(
            FadeIn(recap, shift=RIGHT * 0.15),
            FadeIn(spec, shift=LEFT * 0.15),
            FadeIn(frozen_tag),
            Create(top_rule),
            run_time=0.7,
        )

        # ---- CENTER: the S/Z duel pushed to the edges -------------------
        labA = serif("S", 58, INK).move_to([-5.55, 1.05, 0])
        labB = serif("Z", 58, INK).move_to([5.55, -1.05, 0])
        subA = mono("voiceless", 13, INK_FAINT).next_to(labA, DOWN, buff=0.14)
        subB = mono("voiced", 13, INK_FAINT).next_to(labB, DOWN, buff=0.14)

        valsA = [0.95, 0.20, 0.80, 0.35, 0.70, 0.15]
        valsB = [0.15, 0.85, 0.25, 0.90, 0.30, 0.95]
        vecA = vec_bars(valsA, c=INK).next_to(labA, RIGHT, buff=0.45).set_y(labA.get_y())
        vecB = vec_bars(valsB, c=INK).next_to(labB, LEFT, buff=0.45).set_y(labB.get_y())
        # mirror Z so its bars grow leftward (toward the edge), reader feeds inward
        for b in vecB:
            b.align_to(vecB.get_right(), RIGHT)
        vecB.align_to(labB.get_left(), RIGHT).shift(LEFT * 0.45).set_y(labB.get_y())

        # fixed anchors for feed arrows so they don't clip when vectors reshape
        anchA = vecA.get_right() + RIGHT * 0.05
        anchB = vecB.get_left() + LEFT * 0.05

        vlblA = mono("feature vector", 12, INK_FAINT).next_to(vecA, DOWN, buff=0.18)
        vlblB = mono("feature vector", 12, INK_FAINT).next_to(vecB, DOWN, buff=0.18)

        self.play(
            FadeIn(labA, shift=RIGHT * 0.2), FadeIn(labB, shift=LEFT * 0.2),
            FadeIn(subA), FadeIn(subB),
            run_time=0.5,
        )
        self.play(
            LaggedStartMap(GrowFromEdge, vecA, edge=LEFT, lag_ratio=0.06),
            LaggedStartMap(GrowFromEdge, vecB, edge=RIGHT, lag_ratio=0.06),
            FadeIn(vlblA), FadeIn(vlblB),
            run_time=0.7,
        )

        # ---- CENTER: the tall vertical "phoneme distance" meter ---------
        # Storyboard separation readouts: DISTINCT 0.92 -> BLURRED 0.04 ->
        # DECODABLE 0.90 (sep_of confirms the vectors are maximally apart; we
        # display the brief's tuned values, not the clamped 1.0).
        SEP_DISTINCT, SEP_BLUR, SEP_DECODE = 0.92, 0.04, 0.90
        sep = ValueTracker(SEP_DISTINCT)   # ~0.92 while distinct
        MTR_X = 0.0
        MTR_Y = 0.05
        MTR_H = 3.2
        MTR_W = 0.42
        m_bottom = MTR_Y - MTR_H / 2 + 0.06
        m_inner_h = MTR_H - 0.12

        meter_track = RoundedRectangle(
            corner_radius=0.20, width=MTR_W, height=MTR_H,
            stroke_color=INK_GHOST, stroke_width=1.6, fill_opacity=0,
        ).move_to([MTR_X, MTR_Y, 0])
        meter_lbl = mono("phoneme\ndistance", 13, INK_FAINT, w=NORMAL)
        meter_lbl.move_to([MTR_X, MTR_Y + MTR_H / 2 + 0.42, 0])

        # tick marks at 0 and 1 on the meter
        tick_hi = mono("1.0", 10, INK_GHOST).next_to(
            meter_track, RIGHT, buff=0.12).align_to(meter_track, UP)
        tick_lo = mono("0", 10, INK_GHOST).next_to(
            meter_track, RIGHT, buff=0.12).align_to(meter_track, DOWN)

        def make_meter_fill():
            v = max(0.0, min(1.0, sep.get_value()))
            h = max(0.03, m_inner_h * v)
            f = RoundedRectangle(
                corner_radius=0.16, width=MTR_W - 0.14, height=h,
                stroke_width=0, fill_color=INK, fill_opacity=0.9,
            )
            f.move_to([MTR_X, m_bottom + h / 2, 0])
            return f
        meter_fill = always_redraw(make_meter_fill)

        # a needle/marker that rides the top of the fill
        def make_needle():
            v = max(0.0, min(1.0, sep.get_value()))
            y = m_bottom + m_inner_h * v
            return Line([MTR_X - MTR_W / 2 - 0.14, y, 0],
                        [MTR_X + MTR_W / 2 + 0.14, y, 0],
                        stroke_color=INK, stroke_width=2.4)
        needle = always_redraw(make_needle)

        self.play(
            FadeIn(meter_lbl), Create(meter_track),
            FadeIn(tick_hi), FadeIn(tick_lo),
            FadeIn(meter_fill), FadeIn(needle),
            run_time=0.55,
        )

        # ---- BOTTOM strip: running takeaway (y ~ -3.5 .. -2.6) ----------
        bar_y = -2.95
        BAR_X0 = -5.0
        BAR_W = 6.4
        bottom_lbl = mono("separation", 13, INK_FAINT).move_to(
            [BAR_X0 + 0.55, bar_y + 0.42, 0])
        bar_track = RoundedRectangle(
            corner_radius=0.07, width=BAR_W, height=0.22,
            stroke_color=INK_GHOST, stroke_width=1.4, fill_opacity=0,
        ).move_to([BAR_X0 + BAR_W / 2, bar_y, 0])
        bx0 = bar_track.get_left()[0] + 0.05
        bw = BAR_W - 0.10

        def make_bar_fill():
            v = max(0.0, min(1.0, sep.get_value()))
            w = max(0.03, bw * v)
            f = RoundedRectangle(
                corner_radius=0.05, width=w, height=0.14,
                stroke_width=0, fill_color=INK, fill_opacity=0.88,
            )
            f.move_to([bx0 + w / 2, bar_y, 0])
            return f
        bar_fill = always_redraw(make_bar_fill)

        # verdict word + live number, to the right of the bar
        VERD_X = 2.85
        SEPNUM_X = 4.55   # fixed anchor for the live number (verdict words swap under it)
        verdict = mono("DISTINCT", 22, INK).move_to([VERD_X, bar_y + 0.02, 0])
        sep_num = num(f"{sep.get_value():.2f}", 22, INK).move_to([SEPNUM_X, bar_y + 0.02, 0])
        sep_num.add_updater(lambda m: m.become(
            num(f"{sep.get_value():.2f}", 22, INK).move_to([SEPNUM_X, bar_y + 0.02, 0])))

        self.play(
            FadeIn(bottom_lbl), Create(bar_track),
            FadeIn(bar_fill), FadeIn(verdict), FadeIn(sep_num),
            run_time=0.55,
        )
        self.wait(0.2)

        # =================================================================
        # BEAT 2 — THE FAILURE COLLAPSE.  Two sounds → one blurry average.
        # =================================================================
        blur = [0.52, 0.50, 0.55, 0.49, 0.53, 0.50]
        vecA_blur = vec_bars(blur, c=INK_FAINT, op=0.7).next_to(
            labA, RIGHT, buff=0.45).set_y(labA.get_y())
        vecB_blur = vec_bars(blur, c=INK_FAINT, op=0.7)
        for b in vecB_blur:
            b.align_to(vecB_blur.get_right(), RIGHT)
        vecB_blur.align_to(labB.get_left(), RIGHT).shift(LEFT * 0.45).set_y(labB.get_y())

        verdict_blur = mono("BLURRED", 22, INK_FAINT).move_to(verdict)

        punch1 = mono("close on average — useless for telling sounds apart",
                      18, INK_FAINT).move_to([0.0, -3.62, 0])

        self.play(
            Transform(vecA, vecA_blur),
            Transform(vecB, vecB_blur),
            sep.animate.set_value(SEP_BLUR),
            FadeOut(verdict, scale=0.9), FadeIn(verdict_blur, scale=1.05),
            FadeIn(punch1),
            run_time=1.2,
        )
        verdict = verdict_blur   # keep a clean handle for later swaps
        # ghost "≈" between the two collapsed vectors + a flash on the readout
        approx = mono("≈", 46, INK_DIM).move_to([MTR_X, MTR_Y + 1.45, 0])
        self.play(
            FadeIn(approx, scale=0.6),
            Flash(sep_num, color=INK, line_length=0.14, num_lines=10,
                  flash_radius=0.42),
            run_time=0.45,
        )
        self.wait(0.2)

        # =================================================================
        # BEAT 3 — THE LOCK SNAPS.  Center reader box + padlock, two-zone
        # synchronized freeze (top FROZEN tag gets its snowflake on the same beat).
        # =================================================================
        # the meter dims to ghost and slides slightly aside so the reader owns center
        self.play(
            FadeOut(approx),
            FadeOut(punch1),
            meter_track.animate.set_stroke(opacity=0.35).shift(LEFT * 1.85),
            meter_lbl.animate.set_opacity(0.45).shift(LEFT * 1.85),
            tick_hi.animate.shift(LEFT * 1.85),
            tick_lo.animate.shift(LEFT * 1.85),
            run_time=0.5,
        )
        # rebind meter visuals to the shifted x
        MTR_X = -1.85

        reader = RoundedRectangle(
            corner_radius=0.14, width=2.9, height=2.3,
            stroke_color=INK, stroke_width=2.2, fill_color=BG, fill_opacity=1,
        ).move_to([0.55, 0.30, 0])
        reader_lbl = mono("PHONEME\nREADER", 19, INK).move_to(
            reader.get_center() + UP * 0.42)

        # padlock built OPEN (shackle lifted/rotated), below the label
        body = RoundedRectangle(corner_radius=0.06, width=0.56, height=0.44,
                                stroke_color=INK, stroke_width=2.8,
                                fill_color=BG, fill_opacity=1)
        shackle = Arc(radius=0.18, start_angle=0, angle=PI,
                      stroke_color=INK, stroke_width=2.8)
        keyhole = Dot(radius=0.04, color=INK)
        body.move_to(reader.get_center() + DOWN * 0.42)
        shackle.next_to(body, UP, buff=-0.03)
        keyhole.move_to(body.get_center())
        shackle_open = shackle.copy().shift(UP * 0.16 + RIGHT * 0.13).rotate(0.38)

        self.play(Create(reader), FadeIn(reader_lbl), run_time=0.6)
        self.play(FadeIn(body), FadeIn(keyhole),
                  TransformFromCopy(shackle, shackle_open), run_time=0.45)
        self.remove(shackle_open)
        self.add(shackle_open)

        cap_lock = mono("trained to ~10% error, then frozen — no longer learns",
                        18, INK_DIM).move_to([0.0, -3.62, 0])
        self.play(FadeIn(cap_lock), run_time=0.3)

        # THE SNAP — synchronized across two zones:
        locked_tag = mono("LOCKED", 15, INK).next_to(body, DOWN, buff=0.20)
        flake.set_opacity(1.0)
        self.play(
            Transform(shackle_open, shackle),                       # shackle drops home
            Flash(keyhole, color=INK, line_length=0.16, num_lines=12,
                  flash_radius=0.42),                               # click
            FadeIn(locked_tag, shift=UP * 0.1),
            FadeIn(flake, scale=0.5),                               # snowflake in TOP strip
            Indicate(frozen_tag, color=INK, scale_factor=1.08),    # FROZEN tag pulses
            run_time=0.6,
        )
        self.wait(0.2)

        # =================================================================
        # BEAT 4 — FORCED APART (THE WOW).  Lock + CTC demand splinter the
        # blurry bars back into opposite crisp profiles; needle SURGES; counter
        # races up; one pure-white ✓.
        # =================================================================
        self.play(FadeOut(cap_lock), run_time=0.3)

        # arrows: blurry vectors -> reader edges (fixed anchors, never clip)
        arrA = Arrow(anchA, reader.get_left() + UP * 0.55,
                     stroke_width=2.2, color=INK_DIM, buff=0.2,
                     max_tip_length_to_length_ratio=0.10)
        arrB = Arrow(anchB, reader.get_right() + DOWN * 0.55,
                     stroke_width=2.2, color=INK_DIM, buff=0.2,
                     max_tip_length_to_length_ratio=0.10)
        self.play(GrowArrow(arrA), GrowArrow(arrB), run_time=0.45)

        # traveling pulses carry the (blurry) features INTO the reader
        pulses = VGroup(Dot(radius=0.055, color=INK).move_to(arrA.get_start()),
                        Dot(radius=0.055, color=INK).move_to(arrB.get_start()))
        self.add(pulses)
        self.play(pulses[0].animate.move_to(arrA.get_end()),
                  pulses[1].animate.move_to(arrB.get_end()),
                  run_time=0.5, rate_func=rate_functions.ease_in_sine)
        self.remove(pulses)

        # CTC demand at the reader exits: must output the right phonemes
        outS = serif("S", 38, INK).move_to([2.95, 1.35, 0])
        outZ = serif("Z", 38, INK).move_to([2.95, -0.75, 0])
        outArrU = Arrow(reader.get_right() + UP * 0.45, outS.get_left(),
                        stroke_width=2.0, color=INK_DIM, buff=0.22,
                        max_tip_length_to_length_ratio=0.14)
        outArrD = Arrow(reader.get_right() + DOWN * 0.45, outZ.get_left(),
                        stroke_width=2.0, color=INK_DIM, buff=0.22,
                        max_tip_length_to_length_ratio=0.14)
        demand = mono("+1.0 · CTC", 17, INK).move_to([3.55, 0.30, 0])
        demand_sub = mono("must spell\nthe sounds", 13, INK_FAINT).move_to(
            [3.55, -0.30, 0])
        self.play(GrowArrow(outArrU), GrowArrow(outArrD),
                  FadeIn(outS), FadeIn(outZ), FadeIn(demand), FadeIn(demand_sub),
                  run_time=0.6)

        # THE PRESSURE BEAT: blurry -> crisp opposite profiles (splinter apart),
        # needle SURGES, bottom counter climbs to DECODABLE 0.90.
        crispA = vec_bars(valsA, c=INK).next_to(labA, RIGHT, buff=0.45).set_y(labA.get_y())
        crispB = vec_bars(valsB, c=INK)
        for b in crispB:
            b.align_to(crispB.get_right(), RIGHT)
        crispB.align_to(labB.get_left(), RIGHT).shift(LEFT * 0.45).set_y(labB.get_y())

        verdict_dec = mono("DECODABLE", 22, INK).move_to([VERD_X, bar_y + 0.02, 0])
        # word-by-word punchline assembling along the bottom
        pw = VGroup(
            mono("phoneme-decodable", 19, INK),
            mono("—", 19, INK_DIM),
            mono("not just similar.", 19, INK_DIM),
        ).arrange(RIGHT, buff=0.22).move_to([0.0, -3.62, 0])

        self.play(
            ReplacementTransform(vecA, crispA),
            ReplacementTransform(vecB, crispB),
            sep.animate.set_value(SEP_DECODE),
            FadeOut(verdict, scale=0.9), FadeIn(verdict_dec, scale=1.05),
            LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in pw], lag_ratio=0.35),
            run_time=1.3,
        )
        verdict = verdict_dec
        sep_num.clear_updaters()

        # peak: one pure-white ✓ + indicate the recovered vectors and the meter
        check = mono("✓", 30, WHITE).next_to(demand, RIGHT, buff=0.20)
        self.play(
            Indicate(crispA, color=INK, scale_factor=1.12),
            Indicate(crispB, color=INK, scale_factor=1.12),
            Indicate(meter_fill, color=WHITE, scale_factor=1.06),
            FadeIn(check, scale=0.6),
            run_time=0.65,
        )
        self.wait(0.2)

        # =================================================================
        # BEAT 5 — NAME IT + REST.  Clear the working layer; lay a dense recap
        # line low in the canvas; hold the poster.
        # =================================================================
        rule = Line([-6.0, -3.42, 0], [6.0, -3.42, 0],
                    stroke_color=INK_GHOST, stroke_width=1.2)
        recap_line = mono(
            "frozen recognizer   ·   +1.0·CTC loss   ·   decodable, not just close",
            16, INK_DIM).move_to([0.0, -3.62, 0])
        self.play(
            FadeOut(arrA), FadeOut(arrB),
            FadeOut(demand_sub),
            FadeOut(pw),
            Create(rule),
            run_time=0.5,
        )
        self.play(FadeIn(recap_line, shift=UP * 0.1), run_time=0.45)
        # freeze the live meter/needle so the poster is rock-steady
        meter_fill.clear_updaters()
        needle.clear_updaters()
        bar_fill.clear_updaters()
        self.wait(0.6)
