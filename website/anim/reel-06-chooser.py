# REEL 6 — CHOOSER. "Dozens of candidates survive. A language model reads them all,
# alongside the detected sounds — and picks the one that makes the most sense."
# OPENS ON: the sentence from scene 5, which is revealed to be just ONE candidate.
# NOTE: scene 5 already showed a sentence being *built*; this scene is only about
# CHOOSING among ready-made candidates — no re-building. The detected sounds cover
# the WHOLE sentence, so they stay consistent with the candidates.
# CLOSES ON: the single chosen sentence at ORIGIN, size 30  (== scene 7 open).
from manim import *
from style import *
from reel_common import WHITE, motes, drift

WINNER_TXT = "the cat sat by the door"
# The candidates, winner in the MIDDLE so it stays centred through the scene.
DISPLAY = [
    "the cat sped by the door",
    "a cat sat by the door",
    "the cat sat by the door",   # WINNER
    "the cat sat by the floor",
    "the cat sat by the dock",
]
WIN_I = 2
# Detected phonemes for the WHOLE sentence, grouped by word (the ↔ DH AH, etc.).
PHON_GROUPS = [["DH", "AH"], ["K", "AE", "T"], ["S", "AE", "T"],
               ["B", "AY"], ["DH", "AH"], ["D", "AO", "R"]]


class Chooser(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the winning sentence (matched from scene 5) ---------
        self.next_section("open")
        win0 = mono(WINNER_TXT, 30, INK).move_to([0, 0.1, 0])
        self.add(win0)
        self.wait(0.1)

        # detected sounds — the WHOLE sentence, grouped by word, along the top
        self.next_section("sounds")
        groups = VGroup(*[VGroup(*[mono(p, 16, INK_DIM) for p in g]).arrange(RIGHT, buff=0.12)
                          for g in PHON_GROUPS]).arrange(RIGHT, buff=0.46)
        slab = mono("detected sounds", 14, INK_FAINT)
        snd = VGroup(slab, groups).arrange(DOWN, buff=0.16)
        if snd.width > 12.4:
            snd.scale(12.4 / snd.width)
        snd.move_to([0, 2.75, 0])
        self.play(FadeIn(slab), LaggedStart(*[FadeIn(g, shift=DOWN * 0.06) for g in groups],
                                            lag_ratio=0.05), run_time=0.7)

        # ---- BEAT 1: it's one of several candidates that fit the sounds -
        self.next_section("candidates")
        rows = VGroup(*[mono(t, 24, INK) for t in DISPLAY])
        rows.arrange(DOWN, buff=0.42, aligned_edge=LEFT).move_to([0, 0, 0])
        for i, r in enumerate(rows):
            if i != WIN_I:
                r.set_color(INK_DIM).set_opacity(0.5)
        self.play(Transform(win0, rows[WIN_I]), run_time=0.5, rate_func=smooth)
        self.remove(win0)
        self.add(rows[WIN_I])
        self.play(LaggedStart(*[FadeIn(rows[i], shift=UP * 0.05)
                                for i in range(5) if i != WIN_I], lag_ratio=0.08),
                  run_time=0.7)
        cap = mono("several sentences fit the sounds", 16, INK_FAINT).move_to([0, -2.55, 0])
        self.play(FadeIn(cap), run_time=0.3)

        # ---- BEAT 2: a language model reads each against the sounds -----
        self.next_section("read")
        cap2 = mono("a language model reads each one", 16, INK_FAINT).move_to([0, -2.55, 0])
        self.play(ReplacementTransform(cap, cap2),
                  groups.animate.set_color(INK), run_time=0.3)
        band = RoundedRectangle(width=rows.width + 0.7, height=0.56, corner_radius=0.1,
                                stroke_width=0, fill_color=INK, fill_opacity=0.09)
        band.move_to([rows.get_center()[0], rows[0].get_center()[1], 0])
        self.add(band)
        for i, r in enumerate(rows):
            self.play(band.animate.move_to([rows.get_center()[0], r.get_center()[1], 0]),
                      r.animate.set_opacity(1.0).set_color(INK),
                      run_time=0.28, rate_func=smooth)
            if i != WIN_I:
                self.play(r.animate.set_opacity(0.5).set_color(INK_DIM), run_time=0.1)
        self.play(FadeOut(band), groups.animate.set_color(INK_DIM), run_time=0.2)

        # ---- BEAT 3: it locks the best one; the rest fade --------------
        self.next_section("pick")
        cap3 = mono("picks the one that makes the most sense", 16, INK_FAINT).move_to([0, -2.55, 0])
        self.play(ReplacementTransform(cap2, cap3), run_time=0.3)
        win = rows[WIN_I]
        losers = VGroup(*[rows[i] for i in range(5) if i != WIN_I])
        underline = Line(win.get_left() + DOWN * 0.28, win.get_right() + DOWN * 0.28,
                         stroke_color=WHITE, stroke_width=2)
        self.play(win.animate.set_color(WHITE),
                  Create(underline),
                  Flash(win.get_center(), color=WHITE, num_lines=14, flash_radius=1.5,
                        line_length=0.16),
                  losers.animate.set_opacity(0.12).set_color(INK_GHOST),
                  run_time=0.6)
        self.play(FadeOut(losers), FadeOut(snd), FadeOut(cap3), run_time=0.45)

        # settle the winner at ORIGIN, size 30 (== scene 7 open)
        self.next_section("settle")
        self.play(win.animate.move_to(ORIGIN).scale(30 / 24).set_color(INK),
                  underline.animate.set_opacity(0.0), run_time=0.5, rate_func=smooth)
        self.remove(underline)
        self.wait(0.4)
