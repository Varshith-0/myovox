# b06 — "Two answer keys"  (bridge after "where-units-from", before "alignment-problem")
#
# TEACHES: the reader is graded against TWO answer keys on the SAME frames at once —
#   coarse human PHONEMES (~40, clean & meaningful) and fine self-supervised UNITS
#   (100, strange but precise). Two keys catch complementary errors and resist
#   shortcuts: a guess that satisfies one key can still be struck out by the other.
#   Metaphor: revising from two independent sets of class notes — the overlap forces
#   real understanding. Hand-off: neither key says WHEN each sound happens.
#
# Three-zone full-canvas composition (pose -> build -> transform -> name):
#   CENTER FORK: a single frame-stream enters from below and forks into two target
#                rails — TOP "phonemes (~40, coarse)", BOTTOM "units (100, fine)",
#                each with its own check/cross grading mark.
#   TRANSFORM:   two trial guesses ride the fork. (1) a cheap shortcut lights the
#                coarse rail (check) but the fine rail catches it (cross). (2) a slip
#                the coarse rail misses (check) but the fine rail flags (cross).
#                Only when BOTH agree does a shared core glow pure #fff.
#   BOTTOM:      a live "fooled?" tally — one key is easy to fool, two keys far harder.
#   NAME:        serif "two views, one sound" + mono "harder to fake than one",
#                then the hand-off "but neither key tells us WHEN".
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# --- geometry ---------------------------------------------------------------
STREAM_Y = -2.55          # the incoming frame-stream baseline
FORK_X = -1.9             # where the stream splits
PH_Y = 1.55               # phoneme (coarse) rail height
UN_Y = -0.45              # unit (fine) rail height
RAIL_X0 = -0.2            # rails start
RAIL_X1 = 4.7             # rails end (grade mark sits just past)
GRADE_X = 5.35            # x of the check/cross grade marks
LABEL_X = -6.4            # left column for rail names/tags


