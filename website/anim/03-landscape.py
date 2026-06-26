# I3 — Landscape. Three ways to read speech from the body, scored honestly —
# including safety — and why surface EMG is the promising middle path.
# Beats (one per narration sentence):
#   1 DOORS     three columns: brain implant, scalp cap, skin sensors (EMG).
#   2 INVASIVE  fill implant: surgery, strong signal, no movement, surgical risk.
#   3 SCALP     fill cap: no surgery, weak signal, no movement, safe.
#   4 SKIN      fill EMG: no surgery, strong signal, needs movement, safe — the
#               promising sweet spot.
#   5 CAVEAT    the honesty line: EMG needs movement — not for the fully
#               paralyzed, but the safe middle path for everyone who can move.
from manim import *
from style import *
import numpy as np

COLX = [-4.0, 0.2, 4.4]
ICON_Y = 1.75
ROWY = [0.45, -0.4, -1.25, -2.1]
LABX = -5.6


def head_base(cx, cy):
    return Circle(radius=0.42, stroke_color=INK, stroke_width=2).set_fill(INK, 0.03).move_to([cx, cy, 0])


def implant_icon(cx, cy):
    return VGroup(head_base(cx, cy),
                  Line([cx, cy + 0.52, 0], [cx, cy + 0.02, 0]).set_stroke("#ffffff", 2.4),
                  Dot([cx, cy + 0.02, 0], radius=0.05, color="#ffffff"))


def cap_icon(cx, cy):
    cap = Arc(0.52, PI * 0.18, PI * 0.64, arc_center=[cx, cy, 0]).set_stroke(INK_DIM, 2.4)
    dots = VGroup(*[Dot([cx + 0.52 * np.cos(a), cy + 0.52 * np.sin(a), 0], radius=0.04, color=INK_DIM)
                    for a in np.linspace(PI * 0.22, PI * 0.78, 4)])
    return VGroup(head_base(cx, cy), cap, dots)


def skin_icon(cx, cy):
    pts = [(-0.16, -0.05), (-0.03, -0.19), (0.12, -0.1), (0.02, 0.07), (-0.19, 0.1), (0.18, 0.05)]
    dots = VGroup(*[Dot([cx + dx, cy + dy, 0], radius=0.045, color="#ffffff") for dx, dy in pts])
    return VGroup(head_base(cx, cy), dots)


def meter(cx, cy, filled):
    bars = VGroup()
    for i in range(3):
        h = 0.16 + 0.14 * i
        b = Rectangle(width=0.14, height=h).move_to([cx - 0.24 + 0.24 * i, cy - 0.24 + h / 2, 0])
        b.set_stroke(INK_GHOST, 1.2).set_fill("#ffffff" if i < filled else INK, 0.95 if i < filled else 0.04)
        bars.add(b)
    return bars


def word(t, cx, cy, c=INK):
    return mono(t, 22, c).move_to([cx, cy, 0])


