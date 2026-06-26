# website/anim/s12_ctc.py  —  S12 "Lining up (CTC)"  (centerpiece)
#
# CTC's "aha": timing is UNLABELED, yet the model still learns the right ORDER
# of sounds — because MANY different per-snapshot timings collapse to the same
# word. This scene lands cleanly on ORDER-vs-TIMING; the "reward every timing /
# sum over paths" mechanism is b08's job and is NOT shown here.
#
# Locked 9-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 carry-over    dim ~150 ruler + recap "we know the word — not which..."
#   2 don't pin     box slab 60-68, zoom down into 9 EMPTY alignment cells
#   3 guess         caption "guess a sound — or blank — per snapshot" + a tiny
#                   one-time gloss "blank = nothing here yet" under cell 0
#   4 read L->R     read-head sweeps; ∅ K K ∅ AE AE AE T ∅ pop; ruler index travels
#   5 collapse      fade ruler + captions; only the filled 9-cell row is bright
#   6 merge         run-underlines + blank cross-outs as ONE gesture -> K AE T
#   7 cat           K AE T rises into a big serif "cat", brightened white (peak)
#   8 many timings  three rows of different DURATION drain into one shared K AE T
#   9 name + poster "many timings -> one answer" / "it learns the order, not the
#                   timing"; brief poster hold.
from manim import *
from emg_style import *


def alignment_row(labs, sq=0.50, buff=0.16, fs=26):
    """A row of snapshot-squares with a phoneme-or-blank label inside each.
    Returns (group, squares, texts). Blanks read dim."""
    squares = VGroup(*[
        Square(sq, stroke_color=INK_GHOST, stroke_width=1.2, fill_opacity=0)
        for _ in labs
    ]).arrange(RIGHT, buff=buff)
    texts = VGroup()
    for i, l in enumerate(labs):
        c = INK_FAINT if l == "∅" else INK
        texts.add(mono(l, fs, c).move_to(squares[i]))
    return VGroup(squares, texts), squares, texts


