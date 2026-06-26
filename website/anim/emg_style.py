"""Shared style for all emg2text Manim scenes.

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
