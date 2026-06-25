# website/anim/s19_wfst.py  —  S19 "The map of words" (WFST / HLG)
#
# Sounds aren't words yet. They become words by walking the single cheapest
# road through a vast map of how English is spelled and spoken. The aha: that
# one giant map is secretly THREE smaller maps — H (collapse the raw sounds)
# composed with L (a 34,546-word pronunciation dictionary) composed with G
# (how English words follow each other) — one object you can walk in one pass.
#
# Locked 6-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 sounds-in    the CTC phone ribbon flows into the map's mouth-node
#   2 lay the map  the wide 7-node toll lattice grows edge to edge + legend
#   3 cheapest     a pulse walks the cheapest route to white; rival -> ghost;
#                  meter ticks 0->8 (rival 11); "the quiet morning" writes out
#   4 one is three lattice contracts to one HLG ring, bursts into 3 lobes H/L/G
#   5 dictionary   spotlight ONLY the L-lobe; scoreboard 34,546 words / ~5x
#   6 unseen words 3 lobes re-compose into one HLG map; floor line settles
from manim import *
from emg_style import *


def node(r=0.16, fill=0.0, stroke=INK, sw=2.0):
    return Circle(radius=r, stroke_color=stroke, stroke_width=sw,
                  fill_color=BG, fill_opacity=1.0 if fill == 0 else fill)


def pulse(point, r=0.20):
    """A small travelling marker — bright dot with a soft halo."""
    halo = Circle(radius=r * 1.9, stroke_width=0, fill_color=INK, fill_opacity=0.12)
    core = Dot(point, radius=r * 0.5, color="#ffffff")
    return VGroup(halo, core).move_to(point)


def corner_ticks():
    """Faint registration marks in the four corners — frames the full canvas."""
    g = VGroup()
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = np.array([sx * 6.78, sy * 3.78, 0.0])
            g.add(Line(c, c - np.array([sx * 0.34, 0, 0]),
                       stroke_color=INK_GHOST, stroke_width=1.2))
            g.add(Line(c, c - np.array([0, sy * 0.34, 0]),
                       stroke_color=INK_GHOST, stroke_width=1.2))
    return g


