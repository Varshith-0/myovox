# website/anim/b13_voice_as_teacher.py  —  B13 "The voice as teacher"
#
# THE IDEA: who is the teacher in distillation?  The real VOICE.  While the
# data was recorded, a microphone ran beside the EMG sensors — just for this.
# A big audio model (WavLM) that already heard an ocean of speech turns that
# voice into a rich middle-layer picture (layer 9, "the tap").  The muscle
# model's third output is trained to COPY that picture.  At real use, the
# microphone is gone — only the lesson stays.
#
# Locked 6-beat sheet (one self.next_section per beat, timed to dur_sec):
#   1 puzzle (0.64) empty stage + ghost "?" over top; lone dim EMG lane below.
#   2 trick  (0.60) mic + clean voice wave fade in, time-aligned by word ticks;
#                   TRAINING ONLY stamp.
#   3 model  (5.81) voice feeds the tall layer stack; pulse rises; layer 9 lights
#                   as "the tap"; the structured field grows to its right.
#   4 copy   (1.29) muscle model's three heads appear; bright stream + droplet
#                   pour from the field into the third output; distance bar shrinks.
#   5 caveat (2.17) dim everything; two chips — sounds (PER) brightens/ticks down,
#                   words (WER) stays grey/static.
#   6 use    (1.64) "now in use" divider; mic/voice/stack/field fade to near-zero;
#                   EMG + shaped third output stay lit; serif "only the lesson remains".
from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"

X_L, X_R = -6.6, 6.6


def squiggle(x0, x1, y, n=120, amp=0.18, seed_n=1, op=0.9, sw=1.8, c=INK):
    """A clean-ish audio waveform (smooth, low jitter)."""
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


def mic_glyph():
    body = RoundedRectangle(width=0.18, height=0.34, corner_radius=0.09,
                            stroke_color=INK, stroke_width=2.0,
                            fill_color=BG, fill_opacity=1.0)
    stem = Line(ORIGIN, DOWN * 0.16, stroke_color=INK, stroke_width=2.0)
    base = Line(LEFT * 0.1, RIGHT * 0.1, stroke_color=INK, stroke_width=2.0)
    stem.next_to(body, DOWN, buff=0.0)
    base.next_to(stem, DOWN, buff=0.0)
    return VGroup(body, stem, base)


