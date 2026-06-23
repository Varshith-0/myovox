# b02_every_pair_grid.py — "Everyone with everyone"  (bridge after features-cov)
#
# THE IDEA: the per-frame 31x31 covariance matrix is just the two-sensor "do
# these two move together?" test, TILED over every sensor pair. A round-robin
# tournament table — everyone versus everyone. Self-pairs sit on the diagonal
# (a sensor against itself = its own size); the off-diagonal cells carry the
# real story of who moved with whom. The grid is mirror-symmetric across the
# diagonal. The PATTERN of bright cells — not its overall loudness — names the
# sound.
#
# Three-zone full-canvas composition (pose -> build -> transform -> NAME):
#   TOP   (y ~ +3.0): context cap + the carried-over two-sensor cloud & value.
#   CENTER(-2.2..+2.4): the 31x31 lattice grows out of one glowing cell; a
#         scan-head walks the rows filling it (static-then-reveal); diagonal
#         lights brightest; a fold-line shows top-right mirrors bottom-left.
#   BOTTOM(-3.5): a dim 'loudness' bar (barely moves) vs the pattern that
#         flips between two gestures; resolves to the NAME.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# Geometry — keep everything well inside x in [-7,7], y in [-3.9,3.9].
GRID_N = 31                 # the real matrix size
SHOW_N = 16                 # legible stand-in tiling (16x16 reads as "a full grid")
CELL = 0.205                # cell side for the SHOW_N grid
GRID_C = np.array([-1.55, 0.05, 0])   # centre of the lattice in the canvas
TOP_Y = 3.18


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


def grid_of(vals, c=CELL, at=GRID_C):
    """A VGroup of square cells, fill_opacity = matrix value. row i, col j."""
    n = vals.shape[0]
    g = VGroup()
    for i in range(n):
        for j in range(n):
            sq = Square(c, stroke_width=0, fill_color=INK,
                        fill_opacity=float(vals[i, j]))
            sq.move_to(at + np.array([(j - (n - 1) / 2) * c,
                                      ((n - 1) / 2 - i) * c, 0]))
            g.add(sq)
    return g


