# S18 — Two readers (warm-start + tougher twin)
#
# Locked 8-beat sheet (one self.next_section per spoken sentence, timed to dur_sec):
#   1 have one      reader A sits solid + lone focus; ancestry glyph at INK_GHOST,
#                   bottom rail quiet. We already have ONE reader.
#   2 why a second? faint "why a second?" tag over A; the empty right slot pulses
#                   once, hinting a second reader is coming.
#   3 warm-start    two inheritance arcs flow DOWN from the ghost old-model glyph
#                   into A's front-end + heads; both tiers snap solid, relabel
#                   "copied"; a brief "copy what it already knows" tag fades.
#   4 train middle  the dashed "fresh" middle is swept solid by a training pass;
#                   label flips fresh -> trained; warm-start bar fills full.
#   5 the twin      a "same design" arc spawns reader B on the right; five defence
#                   chips fire ONE cascade of pulses into B as the 0/5 tally counts
#                   to 5; B's frame thickens.
#   6 the wall      a compact "20.9% PER" tag under each reader, joined by a dashed
#                   tie line "both plateau — the wall". Same accuracy FIRST.
#   7 different     each reader emits a 5-cell ARPABET strip; A's slip at idx1, B's
#                   slip at idx2 — different cells; agreement meter shows two
#                   differing squares among matching dots.
#   8 open loop     spotlight the two differing meter squares; bottom resolves to
#                   "they fail differently"; the tied 20.9% pair gets the single
#                   pure-#fff Indicate as everything else dims.
#
# CUT vs old scene: the standing "ancestor -> two new readers" family-tree bracket
# and labels at beat 1; the persistent "a head start" standing tag; the pre-stated
# "trained to fail differently" over-title on the twin; and the ENTIRE averaging
# hand-off climax (recovery beams, threaded glow Dots, corrected tokens, "averaging
# recovers each other's miss"). That resolution belongs to the next stage — this one
# ends OPEN on "they fail differently — about to become useful".
#
# Strict monochrome — emphasis via opacity / stroke width / scale / glow only.
from manim import *
from style import *

WHITE_ACCENT = "#ffffff"

READER_Y = 0.15
AX, BX = -3.45, 3.45
RAIL_Y = -2.95


def reader_block(label, label_size=19, w=2.05, mid_h=0.84, side_h=0.62):
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
    return VGroup(
        RoundedRectangle(width=w, height=0.20, corner_radius=0.04,
                         stroke_color=c, stroke_width=sw, fill_opacity=0),
        RoundedRectangle(width=w, height=0.28, corner_radius=0.04,
                         stroke_color=c, stroke_width=sw, fill_opacity=0),
        RoundedRectangle(width=w, height=0.20, corner_radius=0.04,
                         stroke_color=c, stroke_width=sw, fill_opacity=0),
    ).arrange(DOWN, buff=0.07)


