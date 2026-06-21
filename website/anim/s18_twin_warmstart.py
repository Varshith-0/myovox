# S18 — Two readers (warm-start + tougher twin)
#
# A living family tree, full-canvas, in three persistent horizontal zones:
#   TOP  (y ~ +2.4..+3.6): a quiet ANCESTRY strip — a ghosted "old baseline model"
#         glyph anchored upper-LEFT (this IS S16/S17), a hairline INK_GHOST bracket
#         spanning the top reading "ancestor -> two new readers", and a small label
#         "from the earlier model (S16/S17)". It frames everything as descent from
#         the previous stage and never moves; only its inheritance arcs reach DOWN
#         into the center during the warm-start beat, then it dims to INK_GHOST.
#   CENTER (y ~ -1.8..+2.0): the MECHANISM. Reader A is built on the left-center
#         from inherited tiers (front-end + heads copied as solid INK; Conformer
#         middle dashed = "fresh" then swept solid = "trained"). Reader B (the
#         twin) grows on the right-center from a "same design" arc, then absorbs a
#         tight cascade of five defence pulses that flex its frame and thicken its
#         stroke. In the climax both readers emit a 5-cell ARPABET error strip that
#         slides DOWN into the bottom zone; a 5-cell agreement meter forms on the
#         center axis showing they slip on DIFFERENT positions (idx 1 vs idx 2).
#   BOTTOM (y ~ -3.6..-2.6): a running TAKEAWAY rail — first a warm-start progress
#         bar ("inherited: front-end / heads / middle: training..."), then a defence
#         TALLY ("defences fired: 0/5") counting up, then the punchline in two
#         clauses ("they fail differently -> averaging recovers each other's miss")
#         with a tiny twin "20.9% PER" pair tied by a dashed line: the shared wall.
#
# wow: inheritance flows DOWN from a single ancestor into two diverging descendants,
# then the snap reveal that both readers hit the IDENTICAL 20.9% wall yet their
# error strips light up on DIFFERENT cells — same ceiling, different cracks. The
# single pure-#fff accent is reserved for the tied "20.9%" pair on its final Indicate.
# Strict monochrome — emphasis via opacity, stroke width, scale, glow.
from manim import *
from emg_style import *

WHITE_ACCENT = "#ffffff"


def reader_block(label, label_size=19, w=2.0, mid_h=0.84, side_h=0.62):
    """A stacked 3-tier reader: front-end / middle / heads, with labelled tiers."""
    front = RoundedRectangle(width=w, height=side_h, corner_radius=0.08,
                             stroke_color=INK, stroke_width=1.7, fill_opacity=0)
    mid = RoundedRectangle(width=w, height=mid_h, corner_radius=0.08,
                           stroke_color=INK, stroke_width=1.7, fill_opacity=0)
    heads = RoundedRectangle(width=w, height=side_h, corner_radius=0.08,
                             stroke_color=INK, stroke_width=1.7, fill_opacity=0)
    stack = VGroup(front, mid, heads).arrange(DOWN, buff=0.17)

    f_lab = mono("front-end", 15, INK_DIM).move_to(front)
    m_lab = mono("Conformer", 15, INK_DIM).move_to(mid)
    h_lab = mono("heads", 15, INK_DIM).move_to(heads)
    labs = VGroup(f_lab, m_lab, h_lab)

    title = mono(label, label_size, INK).next_to(stack, UP, buff=0.26)
    group = VGroup(stack, labs, title)
    group.front, group.mid, group.heads = front, mid, heads
    group.f_lab, group.m_lab, group.h_lab = f_lab, m_lab, h_lab
    group.labs = labs
    group.title = title
    group.stack = stack
    return group


def mini_glyph(c=INK_GHOST, w=0.86, sw=1.2):
    """A tiny 3-tier model glyph for the ancestry strip (the old baseline model)."""
    bars = VGroup(
        RoundedRectangle(width=w, height=0.20, corner_radius=0.04,
                         stroke_color=c, stroke_width=sw, fill_opacity=0),
        RoundedRectangle(width=w, height=0.28, corner_radius=0.04,
                         stroke_color=c, stroke_width=sw, fill_opacity=0),
        RoundedRectangle(width=w, height=0.20, corner_radius=0.04,
                         stroke_color=c, stroke_width=sw, fill_opacity=0),
    ).arrange(DOWN, buff=0.07)
    return bars