class EveryPairGrid(Scene):
    def construct(self):
        seed()
        patternA = covariance_pattern(0)
        patternB = covariance_pattern(11)

        # =================================================================
        # B0 — POSE: carry over the two-sensor cloud + its one value, then
        #      shrink that value into a single glowing cell.
        # =================================================================
        self.next_section("pose")

        cap = mono("EVERYONE WITH EVERYONE", 24, INK_DIM, w=BOLD).move_to([0, TOP_Y, 0])
        sub = mono("the two-sensor test, run for every pair", 16, INK_FAINT).move_to(
            [0, TOP_Y - 0.46, 0])
        rule = Line([-6.4, TOP_Y - 0.72, 0], [6.4, TOP_Y - 0.72, 0],
                    stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(cap, shift=DOWN * 0.12), run_time=0.4)
        self.play(FadeIn(sub), Create(rule), run_time=0.34)

        # The carried-over two-sensor cloud: a tilted scatter of dots (sensor A
        # vs sensor B co-vary), with its single covariance value beside it.
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
        val_tag = mono("do they agree?", 13, INK_FAINT).next_to(
            one_val, UP, buff=0.1)

        self.play(Create(ax), FadeIn(ax_a), FadeIn(ax_b),
                  LaggedStartMap(FadeIn, cloud, lag_ratio=0.03), run_time=0.6)
        self.play(FadeIn(pair_lbl, shift=UP * 0.06),
                  FadeIn(one_val, shift=DOWN * 0.06),
                  FadeIn(val_tag), run_time=0.45)

        # Shrink that one value into a single glowing cell.
        seed_cell = Square(0.5, stroke_width=1.4, stroke_color=INK,
                           fill_color=INK, fill_opacity=0.71).move_to(GRID_C)
        seed_glow = glow(seed_cell.copy())
        self.play(
            ReplacementTransform(one_val.copy(), seed_cell),
            FadeIn(seed_glow),
            VGroup(cloud, ax, ax_a, ax_b, pair_lbl, one_val, val_tag).animate.set_opacity(0.4),
            run_time=0.7)

        # =================================================================
        # B1 — BUILD: the cell drops into position (A,B) of an empty 16x16
        #      lattice; sensor dots line the top and left edges as axes.
        # =================================================================
        self.next_section("build")

        # Empty lattice of faint cell-outlines.
        lattice = VGroup()
        for i in range(SHOW_N):
            for j in range(SHOW_N):
                lattice.add(Square(CELL, stroke_width=0.7, stroke_color=INK_GHOST,
                                   fill_opacity=0).move_to(
                    GRID_C + np.array([(j - (SHOW_N - 1) / 2) * CELL,
                                       ((SHOW_N - 1) / 2 - i) * CELL, 0])))

        def cell_at(i, j):
            return GRID_C + np.array([(j - (SHOW_N - 1) / 2) * CELL,
                                      ((SHOW_N - 1) / 2 - i) * CELL, 0])

        # Position (A,B) — an arbitrary off-diagonal slot, e.g. row 2, col 6.
        ai, bj = 2, 6
        slot = cell_at(ai, bj)

        # 31 sensor dots along the top and left edges (axes of the round-robin).
        top_y = GRID_C[1] + (SHOW_N / 2) * CELL + 0.18
        left_x = GRID_C[0] - (SHOW_N / 2) * CELL - 0.18
        edge_xs = [cell_at(0, j)[0] for j in range(SHOW_N)]
        edge_ys = [cell_at(i, 0)[1] for i in range(SHOW_N)]
        top_dots = VGroup(*[Dot([x, top_y, 0], radius=0.032, color=INK_FAINT)
                            for x in edge_xs])
        left_dots = VGroup(*[Dot([left_x, y, 0], radius=0.032, color=INK_FAINT)
                             for y in edge_ys])
        axis_top = mono("31 sensors", 14, INK_FAINT).next_to(top_dots, UP, buff=0.12)
        axis_left = mono("31 sensors", 14, INK_FAINT).rotate(PI / 2).next_to(
            left_dots, LEFT, buff=0.12)

        self.play(LaggedStart(*[Create(c) for c in lattice], lag_ratio=0.0008,
                              run_time=0.7),
                  LaggedStartMap(FadeIn, top_dots, lag_ratio=0.015),
                  LaggedStartMap(FadeIn, left_dots, lag_ratio=0.015),
                  FadeIn(axis_top), FadeIn(axis_left),
                  run_time=0.8)

        # Highlight the matching A and B sensor dots and drop the seed cell in.
        a_mark = Dot([edge_xs[bj], top_y, 0], radius=0.05, color=INK)
        b_mark = Dot([left_x, edge_ys[ai], 0], radius=0.05, color=INK)
        guide = VGroup(
            DashedLine([edge_xs[bj], top_y - 0.06, 0], slot + UP * 0.1,
                       stroke_color=INK_GHOST, stroke_width=1.0, dash_length=0.05),
            DashedLine([left_x + 0.06, edge_ys[ai], 0], slot + LEFT * 0.1,
                       stroke_color=INK_GHOST, stroke_width=1.0, dash_length=0.05),
        )
        self.play(FadeIn(a_mark, scale=1.4), FadeIn(b_mark, scale=1.4),
                  Create(guide), run_time=0.4)
        target_cell = Square(CELL, stroke_width=0, fill_color=INK,
                             fill_opacity=0.71).move_to(slot)
        self.play(seed_cell.animate.move_to(slot).set(width=CELL),
                  seed_glow.animate.move_to(slot).scale(CELL / 0.5).set_opacity(0.3),
                  run_time=0.6)
        self.add(target_cell)
        self.remove(seed_cell)
        self.play(FadeOut(guide), FadeOut(seed_glow), run_time=0.3)

        # =================================================================
        # B2 — TRANSFORM: a scan-head walks the rows; cells fill in a
        #      deterministic static-then-reveal; the diagonal lights brightest.
        # =================================================================
        self.next_section("fill")

        # Build the full filled grid once (static), start hidden, reveal by row.
        full = grid_of(patternA)
        for c in full:
            c.set_opacity(0.0)
        self.add(full)

        scan_cap = mono("each cell : do these two move together?", 16, INK_FAINT)
        scan_cap.next_to(lattice, DOWN, buff=0.34).set_x(GRID_C[0])

        # A scan-head: a bright row-wide bar that walks top -> bottom.
        head = Rectangle(width=SHOW_N * CELL, height=CELL, stroke_width=0,
                         fill_color=INK, fill_opacity=0.14).move_to(cell_at(0, 0))
        head.set_x(GRID_C[0])
        self.play(FadeIn(scan_cap), FadeIn(head), run_time=0.34)

        # Reveal row by row. The already-placed (ai,bj) cell + its mirror are
        # already represented in `full`; fade target_cell as the head passes.
        for i in range(SHOW_N):
            row_cells = VGroup(*[full[i * SHOW_N + j] for j in range(SHOW_N)])
            real = [float(patternA[i, j]) for j in range(SHOW_N)]
            self.play(
                head.animate.move_to([GRID_C[0], cell_at(i, 0)[1], 0]),
                LaggedStart(*[c.animate.set_opacity(real[j])
                              for j, c in enumerate(row_cells)],
                            lag_ratio=0.04),
                run_time=0.12 if i not in (0, SHOW_N - 1) else 0.16,
                rate_func=linear)
            if i == ai:
                target_cell.set_opacity(0.0)

        self.remove(target_cell)
        self.play(FadeOut(head), run_time=0.2)

        # Brighten the diagonal: self-variance, "a sensor against itself".
        diag = VGroup(*[full[i * SHOW_N + i] for i in range(SHOW_N)])
        diag_glow = VGroup(*[
            Square(CELL, stroke_width=0, fill_color=WHITE, fill_opacity=0.0).move_to(
                cell_at(i, i)) for i in range(SHOW_N)])
        self.add(diag_glow)
        diag_lbl = mono("diagonal : a sensor vs itself", 14, INK_DIM)
        diag_lbl.next_to(lattice, RIGHT, buff=0.5).align_to(lattice, UP).shift(DOWN * 0.2)
        self.play(
            *[c.animate.set_opacity(1.0) for c in diag],
            *[g.animate.set_opacity(0.18) for g in diag_glow],
            FadeIn(diag_lbl, shift=LEFT * 0.1),
            run_time=0.55)

        # Fold-line across the diagonal: top-right mirrors bottom-left.
        tl = cell_at(0, 0) + np.array([-CELL / 2, CELL / 2, 0])
        br = cell_at(SHOW_N - 1, SHOW_N - 1) + np.array([CELL / 2, -CELL / 2, 0])
        fold = DashedLine(tl, br, stroke_color=INK, stroke_width=1.6,
                          dash_length=0.08)
        mirror_lbl = mono("symmetric : top-right mirrors bottom-left", 14, INK_DIM)
        mirror_lbl.next_to(diag_lbl, DOWN, buff=0.16).align_to(diag_lbl, LEFT)
        # two mirrored example cells flash.
        ex1 = SurroundingRectangle(full[2 * SHOW_N + 11], color=WHITE, buff=0.0,
                                   stroke_width=2.0)
        ex2 = SurroundingRectangle(full[11 * SHOW_N + 2], color=WHITE, buff=0.0,
                                   stroke_width=2.0)
        self.play(Create(fold), FadeIn(mirror_lbl, shift=LEFT * 0.1), run_time=0.5)
        self.play(Create(ex1), Create(ex2), run_time=0.35)
        self.play(FadeOut(ex1), FadeOut(ex2), run_time=0.3)

        # =================================================================
        # B3 — TWO GESTURES: cross-fade A -> B. The pattern clearly changes,
        #      while a dim 'loudness' bar barely moves. Pattern, not volume.
        # =================================================================
        self.next_section("two_gestures")

        # Bottom loudness bar (overall energy) — present, but it barely shifts.
        BY = -3.4
        loud_track = RoundedRectangle(width=3.4, height=0.2, corner_radius=0.05,
                                      stroke_color=INK_GHOST, stroke_width=1.0,
                                      fill_opacity=0).move_to([3.2, BY, 0])
        loud_fill = Rectangle(width=3.4 * 0.62, height=0.2, stroke_width=0,
                              fill_color=INK_FAINT, fill_opacity=0.5)
        loud_fill.align_to(loud_track, LEFT).set_y(BY)
        loud_lbl = mono("loudness", 13, INK_FAINT).next_to(loud_track, LEFT, buff=0.2)
        gesture_lbl = mono("gesture 1", 16, INK).move_to([-3.2, BY, 0])

        self.play(FadeOut(diag_lbl), FadeOut(mirror_lbl),
                  Create(loud_track), FadeIn(loud_fill), FadeIn(loud_lbl),
                  FadeIn(gesture_lbl), run_time=0.45)

        # Build pattern B grid (static) at the same place, hidden.
        fullB = grid_of(patternB)
        for c in fullB:
            c.set_opacity(0.0)
        self.add(fullB)
        diagB = VGroup(*[fullB[i * SHOW_N + i] for i in range(SHOW_N)])

        gesture2 = mono("gesture 2", 16, INK).move_to([-3.2, BY, 0])
        # cross-fade: pattern flips a lot; loudness nudges a hair.
        self.play(
            *[full[k].animate.set_opacity(0.0) for k in range(SHOW_N * SHOW_N)],
            *[fullB[k].animate.set_opacity(float(patternB[k // SHOW_N, k % SHOW_N]))
              for k in range(SHOW_N * SHOW_N)],
            *[c.animate.set_opacity(1.0) for c in diagB],
            loud_fill.animate.stretch_to_fit_width(3.4 * 0.66).align_to(
                loud_track, LEFT),
            ReplacementTransform(gesture_lbl, gesture2),
            run_time=0.8)
        loud_fill.align_to(loud_track, LEFT)
        # snap back to gesture 1 to show the contrast again, quickly.
        gesture1b = mono("gesture 1", 16, INK).move_to([-3.2, BY, 0])
        self.play(
            *[fullB[k].animate.set_opacity(0.0) for k in range(SHOW_N * SHOW_N)],
            *[full[k].animate.set_opacity(float(patternA[k // SHOW_N, k % SHOW_N]))
              for k in range(SHOW_N * SHOW_N)],
            loud_fill.animate.stretch_to_fit_width(3.4 * 0.62).align_to(
                loud_track, LEFT),
            ReplacementTransform(gesture2, gesture1b),
            run_time=0.55)
        loud_fill.align_to(loud_track, LEFT)
        contrast = mono("the pattern names the sound — not the volume", 15, INK_DIM)
        contrast.move_to([0, BY - 0.42, 0])
        self.play(FadeIn(contrast, shift=UP * 0.06), run_time=0.4)

        # =================================================================
        # B4 — NAME + POSTER HOLD.
        # =================================================================
        self.next_section("name")

        # Clear the loudness strip's clutter; let the grid + name own the frame.
        size_line = mono("31 x 31  ·  one snapshot", 22, INK_DIM).move_to([3.55, 1.6, 0])
        portrait = serif("a portrait", 46, WHITE).move_to([3.55, 0.7, 0])
        portrait_g = glow(portrait)
        sub2 = mono("of how the face moved together, this instant", 14, INK_FAINT)
        sub2.next_to(portrait, DOWN, buff=0.22)

        box = SurroundingRectangle(lattice, color=INK_FAINT, buff=0.06,
                                   stroke_width=1.4)
        self.add(portrait_g)
        self.play(
            FadeIn(size_line, shift=DOWN * 0.08),
            GrowFromCenter(portrait),
            FadeIn(sub2),
            Create(box),
            FadeIn(a_mark.copy()),  # keep edge marks crisp
            run_time=0.6)
        self.wait(0.6)
