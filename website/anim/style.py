"""Shared style for all myovox Manim scenes.

Strict monochrome — emphasis comes from opacity, stroke width, scale, and the
`glow` helper, never colour. Palette and fonts mirror website/src/styles/tokens.css
so rendered clips blend seamlessly into the #050505 page.
"""

from manim import *
import numpy as np
import random


def seed(n=7):
    """Deterministic renders so re-renders match (important for scrubbed video)."""
    random.seed(n)
    np.random.seed(n)


# ---- Brand palette (must match tokens.css) --------------------------------
BG = "#050505"
INK = "#f5f4f1"  # primary white
INK_DIM = "#b6b6b2"
INK_FAINT = "#828280"  # WCAG: ~5.3:1 on BG (was #6c6c69, 3.87:1)
INK_GHOST = "#606060"  # WCAG: ~3.2:1 on BG (was #3a3a38, 1.86:1)
LINE = "#2a2a28"

config.background_color = BG
# Fix fps at 30 globally but let the CLI quality flag pick resolution, so
# `-ql` => fast 480p30 iteration and `-qh` => final 1080p30 (matches encode.sh).
config.frame_rate = 30  # drop to 24 if files get too big

MONO = "JetBrains Mono"
SERIF = "Fraunces"


def mono(t, s=28, c=INK, w=NORMAL):
    return Text(t, font=MONO, font_size=s, color=c, weight=w)


def serif(t, s=52, c=INK):
    return Text(t, font=SERIF, font_size=s, color=c)


def num(t, s=90, c=INK):
    """A number as Pango Text — NEVER DecimalNumber/Integer (those need LaTeX)."""
    return Text(str(t), font=MONO, font_size=s, color=c)


def counter(tracker, fmt=lambda v: str(round(v)), s=90, c=INK, at=ORIGIN):
    """A live integer/number readout driven by a ValueTracker, LaTeX-free.
    Rebuilds a Pango Text each frame via become(); cheap enough for our scenes."""
    m = num(fmt(tracker.get_value()), s, c).move_to(at)
    m.add_updater(lambda x: x.become(num(fmt(tracker.get_value()), s, c).move_to(at)))
    return m


def dim(m, o=0.45):
    return m.set_opacity(o)


def glow(m):
    """Cheap white glow — layered translucent stroke copies behind the mobject."""
    g = VGroup(*[m.copy().set_stroke(width=6 + 3 * i, opacity=0.06) for i in range(3)])
    return VGroup(g, m)


WHITE = "#ffffff"  # the single payoff accent, shared across scenes


def learned_card(scene, term, plain, aside=None, kicker="you just learned", hold=0.8):
    """The canonical end-of-chapter lesson card.

    Every concept scene closes with this identical beat: a soft veil settles the
    scene back, a small mono kicker ("YOU JUST LEARNED") rises, then the big serif
    term — optionally with a smaller jargon aside beneath it (e.g. term "the reader",
    aside "Conformer") for the tiered naming — and a one-line plain-English gloss.
    One white flare, then a poster hold. Call once, as the final line of construct().

    Keeping the payoff in one helper is deliberate: the "name" moment must read the
    same in all ~24 chapters, and each scene stays a single call so re-renders are low
    risk. `plain` is the layman gloss; `aside` is the optional technical name.
    """
    scene.next_section("learned")

    veil = FullScreenRectangle(fill_color=BG, fill_opacity=0.95, stroke_width=0)

    kick = mono(kicker.upper(), 17, INK_FAINT)
    kick.set_stroke(width=0)
    # letter-spacing-ish: mono already reads as a label; keep it simple.
    name = serif(term, 62, INK)
    kick.next_to(name, UP, buff=0.30)

    below = name
    tag = None
    if aside:
        tag = mono(aside, 19, INK_FAINT).next_to(name, DOWN, buff=0.20)
        below = tag

    sub = mono(plain, 20, INK_DIM).next_to(below, DOWN, buff=0.34)

    group = VGroup(kick, name, sub)
    if tag is not None:
        group.add(tag)
    group.move_to(ORIGIN)

    glowing = glow(name.copy().set_color(WHITE))
    glowing.set_opacity(0.0)

    scene.play(FadeIn(veil), run_time=0.5)
    scene.add(glowing)
    scene.play(FadeIn(kick, shift=UP * 0.10), run_time=0.35)
    scene.play(FadeIn(name, shift=UP * 0.12),
               glowing.animate.set_opacity(0.32), run_time=0.5)
    if tag is not None:
        scene.play(FadeIn(tag, shift=UP * 0.06), run_time=0.30)
    scene.play(FadeIn(sub, shift=UP * 0.08), run_time=0.35)
    scene.play(Indicate(name, scale_factor=1.08, color=WHITE),
               glowing.animate.set_opacity(0.0), run_time=0.55)
    scene.remove(glowing)
    scene.wait(hold)
