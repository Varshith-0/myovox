# website/anim/b07_alignment_problem.py — B07 "Subtitles, no clock"
#
# THE PUZZLE before CTC can train: training data gives the SEQUENCE of sounds
# (the words, in order) but NOT which input frame each sound lands on. The
# alignment is missing — like a movie's subtitles with every timestamp erased.
#
# Three-zone full-canvas composition (pose -> build -> transform -> NAME):
#   TOP   (y ~ +1.6..+3.5)  the FILMSTRIP: ~9 blank ghost frames at 50/sec, the
#                  incoming snapshots — known to exist, but unlabeled. Each frame
#                  carries a tiny struck-out timestamp; a "when?" marker hops them.
#   CENTER(y ~ -0.6..+0.9)  the WORD: three known sounds "K  AE  T" on a slim
#                  carriage that SLIDES freely left<->right under the frames;
#                  dotted leaders of many lengths fan up to many plausible frames
#                  and dangle with question marks — many placements, none labeled.
#   BOTTOM(y ~ -3.4..-2.2)  the LEDGER: "order: known" gets a check, "timing:
#                  unknown" gets a Cross; resolves to the serif #fff payoff
#                  "word: yes  —  timing: no".  Ends on a ~0.6s poster hold.
#
# Hand-off: pose ONLY. We do NOT say "nobody labeled which frame is which sound"
# (that is s12/ctc's line); we leave the SOLUTION for the ctc anchor next.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"   # the single payoff accent

TOP_Y = 2.55        # filmstrip band centre
CENTER_Y = 0.15     # word carriage band centre
BOT_Y = -2.9        # ledger band centre
X_L = -6.6
X_R = 6.6

NF = 9              # number of visible blank frames
SOUNDS = ["K", "AE", "T"]


