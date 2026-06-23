# b17_sounds_to_words_search.py — "Cheapest road"  (bridge after the WFST anchor)
#
# THE IDEA: turning a stream of per-frame sounds into words is a SEARCH problem —
# least-cost path through a weighted graph. Every word choice is a toll-bearing
# edge; the best sentence is the lowest-total-cost route from start to end.
#
# Three persistent zones (3b1b: pose -> build -> transform -> name):
#   TOP    (y ~ +2.6..+3.5)  CONTEXT: the per-frame sounds carried from the heads
#          look — a slim ghost ribbon of phoneme tokens feeding a left "start" node.
#   CENTER (y ~ -1.6..+2.2)  MECHANISM: roads branch out into a node-and-edge
#          lattice; gibberish dead-ends dim out; surviving edges get small num()
#          tolls (cheap when sound+grammar agree, dear when they fight); a
#          Dijkstra wavefront explores; a tempting-but-pricey detour is rejected;
#          one continuous route lights up start->end spelling a real sentence.
#   BOTTOM (y ~ -3.4..-2.6) TAKEAWAY: a live running-total of the winning route's
#          tolls ticks up edge by edge; resolves to the named payoff.
#   final  a balanced poster holds ~0.6s.
from manim import *
from emg_style import *

WHITE = "#ffffff"


def tri(angle, c, op=1.0, s=0.075):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def toll_label(value, edge, c=INK_FAINT, fs=15, off=0.20):
    """A small toll number parked beside the midpoint of an edge."""
    t = num(value, fs, c)
    mid = (edge.get_start() + edge.get_end()) / 2
    # nudge perpendicular to the edge so the number sits off the road, not on it.
    d = edge.get_unit_vector()
    perp = np.array([-d[1], d[0], 0]) * off
    t.move_to(mid + perp)
    return t


