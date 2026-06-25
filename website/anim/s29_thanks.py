# S29 — Thank you (the reader, the maker, Claude)
# The emotional coda. The calmest scene: four sentences, four reveals. Each new
# line is spotlit while everything already shown dims back so attention always
# rests on the newest words.
#   beat 1  the "EMG → TEXT" brand mark fades in — the title of the whole journey
#   beat 2  "Thank you" writes in with a single soft white Flash
#   beat 3  divider + "made by" + the glowing "Varshith Madishetty" plate
#   beat 4  "built with the help of" + the rotating Claude sunburst + "Claude"
# Strict monochrome; the pure-#fff accents are "Thank you" and the Claude Flash.
from manim import *
from emg_style import *

WHITE = "#ffffff"


def claude_mark(c=INK, s=1.0):
    """A monochrome homage to the Claude / Anthropic sunburst: radiating rays."""
    rays = VGroup()
    n = 12
    for i in range(n):
        ray = RoundedRectangle(width=0.055 * s, height=0.20 * s, corner_radius=0.025 * s,
                               stroke_width=0, fill_color=c, fill_opacity=1.0)
        ray.move_to([0, 0.235 * s, 0]).rotate(i * TAU / n, about_point=ORIGIN)
        rays.add(ray)
    return rays


class Thanks(Scene):
    def construct(self):
        seed()

        # ============================================================== #
        #  BEAT 1 — "That's the whole journey — from faint electricity     #
        #  on the skin to words on a screen."                              #
        #  The brand mark fades in at top — the title of everything.       #
        # ============================================================== #
        self.next_section("brand")
        brand = mono("EMG → TEXT", 30, INK, w=BOLD).move_to([0, 0.55, 0])
        sub = mono("skin electricity  →  words on a screen", 16, INK_FAINT).next_to(
            brand, DOWN, buff=0.34)
        self.play(FadeIn(brand, shift=DOWN * 0.12), run_time=0.9)
        self.play(FadeIn(sub, shift=UP * 0.06), run_time=0.7)
        self.wait(2.6)

        # settle the brand mark up to its title position for the rest of the scene
        brand_small = mono("EMG → TEXT", 16, INK_FAINT, w=BOLD).move_to([0, 3.15, 0])
        self.play(ReplacementTransform(brand, brand_small),
                  FadeOut(sub, shift=UP * 0.1), run_time=0.4)

        # ============================================================== #
        #  BEAT 2 — "Thank you for reading all the way to the end."        #
        #  "Thank you" writes in with a single soft white Flash.          #
        # ============================================================== #
        self.next_section("thanks")
        ty = serif("Thank you", 58, WHITE).move_to([0, 1.55, 0])
        self.play(Write(ty), run_time=0.8)
        self.play(Flash(ty.get_center(), color=WHITE, line_length=0.22, num_lines=18,
                        flash_radius=2.3, time_width=0.5), run_time=0.5)
        reader = serif("for making it all the way to the end.", 26, INK_DIM).move_to(
            [0, 0.55, 0])
        self.play(FadeIn(reader, shift=UP * 0.06), run_time=0.5)
        self.wait(0.5)

        # ============================================================== #
        #  BEAT 3 — "This was made by Varshith Madishetty."               #
        #  Divider draws, "made by" appears, the glowing name plate rises. #
        #  Everything above dims so the maker line is the focus.          #
        # ============================================================== #
        self.next_section("maker")
        self.play(ty.animate.set_opacity(0.4),
                  reader.animate.set_opacity(0.4), run_time=0.4)

        rule = Line([-2.0, -0.18, 0], [2.0, -0.18, 0], stroke_color=LINE, stroke_width=1.1)
        by = mono("made by", 13, INK_FAINT).move_to([0, -0.62, 0])
        name = serif("Varshith Madishetty", 34, INK).move_to([0, -1.18, 0])
        self.play(Create(rule), FadeIn(by), run_time=0.5)
        self.play(FadeIn(name, shift=UP * 0.08), run_time=0.6)
        self.wait(0.9)

        # ============================================================== #
        #  BEAT 4 — "And built with the help of Claude."                  #
        #  The Claude row resolves: lead text, the rotating sunburst mark  #
        #  with a tiny Flash, and "Claude". Then the frame holds.          #
        # ============================================================== #
        self.next_section("claude")
        self.play(rule.animate.set_opacity(0.5),
                  by.animate.set_opacity(0.5),
                  name.animate.set_opacity(0.5), run_time=0.4)

        lead = mono("built with the help of", 15, INK_FAINT)
        mark = claude_mark(INK, 0.72)
        cname = mono("Claude", 19, INK).set_z_index(1)
        row = VGroup(lead, mark, cname).arrange(RIGHT, buff=0.32).move_to([0, -2.15, 0])
        mark_g = glow(mark)
        self.play(FadeIn(lead), run_time=0.35)
        self.add(mark_g)
        self.play(GrowFromCenter(mark),
                  Rotate(mark, TAU / 12, about_point=mark.get_center()), run_time=0.45)
        self.play(FadeIn(cname, shift=RIGHT * 0.08),
                  Flash(mark.get_center(), color=WHITE, line_length=0.12, num_lines=12,
                        flash_radius=0.5, time_width=0.4), run_time=0.4)

        # a final quiet breath under the held frame — no new text
        self.play(Indicate(ty, scale_factor=1.04, color=WHITE), run_time=0.7)
        self.wait(0.35)


if __name__ == "__main__":
    pass
