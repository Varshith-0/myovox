# b06 — "Two answer keys"  (bridge after "where-units-from", before "alignment-problem")
#
# TEACHES: the same stream of snapshots is graded against TWO answer keys at once —
#   coarse human PHONEMES (~40, clean & meaningful) and fine self-supervised UNITS
#   (100, strange but precise). Two keys catch complementary errors and resist
#   shortcuts: a guess that satisfies one key can still be struck out by the other.
#   Only what BOTH agree on is real. Hand-off: neither key says WHEN each sound happens.
#
# Locked 8-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 fork        stream rides in along bottom, forks into two EMPTY rails (1.54s)
#   2 top key     top rail fills ~40 coarse phonemes "human-named"; bottom dim (1.62s)
#   3 bottom key  bottom rail fills 100 fine units "machine-found"; spotlight down (1.86s)
#   4 lazy guess  top passes (check); 3 fine cells smear to u88, boxed, fine cross (2.52s)
#   5 symmetry    reset; slip units miss but the forty flag -> "each catches..." (1.21s)
#   6 agree       ONE guess lights BOTH; #fff checks + bright agreement core (2.14s)
#   7 name        machinery -> ghost; serif "two views, one sound" + sub (1.46s)
#   8 hand-off    bottom line "but neither key tells us WHEN each sound happens" (1.21s)
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

# --- geometry ---------------------------------------------------------------
STREAM_Y = -2.7           # the incoming frame-stream baseline
FORK_X = -2.1             # where the stream splits
PH_Y = 1.55               # phoneme (coarse) rail height
UN_Y = -0.45              # unit (fine) rail height
RAIL_X0 = 0.0             # rails start
RAIL_X1 = 4.6             # rails end (grade mark sits just past)
GRADE_X = 5.4             # x of the check/cross grade marks
LABEL_X = -6.5            # left column for rail names/tags


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


def token_row(labels, y, x0, x1, sq=0.42, fs=20):
    """A rail of small token cells across [x0,x1] at height y."""
    n = len(labels)
    xs = np.linspace(x0, x1, n)
    cells = VGroup()
    texts = VGroup()
    for i, lab in enumerate(labels):
        c = Square(sq, stroke_color=INK_GHOST, stroke_width=1.3,
                   fill_color=BG, fill_opacity=1.0).move_to([xs[i], y, 0])
        t = mono(lab, fs, INK_DIM).move_to(c)
        cells.add(c)
        texts.add(t)
    return VGroup(cells, texts), cells, texts