class SoundsToWordsSearch(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B0 — POSE: the per-frame sounds (carried in) feed a left START node.
        # =================================================================
        self.next_section("pose")

        top1 = mono("the sounds are in — now read them as words", 20, INK_DIM).move_to([0, 3.42, 0])
        rule = Line([-6.5, 3.06, 0], [6.5, 3.06, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.12), Create(rule), run_time=0.42)

        # a slim ribbon of per-frame phoneme tokens — the carried-over stream.
        toks = ["DH", "AH", "K", "AE", "T", "S", "AE", "T"]
        ribbon = VGroup(*[mono(t, 16, INK_FAINT) for t in toks]).arrange(RIGHT, buff=0.30)
        ribbon.move_to([-2.1, 2.62, 0])
        ribbon_tag = mono("per-frame sounds", 13, INK_GHOST).next_to(ribbon, LEFT, buff=0.3)
        self.play(LaggedStartMap(FadeIn, ribbon, lag_ratio=0.06, run_time=0.5),
                  FadeIn(ribbon_tag), run_time=0.5)

        # START node on the left of the center band.
        start_pt = np.array([-6.0, 0.3, 0])
        start = Circle(0.26, stroke_color=INK, stroke_width=2.6, fill_color=BG, fill_opacity=1)
        start.move_to(start_pt)
        start_lab = mono("start", 14, INK_DIM).next_to(start, DOWN, buff=0.16)
        # the ribbon feeds the start node.
        feed = flat_line(ribbon.get_bottom() + DOWN * 0.05, start.get_top(), INK_GHOST, 1.4)
        self.play(GrowFromCenter(start), FadeIn(start_lab),
                  Create(feed), run_time=0.45)

        # =================================================================
        # B1 — BUILD: roads branch into a lattice; surviving edges get tolls.
        # =================================================================
        self.next_section("build")

        # Layered node lattice. Columns are decode "stages"; each node is a partial
        # word hypothesis. We hand-author a small legible map of word choices.
        end_pt = np.array([6.2, 0.3, 0])
        cols_x = [-3.6, -1.2, 1.2, 3.8]
        col_ys = [
            [1.5, 0.3, -1.0],          # col 0: "the" / "a" / "duh"(gibberish)
            [1.5, 0.3, -1.0],          # col 1: "cat" / "cad" / "kat"(gibberish)
            [1.5, 0.3, -1.0],          # col 2: "sat" / "set" / "zat"(gibberish)
            [0.3],                     # col 3 collapses toward END
        ]
        col_words = [
            ["the", "a", "duh"],
            ["cat", "cad", "kat"],
            ["sat", "set", "zat"],
            ["·"],
        ]
        # which (col,row) indices are gibberish dead-ends to be dimmed/pruned.
        gibberish = {(0, 2), (1, 2), (2, 2)}

        nodes = {}     # (col,row) -> Circle
        node_lab = {}  # (col,row) -> Text
        node_grp = VGroup()
        for ci, xs in enumerate(cols_x):
            for ri, y in enumerate(col_ys[ci]):
                n = Circle(0.30, stroke_color=INK_FAINT, stroke_width=1.8,
                           fill_color=BG, fill_opacity=1).move_to([xs, y, 0])
                w = col_words[ci][ri]
                lab = mono(w, 15, INK if w != "·" else INK_FAINT).move_to(n)
                nodes[(ci, ri)] = n
                node_lab[(ci, ri)] = lab
                node_grp.add(n, lab)

        end = Circle(0.26, stroke_color=INK, stroke_width=2.6, fill_color=BG, fill_opacity=1)
        end.move_to(end_pt)
        end_lab = mono("end", 14, INK_DIM).next_to(end, DOWN, buff=0.16)

        # Edges: start -> col0, col0 -> col1, col1 -> col2, col2 -> end.
        # Each edge carries a toll. Small toll = sound & grammar agree.
        # We only wire the SENSIBLE through-routes (no gibberish targets), and
        # add a couple of cross edges so there are competing partial paths.
        # edge spec: (src_key, dst_key, toll). keys: "start","end", or (col,row).
        edge_spec = [
            ("start", (0, 0), 1),   # the
            ("start", (0, 1), 2),   # a
            ("start", (0, 2), 7),   # duh (gibberish, expensive)
            ((0, 0), (1, 0), 1),    # the->cat  (cheap, agrees)
            ((0, 0), (1, 1), 4),    # the->cad  (pricey detour)
            ((0, 1), (1, 0), 3),    # a->cat
            ((0, 2), (1, 2), 6),    # duh->kat (dead-end chain)
            ((1, 0), (2, 0), 1),    # cat->sat (cheap)
            ((1, 0), (2, 1), 5),    # cat->set (pricey)
            ((1, 1), (2, 0), 3),    # cad->sat
            ((1, 2), (2, 2), 6),    # kat->zat (dead-end chain)
            ((2, 0), "end", 1),     # sat->end (cheap)
            ((2, 1), "end", 4),     # set->end
            ((2, 2), "end", 8),     # zat->end (dead-end, very dear)
        ]

        def pt_of(key):
            if key == "start":
                return start.get_right()
            if key == "end":
                return end.get_left()
            return nodes[key].get_center()

        # build edges + tolls
        edges = {}      # (src,dst) -> Line
        tolls = {}      # (src,dst) -> Text
        edge_grp = VGroup()
        toll_grp = VGroup()
        for src, dst, c in edge_spec:
            a = pt_of(src)
            b = pt_of(dst)
            # shorten so the road meets node rims, not centers
            d = (b - a)
            L = np.linalg.norm(d)
            u = d / L
            a2 = a + u * 0.30 if src not in ("start",) else a + u * 0.02
            b2 = b - u * 0.30 if dst not in ("end",) else b - u * 0.02
            ln = Line(a2, b2, stroke_color=INK_GHOST, stroke_width=1.6)
            edges[(src, dst)] = ln
            edge_grp.add(ln)
            # push the diagonal cross-edge tolls further off the road so the two
            # diagonals crossing near mid-column don't collide.
            off = 0.34 if (src not in ("start",) and dst not in ("end",)) else 0.20
            tl = toll_label(c, ln, INK_FAINT, 14, off)
            tolls[(src, dst)] = tl
            toll_grp.add(tl)

        cap_build = mono("every route is a way the sounds spell real words",
                         16, INK_FAINT).move_to([0, -2.0, 0])

        # branch the roads outward column by column.
        self.play(GrowFromCenter(end), FadeIn(end_lab), run_time=0.3)
        self.play(LaggedStartMap(FadeIn, node_grp, lag_ratio=0.03, run_time=0.6),
                  FadeIn(cap_build), run_time=0.6)
        self.play(LaggedStartMap(Create, edge_grp, lag_ratio=0.04, run_time=0.7))

        # tolls fade in — "give each step a toll"
        cap_toll = mono("each step pays a toll — cheap when sound & grammar agree",
                        16, INK_FAINT).move_to([0, -2.0, 0])
        self.play(ReplacementTransform(cap_build, cap_toll),
                  LaggedStartMap(FadeIn, toll_grp, lag_ratio=0.04, run_time=0.6),
                  run_time=0.6)

        # =================================================================
        # B2 — PRUNE: gibberish dead-ends dim out.
        # =================================================================
        self.next_section("prune")

        dead_nodes = VGroup(*[VGroup(nodes[k], node_lab[k]) for k in gibberish])
        dead_edges = VGroup(*[edges[e] for e in edges if e[0] in gibberish or e[1] in gibberish])
        dead_tolls = VGroup(*[tolls[e] for e in tolls if e[0] in gibberish or e[1] in gibberish])
        cap_prune = mono("roads that spell gibberish dead-end and drop away",
                         16, INK_FAINT).move_to([0, -2.0, 0])
        self.play(ReplacementTransform(cap_toll, cap_prune), run_time=0.3)
        self.play(dead_nodes.animate.set_opacity(0.10),
                  dead_edges.animate.set_stroke(opacity=0.08),
                  dead_tolls.animate.set_opacity(0.10),
                  run_time=0.55)
        self.wait(0.3)

        # =================================================================
        # B3 — TRANSFORM: a Dijkstra-like wavefront explores; the cheap route
        #      wins; a tempting-but-pricey detour is rejected. Running total below.
        # =================================================================
        self.next_section("explore")

        # bottom: running total of the winning route's tolls.
        bot_tag = mono("cheapest route — running toll", 15, INK_FAINT).move_to([-3.4, -3.0, 0])
        total = ValueTracker(0)
        total_read = counter(total, fmt=lambda v: str(int(round(v))), s=40, c=INK,
                             at=np.array([0.3, -3.0, 0]))
        self.add(total_read)
        self.play(FadeIn(bot_tag), FadeIn(total_read), run_time=0.3)

        cap_explore = mono("a search explores outward, keeping the cheapest so far",
                           16, INK_FAINT).move_to([0, -2.0, 0])
        self.play(ReplacementTransform(cap_prune, cap_explore), run_time=0.3)

        # wavefront: pulse circles bloom from start across reachable nodes.
        wave_keys = ["start", (0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), "end"]
        fronts = VGroup()
        for k in wave_keys:
            c = (start if k == "start" else end if k == "end" else nodes[k])
            ring = Circle(0.30, stroke_color=INK, stroke_width=2.0,
                          fill_opacity=0).move_to(c.get_center())
            fronts.add(ring)
        self.play(LaggedStart(*[ShowPassingFlash(r, time_width=0.6) for r in fronts],
                              lag_ratio=0.10, run_time=1.0))

        # the tempting-but-pricey detour: the->cad (toll 4) lights, then is rejected.
        detour_edge = edges[((0, 0), (1, 1))]
        detour_node = VGroup(nodes[(1, 1)], node_lab[(1, 1)])
        detour_toll = tolls[((0, 0), (1, 1))]
        cross = Cross(nodes[(1, 1)], stroke_color=INK, stroke_width=2.2).scale(0.7)
        self.play(detour_edge.animate.set_stroke(INK_DIM, width=2.6),
                  Indicate(detour_toll, scale_factor=1.3, color=INK), run_time=0.4)
        self.play(Create(cross),
                  detour_edge.animate.set_stroke(INK_GHOST, width=1.2, opacity=0.25),
                  detour_node.animate.set_opacity(0.18),
                  detour_toll.animate.set_opacity(0.18),
                  run_time=0.45)
        self.remove(cross)

        # =================================================================
        # B4 — WIN: one continuous lowest-cost route lights up start->end.
        # =================================================================
        self.next_section("win")

        cap_win = mono("one route is cheapest end to end", 16, INK_FAINT).move_to([0, -2.0, 0])
        self.play(ReplacementTransform(cap_explore, cap_win), run_time=0.3)

        # winning path: start -1-> the -1-> cat -1-> sat -1-> end  (total 4)
        win_seq = ["start", (0, 0), (1, 0), (2, 0), "end"]
        win_edges = [("start", (0, 0)), ((0, 0), (1, 0)),
                     ((1, 0), (2, 0)), ((2, 0), "end")]
        win_tolls_vals = [1, 1, 1, 1]

        # light the start node.
        self.play(start.animate.set_stroke(WHITE, width=3.2), run_time=0.2)

        running = 0
        for ei, ekey in enumerate(win_edges):
            ln = edges[ekey]
            dst = win_seq[ei + 1]
            dst_node = end if dst == "end" else nodes[dst]
            dst_lab = end_lab if dst == "end" else node_lab[dst]
            running += win_tolls_vals[ei]
            # a bright pulse traces the road, the node ignites, the total ticks.
            pulse = Dot(ln.get_start(), radius=0.06, color=WHITE)
            self.add(pulse)
            anims = [
                ln.animate.set_stroke(WHITE, width=3.4),
                pulse.animate.move_to(ln.get_end()),
                dst_node.animate.set_stroke(WHITE, width=3.0),
                total.animate.set_value(running),
                Indicate(tolls[ekey], scale_factor=1.25, color=INK),
            ]
            if dst != "end":
                anims.append(dst_lab.animate.set_color(WHITE))
            self.play(*anims, run_time=0.55, rate_func=linear)
            self.remove(pulse)

        # the spelled sentence rises from the lit word-nodes.
        sentence = serif("the cat sat", 46, WHITE).move_to([0, -1.05, 0])
        sent_src = VGroup(node_lab[(0, 0)], node_lab[(1, 0)], node_lab[(2, 0)])
        self.play(ReplacementTransform(cap_win, sentence), run_time=0.5)
        self.wait(0.35)

        # =================================================================
        # B5 — NAME IT + POSTER HOLD.
        # =================================================================
        self.next_section("name")

        total.clear_updaters()
        total_read.clear_updaters()
        payoff = serif("cheapest path", 40, WHITE).move_to([0, 0.3, 0])
        payoff_g = glow(payoff)
        sub = mono("decoding = shortest route through a graph", 17, INK_DIM)
        sub.next_to(payoff, DOWN, buff=0.22)

        # clear the lattice clutter so the name owns the frame; keep start/end glow.
        clutter = VGroup(node_grp, edge_grp, toll_grp, start, end, start_lab, end_lab,
                         feed, ribbon, ribbon_tag, sentence, fronts)
        self.play(FadeOut(clutter, run_time=0.45),
                  FadeOut(bot_tag), FadeOut(total_read), run_time=0.45)
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  Flash([0, 0.3, 0], color=WHITE, line_length=0.22, num_lines=14,
                        flash_radius=1.5, time_width=0.4), run_time=0.55)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.4)
        self.wait(0.6)


def flat_line(start, end, c=INK_GHOST, w=1.4):
    return Line(start, end, stroke_color=c, stroke_width=w)
