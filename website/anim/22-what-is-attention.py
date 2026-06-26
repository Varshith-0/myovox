# website/anim/b09_what_is_attention.py — b09 "What is attention"
#
# Attention's "aha": to name one blurry snapshot, it REACHES to every other
# snapshot in the sentence — near AND far — asks "how relevant are you to me?",
# gets a weight back, and rebuilds itself mostly from the few that matter. The
# loudest answer can come from far away — distance does not matter to it.
#
# Locked 9-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 context   rail "looking both ways was the gentle version / here is the
#               real tool" + caption "a sentence of snapshots".
#   2 pose      one snapshot lights as the QUERY: bright stroke, serif '?',
#               white glow; cap "stand on one snapshot".
#   3 reach     thin faint query-lines fan to ALL others, near and far.
#   4 ask       held: "how relevant are you to me?" — lines still equal/faint.
#   5 reweight  a few thicken/brighten (a FAR one wins), the rest ghost out;
#               weight readouts 0.85 / 0.70 / 0.95 appear.
#   6 rebuild   pulses flow back along the strong lines; '?' -> serif 'AE' flash.
#   7 far       white box snaps around the FAR strong snapshot; distance callout;
#               everything else dims — this is the focal aha.
#   8 sweep     the query slot sweeps the whole row; each stop draws its own
#               live fan (one near + one far pull).
#   9 name      row settles dim; serif 'attention' rises + mono subtitle, one
#               Indicate flare; poster hold.
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"  # single payoff accent

ROW_Y = 0.55
N = 13                # snapshots in the row
CELL = 0.62
BUFF = 0.20
QUERY_I = 4           # the snapshot we disambiguate first
FAR_I = 11            # the deliberately FAR snapshot that wins a strong weight

CAP_Y = 2.18
SUBCAP_Y = ROW_Y - 1.05


def frame_cell(stroke=INK_GHOST, sw=1.2):
    return Square(CELL, stroke_color=stroke, stroke_width=sw, fill_opacity=0)


def fan_bezier(src, tgt, col, sw, op):
    # arc height grows with horizontal span so far lines ride higher than near
    # ones — keeps the fan legible as separate strands, not a blob.
    span = abs(tgt[0] - src[0])
    arch = min(0.18 + 0.14 * span, 0.72)
    mid = (src + tgt) / 2 + UP * arch
    return CubicBezier(src, (src + mid) / 2, (tgt + mid) / 2, tgt,
                       stroke_color=col, stroke_width=sw).set_opacity(op)


