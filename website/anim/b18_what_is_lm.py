# website/anim/b18_what_is_lm.py  —  B18 "What English expects" (the language model)
#
# The "aha": a language model has read mountains of text and learned ONE thing —
# given the words so far, which word likely comes NEXT. It can't hear; it only
# reads. The map's toll borrows this: likely continuations are cheap edges, wild
# ones are expensive edges, so the cheapest road bends toward sensible English.
#
# Three persistent zones (pose -> build -> transform -> name), read at any frame:
#   TOP    (y ~ +3.0): context cap — part of the toll comes from a language model.
#   CENTER (-1.6..+2.3): the mechanism — a stub "the peanut ___" fans into ranked
#          candidate words (bar = likelihood), then each candidate becomes a
#          toll-road EDGE whose thickness is the cost: 'butter' thin/cheap,
#          'bicycle' thick/expensive; a route bends toward 'butter'.
#   BOTTOM (-3.6..-2.6): the takeaway — "it can't hear — only reads" resolving to
#          the NAME: a next-word guesser, with the 4-gram-vs-7B clarifier.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

TOP_Y = 3.12
STUB_Y = 1.95
FAN_Y = 0.30
BOT_Y = -3.05


def tri(angle, c, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def flat_arrow(start, end, c=INK_FAINT, w=2.0):
    """Thin shaft + triangular head — avoids Arrow tip glitches."""
    shaft = Line(start, end, stroke_color=c, stroke_width=w)
    head = tri(shaft.get_angle() - PI / 2, c, 1.0, 0.085).move_to(shaft.get_end())
    return VGroup(shaft, head)


class WhatIsLm(Scene):
    def construct(self):
        seed()

        # candidate next words after "the peanut", with relative likelihood 0..1.
        # 'butter' lights up bright; 'bicycle' stays dim.
        cands = [
            ("butter", 1.00),
            ("brittle", 0.42),
            ("oil", 0.30),
            ("allergy", 0.18),
            ("bicycle", 0.05),
        ]

        # =================================================================
        # B0 — POSE: the partial sentence, and the context cap up top.
        # =================================================================
        self.next_section("pose")

        cap = mono("part of every toll comes from a language model", 19, INK_FAINT)
        cap.move_to([0, TOP_Y, 0])
        rule = Line([-6.2, TOP_Y - 0.34, 0], [6.2, TOP_Y - 0.34, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(cap, shift=DOWN * 0.12), Create(rule), run_time=0.5)

        # "the peanut ___" — the stub the model must continue. The blank is a
        # faint underscored slot waiting for a word.
        the_w = mono("the", 34, INK_DIM)
        peanut_w = mono("peanut", 34, INK)
        slot_line = Line(LEFT * 0.55, RIGHT * 0.55, stroke_color=INK_FAINT,
                         stroke_width=2.2)
        slot = VGroup(slot_line)
        stub = VGroup(the_w, peanut_w, slot).arrange(RIGHT, buff=0.34)
        stub.move_to([0, STUB_Y, 0])

        self.play(FadeIn(the_w, shift=RIGHT * 0.1), run_time=0.28)
        self.play(FadeIn(peanut_w, shift=RIGHT * 0.1), run_time=0.3)
        self.play(Create(slot_line), run_time=0.3)
        # a soft pulse on the slot — "what comes next?"
        self.play(slot_line.animate.set_stroke(INK, width=2.6),
                  run_time=0.25)
        self.play(slot_line.animate.set_stroke(INK_FAINT, width=2.2),
                  run_time=0.25)

        # =================================================================
        # B1 — BUILD: a fan of candidate next words drops in, ranked by
        #      likelihood (bar height + a num() readout each).
        # =================================================================
        self.next_section("fan")

        ask = mono("which word likely comes next?", 16, INK_FAINT)
        ask.next_to(stub, DOWN, buff=0.30)
        self.play(FadeIn(ask, shift=UP * 0.06), run_time=0.32)

        # five vertical likelihood bars across the centre band.
        n = len(cands)
        col_w = 2.30
        bar_w = 0.46
        max_h = 1.70
        base_y = FAN_Y - 0.55
        xs = [(i - (n - 1) / 2) * col_w for i in range(n)]

        bars = VGroup()
        word_lbls = VGroup()
        pct_lbls = VGroup()
        for i, (w, p) in enumerate(cands):
            h = 0.14 + max_h * p
            op = 0.30 + 0.65 * p
            r = Rectangle(width=bar_w, height=h, stroke_width=0,
                          fill_color=INK, fill_opacity=op)
            r.move_to([xs[i], base_y + h / 2, 0])
            bars.add(r)
            wl = mono(w, 18, INK if p > 0.6 else INK_DIM)
            wl.next_to(r, UP, buff=0.16)
            word_lbls.add(wl)
            pl = num(f"{int(round(p * 100))}", 22, INK if p > 0.6 else INK_FAINT)
            pl.move_to([xs[i], base_y - 0.34, 0])
            pct_lbls.add(pl)

        baseline = Line([xs[0] - 0.5, base_y, 0], [xs[-1] + 0.5, base_y, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2)
        pct_tag = mono("likelihood", 13, INK_GHOST)
        pct_tag.next_to(baseline, DOWN, buff=0.06).align_to(baseline, LEFT)

        # pre-shrink bars so they grow from the baseline.
        targets_h = [b.height for b in bars]
        for i, b in enumerate(bars):
            b.stretch_to_fit_height(0.001)
            b.move_to([xs[i], base_y, 0])

        # connector lines fan from the slot down to each bar top — the model
        # "reaching" for each continuation.
        fans = VGroup(*[
            Line(slot_line.get_center() + DOWN * 0.05,
                 [xs[i], base_y + targets_h[i] + 0.02, 0],
                 stroke_color=INK_GHOST, stroke_width=0.9)
            for i in range(n)
        ])

        self.play(Create(baseline), FadeIn(pct_tag), run_time=0.3)
        self.play(LaggedStartMap(Create, fans, lag_ratio=0.08, run_time=0.5))

        grow = []
        for i, b in enumerate(bars):
            b.target = b.copy()
            b.target.stretch_to_fit_height(targets_h[i])
            b.target.move_to([xs[i], base_y + targets_h[i] / 2, 0])
            grow.append(MoveToTarget(b))
        self.play(LaggedStart(*grow, lag_ratio=0.10),
                  LaggedStart(*[FadeIn(w, shift=UP * 0.06) for w in word_lbls],
                              lag_ratio=0.10),
                  LaggedStart(*[FadeIn(p) for p in pct_lbls], lag_ratio=0.10),
                  run_time=0.85)

        # 'butter' lights up — the single bright candidate (the one #fff peak).
        butter_grp = VGroup(bars[0], word_lbls[0], pct_lbls[0])
        self.play(Indicate(butter_grp, scale_factor=1.08, color=WHITE),
                  bars[0].animate.set_fill(WHITE, 0.95),
                  word_lbls[0].animate.set_color(WHITE),
                  run_time=0.5)
        # cool it back to INK so #fff stays reserved for the final name.
        self.play(bars[0].animate.set_fill(INK, 0.95),
                  word_lbls[0].animate.set_color(INK), run_time=0.25)

        # =================================================================
        # B2 — TRANSFORM: each candidate becomes a toll-road EDGE. Tall bar
        #      -> thin cheap edge; short bar -> thick expensive edge. A route
        #      bends toward the likely word.
        # =================================================================
        self.next_section("toll")

        bridge = mono("the search pays a toll per edge  ·  likely = cheap", 16,
                      INK_FAINT)
        bridge.next_to(stub, DOWN, buff=0.26)
        self.play(ReplacementTransform(ask, bridge), run_time=0.4)

        # a shared start node on the left; each candidate is an edge to a node
        # on the right, stacked top (likely) to bottom (unlikely). The fan sits
        # in a band BELOW the bridge caption so nothing collides.
        graph_y = -0.35
        start_node = Dot([-4.7, graph_y, 0], radius=0.10, color=INK)
        start_lbl = mono("…peanut", 15, INK_DIM).next_to(start_node, LEFT, buff=0.18)
        if start_lbl.get_left()[0] < -6.9:
            start_lbl.next_to(start_node, UP, buff=0.12)

        node_x = 3.4
        ys = np.linspace(graph_y + 1.15, graph_y - 1.15, n)
        edges = VGroup()
        end_nodes = VGroup()
        edge_words = VGroup()
        toll_lbls = VGroup()
        for i, (w, p) in enumerate(cands):
            # cost is INVERSE to likelihood: likely -> cheap (thin), unlikely ->
            # expensive (thick). Edge thickness encodes the toll.
            cost = round(1.0 + (1.0 - p) * 8.0, 1)
            sw = 1.3 + (1.0 - p) * 5.5
            op = 0.85 if p > 0.6 else 0.40
            e = Line(start_node.get_center(), [node_x, ys[i], 0],
                     stroke_color=INK, stroke_width=sw, stroke_opacity=op)
            edges.add(e)
            nd = Dot([node_x, ys[i], 0], radius=0.06,
                     color=INK if p > 0.6 else INK_FAINT)
            end_nodes.add(nd)
            ew = mono(w, 17, INK if p > 0.6 else INK_FAINT)
            ew.next_to(nd, RIGHT, buff=0.18)
            edge_words.add(ew)
            # toll readout docks just LEFT of each node, off the edge body.
            tl = mono(f"toll {cost}", 12, INK_DIM if p > 0.6 else INK_GHOST)
            tl.next_to(nd, UP, buff=0.10).shift(LEFT * 0.05)
            toll_lbls.add(tl)

        # morph: bars + words slide/restyle into the edge graph.
        self.play(
            FadeOut(fans), FadeOut(baseline), FadeOut(pct_tag),
            FadeOut(pct_lbls),
            FadeIn(start_node, scale=0.6), FadeIn(start_lbl),
            run_time=0.45,
        )
        anims = []
        for i in range(n):
            anims.append(ReplacementTransform(bars[i], edges[i]))
            anims.append(ReplacementTransform(word_lbls[i], edge_words[i]))
            anims.append(FadeIn(end_nodes[i], scale=0.6))
        self.play(LaggedStart(*anims, lag_ratio=0.06), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(t) for t in toll_lbls], lag_ratio=0.08),
                  run_time=0.5)

        # the cheapest route — a bright pulse travels the thin 'butter' edge,
        # the road bending toward the likely word.
        route = edges[0].copy().set_stroke(WHITE, width=3.0, opacity=1.0)
        pulse = Dot(start_node.get_center(), radius=0.07, color=WHITE)
        self.add(route.set_stroke(opacity=0.0), pulse)
        self.play(Create(route.set_stroke(opacity=0.95)),
                  pulse.animate.move_to(end_nodes[0].get_center()),
                  run_time=0.6, rate_func=linear)
        self.play(FadeOut(pulse, scale=0.5),
                  Indicate(edge_words[0], scale_factor=1.10, color=WHITE),
                  run_time=0.4)
        cheap_tag = mono("cheapest road  →  butter", 16, INK_DIM)
        cheap_tag.move_to([-2.4, graph_y - 1.75, 0])
        self.play(FadeIn(cheap_tag, shift=UP * 0.06), run_time=0.32)

        # =================================================================
        # B3 — NOTE: it can't hear — only reads.
        # =================================================================
        self.next_section("note")

        note = mono("it can't hear — it only reads", 18, INK_DIM)
        note.move_to([0, BOT_Y + 0.18, 0])
        self.play(FadeIn(note, shift=UP * 0.1), run_time=0.4)
        self.wait(0.15)

        # =================================================================
        # B4 — NAME IT + the 4-gram / 7B clarifier + poster hold.
        # =================================================================
        self.next_section("name")

        # clear the centre mechanism so the name owns the frame; keep top cap.
        mech = VGroup(stub, bridge, edges, end_nodes, edge_words, toll_lbls,
                      start_node, start_lbl, route, cheap_tag)
        self.play(FadeOut(mech, shift=DOWN * 0.12),
                  note.animate.move_to([0, BOT_Y - 0.55, 0]).set_opacity(0.7),
                  run_time=0.5)

        name = serif("a next-word guesser", 50, WHITE).move_to([0, 0.95, 0])
        name_g = glow(name)
        sub = mono("learned only from reading mountains of text", 17, INK_DIM)
        sub.next_to(name, DOWN, buff=0.30)
        self.add(name_g)
        self.play(GrowFromCenter(name), FadeIn(sub),
                  Flash([0, 0.95, 0], color=WHITE, line_length=0.2, num_lines=14,
                        flash_radius=1.6, time_width=0.4), run_time=0.6)

        # the clarifier: small 4-gram scores the map here; a much bigger 7B
        # chooses later. Two quiet chips, no contradiction.
        chip_small = VGroup(
            mono("small one  ·  scores the map here", 15, INK_DIM),
        )
        chip_big = VGroup(
            mono("a much bigger one  ·  chooses later", 15, INK_FAINT),
        )
        chips = VGroup(chip_small, chip_big).arrange(DOWN, buff=0.18)
        chips.move_to([0, -0.95, 0])
        div = Line(chips.get_left() + LEFT * 0.1, chips.get_right() + RIGHT * 0.1,
                   stroke_color=LINE, stroke_width=1.0)
        div.move_to([0, -0.95, 0])
        self.play(FadeIn(chip_small, shift=UP * 0.06), run_time=0.3)
        self.play(Create(div), run_time=0.2)
        self.play(FadeIn(chip_big, shift=UP * 0.06), run_time=0.3)

        self.wait(0.6)
