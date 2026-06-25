# website/anim/b03_what_is_a_net.py — B03 "What 'the model' is"
#
# The idea this scene must land: a neural network is a LAYERED PARAMETERISED
# FUNCTION mapping a fingerprint -> a guess; its whole behaviour is fixed by
# adjustable dials (weights) that start RANDOM and therefore USELESS.
#
# Reframed as a puzzle (locked 8-beat sheet, one self.next_section per beat,
# each timed to dur_sec so the visual locks to the spoken sentence):
#   1 in/out     fingerprint enters left "numbers in"; faint empty guess slot
#                appears far right "a guess out". Nothing between.
#   2 question   a dim "?" box pulses in the empty middle gap; both ends dim.
#   3 stack      the "?" resolves into 3 dial-banks (layers); label above.
#   4 flow       one bright pulse rides in -> L1 -> L2 -> L3 -> output.
#   5 brace      a quiet brace over the stack: "no hand-written rules — only dials".
#   6 nonsense   the guess pops out dim & garbled, flickering nonsense strings.
#   7 dials      threads + output dim; only the dial-banks stay lit, one pulse.
#   8 name       serif #fff payoff "a function of its dials"; brief poster hold.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"  # the SINGLE payoff accent

MID_Y = 0.35
BOT_Y = -3.05
X_L = -6.4
X_R = 6.4


def tri(angle, c, op=1.0, s=0.085):
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


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
    ring = Circle(radius=radius, stroke_color=c, stroke_width=sw,
                  fill_color=BG, fill_opacity=0)
    pointer = Line(ring.get_center(),
                   ring.get_center() + radius * 0.92 * np.array(
                       [np.cos(angle), np.sin(angle), 0.0]),
                   stroke_color=c, stroke_width=sw)
    g = VGroup(ring, pointer)
    g.set_stroke(opacity=op)
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


def _box_pts(box, side, n, span):
    """`n` points spread +/-span vertically on the box's right/left edge."""
    x = (box.get_right() if side[0] > 0 else box.get_left())[0]
    cy = box.get_center()[1]
    return [np.array([x, cy + y, 0.0]) for y in np.linspace(-span, span, n)]


def _edge_at_knobs(box, bank, side):
    """Points exactly on the box edge, one aligned to each dial's height —
    so the threads attach across the whole edge, dial by dial."""
    x = (box.get_right() if side[0] > 0 else box.get_left())[0]
    return [np.array([x, kn[0].get_center()[1], 0.0]) for kn in bank]


def connect(left_pts, right_pts, c=INK_GHOST, w=0.65):
    """Fully-connected faint threads between two sets of anchor points."""
    tg = VGroup()
    for lp in left_pts:
        for rp in right_pts:
            tg.add(Line(lp, rp, stroke_color=c, stroke_width=w))
    return tg


