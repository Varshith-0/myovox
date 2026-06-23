# b20_binding_constraint.py — "The honest ceiling"
#
# The aha: the reranker is a brilliant EDITOR, but an editor can only reorder the
# sentences already on the desk — it can never write a new one. When the right
# word is absent from every candidate (because it was never in the per-frame
# SOUNDS), no language model on earth can conjure it. So WER levels off at 18.53,
# and the true binding constraint is the ACOUSTIC sound-error (~20.9%), not the
# chooser. Progress needs sharper ears, not a smarter chooser.
#
# Three persistent zones (3b1b: pose -> build -> transform -> name):
#   TOP   (y~+3.0): carry-over from rerank — "THE CHOOSER" + the n-best pool,
#                   a hovering hand/caret that picks.
#   CENTER(-1.4..+2.2): the editor's desk. The chooser picks correctly on many
#                   (WER counter settles 18.53). Then ONE hard sentence: zoom into
#                   the per-frame sounds, the true word's slot is GHOSTED/EMPTY in
#                   every candidate; the hand reaches and finds nothing — a Cross.
#   BOTTOM(-3.6..-2.4): two gauges side by side — word-error refuses below 18.5,
#                   sound-error holds firm near 20.9 (the ceiling); a faint
#                   "under 10% not reached" line. Resolve to the serif name.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

X_L, X_R = -6.7, 6.7
TOP_Y = 3.12


