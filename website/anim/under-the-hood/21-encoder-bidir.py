# S13 — Looking both ways (causal vs bidirectional)
# Goal: to name a sound at one instant, it helps to see frames *before AND after*.
#
# Locked 7-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 pose      one snapshot, sound is a toss-up — serif "?" + "now" needle      (1.87s)
#   2 candidates "?" -> flickering "D?" / "T?", neither winning                  (1.01s)
#   3 causal    LIVE dot; future dims; 6 LEFT arrows; bar fills left half        (3.44s)
#   4 hedged    "T?" brightens over "D?" but both stay; "live: limited"         (0.84s)
#   5 finished  LIVE fades; future re-lights; label -> BIDIRECTIONAL            (1.76s)
#   6 collapse  6 RIGHT arrows; bar fills full; "D?/T?" -> confident white "T"   (1.22s)
#   7 payoff    focus flashes; cross out "live: limited" -> strictly better      (1.82s)
#
# The spine is one transform: the SAME ambiguous guess "D?/T?" resolves to a
# confident "T" the instant context arrives from the right as well as the left.
# Strict monochrome.
from manim import *
from style import *


class BothWays(Scene):
    def construct(self):
        seed()

        WHITE_ = "#ffffff"
        N = 13
        focus = 6            # mid-strip frame we are trying to name
        ROW_Y = 0.9          # strip sits high; arcs bow up into the headroom

        # =====================================================================
        # CENTER — the strip of recorded frames + the EMG trace
        # =====================================================================
        frames = VGroup(*[
            Square(0.50, stroke_color=INK_GHOST, stroke_width=1.4, fill_opacity=0)
            for _ in range(N)
        ]).arrange(RIGHT, buff=0.16).move_to(np.array([0, ROW_Y, 0]))
        fsq = frames[focus]

        left_x = frames[0].get_left()[0] - 0.05
        right_x = frames[-1].get_right()[0] + 0.05
        sig_y = ROW_Y
        xs = np.linspace(left_x, right_x, 320)
        ys = (0.15 * np.sin(xs * 6.5)
              + 0.07 * np.sin(xs * 16.0 + 1.3)
              + 0.04 * np.sin(xs * 30.0 + 0.4))

        def trace_segment(mask, color=INK_GHOST, width=1.6):
            m = VMobject(stroke_color=color, stroke_width=width)
            m.set_points_as_corners(
                [np.array([x, sig_y + y, 0]) for x, y in zip(xs[mask], ys[mask])])
            return m

        trace = trace_segment(np.ones_like(xs, dtype=bool), color=INK_FAINT)

        split_x = fsq.get_right()[0]
        past_mask = xs <= split_x
        future_mask = xs >= split_x

        # =====================================================================
        # BOTTOM — running takeaway: context-window bar + counter + punchline
        # =====================================================================
        BAR_Y = -3.0
        bar_left = frames[0].get_left()[0]
        bar_right = frames[-1].get_right()[0]
        bar_w = bar_right - bar_left
        bar_h = 0.26
        ghost_bar = Rectangle(
            width=bar_w, height=bar_h,
            stroke_color=INK_GHOST, stroke_width=1.4, fill_opacity=0,
        ).move_to(np.array([(bar_left + bar_right) / 2, BAR_Y, 0]))
        seps = VGroup(*[
            Line(np.array([bar_left + bar_w * i / N, BAR_Y - bar_h / 2, 0]),
                 np.array([bar_left + bar_w * i / N, BAR_Y + bar_h / 2, 0]),
                 stroke_color=INK_GHOST, stroke_width=1.0)
            for i in range(1, N)
        ])

        fill_t = ValueTracker(0.0)
        fill_bar = Rectangle(
            width=0.001, height=bar_h,
            stroke_width=0, fill_color=INK, fill_opacity=0.32,
        ).move_to(np.array([bar_left, BAR_Y, 0]), aligned_edge=LEFT)

        def update_fill(m):
            frac = fill_t.get_value() / N
            w = max(bar_w * frac, 0.001)
            new = Rectangle(width=w, height=bar_h, stroke_width=0,
                            fill_color=INK, fill_opacity=0.32)
            new.move_to(np.array([bar_left, BAR_Y, 0]), aligned_edge=LEFT)
            m.become(new)
        fill_bar.add_updater(update_fill)

        # live "frames in view: N — ..." counter, LaTeX-free
        count_suffix = ValueTracker(0.0)  # 0=blank,1=past only,2=past+future

        def count_text():
            n = int(round(fill_t.get_value()))
            if count_suffix.get_value() < 0.5:
                tail = ""
            elif count_suffix.get_value() < 1.5:
                tail = "  —  past only"
            else:
                tail = "  —  past + future"
            return f"in view: {n}{tail}"
        counter_lbl = mono(count_text(), 18, INK_DIM)
        counter_lbl.next_to(ghost_bar, UP, buff=0.18).align_to(ghost_bar, RIGHT)
        counter_lbl.add_updater(
            lambda m: m.become(mono(count_text(), 18, INK_DIM)
                               .next_to(ghost_bar, UP, buff=0.18)
                               .align_to(ghost_bar, RIGHT)))

        # =====================================================================
        # helpers — arrows that bow UP into the headroom carrying pulse-dots
        # =====================================================================
        APEX_Y = 2.05

        def arrow_from(i):
            src = frames[i]
            start = src.get_top() + UP * 0.05
            end = fsq.get_top() + UP * 0.05
            dist = abs(i - focus)
            apex_h = ROW_Y + 0.55 + (APEX_Y - (ROW_Y + 0.55)) * (dist / focus)
            apex_x = (start[0] + end[0]) / 2.0
            apex = np.array([apex_x, apex_h, 0])
            curve = VMobject(stroke_color=INK, stroke_width=2.0)
            curve.set_points_smoothly([start, apex, end])
            tangent = end - curve.points[-4]
            ang = np.arctan2(tangent[1], tangent[0])
            tip = (Triangle(fill_color=INK, fill_opacity=1.0, stroke_width=0)
                   .scale(0.07))
            tip.rotate(ang - PI / 2)
            tip.move_to(end)
            arrow = VGroup(curve, tip)
            arrow.path = curve
            return arrow

        # =====================================================================
        # BEAT 1 — POSE (~1.87s): one snapshot, sound is a toss-up
        # =====================================================================
        self.next_section("pose")
        self.play(LaggedStartMap(Create, frames, lag_ratio=0.05, run_time=0.6))
        self.play(Create(trace), run_time=0.35)

        # everything dim — only the focus frame will be bright
        frames.set_stroke(opacity=0.30)
        trace.set_stroke(opacity=0.22)

        self.play(
            fsq.animate.set_stroke(color=INK, opacity=1.0, width=2.8)
               .set_fill(INK, opacity=0.10),
            run_time=0.4,
        )
        glow_ring = VGroup(*[
            Square(0.50, stroke_color=INK, stroke_width=5 + 3 * k,
                   stroke_opacity=0.05, fill_opacity=0).move_to(fsq)
            for k in range(3)
        ])
        self.add(glow_ring)
        qmark = serif("?", 30, INK).move_to(fsq)
        self.play(FadeIn(qmark, scale=0.6), run_time=0.32)

        needle = DashedLine(
            fsq.get_bottom() + DOWN * 0.02,
            np.array([fsq.get_center()[0], BAR_Y + bar_h / 2 + 0.05, 0]),
            stroke_color=INK_FAINT, stroke_width=1.4, dash_length=0.07,
        )
        now_tag = mono("now", 15, INK_FAINT).next_to(needle, LEFT, buff=0.10).shift(UP * 0.1)
        self.play(Create(needle), FadeIn(now_tag), run_time=0.4)
        self.wait(0.15)

        # =====================================================================
        # BEAT 2 — CANDIDATES (~1.01s): on its own, the reader can't tell
        # =====================================================================
        self.next_section("candidates")
        guess = VGroup(
            mono("D?", 24, INK_DIM),
            mono("T?", 24, INK_DIM),
        ).arrange(RIGHT, buff=0.42)
        guess.move_to(np.array([fsq.get_center()[0], ROW_Y - 1.15, 0]))
        self.play(FadeOut(qmark, scale=0.6), FadeIn(guess),
                  FadeOut(needle), FadeOut(now_tag), run_time=0.4)
        # flicker — neither candidate wins
        self.play(
            guess[0].animate.set_opacity(0.95), guess[1].animate.set_opacity(0.4),
            rate_func=there_and_back, run_time=0.55,
        )

        # =====================================================================
        # BEAT 3 — CAUSAL (~3.44s): peek backward only — past context arrives
        # =====================================================================
        self.next_section("causal")
        # build the bottom takeaway scaffolding now (the context window bar)
        self.add(fill_bar, counter_lbl)
        self.play(
            Create(ghost_bar), LaggedStartMap(Create, seps, lag_ratio=0.03),
            run_time=0.5,
        )

        # dim the FUTURE frames + future trace — visibly unavailable
        future_frames = VGroup(*[frames[i] for i in range(focus + 1, N)])
        future_trace = trace_segment(future_mask, color=INK_FAINT)
        self.add(future_trace)
        self.remove(trace)
        past_trace = trace_segment(past_mask, color=INK_FAINT)
        past_trace.set_stroke(opacity=0.22)
        self.add(past_trace)
        self.play(
            future_frames.animate.set_stroke(opacity=0.12),
            future_trace.animate.set_stroke(opacity=0.07),
            run_time=0.5,
        )

        # LIVE ● tag streaming off the strip's left
        live_dot = Dot(radius=0.055, color=WHITE_)
        live_dot.move_to(np.array([bar_left - 0.55, ROW_Y + 0.45, 0]))
        live_tag = mono("LIVE", 15, INK_DIM).next_to(live_dot, RIGHT, buff=0.12)
        self.play(FadeIn(live_dot), FadeIn(live_tag), run_time=0.35)

        # 6 past arrows; bottom bar fills 0->6 as they land
        past_arrows = VGroup(*[arrow_from(i) for i in range(focus)])
        count_suffix.set_value(1.0)
        dots = VGroup(*[Dot(radius=0.05, color=WHITE_).move_to(a.path.get_start())
                        for a in past_arrows])
        self.add(dots)
        self.play(
            LaggedStart(*[Create(a) for a in past_arrows], lag_ratio=0.16),
            LaggedStart(*[MoveAlongPath(d, a.path)
                          for d, a in zip(dots, past_arrows)], lag_ratio=0.16),
            fill_t.animate.set_value(6),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(dots)
        self.wait(0.2)

        # =====================================================================
        # BEAT 4 — HEDGED (~0.84s): sharper, but still hedged
        # =====================================================================
        self.next_section("hedged")
        self.play(
            guess[1].animate.set_opacity(0.95).scale(1.08),
            guess[0].animate.set_opacity(0.4),
            run_time=0.35,
        )
        punch_live = mono("live: limited", 19, INK_DIM)
        punch_live.move_to(np.array([0, BAR_Y - 0.62, 0]))
        self.play(FadeIn(punch_live, shift=UP * 0.1), run_time=0.35)

        # =====================================================================
        # BEAT 5 — FINISHED (~1.76s): a finished recording — future exists too
        # =====================================================================
        self.next_section("finished")
        causal_tag = mono("LIVE  ·  past only", 22, INK_DIM)
        causal_tag.move_to(np.array([bar_left + 0.1, -1.45, 0]), aligned_edge=LEFT)
        self.add(causal_tag)
        bidir_label = mono("BIDIRECTIONAL  ·  before AND after", 22, INK)
        bidir_label.move_to(causal_tag, aligned_edge=LEFT)
        self.play(
            ReplacementTransform(causal_tag, bidir_label),
            future_frames.animate.set_stroke(opacity=0.30),
            future_trace.animate.set_stroke(opacity=0.22),
            FadeOut(live_dot), FadeOut(live_tag),
            run_time=1.0,
        )
        self.wait(0.5)

        # =====================================================================
        # BEAT 6 — COLLAPSE (~1.22s): look both ways -> clear T
        # =====================================================================
        self.next_section("collapse")
        future_arrows = VGroup(*[arrow_from(i) for i in range(focus + 1, N)])
        count_suffix.set_value(2.0)
        dots2 = VGroup(*[Dot(radius=0.05, color=WHITE_).move_to(a.path.get_start())
                         for a in future_arrows])
        self.add(dots2)
        self.play(
            LaggedStart(*[Create(a) for a in future_arrows], lag_ratio=0.12),
            LaggedStart(*[MoveAlongPath(d, a.path)
                          for d, a in zip(dots2, future_arrows)], lag_ratio=0.12),
            fill_t.animate.set_value(13),
            run_time=0.8,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(dots2)

        # THE PAYOFF: ambiguity collapses to one confident white "T"
        answer = serif("T", 34, INK).move_to(guess.get_center())
        self.play(ReplacementTransform(guess, answer), run_time=0.3)
        self.play(answer.animate.set_color(WHITE_).scale(1.15), run_time=0.12)

        # =====================================================================
        # BEAT 7 — PAYOFF (~1.82s): before and after is what pulls error down
        # =====================================================================
        self.next_section("payoff")
        self.play(
            Indicate(fsq, color=INK, scale_factor=1.12),
            Flash(fsq, color=INK, line_length=0.16, num_lines=12, flash_radius=0.5),
            run_time=0.45,
        )
        fsq.set_stroke(color=INK, width=2.8).set_fill(INK, opacity=0.10)

        punch_better = mono("finished recording: strictly better", 19, INK)
        punch_better.move_to(np.array([0, BAR_Y - 0.62, 0]))
        cross = Line(punch_live.get_left(), punch_live.get_right(),
                     stroke_color=INK_FAINT, stroke_width=2.0)
        self.play(Create(cross), run_time=0.3)
        self.play(
            FadeOut(punch_live, shift=DOWN * 0.1), FadeOut(cross),
            Write(punch_better), run_time=0.5,
        )
        # peak-white glow sweep across the now-full bar
        sweep = Dot(radius=0.07, color=WHITE_).move_to(np.array([bar_left, BAR_Y, 0]))
        self.add(sweep)
        self.play(
            sweep.animate.move_to(np.array([bar_right, BAR_Y, 0])),
            run_time=0.55, rate_func=linear,
        )
        self.remove(sweep)

        # freeze readouts so the poster is clean & deterministic
        fill_t.set_value(13)
        counter_lbl.clear_updaters()
        fill_bar.clear_updaters()
        counter_lbl.become(mono("in view: 13  —  past + future", 18, INK_DIM)
                           .next_to(ghost_bar, UP, buff=0.18)
                           .align_to(ghost_bar, RIGHT))
        glow_ans = glow(answer.copy().set_color(WHITE_))
        self.add(glow_ans)
        self.play(Indicate(answer, color=WHITE_, scale_factor=1.06),
                  glow_ans.animate.set_opacity(0.0), run_time=0.35)
        self.remove(glow_ans)
        self.wait(0.25)