class TwoReaders(Scene):
    def construct(self):
        seed()

        READER_Y = 0.05
        AX, BX = -3.55, 3.55

        # ============================================================
        # BEAT 1 — POSE / ancestry  (top strip + empty reader A + bottom track)
        # ============================================================
        self.next_section("ancestry")

        # --- TOP ancestry strip (persistent context) --------------------
        bracket = VGroup()
        bracket_y = 3.45
        hline = Line(LEFT * 6.4, RIGHT * 6.4, stroke_color=INK_GHOST, stroke_width=1.1).move_to(UP * bracket_y)
        ltick = Line(UP * bracket_y, UP * (bracket_y - 0.16), stroke_color=INK_GHOST, stroke_width=1.1).move_to(LEFT * 6.4 + UP * (bracket_y - 0.08))
        rtick = Line(UP * bracket_y, UP * (bracket_y - 0.16), stroke_color=INK_GHOST, stroke_width=1.1).move_to(RIGHT * 6.4 + UP * (bracket_y - 0.08))
        brk_lab = mono("ancestor  ->  two new readers", 16, INK_FAINT).move_to(UP * (bracket_y + 0.22))
        bracket.add(hline, ltick, rtick, brk_lab)

        # ghosted old-model glyph anchored upper-LEFT — this IS S16/S17
        glyph = mini_glyph(INK_GHOST).move_to(LEFT * 5.55 + UP * 2.78)
        glyph_box = SurroundingRectangle(glyph, color=INK_GHOST, stroke_width=1.0, buff=0.14, corner_radius=0.06)
        glyph_lab = mono("from the earlier model", 14, INK_FAINT).next_to(glyph_box, RIGHT, buff=0.22)
        glyph_sub = mono("(S16 / S17)", 12, INK_GHOST).next_to(glyph_lab, DOWN, buff=0.08, aligned_edge=LEFT)
        old_glyph = VGroup(glyph, glyph_box, glyph_lab, glyph_sub)

        self.play(
            Create(hline), Create(ltick), Create(rtick),
            FadeIn(brk_lab, shift=DOWN * 0.1),
            run_time=0.5)
        self.play(
            LaggedStartMap(Create, glyph, lag_ratio=0.15),
            Create(glyph_box),
            FadeIn(glyph_lab), FadeIn(glyph_sub),
            run_time=0.5)

        # --- CENTER: empty Reader-A frame on the left (fresh) -----------
        rA = reader_block("new reader", w=2.05).move_to(LEFT * AX * 0 + np.array([AX, READER_Y, 0]))
        # front + heads as faint INK_FAINT outlines (not yet inherited)
        rA.front.set_stroke(INK_FAINT, 1.5, opacity=0.5)
        rA.heads.set_stroke(INK_FAINT, 1.5, opacity=0.5)
        rA.f_lab.set_color(INK_FAINT).set_opacity(0.7)
        rA.h_lab.set_color(INK_FAINT).set_opacity(0.7)
        # Conformer middle dashed = "fresh"
        rA.mid.set_stroke(opacity=0)
        fresh_mid = DashedVMobject(rA.mid.copy().set_stroke(INK, 1.7, opacity=0.6),
                                   num_dashes=28, dashed_ratio=0.5)
        fresh_lab = mono("fresh", 15, INK_FAINT).move_to(rA.m_lab)
        rA.m_lab.set_opacity(0)

        self.play(
            LaggedStart(
                Create(rA.front), Create(fresh_mid), Create(rA.heads),
                lag_ratio=0.18),
            FadeIn(rA.f_lab), FadeIn(fresh_lab), FadeIn(rA.h_lab),
            FadeIn(rA.title),
            run_time=0.6)

        # --- BOTTOM: empty warm-start progress track --------------------
        rail_y = -3.05
        bar_w = 6.4
        track = RoundedRectangle(width=bar_w, height=0.34, corner_radius=0.17,
                                 stroke_color=INK_GHOST, stroke_width=1.4, fill_opacity=0)
        track.move_to(np.array([0, rail_y, 0]))
        rail_lab = mono("inherited:  front-end ...   heads ...   middle ...", 15, INK_FAINT)
        rail_lab.next_to(track, UP, buff=0.18)
        # the fill (three logical segments), driven by a ValueTracker
        fill_pt = ValueTracker(0.0)  # 0..1 fraction of bar filled
        fill_left = track.get_left() + RIGHT * 0.04 + UP * 0  # inner left edge
        inner_w = bar_w - 0.08

        def make_fill():
            frac = fill_pt.get_value()
            if frac <= 0.001:
                return VGroup()
            f = RoundedRectangle(width=inner_w * frac, height=0.24, corner_radius=0.12,
                                 stroke_width=0, fill_color=INK, fill_opacity=0.9)
            f.move_to(fill_left + RIGHT * (inner_w * frac / 2))
            return f
        fill = always_redraw(make_fill)

        # segment ticks at 1/3, 2/3 of the bar
        seg1 = Line(UP * 0.13, DOWN * 0.13, stroke_color=INK_GHOST, stroke_width=1.0).move_to(fill_left + RIGHT * (inner_w / 3))
        seg2 = Line(UP * 0.13, DOWN * 0.13, stroke_color=INK_GHOST, stroke_width=1.0).move_to(fill_left + RIGHT * (2 * inner_w / 3))
        VGroup(seg1, seg2).shift(np.array([0, rail_y, 0]))

        self.add(fill)
        self.play(Create(track), Create(seg1), Create(seg2), FadeIn(rail_lab), run_time=0.5)

        # ============================================================
        # BEAT 2 — BUILD / warm-start inheritance (arcs DOWN from ancestor)
        # ============================================================
        self.next_section("warmstart")

        # two curved arcs reach from the top old-model glyph DOWN into A's front + heads
        glyph_anchor = glyph.get_bottom() + DOWN * 0.04
        path_f = ArcBetweenPoints(glyph_anchor, rA.front.get_left() + LEFT * 0.04, angle=0.7)
        path_h = ArcBetweenPoints(glyph_anchor, rA.heads.get_left() + LEFT * 0.04, angle=0.9)
        path_f.set_stroke(INK_GHOST, 1.3)
        path_h.set_stroke(INK_GHOST, 1.3)
        inherit_tag = mono("a head start: copy what the old model already knows", 15, INK_DIM)
        inherit_tag.move_to(np.array([0.4, 1.95, 0]))

        self.play(Create(path_f), Create(path_h), FadeIn(inherit_tag), run_time=0.5)

        # two glow pulses travel DOWN the arcs together (parallel hand-off)
        pf = glow(Dot(color=INK, radius=0.07)).move_to(path_f.get_start())
        ph = glow(Dot(color=INK, radius=0.07)).move_to(path_h.get_start())
        self.add(pf, ph)
        self.play(MoveAlongPath(pf, path_f), MoveAlongPath(ph, path_h),
                  run_time=0.5, rate_func=rate_functions.ease_in_out_sine)

        # on arrival the two tiers go solid INK + labels become "copied"; bar fills 2/3
        copied_f = mono("copied", 15, INK).move_to(rA.f_lab)
        copied_h = mono("copied", 15, INK).move_to(rA.h_lab)
        self.play(
            rA.front.animate.set_stroke(INK, 1.7, opacity=1.0),
            rA.heads.animate.set_stroke(INK, 1.7, opacity=1.0),
            ReplacementTransform(rA.f_lab, copied_f),
            ReplacementTransform(rA.h_lab, copied_h),
            FadeOut(pf), FadeOut(ph),
            FadeOut(path_f), FadeOut(path_h),
            fill_pt.animate.set_value(2 / 3),
            run_time=0.5)
        # bottom label updates
        rail_lab2 = mono("inherited:  front-end OK   heads OK   middle: training ...", 15, INK_DIM)
        rail_lab2.next_to(track, UP, buff=0.18)
        self.play(ReplacementTransform(rail_lab, rail_lab2),
                  FadeOut(inherit_tag),
                  # top strip dims to ghost now that inheritance landed
                  old_glyph.animate.set_opacity(0.45),
                  run_time=0.45)

        # ============================================================
        # BEAT 3 — TRANSFORM / the fresh middle trains
        # ============================================================
        self.next_section("train")
        train_tag = mono("only the middle starts fresh — it trains up", 15, INK_DIM)
        train_tag.move_to(np.array([0.4, 1.95, 0]))

        sweep = Line(rA.mid.get_corner(DL), rA.mid.get_corner(UL),
                     stroke_color=INK, stroke_width=2.8).set_opacity(0.9)
        trained_mid = rA.mid.copy().set_stroke(INK, 1.7, opacity=1.0)
        trained_lab = mono("trained", 15, INK_DIM).move_to(rA.m_lab)
        self.add(sweep)
        self.play(
            sweep.animate.move_to(rA.mid.get_right()),
            ReplacementTransform(fresh_mid, trained_mid),
            ReplacementTransform(fresh_lab, trained_lab),
            FadeIn(train_tag),
            fill_pt.animate.set_value(1.0),
            run_time=0.65, rate_func=linear)

        # rename reader A title; settle bottom label
        readerA_title = mono("reader A", 19, INK).move_to(rA.title)
        rail_lab3 = mono("inherited front-end + heads  -  middle trained from scratch", 15, INK_DIM)
        rail_lab3.next_to(track, UP, buff=0.18)
        self.play(
            FadeOut(sweep), FadeOut(train_tag),
            rA.title.animate.become(readerA_title),
            ReplacementTransform(rail_lab2, rail_lab3),
            run_time=0.4)

        # finished reader A handle (so later transforms / PER readouts can attach)
        rA_solid_mid = trained_mid
        self.rA = rA

        # ============================================================
        # BEAT 4 — BUILD / the tougher twin (same design + 5 defences)
        # ============================================================
        self.next_section("twin")

        # "same design" arc sweeps A's blueprint RIGHT to spawn reader B
        rB = reader_block("reader B", w=2.05).move_to(np.array([BX, READER_Y, 0]))
        rB_frame = VGroup(rB.front, rB.mid, rB.heads)
        design_arc = ArcBetweenPoints(
            VGroup(rA.front, rA.heads).get_right() + RIGHT * 0.1,
            rB_frame.get_left() + LEFT * 0.1, angle=-0.45)
        design_arc.set_stroke(INK_GHOST, 1.3)
        same_tag = mono("same design", 14, INK_FAINT).next_to(design_arc, UP, buff=0.06)

        self.play(
            Create(design_arc), FadeIn(same_tag),
            LaggedStart(
                Create(rB.front), Create(rB.mid), Create(rB.heads),
                FadeIn(rB.labs), FadeIn(rB.title),
                lag_ratio=0.12),
            run_time=0.65)
        self.play(FadeOut(design_arc), FadeOut(same_tag), run_time=0.2)

        # bottom rail morphs into a defence tally. NOTE: counter()'s updater pins
        # the live number to its `at=` point each frame (it ignores VGroup.arrange),
        # so we place the label first and hand the counter an explicit `at`.
        tally_pt = ValueTracker(0)
        tally_label = mono("defences fired:", 16, INK_DIM)
        tally_label.move_to(np.array([-0.55, rail_y, 0]))
        count_at = tally_label.get_right() + RIGHT * 0.42
        tally_count = counter(tally_pt, fmt=lambda v: f"{int(round(v))}/5", s=16, c=INK,
                              at=count_at)
        tally = VGroup(tally_label, tally_count)
        self.play(
            FadeOut(track), FadeOut(fill), FadeOut(seg1), FadeOut(seg2),
            FadeOut(rail_lab3),
            FadeIn(tally_label), FadeIn(tally_count),
            run_time=0.45)

        # five defence chips stacked in the narrow center gap
        defences = ["time-masking", "sensor dropout", "gentle noise",
                    "frame rotation", "2nd audio teacher"]
        chips = VGroup(*[mono(d, 14, INK_DIM) for d in defences]).arrange(
            DOWN, buff=0.22, aligned_edge=LEFT)
        chips.move_to(np.array([0, 0.05, 0]))
        bullets = VGroup(*[Dot(radius=0.026, color=INK_FAINT).next_to(c, LEFT, buff=0.14)
                           for c in chips])
        defence_title = mono("heavier defences", 15, INK_FAINT).next_to(chips, UP, buff=0.22)
        self.play(
            FadeIn(defence_title),
            LaggedStart(
                *[FadeIn(VGroup(c, b), shift=LEFT * 0.18) for c, b in zip(chips, bullets)],
                lag_ratio=0.13),
            run_time=0.6)

        # each defence fires a pulse into the twin in a tight cascade; tally counts up.
        # Launch all pulses from a common x just right of the widest chip so none
        # ever crosses over another chip's text.
        launch_x = chips.get_right()[0] + 0.22
        pulses = VGroup()
        anims = []
        for i, c in enumerate(chips):
            start = np.array([launch_x, c.get_center()[1], 0])
            path = Line(start,
                        rB_frame.get_left() + LEFT * 0.08 + UP * (0.3 - 0.15 * i),
                        stroke_width=0)
            pulse = Dot(color=INK, radius=0.05).move_to(start)
            pulses.add(pulse)
            anims.append(AnimationGroup(
                MoveAlongPath(pulse, path),
                c.animate.set_color(INK),
                tally_pt.animate.set_value(i + 1),
            ))
        self.add(pulses)
        self.play(LaggedStart(*anims, lag_ratio=0.22), run_time=0.85, rate_func=linear)
        self.remove(pulses)

        # the twin frame flexes + stroke thickens = "hardened"
        tough_tag = mono("trained to fail differently", 15, INK).next_to(rB.title, UP, buff=0.20)
        self.play(
            Indicate(rB_frame, scale_factor=1.06, color=INK),
            rB_frame.animate.set_stroke(width=2.4),
            FadeIn(tough_tag),
            run_time=0.55)

        # clear chips (before error strips arrive — no crowding)
        self.play(FadeOut(chips), FadeOut(bullets), FadeOut(defence_title),
                  FadeOut(tough_tag), run_time=0.35)

        # ============================================================
        # BEAT 5 — NAME IT / different errors (strips slide DOWN + meter)
        # ============================================================
        self.next_section("differ")

        # ARPABET reference: DH AH K AE T. A slips idx1 (AH->AE); B slips idx2 (K->G).
        seqA = ["DH", "AE", "K", "AE", "T"]   # A slips at idx 1
        seqB = ["DH", "AH", "G", "AE", "T"]   # B slips at idx 2
        wrongA, wrongB = 1, 2
        strip_y = -2.15

        def token_strip(seq, wrong_idx, cx):
            cells = VGroup()
            for i, s in enumerate(seq):
                box = Square(0.48, stroke_color=INK_GHOST, stroke_width=1.2, fill_opacity=0)
                if i == wrong_idx:
                    box.set_stroke(INK, 1.9)
                t = mono(s, 16, INK_DIM if i != wrong_idx else INK).move_to(box)
                cells.add(VGroup(box, t))
            cells.arrange(RIGHT, buff=0.08)
            cells.move_to(np.array([cx, strip_y, 0]))
            return cells

        stripA = token_strip(seqA, wrongA, AX)
        stripB = token_strip(seqB, wrongB, BX)
        labA = mono("reader A reads", 13, INK_FAINT).next_to(stripA, UP, buff=0.14)
        labB = mono("reader B reads", 13, INK_FAINT).next_to(stripB, UP, buff=0.14)

        # strips appear to "emit" from each reader's middle and slide DOWN
        startA = stripA.copy().move_to(rA.mid.get_bottom() + DOWN * 0.2).scale(0.8).set_opacity(0.0)
        startB = stripB.copy().move_to(rB.mid.get_bottom() + DOWN * 0.2).scale(0.8).set_opacity(0.0)
        self.add(startA, startB)
        self.play(
            Transform(startA, stripA), Transform(startB, stripB),
            run_time=0.6)
        self.remove(startA, startB)
        self.add(stripA, stripB)
        # indicate the differing cells (color=INK), tag each slip
        slipA = mono("slip", 12, INK).next_to(stripA[wrongA], DOWN, buff=0.10)
        slipB = mono("slip", 12, INK).next_to(stripB[wrongB], DOWN, buff=0.10)
        self.play(
            FadeIn(labA), FadeIn(labB),
            Indicate(stripA[wrongA], color=INK, scale_factor=1.22),
            Indicate(stripB[wrongB], color=INK, scale_factor=1.22),
            FadeIn(slipA), FadeIn(slipB),
            run_time=0.6)

        # 5-cell agreement meter on the center axis: dots=agree, squares=differ
        meter = VGroup()
        for i in range(5):
            differ = (i == wrongA) or (i == wrongB)
            cell = (Square(0.18, stroke_color=INK, stroke_width=1.7, fill_opacity=0)
                    if differ else Dot(radius=0.07, color=INK))
            meter.add(cell)
        meter.arrange(RIGHT, buff=0.30).move_to(np.array([0, -1.0, 0]))
        meter_lab = mono("where they agree / differ", 13, INK_FAINT).next_to(meter, UP, buff=0.18)
        agree_lab = mono("agree", 12, INK_DIM).next_to(meter, LEFT, buff=0.24)
        differ_lab = mono("differ", 12, INK_FAINT).next_to(meter, RIGHT, buff=0.24)
        self.play(
            FadeIn(meter_lab),
            LaggedStartMap(FadeIn, meter, lag_ratio=0.12),
            FadeIn(agree_lab), FadeIn(differ_lab),
            run_time=0.6)

        # BOTTOM punchline clause 1 — freeze the live counter first (its updater
        # rebuilds Text each frame and would fight the transform's interpolation).
        tally_count.clear_updaters()
        self.remove(tally_count, tally_label)
        tally_static = VGroup(tally_label.copy(), mono("5/5", 16, INK).move_to(count_at))
        self.add(tally_static)
        punch1 = mono("they fail differently", 19, INK)
        punch1.move_to(np.array([0, rail_y, 0]))
        self.play(
            ReplacementTransform(tally_static, punch1),
            run_time=0.5)

        # ============================================================
        # BEAT 6 — BEAT / the shared wall (poster)
        # ============================================================
        self.next_section("wall")

        # punchline completes (clause 2)
        punch_full = VGroup(
            mono("they fail differently", 18, INK),
            mono("->", 18, INK_FAINT),
            mono("averaging recovers each other's miss", 18, INK_DIM),
        ).arrange(RIGHT, buff=0.26)
        punch_full.move_to(np.array([0, rail_y, 0]))
        self.play(ReplacementTransform(punch1, punch_full[0]),
                  FadeIn(punch_full[1], shift=RIGHT * 0.1),
                  FadeIn(punch_full[2], shift=RIGHT * 0.1),
                  run_time=0.6)

        # ----------------------------------------------------------------
        # THE WOW: the "average" hand-off. Each reader's CORRECT cell is
        # threaded across to cover the OTHER reader's slip:
        #   A is right at idx2 (K)  -> covers B's slip at idx2 (G)
        #   B is right at idx1 (AH) -> covers A's slip at idx1 (AE)
        # Two faint dashed beams arc between the strips through the meter;
        # a glow Dot runs each so the recovery reads as a hand-off, not a
        # statement. The "average" label sits on the center axis.
        # ----------------------------------------------------------------
        avg_lab = mono("average", 13, INK_DIM).move_to(np.array([0, -1.62, 0]))
        avg_sub = mono("each fills the other's gap", 11, INK_FAINT).next_to(
            avg_lab, DOWN, buff=0.08)
        self.play(FadeIn(avg_lab), FadeIn(avg_sub), run_time=0.3)

        # beam 1: A's good idx2 (K) reaches RIGHT to cover B's slip idx2 (G)
        a_good = stripA[2].get_top() + UP * 0.04
        b_miss = stripB[2].get_top() + UP * 0.04
        beam_AB = ArcBetweenPoints(a_good, b_miss, angle=-0.55)
        beam_AB.set_stroke(INK_GHOST, 1.2)
        beam_AB_d = DashedVMobject(beam_AB, num_dashes=30, dashed_ratio=0.55)
        # beam 2: B's good idx1 (AH) reaches LEFT to cover A's slip idx1 (AE)
        b_good = stripB[1].get_top() + UP * 0.04
        a_miss = stripA[1].get_top() + UP * 0.04
        beam_BA = ArcBetweenPoints(b_good, a_miss, angle=-0.55)
        beam_BA.set_stroke(INK_GHOST, 1.2)
        beam_BA_d = DashedVMobject(beam_BA, num_dashes=30, dashed_ratio=0.55)

        self.play(Create(beam_AB_d), Create(beam_BA_d), run_time=0.45)

        # glow Dots hand the correct cell across each beam (visible recovery)
        hopAB = glow(Dot(color=INK, radius=0.06)).move_to(beam_AB.get_start())
        hopBA = glow(Dot(color=INK, radius=0.06)).move_to(beam_BA.get_start())
        self.add(hopAB, hopBA)
        self.play(
            MoveAlongPath(hopAB, beam_AB),
            MoveAlongPath(hopBA, beam_BA),
            run_time=0.85, rate_func=rate_functions.ease_in_out_sine)
        # the recovered cells light: the slip boxes get a clean INK outline,
        # their wrong glyph dims, a faint corrected token rises = "fixed"
        fixA = mono("AH", 16, INK).move_to(stripA[wrongA][1])
        fixB = mono("K", 16, INK).move_to(stripB[wrongB][1])
        self.play(
            stripA[wrongA][0].animate.set_stroke(INK, 1.9, opacity=1.0),
            stripB[wrongB][0].animate.set_stroke(INK, 1.9, opacity=1.0),
            FadeOut(stripA[wrongA][1], scale=0.4),
            FadeOut(stripB[wrongB][1], scale=0.4),
            FadeIn(fixA, shift=UP * 0.06), FadeIn(fixB, shift=UP * 0.06),
            # the two differ-squares in the meter close to solid agreement dots
            meter[wrongA].animate.set_fill(INK, opacity=0.9),
            meter[wrongB].animate.set_fill(INK, opacity=0.9),
            FadeOut(hopAB), FadeOut(hopBA),
            run_time=0.6)
        # fade the slip tags now that the misses are recovered
        self.play(FadeOut(slipA), FadeOut(slipB), run_time=0.25)

        # compact "20.9% PER" under each reader, tied by a dashed line = the wall
        def per_tag(reader):
            n = mono("20.9%", 17, INK_DIM)
            l = mono("PER", 12, INK_FAINT)
            g = VGroup(n, l).arrange(RIGHT, buff=0.10)
            g.next_to(reader.title, UP, buff=0.20)
            g.num = n
            return g
        gA = per_tag(rA)
        gB = per_tag(rB)
        tie = DashedLine(gA.get_right() + RIGHT * 0.12, gB.get_left() + LEFT * 0.12,
                         stroke_color=INK_GHOST, stroke_width=1.3, dash_length=0.09)
        wall_lab = mono("both plateau — the wall", 14, INK_FAINT)
        wall_lab.move_to((gA.get_center() + gB.get_center()) / 2 + UP * 0.30)
        self.play(
            FadeIn(gA, shift=DOWN * 0.08), FadeIn(gB, shift=DOWN * 0.08),
            Create(tie), FadeIn(wall_lab),
            run_time=0.6)

        # the single pure-#fff accent: the tied 20.9% pair on its final Indicate
        gA.num.set_color(WHITE_ACCENT)
        gB.num.set_color(WHITE_ACCENT)
        self.play(
            Indicate(VGroup(gA.num, gB.num), color=WHITE_ACCENT, scale_factor=1.18),
            run_time=0.6)

        self.wait(0.6)


if __name__ == "__main__":
    pass
