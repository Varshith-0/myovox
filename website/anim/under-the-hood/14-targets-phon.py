# S10 — Sounds (phonemes). The model predicts sounds, not spelling, so it can
# handle any word it has never seen.
#
# Locked 8-beat discovery sheet (one self.next_section per spoken sentence):
#   B1  recap tag: "we showed it a known answer -> but the answer to what?"
#   B2  bottom rail "the prediction target" frames the open question; center empty
#   B3  the obvious guess: though / tough / through as PLAIN letters
#   B4  brace shared "ough"; differing sounds OH / UH F / R UW reveal, pulse white
#   B5  letters lie: strike all three spellings, fade the exhibit fully out
#   B6  serif "cat" -> K . AE . T morph 1:1, three sounds light left to right
#   B7  K.AE.T slides to a top banner; bottom blooms to the ~40-cell row, 3 -> 40
#   B8  one sweep across the closed row; serif #fff payoff; all three zones held
#
# Strict monochrome on #050505 — emphasis from opacity / stroke / scale / glow,
# plus a single pure-#fff accent per beat.
from manim import *
from style import *

WHITE_HOT = "#ffffff"


class Sounds(Scene):
    def construct(self):
        seed()

        # ===================================================================
        # BEAT 1 — RECAP: carry over from training. We showed a known answer,
        # but the answer to WHAT? Top-right tag only; center empty.
        # ===================================================================
        self.next_section("recap")

        recap = mono("we showed it a known answer  →  but the answer to what?",
                     19, INK_GHOST)
        recap.to_corner(UR, buff=0.45)
        self.play(FadeIn(recap, shift=DOWN * 0.12, run_time=0.55))
        self.wait(0.5)

        # ===================================================================
        # BEAT 2 — FRAME THE QUESTION: a quiet bottom rail labelled "the
        # prediction target". Center stays empty — the question hangs.
        # ===================================================================
        self.next_section("frame")

        base_rail = Line(
            np.array([-6.6, -3.55, 0]), np.array([6.6, -3.55, 0]),
            stroke_color=INK_GHOST, stroke_width=1.6,
        )
        rail_tag = mono("the prediction target", 16, INK_GHOST)
        rail_tag.next_to(base_rail, UP, buff=0.16).align_to(base_rail, LEFT).shift(RIGHT * 0.05)
        self.play(
            Create(base_rail, run_time=0.55),
            FadeIn(rail_tag, shift=UP * 0.08, run_time=0.5),
        )
        self.wait(0.35)

        # ===================================================================
        # BEAT 3 — THE OBVIOUS GUESS: letters. though / tough / through fade in
        # as PLAIN spellings, stacked tall. No sounds yet.
        # ===================================================================
        self.next_section("plain-letters")

        words = ["though", "tough", "through"]
        sounds_hint = ["OW", "UH F", "R UW"]

        rows = VGroup()
        for w in words:
            head = w[: w.index("ough")]
            wt = mono(head, 40, INK)
            ot = mono("ough", 40, INK).next_to(wt, RIGHT, buff=0.02)
            rows.add(VGroup(wt, ot))
        rows.arrange(DOWN, buff=1.0, aligned_edge=LEFT)

        # arrow + sounds columns are pre-positioned (revealed in beat 4).
        block = VGroup(rows)
        block.move_to(LEFT * 1.6 + UP * 0.25)

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

        guess_lbl = mono("the obvious guess: letters", 22, INK_FAINT)
        guess_lbl.next_to(rows, UP, buff=0.7, aligned_edge=LEFT)

        self.play(FadeIn(guess_lbl, shift=UP * 0.15, run_time=0.35))
        self.play(
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.18) for r in rows],
                        lag_ratio=0.2, run_time=0.5)
        )
        self.wait(0.2)

        # ===================================================================
        # BEAT 4 — WATCH WHAT LETTERS DO: brace the shared "ough" (same
        # letters), reveal the three differing sounds; sounds pulse white.
        # ===================================================================
        self.next_section("sounds-differ")

        oughs = VGroup(*[r[1] for r in rows])
        brace = Brace(oughs, RIGHT, color=INK_FAINT, buff=0.16)
        same = mono("same letters", 18, INK_FAINT)
        same.next_to(rows, DOWN, buff=0.28).align_to(rows, LEFT)
        self.play(
            GrowFromCenter(brace), FadeIn(same, shift=DOWN * 0.1),
            run_time=0.5,
        )

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
        self.play(Indicate(diffs, scale_factor=1.14, color=WHITE_HOT), run_time=0.5)
        self.wait(0.15)

        # ===================================================================
        # BEAT 5 — LETTERS LIE: strike all three spellings, then fade the whole
        # exhibit fully out. Letters are a shaky thing to predict.
        # ===================================================================
        self.next_section("strike")

        strikes = VGroup(
            *[
                Line(r.get_left() + LEFT * 0.06, r.get_right() + RIGHT * 0.06,
                     stroke_color=INK_FAINT, stroke_width=2.5)
                for r in rows
            ]
        )
        self.play(LaggedStart(*[Create(s) for s in strikes],
                              lag_ratio=0.12, run_time=0.5))

        exhibit = VGroup(guess_lbl, rows, arrows, diffs, brace, strikes, same, diff_lbl)
        self.play(FadeOut(exhibit, run_time=0.55))

        # ===================================================================
        # BEAT 6 — SO INSTEAD: serif "cat" writes center, then each letter
        # morphs 1:1 into K . AE . T; the three sounds light left to right.
        # ===================================================================
        self.next_section("cat-morph")

        word = serif("cat", 100, INK).move_to(LEFT * 3.2 + UP * 0.35)
        self.play(Write(word), run_time=0.6)

        arrow2 = mono("→", 44, INK_FAINT).next_to(word, RIGHT, buff=0.8)
        self.play(FadeIn(arrow2, shift=RIGHT * 0.1, run_time=0.3))

        letters = serif("cat", 100, INK).move_to(word)
        c_let, a_let, t_let = letters[0], letters[1], letters[2]

        phon = VGroup(
            mono("K", 64, INK),
            mono("·", 46, INK_FAINT),
            mono("AE", 64, INK),
            mono("·", 46, INK_FAINT),
            mono("T", 64, INK),
        ).arrange(RIGHT, buff=0.42).next_to(arrow2, RIGHT, buff=0.8)
        K, dot1, AE, dot2, T = phon

        self.remove(word)
        self.add(letters)
        self.play(
            ReplacementTransform(c_let, K),
            ReplacementTransform(a_let, AE),
            ReplacementTransform(t_let, T),
            FadeIn(dot1, scale=0.4),
            FadeIn(dot2, scale=0.4),
            run_time=0.85,
        )

        anims = []
        for g in (K, AE, T):
            anims.append(
                AnimationGroup(
                    Indicate(g, scale_factor=1.25, color=WHITE_HOT),
                    Flash(g, color=WHITE_HOT, line_length=0.18,
                          num_lines=10, flash_radius=0.42, line_stroke_width=1.6),
                )
            )
        self.play(LaggedStart(*anims, lag_ratio=0.4, run_time=0.85))

        # ===================================================================
        # BEAT 7 — COUNTED ALREADY: K.AE.T slides up to a top banner; the bottom
        # blooms to the full ~40-cell sound row as the tally ticks 3 -> 40.
        # ===================================================================
        self.next_section("forty")

        inventory = [
            "AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH",
            "EH", "ER", "EY", "F", "G", "HH", "IH", "IY", "JH", "K",
            "L", "M", "N", "NG", "OW", "OY", "P", "R", "S", "SH",
            "T", "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH", "AX",
        ]  # 40 phonemes
        hot = ("K", "AE", "T")
        rest = [s for s in inventory if s not in hot]
        ordered = ["K", "AE", "T"] + rest

        cells = VGroup(*[
            mono(sym, 20, INK if sym in hot else INK_DIM) for sym in ordered
        ])
        cells.arrange(RIGHT, buff=0.205)
        max_w = 13.4
        if cells.width > max_w:
            cells.scale(max_w / cells.width)
        cells.move_to(np.array([0, -3.05, 0]))
        cell_by_sym = {sym: c for sym, c in zip(ordered, cells)}
        hot_cells = VGroup(cell_by_sym["K"], cell_by_sym["AE"], cell_by_sym["T"])
        cold_cells = VGroup(*[cell_by_sym[s] for s in rest])

        # retire the placeholder rail tag and re-seat the rail under the row.
        self.play(
            base_rail.animate.put_start_and_end_on(
                np.array([cells.get_left()[0] - 0.1, -3.5, 0]),
                np.array([cells.get_right()[0] + 0.1, -3.5, 0]),
            ),
            FadeOut(rail_tag, run_time=0.4),
            run_time=0.5,
        )

        # tally counter (LaTeX-free), dim while the row is the focus.
        tally = ValueTracker(3)
        inv_label = mono("sounds in the alphabet:", 19, INK_GHOST)
        inv_label.move_to(DOWN * 2.42).set_x(-1.0)
        count_at = np.array([inv_label.get_right()[0] + 0.45, inv_label.get_center()[1], 0])
        count_txt = counter(tally, fmt=lambda v: str(round(v)), s=24, c=INK_DIM, at=count_at)

        # banner: slide K.AE.T up to the top context band, clear the morph arrow,
        # bring the three hot cells + tally to life on the bottom row.
        self.play(
            phon.animate.scale(0.80).move_to(UP * 2.85),
            FadeOut(arrow2, run_time=0.4),
            FadeIn(inv_label, shift=UP * 0.1, run_time=0.5),
            FadeIn(count_txt, run_time=0.5),
            FadeIn(hot_cells, shift=UP * 0.1, run_time=0.5),
            run_time=0.6,
        )

        # the ~37 remaining cells bloom while the tally ticks 3 -> 40.
        self.play(
            LaggedStart(*[FadeIn(c, scale=0.7) for c in cold_cells],
                        lag_ratio=0.022, run_time=1.1),
            tally.animate.set_value(40),
            run_time=1.1,
        )
        count_txt.clear_updaters()
        self.wait(0.1)

        # ===================================================================
        # BEAT 8 — PAYOFF: one sweep across the closed ~40-cell row; the serif
        # #fff punchline lights; all three zones held for a brief poster.
        # ===================================================================
        self.next_section("payoff")

        # tally resolves to a plain caption; counter dims to a footnote.
        full_label = mono("~40 sounds — a fixed alphabet", 19, INK_GHOST)
        full_label.move_to(inv_label, aligned_edge=LEFT)
        new_count_at = full_label.get_right()[0] + 0.45
        self.play(
            FadeOut(inv_label, run_time=0.3),
            FadeIn(full_label, run_time=0.4),
            count_txt.animate.set_x(new_count_at).set_y(full_label.get_center()[1]),
            run_time=0.45,
        )

        # one sweep passes across the closed row — "a closed set".
        sweep = Rectangle(
            width=0.6, height=cells.height + 0.45,
            stroke_width=0, fill_color=INK, fill_opacity=0.06,
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

        # the single serif #fff payoff word, center, with glow.
        punch = serif("any word is just a sequence of these", 34, WHITE_HOT)
        punch.move_to(UP * 0.2)
        self.play(FadeIn(glow(punch), shift=UP * 0.1, run_time=0.6))

        # light all three zones together once, then hold the poster.
        self.play(
            Indicate(hot_cells, scale_factor=1.3, color=WHITE_HOT),
            Indicate(phon, scale_factor=1.08, color=WHITE_HOT),
            Indicate(punch, scale_factor=1.04, color=WHITE_HOT),
            run_time=0.7,
        )
        self.wait(0.6)
