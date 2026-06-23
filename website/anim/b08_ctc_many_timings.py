# website/anim/b08_ctc_many_timings.py — B08 "Reward every right timing"
#
# Carries over from S12 (CTC): timing is unlabeled, yet MANY per-frame timings
# collapse to the same word "cat". This bridge answers HOW that becomes a
# training signal: instead of betting on ONE true timing, training sums the
# odds of EVERY timing that spells the word, and pushes that one total up —
# so all valid orderings rise together, while a WRONG-ORDER row gets no push.
#
# Metaphor: many roads, one destination, all the right tolls refunded.
#
# Three-zone full-canvas composition (pose -> build -> transform -> name):
#   TOP   (y ~ +2.6..+3.6) CONTEXT: carried-over target word "cat" + caption.
#   CENTER(y ~ -0.6..+2.0) MECHANISM: three valid 9-cell alignment rows that all
#                  spell "cat", each gaining a small probability bar; a Σ gathers
#                  the three into ONE "P(cat)" meter that an upward force pushes
#                  higher — and the three source bars rise in lockstep.
#   LOWER (y ~ -2.0) CONTRAST: a WRONG-ORDER row gets no push, dims, is crossed.
#   BOTTOM(y ~ -3.3) TAKEAWAY: a single live counter — P(cat) total — climbing,
#                  resolving to the serif payoff. Poster holds ~0.6 s.
from manim import *
from emg_style import *

WHITE = "#ffffff"

ROW_LABS = [
    ["∅", "K", "K", "∅", "AE", "AE", "AE", "T", "∅"],
    ["K", "K", "∅", "AE", "AE", "T", "T", "T", "∅"],
    ["∅", "∅", "K", "AE", "AE", "AE", "T", "T", "∅"],
]
ROW_PROB = [0.18, 0.13, 0.10]            # individual valid-path odds
NEW_PROB = [0.31, 0.24, 0.19]            # after the push, all rise together
WRONG_LABS = ["∅", "T", "T", "∅", "AE", "AE", "K", "K", "∅"]  # spells "tak"

CELL = 0.34
BUFF = 0.10
ROW_X = -6.3            # shared left edge of every cell row
BAR_X = -0.55          # left edge of every probability bar
BAR_W = 1.55
MAX_P = 0.36           # bar full scale (leaves headroom past the boosted 0.31)
MAX_TOTAL = 0.80       # meter full scale
SIG_X = 2.55
METER_X = 4.6
METER_TOP, METER_BOT = 1.95, -0.55


def alignment_row(labs, sq=CELL, buff=BUFF, fs=18):
    """A row of frame-squares with a phoneme-or-blank label inside each.
    Returns (group, squares, texts). Blanks are dim. (Rhymes with s12.)"""
    squares = VGroup(*[
        Square(sq, stroke_color=INK_GHOST, stroke_width=1.2, fill_opacity=0)
        for _ in labs
    ]).arrange(RIGHT, buff=buff)
    texts = VGroup()
    for i, l in enumerate(labs):
        c = INK_FAINT if l == "∅" else INK
        texts.add(mono(l, fs, c).move_to(squares[i]))
    return VGroup(squares, texts), squares, texts


def fill_width(value, max_val=MAX_P, w_full=BAR_W):
    return max(1e-3, w_full * value / max_val)


