# website/anim/s12_ctc.py  —  S12 "Lining up (CTC)"  (centerpiece)
#
# CTC's "aha": timing is UNLABELED, yet the model still learns the right ORDER
# of sounds — because MANY different per-frame timings collapse to the same word,
# and training rewards every one of them.
#
# Three-zone full-canvas composition (3b1b: pose -> build -> transform -> name):
#   TOP  (y~+2.4..+3.6)  CONTEXT: a slim ~150-frame ghost ruler carried over from
#                  S11's per-time-slice timeline + its ∅ marker; "~150 frames"
#                  (left) / "~30 sounds" (right). A bright read-head index travels
#                  it in lockstep with the center action — naming time, slice by
#                  slice. Stays present (dimmed) the whole clip as the time anchor.
#   CENTER(-1.8..+2.1) MECHANISM: a 9-cell alignment row morphs out of the ruler;
#                  a read-head sweeps + names ∅ K K ∅ AE AE AE T ∅; a vertical
#                  collapse pipeline merges repeats -> "K AE T ∅" -> drops blanks
#                  -> "K AE T" -> big serif "cat". Then the WOW: three DIFFERENT
#                  9-cell timing rows sweep at once and DRAIN through one brace +
#                  arrow into a single shared bright "K AE T".
#   BOTTOM(-3.6..-2.6) TAKEAWAY: a live Σ tally — "valid alignments -> same word"
#                  ticks 1 -> 2 -> 3 -> "many" as each path lands, beside
#                  "Σ over all paths" filling token by token; a progress underline
#                  grows L->R; resolves to "training rewards every timing that
#                  spells the same sounds."
#   final          a dense, balanced poster holds ~0.6 s.
from manim import *
from emg_style import *


def alignment_row(labs, sq=0.34, buff=0.10, fs=20):
    """A row of frame-squares with a phoneme-or-blank label inside each.
    Returns (group, squares, texts). Blanks are dim."""
    squares = VGroup(*[
        Square(sq, stroke_color=INK_GHOST, stroke_width=1.2, fill_opacity=0)
        for _ in labs
    ]).arrange(RIGHT, buff=buff)
    texts = VGroup()
    for i, l in enumerate(labs):
        c = INK_FAINT if l == "∅" else INK
        texts.add(mono(l, fs, c).move_to(squares[i]))
    return VGroup(squares, texts), squares, texts