def tri(angle, c, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def flat_arrow(start, end, c=INK_FAINT, w=2.0):
    shaft = Line(start, end, stroke_color=c, stroke_width=w)
    head = tri(shaft.get_angle() - PI / 2, c, 1.0, 0.085).move_to(shaft.get_end())
    return VGroup(shaft, head)


def check(center, c=INK, w=3.0, s=0.5):
    """A tick mark (does NOT need LaTeX)."""
    a = center + np.array([-0.18, 0.02, 0]) * s / 0.5
    b = center + np.array([-0.04, -0.16, 0]) * s / 0.5
    d = center + np.array([0.22, 0.20, 0]) * s / 0.5
    return VGroup(Line(a, b, stroke_color=c, stroke_width=w),
                  Line(b, d, stroke_color=c, stroke_width=w))


def token_row(labels, y, x0, x1, sq=0.42, fs=20, dim_set=()):
    """A rail of small token cells across [x0,x1] at height y."""
    n = len(labels)
    xs = np.linspace(x0, x1, n)
    cells = VGroup()
    texts = VGroup()
    for i, lab in enumerate(labels):
        c = Square(sq, stroke_color=INK_GHOST, stroke_width=1.3,
                   fill_color=BG, fill_opacity=1.0).move_to([xs[i], y, 0])
        col = INK_FAINT if i in dim_set else INK_DIM
        t = mono(lab, fs, col).move_to(c)
        cells.add(c)
        texts.add(t)
    return VGroup(cells, texts), cells, texts


class TwoAnswerKeys(Scene):
    def construct(self):
        seed()

        # ============================================================
        # B0 — POSE: the single frame-stream enters from below.
        # ============================================================
        self.next_section("pose")

        title = mono("ONE STREAM OF FRAMES  ·  TWO ANSWER KEYS", 24, INK_DIM, w=BOLD)
        title.move_to([0, 3.35, 0])
        subtitle = mono("graded against both at once", 16, INK_FAINT).move_to([0, 2.86, 0])
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.42)
        self.play(FadeIn(subtitle), run_time=0.3)

        # a compact filmstrip of frames rides in from the left along STREAM_Y.
        nframes = 9
        fw = 0.46
        strip = VGroup()
        for k in range(nframes):
            card = VGroup(
                Square(fw, stroke_color=INK_FAINT, stroke_width=1.2,
                       fill_color=BG, fill_opacity=1.0),
                VGroup(*[Line([-0.13, h, 0], [0.13, h, 0],
                              stroke_color=INK_GHOST, stroke_width=1.0)
                         for h in (-0.08, 0.02, 0.12)]),
            )
            strip.add(card)
        strip.arrange(RIGHT, buff=0.08).move_to([-3.6, STREAM_Y, 0])
        stream_lbl = mono("frames  ·  50 / sec", 15, INK_FAINT)
        stream_lbl.next_to(strip, LEFT, buff=0.28)
        if stream_lbl.get_left()[0] < -6.9:
            stream_lbl.next_to(strip, DOWN, buff=0.14).align_to(strip, LEFT)

        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.12) for c in strip],
                              lag_ratio=0.05, run_time=0.55),
                  FadeIn(stream_lbl), run_time=0.55)

        # a fork node where the stream splits up (phonemes) and down (units).
        fork = Dot([FORK_X, STREAM_Y, 0], radius=0.06, color=INK)
        feed = Line(strip.get_right() + RIGHT * 0.04, [FORK_X, STREAM_Y, 0],
                    stroke_color=INK_FAINT, stroke_width=2.0)
        self.play(Create(feed), FadeIn(fork, scale=0.6), run_time=0.35)

        # ============================================================
        # B1 — BUILD: fork into two target rails, each with a grading mark.
        # ============================================================
        self.next_section("build")

        up_arrow = flat_arrow([FORK_X, STREAM_Y, 0],
                              [RAIL_X0 - 0.45, PH_Y, 0], INK_FAINT, 2.0)
        dn_arrow = flat_arrow([FORK_X, STREAM_Y, 0],
                              [RAIL_X0 - 0.45, UN_Y, 0], INK_FAINT, 2.0)
        self.play(Create(up_arrow), Create(dn_arrow), run_time=0.45)

        # TOP rail — phonemes: coarse, clean, human-named.
        ph_labels = ["K", "AE", "T", "S"]
        ph_row, ph_cells, ph_tx = token_row(ph_labels, PH_Y, RAIL_X0, RAIL_X1,
                                             sq=0.5, fs=22)
        ph_name = mono("phonemes", 22, INK).move_to([LABEL_X, PH_Y + 0.22, 0])
        ph_name.align_to([LABEL_X, 0, 0], LEFT)
        ph_tag = mono("~40 · coarse", 14, INK_FAINT)
        ph_tag.next_to(ph_name, DOWN, buff=0.12).align_to(ph_name, LEFT)
        ph_tag2 = mono("human-named", 14, INK_FAINT)
        ph_tag2.next_to(ph_tag, DOWN, buff=0.06).align_to(ph_name, LEFT)
        ph_label = VGroup(ph_name, ph_tag, ph_tag2)

        # BOTTOM rail — units: fine, strange, machine-found (more, smaller cells).
        un_labels = ["u17", "u17", "u88", "u88", "u04", "u52", "u52", "u91"]
        un_row, un_cells, un_tx = token_row(un_labels, UN_Y, RAIL_X0, RAIL_X1,
                                            sq=0.42, fs=15)
        un_name = mono("units", 22, INK).move_to([LABEL_X, UN_Y + 0.22, 0])
        un_name.align_to([LABEL_X, 0, 0], LEFT)
        un_tag = mono("100 · fine", 14, INK_FAINT)
        un_tag.next_to(un_name, DOWN, buff=0.12).align_to(un_name, LEFT)
        un_tag2 = mono("machine-found", 14, INK_FAINT)
        un_tag2.next_to(un_tag, DOWN, buff=0.06).align_to(un_name, LEFT)
        un_label = VGroup(un_name, un_tag, un_tag2)

        self.play(
            LaggedStart(*[Create(c) for c in ph_cells], lag_ratio=0.06),
            LaggedStart(*[Create(c) for c in un_cells], lag_ratio=0.05),
            FadeIn(ph_name, shift=RIGHT * 0.06), FadeIn(un_name, shift=RIGHT * 0.06),
            run_time=0.6,
        )
        self.play(
            LaggedStart(*[FadeIn(t) for t in ph_tx], lag_ratio=0.06),
            LaggedStart(*[FadeIn(t) for t in un_tx], lag_ratio=0.05),
            FadeIn(ph_tag), FadeIn(ph_tag2), FadeIn(un_tag), FadeIn(un_tag2),
            run_time=0.5,
        )

        # the two grading marks: a slot just past each rail's right end.
        ph_grade_c = np.array([GRADE_X, PH_Y, 0])
        un_grade_c = np.array([GRADE_X, UN_Y, 0])
        ph_slot = mono("grade", 14, INK_GHOST).move_to(ph_grade_c + UP * 0.55)
        un_slot = mono("grade", 14, INK_GHOST).move_to(un_grade_c + DOWN * 0.55)
        self.play(FadeIn(ph_slot), FadeIn(un_slot), run_time=0.3)

        # ---- BOTTOM tally skeleton: "fooled?" ----
        LY = -3.45
        tally_rule = Line([-6.4, LY + 0.42, 0], [6.4, LY + 0.42, 0],
                          stroke_color=LINE, stroke_width=1.0)
        tally_lbl = mono("one key — easy to fool", 16, INK_FAINT).move_to([0, LY, 0])
        self.play(Create(tally_rule), FadeIn(tally_lbl), run_time=0.35)

        # ============================================================
        # B2 — TRANSFORM (1): a cheap shortcut satisfies COARSE, fails FINE.
        # ============================================================
        self.next_section("shortcut")

        trial1 = mono("trial: a blurry shortcut", 17, INK_DIM).move_to([0, 2.86, 0])
        self.play(ReplacementTransform(subtitle, trial1), run_time=0.35)

        # a guess-pulse rides up to the phoneme rail and lights it: the coarse names
        # are right, so the coarse key is satisfied (check).
        pulse_up = Dot([FORK_X, STREAM_Y, 0], radius=0.07, color=WHITE)
        self.add(pulse_up)
        self.play(pulse_up.animate.move_to([RAIL_X0 - 0.2, PH_Y, 0]),
                  run_time=0.45, rate_func=smooth)
        self.play(
            LaggedStart(*[c.animate.set_stroke(INK, width=2.2) for c in ph_cells],
                        lag_ratio=0.08),
            LaggedStart(*[t.animate.set_color(INK) for t in ph_tx], lag_ratio=0.08),
            FadeOut(pulse_up, scale=0.3),
            run_time=0.5,
        )
        ph_ok = check(ph_grade_c, c=INK, w=3.2, s=0.55)
        self.play(Create(ph_ok), run_time=0.3)

        # but the SAME blurry guess collapses two distinct units into one — the fine
        # key catches the difference it erased (u88 vs u04 both came out "u88").
        blur_idx = (2, 3, 4)   # cells that should differ but got smeared
        for i in blur_idx:
            un_tx[i].generate_target()
            un_tx[i].target = mono("u88", 15, INK).move_to(un_cells[i])
        self.play(*[MoveToTarget(un_tx[i]) for i in blur_idx],
                  *[un_cells[i].animate.set_stroke(INK_DIM, width=1.8) for i in blur_idx],
                  run_time=0.45)
        # the fine key flags the smear: cross over the offending cells.
        smear_box = SurroundingRectangle(VGroup(*[un_cells[i] for i in blur_idx]),
                                         color=INK, stroke_width=1.8, buff=0.06)
        un_cross = Cross(Square(0.5).move_to(un_grade_c), stroke_color=INK,
                         stroke_width=3.2).scale(0.55)
        self.play(Create(smear_box), run_time=0.25)
        self.play(Create(un_cross),
                  Flash(un_grade_c, color=INK, flash_radius=0.5,
                        line_length=0.1, num_lines=10), run_time=0.35)

        verdict1 = mono("coarse: fooled    fine: caught it", 16, INK_DIM).move_to([0, LY, 0])
        self.play(ReplacementTransform(tally_lbl, verdict1), run_time=0.35)
        self.wait(0.1)

        # ============================================================
        # B3 — TRANSFORM (2): a slip COARSE misses, FINE flags. (symmetry)
        # ============================================================
        self.next_section("symmetry")

        trial2 = mono("trial: a subtle slip", 17, INK_DIM).move_to([0, 2.86, 0])
        self.play(ReplacementTransform(trial1, trial2),
                  # reset rail 1 visuals to neutral for the second trial.
                  FadeOut(ph_ok), FadeOut(un_cross), FadeOut(smear_box),
                  *[un_cells[i].animate.set_stroke(INK_GHOST, width=1.3) for i in blur_idx],
                  run_time=0.4)
        # restore the smeared units to their distinct values.
        for i, lab in zip(blur_idx, ("u88", "u04", "u52")):
            un_tx[i].generate_target()
            un_tx[i].target = mono(lab, 15, INK_DIM).move_to(un_cells[i])
        self.play(*[MoveToTarget(un_tx[i]) for i in blur_idx],
                  *[c.animate.set_stroke(INK_GHOST, width=1.3) for c in ph_cells],
                  *[t.animate.set_color(INK_DIM) for t in ph_tx],
                  run_time=0.4)

        # this time the slip lands a phoneme that the coarse key happily accepts
        # (T vs the fine-grained variant) — coarse check — but the fine units catch
        # the wrong micro-texture.
        slip_i = 2   # the "T" cell on the coarse rail
        ph_tx[slip_i].generate_target()
        ph_tx[slip_i].target = mono("T", 22, INK).move_to(ph_cells[slip_i])
        pulse_dn = Dot([FORK_X, STREAM_Y, 0], radius=0.07, color=WHITE)
        self.add(pulse_dn)
        self.play(pulse_dn.animate.move_to([RAIL_X0 - 0.2, PH_Y, 0]),
                  MoveToTarget(ph_tx[slip_i]),
                  ph_cells[slip_i].animate.set_stroke(INK, width=2.2),
                  FadeOut(pulse_dn, scale=0.3),
                  run_time=0.5)
        ph_ok2 = check(ph_grade_c, c=INK, w=3.2, s=0.55)
        self.play(Create(ph_ok2), run_time=0.3)

        # the fine units flag the offending texture cells.
        fine_idx = (5, 6)
        for i in fine_idx:
            un_tx[i].generate_target()
            un_tx[i].target = mono("u52", 15, INK).move_to(un_cells[i])
        fine_box = SurroundingRectangle(VGroup(*[un_cells[i] for i in fine_idx]),
                                        color=INK, stroke_width=1.8, buff=0.06)
        un_cross2 = Cross(Square(0.5).move_to(un_grade_c), stroke_color=INK,
                          stroke_width=3.2).scale(0.55)
        self.play(*[MoveToTarget(un_tx[i]) for i in fine_idx],
                  *[un_cells[i].animate.set_stroke(INK_DIM, width=1.8) for i in fine_idx],
                  Create(fine_box), run_time=0.4)
        self.play(Create(un_cross2),
                  Flash(un_grade_c, color=INK, flash_radius=0.5,
                        line_length=0.1, num_lines=10), run_time=0.35)

        verdict2 = mono("each key catches what the other misses", 16, INK_DIM).move_to([0, LY, 0])
        self.play(ReplacementTransform(verdict1, verdict2), run_time=0.35)
        self.wait(0.1)

        # ============================================================
        # B4 — AGREE: both keys pass; the shared core glows pure #fff.
        # ============================================================
        self.next_section("agree")

        trial3 = mono("right on BOTH — nowhere to hide", 17, INK).move_to([0, 2.86, 0])
        self.play(ReplacementTransform(trial2, trial3),
                  FadeOut(ph_ok2), FadeOut(un_cross2), FadeOut(fine_box),
                  run_time=0.4)
        # restore the fine cells, and make the slip phoneme honest again.
        for i, lab in zip(fine_idx, ("u52", "u52")):
            un_tx[i].generate_target()
            un_tx[i].target = mono(lab, 15, INK_DIM).move_to(un_cells[i])
        self.play(*[MoveToTarget(un_tx[i]) for i in fine_idx],
                  *[un_cells[i].animate.set_stroke(INK_GHOST, width=1.3) for i in fine_idx],
                  ph_cells[slip_i].animate.set_stroke(INK_GHOST, width=1.3),
                  ph_tx[slip_i].animate.set_color(INK_DIM),
                  run_time=0.4)

        # one guess lights BOTH rails; both grade marks turn to checks.
        glow_up = Dot([FORK_X, STREAM_Y, 0], radius=0.08, color=WHITE)
        glow_dn = Dot([FORK_X, STREAM_Y, 0], radius=0.08, color=WHITE)
        self.add(glow_up, glow_dn)
        self.play(
            glow_up.animate.move_to([RAIL_X0 - 0.2, PH_Y, 0]),
            glow_dn.animate.move_to([RAIL_X0 - 0.2, UN_Y, 0]),
            run_time=0.45, rate_func=smooth)
        self.play(
            LaggedStart(*[c.animate.set_stroke(INK, width=2.2) for c in ph_cells],
                        lag_ratio=0.05),
            LaggedStart(*[t.animate.set_color(INK) for t in ph_tx], lag_ratio=0.05),
            LaggedStart(*[c.animate.set_stroke(INK, width=2.0) for c in un_cells],
                        lag_ratio=0.04),
            LaggedStart(*[t.animate.set_color(INK) for t in un_tx], lag_ratio=0.04),
            FadeOut(glow_up, scale=0.3), FadeOut(glow_dn, scale=0.3),
            run_time=0.55,
        )
        both_ph = check(ph_grade_c, c=WHITE, w=3.4, s=0.6)
        both_un = check(un_grade_c, c=WHITE, w=3.4, s=0.6)
        self.play(Create(both_ph), Create(both_un), run_time=0.35)

        # the SHARED CORE: where the two rails agree, one bright peak forms.
        core = Dot([1.85, (PH_Y + UN_Y) / 2, 0], radius=0.16, color=WHITE)
        core_g = glow(core)
        link_up = Line([1.85, PH_Y - 0.3, 0], core.get_center(),
                       stroke_color=WHITE, stroke_width=2.0).set_opacity(0.5)
        link_dn = Line([1.85, UN_Y + 0.3, 0], core.get_center(),
                       stroke_color=WHITE, stroke_width=2.0).set_opacity(0.5)
        core_lbl = mono("the same sound — agreed", 16, INK).next_to(core, RIGHT, buff=0.3)
        self.add(core_g)
        self.play(Create(link_up), Create(link_dn),
                  GrowFromCenter(core), run_time=0.4)
        self.play(FadeIn(core_lbl, shift=RIGHT * 0.1),
                  Flash(core.get_center(), color=WHITE, flash_radius=0.7,
                        line_length=0.14, num_lines=14, time_width=0.4), run_time=0.45)

        verdict3 = mono("two keys — far harder to fool", 16, INK).move_to([0, LY, 0])
        self.play(ReplacementTransform(verdict2, verdict3), run_time=0.35)

        # ============================================================
        # B5 — NAME + HAND-OFF + POSTER HOLD.
        # ============================================================
        self.next_section("name")

        # dim the machinery; let the name own the centre-right.
        machinery = VGroup(strip, feed, fork, up_arrow, dn_arrow,
                           ph_row, un_row, ph_label, un_label,
                           ph_slot, un_slot, both_ph, both_un, stream_lbl,
                           link_up, link_dn)
        name_big = serif("two views, one sound", 40, WHITE).move_to([0, 0.95, 0])
        name_sub = mono("right on both is far harder to fake than one", 18, INK_DIM)
        name_sub.next_to(name_big, DOWN, buff=0.26)
        name_g = glow(name_big)

        self.play(
            machinery.animate.set_opacity(0.16),
            core_lbl.animate.set_opacity(0.0),
            core.animate.move_to([0, 1.7, 0]).scale(0.9),
            FadeOut(core_g),
            run_time=0.55,
        )
        self.remove(core)
        self.add(name_g)
        self.play(GrowFromCenter(name_big), run_time=0.5)
        self.play(FadeIn(name_sub, shift=UP * 0.1), run_time=0.55)

        # hand-off line to the alignment problem.
        handoff = mono("but neither key tells us WHEN each sound happens",
                       17, INK_FAINT).move_to([0, LY, 0])
        self.play(ReplacementTransform(verdict3, handoff), run_time=0.45)

        self.wait(0.6)
