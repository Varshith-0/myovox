# S16 — A teacher voice (cross-modal distillation), refocused on HOW the pull works.
#
# Stage 28 already re-introduced the teacher (waveform -> WavLM -> layer-9) and the
# 'training only / no microphone' framing; stage 30 owns 'close isn't enough'. This
# clip opens ALREADY zoomed onto the two facing vector columns — teacher crisp on
# top, student flat/blurry on bottom — with the pipeline, tags and recap ghosted to
# near-nothing. It then shows the two pulls that make the student match the teacher.
#
# Locked 6-beat sheet (one self.next_section per spoken sentence, timed to dur_sec):
#   1 side by side  hold only the two stacked lanes; ghost everything else.
#   2 match numbers dashed tie-lines drop teacher->student; 'match the numbers'.
#   3 collapse      student cells morph to teacher; distance free-falls 1.00->0.04.
#   4 the trap      one student column flattens to a uniform gray smear + caution
#                   flicker, then snaps back — motivates a second pull.
#   5 InfoNCE       anchor pulls its true partner IN, shoves two rivals OUT/dim.
#   6 recipe        both pulls under one fork; tally '0.5·L2 + 0.5·InfoNCE'; lanes
#                   restore to full opacity for the poster hold.
from manim import *
from emg_style import *


def vec_column(vals, cell_w=0.46, cell_h=0.27, sw=1.2):
    """A vertical stack of cells whose fill opacity encodes a value 0..1."""
    col = VGroup(*[Rectangle(width=cell_w, height=cell_h, stroke_color=INK_GHOST,
                             stroke_width=sw, fill_color=INK,
                             fill_opacity=0.12 + 0.78 * float(v)) for v in vals])
    col.arrange(DOWN, buff=0.0)
    return col


def cells_from(vals, center, cell_w=0.46, cell_h=0.27, sw=1.2):
    """A fresh column matching vec_column styling, filled to vals, at center."""
    col = vec_column(vals, cell_w, cell_h, sw)
    col.move_to(center)
    return col


