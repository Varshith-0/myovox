# b02_every_pair_grid.py — "Everyone with everyone"  (bridge after features-cov)
#
# THE IDEA: the per-frame 31x31 covariance matrix is just the two-sensor "do
# these two move together?" test, TILED over every sensor pair. Ask the same
# question of every pair; drop each answer into its slot; sweep the table full.
# Self-pairs sit on the diagonal (a sensor against itself = its own size); the
# off-diagonal cells carry the real story of who moved with whom, mirror-
# symmetric across the diagonal. One snapshot of the face -> one whole grid.
#
# Locked 8-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 one number   (1.08) dim tilted A-vs-B scatter cloud + value 0.71 at left.
#   2 but 31       (0.63) 31 dots fan along top + left edges; "31 sensors".
#   3 every pair   (3.06) empty 16x16 lattice of faint outlines draws in centre.
#   4 each slot    (2.42) the glowing cell shrinks + travels dashed guides from
#                         the lit top dot & left dot into off-diagonal slot.
#   5 sweep        (1.25) a bright row-wide scan-head walks top->bottom; fills.
#   6 diagonal     (2.09) diagonal cells brighten white + glow; off-diag dim.
#   7 off-diagonal (1.74) diagonal dims back; two mirrored off-diag cells flash
#                         with outline boxes; fold-line shows the symmetry.
#   8 portrait     (1.31) all labels clear; box frames lattice; serif payoff
#                         "a portrait" / "31 x 31 · one snapshot" glows; hold.
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

# Geometry — keep everything well inside x in [-7,7], y in [-3.9,3.9].
SHOW_N = 16                 # legible stand-in tiling (16x16 reads as "a full grid")
CELL = 0.215               # cell side for the SHOW_N grid
GRID_C = np.array([0.35, 0.05, 0])   # centre of the lattice in the canvas


def covariance_pattern(seed_shift, n=SHOW_N):
    """A symmetric covariance-like matrix in [0,1]: bright diagonal (self-
    variance) plus an off-diagonal coordination pattern unique to a gesture."""
    rng = np.random.default_rng(7 + seed_shift)
    centres = rng.integers(0, n, size=4)        # a few co-active sensor clusters
    m = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            v = 0.0
            for c in centres:
                v += np.exp(-((i - c) ** 2 + (j - c) ** 2) / 7.0)
            m[i, j] = v
    m = m / m.max()
    np.fill_diagonal(m, 1.0)                     # self-variance brightest
    m = (m + m.T) / 2                            # enforce symmetry
    return np.clip(0.10 + 0.85 * m, 0.05, 1.0)


def cell_at(i, j):
    return GRID_C + np.array([(j - (SHOW_N - 1) / 2) * CELL,
                              ((SHOW_N - 1) / 2 - i) * CELL, 0])


def grid_of(vals):
    """A VGroup of square cells, fill_opacity = matrix value, indexed i*N + j."""
    g = VGroup()
    for i in range(SHOW_N):
        for j in range(SHOW_N):
            sq = Square(CELL, stroke_width=0, fill_color=INK,
                        fill_opacity=float(vals[i, j])).move_to(cell_at(i, j))
            g.add(sq)
    return g


