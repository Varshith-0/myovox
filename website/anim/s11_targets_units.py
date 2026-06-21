# S11 — Finer sounds (HuBERT units + blank)
# Goal: a second, finer target (100 units) gives a richer training signal; a
# "blank" marks "no new sound right now." Strict monochrome.
#
# Three-zone full-canvas composition (3b1b: pose -> build -> transform -> name):
#   TOP  (y~+3.0)  CARRY-OVER: a slim ~40-phoneme palette from S10 (K AE T),
#                  dimmed, the continuity anchor; ∅ docks at its right end late.
#   CENTER(-1.6..+2.0) STAR: a 10x10 = 100-unit grid blooms via a sweep; one
#                  coarse phoneme flies down and SHATTERS into a finer cluster;
#                  a big "40 ->100" contrast pulses; a unit timeline gets ∅.
#   BOTTOM(-3.6..-2.4) TAKEAWAY: the training-goal recipe assembles bar by bar:
#                  0.8 unit + 0.1 phone + 0.1 consistency, coupled P(phone|unit).
#   final          a dense, balanced poster holds ~0.6 s.
from manim import *
from emg_style import *


class FinerSounds(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B1 — POSE / CARRY-OVER: slim ~40-phoneme palette across the TOP.
        # =================================================================
        self.next_section("phonemes")

        # 40 small faint cells in a single slim row of 20 x 2 (reads as a strip).
        N_PHON = 40
        phon_cells = VGroup(*[
            Square(0.20, stroke_color=INK_FAINT, stroke_width=1.1, fill_opacity=0)
            for _ in range(N_PHON)
        ]).arrange_in_grid(rows=2, cols=20, buff=0.07)
        phon_cells.move_to(UP * 3.0)

        phon_tag = mono("coarse  ·  ~40 phonemes", 17, INK_FAINT)
        phon_tag.next_to(phon_cells, LEFT, buff=0.4).align_to(phon_cells, UP)

        # A few cells labelled K · AE · T to echo "cat" from S10.
        cat_idx = [0, 1, 2]
        cat_lbls = ["K", "AE", "T"]
        cat_text = VGroup()
        for i, lab in zip(cat_idx, cat_lbls):
            t = mono(lab, 12, INK_DIM).move_to(phon_cells[i])
            cat_text.add(t)

        self.play(
            FadeIn(phon_tag, shift=RIGHT * 0.15),
            LaggedStartMap(FadeIn, phon_cells, lag_ratio=0.02, run_time=0.6),
            run_time=0.6,
        )
        # glow the "cat" cells briefly, then settle to a labelled dim state.
        self.play(
            *[phon_cells[i].animate.set_stroke(INK_DIM, width=1.4) for i in cat_idx],
            LaggedStartMap(FadeIn, cat_text, lag_ratio=0.15),
            run_time=0.45,
        )

        # Pick one future-split phoneme cell — lift it to pure INK with a glow.
        pick = phon_cells[26]
        pick_glow = glow(pick.copy().set_stroke(INK, 2.2).set_fill(INK, 0.18))
        self.play(
            pick.animate.set_stroke(INK, width=2.4).set_fill(INK, 0.18),
            FadeIn(pick_glow),
            run_time=0.4,
        )

        # the whole top strip stays present but dims to push focus downward.
        top_strip = VGroup(phon_tag, phon_cells, cat_text, pick_glow)

        # =================================================================
        # B2 — BLOOM 40 -> 100: center 10x10 unit grid + sweep + contrast.
        # =================================================================
        self.next_section("bloom")

        # 100 unit cells, right-of-centre, occupying y ~ -1.6 .. +1.7.
        unit_grid = VGroup(*[
            Square(0.30, stroke_color=INK_FAINT, stroke_width=0.9, fill_opacity=0)
            for _ in range(100)
        ]).arrange_in_grid(rows=10, cols=10, buff=0.06)
        unit_grid.move_to(RIGHT * 2.55 + UP * 0.15)

        unit_tag = mono("fine  ·  100 units", 18, INK_DIM)
        unit_tag.next_to(unit_grid, DOWN, buff=0.28)

        # Big "40 ->100" serif contrast, between top origin and the grid.
        contrast = VGroup(
            serif("40", 64, INK_DIM),
            mono("->", 30, INK_FAINT),
            serif("100", 64, INK),
        ).arrange(RIGHT, buff=0.30)
        contrast.move_to(LEFT * 4.0 + UP * 1.55)

        # build the contrast: 40 dim, arrow, then a bright 100 spawned from it.
        self.play(
            top_strip.animate.set_opacity(0.55),
            FadeIn(contrast[0], shift=UP * 0.1),
            FadeIn(contrast[1]),
            run_time=0.45,
        )
        # keep the picked cell bright even after dimming the strip.
        pick.set_opacity(1.0)
        # spawn the bright 100 AND bloom the grid together.
        self.play(
            TransformFromCopy(contrast[0], contrast[2]),
            LaggedStartMap(FadeIn, unit_grid, lag_ratio=0.004, run_time=0.85),
            run_time=0.85,
        )

        # a bright sweep wipes top->bottom, lighting each row alive.
        sweep = Rectangle(
            width=unit_grid.width + 0.25, height=0.30,
            stroke_width=0, fill_color=INK, fill_opacity=0.18,
        ).move_to(unit_grid.get_top() + UP * 0.06)
        self.add(sweep)
        # a traveling pulse on the arrow, in sync with the sweep.
        pulse = Dot(radius=0.06, color=INK).move_to(contrast[1].get_left())
        self.add(pulse)
        self.play(
            sweep.animate.move_to(unit_grid.get_bottom() + DOWN * 0.06),
            pulse.animate.move_to(contrast[1].get_right()),
            run_time=0.65, rate_func=linear,
        )
        self.remove(sweep, pulse)
        self.play(FadeIn(unit_tag, shift=UP * 0.1), run_time=0.35)

        # =================================================================
        # B3 — SHATTER / SPLIT: one phoneme cracks into a finer cluster.
        # =================================================================
        self.next_section("shatter")

        # target cluster: a 2x2 block + one stray, lifted in the grid.
        cluster_idx = [33, 34, 43, 44]
        stray_idx = 56
        targets = VGroup(*[unit_grid[i] for i in cluster_idx])
        stray = unit_grid[stray_idx]
        all_split = VGroup(*targets, stray)

        # a flying copy of the picked phoneme arcs down to the center-left.
        flyer = pick.copy().set_fill(INK, 0.22).set_stroke(INK, 2.4)
        landing = LEFT * 1.4 + DOWN * 0.15
        self.add(flyer)
        self.play(
            flyer.animate.move_to(landing).scale(1.15),
            top_strip.animate.set_opacity(0.34),  # push focus to the shatter
            run_time=0.55, rate_func=rate_functions.ease_in_out_sine,
        )

        # the fan of connectors opens from the flyer to the cluster (lagged).
        connectors = VGroup(*[
            Line(flyer.get_right(), t.get_center(),
                 stroke_color=INK_GHOST, stroke_width=1.6)
            for t in all_split
        ])
        self.play(LaggedStartMap(Create, connectors, lag_ratio=0.12, run_time=0.5))

        # the cluster flares to pure INK and Indicate-pulses (the only #fff peak).
        self.play(
            *[t.animate.set_stroke(INK, 2.0).set_fill(INK, 0.85) for t in all_split],
            run_time=0.35,
        )
        self.play(Indicate(all_split, scale_factor=1.18, color=INK), run_time=0.45)
        # settle the cluster to a lit-but-readable state.
        self.play(*[t.animate.set_fill(INK, 0.32).set_stroke(INK, 1.6) for t in all_split],
                  run_time=0.25)

        split_note = mono("one phoneme  ->  several finer units", 19, INK_DIM)
        split_note.next_to(unit_grid, UP, buff=0.30).set_x(unit_grid.get_x())
        ssl_note = mono(
            "self-supervised · from unlabeled audio", 15, INK_FAINT)
        ssl_note.next_to(unit_tag, DOWN, buff=0.16)
        self.play(FadeIn(split_note, shift=UP * 0.1),
                  FadeIn(ssl_note, shift=UP * 0.1), run_time=0.45)

        # =================================================================
        # B4 — BLANK ∅: read-head sweeps a unit timeline; ∅ blooms in gaps.
        # =================================================================
        self.next_section("blank")

        # a one-row timeline tucked along the grid's baseline (center-left band).
        n = 9
        gap_idx = {3, 6}
        tl = VGroup(*[
            Square(0.40, stroke_color=INK_FAINT, stroke_width=1.3, fill_opacity=0)
            for _ in range(n)
        ]).arrange(RIGHT, buff=0.10)
        tl.move_to(LEFT * 3.3 + DOWN * 1.1)

        seq = [12, 12, 87, None, 41, 9, None, 63, 5]
        tl_ids = VGroup()
        for f, v in zip(tl, seq):
            if v is None:
                continue
            tl_ids.add(num(v, 16, INK_DIM).move_to(f))

        tl_label = mono("unit per time-slice", 15, INK_FAINT).next_to(tl, UP, buff=0.22)

        self.play(
            FadeIn(tl_label, shift=UP * 0.1),
            LaggedStartMap(FadeIn, tl, lag_ratio=0.06, run_time=0.45),
            LaggedStartMap(FadeIn, tl_ids, lag_ratio=0.05, run_time=0.45),
        )

        head = Rectangle(
            width=0.46, height=0.56, stroke_color=INK, stroke_width=2.2,
            fill_color=INK, fill_opacity=0.06,
        ).move_to(tl[0])
        blanks = {gi: serif("∅", 26, INK).move_to(tl[gi]) for gi in sorted(gap_idx)}

        self.play(FadeIn(head, scale=0.85), run_time=0.18)
        for i in range(1, n):
            anims = [head.animate.move_to(tl[i])]
            run = 0.08
            if i in gap_idx:
                anims.append(FadeIn(blanks[i], scale=0.6))
                run = 0.22
            self.play(*anims, run_time=run, rate_func=smooth)
        self.play(FadeOut(head, scale=0.85), run_time=0.18)

        # one ∅ travels up to dock at the right end of the TOP phoneme palette.
        blank_dock = serif("∅", 22, INK).move_to(phon_cells[-1].get_center() + RIGHT * 0.55)
        plus1 = mono("+1", 13, INK_DIM).next_to(blank_dock, UP, buff=0.08)
        flyer_blank = blanks[3].copy()
        self.play(
            top_strip.animate.set_opacity(0.7),
            flyer_blank.animate.move_to(blank_dock).scale(22 / 26),
            FadeIn(plus1, shift=DOWN * 0.05),
            run_time=0.6, rate_func=rate_functions.ease_in_out_sine,
        )
        self.add(blank_dock)
        self.remove(flyer_blank)

        blank_def = mono("blank ∅  =  no new sound right now", 17, INK_DIM)
        blank_def.next_to(tl, DOWN, buff=0.30)
        self.play(FadeIn(blank_def, shift=UP * 0.1), run_time=0.4)

        # =================================================================
        # B5 — RECIPE / NAME IT: the training goal assembles in the BOTTOM.
        # =================================================================
        self.next_section("recipe")

        # clear the center-left timeline + its blanks + split notes so the bottom
        # is the focus, but KEEP the grid, contrast, cluster, top strip + ∅ dock.
        # also tuck the ssl tag up tight under the grid so the bottom is clear.
        timeline_blanks = VGroup(*blanks.values())
        clear_center = VGroup(tl, tl_ids, tl_label, blank_def, split_note,
                              timeline_blanks)
        self.play(
            FadeOut(clear_center, shift=DOWN * 0.15),
            ssl_note.animate.scale(0.92).next_to(unit_tag, DOWN, buff=0.12),
            run_time=0.45,
        )

        BAR_W = 3.0  # bottom recipe lives on the LEFT, clear of the grid

        def bar_row(w, name, emphasis):
            ink = INK if emphasis else INK_DIM
            fill_o = 0.9 if emphasis else 0.42
            track = RoundedRectangle(
                corner_radius=0.07, width=BAR_W, height=0.30,
                stroke_color=INK_GHOST, stroke_width=1.1, fill_opacity=0,
            )
            fill = RoundedRectangle(
                corner_radius=0.07, width=BAR_W * w, height=0.30,
                stroke_width=0, fill_color=INK, fill_opacity=fill_o,
            ).align_to(track, LEFT)
            wt = mono(f"{w:.1f}", 20, ink).next_to(track, LEFT, buff=0.26)
            nm = mono(name, 19, ink).next_to(track, RIGHT, buff=0.26)
            return VGroup(wt, track, fill, nm)

        r_unit = bar_row(0.8, "unit", True)
        r_phon = bar_row(0.1, "phoneme", False)
        r_cons = bar_row(0.1, "consistency", False)
        bars = VGroup(r_unit, r_phon, r_cons).arrange(DOWN, buff=0.22, aligned_edge=LEFT)

        goal_label = mono("training goal", 16, INK_FAINT).next_to(
            bars, UP, buff=0.24, aligned_edge=LEFT)
        goal_block = VGroup(goal_label, bars)
        # park the recipe in the bottom-LEFT zone, clear of the grid on the right.
        goal_block.move_to(LEFT * 3.55 + DOWN * 3.0, aligned_edge=LEFT)

        # tracks + labels in first, then fills grow from the left.
        for r in (r_unit, r_phon, r_cons):
            r[2].save_state()
            r[2].stretch(0.001, 0, about_edge=LEFT)
        self.play(
            FadeIn(goal_label, shift=UP * 0.08),
            LaggedStart(*[FadeIn(VGroup(r[0], r[1], r[3]))
                          for r in (r_unit, r_phon, r_cons)],
                        lag_ratio=0.18, run_time=0.55),
        )
        self.play(LaggedStart(*[Restore(r[2]) for r in (r_unit, r_phon, r_cons)],
                              lag_ratio=0.18, run_time=0.6))
        self.play(Indicate(VGroup(r_unit[2], r_unit[3]), scale_factor=1.08, color=INK),
                  run_time=0.45)

        # coupling: a fixed table keeps the two heads consistent.
        link = CurvedArrow(
            r_phon[1].get_right() + RIGHT * 0.05,
            r_unit[1].get_right() + RIGHT * 0.05,
            angle=-TAU / 5, stroke_color=INK_FAINT, stroke_width=1.5, tip_length=0.13,
        )
        couple = VGroup(
            mono("P(phone | unit)", 15, INK_DIM),
            mono("a fixed table keeps the two heads consistent", 13, INK_FAINT),
        ).arrange(DOWN, buff=0.07, aligned_edge=LEFT)
        # coupling caption to the right of the bars; clamp so it never clips x=7.1.
        couple.next_to(bars, RIGHT, buff=0.65).set_y(bars.get_y() + 0.05)
        if couple.get_right()[0] > 6.9:
            couple.shift(LEFT * (couple.get_right()[0] - 6.9))
        self.play(Create(link), FadeIn(couple, shift=UP * 0.08), run_time=0.55)

        # =================================================================
        # FINAL HOLD — balanced poster across the full canvas.
        # =================================================================
        self.wait(0.6)