class Teacher(Scene):
    def construct(self):
        seed()

        TOP_Y = 1.55       # teacher (crisp) lane
        BOT_Y = -1.55      # student (flat/blurry) lane
        COL_X = 0.0        # the two columns sit dead centre

        # ---------------------------------------------------------------
        # GHOSTED CONTEXT — pipeline boxes, waveform, lane tags, the S15 recap.
        # Drawn faintly from the first frame so the two columns are the focus.
        # ---------------------------------------------------------------
        from_s15 = mono("from S15 · the third head, a 1024-number projection", 14,
                        INK_GHOST).move_to([0.0, 3.55, 0])

        wave_pts = []
        nw = 70
        for i in range(nw):
            x = -6.1 + 1.7 * i / (nw - 1)
            env = np.exp(-((i - nw * 0.5) ** 2) / (2 * (nw * 0.28) ** 2))
            y = TOP_Y + 0.4 * env * np.sin(i * 0.9) * (0.5 + 0.5 * np.sin(i * 0.27))
            wave_pts.append([x, y, 0])
        wave = VMobject(stroke_color=INK_GHOST, stroke_width=1.6)
        wave.set_points_as_corners(wave_pts)

        wavlm = RoundedRectangle(corner_radius=0.1, width=1.7, height=0.9,
                                 stroke_color=INK_GHOST, stroke_width=1.4,
                                 fill_color=BG, fill_opacity=1.0).move_to([-3.0, TOP_Y, 0])
        wavlm_lab = mono("WavLM", 20, INK_GHOST).move_to(wavlm.get_center())

        reader = RoundedRectangle(corner_radius=0.1, width=1.5, height=0.9,
                                  stroke_color=INK_GHOST, stroke_width=1.4,
                                  fill_color=BG, fill_opacity=1.0).move_to([-3.0, BOT_Y, 0])
        reader_lab = mono("reader", 18, INK_GHOST).move_to(reader.get_center())

        ghost_ctx = VGroup(from_s15, wave, wavlm, wavlm_lab, reader, reader_lab)

        # ---------------------------------------------------------------
        # THE TWO FACING COLUMNS — the sole focus. 5 cells each.
        # Teacher: crisp, high-contrast. Student: flat / near-uniform / blurry.
        # ---------------------------------------------------------------
        np.random.seed(3)
        t_vals = 0.18 + 0.78 * np.random.rand(5)
        s_vals = np.full(5, 0.5) + 0.04 * (np.random.rand(5) - 0.5)

        teacher = cells_from(t_vals, [COL_X, TOP_Y, 0])
        student = cells_from(s_vals, [COL_X, BOT_Y, 0])

        t_tag = mono("teacher · layer 9", 18, INK_DIM).next_to(teacher, UP, buff=0.22)
        s_tag = mono("student · projection", 18, INK_DIM).next_to(student, DOWN, buff=0.22)

        # short flow arrows from ghosted boxes into each column
        a_in = Line(wavlm.get_right(), teacher.get_left(), stroke_color=INK_GHOST,
                    stroke_width=1.2)
        b_in = Line(reader.get_right(), student.get_left(), stroke_color=INK_GHOST,
                    stroke_width=1.2)
        ghost_ctx.add(a_in, b_in)

        # ---------------------------------------------------------------
        # DISTANCE READOUT (top-right) — teacher<->student gap, with shrink-bar.
        # Lives outside any dim group so it persists across beats.
        # ---------------------------------------------------------------
        DIST_X, DIST_Y = 4.3, 0.0
        dist_lab = mono("gap", 15, INK_FAINT).move_to([DIST_X, DIST_Y + 0.62, 0])
        dist = ValueTracker(1.00)
        dist_val = num("1.00", 40, INK).move_to([DIST_X, DIST_Y, 0])
        dist_val.add_updater(lambda m: m.become(
            num(f"{dist.get_value():.2f}", 40, INK).move_to([DIST_X, DIST_Y, 0])))
        BAR_X0, BAR_X1 = 3.35, 5.25
        BAR_Y = DIST_Y - 0.55
        bar_track = Line([BAR_X0, BAR_Y, 0], [BAR_X1, BAR_Y, 0],
                         stroke_color=INK_GHOST, stroke_width=2.2)
        bar = Line([BAR_X0, BAR_Y, 0], [BAR_X1, BAR_Y, 0],
                   stroke_color=INK, stroke_width=5.0)

        def bar_updater(m):
            w = max(0.0, dist.get_value())
            x1 = BAR_X0 + (BAR_X1 - BAR_X0) * w
            m.put_start_and_end_on([BAR_X0, BAR_Y, 0], [x1, BAR_Y, 0])
        bar.add_updater(bar_updater)
        dist_grp = VGroup(dist_lab, dist_val, bar_track, bar)

        # ===============================================================
        # BEAT 1 — SIDE BY SIDE (~1.79s): hold only the two lanes; ghost rest.
        # ===============================================================
        self.next_section("side_by_side")
        self.add(ghost_ctx)
        self.play(FadeIn(teacher, shift=DOWN * 0.12), FadeIn(t_tag),
                  run_time=0.55)
        self.play(FadeIn(student, shift=UP * 0.12), FadeIn(s_tag),
                  run_time=0.5)
        self.wait(0.45)

        # ===============================================================
        # BEAT 2 — MATCH THE NUMBERS (~2.17s): dashed tie-lines + one label.
        # ===============================================================
        self.next_section("match")
        ties = VGroup(*[
            DashedLine([COL_X, teacher[i].get_bottom()[1], 0],
                       [COL_X, student[i].get_top()[1], 0],
                       dash_length=0.07, stroke_color=INK_FAINT, stroke_width=1.6)
            for i in range(len(teacher))
        ])
        # nudge ties so they read per-cell (spread slightly across the column width)
        for i, ln in enumerate(ties):
            x = COL_X + (i - 2) * 0.07
            ln.put_start_and_end_on([x, teacher[i].get_bottom()[1], 0],
                                    [x, student[i].get_top()[1], 0])
        match_lab = mono("match the numbers", 20, INK).move_to([-3.0, 0.0, 0])

        self.play(FadeIn(dist_grp), run_time=0.4)
        self.play(LaggedStart(*[Create(ln) for ln in ties], lag_ratio=0.12,
                              run_time=0.85))
        self.play(FadeIn(match_lab, shift=UP * 0.1), run_time=0.4)
        self.wait(0.52)

        # ===============================================================
        # BEAT 3 — COLLAPSE (~1.13s): student morphs to teacher; gap free-falls.
        # ===============================================================
        self.next_section("collapse")
        pulses = VGroup(*[Dot(radius=0.05, color=INK).move_to(ln.get_start())
                          for ln in ties])
        self.add(pulses)
        self.play(
            *[d.animate.move_to(ln.get_end()) for d, ln in zip(pulses, ties)],
            student.animate.become(cells_from(t_vals, [COL_X, BOT_Y, 0])),
            dist.animate.set_value(0.04),
            run_time=0.85, rate_func=rate_functions.ease_in_out_sine)
        self.remove(pulses)
        self.play(Indicate(dist_val, color=INK, scale_factor=1.25), run_time=0.28)

        # ===============================================================
        # BEAT 4 — THE TRAP (~2.51s): one column flattens to a gray smear, caution
        # flickers, then snaps back. Motivates a second pull.
        # ===============================================================
        self.next_section("trap")
        self.play(FadeOut(ties), FadeOut(match_lab), run_time=0.35)

        avg_vals = np.full(5, 0.5)            # the dull average
        student_now = cells_from(t_vals, [COL_X, BOT_Y, 0])
        student.become(student_now)
        caution = mono("a dull average", 18, INK).next_to(student, RIGHT, buff=0.45)
        bang = mono("!", 30, WHITE).next_to(student, LEFT, buff=0.4)

        # flatten to uniform smear (and let the gap creep back up to show it's worse)
        self.play(student.animate.become(cells_from(avg_vals, [COL_X, BOT_Y, 0])),
                  dist.animate.set_value(0.55),
                  FadeIn(caution, shift=LEFT * 0.1), run_time=0.85)
        # caution flicker
        self.play(FadeIn(bang, scale=0.7), run_time=0.18)
        self.play(Indicate(bang, color=WHITE, scale_factor=1.4), run_time=0.3)
        self.play(FadeOut(bang), run_time=0.18)
        # snap back to the true (distinct) match
        self.play(student.animate.become(cells_from(t_vals, [COL_X, BOT_Y, 0])),
                  dist.animate.set_value(0.04),
                  FadeOut(caution), run_time=0.5)
        self.wait(0.2)

        # ===============================================================
        # BEAT 5 — INFONCE (~2.48s): second pull — claim your own moment, shove
        # the others away. Dim the lanes; show the anchor/repel diagram alone.
        # ===============================================================
        self.next_section("infonce")
        lanes = VGroup(teacher, student, t_tag, s_tag)
        self.play(lanes.animate.set_opacity(0.18),
                  dist_grp.animate.set_opacity(0.18),
                  ghost_ctx.animate.set_opacity(0.06), run_time=0.45)

        anchor = Dot(radius=0.1, color=INK).move_to([-1.7, 0.1, 0])
        anc_lab = mono("this moment", 14, INK_DIM).next_to(anchor, DOWN, buff=0.2)
        match_dot = Dot(radius=0.1, color=INK).move_to([0.6, 0.1, 0])
        match_lab2 = mono("its partner", 13, INK_FAINT).next_to(match_dot, DOWN, buff=0.2)
        rivals = VGroup(*[Dot(radius=0.08, color=INK_FAINT).move_to([0.6, y, 0])
                          for y in (1.25, -1.0)])
        riv_lab = mono("other moments", 13, INK_FAINT).next_to(rivals[1], DOWN, buff=0.18)

        pull_tie = Line(anchor.get_center(), match_dot.get_center(),
                        stroke_color=INK, stroke_width=2.4)
        repel = VGroup(*[DashedLine(anchor.get_center(), o.get_center(),
                                    dash_length=0.06, stroke_color=INK_GHOST,
                                    stroke_width=1.4) for o in rivals])

        self.play(FadeIn(anchor), FadeIn(anc_lab), FadeIn(match_dot),
                  FadeIn(match_lab2), FadeIn(rivals), FadeIn(riv_lab),
                  Create(pull_tie), Create(repel), run_time=0.6)
        # pull partner IN; shove rivals OUT and dim them
        self.play(
            match_dot.animate.move_to([-0.5, 0.1, 0]),
            match_lab2.animate.shift(LEFT * 1.1),
            rivals.animate.shift(RIGHT * 0.7).set_opacity(0.25),
            riv_lab.animate.set_opacity(0.25),
            pull_tie.animate.put_start_and_end_on(
                anchor.get_center(), [-0.5, 0.1, 0]).set_stroke(width=3.6),
            *[repel[k].animate.put_start_and_end_on(
                anchor.get_center(), rivals[k].get_center() + RIGHT * 0.7)
              for k in range(len(rivals))],
            run_time=0.7, rate_func=rate_functions.ease_out_back)
        nce_lab = mono("claim your moment, push the rest away", 16, INK_DIM).move_to(
            [-0.6, -1.7, 0])
        self.play(FadeIn(nce_lab, shift=UP * 0.1), run_time=0.35)
        self.wait(0.2)

        # ===============================================================
        # BEAT 6 — RECIPE (~1.88s): both pulls under one fork; tally + poster.
        # ===============================================================
        self.next_section("recipe")
        nce_grp = VGroup(anchor, anc_lab, match_dot, match_lab2, rivals, riv_lab,
                         pull_tie, repel, nce_lab)
        self.play(FadeOut(nce_grp), run_time=0.35)

        # restore the lanes for the poster; the gap readout has done its job, so
        # ghost it back so the right-hand fork term owns that space cleanly.
        self.play(lanes.animate.set_opacity(1.0),
                  dist_grp.animate.set_opacity(0.16), run_time=0.4)

        # one fork over the two columns, splitting into the two pulls
        fork_knee = [COL_X, 0.0, 0]
        fork = VGroup(
            Line([COL_X, 0.55, 0], fork_knee, stroke_color=INK_DIM, stroke_width=2.0),
            Line(fork_knee, [-2.3, -0.45, 0], stroke_color=INK_DIM, stroke_width=2.0),
            Line(fork_knee, [2.3, -0.45, 0], stroke_color=INK_DIM, stroke_width=2.0),
        )
        l2_term = mono("0.5 · L2", 22, INK).move_to([-2.3, -0.72, 0])
        l2_sub = mono("copy the numbers", 14, INK_FAINT).next_to(l2_term, DOWN, buff=0.14)
        nce_term = mono("0.5 · InfoNCE", 22, INK).move_to([2.3, -0.72, 0])
        nce_sub = mono("keep each moment distinct", 14, INK_FAINT).next_to(
            nce_term, DOWN, buff=0.14)

        self.play(LaggedStartMap(Create, fork, lag_ratio=0.3, run_time=0.4),
                  FadeIn(VGroup(l2_term, l2_sub), shift=RIGHT * 0.1),
                  FadeIn(VGroup(nce_term, nce_sub), shift=LEFT * 0.1))

        # the recipe tally — the single bright payoff line, with glow.
        recipe = serif("0.5·L2 + 0.5·InfoNCE", 30, WHITE).move_to([0.0, -3.2, 0])
        glow_recipe = glow(recipe.copy())
        self.add(glow_recipe)
        self.play(FadeIn(recipe, shift=UP * 0.12),
                  Indicate(recipe, scale_factor=1.08, color=WHITE),
                  glow_recipe.animate.set_opacity(0.0), run_time=0.55)
        self.remove(glow_recipe)

        dist_val.clear_updaters()
        bar.clear_updaters()
        self.wait(0.33)
