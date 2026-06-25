# S17 — The honesty lock (frozen recognizer). The load-bearing idea:
# matching "on average" isn't enough — a locked phoneme reader forces the copied
# features to be genuinely DECODABLE back into sounds. Strict monochrome.
#
# Locked 7-beat sheet (one self.next_section per spoken sentence, timed to dur_sec):
#   1 loophole   : S and Z sit at opposite edges, each its own crisp feature-bar
#                  profile; the central distance meter reads high (DISTINCT).
#   2 two sounds : spotlight S and Z and their distinct profiles; rest dims.
#   3 collapse   : both profiles melt into one identical flat gray profile; a faint
#                  "≈" appears; the distance meter free-falls to near zero (BLURRED).
#   4 failure    : flash the tiny separation number; verdict BLURRED with a
#                  "close on average" punchline beneath.
#   5 lock snap  : the PHONEME READER box appears center; its padlock shackle snaps
#                  shut and a snowflake/FROZEN tag lights in one synchronized click.
#   6 splinter   : blurry bars feed through the reader and splinter back into the
#                  opposite crisp S and Z profiles; the needle surges to DECODABLE.
#   7 decodable  : reader emits clean S and Z; one pure-white check pops; recap line
#                  settles: "frozen recognizer · decodable, not just close." Poster hold.
#
# CUT vs the old scene (those details belong to stage 32 / stage 29):
#   - the dense top-strip spec text (LayerNorm→Conv1d→Linear)
#   - the "+1.0 · CTC" loss-weight label
#   - the persistent live numeric phoneme-distance readout competing during the snap
from manim import *
from emg_style import *

WHITE = "#ffffff"


def vec_bars(values, w=0.20, gap=0.07, unit=1.15, c=INK, op=1.0):
    """A column-vector drawn as horizontal bars (no LaTeX)."""
    bars = VGroup()
    for v in values:
        bars.add(Rectangle(
            width=max(0.05, abs(v) * unit), height=w,
            stroke_width=0, fill_color=c, fill_opacity=op,
        ))
    bars.arrange(DOWN, buff=gap, aligned_edge=LEFT)
    return bars


def snowflake(c=INK, r=0.12, sw=2.0):
    """A tiny 6-spoke snowflake glyph (freeze cue)."""
    g = VGroup()
    for k in range(6):
        a = k * PI / 3
        d = np.array([np.cos(a), np.sin(a), 0]) * r
        g.add(Line(-d, d, stroke_color=c, stroke_width=sw))
        tip = d * 0.55
        for sgn in (+1, -1):
            ba = a + sgn * PI / 4
            bd = np.array([np.cos(ba), np.sin(ba), 0]) * (r * 0.34)
            g.add(Line(tip, tip + bd, stroke_color=c, stroke_width=sw))
    return g


