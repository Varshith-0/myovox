# b17_sounds_to_words_search.py — "Cheapest road" (search framing, invented)
#
# THE IDEA: a stream of sounds is AMBIGUOUS — a hundred sentences fit it. So lead
# with the ambiguity (a fan of ghost candidate sentences), then let the viewer
# invent the framing: lay the choices out as a map of forked roads, give each
# fork a toll, and the best reading is the cheapest route across.
#
# 7-beat sheet (one self.next_section per beat, timed to dur_sec, total ~12.1s):
#   1 ambiguity   phoneme ribbon glows; faint fan of ghost candidate sentences
#   2 which one?  ghosts dim to a question; START lights, ribbon feeds it
#   3 build map   roads branch column by column into the node/edge lattice
#   4 tolls       small toll numbers fade beside each edge (cheap vs steep)
#   5 one route   a sample route lights start->end; running total ticks up
#   6 gibberish   dead-end roads flash big tolls then dim and drop away
#   7 cheapest    the lowest-total route ignites "the cat sat"; lattice clears;
#                 "cheapest path" resolves center-frame; brief poster hold.
from manim import *
from emg_style import *

WHITE = "#ffffff"


def flat_line(a, b, c=INK_GHOST, w=1.4):
    return Line(a, b, stroke_color=c, stroke_width=w)


def toll_label(value, edge, c=INK_FAINT, fs=14, off=0.20):
    """A small toll number parked beside the midpoint of an edge."""
    t = num(value, fs, c)
    mid = (edge.get_start() + edge.get_end()) / 2
    d = edge.get_unit_vector()
    perp = np.array([-d[1], d[0], 0]) * off
    t.move_to(mid + perp)
    return t


