# website/anim/b09_what_is_attention.py — b09 "A spotlight that reaches"
#
# Attention's "aha": to name one blurry frame, the reader REACHES to every other
# frame in the sentence — near AND far — asks "how relevant are you to me?", gets
# a weight back, and updates itself mostly from the few that matter. Distance does
# not matter to it.
#
# Three-zone full-canvas composition (pose -> build -> transform -> name):
#   TOP   (y~+2.6..+3.6) CONTEXT: rail carried from S15 — "one frame can't decide
#                  alone; let it look both ways" softening into "let it look
#                  EVERYWHERE". A caption names the current move.
#   CENTER(-1.6..+2.0) MECHANISM: a long row of ~13 frame-cells. One lights as the
#                  QUERY (dim, unsure, '?'). Thin query-lines fan to ALL others.
#                  They reweight: a few thicken/brighten (a FAR one wins), the rest
#                  ghost out. Weighted info flows back; '?' sharpens to a named
#                  sound 'AE'. Then the query slot SWEEPS along the row, each
#                  position drawing its own pattern of pulls.
#   BOTTOM(-3.6..-2.4) TAKEAWAY: serif #fff 'attention' + mono
#                  'reach anywhere, weigh by relevance'.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"  # single payoff accent

ROW_Y = 0.55
N = 13                # frames in the row
CELL = 0.62
BUFF = 0.20
QUERY_I = 4           # the frame we disambiguate first
FAR_I = 11            # the deliberately FAR frame that wins a strong weight


def frame_cell(label=None, fs=22, stroke=INK_GHOST, sw=1.2):
    sq = Square(CELL, stroke_color=stroke, stroke_width=sw, fill_opacity=0)
    if label is None:
        return VGroup(sq), sq, None
    t = mono(label, fs, INK_FAINT).move_to(sq)
    return VGroup(sq, t), sq, t


