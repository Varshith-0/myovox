# website/anim/b18_what_is_lm.py  —  B18 "What is a language model"
#
# The "aha": a language model has read mountains of text and learned ONE thing —
# given the words so far, which word likely comes NEXT. You do it too: "the
# peanut ___" leans toward "butter", not "bicycle". The map's toll borrows this:
# likely continuations are cheap edges, wild ones expensive, so the cheapest road
# bends toward sensible English. It can't hear; it only reads.
#
# Locked 7-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 pose      open cold on "the peanut ___" — slot gives one soft pulse
#   2 predict   faint bright ghost where butter lands, dim ghost for bicycle
#   3 rank      ranked likelihood fan grows: butter tall+bright, bicycle short+dim
#   4 toll      bars morph into toll edges (thin/cheap butter, thick/dear bicycle);
#               bright pulse traces the cheapest road to butter
#   5 deaf      dim the whole edge graph; "it can't hear — it only reads" alone
#   6 name      clear mechanism; serif #fff "a next-word guesser" + sub
#   7 chips     two clarifier chips: small scores here / bigger chooses later
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

STUB_Y = 1.95
FAN_Y = 0.05
BOT_Y = -3.05


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
        n = len(cands)
        col_w = 2.30
        bar_w = 0.46
        max_h = 1.55
        base_y = FAN_Y - 0.55
        xs = [(i - (n - 1) / 2) * col_w for i in range(n)]

        # =================================================================
        # BEAT 1 — POSE (~0.79s): open cold on "the peanut ___", slot pulses.
        # =================================================================
        self.next_section("pose")

        the_w = mono("the", 34, INK_DIM)
        peanut_w = mono("peanut", 34, INK)
        slot_line = Line(LEFT * 0.55, RIGHT * 0.55, stroke_color=INK_FAINT,
                         stroke_width=2.2)
        stub = VGroup(the_w, peanut_w, slot_line).arrange(RIGHT, buff=0.34)
        stub.move_to([0, STUB_Y, 0])

        self.play(FadeIn(the_w, shift=RIGHT * 0.1),
                  FadeIn(peanut_w, shift=RIGHT * 0.1),
                  Create(slot_line), run_time=0.4)
        self.play(slot_line.animate.set_stroke(INK, width=2.8), run_time=0.18)
        self.play(slot_line.animate.set_stroke(INK_FAINT, width=2.2), run_time=0.18)

        # =================================================================
        # BEAT 2 — PREDICT (~1.48s): the viewer's own guess, pre-bars. A faint
        #          bright ghost where 'butter' will land; a dim ghost for 'bicycle'.
        # =================================================================
        self.next_section("predict")

        butter_ghost = mono("butter", 22, INK).set_opacity(0.55)
        butter_ghost.move_to([xs[0], base_y + 0.55, 0])
        bicycle_ghost = mono("bicycle", 18, INK_GHOST)
        bicycle_ghost.move_to([xs[-1], base_y + 0.30, 0])

        lead = Line(slot_line.get_center() + DOWN * 0.08,
                    butter_ghost.get_top() + UP * 0.06,
                    stroke_color=INK_GHOST, stroke_width=1.0)

        self.play(Create(lead), run_time=0.3)
        self.play(FadeIn(butter_ghost, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(bicycle_ghost, shift=UP * 0.05), run_time=0.45)
        self.wait(0.2)

        # =================================================================
        # BEAT 3 — RANK (~2.65s): the full ranked likelihood fan grows from the
        #          baseline; butter tall+bright, bicycle short+dim; butter pulse.
        # =================================================================
        self.next_section("rank")

        bars = VGroup()
        word_lbls = VGroup()
        targets_h = []
        for i, (w, p) in enumerate(cands):
            h = 0.14 + max_h * p
            targets_h.append(h)
            op = 0.30 + 0.65 * p
            r = Rectangle(width=bar_w, height=h, stroke_width=0,
                          fill_color=INK, fill_opacity=op)
            r.move_to([xs[i], base_y, 0])
            r.stretch_to_fit_height(0.001)
            bars.add(r)
            wl = mono(w, 18, INK if p > 0.6 else INK_DIM)
            wl.move_to([xs[i], base_y + h + 0.20, 0])
            word_lbls.add(wl)

        baseline = Line([xs[0] - 0.5, base_y, 0], [xs[-1] + 0.5, base_y, 0],
                        stroke_color=INK_GHOST, stroke_width=1.2)
        rank_tag = mono("which word likely comes next?", 16, INK_FAINT)
        rank_tag.next_to(stub, DOWN, buff=0.30)

        # the two ghosts resolve into the real butter/bicycle word labels.
        self.play(
            FadeIn(rank_tag, shift=UP * 0.06),
            Create(baseline),
            FadeOut(lead),
            ReplacementTransform(butter_ghost, word_lbls[0]),
            ReplacementTransform(bicycle_ghost, word_lbls[-1]),
            run_time=0.6,
        )

        grow = []
        for i, b in enumerate(bars):
            b.target = b.copy()
            b.target.stretch_to_fit_height(targets_h[i])
            b.target.move_to([xs[i], base_y + targets_h[i] / 2, 0])
            grow.append(MoveToTarget(b))
        mid_words = VGroup(*[word_lbls[i] for i in range(1, n - 1)])
        self.play(
            LaggedStart(*grow, lag_ratio=0.10),
            LaggedStart(*[FadeIn(w, shift=UP * 0.06) for w in mid_words],
                        lag_ratio=0.10),
            run_time=1.1,
        )

        # 'butter' highlight pulse — the single bright candidate.
        butter_grp = VGroup(bars[0], word_lbls[0])
        self.play(Indicate(butter_grp, scale_factor=1.10, color=WHITE),
                  bars[0].animate.set_fill(WHITE, 0.95),
                  word_lbls[0].animate.set_color(WHITE),
                  run_time=0.5)
        self.play(bars[0].animate.set_fill(INK, 0.95),
                  word_lbls[0].animate.set_color(INK), run_time=0.25)
        self.wait(0.15)

        # =================================================================
        # BEAT 4 — TOLL (~2.99s): bars morph into toll-road EDGES (thin/cheap
        #          butter, thick/expensive bicycle); pulse traces cheapest road.
        # =================================================================
        self.next_section("toll")

        bridge = mono("likely = cheap road   ·   wild = expensive", 16, INK_FAINT)
        bridge.next_to(stub, DOWN, buff=0.26)
        self.play(ReplacementTransform(rank_tag, bridge), run_time=0.4)

        graph_y = -0.35
        start_node = Dot([-4.7, graph_y, 0], radius=0.10, color=INK)
        start_lbl = mono("…peanut", 15, INK_DIM).next_to(start_node, UP, buff=0.14)

        node_x = 3.3
        ys = np.linspace(graph_y + 1.10, graph_y - 1.10, n)
        edges = VGroup()
        end_nodes = VGroup()
        edge_words = VGroup()
        for i, (w, p) in enumerate(cands):
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

        self.play(
            FadeOut(baseline),
            FadeIn(start_node, scale=0.6), FadeIn(start_lbl),
            run_time=0.4,
        )
        anims = []
        for i in range(n):
            anims.append(ReplacementTransform(bars[i], edges[i]))
            anims.append(ReplacementTransform(word_lbls[i], edge_words[i]))
            anims.append(FadeIn(end_nodes[i], scale=0.6))
        self.play(LaggedStart(*anims, lag_ratio=0.06), run_time=0.95)

        # the cheapest route — a bright pulse travels the thin 'butter' edge.
        route = edges[0].copy().set_stroke(WHITE, width=3.0, opacity=0.0)
        pulse = Dot(start_node.get_center(), radius=0.07, color=WHITE)
        self.add(route, pulse)
        self.play(route.animate.set_stroke(opacity=0.95),
                  pulse.animate.move_to(end_nodes[0].get_center()),
                  run_time=0.7, rate_func=linear)
        self.play(FadeOut(pulse, scale=0.5),
                  Indicate(edge_words[0], scale_factor=1.10, color=WHITE),
                  run_time=0.4)
        cheap_tag = mono("cheapest road  →  butter", 16, INK_DIM)
        cheap_tag.move_to([-1.9, graph_y - 1.65, 0])
        self.play(FadeIn(cheap_tag, shift=UP * 0.06), run_time=0.3)

        # =================================================================
        # BEAT 5 — DEAF (~1.20s): dim the whole edge graph; the note owns frame.
        # =================================================================
        self.next_section("deaf")

        graph = VGroup(edges, end_nodes, edge_words, start_node, start_lbl,
                       route, cheap_tag, bridge, stub)
        note = mono("it can't hear — it only reads", 20, INK)
        note.move_to([0, BOT_Y + 0.55, 0])
        self.play(graph.animate.set_opacity(0.14), run_time=0.45)
        self.play(FadeIn(note, shift=UP * 0.12), run_time=0.5)
        self.wait(0.25)

        # =================================================================
        # BEAT 6 — NAME (~1.34s): clear mechanism; serif #fff name + sub.
        # =================================================================
        self.next_section("name")

        self.play(FadeOut(graph), FadeOut(note), run_time=0.4)

        name = serif("a next-word guesser", 50, WHITE).move_to([0, 0.95, 0])
        name_g = glow(name)
        sub = mono("learned only from reading mountains of text", 17, INK_DIM)
        sub.next_to(name, DOWN, buff=0.30)
        self.add(name_g)
        self.play(GrowFromCenter(name), FadeIn(sub),
                  Flash([0, 0.95, 0], color=WHITE, line_length=0.2, num_lines=14,
                        flash_radius=1.6, time_width=0.4), run_time=0.7)
        self.wait(0.2)

        # =================================================================
        # BEAT 7 — CHIPS (~1.54s): two clarifier chips together + poster hold.
        # =================================================================
        self.next_section("chips")

        chip_small = mono("small one  ·  scores the map here", 15, INK_DIM)
        chip_big = mono("a much bigger one  ·  chooses later", 15, INK_DIM)
        chips = VGroup(chip_small, chip_big).arrange(DOWN, buff=0.20)
        chips.move_to([0, -1.05, 0])
        div = Line(chips.get_left() + LEFT * 0.1, chips.get_right() + RIGHT * 0.1,
                   stroke_color=LINE, stroke_width=1.0)
        div.move_to([0, -1.05, 0])
        self.play(FadeIn(chip_small, shift=UP * 0.06),
                  FadeIn(chip_big, shift=UP * 0.06),
                  Create(div), run_time=0.55)
        self.wait(0.85)