def tri(angle, c, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def hand_caret(c=INK):
    """A small down-pointing pick marker (the editor's hand / chooser)."""
    return tri(PI, c, 0.95, 0.13)


def candidate_chip(text, fs=18, ink=INK, op=1.0, w=2.6):
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
        # B0 — POSE: carry over the rerank n-best pool + the chooser hand.
        # ==================================================================
        self.next_section("pose")

        top1 = mono("THE CHOOSER", 24, INK_DIM, w=BOLD).move_to([0, TOP_Y, 0])
        top2 = mono("a 7B model reads the n-best list and picks the best line",
                    16, INK_FAINT).move_to([0, TOP_Y - 0.46, 0])
        rule = Line([X_L, TOP_Y - 0.74, 0], [X_R, TOP_Y - 0.74, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.4)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)

        # the editor metaphor, stated once on the left rail.
        editor = mono("like an editor who can only\n"
                      "reorder the lines on the desk", 14, INK_FAINT)
        editor.move_to([-4.45, 1.7, 0])
        if editor.get_left()[0] < X_L + 0.1:
            editor.next_to([X_L + 0.1, 1.7, 0], RIGHT, buff=0).set_y(1.7)

        # the n-best pool of candidate lines (center-left desk).
        cand_texts = [
            "she sells sea shells",
            "she sels see shells",
            "she sails sea shells",
            "she sells she shells",
        ]
        chips = VGroup(*[candidate_chip(t, 17, INK_DIM, 0.92, 4.7) for t in cand_texts])
        chips.arrange(DOWN, buff=0.26).move_to([-0.1, 0.55, 0])
        chip_title = mono("n-best list", 15, INK_FAINT).next_to(chips, UP, buff=0.26)

        self.play(FadeIn(editor, shift=RIGHT * 0.08), run_time=0.4)
        self.play(FadeIn(chip_title, shift=DOWN * 0.06),
                  LaggedStart(*[FadeIn(c, shift=RIGHT * 0.14) for c in chips],
                              lag_ratio=0.12), run_time=0.7)

        # the chooser hand hovers above the pool.
        hand = hand_caret(INK).next_to(chips[0], LEFT, buff=0.45)
        hand_lbl = mono("picks", 13, INK_FAINT).next_to(hand, UP, buff=0.1)
        self.play(FadeIn(hand, shift=DOWN * 0.1), FadeIn(hand_lbl), run_time=0.34)

        # ==================================================================
        # B1 — BUILD: it picks correctly on many; WER counter settles 18.53.
        # ==================================================================
        self.next_section("settle")

        # live WER readout parked top-right of the desk.
        wer = ValueTracker(26.14)
        wer_at = np.array([4.95, 1.9, 0])
        wer_read = counter(wer, fmt=lambda v: f"{v:.2f}%", s=34, c=INK, at=wer_at)
        wer_tag = mono("word error", 14, INK_DIM)
        wer_tag.add_updater(lambda m: m.next_to(wer_read, UP, buff=0.12))
        self.add(wer_read, wer_tag)
        self.play(FadeIn(wer_read), FadeIn(wer_tag), run_time=0.34)

        # the hand sweeps down the pool and lands on the correct (1st) line;
        # the WER ticks down to 18.53 as it makes good picks.
        picked = chips[0]
        for c in (chips[3], chips[2], chips[1]):
            self.play(hand.animate.next_to(c, LEFT, buff=0.45),
                      hand_lbl.animate.next_to(hand, UP, buff=0.1).set_x(
                          hand.get_x()),
                      run_time=0.22, rate_func=linear)
        self.play(hand.animate.next_to(picked, LEFT, buff=0.45),
                  hand_lbl.animate.next_to(picked, LEFT, buff=0.45).shift(UP * 0.4),
                  run_time=0.22)
        # christen the correct pick: bright box + WER lands.
        pick_box = picked[0].copy().set_stroke(INK, width=2.4, opacity=1.0)
        self.play(Create(pick_box),
                  picked[1].animate.set_color(INK).set_opacity(1.0),
                  wer.animate.set_value(18.53),
                  run_time=0.6)
        good_lbl = mono("picks correctly on most sentences", 15, INK_FAINT)
        good_lbl.next_to(chips, DOWN, buff=0.3)
        self.play(FadeIn(good_lbl, shift=UP * 0.08), run_time=0.34)
        self.wait(0.15)

        # ==================================================================
        # B2 — TRANSFORM: one hard sentence. Zoom into the per-frame sounds —
        #      the correct word is ABSENT from every candidate. Hand finds none.
        # ==================================================================
        self.next_section("absent")

        wer.set_value(18.53)
        wer_read.clear_updaters()
        wer_tag.clear_updaters()

        # clear the desk; keep the WER readout (retired to the corner) + top frame.
        desk = VGroup(editor, chip_title, chips, hand, hand_lbl, good_lbl, pick_box)
        self.play(FadeOut(desk, shift=LEFT * 0.2),
                  wer_read.animate.scale(0.8).move_to([5.7, 2.75, 0]),
                  wer_tag.animate.set_opacity(0.0),
                  run_time=0.45)
        self.remove(wer_tag)
        corner_wer_tag = mono("WER", 12, INK_FAINT).next_to(wer_read, LEFT, buff=0.14)
        self.add(corner_wer_tag)

        hard_cap = mono("but on the hardest sentence …", 18, INK_DIM).move_to([0, 2.05, 0])
        self.play(FadeIn(hard_cap, shift=DOWN * 0.08), run_time=0.34)

        # the per-frame SOUNDS underneath — a strip of acoustic frames. The slot
        # that should carry the true word is a GHOSTED gap in every guess.
        truth_lbl = mono('truth:  "ocean"', 16, INK_FAINT).move_to([-4.4, 1.25, 0])

        # acoustic posterior strip: 9 frames, each a phoneme guess, but the run
        # that should read OW-SH-AH-N is missing — only a ghost gap sits there.
        frame_labs = ["S", "EH", "?", "?", "?", "?", "?", "L", "Z"]
        sq = 0.5
        cells = VGroup()
        texts = VGroup()
        for i, l in enumerate(frame_labs):
            ghost = (l == "?")
            box = Square(sq, stroke_color=INK_GHOST,
                         stroke_width=(1.0 if ghost else 1.4),
                         fill_opacity=0)
            if ghost:
                box.set_stroke(opacity=0.4)
            cells.add(box)
            c = INK_GHOST if ghost else INK_DIM
            txt = mono(l, 22, c).move_to(box)
            texts.add(txt)
        cells.arrange(RIGHT, buff=0.14)
        for i, t in enumerate(texts):
            t.move_to(cells[i])
        sounds = VGroup(cells, texts).move_to([0, 0.55, 0])
        for i, t in enumerate(texts):
            t.move_to(cells[i])
        sounds_lbl = mono("per-frame sounds  ·  what the ears heard", 14, INK_FAINT)
        sounds_lbl.next_to(sounds, UP, buff=0.24)

        self.play(FadeIn(truth_lbl, shift=RIGHT * 0.08),
                  LaggedStart(*[Create(b) for b in cells], lag_ratio=0.05),
                  run_time=0.6)
        self.play(LaggedStart(*[FadeIn(t) for t in texts], lag_ratio=0.05),
                  FadeIn(sounds_lbl, shift=DOWN * 0.06), run_time=0.5)

        # bracket the ghost run as "the slot for 'ocean'".
        gap = VGroup(*cells[2:7])
        gap_brace = Brace(gap, DOWN, color=INK_GHOST, buff=0.16).set_stroke(width=1)
        gap_lbl = mono('the sounds for "ocean" were never heard', 15, INK_FAINT)
        gap_lbl.next_to(gap_brace, DOWN, buff=0.14)
        self.play(GrowFromCenter(gap_brace), FadeIn(gap_lbl, shift=UP * 0.06),
                  run_time=0.45)

        # the hand reaches into the gap looking for "ocean" — and finds nothing.
        reach = hand_caret(INK).next_to(gap, UP, buff=0.62)
        reach_lbl = mono('looking for "ocean"', 13, INK_DIM).next_to(reach, UP, buff=0.1)
        self.play(FadeIn(reach_lbl), FadeIn(reach, shift=DOWN * 0.1), run_time=0.3)
        self.play(reach.animate.next_to(gap, UP, buff=0.18), run_time=0.4)
        # a Cross over the empty slot — the single hardest moment.
        cross = Cross(gap, stroke_color=INK, stroke_width=3.0).scale(0.92)
        self.play(Create(cross), run_time=0.4)
        absent = serif("not in any candidate", 26, INK).move_to([0, -1.25, 0])
        self.play(Write(absent), run_time=0.5)
        nolm = mono("no language model can conjure a word the ears never carried",
                    15, INK_FAINT).next_to(absent, DOWN, buff=0.18)
        self.play(FadeIn(nolm, shift=UP * 0.06), run_time=0.34)
        self.wait(0.15)

        # ==================================================================
        # B3 — TWO GAUGES: word-error refuses below 18.5; sound-error holds
        #      firm near 20.9 (the real ceiling). "under 10% not reached".
        # ==================================================================
        self.next_section("gauges")

        # clear the center mechanism; keep the top frame + corner WER.
        center = VGroup(hard_cap, truth_lbl, sounds, sounds_lbl, gap_brace,
                        gap_lbl, reach, reach_lbl, cross, absent, nolm)
        self.play(FadeOut(center, shift=UP * 0.15),
                  FadeOut(wer_read), FadeOut(corner_wer_tag), run_time=0.45)
        self.remove(wer_read, corner_wer_tag)

        gauge_title = mono("the same numbers, side by side", 18, INK_DIM).move_to(
            [0, 2.1, 0])
        self.play(FadeIn(gauge_title, shift=DOWN * 0.08), run_time=0.3)

        # two vertical gauges. Each: a track 0..40, a fill bar, a floor line we
        # cannot cross, a live readout. word-error stuck at 18.5; sound 20.9.
        def make_gauge(x, top_val, floor_val, fill_op, name):
            track_h = 3.0
            top_scale = 35.0  # gauge spans 0..35%
            track = RoundedRectangle(width=0.66, height=track_h, corner_radius=0.08,
                                     stroke_color=INK_GHOST, stroke_width=1.4,
                                     fill_opacity=0).move_to([x, -0.25, 0])
            base_y = track.get_bottom()[1] + 0.05
            top_y = track.get_top()[1] - 0.05

            def y_for(v):
                return base_y + (v / top_scale) * (top_y - base_y)
            fill = Rectangle(width=0.6, height=0.02, stroke_width=0,
                             fill_color=INK, fill_opacity=fill_op)
            fill.move_to([x, base_y + 0.01, 0])
            return track, fill, base_y, y_for, x

        # word-error gauge (left)
        wg_track, wg_fill, wg_base, wg_yfor, wg_x = make_gauge(
            -2.6, 18.53, 18.5, 0.55, "word")
        # sound-error gauge (right) — denser fill, the binding one.
        sg_track, sg_fill, sg_base, sg_yfor, sg_x = make_gauge(
            2.6, 20.9, 20.9, 0.85, "sound")

        wg_name = mono("word error", 15, INK_DIM).next_to(wg_track, UP, buff=0.18)
        sg_name = mono("sound error", 15, INK).next_to(sg_track, UP, buff=0.18)

        # live trackers + readouts under each gauge.
        wgv = ValueTracker(0.0)
        sgv = ValueTracker(0.0)
        wg_read = counter(wgv, fmt=lambda v: f"{v:.2f}", s=26, c=INK,
                          at=[wg_x, -2.15, 0])
        sg_read = counter(sgv, fmt=lambda v: f"{v:.1f}", s=26, c=INK,
                          at=[sg_x, -2.15, 0])
        wg_unit = mono("WER %", 12, INK_FAINT).move_to([wg_x, -2.58, 0])
        sg_unit = mono("PER %", 12, INK_FAINT).move_to([sg_x, -2.58, 0])

        self.play(Create(wg_track), Create(sg_track),
                  FadeIn(wg_name), FadeIn(sg_name),
                  FadeIn(wg_unit), FadeIn(sg_unit), run_time=0.5)
        self.add(wg_read, sg_read)
        self.play(FadeIn(wg_read), FadeIn(sg_read), run_time=0.2)

        # bind fills to trackers.
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

        # fill both gauges to their values.
        self.play(wgv.animate.set_value(18.53), sgv.animate.set_value(20.9),
                  run_time=0.9, rate_func=smooth)

        # the floor lines: where each refuses to drop below.
        wg_floor = DashedLine([wg_x - 0.55, wg_yfor(18.5), 0],
                              [wg_x + 0.55, wg_yfor(18.5), 0],
                              stroke_color=INK_DIM, stroke_width=2.0, dash_length=0.08)
        sg_floor = DashedLine([sg_x - 0.55, sg_yfor(20.9), 0],
                              [sg_x + 0.55, sg_yfor(20.9), 0],
                              stroke_color=INK, stroke_width=2.2, dash_length=0.08)
        wg_floor_lbl = mono("won't drop below 18.5", 13, INK_FAINT).next_to(
            wg_floor, LEFT, buff=0.2)
        if wg_floor_lbl.get_left()[0] < X_L:
            wg_floor_lbl = mono("won't drop below 18.5", 12, INK_FAINT).next_to(
                wg_floor, LEFT, buff=0.16)
        sg_floor_lbl = mono("the ceiling: ~20.9", 13, INK).next_to(
            sg_floor, RIGHT, buff=0.2)
        self.play(Create(wg_floor), Create(sg_floor),
                  FadeIn(wg_floor_lbl, shift=RIGHT * 0.06),
                  FadeIn(sg_floor_lbl, shift=LEFT * 0.06), run_time=0.5)

        # the WER tries to push lower and bounces off the floor (refuses below 18.5).
        self.play(wgv.animate.set_value(15.5), run_time=0.3, rate_func=rush_into)
        self.play(wgv.animate.set_value(18.53), run_time=0.4, rate_func=rush_from)
        self.play(Indicate(wg_floor, scale_factor=1.0, color=WHITE), run_time=0.4)

        # faint "under 10% not reached" marker low on the word gauge.
        ten_y = wg_yfor(10.0)
        ten_line = DashedLine([wg_x - 0.7, ten_y, 0], [sg_x + 0.7, ten_y, 0],
                              stroke_color=INK_GHOST, stroke_width=1.0,
                              dash_length=0.06)
        ten_lbl = mono("under 10% — not reached", 13, INK_GHOST).next_to(
            ten_line, DOWN, buff=0.1).set_x(0)
        self.play(Create(ten_line), FadeIn(ten_lbl), run_time=0.4)

        # ==================================================================
        # B4 — NAME + poster hold: the sound-error gauge is the binding one.
        # ==================================================================
        self.next_section("name")

        for m in (wg_fill, sg_fill):
            m.clear_updaters()

        # highlight the sound gauge as the constraint — the single #fff accent.
        sg_glow = glow(sg_track.copy().set_stroke(WHITE, width=2.0, opacity=0.0))
        self.play(sg_track.animate.set_stroke(WHITE, width=2.4),
                  sg_fill.animate.set_fill(WHITE, 0.9),
                  sg_floor.animate.set_stroke(WHITE, width=2.4),
                  Indicate(VGroup(sg_track, sg_name), scale_factor=1.05, color=WHITE),
                  run_time=0.6)

        name = serif("better ears, not a better chooser", 30, WHITE).move_to(
            [0, 0.95, 0])
        name_g = glow(name)
        sub = mono("the limit is the sound-error, not the language model", 16, INK_DIM)
        sub.next_to(name, DOWN, buff=0.2)
        self.add(name_g)
        self.play(Write(name), run_time=0.6)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.55)
        self.wait(0.6)