class WhatIsAttention(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B0 — CONTEXT RAIL: inherit "look both ways", widen to "everywhere".
        # =================================================================
        self.next_section("context")

        top1 = mono("looking both ways was the gentle version", 19, INK_DIM)
        top1.move_to([0, 3.25, 0])
        top2 = mono("here is the real tool", 16, INK_FAINT)
        top2.next_to(top1, DOWN, buff=0.16)
        rule = Line([-6.4, 2.58, 0], [6.4, 2.58, 0], stroke_color=LINE,
                    stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), run_time=0.4)
        self.play(FadeIn(top2), Create(rule), run_time=0.34)

        # a caption slot just under the rule that names each move in turn.
        cap = mono("a sentence of frames", 18, INK_FAINT).move_to([0, 2.18, 0])
        self.play(FadeIn(cap), run_time=0.3)

        # =================================================================
        # B1 — POSE: the long row of frames; one lights as the unsure QUERY.
        # =================================================================
        self.next_section("pose")

        cells = VGroup()
        squares = []
        for i in range(N):
            g, sq, _ = frame_cell(None)
            cells.add(g)
            squares.append(sq)
        cells.arrange(RIGHT, buff=BUFF).move_to([0, ROW_Y, 0])
        squares = [c[0] for c in cells]

        baseline = Line(cells.get_left() + DOWN * (CELL / 2 + 0.16),
                        cells.get_right() + DOWN * (CELL / 2 + 0.16),
                        stroke_color=INK_GHOST, stroke_width=1.0)
        time_lbl = mono("time  →", 15, INK_GHOST).next_to(baseline, DOWN, buff=0.14)
        time_lbl.align_to(cells, LEFT)

        self.play(LaggedStartMap(Create, cells, lag_ratio=0.04, run_time=0.7),
                  Create(baseline), FadeIn(time_lbl), run_time=0.7)

        # light QUERY_I as the query: brighter frame, a '?' inside, a soft glow.
        q_sq = squares[QUERY_I]
        q_mark = serif("?", 30, INK_DIM).move_to(q_sq)
        q_glow = q_sq.copy().set_stroke(WHITE, width=3.2, opacity=0.0)
        self.add(q_glow)
        q_cap = mono("this frame is blurry — which sound is it?", 17, INK_FAINT)
        q_cap = q_cap.move_to([0, ROW_Y - 1.05, 0])

        self.play(
            q_sq.animate.set_stroke(INK, width=2.2),
            FadeIn(q_mark, scale=0.6),
            q_glow.animate.set_stroke(WHITE, width=3.2, opacity=0.5),
            cap.animate.become(
                mono("stand on one frame", 18, INK_FAINT).move_to([0, 2.18, 0])),
            FadeIn(q_cap, shift=UP * 0.08),
            run_time=0.55,
        )

        # =================================================================
        # B2 — BUILD: thin query-lines fan from the query to ALL other frames.
        # =================================================================
        self.next_section("reach")

        q_top = q_sq.get_top() + UP * 0.02
        others = [i for i in range(N) if i != QUERY_I]

        def fan_bezier(src, tgt, col, sw, op):
            # arc height grows with horizontal span so far lines ride higher than
            # near ones — keeps the fan legible as separate strands, not a blob.
            span = abs(tgt[0] - src[0])
            arch = min(0.18 + 0.14 * span, 0.72)
            mid = (src + tgt) / 2 + UP * arch
            return CubicBezier(src, (src + mid) / 2, (tgt + mid) / 2, tgt,
                               stroke_color=col, stroke_width=sw).set_opacity(op)

        lines = {}
        for i in others:
            tgt = squares[i].get_top() + UP * 0.02
            lines[i] = fan_bezier(q_top, tgt, INK_FAINT, 1.0, 0.22)
        line_grp = VGroup(*[lines[i] for i in others])

        self.play(
            cap.animate.become(
                mono("shine a beam at every other frame — near and far", 18,
                     INK_FAINT).move_to([0, 2.18, 0])),
            FadeOut(q_cap, shift=DOWN * 0.06),
            run_time=0.4,
        )
        self.play(LaggedStartMap(Create, line_grp, lag_ratio=0.05, run_time=0.85))

        ask_cap = mono('each asks: "how relevant are you to me?"', 17, INK_FAINT)
        ask_cap.move_to([0, ROW_Y - 1.05, 0])
        self.play(FadeIn(ask_cap, shift=UP * 0.08), run_time=0.35)

        # =================================================================
        # B3 — TRANSFORM: lines reweight. A few thicken/brighten (a FAR one
        #      wins); the rest thin to ghost. Weighted info flows back; '?' -> 'AE'.
        # =================================================================
        self.next_section("reweight")

        # learned relevance weights (FAR_I deliberately strong to prove distance
        # does not matter; two near neighbours moderate; everything else faint).
        strong = {QUERY_I - 1: 0.85, QUERY_I + 1: 0.7, FAR_I: 0.95}

        def weight_of(i):
            return strong.get(i, 0.08)

        reweights = []
        for i in others:
            w = weight_of(i)
            sw = 0.6 + 3.4 * w
            op = 0.06 + 0.9 * w if i in strong else 0.05
            col = WHITE if i == FAR_I else INK
            reweights.append(lines[i].animate.set_stroke(col, width=sw, opacity=op))

        self.play(
            cap.animate.become(
                mono("a few answer loudly — the rest barely", 18, INK_FAINT)
                .move_to([0, 2.18, 0])),
            FadeOut(ask_cap, shift=DOWN * 0.06),
            *reweights,
            run_time=0.85,
        )

        # weight readouts above the strong frames so the relevance is explicit.
        w_reads = VGroup()
        for i, w in strong.items():
            c = WHITE if i == FAR_I else INK_DIM
            r = mono(f"{w:.2f}", 15, c).next_to(squares[i], UP, buff=0.62)
            w_reads.add(r)
        self.play(LaggedStartMap(FadeIn, w_reads, lag_ratio=0.15, run_time=0.4))

        # call out distance-independence: the FAR frame won a heavy weight.
        far_box = SurroundingRectangle(squares[FAR_I], color=WHITE,
                                       stroke_width=1.8, buff=0.06)
        far_cap = mono("a far frame can matter most — distance is irrelevant", 17,
                       INK_DIM).move_to([0, ROW_Y - 1.05, 0])
        self.play(Create(far_box), FadeIn(far_cap, shift=UP * 0.08), run_time=0.5)
        self.wait(0.1)

        # weighted information flows BACK along the strong lines into the query —
        # pulses ride each strong bezier from the frame toward the query.
        pulses = VGroup()
        flows = []
        for i in strong:
            d = Dot(radius=0.055, color=(WHITE if i == FAR_I else INK),
                    fill_opacity=0.95).move_to(squares[i].get_top() + UP * 0.02)
            pulses.add(d)
            flows.append(MoveAlongPath(d, lines[i].copy().reverse_direction()))
        self.add(pulses)
        self.play(
            cap.animate.become(
                mono("the frame updates itself from the few that matter", 18,
                     INK_FAINT).move_to([0, 2.18, 0])),
            FadeOut(far_cap, shift=DOWN * 0.06),
            FadeOut(far_box),
            *flows,
            run_time=0.85, rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(*pulses)

        # the query sharpens: '?' -> a named sound, glow flares.
        named = serif("AE", 28, INK).move_to(q_sq)
        self.play(
            ReplacementTransform(q_mark, named),
            q_sq.animate.set_stroke(WHITE, width=2.6),
            Flash(q_sq.get_center(), color=WHITE, flash_radius=0.62,
                  line_length=0.12, num_lines=14, run_time=0.6),
            run_time=0.55,
        )

        # =================================================================
        # B4 — SWEEP: the query slot travels the row; each frame draws its own
        #      pattern of pulls (a thin live fan that re-aims as it moves).
        # =================================================================
        self.next_section("sweep")

        # retire the first query's fan + named result, keep the row + glow gone.
        self.play(
            FadeOut(line_grp), FadeOut(w_reads), FadeOut(named),
            q_glow.animate.set_opacity(0.0),
            q_sq.animate.set_stroke(INK_GHOST, width=1.2),
            cap.animate.become(
                mono("every frame does the same — its own pattern of pulls", 18,
                     INK_FAINT).move_to([0, 2.18, 0])),
            run_time=0.5,
        )
        self.remove(q_glow)

        # a live fan that follows a moving query index. We pre-pick, per source
        # frame, a couple of "relevant" targets (one near, one far) so the sweep
        # visibly reaches across distances at every stop.
        rng = np.random.default_rng(11)
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
        marker.move_to(squares[QUERY_I])

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
                op = 0.92 if strong_j else 0.07
                col = INK if strong_j else INK_FAINT
                new.add(fan_bezier(src, tgt, col, sw, op))
            grp.become(new)

        live_fan = VGroup()
        fan_updater(live_fan)
        live_fan.add_updater(fan_updater)
        marker.add_updater(lambda m: m.move_to(squares[cur_idx()]))
        self.add(live_fan, marker)

        # sweep right to the end, then back left past the start — each stop reaches.
        self.play(qT.animate.set_value(float(N - 1)), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(qT.animate.set_value(1.0), run_time=1.4,
                  rate_func=rate_functions.ease_in_out_sine)
        live_fan.clear_updaters()
        marker.clear_updaters()
        self.play(FadeOut(live_fan), FadeOut(marker), run_time=0.3)

        # =================================================================
        # B5 — NAME IT + POSTER HOLD.
        # =================================================================
        self.next_section("name")

        # settle the row to a quiet anchor; bring the name up from the bottom.
        self.play(
            cells.animate.set_opacity(0.5),
            baseline.animate.set_stroke(opacity=0.4),
            time_lbl.animate.set_opacity(0.35),
            FadeOut(cap, shift=UP * 0.08),
            run_time=0.4,
        )

        name = serif("attention", 60, INK).move_to([0, -2.55, 0])
        sub = mono("reach anywhere, weigh by relevance", 20, INK_DIM)
        sub.next_to(name, DOWN, buff=0.22)
        self.play(FadeIn(name, shift=UP * 0.12), run_time=0.5)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.35)
        self.play(Indicate(name, scale_factor=1.1, color=WHITE), run_time=0.55)

        self.wait(0.6)