class WhatIsANet(Scene):
    def construct(self):
        seed()

        out_x = X_R - 1.15

        # =================================================================
        # BEAT 1 — IN / OUT (~1.37s): fingerprint in left, empty guess slot right.
        # =================================================================
        self.next_section("in_out")

        fp = fingerprint_row(12, 1.7, 0.95, 0.9, seedval=11)
        fp_box = SurroundingRectangle(fp, color=INK_FAINT, stroke_width=1.4, buff=0.16,
                                      fill_color=BG, fill_opacity=0)
        fp_card = VGroup(fp_box, fp).move_to([X_L + 1.05, MID_Y, 0])
        in_lbl = mono("numbers in", 18, INK_DIM).next_to(fp_card, UP, buff=0.22)

        out_slot = RoundedRectangle(width=1.5, height=0.9, corner_radius=0.08,
                                    stroke_color=INK_GHOST, stroke_width=1.4,
                                    fill_color=BG, fill_opacity=0)
        out_slot.move_to([out_x, MID_Y, 0])
        out_lbl = mono("a guess out", 18, INK_FAINT).next_to(out_slot, UP, buff=0.22)

        self.play(
            LaggedStart(*[FadeIn(b, shift=UP * 0.05) for b in fp], lag_ratio=0.03),
            Create(fp_box),
            FadeIn(in_lbl, shift=DOWN * 0.08),
            run_time=0.7,
        )
        self.play(Create(out_slot),
                  FadeIn(out_lbl, shift=DOWN * 0.06), run_time=0.5)
        self.wait(0.15)

        # =================================================================
        # BEAT 2 — QUESTION (~1.17s): a "?" box pulses in the empty middle gap.
        # =================================================================
        self.next_section("question")

        q_box = RoundedRectangle(width=1.6, height=1.6, corner_radius=0.1,
                                 stroke_color=INK_FAINT, stroke_width=1.5,
                                 fill_color=BG, fill_opacity=0).move_to([0, MID_Y, 0])
        q_mark = mono("?", 54, INK_DIM).move_to(q_box)

        self.play(
            VGroup(fp_card, in_lbl).animate.set_opacity(0.45),
            VGroup(out_slot, out_lbl).animate.set_opacity(0.45),
            FadeIn(q_box, scale=0.85),
            FadeIn(q_mark, scale=0.85),
            run_time=0.6,
        )
        self.play(VGroup(q_box, q_mark).animate.scale(1.08), run_time=0.28)
        self.play(VGroup(q_box, q_mark).animate.scale(1 / 1.08), run_time=0.18)
        self.wait(0.1)

        # =================================================================
        # BEAT 3 — STACK (~2.45s): the "?" resolves into 3 dial-banks (layers).
        # =================================================================
        self.next_section("stack")

        n_layers = 3
        layer_x = [-2.2, 0.0, 2.2]
        knob_r = 0.16
        n_knobs = 5
        banks = VGroup()
        layer_boxes = VGroup()
        layer_caps = VGroup()
        for li, lx in enumerate(layer_x):
            bank = dial_bank(n_knobs, knob_r, [lx, MID_Y, 0],
                             c=INK_DIM, op=0.85, seedval=20 + li)
            box = SurroundingRectangle(bank, color=INK_GHOST, stroke_width=1.3,
                                       buff=0.20, corner_radius=0.06,
                                       fill_color=BG, fill_opacity=0)
            cap = mono(f"layer {li + 1}", 13, INK_FAINT).next_to(box, DOWN, buff=0.14)
            banks.add(bank)
            layer_boxes.add(box)
            layer_caps.add(cap)

        stack_lbl = mono("a deep stack of layers", 18, INK_DIM)
        stack_lbl.move_to([layer_x[1], MID_Y + 2.0, 0])

        # bring the input/output ends back up as the unknown is resolved.
        self.play(
            FadeOut(q_mark, scale=1.2),
            ReplacementTransform(q_box, layer_boxes[1]),
            VGroup(fp_card, in_lbl).animate.set_opacity(1.0),
            VGroup(out_slot, out_lbl).animate.set_opacity(0.6),
            run_time=0.55,
        )
        self.play(
            LaggedStart(
                FadeIn(VGroup(layer_boxes[0], banks[0]), shift=UP * 0.1),
                FadeIn(banks[1], shift=UP * 0.1),
                FadeIn(VGroup(layer_boxes[2], banks[2]), shift=UP * 0.1),
                lag_ratio=0.25),
            LaggedStart(*[FadeIn(c) for c in layer_caps], lag_ratio=0.2),
            FadeIn(stack_lbl, shift=DOWN * 0.08),
            run_time=1.0,
        )

        # connection threads, anchored ON each box edge at every dial's height
        # (full-edge coverage) so the layers read as truly wired together.
        anchors = [fp_card] + [layer_boxes[i] for i in range(n_layers)]
        thread_groups = [
            connect(_box_pts(fp_box, RIGHT, 4, 0.42),
                    _edge_at_knobs(layer_boxes[0], banks[0], LEFT)),
            connect(_edge_at_knobs(layer_boxes[0], banks[0], RIGHT),
                    _edge_at_knobs(layer_boxes[1], banks[1], LEFT)),
            connect(_edge_at_knobs(layer_boxes[1], banks[1], RIGHT),
                    _edge_at_knobs(layer_boxes[2], banks[2], LEFT)),
        ]
        all_threads = VGroup(*thread_groups)
        self.play(LaggedStart(*[Create(tg) for tg in thread_groups],
                              lag_ratio=0.2), run_time=0.55)
        self.wait(0.1)

        # =================================================================
        # BEAT 4 — FLOW (~2.24s): one bright pulse rides in -> L1 -> L2 -> L3 -> out.
        # =================================================================
        self.next_section("flow")

        # short output vector replaces the empty slot as the pulse arrives.
        out_vec = fingerprint_row(6, 0.85, 0.85, 0.9, seedval=4)
        out_box = SurroundingRectangle(out_vec, color=INK_FAINT, stroke_width=1.4,
                                       buff=0.14, fill_color=BG, fill_opacity=0)
        out_card = VGroup(out_box, out_vec).move_to(out_slot.get_center())
        out_thread = connect(_edge_at_knobs(layer_boxes[-1], banks[-1], RIGHT),
                             _box_pts(out_card, LEFT, 3, 0.3))
        self.add(out_thread)
        out_thread.set_stroke(INK_GHOST, width=0.65)

        ride = anchors + [out_card]
        rt_legs = all_threads.copy()  # not used; just keep names clear
        legs = thread_groups + [out_thread]
        for li in range(len(ride) - 1):
            pulse = Rectangle(width=0.16, height=1.1, stroke_width=0,
                              fill_color=WHITE, fill_opacity=0.6)
            pulse.move_to(ride[li].get_right() + RIGHT * 0.05)
            self.add(pulse)
            self.play(
                pulse.animate.move_to(ride[li + 1].get_left() + LEFT * 0.05),
                legs[li].animate.set_stroke(INK_FAINT, width=1.0),
                run_time=0.4, rate_func=linear,
            )
            self.remove(pulse)
            if li < n_layers:
                self.play(banks[li].animate.set_stroke(INK, opacity=0.95)
                          .scale(1.06), run_time=0.16)
                self.play(banks[li].animate.scale(1 / 1.06), run_time=0.1)

        # the output vector lands where the empty slot was.
        self.play(
            FadeOut(out_slot), FadeOut(out_lbl, shift=UP * 0.06),
            LaggedStart(*[FadeIn(b) for b in out_vec], lag_ratio=0.05),
            Create(out_box),
            run_time=0.45,
        )
        new_out_lbl = mono("a guess out", 18, INK_DIM).next_to(out_card, UP, buff=0.22)
        self.add(new_out_lbl)
        self.wait(0.1)

        # =================================================================
        # BEAT 5 — BRACE (~1.63s): "no hand-written rules — only dials".
        # =================================================================
        self.next_section("brace")

        self.play(FadeOut(stack_lbl), run_time=0.25)
        brace = Brace(VGroup(layer_boxes, banks), UP, color=INK_GHOST,
                      buff=0.22).set_stroke(width=1)
        brace_lbl = mono("no hand-written rules — only dials", 17, INK_DIM)
        brace_lbl.next_to(brace, UP, buff=0.12)
        self.play(GrowFromCenter(brace),
                  FadeIn(brace_lbl, shift=UP * 0.06), run_time=0.7)
        self.wait(0.6)

        # =================================================================
        # BEAT 6 — NONSENSE (~1.82s): the guess pops out dim & garbled.
        # =================================================================
        self.next_section("nonsense")

        guess = mono("?qz·le?", 26, INK_FAINT).next_to(out_card, DOWN, buff=0.34)
        guess_tag = mono("first guess — nonsense", 13, INK_GHOST)
        guess_tag.next_to(guess, DOWN, buff=0.12)
        self.play(FadeIn(guess, shift=DOWN * 0.06, scale=0.9),
                  FadeIn(guess_tag), run_time=0.5)
        for s in ["zx?·ql", "?gv·tk?", "qz·le?"]:
            g2 = mono(s, 26, INK_FAINT).move_to(guess)
            self.play(Transform(guess, g2), run_time=0.22)
        self.wait(0.5)

        # =================================================================
        # BEAT 7 — DIALS (~1.71s): threads + output dim; only the dials stay lit.
        # =================================================================
        self.next_section("dials")

        dimmed = VGroup(fp_card, in_lbl, all_threads, out_thread, out_card,
                        new_out_lbl, guess, guess_tag, brace, brace_lbl)
        self.play(dimmed.animate.set_opacity(0.18), run_time=0.55)
        self.play(banks.animate.set_stroke(INK, opacity=1.0).scale(1.06),
                  run_time=0.45)
        self.play(banks.animate.scale(1 / 1.06), run_time=0.4)
        self.wait(0.25)

        # =================================================================
        # BEAT 8 — NAME (~1.17s): serif #fff payoff + poster hold.
        # =================================================================
        self.next_section("name")

        payoff = serif("a function of its dials", 44, WHITE).move_to([0, BOT_Y + 0.2, 0])
        sub = mono("all it knows is how they are set", 17, INK_DIM)
        sub.next_to(payoff, DOWN, buff=0.20)
        glow_payoff = glow(payoff.copy())
        self.add(glow_payoff)
        self.play(Write(payoff),
                  glow_payoff.animate.set_opacity(0.0), run_time=0.6)
        self.remove(glow_payoff)
        self.play(FadeIn(sub, shift=UP * 0.08),
                  Indicate(payoff, scale_factor=1.05, color=WHITE), run_time=0.35)
        self.wait(0.3)
