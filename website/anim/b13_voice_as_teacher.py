# website/anim/b13_voice_as_teacher.py  —  B13 "The recording in the room"
#
# THE IDEA: who is the teacher in distillation?  The real VOICE.  While the
# data was recorded, a microphone ran beside the EMG sensors — just for this.
# A big audio model (WavLM) that already heard an ocean of speech turns that
# voice into a rich middle-layer picture (layer 9, "the tap").  The muscle
# model's third output is trained to COPY that picture.  At real use, the
# microphone is gone — only the lesson stays.
#
# Metaphor: a tutor who attends only the REHEARSALS, never the live show.
#
# Three persistent zones (pose -> build -> transform -> use-time -> name):
#   TOP   (y ~ +2.3..+3.6)  the two time-aligned LANES, same word ticks, a
#                            "training only" stamp.
#   CENTER(y ~ -2.0..+2.0)  the tall LAYER STACK rising from raw squiggle to a
#                            clean structured field; layer 9 highlighted as the
#                            tap; a thin stream pours down into the muscle lane's
#                            THIRD OUTPUT, which reshapes to match (distance bar
#                            shrinks).  Then a "now in use" divider: the mic +
#                            top lane fade, the microphone is struck with a Cross.
#   BOTTOM(y ~ -3.6..-2.7)  the resolved punchline.
from manim import *
from emg_style import *
import numpy as np

WHITE = "#ffffff"

X_L, X_R = -6.6, 6.6


def squiggle(x0, x1, y, n=120, amp=0.18, seed_n=1, op=0.9, sw=1.8, c=INK):
    """A clean-ish audio waveform (smooth, low jitter)."""
    rng = np.random.default_rng(seed_n)
    xs = np.linspace(x0, x1, n)
    env = 0.4 + 0.6 * np.abs(np.sin(np.linspace(0, 3.2, n)))
    base = np.sin(np.linspace(0, 26, n)) + 0.5 * np.sin(np.linspace(0, 61, n))
    ys = y + amp * env * base / 1.5
    pts = [np.array([xs[i], ys[i], 0]) for i in range(n)]
    return VMobject(stroke_color=c, stroke_width=sw, stroke_opacity=op).set_points_smoothly(pts)


def speckle_row(x0, x1, y, n=90, amp=0.16, seed_n=2, op=0.8, c=INK_DIM):
    """A noisy EMG row — short jittery vertical strokes (no smooth structure)."""
    rng = np.random.default_rng(seed_n)
    xs = np.linspace(x0, x1, n)
    g = VGroup()
    for xv in xs:
        h = amp * (0.25 + rng.random())
        g.add(Line([xv, y - h, 0], [xv, y + h, 0], stroke_color=c,
                   stroke_width=1.2, stroke_opacity=op))
    return g


def field_grid(cx, cy, w=2.2, h=1.7, rows=7, cols=11, seed_n=4, op=0.95):
    """A clean STRUCTURED field — a small heatmap with smooth diagonal banding
    (what a deep audio layer's representation 'looks like')."""
    rng = np.random.default_rng(seed_n)
    cw, ch = w / cols, h / rows
    g = VGroup()
    for i in range(rows):
        for j in range(cols):
            v = np.exp(-((i - (rows - 1) * (j / (cols - 1))) ** 2) / 3.5)
            v = max(0.06, min(1.0, v * op + 0.03 * rng.random()))
            sq = Square(min(cw, ch) * 0.94, stroke_width=0, fill_color=INK,
                        fill_opacity=float(v))
            sq.move_to([cx + (j - (cols - 1) / 2) * cw,
                        cy + ((rows - 1) / 2 - i) * ch, 0])
            g.add(sq)
    return g


