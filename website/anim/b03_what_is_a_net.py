# website/anim/b03_what_is_a_net.py — B03 "What 'the model' is"
#
# The idea we must land (teaches): a neural network is a LAYERED PARAMETERISED
# FUNCTION mapping inputs -> a guess; its whole behaviour is fixed by adjustable
# dials (weights) that start RANDOM and therefore USELESS.
#
# Metaphor: a layered mixing desk / box of knobs that is really a function.
# Three-zone, left->right, monotonic (reads at any scrubbed frame):
#   TOP    (y ~ +2.6..+3.6) CONTEXT: the carried-over fingerprint bar-row from
#          features-embed, tagged "numbers in"; a faint progress rule + caret.
#   CENTER (y ~ -1.4..+2.1) MECHANISM: the fingerprint flows LEFT->RIGHT through
#          a STACK of dial-banks (3 layers, each a column of little random-angle
#          knobs). Threads between layers brighten as signal passes. The SAME
#          numbers->numbers move repeats layer by layer. Out the right: a short
#          "numbers out" vector + a garbled, dim guessed label. A bracket reads
#          "no hand-written rules — only dials".
#   BOTTOM (y ~ -3.5..-2.5) TAKEAWAY: serif #fff payoff "a function of its dials"
#          with mono sub "all it knows is how they are set".
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"  # the SINGLE payoff accent

TOP_Y = 3.15
RULE_Y = 2.55
MID_Y = 0.35
BOT_Y = -3.05
X_L = -6.6
X_R = 6.6


