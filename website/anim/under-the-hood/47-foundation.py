# S26 — The ground we stood on (the foundation: Harshavardhana T. Gowda)
# A closing gratitude scene. Everything in this project rests on Harshavardhana
# T. Gowda's work — the corpus, the 31-channel sensor array, the SPD/geometric
# features, and the first EMG->text decoder. Our pipeline is a small block resting
# on two foundation stones (the two papers).
#
# ART DIRECTION — a literal foundation. Two wide stones (the two papers) rise and
# settle; our pipeline block descends and rests ON them; a serif name plate glows
# above as the single pure-#fff accent. Strict monochrome.
#   TOP    (y ~ +3.0): cap "THE GROUND WE STOOD ON"
#   CENTER : name plate (glow) -> our block -> two foundation stones
#   BOTTOM (y ~ -3.0): the running credit line, then the faint "built upward" sub-line
#
# Beat sheet (one next_section per spoken sentence), clip_T ~ 12.0s:
#   1 cap          1.87  look at the ground all of this stood on
#   2 stones       4.59  corpus / array / features / decoder — all UC Davis
#   3 our-block    1.79  our pipeline is one small block resting on that work
#   4 name         2.26  credit to Gowda, with Comstock and Miller
#   5 credit       0.78  we didn't start from zero
#   6 upward       0.68  we only built upward
from manim import *
from style import *

WHITE = "#ffffff"


def stone(title, gave, lines, w=5.5, h=2.45):
    """A foundation stone: a rounded slab carrying a paper's contribution."""
    slab = RoundedRectangle(width=w, height=h, corner_radius=0.10,
                            stroke_color=INK_DIM, stroke_width=1.8,
                            fill_color=BG, fill_opacity=0)
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

        # ============================================================== #
        #  BEAT 1 — "look at the ground all of this stood on"  (1.87s)    #
        # ============================================================== #
        self.next_section("cap")
        top1 = mono("THE GROUND I STOOD ON", 26, INK_DIM, w=BOLD).move_to([0, 3.16, 0])
        rule = Line([-6.4, 2.64, 0], [6.4, 2.64, 0], stroke_color=LINE, stroke_width=1.2)
        self.play(FadeIn(top1, shift=DOWN * 0.14), Create(rule), run_time=0.6)
        self.wait(1.27)

        # ============================================================== #
        #  BEAT 2 — the two foundation stones rise  (4.59s)              #
        # ============================================================== #
        self.next_section("stones")
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

        # Stones rise from below and settle. FadeIn preserves each child's own
        # opacity — set_opacity(1) would clobber the slab's 0.05 fill.
        self.play(
            FadeIn(left, shift=UP * 0.5),
            FadeIn(right, shift=UP * 0.5),
            run_time=1.1, rate_func=smooth)
        self.wait(3.49)

        stones_top = left[0].get_top()[1]   # y of the stones' top edge

        # ============================================================== #
        #  BEAT 3 — our pipeline block descends and rests on them (1.79s)#
        # ============================================================== #
        self.next_section("our-block")
        our = RoundedRectangle(width=4.6, height=0.92, corner_radius=0.10,
                               stroke_color=INK, stroke_width=2.2,
                               fill_color=BG, fill_opacity=0)
        our_lbl = VGroup(
            mono("my pipeline", 17, INK),
            mono("bidirectional Conformer · ensemble · rerank", 12.5, INK_FAINT),
        ).arrange(DOWN, buff=0.10)
        our_block = VGroup(our, our_lbl)
        our_lbl.move_to(our.get_center())
        land_y = stones_top + our.height / 2 + 0.06
        our_block.move_to([0, land_y, 0])
        # Descends and rests on the stones (FadeIn keeps the slab fill + label).
        self.play(FadeIn(our_block, shift=DOWN * 1.1),
                  run_time=0.6, rate_func=rate_functions.ease_in_quad)
        # Short load-lines reach down FROM the block INTO each stone (it is rooted).
        loadL = Line([-2.0, land_y - our.height / 2, 0], [-2.0, stones_top - 0.55, 0],
                     stroke_color=INK_GHOST, stroke_width=1.4)
        loadR = Line([2.0, land_y - our.height / 2, 0], [2.0, stones_top - 0.55, 0],
                     stroke_color=INK_GHOST, stroke_width=1.4)
        # A soft "resting" flash — trimmed so it reads as settling, not impact.
        self.play(
            Flash([0, stones_top, 0], color=WHITE, line_length=0.10, num_lines=14,
                  flash_radius=1.0, time_width=0.5),
            Create(loadL), Create(loadR), run_time=0.5)
        self.wait(0.69)

        # ============================================================== #
        #  BEAT 4 — the name plate ignites (single white accent)  (2.26s)#
        # ============================================================== #
        self.next_section("name")
        # Dim the supporting structure so the eye goes to the name. Dim STROKE +
        # inner text only — NEVER set_opacity on the slabs (it clobbers their
        # transparent fill into a solid grey).
        slabs = VGroup(left[0], right[0], our)
        inner_bits = VGroup(left[1], right[1], our_lbl, loadL, loadR)
        name = serif("Harshavardhana T. Gowda", 34, WHITE).move_to([0, 2.05, 0])
        affil = mono("with Zachary D. McNaughton, Daniel C. Comstock & Lee M. Miller   ·   UC Davis",
                     13, INK_FAINT).next_to(name, DOWN, buff=0.16)
        name_g = glow(name)
        self.add(name_g)
        self.play(slabs.animate.set_stroke(opacity=0.4),
                  inner_bits.animate.set_opacity(0.5),
                  FadeIn(name, shift=DOWN * 0.12), run_time=0.7)
        self.play(FadeIn(affil),
                  Flash(name.get_center(), color=WHITE, line_length=0.18, num_lines=16,
                        flash_radius=1.9, time_width=0.5), run_time=0.6)
        self.wait(0.96)

        # ============================================================== #
        #  BEAT 5 — "we didn't start from zero"  (0.78s)                 #
        # ============================================================== #
        self.next_section("credit")
        credit = mono("the corpus  ·  the sensors  ·  the architecture  ·  the baseline",
                      17, INK_DIM).move_to([0, -3.02, 0])
        self.play(FadeIn(credit, shift=UP * 0.08), run_time=0.45)
        self.wait(0.33)

        # ============================================================== #
        #  BEAT 6 — "we only built upward"  (0.68s)                      #
        # ============================================================== #
        self.next_section("upward")
        upward = mono("all from UC Davis — I only built upward", 15, INK_FAINT).next_to(
            credit, DOWN, buff=0.12)
        self.play(FadeIn(upward), run_time=0.38)
        self.wait(0.3)


if __name__ == "__main__":
    pass
