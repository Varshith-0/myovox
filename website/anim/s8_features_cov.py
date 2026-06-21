# S08 — Coordination (covariance).
# Goal: we record WHICH sensors move together (coordination), not how strong each is.
# We earn the idea on TWO channels (a pulse sweeps both, they rise & fall in lock-step,
# feeding ONE bright "togetherness" cell), then PROMOTE it: that single cell grows into
# a full 31x31 coordination matrix that fills the center, with a bright self-diagonal and
# visible muscle-group blocks, while a bottom counter races "pairs measured: 1 -> 961".
# Finale: two gestures produce two visibly different matrices -> "each sound = its own
# pattern of coordination."  Whole-frame sandwich: ghost frame-ruler context strip on top,
# matrix mechanism in center, running tally/legend/punchline on the bottom.
# Ground truth: 31x31 covariance (SPD), vec(E) = 961-dim; coordination, not amplitude.
from manim import *
from emg_style import *
import numpy as np

N = 31  # 31 channels -> 31x31 covariance


def wave(seed_n, n=48):
    """A short EMG-like snippet as a normalized 1-D signal."""
    rng = np.random.default_rng(seed_n)
    t = np.linspace(0, 1, n)
    s = (np.sin(2 * np.pi * (1.3 + 0.7 * rng.random()) * t + rng.random() * 6)
         + 0.5 * np.sin(2 * np.pi * (3.1 + rng.random()) * t + rng.random() * 6)
         + 0.18 * rng.standard_normal(n))
    s = s - s.mean()
    s = s / (np.abs(s).max() + 1e-6)
    return s


def snippet_curve(sig, w=3.0, h=1.0, c=INK, sw=2.6):
    pts = [np.array([x, y, 0]) for x, y in
           zip(np.linspace(-w / 2, w / 2, len(sig)), sig * h / 2)]
    return VMobject(stroke_color=c, stroke_width=sw).set_points_smoothly(pts)


def cov_matrix(gesture):
    """A plausible SPD coordination matrix in [0,1] with visible block structure and a
    clean BRIGHT diagonal. Brightness = strength of co-movement (|correlation|)."""
    rng = np.random.default_rng(100 + gesture)
    # low-rank coordination patterns -> a few muscle groups move together
    F = rng.standard_normal((N, 3)) * (1.0 + 0.5 * rng.standard_normal((N, 1)))
    # plant 2 coordinated blocks (channels that co-activate for this gesture)
    for _ in range(2):
        idx = rng.choice(N, size=rng.integers(5, 9), replace=False)
        v = rng.standard_normal(3)
        F[idx] += 1.6 * v
    C = F @ F.T
    d = np.sqrt(np.clip(np.diag(C), 1e-6, None))
    C = C / np.outer(d, d)        # normalize -> correlation, diag = 1
    M = np.abs(C) ** 1.3          # brightness = strength of co-movement; gamma for contrast
    np.fill_diagonal(M, 1.0)
    return M