def tri(angle, c, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def flat_arrow(start, end, c=INK_FAINT, w=2.0):
    shaft = Line(start, end, stroke_color=c, stroke_width=w)
    head = tri(shaft.get_angle() - PI / 2, c, 1.0, 0.085).move_to(shaft.get_end())
    return VGroup(shaft, head)


def fingerprint_row(n=12, w=1.7, hmax=0.95, op=0.9, seedval=11):
    """A slim bar-row standing in for one 384-number fingerprint."""
    rng = np.random.default_rng(seedval)
    hh = np.abs(rng.standard_normal(n))
    hh = 0.12 + hmax * (hh / hh.max())
    bw = w / n
    g = VGroup()
    for k in range(n):
        h = float(hh[k])
        r = Rectangle(width=bw * 0.62, height=h, stroke_width=0,
                      fill_color=INK, fill_opacity=op)
        r.move_to([(k - (n - 1) / 2) * bw, h * 0.5, 0])
        g.add(r)
    return g


def knob(radius, angle, c=INK, op=0.9, sw=1.6):
    """A dial: a small ring with a pointer at `angle` — the unit of a network."""
    ring = Circle(radius=radius, stroke_color=c, stroke_width=sw, fill_opacity=0)
    pointer = Line(ring.get_center(),
                   ring.get_center() + radius * 0.92 * np.array(
                       [np.cos(angle), np.sin(angle), 0.0]),
                   stroke_color=c, stroke_width=sw)
    g = VGroup(ring, pointer)
    g.set_opacity(op)
    return g


def dial_bank(n_knobs, radius, center, c=INK, op=0.9, seedval=0):
    """A vertical column of random-angle dials — one LAYER of the network."""
    rng = np.random.default_rng(seedval)
    bank = VGroup()
    for i in range(n_knobs):
        ang = float(rng.uniform(0, TAU))
        bank.add(knob(radius, ang, c, op))
    bank.arrange(DOWN, buff=radius * 0.85)
    bank.move_to(center)
    return bank


class WhatIsANet(Scene):
    def construct(self):
        seed()

        # ============================================================
        # B0 — POSE: carry the fingerprint in as "numbers in".
        # ============================================================
        self.next_section("pose")

        # Faint progress rule + caret along the top (3 stage marks).
        rule = Line([X_L, RULE_Y, 0], [X_R, RULE_Y, 0],
                    stroke_color=INK_GHOST, stroke_width=1.2)
        stage_x = {"numbers in": X_L + 1.0, "through the dials": 0.0,
                   "a guess out": X_R - 1.4}
        ticks = VGroup()
        stage_lbls = {}
        for name, x in stage_x.items():
            ticks.add(Line([x, RULE_Y - 0.08, 0], [x, RULE_Y + 0.08, 0],
                           stroke_color=INK_GHOST, stroke_width=1.2))
            stage_lbls[name] = mono(name, 15, INK_GHOST).move_to([x, RULE_Y + 0.27, 0])
        stage_lbl_grp = VGroup(*stage_lbls.values())
        caret = tri(PI, INK, 0.9, 0.09).move_to([stage_x["numbers in"], RULE_Y - 0.22, 0])

        def goto_stage(name, rt=0.45):
            anims = [caret.animate.move_to([stage_x[name], RULE_Y - 0.22, 0])]
            for n2, lb in stage_lbls.items():
                anims.append(lb.animate.set_color(INK_DIM if n2 == name else INK_GHOST))
            self.play(*anims, run_time=rt)

        # The fingerprint bar-row enters at the left, framed in a small card.
        fp = fingerprint_row(12, 1.7, 0.95, 0.9, seedval=11)
        fp_box = SurroundingRectangle(fp, color=INK_FAINT, stroke_width=1.4, buff=0.16)
        fp_card = VGroup(fp_box, fp).move_to([X_L + 1.05, MID_Y, 0])
        in_lbl = mono("numbers in", 18, INK_DIM).next_to(fp_card, UP, buff=0.22)
        in_sub = mono("one 384-number fingerprint", 14, INK_FAINT)
        in_sub.next_to(fp_card, DOWN, buff=0.20)

        title = mono('what "the model" really is', 22, INK_DIM).move_to([0, TOP_Y, 0])

        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.4)
        self.play(Create(rule),
                  LaggedStartMap(Create, ticks, lag_ratio=0.2),
                  FadeIn(stage_lbl_grp), run_time=0.55)
        stage_lbls["numbers in"].set_color(INK_DIM)
        self.add(caret)
        self.play(LaggedStartMap(FadeIn, fp, lag_ratio=0.03),
                  Create(fp_box),
                  FadeIn(in_lbl, shift=DOWN * 0.08),
                  FadeIn(in_sub, shift=UP * 0.08), run_time=0.6)

        # ============================================================
        # B1 — BUILD: a STACK of dial-banks (layers). Signal flows in.
        # ============================================================
        self.next_section("build")

        n_layers = 3
        layer_x = [-2.3, -0.1, 2.1]
        knob_r = 0.16
        n_knobs = 5
        banks = VGroup()
        layer_boxes = VGroup()
        layer_caps = VGroup()
        for li, lx in enumerate(layer_x):
            bank = dial_bank(n_knobs, knob_r, [lx, MID_Y, 0],
                             c=INK_DIM, op=0.85, seedval=20 + li)
            box = SurroundingRectangle(bank, color=INK_GHOST, stroke_width=1.3,
                                       buff=0.20, corner_radius=0.06)
            cap = mono(f"layer {li + 1}", 13, INK_FAINT).next_to(box, DOWN, buff=0.14)
            banks.add(bank)
            layer_boxes.add(box)
            layer_caps.add(cap)

        stack_lbl = mono("a deep stack of layers", 18, INK_DIM)
        stack_lbl.move_to([layer_x[1], MID_Y + 1.85, 0])

        goto_stage("through the dials")
        self.play(
            LaggedStart(*[FadeIn(VGroup(layer_boxes[i], banks[i]), shift=UP * 0.1)
                          for i in range(n_layers)], lag_ratio=0.18),
            LaggedStart(*[FadeIn(c) for c in layer_caps], lag_ratio=0.18),
            FadeIn(stack_lbl, shift=DOWN * 0.08),
            run_time=0.85,
        )

        # Connection threads between consecutive stages (in -> L1 -> L2 -> L3).
        anchors = [fp_card] + [layer_boxes[i] for i in range(n_layers)]
        thread_groups = []
        for a, b in zip(anchors[:-1], anchors[1:]):
            left_pts = [a.get_right() + UP * y for y in np.linspace(-0.55, 0.55, 4)]
            right_pts = [b.get_left() + UP * y for y in np.linspace(-0.55, 0.55, 4)]
            tg = VGroup()
            for lp in left_pts:
                for rp in right_pts:
                    tg.add(Line(lp, rp, stroke_color=INK_GHOST, stroke_width=0.7))
            thread_groups.append(tg)
        all_threads = VGroup(*thread_groups)
        self.play(LaggedStart(*[Create(tg) for tg in thread_groups],
                              lag_ratio=0.2), run_time=0.6)

        # A bright pulse rides the threads stage by stage; as it lands on a layer,
        # that layer's dials brighten — the SAME numbers->numbers move repeats.
        same_move = mono("same move: numbers in  →  numbers out", 15, INK_FAINT)
        same_move.move_to([layer_x[1], MID_Y - 2.05, 0])
        self.play(FadeIn(same_move, shift=UP * 0.06), run_time=0.4)

        for li in range(n_layers):
            pulse = Rectangle(width=0.16, height=1.2, stroke_width=0,
                              fill_color=WHITE, fill_opacity=0.0)
            pulse.move_to(anchors[li].get_right() + RIGHT * 0.05)
            pulse.set_fill(opacity=0.55)
            self.add(pulse)
            self.play(
                pulse.animate.move_to(anchors[li + 1].get_left() + LEFT * 0.05),
                thread_groups[li].animate.set_stroke(INK_FAINT, width=1.0),
                run_time=0.46, rate_func=linear,
            )
            self.remove(pulse)
            # the layer's dials brighten — underscoring that behaviour lives in
            # the settings. Emphasis via opacity + a brief scale, never colour.
            self.play(banks[li].animate.set_color(INK).set_opacity(0.95)
                      .scale(1.06),
                      run_time=0.22)
            self.play(banks[li].animate.scale(1 / 1.06), run_time=0.12)
        self.wait(0.25)

        # ============================================================
        # B2 — TRANSFORM: numbers OUT + a garbled, dim first guess.
        # ============================================================
        self.next_section("transform")

        # short output vector to the right of the last layer
        out_x = X_R - 1.15
        out_vec = fingerprint_row(6, 0.85, 0.85, 0.9, seedval=4)
        out_box = SurroundingRectangle(out_vec, color=INK_FAINT, stroke_width=1.4,
                                       buff=0.14)
        out_card = VGroup(out_box, out_vec).move_to([out_x, MID_Y + 0.05, 0])
        out_lbl = mono("numbers out", 18, INK_DIM).next_to(out_card, UP, buff=0.22)

        out_thread = VGroup()
        for lp in [layer_boxes[-1].get_right() + UP * y
                   for y in np.linspace(-0.55, 0.55, 4)]:
            for rp in [out_card.get_left() + UP * y for y in np.linspace(-0.3, 0.3, 3)]:
                out_thread.add(Line(lp, rp, stroke_color=INK_GHOST, stroke_width=0.7))

        goto_stage("a guess out")
        self.play(LaggedStartMap(Create, out_thread, lag_ratio=0.01), run_time=0.4)
        pulse = Rectangle(width=0.16, height=1.2, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.55)
        pulse.move_to(layer_boxes[-1].get_right() + RIGHT * 0.05)
        self.add(pulse)
        self.play(pulse.animate.move_to(out_card.get_left() + LEFT * 0.05),
                  out_thread.animate.set_stroke(INK_FAINT, width=1.0),
                  run_time=0.34, rate_func=linear)
        self.remove(pulse)
        self.play(LaggedStartMap(FadeIn, out_vec, lag_ratio=0.05),
                  Create(out_box),
                  FadeIn(out_lbl, shift=DOWN * 0.08), run_time=0.5)

        # The garbled first guess pops out, dim & scrambled — nonsense at first.
        guess = mono("?qz·le?", 26, INK_FAINT).next_to(out_card, DOWN, buff=0.34)
        guess_tag = mono("first guess — nonsense", 13, INK_GHOST)
        guess_tag.next_to(guess, DOWN, buff=0.12)
        self.play(FadeIn(guess, shift=DOWN * 0.06, scale=0.9),
                  FadeIn(guess_tag), run_time=0.45)
        # the garbled guess flickers through a few nonsense strings — random dials
        # mean a meaningless answer at the start.
        for s in ["zx?·ql", "?gv·tk?", "qz·le?"]:
            g2 = mono(s, 26, INK_FAINT).move_to(guess)
            self.play(Transform(guess, g2), run_time=0.18)
        self.wait(0.2)

        # Bracket the whole box: no hand-written rules — only dials.
        whole = VGroup(fp_card, layer_boxes, banks, out_card)
        brace = Brace(VGroup(layer_boxes, banks), UP, color=INK_GHOST,
                      buff=0.22).set_stroke(width=1)
        brace_lbl = mono("no hand-written rules — only dials", 17, INK_DIM)
        brace_lbl.next_to(brace, UP, buff=0.12)
        # tuck below the top rule / stack label by lowering the stack label first
        self.play(FadeOut(stack_lbl), run_time=0.2)
        self.play(GrowFromCenter(brace),
                  FadeIn(brace_lbl, shift=UP * 0.06), run_time=0.5)
        self.wait(0.3)

        # ============================================================
        # B3 — NAME: serif #fff payoff in the bottom strip.
        # ============================================================
        self.next_section("name")

        # quiet the mechanism so the payoff owns the eye
        self.play(
            all_threads.animate.set_stroke(INK_GHOST, width=0.7),
            out_thread.animate.set_stroke(INK_GHOST, width=0.7),
            banks.animate.set_opacity(0.7),
            run_time=0.35,
        )

        payoff = serif("a function of its dials", 46, WHITE).move_to([0, BOT_Y + 0.18, 0])
        sub = mono("all it knows is how they are set", 18, INK_DIM)
        sub.next_to(payoff, DOWN, buff=0.20)
        self.play(Write(payoff), run_time=0.7)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.35)
        self.play(Indicate(payoff, scale_factor=1.06, color=WHITE), run_time=0.45)

        # ============================================================
        # B4 — POSTER HOLD (~0.6s)
        # ============================================================
        self.wait(0.6)