class TwoReaders(Scene):
    def construct(self):
        seed()

        # ============================================================
        # BEAT 1 — HAVE ONE (~0.6s): reader A is the lone solid focus.
        # ============================================================
        self.next_section("have_one")

        # ghost old-model glyph, anchored upper-LEFT, kept at INK_GHOST so the
        # opening reads "we already have one reader", NOT "here is a family tree".
        glyph = mini_glyph(INK_GHOST).move_to(LEFT * 5.6 + UP * 2.85)
        glyph_lab = mono("earlier model", 13, INK_GHOST).next_to(glyph, DOWN, buff=0.12)
        old_glyph = VGroup(glyph, glyph_lab)

        # Reader A — fully built and solid (front-end + heads inherited? not yet;
        # at beat 1 it is simply our one good reader, all tiers solid INK).
        rA = reader_block("reader A", w=2.05).move_to(np.array([AX, READER_Y, 0]))

        self.play(
            FadeIn(old_glyph),
            LaggedStart(
                Create(rA.front), Create(rA.mid), Create(rA.heads),
                FadeIn(rA.labs), FadeIn(rA.title),
                lag_ratio=0.10),
            run_time=0.45)
        self.wait(0.15)

        # ============================================================
        # BEAT 2 — WHY A SECOND? (~0.88s): question over A; empty slot pulses.
        # ============================================================
        self.next_section("why_second")

        q_tag = mono("why a second?", 17, INK_DIM).next_to(rA.title, UP, buff=0.30)
        # a ghost outline of where reader B will appear, pulsing once.
        slot = reader_block("", w=2.05).move_to(np.array([BX, READER_Y, 0]))
        slot_frame = VGroup(slot.front, slot.mid, slot.heads)
        slot_frame.set_stroke(INK_GHOST, 1.2)

        self.add(slot_frame)
        slot_frame.set_opacity(0)
        self.play(FadeIn(q_tag, shift=DOWN * 0.08), run_time=0.32)
        self.play(
            slot_frame.animate.set_stroke(INK_FAINT, 1.4, opacity=0.55),
            rate_func=there_and_back, run_time=0.46)
        slot_frame.set_stroke(INK_GHOST, 1.2, opacity=0.0)
        self.wait(0.1)

        # ============================================================
        # BEAT 3 — WARM-START (~2.63s): inheritance arcs DOWN into A.
        # ============================================================
        self.next_section("warmstart")

        self.play(FadeOut(q_tag, shift=UP * 0.06), run_time=0.3)

        # demote A's front-end + heads to faint so the inheritance can "fill" them.
        for tier, lab in ((rA.front, rA.f_lab), (rA.heads, rA.h_lab)):
            tier.set_stroke(INK_FAINT, 1.5, opacity=0.5)
            lab.set_color(INK_FAINT).set_opacity(0.7)

        glyph_anchor = glyph.get_bottom() + DOWN * 0.04
        path_f = ArcBetweenPoints(glyph_anchor, rA.front.get_left() + LEFT * 0.04, angle=0.7)
        path_h = ArcBetweenPoints(glyph_anchor, rA.heads.get_left() + LEFT * 0.04, angle=0.9)
        path_f.set_stroke(INK_GHOST, 1.3)
        path_h.set_stroke(INK_GHOST, 1.3)
        copy_tag = mono("copy what it already knows", 15, INK_DIM)
        copy_tag.move_to(np.array([0.0, 1.95, 0]))

        self.play(Create(path_f), Create(path_h),
                  FadeIn(copy_tag, shift=DOWN * 0.06), run_time=0.6)

        # two glow pulses travel DOWN the arcs together (parallel hand-off).
        pf = glow(Dot(color=INK, radius=0.07)).move_to(path_f.get_start())
        ph = glow(Dot(color=INK, radius=0.07)).move_to(path_h.get_start())
        self.add(pf, ph)
        self.play(MoveAlongPath(pf, path_f), MoveAlongPath(ph, path_h),
                  run_time=0.55, rate_func=rate_functions.ease_in_out_sine)

        # on arrival the two tiers snap solid + relabel "copied".
        copied_f = mono("copied", 15, INK).move_to(rA.f_lab)
        copied_h = mono("copied", 15, INK).move_to(rA.h_lab)
        self.play(
            rA.front.animate.set_stroke(INK, 1.7, opacity=1.0),
            rA.heads.animate.set_stroke(INK, 1.7, opacity=1.0),
            ReplacementTransform(rA.f_lab, copied_f),
            ReplacementTransform(rA.h_lab, copied_h),
            FadeOut(pf), FadeOut(ph),
            FadeOut(path_f), FadeOut(path_h),
            run_time=0.6)
        rA.f_lab, rA.h_lab = copied_f, copied_h

        self.play(FadeOut(copy_tag, shift=UP * 0.06), run_time=0.4)
        self.wait(0.03)

        # ============================================================
        # BEAT 4 — TRAIN MIDDLE (~1.24s): fresh middle trains; bar fills.
        # ============================================================
        self.next_section("train")

        # mark the middle as "fresh" (dashed) just before training it.
        rA.mid.set_stroke(opacity=0)
        fresh_mid = DashedVMobject(
            rA.mid.copy().set_stroke(INK, 1.7, opacity=0.6),
            num_dashes=28, dashed_ratio=0.5)
        fresh_lab = mono("fresh", 15, INK_FAINT).move_to(rA.m_lab)
        rA.m_lab.set_opacity(0)

        # a compact warm-start bar on the bottom rail.
        bar_w = 4.6
        track = RoundedRectangle(width=bar_w, height=0.30, corner_radius=0.15,
                                 stroke_color=INK_GHOST, stroke_width=1.4,
                                 fill_opacity=0).move_to(np.array([AX, RAIL_Y, 0]))
        bar_lab = mono("warm-start", 14, INK_FAINT).next_to(track, UP, buff=0.16)
        fill_pt = ValueTracker(2 / 3)  # front-end + heads already inherited
        fill_left = track.get_left() + RIGHT * 0.04
        inner_w = bar_w - 0.08

        def make_fill():
            frac = fill_pt.get_value()
            if frac <= 0.001:
                return VGroup()
            f = RoundedRectangle(width=inner_w * frac, height=0.20, corner_radius=0.10,
                                 stroke_width=0, fill_color=INK, fill_opacity=0.9)
            f.move_to(fill_left + RIGHT * (inner_w * frac / 2))
            return f
        fill = always_redraw(make_fill)
        self.add(fill)

        self.play(
            FadeIn(fresh_mid), FadeIn(fresh_lab),
            Create(track), FadeIn(bar_lab),
            run_time=0.4)

        sweep = Line(rA.mid.get_corner(DL), rA.mid.get_corner(UL),
                     stroke_color=INK, stroke_width=2.8).set_opacity(0.9)
        trained_mid = rA.mid.copy().set_stroke(INK, 1.7, opacity=1.0)
        trained_lab = mono("trained", 15, INK_DIM).move_to(rA.m_lab)
        self.add(sweep)
        self.play(
            sweep.animate.move_to(rA.mid.get_right()),
            ReplacementTransform(fresh_mid, trained_mid),
            ReplacementTransform(fresh_lab, trained_lab),
            fill_pt.animate.set_value(1.0),
            run_time=0.6, rate_func=linear)
        self.play(FadeOut(sweep), run_time=0.2)
        # drop the hidden "Conformer" placeholder so it can't resurface under
        # "trained" when A's labels are later restored to full opacity.
        self.remove(rA.m_lab)
        rA.labs = VGroup(rA.f_lab, trained_lab, rA.h_lab)
        rA.m_lab = trained_lab
        self.wait(0.04)

        # ============================================================
        # BEAT 5 — THE TWIN (~3.59s): same design spawns B + 5 defences fire.
        # ============================================================
        self.next_section("twin")

        # fade the warm-start bar; A is done — dim it slightly so B can be focus.
        self.play(FadeOut(track), FadeOut(fill), FadeOut(bar_lab), run_time=0.3)

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
            # A recedes to make B the focus.
            rA.stack.animate.set_stroke(opacity=0.55),
            rA.labs.animate.set_opacity(0.5), rA.title.animate.set_opacity(0.6),
            run_time=0.7)
        self.play(FadeOut(design_arc), FadeOut(same_tag), run_time=0.2)

        # bottom rail = defence tally that counts up to 5.
        tally_pt = ValueTracker(0)
        tally_label = mono("defences fired:", 16, INK_DIM)
        tally_label.move_to(np.array([-0.7, RAIL_Y, 0]))
        count_at = tally_label.get_right() + RIGHT * 0.42
        tally_count = counter(tally_pt, fmt=lambda v: f"{int(round(v))}/3", s=16,
                              c=INK, at=count_at)
        self.play(FadeIn(tally_label), FadeIn(tally_count), run_time=0.3)

        # the report-accurate ways the twin differs (training/augment.py "p2",
        # report Section 5.1): stronger jitter + dropout, plus a different audio teacher
        # (BiLSTM frame-KL, distinct from reader A's WavLM-L9). NOT "abuse".
        defences = ["stronger jitter", "heavier dropout", "a different audio teacher"]
        chips = VGroup(*[mono(d, 14, INK_DIM) for d in defences]).arrange(
            DOWN, buff=0.20, aligned_edge=LEFT)
        chips.move_to(np.array([-0.15, READER_Y, 0]))
        bullets = VGroup(*[Dot(radius=0.026, color=INK_FAINT).next_to(c, LEFT, buff=0.14)
                           for c in chips])
        defence_title = mono("trained differently", 14, INK_FAINT).next_to(
            chips, UP, buff=0.22)
        self.play(
            FadeIn(defence_title),
            LaggedStart(
                *[FadeIn(VGroup(c, b), shift=LEFT * 0.16) for c, b in zip(chips, bullets)],
                lag_ratio=0.12),
            run_time=0.55)

        # ONE cascade: each chip fires a pulse into B; tally counts up.
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
        self.play(LaggedStart(*anims, lag_ratio=0.28), run_time=0.85, rate_func=linear)

        # B's frame flexes + thickens = hardened (no over-title here); the spent
        # pulses fade out on the same beat so none linger at B's edge.
        self.play(
            Indicate(rB_frame, scale_factor=1.06, color=INK),
            rB_frame.animate.set_stroke(width=2.4),
            *[FadeOut(p) for p in pulses],
            run_time=0.5)
        self.remove(*pulses)

        # clear chips + tally before the wall lands.
        tally_count.clear_updaters()
        self.play(
            FadeOut(chips), FadeOut(bullets), FadeOut(defence_title),
            FadeOut(tally_count), FadeOut(tally_label),
            # A returns to full strength now that both readers exist.
            rA.stack.animate.set_stroke(opacity=1.0),
            rA.labs.animate.set_opacity(1.0), rA.title.animate.set_opacity(1.0),
            run_time=0.45)
        self.wait(0.04)

        # ============================================================
        # BEAT 6 — THE WALL (~1.62s): same accuracy, both at 20.9% PER.
        # ============================================================
        self.next_section("wall")

        def per_tag(reader):
            n = mono("20.9%", 17, INK_DIM)
            l = mono("PER", 12, INK_FAINT)
            g = VGroup(n, l).arrange(RIGHT, buff=0.10)
            g.next_to(reader.title, UP, buff=0.22)
            g.num = n
            return g
        gA = per_tag(rA)
        gB = per_tag(rB)
        tie = DashedLine(gA.get_right() + RIGHT * 0.12, gB.get_left() + LEFT * 0.12,
                         stroke_color=INK_GHOST, stroke_width=1.3, dash_length=0.09)
        wall_lab = mono("both plateau — the wall", 14, INK_FAINT)
        wall_lab.move_to((gA.get_center() + gB.get_center()) / 2 + UP * 0.32)

        self.play(
            FadeIn(gA, shift=DOWN * 0.08), FadeIn(gB, shift=DOWN * 0.08),
            run_time=0.6)
        self.play(Create(tie), FadeIn(wall_lab), run_time=0.55)
        self.wait(0.2)

        # ============================================================
        # BEAT 7 — DIFFERENT (~1.26s): strips emit; slips at idx1 vs idx2.
        # ============================================================
        self.next_section("differ")

        # ARPABET reference: DH AH K AE T. A slips idx1; B slips idx2.
        seqA = ["DH", "AE", "K", "AE", "T"]   # A slips at idx 1
        seqB = ["DH", "AH", "G", "AE", "T"]   # B slips at idx 2
        wrongA, wrongB = 1, 2
        strip_y = -1.55

        def token_strip(seq, wrong_idx, cx):
            cells = VGroup()
            for i, s in enumerate(seq):
                box = Square(0.42, stroke_color=INK_GHOST, stroke_width=1.2, fill_opacity=0)
                if i == wrong_idx:
                    box.set_stroke(INK, 1.9)
                t = mono(s, 15, INK_DIM if i != wrong_idx else INK).move_to(box)
                cells.add(VGroup(box, t))
            cells.arrange(RIGHT, buff=0.07)
            cells.move_to(np.array([cx, strip_y, 0]))
            return cells

        stripA = token_strip(seqA, wrongA, AX)
        stripB = token_strip(seqB, wrongB, BX)

        # strips "emit" from each reader's middle and slide DOWN.
        startA = stripA.copy().move_to(rA.mid.get_bottom() + DOWN * 0.2).scale(0.8).set_opacity(0.0)
        startB = stripB.copy().move_to(rB.mid.get_bottom() + DOWN * 0.2).scale(0.8).set_opacity(0.0)
        self.add(startA, startB)
        self.play(Transform(startA, stripA), Transform(startB, stripB), run_time=0.45)
        self.remove(startA, startB)
        self.add(stripA, stripB)

        slipA = mono("slip", 12, INK).next_to(stripA[wrongA], DOWN, buff=0.10)
        slipB = mono("slip", 12, INK).next_to(stripB[wrongB], DOWN, buff=0.10)
        self.play(
            Indicate(stripA[wrongA], color=INK, scale_factor=1.22),
            Indicate(stripB[wrongB], color=INK, scale_factor=1.22),
            FadeIn(slipA), FadeIn(slipB),
            run_time=0.7)

        # ============================================================
        # BEAT 8 — OPEN LOOP (~1.78s): agreement meter; spotlight differing
        # squares; resolve "they fail differently"; white Indicate on 20.9%.
        # ============================================================
        self.next_section("open_loop")

        # 5-cell agreement meter on the center axis: dots=agree, squares=differ.
        meter = VGroup()
        for i in range(5):
            differ = (i == wrongA) or (i == wrongB)
            cell = (Square(0.18, stroke_color=INK, stroke_width=1.7, fill_opacity=0)
                    if differ else Dot(radius=0.07, color=INK))
            meter.add(cell)
        meter.arrange(RIGHT, buff=0.30).move_to(np.array([0, -2.95, 0]))
        agree_lab = mono("agree", 12, INK_DIM).next_to(meter, LEFT, buff=0.24)
        differ_lab = mono("differ", 12, INK).next_to(meter, RIGHT, buff=0.24)
        self.play(
            LaggedStartMap(FadeIn, meter, lag_ratio=0.12),
            FadeIn(agree_lab), FadeIn(differ_lab),
            run_time=0.5)

        # spotlight the two differing meter squares; resolve the punchline.
        punch = mono("they fail differently", 19, INK).move_to(
            np.array([0, -2.0, 0]))
        # everything but the focal elements drops to INK_GHOST.
        dim_targets = VGroup(rA.labs, rA.title, rB.labs, rB.title,
                             stripA, stripB, slipA, slipB, old_glyph, glyph_lab)
        self.play(
            Indicate(meter[wrongA], color=INK, scale_factor=1.4),
            Indicate(meter[wrongB], color=INK, scale_factor=1.4),
            meter[wrongA].animate.set_stroke(WHITE_ACCENT, 2.2),
            meter[wrongB].animate.set_stroke(WHITE_ACCENT, 2.2),
            FadeIn(punch, shift=UP * 0.06),
            dim_targets.animate.set_opacity(0.28),
            rA.stack.animate.set_stroke(opacity=0.3),
            rB_frame.animate.set_stroke(opacity=0.3),
            run_time=0.7)

        # the single pure-#fff accent: the tied 20.9% pair Indicate as all else dims.
        gA.num.set_color(WHITE_ACCENT)
        gB.num.set_color(WHITE_ACCENT)
        glowing = glow(VGroup(gA.num, gB.num).copy())
        self.add(glowing)
        self.play(
            Indicate(VGroup(gA.num, gB.num), color=WHITE_ACCENT, scale_factor=1.18),
            glowing.animate.set_opacity(0.0),
            run_time=0.6)
        self.remove(glowing)
        self.wait(0.4)


if __name__ == "__main__":
    pass