class Landscape(Scene):
    def construct(self):
        seed()

        title = mono("three ways to read speech from the body", 26, INK_FAINT).to_edge(UP, buff=0.4)

        heads = [("brain implant", "in the brain"),
                 ("scalp cap", "EEG / MEG"),
                 ("skin sensors", "surface EMG")]
        icons = [implant_icon, cap_icon, skin_icon]
        col_head = VGroup()
        col_icon = VGroup()
        for cx, (h, sub), mk in zip(COLX, heads, icons):
            ht = mono(h, 23, INK).move_to([cx, 2.75, 0])
            st = mono(sub, 15, INK_FAINT).move_to([cx, 2.4, 0])
            col_head.add(VGroup(ht, st))
            col_icon.add(mk(cx, ICON_Y))

        labels = ["surgery", "signal", "movement", "safety"]
        rlabels = VGroup(*[mono(l, 21, INK_DIM).move_to([LABX, y, 0]).align_to([-5.05, 0, 0], RIGHT)
                           for l, y in zip(labels, ROWY)])
        sep = Line([LABX - 0.9, 2.18, 0], [6.4, 2.18, 0], stroke_color=INK_GHOST, stroke_width=1)

        # ---- BEAT 1: DOORS ----------------------------------------------
        self.next_section("doors")
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in col_head], lag_ratio=0.15, run_time=0.8),
                  LaggedStart(*[GrowFromCenter(ic) for ic in col_icon], lag_ratio=0.15, run_time=0.9))
        self.play(Create(sep), LaggedStart(*[FadeIn(r) for r in rlabels], lag_ratio=0.1), run_time=0.7)
        self.wait(0.3)

        # cells[col] = (surgery, meter, movement, safety)
        cells = [
            (word("yes", COLX[0], ROWY[0], INK), meter(COLX[0], ROWY[1], 3),
             word("no", COLX[0], ROWY[2], INK_DIM), word("risk", COLX[0], ROWY[3], INK)),
            (word("no", COLX[1], ROWY[0], INK_DIM), meter(COLX[1], ROWY[1], 1),
             word("no", COLX[1], ROWY[2], INK_DIM), word("safe", COLX[1], ROWY[3], INK_DIM)),
            (word("no", COLX[2], ROWY[0], INK_DIM), meter(COLX[2], ROWY[1], 3),
             word("yes", COLX[2], ROWY[2], INK), word("safe", COLX[2], ROWY[3], INK)),
        ]

        def reveal(col):
            s, m, mv, sf = cells[col]
            self.play(FadeIn(s, shift=UP * 0.05),
                      LaggedStart(*[GrowFromEdge(b, DOWN) for b in m], lag_ratio=0.12),
                      FadeIn(mv, shift=UP * 0.05), FadeIn(sf, shift=UP * 0.05), run_time=0.75)

        # ---- BEAT 2: INVASIVE -------------------------------------------
        self.next_section("invasive")
        self.play(Indicate(col_icon[0], scale_factor=1.1, color=WHITE), run_time=0.4)
        reveal(0)
        note0 = mono("strongest signal, works without movement — but open-skull surgery", 19, INK_FAINT).move_to([0, -3.35, 0])
        self.play(FadeIn(note0), run_time=0.4)
        self.wait(0.3)

        # ---- BEAT 3: SCALP ----------------------------------------------
        self.next_section("scalp")
        self.play(Indicate(col_icon[1], scale_factor=1.1, color=WHITE), FadeOut(note0), run_time=0.4)
        reveal(1)
        note1 = mono("no surgery — but the skull blurs it; reading speech barely works", 19, INK_FAINT).move_to([0, -3.35, 0])
        self.play(FadeIn(note1), run_time=0.4)
        self.wait(0.3)

        # ---- BEAT 4: SKIN -----------------------------------------------
        self.next_section("skin")
        hl = RoundedRectangle(width=2.9, height=5.6, corner_radius=0.12).move_to([COLX[2], 0.35, 0])
        hl.set_stroke("#ffffff", 1.8, opacity=0.8).set_fill(INK, 0.05)
        self.play(FadeOut(note1), Create(hl), Indicate(col_icon[2], scale_factor=1.12, color=WHITE), run_time=0.5)
        reveal(2)
        tag = mono("implant-grade access to the speech muscles — without opening the skull", 21, INK)
        if tag.width > 12.6:
            tag.set_width(12.6)
        tag.move_to([0, -3.35, 0])
        self.play(FadeIn(tag, shift=UP * 0.1), run_time=0.6)
        self.wait(0.4)

        # ---- BEAT 5: CAVEAT — the honesty line (must be able to move) ----
        self.next_section("caveat")
        # contrast the movement row: the implant works WITHOUT movement (its edge
        # for the fully paralyzed); EMG needs movement (its one catch).
        self.play(FadeOut(tag),
                  Indicate(rlabels[2], scale_factor=1.18, color=WHITE),
                  cells[2][2].animate.set_color(WHITE),
                  run_time=0.5)
        caveat = VGroup(
            mono("the one catch: surface EMG needs movement", 21, INK),
            mono("not for the fully paralyzed — but the safe middle path for anyone who can move",
                 17, INK_FAINT),
        ).arrange(DOWN, buff=0.16).move_to([0, -3.25, 0])
        self.play(FadeIn(caveat, shift=UP * 0.1), run_time=0.6)
        self.wait(0.6)
