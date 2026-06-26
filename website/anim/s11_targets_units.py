# S11 — Finer sounds (HuBERT units + blank)
# Goal: a second, finer target (100 units) gives a richer training signal; a
# "blank" marks "no new sound right now." Strict monochrome.
#
# Beat sheet (7 beats, ~12.0s; one self.next_section per beat):
#   1  carry-over: the slim ~40-sound strip fades in dim, K·AE·T lit, ALONE.
#   2  one sound cell lifts bright + glow, the rest dims — "40 buckets is coarse".
#   3  the 40 -> 100 contrast resolves and the 10x10 unit grid blooms via sweep.
#   4  the lit sound flies down; a connector fan opens to a cluster that flares to
#      pure white — the shatter, the single peak of the scene.
#   5  a unit timeline; a read-head sweeps; ∅ blooms in two empty slices; one ∅
#      docks at the strip's end as "+1".
#   6  a faint forward-teaser "self-supervised · discovered next"; then clear.
#   7  the bottom recipe assembles: 0.8 fine + 0.1 forty + 0.1 consistency, then a
#      curved P(phone | unit) link couples the two heads. Serif payoff + hold.
from manim import *
from emg_style import *


class FinerSounds(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B1 — CARRY-OVER: slim ~40-sound strip across the TOP, ALONE & dim.
        # =================================================================
        self.next_section("forty")

        N_PHON = 40
        phon_cells = VGroup(*[
            Square(0.20, stroke_color=INK_FAINT, stroke_width=1.1, fill_opacity=0)
            for _ in range(N_PHON)
        ]).arrange_in_grid(rows=2, cols=20, buff=0.07)
        phon_cells.move_to(UP * 3.0)

        phon_tag = mono("coarse  ·  ~40 sounds", 17, INK_FAINT)
        phon_tag.next_to(phon_cells, LEFT, buff=0.4).align_to(phon_cells, UP)

        # K · AE · T lit inside the first cells — the carry-over from S10.
        cat_idx = [0, 1, 2]
        cat_lbls = ["K", "AE", "T"]
        cat_text = VGroup()
        for i, lab in zip(cat_idx, cat_lbls):
            cat_text.add(mono(lab, 12, INK_DIM).move_to(phon_cells[i]))

        self.play(
            FadeIn(phon_tag, shift=RIGHT * 0.15),
            LaggedStart(*[FadeIn(c) for c in phon_cells], lag_ratio=0.02),
            run_time=0.55,
        )
        self.play(
            *[phon_cells[i].animate.set_stroke(INK_DIM, width=1.4) for i in cat_idx],
            LaggedStart(*[FadeIn(t) for t in cat_text], lag_ratio=0.15),
            run_time=0.4,
        )
        top_strip = VGroup(phon_tag, phon_cells, cat_text)

        # =================================================================
        # B2 — COARSE: one cell lifts bright + glow; the rest of the strip dims.
        # =================================================================
        self.next_section("coarse")

        pick = phon_cells[26]
        pick_glow = glow(pick.copy().set_stroke(INK, 2.2).set_fill(INK, 0.20))
        # everything except the picked cell dims to ~0.5 to feel "too blunt".
        rest = VGroup(phon_tag, cat_text,
                      *[c for i, c in enumerate(phon_cells) if i != 26])
        self.play(
            rest.animate.set_opacity(0.5),
            pick.animate.set_stroke(INK, width=2.6).set_fill(INK, 0.22),
            FadeIn(pick_glow),
            run_time=0.55,
        )
        coarse_note = mono("many noises rounded into one", 16, INK_FAINT)
        coarse_note.next_to(phon_cells, DOWN, buff=0.30)
        self.play(FadeIn(coarse_note, shift=UP * 0.08), run_time=0.45)
        top_strip.add(pick_glow)
        self.wait(0.35)

        # =================================================================
        # B3 — BLOOM 40 -> 100: contrast resolves + 10x10 grid blooms via sweep.
        # =================================================================
        self.next_section("bloom")

        unit_grid = VGroup(*[
            Square(0.30, stroke_color=INK_FAINT, stroke_width=0.9, fill_opacity=0)
            for _ in range(100)
        ]).arrange_in_grid(rows=10, cols=10, buff=0.06)
        unit_grid.move_to(RIGHT * 2.55 + UP * 0.15)

        unit_tag = mono("fine  ·  100 units", 18, INK_DIM)
        unit_tag.next_to(unit_grid, DOWN, buff=0.28)

        contrast = VGroup(
            serif("40", 64, INK_DIM),
            mono("->", 30, INK_FAINT),
            serif("100", 64, INK),
        ).arrange(RIGHT, buff=0.30)
        contrast.move_to(LEFT * 4.0 + UP * 1.55)

        self.play(
            FadeOut(coarse_note, shift=DOWN * 0.1),
            FadeIn(contrast[0], shift=UP * 0.1),
            FadeIn(contrast[1]),
            run_time=0.5,
        )
        self.play(
            TransformFromCopy(contrast[0], contrast[2]),
            LaggedStart(*[FadeIn(c) for c in unit_grid], lag_ratio=0.004),
            run_time=0.8,
        )

        sweep = Rectangle(
            width=unit_grid.width + 0.25, height=0.30,
            stroke_width=0, fill_color=INK, fill_opacity=0.18,
        ).move_to(unit_grid.get_top() + UP * 0.06)
        self.add(sweep)
        self.play(
            sweep.animate.move_to(unit_grid.get_bottom() + DOWN * 0.06),
            run_time=0.6, rate_func=linear,
        )
        self.remove(sweep)
        self.play(FadeIn(unit_tag, shift=UP * 0.1), run_time=0.35)

        # =================================================================
        # B4 — SHATTER: the lit sound flies down; a fan opens to a cluster that
        #      flares to pure white — the single peak of the scene.
        # =================================================================
        self.next_section("shatter")

        cluster_idx = [33, 34, 43, 44]
        stray_idx = 56
        all_split = VGroup(*[unit_grid[i] for i in cluster_idx], unit_grid[stray_idx])

        flyer = pick.copy().set_fill(INK, 0.22).set_stroke(INK, 2.4)
        landing = LEFT * 1.4 + DOWN * 0.15
        self.add(flyer)
        self.play(
            flyer.animate.move_to(landing).scale(1.15),
            top_strip.animate.set_opacity(0.30),  # push focus to the shatter
            run_time=0.5, rate_func=rate_functions.ease_in_out_sine,
        )

        connectors = VGroup(*[
            Line(flyer.get_right(), t.get_center(),
                 stroke_color=INK_GHOST, stroke_width=1.6)
            for t in all_split
        ])
        self.play(LaggedStart(*[Create(c) for c in connectors],
                              lag_ratio=0.12), run_time=0.4)

        self.play(
            *[t.animate.set_stroke(INK, 2.0).set_fill(INK, 0.85) for t in all_split],
            run_time=0.25,
        )
        self.play(Indicate(all_split, scale_factor=1.18, color=INK), run_time=0.4)
        self.play(*[t.animate.set_fill(INK, 0.32).set_stroke(INK, 1.6) for t in all_split],
                  run_time=0.2)

        # =================================================================
        # B5 — BLANK ∅: read-head sweeps a unit timeline; ∅ blooms; one ∅ docks.
        # =================================================================
        self.next_section("blank")

        n = 9
        gap_idx = {3, 6}
        tl = VGroup(*[
            Square(0.40, stroke_color=INK_FAINT, stroke_width=1.3, fill_opacity=0)
            for _ in range(n)
        ]).arrange(RIGHT, buff=0.10)
        tl.move_to(LEFT * 3.3 + DOWN * 1.4)

        seq = [12, 12, 87, None, 41, 9, None, 63, 5]
        tl_ids = VGroup()
        for f, v in zip(tl, seq):
            if v is not None:
                tl_ids.add(num(v, 16, INK_DIM).move_to(f))
        tl_label = mono("unit per snapshot", 15, INK_FAINT).next_to(tl, UP, buff=0.22)

        self.play(
            FadeIn(tl_label, shift=UP * 0.1),
            LaggedStart(*[FadeIn(c) for c in tl], lag_ratio=0.06),
            LaggedStart(*[FadeIn(t) for t in tl_ids], lag_ratio=0.05),
            run_time=0.4,
        )

        head = Rectangle(
            width=0.46, height=0.56, stroke_color=INK, stroke_width=2.2,
            fill_color=INK, fill_opacity=0.06,
        ).move_to(tl[0])
        blanks = {gi: serif("∅", 26, INK).move_to(tl[gi]) for gi in sorted(gap_idx)}

        self.add(head)
        for i in range(1, n):
            anims = [head.animate.move_to(tl[i])]
            run = 0.045
            if i in gap_idx:
                anims.append(FadeIn(blanks[i], scale=0.6))
                run = 0.10
            self.play(*anims, run_time=run, rate_func=smooth)
        self.remove(head)

        # one ∅ docks at the right end of the TOP strip as "+1".
        blank_dock = serif("∅", 22, INK).move_to(phon_cells[-1].get_center() + RIGHT * 0.55)
        plus1 = mono("+1", 13, INK_DIM).next_to(blank_dock, UP, buff=0.08)
        flyer_blank = blanks[3].copy()
        self.play(
            flyer_blank.animate.move_to(blank_dock).scale(22 / 26),
            FadeIn(plus1, shift=DOWN * 0.05),
            run_time=0.4, rate_func=rate_functions.ease_in_out_sine,
        )
        self.add(blank_dock)
        self.remove(flyer_blank)

        # =================================================================
        # B6 — FORWARD TEASER: one restrained tag points ahead, then clear.
        # =================================================================
        self.next_section("teaser")

        teaser = mono("self-supervised  ·  discovered next", 15, INK_FAINT)
        teaser.next_to(unit_tag, DOWN, buff=0.20)
        self.play(FadeIn(teaser, shift=UP * 0.08), run_time=0.4)

        # clear the center-left timeline + blanks so the bottom opens.
        timeline_blanks = VGroup(*blanks.values())
        clear_center = VGroup(tl, tl_ids, tl_label, timeline_blanks)
        self.play(
            FadeOut(clear_center, shift=DOWN * 0.15),
            FadeOut(teaser, shift=DOWN * 0.1),
            run_time=0.45,
        )
        self.wait(0.3)

        # =================================================================
        # B7 — RECIPE / NAME IT: training goal assembles, heads couple, payoff.
        # =================================================================
        self.next_section("recipe")

        BAR_W = 3.0

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

        r_unit = bar_row(0.8, "fine units", True)
        r_phon = bar_row(0.1, "the forty", False)
        r_cons = bar_row(0.1, "consistency", False)
        bars = VGroup(r_unit, r_phon, r_cons).arrange(DOWN, buff=0.22, aligned_edge=LEFT)

        goal_label = mono("training goal", 16, INK_FAINT).next_to(
            bars, UP, buff=0.24, aligned_edge=LEFT)
        goal_block = VGroup(goal_label, bars)
        goal_block.move_to(LEFT * 3.55 + DOWN * 2.9, aligned_edge=LEFT)

        for r in (r_unit, r_phon, r_cons):
            r[2].save_state()
            r[2].stretch(0.001, 0, about_edge=LEFT)
        self.play(
            FadeIn(goal_label, shift=UP * 0.08),
            LaggedStart(*[FadeIn(VGroup(r[0], r[1], r[3]))
                          for r in (r_unit, r_phon, r_cons)],
                        lag_ratio=0.18),
            run_time=0.6,
        )
        self.play(LaggedStart(*[Restore(r[2]) for r in (r_unit, r_phon, r_cons)],
                              lag_ratio=0.18), run_time=0.6)
        self.play(Indicate(VGroup(r_unit[2], r_unit[3]), scale_factor=1.08, color=INK),
                  run_time=0.4)

        # coupling: a fixed table ties the two heads so they never disagree.
        link = CurvedArrow(
            r_phon[1].get_right() + RIGHT * 0.05,
            r_unit[1].get_right() + RIGHT * 0.05,
            angle=-TAU / 5, stroke_color=INK_FAINT, stroke_width=1.5, tip_length=0.13,
        )
        # coupling caption tucked just left of the curved link, clear of bars.
        couple = mono("P(phone | unit)", 14, INK_DIM)
        couple.next_to(link, UP, buff=0.20).shift(LEFT * 0.15)
        self.play(Create(link), FadeIn(couple, shift=UP * 0.08), run_time=0.45)

        # single serif #fff payoff, lower-RIGHT under the grid, clear of bars.
        payoff = serif("two answer keys", 30, WHITE)
        payoff.move_to([3.5, -2.48, 0])
        payoff_glow = glow(payoff.copy())
        self.play(FadeIn(payoff_glow), FadeIn(payoff, shift=UP * 0.1), run_time=0.45)
        self.play(Indicate(payoff, scale_factor=1.06, color=WHITE), run_time=0.35)

        # poster hold.
        self.wait(0.5)