class HonestyLock(Scene):
    def construct(self):
        seed()

        WHITE = "#ffffff"

        # ---- shared geometry ----------------------------------------------
        labA = serif("S", 58, INK).move_to([-5.4, 1.05, 0])
        labB = serif("Z", 58, INK).move_to([5.4, -1.05, 0])
        subA = mono("voiceless", 13, INK_FAINT).next_to(labA, DOWN, buff=0.16)
        subB = mono("voiced", 13, INK_FAINT).next_to(labB, DOWN, buff=0.16)

        valsA = [0.95, 0.20, 0.80, 0.35, 0.70, 0.15]
        valsB = [0.15, 0.85, 0.25, 0.90, 0.30, 0.95]

        def build_vecA(vals, c=INK, op=1.0):
            v = vec_bars(vals, c=c, op=op)
            v.next_to(labA, RIGHT, buff=0.42).set_y(labA.get_y())
            return v

        def build_vecB(vals, c=INK, op=1.0):
            v = vec_bars(vals, c=c, op=op)
            for b in v:
                b.align_to(v.get_right(), RIGHT)
            v.next_to(labB, LEFT, buff=0.42).set_y(labB.get_y())
            return v

        vecA = build_vecA(valsA)
        vecB = build_vecB(valsB)

        # central vertical distance meter
        SEP_DISTINCT, SEP_BLUR, SEP_DECODE = 0.92, 0.05, 0.90
        sep = ValueTracker(SEP_DISTINCT)
        MTR_X, MTR_Y, MTR_H, MTR_W = 0.0, 0.05, 3.0, 0.42
        m_bottom = MTR_Y - MTR_H / 2 + 0.06
        m_inner_h = MTR_H - 0.12

        meter_track = RoundedRectangle(
            corner_radius=0.20, width=MTR_W, height=MTR_H,
            stroke_color=INK_GHOST, stroke_width=1.6, fill_opacity=0,
        ).move_to([MTR_X, MTR_Y, 0])
        meter_lbl = mono("phoneme\ndistance", 13, INK_FAINT)
        meter_lbl.move_to([MTR_X, MTR_Y + MTR_H / 2 + 0.42, 0])
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

        def make_needle():
            v = max(0.0, min(1.0, sep.get_value()))
            y = m_bottom + m_inner_h * v
            return Line([MTR_X - MTR_W / 2 - 0.14, y, 0],
                        [MTR_X + MTR_W / 2 + 0.14, y, 0],
                        stroke_color=INK, stroke_width=2.4)
        needle = always_redraw(make_needle)

        # bottom takeaway: verdict word + the (quiet) live number
        bar_y = -3.0
        VERD_X, SEPNUM_X = -1.7, 0.6
        verdict = mono("DISTINCT", 24, INK).move_to([VERD_X, bar_y, 0])
        sep_num = num(f"{sep.get_value():.2f}", 22, INK_DIM).move_to([SEPNUM_X, bar_y, 0])
        sep_num.add_updater(lambda m: m.become(
            num(f"{sep.get_value():.2f}", 22, INK_DIM).move_to([SEPNUM_X, bar_y, 0])))

        # =================================================================
        # BEAT 1 — LOOPHOLE (~0.84s): distinct pose, meter high (DISTINCT).
        # =================================================================
        self.next_section("loophole")
        self.play(
            FadeIn(labA, shift=RIGHT * 0.2), FadeIn(labB, shift=LEFT * 0.2),
            FadeIn(subA), FadeIn(subB),
            FadeIn(vecA, shift=RIGHT * 0.1), FadeIn(vecB, shift=LEFT * 0.1),
            FadeIn(meter_lbl), Create(meter_track),
            FadeIn(tick_hi), FadeIn(tick_lo),
            FadeIn(meter_fill), FadeIn(needle),
            FadeIn(verdict), FadeIn(sep_num),
            run_time=0.6,
        )
        self.wait(0.24)

        # =================================================================
        # BEAT 2 — TWO SOUNDS (~1.69s): spotlight S/Z + profiles; rest dims.
        # =================================================================
        self.next_section("two_sounds")
        self.play(
            Indicate(vecA, color=INK, scale_factor=1.08),
            Indicate(vecB, color=INK, scale_factor=1.08),
            labA.animate.set_opacity(1.0), labB.animate.set_opacity(1.0),
            meter_track.animate.set_stroke(opacity=0.4),
            meter_lbl.animate.set_opacity(0.4),
            tick_hi.animate.set_opacity(0.4),
            tick_lo.animate.set_opacity(0.4),
            run_time=0.7,
        )
        self.wait(0.99)

        # =================================================================
        # BEAT 3 — COLLAPSE (~2.02s): both melt to one flat gray; "≈"; meter falls.
        # =================================================================
        self.next_section("collapse")
        blur = [0.52, 0.50, 0.55, 0.49, 0.53, 0.50]
        vecA_blur = build_vecA(blur, c=INK_FAINT, op=0.7)
        vecB_blur = build_vecB(blur, c=INK_FAINT, op=0.7)
        approx = mono("≈", 46, INK_DIM).move_to([MTR_X, MTR_Y + 1.4, 0])
        verdict_blur = mono("BLURRED", 24, INK_DIM).move_to(verdict)

        self.play(
            Transform(vecA, vecA_blur),
            Transform(vecB, vecB_blur),
            sep.animate.set_value(SEP_BLUR),
            FadeOut(verdict, scale=0.9), FadeIn(verdict_blur, scale=1.05),
            FadeIn(approx, scale=0.6),
            meter_track.animate.set_stroke(opacity=0.7),
            meter_lbl.animate.set_opacity(0.7),
            run_time=1.35,
        )
        verdict = verdict_blur
        self.wait(0.67)

        # =================================================================
        # BEAT 4 — FAILURE (~2.06s): flash the separation number; punchline.
        # =================================================================
        self.next_section("failure")
        punch = mono("close on average — neither sound, unreadable as either",
                     17, INK_FAINT).move_to([0.0, -3.62, 0])
        sep_num.set_color(INK)
        self.play(
            Flash(sep_num, color=INK, line_length=0.16, num_lines=12,
                  flash_radius=0.45),
            Indicate(verdict, color=INK, scale_factor=1.1),
            FadeIn(punch, shift=UP * 0.08),
            run_time=0.85,
        )
        self.wait(1.21)

        # =================================================================
        # BEAT 5 — LOCK SNAP (~2.2s): reader + padlock; shackle snaps shut;
        # snowflake/FROZEN lights in one synchronized click. Dim everything else.
        # =================================================================
        self.next_section("lock_snap")
        # slide the meter aside and quiet it so the reader owns center; freeze the
        # live number so it rides quietly (no competing readout during the snap).
        self.play(
            FadeOut(approx), FadeOut(punch),
            FadeOut(sep_num),
            meter_track.animate.set_stroke(opacity=0.3).shift(LEFT * 1.95),
            meter_lbl.animate.set_opacity(0.3).shift(LEFT * 1.95),
            tick_hi.animate.set_opacity(0.3).shift(LEFT * 1.95),
            tick_lo.animate.set_opacity(0.3).shift(LEFT * 1.95),
            vecA.animate.set_opacity(0.4), vecB.animate.set_opacity(0.4),
            verdict.animate.set_opacity(0.35),
            run_time=0.5,
        )
        sep_num.clear_updaters()
        MTR_X = -1.95  # rebind meter visuals to the shifted x

        reader = RoundedRectangle(
            corner_radius=0.14, width=2.9, height=2.2,
            stroke_color=INK, stroke_width=2.2, fill_color=BG, fill_opacity=1,
        ).move_to([0.55, 0.30, 0])
        reader_lbl = mono("PHONEME\nREADER", 19, INK).move_to(
            reader.get_center() + UP * 0.40)

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

        flake = snowflake(INK, r=0.13).move_to([0.05, 2.55, 0])
        frozen_tag = mono("FROZEN", 16, INK).next_to(flake, RIGHT, buff=0.18)
        frozen_grp = VGroup(flake, frozen_tag).move_to([0.55, 2.55, 0])

        self.play(Create(reader), FadeIn(reader_lbl), run_time=0.5)
        self.play(FadeIn(body), FadeIn(keyhole),
                  TransformFromCopy(shackle, shackle_open), run_time=0.4)
        self.remove(shackle_open)
        self.add(shackle_open)

        # THE SNAP — synchronized: shackle drops, click flash, snowflake + FROZEN.
        self.play(
            Transform(shackle_open, shackle),
            Flash(keyhole, color=INK, line_length=0.16, num_lines=12,
                  flash_radius=0.42),
            FadeIn(flake, scale=0.5),
            FadeIn(frozen_tag, shift=UP * 0.08),
            run_time=0.55,
        )
        self.wait(0.25)

        # =================================================================
        # BEAT 6 — SPLINTER APART (~0.6s): blurry bars feed through, splinter back
        # into opposite crisp profiles; needle SURGES to DECODABLE.
        # =================================================================
        self.next_section("splinter")
        anchA = vecA.get_right() + RIGHT * 0.05
        anchB = vecB.get_left() + LEFT * 0.05
        flowA = Line(anchA, reader.get_left() + UP * 0.5,
                     stroke_color=INK_FAINT, stroke_width=1.6)
        flowB = Line(anchB, reader.get_right() + DOWN * 0.5,
                     stroke_color=INK_FAINT, stroke_width=1.6)

        crispA = build_vecA(valsA, c=INK)
        crispB = build_vecB(valsB, c=INK)
        verdict_dec = mono("DECODABLE", 24, INK).move_to([VERD_X, bar_y, 0])

        self.play(
            Create(flowA), Create(flowB),
            ReplacementTransform(vecA, crispA),
            ReplacementTransform(vecB, crispB),
            sep.animate.set_value(SEP_DECODE),
            FadeOut(verdict, scale=0.9), FadeIn(verdict_dec, scale=1.05),
            reader.animate.set_stroke(opacity=0.55),
            reader_lbl.animate.set_opacity(0.55),
            run_time=0.6,
        )
        verdict = verdict_dec

        # =================================================================
        # BEAT 7 — DECODABLE (~3.15s): reader emits clean S and Z; one white check;
        # recap line settles. Poster hold.
        # =================================================================
        self.next_section("decodable")
        outS = serif("S", 36, INK).move_to([2.95, 1.45, 0])
        outZ = serif("Z", 36, INK).move_to([2.95, -0.85, 0])
        outU = Line(reader.get_right() + UP * 0.42, outS.get_left() + LEFT * 0.1,
                    stroke_color=INK_FAINT, stroke_width=1.8)
        outD = Line(reader.get_right() + DOWN * 0.42, outZ.get_left() + LEFT * 0.1,
                    stroke_color=INK_FAINT, stroke_width=1.8)
        self.play(
            Create(outU), Create(outD),
            FadeIn(outS, shift=RIGHT * 0.1), FadeIn(outZ, shift=RIGHT * 0.1),
            run_time=0.55,
        )

        check = serif("✓", 34, WHITE).move_to([4.15, 0.30, 0])
        glowing = glow(check.copy())
        self.add(glowing)
        self.play(
            Indicate(crispA, color=INK, scale_factor=1.1),
            Indicate(crispB, color=INK, scale_factor=1.1),
            Indicate(meter_fill, color=WHITE, scale_factor=1.06),
            FadeIn(check, scale=0.6),
            glowing.animate.set_opacity(0.0),
            run_time=0.85,
        )
        self.remove(glowing)

        # freeze live visuals so the poster is rock-steady
        meter_fill.clear_updaters()
        needle.clear_updaters()

        rule = Line([-6.0, -3.42, 0], [6.0, -3.42, 0],
                    stroke_color=INK_GHOST, stroke_width=1.2)
        recap_line = mono(
            "frozen recognizer   ·   decodable, not just close",
            17, INK_DIM).move_to([0.0, -3.66, 0])
        self.play(Create(rule), FadeIn(recap_line, shift=UP * 0.1), run_time=0.5)
        self.wait(1.25)
