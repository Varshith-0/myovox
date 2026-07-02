# REEL 6 — CHOOSER. "Dozens of candidates survive. A language model reads them all,
# alongside the detected sounds — and picks the one that makes the most sense."
# OPENS ON: winner sentence + ghost rivals (== scene 5 close).
# The candidates form a neat column; a scan band sweeps and reads each; four fade
# to ghost-gray and one blooms to white and re-types itself.
# CLOSES ON: the single chosen sentence, centred  (== scene 7 open).
from manim import *
from style import *
from reel_common import WHITE, motes, drift
import numpy as np

CANDIDATES = [
    "the cat sat by the door",
    "the cat sped by the door",
    "a cat sat by the door",
    "the cat sat by the floor",
    "the cat sat by the dock",
]
WINNER = 0


class Chooser(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: gather winner + rivals into a neat column -----------
        self.next_section("open")
        rows = VGroup()
        for i, c in enumerate(CANDIDATES):
            col = INK if i == 0 else INK_GHOST
            op = 1.0 if i == 0 else 0.4
            rows.add(mono(c, 24, col).set_opacity(op))
        rows.arrange(DOWN, buff=0.42, aligned_edge=LEFT).move_to([-0.6, 0, 0])
        # start from scene 5's pose (winner high, three rivals) then settle to column
        self.add(rows)
        self.play(rows.animate.set_opacity(1.0), run_time=0.1)
        for i, r in enumerate(rows):
            r.set_opacity(1.0 if i == 0 else 0.45)
        self.wait(0.1)

        # detected-sounds reference column on the right
        self.next_section("evidence")
        phon = mono("detected sounds", 15, INK_FAINT)
        phon_row = VGroup(*[mono(x, 18, INK_DIM) for x in
                            ["DH", "AH", "K", "AE", "T", "S", "AE", "T"]]
                          ).arrange(RIGHT, buff=0.16)
        ev = VGroup(phon, phon_row).arrange(DOWN, buff=0.14).to_edge(RIGHT, buff=0.4)
        ev.shift(UP * 2.4)
        self.play(FadeIn(ev, shift=DOWN * 0.1), run_time=0.5)

        # ---- BEAT 1: a scan band reads each candidate ------------------
        self.next_section("scan")
        band = Rectangle(width=7.6, height=0.5, stroke_width=0,
                         fill_color=INK, fill_opacity=0.06)
        band.move_to([rows.get_center()[0], rows[0].get_center()[1], 0])
        self.add(band)
        for r in rows:
            self.play(band.animate.move_to([rows.get_center()[0], r.get_center()[1], 0]),
                      r.animate.set_opacity(1.0).set_color(INK),
                      run_time=0.32, rate_func=smooth)
            self.play(r.animate.set_opacity(0.55 if r is not rows[0] else 1.0),
                      run_time=0.12)
        self.play(FadeOut(band), run_time=0.25)

        # ---- BEAT 2: four dim out, the winner blooms and re-types ------
        self.next_section("pick")
        losers = VGroup(*[rows[i] for i in range(len(rows)) if i != WINNER])
        win = rows[WINNER]
        self.play(losers.animate.set_opacity(0.16).set_color(INK_GHOST),
                  FadeOut(ev),
                  Flash(win.get_center(), color=WHITE, num_lines=14, flash_radius=1.2,
                        line_length=0.16),
                  win.animate.set_color(WHITE),
                  run_time=0.7)
        self.play(FadeOut(losers), run_time=0.4)

        # re-type the winner, centred, with a cursor
        final = mono(CANDIDATES[WINNER], 30, INK).move_to(ORIGIN)
        cursor = Line(UP * 0.16, DOWN * 0.16).set_stroke(WHITE, 2).next_to(final, RIGHT, buff=0.1)
        self.play(win.animate.move_to(ORIGIN).scale(30 / 24).set_color(INK),
                  run_time=0.6, rate_func=smooth)
        self.remove(win)
        self.add(final)
        self.play(FadeIn(cursor), run_time=0.2)
        self.play(cursor.animate.set_opacity(0.0), run_time=0.4)
        self.wait(0.4)
