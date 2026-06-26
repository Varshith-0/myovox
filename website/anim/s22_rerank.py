# S22 — The chooser (LLM rerank / LIFT)
# A language model reads the candidate sentences AND the raw sounds, then picks
# the most sensible one. Qwen2.5-7B; input = ~10 candidates + detected phonemes
# -> one final sentence; a single verbatim-recall audit lands on a hard white 0.
#
# Locked 6-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 (1.92) PUZZLE  : the carried candidate cloud — the right sentence is already
#                      in the pool; one ghost guess spotlit as "the one we want".
#   2 (2.80) SQUEEZE : the chooser brain appears (7 billion patterns), then a single
#                      padlock stamps + "fits on one modest machine".
#   3 (1.54) READ    : the 10-candidate column + detected-sound strip flow into the
#                      brain; it pulses once as it reads both.
#   4 (2.11) TIE-BREAK: all dim but the two look-alikes (quick / quiet); the K
#                      brightens — a hard k.
#   5 (1.48) CHOOSE  : a bright dot launches from the K to "quick"; it ignites white,
#                      "quiet" ghosts, the serif final sentence resolves.
#   6 (2.13) AUDIT   : inputs clear, brain ghosts; the audit counter ticks to a hard
#                      white 0 — never invents unsupported words. Poster hold.
# Strict monochrome (emg_style inks + pure #fff peak accent only). No LaTeX.
from manim import *
from emg_style import *


WHITE = "#ffffff"