class SoundsToWordsSearch(Scene):
    def construct(self):
        seed()

        # =================================================================
        # BEAT 1 — AMBIGUITY (~1.43s): the phoneme ribbon glows; a faint fan of
        #          ghost candidate sentences hovers above it, none chosen.
        # =================================================================
        self.next_section("ambiguity")

        toks = ["DH", "AH", "K", "AE", "T", "S", "AE", "T"]
        ribbon = VGroup(*[mono(t, 18, INK) for t in toks]).arrange(RIGHT, buff=0.34)
        ribbon.move_to([0, 1.4, 0])
        ribbon_tag = mono("a stream of sounds", 14, INK_FAINT)
        ribbon_tag.next_to(ribbon, DOWN, buff=0.22)

        # a faint fan of candidate sentences — "a hundred could fit".
        ghosts_txt = ["the cat sat", "a cad set", "duh kat zat", "the cad sat"]
        ghosts = VGroup(*[serif(g, 24, INK_GHOST) for g in ghosts_txt])
        ghosts.arrange(DOWN, buff=0.30).move_to([0, 3.0, 0])

        self.play(
            LaggedStart(*[FadeIn(t, shift=DOWN * 0.08) for t in ribbon],
                        lag_ratio=0.07),
            FadeIn(ribbon_tag),
            run_time=0.6,
        )
        glow_ribbon = glow(ribbon.copy().set_color(WHITE))
        self.add(glow_ribbon)
        self.play(
            LaggedStart(*[FadeIn(g) for g in ghosts], lag_ratio=0.10),
            glow_ribbon.animate.set_opacity(0.0),
            run_time=0.55,
        )
        self.remove(glow_ribbon)
        # flicker the ghosts — none chosen.
        self.play(ghosts.animate.set_opacity(0.55), run_time=0.14)
        self.play(ghosts.animate.set_opacity(0.22), run_time=0.14)

        # =================================================================
        # BEAT 2 — WHICH ONE? (~0.6s): ghosts dim to a question; START lights,
        #          the ribbon feeding into it.
        # =================================================================
        self.next_section("which")

        question = serif("which one?", 30, INK_DIM).move_to([0, 3.0, 0])
        start_pt = np.array([-6.0, 0.3, 0])
        start = Circle(0.26, stroke_color=INK, stroke_width=2.8,
                       fill_color=BG, fill_opacity=1).move_to(start_pt)
        start_lab = mono("start", 14, INK_DIM).next_to(start, DOWN, buff=0.16)
        feed = flat_line(ribbon.get_left() + LEFT * 0.1, start.get_top() + RIGHT * 0.05,
                         INK_GHOST, 1.4)

        self.play(
            ReplacementTransform(ghosts, question),
            ribbon.animate.set_color(INK_DIM).scale(0.85).move_to([-1.6, 2.5, 0]),
            ribbon_tag.animate.set_opacity(0.0),
            run_time=0.32,
        )
        self.play(
            GrowFromCenter(start), FadeIn(start_lab),
            Create(feed),
            start.animate.set_stroke(WHITE, width=3.2),
            run_time=0.34,
        )

        # =================================================================
        # BEAT 3 — BUILD MAP (~2.27s): roads branch column by column into the
        #          node-and-edge lattice. Forks visible, no tolls yet.
        # =================================================================
        self.next_section("build")

        self.play(question.animate.set_opacity(0.18),
                  start.animate.set_stroke(INK, width=2.8), run_time=0.3)

        end_pt = np.array([6.0, 0.3, 0])
        cols_x = [-3.4, 0.0, 3.4]
        col_ys = [
            [1.5, 0.3, -1.0],
            [1.5, 0.3, -1.0],
            [1.5, 0.3, -1.0],
        ]
        col_words = [
            ["the", "a", "duh"],
            ["cat", "cad", "kat"],
            ["sat", "set", "zat"],
        ]
        gibberish = {(0, 2), (1, 2), (2, 2)}

        nodes = {}
        node_lab = {}
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

        end = Circle(0.26, stroke_color=INK, stroke_width=2.8,
                     fill_color=BG, fill_opacity=1).move_to(end_pt)
        end_lab = mono("end", 14, INK_DIM).next_to(end, DOWN, buff=0.16)

        edge_spec = [
            ("start", (0, 0), 1),
            ("start", (0, 1), 2),
            ("start", (0, 2), 7),
            ((0, 0), (1, 0), 1),
            ((0, 0), (1, 1), 4),
            ((0, 1), (1, 0), 3),
            ((0, 2), (1, 2), 6),
            ((1, 0), (2, 0), 1),
            ((1, 0), (2, 1), 5),
            ((1, 1), (2, 0), 3),
            ((1, 2), (2, 2), 6),
            ((2, 0), "end", 1),
            ((2, 1), "end", 4),
            ((2, 2), "end", 8),
        ]

        def pt_of(key):
            if key == "start":
                return start.get_right()
            if key == "end":
                return end.get_left()
            return nodes[key].get_center()

        edges = {}
        tolls = {}
        edge_grp = VGroup()
        toll_grp = VGroup()
        for src, dst, c in edge_spec:
            a = pt_of(src)
            b = pt_of(dst)
            d = (b - a)
            L = np.linalg.norm(d)
            u = d / L
            a2 = a + u * 0.30 if src != "start" else a + u * 0.02
            b2 = b - u * 0.30 if dst != "end" else b - u * 0.02
            ln = Line(a2, b2, stroke_color=INK_GHOST, stroke_width=1.6)
            edges[(src, dst)] = ln
            edge_grp.add(ln)
            off = 0.34 if (src != "start" and dst != "end") else 0.20
            tl = toll_label(c, ln, INK_FAINT, 14, off)
            tolls[(src, dst)] = tl
            toll_grp.add(tl)

        cap_build = mono("each fork is a way the sounds could spell a word",
                         16, INK_FAINT).move_to([0, -2.3, 0])

        self.play(GrowFromCenter(end), FadeIn(end_lab), run_time=0.32)
        self.play(LaggedStart(*[FadeIn(m) for m in node_grp], lag_ratio=0.03),
                  FadeIn(cap_build), run_time=0.7)
        self.play(LaggedStart(*[Create(e) for e in edge_grp], lag_ratio=0.04),
                  run_time=0.8)
        self.wait(0.4)

        # =================================================================
        # BEAT 4 — TOLLS (~1.92s): small toll numbers fade in beside each edge.
        # =================================================================
        self.next_section("tolls")

        cap_toll = mono("give every step a toll — cheap when sound & grammar agree",
                        16, INK_FAINT).move_to([0, -2.3, 0])
        self.play(ReplacementTransform(cap_build, cap_toll),
                  LaggedStart(*[FadeIn(t) for t in toll_grp], lag_ratio=0.05),
                  run_time=0.9)
        self.wait(0.85)

        # =================================================================
        # BEAT 5 — ONE ROUTE (~2.1s): a sample route lights start->end; the
        #          running total ticks up edge by edge.
        # =================================================================
        self.next_section("route")

        cap_route = mono("a sentence is one route — its cost is the sum of its tolls",
                         16, INK_FAINT).move_to([0, -2.3, 0])
        self.play(ReplacementTransform(cap_toll, cap_route), run_time=0.3)

        bot_tag = mono("running toll", 15, INK_FAINT).move_to([-1.5, -3.3, 0])
        total = ValueTracker(0)
        total_read = counter(total, fmt=lambda v: str(int(round(v))), s=34, c=INK,
                             at=np.array([0.4, -3.3, 0]))
        self.add(total_read)
        self.play(FadeIn(bot_tag), FadeIn(total_read), run_time=0.25)

        # dim the lattice so the sample route reads as the one focal object.
        self.play(node_grp.animate.set_opacity(0.4),
                  edge_grp.animate.set_stroke(opacity=0.22),
                  toll_grp.animate.set_opacity(0.4),
                  run_time=0.25)

        win_seq = ["start", (0, 0), (1, 0), (2, 0), "end"]
        win_edges = [("start", (0, 0)), ((0, 0), (1, 0)),
                     ((1, 0), (2, 0)), ((2, 0), "end")]
        win_tolls_vals = [1, 1, 1, 1]

        self.play(start.animate.set_stroke(INK, width=3.0), run_time=0.12)
        running = 0
        for ei, ekey in enumerate(win_edges):
            ln = edges[ekey]
            dst = win_seq[ei + 1]
            dst_node = end if dst == "end" else nodes[dst]
            dst_lab = end_lab if dst == "end" else node_lab[dst]
            running += win_tolls_vals[ei]
            pulse = Dot(ln.get_start(), radius=0.06, color=INK)
            self.add(pulse)
            anims = [
                ln.animate.set_stroke(INK, width=3.0, opacity=1.0),
                pulse.animate.move_to(ln.get_end()),
                dst_node.animate.set_stroke(INK, width=2.6).set_opacity(1.0),
                total.animate.set_value(running),
                Indicate(tolls[ekey], scale_factor=1.25, color=INK),
            ]
            if dst != "end":
                anims.append(dst_lab.animate.set_color(INK).set_opacity(1.0))
            self.play(*anims, run_time=0.32, rate_func=linear)
            self.remove(pulse)
        self.wait(0.2)

        # =================================================================
        # BEAT 6 — GIBBERISH (~1.41s): dead-end roads flash big tolls then dim
        #          and drop away.
        # =================================================================
        self.next_section("gibberish")

        cap_gib = mono("gibberish roads pile up huge tolls — never taken",
                       16, INK_FAINT).move_to([0, -2.3, 0])
        self.play(ReplacementTransform(cap_route, cap_gib), run_time=0.3)

        dead_nodes = VGroup(*[VGroup(nodes[k], node_lab[k]) for k in gibberish])
        dead_edges = VGroup(*[edges[e] for e in edges
                              if e[0] in gibberish or e[1] in gibberish])
        dead_tolls = VGroup(*[tolls[e] for e in tolls
                              if e[0] in gibberish or e[1] in gibberish])

        # flash the big tolls bright, then drop the dead-ends away.
        self.play(dead_tolls.animate.set_opacity(1.0).set_color(INK),
                  dead_edges.animate.set_stroke(INK_DIM, opacity=0.6, width=2.0),
                  run_time=0.35)
        self.play(Indicate(dead_tolls, scale_factor=1.2, color=INK), run_time=0.3)
        self.play(dead_nodes.animate.set_opacity(0.06),
                  dead_edges.animate.set_stroke(opacity=0.05),
                  dead_tolls.animate.set_opacity(0.06),
                  run_time=0.46)

        # =================================================================
        # BEAT 7 — CHEAPEST (~2.41s): the lowest-total route ignites the words;
        #          lattice clears; "cheapest path" resolves; poster hold.
        # =================================================================
        self.next_section("cheapest")

        cap_cheap = mono("the best reading is the cheapest way across",
                         16, INK_FAINT).move_to([0, -2.3, 0])
        self.play(ReplacementTransform(cap_gib, cap_cheap), run_time=0.3)

        # ignite the winning route in white, start->end.
        win_path = VGroup(start, *[edges[e] for e in win_edges],
                          *[nodes[k] for k in win_seq if k not in ("start", "end")],
                          end)
        self.play(start.animate.set_stroke(WHITE, width=3.4),
                  end.animate.set_stroke(WHITE, width=3.4),
                  *[edges[e].animate.set_stroke(WHITE, width=3.4) for e in win_edges],
                  *[nodes[k].animate.set_stroke(WHITE, width=3.0)
                    for k in win_seq if k not in ("start", "end")],
                  *[node_lab[k].animate.set_color(WHITE)
                    for k in win_seq if k not in ("start", "end")],
                  run_time=0.5)

        sentence = serif("the cat sat", 40, WHITE).move_to([0, -1.1, 0])
        sent_src = VGroup(node_lab[(0, 0)], node_lab[(1, 0)], node_lab[(2, 0)])
        self.play(TransformFromCopy(sent_src, sentence), run_time=0.5)
        self.wait(0.35)

        # clear the lattice; the name lands plainly.
        total.clear_updaters()
        total_read.clear_updaters()
        clutter = VGroup(node_grp, edge_grp, toll_grp, start, end, start_lab, end_lab,
                         feed, ribbon, question, sentence, cap_cheap,
                         bot_tag, total_read)
        self.play(FadeOut(clutter), run_time=0.5)

        payoff = serif("cheapest path", 44, WHITE).move_to(ORIGIN)
        payoff_g = glow(payoff)
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  Flash(ORIGIN, color=WHITE, line_length=0.22, num_lines=14,
                        flash_radius=1.6, time_width=0.4),
                  run_time=0.55)
        self.wait(0.65)
