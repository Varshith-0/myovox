# REEL 5 — WORDS. "It guesses sounds, not spelling. A map of 34,546 English words
# turns sounds into sentences — by finding the cheapest path through it."
# OPENS ON: the phoneme row K AE T (== scene 4 close).
# The sounds arc onto a constellation of word-nodes; candidate paths flicker; the
# cheapest route ignites end to end and its words lift into a sentence.
# CLOSES ON: the lit sentence + 3 ghost rivals  (== scene 6 open).
from manim import *
from style import *
from reel_common import WHITE, phoneme_row, motes, drift
import numpy as np

SENTENCE = "the cat sat by the door"


class Words(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the phoneme row (matched), drift it up ---------------
        self.next_section("open")
        row = phoneme_row(("K", "AE", "T"), at=[3.7, 0, 0], s=30)
        self.add(row)
        self.play(row.animate.move_to([0, 2.6, 0]).scale(0.8), run_time=0.7,
                  rate_func=smooth)

        # ---- BEAT 1: a constellation of words ---------------------------
        self.next_section("map")
        rng = np.random.RandomState(4)
        nodes = VGroup()
        node_pts = []
        for _ in range(46):
            p = [rng.uniform(-5.6, 5.6), rng.uniform(-2.4, 1.4), 0]
            node_pts.append(p)
            nodes.add(Dot(p, radius=0.03, color=INK).set_opacity(rng.uniform(0.25, 0.6)))
        edges = VGroup()
        node_pts = np.array(node_pts)
        for i in range(len(node_pts)):
            d = np.linalg.norm(node_pts - node_pts[i], axis=1)
            for j in np.argsort(d)[1:3]:
                edges.add(Line(node_pts[i], node_pts[j], stroke_color=INK_GHOST,
                               stroke_width=0.8).set_opacity(0.3))
        maplab = mono("34,546 words", 20, INK_FAINT).to_edge(DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(e) for e in edges], lag_ratio=0.004),
                  LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.01),
                  FadeIn(maplab), run_time=1.2)

        # ---- BEAT 2: candidate paths flicker ---------------------------
        self.next_section("candidates")
        # pick a route across the map (left→right ordered nodes) for the winner
        order = np.argsort(node_pts[:, 0])
        route_idx = [order[k] for k in np.linspace(0, len(order) - 1, 6).astype(int)]
        route = [node_pts[i] for i in route_idx]

        for s in range(2):
            ridx = rng.choice(len(node_pts), 5, replace=False)
            rpts = sorted([node_pts[i] for i in ridx], key=lambda p: p[0])
            faint = VMobject().set_points_as_corners(rpts).set_stroke(INK, 1.4, opacity=0.35)
            self.play(Create(faint, run_time=0.4))
            self.play(FadeOut(faint, run_time=0.25))

        # ---- BEAT 3: the cheapest route ignites ------------------------
        self.next_section("ignite")
        winner = VMobject().set_points_as_corners(route).set_stroke(WHITE, 2.4)
        scan = Dot(route[0], radius=0.06, color=WHITE)
        self.add(scan)
        self.play(Create(winner), MoveAlongPath(scan, winner),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(scan), run_time=0.2)

        # words lift off the route and assemble into a sentence up top
        words = SENTENCE.split()
        sent = VGroup(*[mono(w, 30, INK) for w in words]).arrange(RIGHT, buff=0.32)
        sent.move_to([0, 1.6, 0])
        risers = VGroup()
        for k, w in enumerate(words):
            anchor = route[min(k, len(route) - 1)]
            wm = mono(w, 30, INK).move_to(anchor).scale(0.5).set_opacity(0.0)
            risers.add(wm)
        self.add(risers)
        self.play(
            FadeOut(nodes), FadeOut(edges), FadeOut(winner), FadeOut(maplab),
            FadeOut(row),
            LaggedStart(*[Transform(risers[k], sent[k]) for k in range(len(words))],
                        lag_ratio=0.08),
            run_time=1.1, rate_func=smooth)

        # ---- CLOSE: winner up, 3 ghost rivals beneath -------------------
        self.next_section("rivals")
        rivals_txt = ["the cat sat by the door", "the cat sped by the door",
                      "a cat sat by the door"]
        rivals = VGroup()
        for i, r in enumerate(rivals_txt):
            rg = mono(r, 24, INK_GHOST).set_opacity(0.4).move_to([0, 0.4 - i * 0.7, 0])
            rivals.add(rg)
        self.play(risers.animate.move_to([0, 1.6, 0]),  # settle winner
                  LaggedStart(*[FadeIn(r, shift=UP * 0.06) for r in rivals],
                              lag_ratio=0.1),
                  run_time=0.8)
        self.wait(0.4)
