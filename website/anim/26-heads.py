# S15 — Three outputs (heads)
# The reader (encoder) finishes ONE snapshot and emits THREE answers at once.
# The lesson is a contrast: two confident SNAPS (votes for text) then a deliberate
# NON-snap (a 1024-number stream that imitates a voice).
#
# Locked 9-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 slice in      reader at far left; one 5-tick slice glides in, left face flashes
#   2 three answers branches fan + 3 white pulses race + 3 empty panels materialize
#   3 units vote    top ~100-bin strip grows, ONE bar SNAPS to #fff; rail 1/3
#   4 sounds vote   middle ~40-bin strip snaps -> serif "AE"; load-bearing; rail 2/3
#   5 now the third top+middle dim to 0.3; projection 1024-D vector writes in
#   6 never picks   deliberate NON-snap: glow blooms + "not a vote"; rail 3/3
#   7 thousand nums "1024 numbers" detail brightens; "not for reading text" band
#   8 imitate voice band completes "—it exists to imitate a real voice"; punchline
#   9 why it matters lead arrow + "the teacher voice"; rows restore to dense frame
from manim import *
from style import *


class ThreeHeads(Scene):
    def construct(self):
        seed()

        TOP_Y  = 3.05
        RULE_Y = 2.55
        RAIL_Y = -3.25
        ROW_Y  = [1.92, 0.0, -1.92]   # Units / Phonemes / Projection
        ENC_X  = -5.15

        # ---- TOP continuity strip (context only, never above INK_DIM) ----------
        recap_stack = VGroup(*[
            Line(LEFT * 0.32, RIGHT * 0.32, stroke_color=INK_GHOST, stroke_width=2.2)
            for _ in range(4)
        ]).arrange(DOWN, buff=0.08).move_to(np.array([-6.05, TOP_Y, 0]))
        recap_lab = mono("the reader · Conformer", 17, INK_FAINT)
        recap_lab.next_to(recap_stack, RIGHT, buff=0.28).set_y(TOP_Y)
        frame_line = mono("one snapshot in  →  three answers out", 18, INK_FAINT)
        frame_line.move_to(np.array([3.55, TOP_Y, 0]))
        rule = Line(LEFT * 6.6, RIGHT * 6.6, stroke_color=LINE, stroke_width=1.4)
        rule.set_y(RULE_Y)

        # ---- reader block --------------------------------------------------
        enc = RoundedRectangle(
            corner_radius=0.12, width=1.85, height=2.6,
            stroke_color=INK, stroke_width=2.2, fill_color=INK_GHOST, fill_opacity=0.10,
        ).move_to(np.array([ENC_X, 0, 0]))
        enc_label = mono("reader", 23, INK_DIM).move_to(enc.get_center() + UP * 0.16)
        enc_sub = mono("encoder", 14, INK_FAINT).move_to(enc.get_center() + DOWN * 0.20)

        # ---- bottom rail ---------------------------------------------------
        rail_l, rail_r = -5.0, 5.0
        rail_track = Line(np.array([rail_l, RAIL_Y, 0]), np.array([rail_r, RAIL_Y, 0]),
                          stroke_color=INK_GHOST, stroke_width=3)
        seg_w = (rail_r - rail_l) / 3.0
        rail_ticks = VGroup(*[
            Line(np.array([rail_l + i * seg_w, RAIL_Y - 0.10, 0]),
                 np.array([rail_l + i * seg_w, RAIL_Y + 0.10, 0]),
                 stroke_color=INK_FAINT, stroke_width=2)
            for i in range(4)
        ])
        rail_lab = mono("answers per snapshot", 16, INK_FAINT)
        rail_lab.move_to(np.array([rail_l, RAIL_Y + 0.32, 0])).align_to(rail_track, LEFT)

        prog = ValueTracker(0)
        counter_at = np.array([rail_r, RAIL_Y, 0])
        rail_counter = num("0/3", 26, INK_DIM).move_to(counter_at).align_to(rail_track, RIGHT)
        rail_counter.add_updater(lambda m: m.become(
            num(f"{int(round(prog.get_value()))}/3", 26, INK_DIM)
        ).move_to(counter_at).align_to(rail_track, RIGHT))
        rail_fill = Line(np.array([rail_l, RAIL_Y, 0]), np.array([rail_l, RAIL_Y, 0]),
                         stroke_color=INK, stroke_width=4.5)
        def fill_updater(m):
            x = rail_l + (prog.get_value() / 3.0) * (rail_r - rail_l)
            m.put_start_and_end_on(np.array([rail_l, RAIL_Y, 0]),
                                   np.array([max(rail_l + 1e-3, x), RAIL_Y, 0]))
        rail_fill.add_updater(fill_updater)

        # =================================================================
        # BEAT 1 (1.47s) — the reader finishes one snapshot.
        # =================================================================
        self.next_section("slice_in")
        # context frame established quietly, then the slice arrives + flash.
        self.play(
            LaggedStart(*[Create(l) for l in recap_stack], lag_ratio=0.12),
            FadeIn(recap_lab), FadeIn(frame_line, shift=LEFT * 0.1),
            Create(rule), Create(enc), FadeIn(enc_label, shift=UP * 0.12),
            run_time=0.55,
        )
        self.add(rail_track, rail_ticks, rail_lab, rail_fill, rail_counter)
        ticks = VGroup(*[
            Line(ORIGIN, RIGHT * 0.42, stroke_color=INK_FAINT, stroke_width=3)
            for _ in range(5)
        ]).arrange(DOWN, buff=0.11).next_to(enc, LEFT, buff=0.32)
        slice_lab = mono("one snapshot", 14, INK_FAINT).next_to(ticks, UP, buff=0.16)
        slice_lab.align_to(np.array([-6.9, 0, 0]), LEFT)  # keep the longer label on-frame
        self.play(
            FadeIn(enc_sub),
            LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.10),
            FadeIn(slice_lab), run_time=0.45,
        )
        self.play(
            ticks.animate.set_opacity(0.30).shift(RIGHT * 0.22),
            Flash(enc.get_left() + RIGHT * 0.1, color=INK, line_length=0.16,
                  num_lines=10, flash_radius=0.42, run_time=0.45),
            run_time=0.45,
        )
        self.wait(0.02)

        # =================================================================
        # BEAT 2 (2.14s) — it gives three answers at once (fan, one event).
        # =================================================================
        self.next_section("three_answers")
        rows_meta = [
            ("Units",      "100 + blank",  ROW_Y[0]),
            ("Phonemes",   "~40 + blank",  ROW_Y[1]),
            ("Projection", "1024 numbers", ROW_Y[2]),
        ]
        bx = -1.55
        box_w, box_h = 2.9, 1.12
        boxes, titles, details, branches = [], [], [], []
        start = enc.get_right() + RIGHT * 0.04
        for name, detail, y in rows_meta:
            box = RoundedRectangle(
                corner_radius=0.10, width=box_w, height=box_h,
                stroke_color=INK, stroke_width=1.8, fill_color=BG, fill_opacity=1.0,
            ).move_to(np.array([bx, y, 0]))
            t = serif(name, 28, INK).move_to(box.get_center() + UP * 0.26)
            d = mono(detail, 19, INK_DIM).move_to(box.get_center() + DOWN * 0.26)
            br = Line(start, box.get_left(), stroke_color=INK_FAINT, stroke_width=2.0)
            boxes.append(box); titles.append(t); details.append(d); branches.append(br)
        boxes = VGroup(*boxes); titles = VGroup(*titles)
        details = VGroup(*details); branches = VGroup(*branches)

        self.play(LaggedStart(*[Create(b) for b in branches],
                              lag_ratio=0.15, run_time=0.7))
        pulses = VGroup(*[Dot(radius=0.06, color="#ffffff").move_to(br.get_start())
                          for br in branches])
        self.add(pulses)
        self.play(LaggedStart(*[
            MoveAlongPath(d, br, rate_func=rate_functions.ease_in_out_sine)
            for d, br in zip(pulses, branches)
        ], lag_ratio=0.18, run_time=0.75))
        self.remove(pulses)
        self.play(
            LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.12),
            LaggedStart(*[FadeIn(t) for t in titles], lag_ratio=0.12),
            LaggedStart(*[FadeIn(d) for d in details], lag_ratio=0.12),
            run_time=0.6,
        )
        self.wait(0.08)

        out_x = boxes[0].get_right()[0] + 0.5
        out_w, out_h = 2.55, 0.66

        def softmax_strip(n, peak_idx, y, width=out_w, height=out_h):
            bars = VGroup()
            heights = np.random.rand(n) * 0.16 + 0.03
            heights[peak_idx] = 1.0
            bw = width / n
            for i, h in enumerate(heights):
                is_peak = (i == peak_idx)
                bar = Rectangle(
                    width=bw * 0.74, height=max(h * height, 0.015), stroke_width=0,
                    fill_color=INK if is_peak else INK_FAINT,
                    fill_opacity=0.85 if is_peak else 0.50,
                )
                bar.move_to(np.array([out_x + i * bw + bw / 2,
                                      y - height / 2 + bar.height / 2, 0]))
                bars.add(bar)
            return bars

        # =================================================================
        # BEAT 3 (1.58s) — the first is a vote over a hundred fine units.
        # =================================================================
        self.next_section("units_vote")
        u_peak = 17
        units_strip = softmax_strip(100, u_peak, ROW_Y[0])
        cap_units = mono("a vote over 100 fine units", 15, INK_FAINT)
        cap_units.next_to(units_strip, UP, buff=0.12, aligned_edge=LEFT)
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in units_strip], lag_ratio=0.008),
            FadeIn(cap_units, shift=UP * 0.06), run_time=0.6,
        )
        self.play(
            units_strip[u_peak].animate.set_fill("#ffffff", opacity=1.0).scale(1.18, about_edge=DOWN),
            Indicate(units_strip[u_peak], scale_factor=1.0, color="#ffffff"),
            prog.animate.set_value(1), run_time=0.6,
        )
        self.wait(0.1)

        # =================================================================
        # BEAT 4 (3.01s) — the second is a vote over forty sounds (load-bearing).
        # =================================================================
        self.next_section("sounds_vote")
        p_peak = 23
        phon_strip = softmax_strip(40, p_peak, ROW_Y[1])
        cap_phon = mono("a vote over ~40 sounds", 15, INK_FAINT)
        cap_phon.next_to(phon_strip, UP, buff=0.12, aligned_edge=LEFT)
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in phon_strip], lag_ratio=0.01),
            FadeIn(cap_phon, shift=UP * 0.06), run_time=0.65,
        )
        self.play(
            phon_strip[p_peak].animate.set_fill("#ffffff", opacity=1.0).scale(1.18, about_edge=DOWN),
            Indicate(phon_strip[p_peak], scale_factor=1.0, color="#ffffff"),
            run_time=0.55,
        )
        win_lab = serif("AE", 30, "#ffffff").next_to(phon_strip, RIGHT, buff=0.30).set_y(ROW_Y[1])
        bar_copy = phon_strip[p_peak].copy()
        self.play(ReplacementTransform(bar_copy, win_lab), prog.animate.set_value(2), run_time=0.6)
        # load-bearing: brighten the phoneme box stroke + a quiet tag.
        ph_box, ph_branch = boxes[1], branches[1]
        load_tag = VGroup(
            mono("everything", 17, INK),
            mono("downstream", 17, INK),
            mono("relies on this", 17, INK_DIM),
        ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        load_tag.next_to(win_lab, RIGHT, buff=0.45).set_y(ROW_Y[1])
        self.play(
            ph_box.animate.set_stroke(width=3.4, color="#ffffff"),
            ph_branch.animate.set_stroke(width=3.2, color=INK),
            FadeIn(load_tag, shift=LEFT * 0.15), run_time=0.7,
        )
        self.wait(0.7)

        units_group = VGroup(units_strip, cap_units)
        phon_group = VGroup(phon_strip, win_lab, cap_phon)

        # =================================================================
        # BEAT 5 (1.05s) — now watch the third (spotlight moves down).
        # =================================================================
        self.next_section("now_the_third")
        self.play(
            boxes[0].animate.set_opacity(0.3), titles[0].animate.set_opacity(0.3),
            details[0].animate.set_opacity(0.3), branches[0].animate.set_opacity(0.3),
            units_group.animate.set_opacity(0.3),
            ph_box.animate.set_stroke(width=2.4, color=INK).set_opacity(0.3),
            titles[1].animate.set_opacity(0.3), details[1].animate.set_opacity(0.3),
            ph_branch.animate.set_stroke(width=2.0, color=INK_FAINT).set_opacity(0.3),
            phon_group.animate.set_opacity(0.3),
            load_tag.animate.set_opacity(0.0),
            run_time=0.5,
        )
        self.remove(load_tag)
        proj_vals = ["+0.83", "-1.20", "...", "+1.91"]
        proj_nums = VGroup(*[mono(v, 17, INK_DIM) for v in proj_vals]).arrange(RIGHT, buff=0.20)
        proj_brk_l = mono("[", 23, INK_FAINT).next_to(proj_nums, LEFT, buff=0.12)
        proj_brk_r = mono("]", 23, INK_FAINT).next_to(proj_nums, RIGHT, buff=0.12)
        proj_vec = VGroup(proj_brk_l, proj_nums, proj_brk_r)
        proj_vec.set_y(ROW_Y[2]).align_to(np.array([out_x, 0, 0]), LEFT)
        self.play(Write(proj_vec), run_time=0.5)
        self.wait(0.02)

        # =================================================================
        # BEAT 6 (0.84s) — it never picks a winner (deliberate NON-snap).
        # =================================================================
        self.next_section("never_picks")
        proj_glow = glow(proj_vec.copy())
        not_vote = mono("not a vote", 19, INK).next_to(proj_vec, RIGHT, buff=0.6).set_y(ROW_Y[2])
        self.play(
            FadeIn(proj_glow),
            FadeIn(not_vote, shift=LEFT * 0.12),
            prog.animate.set_value(3), run_time=0.55,
        )
        prog.set_value(3)
        rail_fill.clear_updaters()
        rail_counter.clear_updaters()
        self.wait(0.1)

        # =================================================================
        # BEAT 7 (2.2s) — a stream of a thousand numbers, not for reading text.
        # =================================================================
        self.next_section("thousand_numbers")
        band_y = -2.66
        not_text = mono("not for reading text", 18, INK).move_to(np.array([0, band_y, 0]))
        self.play(
            details[2].animate.set_opacity(1.0).set_color(INK).scale(1.12),
            Indicate(details[2], scale_factor=1.0, color="#ffffff"),
            run_time=0.6,
        )
        self.play(FadeIn(not_text, shift=UP * 0.1), run_time=0.6)
        self.wait(1.0)

        # =================================================================
        # BEAT 8 (1.93s) — its only job is to imitate a real human voice.
        # =================================================================
        self.next_section("imitate_voice")
        full_band = VGroup(
            mono("not for reading text", 18, INK_DIM),
            mono("—", 18, INK_FAINT),
            mono("it exists to imitate a real voice", 18, INK),
        ).arrange(RIGHT, buff=0.24).move_to(np.array([0, band_y, 0]))
        self.play(ReplacementTransform(not_text, full_band), run_time=0.55)
        punch = VGroup(
            mono("two are votes for text", 21, INK_DIM),
            mono("·", 21, INK_FAINT),
            mono("one imitates", 21, INK_DIM),
            mono("a voice", 21, INK),
        ).arrange(RIGHT, buff=0.22).move_to(np.array([0, RAIL_Y, 0]))
        voice_glow = glow(punch[3].copy())
        self.add(voice_glow)
        self.play(
            FadeOut(rail_fill), FadeOut(rail_counter), FadeOut(rail_lab),
            rail_track.animate.set_stroke(opacity=0.0),
            rail_ticks.animate.set_stroke(opacity=0.0),
            FadeIn(punch, shift=UP * 0.1),
            voice_glow.animate.set_opacity(0.0),
            run_time=0.7,
        )
        self.remove(voice_glow)
        self.wait(0.6)

        # =================================================================
        # BEAT 9 (1.03s) — here is why that matters (hand-off to teacher voice).
        # =================================================================
        self.next_section("why_matters")
        lead_stem = Line(np.array([5.05, band_y, 0]), np.array([6.15, band_y, 0]),
                         stroke_color=INK, stroke_width=3.5)
        lead_head = Triangle(stroke_width=0, fill_color=INK, fill_opacity=1.0)
        lead_head.scale(0.10).rotate(-PI / 2).move_to(np.array([6.25, band_y, 0]))
        next_hint = mono("the teacher voice", 12, INK_FAINT).next_to(lead_stem, UP, buff=0.10)
        self.play(
            # restore the three rows to a balanced dense frame, phoneme kept marked.
            boxes[0].animate.set_opacity(1.0), titles[0].animate.set_opacity(1.0),
            details[0].animate.set_opacity(1.0), branches[0].animate.set_opacity(0.7),
            units_group.animate.set_opacity(1.0),
            ph_box.animate.set_stroke(width=2.8, color="#ffffff").set_opacity(1.0),
            titles[1].animate.set_opacity(1.0), details[1].animate.set_opacity(1.0),
            ph_branch.animate.set_opacity(1.0), phon_group.animate.set_opacity(1.0),
            Create(lead_stem), FadeIn(lead_head), FadeIn(next_hint),
            run_time=0.6,
        )
        self.wait(0.62)
