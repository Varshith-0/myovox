# S10 — Sounds (phonemes). The model predicts sounds, not spelling, so it can
# handle any word it has never seen.
#
# Three-zone full-canvas composition (3b1b rhythm: pose -> build -> transform
# -> name -> beat). Every beat keeps ALL THREE horizontal zones alive so the
# frame never collapses into a thin central band:
#   TOP    (y ~ +2.4..+3.6)  CONTEXT — recap tag linking back to S09, and later
#                      the K·AE·T banner that the transform produces.
#   CENTER (y ~ -2.2..+2.2)  MECHANISM — the star: the "spelling lies" exhibit
#                      spread tall and wide across the right half, then serif
#                      "cat" physically comes apart and re-forms as K · AE · T.
#   BOTTOM (y ~ -3.6..-2.4)  RUNNING TAKEAWAY — a sound-inventory rail that
#                      appears EARLY (so the bottom is never blank) and blooms
#                      to the full ~40-cell ARPABET row while a LaTeX-free tally
#                      ticks 3 -> ~40 and a progress underline grows.
#
# Strict monochrome — emphasis from opacity / stroke / scale / glow, plus a
# single pure-#fff accent per beat. ARPABET (~40 phonemes, stress stripped).
from manim import *
from emg_style import *

WHITE_HOT = "#ffffff"