class EveryPairGrid(Scene):
    def construct(self):
        seed()
        pattern = covariance_pattern(0)

        # =================================================================
        # BEAT 1 — ONE NUMBER (1.08s): the carried-over two-sensor scatter
        #          cloud + its single value 0.71, dim, alone at left.
        # =================================================================
        self.next_section("one_number")

        cloud_c = np.array([-4.6, 0.4, 0])
        rng = np.random.default_rng(3)
        t = rng.normal(0, 1, 26)
        pts = np.stack([t + rng.normal(0, 0.32, 26),
                        0.85 * t + rng.normal(0, 0.32, 26)], axis=1)
        cloud = VGroup(*[
            Dot(cloud_c + np.array([p[0] * 0.34, p[1] * 0.34, 0]),
                radius=0.045, color=INK, fill_opacity=0.85)
            for p in pts
        ])
        ax = VGroup(
            Line(cloud_c + LEFT * 0.95, cloud_c + RIGHT * 0.95,
                 stroke_color=INK_GHOST, stroke_width=1.2),
            Line(cloud_c + DOWN * 0.95, cloud_c + UP * 0.95,
                 stroke_color=INK_GHOST, stroke_width=1.2),
        )
        ax_a = mono("A", 14, INK_FAINT).next_to(ax[0], RIGHT, buff=0.1)
        ax_b = mono("B", 14, INK_FAINT).next_to(ax[1], UP, buff=0.1)
        pair_lbl = mono("sensors A · B", 15, INK_DIM).next_to(
            VGroup(ax, cloud), DOWN, buff=0.22)
        one_val = num("0.71", 30, INK).next_to(VGroup(ax, cloud), UP, buff=0.26)
        cloud_grp = VGroup(ax, ax_a, ax_b, cloud, pair_lbl, one_val)

        self.play(Create(ax), FadeIn(ax_a), FadeIn(ax_b),
                  LaggedStart(*[FadeIn(d) for d in cloud], lag_ratio=0.03),
                  run_time=0.55)
        self.play(FadeIn(pair_lbl, shift=UP * 0.06),
                  FadeIn(one_val, shift=DOWN * 0.06), run_time=0.4)

        # =================================================================
        # BEAT 2 — BUT 31 (0.63s): 31 sensor dots fan along the top & left
        #          edges; the lone pair feels tiny. Dim the cloud.
        # =================================================================
        self.next_section("but_31")

        top_y = GRID_C[1] + (SHOW_N / 2) * CELL + 0.20
        left_x = GRID_C[0] - (SHOW_N / 2) * CELL - 0.20
        edge_xs = [cell_at(0, j)[0] for j in range(SHOW_N)]
        edge_ys = [cell_at(i, 0)[1] for i in range(SHOW_N)]
        top_dots = VGroup(*[Dot([x, top_y, 0], radius=0.034, color=INK_FAINT)
                            for x in edge_xs])
        left_dots = VGroup(*[Dot([left_x, y, 0], radius=0.034, color=INK_FAINT)
                             for y in edge_ys])
        axis_top = mono("31 sensors", 14, INK_FAINT).next_to(top_dots, UP, buff=0.14)
        axis_left = mono("31 sensors", 14, INK_FAINT).rotate(PI / 2).next_to(
            left_dots, LEFT, buff=0.14)

        self.play(
            cloud_grp.animate.set_opacity(0.32),
            LaggedStart(*[FadeIn(d, scale=1.3) for d in top_dots], lag_ratio=0.012),
            LaggedStart(*[FadeIn(d, scale=1.3) for d in left_dots], lag_ratio=0.012),
            FadeIn(axis_top), FadeIn(axis_left),
            run_time=0.6,
        )

        # =================================================================
        # BEAT 3 — EVERY PAIR (3.06s): empty 16x16 lattice of faint
        #          cell-outlines draws in across the centre.
        # =================================================================
        self.next_section("every_pair")

        lattice = VGroup()
        for i in range(SHOW_N):
            for j in range(SHOW_N):
                lattice.add(Square(CELL, stroke_width=0.7, stroke_color=INK_GHOST,
                                   fill_opacity=0).move_to(cell_at(i, j)))

        ask_cap = mono("the same question, for every pair", 16, INK_FAINT)
        ask_cap.next_to(lattice, DOWN, buff=0.34).set_x(GRID_C[0])

        self.play(
            LaggedStart(*[Create(c) for c in lattice], lag_ratio=0.0012),
            run_time=2.4,
        )
        self.play(FadeIn(ask_cap), run_time=0.45)
        self.wait(0.2)

        # =================================================================
        # BEAT 4 — EACH SLOT (2.42s): the glowing cell shrinks and travels
        #          along dashed guides from the lit top dot & left dot into
        #          its off-diagonal slot (row 2, col 6).
        # =================================================================
        self.next_section("each_slot")

        ai, bj = 2, 6
        slot = cell_at(ai, bj)

        # The single covariance answer, as a glowing cell, born from the value.
        seed_cell = Square(0.5, stroke_width=1.4, stroke_color=INK,
                           fill_color=INK, fill_opacity=0.71).move_to(cloud_c)
        seed_glow = glow(seed_cell.copy())
        self.play(
            ReplacementTransform(one_val.copy(), seed_cell),
            FadeIn(seed_glow),
            FadeOut(ask_cap),
            run_time=0.5)

        # light the matching top (col) and left (row) sensor dots + guides.
        a_mark = Dot([edge_xs[bj], top_y, 0], radius=0.055, color=INK)
        b_mark = Dot([left_x, edge_ys[ai], 0], radius=0.055, color=INK)
        guide = VGroup(
            DashedLine([edge_xs[bj], top_y - 0.07, 0], slot + UP * 0.1,
                       stroke_color=INK_FAINT, stroke_width=1.0, dash_length=0.05),
            DashedLine([left_x + 0.07, edge_ys[ai], 0], slot + LEFT * 0.1,
                       stroke_color=INK_FAINT, stroke_width=1.0, dash_length=0.05),
        )
        self.play(FadeIn(a_mark, scale=1.4), FadeIn(b_mark, scale=1.4),
                  run_time=0.45)
        self.play(Create(guide), run_time=0.5)

        # travel the seed cell into the slot, shrinking to cell size.
        target_cell = Square(CELL, stroke_width=0, fill_color=INK,
                             fill_opacity=0.71).move_to(slot)
        self.play(seed_cell.animate.move_to(slot).set(width=CELL),
                  seed_glow.animate.move_to(slot).scale(CELL / 0.5).set_opacity(0.3),
                  run_time=0.65)
        self.add(target_cell)
        self.remove(seed_cell)
        self.play(FadeOut(guide), FadeOut(seed_glow), run_time=0.3)

        # =================================================================
        # BEAT 5 — SWEEP (1.25s): a bright row-wide scan-head walks top to
        #          bottom; the table fills row by row in one continuous pass.
        # =================================================================
        self.next_section("sweep")

        full = grid_of(pattern)
        for c in full:
            c.set_opacity(0.0)
        self.add(full)

        head = Rectangle(width=SHOW_N * CELL + 0.06, height=CELL, stroke_width=0,
                         fill_color=INK, fill_opacity=0.16).move_to(cell_at(0, 0))
        head.set_x(GRID_C[0])
        self.play(a_mark.animate.set_opacity(0.0), b_mark.animate.set_opacity(0.0),
                  FadeIn(head), run_time=0.12)

        for i in range(SHOW_N):
            row_cells = VGroup(*[full[i * SHOW_N + j] for j in range(SHOW_N)])
            real = [float(pattern[i, j]) for j in range(SHOW_N)]
            self.play(
                head.animate.move_to([GRID_C[0], cell_at(i, 0)[1], 0]),
                LaggedStart(*[c.animate.set_opacity(real[j])
                              for j, c in enumerate(row_cells)],
                            lag_ratio=0.03),
                run_time=0.062, rate_func=linear)
            if i == ai:
                target_cell.set_opacity(0.0)

        self.remove(target_cell)
        self.play(FadeOut(head), run_time=0.18)

        # =================================================================
        # BEAT 6 — DIAGONAL (2.09s): a sensor meets itself; diagonal cells
        #          brighten to white + glow; off-diagonal dims slightly.
        # =================================================================
        self.next_section("diagonal")

        diag = VGroup(*[full[i * SHOW_N + i] for i in range(SHOW_N)])
        off_diag = VGroup(*[full[i * SHOW_N + j]
                            for i in range(SHOW_N) for j in range(SHOW_N) if i != j])
        diag_glow = VGroup(*[
            Square(CELL, stroke_width=0, fill_color=WHITE, fill_opacity=0.0).move_to(
                cell_at(i, i)) for i in range(SHOW_N)])
        self.add(diag_glow)
        diag_lbl = mono("a sensor meets itself", 15, INK_DIM)
        diag_lbl.next_to(lattice, DOWN, buff=0.34).set_x(GRID_C[0])
        self.play(
            *[c.animate.set_fill(WHITE, 1.0) for c in diag],
            *[g.animate.set_opacity(0.16) for g in diag_glow],
            off_diag.animate.set_opacity(0.55),
            FadeIn(diag_lbl, shift=UP * 0.08),
            run_time=0.9)
        self.wait(1.0)

        # =================================================================
        # BEAT 7 — OFF-DIAGONAL (1.74s): diagonal dims back; two mirrored
        #          off-diagonal cells flash with outline boxes; fold-line.
        # =================================================================
        self.next_section("off_diagonal")

        off_lbl = mono("these tell who moved with whom", 15, INK_DIM)
        off_lbl.move_to(diag_lbl)
        self.play(
            *[c.animate.set_fill(INK, float(pattern[k, k])) for k, c in enumerate(diag)],
            *[g.animate.set_opacity(0.0) for g in diag_glow],
            off_diag.animate.set_opacity(1.0),
            ReplacementTransform(diag_lbl, off_lbl),
            run_time=0.5)
        self.remove(diag_glow)

        tl = cell_at(0, 0) + np.array([-CELL / 2, CELL / 2, 0])
        br = cell_at(SHOW_N - 1, SHOW_N - 1) + np.array([CELL / 2, -CELL / 2, 0])
        fold = DashedLine(tl, br, stroke_color=INK_FAINT, stroke_width=1.4,
                          dash_length=0.08)
        ex1 = SurroundingRectangle(full[2 * SHOW_N + 11], color=WHITE, buff=0.0,
                                   stroke_width=2.2)
        ex2 = SurroundingRectangle(full[11 * SHOW_N + 2], color=WHITE, buff=0.0,
                                   stroke_width=2.2)
        self.play(Create(fold), run_time=0.45)
        self.play(Create(ex1), Create(ex2), run_time=0.4)
        self.wait(0.35)

        # =================================================================
        # BEAT 8 — PORTRAIT (1.31s): all labels clear; a box frames the
        #          lattice; serif #fff payoff glows; brief poster hold.
        # =================================================================
        self.next_section("portrait")

        box = SurroundingRectangle(lattice, color=INK_FAINT, buff=0.08,
                                   stroke_width=1.4)
        size_line = mono("31 x 31  ·  one snapshot", 20, INK_DIM).move_to([-4.4, 1.5, 0])
        portrait = serif("a portrait", 44, WHITE).move_to([-4.4, 0.6, 0])
        portrait_g = glow(portrait)

        self.play(
            FadeOut(ex1), FadeOut(ex2), FadeOut(fold), FadeOut(off_lbl),
            FadeOut(axis_top), FadeOut(axis_left),
            FadeOut(top_dots), FadeOut(left_dots),
            FadeOut(cloud_grp),
            run_time=0.45)
        self.add(portrait_g)
        self.play(
            Create(box),
            GrowFromCenter(portrait),
            FadeIn(size_line, shift=DOWN * 0.08),
            run_time=0.55)
        self.play(Indicate(portrait, scale_factor=1.08, color=WHITE),
                  portrait_g.animate.set_opacity(0.0), run_time=0.3)
        self.remove(portrait_g)
        self.wait(0.35)
