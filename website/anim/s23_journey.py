# website/anim/s23_journey.py  —  S23 "The whole journey" (recap)
# A single uninterrupted left->right "current" through the WHOLE machine, staged
# across the FULL canvas as a three-deck circuit board:
#   TOP strip   : a quiet context line — "everything you have just seen, in order"
#                 — over a thin fenced rule, with a live "stage k / 9" readout.
#   CENTER deck : the nine reused station glyphs (mouth, dotted head, fingerprint
#                 filmstrip, READER, phoneme cells, word-map, candidate pool, LLM
#                 chooser, TEXT) drawn LARGE on one horizontal rail; a bright white
#                 pulse sweeps it and lights each station one-by-one as a lit_rail
#                 segment fills behind it.
#   BOTTOM deck : a 0..100% completion bar with a morphing data token, and — as the
#                 pulse arrives — the sentence "the quick brown fox" assembling one
#                 word at a time, then the compact pipeline breadcrumb of the chain.
# The point is motion-as-recap: nothing restated in words — you WATCH one packet of
# data flow through every stage and come out as one glowing sentence.
#
# Strict monochrome (emg_style inks + pure #fff for the single peak accent). No LaTeX.
from manim import *
from emg_style import *
import numpy as np


WHITE = "#ffffff"


def set_op(m, o):
    """Set opacity touching stroke + fill, preserving the relative fill level so a
    BG-filled hollow shape stays hollow as it brightens. Returns m for chaining."""
    for sm in m.family_members_with_points():
        keep_fill = sm.get_fill_opacity()
        sm.set_stroke(opacity=o)
        sm.set_fill(opacity=keep_fill * o)
    return m


