# I2 — Why this exists. The work stands on three dense UC Davis papers; this site
# makes them watchable and shows what we changed on top.
# Beats (one per narration sentence):
#   1 PAPERS   three dense research-paper cards fan in — walls of math.
#   2 DAVIS    they come from one lab: UC Davis (Gowda, Miller & colleagues).
#   3 ONTOP    their work is the foundation; we build one block higher.
#   4 WATCH    so this is that science, made to watch — ~50 short scenes.
from manim import *
from style import *
import numpy as np


def paper(title_lines):
    pg = RoundedRectangle(width=2.7, height=3.5, corner_radius=0.07)
    pg.set_stroke(INK_GHOST, 1.5).set_fill(INK, 0.03)
    head = VGroup(*[mono(t, 13, INK_DIM) for t in title_lines]).arrange(DOWN, buff=0.07)
    rows = VGroup(*[Line(ORIGIN, [(1.7 if k % 4 else 1.0), 0, 0], stroke_color=INK_FAINT, stroke_width=1.2)
                    for k in range(9)]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    # abstract notation marks (no real on-screen formula) — the dense-paper texture
    eq = VGroup(Line(ORIGIN, [0.55, 0, 0]), Line(ORIGIN, [0.2, 0, 0]),
                Line(ORIGIN, [0.7, 0, 0])).arrange(RIGHT, buff=0.14).set_stroke(INK_FAINT, 1.4)
    inner = VGroup(head, rows, eq).arrange(DOWN, buff=0.2)
    inner.set_width(pg.width - 0.5).move_to(pg.get_center())
    return VGroup(pg, inner)


class Why(Scene):
    def construct(self):
        seed()

        # ---- BEAT 1: PAPERS ---------------------------------------------
        self.next_section("papers")
        titles = [
            ["Geometry of orofacial", "neuromuscular signals"],
            ["Non-invasive EMG speech", "neuroprosthesis"],
            ["emg2speech: synthesizing", "speech from EMG"],
        ]
        papers = VGroup(*[paper(t) for t in titles]).arrange(RIGHT, buff=0.6).move_to([0, 0.35, 0])
        papers[0].rotate(-0.05)
        papers[2].rotate(0.05)
        tag = mono("three dense research papers", 24, INK_FAINT).next_to(papers, UP, buff=0.45)
        unread = mono("walls of math most people never read", 20, INK_DIM).next_to(papers, DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.12) for p in papers], lag_ratio=0.22, run_time=1.3),
                  FadeIn(tag, run_time=0.6))
        self.play(FadeIn(unread, shift=UP * 0.08), run_time=0.5)
        self.wait(0.4)

        # ---- BEAT 2: UC DAVIS -------------------------------------------
        self.next_section("davis")
        self.play(papers.animate.scale(0.62).to_edge(UP, buff=0.9), FadeOut(unread), FadeOut(tag), run_time=0.8)
        plate = VGroup(
            mono("UC DAVIS", 30, INK, w=BOLD),
            mono("Harshavardhana T. Gowda · Lee M. Miller", 19, INK_DIM),
            mono("with Daniel C. Comstock · Zachary D. McNaughton", 17, INK_FAINT),
        ).arrange(DOWN, buff=0.16).move_to([0, -0.3, 0])
        line = Line(papers.get_bottom() + DOWN * 0.1, plate.get_top() + UP * 0.15,
                    stroke_color=INK_GHOST, stroke_width=1.2)
        self.play(Create(line), FadeIn(plate, shift=UP * 0.1), run_time=0.8)
        self.wait(0.4)

        # ---- BEAT 3: WE BUILD ON TOP ------------------------------------
        self.next_section("ontop")
        self.play(FadeOut(VGroup(papers, line)), plate.animate.scale(0.8).to_edge(UP, buff=1.0), run_time=0.7)
        found = RoundedRectangle(width=6.8, height=0.95, corner_radius=0.08).set_stroke(INK_DIM, 2).set_fill(INK, 0.05)
        found_t = mono("their foundation — approach · corpus · features", 16, INK_DIM)
        if found_t.width > found.width - 0.5:
            found_t.set_width(found.width - 0.5)
        found_t.move_to(found.get_center())
        found_g = VGroup(found, found_t).move_to([0, -1.4, 0])
        ours = RoundedRectangle(width=3.0, height=0.85, corner_radius=0.08).set_stroke("#ffffff", 2).set_fill(INK, 0.06)
        ours_t = mono("what I changed", 19, INK)
        ours_t.move_to(ours.get_center())
        ours_g = VGroup(ours, ours_t).next_to(found_g, UP, buff=0.3)
        arrow = mono("the next pages →", 17, INK_FAINT).next_to(ours_g, UP, buff=0.3)
        self.play(FadeIn(found_g, shift=UP * 0.1), run_time=0.6)
        self.play(FadeIn(ours_g, shift=DOWN * 0.1),
                  Flash(ours.get_center(), color="#ffffff", num_lines=10, flash_radius=1.0), run_time=0.6)
        self.play(FadeIn(arrow, shift=UP * 0.08), run_time=0.4)
        self.wait(0.4)

        # ---- BEAT 4: WATCHABLE ------------------------------------------
        self.next_section("watch")
        self.play(FadeOut(VGroup(plate, found_g, ours_g, arrow)), run_time=0.5)
        head = serif("the same science — made to watch", 44).move_to([0, 0.7, 0])
        axis = Line([-5.6, -0.6, 0], [5.6, -0.6, 0], stroke_color=INK_GHOST, stroke_width=1.5)
        ticks = VGroup(*[Line([x, -0.78, 0], [x, -0.42, 0], stroke_color=INK, stroke_width=2)
                         for x in np.linspace(-5.4, 5.4, 50)])
        sub = mono("≈ 50 short scenes — one idea each", 24, INK_DIM).move_to([0, -1.7, 0])
        self.play(Write(head, run_time=0.9))
        self.play(Create(axis), LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.015, run_time=1.0),
                  FadeIn(sub, shift=UP * 0.1))
        self.wait(0.5)