class CtcManyTimings(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B0 — CARRY-OVER: the target word "cat" from S12, posed up top.
        # =================================================================
        self.next_section("carryover")

        word = serif("cat", 40, INK).move_to([0, 3.18, 0])
        word_tag = mono("the word we want", 16, INK_FAINT).next_to(word, RIGHT, buff=0.4)
        cap = mono("timing is unlabeled — so reward EVERY timing that spells it",
                   17, INK_FAINT).move_to([0, 2.60, 0])
        rule = Line([-6.4, 2.30, 0], [6.4, 2.30, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(word, shift=DOWN * 0.12), FadeIn(word_tag), run_time=0.5)
        self.play(FadeIn(cap), Create(rule), run_time=0.45)
        self.wait(0.25)

        # =================================================================
        # B1 — POSE: three valid 9-cell alignment rows; tag that all spell cat.
        # =================================================================
        self.next_section("pose")

        ROW_Y = [1.55, 0.55, -0.45]
        rows = []
        for k, labs in enumerate(ROW_LABS):
            r, rsq, rtx = alignment_row(labs)
            r.move_to([0, ROW_Y[k], 0])
            r.align_to([ROW_X, 0, 0], LEFT)
            rows.append((r, rsq, rtx))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r, _, _ in rows],
                              lag_ratio=0.25, run_time=1.0))

        same_tag = mono("three different timings — all spell  c a t", 15, INK_FAINT)
        same_tag.next_to(rows[2][0], DOWN, buff=0.30).align_to([ROW_X, 0, 0], LEFT)
        self.play(FadeIn(same_tag), run_time=0.45)
        self.wait(0.3)

        # =================================================================
        # B2 — BUILD: each row gets its own small probability bar + readout.
        #      A thin arrow leads from each row into its bar.
        # =================================================================
        self.next_section("build")

        bars = []
        for k, y in enumerate(ROW_Y):
            arr = Line([rows[k][1].get_right()[0] + 0.16, y, 0], [BAR_X - 0.14, y, 0],
                       stroke_color=INK_GHOST, stroke_width=1.4)
            head = Triangle(stroke_width=0, fill_color=INK_GHOST, fill_opacity=1.0)\
                .scale(0.055).rotate(-PI / 2).move_to(arr.get_end())
            track = Rectangle(width=BAR_W, height=0.16, stroke_color=INK_GHOST,
                              stroke_width=1.2, fill_opacity=0)\
                .move_to([BAR_X, y, 0], aligned_edge=LEFT)
            track.align_to([BAR_X, 0, 0], LEFT)
            fill = Rectangle(width=fill_width(ROW_PROB[k]), height=0.16, stroke_width=0,
                             fill_color=INK, fill_opacity=0.85)\
                .align_to(track, LEFT).set_y(y)
            val = num(f"{ROW_PROB[k]:.2f}", 19, INK)\
                .next_to(track, RIGHT, buff=0.20)
            bars.append(dict(arr=VGroup(arr, head), track=track, fill=fill,
                             val=val, base=ROW_PROB[k]))

        bar_head = mono("odds of this timing", 14, INK_FAINT)\
            .next_to(bars[0]["track"], UP, buff=0.30).align_to(bars[0]["track"], LEFT)
        self.play(
            *[Create(b["arr"]) for b in bars],
            *[Create(b["track"]) for b in bars],
            FadeIn(bar_head),
            run_time=0.45,
        )
        # grow each fill from zero, left-anchored.
        for b in bars:
            b["fill"].stretch_to_fit_width(1e-3).align_to(b["track"], LEFT)
            self.add(b["fill"])
        self.play(
            *[b["fill"].animate.stretch_to_fit_width(fill_width(b["base"]))
              .align_to(b["track"], LEFT) for b in bars],
            *[FadeIn(b["val"]) for b in bars],
            run_time=0.8,
        )
        self.wait(0.3)

        # =================================================================
        # B3 — TRANSFORM: a Σ gathers the three bars into ONE P(cat) meter,
        #      and an upward force pushes the total higher — all bars rise too.
        # =================================================================
        self.next_section("sum")

        meter_track = Line([METER_X, METER_BOT, 0], [METER_X, METER_TOP, 0],
                           stroke_color=INK_GHOST, stroke_width=2.0)
        total = ValueTracker(sum(ROW_PROB))     # 0.41
        meter_fill = Rectangle(width=0.34, height=1e-3, stroke_width=0,
                               fill_color=INK, fill_opacity=0.9)

        def update_meter(m):
            h = (METER_TOP - METER_BOT) * total.get_value() / MAX_TOTAL
            m.become(Rectangle(width=0.34, height=max(1e-3, h), stroke_width=0,
                               fill_color=INK, fill_opacity=0.9))
            m.move_to([METER_X, METER_BOT + h / 2, 0])
        meter_fill.add_updater(update_meter)

        sig = serif("Σ", 44, INK).move_to([SIG_X, 0.55, 0])
        meter_lab = mono("P(cat)", 15, INK_DIM).move_to([METER_X, METER_TOP + 0.28, 0])

        # gathering lines from each value into the Σ.
        gathers = VGroup(*[
            Line(bars[k]["val"].get_right() + RIGHT * 0.10, sig.get_left() + LEFT * 0.10,
                 stroke_color=INK_GHOST, stroke_width=1.1)
            for k in range(3)
        ])
        # one line from Σ into the meter.
        feed = Line(sig.get_right() + RIGHT * 0.10, [METER_X - 0.30, 0.55, 0],
                    stroke_color=INK_GHOST, stroke_width=1.1)

        self.add(meter_fill)
        self.play(
            FadeIn(sig, scale=0.7),
            LaggedStartMap(Create, gathers, lag_ratio=0.12),
            run_time=0.5,
        )
        self.play(
            Create(feed),
            Create(meter_track),
            FadeIn(meter_lab),
            run_time=0.45,
        )

        # BOTTOM live counter — the single live counter() in the scene (s12 rule).
        cnt_at = np.array([-3.3, -3.30, 0])
        cnt_read = counter(total, fmt=lambda v: f"{v:.2f}", s=42, c=INK, at=cnt_at)
        cnt_tag = mono("total P(cat) = Σ over all valid timings", 15, INK_FAINT)
        cnt_tag.next_to(cnt_read, UP, buff=0.18)
        self.add(cnt_read)
        self.play(FadeIn(cnt_tag), run_time=0.3)

        # THE PUSH: an upward force arrow drives the meter up; all three source
        # bars rise together — none singled out.
        force_shaft = Line([METER_X, METER_BOT - 1.05, 0], [METER_X, METER_BOT - 0.28, 0],
                           stroke_color=INK, stroke_width=3.5)
        force_head = Triangle(stroke_width=0, fill_color=INK, fill_opacity=1.0)\
            .scale(0.11).move_to([METER_X, METER_BOT - 0.18, 0])
        force = VGroup(force_shaft, force_head)
        push_lab = mono("push the TOTAL up", 14, INK_DIM).next_to(force, DOWN, buff=0.12)
        self.play(FadeIn(force, shift=UP * 0.12), FadeIn(push_lab), run_time=0.45)
        self.wait(0.3)

        self.play(
            total.animate.set_value(sum(NEW_PROB)),
            *[bars[k]["fill"].animate.stretch_to_fit_width(fill_width(NEW_PROB[k]))
              .align_to(bars[k]["track"], LEFT) for k in range(3)],
            *[bars[k]["val"].animate.become(
                num(f"{NEW_PROB[k]:.2f}", 19, INK).next_to(bars[k]["track"], RIGHT, buff=0.20))
              for k in range(3)],
            force.animate.shift(UP * 0.5),
            push_lab.animate.shift(UP * 0.5),
            run_time=1.15, rate_func=smooth,
        )
        self.play(Indicate(meter_lab, scale_factor=1.14, color=WHITE), run_time=0.45)
        rise_note = mono("all valid timings rise together — none chosen as the truth",
                         14, INK_FAINT).move_to([-2.6, -1.55, 0])
        self.play(FadeIn(rise_note, shift=UP * 0.06), run_time=0.45)
        self.wait(0.4)

        # =================================================================
        # B4 — CONTRAST: a WRONG-ORDER row gets no push, dims, and is crossed.
        # =================================================================
        self.next_section("contrast")

        self.play(FadeOut(rise_note), run_time=0.2)
        wrong_y = -1.55
        wr, wrsq, wrtx = alignment_row(WRONG_LABS)
        wr.move_to([0, wrong_y, 0]).align_to([ROW_X, 0, 0], LEFT)
        warr = Line([wrsq.get_right()[0] + 0.16, wrong_y, 0], [BAR_X - 0.14, wrong_y, 0],
                    stroke_color=INK_GHOST, stroke_width=1.4)
        wtrack = Rectangle(width=BAR_W, height=0.16, stroke_color=INK_GHOST,
                           stroke_width=1.2, fill_opacity=0)\
            .move_to([BAR_X, wrong_y, 0], aligned_edge=LEFT).align_to([BAR_X, 0, 0], LEFT)
        wfill = Rectangle(width=fill_width(0.02), height=0.16, stroke_width=0,
                          fill_color=INK, fill_opacity=0.4)\
            .align_to(wtrack, LEFT).set_y(wrong_y)
        wlab = mono("wrong order — spells \"tak\"", 13, INK_FAINT)\
            .next_to(wr, DOWN, buff=0.16).align_to([ROW_X, 0, 0], LEFT)
        wrong_grp = VGroup(wr, warr, wtrack, wfill, wlab)
        self.play(FadeIn(wrong_grp, shift=RIGHT * 0.08), run_time=0.5)

        # the upward force does NOT reach it: it stays low, dims, gets crossed.
        cross = Cross(wrsq, stroke_color=INK, stroke_width=2.6).scale(0.55)
        no_push = mono("no push", 13, INK_FAINT).next_to(wtrack, RIGHT, buff=0.45)
        self.play(
            VGroup(wr, warr, wtrack, wfill).animate.set_opacity(0.30),
            wlab.animate.set_opacity(0.30),
            Create(cross),
            FadeIn(no_push, shift=LEFT * 0.05),
            run_time=0.65,
        )
        self.wait(0.4)

        # =================================================================
        # B5 — NAME IT + POSTER HOLD.
        # =================================================================
        self.next_section("name_it")

        total.clear_updaters()
        meter_fill.clear_updaters()
        cnt_read.clear_updaters()

        payoff = serif("reward every right timing", 32, WHITE).move_to([0, -3.05, 0])
        payoff_g = glow(payoff)
        sub = mono("sum over all valid alignments", 15, INK_DIM)\
            .next_to(payoff, UP, buff=0.16)
        self.play(
            FadeOut(cnt_read), FadeOut(cnt_tag),
            FadeIn(sub, shift=UP * 0.08),
            run_time=0.5,
        )
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff), run_time=0.6)
        self.wait(0.6)


if __name__ == "__main__":
    pass