class TwoAnswerKeys(Scene):
    def construct(self):
        seed()

        # ============================================================
        # BEAT 1 — FORK (1.54s): the single frame-stream rides in and
        #          forks at one node into two EMPTY rails (up and down).
        # ============================================================
        self.next_section("fork")

        title = mono("ONE STREAM  ·  TWO ANSWER KEYS", 24, INK_DIM, w=BOLD)
        title.move_to([0, 3.4, 0])
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.4)

        # a compact filmstrip of frames rides in along the bottom STREAM_Y.
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
        strip.arrange(RIGHT, buff=0.08).move_to([-4.1, STREAM_Y, 0])
        stream_lbl = mono("snapshots  ·  50 / sec", 15, INK_FAINT)
        stream_lbl.next_to(strip, DOWN, buff=0.16).align_to(strip, LEFT)

        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.12) for c in strip],
                              lag_ratio=0.05),
                  FadeIn(stream_lbl), run_time=0.55)

        # a fork node where the stream splits up (phonemes) and down (units).
        fork = Dot([FORK_X, STREAM_Y, 0], radius=0.06, color=INK)
        feed = Line(strip.get_right() + RIGHT * 0.04, [FORK_X, STREAM_Y, 0],
                    stroke_color=INK_FAINT, stroke_width=2.0)
        self.play(Create(feed), FadeIn(fork, scale=0.6), run_time=0.3)

        # two empty rails fork out (just the routing arrows + grade slots).
        up_arrow = flat_arrow([FORK_X, STREAM_Y, 0],
                              [RAIL_X0 - 0.45, PH_Y, 0], INK_FAINT, 2.0)
        dn_arrow = flat_arrow([FORK_X, STREAM_Y, 0],
                              [RAIL_X0 - 0.45, UN_Y, 0], INK_FAINT, 2.0)
        up_guide = Line([RAIL_X0 - 0.2, PH_Y, 0], [RAIL_X1 + 0.5, PH_Y, 0],
                        stroke_color=INK_GHOST, stroke_width=1.0)
        dn_guide = Line([RAIL_X0 - 0.2, UN_Y, 0], [RAIL_X1 + 0.5, UN_Y, 0],
                        stroke_color=INK_GHOST, stroke_width=1.0)
        self.play(Create(up_arrow), Create(dn_arrow),
                  Create(up_guide), Create(dn_guide), run_time=0.4)
        self.wait(0.1)

        # the two grading slots: just past each rail's right end.
        ph_grade_c = np.array([GRADE_X, PH_Y, 0])
        un_grade_c = np.array([GRADE_X, UN_Y, 0])

        # ============================================================
        # BEAT 2 — TOP KEY (1.62s): the coarse ~40 phonemes; bottom dim.
        # ============================================================
        self.next_section("top_key")

        ph_labels = ["K", "AE", "T", "S"]
        ph_row, ph_cells, ph_tx = token_row(ph_labels, PH_Y, RAIL_X0 + 0.3, RAIL_X1,
                                             sq=0.52, fs=24)
        ph_name = mono("phonemes", 22, INK)
        ph_name.move_to([LABEL_X, PH_Y + 0.2, 0]).align_to([LABEL_X, 0, 0], LEFT)
        ph_tag = mono("~40 · coarse", 14, INK_FAINT)
        ph_tag.next_to(ph_name, DOWN, buff=0.12).align_to(ph_name, LEFT)
        ph_tag2 = mono("human-named", 14, INK_FAINT)
        ph_tag2.next_to(ph_tag, DOWN, buff=0.06).align_to(ph_name, LEFT)
        ph_label = VGroup(ph_name, ph_tag, ph_tag2)

        self.play(FadeOut(up_guide),
                  LaggedStart(*[Create(c) for c in ph_cells], lag_ratio=0.08),
                  FadeIn(ph_name, shift=RIGHT * 0.06),
                  run_time=0.7)
        self.play(LaggedStart(*[FadeIn(t) for t in ph_tx], lag_ratio=0.08),
                  FadeIn(ph_tag), FadeIn(ph_tag2),
                  # keep the bottom rail clearly ghosted for now.
                  dn_arrow.animate.set_opacity(0.3), dn_guide.animate.set_opacity(0.3),
                  run_time=0.5)
        self.wait(0.15)

        # ============================================================
        # BEAT 3 — BOTTOM KEY (1.86s): the fine 100 units; spotlight down.
        # ============================================================
        self.next_section("bottom_key")

        un_labels = ["u17", "u17", "u88", "u88", "u04", "u52", "u52", "u91"]
        un_row, un_cells, un_tx = token_row(un_labels, UN_Y, RAIL_X0 + 0.3, RAIL_X1,
                                            sq=0.42, fs=15)
        un_name = mono("units", 22, INK)
        un_name.move_to([LABEL_X, UN_Y + 0.2, 0]).align_to([LABEL_X, 0, 0], LEFT)
        un_tag = mono("100 · fine", 14, INK_FAINT)
        un_tag.next_to(un_name, DOWN, buff=0.12).align_to(un_name, LEFT)
        un_tag2 = mono("machine-found", 14, INK_FAINT)
        un_tag2.next_to(un_tag, DOWN, buff=0.06).align_to(un_name, LEFT)
        un_label = VGroup(un_name, un_tag, un_tag2)

        # spotlight moves DOWN: dim the top, brighten the bottom rail.
        self.play(FadeOut(dn_guide),
                  dn_arrow.animate.set_opacity(1.0),
                  ph_row.animate.set_opacity(0.4), ph_label.animate.set_opacity(0.4),
                  run_time=0.4)
        self.play(LaggedStart(*[Create(c) for c in un_cells], lag_ratio=0.05),
                  FadeIn(un_name, shift=RIGHT * 0.06),
                  run_time=0.6)
        self.play(LaggedStart(*[FadeIn(t) for t in un_tx], lag_ratio=0.05),
                  FadeIn(un_tag), FadeIn(un_tag2),
                  run_time=0.5)
        self.wait(0.16)

        # ============================================================
        # BEAT 4 — LAZY GUESS (2.52s): a blurry guess passes COARSE but the
        #          fine units catch the smear (3 cells collapse to "u88").
        # ============================================================
        self.next_section("lazy_guess")

        trial1 = mono("a lazy guess blurs three sounds into one", 17, INK_DIM)
        trial1.move_to([0, 2.85, 0])
        # re-brighten both rails to neutral so the trial reads cleanly.
        self.play(FadeIn(trial1, shift=DOWN * 0.08),
                  ph_row.animate.set_opacity(1.0), ph_label.animate.set_opacity(1.0),
                  run_time=0.4)

        # guess-pulse rides up to the coarse rail and lights it: the coarse names
        # are right, so the coarse key shrugs and passes (check).
        pulse_up = Dot([FORK_X, STREAM_Y, 0], radius=0.07, color=WHITE)
        self.add(pulse_up)
        self.play(pulse_up.animate.move_to([RAIL_X0, PH_Y, 0]),
                  run_time=0.4, rate_func=smooth)
        self.play(
            LaggedStart(*[c.animate.set_stroke(INK, width=2.2) for c in ph_cells],
                        lag_ratio=0.06),
            LaggedStart(*[t.animate.set_color(INK) for t in ph_tx], lag_ratio=0.06),
            FadeOut(pulse_up, scale=0.3),
            run_time=0.45,
        )
        ph_ok = check(ph_grade_c, c=INK, w=3.2, s=0.55)
        self.play(Create(ph_ok), run_time=0.25)

        # but the SAME blurry guess collapses three distinct units into one — the
        # fine key catches the difference it erased.
        blur_idx = (2, 3, 4)
        for i in blur_idx:
            un_tx[i].generate_target()
            un_tx[i].target = mono("u88", 15, INK).move_to(un_cells[i])
        self.play(*[MoveToTarget(un_tx[i]) for i in blur_idx],
                  *[un_cells[i].animate.set_stroke(INK_DIM, width=1.8) for i in blur_idx],
                  run_time=0.45)
        smear_box = SurroundingRectangle(VGroup(*[un_cells[i] for i in blur_idx]),
                                         color=INK, stroke_width=1.8, buff=0.06)
        un_cross = Cross(Square(0.5).move_to(un_grade_c), stroke_color=INK,
                         stroke_width=3.2).scale(0.55)
        self.play(Create(smear_box), run_time=0.25)
        self.play(Create(un_cross),
                  Flash(un_grade_c, color=INK, flash_radius=0.5,
                        line_length=0.1, num_lines=10), run_time=0.35)
        self.wait(0.15)

        # ============================================================
        # BEAT 5 — SYMMETRY (1.21s): a slip the units miss is exactly what the
        #          forty flag — resolve to the tally line.
        # ============================================================
        self.next_section("symmetry")

        # reset trial 1, restore distinct units, and play the symmetric trial fast.
        for i, lab in zip(blur_idx, ("u88", "u04", "u52")):
            un_tx[i].generate_target()
            un_tx[i].target = mono(lab, 15, INK_DIM).move_to(un_cells[i])
        # coarse rail flags the slip (cross); fine rail shrugs (check).
        ph_cross = Cross(Square(0.5).move_to(ph_grade_c), stroke_color=INK,
                         stroke_width=3.2).scale(0.55)
        un_ok = check(un_grade_c, c=INK, w=3.2, s=0.55)
        slip_box = SurroundingRectangle(ph_cells[2], color=INK,
                                        stroke_width=1.8, buff=0.06)

        self.play(
            FadeOut(ph_ok), FadeOut(un_cross), FadeOut(smear_box),
            *[MoveToTarget(un_tx[i]) for i in blur_idx],
            *[un_cells[i].animate.set_stroke(INK_GHOST, width=1.3) for i in blur_idx],
            FadeOut(trial1),
            run_time=0.35,
        )
        self.play(Create(slip_box), Create(ph_cross), Create(un_ok), run_time=0.4)

        tally = mono("each key catches what the other misses", 18, INK_DIM)
        tally.move_to([0, -3.45, 0])
        self.play(FadeIn(tally, shift=UP * 0.08), run_time=0.3)
        self.wait(0.16)

        # ============================================================
        # BEAT 6 — AGREE (2.14s): one guess lights BOTH rails; #fff checks +
        #          a single bright core where they agree. THE payoff.
        # ============================================================
        self.next_section("agree")

        self.play(FadeOut(slip_box), FadeOut(ph_cross), FadeOut(un_ok),
                  run_time=0.3)

        # one guess lights BOTH rails at once.
        glow_up = Dot([FORK_X, STREAM_Y, 0], radius=0.08, color=WHITE)
        glow_dn = Dot([FORK_X, STREAM_Y, 0], radius=0.08, color=WHITE)
        self.add(glow_up, glow_dn)
        self.play(glow_up.animate.move_to([RAIL_X0, PH_Y, 0]),
                  glow_dn.animate.move_to([RAIL_X0, UN_Y, 0]),
                  run_time=0.45, rate_func=smooth)
        self.play(
            LaggedStart(*[c.animate.set_stroke(INK, width=2.2) for c in ph_cells],
                        lag_ratio=0.04),
            LaggedStart(*[t.animate.set_color(INK) for t in ph_tx], lag_ratio=0.04),
            LaggedStart(*[c.animate.set_stroke(INK, width=2.0) for c in un_cells],
                        lag_ratio=0.03),
            LaggedStart(*[t.animate.set_color(INK) for t in un_tx], lag_ratio=0.03),
            FadeOut(glow_up, scale=0.3), FadeOut(glow_dn, scale=0.3),
            run_time=0.5,
        )
        both_ph = check(ph_grade_c, c=WHITE, w=3.6, s=0.62)
        both_un = check(un_grade_c, c=WHITE, w=3.6, s=0.62)
        self.play(Create(both_ph), Create(both_un), run_time=0.35)

        # the SHARED CORE: one bright #fff peak where the two rails agree.
        core = Dot([2.0, (PH_Y + UN_Y) / 2, 0], radius=0.17, color=WHITE)
        core_g = glow(core)
        link_up = Line([2.0, PH_Y - 0.3, 0], core.get_center(),
                       stroke_color=WHITE, stroke_width=2.0).set_opacity(0.5)
        link_dn = Line([2.0, UN_Y + 0.3, 0], core.get_center(),
                       stroke_color=WHITE, stroke_width=2.0).set_opacity(0.5)
        # dim everything else so the agreement core is the brightest object.
        self.add(core_g)
        self.play(
            Create(link_up), Create(link_dn), GrowFromCenter(core),
            ph_label.animate.set_opacity(0.4), un_label.animate.set_opacity(0.4),
            stream_lbl.animate.set_opacity(0.3),
            run_time=0.45,
        )
        self.play(Flash(core.get_center(), color=WHITE, flash_radius=0.75,
                        line_length=0.14, num_lines=14, time_width=0.4),
                  Indicate(core, scale_factor=1.25, color=WHITE),
                  run_time=0.45)
        self.wait(0.14)

        # ============================================================
        # BEAT 7 — NAME (1.46s): machinery -> ghost; serif payoff owns center.
        # ============================================================
        self.next_section("name")

        machinery = VGroup(strip, feed, fork, up_arrow, dn_arrow,
                           ph_row, un_row, ph_label, un_label, stream_lbl,
                           both_ph, both_un, link_up, link_dn, tally, title)
        name_big = serif("two views, one sound", 42, WHITE).move_to([0, 0.95, 0])
        name_sub = mono("right on both is far harder to fake than one", 18, INK_DIM)
        name_sub.next_to(name_big, DOWN, buff=0.28)
        name_g = glow(name_big)

        self.play(
            machinery.animate.set_opacity(0.16),
            core.animate.move_to([0, 1.85, 0]).scale(0.85),
            FadeOut(core_g),
            run_time=0.5,
        )
        self.remove(core)
        self.add(name_g)
        self.play(GrowFromCenter(name_big), run_time=0.5)
        self.play(FadeIn(name_sub, shift=UP * 0.1), run_time=0.46)

        # ============================================================
        # BEAT 8 — HAND-OFF (1.21s): neither key says WHEN each sound happens.
        # ============================================================
        self.next_section("handoff")

        handoff = mono("but neither key tells us WHEN each sound happens",
                       18, INK_FAINT).move_to([0, -2.4, 0])
        self.play(FadeIn(handoff, shift=UP * 0.1), run_time=0.5)
        self.wait(0.5)