class Coordination(Scene):
    def construct(self):
        seed()

        # ============================================================
        # BEAT 0 — CONTINUITY OPEN: top context strip (ghost frame-ruler
        # echoing S7's 50 fps ruler, one window highlighted = "inside it")
        # ============================================================
        strip_y = 3.18
        # the ghost ruler: 12 faint ticks on the top-left
        ruler_x0, ruler_x1 = -6.5, -2.7
        tick_xs = np.linspace(ruler_x0, ruler_x1, 12)
        ruler_axis = Line([ruler_x0 - 0.12, strip_y, 0], [ruler_x1 + 0.12, strip_y, 0],
                          stroke_color=INK_GHOST, stroke_width=1.4)
        ticks = VGroup(*[
            Line([x, strip_y - 0.13, 0], [x, strip_y + 0.13, 0],
                 stroke_color=INK_FAINT, stroke_width=1.6)
            for x in tick_xs])
        hi_i = 7                       # the highlighted window
        hi_x = tick_xs[hi_i]
        hi_box = SurroundingRectangle(ticks[hi_i], color=INK, stroke_width=2.2,
                                      buff=0.06)
        ruler_lbl = mono("one 20 ms frame", 17, INK_DIM)
        ruler_lbl.next_to(hi_box, DOWN, buff=0.16)
        thesis = mono("coordination,  not loudness", 21, INK)
        thesis.move_to([1.9, strip_y, 0])

        self.add(ruler_axis)
        self.play(LaggedStartMap(Create, ticks, lag_ratio=0.05, run_time=0.45))
        self.play(Create(hi_box), FadeIn(ruler_lbl, shift=DOWN * 0.06),
                  FadeIn(thesis, shift=RIGHT * 0.1), run_time=0.4)

        # a faint guide line drops from the highlighted tick toward center
        guide = DashedLine([hi_x, strip_y - 0.18, 0], [hi_x, 1.9, 0],
                           stroke_color=INK_GHOST, stroke_width=1.2,
                           dash_length=0.1)
        self.play(Create(guide), run_time=0.3)
        top_strip = VGroup(ruler_axis, ticks, hi_box, ruler_lbl, thesis)

        # ============================================================
        # BEAT 1 — TWO CHANNELS, IN SYNC  -> one bright togetherness cell
        # ============================================================
        a = wave(11)
        b = 0.82 * a + 0.18 * wave(12)   # strongly correlated with a
        b = b / (np.abs(b).max() + 1e-6)

        labA = mono("ch 7", 22, INK_DIM)
        labB = mono("ch 18", 22, INK_DIM)
        curveA = snippet_curve(a, c=INK)
        curveB = snippet_curve(b, c=INK)
        rowA = VGroup(labA, curveA).arrange(RIGHT, buff=0.5)
        rowB = VGroup(labB, curveB).arrange(RIGHT, buff=0.4)
        rowB.shift(RIGHT * (rowA[1].get_x() - rowB[1].get_x()))
        snippets = VGroup(rowA, rowB).arrange(DOWN, buff=1.15)
        snippets.move_to(LEFT * 2.3 + UP * 0.45)

        self.play(LaggedStart(
            Create(curveA), Create(curveB),
            FadeIn(labA), FadeIn(labB),
            lag_ratio=0.25, run_time=0.7))

        ask = mono("rise and fall together?", 24, INK)
        ask.next_to(snippets, DOWN, buff=0.55)
        self.play(Write(ask), run_time=0.4)

        # a vertical pulse bar sweeps across BOTH curves, a dot riding each, so the
        # eye sees the two signals peak and dip in lock-step.
        cA, cB = rowA[1], rowB[1]
        sweep = ValueTracker(0.0)
        bar = Line(UP * 0.6, DOWN * 0.6, stroke_color=INK, stroke_width=1.6)
        bar.set_opacity(0.55)
        y_mid = (cA.get_center()[1] + cB.get_center()[1]) / 2

        def bar_x():
            return cA.get_left()[0] + sweep.get_value() * cA.width
        bar.add_updater(lambda m: m.move_to([bar_x(), y_mid, 0]).set_height(
            abs(cA.get_center()[1] - cB.get_center()[1]) + 1.1))
        dotA = Dot(radius=0.07, color="#ffffff")
        dotB = Dot(radius=0.07, color="#ffffff")
        dotA.add_updater(lambda m: m.move_to(cA.point_from_proportion(sweep.get_value())))
        dotB.add_updater(lambda m: m.move_to(cB.point_from_proportion(sweep.get_value())))
        self.add(bar, dotA, dotB)
        self.play(sweep.animate.set_value(1.0), run_time=0.95, rate_func=linear)
        for m in (bar, dotA, dotB):
            m.clear_updaters()
        sync = mono("in sync", 20, INK).next_to(ask, RIGHT, buff=0.35)
        self.play(FadeOut(bar), FadeOut(dotA), FadeOut(dotB),
                  FadeIn(sync, shift=RIGHT * 0.1), run_time=0.35)

        # one grid cell that fills with brightness = how together they move
        cell = Square(1.25, stroke_color=INK_FAINT, stroke_width=2,
                      fill_color=INK, fill_opacity=0.0)
        cell.move_to(RIGHT * 4.2 + UP * 0.45)
        cell_lbl = mono("pair (7, 18)", 20, INK_FAINT).next_to(cell, UP, buff=0.22)
        arrow = Arrow(snippets.get_right() + RIGHT * 0.15,
                      cell.get_left() + LEFT * 0.05,
                      stroke_width=2.6, color=INK_FAINT, buff=0.18,
                      max_tip_length_to_length_ratio=0.1)
        self.play(Create(cell), FadeIn(cell_lbl), GrowArrow(arrow), run_time=0.5)
        val = num("0.9", 38, BG).move_to(cell)  # dark text on bright cell
        self.play(cell.animate.set_fill(INK, opacity=0.9),
                  FadeIn(val),
                  Flash(cell, color=INK, line_length=0.2, num_lines=12,
                        flash_radius=0.92, run_time=0.7))

        # ---- bottom running takeaway: pair tally "1 pair measured" ----
        bot_y = -3.2
        tally = mono("1 pair measured", 22, INK_DIM).move_to([0, bot_y, 0])
        self.play(FadeIn(tally, shift=UP * 0.08), run_time=0.35)

        # ============================================================
        # BEAT 2 — PROMOTE TO THE 31x31 MATRIX (the wow moment)
        # ============================================================
        # keep the bright cell; fade everything else of beat 1.
        beat1 = VGroup(snippets, ask, sync, cell_lbl, val, arrow)
        self.play(FadeOut(beat1), run_time=0.4)

        M1 = cov_matrix(0)
        SIDE = 4.4
        grid1 = self.make_heatmap(M1, side=SIDE).move_to([0, 0.1, 0])

        # the single earned cell flows INTO the matrix (it lands on the diagonal
        # start), then the matrix paints itself in a diagonal opacity sweep.
        cell_target = grid1[0]
        self.play(
            cell.animate.move_to(cell_target.get_center())
            .set_width(cell_target.get_width()).set_stroke(width=0),
            run_time=0.5)
        self.remove(cell)
        grid1[0].set_opacity(grid1[0]._target_op)
        self.add(grid1)

        # build the rest cell-by-cell along a diagonal sweep order, while a bottom
        # counter races 1 -> 961 in lock-step.
        order = sorted(range(N * N), key=lambda k: (k // N) + (k % N))
        cells_in_order = VGroup(*[grid1[k] for k in order])

        pairs = ValueTracker(1)
        counter_mob = num("pairs measured:  1", 24, INK).move_to([0, bot_y, 0])

        def counter_upd(m):
            v = int(round(pairs.get_value()))
            m.become(num(f"pairs measured:  {v}", 24, INK).move_to([0, bot_y, 0]))
        counter_mob.add_updater(counter_upd)
        self.remove(tally)
        self.add(counter_mob)

        self.play(
            LaggedStartMap(lambda m: m.animate.set_opacity(m._target_op),
                           cells_in_order, lag_ratio=0.0022),
            pairs.animate.set_value(961),
            run_time=1.5)
        counter_mob.clear_updaters()
        counter_mob.become(num("pairs measured:  961", 24, INK).move_to([0, bot_y, 0]))

        frame1 = SurroundingRectangle(grid1, color=INK_GHOST, stroke_width=2, buff=0.06)
        # extend the top guide line so it visibly connects ruler -> matrix
        guide2 = DashedLine([hi_x, 1.9, 0], [grid1.get_left()[0] - 0.05,
                                              grid1.get_top()[1] - 0.4, 0],
                            stroke_color=INK_GHOST, stroke_width=1.2,
                            dash_length=0.1)
        self.play(Create(frame1), Create(guide2), run_time=0.4)

        # pair -> cell crosshair: a row band + col band cross at one cell, naming
        # exactly which two sensors that cell compares.
        cw = grid1[0].width
        ri, cj = 6, 17
        row_band = self.band(grid1, "row", ri, cw)
        col_band = self.band(grid1, "col", cj, cw)
        hit = grid1[ri * N + cj]
        crosslbl = mono("every pair\nof sensors", 19, INK_DIM)
        crosslbl.next_to(grid1, RIGHT, buff=0.6).shift(UP * 1.1)
        self.play(FadeIn(row_band), FadeIn(col_band), FadeIn(crosslbl), run_time=0.4)
        self.play(Indicate(hit, color="#ffffff", scale_factor=1.0), run_time=0.4)
        self.play(FadeOut(row_band), FadeOut(col_band), run_time=0.25)

        # the self-diagonal lights up bright (with glow): each sensor with itself
        diag_idx = [i * N + i for i in range(N)]
        diag_cells = VGroup(*[grid1[k] for k in diag_idx])
        diag_glow = VGroup(*[c.copy().set_stroke("#ffffff", width=4, opacity=0.10)
                             for c in diag_cells])
        dlabel = mono("bright diagonal =\neach sensor\nwith itself", 19, INK_DIM)
        dlabel.next_to(grid1, RIGHT, buff=0.6).shift(DOWN * 0.7)
        self.add(diag_glow)
        self.play(diag_cells.animate.set_fill("#ffffff", opacity=1.0),
                  FadeIn(diag_glow),
                  FadeIn(dlabel),
                  Indicate(diag_cells, color="#ffffff", scale_factor=1.0),
                  run_time=0.65)

        # bottom locks to the 961 anchor line
        lock = mono("31 x 31  =  961 numbers   ·   one matrix per frame", 22, INK)
        lock.move_to([0, bot_y, 0])
        self.play(ReplacementTransform(counter_mob, lock), run_time=0.55)

        # ============================================================
        # BEAT 3 — NAME IT: the frame's coordination pattern
        # ============================================================
        namer = mono("this is the frame's coordination pattern", 20, INK_DIM)
        namer.next_to(grid1, DOWN, buff=0.4)
        self.play(FadeIn(namer, shift=UP * 0.08), run_time=0.4)
        self.play(FadeOut(namer), run_time=0.3)

        # ============================================================
        # BEAT 4 — TWO GESTURES, TWO PATTERNS
        # ============================================================
        crosshair_extras = VGroup(crosslbl, dlabel, guide2)
        m1_group = VGroup(grid1, frame1, diag_glow)
        self.play(
            FadeOut(crosshair_extras),
            m1_group.animate.scale(0.62).move_to(LEFT * 3.5 + UP * 0.1),
            run_time=0.65)

        M2 = cov_matrix(5)
        grid2 = self.make_heatmap(M2, side=SIDE * 0.62)
        grid2.move_to(RIGHT * 3.5 + UP * 0.1)
        for c in grid2:
            c.set_opacity(c._target_op)
        diag2 = VGroup(*[grid2[i * N + i] for i in range(N)])
        for c in diag2:
            c.set_fill("#ffffff", opacity=1.0)
        diag2_glow = VGroup(*[c.copy().set_stroke("#ffffff", width=3, opacity=0.10)
                              for c in diag2])
        frame2 = SurroundingRectangle(grid2, color=INK_GHOST, stroke_width=1.6,
                                      buff=0.05)

        g1lbl = serif('gesture  "AE"', 24, INK_DIM).next_to(grid1, UP, buff=0.3)
        g2lbl = serif('gesture  "S"', 24, INK_DIM).next_to(grid2, UP, buff=0.3)
        self.play(FadeIn(g1lbl),
                  FadeIn(VGroup(grid2, diag2_glow, frame2), shift=LEFT * 0.2),
                  FadeIn(g2lbl), run_time=0.7)

        # contrast: sweep an Indicate over each (different block regions), while the
        # faint weak->strong legend bar fades in so the shading is decodable.
        legend = self.legend_bar().scale(0.9).move_to([0, -2.35, 0])
        self.play(Indicate(grid1, color="#ffffff", scale_factor=1.0),
                  Indicate(grid2, color="#ffffff", scale_factor=1.0),
                  FadeIn(legend), run_time=0.6)

        # bottom counter morphs into the punchline
        punch = serif("each sound = its own pattern of coordination", 27, INK)
        punch.move_to([0, bot_y, 0])
        self.play(ReplacementTransform(lock, punch), run_time=0.75)

        # ============================================================
        # BEAT 5 — POSTER HOLD
        # ============================================================
        self.wait(0.6)

    # ----- helpers --------------------------------------------------------
    def make_heatmap(self, M, side=4.4):
        """A VGroup of N*N squares; brightness (fill opacity) = M value.
        Each cell stores its target opacity on ._target_op and starts at 0."""
        cell = side / N
        grid = VGroup()
        for i in range(N):        # row -> top to bottom
            for j in range(N):    # col -> left to right
                op = float(np.clip(M[i, j], 0.03, 1.0))
                sq = Square(cell, stroke_width=0,
                            fill_color=INK, fill_opacity=0.0)
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
            sq = Square(w, stroke_width=0, fill_color=INK, fill_opacity=op)
            bars.add(sq)
        bars.arrange(RIGHT, buff=0.0)
        left = mono("weak", 18, INK_FAINT).next_to(bars, LEFT, buff=0.3)
        right = mono("strong co-movement", 18, INK_DIM).next_to(bars, RIGHT, buff=0.3)
        frame = SurroundingRectangle(bars, color=INK_GHOST, stroke_width=1.2, buff=0.0)
        return VGroup(bars, frame, left, right)
