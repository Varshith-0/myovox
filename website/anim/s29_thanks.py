# S29 — Thank you (to the reader + the maker + Claude)
# No results or research credits here (those live earlier) — this page thanks the
# person who read to the end, names the maker, and credits Claude (with its mark).
#
# ART DIRECTION — strict monochrome, the calmest scene. The pure-#fff accents are
# "Thank you" and the Claude mark.
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

        # ---- brand mark (top) ------------------------------------------
        self.next_section("brand")
        brand = mono("EMG → TEXT", 16, INK_FAINT, w=BOLD).move_to([0, 3.15, 0])
        self.play(FadeIn(brand, shift=DOWN * 0.1), run_time=0.4)

        # ---- "Thank you" + the reader ----------------------------------
        self.next_section("thanks")
        ty = serif("Thank you", 58, WHITE).move_to([0, 1.85, 0])
        ty_g = glow(ty)
        self.add(ty_g)
        self.play(Write(ty), run_time=0.7)
        self.play(Flash(ty.get_center(), color=WHITE, line_length=0.22, num_lines=18,
                        flash_radius=2.3, time_width=0.5), run_time=0.5)
        reader = serif("for making it all the way to the end.", 26, INK_DIM).move_to([0, 0.78, 0])
        self.play(FadeIn(reader, shift=UP * 0.06), run_time=0.5)

        rule = Line([-2.0, 0.18, 0], [2.0, 0.18, 0], stroke_color=LINE, stroke_width=1.1)
        self.play(Create(rule), run_time=0.4)

        # ---- the maker -------------------------------------------------
        self.next_section("maker")
        by = mono("made by", 13, INK_FAINT).move_to([0, -0.32, 0])
        name = serif("Varshith Madishetty", 34, INK).move_to([0, -0.92, 0])
        name_g = glow(name)
        self.play(FadeIn(by), run_time=0.3)
        self.add(name_g)
        self.play(FadeIn(name, shift=UP * 0.08), run_time=0.5)

        # ---- built with Claude (mark + thanks) -------------------------
        self.next_section("claude")
        lead = mono("built with the help of", 15, INK_FAINT)
        mark = claude_mark(INK, 0.72)
        cname = mono("Claude", 19, INK).set_z_index(1)
        row = VGroup(lead, mark, cname).arrange(RIGHT, buff=0.32).move_to([0, -1.95, 0])
        mark_g = glow(mark)
        self.play(FadeIn(lead), run_time=0.3)
        self.add(mark_g)
        self.play(GrowFromCenter(mark), Rotate(mark, TAU / 12, about_point=mark.get_center()),
                  run_time=0.5)
        self.play(FadeIn(cname, shift=RIGHT * 0.08),
                  Flash(mark.get_center(), color=WHITE, line_length=0.12, num_lines=12,
                        flash_radius=0.5, time_width=0.4), run_time=0.45)
        thank_c = mono("thank you, Claude", 13, INK_FAINT).next_to(row, DOWN, buff=0.26)
        self.play(FadeIn(thank_c), run_time=0.35)

        # ---- a final quiet breath --------------------------------------
        self.play(Indicate(ty, scale_factor=1.04, color=WHITE), run_time=0.7)
        self.wait(0.8)


if __name__ == "__main__":
    pass