class WhatIsAttention(Scene):
    def construct(self):
        seed()
        self.squares = []

        self.beat_context()
        self.beat_pose()
        self.beat_reach()
        self.beat_ask()
        self.beat_reweight()
        self.beat_rebuild()
        self.beat_far()
        self.beat_sweep()
        self.beat_name()

    # -- caption helper: the single line just under the rule that names each move.
    def set_caption(self, text):
        new = mono(text, 18, INK_FAINT).move_to([0, CAP_Y, 0])
        return self.cap.animate.become(new)

    # =====================================================================
    # BEAT 1 — CONTEXT (~1.56s): rail + caption "a sentence of snapshots".
    # =====================================================================
    def beat_context(self):
        self.next_section("context")

        top1 = mono("looking both ways was the gentle version", 19, INK_DIM)
        top1.move_to([0, 3.25, 0])
        top2 = mono("here is the real tool", 16, INK_FAINT)
        top2.next_to(top1, DOWN, buff=0.16)
        rule = Line([-6.4, 2.58, 0], [6.4, 2.58, 0], stroke_color=LINE,
                    stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.5)
        self.play(FadeIn(top2), Create(rule), run_time=0.45)

        self.top_rail = VGroup(top1, top2, rule)

        # the snapshot row arrives now so beat 1 already shows "a sentence".
        cells = VGroup()
        for _ in range(N):
            cells.add(frame_cell())
        cells.arrange(RIGHT, buff=BUFF).move_to([0, ROW_Y, 0])
        self.cells = cells
        self.squares = [c for c in cells]

        baseline = Line(cells.get_left() + DOWN * (CELL / 2 + 0.16),
                        cells.get_right() + DOWN * (CELL / 2 + 0.16),
                        stroke_color=INK_GHOST, stroke_width=1.0)
        time_lbl = mono("time  →", 15, INK_GHOST).next_to(baseline, DOWN, buff=0.14)
        time_lbl.align_to(cells, LEFT)
        self.baseline = baseline
        self.time_lbl = time_lbl

        self.cap = mono("a sentence of snapshots", 18, INK_FAINT)
        self.cap.move_to([0, CAP_Y, 0])

        self.play(
            LaggedStart(*[Create(c) for c in cells], lag_ratio=0.04),
            Create(baseline), FadeIn(time_lbl),
            FadeIn(self.cap),
            run_time=0.55,
        )
        self.wait(0.06)

    # =====================================================================
    # BEAT 2 — POSE (~1.11s): one snapshot lights as the unsure QUERY.
    # =====================================================================
    def beat_pose(self):
        self.next_section("pose")

        q_sq = self.squares[QUERY_I]
        self.q_sq = q_sq
        self.q_mark = serif("?", 30, INK_DIM).move_to(q_sq)
        self.q_glow = q_sq.copy().set_stroke(WHITE, width=3.2, opacity=0.0)
        self.add(self.q_glow)

        q_cap = mono("this snapshot is blurry — which sound is it?", 17, INK_FAINT)
        q_cap.move_to([0, SUBCAP_Y, 0])
        self.sub_cap = q_cap

        self.play(
            q_sq.animate.set_stroke(INK, width=2.2),
            FadeIn(self.q_mark, scale=0.6),
            self.q_glow.animate.set_stroke(WHITE, width=3.2, opacity=0.5),
            self.set_caption("stand on one snapshot"),
            FadeIn(q_cap, shift=UP * 0.08),
            run_time=0.6,
        )
        self.wait(0.4)

    # =====================================================================
    # BEAT 3 — REACH (~1.87s): faint query-lines fan to ALL other snapshots.
    # =====================================================================
    def beat_reach(self):
        self.next_section("reach")

        self.q_top = self.q_sq.get_top() + UP * 0.02
        self.others = [i for i in range(N) if i != QUERY_I]

        self.lines = {}
        for i in self.others:
            tgt = self.squares[i].get_top() + UP * 0.02
            self.lines[i] = fan_bezier(self.q_top, tgt, INK_FAINT, 1.0, 0.22)
        self.line_grp = VGroup(*[self.lines[i] for i in self.others])

        self.play(
            self.set_caption("shine a beam at every other snapshot — near and far"),
            FadeOut(self.sub_cap, shift=DOWN * 0.06),
            run_time=0.45,
        )
        self.play(LaggedStart(*[Create(self.lines[i]) for i in self.others],
                              lag_ratio=0.05), run_time=1.0)
        self.wait(0.35)

    # =====================================================================
    # BEAT 4 — ASK (~1.52s): held question, lines still equal-and-faint.
    # =====================================================================
    def beat_ask(self):
        self.next_section("ask")

        ask_cap = mono('each asks: "how relevant are you to me?"', 17, INK_FAINT)
        ask_cap.move_to([0, SUBCAP_Y, 0])
        self.sub_cap = ask_cap

        self.play(
            self.set_caption("each one answers with a weight"),
            FadeIn(ask_cap, shift=UP * 0.08),
            run_time=0.5,
        )
        self.wait(0.95)

    # =====================================================================
    # BEAT 5 — REWEIGHT (~1.11s): a few thicken/brighten (a FAR one wins).
    # =====================================================================
    def beat_reweight(self):
        self.next_section("reweight")

        # learned relevance weights: FAR_I deliberately strongest (proves distance
        # does not matter); two near neighbours moderate; everything else faint.
        self.strong = {QUERY_I - 1: 0.85, QUERY_I + 1: 0.70, FAR_I: 0.95}

        def weight_of(i):
            return self.strong.get(i, 0.08)

        reweights = []
        for i in self.others:
            w = weight_of(i)
            sw = 0.6 + 3.4 * w
            op = 0.06 + 0.9 * w if i in self.strong else 0.05
            col = WHITE if i == FAR_I else INK
            reweights.append(
                self.lines[i].animate.set_stroke(col, width=sw, opacity=op))

        self.play(
            self.set_caption("a few answer loudly — the rest barely"),
            FadeOut(self.sub_cap, shift=DOWN * 0.06),
            *reweights,
            run_time=0.7,
        )

        # weight readouts above the strong snapshots so relevance is explicit.
        self.w_reads = VGroup()
        for i, w in self.strong.items():
            c = WHITE if i == FAR_I else INK_DIM
            r = mono(f"{w:.2f}", 15, c).next_to(self.squares[i], UP, buff=0.62)
            self.w_reads.add(r)
        self.play(LaggedStart(*[FadeIn(r) for r in self.w_reads],
                              lag_ratio=0.15), run_time=0.4)

    # =====================================================================
    # BEAT 6 — REBUILD (~1.94s): pulses flow back; '?' -> serif 'AE' flash.
    # =====================================================================
    def beat_rebuild(self):
        self.next_section("rebuild")

        # dim the ghost (non-strong) lines further so flow-back pulses dominate.
        ghosts = [self.lines[i].animate.set_stroke(opacity=0.03)
                  for i in self.others if i not in self.strong]

        pulses = VGroup()
        flows = []
        for i in self.strong:
            d = Dot(radius=0.055, color=(WHITE if i == FAR_I else INK),
                    fill_opacity=0.95).move_to(self.squares[i].get_top() + UP * 0.02)
            pulses.add(d)
            flows.append(MoveAlongPath(d, self.lines[i].copy().reverse_direction()))
        self.add(pulses)

        self.play(
            self.set_caption("the snapshot rebuilds itself from the few that matter"),
            *ghosts,
            *flows,
            run_time=1.1, rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(*pulses)

        # the query sharpens: '?' -> a named sound, white flash.
        self.named = serif("AE", 28, INK).move_to(self.q_sq)
        self.play(
            ReplacementTransform(self.q_mark, self.named),
            self.q_sq.animate.set_stroke(WHITE, width=2.6),
            Flash(self.q_sq.get_center(), color=WHITE, flash_radius=0.62,
                  line_length=0.12, num_lines=14, run_time=0.6),
            run_time=0.6,
        )
        self.wait(0.2)

    # =====================================================================
    # BEAT 7 — FAR (~2.34s): white box around the FAR snapshot; distance callout.
    # =====================================================================
    def beat_far(self):
        self.next_section("far")

        # dim the entire row + all lines except the far snapshot and its winning
        # line, so the far-frame box is the sole focal aha.
        dims = []
        for i in self.others:
            if i != FAR_I:
                dims.append(self.lines[i].animate.set_stroke(opacity=0.02))
        near_reads = VGroup(*[r for j, r in zip(self.strong, self.w_reads)
                              if j != FAR_I])

        far_box = SurroundingRectangle(self.squares[FAR_I], color=WHITE,
                                       stroke_width=1.8, buff=0.06)
        far_cap = mono("a far snapshot can matter most — distance is irrelevant",
                       17, INK_DIM).move_to([0, SUBCAP_Y, 0])
        self.sub_cap = far_cap

        self.play(
            self.set_caption("the loudest answer came from far away"),
            self.cells.animate.set_stroke(opacity=0.28),
            self.named.animate.set_opacity(0.4),
            self.q_glow.animate.set_opacity(0.0),
            near_reads.animate.set_opacity(0.18),
            *dims,
            run_time=0.7,
        )
        self.play(
            Create(far_box),
            FadeIn(far_cap, shift=UP * 0.08),
            Indicate(self.squares[FAR_I], scale_factor=1.12, color=WHITE),
            run_time=0.7,
        )
        self.far_box = far_box
        self.wait(0.9)

    # =====================================================================
    # BEAT 8 — SWEEP (~1.96s): query slot sweeps the row; each stop draws its fan.
    # =====================================================================
    def beat_sweep(self):
        self.next_section("sweep")

        # retire the first query's fan, readouts, box, named result.
        self.play(
            FadeOut(self.line_grp), FadeOut(self.w_reads), FadeOut(self.named),
            FadeOut(self.far_box),
            FadeOut(self.sub_cap, shift=DOWN * 0.06),
            self.q_sq.animate.set_stroke(INK_GHOST, width=1.2),
            self.cells.animate.set_stroke(opacity=1.0),
            self.set_caption("every snapshot does the same — its own pattern of pulls"),
            run_time=0.5,
        )
        self.remove(self.q_glow)

        # per source snapshot, pre-pick a couple of "relevant" targets (one near,
        # one far) so the sweep visibly reaches across distances at every stop.
        rel = {}
        for s in range(N):
            near = s + (1 if s + 1 < N else -1)
            far = (s + N // 2) % N
            if far == s:
                far = (s + 1) % N
            rel[s] = [near, far]

        qT = ValueTracker(float(QUERY_I))

        marker = Square(CELL, stroke_color=WHITE, stroke_width=2.4,
                        fill_color=WHITE, fill_opacity=0.06)
        marker.move_to(self.squares[QUERY_I])

        squares = self.squares

        def cur_idx():
            return int(round(qT.get_value()))

        def fan_updater(grp):
            i = cur_idx()
            src = squares[i].get_top() + UP * 0.02
            new = VGroup()
            for j in range(N):
                if j == i:
                    continue
                tgt = squares[j].get_top() + UP * 0.02
                strong_j = j in rel[i]
                sw = 1.8 if strong_j else 0.8
                op = 0.92 if strong_j else 0.06
                col = INK if strong_j else INK_FAINT
                new.add(fan_bezier(src, tgt, col, sw, op))
            grp.become(new)

        live_fan = VGroup()
        fan_updater(live_fan)
        live_fan.add_updater(fan_updater)
        marker.add_updater(lambda m: m.move_to(squares[cur_idx()]))
        self.add(live_fan, marker)

        self.play(qT.animate.set_value(float(N - 1)), run_time=0.95,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(qT.animate.set_value(1.0), run_time=0.85,
                  rate_func=rate_functions.ease_in_out_sine)
        live_fan.clear_updaters()
        marker.clear_updaters()
        self.play(FadeOut(live_fan), FadeOut(marker), run_time=0.3)

    # =====================================================================
    # BEAT 9 — NAME (~1.86s): serif 'attention' + subtitle + Indicate; hold.
    # =====================================================================
    def beat_name(self):
        self.next_section("name")

        self.play(
            self.cells.animate.set_opacity(0.5),
            self.baseline.animate.set_stroke(opacity=0.4),
            self.time_lbl.animate.set_opacity(0.35),
            self.top_rail.animate.set_opacity(0.4),
            FadeOut(self.cap, shift=UP * 0.08),
            run_time=0.45,
        )

        name = serif("attention", 60, INK).move_to([0, -2.55, 0])
        sub = mono("reach anywhere, weigh by relevance", 20, INK_DIM)
        sub.next_to(name, DOWN, buff=0.22)
        glowing = glow(name.copy().set_color(WHITE))
        self.add(glowing)
        glowing.set_opacity(0.0)

        self.play(FadeIn(name, shift=UP * 0.12),
                  glowing.animate.set_opacity(0.35), run_time=0.5)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.4)
        self.play(Indicate(name, scale_factor=1.1, color=WHITE),
                  glowing.animate.set_opacity(0.0), run_time=0.55)
        self.remove(glowing)
        self.wait(0.55)
