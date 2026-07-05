# S08 — Coordination (covariance).
# Beat sheet (locked, ~12s):
#   B0  hold the ONE bright pair-(7,18) cell carried from b01: value 0.9, rest dark.
#   B1  a vast empty 31x31 grid outline ghosts in around it; the lone cell dims —
#       "one pair can't tell two sounds apart" (the motivating tension).
#   B2  the lone cell flows into its slot and the full 31x31 matrix paints itself
#       in a diagonal sweep while a bottom counter races 1 -> 961.
#   B3  a row-band + col-band cross at one off-diagonal cell (naming two sensors),
#       it flashes; then the bright self-diagonal lights (each sensor with itself).
#   B4  bands clear; the whole matrix is spotlighted as ONE object; bottom locks to
#       "31 x 31 = 961 numbers · one matrix per snapshot".
#   B5  matrix shrinks left as gesture "AE"; a visibly different matrix fades in
#       right as gesture "S"; a weak->strong legend appears; bottom resolves to the
#       serif payoff "each sound = its own pattern of coordination".
# Strict monochrome on #050505. One focal object per beat; everything else dims.
from manim import *
from style import *
import numpy as np

N = 31  # 31 channels -> 31x31 covariance
BOT_Y = -3.2


def cov_matrix(gesture):
    """A plausible SPD coordination matrix in [0,1] with visible block structure and
    a clean BRIGHT diagonal. Brightness = strength of co-movement (|correlation|)."""
    rng = np.random.default_rng(100 + gesture)
    F = rng.standard_normal((N, 3)) * (1.0 + 0.5 * rng.standard_normal((N, 1)))
    for _ in range(2):
        idx = rng.choice(N, size=rng.integers(5, 9), replace=False)
        v = rng.standard_normal(3)
        F[idx] += 1.6 * v
    C = F @ F.T
    d = np.sqrt(np.clip(np.diag(C), 1e-6, None))
    C = C / np.outer(d, d)        # normalize -> correlation, diag = 1
    M = np.abs(C) ** 1.3          # brightness = strength of co-movement
    np.fill_diagonal(M, 1.0)
    return M