class Sounds(Scene):
    def construct(self):
        seed()

        # ===================================================================
        # TOP CONTEXT — recap tag links S09 fingerprints to this question.
        # ===================================================================
        recap = mono("from fingerprints  →  what do we predict?", 19, INK_GHOST)
        recap.to_corner(UR, buff=0.45)
        self.play(FadeIn(recap, shift=DOWN * 0.12, run_time=0.5))

        # A quiet baseline rail sits in the BOTTOM strip from the very start, so
        # the lower third is never empty. It will later host the ARPABET row.
        base_rail = Line(
            np.array([-6.6, -3.55, 0]), np.array([6.6, -3.55, 0]),
            stroke_color=INK_GHOST, stroke_width=1.6,
        )
        rail_tag = mono("the prediction target", 16, INK_GHOST)
        rail_tag.next_to(base_rail, UP, buff=0.16).align_to(base_rail, LEFT).shift(RIGHT * 0.05)
        self.play(
            Create(base_rail, run_time=0.6),
            FadeIn(rail_tag, shift=UP * 0.08, run_time=0.5),
        )

        # ===================================================================
        # BEAT 1 — POSE: "spelling lies" exhibit (though / tough / through).
        # Same letters ("ough"), three different sounds; strike them out.
        # The exhibit is spread TALL (full center height) and pushed to the
        # RIGHT half so the canvas is used edge to edge.
        # ===================================================================
        self.next_section("spelling-lies")

        words = ["though", "tough", "through"]
        sounds_hint = ["OH", "UH F", "R UW"]

        rows = VGroup()
        for w in words:
            head = w[: w.index("ough")]
            wt = mono(head, 40, INK)
            ot = mono("ough", 40, INK).next_to(wt, RIGHT, buff=0.02)
            rows.add(VGroup(wt, ot))
        # tall vertical spread: occupy most of the center band's height.
        rows.arrange(DOWN, buff=1.0, aligned_edge=LEFT)

        title = mono("English spelling lies", 26, INK_FAINT)
        title.next_to(rows, UP, buff=0.7, aligned_edge=LEFT)

        # arrows + differing sounds in tidy aligned columns, pushed well to the
        # RIGHT so the exhibit spans roughly x = -4 .. +5 (uses the right half).
        arrow_x = rows.get_right()[0] + 1.4
        diff_x = arrow_x + 1.0
        arrows = VGroup()
        diffs = VGroup()
        for r, s in zip(rows, sounds_hint):
            ar = mono("→", 34, INK_FAINT).move_to(np.array([arrow_x, r.get_center()[1], 0]))
            dt = mono(s, 38, INK_DIM)
            dt.move_to(np.array([diff_x + dt.width / 2, r.get_center()[1], 0]))
            arrows.add(ar)
            diffs.add(dt)

        block = VGroup(title, rows, arrows, diffs)
        # center it across the full width, slightly above the bottom rail.
        block.move_to(LEFT * 0.4 + UP * 0.25)

        self.play(FadeIn(title, shift=UP * 0.15, run_time=0.35))
        self.play(
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.18) for r in rows],
                        lag_ratio=0.2, run_time=0.65)
        )

        # brace the shared "ough" column — same letters. Label sits BELOW the
        # words so nothing collides with the sounds column on the right.
        oughs = VGroup(*[r[1] for r in rows])
        brace = Brace(oughs, RIGHT, color=INK_FAINT, buff=0.16)
        same = mono("same letters", 18, INK_FAINT)
        same.next_to(rows, DOWN, buff=0.28).align_to(rows, LEFT)
        self.play(
            GrowFromCenter(brace), FadeIn(same, shift=DOWN * 0.1),
            Indicate(oughs, scale_factor=1.12, color=WHITE_HOT),
            run_time=0.6,
        )

        # reveal the differing sounds (right column).
        diff_lbl = mono("different sounds", 18, INK_FAINT)
        diff_lbl.next_to(diffs, DOWN, buff=0.28).align_to(diffs, LEFT)
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(FadeIn(a, run_time=0.3),
                                   FadeIn(d, shift=RIGHT * 0.12, run_time=0.4))
                    for a, d in zip(arrows, diffs)
                ],
                lag_ratio=0.18,
                run_time=0.6,
            ),
            FadeIn(diff_lbl, shift=DOWN * 0.1, run_time=0.45),
        )
        self.play(Indicate(diffs, scale_factor=1.14, color=WHITE_HOT), run_time=0.4)

        # strike the spellings — letters are unreliable.
        strikes = VGroup(
            *[
                Line(r.get_left() + LEFT * 0.06, r.get_right() + RIGHT * 0.06,
                     stroke_color=INK_FAINT, stroke_width=2.5)
                for r in rows
            ]
        )
        self.play(LaggedStartMap(Create, strikes, lag_ratio=0.12, run_time=0.45))

        # Clear the exhibit COMPLETELY (fade fully out — no faint footnote left
        # to crowd later beats). The lesson has landed; move on to "cat".
        spell_grp = VGroup(block, brace, strikes, same, diff_lbl)
        self.play(FadeOut(spell_grp, run_time=0.6))

        # ===================================================================
        # BEAT 2 — BUILD: the question word "cat" in the center, sized to span
        # the full width. The bottom rail stays as the standing takeaway anchor.
        # ===================================================================
        self.next_section("the-word")

        word = serif("cat", 100, INK).move_to(LEFT * 3.4 + UP * 0.35)
        self.play(Write(word), run_time=0.7)

        g2p = mono("g2p", 22, INK_GHOST).next_to(word, UP, buff=0.45)
        g2p_sub = mono("grapheme → phoneme", 16, INK_GHOST).next_to(g2p, UP, buff=0.14)
        arrow2 = mono("→", 44, INK_FAINT).next_to(word, RIGHT, buff=0.8)
        self.play(
            FadeIn(g2p, shift=UP * 0.1, run_time=0.3),
            FadeIn(g2p_sub, shift=UP * 0.1, run_time=0.3),
            FadeIn(arrow2, shift=RIGHT * 0.1, run_time=0.3),
        )
        # lock the eye on the star.
        self.play(Indicate(word, scale_factor=1.1, color=WHITE_HOT), run_time=0.4)

        # ===================================================================
        # BEAT 3 — TRANSFORM (the star): letters c-a-t become sounds K · AE · T.
        # Per-letter ReplacementTransform so the morph reads as 1:1 substitution.
        # Destination sits on the RIGHT half, filling that previously-dead space.
        # ===================================================================
        self.next_section("morph")

        # split serif "cat" into its three letters.
        letters = serif("cat", 100, INK).move_to(word)
        c_let, a_let, t_let = letters[0], letters[1], letters[2]

        # destination phoneme glyphs + separators, right of the arrow.
        phon = VGroup(
            mono("K", 64, INK),
            mono("·", 46, INK_FAINT),
            mono("AE", 64, INK),
            mono("·", 46, INK_FAINT),
            mono("T", 64, INK),
        ).arrange(RIGHT, buff=0.42).next_to(arrow2, RIGHT, buff=0.8)
        K, dot1, AE, dot2, T = phon

        # swap the written word for the splittable copy, invisibly.
        self.remove(word)
        self.add(letters)

        # 1:1 substitution: each letter morphs into its phoneme; dots crisp in.
        self.play(
            ReplacementTransform(c_let, K),
            ReplacementTransform(a_let, AE),
            ReplacementTransform(t_let, T),
            FadeIn(dot1, scale=0.4),
            FadeIn(dot2, scale=0.4),
            run_time=1.0,
        )

        # name each sound left -> right: a travelling Indicate + Flash to #fff.
        glyphs = [K, AE, T]
        anims = []
        for g in glyphs:
            anims.append(
                AnimationGroup(
                    Indicate(g, scale_factor=1.25, color=WHITE_HOT),
                    Flash(g, color=WHITE_HOT, line_length=0.18,
                          num_lines=10, flash_radius=0.42, line_stroke_width=1.6),
                )
            )
        self.play(LaggedStart(*anims, lag_ratio=0.4, run_time=0.85))

        # ===================================================================
        # BEAT 4 — NAME IT (ARPABET) + seed the bottom tally.
        # K·AE·T slides up to a compact TOP banner; the inventory row's first
        # three (hot) slots fill from the banner; the bottom-strip label + tally
        # come alive on the rail that has been there since the start.
        # ===================================================================
        self.next_section("name-it")

        arpa = mono("ARPABET", 22, INK_FAINT).next_to(phon, DOWN, buff=0.45)
        self.play(FadeIn(arpa, shift=UP * 0.1, run_time=0.4))

        # build the full ~40-cell ARPABET inventory as a SINGLE row along the
        # bottom (stress stripped). K, AE, T are the only hot cells.
        inventory = [
            "AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH",
            "EH", "ER", "EY", "F", "G", "HH", "IH", "IY", "JH", "K",
            "L", "M", "N", "NG", "OW", "OY", "P", "R", "S", "SH",
            "T", "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH", "AX",
        ]  # 40 phonemes
        hot = ("K", "AE", "T")

        # order the row so K, AE, T are the three leftmost (they "fly in" first),
        # the rest follow in their natural order.
        rest = [s for s in inventory if s not in hot]
        ordered = ["K", "AE", "T"] + rest

        cells = VGroup(*[
            mono(sym, 20, INK if sym in hot else INK_DIM) for sym in ordered
        ])
        cells.arrange(RIGHT, buff=0.205)
        # scale the whole row to fit safely inside x = ±7.1 with margin.
        max_w = 13.4
        if cells.width > max_w:
            cells.scale(max_w / cells.width)
        # sit the row ON the existing bottom rail.
        cells.move_to(np.array([0, -3.05, 0]))
        cell_by_sym = {sym: c for sym, c in zip(ordered, cells)}
        hot_cells = VGroup(cell_by_sym["K"], cell_by_sym["AE"], cell_by_sym["T"])
        cold_cells = VGroup(*[cell_by_sym[s] for s in rest])

        # move the bottom rail to hug just under the row, and retire the early
        # placeholder tag (its job — "keep the bottom alive" — is now done by the
        # real inventory).
        self.play(
            base_rail.animate.put_start_and_end_on(
                np.array([cells.get_left()[0] - 0.1, -3.5, 0]),
                np.array([cells.get_right()[0] + 0.1, -3.5, 0]),
            ),
            FadeOut(rail_tag, run_time=0.4),
            run_time=0.5,
        )

        # bottom-strip label + tally counter (LaTeX-free). The counter() helper
        # re-pins itself to `at` every frame via become(); pass the position.
        tally = ValueTracker(3)
        inv_label = mono("sounds in the alphabet:", 19, INK_FAINT)
        inv_label.move_to(DOWN * 2.42).set_x(-1.0)
        count_at = np.array([inv_label.get_right()[0] + 0.45, inv_label.get_center()[1], 0])
        count_txt = counter(tally, fmt=lambda v: str(round(v)), s=24, c=INK, at=count_at)

        # CENTER punchline is prepared now and fades in AS the banner lands, so
        # the middle third is never hollow while K·AE·T sits at the top.
        punch = mono("any word is just a sequence of these", 30, INK_FAINT)
        punch.move_to(UP * 0.15)
        banner_tag = mono("cat  →  three sounds", 18, INK_GHOST)
        banner_tag.next_to(UP * 2.85, DOWN, buff=0.0)  # placeholder; re-pinned below

        # banner: slide the K·AE·T phoneme row up to the top context band, clear
        # the orphaned g2p labels + arrow, light the bottom tally, and bring the
        # center punchline in — all three zones populate in one beat.
        self.play(
            phon.animate.scale(0.80).move_to(UP * 2.85),
            FadeOut(arpa, shift=UP * 0.1, run_time=0.4),
            FadeOut(g2p, run_time=0.4),
            FadeOut(g2p_sub, run_time=0.4),
            FadeOut(arrow2, run_time=0.4),
            FadeIn(inv_label, shift=UP * 0.1, run_time=0.5),
            FadeIn(count_txt, run_time=0.5),
            FadeIn(punch, shift=UP * 0.1, run_time=0.6),
            run_time=0.7,
        )
        banner_tag = mono("cat  →  three sounds", 18, INK_GHOST)
        banner_tag.next_to(phon, DOWN, buff=0.22)

        # the three named sounds drop from the banner into their bottom slots,
        # while the banner caption settles under K·AE·T.
        src = VGroup(phon[0].copy(), phon[2].copy(), phon[4].copy())
        self.play(
            FadeIn(banner_tag, shift=DOWN * 0.06, run_time=0.5),
            LaggedStart(
                *[ReplacementTransform(s, d)
                  for s, d in zip(src, [hot_cells[0], hot_cells[1], hot_cells[2]])],
                lag_ratio=0.18, run_time=0.8,
            ),
        )

        # ===================================================================
        # BEAT 5 — BUILD THE ALPHABET: remaining ~37 cells bloom in while the
        # tally ticks 3 -> 40 and a progress underline grows left -> right.
        # The CENTER punchline comes in EARLY (overlapping this bloom) so the
        # middle third is never hollow while K·AE·T sits at the top.
        # ===================================================================
        self.next_section("build-alphabet")

        # progress underline beneath the row.
        underline = Line(
            cells.get_left() + DOWN * 0.30 + LEFT * 0.02,
            cells.get_right() + DOWN * 0.30 + RIGHT * 0.02,
            stroke_color=INK_GHOST, stroke_width=2.0,
        )
        prog = Line(
            underline.get_start(), underline.get_start(),
            stroke_color=INK, stroke_width=3.0,
        )

        def prog_updater(m):
            frac = (tally.get_value() - 3) / (40 - 3)
            frac = max(0.0, min(1.0, frac))
            end = underline.point_from_proportion(max(frac, 1e-4))
            m.put_start_and_end_on(underline.get_start(), end)

        prog.add_updater(prog_updater)
        self.add(underline, prog)

        # supporting center sub-line under the punchline (which is already on
        # screen from beat 4) — appears as the alphabet blooms below.
        seq_sub = mono("a closed set of building blocks", 19, INK_GHOST)
        seq_sub.next_to(punch, DOWN, buff=0.35)

        self.play(
            LaggedStart(*[FadeIn(c, scale=0.7) for c in cold_cells],
                        lag_ratio=0.022, run_time=1.5),
            tally.animate.set_value(40),
            FadeIn(seq_sub, shift=UP * 0.08, run_time=0.9),
            run_time=1.5,
        )
        prog.clear_updaters()

        # counter lands on 40 and holds; label resolves to the punchline claim,
        # the counter sliding to sit just after it.
        count_txt.clear_updaters()
        full_label = mono("~40 sounds — a fixed alphabet", 19, INK_FAINT)
        full_label.move_to(inv_label, aligned_edge=LEFT)
        new_count_at = full_label.get_right()[0] + 0.45
        self.play(
            FadeOut(inv_label, run_time=0.3),
            FadeIn(full_label, run_time=0.4),
            count_txt.animate.set_x(new_count_at).set_y(full_label.get_center()[1]),
        )

        # a faint sweep passes once across the row — "a closed set".
        sweep = Rectangle(
            width=0.6, height=cells.height + 0.45,
            stroke_width=0, fill_color=INK, fill_opacity=0.05,
        )
        sweep.move_to(cells.get_left() + LEFT * 0.45)
        sweep.set_y(cells.get_center()[1])
        self.add(sweep)
        self.play(
            sweep.animate.move_to(np.array([cells.get_right()[0] + 0.45,
                                            cells.get_center()[1], 0])),
            run_time=0.85, rate_func=linear,
        )
        self.remove(sweep)

        # ===================================================================
        # BEAT 6 — POSTER TIE: light all three zones together — banner (top),
        # punchline (center), hot cells (bottom) — then hold the composed frame.
        # ===================================================================
        self.next_section("punchline")

        self.play(
            Indicate(hot_cells, scale_factor=1.3, color=WHITE_HOT),
            Indicate(phon, scale_factor=1.08, color=WHITE_HOT),
            Indicate(punch, scale_factor=1.04, color=WHITE_HOT),
            run_time=0.85,
        )

        self.wait(0.6)
