# I5 — Muscles. Speech is movement: the brain fires electrical commands down
# nerves to the face & throat muscles; each contraction is itself electrical.
# Beats (one per narration sentence):
#   1 FACE      a stylized front face appears.
#   2 BRAIN     a labelled "brain" dot fires electrical pulses down nerves to
#               muscle patches across the face, jaw and throat.
#   3 LIPS      orbicularis oris (lips) lights + callout.
#   4 CHEEKJAW  zygomaticus (cheek) + masseter (jaw) light + callouts.
#   5 TONGUETHROAT genioglossus (tongue) + sternohyoid (larynx) light + callouts.
#   6 SEQUENCE  all fire in a quick rhythmic sequence.
#   7 ELECTRIC  a contracting muscle is itself a burst of electricity.
from manim import *
from style import *
import numpy as np

M = {
    "oris": [0.0, -0.55, 0],
    "zyg_l": [-0.95, 0.05, 0], "zyg_r": [0.95, 0.05, 0],
    "mas_l": [-1.2, -0.7, 0], "mas_r": [1.2, -0.7, 0],
    "genio": [0.0, -1.15, 0],
    "sth": [0.0, -2.05, 0],
}
BRAIN = [0.0, 2.4, 0]


def face():
    head = Ellipse(width=3.0, height=4.0).set_stroke(INK, 2.2).move_to([0, 0.6, 0])
    eye_l = Arc(0.22, PI, PI, arc_center=[-0.5, 1.15, 0]).set_stroke(INK_DIM, 2)
    eye_r = Arc(0.22, PI, PI, arc_center=[0.5, 1.15, 0]).set_stroke(INK_DIM, 2)
    nose = VMobject().set_points_as_corners([[0, 0.85, 0], [-0.12, 0.2, 0], [0.12, 0.2, 0]]).set_stroke(INK_DIM, 2)
    ear_l = Arc(0.28, -PI / 2, PI, arc_center=[-1.5, 0.6, 0]).set_stroke(INK_DIM, 2)
    ear_r = Arc(0.28, PI / 2, PI, arc_center=[1.5, 0.6, 0]).set_stroke(INK_DIM, 2)
    neck = VGroup(Line([-0.55, -1.35, 0], [-0.7, -2.7, 0]), Line([0.55, -1.35, 0], [0.7, -2.7, 0])).set_stroke(INK, 2)
    shoulders = ArcBetweenPoints([-2.4, -3.1, 0], [2.4, -3.1, 0], angle=-0.5).set_stroke(INK, 2)
    return VGroup(head, eye_l, eye_r, nose, ear_l, ear_r, neck, shoulders)


def marker(key):
    return Circle(radius=0.16, stroke_color=INK_FAINT, stroke_width=2).set_fill(INK, 0.04).move_to(M[key])


def callout(mk, text, sub, lx, ly, side):  # side "L"/"R"
    al = RIGHT if side == "L" else LEFT
    label = VGroup(mono(text, 22, INK), mono(sub, 16, INK_FAINT)).arrange(DOWN, buff=0.06, aligned_edge=al)
    label.move_to([lx, ly, 0]).align_to([lx, ly, 0], al)
    edge = label.get_right() if side == "L" else label.get_left()
    leader = Line(mk.get_center(), edge + (LEFT if side == "L" else RIGHT) * 0.15,
                  stroke_color=INK_GHOST, stroke_width=1.2)
    return label, leader


