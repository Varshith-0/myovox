# website/anim/s9_features_embed.py — S9 "Fingerprint" (shrinkage + embedding)
#
# FULL-CANVAS vertical pipeline column (x in [-7.1,7.1], y in [-4,4]):
#   TOP strip  (y ~ +2.4..+3.6): quiet context — a ghost thumbnail of S8's
#       bright-diagonal 31x31 covariance heatmap + caption, and a full-width
#       INK_GHOST progress rule with a caret that slides steady -> squeeze ->
#       filmstrip marking the current sub-stage.
#   CENTER     (y ~ -1.2..+2.0): the star mechanism, left->right pipeline —
#       Stage A: noisy 11x11 stand-in covariance (~961 numbers) is STEADIED by a
#                90% measured + 10% plain blend bar (shrinkage, alpha = 0.1).
#       Stage B: the clean grid's cells stream as ghost dots through a narrow
#                "waist" (squeeze) and re-emerge as a slim 384-bar row.
#       Stage C: the bar-row collapses into one compact fingerprint card.
#   BOTTOM strip (y ~ -3.6..-2.2): a big live counter free-falls 961 -> 384 in
#       LOCKSTEP with the squeeze (compression bar shrinks ~2.5x), then shrinks
#       to a corner readout and the strip becomes the FILMSTRIP rail of
#       fingerprint cards at 50/sec — what the network actually reads.
from manim import *
from emg_style import *
import numpy as np

# Geometry of the three horizontal zones (keep everything inside the canvas).
TOP_Y = 3.05          # context strip baseline
RULE_Y = 2.42         # full-width progress rule
CENTER_Y = 0.45       # mechanism band centre
BOT_Y = -2.7          # takeaway strip centre
X_L = -6.7            # full-width left edge
X_R = 6.7            # full-width right edge


