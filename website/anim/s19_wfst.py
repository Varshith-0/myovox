# website/anim/s19_wfst.py  —  S19 "The map of words" (WFST / HLG)
#
# Sounds aren't words yet. They become words by walking the single cheapest
# legal road through a vast map of how English is spelled and spoken. The aha:
# that one giant map is secretly THREE smaller maps — H (collapse + drop blanks)
# composed with L (a 34,546-word pronunciation dictionary) composed with G
# (how words follow words) — one object you can walk in a single pass.
#
# Full-canvas, three-zone composition (3b1b rhythm: pose -> build -> transform
# -> name -> beat):
#   TOP   (y~+2.4..+3.6)  CONTEXT RAIL: the previous stage's CTC phone ribbon
#                  (∅ DH AH ∅ K W AY AH T ∅) flows rightward into the map's
#                  mouth-node — literally the sounds arriving. Center: a quiet
#                  "the map of words" label. Right: a legend that fades in once
#                  tolls matter. The rail persists; in Beat 4 the H/L/G letters
#                  are carried UP into it as labelled lobes.
#   CENTER(-1.6..+2.0)  the MECHANISM: a wide 7-node toll lattice; a bright pulse
#                  enters from the ribbon, walks the cheapest legal path lighting
#                  each edge to #fff, the rival path dims. The lattice then
#                  CONTRACTS into one HLG ring, which SPLITS into three orbiting
#                  transducer-lobes H ∘ L ∘ G, then RE-COMPOSES into one graph.
#   BOTTOM(-3.6..-2.4)  RUNNING TAKEAWAY: a live running-cost counter ticks 0->8
#                  with a meter bar filling in lockstep (ghost rival total 11 so
#                  "cheapest" is quantified); then it morphs into the
#                  open-vocabulary scoreboard — 34,546 words, ~5x the training
#                  words, 0.49% out-of-lexicon (12 / 2,429).
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
    """Faint registration marks in the four corners — frames the full canvas so
    the dead corners read as intentional negative space, not waste."""
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

        # faint full-canvas registration — frames all four corners so the
        # negative space reads as composition, not waste. Persists the whole clip.
        ticks = corner_ticks()
        self.add(ticks)

        # ============================================================
        # BEAT 1 — POSE the map (0–2.4s): top rail carries the heard
        #          sounds in; the toll-lattice sprawls edge to edge.
        # ============================================================

        # ---- TOP CONTEXT RAIL (persists the whole clip) -------------
        rail_y = 3.05
        # previous stage's CTC phone ribbon (the handoff: "sounds arrive here")
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

        # the mouth-of-the-map node the ribbon feeds into
        mouth = node(0.13, stroke=INK_FAINT, sw=1.8).move_to(RIGHT * 0.05 + UP * rail_y)
        feed = Arrow(ribbon.get_right() + RIGHT * 0.12, mouth.get_left() + LEFT * 0.04,
                     buff=0.06, stroke_width=2.0, color=INK_FAINT,
                     max_tip_length_to_length_ratio=0.22)

        # center-top quiet label (NOT a big title)
        map_lab = mono("the map of words", 19, INK_DIM).move_to(UP * (rail_y + 0.02) + RIGHT * 1.55)
        map_lab.align_to(mouth, LEFT).shift(RIGHT * 0.5)

        self.play(
            LaggedStartMap(FadeIn, ribbon, shift=RIGHT * 0.18, lag_ratio=0.06,
                           run_time=0.7),
            Create(ribbon_under, run_time=0.7),
        )
        self.play(
            FadeIn(ribbon_lab, run_time=0.3),
            GrowFromCenter(mouth), GrowArrow(feed),
            FadeIn(map_lab, shift=RIGHT * 0.1),
            run_time=0.45,
        )

        # ---- CENTER: the wide toll-lattice ---------------------------
        # 7 nodes left->right, pushed wide (x ~ -6.1..+6.1), y in ~ -1.6..+2.0
        pos = [
            LEFT * 6.1 + UP * 0.5,           # 0 start
            LEFT * 3.2 + UP * 1.7,           # 1 upper
            LEFT * 3.2 + DOWN * 0.9,         # 2 lower
            RIGHT * 0.05 + UP * 0.55,        # 3 mid
            RIGHT * 3.3 + UP * 1.7,          # 4 upper
            RIGHT * 3.3 + DOWN * 0.9,        # 5 lower
            RIGHT * 6.1 + UP * 0.5,          # 6 end
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

        start_lab = mono("start", 14, INK_FAINT).next_to(nodes[0], LEFT, buff=0.16)
        end_lab = mono("end", 14, INK_FAINT).next_to(nodes[6], RIGHT, buff=0.16)
        # keep within frame
        if start_lab.get_left()[0] < -7.0:
            start_lab.next_to(nodes[0], UP, buff=0.14)
        if end_lab.get_right()[0] > 7.0:
            end_lab.next_to(nodes[6], UP, buff=0.14)

        # a faint line from the mouth-node down into node 0 — the handoff path
        mouth_feed = DashedLine(mouth.get_bottom() + DOWN * 0.04,
                                nodes[0].get_top() + UP * 0.04,
                                stroke_color=INK_GHOST, stroke_width=1.4,
                                dash_length=0.10)

        self.play(
            LaggedStartMap(Create, edge_group, lag_ratio=0.07, run_time=0.9),
            LaggedStartMap(GrowFromCenter, nodes, lag_ratio=0.05, run_time=0.9),
            FadeIn(tolls, run_time=0.9),
            FadeIn(start_lab), FadeIn(end_lab),
            Create(mouth_feed),
        )

        # legend (top-right) fades in once tolls matter
        legend = VGroup(
            mono("road = consume a sound", 13, INK_FAINT),
            mono("toll = cost", 13, INK_FAINT),
        ).arrange(DOWN, buff=0.10, aligned_edge=RIGHT)
        legend.to_corner(UR, buff=0.42).shift(DOWN * 0.05)
        self.play(FadeIn(legend, shift=LEFT * 0.12), run_time=0.4)

        # ============================================================
        # BEAT 2 — WALK the cheapest legal path (2.4–5.0s).
        # ============================================================
        path_nodes = [0, 1, 3, 4, 6]
        path_edges = [(0, 1), (1, 3), (3, 4), (4, 6)]
        path_costs = [2, 1, 3, 2]                       # total 8
        rival_edges = [(0, 2), (2, 3), (3, 5), (5, 6)]  # total 5+4+2+6 = 17 -> show 11 ghost

        glow_edges = VGroup()
        for (a, b) in path_edges:
            base = Line(pos[a], pos[b], stroke_color="#ffffff", stroke_width=4.5, buff=0.18)
            glow_edges.add(glow(base))
        lit_nodes = VGroup(*[nodes[i].copy().set_stroke("#ffffff", 3.2) for i in path_nodes])

        # ---- BOTTOM: running-cost meter ------------------------------
        meter_y = -3.0
        cost_tr = ValueTracker(0)
        cost_lab = mono("running cost", 15, INK_FAINT).move_to(LEFT * 5.1 + UP * (meter_y + 0.42))
        cost_lab.align_to(LEFT * 5.6, LEFT)
        cost_anchor = LEFT * 4.55 + UP * (meter_y - 0.12)
        cost_val = counter(cost_tr, fmt=lambda v: str(round(v)), s=52, c=INK,
                           at=cost_anchor)

        # the cost-meter bar (fills left->right in lockstep, full total = 8)
        bar_x0, bar_x1 = -3.1, 4.6
        TOTAL = 8
        bar_track = Line(RIGHT * bar_x0 + UP * meter_y, RIGHT * bar_x1 + UP * meter_y,
                         stroke_color=INK_GHOST, stroke_width=3.0)
        bar_fill = Line(bar_track.get_start(), bar_track.get_start(),
                        stroke_color=INK, stroke_width=5.0)
        bar_fill.add_updater(lambda m: m.put_start_and_end_on(
            bar_track.get_start(),
            bar_track.point_from_proportion(
                max(1e-3, min(1.0, cost_tr.get_value() / TOTAL)))))
        # ghost rival marker at the higher total (11) — past the end of our bar
        rival_mark_x = bar_x0 + (bar_x1 - bar_x0) * (11 / 11.0)  # full track = rival 11
        # rescale: track end maps to 11, our 8 fills 8/11
        def cost_to_x(c):
            return bar_x0 + (bar_x1 - bar_x0) * (c / 11.0)
        bar_fill.clear_updaters()
        # clamp to a tiny floor so the fill always has nonzero length (a zero-length
        # Line crashes put_start_and_end_on); at cost 0 it reads as a hairline.
        bar_fill.add_updater(lambda m: m.put_start_and_end_on(
            RIGHT * bar_x0 + UP * meter_y,
            RIGHT * cost_to_x(max(0.06, min(8.0, cost_tr.get_value()))) + UP * meter_y))
        rival_tick = Line(RIGHT * cost_to_x(11) + UP * (meter_y + 0.16),
                          RIGHT * cost_to_x(11) + UP * (meter_y - 0.16),
                          stroke_color=INK_FAINT, stroke_width=2.0)
        rival_lab = mono("rival path  11", 13, INK_GHOST).next_to(rival_tick, UP, buff=0.08)
        cheap_lab = mono("cheapest  8", 13, INK_FAINT)
        cheap_lab.move_to(RIGHT * cost_to_x(8) + UP * (meter_y + 0.40))

        self.add(cost_lab, cost_val)
        self.play(
            Create(bar_track),
            FadeIn(cost_lab),
            Create(rival_tick), FadeIn(rival_lab),
            run_time=0.4,
        )
        self.add(bar_fill)

        # ---- launch the pulse from the mouth-node into node 0 --------
        # (MoveAlongPath needs a mobject WITH points — a DashedLine is a VGroup of
        # dash submobjects and has none, so walk a plain Line on the same span.)
        mouth_feed_path = Line(mouth.get_bottom() + DOWN * 0.04,
                               nodes[0].get_top() + UP * 0.04)
        trav = pulse(mouth.get_center(), r=0.13)
        self.add(trav)
        self.play(MoveAlongPath(trav, mouth_feed_path), run_time=0.35, rate_func=linear)
        self.play(FadeIn(lit_nodes[0], scale=0.6), run_time=0.18)

        for i, ((a, b), seg, lit_to) in enumerate(
                zip(path_edges, glow_edges, lit_nodes[1:])):
            self.play(
                MoveAlongPath(trav, Line(pos[a], pos[b], buff=0.18)),
                Create(seg),
                cost_tr.animate.set_value(sum(path_costs[:i + 1])),
                toll_by_edge[(a, b)].animate.set_color(INK),
                FadeIn(lit_to, scale=0.6),
                run_time=0.36, rate_func=linear,
            )
        self.play(FadeOut(trav, scale=0.4), run_time=0.18)

        # dim the losing rival; flash the final cost; reveal the cheapest label
        rival_dim = VGroup(*[edges[e] for e in rival_edges])
        self.play(
            rival_dim.animate.set_stroke(opacity=0.18),
            FadeIn(cheap_lab, shift=UP * 0.1),
            Flash(cost_val, color=INK, line_length=0.12, num_lines=10,
                  flash_radius=0.5),
            run_time=0.45,
        )

        # NAME IT — one quiet caption just under the lit path
        name_cap = mono("cheapest legal path", 18, INK_DIM)
        name_cap.move_to(DOWN * 1.85)
        self.play(FadeIn(name_cap, shift=UP * 0.1), run_time=0.35)

        # ============================================================
        # BEAT 3 — EMIT words + collapse to one map (5.0–6.8s).
        # ============================================================
        words = serif("the  quiet  morning", 30, INK).move_to(DOWN * 2.42)
        warrow = mono("->", 20, INK_FAINT).next_to(words, LEFT, buff=0.26)
        self.play(FadeIn(warrow, run_time=0.3), Write(words, run_time=0.7))
        self.wait(0.18)

        # everything in the lattice + emission collapses into ONE bright ring
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
        hlg_obj = VGroup(hlg_ring, hlg_inner, hlg_label)

        self.play(
            ReplacementTransform(lattice, VGroup(hlg_ring, hlg_inner)),
            FadeIn(hlg_label, scale=0.7),
            FadeOut(VGroup(words, warrow), shift=DOWN * 0.2),
            FadeOut(name_cap, shift=DOWN * 0.2),
            FadeOut(bottom_meter, shift=DOWN * 0.25),
            run_time=1.0,
        )
        self.play(glow(hlg_ring.copy())[0].animate.set_opacity(0), run_time=0.01)
        self.play(Indicate(hlg_label, color="#ffffff", scale_factor=1.12), run_time=0.4)

        # ============================================================
        # BEAT 4 — THE REVEAL: one map is three (6.8–9.4s).
        #          ring SPLITS into H ∘ L ∘ G across the full width,
        #          the bottom morphs into the open-vocab scoreboard.
        # ============================================================
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

        gH, H_letter, ringH = minigraph("H", "collapse + drop blanks",
                                        LEFT * 4.5 + UP * 0.55)
        gL, L_letter, ringL = minigraph("L", "pronunciation dictionary",
                                        ORIGIN + UP * 0.55, accent="#ffffff")
        gG, G_letter, ringG = minigraph("G", "how words follow words",
                                        RIGHT * 4.5 + UP * 0.55)

        comp1 = serif("∘", 48, INK_DIM).move_to((gH[0].get_center() + gL[0].get_center()) / 2)
        comp2 = serif("∘", 48, INK_DIM).move_to((gL[0].get_center() + gG[0].get_center()) / 2)

        reveal_cap = mono("one map is three smaller maps, composed", 17, INK_DIM)
        reveal_cap.move_to(UP * 1.95)

        # the WOW pulse — a bright ring bursts outward from the single map at the
        # instant it splits, so the eye reads "one thing opening into three".
        burst = Circle(radius=0.95, stroke_color="#ffffff", stroke_width=3.0)
        burst.move_to(hlg_ring.get_center())
        self.add(burst)

        # SPLIT: the single ring becomes three lobes
        self.play(
            FadeIn(reveal_cap, shift=DOWN * 0.1),
            ReplacementTransform(VGroup(hlg_ring, hlg_inner, hlg_label),
                                 VGroup(gH[0], gL[0], gG[0])),
            burst.animate(rate_func=rush_from).scale(6.6).set_stroke(opacity=0.0),
            run_time=0.9,
        )
        self.remove(burst)
        self.play(
            FadeIn(gH[1]), FadeIn(gL[1]), FadeIn(gG[1]),
            Write(comp1), Write(comp2),
            run_time=0.5,
        )

        # ---- BOTTOM morphs into the open-vocabulary scoreboard -------
        score_num = mono("34,546", 40, "#ffffff")
        score_word = mono("words", 22, INK_DIM)
        score = VGroup(score_num, score_word).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
        score.move_to(DOWN * 2.7)
        score_sub = mono("open-vocabulary  ·  ~5× the words we trained on", 16, INK_FAINT)
        score_sub.next_to(score, DOWN, buff=0.22)

        # Indicate each ring as its letter is named, landing the L + number together
        self.play(Indicate(ringH, color=INK, scale_factor=1.12), run_time=0.35)
        self.play(
            Indicate(ringL, color="#ffffff", scale_factor=1.14),
            FadeIn(score, shift=UP * 0.12),
            Flash(score_num, color="#ffffff", line_length=0.14, num_lines=12,
                  flash_radius=0.9),
            run_time=0.55,
        )
        self.play(
            Indicate(ringG, color=INK, scale_factor=1.12),
            FadeIn(score_sub, shift=UP * 0.1),
            run_time=0.4,
        )
        self.wait(0.12)

        # ============================================================
        # BEAT 5 — RE-COMPOSE + name it (9.4–11.4s).
        # ============================================================
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

        eqn = VGroup(
            serif("HLG", 26, INK),
            serif("=", 26, INK_DIM),
            serif("H ∘ L ∘ G", 26, INK_DIM),
        ).arrange(RIGHT, buff=0.26)
        eqn.next_to(merged_ring, DOWN, buff=0.48)

        three = VGroup(gH, gL, gG, comp1, comp2)
        self.play(
            ReplacementTransform(three, merged_core),
            ReplacementTransform(
                VGroup(H_letter.copy(), L_letter.copy(), G_letter.copy()), hlg_top),
            FadeOut(reveal_cap, shift=UP * 0.15),
            run_time=1.0,
        )
        self.play(Write(eqn), run_time=0.45)

        # a final small pulse threads the merged map's internal lattice -> words
        mp_world = [n.get_center() for n in mnodes]
        thread_idx = [0, 1, 3, 4]
        tp = pulse(mp_world[0], r=0.10)
        self.add(tp)
        for ia, ib in zip(thread_idx[:-1], thread_idx[1:]):
            seg = Line(mp_world[ia], mp_world[ib], stroke_color="#ffffff",
                       stroke_width=3.0, buff=0.09)
            self.play(MoveAlongPath(tp, Line(mp_world[ia], mp_world[ib], buff=0.09)),
                      Create(seg), run_time=0.2, rate_func=linear)
        self.play(FadeOut(tp, scale=0.4), run_time=0.14)

        out_words = serif("words", 24, INK).next_to(merged_ring, RIGHT, buff=0.6)
        out_arrow = mono("->", 18, INK_FAINT).next_to(merged_ring, RIGHT, buff=0.14)
        self.play(FadeIn(out_arrow), FadeIn(out_words, shift=RIGHT * 0.1), run_time=0.35)

        # bottom stamp settles to the out-of-lexicon floor
        floor = mono("open-vocabulary  ·  only 0.49% of test words out-of-lexicon  (12 / 2,429)",
                     15, INK_FAINT)
        floor.move_to(DOWN * 3.35)
        self.play(
            FadeOut(VGroup(score, score_sub), shift=DOWN * 0.12),
            FadeIn(floor, shift=UP * 0.1),
            run_time=0.5,
        )

        # ============================================================
        # BEAT 6 — POSTER HOLD (11.4–12.0s): balanced across all zones.
        # ============================================================
        # a faint cost memory on the bottom strip
        cost_memory = mono("cheapest path  8  ·  rival  11", 13, INK_GHOST)
        cost_memory.next_to(floor, UP, buff=0.18)
        self.play(FadeIn(cost_memory), run_time=0.3)
        self.wait(0.6)
