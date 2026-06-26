# website/anim/s9_features_embed.py — S9 "Fingerprint" (shrinkage + embedding)
#
# Discovery arc (locked beat sheet, one next_section per spoken sentence):
#   B1  puzzle   : the inherited 31x31 grid is NOISY — a handful of cells flicker
#                  so "jittery and unreliable" is something you SEE.
#   B2  nudge    : a blend bar (90% measured + 10% plain calm pattern); one white
#                  pulse rides across it.
#   B3  steadier : grid settles noisy->clean, label -> "shrinkage alpha = 0.1";
#                  the big 961 counter Indicate-pulses on "a lot to carry".
#   B4  squeeze  : grid funnels through a waist and re-emerges as a slim 384-bar
#                  row; counter free-falls 961 -> 384 in lockstep.
#   B5  filmstrip: the bar-row collapses to ONE fingerprint card, then a rail of
#                  identical cards fades in with film rails + sprockets.
#   B6  payoff   : a single white scan line sweeps the strip; settles to
#                  "what the reader actually reads · 50 / sec".
#
# STRICT MONOCHROME on #050505. One white accent (pulse / sweep) per beat.
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

        # Top progress rule + caret, shared across the clip (stage labels GHOST
        # except the active one).
        rule = Line([X_L, RULE_Y, 0], [X_R, RULE_Y, 0],
                    stroke_color=INK_GHOST, stroke_width=1.2)
        stage_x = {"steady": X_L + 0.55, "squeeze": 0.0, "filmstrip": X_R - 2.4}
        ticks = VGroup()
        stage_lbls = {}
        for name, x in stage_x.items():
            ticks.add(Line([x, RULE_Y - 0.08, 0], [x, RULE_Y + 0.08, 0],
                           stroke_color=INK_GHOST, stroke_width=1.2))
            stage_lbls[name] = mono(name, 15, INK_GHOST).move_to([x, RULE_Y + 0.26, 0])
        stage_lbl_grp = VGroup(*stage_lbls.values())
        caret = Triangle(fill_color=INK, fill_opacity=0.9, stroke_width=0).scale(0.09)
        caret.rotate(PI)
        caret.move_to([stage_x["steady"], RULE_Y - 0.22, 0])

        def light_stage(name):
            return [stage_lbls[n].animate.set_color(INK_DIM if n == name else INK_GHOST)
                    for n in stage_lbls]

        # Ghost thumbnail of S8's bright-diagonal covariance heatmap — lineage only.
        tn = 11
        tcell = 0.062
        thumb = VGroup()
        for i in range(tn):
            for j in range(tn):
                v = max(np.exp(-((i - j) ** 2) / 2.0), 0.05)
                thumb.add(Square(tcell, stroke_width=0, fill_color=INK,
                                 fill_opacity=v * 0.5).move_to(
                    [(j - (tn - 1) / 2) * tcell, ((tn - 1) / 2 - i) * tcell, 0]))
        thumb_box = SurroundingRectangle(thumb, color=INK_GHOST, stroke_width=1.0, buff=0.04)
        thumb_grp = VGroup(thumb, thumb_box).move_to([X_L + 0.45, TOP_Y, 0])
        ctx_cap = mono("from the last step  ·  one 31 x 31 matrix per frame", 17, INK_FAINT)
        ctx_cap.next_to(thumb_grp, RIGHT, buff=0.3).align_to(thumb_grp, UP).shift(DOWN * 0.02)

        # ============================================================
        # BEAT 1 — Puzzle: a NOISY grid that visibly jitters (~2.32s)
        # ============================================================
        self.next_section("noisy")
        self.play(FadeIn(thumb_grp, shift=DOWN * 0.15), FadeIn(ctx_cap), run_time=0.45)
        self.play(Create(rule),
                  LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.2),
                  FadeIn(stage_lbl_grp), *light_stage("steady"), run_time=0.5)
        self.add(caret)

        gridC = LEFT * 4.05 + UP * (CENTER_Y - 0.05)
        mat = grid_from(noisy)
        frame_box = Square(N * cell + 0.1, stroke_color=INK_FAINT, stroke_width=1.4,
                           fill_opacity=0)
        matrix = VGroup(frame_box, mat).move_to(gridC)
        frame_box.move_to(mat.get_center())

        noisy_lbl = mono("noisy", 17, INK_DIM).next_to(matrix, UP, buff=0.14)
        size_lbl = mono("31 x 31 covariance  ·  961 numbers", 17, INK_FAINT)
        size_lbl.next_to(matrix, DOWN, buff=0.24)

        cnt = ValueTracker(961.0)
        count_txt = counter(cnt, fmt=lambda v: str(int(round(v))), s=74, c=INK,
                            at=[0, BOT_Y + 0.18, 0])

        self.play(LaggedStart(*[FadeIn(s) for s in mat], lag_ratio=0.004),
                  Create(frame_box), run_time=0.55)
        self.play(FadeIn(noisy_lbl, shift=DOWN * 0.08),
                  FadeIn(size_lbl, shift=UP * 0.1), FadeIn(count_txt), run_time=0.4)

        # The jitter: a handful of cells flicker their opacity — instability you SEE.
        flick = [mat[int(k)] for k in
                 np.random.default_rng(11).choice(len(mat), size=6, replace=False)]
        base_op = {id(c): c.get_fill_opacity() for c in flick}
        for _ in range(2):
            self.play(*[c.animate.set_fill(opacity=min(1.0, base_op[id(c)] + 0.5))
                        for c in flick], run_time=0.18, rate_func=there_and_back)
            self.play(*[c.animate.set_fill(opacity=max(0.0, base_op[id(c)] - 0.4))
                        for c in flick], run_time=0.18, rate_func=there_and_back)
        self.wait(0.12)

        # ============================================================
        # BEAT 2 — Nudge toward one calm plain pattern (blend bar) (~2.54s)
        # ============================================================
        self.next_section("blend")
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
        steady_lbl = mono("nudge toward a calm pattern", 20, INK).next_to(bar, UP, buff=0.5)
        m_lbl = mono("90%  measured", 16, INK_DIM).next_to(meas, DOWN, buff=0.18)
        p_lbl = mono("10%  plain", 15, INK_FAINT).next_to(plain, DOWN, buff=0.18).shift(RIGHT * 0.04)
        blend_grp = VGroup(bar, meas, plain, steady_lbl, m_lbl, p_lbl)

        op_arrow = Arrow(matrix.get_right() + RIGHT * 0.05,
                         [bar.get_left()[0] - 0.2, CENTER_Y - 0.05, 0],
                         stroke_width=2.2, color=INK_GHOST, buff=0.1,
                         max_tip_length_to_length_ratio=0.08)

        # Dim the bottom counter strip during the blend (signaling: bar is focus).
        self.play(FadeIn(steady_lbl, shift=DOWN * 0.1), FadeIn(bar),
                  GrowFromEdge(meas, LEFT), GrowFromEdge(plain, LEFT),
                  FadeIn(m_lbl), FadeIn(p_lbl), GrowArrow(op_arrow),
                  count_txt.animate.set_opacity(0.4), run_time=0.7)

        # Pure-white pulse travels across the blend bar (the single #fff accent).
        pulse = Rectangle(width=0.13, height=0.32, stroke_width=0,
                          fill_color="#ffffff", fill_opacity=0.92)
        pulse.move_to(bar.get_left() + RIGHT * 0.07)
        self.add(pulse)
        self.play(pulse.animate.move_to(bar.get_right() + LEFT * 0.07),
                  run_time=0.85, rate_func=linear)
        self.remove(pulse)
        self.wait(0.5)

        # ============================================================
        # BEAT 3 — Steadier, but still 961 numbers (~1.98s)
        # ============================================================
        self.next_section("steady")
        clean_grid = grid_from(clean).move_to(mat.get_center())
        alpha_lbl = mono("shrinkage   alpha = 0.1", 19, INK).move_to(noisy_lbl)
        self.play(Transform(mat, clean_grid),
                  ReplacementTransform(noisy_lbl, alpha_lbl),
                  count_txt.animate.set_opacity(1.0), run_time=0.85)
        self.play(FadeOut(blend_grp), FadeOut(op_arrow), run_time=0.35)
        # The 961 counter pulses once exactly on "a lot to carry".
        self.play(Indicate(count_txt, scale_factor=1.14, color=INK), run_time=0.55)
        self.wait(0.23)

        # ============================================================
        # BEAT 4 — The squeeze: 961 -> 384 fingerprint (~2.36s)
        # ============================================================
        self.next_section("squeeze")
        gridL = LEFT * 4.3 + UP * CENTER_Y
        self.play(matrix.animate.scale(0.82).move_to(gridL),
                  caret.animate.move_to([stage_x["squeeze"], RULE_Y - 0.22, 0]),
                  *light_stage("squeeze"), run_time=0.5)
        size_lbl.next_to(matrix, DOWN, buff=0.22)

        waist = RoundedRectangle(width=0.5, height=2.0, corner_radius=0.1,
                                 stroke_color=INK, stroke_width=1.8,
                                 fill_color=BG, fill_opacity=1.0)
        waist.move_to([-0.35, CENTER_Y, 0])
        waist_lbl = mono("funnel", 16, INK_DIM).next_to(waist, UP, buff=0.2)

        funnel = VGroup(*[
            Line(matrix.get_right() + UP * y, waist.get_left(),
                 stroke_color=INK_GHOST, stroke_width=0.9)
            for y in np.linspace(-1.0, 1.0, 7)
        ])

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
            r.move_to([bars_c[0] + (k - (nbars - 1) / 2) * bw, bars_c[1] + h / 2, 0])
            bars.add(r)
        baseline = Line([bars.get_left()[0], bars_c[1], 0],
                        [bars.get_right()[0], bars_c[1], 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        targets = [float(hh[k]) for k in range(nbars)]
        for b in bars:
            b.stretch_to_fit_height(0.001)
            b.move_to([b.get_x(), bars_c[1], 0])

        flow = VGroup(*[
            Line(waist.get_right(), [bars.get_left()[0], bars_c[1] + y, 0],
                 stroke_color=INK_GHOST, stroke_width=0.9)
            for y in np.linspace(-0.2, 0.7, 4)
        ])

        dots = VGroup()
        rng = np.random.default_rng(3)
        src_idx = rng.choice(len(mat), size=16, replace=False)
        for ci in src_idx:
            d = Dot(radius=0.03, color=INK, fill_opacity=0.5)
            d.move_to(mat[int(ci)].get_center())
            dots.add(d)
        self.add(dots)

        self.play(Create(waist), FadeIn(waist_lbl),
                  LaggedStart(*[Create(f) for f in funnel], lag_ratio=0.05),
                  LaggedStart(*[Create(f) for f in flow], lag_ratio=0.08),
                  run_time=0.5)

        # converge dots into the waist
        self.play(LaggedStart(*[d.animate.move_to(waist.get_center()) for d in dots],
                              lag_ratio=0.03), run_time=0.45)

        emb_lbl = mono("384 numbers", 22, INK).move_to([bars_c[0], CENTER_Y + 1.35, 0])
        grow_anims = []
        for k, b in enumerate(bars):
            b.target = b.copy()
            b.target.stretch_to_fit_height(targets[k])
            b.target.move_to([b.get_x(), bars_c[1] + targets[k] / 2, 0])
            grow_anims.append(MoveToTarget(b))

        # LOCKSTEP: counter free-falls 961 -> 384 as the bars grow.
        self.play(cnt.animate.set_value(384.0),
                  LaggedStart(*grow_anims, lag_ratio=0.012),
                  Create(baseline), FadeOut(dots, scale=0.2), run_time=0.85)
        self.remove(*dots)
        count_txt.clear_updaters()
        self.play(FadeIn(emb_lbl, shift=DOWN * 0.08), run_time=0.25)

        # ============================================================
        # BEAT 5 — Every snapshot -> a filmstrip of fingerprints (~2.0s)
        # ============================================================
        self.next_section("filmstrip")

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

        FILM_Y = -1.25
        rail_y = 0.7
        fp_card = make_fp(1.0, op=0.85, sw=1.5).move_to([bars_c[0], CENTER_Y - 0.05, 0])

        # Collapse the bar-row into one card; clear the upstream machinery; dim the
        # top context (filmstrip owns the canvas).
        self.play(
            FadeOut(matrix), FadeOut(size_lbl), FadeOut(alpha_lbl),
            FadeOut(waist), FadeOut(waist_lbl), FadeOut(funnel), FadeOut(flow),
            FadeOut(baseline),
            ReplacementTransform(bars, fp_card),
            FadeOut(emb_lbl, target_position=[bars_c[0], CENTER_Y - 0.05, 0], scale=0.4),
            count_txt.animate.set_opacity(0),
            thumb_grp.animate.set_opacity(0.4), ctx_cap.animate.set_opacity(0.3),
            caret.animate.move_to([stage_x["filmstrip"], RULE_Y - 0.22, 0]),
            *light_stage("filmstrip"),
            run_time=0.6)
        self.remove(count_txt)

        # Card drops into the filmstrip band, then the rail of identical cards.
        ncards = 11
        strip = VGroup(*[make_fp(0.62, op=0.78, sw=1.0) for _ in range(ncards)])
        strip.arrange(RIGHT, buff=0.22).move_to([0, FILM_Y, 0])
        mid = ncards // 2
        self.play(fp_card.animate.scale(0.62).move_to(strip[mid].get_center()),
                  run_time=0.4)
        strip.submobjects[mid] = fp_card
        others = VGroup(*[strip[i] for i in range(ncards) if i != mid])
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.12) for c in others],
                              lag_ratio=0.045), run_time=0.55)

        top_rail = Line([X_L, FILM_Y + rail_y, 0], [X_R, FILM_Y + rail_y, 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        bot_rail = Line([X_L, FILM_Y - rail_y, 0], [X_R, FILM_Y - rail_y, 0],
                        stroke_color=INK_FAINT, stroke_width=1.1)
        sprockets = VGroup()
        for x in np.linspace(X_L + 0.25, X_R - 0.25, 26):
            for yy in (FILM_Y + rail_y, FILM_Y - rail_y):
                sprockets.add(Square(0.05, stroke_width=0, fill_color=INK_FAINT,
                                     fill_opacity=0.5).move_to([x, yy, 0]))
        self.play(Create(top_rail), Create(bot_rail),
                  LaggedStart(*[FadeIn(s) for s in sprockets], lag_ratio=0.01),
                  run_time=0.45)

        # ============================================================
        # BEAT 6 — What the reader actually reads (white scan) (~0.78s)
        # ============================================================
        self.next_section("scan")
        read_lbl = mono("what the reader actually reads  ·  50 / sec", 21, INK)
        read_lbl.move_to([0, BOT_Y + 0.05, 0])
        self.play(FadeIn(read_lbl, shift=UP * 0.1), run_time=0.22)

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
        self.play(scan.animate.move_to([X_R, FILM_Y, 0]), run_time=0.4, rate_func=linear)
        strip.remove_updater(card_brighten)
        self.play(FadeOut(scan), Indicate(fp_card, scale_factor=1.06, color=INK),
                  run_time=0.25)
        self.wait(0.2)
