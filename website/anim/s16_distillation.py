# S16 — A teacher voice (cross-modal distillation).
# A teacher/student diptych that FILLS the canvas: the real recorded VOICE lives
# high (top lane: waveform -> WavLM -> layer-9 teacher vectors); the MUSCLE signal
# lives low (bottom lane: fingerprints -> reader -> projection). The drama is the
# student's projection being physically TUGGED upward, frame by frame, until it
# matches the teacher's layer-9 vectors.
#
# Three horizontal zones:
#   TOP strip   (y ~ +2.4..+3.6) : a quiet recap linking to S15's projection head.
#   CENTER      (y ~ -2.4..+2.4) : the two-lane distillation engine + loss diagrams.
#   BOTTOM strip(y ~ -3.4..-3.0) : a live teacher<->student DISTANCE collapsing
#                                  1.00 -> 0.04 (+ a shrink-bar) and a building
#                                  loss-recipe TALLY assembling token by token.
# Ends crossed out: TRAINING ONLY — at real use there is no microphone.
from manim import *
from emg_style import *


def vec_column(vals, cell_w=0.46, cell_h=0.27, sw=1.2, fill_c=INK, base_op=0.0):
    """A short vertical stack of cells whose fill opacity encodes a value 0..1."""
    col = VGroup()
    for v in vals:
        cell = Rectangle(width=cell_w, height=cell_h, stroke_color=INK_GHOST,
                         stroke_width=sw, fill_color=fill_c, fill_opacity=base_op)
        col.add(cell)
    col.arrange(DOWN, buff=0.0)
    return col


def set_col(col, vals):
    for cell, v in zip(col, vals):
        cell.set_fill(INK, opacity=0.12 + 0.78 * float(v))


def cells_from(vals, center, cell_w=0.46, cell_h=0.27, sw=1.2):
    """Build a fresh column matching the styling of vec_column, filled to vals."""
    col = VGroup(*[Rectangle(width=cell_w, height=cell_h, stroke_color=INK_GHOST,
                             stroke_width=sw, fill_color=INK,
                             fill_opacity=0.12 + 0.78 * float(v)) for v in vals])
    col.arrange(DOWN, buff=0.0).move_to(center)
    return col