class VoiceAsTeacher(Scene):
    def construct(self):
        seed()

        lane_l, lane_r = -4.7, 4.7
        voice_y = 3.05
        mus_y = 2.05

        # =================================================================
        # BEAT 1 — PUZZLE (~0.64s): a lone dim EMG lane + a ghost "?".
        # =================================================================
        self.next_section("puzzle")

        # word ticks shared by both lanes (drawn ghosted now, used in beat 2).
        n_ticks = 6
        tick_xs = np.linspace(lane_l + 0.4, lane_r - 0.4, n_ticks)
        v_ticks = VGroup(*[Line([x, voice_y - 0.34, 0], [x, mus_y + 0.34, 0],
                                stroke_color=INK_GHOST, stroke_width=1.0)
                           for x in tick_xs])

        emg = speckle_row(lane_l + 0.15, lane_r - 0.15, mus_y, c=INK_FAINT)
        m_lab = mono("muscles (EMG)", 16, INK_FAINT).next_to(
            emg, RIGHT, buff=0.22).set_y(mus_y)

        q_mark = serif("?", 84, INK_GHOST).move_to([0, voice_y - 0.1, 0])

        self.play(LaggedStartMap(FadeIn, emg, lag_ratio=0.01, run_time=0.35),
                  FadeIn(m_lab), FadeIn(q_mark, scale=0.8), run_time=0.4)
        self.wait(0.24)

        # =================================================================
        # BEAT 2 — TRICK (~0.60s): mic + clean voice wave, time-aligned; stamp.
        # =================================================================
        self.next_section("trick")

        wave = squiggle(lane_l + 0.15, lane_r - 0.15, voice_y, op=0.92)
        mic = mic_glyph().scale(0.9).move_to([lane_l - 0.55, voice_y, 0])

        stamp_t = mono("TRAINING ONLY", 14, INK_DIM, w=BOLD)
        stamp = VGroup(stamp_t, SurroundingRectangle(stamp_t, color=INK_FAINT,
                                                     stroke_width=1.2, buff=0.12))
        stamp.move_to([X_R - 1.0, 3.6, 0])

        self.play(FadeOut(q_mark, scale=1.2), run_time=0.2)
        self.play(Create(wave), FadeIn(mic, shift=RIGHT * 0.1),
                  LaggedStartMap(Create, v_ticks, lag_ratio=0.06),
                  FadeIn(stamp, shift=DOWN * 0.08), run_time=0.4)

        top_lane = VGroup(wave, mic)

        # =================================================================
        # BEAT 3 — MODEL (~5.81s): voice -> tall layer stack -> layer 9 field.
        # =================================================================
        self.next_section("model")

        # dim the lanes a touch; the stack now owns the stage.
        self.play(top_lane.animate.set_opacity(0.55),
                  emg.animate.set_opacity(0.30),
                  m_lab.animate.set_opacity(0.30),
                  v_ticks.animate.set_opacity(0.4), run_time=0.5)

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

        raw_in = squiggle(stack_x - 0.9, stack_x + 0.9, stack_bottom - 0.55,
                          n=60, amp=0.10, op=0.7, sw=1.4, c=INK_DIM)

        # a feed line from the voice lane down into the stack input.
        feed = VGroup(
            Line([lane_l - 0.55, voice_y - 0.42, 0], [lane_l - 0.55, stack_bottom - 0.55, 0],
                 stroke_color=INK_GHOST, stroke_width=1.4),
            Line([lane_l - 0.55, stack_bottom - 0.55, 0],
                 [stack_x - 0.95, stack_bottom - 0.55, 0],
                 stroke_color=INK_GHOST, stroke_width=1.4),
        )

        self.play(Create(feed), FadeIn(raw_in), run_time=0.6)
        self.play(LaggedStartMap(FadeIn, plates, lag_ratio=0.12,
                                 shift=UP * 0.06, run_time=0.9),
                  FadeIn(stack_lab), FadeIn(stack_sub), run_time=0.9)

        # a pulse rises through the stack: raw -> structured.
        pulse = Rectangle(width=plate_w, height=0.10, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.55).move_to(
            [stack_x, stack_bottom - 0.3, 0])
        self.add(pulse)
        self.play(pulse.animate.move_to([stack_x, plates[-1].get_y() + 0.2, 0]),
                  run_time=1.0, rate_func=linear)
        self.remove(pulse)

        # LAYER 9 = "the tap": highlight a middle plate.
        tap_idx = 3
        tap_plate = plates[tap_idx]
        l9_lab = mono("layer 9", 14, INK).next_to(tap_plate, LEFT, buff=0.20)
        tap_tag = mono("the tap", 13, INK_DIM).next_to(l9_lab, DOWN, buff=0.06)
        tap_tag.align_to(l9_lab, RIGHT)

        self.play(tap_plate.animate.set_stroke(INK, width=2.4).set_fill(INK, 0.30),
                  FadeIn(l9_lab, shift=RIGHT * 0.06),
                  FadeIn(tap_tag, shift=RIGHT * 0.06), run_time=0.7)

        # the rich structured field that layer 9 holds (center of stage).
        field_cx = -0.55
        field_cy = tap_plate.get_y()
        field = field_grid(field_cx, field_cy, w=2.3, h=1.5, rows=7, cols=11)
        field_box = SurroundingRectangle(field, color=INK, stroke_width=1.6, buff=0.10)
        field_cap = mono("a rich, structured picture", 14, INK_DIM).next_to(
            field_box, UP, buff=0.14)
        tap_line = Line(tap_plate.get_right(), field_box.get_left(),
                        stroke_color=INK, stroke_width=1.6)

        self.play(Create(tap_line),
                  LaggedStartMap(FadeIn, field, lag_ratio=0.01, run_time=1.0),
                  Create(field_box), FadeIn(field_cap), run_time=1.1)
        self.wait(0.6)

        # =================================================================
        # BEAT 4 — COPY (~1.29s): stream the field into the third output.
        # =================================================================
        self.next_section("copy")

        # the field is now the focus; dim the stack chrome.
        self.play(field_cap.animate.set_opacity(0.35),
                  VGroup(stack_lab, stack_sub).animate.set_opacity(0.25),
                  run_time=0.25)

        heads_x = 3.7
        head_ys = [-0.45, -1.25, -2.05]
        head_names = ["100 units", "40 phonemes", "1024-number projection"]
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

        third = head_boxes[2]

        # the distillation STREAM: from the field, down and over into the third.
        stream = VGroup(
            Line(field_box.get_bottom(), [field_cx, third.get_y(), 0],
                 stroke_color=INK, stroke_width=2.2),
            Line([field_cx, third.get_y(), 0], third.get_left(),
                 stroke_color=INK, stroke_width=2.2),
        )

        self.play(LaggedStartMap(FadeIn, heads, lag_ratio=0.08, run_time=0.4),
                  FadeIn(muscle_lab), run_time=0.4)

        # a #fff droplet travels the stream into the third output (the teaching).
        drop = Dot(field_box.get_bottom(), radius=0.06, color=WHITE)
        self.add(drop)
        self.play(LaggedStartMap(Create, stream, lag_ratio=0.4),
                  MoveAlongPath(drop, stream[0]), run_time=0.35,
                  rate_func=linear)
        self.play(MoveAlongPath(drop, stream[1]), run_time=0.3, rate_func=linear)
        self.play(FadeOut(drop, scale=0.3),
                  third.animate.set_fill(INK, 0.22).set_stroke(WHITE, width=2.2),
                  run_time=0.2)

        # DISTANCE BAR shrinks: the third output "reshapes to match" the teacher.
        dist_track = RoundedRectangle(width=3.0, height=0.14, corner_radius=0.05,
                                      stroke_color=INK_GHOST, stroke_width=1.0,
                                      fill_opacity=0).move_to([heads_x, -2.85, 0])
        dist_fill = Rectangle(width=3.0, height=0.14, stroke_width=0,
                              fill_color=INK, fill_opacity=0.7)
        dist_fill.align_to(dist_track, LEFT).set_y(dist_track.get_y())
        dist_lab = mono("distance to teacher", 12, INK_FAINT).next_to(
            dist_track, UP, buff=0.10).set_x(dist_track.get_x())

        self.play(Create(dist_track), FadeIn(dist_fill), FadeIn(dist_lab),
                  run_time=0.25)
        self.play(dist_fill.animate.stretch_to_fit_width(3.0 * 0.18).align_to(
                      dist_track, LEFT),
                  third.animate.set_fill(INK, 0.16).set_stroke(INK, width=1.8),
                  run_time=0.45)
        dist_fill.align_to(dist_track, LEFT)

        # =================================================================
        # BEAT 5 — CAVEAT (~2.17s): two chips — sounds (PER) down, words static.
        # =================================================================
        self.next_section("caveat")

        apparatus = VGroup(top_lane, v_ticks, stamp, feed, raw_in, plates,
                           stack_lab, stack_sub, l9_lab, tap_tag, tap_line,
                           field, field_box, field_cap, stream, heads,
                           muscle_lab, dist_track, dist_fill, dist_lab,
                           emg, m_lab)
        # Fade the whole apparatus fully out (not to 0.12): this both clears the
        # caveat chips of any bleed-through AND ensures the audio teacher +
        # TRAINING-ONLY stamp are GONE at use-time (beat 6 restores only the
        # surviving muscle path: emg + the third output + the struck mic).
        self.play(apparatus.animate.set_opacity(0.0), run_time=0.55)

        # two chips, centered.
        per_box = RoundedRectangle(width=2.7, height=1.0, corner_radius=0.10,
                                   stroke_color=INK, stroke_width=2.0,
                                   fill_color=INK, fill_opacity=0.06)
        per_box.move_to([-1.9, 0.2, 0])
        per_t = mono("sounds (PER)", 18, INK).next_to(per_box.get_top(), DOWN, buff=0.16)
        per_arrow = Triangle(stroke_width=0, fill_color=WHITE,
                             fill_opacity=0.9).scale(0.12)
        per_arrow.next_to(per_t, DOWN, buff=0.18)
        per_word = mono("ticking down", 14, INK_DIM).next_to(per_arrow, DOWN, buff=0.12)
        per_grp = VGroup(per_box, per_t)

        wer_box = RoundedRectangle(width=2.7, height=1.0, corner_radius=0.10,
                                   stroke_color=INK_GHOST, stroke_width=1.4,
                                   fill_color=INK, fill_opacity=0.0)
        wer_box.move_to([1.9, 0.2, 0])
        wer_t = mono("words (WER)", 18, INK_FAINT).next_to(wer_box.get_top(), DOWN, buff=0.16)
        wer_word = mono("unchanged", 14, INK_GHOST).next_to(wer_t, DOWN, buff=0.30)
        wer_grp = VGroup(wer_box, wer_t, wer_word)

        cap = mono("this mostly sharpens raw sounds — not words yet", 16, INK_DIM)
        cap.move_to([0, -1.9, 0])

        self.play(FadeIn(per_grp), FadeIn(wer_grp), FadeIn(cap, shift=UP * 0.06),
                  run_time=0.6)
        # PER ticks down (arrow drops + glow); WER holds grey.
        self.add(per_arrow)
        self.play(FadeIn(per_arrow, shift=DOWN * 0.1),
                  Indicate(per_t, scale_factor=1.08, color=WHITE), run_time=0.5)
        self.play(per_arrow.animate.shift(DOWN * 0.18),
                  FadeIn(per_word), run_time=0.4)
        self.wait(0.55)

        # =================================================================
        # BEAT 6 — USE-TIME (~1.64s): mic gone, lesson stays; serif payoff.
        # =================================================================
        self.next_section("usetime")

        caveat_grp = VGroup(per_grp, per_arrow, per_word, wer_grp, cap)
        self.play(FadeOut(caveat_grp, shift=DOWN * 0.1), run_time=0.4)

        # bring back the surviving muscle path (EMG + shaped third output).
        third_box = head_boxes[2]
        third_lab = heads[2][1]
        # restore the third output WITHOUT set_opacity(1) clobbering the box fill
        # into a solid block that hides its "1024-number projection" label.
        self.play(emg.animate.set_opacity(0.9),
                  third_box.animate.set_stroke(WHITE, width=2.2, opacity=1.0).set_fill(INK, 0.14),
                  third_lab.animate.set_opacity(1.0),
                  m_lab.animate.set_opacity(0.6), run_time=0.3)

        # strike the mic; the audio apparatus stays near-zero (it's gone at use).
        mic_struck = mic.copy().set_opacity(0.5)
        cross = Cross(mic, stroke_color=INK_DIM, stroke_width=2.4).scale(1.3)
        now_lab = mono("now in use", 14, INK_DIM).move_to([3.4, 3.05, 0])
        self.play(mic.animate.set_opacity(0.5), Create(cross),
                  FadeIn(now_lab, shift=DOWN * 0.06), run_time=0.4)

        payoff = serif("only the lesson remains", 40, WHITE).move_to([0, 0.4, 0])
        payoff_g = glow(payoff)
        self.add(payoff_g)
        self.play(GrowFromCenter(payoff),
                  Flash([0, 0.4, 0], color=WHITE, line_length=0.2, num_lines=14,
                        flash_radius=1.5, time_width=0.4), run_time=0.55)
        self.wait(0.55)
