# S26 — The ground we stood on (the foundation: Harshavardhana T. Gowda)
# Everything in this project rests on Harshavardhana T. Gowda's work — the corpus,
# the 31-channel sensor array, the SPD/geometric features, and the first EMG->text
# decoder. We give it the whole credit: our pipeline is a small block resting on
# two foundation stones (the two papers).
#
# ART DIRECTION — a literal foundation. Two wide stones (the two papers) rise and
# settle; our pipeline block descends and lands ON them; a serif name plate glows
# above. Strict monochrome; the single pure-#fff accent is the name itself.
#   TOP strip   (y ~ +3.0): cap "THE GROUND WE STOOD ON"
#   CENTER      : name plate (glow) -> our block -> two foundation stones
#   BOTTOM strip(y ~ -3.2): "his data · his sensors · his architecture · his baseline"
from manim import *
from emg_style import *

WHITE = "#ffffff"


def stone(title, gave, lines, w=5.5, h=2.45):
    """A foundation stone: a rounded slab carrying a paper's contribution."""
    slab = RoundedRectangle(width=w, height=h, corner_radius=0.10,
                            stroke_color=INK_DIM, stroke_width=1.8,
                            fill_color=INK, fill_opacity=0.05)
    head = mono(title, 18, INK)
    gave_l = mono(gave, 12.5, INK_FAINT)
    body = VGroup(*[mono(t, 12.5, INK_DIM) for t in lines]).arrange(
        DOWN, buff=0.10, aligned_edge=LEFT)
    inner = VGroup(head, gave_l, body).arrange(DOWN, buff=0.12)
    inner.move_to(slab.get_center())
    return VGroup(slab, inner)


class Foundation(Scene):
    def construct(self):
        seed()

        self.next_section("cap")
        top1 = mono("THE GROUND WE STOOD ON", 26, INK_DIM, w=BOLD).move_to([0, 3.16, 0])
        rule = Line([-6.4, 2.64, 0], [6.4, 2.64, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.14), Create(rule), run_time=0.45)

        # ---- the two foundation stones (the two papers) ----------------
        left = stone(
            "a geometric perspective",
            "Gowda & Miller",
            ["31-channel surface array", "SPD covariance features",
             "EMG → text at the phoneme level", "the dual-CTC decoder"],
        )
        right = stone(
            "emg2speech",
            "Gowda, Comstock & Miller",
            ["the General Corpus — 9,660 sentences", "one healthy subject, 5 kHz",
             "simultaneous parallel audio", "self-supervised speech features"],
        )
        left.move_to([-2.95, -1.05, 0])
        right.move_to([2.95, -1.05, 0])

        # stones rise from just below and settle (FadeIn preserves each child's
        # own opacity — set_opacity(1) would clobber the slab's 0.05 fill).
        self.play(
            FadeIn(left, shift=UP * 0.5),
            FadeIn(right, shift=UP * 0.5),
            run_time=0.6, rate_func=smooth)

        stones_top = left[0].get_top()[1]   # y of the stones' top edge

        # ---- our pipeline block descends and lands ON the stones -------
        our = RoundedRectangle(width=4.6, height=0.92, corner_radius=0.10,
                               stroke_color=INK, stroke_width=2.2,
                               fill_color=INK, fill_opacity=0.07)
        our_lbl = VGroup(
            mono("our pipeline", 17, INK),
            mono("bidirectional Conformer · ensemble · rerank", 12.5, INK_FAINT),
        ).arrange(DOWN, buff=0.10)
        our_block = VGroup(our, our_lbl)
        our_lbl.move_to(our.get_center())
        land_y = stones_top + our.height / 2 + 0.06
        our_block.move_to([0, land_y, 0])
        # descends from above and lands on the stones (FadeIn keeps the slab's
        # own 0.07 fill and the bright label intact).
        self.play(FadeIn(our_block, shift=DOWN * 1.1),
                  run_time=0.6, rate_func=rate_functions.ease_in_quad)
        # short load-lines reach down FROM the block INTO each stone (it is rooted)
        loadL = Line([-2.0, land_y - our.height / 2, 0], [-2.0, stones_top - 0.55, 0],
                     stroke_color=INK_GHOST, stroke_width=1.4)
        loadR = Line([2.0, land_y - our.height / 2, 0], [2.0, stones_top - 0.55, 0],
                     stroke_color=INK_GHOST, stroke_width=1.4)
        self.play(
            Flash([0, stones_top, 0], color=WHITE, line_length=0.14, num_lines=16,
                  flash_radius=1.4, time_width=0.4),
            Create(loadL), Create(loadR), run_time=0.45)

        # ---- the name plate ignites above (the single white accent) ----
        self.next_section("name")
        name = serif("Harshavardhana T. Gowda", 34, WHITE).move_to([0, 2.05, 0])
        affil = mono("with Daniel C. Comstock & Lee M. Miller   ·   University of California, Davis",
                     13, INK_FAINT).next_to(name, DOWN, buff=0.16)
        name_g = glow(name)
        self.add(name_g)
        self.play(FadeIn(name, shift=DOWN * 0.12), run_time=0.5)
        self.play(FadeIn(affil),
                  Flash(name.get_center(), color=WHITE, line_length=0.18, num_lines=16,
                        flash_radius=1.9, time_width=0.5), run_time=0.5)

        # ---- BOTTOM strip: the running credit line ---------------------
        self.next_section("credit")
        credit = mono("the corpus  ·  the sensors  ·  the architecture  ·  the baseline",
                      17, INK_DIM).move_to([0, -3.02, 0])
        upward = mono("all from UC Davis — we only built upward", 15, INK_FAINT).next_to(
            credit, DOWN, buff=0.12)
        self.play(FadeIn(credit, shift=UP * 0.08), run_time=0.45)
        self.play(FadeIn(upward), run_time=0.35)
        self.wait(0.6)


if __name__ == "__main__":
    pass