class Muscles(Scene):
    def construct(self):
        seed()
        fc = face()
        markers = {k: marker(k) for k in M}

        def glow_on(*keys):
            return [markers[k].animate.set_stroke("#ffffff", 2.6).set_fill("#ffffff", 0.55) for k in keys]

        # ---- BEAT 1: FACE -----------------------------------------------
        self.next_section("face")
        title = mono("speech starts as movement", 26, INK_FAINT).to_edge(UP, buff=0.45)
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.4)
        self.play(Create(fc, run_time=1.3))
        self.wait(0.3)

        # ---- BEAT 2: BRAIN FIRES DOWN NERVES ----------------------------
        self.next_section("brain")
        brain = Dot(BRAIN, radius=0.12, color="#ffffff")
        brain_lab = mono("brain", 22, INK).next_to(brain, RIGHT, buff=0.2)
        targets = ["oris", "zyg_l", "zyg_r", "mas_l", "mas_r", "genio", "sth"]
        nerves = VGroup(*[Line(BRAIN, M[k], stroke_color=INK_GHOST, stroke_width=1.4) for k in targets])
        nerve_lab = mono("nerve", 17, INK_FAINT)
        # sit clear of the head outline (a midpoint label crosses the ellipse stroke)
        nerve_lab.move_to([2.35, 1.7, 0])
        note = mono("the brain fires electrical commands down the nerves", 20, INK_DIM).move_to([0, -3.4, 0])

        self.play(FadeIn(brain, scale=1.6), FadeIn(brain_lab),
                  Flash(brain.get_center(), color="#ffffff", num_lines=12, flash_radius=0.4), run_time=0.5)
        self.play(LaggedStart(*[Create(n) for n in nerves], lag_ratio=0.08, run_time=0.8),
                  FadeIn(nerve_lab), FadeIn(note))
        # electrical pulses travel from brain down each nerve to its muscle
        pulses = VGroup(*[Dot(BRAIN, radius=0.07, color="#ffffff") for _ in targets])
        self.add(pulses)
        self.play(*[MoveAlongPath(pulses[i], nerves[i]) for i in range(len(targets))],
                  LaggedStart(*[GrowFromCenter(markers[k]) for k in targets], lag_ratio=0.04),
                  run_time=1.1, rate_func=rush_into)
        self.play(FadeOut(pulses), run_time=0.2)
        self.wait(0.25)

        # ---- BEAT 3: LIPS -----------------------------------------------
        self.next_section("lips")
        self.play(FadeOut(note), FadeOut(nerve_lab), nerves.animate.set_stroke(opacity=0.25), run_time=0.3)
        l_oris, ld_oris = callout(markers["oris"], "orbicularis oris", "lips · rounding", 3.6, -0.4, "R")
        self.play(*glow_on("oris"), Create(ld_oris), FadeIn(l_oris, shift=RIGHT * 0.1), run_time=0.7)
        self.wait(0.2)

        # ---- BEAT 4: CHEEK + JAW ----------------------------------------
        self.next_section("cheekjaw")
        l_zyg, ld_zyg = callout(markers["zyg_l"], "zygomaticus", "cheek · lifts", -3.6, 0.35, "L")
        l_mas, ld_mas = callout(markers["mas_r"], "masseter", "jaw · closes", 3.6, -1.55, "R")
        self.play(*glow_on("zyg_l", "zyg_r"), Create(ld_zyg), FadeIn(l_zyg, shift=LEFT * 0.1), run_time=0.6)
        self.play(*glow_on("mas_l", "mas_r"), Create(ld_mas), FadeIn(l_mas, shift=RIGHT * 0.1), run_time=0.6)
        self.wait(0.2)

        # ---- BEAT 5: TONGUE + THROAT ------------------------------------
        self.next_section("tonguethroat")
        l_gen, ld_gen = callout(markers["genio"], "genioglossus", "tongue · under chin", -3.6, -1.25, "L")
        l_sth, ld_sth = callout(markers["sth"], "sternohyoid", "larynx · steadies", 3.6, -2.5, "R")
        self.play(*glow_on("genio"), Create(ld_gen), FadeIn(l_gen, shift=LEFT * 0.1), run_time=0.6)
        self.play(*glow_on("sth"), Create(ld_sth), FadeIn(l_sth, shift=RIGHT * 0.1), run_time=0.6)
        self.wait(0.2)

        # ---- BEAT 6: SEQUENCE -------------------------------------------
        self.next_section("sequence")
        callouts = VGroup(l_oris, ld_oris, l_zyg, ld_zyg, l_mas, ld_mas, l_gen, ld_gen, l_sth, ld_sth)
        seq_note = mono("dozens of muscles — a precise sequence", 22, INK_DIM).move_to([0, -3.45, 0])
        self.play(callouts.animate.set_opacity(0.22), FadeIn(seq_note), run_time=0.4)
        order = ["mas_l", "mas_r", "oris", "zyg_l", "zyg_r", "genio", "sth", "oris", "mas_l", "mas_r"]
        for k in order:
            self.play(Indicate(markers[k], scale_factor=1.5, color=WHITE), run_time=0.16)
        self.wait(0.15)

        # ---- BEAT 7: A CONTRACTION IS ELECTRICAL ------------------------
        self.next_section("electric")
        self.play(FadeOut(seq_note), FadeOut(callouts), FadeOut(VGroup(brain, brain_lab, nerves)), run_time=0.3)
        bolt = VMobject().set_points_as_corners([
            [1.2, -0.55, 0], [1.45, -0.2, 0], [1.3, -0.2, 0], [1.6, 0.25, 0],
        ]).set_stroke("#ffffff", 3)
        flick = mono("a contracting muscle is itself a burst of electricity", 23, INK).move_to([0, -3.4, 0])
        self.play(*glow_on("mas_r"), Create(bolt),
                  Flash(M["mas_r"], color="#ffffff", num_lines=14, flash_radius=0.6),
                  FadeIn(flick, shift=UP * 0.1), run_time=0.8)
        self.wait(0.6)
