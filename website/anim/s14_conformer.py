# website/anim/s14_conformer.py  —  S14 "The reader (Conformer)"
# The encoder reads one frame-strip through TWO superimposed lenses at once:
# a GLOBAL attention web bowing into the whole top half, and a LOCAL k=31
# convolution bracket sliding along the bottom half. We hold the strip dead
# centre as a living spine and let both lenses operate on it SIMULTANEOUSLY
# (the wow), then fuse into one CONFORMER block whose "smallness" is staged as
# a deliberate choice against a looming oversized stack.
#
# Three zones, full canvas:
#   TOP  (y ~ +2.8..+3.5): context recap -> spec ledger that fills token by token
#   CENTER (y ~ -2.2..+2.4): the spine + the two lenses (the star)
#   BOTTOM (y ~ -3.6..-2.6): "two lenses, one reader" -> capacity readout + the
#                            "small on purpose — one person, 8,500 sentences" tally
#
# Ground truth (brief §6.2): Conformer = self-attention + depthwise conv;
# 4 layers, 4 heads, ffn 1024, kernel 31; small to avoid overfitting a single
# subject with 8,500 sentences. Strict monochrome.
from manim import *
from emg_style import *


class Conformer(Scene):
    def construct(self):
        seed()

        N = 13            # time-frame squares along the spine
        SPINE_Y = -0.10   # spine sits dead centre; web bows up, bracket slides below
        FOCUS = 6         # the "current" frame (centre of the strip)

        # ============================================================
        #  THE SPINE  (centre zone, persistent for the whole clip)
        # ============================================================
        frames = VGroup(*[
            Square(0.40, stroke_color=INK, stroke_width=1.4, fill_opacity=0)
            for _ in range(N)
        ]).arrange(RIGHT, buff=0.16).move_to(np.array([0, SPINE_Y, 0]))

        x0 = frames[0].get_left()[0]
        x1 = frames[-1].get_right()[0]

        # ------------------------------------------------------------
        #  TOP ZONE — recap line + a full-width ghost tick-axis (S13 callback)
        # ------------------------------------------------------------
        recap = mono("a finished recording, read both ways", 20, INK_GHOST)
        recap.move_to(np.array([0, 3.30, 0]))

        axis = Line(np.array([-6.0, 2.78, 0]), np.array([6.0, 2.78, 0]),
                    stroke_color=INK_GHOST, stroke_width=1.4)
        ticks = VGroup(*[
            Line(np.array([x, 2.78, 0]), np.array([x, 2.66, 0]),
                 stroke_color=INK_GHOST, stroke_width=1.2)
            for x in np.linspace(-6.0, 6.0, 25)
        ])

        # ------------------------------------------------------------
        #  BOTTOM ZONE — early takeaway
        # ------------------------------------------------------------
        take = mono("two lenses, one reader", 22, INK_DIM)
        take.move_to(np.array([0, -3.30, 0]))

        # ============================================================
        #  BEAT 0 — POSE  (0.0 - 1.4s)
        # ============================================================
        self.play(
            FadeIn(recap, shift=DOWN * 0.12),
            Create(axis), LaggedStartMap(Create, ticks, lag_ratio=0.02, run_time=0.6),
            run_time=0.6,
        )
        self.play(
            LaggedStartMap(Create, frames, lag_ratio=0.05, run_time=0.6),
            FadeIn(take, shift=UP * 0.1, run_time=0.5),
        )

        # ============================================================
        #  helpers — arcs that bow UPWARD between frame tops
        # ============================================================
        def arc(i, j, color, width, op):
            p, q = frames[i].get_top(), frames[j].get_top()
            span = abs(j - i)
            # far spans bow higher (reach into the upper third), clamped < y+2.4
            a = ArcBetweenPoints(p, q, angle=-PI * min(0.62, 0.20 + 0.045 * span))
            a.set_stroke(color=color, width=width, opacity=op)
            return a

        def full_web(width, op):
            return VGroup(*[arc(i, j, INK_FAINT, width, op)
                            for i in range(N) for j in range(i + 1, N)])

        # ------------------------------------------------------------
        #  TOP ZONE becomes a left-aligned SPEC LEDGER that fills token by token
        # ------------------------------------------------------------
        LEDGER_X = -6.0
        LEDGER_Y = 3.30
        ledger = VGroup()  # we append mono lines to this as beats land

        def ledger_line(text, c=INK_DIM):
            return mono(text, 18, c)

        # ============================================================
        #  BEAT 1 — GLOBAL LENS (1.4 - 3.6s) : fills the UPPER canvas
        # ============================================================
        # recap cross-fades into the first ledger token
        l1 = ledger_line("self-attention · 4 heads", INK_DIM)
        l1.move_to(np.array([0, LEDGER_Y, 0]))
        l1.align_to(np.array([LEDGER_X, 0, 0]), LEFT)
        self.play(
            recap.animate.become(l1),
            FadeOut(axis), FadeOut(ticks),
            run_time=0.5,
        )
        ledger.add(recap)  # recap is now the first ledger token

        # light the focus frame to pure white, draw reach-arcs to every frame
        reach = VGroup(*[arc(FOCUS, j, INK, 2.0, 0.9) for j in range(N) if j != FOCUS])
        self.play(
            frames[FOCUS].animate.set_stroke(width=2.8, color="#ffffff"),
            LaggedStartMap(Create, reach, lag_ratio=0.045, run_time=0.75),
        )

        gloss = mono("every moment pulls context from anywhere", 19, INK_FAINT)
        gloss.next_to(frames, DOWN, buff=0.52)
        self.play(FadeIn(gloss), run_time=0.3)

        # context pulse: bright dots travel each arc BACK into the focus frame
        pulses = VGroup(*[Dot(radius=0.05, color="#ffffff") for _ in reach])
        for d, a in zip(pulses, reach):
            d.move_to(a.get_start())
        self.add(pulses)
        self.play(
            *[MoveAlongPath(d, a.copy().reverse_points()) for d, a in zip(pulses, reach)],
            run_time=0.6, rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(pulses)

        # bloom into the full all-pairs web filling the upper third
        web = full_web(1.4, 0.6)
        self.play(
            FadeOut(reach),
            frames[FOCUS].animate.set_stroke(width=1.6, color=INK),
            Create(web), run_time=0.75,
        )

        # ============================================================
        #  BEAT 2 — LOCAL LENS (3.6 - 5.8s) : fills the LOWER canvas
        # ============================================================
        # web dims but STAYS (so we can re-brighten it for the wow)
        self.play(web.animate.set_stroke(opacity=0.28), run_time=0.3)

        # ledger appends the conv token below the first
        l2 = ledger_line("+ depthwise conv · kernel 31", INK_DIM)
        l2.next_to(recap, DOWN, buff=0.16).align_to(recap, LEFT)
        ledger.add(l2)
        self.play(
            FadeIn(l2, shift=DOWN * 0.06),
            gloss.animate.become(
                mono("and the fine texture right around each moment", 19, INK_FAINT)
                .next_to(frames, DOWN, buff=0.52)
            ),
            run_time=0.4,
        )

        # k=31 honoured as a WIDE window spanning ~7 frames, BELOW the spine.
        HALF = 3  # half-window -> spans 2*3+1 = 7 frames

        def window_frames(c):
            lo = max(0, c - HALF)
            hi = min(N - 1, c + HALF)
            return VGroup(*[frames[k] for k in range(lo, hi + 1)])

        def bracket_at(c):
            grp = window_frames(c)
            r = SurroundingRectangle(grp, color=INK, stroke_width=2.6, buff=0.10)
            r.set_stroke(opacity=1.0)
            # shift the bracket DOWN so it reads as the lower lens around the spine
            return r

        # mini "local texture" trace under a window (short jagged VMobject) —
        # sits clearly BELOW the spine in its own band so it never hits the gloss.
        def mini_trace(c):
            grp = window_frames(c)
            lx = grp.get_left()[0] + 0.08
            rx = grp.get_right()[0] - 0.08
            base_y = -1.30
            xs = np.linspace(lx, rx, 60)
            ph = c * 1.7
            ys = (0.12 * np.sin(xs * 9.0 + ph)
                  + 0.06 * np.sin(xs * 23.0 + ph * 1.3))
            t = VMobject(stroke_color=INK_FAINT, stroke_width=1.6)
            t.set_points_as_corners([np.array([x, base_y + y, 0]) for x, y in zip(xs, ys)])
            return t

        c0 = 3
        brk = bracket_at(c0)
        ktag = mono("k=31", 16, INK_DIM).next_to(brk, UP, buff=0.10)
        trace0 = mini_trace(c0)
        self.play(Create(brk), FadeIn(ktag), Create(trace0), run_time=0.42)

        prev_trace = trace0
        for c in (5, 8, 10):
            tgt = bracket_at(c)
            tr = mini_trace(c)
            self.play(
                Transform(brk, tgt),
                ktag.animate.next_to(tgt, UP, buff=0.10),
                FadeOut(prev_trace, run_time=0.20),
                Create(tr),
                Indicate(window_frames(c), scale_factor=1.06, color=INK),
                run_time=0.34,
            )
            prev_trace = tr

        # ============================================================
        #  BEAT 3 — BOTH AT ONCE  (5.8 - 7.6s)  ← THE WOW
        #  re-brighten the web while the bracket is still live & parked
        # ============================================================
        # park the bracket at the focus column, keep its trace; the web
        # RE-brightens (it never left), the ffn token lands in the ledger, and
        # the gloss names both lenses — all at once, building to the wow.
        focus_brk = bracket_at(FOCUS)
        focus_tr = mini_trace(FOCUS)
        l3 = ledger_line("ffn 1024", INK_DIM)
        l3.next_to(l2, DOWN, buff=0.16).align_to(l2, LEFT)
        ledger.add(l3)
        self.play(
            Transform(brk, focus_brk),
            ktag.animate.next_to(focus_brk, UP, buff=0.10),
            FadeOut(prev_trace, run_time=0.3),
            Create(focus_tr),
            web.animate.set_stroke(opacity=0.55),
            FadeIn(l3, shift=DOWN * 0.06),
            gloss.animate.become(
                mono("the whole sentence  +  the fine local detail", 19, INK)
                .next_to(frames, DOWN, buff=0.52)
            ),
            run_time=0.5,
        )
        prev_trace = focus_tr

        # the single frame where the WHOLE canvas is in use, top to bottom:
        #   web bowing above · spine glowing · bracket sitting below
        self.play(
            frames[FOCUS].animate.set_stroke(width=2.8, color="#ffffff"),
            Flash(frames[FOCUS], color=INK, line_length=0.20,
                  num_lines=14, flash_radius=0.50),
            run_time=0.5,
        )
        self.wait(0.3)

        # ============================================================
        #  BEAT 4 — FUSE TO ONE BLOCK  (7.6 - 9.4s)
        # ============================================================
        block = RoundedRectangle(width=2.7, height=1.0, corner_radius=0.12,
                                 stroke_color=INK, stroke_width=2.2, fill_opacity=0)
        block.move_to(frames.get_center())
        blabel = mono("CONFORMER", 22, INK).move_to(block.get_center())

        apparatus = VGroup(frames, web, brk, focus_tr, ktag)
        self.play(
            ReplacementTransform(apparatus, block),
            FadeIn(blabel),
            FadeOut(gloss),
            run_time=0.8,
        )
        block_spec = mono("attn  +  depthwise conv", 16, INK_FAINT)
        block_spec.next_to(block, DOWN, buff=0.22)
        # name the block AND repurpose the bottom takeaway into a capacity track
        self.play(
            FadeIn(block_spec),
            take.animate.become(mono("model size", 16, INK_FAINT)
                               .move_to(np.array([-5.2, -3.00, 0]))),
            run_time=0.4,
        )

        # ============================================================
        #  BEAT 5 — SMALL ON PURPOSE + POSTER  (9.4 - 12.0s)
        # ============================================================
        # slide the fused block up-left to make room for the contrast
        self.play(
            VGroup(block, blabel).animate.scale(0.88).move_to(np.array([-3.4, 1.05, 0])),
            FadeOut(block_spec),
            run_time=0.5,
        )

        def stack(n, x, y, h=0.22, w=1.9):
            return VGroup(*[
                RoundedRectangle(width=w, height=h, corner_radius=0.05,
                                 stroke_color=INK, stroke_width=1.7, fill_opacity=0)
                for _ in range(n)
            ]).arrange(DOWN, buff=0.08).move_to(np.array([x, y, 0]))

        # compact 4-layer stack — the conformer is just this
        small = stack(4, -3.4, -0.95)
        small_lab = mono("4 layers", 19, INK_DIM).next_to(small, DOWN, buff=0.22)
        feed = Arrow(block.get_bottom(), small.get_top(),
                     stroke_color=INK_FAINT, stroke_width=2.0, buff=0.12,
                     max_tip_length_to_length_ratio=0.18)
        self.play(
            GrowArrow(feed),
            LaggedStartMap(FadeIn, small, lag_ratio=0.12, run_time=0.5),
            FadeIn(small_lab),
            run_time=0.5,
        )
        ok = mono("just right", 16, INK_FAINT).next_to(small, RIGHT, buff=0.32)

        # the looming oversized stack on the right (would memorize) +
        # the capacity bar appear together — ghost extends far past the reader.
        big = stack(14, 3.4, 0.10, h=0.16, w=2.1).set_stroke(opacity=0.5)
        big_lab = mono("would memorize", 18, INK_FAINT).next_to(big, DOWN, buff=0.22)
        bar_y = -3.00
        bar_lo, bar_hi = -4.0, 5.4
        track = Line(np.array([bar_lo, bar_y, 0]), np.array([bar_hi, bar_y, 0]),
                     stroke_color=INK_GHOST, stroke_width=2.0)
        small_x = bar_lo + 0.10 * (bar_hi - bar_lo)
        reader_seg = Line(np.array([bar_lo, bar_y, 0]), np.array([small_x, bar_y, 0]),
                          stroke_color=INK, stroke_width=3.0)
        marker = Dot(np.array([small_x, bar_y, 0]), radius=0.06, color="#ffffff")
        reader_tick = mono("this reader", 14, INK_DIM).next_to(marker, UP, buff=0.10)
        self.play(
            FadeIn(ok),
            LaggedStartMap(FadeIn, big, lag_ratio=0.04, run_time=0.45),
            FadeIn(big_lab),
            Create(track),
            run_time=0.5,
        )
        self.play(
            Create(reader_seg), FadeIn(marker), FadeIn(reader_tick),
            run_time=0.35,
        )

        # cross out the big stack, then dim it while the small stack lifts to white
        cross = VGroup(
            Line(big.get_corner(UL), big.get_corner(DR), stroke_color="#ffffff", stroke_width=4),
            Line(big.get_corner(UR), big.get_corner(DL), stroke_color="#ffffff", stroke_width=4),
        )
        self.play(Create(cross), run_time=0.35)
        # dim BOTH the big stack and its cross down to ghost so the ONLY pure-#fff
        # accent left at rest is the small stack lifting — keeps monochrome depth.
        self.play(
            VGroup(big, big_lab).animate.set_opacity(0.26),
            cross.animate.set_stroke(color=INK_FAINT, opacity=0.40),
            small.animate.set_stroke(width=2.4, color="#ffffff"),
            run_time=0.4,
        )

        # the punchline assembles with the 8,500 ticking UP via counter().
        # Reserve the number's slot first (using the final value's width) so the
        # ticking digits never push the surrounding words around.
        PUNCH_Y = -3.62
        line_a = mono("small on purpose — one person,", 19, INK)
        line_b = mono("sentences", 19, INK)
        sample = mono("8,500", 19, "#ffffff")  # reserves the slot width
        # arrange the three pieces in a row (Pango strips literal spaces, so use
        # buff for the gaps), then centre the whole line
        layout = VGroup(line_a.copy(), sample.copy(), line_b.copy())
        layout.arrange(RIGHT, buff=0.16).move_to(np.array([0, PUNCH_Y, 0]))
        line_a.move_to(layout[0]).align_to(layout[0], LEFT)
        slot_center = layout[1].get_center()
        line_b.move_to(layout[2]).align_to(layout[2], LEFT)

        n_tracker = ValueTracker(0)
        num_txt = counter(
            n_tracker,
            fmt=lambda v: f"{int(round(v)):,}",
            s=19, c="#ffffff",
            at=slot_center,
        )

        self.add(num_txt)
        self.play(FadeIn(line_a), FadeIn(line_b), run_time=0.35)
        self.play(n_tracker.animate.set_value(8500), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        n_tracker.set_value(8500)
        num_txt.clear_updaters()
        num_txt.become(mono("8,500", 19, "#ffffff").move_to(slot_center))

        # top strip stamps the FULL spec (replaces the running ledger)
        full_spec = mono("self-attention · 4 heads · ffn 1024 · kernel 31 · 4 layers",
                         18, INK_DIM)
        full_spec.move_to(np.array([0, 3.30, 0]))
        self.play(
            ReplacementTransform(ledger, full_spec),
            run_time=0.5,
        )

        self.wait(0.6)
