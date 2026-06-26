# b20_binding_constraint.py — "The honest ceiling"
#
# The aha: the chooser is brilliant, but it can only pick from the short list of
# guesses it is handed. On the hardest sentences the right word was never in the
# per-frame SOUNDS the reader heard — so no chooser can reach for a word that
# simply is not there. WER levels off near 18.5; the real binding constraint is
# the ACOUSTIC sound-error (~20.9). Progress needs a sharper reader, not a
# smarter chooser.
#
# Locked 7-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 pose      carry-over chooser + n-best list + hovering hand; settle, no motion
#   2 settle    hand lands on the correct line; it brightens; WER lands 18.53
#   3 absent    desk clears; zoom to per-frame SOUNDS for "ocean" — middle gap empty
#   4 reach     hand reaches into the gap; Cross; serif "not in any candidate"
#   5 gauges    two gauges; word-error fills 18.53, dips to 15, bounces off 18.5
#   6 ceiling   spotlight sound-error gauge to pure white; word gauge dims
#   7 name      serif "a sharper reader, not a smarter chooser"
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

X_L, X_R = -6.7, 6.7
TOP_Y = 3.12


def tri(angle, c, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def hand_caret(c=INK):
    """A small down-pointing pick marker (the chooser's hand)."""
    return tri(PI, c, 0.95, 0.13)


def candidate_chip(text, fs=18, ink=INK, op=1.0, w=4.7):
    """A boxed n-best candidate sentence."""
    label = mono(text, fs, ink).set_opacity(op)
    box = SurroundingRectangle(label, color=INK_GHOST, buff=0.16,
                               stroke_width=1.2).set_stroke(opacity=0.0)
    box.set_fill(INK, 0.0)
    box.stretch_to_fit_width(w)
    label.move_to(box.get_center())
    return VGroup(box, label)


class BindingConstraint(Scene):
    def construct(self):
        seed()

        # ==================================================================
        # BEAT 1 — POSE (~1.11s): carry over the chooser + n-best + hand.
        #          Everything calm, nothing new — just settle.
        # ==================================================================
        self.next_section("pose")

        top1 = mono("THE CHOOSER", 24, INK_DIM, w=BOLD).move_to([0, TOP_Y, 0])
        top2 = mono("a model reads the n-best list and picks the best line",
                    15, INK_FAINT).move_to([0, TOP_Y - 0.44, 0])
        rule = Line([X_L, TOP_Y - 0.72, 0], [X_R, TOP_Y - 0.72, 0],
                    stroke_color=LINE, stroke_width=1.2)

        cand_texts = [
            "she sells sea shells",
            "she sels see shells",
            "she sails sea shells",
            "she sells she shells",
        ]
        chips = VGroup(*[candidate_chip(t, 17, INK_DIM, 0.92, 4.7) for t in cand_texts])
        chips.arrange(DOWN, buff=0.28).move_to([-0.1, 0.25, 0])
        chip_title = mono("n-best list", 15, INK_FAINT).next_to(chips, UP, buff=0.3)

        hand = hand_caret(INK).next_to(chips[1], LEFT, buff=0.5)
        hand_lbl = mono("picks", 13, INK_FAINT).next_to(hand, UP, buff=0.1)

        self.play(FadeIn(top1, shift=DOWN * 0.12),
                  FadeIn(top2), Create(rule), run_time=0.45)
        self.play(FadeIn(chip_title, shift=DOWN * 0.06),
                  LaggedStart(*[FadeIn(c, shift=RIGHT * 0.12) for c in chips],
                              lag_ratio=0.1), run_time=0.45)
        self.play(FadeIn(hand, shift=DOWN * 0.1), FadeIn(hand_lbl), run_time=0.21)
        self.wait(0.05)

        # ==================================================================
        # BEAT 2 — SETTLE (~1.68s): hand lands on the correct line; it
        #          brightens; the WER readout settles to 18.53.
        # ==================================================================
        self.next_section("settle")

        wer = ValueTracker(26.14)
        wer_at = np.array([5.0, 1.95, 0])
        wer_read = counter(wer, fmt=lambda v: f"{v:.2f}%", s=34, c=INK, at=wer_at)
        wer_tag = mono("word error", 14, INK_DIM)
        wer_tag.add_updater(lambda m: m.next_to(wer_read, UP, buff=0.12))
        self.add(wer_read, wer_tag)
        self.play(FadeIn(wer_read), FadeIn(wer_tag), run_time=0.3)

        # one decisive land on the correct (1st) line.
        picked = chips[0]
        self.play(hand.animate.next_to(picked, LEFT, buff=0.5),
                  hand_lbl.animate.next_to(picked, LEFT, buff=0.5).shift(UP * 0.38),
                  run_time=0.45)
        pick_box = picked[0].copy().set_stroke(INK, width=2.4, opacity=1.0)
        self.play(Create(pick_box),
                  picked[1].animate.set_color(INK).set_opacity(1.0),
                  wer.animate.set_value(18.53),
                  run_time=0.7)
        self.wait(0.2)

        # ==================================================================
        # BEAT 3 — ABSENT (~1.86s): desk clears; zoom to the per-frame SOUNDS
        #          for "ocean" — the middle run of frames is a ghosted gap.
        # ==================================================================
        self.next_section("absent")

        wer.set_value(18.53)
        wer_read.clear_updaters()
        wer_tag.clear_updaters()

        # dim the top chooser strip to faint; clear the desk; retire WER to corner.
        desk = VGroup(chip_title, chips, hand, hand_lbl, pick_box)
        top_strip = VGroup(top1, top2, rule)
        self.play(FadeOut(desk, shift=LEFT * 0.2),
                  top_strip.animate.set_opacity(0.28),
                  wer_read.animate.scale(0.78).move_to([5.7, 2.5, 0]),
                  wer_tag.animate.set_opacity(0.0),
                  run_time=0.5)
        self.remove(wer_tag)
        corner_wer = mono("WER", 12, INK_FAINT).next_to(wer_read, LEFT, buff=0.14)
        self.add(corner_wer)

        truth_lbl = mono('truth:  "ocean"', 17, INK_DIM).move_to([-4.2, 1.35, 0])

        # acoustic posterior strip: the run that should read OW-SH-AH-N is missing.
        frame_labs = ["S", "EH", "?", "?", "?", "?", "?", "L", "Z"]
        sq = 0.5
        cells = VGroup()
        texts = VGroup()
        for l in frame_labs:
            ghost = (l == "?")
            box = Square(sq, stroke_color=INK_GHOST,
                         stroke_width=(1.0 if ghost else 1.4), fill_opacity=0)
            if ghost:
                box.set_stroke(opacity=0.4)
            cells.add(box)
            txt = mono(l, 22, INK_GHOST if ghost else INK_DIM)
            texts.add(txt)
        cells.arrange(RIGHT, buff=0.14)
        sounds = VGroup(cells, texts).move_to([0, 0.45, 0])
        for i, t in enumerate(texts):
            t.move_to(cells[i])
        sounds_lbl = mono("per-frame sounds  ·  what the ears heard", 14, INK_FAINT)
        sounds_lbl.next_to(sounds, UP, buff=0.24)

        self.play(FadeIn(truth_lbl, shift=RIGHT * 0.08),
                  LaggedStart(*[Create(b) for b in cells], lag_ratio=0.05),
                  run_time=0.6)
        self.play(LaggedStart(*[FadeIn(t) for t in texts], lag_ratio=0.05),
                  FadeIn(sounds_lbl, shift=DOWN * 0.06), run_time=0.5)

        # name the empty gap as the missing sounds of "ocean" — one beat.
        gap = VGroup(*cells[2:7])
        gap_brace = Brace(gap, DOWN, color=INK_GHOST, buff=0.16).set_stroke(width=1)
        gap_lbl = mono('the sounds for "ocean" were never heard', 15, INK_FAINT)
        gap_lbl.next_to(gap_brace, DOWN, buff=0.14)
        self.play(GrowFromCenter(gap_brace), FadeIn(gap_lbl, shift=UP * 0.06),
                  run_time=0.45)
        self.wait(0.05)

        # ==================================================================
        # BEAT 4 — REACH (~1.95s): the hand reaches into the empty gap and a
        #          Cross strikes it; serif "not in any candidate" writes in.
        # ==================================================================
        self.next_section("reach")

        reach = hand_caret(INK).next_to(gap, UP, buff=0.6)
        reach_lbl = mono('reaching for "ocean"', 13, INK_DIM).next_to(reach, UP, buff=0.1)
        self.play(FadeIn(reach_lbl), FadeIn(reach, shift=DOWN * 0.1), run_time=0.4)
        self.play(reach.animate.next_to(gap, UP, buff=0.16), run_time=0.5)
        cross = Cross(gap, stroke_color=INK, stroke_width=3.0).scale(0.92)
        self.play(Create(cross), run_time=0.4)
        absent = serif("not in any candidate", 28, INK).move_to([0, -1.45, 0])
        self.play(Write(absent), run_time=0.55)
        self.wait(0.1)

        # ==================================================================
        # BEAT 5 — GAUGES (~1.98s): two gauges; word-error fills 18.53, dips
        #          toward 15, then bounces back off its 18.5 floor.
        # ==================================================================
        self.next_section("gauges")

        center = VGroup(truth_lbl, sounds, sounds_lbl, gap_brace, gap_lbl,
                        reach, reach_lbl, cross, absent)
        self.play(FadeOut(center, shift=UP * 0.15),
                  FadeOut(wer_read), FadeOut(corner_wer),
                  run_time=0.45)
        self.remove(wer_read, corner_wer)

        # two vertical gauges, each 0..35 scale.
        def make_gauge(x, fill_op):
            track_h = 3.0
            track = RoundedRectangle(width=0.66, height=track_h, corner_radius=0.08,
                                     stroke_color=INK_GHOST, stroke_width=1.4,
                                     fill_opacity=0).move_to([x, -0.2, 0])
            base_y = track.get_bottom()[1] + 0.05
            top_y = track.get_top()[1] - 0.05

            def y_for(v):
                return base_y + (v / 35.0) * (top_y - base_y)
            fill = Rectangle(width=0.6, height=0.02, stroke_width=0,
                             fill_color=INK, fill_opacity=fill_op)
            fill.move_to([x, base_y + 0.01, 0])
            return track, fill, base_y, y_for, x

        wg_track, wg_fill, wg_base, wg_yfor, wg_x = make_gauge(-2.6, 0.55)
        sg_track, sg_fill, sg_base, sg_yfor, sg_x = make_gauge(2.6, 0.85)

        wg_name = mono("word error", 15, INK_DIM).next_to(wg_track, UP, buff=0.2)
        sg_name = mono("sound error", 15, INK_DIM).next_to(sg_track, UP, buff=0.2)

        wgv = ValueTracker(0.0)
        sgv = ValueTracker(0.0)
        wg_read = counter(wgv, fmt=lambda v: f"{v:.2f}", s=26, c=INK,
                          at=[wg_x, -2.1, 0])
        sg_read = counter(sgv, fmt=lambda v: f"{v:.1f}", s=26, c=INK,
                          at=[sg_x, -2.1, 0])
        wg_unit = mono("WER %", 12, INK_FAINT).move_to([wg_x, -2.52, 0])
        sg_unit = mono("PER %", 12, INK_FAINT).move_to([sg_x, -2.52, 0])

        self.play(Create(wg_track), Create(sg_track),
                  FadeIn(wg_name), FadeIn(sg_name),
                  FadeIn(wg_unit), FadeIn(sg_unit), run_time=0.45)
        self.add(wg_read, sg_read)

        def bind_fill(fill, tracker, base_y, y_for, x):
            def upd(m):
                v = tracker.get_value()
                h = max(0.02, y_for(v) - base_y)
                m.stretch_to_fit_height(h)
                m.move_to([x, base_y + h / 2, 0])
            fill.add_updater(upd)
        bind_fill(wg_fill, wgv, wg_base, wg_yfor, wg_x)
        bind_fill(sg_fill, sgv, sg_base, sg_yfor, sg_x)
        self.add(wg_fill, sg_fill)

        # both fill to their values.
        self.play(wgv.animate.set_value(18.53), sgv.animate.set_value(20.9),
                  run_time=0.6, rate_func=smooth)

        # word-error floor line at 18.5.
        wg_floor = DashedLine([wg_x - 0.55, wg_yfor(18.5), 0],
                              [wg_x + 0.55, wg_yfor(18.5), 0],
                              stroke_color=INK_DIM, stroke_width=2.0, dash_length=0.08)
        wg_floor_lbl = mono("floor 18.5", 12, INK_FAINT).next_to(
            wg_floor, LEFT, buff=0.18)
        self.play(Create(wg_floor), FadeIn(wg_floor_lbl, shift=RIGHT * 0.06),
                  run_time=0.35)

        # WER tries to push lower, then bounces back off the floor.
        self.play(wgv.animate.set_value(15.0), run_time=0.3, rate_func=rush_into)
        self.play(wgv.animate.set_value(18.53), run_time=0.35, rate_func=rush_from)
        self.wait(0.05)

        # ==================================================================
        # BEAT 6 — CEILING (~1.7s): spotlight the sound-error gauge to pure
        #          white; its ceiling line ignites; the word gauge dims.
        # ==================================================================
        self.next_section("ceiling")

        for m in (wg_fill, sg_fill):
            m.clear_updaters()

        sg_floor = DashedLine([sg_x - 0.55, sg_yfor(20.9), 0],
                              [sg_x + 0.55, sg_yfor(20.9), 0],
                              stroke_color=WHITE, stroke_width=2.4, dash_length=0.08)
        sg_ceil_lbl = mono("the ceiling: ~20.9", 13, WHITE).next_to(
            sg_floor, RIGHT, buff=0.2)

        word_group = VGroup(wg_track, wg_fill, wg_name, wg_read, wg_unit,
                            wg_floor, wg_floor_lbl)
        self.play(
            word_group.animate.set_opacity(0.28),
            sg_track.animate.set_stroke(WHITE, width=2.4),
            sg_fill.animate.set_fill(WHITE, 0.92),
            sg_name.animate.set_color(WHITE),
            run_time=0.7,
        )
        self.play(Create(sg_floor),
                  FadeIn(sg_ceil_lbl, shift=LEFT * 0.06),
                  Indicate(VGroup(sg_track, sg_name), scale_factor=1.05, color=WHITE),
                  run_time=0.7)
        self.wait(0.1)

        # ==================================================================
        # BEAT 7 — NAME (~1.69s): the serif payoff under the sound gauge.
        # ==================================================================
        self.next_section("name")

        sg_focus = VGroup(sg_track, sg_fill, sg_name, sg_read, sg_unit,
                          sg_floor, sg_ceil_lbl)
        self.play(sg_focus.animate.shift(UP * 0.15), run_time=0.3)

        name = serif("a sharper reader,\nnot a smarter chooser", 30, WHITE)
        name.move_to([0, -3.0, 0])
        name_g = glow(name)
        self.add(name_g)
        self.play(Write(name), run_time=0.7)
        self.play(Indicate(name, scale_factor=1.05, color=WHITE), run_time=0.4)
        self.wait(0.4)
