# ONE BREATH 7 — SCORE. "Where the baseline got half the words wrong, this gets four of
# five right — 18.5% word error, from muscles alone."  (the results payoff)
# OPENS ON: the chosen sentence (== scene 6 close).
# The sentence gives way to ONE big word-error number that falls 51 → 18.5 with a
# shrinking bar; it reframes as four-in-five (filled vs dim pills, not empty boxes);
# then the SAME number settles smoothly to the small dim "18.5" scene 8 opens on —
# one continuous element the whole way, so nothing jumps.
from manim import *
from style import *
from one_breath_common import WHITE, counter, motes, drift

STEPS = [51.17, 40.63, 26.14, 18.53]
SENTENCE = "the cat sat by the door"
NUM_C = [0, 0.55, 0]


class Score(Scene):
    def construct(self):
        seed()
        field = drift(motes(seed_n=3))
        self.add(field)

        # ---- OPEN: the chosen sentence (matched) -----------------------
        self.next_section("open")
        sent = mono(SENTENCE, 30, INK).move_to(ORIGIN)
        self.add(sent)
        self.wait(0.1)

        # ---- BEAT 1: the sentence gives way to a big word-error number --
        self.next_section("reveal")
        wer_t = ValueTracker(STEPS[0])
        big = counter(wer_t, fmt=lambda v: f"{v:.1f}", s=150, c=INK, at=NUM_C)
        pct = mono("% of words wrong", 22, INK_FAINT).move_to([0, -1.0, 0])
        tag = mono("published baseline", 18, INK_FAINT).move_to([0, 2.55, 0])
        self.play(sent.animate.shift(DOWN * 0.5).set_opacity(0.0), run_time=0.4)
        self.remove(sent)
        self.add(big)
        self.play(FadeIn(big, scale=0.6), FadeIn(pct, shift=UP * 0.1),
                  FadeIn(tag, shift=DOWN * 0.1),
                  Flash(NUM_C, color=WHITE, num_lines=16, flash_radius=2.4, line_length=0.2),
                  run_time=0.6)

        # ---- BEAT 2: the number falls; a bar shrinks in step -----------
        self.next_section("fall")
        BAR_L, BAR_R, BAR_Y = -3.8, 3.8, -2.45
        track = RoundedRectangle(width=BAR_R - BAR_L, height=0.18, corner_radius=0.05,
                                 stroke_color=INK_GHOST, stroke_width=1.4, fill_opacity=0
                                 ).move_to([(BAR_L + BAR_R) / 2, BAR_Y, 0])

        def bar_for(v):
            w = (BAR_R - BAR_L) * (v / STEPS[0])
            return RoundedRectangle(width=max(0.06, w), height=0.18, corner_radius=0.05,
                                    stroke_width=0, fill_color=INK, fill_opacity=0.85
                                    ).move_to([BAR_L + w / 2, BAR_Y, 0])
        fill = bar_for(STEPS[0])
        fill.add_updater(lambda m: m.become(bar_for(wer_t.get_value())))
        self.play(Create(track), FadeIn(fill), FadeOut(tag), run_time=0.4)
        for v in STEPS[1:]:
            self.play(wer_t.animate.set_value(v), run_time=0.8,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(Flash(NUM_C, color=WHITE, num_lines=10, flash_radius=1.7,
                            line_length=0.12), run_time=0.2)
        fill.clear_updaters()
        wer_t.set_value(STEPS[-1])
        big.clear_updaters()   # freeze the number at 18.5

        # land: the winning number pulses bright, tagged "this pipeline"
        tag2 = mono("this pipeline · from muscles alone", 18, INK).move_to([0, 2.55, 0])
        self.play(Indicate(big, scale_factor=1.1, color=WHITE),
                  Flash(NUM_C, color=WHITE, num_lines=18, flash_radius=2.6, line_length=0.22),
                  FadeIn(tag2, shift=DOWN * 0.1), run_time=0.6)

        # ---- BEAT 3: reframe as four-in-five — filled vs dim pills ------
        self.next_section("four")
        headline = VGroup(big, pct)
        self.play(headline.animate.scale(0.46).move_to([0, 1.55, 0]),
                  FadeOut(track), FadeOut(fill), FadeOut(tag2), run_time=0.6)

        pills = VGroup(*[RoundedRectangle(width=1.15, height=0.62, corner_radius=0.31,
                                          stroke_color=INK, stroke_width=1.8,
                                          fill_color=WHITE,
                                          fill_opacity=(0.92 if i < 4 else 0.1))
                         for i in range(5)]).arrange(RIGHT, buff=0.32).move_to([0, -0.35, 0])
        cap = mono("four words in five, correct", 22, INK_DIM).move_to([0, -1.55, 0])
        self.play(LaggedStart(*[GrowFromCenter(p) for p in pills], lag_ratio=0.08), run_time=0.7)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=0.3)
        self.wait(0.3)

        # ---- BEAT 4: the SAME number settles to the scene-8 block -------
        self.next_section("settle")
        final = mono("18.5", 30, INK_FAINT).move_to([0, -1.4, 0]).set_opacity(0.5)
        self.play(FadeOut(pills), FadeOut(cap), pct.animate.set_opacity(0.0), run_time=0.4)
        self.play(Transform(big, final), run_time=0.7, rate_func=smooth)
        self.wait(0.4)