class Coordination(Scene):
    def construct(self):
        seed()
        SIDE = 4.4
        cw = SIDE / N

        # ============================================================
        # BEAT 0 — hold the ONE bright cell carried over from b01 (~1.87s)
        # ============================================================
        cell = Square(1.3, stroke_width=0, fill_color=INK, fill_opacity=0.9)
        cell.move_to(ORIGIN)
        cell_glow = glow(cell.copy().set_fill(opacity=0))
        val = num("0.9", 40, BG).move_to(cell)
        cell_lbl = mono("pair (7, 18)", 22, INK_DIM).next_to(cell, UP, buff=0.3)
        sub = mono("one number  ·  how together they move", 19, INK_FAINT)
        sub.next_to(cell, DOWN, buff=0.4)

        self.play(FadeIn(cell_glow), FadeIn(cell),
                  FadeIn(val), FadeIn(cell_lbl, shift=DOWN * 0.08), run_time=0.7)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.4)
        self.wait(0.55)

        # ============================================================
        # BEAT 1 — TENSION: the lone cell is tiny in an empty grid (~1.21s)
        # ============================================================
        grid = self.make_heatmap(cov_matrix(0), SIDE).move_to(ORIGIN)
        outline = SurroundingRectangle(grid, color=INK_GHOST, stroke_width=1.8,
                                       buff=0.05)
        # faint empty lattice (column + row rules) to feel the vastness
        lattice = VGroup()
        for k in range(N + 1):
            x = grid.get_left()[0] + k * cw
            y = grid.get_top()[1] - k * cw
            lattice.add(Line([x, grid.get_bottom()[1], 0],
                             [x, grid.get_top()[1], 0],
                             stroke_color=INK_GHOST, stroke_width=0.5))
            lattice.add(Line([grid.get_left()[0], y, 0],
                             [grid.get_right()[0], y, 0],
                             stroke_color=INK_GHOST, stroke_width=0.5))

        need = mono("one pair can't tell two sounds apart", 21, INK_DIM)
        need.move_to([0, BOT_Y, 0])

        self.play(FadeOut(sub), FadeOut(val), FadeOut(cell_lbl),
                  Create(outline), FadeIn(lattice), run_time=0.55)
        # shrink + dim the lone cell so its smallness is felt
        self.play(cell.animate.scale(cw / 1.3).set_fill(opacity=0.5),
                  cell_glow.animate.set_opacity(0.0),
                  FadeIn(need, shift=UP * 0.06), run_time=0.55)
        self.remove(cell_glow)

        # ============================================================
        # BEAT 2 — PROMOTE: the lone cell flows in; matrix paints; 1 -> 961 (~2.63s)
        # ============================================================
        cell_target = grid[6 * N + 17]   # land it at pair (6,17) off-diagonal slot
        self.play(cell.animate.move_to(cell_target.get_center())
                  .set_width(cw).set_fill(opacity=cell_target._target_op),
                  FadeOut(need), run_time=0.55)
        self.remove(cell)
        grid[6 * N + 17].set_opacity(grid[6 * N + 17]._target_op)
        self.add(grid)

        order = sorted(range(N * N), key=lambda k: (k // N) + (k % N))
        cells_in_order = VGroup(*[grid[k] for k in order])

        pairs = ValueTracker(1)
        counter_mob = num("pairs measured:  1", 24, INK).move_to([0, BOT_Y, 0])
        counter_mob.add_updater(
            lambda m: m.become(num(
                f"pairs measured:  {int(round(pairs.get_value()))}", 24, INK)
                .move_to([0, BOT_Y, 0])))
        self.add(counter_mob)

        self.play(
            LaggedStart(*[c.animate.set_opacity(c._target_op)
                          for c in cells_in_order], lag_ratio=0.0022),
            pairs.animate.set_value(961),
            FadeOut(lattice),
            run_time=1.8)
        counter_mob.clear_updaters()
        counter_mob.become(num("pairs measured:  961", 24, INK)
                           .move_to([0, BOT_Y, 0]))
        self.wait(0.28)

        # ============================================================
        # BEAT 3 — name a pair (crosshair) then light the diagonal (~1.60s)
        # ============================================================
        ri, cj = 6, 17
        row_band = self.band(grid, "row", ri, cw)
        col_band = self.band(grid, "col", cj, cw)
        hit = grid[ri * N + cj]
        crosslbl = mono("these two sensors\nmoved as a team", 19, INK_DIM)
        crosslbl.next_to(grid, RIGHT, buff=0.55).shift(UP * 1.0)
        self.play(FadeIn(row_band), FadeIn(col_band),
                  FadeIn(crosslbl, shift=RIGHT * 0.08), run_time=0.4)
        self.play(Indicate(hit, color="#ffffff", scale_factor=1.0), run_time=0.35)
        self.play(FadeOut(row_band), FadeOut(col_band), FadeOut(crosslbl),
                  run_time=0.25)

        diag_cells = VGroup(*[grid[i * N + i] for i in range(N)])
        diag_glow = VGroup(*[c.copy().set_stroke("#ffffff", width=4, opacity=0.10)
                             for c in diag_cells])
        dlabel = mono("each sensor\nwith itself", 19, INK_DIM)
        dlabel.next_to(grid, RIGHT, buff=0.55).shift(DOWN * 0.6)
        self.add(diag_glow)
        self.play(diag_cells.animate.set_fill("#ffffff", opacity=1.0),
                  FadeIn(diag_glow), FadeIn(dlabel),
                  Indicate(diag_cells, color="#ffffff", scale_factor=1.0),
                  run_time=0.6)

        # ============================================================
        # BEAT 4 — the whole grid is the snapshot's signature (~2.34s)
        # ============================================================
        frame1 = SurroundingRectangle(grid, color=INK_GHOST, stroke_width=2,
                                      buff=0.05)
        sig = mono("this snapshot's signature  ·  which muscles pulled together",
                   19, INK_DIM).next_to(grid, UP, buff=0.32)
        self.play(FadeOut(dlabel), ReplacementTransform(outline, frame1),
                  FadeIn(sig, shift=DOWN * 0.06),
                  Indicate(grid, color=INK, scale_factor=1.02), run_time=0.7)

        lock = mono("31 x 31  =  961 numbers   ·   one matrix per snapshot",
                    22, INK).move_to([0, BOT_Y, 0])
        self.play(ReplacementTransform(counter_mob, lock), run_time=0.55)
        self.wait(0.85)

        # ============================================================
        # BEAT 5 — two gestures, two patterns + payoff (~2.32s)
        # ============================================================
        m1_group = VGroup(grid, frame1, diag_glow)
        self.play(FadeOut(sig),
                  m1_group.animate.scale(0.62).move_to(LEFT * 3.5 + UP * 0.15),
                  run_time=0.6)

        grid2 = self.make_heatmap(cov_matrix(5), SIDE * 0.62)
        grid2.move_to(RIGHT * 3.5 + UP * 0.15)
        for c in grid2:
            c.set_opacity(c._target_op)
        diag2 = VGroup(*[grid2[i * N + i] for i in range(N)])
        diag2.set_fill("#ffffff", opacity=1.0)
        diag2_glow = VGroup(*[c.copy().set_stroke("#ffffff", width=3, opacity=0.10)
                              for c in diag2])
        frame2 = SurroundingRectangle(grid2, color=INK_GHOST, stroke_width=1.6,
                                      buff=0.05)

        g1lbl = serif('gesture  "AE"', 24, INK_DIM).next_to(grid, UP, buff=0.3)
        g2lbl = serif('gesture  "S"', 24, INK_DIM).next_to(grid2, UP, buff=0.3)
        self.play(FadeIn(g1lbl),
                  FadeIn(VGroup(grid2, diag2_glow, frame2), shift=LEFT * 0.2),
                  FadeIn(g2lbl), run_time=0.7)

        legend = self.legend_bar().scale(0.9).move_to([0, -2.4, 0])
        self.play(Indicate(grid, color="#ffffff", scale_factor=1.0),
                  Indicate(grid2, color="#ffffff", scale_factor=1.0),
                  FadeIn(legend), run_time=0.55)

        punch = serif("each sound = its own pattern of coordination", 27, INK)
        punch.move_to([0, BOT_Y, 0])
        self.play(ReplacementTransform(lock, punch), run_time=0.6)
        self.wait(0.55)

    # ----- helpers --------------------------------------------------------
    def make_heatmap(self, M, side=4.4):
        """A VGroup of N*N squares; brightness (fill opacity) = M value.
        Each cell stores its target opacity on ._target_op and starts at 0."""
        cell = side / N
        grid = VGroup()
        for i in range(N):
            for j in range(N):
                op = float(np.clip(M[i, j], 0.03, 1.0))
                sq = Square(cell, stroke_width=0, fill_color=INK, fill_opacity=0.0)
                sq._target_op = op
                sq.move_to([(j - (N - 1) / 2) * cell,
                            ((N - 1) / 2 - i) * cell, 0])
                grid.add(sq)
        grid.move_to(ORIGIN)
        return grid

    def band(self, grid, kind, k, cell):
        """A translucent highlight band over a whole row or column of the heatmap."""
        side = cell * N
        if kind == "row":
            y = grid.get_top()[1] - (k + 0.5) * cell
            r = Rectangle(width=side, height=cell, stroke_width=0,
                          fill_color="#ffffff", fill_opacity=0.18)
            r.move_to([grid.get_center()[0], y, 0])
        else:
            x = grid.get_left()[0] + (k + 0.5) * cell
            r = Rectangle(width=cell, height=side, stroke_width=0,
                          fill_color="#ffffff", fill_opacity=0.18)
            r.move_to([x, grid.get_center()[1], 0])
        return r

    def legend_bar(self):
        """A horizontal faint->bright strip with end labels (LaTeX-free)."""
        n = 22
        w = 0.16
        bars = VGroup()
        for i in range(n):
            op = 0.05 + 0.95 * (i / (n - 1))
            bars.add(Square(w, stroke_width=0, fill_color=INK, fill_opacity=op))
        bars.arrange(RIGHT, buff=0.0)
        left = mono("weak", 18, INK_FAINT).next_to(bars, LEFT, buff=0.3)
        right = mono("strong co-movement", 18, INK_DIM).next_to(bars, RIGHT, buff=0.3)
        frame = SurroundingRectangle(bars, color=INK_GHOST, stroke_width=1.2, buff=0.0)
        return VGroup(bars, frame, left, right)