class WordMap(Scene):
    def construct(self):
        seed()

        ticks = corner_ticks()
        self.add(ticks)

        # ============================================================
        # BEAT 1 — SOUNDS IN (1.33s): the CTC phone ribbon flows into
        #          the map's mouth-node. Quiet "sounds from the reader".
        # ============================================================
        self.next_section("sounds_in")

        rail_y = 3.05
        phones = ["∅", "DH", "AH", "∅", "K", "W", "AY", "AH", "T", "∅"]
        ribbon = VGroup()
        for p in phones:
            c = INK_GHOST if p == "∅" else INK_FAINT
            ribbon.add(mono(p, 16, c))
        ribbon.arrange(RIGHT, buff=0.20).move_to(LEFT * 3.4 + UP * rail_y)
        ribbon_under = Line(
            ribbon.get_left() + DOWN * 0.22, ribbon.get_right() + DOWN * 0.22,
            stroke_color=INK_GHOST, stroke_width=1.0)
        ribbon_lab = mono("sounds from the reader", 13, INK_GHOST)
        ribbon_lab.next_to(ribbon_under, DOWN, buff=0.08).align_to(ribbon, LEFT)

        mouth = node(0.13, stroke=INK_FAINT, sw=1.8).move_to(RIGHT * 0.05 + UP * rail_y)
        feed = Arrow(ribbon.get_right() + RIGHT * 0.12, mouth.get_left() + LEFT * 0.04,
                     buff=0.06, stroke_width=2.0, color=INK_FAINT,
                     max_tip_length_to_length_ratio=0.22)
        map_lab = mono("the map of words", 19, INK_DIM)
        map_lab.move_to(UP * (rail_y + 0.02)).align_to(mouth, LEFT).shift(RIGHT * 0.55)

        # a faint travelling marker carrying the sounds rightward into the mouth
        carry = pulse(ribbon.get_left() + LEFT * 0.1, r=0.10)

        self.play(
            LaggedStart(*[FadeIn(m, shift=RIGHT * 0.18) for m in ribbon],
                        lag_ratio=0.05, run_time=0.55),
            Create(ribbon_under, run_time=0.55),
        )
        self.play(
            FadeIn(ribbon_lab),
            GrowFromCenter(mouth), GrowArrow(feed),
            FadeIn(map_lab, shift=RIGHT * 0.1),
            run_time=0.4,
        )
        self.add(carry)
        self.play(MoveAlongPath(
            carry, Line(ribbon.get_left() + LEFT * 0.1, mouth.get_center())),
            run_time=0.25, rate_func=linear)
        self.play(FadeOut(carry, scale=0.4), run_time=0.1)
        self.wait(0.03)

        # ============================================================
        # BEAT 2 — LAY THE MAP (2.45s): the wide 7-node toll lattice
        #          grows edge to edge; legend "road = a word · toll = cost".
        # ============================================================
        self.next_section("lay_the_map")

        pos = [
            LEFT * 6.1 + UP * 0.5,
            LEFT * 3.2 + UP * 1.7,
            LEFT * 3.2 + DOWN * 0.9,
            RIGHT * 0.05 + UP * 0.55,
            RIGHT * 3.3 + UP * 1.7,
            RIGHT * 3.3 + DOWN * 0.9,
            RIGHT * 6.1 + UP * 0.5,
        ]
        pos = [p + DOWN * 0.05 for p in pos]
        nodes = VGroup(*[node().move_to(p) for p in pos])

        edges_def = [
            (0, 1, "2"), (0, 2, "5"),
            (1, 3, "1"), (2, 3, "4"),
            (3, 4, "3"), (3, 5, "2"),
            (4, 6, "2"), (5, 6, "6"),
        ]
        edges = {}
        tolls = VGroup()
        toll_by_edge = {}
        for a, b, cost in edges_def:
            ln = Line(pos[a], pos[b], stroke_color=INK_GHOST, stroke_width=2.2,
                      buff=0.18)
            edges[(a, b)] = ln
            mid = ln.point_from_proportion(0.5)
            off = UP * 0.26 if pos[b][1] >= pos[a][1] else DOWN * 0.26
            t = mono(cost, 17, INK_FAINT).move_to(mid + off + RIGHT * 0.05)
            tolls.add(t)
            toll_by_edge[(a, b)] = t
        edge_group = VGroup(*edges.values())

        start_lab = mono("start", 14, INK_FAINT).next_to(nodes[0], UP, buff=0.14)
        end_lab = mono("end", 14, INK_FAINT).next_to(nodes[6], UP, buff=0.14)

        mouth_feed = DashedLine(mouth.get_bottom() + DOWN * 0.04,
                                nodes[0].get_top() + UP * 0.04,
                                stroke_color=INK_GHOST, stroke_width=1.4,
                                dash_length=0.10)

        self.play(
            LaggedStart(*[Create(e) for e in edge_group], lag_ratio=0.08,
                        run_time=1.05),
            LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.05,
                        run_time=1.05),
            FadeIn(start_lab), FadeIn(end_lab),
            Create(mouth_feed),
        )
        self.play(FadeIn(tolls, run_time=0.55))

        legend = VGroup(
            mono("road = a word", 13, INK_FAINT),
            mono("toll = cost", 13, INK_FAINT),
        ).arrange(DOWN, buff=0.10, aligned_edge=RIGHT)
        legend.to_corner(UR, buff=0.42).shift(DOWN * 0.05)
        self.play(FadeIn(legend, shift=LEFT * 0.12), run_time=0.4)
        self.wait(0.35)

        # ============================================================
        # BEAT 3 — CHEAPEST PATH (2.01s): pulse walks the cheapest route
        #          to white; rival -> ghost; meter 0->8 (rival 11);
        #          "the quiet morning" writes out below.
        # ============================================================
        self.next_section("cheapest")

        path_nodes = [0, 1, 3, 4, 6]
        path_edges = [(0, 1), (1, 3), (3, 4), (4, 6)]
        path_costs = [2, 1, 3, 2]                       # total 8
        rival_edges = [(0, 2), (2, 3), (3, 5), (5, 6)]

        glow_edges = VGroup()
        for (a, b) in path_edges:
            base = Line(pos[a], pos[b], stroke_color="#ffffff", stroke_width=4.5, buff=0.18)
            glow_edges.add(glow(base))
        lit_nodes = VGroup(*[nodes[i].copy().set_stroke("#ffffff", 3.2) for i in path_nodes])

        meter_y = -3.0
        cost_tr = ValueTracker(0)
        cost_lab = mono("running cost", 15, INK_FAINT).move_to(LEFT * 5.1 + UP * (meter_y + 0.42))
        cost_lab.align_to(LEFT * 5.6, LEFT)
        cost_anchor = LEFT * 4.55 + UP * (meter_y - 0.12)
        cost_val = counter(cost_tr, fmt=lambda v: str(round(v)), s=52, c=INK,
                           at=cost_anchor)

        bar_x0, bar_x1 = -3.1, 4.6

        def cost_to_x(c):
            return bar_x0 + (bar_x1 - bar_x0) * (c / 11.0)

        bar_track = Line(RIGHT * bar_x0 + UP * meter_y, RIGHT * bar_x1 + UP * meter_y,
                         stroke_color=INK_GHOST, stroke_width=3.0)
        bar_fill = Line(bar_track.get_start(), bar_track.get_start(),
                        stroke_color=INK, stroke_width=5.0)
        bar_fill.add_updater(lambda m: m.put_start_and_end_on(
            RIGHT * bar_x0 + UP * meter_y,
            RIGHT * cost_to_x(max(0.06, min(8.0, cost_tr.get_value()))) + UP * meter_y))
        rival_tick = Line(RIGHT * cost_to_x(11) + UP * (meter_y + 0.16),
                          RIGHT * cost_to_x(11) + UP * (meter_y - 0.16),
                          stroke_color=INK_FAINT, stroke_width=2.0)
        rival_lab = mono("rival  11", 13, INK_GHOST).next_to(rival_tick, UP, buff=0.08)
        cheap_lab = mono("cheapest  8", 13, INK_FAINT)
        cheap_lab.move_to(RIGHT * cost_to_x(8) + UP * (meter_y + 0.40))

        self.add(cost_lab, cost_val)
        self.play(
            Create(bar_track), FadeIn(cost_lab),
            Create(rival_tick), FadeIn(rival_lab),
            run_time=0.3,
        )
        self.add(bar_fill)

        mouth_feed_path = Line(mouth.get_bottom() + DOWN * 0.04,
                               nodes[0].get_top() + UP * 0.04)
        trav = pulse(mouth.get_center(), r=0.13)
        self.add(trav)
        self.play(MoveAlongPath(trav, mouth_feed_path), run_time=0.22, rate_func=linear)
        self.play(FadeIn(lit_nodes[0], scale=0.6), run_time=0.12)

        for i, ((a, b), seg, lit_to) in enumerate(
                zip(path_edges, glow_edges, lit_nodes[1:])):
            self.play(
                MoveAlongPath(trav, Line(pos[a], pos[b], buff=0.18)),
                Create(seg),
                cost_tr.animate.set_value(sum(path_costs[:i + 1])),
                toll_by_edge[(a, b)].animate.set_color(INK),
                FadeIn(lit_to, scale=0.6),
                run_time=0.19, rate_func=linear,
            )
        self.play(FadeOut(trav, scale=0.4), run_time=0.1)

        rival_dim = VGroup(*[edges[e] for e in rival_edges])
        words = serif("the  quiet  morning", 30, INK).move_to(DOWN * 2.05)
        warrow = mono("->", 20, INK_FAINT).next_to(words, LEFT, buff=0.26)
        self.play(
            rival_dim.animate.set_stroke(opacity=0.16),
            FadeIn(cheap_lab, shift=UP * 0.1),
            Flash(cost_val, color=INK, line_length=0.12, num_lines=10,
                  flash_radius=0.5),
            FadeIn(warrow), Write(words),
            run_time=0.5,
        )
        self.wait(0.12)

        # ============================================================
        # BEAT 4 — ONE MAP IS THREE (3.5s): the lattice contracts to one
        #          HLG ring, a white burst splits it into H / L / G with
        #          plain captions.
        # ============================================================
        self.next_section("one_is_three")

        cost_val.clear_updaters()
        bar_fill.clear_updaters()
        lattice = VGroup(nodes, edge_group, tolls, glow_edges, lit_nodes,
                         start_lab, end_lab, mouth_feed)
        bottom_meter = VGroup(cost_lab, cost_val, bar_track, bar_fill, rival_tick,
                              rival_lab, cheap_lab)

        hlg_ring = Circle(radius=0.95, stroke_color="#ffffff", stroke_width=2.6)
        hlg_ring.move_to(UP * 0.3)
        hlg_inner = VGroup(*[
            node(0.07, stroke=INK, sw=1.6).move_to(
                UP * 0.3 + 0.45 * np.array([np.cos(a), np.sin(a), 0]))
            for a in np.linspace(0, TAU, 5, endpoint=False)
        ])
        hlg_label = serif("HLG", 34, "#ffffff").next_to(hlg_ring, UP, buff=0.16)

        # the lattice + emitted words all collapse to ONE ring; the meter fully
        # fades here so the bottom strip is empty before the scoreboard arrives.
        self.play(
            ReplacementTransform(lattice, VGroup(hlg_ring, hlg_inner)),
            FadeIn(hlg_label, scale=0.7),
            FadeOut(VGroup(words, warrow), shift=DOWN * 0.2),
            FadeOut(bottom_meter, shift=DOWN * 0.25),
            FadeOut(legend, shift=RIGHT * 0.2),
            run_time=0.95,
        )
        self.play(Indicate(hlg_label, color="#ffffff", scale_factor=1.12), run_time=0.4)

        def minigraph(label, sub, where, accent=INK):
            p = [LEFT * 0.5 + DOWN * 0.32, RIGHT * 0.52 + UP * 0.36,
                 RIGHT * 0.55 + DOWN * 0.42]
            nd = VGroup(*[node(0.10, stroke=INK_DIM, sw=1.6).move_to(q) for q in p])
            arcs = VGroup(
                Line(p[0], p[1], stroke_color=INK_FAINT, stroke_width=1.6, buff=0.11),
                Line(p[1], p[2], stroke_color=INK_FAINT, stroke_width=1.6, buff=0.11),
                Line(p[0], p[2], stroke_color=INK_FAINT, stroke_width=1.6, buff=0.11),
            )
            big = serif(label, 58, accent).move_to(nd.get_center())
            ring = Circle(radius=0.92, stroke_color=LINE, stroke_width=1.6)
            g = VGroup(ring, arcs, nd, big).move_to(where)
            cap = mono(sub, 14, INK_FAINT).next_to(g, DOWN, buff=0.22)
            return VGroup(g, cap), big, ring

        gH, H_letter, ringH = minigraph("H", "collapse sounds",
                                        LEFT * 4.5 + UP * 0.55)
        gL, L_letter, ringL = minigraph("L", "pronunciation dictionary",
                                        ORIGIN + UP * 0.55)
        gG, G_letter, ringG = minigraph("G", "how words follow words",
                                        RIGHT * 4.5 + UP * 0.55)

        comp1 = serif("∘", 48, INK_DIM).move_to((gH[0].get_center() + gL[0].get_center()) / 2)
        comp2 = serif("∘", 48, INK_DIM).move_to((gL[0].get_center() + gG[0].get_center()) / 2)

        reveal_cap = mono("one map is three smaller maps, composed", 17, INK_DIM)
        reveal_cap.move_to(UP * 2.45)

        burst = Circle(radius=0.95, stroke_color="#ffffff", stroke_width=3.0)
        burst.move_to(hlg_ring.get_center())
        self.add(burst)

        self.play(
            FadeIn(reveal_cap, shift=DOWN * 0.1),
            ReplacementTransform(VGroup(hlg_ring, hlg_inner, hlg_label),
                                 VGroup(gH[0], gL[0], gG[0])),
            burst.animate(rate_func=rush_from).scale(6.6).set_stroke(opacity=0.0),
            run_time=0.85,
        )
        self.remove(burst)
        self.play(
            FadeIn(gH[1]), FadeIn(gL[1]), FadeIn(gG[1]),
            Write(comp1), Write(comp2),
            run_time=0.5,
        )
        # name the lobes — equal weight, no single spotlight yet
        self.play(
            LaggedStart(
                Indicate(ringH, color=INK, scale_factor=1.10),
                Indicate(ringL, color=INK, scale_factor=1.10),
                Indicate(ringG, color=INK, scale_factor=1.10),
                lag_ratio=0.4, run_time=0.7),
        )
        self.wait(0.25)

        # ============================================================
        # BEAT 5 — THE DICTIONARY (1.75s): spotlight ONLY the L-lobe
        #          (dim H and G); scoreboard 34,546 words / ~5x.
        # ============================================================
        self.next_section("dictionary")

        score_num = mono("34,546", 40, "#ffffff")
        score_word = mono("words", 22, INK_DIM)
        score = VGroup(score_num, score_word).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
        score.move_to(DOWN * 2.7)
        score_sub = mono("open-vocabulary  ·  ~5× the words we trained on", 16, INK_FAINT)
        score_sub.next_to(score, DOWN, buff=0.22)

        # the 34,546 visibly comes FROM the dictionary lobe: dim H and G (stroke
        # only — set_opacity would expose a default fill and break monochrome),
        # glow L.
        self.play(
            gH.animate.set_color(INK_GHOST),
            gG.animate.set_color(INK_GHOST),
            comp1.animate.set_color(INK_GHOST),
            comp2.animate.set_color(INK_GHOST),
            ringL.animate.set_stroke(color="#ffffff", width=2.6),
            L_letter.animate.set_color("#ffffff"),
            run_time=0.5,
        )
        self.play(
            FadeIn(score, shift=UP * 0.12),
            Flash(score_num, color="#ffffff", line_length=0.14, num_lines=12,
                  flash_radius=0.9),
            run_time=0.55,
        )
        self.play(FadeIn(score_sub, shift=UP * 0.1), run_time=0.4)
        self.wait(0.25)

        # ============================================================
        # BEAT 6 — UNSEEN WORDS (0.94s): three lobes re-compose into one
        #          HLG map; floor line settles. Poster hold.
        # ============================================================
        self.next_section("unseen_words")

        merged_ring = Circle(radius=1.15, stroke_color=INK, stroke_width=2.2)
        merged_ring.move_to(UP * 0.45)
        mp = [LEFT * 0.65, LEFT * 0.08 + UP * 0.45, LEFT * 0.08 + DOWN * 0.45,
              RIGHT * 0.5 + UP * 0.18, RIGHT * 0.78 + DOWN * 0.42]
        mp = [q + UP * 0.45 for q in mp]
        mnodes = VGroup(*[node(0.09, stroke=INK, sw=1.6).move_to(q) for q in mp])
        marcs = VGroup(
            Line(mp[0], mp[1], stroke_color=INK_DIM, stroke_width=1.6, buff=0.10),
            Line(mp[0], mp[2], stroke_color=INK_DIM, stroke_width=1.6, buff=0.10),
            Line(mp[1], mp[3], stroke_color=INK_DIM, stroke_width=1.6, buff=0.10),
            Line(mp[2], mp[3], stroke_color=INK_DIM, stroke_width=1.6, buff=0.10),
            Line(mp[3], mp[4], stroke_color=INK_DIM, stroke_width=1.6, buff=0.10),
        )
        hlg_top = serif("HLG", 36, INK).next_to(merged_ring, UP, buff=0.16)
        merged_core = VGroup(merged_ring, marcs, mnodes)

        three = VGroup(gH, gL, gG, comp1, comp2)
        out_words = serif("words", 24, "#ffffff").next_to(merged_ring, RIGHT, buff=0.6)
        out_arrow = mono("->", 18, INK_FAINT).next_to(merged_ring, RIGHT, buff=0.14)
        floor = mono("open-vocabulary  ·  only 0.49% of test words out-of-lexicon  (12 / 2,429)",
                     15, INK_FAINT)
        floor.move_to(DOWN * 3.35)

        self.play(
            ReplacementTransform(three, merged_core),
            ReplacementTransform(
                VGroup(H_letter.copy(), L_letter.copy(), G_letter.copy()), hlg_top),
            FadeOut(reveal_cap, shift=UP * 0.15),
            FadeOut(VGroup(score, score_sub), shift=DOWN * 0.12),
            FadeIn(floor, shift=UP * 0.1),
            run_time=0.55,
        )
        self.play(
            FadeIn(out_arrow), FadeIn(out_words, shift=RIGHT * 0.1),
            run_time=0.22,
        )
        self.wait(0.25)
