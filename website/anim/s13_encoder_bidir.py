# S13 — Looking both ways (causal vs bidirectional)
# Goal: to name a sound at one instant, it helps to see frames *before AND after*.
#
# Composition fills the whole canvas in three horizontal zones:
#   TOP    (y ~ +3.0): a quiet CONTEXT strip — a recap tag linking S12/S14 (we
#          already make a per-frame sound guess) + a "finished recording ▸" axis,
#          framing the strip below as a fixed, fully-recorded timeline.
#   CENTER (y ~ +0.9): the star — a 13-frame strip with an EMG trace threading it,
#          a brightened mid-strip focus frame, context flowing in as CurvedArrows
#          that bow up into the headroom carrying white pulse-dots, a vertical
#          "now" needle, and the per-frame guess that TRANSFORMS "D?/T?" -> "T".
#   BOTTOM (y ~ -3.0): a RUNNING TAKEAWAY — a "context window" bar that fills as
#          arrows land, a live "frames in view: N" counter, and a one-line
#          punchline that builds: "live: limited" -> "finished recording:
#          strictly better".
#
# The spine is one transform: the SAME ambiguous guess "D?/T?" resolves to a
# confident "T" the instant context arrives from the right as well as the left.
# Causal = half a window of context (6 frames, past only); bidirectional = full
# window (13 frames, past + future). Strict monochrome.
from manim import *
from emg_style import *


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
            Square(0.50, stroke_color=INK_FAINT, stroke_width=1.4, fill_opacity=0)
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

        trace = trace_segment(np.ones_like(xs, dtype=bool))

        # split the trace into past / future stretches around the focus frame edge
        split_x = fsq.get_right()[0]
        past_mask = xs <= split_x
        future_mask = xs >= split_x

        # =====================================================================
        # TOP — quiet CONTEXT strip (stays put the whole clip)
        # =====================================================================
        recap = mono("the reader  ·  per-frame sounds", 19, INK_FAINT)
        recap.move_to(np.array([-7.1, 3.0, 0]), aligned_edge=LEFT).shift(RIGHT * 0.55)

        axis_label = mono("a finished recording  ▸", 19, INK_DIM)
        axis_label.move_to(np.array([7.1, 3.05, 0]), aligned_edge=RIGHT).shift(LEFT * 0.55)
        axis_tick = Line(
            np.array([axis_label.get_left()[0] - 0.05, 2.78, 0]),
            np.array([7.1 - 0.55, 2.78, 0]),
            stroke_color=INK_GHOST, stroke_width=1.4,
        )
        # little ticks along the recording axis to read it as a timeline
        ticks = VGroup(*[
            Line(np.array([x, 2.78, 0]), np.array([x, 2.86, 0]),
                 stroke_color=INK_GHOST, stroke_width=1.2)
            for x in np.linspace(axis_tick.get_left()[0] + 0.15,
                                 axis_tick.get_right()[0] - 0.05, 7)
        ])

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
        # 13 cell separators so the bar reads as a per-frame window
        seps = VGroup(*[
            Line(np.array([bar_left + bar_w * i / N, BAR_Y - bar_h / 2, 0]),
                 np.array([bar_left + bar_w * i / N, BAR_Y + bar_h / 2, 0]),
                 stroke_color=INK_GHOST, stroke_width=1.0)
            for i in range(1, N)
        ])

        # fill driven by a ValueTracker (number of frames currently in view)
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

        bar_caption = mono("context window", 16, INK_FAINT).next_to(
            ghost_bar, UP, buff=0.16).align_to(ghost_bar, LEFT)

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
            return f"frames in view: {n}{tail}"
        counter_lbl = mono(count_text(), 18, INK_DIM)
        counter_lbl.next_to(ghost_bar, UP, buff=0.16).align_to(ghost_bar, RIGHT)
        counter_lbl.add_updater(
            lambda m: m.become(mono(count_text(), 18, INK_DIM)
                               .next_to(ghost_bar, UP, buff=0.16)
                               .align_to(ghost_bar, RIGHT)))

        # =====================================================================
        # helpers — arrows that bow UP into the headroom carrying pulse-dots
        # =====================================================================
        TIP_SCALE = 0.62
        APEX_Y = 2.05   # arcs bow up to here (clear of the top strip at y~3.0)

        def arrow_from(i):
            # an arc that bows UP into the headroom: the farther the source frame,
            # the higher it bows, so the fan opens out symmetrically around focus.
            src = frames[i]
            start = src.get_top() + UP * 0.05
            end = fsq.get_top() + UP * 0.05
            dist = abs(i - focus)
            # apex rises with distance (near arcs short & low, far arcs tall)
            apex_h = ROW_Y + 0.55 + (APEX_Y - (ROW_Y + 0.55)) * (dist / focus)
            apex_x = (start[0] + end[0]) / 2.0
            apex = np.array([apex_x, apex_h, 0])
            curve = VMobject(stroke_color=INK, stroke_width=2.0)
            # smooth bezier through the apex, bowing up into the headroom
            curve.set_points_smoothly([start, apex, end])
            # a small filled triangle tip aimed along the curve's final tangent
            tangent = end - curve.points[-4]
            ang = np.arctan2(tangent[1], tangent[0])
            tip = (Triangle(fill_color=INK, fill_opacity=1.0, stroke_width=0)
                   .scale(0.07))
            tip.rotate(ang - PI / 2)  # Triangle points up by default
            tip.move_to(end)
            arrow = VGroup(curve, tip)
            arrow.path = curve  # remember the path for MoveAlongPath
            return arrow

        # =====================================================================
        # BEAT 0 — POSE (build all three zones; name the lit frame)
        # =====================================================================
        self.next_section("pose")
        # top context strip first
        self.play(
            FadeIn(recap, shift=RIGHT * 0.12),
            FadeIn(axis_label, shift=LEFT * 0.12),
            run_time=0.5,
        )
        self.play(Create(axis_tick), LaggedStartMap(Create, ticks, lag_ratio=0.04),
                  run_time=0.45)

        # the strip + trace
        self.play(LaggedStartMap(Create, frames, lag_ratio=0.05, run_time=0.85))
        self.play(Create(trace), run_time=0.5)

        # brighten focus frame + glow + a serif "?"
        self.play(
            fsq.animate.set_stroke(color=INK, width=2.8).set_fill(INK, opacity=0.10),
            run_time=0.45,
        )
        glow_ring = VGroup(*[
            Square(0.50, stroke_color=INK, stroke_width=5 + 3 * k,
                   stroke_opacity=0.05, fill_opacity=0).move_to(fsq)
            for k in range(3)
        ])
        self.add(glow_ring)
        qmark = serif("?", 30, INK).move_to(fsq)
        self.play(FadeIn(qmark, scale=0.6), run_time=0.35)

        # vertical "now" needle dropping from the focus frame down through trace
        needle = DashedLine(
            fsq.get_bottom() + DOWN * 0.02,
            np.array([fsq.get_center()[0], BAR_Y + bar_h / 2 + 0.05, 0]),
            stroke_color=INK_FAINT, stroke_width=1.4, dash_length=0.07,
        )
        now_tag = mono("now", 15, INK_FAINT).next_to(needle, LEFT, buff=0.10).shift(UP * 0.1)
        self.play(Create(needle), FadeIn(now_tag), run_time=0.45)

        # bottom takeaway scaffolding (empty ghost bar + counter at 0)
        self.add(fill_bar, counter_lbl)
        self.play(
            Create(ghost_bar), LaggedStartMap(Create, seps, lag_ratio=0.03),
            FadeIn(bar_caption), run_time=0.55,
        )

        # =====================================================================
        # BEAT 1 — CAUSAL: context only from the left (the past)
        # =====================================================================
        self.next_section("causal")
        causal_label = mono("CAUSAL  ·  past only", 24, INK)
        causal_label.move_to(np.array([bar_left + 0.1, -1.45, 0]), aligned_edge=LEFT)
        self.play(FadeIn(causal_label, shift=UP * 0.12), run_time=0.4)

        # dim the FUTURE frames + the future trace stretch — visibly unavailable
        future_frames = VGroup(*[frames[i] for i in range(focus + 1, N)])
        future_trace = trace_segment(future_mask)
        self.add(future_trace)
        self.remove(trace)
        past_trace = trace_segment(past_mask)
        self.add(past_trace)
        self.play(
            future_frames.animate.set_stroke(opacity=0.20),
            future_trace.animate.set_stroke(opacity=0.10),
            run_time=0.5,
        )

        # a LIVE ● tag streaming off the strip's left
        live_dot = Dot(radius=0.055, color=WHITE_)
        live_dot.move_to(np.array([bar_left - 0.55, ROW_Y + 0.45, 0]))
        live_tag = mono("LIVE", 15, INK_DIM).next_to(live_dot, RIGHT, buff=0.12)
        self.play(FadeIn(live_dot), FadeIn(live_tag), run_time=0.3)

        # draw the 6 past arrows; sync the bottom bar filling 0->6 as they land
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
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(dots)

        # the guess is AMBIGUOUS — two candidates flickering, directly under focus
        guess = VGroup(
            mono("D?", 24, INK_DIM),
            mono("T?", 24, INK_DIM),
        ).arrange(RIGHT, buff=0.42)
        guess.move_to(np.array([fsq.get_center()[0], ROW_Y - 1.15, 0]))
        self.play(FadeOut(qmark, scale=0.6), FadeIn(guess), run_time=0.4)
        self.play(
            guess[0].animate.set_opacity(0.35), guess[1].animate.set_opacity(0.95),
            rate_func=there_and_back, run_time=0.65,
        )

        # punchline begins: "live: limited"
        punch_live = mono("live: limited", 19, INK_DIM)
        punch_live.move_to(np.array([0, BAR_Y - 0.62, 0]))
        self.play(FadeIn(punch_live, shift=UP * 0.1), run_time=0.4)
        self.wait(0.2)

        # =====================================================================
        # BEAT 2 — BIDIRECTIONAL — THE TRANSFORM
        # =====================================================================
        self.next_section("bidirectional")
        bidir_label = mono("BIDIRECTIONAL  ·  before AND after", 24, INK)
        bidir_label.move_to(causal_label, aligned_edge=LEFT)
        # the future re-lights; label transforms; drop the LIVE tag
        self.play(
            ReplacementTransform(causal_label, bidir_label),
            future_frames.animate.set_stroke(opacity=1.0),
            future_trace.animate.set_stroke(opacity=1.0),
            FadeOut(live_dot), FadeOut(live_tag),
            run_time=0.6,
        )

        # 6 future arrows arc up-RIGHT into focus; bar fills right-half 6->13
        future_arrows = VGroup(*[arrow_from(i) for i in range(focus + 1, N)])
        count_suffix.set_value(2.0)
        dots2 = VGroup(*[Dot(radius=0.05, color=WHITE_).move_to(a.path.get_start())
                         for a in future_arrows])
        self.add(dots2)
        self.play(
            LaggedStart(*[Create(a) for a in future_arrows], lag_ratio=0.14),
            LaggedStart(*[MoveAlongPath(d, a.path)
                          for d, a in zip(dots2, future_arrows)], lag_ratio=0.14),
            fill_t.animate.set_value(13),
            run_time=1.1,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(dots2)

        # THE PAYOFF: ambiguity collapses to one confident "T"
        answer = mono("T", 28, INK).move_to(guess.get_center())
        self.play(ReplacementTransform(guess, answer), run_time=0.45)
        self.play(answer.animate.set_color(WHITE_).scale(1.15), run_time=0.3)
        self.wait(0.15)

        # =====================================================================
        # BEAT 3 — NAME IT (fed from both sides; punchline lands)
        # =====================================================================
        self.next_section("name_it")
        self.play(
            Indicate(fsq, color=INK, scale_factor=1.12),
            Flash(fsq, color=INK, line_length=0.16, num_lines=12, flash_radius=0.5),
            run_time=0.55,
        )
        fsq.set_stroke(color=INK, width=2.8).set_fill(INK, opacity=0.10)

        # punchline: live:limited -> finished recording: strictly better
        punch_better = mono("finished recording: strictly better", 19, INK)
        punch_better.move_to(np.array([0, BAR_Y - 0.62, 0]))
        cross = Line(punch_live.get_left(), punch_live.get_right(),
                     stroke_color=INK_FAINT, stroke_width=2.0)
        self.play(Create(cross), run_time=0.3)
        self.play(
            FadeOut(punch_live, shift=DOWN * 0.1), FadeOut(cross),
            Write(punch_better), run_time=0.55,
        )
        # make "strictly better" land in peak white via a sweeping glow dot on bar
        sweep = Dot(radius=0.07, color=WHITE_).move_to(
            np.array([bar_left, BAR_Y, 0]))
        self.add(sweep)
        self.play(
            sweep.animate.move_to(np.array([bar_right, BAR_Y, 0])),
            run_time=0.6, rate_func=linear,
        )
        self.remove(sweep)

        # =====================================================================
        # BEAT 4 — SETTLE / POSTER  (balanced, symmetric, the answer reads)
        # =====================================================================
        self.next_section("poster")
        # freeze the live readouts so the poster is clean & deterministic
        fill_t.set_value(13)
        counter_lbl.clear_updaters()
        fill_bar.clear_updaters()
        counter_lbl.become(mono("frames in view: 13  —  past + future", 18, INK_DIM)
                           .next_to(ghost_bar, UP, buff=0.16)
                           .align_to(ghost_bar, RIGHT))
        # final tiny breath: glow the answer once more so the poster reads
        self.play(Indicate(answer, color=WHITE_, scale_factor=1.06), run_time=0.4)
        self.wait(0.6)
