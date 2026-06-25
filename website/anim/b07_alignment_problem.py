# website/anim/b07_alignment_problem.py — B07 "Subtitles, no clock"
#
# THE PUZZLE before CTC can train: training data gives the SEQUENCE of sounds
# (the words, in order) but NOT which input snapshot each sound lands on. The
# alignment is missing — like a movie's subtitles with every timestamp erased.
#
# Discovery arc (have -> don't have -> name the gap). Three-zone canvas:
#   TOP   (y ~ +1.7..+3.5)  the FILMSTRIP: 9 blank ghost snapshots at 50/sec —
#                  known to exist, but unlabeled. A "when?" marker hops them;
#                  later a "?" settles into each; each carries a struck-out stamp.
#   CENTER(y ~ -0.6..+0.9)  the WORD: three known sounds "K  AE  T" on a slim
#                  carriage that SLIDES freely under the snapshots; dotted leaders
#                  fan up to many plausible snapshots — many placements, none labeled.
#   BOTTOM(y ~ -3.4..-2.2)  the LEDGER: "order: known" check vs "which snapshot:
#                  unknown" cross; resolves to serif #fff "word: yes — timing: no".
#
# Locked 9-beat sheet (one self.next_section per beat, timed to dur_sec, clip_T 15.3):
#   1 word (1.68)   the KNOWN word K AE T fades in, "the word we know"
#   2 filmstrip(1.0) carriage dims; blank ghost filmstrip slides in top (no rate yet)
#   3 mismatch(3.07) "50 snapshots / second" appears; many snapshots vs 3 sounds felt
#   4 hop (1.37)    "when?" marker hops over the K snapshots, then the T snapshots
#   5 slide(0.83)   carriage slides freely; dotted leaders fan up with "?" marks
#   6 subtitles(.83) top caption holds; one "?" settles into EVERY snapshot, leaders ghost
#   7 erased(4.59)  tiny timestamps appear under each snapshot, then struck out
#   8 ledger(1.21)  order known (check) vs which-snapshot unknown (cross)
#   9 payoff(0.68)  serif #fff "word: yes — timing: no"; indicate pulse; poster hold
#
# Hand-off: pose ONLY. We do NOT hint at the solution (collapsing many timings to
# one word) — that is s12/ctc's job. We end on the unresolved "timing: no".
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"   # the single payoff accent

TOP_Y = 2.55        # filmstrip band centre
CENTER_Y = 0.15     # word carriage band centre
BOT_Y = -2.9        # ledger band centre
X_L = -6.6
X_R = 6.6

NF = 9              # number of visible blank snapshots
SOUNDS = ["K", "AE", "T"]


