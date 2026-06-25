# website/anim/s14_conformer.py  —  S14 "The reader (Conformer)"
#
# CALLBACK, not a lesson. The viewer already learned attention (b09) and
# convolution (b10). So both lenses arrive ALREADY KNOWN and quiet on a central
# spine of snapshots: a faint global reach-web bows above, a local sliding-window
# bracket sits below. The discovery is "what if BOTH at the very same time?" —
# the WOW is both lenses landing on ONE snapshot together (white flare). Then the
# whole apparatus fuses into one CONFORMER block, which is kept tiny — 4 layers —
# because a bigger reader would only memorize one person's data.
#
# Locked 5-beat sheet (one self.next_section per spoken sentence, timed to dur_sec):
#   1 recap     spine + web (faint above) + bracket (below), both static, quiet.
#   2 question  both lenses dim to a hold; a single "both at once?" caption rises;
#               the focus snapshot pulses.
#   3 WOW       web re-brightens + bracket parks on focus + focus flares white.
#   4 fuse      apparatus collapses into one CONFORMER block ("attn + depthwise conv").
#   5 small     block feeds a 4-layer stack lifting to white; an oversized ghost
#               stack on the right is crossed out + dimmed. "4 layers" settles.
#
# STRICT MONOCHROME on #050505. One white accent per beat. No LaTeX.
from manim import *
from emg_style import *