class Fingerprint(Scene):
    def construct(self):
        seed()

        # ============================================================
        # SHARED FIELDS / DATA
        # ============================================================
        N = 11                                  # legible stand-in for 31x31
        cell = 0.26
        base = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                base[i, j] = np.exp(-((i - j) ** 2) / 8.0)
        speckle = (np.random.rand(N, N) - 0.5) * 0.95
        speckle = (speckle + speckle.T) / 2
        noisy = np.clip(base + speckle, 0, 1)
        ident = np.eye(N) * 0.62 + 0.07         # the "plain steady pattern"
        clean = 0.9 * noisy + 0.1 * ident       # shrinkage, alpha = 0.1

        def grid_from(vals, c=cell):
            g = VGroup()
            for i in range(N):
                for j in range(N):
                    sq = Square(c, stroke_width=0, fill_color=INK,
                                fill_opacity=float(vals[i, j]))
                    sq.move_to([(j - (N - 1) / 2) * c, ((N - 1) / 2 - i) * c, 0])
                    g.add(sq)
            return g

        # ============================================================
        # TOP STRIP — context spine (built first, persists the whole clip)
        # ============================================================
        # Ghost thumbnail of S8's bright-diagonal covariance heatmap.
        tn = 11
        tcell = 0.062
        thumb = VGroup()
        for i in range(tn):
            for j in range(tn):
                v = np.exp(-((i - j) ** 2) / 2.0)         # bright diagonal
                v = max(v, 0.05)
                thumb.add(Square(tcell, stroke_width=0, fill_color=INK,
                                 fill_opacity=v * 0.5).move_to(
                    [(j - (tn - 1) / 2) * tcell, ((tn - 1) / 2 - i) * tcell, 0]))
        thumb_box = SurroundingRectangle(thumb, color=INK_GHOST, stroke_width=1.0,
                                         buff=0.04)
        thumb_grp = VGroup(thumb, thumb_box).move_to([X_L + 0.45, TOP_Y, 0])
        ctx_cap = mono("from the last step  ·  one 31 x 31 matrix per frame", 17,
                       INK_FAINT)
        ctx_cap.next_to(thumb_grp, RIGHT, buff=0.3).align_to(thumb_grp, UP).shift(DOWN * 0.02)
        ctx_cap2 = mono("we steady it, then squeeze it", 16, INK_GHOST)
        ctx_cap2.next_to(ctx_cap, DOWN, buff=0.12).align_to(ctx_cap, LEFT)

        # Full-width progress rule with caret + 3 stage ticks.
        rule = Line([X_L, RULE_Y, 0], [X_R, RULE_Y, 0],
                    stroke_color=INK_GHOST, stroke_width=1.2)
        # 'steady' tick pushed hard to the far left so its caret/down-triangle and
        # rule tick never collide with the center-band 'shrinkage  alpha = 0.1'
        # label below it (whose left edge sits near x = -5.3).
        stage_x = {"steady": X_L + 0.55, "squeeze": 0.0, "filmstrip": X_R - 2.4}
        ticks = VGroup()
        stage_lbls = {}
        for name, x in stage_x.items():
            ticks.add(Line([x, RULE_Y - 0.08, 0], [x, RULE_Y + 0.08, 0],
                           stroke_color=INK_GHOST, stroke_width=1.2))
            lb = mono(name, 15, INK_GHOST).move_to([x, RULE_Y + 0.26, 0])
            stage_lbls[name] = lb
        stage_lbl_grp = VGroup(*stage_lbls.values())
        caret = Triangle(fill_color=INK, fill_opacity=0.9, stroke_width=0).scale(0.09)
        caret.rotate(PI)  # point down at the rule
        caret.move_to([stage_x["steady"], RULE_Y - 0.22, 0])

        def goto_stage(name, rt=0.5):
            tgt = stage_x[name]
            anims = [caret.animate.move_to([tgt, RULE_Y - 0.22, 0])]
            for n2, lb in stage_lbls.items():
                anims.append(lb.animate.set_color(INK_DIM if n2 == name else INK_GHOST))
            self.play(*anims, run_time=rt)

        # ============================================================
        # BEAT 1 — Pose & inherit (~2.2s)
        # ============================================================
        self.play(FadeIn(thumb_grp, shift=DOWN * 0.15),
                  FadeIn(ctx_cap), FadeIn(ctx_cap2), run_time=0.5)
        stage_lbls["steady"].set_color(INK_DIM)  # current stage starts active
        self.play(Create(rule),
                  LaggedStartMap(Create, ticks, lag_ratio=0.2, run_time=0.5),
                  FadeIn(stage_lbl_grp), run_time=0.55)
        self.add(caret)

        # Center-left: the noisy covariance grid in a faint frame.
        gridC = LEFT * 4.05 + UP * (CENTER_Y - 0.05)
        mat = grid_from(noisy)
        frame_box = Square(N * cell + 0.1, stroke_color=INK_FAINT, stroke_width=1.4,
                           fill_opacity=0)
        matrix = VGroup(frame_box, mat).move_to(gridC)
        frame_box.move_to(mat.get_center())

        noisy_lbl = mono("noisy", 17, INK_DIM).next_to(matrix, UP, buff=0.14)
        size_lbl = mono("31 x 31 covariance  ·  ~961 numbers", 17, INK_FAINT)
        size_lbl.next_to(matrix, DOWN, buff=0.24)

        # Big live counter in the bottom strip.
        cnt = ValueTracker(961.0)
        count_txt = counter(cnt, fmt=lambda v: str(int(round(v))), s=74, c=INK,
                            at=[0, BOT_Y + 0.18, 0])

        self.play(LaggedStartMap(FadeIn, mat, lag_ratio=0.004, run_time=0.65),
                  Create(frame_box), run_time=0.65)
        self.play(FadeIn(noisy_lbl, shift=DOWN * 0.08),
                  FadeIn(size_lbl, shift=UP * 0.1),
                  FadeIn(count_txt), run_time=0.5)

        # ============================================================
        # BEAT 2 — Steady it (shrinkage) (~2.4s)
        # ============================================================
        # Blend bar sits center, to the RIGHT of the grid (the "operation").
        bar_w = 4.1
        bar_c = RIGHT * 2.05 + UP * (CENTER_Y + 0.55)
        bar = RoundedRectangle(width=bar_w, height=0.32, corner_radius=0.06,
                               stroke_color=INK_FAINT, stroke_width=1.4,
                               fill_opacity=0).move_to(bar_c)
        meas = Rectangle(width=bar_w * 0.9, height=0.32, stroke_width=0,
                         fill_color=INK, fill_opacity=0.82)
        plain = Rectangle(width=bar_w * 0.1, height=0.32, stroke_width=0,
                          fill_color=INK, fill_opacity=0.26)
        meas.align_to(bar, LEFT).set_y(bar.get_y())
        plain.next_to(meas, RIGHT, buff=0)
        steady_lbl = mono("steady the matrix", 20, INK).next_to(bar, UP, buff=0.5)
        m_lbl = mono("90%  measured", 16, INK_DIM).next_to(meas, DOWN, buff=0.18)
        p_lbl = mono("10%  plain", 15, INK_FAINT).next_to(plain, DOWN, buff=0.18).shift(RIGHT * 0.04)
        blend_grp = VGroup(bar, meas, plain, steady_lbl, m_lbl, p_lbl)

        # Arrow from grid into the operation.
        op_arrow = Arrow(matrix.get_right() + RIGHT * 0.05,
                         [bar.get_left()[0] - 0.2, CENTER_Y - 0.05, 0],
                         stroke_width=2.2, color=INK_GHOST, buff=0.1,
                         max_tip_length_to_length_ratio=0.08)

        self.play(FadeIn(steady_lbl, shift=DOWN * 0.1), FadeIn(bar),
                  GrowFromEdge(meas, LEFT), GrowFromEdge(plain, LEFT),
                  FadeIn(m_lbl), FadeIn(p_lbl), GrowArrow(op_arrow), run_time=0.6)

        # Pure-white pulse travels across the blend bar (the single #fff accent).
        pulse = Rectangle(width=0.13, height=0.32, stroke_width=0,
                          fill_color="#ffffff", fill_opacity=0.92)
        pulse.move_to(bar.get_left() + RIGHT * 0.07)
        self.add(pulse)
        self.play(pulse.animate.move_to(bar.get_right() + LEFT * 0.07),
                  run_time=0.6, rate_func=linear)
        self.remove(pulse)

        # Settle: noisy -> clean; rename label to the shrinkage operation.
        clean_grid = grid_from(clean).move_to(mat.get_center())
        alpha_lbl = mono("shrinkage   alpha = 0.1", 19, INK).move_to(noisy_lbl)
        self.play(Transform(mat, clean_grid, run_time=0.85),
                  ReplacementTransform(noisy_lbl, alpha_lbl),
                  cnt.animate.set_value(961.0))   # counter holds
        self.play(Indicate(alpha_lbl, scale_factor=1.06, color=INK),
                  Flash(matrix.get_center(), color=INK, flash_radius=1.5,
                        line_length=0.14, num_lines=16, run_time=0.55))

        # ============================================================
        # BEAT 3 — The squeeze (WOW) (~3.0s)
        # ============================================================
        self.play(FadeOut(blend_grp), FadeOut(op_arrow), FadeOut(alpha_lbl),
                  run_time=0.35)
        # advance the caret to 'squeeze' while sliding the grid left (combined).
        caret_sq = caret.animate.move_to([stage_x["squeeze"], RULE_Y - 0.22, 0])
        sq_lbls = [stage_lbls["squeeze"].animate.set_color(INK_DIM),
                   stage_lbls["steady"].animate.set_color(INK_GHOST)]
        gridL = LEFT * 4.3 + UP * CENTER_Y
        self.play(matrix.animate.scale(0.82).move_to(gridL),
                  size_lbl.animate.scale(0.95).next_to(
                      LEFT * 4.3 + UP * CENTER_Y, DOWN, buff=1.15),
                  caret_sq, *sq_lbls,
                  run_time=0.6)
        size_lbl.next_to(matrix, DOWN, buff=0.22)

        # The narrow "waist" block near x = 0.
        waist = RoundedRectangle(width=0.5, height=2.0, corner_radius=0.1,
                                 stroke_color=INK, stroke_width=1.8,
                                 fill_color=BG, fill_opacity=1.0)
        waist.move_to([-0.35, CENTER_Y, 0])
        waist_lbl = mono("front-end", 16, INK_DIM).next_to(waist, UP, buff=0.2)
        waist_lbl2 = mono("squeeze", 15, INK_FAINT).next_to(waist, DOWN, buff=0.2)

        # Funnel guide lines from the grid edge converging into the waist top.
        funnel = VGroup(*[
            Line(matrix.get_right() + UP * y, waist.get_left() + UP * 0.0,
                 stroke_color=INK_GHOST, stroke_width=0.9)
            for y in np.linspace(-1.0, 1.0, 7)
        ])
        self.play(Create(waist), FadeIn(waist_lbl), FadeIn(waist_lbl2),
                  LaggedStartMap(Create, funnel, lag_ratio=0.05), run_time=0.55)

        # The 384 embedding bars (render 48 as legible stand-in) — built up to the
        # RIGHT of the waist, growing from a baseline.
        nbars = 48
        emb_w = 4.6
        bw = emb_w / nbars
        hh = np.abs(np.random.randn(nbars))
        hh = 0.12 + 1.35 * (hh / hh.max())
        bars_c = RIGHT * 3.55 + UP * (CENTER_Y - 0.2)
        bars = VGroup()
        for k in range(nbars):
            h = float(hh[k])
            r = Rectangle(width=bw * 0.62, height=h, stroke_width=0,
                          fill_color=INK, fill_opacity=0.9)
            r.move_to([bars_c[0] + (k - (nbars - 1) / 2) * bw,
                       bars_c[1] + h / 2, 0])
            bars.add(r)
        baseline = Line([bars.get_left()[0], bars_c[1], 0],
                        [bars.get_right()[0], bars_c[1], 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        # Pre-shrink bars to zero height for GrowFromEdge.
        for b in bars:
            b.stretch_to_fit_height(0.001)
            b.move_to([b.get_x(), bars_c[1], 0])

        flow = VGroup(*[
            Line(waist.get_right(), [bars.get_left()[0], bars_c[1] + y, 0],
                 stroke_color=INK_GHOST, stroke_width=0.9)
            for y in np.linspace(-0.2, 0.7, 4)
        ])

        # Ghost dots: a few cells from the grid stream into the waist.
        dots = VGroup()
        rng = np.random.default_rng(3)
        src_idx = rng.choice(len(mat), size=16, replace=False)
        for ci in src_idx:
            d = Dot(radius=0.03, color=INK, fill_opacity=0.5)
            d.move_to(mat[int(ci)].get_center())
            dots.add(d)
        self.add(dots)

        # Restore target heights for the grow.
        targets = [float(hh[k]) for k in range(nbars)]

        # LOCKSTEP: dots funnel in -> bars grow -> counter free-falls 961->384 ->
        # compression bar shrinks, all landing together. One #fff sweep christens.
        comp_full = 4.4   # full-width compression bar under the counter
        comp_track = RoundedRectangle(width=comp_full, height=0.12, corner_radius=0.05,
                                      stroke_color=INK_GHOST, stroke_width=1.0,
                                      fill_opacity=0).move_to([0, BOT_Y - 0.52, 0])
        comp_fill = Rectangle(width=comp_full, height=0.12, stroke_width=0,
                              fill_color=INK, fill_opacity=0.6)
        comp_fill.align_to(comp_track, LEFT).set_y(comp_track.get_y())
        comp_lbl = mono("961  ->  384   ·   ~2.5x squeeze", 15, INK_FAINT)
        comp_lbl.next_to(comp_track, DOWN, buff=0.13)
        self.play(Create(comp_track), FadeIn(comp_fill), FadeIn(comp_lbl),
                  LaggedStartMap(Create, flow, lag_ratio=0.08), run_time=0.5)

        # converge dots into the waist (they dissolve as the bars emerge below)
        self.play(LaggedStart(*[d.animate.move_to(waist.get_center())
                                for d in dots],
                              lag_ratio=0.03, run_time=0.5))

        emb_lbl = mono("384 numbers", 22, INK).next_to(bars_c, UP, buff=1.0)
        emb_lbl.move_to([bars_c[0], CENTER_Y + 1.35, 0])

        grow_anims = []
        for k, b in enumerate(bars):
            b.target = b.copy()
            b.target.stretch_to_fit_height(targets[k])
            b.target.move_to([b.get_x(), bars_c[1] + targets[k] / 2, 0])
            grow_anims.append(MoveToTarget(b))

        self.play(
            cnt.animate.set_value(384.0),
            comp_fill.animate.stretch_to_fit_width(comp_full * 0.40).align_to(
                comp_track, LEFT),
            LaggedStart(*grow_anims, lag_ratio=0.012),
            Create(baseline),
            FadeOut(dots, scale=0.2),
            run_time=1.0,
        )
        self.remove(*dots)
        count_txt.clear_updaters()
        # keep comp_fill left-anchored after stretch
        comp_fill.align_to(comp_track, LEFT)

        # Snap the "384 numbers" header in crisply AFTER the bars finish so it never
        # reads as a half-rendered dim-grey title mid-grow (reviewer note at frame 17).
        self.play(FadeIn(emb_lbl, shift=DOWN * 0.08), run_time=0.3)

        # The single #fff sweep christens the new fingerprint row.
        sweep = Rectangle(width=0.16, height=1.9, stroke_width=0,
                          fill_color="#ffffff", fill_opacity=0.7)
        sweep.move_to([bars.get_left()[0], bars_c[1] + 0.75, 0])
        self.add(sweep)
        self.play(sweep.animate.move_to([bars.get_right()[0], bars_c[1] + 0.75, 0]),
                  run_time=0.55, rate_func=linear)
        self.play(FadeOut(sweep), Indicate(emb_lbl, scale_factor=1.08, color=INK),
                  run_time=0.4)

        # ============================================================
        # BEAT 4 — Name the fingerprint (~1.4s)
        # ============================================================
        # Build the target fingerprint card (mini bars in a rounded frame).
        def make_fp(scale=1.0, op=0.82, sw=1.2):
            cardR = RoundedRectangle(width=0.9, height=1.25, corner_radius=0.07,
                                     stroke_color=INK, stroke_width=sw,
                                     fill_color=BG, fill_opacity=1.0)
            mm = VGroup()
            mn = 12
            mw = 0.62 / mn
            hs = 0.12 + 1.0 * np.abs(np.random.randn(mn))
            hs = hs / hs.max()
            for k in range(mn):
                h = float(hs[k]) * 0.78 + 0.08
                r = Rectangle(width=mw * 0.62, height=h, stroke_width=0,
                              fill_color=INK, fill_opacity=op)
                r.move_to([(k - (mn - 1) / 2) * mw, h * 0.5 - 0.42, 0])
                mm.add(r)
            return VGroup(cardR, mm).scale(scale)

        fp_card = make_fp(1.0, op=0.85, sw=1.5).move_to(
            [bars_c[0], CENTER_Y - 0.05, 0])

        # The filmstrip lives in the lower-CENTER (fills the void) so the punchline
        # has room below it without clipping the canvas.
        FILM_Y = -1.45
        rail_y = 0.7

        corner_read = mono("384 numbers · one fingerprint", 15, INK_FAINT)
        corner_read.move_to([X_L + 1.85, FILM_Y + rail_y + 0.3, 0])

        # Retire the big "384 numbers" header into the card itself so it does NOT
        # linger near where the right-hand recap card will fade in (kills the
        # ghost/double-text crossfade the reviewer flagged at frame 23).
        self.play(
            FadeOut(matrix), FadeOut(size_lbl), FadeOut(waist),
            FadeOut(waist_lbl), FadeOut(waist_lbl2), FadeOut(funnel),
            FadeOut(flow), FadeOut(baseline),
            ReplacementTransform(bars, fp_card),
            FadeOut(emb_lbl, target_position=fp_card.get_center(), scale=0.4),
            run_time=0.75,
        )

        # A quiet lineage recap holds the upper-CENTER while we pull back: it
        # restates the whole pipeline (matrix -> steady -> squeeze -> fingerprint)
        # so the canvas stays full and the filmstrip below has a "source".
        rc_y = 1.05
        rc_mat = VGroup(*[Square(0.05, stroke_width=0, fill_color=INK,
                                 fill_opacity=max(np.exp(-((i - j) ** 2) / 4.0), 0.05) * 0.5)
                          .move_to([(j - 5) * 0.05, (5 - i) * 0.05, 0])
                          for i in range(11) for j in range(11)])
        rc_matbox = SurroundingRectangle(rc_mat, color=INK_GHOST, stroke_width=1.0, buff=0.04)
        rc_m = VGroup(rc_mat, rc_matbox)
        rc_card = make_fp(0.5, op=0.7, sw=1.0)
        rc_m.move_to([-3.4, rc_y, 0])
        rc_card.move_to([3.4, rc_y, 0])
        rc_mid = mono("steady · squeeze", 16, INK_FAINT).move_to([0, rc_y, 0])
        rc_a1 = Arrow(rc_m.get_right(), rc_mid.get_left(), buff=0.22,
                      stroke_width=1.6, color=INK_GHOST,
                      max_tip_length_to_length_ratio=0.06)
        rc_a2 = Arrow(rc_mid.get_right(), rc_card.get_left(), buff=0.22,
                      stroke_width=1.6, color=INK_GHOST,
                      max_tip_length_to_length_ratio=0.06)
        rc_capL = mono("961 numbers", 14, INK_GHOST).next_to(rc_m, DOWN, buff=0.16)
        rc_capR = mono("384-number fingerprint", 14, INK_GHOST).next_to(rc_card, DOWN, buff=0.16)
        recap = VGroup(rc_m, rc_card, rc_mid, rc_a1, rc_a2, rc_capL, rc_capR)

        # Card animates down into the filmstrip band; big counter retires to a
        # quiet corner readout above the rail; recap fades in up top; caret -> film.
        self.play(count_txt.animate.scale(16 / 74).move_to(
                      [0, FILM_Y + rail_y + 0.95, 0]).set_opacity(0),
                  FadeIn(corner_read),
                  fp_card.animate.scale(0.62).move_to([0, FILM_Y, 0]),
                  comp_fill.animate.set_opacity(0), comp_track.animate.set_opacity(0),
                  FadeOut(comp_lbl),
                  caret.animate.move_to([stage_x["filmstrip"], RULE_Y - 0.22, 0]),
                  stage_lbls["filmstrip"].animate.set_color(INK_DIM),
                  stage_lbls["squeeze"].animate.set_color(INK_GHOST),
                  LaggedStart(FadeIn(rc_m), GrowArrow(rc_a1), FadeIn(rc_mid),
                              GrowArrow(rc_a2), FadeIn(rc_card),
                              FadeIn(rc_capL), FadeIn(rc_capR), lag_ratio=0.1),
                  run_time=0.8)
        self.remove(count_txt, comp_fill, comp_track)

        # ============================================================
        # BEAT 5 — Pull back to the filmstrip (~2.6s)
        # ============================================================
        ncards = 11
        strip = VGroup(*[make_fp(0.62, op=0.78, sw=1.0) for _ in range(ncards)])
        strip.arrange(RIGHT, buff=0.22)
        strip.move_to([0, FILM_Y, 0])
        mid = ncards // 2
        # Move the existing card to the centre slot, replace it in the strip group.
        self.play(fp_card.animate.move_to(strip[mid].get_center()), run_time=0.4)
        strip.submobjects[mid] = fp_card
        others = VGroup(*[strip[i] for i in range(ncards) if i != mid])

        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.12) for c in others],
                              lag_ratio=0.045), run_time=0.65)

        # Thin top/bottom rails + sprocket dots so it reads as film.
        top_rail = Line([X_L, FILM_Y + rail_y, 0], [X_R, FILM_Y + rail_y, 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        bot_rail = Line([X_L, FILM_Y - rail_y, 0], [X_R, FILM_Y - rail_y, 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        sprockets = VGroup()
        xs = np.linspace(X_L + 0.25, X_R - 0.25, 26)
        for x in xs:
            for yy in (FILM_Y + rail_y, FILM_Y - rail_y):
                sprockets.add(Square(0.05, stroke_width=0, fill_color=INK_FAINT,
                                     fill_opacity=0.5).move_to([x, yy, 0]))
        self.play(Create(top_rail), Create(bot_rail),
                  LaggedStartMap(FadeIn, sprockets, lag_ratio=0.01),
                  run_time=0.6)

        # Punchline in the bottom strip, comfortably above the canvas edge.
        rate_lbl = mono("filmstrip of 384-number fingerprints  ·  50 / sec", 21, INK)
        rate_lbl.move_to([0, BOT_Y - 0.18, 0])
        read_lbl = mono("what the network actually reads", 16, INK_FAINT)
        read_lbl.next_to(rate_lbl, DOWN, buff=0.16)
        self.play(FadeIn(rate_lbl, shift=UP * 0.12),
                  FadeIn(read_lbl, shift=UP * 0.08), run_time=0.5)

        # The single #fff scan line sweeps the whole strip, briefly brightening
        # each card's frame as it passes (50/sec streaming read).
        scan = Line([X_L, FILM_Y + rail_y, 0], [X_L, FILM_Y - rail_y, 0],
                    stroke_color="#ffffff", stroke_width=2.2).set_opacity(0.65)
        base_sw = {i: c[0].get_stroke_width() for i, c in enumerate(strip)}

        def card_brighten(group):
            sx = scan.get_x()
            for i, c in enumerate(group):
                d = abs(c.get_x() - sx)
                if d < 0.45:
                    f = 1.0 - d / 0.45
                    c[0].set_stroke(width=base_sw[i] + 1.8 * f)
                    c[1].set_opacity(0.78 + 0.22 * f)
                else:
                    c[0].set_stroke(width=base_sw[i])
                    c[1].set_opacity(0.78)

        strip.add_updater(card_brighten)
        self.add(scan, strip)
        self.play(scan.animate.move_to([X_R, FILM_Y, 0]),
                  run_time=1.0, rate_func=linear)
        strip.remove_updater(card_brighten)

        # ============================================================
        # BEAT 6 — Poster hold (~0.6s)
        # ============================================================
        self.play(FadeOut(scan),
                  fp_card.animate.set_stroke(width=2.2),
                  Indicate(fp_card, scale_factor=1.06, color=INK), run_time=0.5)
        self.wait(0.6)