class VoiceAsTeacher(Scene):
    def construct(self):
        seed()

        # =================================================================
        # B0 — POSE: two time-aligned lanes + "training only" stamp.
        # =================================================================
        self.next_section("pose")

        lane_l, lane_r = -4.7, 4.7
        voice_y = 3.05
        mus_y = 2.05

        # word ticks shared by BOTH lanes — same sentence, same time axis.
        n_ticks = 6
        tick_xs = np.linspace(lane_l + 0.4, lane_r - 0.4, n_ticks)
        v_ticks = VGroup(*[Line([x, voice_y - 0.34, 0], [x, mus_y + 0.34, 0],
                                stroke_color=INK_GHOST, stroke_width=1.0)
                           for x in tick_xs])

        # TOP lane: clean voice waveform + a mic glyph + label.
        wave = squiggle(lane_l + 0.15, lane_r - 0.15, voice_y, op=0.92)
        mic_body = RoundedRectangle(width=0.18, height=0.34, corner_radius=0.09,
                                    stroke_color=INK, stroke_width=2.0,
                                    fill_color=BG, fill_opacity=1.0)
        mic_stem = Line(ORIGIN, DOWN * 0.16, stroke_color=INK, stroke_width=2.0)
        mic_base = Line(LEFT * 0.1, RIGHT * 0.1, stroke_color=INK, stroke_width=2.0)
        mic = VGroup(mic_body, mic_stem, mic_base)
        mic_stem.next_to(mic_body, DOWN, buff=0.0)
        mic_base.next_to(mic_stem, DOWN, buff=0.0)
        mic.scale(0.9).move_to([lane_l - 0.55, voice_y, 0])
        v_lab = mono("voice (mic)", 16, INK_DIM).next_to(wave, RIGHT, buff=0.22).set_y(voice_y)

        # BOTTOM lane: speckled EMG + label.
        emg = speckle_row(lane_l + 0.15, lane_r - 0.15, mus_y)
        m_lab = mono("muscles (EMG)", 16, INK_FAINT).next_to(emg, RIGHT, buff=0.22).set_y(mus_y)

        # "training only" stamp top-right, boxed.
        stamp_t = mono("TRAINING ONLY", 14, INK_DIM, w=BOLD)
        stamp = VGroup(stamp_t, SurroundingRectangle(stamp_t, color=INK_FAINT,
                                                     stroke_width=1.2, buff=0.12))
        stamp.move_to([X_R - 1.0, 3.6, 0])

        ctx = mono("one sentence, recorded two ways at once", 17, INK_FAINT)
        ctx.move_to([0, 1.45, 0])

        self.play(LaggedStartMap(Create, v_ticks, lag_ratio=0.06, run_time=0.5))
        self.play(Create(wave), FadeIn(mic, shift=RIGHT * 0.1),
                  FadeIn(v_lab), run_time=0.6)
        self.play(LaggedStartMap(FadeIn, emg, lag_ratio=0.01, run_time=0.5),
                  FadeIn(m_lab), run_time=0.5)
        self.play(FadeIn(stamp, shift=DOWN * 0.1), FadeIn(ctx, shift=UP * 0.08),
                  run_time=0.45)

        top_lane = VGroup(wave, mic, v_lab)

        # =================================================================
        # B1 — BUILD: the voice pours up through a tall LAYER STACK.
        #      raw squiggle at the bottom -> clean structured field by layer 9.
        # =================================================================
        self.next_section("stack")

        self.play(FadeOut(ctx, shift=DOWN * 0.1), run_time=0.25)

        # the layer stack lives center-LEFT; plates stacked bottom (raw) -> top.
        stack_x = -3.7
        n_layers = 6
        plate_w = 2.55
        plate_h = 0.30
        plate_gap = 0.20
        stack_bottom = -1.55
        plates = VGroup()
        for k in range(n_layers):
            y = stack_bottom + k * (plate_h + plate_gap)
            op = 0.10 + 0.10 * k / (n_layers - 1)
            pl = RoundedRectangle(width=plate_w, height=plate_h, corner_radius=0.05,
                                  stroke_color=INK_FAINT, stroke_width=1.2,
                                  fill_color=INK, fill_opacity=op)
            pl.move_to([stack_x, y, 0])
            plates.add(pl)
        stack_lab = mono("audio model", 16, INK_DIM).next_to(plates, UP, buff=0.18)
        stack_sub = mono("heard an ocean of speech", 13, INK_GHOST).next_to(
            stack_lab, UP, buff=0.08)

        # the raw input under the stack: a tiny squiggle.
        raw_in = squiggle(stack_x - 0.9, stack_x + 0.9, stack_bottom - 0.55,
                          n=60, amp=0.10, op=0.7, sw=1.4, c=INK_DIM)
        raw_lab = mono("raw squiggle", 12, INK_GHOST).next_to(raw_in, DOWN, buff=0.10)

        # a feed line from the TOP voice lane down into the stack input.
        feed = VGroup(
            Line([lane_l - 0.55, voice_y - 0.42, 0], [lane_l - 0.55, stack_bottom - 0.55, 0],
                 stroke_color=INK_GHOST, stroke_width=1.4),
            Line([lane_l - 0.55, stack_bottom - 0.55, 0],
                 [stack_x - 0.95, stack_bottom - 0.55, 0],
                 stroke_color=INK_GHOST, stroke_width=1.4),
        )

        self.play(Create(feed), FadeIn(raw_in), FadeIn(raw_lab), run_time=0.45)
        self.play(LaggedStartMap(FadeIn, plates, lag_ratio=0.12,
                                 shift=UP * 0.06, run_time=0.7),
                  FadeIn(stack_lab), FadeIn(stack_sub), run_time=0.7)

        # a pulse rises through the stack: raw -> structured.
        pulse = Rectangle(width=plate_w, height=0.10, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.55).move_to(
            [stack_x, stack_bottom - 0.3, 0])
        self.add(pulse)
        self.play(pulse.animate.move_to([stack_x, plates[-1].get_y() + 0.2, 0]),
                  run_time=0.7, rate_func=linear)
        self.remove(pulse)

        # LAYER 9 = "the tap": highlight a middle plate and grow its structured
        # field to the RIGHT of the stack.
        tap_idx = 3
        tap_plate = plates[tap_idx]
        l9_lab = mono("layer 9", 14, INK).next_to(tap_plate, LEFT, buff=0.20)
        tap_tag = mono("the tap", 13, INK_DIM).next_to(tap_plate, LEFT, buff=0.20)
        tap_tag.next_to(l9_lab, DOWN, buff=0.06).align_to(l9_lab, RIGHT)

        self.play(tap_plate.animate.set_stroke(INK, width=2.4).set_fill(INK, 0.30),
                  FadeIn(l9_lab, shift=RIGHT * 0.06),
                  FadeIn(tap_tag, shift=RIGHT * 0.06), run_time=0.5)

        # the rich structured field that layer 9 holds (center-right of stack).
        field_cx = -0.55
        field_cy = tap_plate.get_y() + 0.0
        field = field_grid(field_cx, field_cy, w=2.3, h=1.5, rows=7, cols=11)
        field_box = SurroundingRectangle(field, color=INK, stroke_width=1.6, buff=0.10)
        field_cap = mono("a rich, structured picture", 14, INK_DIM).next_to(
            field_box, UP, buff=0.14)
        tap_line = Line(tap_plate.get_right(), field_box.get_left(),
                        stroke_color=INK, stroke_width=1.6)

        self.play(Create(tap_line),
                  LaggedStartMap(FadeIn, field, lag_ratio=0.01, run_time=0.6),
                  Create(field_box), FadeIn(field_cap), run_time=0.7)

        # =================================================================
        # B2 — TRANSFORM: a thin stream lifts off layer 9 / the field and pours
        #      down into the MUSCLE model's THIRD OUTPUT, which reshapes to match.
        # =================================================================
        self.next_section("distil")

        # the muscle model's three heads, center-RIGHT lower area. Third = target.
        heads_x = 3.7
        head_ys = [-0.55, -1.35, -2.15]
        head_names = ["100 units", "40 phonemes", "1024-num projection"]
        heads = VGroup()
        head_boxes = []
        for i, (hy, hn) in enumerate(zip(head_ys, head_names)):
            active = (i == 2)
            box = RoundedRectangle(width=2.7, height=0.52, corner_radius=0.07,
                                   stroke_color=INK if active else INK_GHOST,
                                   stroke_width=1.8 if active else 1.2,
                                   fill_color=INK,
                                   fill_opacity=0.10 if active else 0.0)
            box.move_to([heads_x, hy, 0])
            lab = mono(hn, 14, INK if active else INK_FAINT).move_to(box)
            heads.add(VGroup(box, lab))
            head_boxes.append(box)
        muscle_lab = mono("muscle model", 15, INK_DIM).next_to(heads, UP, buff=0.18)

        self.play(LaggedStartMap(FadeIn, heads, lag_ratio=0.12, run_time=0.55),
                  FadeIn(muscle_lab), run_time=0.55)

        third = head_boxes[2]
        third_tag = mono("third output", 12, INK_FAINT).next_to(third, DOWN, buff=0.12)
        self.play(FadeIn(third_tag, shift=UP * 0.05), run_time=0.3)

        # the distillation STREAM: from the field, down and over into the third head.
        stream = VGroup(
            Line(field_box.get_bottom(), [field_cx, third.get_y(), 0],
                 stroke_color=INK, stroke_width=2.2),
            Line([field_cx, third.get_y(), 0], third.get_left(),
                 stroke_color=INK, stroke_width=2.2),
        )
        copy_lab = mono("copy the picture", 13, INK_DIM)
        copy_lab.next_to(stream[1], DOWN, buff=0.10).set_x((field_cx + heads_x) / 2)

        self.play(LaggedStartMap(Create, stream, lag_ratio=0.4, run_time=0.55),
                  FadeIn(copy_lab), run_time=0.55)

        # a #fff droplet travels the stream into the third output (the teaching).
        drop = Dot(field_box.get_bottom(), radius=0.06, color=WHITE)
        self.add(drop)
        self.play(MoveAlongPath(drop, stream[0]), run_time=0.35, rate_func=linear)
        self.play(MoveAlongPath(drop, stream[1]), run_time=0.4, rate_func=linear)
        self.play(FadeOut(drop, scale=0.3),
                  third.animate.set_fill(INK, 0.22).set_stroke(WHITE, width=2.2),
                  run_time=0.3)

        # DISTANCE BAR shrinks: the third output "reshapes to match" the teacher.
        dist_track = RoundedRectangle(width=3.0, height=0.14, corner_radius=0.05,
                                      stroke_color=INK_GHOST, stroke_width=1.0,
                                      fill_opacity=0).move_to([0, -3.0, 0])
        dist_fill = Rectangle(width=3.0, height=0.14, stroke_width=0,
                              fill_color=INK, fill_opacity=0.7)
        dist_fill.align_to(dist_track, LEFT).set_y(dist_track.get_y())
        dist_lab = mono("distance to teacher", 13, INK_FAINT).next_to(
            dist_track, LEFT, buff=0.24)
        if dist_lab.get_left()[0] < X_L:
            dist_lab.next_to(dist_track, UP, buff=0.10).set_x(dist_track.get_x())

        self.play(Create(dist_track), FadeIn(dist_fill), FadeIn(dist_lab),
                  run_time=0.4)
        self.play(dist_fill.animate.stretch_to_fit_width(3.0 * 0.18).align_to(
                      dist_track, LEFT),
                  third.animate.set_fill(INK, 0.16).set_stroke(INK, width=1.8),
                  run_time=0.7)
        dist_fill.align_to(dist_track, LEFT)

        # =================================================================
        # B3 — USE-TIME: divider "now in use" — mic + top lane fade, mic struck.
        # =================================================================
        self.next_section("usetime")

        divider = DashedLine([0, 1.7, 0], [0, -2.5, 0], dash_length=0.12,
                             stroke_color=INK_GHOST, stroke_width=1.2)
        now_lab = mono("now in use", 14, INK_DIM)
        # park the divider label up top-right, clear of the lanes.
        now_lab.move_to([1.4, 1.62, 0])

        # strike the microphone with a Cross.
        cross = Cross(mic, stroke_color=INK, stroke_width=3.0).scale(1.3)

        self.play(Create(divider), FadeIn(now_lab, shift=DOWN * 0.06), run_time=0.4)
        self.play(Create(cross), run_time=0.35)
        # the top voice lane + ticks + stamp + feed + stack-side teacher fade:
        # at inference there is NO audio.  Only the muscle path remains.
        fade_grp = VGroup(top_lane, cross, mic, v_ticks, stamp,
                          stack_lab, stack_sub, raw_in, raw_lab, feed, plates,
                          l9_lab, tap_tag, tap_line, field, field_box, field_cap,
                          stream, copy_lab, divider, now_lab, m_lab,
                          dist_track, dist_fill, dist_lab)
        self.play(fade_grp.animate.set_opacity(0.12), run_time=0.6)

        # bring the muscle lane + third head forward as the surviving path.
        surv = VGroup(emg, heads, muscle_lab, third_tag)
        self.play(emg.animate.set_opacity(0.95),
                  Indicate(third, scale_factor=1.06, color=INK), run_time=0.5)

        # =================================================================
        # B4 — NAME + poster hold.
        # =================================================================
        self.next_section("name")

        payoff = serif("only the lesson remains", 40, WHITE).move_to([0, 0.55, 0])
        payoff_g = glow(payoff)
        sub = mono("sharpens the sounds — not yet the words", 18, INK_DIM)
        sub.next_to(payoff, DOWN, buff=0.26)

        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  Flash([0, 0.55, 0], color=WHITE, line_length=0.2, num_lines=14,
                        flash_radius=1.5, time_width=0.4), run_time=0.6)
        self.play(FadeIn(sub, shift=UP * 0.08), run_time=0.4)
        self.wait(0.6)