class Journey(Scene):
    def construct(self):
        seed()

        # ---- canvas geometry -------------------------------------------------
        # Three decks filling the whole frame (x in [-7.1,7.1], y in [-4,4]):
        #   TOP    strip  ~ +2.5 .. +3.6   context line + stage counter
        #   CENTER deck   ~ -1.3 .. +2.0   nine stations on one rail
        #   BOTTOM strip  ~ -3.7 .. -2.0   sentence assembling + breadcrumb
        xs = np.linspace(-5.95, 5.95, 9)
        STY = 0.95                     # station row y (CENTER)
        rail_y = STY - 1.05            # rail just below the stations  (~-0.10)
        TOP_Y = 3.05                   # context strip
        SENT_Y = -2.55                 # assembling sentence
        BAR_Y = -3.55                  # bottom progress bar / breadcrumb

        # =================================================================
        # TOP STRIP — context line + fenced rule + stage counter
        # =================================================================
        context = mono("everything you have just seen, in order",
                       21, INK_FAINT).move_to([-0.55, TOP_Y, 0])
        top_rule = Line([-6.4, TOP_Y - 0.5, 0], [6.4, TOP_Y - 0.5, 0],
                        stroke_color=INK_GHOST, stroke_width=1.0)

        # stage readout sits at the right end of the strip — "stage  k / 9".
        stage = ValueTracker(0)
        counter_at = np.array([5.55, TOP_Y, 0])
        counter_val = counter(stage, fmt=lambda v: f"{int(round(v))} / 9", s=22, c=INK,
                              at=counter_at)
        counter_lbl = mono("stage", 13, INK_FAINT).move_to([4.6, TOP_Y, 0])

        # =================================================================
        # CENTER DECK — the rail + nine station glyphs (drawn LARGE)
        # =================================================================
        rail = Line([xs[0], rail_y, 0], [xs[-1], rail_y, 0],
                    stroke_color=INK_GHOST, stroke_width=1.6)

        # 0 — SPEAK: a mouth (two lip arcs).
        def st_speak(x):
            top = Arc(radius=0.40, start_angle=PI, angle=-PI,
                      stroke_color=INK, stroke_width=2.6)
            bot = Arc(radius=0.40, start_angle=PI, angle=PI,
                      stroke_color=INK, stroke_width=2.6)
            seam = Line(LEFT * 0.40, RIGHT * 0.40, stroke_color=INK_FAINT, stroke_width=1.6)
            return VGroup(top, bot, seam).move_to([x, STY, 0])

        # 1 — 31 SENSORS: a head outline studded with dots.
        def st_sensors(x):
            head = Circle(radius=0.46, stroke_color=INK_FAINT, stroke_width=1.8,
                          fill_color=BG, fill_opacity=1.0)
            dots = VGroup()
            for k in range(13):
                a = 2 * PI * k / 13 + 0.3
                r = 0.46 * (0.6 + 0.34 * (k % 3 == 0))
                d = Dot(radius=0.045, color=INK, fill_opacity=1.0)
                d.move_to([np.cos(a) * r, np.sin(a) * r, 0])
                dots.add(d)
            return VGroup(head, dots).move_to([x, STY, 0])

        # 2 — FINGERPRINT FILMSTRIP: three little bar-cards in a strip.
        def st_fingerprint(x):
            def card():
                box = RoundedRectangle(width=0.37, height=0.66, corner_radius=0.03,
                                       stroke_color=INK, stroke_width=1.4,
                                       fill_color=BG, fill_opacity=1.0)
                bars = VGroup()
                hs = 0.1 + 0.4 * np.abs(np.random.randn(5))
                hs = hs / hs.max() * 0.46 + 0.06
                for j in range(5):
                    h = float(hs[j])
                    bars.add(Rectangle(width=0.045, height=h, stroke_width=0,
                                       fill_color=INK, fill_opacity=0.9).move_to(
                        [(j - 2) * 0.066, h / 2 - 0.26, 0]))
                return VGroup(box, bars)
            strip = VGroup(*[card() for _ in range(3)]).arrange(RIGHT, buff=0.07)
            return strip.move_to([x, STY, 0])

        # 3 — THE READER: a labelled block.
        def st_reader(x):
            block = RoundedRectangle(width=1.12, height=0.72, corner_radius=0.08,
                                     stroke_color=INK, stroke_width=2.2,
                                     fill_color=BG, fill_opacity=1.0)
            lbl = mono("READER", 12, INK).move_to(block.get_center())
            return VGroup(block, lbl).move_to([x, STY, 0])

        # 4 — PER-FRAME SOUNDS: a row of phoneme cells.
        def st_sounds(x):
            labs = ["DH", "AH", "K", "W"]
            cells = VGroup()
            for i, l in enumerate(labs):
                sq = Square(0.33, stroke_color=INK_FAINT, stroke_width=1.2,
                            fill_color=BG, fill_opacity=1.0)
                t = mono(l, 11, INK if i % 2 == 0 else INK_DIM).move_to(sq)
                cells.add(VGroup(sq, t))
            cells.arrange(RIGHT, buff=0.045)
            return cells.move_to([x, STY, 0])

        # 5 — THE WORD-MAP: a tiny lattice with one path lit.
        def st_wordmap(x):
            p = [np.array(q) for q in (
                [-0.46, 0.0, 0], [-0.05, 0.34, 0], [-0.05, -0.34, 0], [0.44, 0.0, 0])]
            edges = VGroup(
                Line(p[0], p[1], stroke_color=INK_GHOST, stroke_width=1.4),
                Line(p[0], p[2], stroke_color=INK_GHOST, stroke_width=1.4),
                Line(p[1], p[3], stroke_color=INK_GHOST, stroke_width=1.4),
                Line(p[2], p[3], stroke_color=INK_GHOST, stroke_width=1.4),
            )
            path = VGroup(
                Line(p[0], p[1], stroke_color=INK, stroke_width=2.6),
                Line(p[1], p[3], stroke_color=INK, stroke_width=2.6),
            )
            nodes = VGroup(*[Circle(radius=0.065, stroke_color=INK, stroke_width=1.6,
                                    fill_color=BG, fill_opacity=1.0).move_to(q)
                             for q in p])
            return VGroup(edges, path, nodes).move_to([x, STY, 0])

        # 6 — POOL OF CANDIDATES: a small stack of sentence lines.
        def st_pool(x):
            cs = [INK, INK_DIM, INK_DIM, INK_FAINT, INK_FAINT]
            lines = VGroup(*[
                Line(ORIGIN, RIGHT * (0.80 - 0.05 * i), stroke_color=c, stroke_width=2.4)
                for i, c in enumerate(cs)
            ]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            return lines.move_to([x, STY, 0])

        # 7 — THE CHOOSER: a small LLM block.
        def st_chooser(x):
            block = RoundedRectangle(width=1.04, height=0.72, corner_radius=0.14,
                                     stroke_color=INK, stroke_width=2.2,
                                     fill_color=BG, fill_opacity=1.0)
            lbl = mono("LLM", 14, INK).move_to(block.get_center())
            return VGroup(block, lbl).move_to([x, STY, 0])

        # 8 — TEXT: the resolved word in a serif card (the output).
        def st_text(x):
            box = RoundedRectangle(width=1.16, height=0.72, corner_radius=0.06,
                                   stroke_color=INK, stroke_width=2.4,
                                   fill_color=BG, fill_opacity=1.0)
            lbl = serif("fox", 26, INK).move_to(box.get_center())
            return VGroup(box, lbl).move_to([x, STY, 0])

        builders = [st_speak, st_sensors, st_fingerprint, st_reader, st_sounds,
                    st_wordmap, st_pool, st_chooser, st_text]
        names = ["speak", "31 sensors", "fingerprints", "the reader", "sounds",
                 "word-map", "guesses", "the chooser", "text"]
        # one-word "what flows out of this station" tokens, shown on the data token.
        carries = ["voice", "signal", "print", "read", "DH AH K", "word",
                   "guesses", "FOX", "text"]

        stations = VGroup(*[b(x) for b, x in zip(builders, xs)])
        labels = VGroup(*[mono(n, 12, INK_FAINT) for n in names])
        for i, lab in enumerate(labels):
            lab.move_to([xs[i], STY + 0.72, 0])

        stems = VGroup(*[
            Line([x, rail_y, 0], [x, STY - 0.56, 0],
                 stroke_color=INK_GHOST, stroke_width=1.4)
            for x in xs
        ])

        # =================================================================
        # BOTTOM DECK — assembling sentence + progress bar + morphing token
        # =================================================================
        BAR_W = 11.9
        bar_track = RoundedRectangle(width=BAR_W, height=0.12, corner_radius=0.06,
                                     stroke_width=0, fill_color=INK_GHOST,
                                     fill_opacity=1.0).move_to([0, BAR_Y, 0])
        bar_left = bar_track.get_left()[0]
        prog = ValueTracker(0.0)
        bar_fill = always_redraw(lambda: RoundedRectangle(
            width=max(0.0001, BAR_W * prog.get_value()), height=0.12, corner_radius=0.06,
            stroke_width=0, fill_color=INK, fill_opacity=1.0).move_to(
            [bar_left + BAR_W * prog.get_value() / 2, BAR_Y, 0]))
        pct = counter(prog, fmt=lambda v: f"{int(round(v * 100))}%", s=17, c=INK_DIM,
                      at=np.array([bar_left - 0.58, BAR_Y, 0]))
        bar_endlbl = mono("100%", 13, INK_FAINT).move_to([bar_left + BAR_W + 0.58, BAR_Y, 0])

        # the data token: a small capsule with a morphing one-word payload, riding
        # just below the rail to show WHAT is flowing (not just how far).
        TOK_Y = rail_y - 0.55
        def token(text, frac):
            x = xs[0] + (xs[-1] - xs[0]) * frac
            cap_box = RoundedRectangle(width=1.10, height=0.38, corner_radius=0.19,
                                       stroke_color=INK, stroke_width=1.8,
                                       fill_color=BG, fill_opacity=1.0)
            t = mono(text, 14, WHITE)
            if t.get_width() > 0.94:
                t.scale_to_fit_width(0.94)
            t.move_to(cap_box.get_center())
            return VGroup(cap_box, t).move_to([x, TOK_Y, 0])

        # the sentence assembles word-by-word in the bottom strip as the pulse lands.
        # Built as ONE serif Text so Pango keeps a single consistent baseline (no
        # per-word vertical drift from descenders), then sliced into word groups by
        # glyph index so each word can fade in on its own beat.
        sent_str = "the quick brown fox"
        sent = serif(sent_str, 44, INK).move_to([0, SENT_Y, 0])
        # glyph ranges per word (spaces are not glyphs in Pango Text submobjects).
        word_lens = [len(w) for w in sent_str.split(" ")]
        sent_words = VGroup()
        _cur = 0
        for wl in word_lens:
            sent_words.add(VGroup(*sent[_cur:_cur + wl]))
            _cur += wl
        # which station "reveals" each word (last four stations).
        word_at_station = [5, 6, 7, 8]

        # =================================================================
        # ANIMATION
        # =================================================================

        # 0) POSE — fade in the top context strip + empty meters. Establishes the
        #    question: one packet, everything-in-order, with empty meters waiting.
        self.next_section("pose")
        self.play(FadeIn(context, shift=DOWN * 0.1), Create(top_rule), run_time=0.55)
        self.play(FadeIn(counter_lbl), FadeIn(counter_val),
                  FadeIn(bar_track), FadeIn(pct), FadeIn(bar_endlbl),
                  run_time=0.5)
        self.add(bar_fill)

        # 1) BUILD THE BOARD — rail, then LaggedStart-drop the nine stations in
        #    pipeline order with stems + labels, then dim them dormant.
        self.next_section("board")
        self.play(Create(rail), run_time=0.45)
        self.play(
            LaggedStart(
                *[AnimationGroup(
                    FadeIn(stations[i], shift=DOWN * 0.15),
                    FadeIn(labels[i]),
                    Create(stems[i]),
                ) for i in range(9)],
                lag_ratio=0.26, run_time=2.4,
            )
        )
        for s in stations:
            set_op(s, 0.36)
        for lab in labels:
            lab.set_opacity(0.5)

        # 2) SWEEP THE CURRENT — the white pulse races the rail. Three meters move in
        #    sync: TOP counter ticks 1->9, BOTTOM bar fills 0->100%, token morphs.
        #    Stations ignite one bright peak at a time behind the pulse; the last
        #    four also drop a word of "the quick brown fox" into the bottom strip.
        self.next_section("sweep")
        pulse = Dot(radius=0.09, color=WHITE, fill_opacity=1.0)
        pulse.move_to([xs[0], rail_y, 0])
        halo = always_redraw(lambda: VGroup(*[
            Circle(radius=0.09 + 0.055 * (k + 1), stroke_color=WHITE,
                   stroke_width=2.5, stroke_opacity=0.10, fill_opacity=0)
            .move_to(pulse.get_center())
            for k in range(3)
        ]))
        lit_rail = always_redraw(lambda: Line(
            [xs[0], rail_y, 0],
            [xs[0] + (xs[-1] - xs[0]) * prog.get_value(), rail_y, 0],
            stroke_color=INK, stroke_width=2.8, stroke_opacity=0.65))

        # the sentence words start invisible; each fades in on its station's beat.
        for w in sent_words:
            w.set_opacity(0.0)
        self.add(sent_words)

        tok = token(carries[0], 0.0)
        self.add(lit_rail, halo, pulse, tok)
        for i in range(9):
            frac = i / 8.0
            new_tok = token(carries[i], frac)
            self.play(
                pulse.animate.move_to([xs[i], rail_y, 0]),
                prog.animate.set_value(frac),
                stage.animate.set_value(i + 1),
                ApplyFunction(lambda m: set_op(m, 1.0), stations[i]),
                labels[i].animate.set_opacity(1.0),
                Transform(tok, new_tok),
                run_time=0.30, rate_func=smooth,
            )
            # ignite the station + (for the last four) reveal a word.
            extra = []
            if i in word_at_station:
                w = sent_words[word_at_station.index(i)]
                extra.append(w.animate.set_opacity(1.0))
            self.play(
                Indicate(stations[i], scale_factor=1.10, color=INK),
                *extra,
                run_time=0.18,
            )

        # 3) ARRIVE & RESOLVE — pulse exits & fades; bake a static fully-lit rail.
        #    The sentence already sits in the bottom strip; bloom it with glow().
        self.next_section("resolve")
        stage.set_value(9)
        self.play(
            pulse.animate.move_to([xs[-1] + 0.55, rail_y, 0]).set_opacity(0),
            tok.animate.shift(RIGHT * 0.4).set_opacity(0),
            run_time=0.3)
        self.remove(halo, pulse, tok, lit_rail)
        full_lit = Line([xs[0], rail_y, 0], [xs[-1], rail_y, 0],
                        stroke_color=INK, stroke_width=2.8, stroke_opacity=0.65)
        counter_val.clear_updaters()
        self.add(full_lit)

        # link the TEXT station down to the finished sentence, then bloom it.
        arrow = Arrow(stations[-1].get_bottom() + DOWN * 0.02,
                      [xs[-1], rail_y - 0.55, 0],
                      stroke_width=2.2, color=INK_DIM, buff=0.05,
                      max_tip_length_to_length_ratio=0.22)
        fg = glow(sent)
        self.play(GrowArrow(arrow), run_time=0.3)
        self.play(FadeIn(fg), run_time=0.45)
        self.play(Flash(sent, color=WHITE, line_length=0.22, num_lines=20,
                        flash_radius=2.6, time_width=0.4), run_time=0.5)

        # 4) NAME THE WHOLE — the bottom progress bar gives way to the compact
        #    pipeline breadcrumb of the whole chain, beneath the sentence.
        self.next_section("name")
        prog.clear_updaters()
        pct.clear_updaters()
        chain = VGroup()
        parts = ["muscle", "sensors", "print", "read", "sounds",
                 "map", "guesses", "choose", "text"]
        for i, p in enumerate(parts):
            chain.add(mono(p, 13, INK_DIM if i in (0, len(parts) - 1) else INK_FAINT))
            if i < len(parts) - 1:
                chain.add(mono(">", 12, INK_GHOST))
        chain.arrange(RIGHT, buff=0.13).move_to([0, BAR_Y, 0])
        self.play(
            FadeOut(bar_fill), FadeOut(pct), FadeOut(bar_endlbl),
            bar_track.animate.set_opacity(0.0),
            run_time=0.4,
        )
        self.remove(bar_fill, bar_track)
        self.play(LaggedStartMap(FadeIn, chain, lag_ratio=0.05, run_time=0.8))

        # 5) POSTER HOLD — the dense final frame: TOP context line + counter(9/9),
        #    CENTER all nine stations lit on the full rail, the glowing sentence,
        #    BOTTOM breadcrumb of the whole chain. One balanced image.
        self.wait(0.6)


if __name__ == "__main__":
    pass