class Teacher(Scene):
    def construct(self):
        seed()

        # ===============================================================
        # Layout — spread the two lanes to occupy the full vertical extent.
        # ===============================================================
        TOP_Y = 2.35       # AUDIO (teacher) lane
        BOT_Y = -2.35      # EMG (student) lane

        # ---------------------------------------------------------------
        # TOP CONTEXT STRIP — recall S15's projection head, frame the scene.
        # Owns the very top edge alone, centred, so nothing collides with it.
        # ---------------------------------------------------------------
        from_s15 = mono(
            "from S15 · the third head — a 1024-number projection, not for reading text",
            16, INK_FAINT).move_to([0.0, 3.7, 0])

        # ---------------------------------------------------------------
        # Lane tags — single compact line each, far left, tucked just outside
        # their lane (below the recap up top, above the distance strip down low).
        # ---------------------------------------------------------------
        top_tag = mono("THE REAL VOICE · recorded only while training", 16, INK_DIM)
        top_tag.to_edge(LEFT, buff=0.5).set_y(TOP_Y + 0.92)

        bot_tag = mono("THE MUSCLE SIGNAL · the only thing left at real use", 16, INK_DIM)
        bot_tag.to_edge(LEFT, buff=0.5).set_y(BOT_Y - 0.62)

        # ---------------------------------------------------------------
        # TOP LANE: waveform -> WavLM box -> layer-9 teacher vectors
        # ---------------------------------------------------------------
        wave_pts = []
        n = 90
        for i in range(n):
            x = -5.7 + 1.9 * i / (n - 1)
            env = np.exp(-((i - n * 0.5) ** 2) / (2 * (n * 0.28) ** 2))
            y = TOP_Y + 0.46 * env * np.sin(i * 0.9) * (0.5 + 0.5 * np.sin(i * 0.27))
            wave_pts.append([x, y, 0])
        wave = VMobject(stroke_color=INK, stroke_width=2.0)
        wave.set_points_as_corners(wave_pts)

        wavlm = RoundedRectangle(corner_radius=0.1, width=1.95, height=1.02,
                                 stroke_color=INK, stroke_width=1.8,
                                 fill_color=BG, fill_opacity=1.0).move_to([-2.85, TOP_Y, 0])
        wavlm_lab = mono("WavLM", 24, INK).move_to(wavlm.get_center() + UP * 0.14)
        wavlm_sub = mono("self-taught speech", 12, INK_FAINT).move_to(
            wavlm.get_center() + DOWN * 0.27)
        wavlm_grp = VGroup(wavlm, wavlm_lab, wavlm_sub)

        # layer-9 teacher vectors (4 frames, 5 cells each)
        np.random.seed(3)
        t_vals = [0.25 + 0.72 * np.random.rand(5) for _ in range(4)]
        teacher = VGroup(*[vec_column(v) for v in t_vals]).arrange(RIGHT, buff=0.16)
        teacher.move_to([2.55, TOP_Y, 0])
        for col, v in zip(teacher, t_vals):
            set_col(col, v)
        l9_lab = mono("layer 9 · 1024-dim", 16, INK_DIM).next_to(teacher, UP, buff=0.2)

        # ---------------------------------------------------------------
        # BOTTOM LANE: fingerprints -> reader -> projection
        # ---------------------------------------------------------------
        fp = VGroup(*[Square(0.3, stroke_color=INK, stroke_width=1.2, fill_opacity=0)
                      for _ in range(7)]).arrange(RIGHT, buff=0.1).move_to([-4.78, BOT_Y, 0])
        np.random.seed(9)
        for sq in fp:
            sq.set_fill(INK, opacity=0.1 + 0.55 * np.random.rand())

        reader = RoundedRectangle(corner_radius=0.1, width=1.7, height=1.02,
                                  stroke_color=INK, stroke_width=1.8,
                                  fill_color=BG, fill_opacity=1.0).move_to([-2.85, BOT_Y, 0])
        reader_lab = mono("reader", 22, INK).move_to(reader.get_center())

        # student projection — starts flat/blurry, will be pulled toward teacher
        s_start = [np.full(5, 0.5) + 0.05 * (np.random.rand(5) - 0.5) for _ in range(4)]
        student = VGroup(*[vec_column(v) for v in s_start]).arrange(RIGHT, buff=0.16)
        student.move_to([2.55, BOT_Y, 0])
        for col, v in zip(student, s_start):
            set_col(col, v)
        proj_lab = mono("projection · 1024-dim", 16, INK_DIM).next_to(student, DOWN, buff=0.2)

        # flow arrows
        a1 = Arrow(wave.get_right(), wavlm.get_left(), buff=0.12, stroke_width=2.2,
                   color=INK_FAINT, max_tip_length_to_length_ratio=0.18)
        a2 = Arrow(wavlm.get_right(), teacher.get_left(), buff=0.12, stroke_width=2.2,
                   color=INK_FAINT, max_tip_length_to_length_ratio=0.18)
        b1 = Arrow(fp.get_right(), reader.get_left(), buff=0.12, stroke_width=2.2,
                   color=INK_FAINT, max_tip_length_to_length_ratio=0.18)
        b2 = Arrow(reader.get_right(), student.get_left(), buff=0.12, stroke_width=2.2,
                   color=INK_FAINT, max_tip_length_to_length_ratio=0.18)

        # ---------------------------------------------------------------
        # BOTTOM STRIP — distance readout (far left) + loss tally (right).
        # These live OUTSIDE the scaffold VGroup so they persist through the
        # dim/restore in Beat 3.
        # ---------------------------------------------------------------
        DIST_Y = -3.58
        dist_box = mono("teacher ↔ student distance", 14, INK_FAINT)
        dist_box.move_to([-4.95, DIST_Y + 0.34, 0])
        dist = ValueTracker(1.00)
        dist_val = num("1.00", 34, INK).move_to([-5.65, DIST_Y - 0.18, 0])
        # shrink-bar whose width tracks the distance
        BAR_X0, BAR_X1 = -4.7, -2.55     # full-width extent at distance 1.00
        bar_track = Line([BAR_X0, DIST_Y - 0.2, 0], [BAR_X1, DIST_Y - 0.2, 0],
                         stroke_color=INK_GHOST, stroke_width=2.4)
        bar = Line([BAR_X0, DIST_Y - 0.2, 0], [BAR_X1, DIST_Y - 0.2, 0],
                   stroke_color=INK, stroke_width=5.0)

        def bar_updater(m):
            w = max(0.0, dist.get_value())
            x1 = BAR_X0 + (BAR_X1 - BAR_X0) * w
            m.put_start_and_end_on([BAR_X0, DIST_Y - 0.2, 0], [x1, DIST_Y - 0.2, 0])

        # loss-recipe tally (far right, clear of the projection lane label) —
        # built token by token across the beats. Pushed to the very right edge and
        # dropped onto the bottom strip so it never crowds the projection grid.
        TALLY_CX = 5.15
        tally_lab = mono("loss recipe", 14, INK_FAINT).move_to([TALLY_CX, DIST_Y + 0.22, 0])
        # a faint divider keeps the bottom-strip readouts visually separate from
        # the projection lane sitting just above them.
        strip_rule = Line([-6.6, DIST_Y + 0.52, 0], [6.6, DIST_Y + 0.52, 0],
                          stroke_color=INK_GHOST, stroke_width=1.0).set_opacity(0.5)

        # ===============================================================
        # BEAT 0 — POSE the diptych (~2.0s)
        # ===============================================================
        self.play(FadeIn(from_s15, shift=DOWN * 0.12),
                  FadeIn(top_tag, shift=RIGHT * 0.2),
                  FadeIn(bot_tag, shift=RIGHT * 0.2), run_time=0.55)
        self.play(Create(wave), FadeIn(VGroup(*fp), lag_ratio=0.08), run_time=0.55)
        self.play(FadeIn(wavlm_grp, shift=RIGHT * 0.2),
                  FadeIn(reader), FadeIn(reader_lab), run_time=0.4)
        self.play(LaggedStartMap(FadeIn, teacher, lag_ratio=0.1, run_time=0.5),
                  FadeIn(l9_lab),
                  LaggedStartMap(FadeIn, student, lag_ratio=0.1, run_time=0.5),
                  FadeIn(proj_lab))
        # flow arrows + bottom-strip skeleton appear together
        self.play(*[GrowArrow(a) for a in (a1, a2, b1, b2)],
                  FadeIn(dist_box), FadeIn(dist_val), Create(bar_track),
                  Create(bar), FadeIn(tally_lab), Create(strip_rule), run_time=0.45)

        # live distance number + bar updaters
        dist_val.add_updater(lambda m: m.become(
            num(f"{dist.get_value():.2f}", 34, INK).move_to([-5.65, DIST_Y - 0.18, 0])))
        bar.add_updater(bar_updater)

        # ===============================================================
        # BEAT 1 — SAME MOMENT (~1.2s): one recording, two channels.
        # ===============================================================
        cur_x = ValueTracker(-5.75)

        def cursor_pts():
            return ([cur_x.get_value(), BOT_Y - 0.62, 0],
                    [cur_x.get_value(), TOP_Y + 0.62, 0])
        cursor = Line(*cursor_pts(), stroke_color=INK, stroke_width=1.5).set_opacity(0.55)
        cursor.add_updater(lambda m: m.put_start_and_end_on(*cursor_pts()))
        sync_lab = mono("one moment, two recordings", 16, INK_DIM)
        sync_lab.add_updater(lambda m: m.move_to([cur_x.get_value(), 0.0, 0]))
        self.add(cursor, sync_lab)
        self.play(cur_x.animate.set_value(-3.7), run_time=0.75,
                  rate_func=rate_functions.ease_in_out_sine)
        cursor.clear_updaters()
        sync_lab.clear_updaters()
        self.play(FadeOut(cursor), FadeOut(sync_lab), run_time=0.22)

        # ===============================================================
        # BEAT 2 — THE POUR / THE TUG (~2.6s) — the wow moment.
        # Dashed lines connect each teacher column down to its student column;
        # pulses run down while student cells morph to match teacher; in sync
        # the bottom distance free-falls 1.00 -> 0.04 and the bar collapses.
        # ===============================================================
        pour = VGroup()
        for tc, sc in zip(teacher, student):
            ln = DashedLine(tc.get_bottom(), sc.get_top(), dash_length=0.08,
                            stroke_color=INK_FAINT, stroke_width=1.6)
            pour.add(ln)
        self.play(LaggedStart(*[Create(ln) for ln in pour],
                              lag_ratio=0.12, run_time=0.7))

        pulses = VGroup(*[Dot(radius=0.055, color=INK).move_to(ln.get_start())
                          for ln in pour])
        self.add(pulses)
        self.play(
            *[d.animate.move_to(ln.get_end()) for d, ln in zip(pulses, pour)],
            *[col.animate.become(cells_from(tv, col.get_center()))
              for col, tv in zip(student, t_vals)],
            dist.animate.set_value(0.04),
            run_time=1.35, rate_func=rate_functions.ease_in_out_sine)
        self.remove(pulses)

        # flash the now-tiny distance number
        self.play(Indicate(dist_val, color=INK, scale_factor=1.3), run_time=0.4)

        pull_lab = mono("pulled toward the teacher, frame by frame", 18, INK).move_to(
            [0.0, 0.0, 0])
        self.play(FadeIn(pull_lab, shift=UP * 0.15), run_time=0.35)
        self.wait(0.15)
        self.play(FadeOut(pull_lab), run_time=0.25)

        # ===============================================================
        # BEAT 3 — TWO PULLS NAMED (~2.8s): dim lanes, show two loss diagrams
        # in the clean centre band; the bottom tally assembles in sync.
        # NB: bottom-strip elements are NOT in the scaffold (they persist).
        # ===============================================================
        scaffold = VGroup(top_tag, wave, wavlm_grp, teacher, l9_lab,
                          fp, reader, reader_lab, student, proj_lab, bot_tag,
                          a1, a2, b1, b2, pour, from_s15)
        self.play(scaffold.animate.set_opacity(0.16), run_time=0.45)

        loss_title = mono("two pulls", 24, INK).move_to([0.0, 1.7, 0])
        # A splitter that physically fans the one objective into its two terms,
        # filling the previously-hollow centre spine. Stem drops from the title,
        # then forks left (to L2) and right (to InfoNCE).
        fork_top = [0.0, 1.42, 0]
        fork_knee = [0.0, 0.95, 0]
        split = VGroup(
            Line(fork_top, fork_knee, stroke_color=INK_DIM, stroke_width=2.0),
            Line(fork_knee, [-1.55, 0.62, 0], stroke_color=INK_DIM, stroke_width=2.0),
            Line(fork_knee, [1.55, 0.62, 0], stroke_color=INK_DIM, stroke_width=2.0),
        )
        # the recipe weights sit dead-centre on the spine so the gap reads as
        # meaning, not emptiness: half regression + half contrastive.
        weight_note = mono("½ + ½", 20, INK_DIM).move_to([0.0, 0.05, 0])
        weight_sub = mono("equal weight", 12, INK_FAINT).next_to(
            weight_note, DOWN, buff=0.16)
        divider = VGroup(
            DashedLine([0.0, -0.35, 0], [0.0, -1.05, 0], dash_length=0.08,
                       stroke_color=INK_GHOST, stroke_width=1.4),
            DashedLine([0.0, 0.55, 0], [0.0, 1.2, 0], dash_length=0.08,
                       stroke_color=INK_GHOST, stroke_width=1.4),
        )

        # -- LEFT: L2 regression — two cells joined by a double-arrow.
        t_cell = Rectangle(width=0.46, height=0.46, stroke_color=INK_GHOST,
                           stroke_width=1.6, fill_color=INK, fill_opacity=0.82)
        s_cell = Rectangle(width=0.46, height=0.46, stroke_color=INK_GHOST,
                           stroke_width=1.6, fill_color=INK, fill_opacity=0.5)
        l2_pair = VGroup(t_cell, s_cell).arrange(RIGHT, buff=0.8).move_to([-3.35, 0.1, 0])
        l2_tie = DoubleArrow(t_cell.get_right(), s_cell.get_left(), buff=0.06,
                             stroke_width=2.2, color=INK,
                             max_tip_length_to_length_ratio=0.2)
        l2_t_lab = mono("teacher", 11, INK_FAINT).next_to(t_cell, DOWN, buff=0.14)
        l2_s_lab = mono("student", 11, INK_FAINT).next_to(s_cell, DOWN, buff=0.14)
        l2_name = mono("0.5 · L2", 22, INK).move_to([-3.35, 0.82, 0])
        l2_desc = mono("match the numbers", 15, INK_FAINT).move_to([-3.35, -0.92, 0])
        l2_grp = VGroup(l2_pair, l2_tie, l2_t_lab, l2_s_lab, l2_name, l2_desc)

        # -- RIGHT: InfoNCE contrastive — anchor pulls its own moment in,
        #    pushes two others away.
        anchor = Dot(radius=0.09, color=INK).move_to([2.5, 0.1, 0])
        anc_lab = mono("its moment", 11, INK_FAINT).next_to(anchor, DOWN, buff=0.16)
        match = Dot(radius=0.09, color=INK).move_to([4.1, 0.1, 0])
        others = VGroup(*[Dot(radius=0.07, color=INK_FAINT).move_to([4.1, y, 0])
                          for y in (0.85, -0.6)])
        pull_tie = Line(anchor.get_center(), match.get_center(),
                        stroke_color=INK, stroke_width=2.2)
        repel = VGroup(*[DashedLine(anchor.get_center(), o.get_center(),
                                    dash_length=0.05, stroke_color=INK_GHOST,
                                    stroke_width=1.4) for o in others])
        nce_name = mono("0.5 · InfoNCE", 22, INK).move_to([3.3, 0.82, 0])
        nce_desc = mono("its own moment, push others away", 14, INK_FAINT).move_to(
            [3.3, -0.92, 0])
        nce_sub = mono("τ = 0.1", 13, INK_FAINT).next_to(nce_desc, DOWN, buff=0.14)
        nce_grp = VGroup(anchor, anc_lab, match, others, pull_tie, repel,
                         nce_name, nce_desc, nce_sub)

        self.play(FadeIn(loss_title, shift=DOWN * 0.1),
                  LaggedStartMap(Create, split, lag_ratio=0.3),
                  FadeIn(weight_note), FadeIn(weight_sub),
                  Create(divider), run_time=0.5)

        # LEFT diagram + tally token "0.5·L2" (first token, parked at the
        # tally centre; it will slide left when InfoNCE joins).
        tally_l2 = mono("0.5·L2", 18, INK).move_to([TALLY_CX, DIST_Y - 0.18, 0])
        self.play(FadeIn(l2_name), FadeIn(l2_pair), GrowFromCenter(l2_tie),
                  FadeIn(l2_t_lab), FadeIn(l2_s_lab), FadeIn(l2_desc),
                  FadeIn(tally_l2, shift=UP * 0.1), run_time=0.5)
        # snap the two cells equal
        self.play(s_cell.animate.set_fill(INK, opacity=0.82),
                  Indicate(VGroup(t_cell, s_cell), color=INK, scale_factor=1.14),
                  run_time=0.4)

        # RIGHT diagram
        self.play(FadeIn(nce_name), FadeIn(anchor), FadeIn(anc_lab), FadeIn(match),
                  FadeIn(others), Create(pull_tie), Create(repel),
                  FadeIn(nce_desc), FadeIn(nce_sub), run_time=0.5)
        # pull match IN (ease_out_back), push others OUT and dim them
        self.play(match.animate.move_to([3.15, 0.1, 0]),
                  others.animate.shift(RIGHT * 0.45).set_opacity(0.3),
                  pull_tie.animate.put_start_and_end_on(
                      anchor.get_center(), [3.15, 0.1, 0]).set_stroke(width=3.4),
                  run_time=0.5, rate_func=rate_functions.ease_out_back)
        # tally appends "+ 0.5·InfoNCE" — the full recipe stands assembled,
        # centred on the tally column so it stays clear of the lane label.
        full_recipe = mono("0.5·L2 + 0.5·InfoNCE", 18, INK).move_to(
            [TALLY_CX, DIST_Y - 0.18, 0])
        tally_l2_b = mono("0.5·L2", 18, INK).move_to(
            full_recipe.get_left(), aligned_edge=LEFT)
        tally_nce = mono("+ 0.5·InfoNCE", 18, INK).next_to(tally_l2_b, RIGHT, buff=0.16)
        self.play(ReplacementTransform(tally_l2, tally_l2_b),
                  FadeIn(tally_nce, shift=LEFT * 0.12), run_time=0.45)
        tally_full = VGroup(tally_l2_b, tally_nce)
        self.wait(0.15)

        self.play(FadeOut(VGroup(loss_title, l2_grp, nce_grp, divider,
                                 split, weight_note, weight_sub)),
                  scaffold.animate.set_opacity(1.0), run_time=0.45)

        # ===============================================================
        # BEAT 4 — TRAINING ONLY (~1.6s): cross out the audio lane.
        # ===============================================================
        top_lane = VGroup(top_tag, wave, wavlm_grp, teacher, l9_lab, a1, a2)
        # big two-stroke X spanning the raised audio lane (y ~ +1.4..+3.4).
        # Bold strokes so the TOP zone keeps strong visual mass in the poster.
        cross = VGroup(
            Line([-6.6, 1.45, 0], [6.6, 3.35, 0], stroke_color=INK, stroke_width=5),
            Line([-6.6, 3.35, 0], [6.6, 1.45, 0], stroke_color=INK, stroke_width=5),
        )
        stamp = mono("teacher used in TRAINING only", 28, INK).move_to([0.0, 0.55, 0])
        stamp_sub = mono("at real use there is no microphone", 17, INK_FAINT).next_to(
            stamp, DOWN, buff=0.2)
        stamp_grp = VGroup(stamp, stamp_sub)
        halo = VGroup(*[stamp.copy().set_stroke(width=6 + 3 * i, opacity=0.06)
                        for i in range(3)])

        # keep the crossed-out lane present (not ghosted to nothing) so the upper
        # third still carries the composition — the poster must fill top->bottom.
        self.play(top_lane.animate.set_opacity(0.3),
                  pour.animate.set_opacity(0.0), Create(cross), run_time=0.7)
        self.play(FadeIn(stamp_grp, scale=0.92), FadeIn(halo),
                  Flash(stamp, color=INK, line_length=0.2, num_lines=14,
                        flash_radius=2.5), run_time=0.6)

        # ===============================================================
        # BEAT 5 — REST / POSTER (~1.0s)
        # ===============================================================
        rule = Line([-3.2, -0.45, 0], [3.2, -0.45, 0],
                    stroke_color=INK_GHOST, stroke_width=1.2)
        recap = mono("WavLM layer 9  →  projection", 17, INK_DIM).move_to([0.0, -0.78, 0])
        self.play(Create(rule), FadeIn(recap, shift=UP * 0.1), run_time=0.5)

        dist_val.clear_updaters()
        bar.clear_updaters()
        self.wait(0.65)