def tri(angle, c, op=1.0, s=0.08):
    """Bare triangular arrowhead (points up at angle=0; rotate to aim)."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def dotted_leader(start, end, c=INK_FAINT, n=9, w=1.4):
    """A dashed leader line (frame -> sound) built from short segments."""
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

        # =================================================================
        # B0 — POSE: the filmstrip of blank frames (50/sec) + the known word.
        # =================================================================
        self.next_section("pose")

        cap = mono("a movie's subtitles  —  with every timestamp erased", 20, INK_DIM)
        cap.move_to([0, 3.74, 0])
        self.play(FadeIn(cap, shift=DOWN * 0.12), run_time=0.45)

        # Filmstrip: NF blank cells between two rails, with sprocket squares.
        fw = 0.92                      # frame width
        gap = 0.14
        strip_w = NF * fw + (NF - 1) * gap
        frames = VGroup()
        for i in range(NF):
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

        rate_lbl = mono("50 snapshots / second", 16, INK_FAINT)
        rate_lbl.next_to(bot_rail, DOWN, buff=0.18).align_to(bot_rail, LEFT).shift(RIGHT * 0.05)

        self.play(
            Create(top_rail), Create(bot_rail),
            LaggedStartMap(FadeIn, sprockets, lag_ratio=0.02, run_time=0.5),
            LaggedStart(*[FadeIn(f, shift=RIGHT * 0.08) for f in frames],
                        lag_ratio=0.05, run_time=0.7),
            run_time=0.75,
        )
        self.play(FadeIn(rate_lbl, shift=DOWN * 0.06), run_time=0.3)

        # The KNOWN word: three sounds, in order, on a slim carriage.
        carriage = RoundedRectangle(width=2.8, height=0.78, corner_radius=0.10,
                                    stroke_color=INK, stroke_width=1.6,
                                    fill_color=BG, fill_opacity=1.0)
        snd_tx = VGroup(*[mono(s, 30, INK) for s in SOUNDS]).arrange(RIGHT, buff=0.46)
        word = VGroup(carriage, snd_tx)
        snd_tx.move_to(carriage.get_center())
        word.move_to([0, CENTER_Y, 0])
        word_lbl = mono("the word we know:  K  AE  T  (in order)", 18, INK_DIM)
        word_lbl.next_to(word, DOWN, buff=0.28)

        self.play(FadeIn(word, shift=UP * 0.10), run_time=0.45)
        self.play(FadeIn(word_lbl, shift=UP * 0.06), run_time=0.3)

        # =================================================================
        # B1 — BUILD: a "when?" marker hops the frames, trying to pin sounds.
        # =================================================================
        self.next_section("build")

        ask = mono("when?", 18, INK_DIM)
        bubble = SurroundingRectangle(ask, color=INK_FAINT, buff=0.12,
                                      corner_radius=0.08).set_stroke(width=1.3)
        marker = VGroup(bubble, ask)
        marker.move_to([frames[0].get_x(), TOP_Y + rail_y + 0.30, 0])
        tip = tri(PI, INK_FAINT, 0.9, 0.07).next_to(bubble, DOWN, buff=0.02)
        marker.add(tip)
        self.play(FadeIn(marker, shift=DOWN * 0.08), run_time=0.3)

        # the marker hops across several frames — each is an equally plausible
        # home for a sound, and none is labeled.
        hop_idx = [1, 3, 5, 7]
        for i in hop_idx:
            self.play(marker.animate.move_to(
                [frames[i].get_x(), TOP_Y + rail_y + 0.30, 0]),
                run_time=0.26, rate_func=smooth)
        self.play(marker.animate.set_opacity(0.0), run_time=0.2)
        self.remove(marker)

        # The carriage SLIDES freely — there is no fixed home. Dotted leaders of
        # many lengths fan up from the three sounds to many plausible frames.
        slide_lbl = mono("the carriage slides freely  —  no fixed home", 16, INK_FAINT)
        slide_lbl.move_to([0, CENTER_Y - 1.05, 0])
        self.play(ReplacementTransform(word_lbl, slide_lbl), run_time=0.4)

        slide = 1.6
        # explicit free slide: left, then right, then settle centre.
        self.play(word.animate.shift(LEFT * slide), run_time=0.55, rate_func=smooth)
        self.play(word.animate.shift(RIGHT * 2 * slide), run_time=0.8, rate_func=smooth)
        self.play(word.animate.shift(LEFT * slide), run_time=0.55, rate_func=smooth)
        self.wait(0.2)

        # Many plausible placements: dotted leaders fan from each sound up to
        # several different frames (varied lengths == varied timings).
        candidates = {0: [1, 2, 3], 1: [3, 4, 5], 2: [6, 7, 8]}  # sound -> frames
        leaders = VGroup()
        qmarks = VGroup()
        for si, fids in candidates.items():
            src = snd_tx[si].get_top() + UP * 0.05
            for fid in fids:
                dst = frames[fid].get_bottom() + DOWN * 0.02
                ld = dotted_leader(src, dst, c=INK_GHOST, n=8, w=1.2)
                leaders.add(ld)
                q = mono("?", 16, INK_FAINT).move_to(
                    (np.array(src) + np.array(dst)) / 2 + RIGHT * 0.12)
                qmarks.add(q)
        many_lbl = mono("many plausible placements", 16, INK_FAINT)
        many_lbl.next_to(bot_rail, DOWN, buff=0.18).align_to(bot_rail, RIGHT).shift(LEFT * 0.05)

        self.play(LaggedStart(*[Create(ld) for ld in leaders], lag_ratio=0.04),
                  FadeIn(many_lbl, shift=DOWN * 0.06), run_time=0.9)
        self.play(LaggedStartMap(FadeIn, qmarks, lag_ratio=0.05, run_time=0.5))

        # =================================================================
        # B2 — TRANSFORM: a dangling '?' settles over EVERY frame; the
        #      timestamps are struck out (Cross in INK).
        # =================================================================
        self.next_section("transform")

        # fade the candidate fan to ghosts (they stay as texture) and drop a
        # single hovering '?' into every frame: the timing of each is unknown.
        self.play(leaders.animate.set_stroke(opacity=0.0),
                  qmarks.animate.set_opacity(0.0),
                  FadeOut(rate_lbl), FadeOut(many_lbl),
                  run_time=0.35)
        self.remove(qmarks, leaders)

        frame_qs = VGroup(*[mono("?", 26, INK_DIM).move_to(frames[i].get_center())
                            for i in range(NF)])
        # a tiny struck-out timestamp under each frame.
        stamps = VGroup()
        crosses = VGroup()
        for i in range(NF):
            ts = mono(f"{i * 20:>3}ms", 11, INK_FAINT).move_to(
                [frames[i].get_x(), TOP_Y - rail_y - 0.26, 0])
            stamps.add(ts)
            cr = Line(ts.get_left() + LEFT * 0.02, ts.get_right() + RIGHT * 0.02,
                      stroke_color=INK, stroke_width=2.0)
            crosses.add(cr)

        self.play(LaggedStartMap(FadeIn, frame_qs, lag_ratio=0.04, run_time=0.55),
                  run_time=0.55)
        self.play(LaggedStartMap(FadeIn, stamps, lag_ratio=0.03, run_time=0.4))
        # strike every timestamp out — timing erased.
        self.play(LaggedStartMap(Create, crosses, lag_ratio=0.04, run_time=0.55))

        # =================================================================
        # B3 — LEDGER: order known (check) vs timing unknown (Cross), then NAME.
        # =================================================================
        self.next_section("ledger")

        ledger_track = Line([X_L + 1.0, BOT_Y + 0.7, 0], [X_R - 1.0, BOT_Y + 0.7, 0],
                            stroke_color=LINE, stroke_width=1.2)

        # left ledger line: order — KNOWN (check mark, plain INK).
        order_lbl = mono("order of sounds", 19, INK_DIM)
        order_val = mono("known", 19, INK)
        order_row = VGroup(order_lbl, order_val).arrange(RIGHT, buff=0.5)
        check = VGroup(
            Line(LEFT * 0.09 + DOWN * 0.02, DOWN * 0.10, stroke_color=INK, stroke_width=2.6),
            Line(DOWN * 0.10, RIGHT * 0.16 + UP * 0.13, stroke_color=INK, stroke_width=2.6),
        ).next_to(order_row, LEFT, buff=0.30)
        left_block = VGroup(check, order_row)

        # right ledger line: timing — UNKNOWN (Cross, plain INK).
        time_lbl = mono("which frame is which", 19, INK_DIM)
        time_val = mono("unknown", 19, INK)
        time_row = VGroup(time_lbl, time_val).arrange(RIGHT, buff=0.5)
        xcross = VGroup(
            Line(UL * 0.12, DR * 0.12, stroke_color=INK, stroke_width=2.6),
            Line(UR * 0.12, DL * 0.12, stroke_color=INK, stroke_width=2.6),
        ).next_to(time_row, LEFT, buff=0.30)
        right_block = VGroup(xcross, time_row)

        ledger = VGroup(left_block, right_block).arrange(RIGHT, buff=1.1)
        ledger.move_to([0, BOT_Y + 0.18, 0])

        self.play(Create(ledger_track), run_time=0.3)
        self.play(FadeIn(left_block, shift=UP * 0.08), run_time=0.4)
        self.play(FadeIn(right_block, shift=UP * 0.08), run_time=0.4)

        # NAME — the serif #fff payoff.
        payoff = serif("word: yes  —  timing: no", 40, WHITE)
        payoff.move_to([0, BOT_Y - 0.75, 0])
        self.play(Write(payoff), run_time=0.6)

        # =================================================================
        # B4 — POSTER HOLD.
        # =================================================================
        self.next_section("poster")
        self.play(Indicate(payoff, scale_factor=1.05, color=WHITE), run_time=0.5)
        self.wait(0.7)
