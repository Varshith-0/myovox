# S15 — Three outputs (heads)
# The reader (encoder) splits ONE snapshot into THREE answers. Composed full-bleed
# in three horizontal zones:
#   TOP   — a quiet continuity strip linking back to S14 (the reader · Conformer,
#           shown there as a 4-layer stack) + the framing "one slice in -> three out".
#   CENTER— the mechanism: the reader block at far-left fans (one event) into three
#           stacked panels, each animating its own NATIVE output:
#             Units      — a ~100-bin softmax strip; one bar SNAPS to pure #fff (a vote)
#             Phonemes   — a ~40-bin strip; one bar snaps to #fff and morphs into "AE"
#                          (the load-bearing output: everything downstream uses this)
#             Projection — a 1024-D vector that pointedly does NOT snap; it just GLOWS
#                          (not for reading text — it exists to imitate a real voice)
#   BOTTOM— a running rail tallying "answers per slice: 0/3 -> 3/3" that resolves into
#           the one-line punchline "two are votes for text · one imitates a voice".
#
# The reveal: two confident SNAPS, then a deliberate NON-snap — that contrast IS the idea.
# Strict monochrome — emphasis via opacity, stroke width, scale, glow; #fff only for peaks.
from manim import *
from emg_style import *


class ThreeHeads(Scene):
    def construct(self):
        seed()

        # =================================================================
        # ZONE FRAME — geometry constants so the three zones never collide.
        # =================================================================
        TOP_Y   = 3.05      # continuity strip
        RULE_Y  = 2.55      # hairline rule sealing the top zone
        RAIL_Y  = -3.25     # bottom progress rail
        ROW_Y   = [1.92, 0.0, -1.92]   # Units / Phonemes / Projection
        ENC_X   = -5.15     # reader block, far left, vertically centred

        # =================================================================
        # TOP STRIP — context only (never brighter than INK_DIM).
        #   left:  ghosted S14 recap — a faint 4-layer stack glyph + label.
        #   right: the framing line "one slice in -> three answers out".
        # =================================================================
        recap_stack = VGroup(*[
            Line(LEFT * 0.32, RIGHT * 0.32, stroke_color=INK_GHOST, stroke_width=2.2)
            for _ in range(4)
        ]).arrange(DOWN, buff=0.08)
        recap_stack.move_to(np.array([-6.05, TOP_Y, 0]))
        recap_lab = mono("the reader · Conformer", 17, INK_FAINT)
        recap_lab.next_to(recap_stack, RIGHT, buff=0.28).set_y(TOP_Y)

        frame_line = mono("one slice in  →  three answers out", 18, INK_FAINT)
        frame_line.move_to(np.array([3.55, TOP_Y, 0]))

        rule = Line(LEFT * 6.6, RIGHT * 6.6, stroke_color=LINE, stroke_width=1.4)
        rule.set_y(RULE_Y)

        self.play(
            LaggedStartMap(Create, recap_stack, lag_ratio=0.12, run_time=0.5),
            FadeIn(recap_lab, run_time=0.5),
        )
        self.play(
            FadeIn(frame_line, shift=LEFT * 0.15, run_time=0.45),
            Create(rule, run_time=0.5),
        )

        # =================================================================
        # CENTER — the reader block at far left, plus one slice arriving.
        # =================================================================
        enc = RoundedRectangle(
            corner_radius=0.12, width=1.85, height=2.6,
            stroke_color=INK, stroke_width=2.2, fill_color=INK_GHOST, fill_opacity=0.10,
        ).move_to(np.array([ENC_X, 0, 0]))
        enc_label = mono("reader", 23, INK_DIM).move_to(enc.get_center() + UP * 0.16)
        enc_sub = mono("encoder", 14, INK_FAINT).move_to(enc.get_center() + DOWN * 0.20)
        self.play(Create(enc), FadeIn(enc_label, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(enc_sub, run_time=0.3))

        # one input slice — a short stack of 5 ticks gliding into the left face.
        ticks = VGroup(*[
            Line(ORIGIN, RIGHT * 0.42, stroke_color=INK_FAINT, stroke_width=3)
            for _ in range(5)
        ]).arrange(DOWN, buff=0.11)
        ticks.next_to(enc, LEFT, buff=0.32)
        slice_lab = mono("one slice", 14, INK_FAINT).next_to(ticks, UP, buff=0.16)
        self.play(
            LaggedStartMap(Create, ticks, lag_ratio=0.10, run_time=0.45),
            FadeIn(slice_lab, run_time=0.4),
        )
        self.play(
            ticks.animate.set_opacity(0.30).shift(RIGHT * 0.22),
            Flash(enc.get_left() + RIGHT * 0.1, color=INK, line_length=0.16,
                  num_lines=10, flash_radius=0.42, run_time=0.55),
            run_time=0.5,
        )

        # =================================================================
        # BOTTOM RAIL — drawn empty, counter at "0/3".
        # =================================================================
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
        rail_lab = mono("answers per slice", 16, INK_FAINT)
        rail_lab.next_to(rail_track, LEFT, buff=0.0).move_to(
            np.array([rail_l, RAIL_Y + 0.32, 0])).align_to(rail_track, LEFT)

        prog = ValueTracker(0)   # 0..3 answers landed
        counter_at = np.array([rail_r, RAIL_Y, 0])
        rail_counter = num("0/3", 26, INK_DIM).move_to(counter_at).align_to(rail_track, RIGHT)
        rail_counter.add_updater(lambda m: m.become(
            num(f"{int(round(prog.get_value()))}/3", 26, INK_DIM)
        ).move_to(counter_at).align_to(rail_track, RIGHT))

        # the filled portion of the rail tracks prog (0..3 -> rail_l..rail_r).
        rail_fill = Line(np.array([rail_l, RAIL_Y, 0]), np.array([rail_l, RAIL_Y, 0]),
                         stroke_color=INK, stroke_width=4.5)
        def fill_updater(m):
            x = rail_l + (prog.get_value() / 3.0) * (rail_r - rail_l)
            m.put_start_and_end_on(np.array([rail_l, RAIL_Y, 0]),
                                   np.array([max(rail_l + 1e-3, x), RAIL_Y, 0]))
        rail_fill.add_updater(fill_updater)

        self.play(
            Create(rail_track),
            LaggedStartMap(Create, rail_ticks, lag_ratio=0.08, run_time=0.5),
            FadeIn(rail_lab, run_time=0.4),
        )
        self.add(rail_fill, rail_counter)

        # =================================================================
        # BEAT 1 — the fan: three branches + three panels, one event.
        # =================================================================
        rows_meta = [
            ("Units",      "100 + ∅",      ROW_Y[0]),
            ("Phonemes",   "~40 + ∅",      ROW_Y[1]),
            ("Projection", "1024 numbers", ROW_Y[2]),
        ]
        bx = -1.55          # panel-box centre x
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

        # branches fan out (lagged), reading as one event.
        self.play(LaggedStartMap(Create, branches, lag_ratio=0.15, run_time=0.8))

        # three Dot pulses launch in a tight LaggedStart -> the "fan".
        pulses = VGroup(*[Dot(radius=0.06, color="#ffffff").move_to(br.get_start())
                          for br in branches])
        self.add(pulses)
        self.play(
            LaggedStart(*[
                MoveAlongPath(d, br, rate_func=rate_functions.ease_in_out_sine)
                for d, br in zip(pulses, branches)
            ], lag_ratio=0.18, run_time=0.9),
        )
        self.remove(pulses)
        # panels materialize where the pulses landed.
        self.play(
            LaggedStartMap(Create, boxes, lag_ratio=0.12, run_time=0.7),
            LaggedStartMap(FadeIn, titles, lag_ratio=0.12, run_time=0.7),
            LaggedStartMap(FadeIn, details, lag_ratio=0.12, run_time=0.7),
        )

        # =================================================================
        # BEAT 2 — native outputs, top-to-bottom, each in its own language.
        # =================================================================
        out_x = boxes[0].get_right()[0] + 0.5   # common left edge for outputs
        out_w, out_h = 2.55, 0.66

        def softmax_strip(n, peak_idx, y, width=out_w, height=out_h):
            bars = VGroup()
            heights = np.random.rand(n) * 0.16 + 0.03
            heights[peak_idx] = 1.0
            bw = width / n
            for i, h in enumerate(heights):
                is_peak = (i == peak_idx)
                bar = Rectangle(
                    width=bw * 0.74, height=max(h * height, 0.015),
                    stroke_width=0,
                    fill_color=INK if is_peak else INK_FAINT,
                    fill_opacity=0.85 if is_peak else 0.50,
                )
                bar.move_to(np.array([out_x + i * bw + bw / 2,
                                      y - height / 2 + bar.height / 2, 0]))
                bars.add(bar)
            return bars

        # --- Units: ~100-bin strip (60 bars for "100-ish density"); one vote. ---
        u_peak = 17
        units_strip = softmax_strip(60, u_peak, ROW_Y[0])
        cap_units = mono("a vote over 100 fine units", 15, INK_FAINT)
        cap_units.next_to(units_strip, UP, buff=0.12, aligned_edge=LEFT)
        self.play(
            LaggedStartMap(GrowFromEdge, units_strip, edge=DOWN, lag_ratio=0.008, run_time=0.6),
            FadeIn(cap_units, shift=UP * 0.06, run_time=0.5),
        )
        # ONE bar SNAPS to pure #fff — the vote commits.
        self.play(
            units_strip[u_peak].animate.set_fill("#ffffff", opacity=1.0).scale(1.18, about_edge=DOWN),
            Indicate(units_strip[u_peak], scale_factor=1.0, color="#ffffff"),
            run_time=0.55,
        )
        self.play(prog.animate.set_value(1), run_time=0.45, rate_func=rate_functions.ease_out_quad)

        # --- Phonemes: ~40-bin strip; winning bar snaps and morphs into "AE". ---
        p_peak = 23
        phon_strip = softmax_strip(40, p_peak, ROW_Y[1])
        cap_phon = mono("a vote over ~40 sounds", 15, INK_FAINT)
        cap_phon.next_to(phon_strip, UP, buff=0.12, aligned_edge=LEFT)
        self.play(
            LaggedStartMap(GrowFromEdge, phon_strip, edge=DOWN, lag_ratio=0.01, run_time=0.6),
            FadeIn(cap_phon, shift=UP * 0.06, run_time=0.5),
        )
        # snap the winner to #fff...
        self.play(
            phon_strip[p_peak].animate.set_fill("#ffffff", opacity=1.0).scale(1.18, about_edge=DOWN),
            Indicate(phon_strip[p_peak], scale_factor=1.0, color="#ffffff"),
            run_time=0.5,
        )
        # ...then morph a copy of that bar into the crystallized ARPABET "AE".
        win_lab = serif("AE", 30, "#ffffff")
        win_lab.next_to(phon_strip, RIGHT, buff=0.30).set_y(ROW_Y[1])
        bar_copy = phon_strip[p_peak].copy()
        self.play(ReplacementTransform(bar_copy, win_lab), run_time=0.6)
        self.play(prog.animate.set_value(2), run_time=0.45, rate_func=rate_functions.ease_out_quad)

        # --- Projection: a 1024-D vector that does NOT snap — it GLOWS. ---
        proj_vals = ["+0.83", "-1.20", "...", "+1.91"]
        proj_nums = VGroup(*[mono(v, 17, INK_DIM) for v in proj_vals])
        proj_nums.arrange(RIGHT, buff=0.20)
        proj_brk_l = mono("[", 23, INK_FAINT).next_to(proj_nums, LEFT, buff=0.12)
        proj_brk_r = mono("]", 23, INK_FAINT).next_to(proj_nums, RIGHT, buff=0.12)
        proj_vec = VGroup(proj_brk_l, proj_nums, proj_brk_r)
        proj_vec.set_y(ROW_Y[2]).align_to(np.array([out_x, 0, 0]), LEFT)
        cap_proj = mono("a point in a 1024-D space", 15, INK_FAINT)
        cap_proj.next_to(proj_vec, UP, buff=0.14, aligned_edge=LEFT)
        self.play(
            Write(proj_vec, run_time=0.7),
            FadeIn(cap_proj, shift=UP * 0.06, run_time=0.5),
        )
        # the deliberate NON-snap: no winner — a soft glow blooms instead.
        proj_glow = glow(proj_vec.copy())
        self.play(
            FadeIn(proj_glow, run_time=0.55),
            prog.animate.set_value(3),
            run_time=0.55, rate_func=rate_functions.ease_out_quad,
        )
        prog.set_value(3)
        rail_fill.clear_updaters()
        rail_counter.clear_updaters()

        # groups for later opacity moves
        units_group = VGroup(units_strip, cap_units)
        phon_group = VGroup(phon_strip, win_lab, cap_phon)
        proj_group = VGroup(proj_vec, cap_proj)

        self.wait(0.2)

        # =================================================================
        # BEAT 3 — name it: the phoneme head is load-bearing.
        # =================================================================
        ph_box, ph_branch = boxes[1], branches[1]
        tag = VGroup(
            mono("everything", 18, INK),
            mono("downstream", 18, INK),
            mono("uses this", 18, INK_DIM),
        ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        tag.next_to(win_lab, RIGHT, buff=0.5).set_y(ROW_Y[1])

        self.play(
            boxes[0].animate.set_opacity(0.3), titles[0].animate.set_opacity(0.35),
            details[0].animate.set_opacity(0.35), branches[0].animate.set_opacity(0.3),
            units_group.animate.set_opacity(0.3),
            boxes[2].animate.set_opacity(0.3), titles[2].animate.set_opacity(0.35),
            details[2].animate.set_opacity(0.35), branches[2].animate.set_opacity(0.3),
            proj_group.animate.set_opacity(0.3), proj_glow.animate.set_opacity(0.08),
            ph_box.animate.set_stroke(width=3.4, color="#ffffff"),
            ph_branch.animate.set_stroke(width=3.2, color=INK),
            run_time=0.65,
        )
        pulse = Dot(color="#ffffff", radius=0.07).move_to(ph_branch.get_start())
        self.add(pulse)
        self.play(
            MoveAlongPath(pulse, ph_branch, rate_func=rate_functions.ease_in_out_sine),
            Indicate(VGroup(titles[1], details[1]), scale_factor=1.10, color="#ffffff"),
            run_time=0.6,
        )
        self.remove(pulse)
        self.play(FadeIn(tag, shift=LEFT * 0.2, run_time=0.55))
        self.wait(0.3)

        # =================================================================
        # BEAT 4 — the twist: the third answer is different.
        # =================================================================
        self.play(FadeOut(tag, shift=RIGHT * 0.15, run_time=0.4))
        proj_box, proj_branch = boxes[2], branches[2]

        # ease phoneme emphasis back; restore + brighten the projection row.
        self.play(
            proj_box.animate.set_stroke(width=3.0, color=INK).set_fill(BG, 1.0).set_opacity(1.0),
            proj_branch.animate.set_stroke(width=2.6, color=INK).set_opacity(1.0),
            titles[2].animate.set_opacity(1.0),
            details[2].animate.set_opacity(1.0).set_color(INK),
            proj_group.animate.set_opacity(1.0),
            proj_glow.animate.set_opacity(0.06),
            ph_box.animate.set_stroke(width=2.2, color=INK),
            ph_branch.animate.set_stroke(width=2.0, color=INK_FAINT),
            run_time=0.65,
        )
        # re-bloom the glow, then a short contrast cue to the RIGHT of the vector
        # (one short line per row so it fits inside the frame).
        proj_glow2 = glow(proj_vec.copy())
        not_vote = mono("not a vote", 19, INK).next_to(proj_vec, RIGHT, buff=0.6).set_y(ROW_Y[2])
        self.play(
            FadeIn(not_vote, shift=LEFT * 0.12),
            FadeIn(proj_glow2),
            Indicate(proj_vec, scale_factor=1.08, color="#ffffff"),
            run_time=0.75,
        )

        # the full contrast, as ONE horizontal line in the band just under the
        # panels (full width there), so nothing clips at the frame edge.
        band_y = -2.66
        contrast = VGroup(
            mono("not for reading text", 17, INK),
            mono("—", 17, INK_FAINT),
            mono("it exists to imitate a real voice", 17, INK_DIM),
        ).arrange(RIGHT, buff=0.26)
        contrast.move_to(np.array([0, band_y, 0]))
        # a short lead arrow toward S16 at the far right of that band.
        lead = Arrow(
            np.array([5.0, band_y, 0]), np.array([6.3, band_y, 0]),
            stroke_color=INK, stroke_width=3.5, buff=0.0,
            max_tip_length_to_length_ratio=0.22,
        )
        next_hint = mono("a teacher voice", 12, INK_FAINT).next_to(lead, UP, buff=0.08)
        self.play(
            FadeIn(contrast, shift=UP * 0.1),
            GrowArrow(lead), FadeIn(next_hint),
            run_time=0.6,
        )

        # bottom rail dissolves into the punchline ("imitates a voice" lifts to INK).
        punch = VGroup(
            mono("two are votes for text", 21, INK_DIM),
            mono("·", 21, INK_FAINT),
            mono("one imitates", 21, INK_DIM),
            mono("a voice", 21, INK),
        ).arrange(RIGHT, buff=0.22).move_to(np.array([0, RAIL_Y, 0]))
        self.play(
            FadeOut(rail_fill, run_time=0.4),
            FadeOut(rail_counter, run_time=0.4),
            FadeOut(rail_lab, run_time=0.4),
            rail_track.animate.set_stroke(opacity=0.0),
            rail_ticks.animate.set_stroke(opacity=0.0),
            FadeIn(punch, shift=UP * 0.1, run_time=0.6),
        )

        # =================================================================
        # BEAT 5 — poster: restore all three rows to a balanced dense frame.
        # =================================================================
        self.play(
            units_group.animate.set_opacity(1.0),
            boxes[0].animate.set_opacity(1.0).set_fill(BG, 1.0),
            titles[0].animate.set_opacity(1.0),
            details[0].animate.set_opacity(1.0),
            branches[0].animate.set_opacity(0.7).set_stroke(color=INK_FAINT),
            units_strip[u_peak].animate.set_fill("#ffffff", opacity=1.0),
            # keep phoneme head subtly marked as the load-bearing one
            ph_box.animate.set_stroke(width=2.8, color="#ffffff"),
            ph_branch.animate.set_stroke(width=2.4, color=INK_FAINT).set_opacity(1.0),
            phon_group.animate.set_opacity(1.0),
            run_time=0.7,
        )
        self.wait(0.6)