class Conformer(Scene):
    def construct(self):
        seed()

        N = 13            # time-frame squares along the spine
        SPINE_Y = -0.10   # spine dead centre; web bows up, bracket sits below
        FOCUS = 6         # the "current" frame at the centre of the strip

        # ============================================================
        #  SHARED GEOMETRY
        # ============================================================
        frames = VGroup(*[
            Square(0.40, stroke_color=INK, stroke_width=1.4, fill_opacity=0)
            for _ in range(N)
        ]).arrange(RIGHT, buff=0.16).move_to(np.array([0, SPINE_Y, 0]))

        def arc(i, j, color, width, op):
            p, q = frames[i].get_top(), frames[j].get_top()
            span = abs(j - i)
            a = ArcBetweenPoints(p, q, angle=-PI * min(0.62, 0.20 + 0.045 * span))
            a.set_stroke(color=color, width=width, opacity=op)
            return a

        def full_web(width, op):
            return VGroup(*[arc(i, j, INK_FAINT, width, op)
                            for i in range(N) for j in range(i + 1, N)])

        HALF = 3  # local window spans 2*3+1 = 7 frames (k=31 stand-in)

        def window_frames(c):
            lo = max(0, c - HALF)
            hi = min(N - 1, c + HALF)
            return VGroup(*[frames[k] for k in range(lo, hi + 1)])

        def bracket_at(c):
            r = SurroundingRectangle(window_frames(c), color=INK,
                                     stroke_width=2.6, buff=0.10)
            r.set_stroke(opacity=1.0)
            return r

        # ============================================================
        #  BEAT 1 — RECAP (~3.43s): both lenses already present, quiet.
        # ============================================================
        self.next_section("recap")

        recap = mono("two ways of reading — already met", 20, INK_FAINT)
        recap.move_to(np.array([0, 3.20, 0]))

        self.play(
            FadeIn(recap, shift=DOWN * 0.10),
            LaggedStart(*[Create(f) for f in frames], lag_ratio=0.05),
            run_time=0.9,
        )

        # GLOBAL lens: a faint reach-web bows into the upper canvas, static.
        web = full_web(1.3, 0.40)
        glo_lab = mono("global reach", 16, INK_FAINT)
        glo_lab.move_to(np.array([0, 1.95, 0]))
        self.play(Create(web), FadeIn(glo_lab), run_time=0.9)

        # LOCAL lens: a sliding-window bracket sits below, static, on the focus.
        brk = bracket_at(FOCUS)
        loc_lab = mono("local window", 16, INK_FAINT)
        loc_lab.next_to(window_frames(FOCUS), DOWN, buff=0.30)
        self.play(Create(brk), FadeIn(loc_lab), run_time=0.8)
        self.wait(0.83)

        # ============================================================
        #  BEAT 2 — QUESTION (~1.31s): dim both to a hold; raise the loop.
        # ============================================================
        self.next_section("question")

        question = mono("both at once?", 22, INK)
        question.next_to(frames, DOWN, buff=1.05)

        self.play(
            web.animate.set_stroke(opacity=0.16),
            brk.animate.set_stroke(opacity=0.30),
            glo_lab.animate.set_opacity(0.20),
            loc_lab.animate.set_opacity(0.20),
            recap.animate.set_opacity(0.16),
            FadeIn(question, shift=UP * 0.10),
            Indicate(frames[FOCUS], scale_factor=1.18, color=INK),
            run_time=0.9,
        )
        self.wait(0.41)

        # ============================================================
        #  BEAT 3 — WOW (~2.40s): both lenses land on ONE snapshot together.
        # ============================================================
        self.next_section("wow")

        focus_brk = bracket_at(FOCUS)
        self.play(
            web.animate.set_stroke(opacity=0.60),
            Transform(brk, focus_brk),
            question.animate.become(
                mono("the whole sentence  +  the fine local detail", 19, INK)
                .next_to(frames, DOWN, buff=1.05)
            ),
            run_time=0.8,
        )

        # the single frame where the WHOLE canvas is in use, top to bottom.
        flare = glow(frames[FOCUS].copy().set_stroke(color=WHITE, width=2.8))
        self.add(flare)
        self.play(
            frames[FOCUS].animate.set_stroke(width=2.8, color=WHITE),
            Flash(frames[FOCUS], color=INK, line_length=0.22,
                  num_lines=16, flash_radius=0.52),
            flare.animate.set_opacity(0.0),
            run_time=0.8,
        )
        self.remove(flare)
        self.wait(0.8)

        # ============================================================
        #  BEAT 4 — FUSE (~1.62s): apparatus collapses into one block.
        # ============================================================
        self.next_section("fuse")

        block = RoundedRectangle(width=2.9, height=1.0, corner_radius=0.12,
                                 stroke_color=INK, stroke_width=2.4, fill_opacity=0)
        block.move_to(frames.get_center())
        blabel = mono("CONFORMER", 22, INK).move_to(block.get_center())

        apparatus = VGroup(frames, web, brk, glo_lab, loc_lab)
        self.play(
            ReplacementTransform(apparatus, block),
            FadeIn(blabel),
            FadeOut(question),
            FadeOut(recap),
            run_time=0.9,
        )
        block_spec = mono("attention  +  depthwise conv", 16, INK_FAINT)
        block_spec.next_to(block, DOWN, buff=0.26)
        self.play(FadeIn(block_spec), run_time=0.4)
        self.wait(0.32)

        # ============================================================
        #  BEAT 5 — SMALL ON PURPOSE + POSTER (~3.21s)
        # ============================================================
        self.next_section("small")

        # slide the block up-left to make room for the contrast.
        self.play(
            VGroup(block, blabel).animate.scale(0.86).move_to(np.array([-3.4, 1.30, 0])),
            FadeOut(block_spec),
            run_time=0.6,
        )

        def stack(n, x, y, h, w):
            return VGroup(*[
                RoundedRectangle(width=w, height=h, corner_radius=0.05,
                                 stroke_color=INK, stroke_width=1.7, fill_opacity=0)
                for _ in range(n)
            ]).arrange(DOWN, buff=0.10).move_to(np.array([x, y, 0]))

        # the compact 4-layer stack — the conformer is just this.
        small = stack(4, -3.4, -1.05, h=0.30, w=2.0)
        small_lab = mono("4 layers", 20, INK_DIM).next_to(small, DOWN, buff=0.26)
        feed = Line(VGroup(block, blabel).get_bottom() + DOWN * 0.04,
                    small.get_top() + UP * 0.04,
                    stroke_color=INK_FAINT, stroke_width=2.0)
        feed_head = Triangle(stroke_width=0, fill_color=INK_FAINT,
                             fill_opacity=0.9).scale(0.10).rotate(PI)
        feed_head.move_to(small.get_top() + UP * 0.05)
        self.play(
            Create(feed), FadeIn(feed_head),
            LaggedStart(*[FadeIn(s, shift=DOWN * 0.06) for s in small], lag_ratio=0.12),
            FadeIn(small_lab),
            run_time=0.8,
        )

        # the looming oversized ghost stack on the right (would memorize).
        big = stack(13, 3.4, 0.05, h=0.18, w=2.1).set_stroke(opacity=0.45)
        big_lab = mono("bigger → memorizes", 17, INK_FAINT).next_to(big, DOWN, buff=0.24)
        self.play(
            LaggedStart(*[FadeIn(s) for s in big], lag_ratio=0.04),
            FadeIn(big_lab),
            run_time=0.6,
        )

        # cross out the big stack; dim it; the small stack lifts to white.
        cross = VGroup(
            Line(big.get_corner(UL), big.get_corner(DR), stroke_color=WHITE, stroke_width=4),
            Line(big.get_corner(UR), big.get_corner(DL), stroke_color=WHITE, stroke_width=4),
        )
        self.play(Create(cross), run_time=0.5)
        self.play(
            VGroup(big, big_lab).animate.set_opacity(0.22),
            cross.animate.set_stroke(color=INK_FAINT, opacity=0.40),
            small.animate.set_stroke(width=2.6, color=WHITE),
            small_lab.animate.set_color(INK),
            run_time=0.6,
        )

        # poster hold.
        self.wait(0.61)