def tri(angle, c, op=1.0, s=0.08):
    """A bare triangular arrowhead (no Arrow tip mobject => no tip bug)."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def cloud_glyph(c=INK_FAINT):
    """Carried from S21: a tiny pile of stacked sentence-ticks = the candidate cloud."""
    g = VGroup()
    for k in range(4):
        w = 0.46 - 0.05 * k
        bar = RoundedRectangle(width=w, height=0.085, corner_radius=0.04,
                               stroke_width=0, fill_color=c,
                               fill_opacity=0.55 - 0.10 * k)
        bar.shift(DOWN * 0.135 * k + RIGHT * 0.05 * k)
        g.add(bar)
    return g


def lock_glyph(c=INK, s=1.0):
    """A small padlock: shackle arc + body."""
    body = RoundedRectangle(width=0.26 * s, height=0.20 * s, corner_radius=0.04 * s,
                            stroke_color=c, stroke_width=2.2, fill_color=c, fill_opacity=0.10)
    shackle = Arc(radius=0.085 * s, start_angle=0, angle=PI,
                  stroke_color=c, stroke_width=2.2)
    shackle.next_to(body, UP, buff=-0.02 * s)
    return VGroup(shackle, body)


class Chooser(Scene):
    def construct(self):
        seed()
        CY = 0.30   # vertical centre of the center mechanism zone

        # top stage label + thin rule held the whole clip
        stage = mono("POOL", 22, INK_DIM, w=BOLD).to_edge(RIGHT, buff=0.8).to_edge(UP, buff=0.55)
        rule = Line(LEFT * 6.6, RIGHT * 6.6, stroke_color=LINE, stroke_width=1.2)
        rule.set_y(stage.get_y() - 0.40)

        # ============================================================== #
        #  BEAT 1 (1.92) — PUZZLE: the right sentence is already in pool  #
        # ============================================================== #
        self.next_section("puzzle")
        glyph = cloud_glyph(INK_FAINT)
        crumb = mono("dozens of guesses · oracle 9.30% in the pool", 19, INK_FAINT)
        crumb_grp = VGroup(glyph, crumb).arrange(RIGHT, buff=0.30)
        crumb_grp.to_edge(LEFT, buff=0.7).set_y(stage.get_y())

        self.play(FadeIn(crumb_grp, shift=DOWN * 0.12), FadeIn(stage, shift=DOWN * 0.12),
                  Create(rule), run_time=0.5)

        # the pool sits center: a few ghost guesses, ONE spotlit as the one we want.
        pool_txt = [
            "the quiet brown box",
            "a quick brown fox",
            "the quick brown fox",
            "the quick brow fox",
        ]
        pool = VGroup(*[mono(t, 19, INK_GHOST) for t in pool_txt])
        pool.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([0, CY, 0])
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.05) for m in pool],
                              lag_ratio=0.12), run_time=0.55)
        want = mono("the one we want", 14, INK).next_to(pool[2], RIGHT, buff=0.45)
        self.play(pool[2].animate.set_color(INK).set_opacity(1.0),
                  FadeIn(want, shift=LEFT * 0.08), run_time=0.42)
        self.wait(0.25)

        # ============================================================== #
        #  BEAT 2 (2.80) — SQUEEZE: 7B patterns, padlock, fits on a box   #
        # ============================================================== #
        self.next_section("squeeze")
        stage2 = mono("SQUEEZE", 22, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        # the pool collapses up into the breadcrumb (the puzzle is parked).
        self.play(ReplacementTransform(stage, stage2),
                  FadeOut(want, shift=RIGHT * 0.08),
                  pool.animate.scale(0.2).move_to(glyph).set_opacity(0.0),
                  run_time=0.45)
        stage = stage2

        brain = RoundedRectangle(
            width=3.3, height=2.0, corner_radius=0.18,
            stroke_color=INK, stroke_width=2.2, fill_color=INK, fill_opacity=0.04,
        ).move_to([0, CY, 0])
        name = mono("Qwen2.5-7B", 26, INK).move_to(brain.get_center() + UP * 0.26)
        sub = mono("the chooser", 16, INK_FAINT).next_to(name, DOWN, buff=0.12)
        scale_cue = mono("7 billion learned patterns", 15, INK_GHOST).next_to(brain, DOWN, buff=0.16)
        self.play(Create(brain), FadeIn(name, shift=UP * 0.08), FadeIn(sub),
                  FadeIn(scale_cue), run_time=0.5)

        # one padlock stamp = squeezed small; no 4-bit/adapter jargon.
        brain_grp = VGroup(brain, name, sub, scale_cue)
        padlock = lock_glyph(INK, 1.0)
        self.play(brain_grp.animate.scale(0.82), run_time=0.5)
        padlock.move_to(brain.get_center() + RIGHT * 1.05 + DOWN * 0.55)
        self.play(GrowFromCenter(padlock),
                  Flash(padlock, color=INK, line_length=0.10, num_lines=8, flash_radius=0.26),
                  run_time=0.45)
        fits = mono("fits on one modest machine", 15, INK_FAINT)
        fits.next_to(brain_grp, DOWN, buff=0.32)
        self.play(FadeIn(fits, shift=UP * 0.08), run_time=0.35)
        self.wait(0.15)

        # ============================================================== #
        #  BEAT 3 (1.54) — READ: candidates + sounds flow into the brain  #
        # ============================================================== #
        self.next_section("read")
        stage3 = mono("READ", 22, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        chooser = VGroup(brain, name, sub)
        self.play(ReplacementTransform(stage, stage3),
                  VGroup(chooser, padlock).animate.scale(0.92).move_to([3.45, CY, 0]),
                  FadeOut(fits), FadeOut(scale_cue),
                  run_time=0.4)
        stage = stage3
        padlock.next_to(brain, DOWN, buff=0.08).shift(RIGHT * 1.05)

        cands_txt = [
            "the quick brown fox",
            "the quiet brown fox",
            "the quick brown box",
            "a quick brown fox",
            "the quick brow fox",
        ]
        cand_lines = VGroup(*[
            mono(c, 17, INK if i < 2 else INK_GHOST) for i, c in enumerate(cands_txt)
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.155)
        more = mono("... 10 guesses", 14, INK_GHOST)
        more.next_to(cand_lines, DOWN, aligned_edge=LEFT, buff=0.16)
        cand_box = VGroup(cand_lines, more).move_to([-4.05, CY + 0.85, 0])
        cand_label = mono("candidates", 16, INK_FAINT).next_to(cand_box, UP, aligned_edge=LEFT, buff=0.18)

        phon = mono("DH  AH  K  W  IH  K  ...", 18, INK).move_to([-4.05, CY - 1.45, 0])
        phon_label = mono("detected sounds", 16, INK_FAINT)
        phon_label.next_to(phon, UP, aligned_edge=LEFT, buff=0.16)

        a1 = Line(cand_box.get_right() + RIGHT * 0.20, brain.get_left() + UP * 0.40 + LEFT * 0.14,
                  stroke_width=2.0, color=INK_FAINT)
        a2 = Line(VGroup(phon, phon_label).get_right() + RIGHT * 0.20,
                  brain.get_left() + DOWN * 0.40 + LEFT * 0.14,
                  stroke_width=2.0, color=INK_FAINT)
        a1h = tri(a1.get_angle() - PI / 2, INK_FAINT, 1.0, 0.075).move_to(a1.get_end())
        a2h = tri(a2.get_angle() - PI / 2, INK_FAINT, 1.0, 0.075).move_to(a2.get_end())

        self.play(FadeIn(cand_label), FadeIn(phon_label),
                  LaggedStart(*[FadeIn(m) for m in cand_lines], lag_ratio=0.06),
                  FadeIn(more), Write(phon), run_time=0.45)
        self.play(Create(a1), Create(a2), FadeIn(a1h), FadeIn(a2h), run_time=0.3)

        p1 = Dot(color=INK, radius=0.055).move_to(a1.get_start())
        p2 = Dot(color=INK, radius=0.055).move_to(a2.get_start())
        self.add(p1, p2)
        self.play(p1.animate.move_to(a1.get_end()), p2.animate.move_to(a2.get_end()),
                  run_time=0.3, rate_func=linear)
        self.remove(p1, p2)
        self.play(Indicate(brain, scale_factor=1.06, color=INK), run_time=0.3)

        # ============================================================== #
        #  BEAT 4 (2.11) — TIE-BREAK: quick vs quiet; the hard K          #
        # ============================================================== #
        self.next_section("tiebreak")
        stage4 = mono("TIE-BREAK", 22, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage4),
                  cand_lines[2].animate.set_opacity(0.12),
                  cand_lines[3].animate.set_opacity(0.12),
                  cand_lines[4].animate.set_opacity(0.12),
                  more.animate.set_opacity(0.10),
                  FadeOut(a1), FadeOut(a2), FadeOut(a1h), FadeOut(a2h),
                  run_time=0.4)
        stage = stage4

        # underline the disputed 2nd word (quick / quiet) in each look-alike.
        u0 = Line(ORIGIN, RIGHT, stroke_color=INK, stroke_width=2.2).set_width(0.92)
        u0.next_to(cand_lines[0], DOWN, buff=0.04).align_to(cand_lines[0], LEFT).shift(RIGHT * 0.80)
        u1 = u0.copy().set_stroke(INK_FAINT)
        u1.next_to(cand_lines[1], DOWN, buff=0.04).align_to(cand_lines[1], LEFT).shift(RIGHT * 0.80)
        tie_q = mono("two look-alikes", 15, INK_FAINT).move_to([-4.05, CY - 0.25, 0])
        self.play(Create(u0), Create(u1), FadeIn(tie_q), run_time=0.5)

        # the deciding evidence: the hard K in the detected sounds.
        kmark = mono("hard 'k', not soft 't'", 15, INK)
        kmark.next_to(phon, DOWN, aligned_edge=LEFT, buff=0.22)
        self.play(Indicate(phon, scale_factor=1.05, color=INK),
                  FadeIn(kmark, shift=UP * 0.10), run_time=0.6)
        self.wait(0.61)

        # ============================================================== #
        #  BEAT 5 (1.48) — CHOOSE: K -> quick; serif final sentence       #
        # ============================================================== #
        self.next_section("choose")
        stage5 = mono("CHOOSE", 22, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage5), run_time=0.28)
        stage = stage5

        evid = Dot(color=WHITE, radius=0.07).move_to(phon.get_center() + LEFT * 0.55)
        evid_g = glow(evid)
        self.add(evid_g)
        up_path = ArcBetweenPoints(
            phon.get_center() + LEFT * 0.55,
            cand_lines[0].get_left() + LEFT * 0.18,
            angle=-PI / 2.4,
        )
        self.play(MoveAlongPath(evid_g, up_path), run_time=0.5, rate_func=smooth)

        final = serif("the quick brown fox", 32, INK)
        final.move_to([0.4, CY - 1.85, 0])
        final_g = glow(final)
        self.play(
            cand_lines[0].animate.set_color(WHITE).set_opacity(1.0),
            u0.animate.set_stroke(WHITE, width=3.2),
            cand_lines[1].animate.set_opacity(0.14),
            u1.animate.set_opacity(0.12),
            FadeOut(evid_g),
            run_time=0.35,
        )
        self.add(final_g)
        self.play(TransformFromCopy(cand_lines[0], final),
                  Flash(final, color=WHITE, line_length=0.16, num_lines=12,
                        flash_radius=1.5, time_width=0.4),
                  run_time=0.55)
        self.wait(0.08)

        # ============================================================== #
        #  BEAT 6 (2.13) — AUDIT + poster: the audit ticks to a hard 0    #
        # ============================================================== #
        self.next_section("audit")
        stage6 = mono("AUDIT", 22, INK, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        keep_brain = VGroup(brain, name, padlock)
        self.play(
            ReplacementTransform(stage, stage6),
            FadeOut(cand_box), FadeOut(cand_label),
            FadeOut(phon), FadeOut(phon_label),
            FadeOut(u0), FadeOut(u1), FadeOut(tie_q), FadeOut(kmark),
            keep_brain.animate.scale(0.6).move_to([0, CY + 1.55, 0]).set_opacity(0.30),
            FadeOut(sub),
            VGroup(final_g, final).animate.move_to([0, CY + 0.30, 0]),
            run_time=0.5,
        )
        stage = stage6

        # the audit counter ticks down to a hard white 0 — the only bright accent.
        audit_lbl = mono("out-of-pool answers", 18, INK).move_to([0, CY - 1.55, 0])
        eq = mono("=", 20, INK_FAINT).next_to(audit_lbl, RIGHT, buff=0.26)
        digit_x = eq.get_right()[0] + 0.32

        audit_val = ValueTracker(7.0)
        cnt = num("7", 38, INK)
        cnt.move_to([digit_x, eq.get_y(), 0], aligned_edge=LEFT)
        cnt.add_updater(lambda m: m.become(
            num(str(round(audit_val.get_value())), 38, INK)
            .move_to([digit_x, eq.get_y(), 0], aligned_edge=LEFT)))

        self.play(FadeIn(audit_lbl), FadeIn(eq), run_time=0.3)
        self.add(cnt)
        self.play(audit_val.animate.set_value(0.0), run_time=0.7, rate_func=smooth)
        cnt.clear_updaters()
        zero = num("0", 38, WHITE).move_to([digit_x, eq.get_y(), 0], aligned_edge=LEFT)
        zero_g = glow(zero)
        self.remove(cnt)
        self.add(zero_g)
        sub_line = mono("it only ever picks from the pool", 14, INK_DIM)
        sub_line.next_to(audit_lbl, DOWN, buff=0.18).align_to(audit_lbl, LEFT)
        self.play(Indicate(zero, scale_factor=1.12, color=WHITE),
                  Flash(zero, color=WHITE, line_length=0.12, num_lines=10, flash_radius=0.30),
                  FadeIn(sub_line), run_time=0.45)
        self.wait(0.4)


if __name__ == "__main__":
    pass