class CTC(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B0 — CARRY-OVER: the TOP frame-ruler (~150 ghost ticks) + ∅,
        #      echoing S11's per-time-slice timeline. Pose the puzzle.
        # =================================================================
        self.next_section("carryover")

        N_TICKS = 150
        RULER_W = 11.4
        ruler_y = 3.0
        # A dense run of thin vertical ticks reads as "~150 frames" of unlabeled
        # time — the same stream S11's timeline left us with.
        ticks = VGroup(*[
            Line(UP * 0.16, DOWN * 0.16, stroke_color=INK_GHOST, stroke_width=1.0)
            for _ in range(N_TICKS)
        ]).arrange(RIGHT, buff=(RULER_W - N_TICKS * 0.0) / N_TICKS * 0.0 + 0.0)
        # arrange with even spacing across RULER_W:
        ticks.arrange(RIGHT, buff=RULER_W / (N_TICKS - 1) - ticks[0].width)
        ticks.set_width(RULER_W)
        ticks.move_to(UP * ruler_y)
        base = Line(ticks.get_left() + DOWN * 0.16, ticks.get_right() + DOWN * 0.16,
                    stroke_color=INK_GHOST, stroke_width=1.2)

        f_lab = mono("~150 frames", 18, INK_DIM).next_to(ticks, LEFT, buff=0.34)
        s_lab = mono("~30 sounds", 18, INK_DIM).next_to(ticks, RIGHT, buff=0.34)
        # keep tags inside the frame
        if f_lab.get_left()[0] < -7.0:
            f_lab.next_to(ticks, UP, buff=0.10).align_to(ticks, LEFT)
        if s_lab.get_right()[0] > 7.0:
            s_lab.next_to(ticks, UP, buff=0.10).align_to(ticks, RIGHT)

        self.play(
            LaggedStartMap(Create, ticks, lag_ratio=0.003, run_time=0.65),
            Create(base),
            FadeIn(f_lab, shift=RIGHT * 0.1),
            FadeIn(s_lab, shift=LEFT * 0.1),
            run_time=0.65,
        )

        # a faint pulse sweeps tick[0] -> tick[-1]: frames arrive as a stream.
        pulse = Rectangle(width=0.18, height=0.46, stroke_width=0,
                          fill_color=INK, fill_opacity=0.22).move_to(ticks[0])
        self.add(pulse)
        self.play(pulse.animate.move_to(ticks[-1]), run_time=0.42, rate_func=linear)
        self.remove(pulse)

        # a small ∅ docks at the ruler's right end — continuing from S11's blank.
        blank_dock = serif("∅", 22, INK_DIM).next_to(s_lab, DOWN, buff=0.14)
        recap = mono("nobody labeled which frame is which sound", 17, INK_FAINT)
        recap.next_to(ticks, DOWN, buff=0.26).set_x(ticks.get_x())
        top_ruler = VGroup(ticks, base, f_lab, s_lab, blank_dock)

        # bring up ∅ + recap, then settle the ruler into its dimmed anchor state.
        self.play(FadeIn(blank_dock, scale=0.7),
                  FadeIn(recap, shift=UP * 0.1), run_time=0.4)
        self.play(top_ruler.animate.set_opacity(0.6),
                  recap.animate.set_opacity(0.5), run_time=0.25)

        # A bright read-head index that will travel the ruler in lockstep with the
        # center action — shared ValueTracker so top + center share one clock.
        clk = ValueTracker(0.0)   # 0..1 across the 9-cell window
        # the 9-cell window maps to a contiguous slab of ticks (frames 60..68).
        slab_lo, slab_hi = 60, 68
        idx_marker = Triangle(stroke_width=0, fill_color=INK,
                              fill_opacity=0.95).scale(0.10).rotate(PI)
        idx_marker.move_to(ticks[slab_lo].get_top() + UP * 0.18)

        def update_idx(m):
            f = clk.get_value()
            i = int(round(slab_lo + f * (slab_hi - slab_lo)))
            i = max(slab_lo, min(slab_hi, i))
            m.move_to(ticks[i].get_top() + UP * 0.18)
        idx_marker.add_updater(update_idx)

        # =================================================================
        # B1 — ZOOM + NAME: morph a slab of the ruler into a 9-cell row,
        #      a read-head sweeps it naming ∅ K K ∅ AE AE AE T ∅.
        # =================================================================
        self.next_section("name")

        labs = ["∅", "K", "K", "∅", "AE", "AE", "AE", "T", "∅"]
        row, sq, tx = alignment_row(labs, sq=0.50, buff=0.16, fs=26)
        row.move_to(UP * 1.45)

        # the slab of ticks that becomes the row, lit so the zoom is legible.
        slab = VGroup(*[ticks[i] for i in range(slab_lo, slab_hi + 1)])
        slab_box = SurroundingRectangle(slab, color=INK_FAINT, buff=0.06,
                                        stroke_width=1.4)
        self.play(Create(slab_box), FadeIn(idx_marker), run_time=0.3)
        # zoom: the lit slab transforms down into the 9 empty cells.
        self.play(
            ReplacementTransform(slab_box, sq),
            *[ticks[i].animate.set_stroke(INK_FAINT, width=1.4)
              for i in range(slab_lo, slab_hi + 1)],
            run_time=0.6,
        )

        name_cap = mono("guess a sound — or blank ∅ — per frame", 18, INK_FAINT)
        name_cap.next_to(sq, UP, buff=0.34)
        self.play(FadeIn(name_cap), run_time=0.3)

        # read-head sweeps the row; labels pop as it passes; top index travels too.
        n = len(tx)
        for t in tx:
            t.set_opacity(0.0)
        self.add(tx)
        head = sq[0].copy().set_stroke(INK, width=3.0).set_fill(INK, 0.08)
        self.add(head)

        def update_head(m):
            i = min(int(clk.get_value() * (n - 1) + 0.5), n - 1)
            m.move_to(sq[i])
        head.add_updater(update_head)

        def make_reveal(idx):
            def upd(m):
                m.set_opacity(1.0 if clk.get_value() * (n - 1) >= idx - 0.05 else 0.0)
            return upd
        for i, t in enumerate(tx):
            t.add_updater(make_reveal(i))

        self.play(clk.animate.set_value(1.0), run_time=1.05, rate_func=linear)
        head.clear_updaters()
        for t in tx:
            t.clear_updaters()
            t.set_opacity(1.0)
        idx_marker.clear_updaters()
        self.play(FadeOut(head, run_time=0.2))

        # =================================================================
        # B2 — MERGE REPEATS: underline runs, drop into "K AE T ∅" one zone down.
        # =================================================================
        self.next_section("merge")

        merged_labs = ["K", "AE", "T", "∅"]
        merged_row, m_sq, m_tx = alignment_row(merged_labs, sq=0.50, buff=0.34, fs=28)
        merged_row.move_to(DOWN * 0.15)
        step1 = mono("merge repeats", 17, INK_FAINT).next_to(merged_row, LEFT, buff=0.5)
        if step1.get_left()[0] < -6.9:
            step1.next_to(merged_row, UP, buff=0.18).align_to(merged_row, LEFT)

        src_groups = [
            VGroup(tx[1], tx[2]),         # K K
            VGroup(tx[4], tx[5], tx[6]),  # AE AE AE
            VGroup(tx[7]),                # T
            VGroup(tx[0], tx[3], tx[8]),  # blanks -> ∅
        ]
        runs = VGroup(
            Line(sq[1].get_corner(DL), sq[2].get_corner(DR),
                 stroke_color=INK, stroke_width=2.4),
            Line(sq[4].get_corner(DL), sq[6].get_corner(DR),
                 stroke_color=INK, stroke_width=2.4),
            Line(sq[7].get_corner(DL), sq[7].get_corner(DR),
                 stroke_color=INK, stroke_width=2.4),
        ).shift(DOWN * 0.07)
        self.play(LaggedStartMap(Create, runs, lag_ratio=0.2, run_time=0.38))
        self.play(
            *[TransformFromCopy(src, m_tx[i]) for i, src in enumerate(src_groups)],
            *[Create(s) for s in m_sq],
            FadeIn(step1, shift=RIGHT * 0.1),
            FadeOut(runs),
            run_time=0.65,
        )

        # =================================================================
        # B3 — DROP BLANKS -> WORD: cross the ∅, drop "K AE T", rise to "cat".
        # =================================================================
        self.next_section("word")

        kept_labs = ["K", "AE", "T"]
        kept_row, k_sq, k_tx = alignment_row(kept_labs, sq=0.50, buff=0.34, fs=28)
        kept_row.move_to(DOWN * 1.55)
        step2 = mono("drop blanks", 17, INK_FAINT).next_to(kept_row, LEFT, buff=0.5)
        if step2.get_left()[0] < -6.9:
            step2.next_to(kept_row, UP, buff=0.18).align_to(kept_row, LEFT)

        blank_cell = VGroup(m_sq[3], m_tx[3])
        cross = Cross(m_sq[3], stroke_color=INK, stroke_width=2.4).scale(0.55)
        self.play(Create(cross), run_time=0.22)
        self.play(
            blank_cell.animate.set_opacity(0.0),
            cross.animate.set_opacity(0.0),
            *[TransformFromCopy(VGroup(m_sq[i], m_tx[i]),
                                VGroup(k_sq[i], k_tx[i])) for i in range(3)],
            FadeIn(step2, shift=RIGHT * 0.1),
            run_time=0.6,
        )
        self.remove(cross)

        # rise into a big serif "cat" — the single #fff peak of this beat.
        word = serif("cat", 60, INK).move_to(DOWN * 2.95)
        self.play(TransformFromCopy(k_tx, word), run_time=0.55)
        self.play(Indicate(word, scale_factor=1.16, color=WHITE), run_time=0.45)
        self.wait(0.12)

        # =================================================================
        # B4 — WOW: three DIFFERENT timings, ONE answer.  +  bottom Σ-tally.
        # =================================================================
        self.next_section("payoff")

        # clear the single pipeline (keep the TOP ruler + recap as the anchor).
        pipeline = VGroup(row, sq, tx, merged_row, m_sq, m_tx,
                          kept_row, k_sq, k_tx, step1, step2, word, name_cap, slab)
        self.play(FadeOut(pipeline, shift=DOWN * 0.2),
                  top_ruler.animate.set_opacity(0.45),
                  recap.animate.set_opacity(0.32),
                  run_time=0.42)
        self.remove(*[m for m in self.mobjects if m not in
                      (top_ruler, recap, idx_marker)])
        self.add(top_ruler, recap)

        title = mono("many timings  →  one answer", 24, INK_DIM).move_to(UP * 1.95)
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.3)

        # three valid alignments of the SAME word, different durations / blanks.
        aligns = [
            ["∅", "K", "K", "∅", "AE", "AE", "AE", "T", "∅"],
            ["K", "K", "K", "AE", "AE", "T", "T", "T", "∅"],
            ["∅", "∅", "K", "AE", "AE", "AE", "AE", "∅", "T"],
        ]
        rows = VGroup()
        row_objs = []
        for a in aligns:
            r, rsq, rtx = alignment_row(a, sq=0.40, buff=0.14, fs=20)
            rows.add(r)
            row_objs.append((rsq, rtx))
        rows.arrange(DOWN, buff=0.34).move_to(UP * 0.55)
        self.play(LaggedStartMap(FadeIn, rows, lag_ratio=0.15, run_time=0.5))

        # ---- BOTTOM: the live Σ-tally strip (parked strictly below y=-2.6) ----
        # Fixed layout so nothing jumps: a reserved counter slot, then "paths",
        # then a gap, then "Σ  over all paths" whose tokens fill in.
        tally_label = mono("valid alignments  →  same word", 17, INK_FAINT)
        cnt_slot = ORIGIN  # a fixed anchor point; filled in below.
        cnt_word = mono("paths", 18, INK_FAINT)
        sig = serif("Σ", 36, INK)
        paths_tok = mono("over all paths", 18, INK_DIM)

        cnt = ValueTracker(0)

        def fmt_cnt(v):
            v = int(round(v))
            return str(v) if v < 4 else "many"
        # placeholder to size the fixed slot to the widest readout ("many").
        slot_w = mono("many", 44, INK).width
        cnt_read = counter(cnt, fmt=fmt_cnt, s=44, c=INK, at=ORIGIN)

        # static skeleton: [ slot ] paths      Σ  over all paths
        slot = Rectangle(width=slot_w, height=0.6, stroke_opacity=0, fill_opacity=0)
        left_block = VGroup(slot, cnt_word).arrange(RIGHT, buff=0.22)
        sig_grp = VGroup(sig, paths_tok).arrange(RIGHT, buff=0.20)
        bottom = VGroup(left_block, sig_grp).arrange(RIGHT, buff=1.2)
        bottom.move_to(DOWN * 3.02)
        # pin the counter to the (now positioned) reserved slot centre.
        cnt_read.clear_updaters()
        cnt_read.add_updater(lambda x: x.become(
            num(fmt_cnt(cnt.get_value()), 44, INK).move_to(slot.get_center())))

        tally_label.next_to(bottom, UP, buff=0.20).set_x(bottom.get_x())

        # progress underline beneath the whole bottom strip.
        prog_track = Line(LEFT * 4.4, RIGHT * 4.4, stroke_color=INK_GHOST,
                          stroke_width=1.4).move_to(DOWN * 3.66)
        prog = Line(prog_track.get_start(), prog_track.get_start(),
                    stroke_color=INK, stroke_width=2.6)
        progT = ValueTracker(0.0)
        prog.add_updater(lambda m: m.put_start_and_end_on(
            prog_track.get_start(),
            prog_track.point_from_proportion(max(1e-3, progT.get_value()))))

        # bring up the skeleton: label, "paths", Σ, the live counter, the track.
        self.add(cnt_read)
        self.play(
            FadeIn(tally_label, shift=UP * 0.08),
            FadeIn(cnt_word),
            FadeIn(sig),
            Create(prog_track),
            run_time=0.4,
        )
        self.add(prog)

        # three read-heads sweep ALL rows at once — three distinct valid paths.
        hls = VGroup(*[
            rsq[0].copy().set_stroke(INK, width=2.6).set_fill(INK, 0.08)
            for rsq, _ in row_objs
        ])
        self.add(hls)
        sweepT = ValueTracker(0.0)
        n9 = 9
        for j, (rsq, _) in enumerate(row_objs):
            def mk(rsq):
                def upd(m):
                    i = min(int(sweepT.get_value() * (n9 - 1) + 0.5), n9 - 1)
                    m.move_to(rsq[i])
                return upd
            hls[j].add_updater(mk(rsq))

        # land the three paths one after another, ticking the tally + Σ tokens.
        # the count climbs 1 -> 2 -> 3 as each path's sweep completes — the
        # counter bumps inside each sweep play so the climb stays synced.
        self.play(sweepT.animate.set_value(0.34),
                  cnt.animate.set_value(1),
                  progT.animate.set_value(0.33),
                  FadeIn(paths_tok, shift=RIGHT * 0.1),
                  run_time=0.5, rate_func=linear)
        self.play(sweepT.animate.set_value(0.67),
                  cnt.animate.set_value(2),
                  progT.animate.set_value(0.66),
                  run_time=0.42, rate_func=linear)
        self.play(sweepT.animate.set_value(1.0),
                  cnt.animate.set_value(3),
                  progT.animate.set_value(1.0),
                  run_time=0.42, rate_func=linear)
        for h in hls:
            h.clear_updaters()
        self.play(FadeOut(hls), run_time=0.18)

        # one shared collapsed answer, gathered by a brace + arrow.
        answer = mono("K  AE  T", 40, INK).move_to(DOWN * 1.55)
        brace = Brace(rows, DOWN, color=INK_GHOST, buff=0.18).set_stroke(width=1)
        arrow = Arrow(brace.get_bottom() + DOWN * 0.02,
                      answer.get_top() + UP * 0.12,
                      buff=0.1, stroke_width=3.0, color=INK_FAINT,
                      max_tip_length_to_length_ratio=0.18)
        self.play(GrowFromCenter(brace), GrowArrow(arrow), run_time=0.4)
        self.play(Write(answer), cnt.animate.set_value(4), run_time=0.45)
        self.play(Circumscribe(answer, color=WHITE, stroke_width=2.4,
                               buff=0.18, run_time=0.55))

        # =================================================================
        # B5 — NAME IT + POSTER HOLD.
        # =================================================================
        self.next_section("name_it")

        cnt.clear_updaters()
        cnt_read.clear_updaters()
        prog.clear_updaters()
        punch = mono("training rewards every timing that spells the same sounds",
                     18, INK_DIM)
        punch.move_to(DOWN * 3.62)
        # swap the progress track/underline area for the resolved punchline.
        self.play(
            FadeOut(prog_track), FadeOut(prog),
            FadeOut(tally_label, shift=DOWN * 0.1),
            FadeIn(punch, shift=UP * 0.1),
            run_time=0.45,
        )

        self.wait(0.6)