class CTC(Scene):
    def construct(self):
        seed()

        # =================================================================
        # BEAT 1 — CARRY-OVER (~1.32s): the dim ~150-snapshot ruler + recap.
        # =================================================================
        self.next_section("carryover")

        N_TICKS = 150
        RULER_W = 11.4
        ruler_y = 3.0
        ticks = VGroup(*[
            Line(UP * 0.16, DOWN * 0.16, stroke_color=INK_GHOST, stroke_width=1.0)
            for _ in range(N_TICKS)
        ]).arrange(RIGHT, buff=0.02)
        ticks.set_width(RULER_W)
        ticks.move_to(UP * ruler_y)
        base = Line(ticks.get_left() + DOWN * 0.16, ticks.get_right() + DOWN * 0.16,
                    stroke_color=INK_GHOST, stroke_width=1.2)

        f_lab = mono("~150 snapshots", 18, INK_DIM).next_to(ticks, DOWN, buff=0.12)
        f_lab.align_to(ticks, LEFT)
        s_lab = mono("~40 sounds", 18, INK_DIM).next_to(ticks, DOWN, buff=0.12)
        s_lab.align_to(ticks, RIGHT)

        recap = mono("we know the word — not which snapshot is which sound",
                     17, INK_FAINT)
        recap.next_to(ticks, DOWN, buff=0.55).set_x(ticks.get_x())
        top_ruler = VGroup(ticks, base, f_lab, s_lab)

        self.play(
            LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.003, run_time=0.55),
            Create(base),
            FadeIn(f_lab), FadeIn(s_lab),
            run_time=0.55,
        )
        self.play(FadeIn(recap, shift=UP * 0.1),
                  top_ruler.animate.set_opacity(0.55), run_time=0.45)
        recap.set_opacity(0.5)
        self.wait(0.32)

        # shared clock so the top ruler index travels in lockstep with the read.
        clk = ValueTracker(0.0)
        slab_lo, slab_hi = 60, 68
        idx_marker = Triangle(stroke_width=0, fill_color=INK,
                              fill_opacity=0.95).scale(0.10).rotate(PI)
        idx_marker.move_to(ticks[slab_lo].get_top() + UP * 0.16)

        def update_idx(m):
            f = clk.get_value()
            i = int(round(slab_lo + f * (slab_hi - slab_lo)))
            i = max(slab_lo, min(slab_hi, i))
            m.move_to(ticks[i].get_top() + UP * 0.16)

        # =================================================================
        # BEAT 2 — DON'T PIN (~1.55s): box slab 60-68, zoom into 9 EMPTY cells.
        # =================================================================
        self.next_section("dont_pin")

        labs = ["∅", "K", "K", "∅", "AE", "AE", "AE", "T", "∅"]
        row, sq, tx = alignment_row(labs, sq=0.50, buff=0.16, fs=26)
        row.move_to(UP * 1.35)

        dont_cap = mono("don't pin sounds to snapshots at all", 19, INK_DIM)
        dont_cap.next_to(row, UP, buff=0.5)

        slab = VGroup(*[ticks[i] for i in range(slab_lo, slab_hi + 1)])
        slab_box = SurroundingRectangle(slab, color=INK_FAINT, buff=0.06,
                                        stroke_width=1.4)
        self.play(Create(slab_box), FadeIn(dont_cap, shift=DOWN * 0.1), run_time=0.55)
        # the lit slab transforms down into 9 EMPTY cells (no labels yet).
        self.play(
            ReplacementTransform(slab_box, sq),
            *[ticks[i].animate.set_stroke(INK_FAINT, width=1.4)
              for i in range(slab_lo, slab_hi + 1)],
            run_time=0.7,
        )
        self.wait(0.3)

        # =================================================================
        # BEAT 3 — GUESS (~2.64s): caption + one-time "blank = nothing here yet".
        # =================================================================
        self.next_section("guess")

        self.play(FadeOut(dont_cap, shift=UP * 0.08), run_time=0.3)
        name_cap = mono("guess a sound — or blank — per snapshot", 18, INK_FAINT)
        name_cap.next_to(sq, UP, buff=0.5)
        self.play(FadeIn(name_cap), run_time=0.4)

        # tiny one-time gloss under the FIRST (blank) cell; fades after ~0.6s.
        gloss = mono("blank = nothing here yet", 15, INK_FAINT)
        gloss.next_to(sq[0], DOWN, buff=0.22)
        self.play(FadeIn(gloss, shift=UP * 0.06), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(gloss, shift=DOWN * 0.06), run_time=0.55)
        self.wait(0.35)

        # =================================================================
        # BEAT 4 — READ L->R (~2.57s): read-head sweep, labels pop, index travels.
        # =================================================================
        self.next_section("read")

        self.play(FadeIn(idx_marker), run_time=0.25)
        idx_marker.add_updater(update_idx)

        n = len(tx)
        for t in tx:
            t.set_opacity(0.0)
        self.add(tx)
        head = sq[0].copy().set_stroke(INK, width=3.0).set_fill(INK, 0.08)
        self.add(head)

        def update_head(m):
            i = min(int(clk.get_value() * (n - 1) + 0.5), n - 1)
            m.move_to(sq[i])
        head.add_updater(update_head)

        def make_reveal(idx):
            def upd(m):
                m.set_opacity(1.0 if clk.get_value() * (n - 1) >= idx - 0.05 else 0.0)
            return upd
        for i, t in enumerate(tx):
            t.add_updater(make_reveal(i))

        self.play(clk.animate.set_value(1.0), run_time=1.7, rate_func=linear)
        head.clear_updaters()
        for t in tx:
            t.clear_updaters()
            t.set_opacity(1.0)
        idx_marker.clear_updaters()
        self.play(FadeOut(head), run_time=0.3)
        self.wait(0.3)

        # =================================================================
        # BEAT 5 — COLLAPSE (~2.04s): dim ruler + captions; only the row is bright.
        # =================================================================
        self.next_section("collapse")

        collapse_cap = mono("now collapse them", 20, INK)
        collapse_cap.move_to(name_cap.get_center())
        self.play(
            FadeOut(name_cap),
            top_ruler.animate.set_opacity(0.18),
            recap.animate.set_opacity(0.16),
            idx_marker.animate.set_opacity(0.0),
            run_time=0.6,
        )
        self.remove(idx_marker)
        # bring the row to full focus, lift it slightly to centre.
        self.play(
            FadeIn(collapse_cap, shift=DOWN * 0.08),
            row.animate.move_to(UP * 0.95),
            run_time=0.7,
        )
        self.wait(0.74)

        # =================================================================
        # BEAT 6 — MERGE (~1.12s): run-underlines + blank cross-outs, ONE gesture.
        # =================================================================
        self.next_section("merge")

        merged_labs = ["K", "AE", "T"]
        merged_row, m_sq, m_tx = alignment_row(merged_labs, sq=0.50, buff=0.34, fs=30)
        merged_row.move_to(DOWN * 0.7)

        # underlines gather each repeated run.
        runs = VGroup(
            Line(sq[1].get_corner(DL), sq[2].get_corner(DR),
                 stroke_color=INK, stroke_width=2.4),
            Line(sq[4].get_corner(DL), sq[6].get_corner(DR),
                 stroke_color=INK, stroke_width=2.4),
            Line(sq[7].get_corner(DL), sq[7].get_corner(DR),
                 stroke_color=INK, stroke_width=2.4),
        ).shift(DOWN * 0.07)
        # crosses over the three blank cells (0, 3, 8).
        crosses = VGroup(*[
            Cross(sq[i], stroke_color=INK_FAINT, stroke_width=2.0).scale(0.42)
            for i in (0, 3, 8)
        ])
        src_groups = [
            VGroup(tx[1], tx[2]),         # K K
            VGroup(tx[4], tx[5], tx[6]),  # AE AE AE
            VGroup(tx[7]),                # T
        ]

        # ONE continuous gesture: underlines + cross-outs + drop to K AE T.
        self.play(
            LaggedStart(*[Create(r) for r in runs], lag_ratio=0.12),
            LaggedStart(*[Create(c) for c in crosses], lag_ratio=0.12),
            run_time=0.5,
        )
        self.play(
            *[TransformFromCopy(src, m_tx[i]) for i, src in enumerate(src_groups)],
            *[Create(s) for s in m_sq],
            FadeOut(runs), FadeOut(crosses),
            run_time=0.62,
        )

        # =================================================================
        # BEAT 7 — CAT (~2.54s): K AE T rises into a big serif "cat" (white peak).
        # =================================================================
        self.next_section("cat")

        self.play(
            row.animate.set_opacity(0.22),
            collapse_cap.animate.set_opacity(0.0),
            run_time=0.45,
        )
        self.remove(collapse_cap)

        word = serif("cat", 64, INK).move_to(DOWN * 2.1)
        self.play(TransformFromCopy(m_tx, word), run_time=0.7)
        glowing = glow(word.copy().set_color(WHITE))
        self.add(glowing)
        self.play(Indicate(word, scale_factor=1.18, color=WHITE),
                  glowing.animate.set_opacity(0.0), run_time=0.7)
        self.remove(glowing)
        self.wait(0.69)

        # =================================================================
        # BEAT 8 — MANY TIMINGS (~0.83s): three DIFFERENT-DURATION rows -> K AE T.
        # =================================================================
        self.next_section("many")

        pipeline = VGroup(row, sq, tx, merged_row, m_sq, m_tx, word)
        self.play(FadeOut(pipeline, shift=DOWN * 0.2),
                  FadeOut(recap), FadeOut(top_ruler), run_time=0.3)

        title = mono("many timings  →  one answer", 22, INK_DIM).move_to(UP * 2.55)

        # three valid alignments with visibly DIFFERENT durations (long K / long AE
        # / spread), so "faster or slower saying" is literally legible.
        aligns = [
            ["∅", "K", "K", "K", "K", "AE", "AE", "T", "∅"],   # long K run
            ["K", "AE", "AE", "AE", "AE", "AE", "T", "T", "∅"],  # long AE run
            ["∅", "K", "∅", "AE", "AE", "∅", "T", "T", "∅"],   # sparse / spread
        ]
        rows = VGroup()
        for a in aligns:
            r, _, _ = alignment_row(a, sq=0.40, buff=0.14, fs=20)
            rows.add(r)
        rows.arrange(DOWN, buff=0.34).move_to(UP * 0.85)

        answer = serif("K  AE  T", 38, INK).move_to(DOWN * 1.95)
        brace = Brace(rows, DOWN, color=INK_GHOST, buff=0.22).set_stroke(width=1)
        head_tri = Triangle(stroke_width=0, fill_color=INK_FAINT,
                            fill_opacity=0.9).scale(0.12).rotate(PI)
        head_tri.next_to(answer, UP, buff=0.12)
        stem = Line(brace.get_bottom() + DOWN * 0.02, head_tri.get_top() + UP * 0.02,
                    stroke_color=INK_FAINT, stroke_width=2.4)

        self.play(
            FadeIn(title, shift=DOWN * 0.08),
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows],
                        lag_ratio=0.12),
            run_time=0.45,
        )
        self.play(
            GrowFromCenter(brace), Create(stem), FadeIn(head_tri),
            Write(answer),
            run_time=0.45,
        )

        # =================================================================
        # BEAT 9 — NAME + POSTER (~0.67s): order, not timing.
        # =================================================================
        self.next_section("name_it")

        punch = mono("it learns the order, not the timing", 20, INK)
        punch.move_to(DOWN * 3.1)
        glow_punch = glow(punch.copy().set_color(WHITE))
        self.add(glow_punch)
        self.play(
            FadeIn(punch, shift=UP * 0.1),
            Indicate(answer, scale_factor=1.1, color=WHITE),
            glow_punch.animate.set_opacity(0.0),
            run_time=0.42,
        )
        self.remove(glow_punch)
        self.wait(0.4)