def tri(angle, c, op=1.0, s=0.08):
    """Bare triangular arrowhead (points up at angle=0; rotate to aim)."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def dotted_leader(start, end, c=INK_FAINT, n=9, w=1.4):
    """A dashed leader line (sound -> snapshot) built from short segments."""
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    segs = VGroup()
    for k in range(n):
        a = start + (end - start) * (k / n)
        b = start + (end - start) * ((k + 0.55) / n)
        segs.add(Line(a, b, stroke_color=c, stroke_width=w))
    return segs


class AlignmentProblem(Scene):
    def construct(self):
        seed()

        # build the filmstrip geometry once (used from beat 2 on).
        fw = 0.92
        gap = 0.14
        frames = VGroup()
        for _ in range(NF):
            f = Rectangle(width=fw, height=0.86, stroke_color=INK_GHOST,
                          stroke_width=1.3, fill_color=BG, fill_opacity=1.0)
            frames.add(f)
        frames.arrange(RIGHT, buff=gap).move_to([0, TOP_Y, 0])
        rail_y = 0.66
        top_rail = Line([frames.get_left()[0] - 0.1, TOP_Y + rail_y, 0],
                        [frames.get_right()[0] + 0.1, TOP_Y + rail_y, 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        bot_rail = Line([frames.get_left()[0] - 0.1, TOP_Y - rail_y, 0],
                        [frames.get_right()[0] + 0.1, TOP_Y - rail_y, 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        sprockets = VGroup()
        for i in range(NF):
            for yy in (TOP_Y + rail_y, TOP_Y - rail_y):
                sprockets.add(Square(0.07, stroke_width=0, fill_color=INK_FAINT,
                                     fill_opacity=0.5).move_to([frames[i].get_x(), yy, 0]))
        filmstrip = VGroup(top_rail, bot_rail, sprockets, frames)

        # =================================================================
        # BEAT 1 — WORD (~1.68s): the KNOWN word K AE T, "the word we know".
        # =================================================================
        self.next_section("word")

        carriage = RoundedRectangle(width=2.8, height=0.78, corner_radius=0.10,
                                    stroke_color=INK, stroke_width=1.6,
                                    fill_color=BG, fill_opacity=1.0)
        snd_tx = VGroup(*[mono(s, 30, INK) for s in SOUNDS]).arrange(RIGHT, buff=0.46)
        word = VGroup(carriage, snd_tx)
        snd_tx.move_to(carriage.get_center())
        word.move_to([0, CENTER_Y, 0])
        word_lbl = mono("the word we know  —  three sounds, in order", 18, INK_DIM)
        word_lbl.next_to(word, DOWN, buff=0.30)

        self.play(FadeIn(word, shift=UP * 0.10), run_time=0.6)
        self.play(FadeIn(word_lbl, shift=UP * 0.06), run_time=0.45)
        self.wait(0.55)

        # =================================================================
        # BEAT 2 — FILMSTRIP (~1.0s): word dims; blank ghost snapshots slide in.
        # =================================================================
        self.next_section("filmstrip")

        self.play(
            VGroup(word, word_lbl).animate.set_opacity(0.5),
            Create(top_rail), Create(bot_rail),
            LaggedStart(*[FadeIn(sp) for sp in sprockets], lag_ratio=0.02),
            LaggedStart(*[FadeIn(f, shift=RIGHT * 0.08) for f in frames],
                        lag_ratio=0.05),
            run_time=0.8,
        )
        self.wait(0.2)

        # =================================================================
        # BEAT 3 — MISMATCH (~3.07s): rate label appears; many snapshots vs 3 sounds.
        # =================================================================
        self.next_section("mismatch")

        rate_lbl = mono("50 snapshots / second", 18, INK_DIM)
        rate_lbl.next_to(bot_rail, DOWN, buff=0.20).align_to(bot_rail, LEFT).shift(RIGHT * 0.05)
        three_lbl = mono("but just 3 sounds", 18, INK_DIM)
        three_lbl.next_to(bot_rail, DOWN, buff=0.20).align_to(bot_rail, RIGHT).shift(LEFT * 0.05)

        self.play(FadeIn(rate_lbl, shift=DOWN * 0.06), run_time=0.5)
        # let the filmstrip be the bright focus; spotlight the count mismatch.
        self.play(
            LaggedStart(*[Indicate(f, scale_factor=1.06, color=INK) for f in frames],
                        lag_ratio=0.06),
            run_time=1.2,
        )
        self.play(FadeIn(three_lbl, shift=DOWN * 0.06), run_time=0.5)
        self.wait(0.75)

        # =================================================================
        # BEAT 4 — HOP (~1.37s): "when?" marker hops the K snapshots, then the T.
        # =================================================================
        self.next_section("hop")

        self.play(FadeOut(rate_lbl), FadeOut(three_lbl), run_time=0.25)

        ask = mono("when?", 18, INK_DIM)
        bubble = SurroundingRectangle(ask, color=INK_FAINT, buff=0.12,
                                      corner_radius=0.08).set_stroke(width=1.3)
        marker = VGroup(bubble, ask)
        marker.move_to([frames[0].get_x(), TOP_Y + rail_y + 0.34, 0])
        tip = tri(PI, INK_FAINT, 0.9, 0.07).next_to(bubble, DOWN, buff=0.02)
        marker.add(tip)

        # which snapshot holds the K?  ... which holds the T?
        self.play(FadeIn(marker, shift=DOWN * 0.08), run_time=0.22)
        for i in (1, 2):           # candidate homes for K
            self.play(marker.animate.move_to(
                [frames[i].get_x(), TOP_Y + rail_y + 0.34, 0]),
                run_time=0.22, rate_func=smooth)
        for i in (6, 7):           # candidate homes for T
            self.play(marker.animate.move_to(
                [frames[i].get_x(), TOP_Y + rail_y + 0.34, 0]),
                run_time=0.22, rate_func=smooth)
        self.play(FadeOut(marker), run_time=0.18)

        # =================================================================
        # BEAT 5 — SLIDE (~0.83s): carriage slides freely; leaders fan with "?".
        # =================================================================
        self.next_section("slide")

        # re-brighten the word and drop the label — the carriage is the focus now.
        self.play(VGroup(word, word_lbl).animate.set_opacity(1.0), run_time=0.2)
        self.remove(word_lbl)

        slide = 1.5
        self.play(word.animate.shift(LEFT * slide), run_time=0.22, rate_func=smooth)
        self.play(word.animate.shift(RIGHT * 2 * slide), run_time=0.3, rate_func=smooth)
        self.play(word.animate.shift(LEFT * slide), run_time=0.22, rate_func=smooth)

        # fanned dotted leaders from each sound up to several plausible snapshots.
        candidates = {0: [1, 2, 3], 1: [3, 4, 5], 2: [6, 7, 8]}
        leaders = VGroup()
        qmarks = VGroup()
        for si, fids in candidates.items():
            src = snd_tx[si].get_top() + UP * 0.05
            for fid in fids:
                dst = frames[fid].get_bottom() + DOWN * 0.02
                leaders.add(dotted_leader(src, dst, c=INK_GHOST, n=8, w=1.2))
                q = mono("?", 16, INK_FAINT).move_to(
                    (np.array(src) + np.array(dst)) / 2 + RIGHT * 0.12)
                qmarks.add(q)
        self.play(
            LaggedStart(*[Create(ld) for ld in leaders], lag_ratio=0.03),
            LaggedStart(*[FadeIn(q) for q in qmarks], lag_ratio=0.03),
            run_time=0.5,
        )

        # =================================================================
        # BEAT 6 — SUBTITLES (~0.83s): caption holds; one "?" in EVERY snapshot.
        # =================================================================
        self.next_section("subtitles")

        cap = mono("a movie's subtitles  —  with every timestamp erased", 20, INK_DIM)
        cap.move_to([0, 3.74, 0])
        self.play(FadeIn(cap, shift=DOWN * 0.10), run_time=0.3)

        # leaders + their question marks fade to ghost texture; a single "?"
        # settles into each snapshot.
        frame_qs = VGroup(*[mono("?", 26, INK_DIM).move_to(frames[i].get_center())
                            for i in range(NF)])
        self.play(
            leaders.animate.set_stroke(opacity=0.0),
            FadeOut(qmarks),
            LaggedStart(*[FadeIn(q) for q in frame_qs], lag_ratio=0.04),
            run_time=0.5,
        )
        self.remove(leaders, qmarks)

        # =================================================================
        # BEAT 7 — ERASED (~4.59s): timestamps appear under each, then struck out.
        # =================================================================
        self.next_section("erased")

        # dim the word slightly — the erased timing is the focus.
        self.play(word.animate.set_opacity(0.55), run_time=0.3)

        stamps = VGroup()
        crosses = VGroup()
        for i in range(NF):
            ts = mono(f"{i * 20:>3}ms", 11, INK_FAINT).move_to(
                [frames[i].get_x(), TOP_Y - rail_y - 0.28, 0])
            stamps.add(ts)
            crosses.add(Line(ts.get_left() + LEFT * 0.02, ts.get_right() + RIGHT * 0.02,
                             stroke_color=INK, stroke_width=2.2))

        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.05) for s in stamps],
                              lag_ratio=0.06), run_time=0.8)
        self.wait(0.25)
        # strike every timestamp out — timing erased.
        self.play(LaggedStart(*[Create(c) for c in crosses], lag_ratio=0.08),
                  run_time=1.3)
        # fade the struck stamps to ghost so the erasure reads as permanent loss.
        self.play(VGroup(stamps, crosses).animate.set_opacity(0.35), run_time=0.45)
        self.wait(0.35)

        # =================================================================
        # BEAT 8 — LEDGER (~1.21s): order known (check) vs which-snapshot unknown.
        # =================================================================
        self.next_section("ledger")

        # quiet the top so the ledger is the focus.
        self.play(
            VGroup(filmstrip, frame_qs, stamps, crosses, cap).animate.set_opacity(0.22),
            word.animate.set_opacity(0.22),
            run_time=0.3,
        )

        order_lbl = mono("order of sounds", 19, INK_DIM)
        order_val = mono("known", 19, INK)
        order_row = VGroup(order_lbl, order_val).arrange(RIGHT, buff=0.5)
        check = VGroup(
            Line(LEFT * 0.09 + DOWN * 0.02, DOWN * 0.10, stroke_color=INK, stroke_width=2.6),
            Line(DOWN * 0.10, RIGHT * 0.16 + UP * 0.13, stroke_color=INK, stroke_width=2.6),
        ).next_to(order_row, LEFT, buff=0.30)
        left_block = VGroup(check, order_row)

        time_lbl = mono("which snapshot is which", 19, INK_DIM)
        time_val = mono("unknown", 19, INK)
        time_row = VGroup(time_lbl, time_val).arrange(RIGHT, buff=0.5)
        xcross = VGroup(
            Line(UL * 0.12, DR * 0.12, stroke_color=INK, stroke_width=2.6),
            Line(UR * 0.12, DL * 0.12, stroke_color=INK, stroke_width=2.6),
        ).next_to(time_row, LEFT, buff=0.30)
        right_block = VGroup(xcross, time_row)

        ledger = VGroup(left_block, right_block).arrange(RIGHT, buff=1.1)
        ledger.move_to([0, BOT_Y + 0.55, 0])

        self.play(FadeIn(left_block, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(right_block, shift=UP * 0.08), run_time=0.5)
        self.wait(0.2)

        # =================================================================
        # BEAT 9 — PAYOFF (~0.68s): serif #fff "word: yes — timing: no" + poster.
        # =================================================================
        self.next_section("payoff")

        payoff = serif("word: yes  —  timing: no", 40, WHITE)
        payoff.move_to([0, BOT_Y - 0.55, 0])
        self.play(Write(payoff), run_time=0.5)

        # brief glow + indicate pulse, then a short poster hold.
        glow_payoff = glow(payoff.copy())
        glow_payoff[0].set_opacity(0.0)   # start the stroke halo invisible
        self.add(glow_payoff)
        self.play(
            Indicate(payoff, scale_factor=1.05, color=WHITE),
            glow_payoff[0].animate.set_opacity(0.5),
            run_time=0.4,
        )
        self.play(FadeOut(glow_payoff), run_time=0.18)
        self.wait(0.3)
