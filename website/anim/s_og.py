# Social-share (Open Graph) card — 1200x630 still. Render with:
#   manim -s -r 1200,630 s_og.py OG     (saves images/OG.png)
# On-brand monochrome: brand mark, serif hook line, the headline result, a faint
# sensor→text motif. Used as og:image / twitter:image for link previews.
from manim import *
from emg_style import *

WHITE = "#ffffff"


class OG(Scene):
    def construct(self):
        seed()
        # at 1200x630 the frame is 8 tall, ~15.24 wide (x ~ -7.6..7.6)

        brand = mono("MYOVOX", 22, INK_FAINT, w=BOLD).move_to([0, 2.62, 0])

        line1 = serif("Reading speech from the", 46, INK)
        line2 = serif("muscles of the face.", 46, INK)
        head = VGroup(line1, line2).arrange(DOWN, buff=0.18).move_to([0, 1.15, 0])
        head_g = glow(head)

        # the hook: the headline number, bright
        num_big = num("18.5%", 60, WHITE).move_to([0, -1.05, 0])
        num_g = glow(num_big)
        lab = mono("word error rate  ·  surface EMG, no microphone", 18, INK_DIM).next_to(
            num_big, DOWN, buff=0.22)

        rule = Line([-2.4, -0.2, 0], [2.4, -0.2, 0], stroke_color=LINE, stroke_width=1.2)

        # faint sensor → text motif along the very bottom
        dots = VGroup(*[Dot([x, -2.95, 0], radius=0.04, color=INK_FAINT)
                        for x in np.linspace(-2.2, 0.2, 7)]).set_opacity(0.5)
        arrow = mono("→", 20, INK_FAINT).move_to([0.7, -2.95, 0])
        word = mono("text", 18, INK_DIM).move_to([1.5, -2.95, 0])
        motif = VGroup(dots, arrow, word)

        foot = mono("an interactive explainer", 15, INK_FAINT).move_to([0, -3.45, 0])

        self.add(head_g, brand, rule, num_g, lab, motif, foot)
        self.wait(0.1)
