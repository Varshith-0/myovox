"""Shared geometry + motifs for the "In One Breath" scenes.

One Breath is ten short clips that must read as ONE continuous film: every scene
OPENS on the exact composition the previous scene CLOSED on (a "match cut"). The
only way to guarantee that is to build those shared compositions from one place —
this module — so identical seeds and coordinates produce pixel-identical starts
and ends. Strict monochrome, same inks/fonts as style.py.

Motion rules for smoothness (enforced by convention in every scene):
  * easing is always smooth / ease_in_out_sine — never bounce, elastic, overshoot
  * something is always in slow continuous motion (a drift, a breath, a crawl) so
    no scrubbed frame is ever dead
  * emphasis comes from opacity, stroke width, scale — never colour
"""

from manim import *
from style import *
import numpy as np

WHITE = "#ffffff"


# ---------------------------------------------------------------------------
# EMG-like traces
# ---------------------------------------------------------------------------
def trace(x0, x1, y, amp, n=240, freq=2.0, phase=0.0, jag=0.0, seed_n=None):
    """A smooth wiggly EMG-like line from x0..x1, centred on y, peak amp."""
    if seed_n is not None:
        rng = np.random.RandomState(seed_n)
    else:
        rng = np.random
    xs = np.linspace(x0, x1, n)
    t = np.linspace(0, 1, n)
    w = (np.sin(2 * PI * freq * t + phase)
         + 0.5 * np.sin(2 * PI * freq * 2.3 * t + phase * 1.7)
         + 0.3 * np.sin(2 * PI * freq * 4.1 * t + phase * 0.6))
    if jag:
        w = w + jag * rng.uniform(-1, 1, n)
    w = w / (np.max(np.abs(w)) + 1e-9)
    pts = np.array([[xs[i], y + amp * w[i], 0] for i in range(n)])
    return VMobject().set_points_smoothly(pts)


def waterfall(n=31, x0=-6.0, x1=6.0, ytop=2.35, ybot=-2.35, amp=0.11,
              stroke=1.3, op=0.6):
    """The full 31-channel stack — identical every time (scene 2 end == scene 3 start)."""
    ys = np.linspace(ytop, ybot, n)
    grp = VGroup()
    for i, y in enumerate(ys):
        tr = trace(x0, x1, y, amp, freq=1.35 + 0.11 * i, phase=i * 0.7,
                   jag=0.05, seed_n=1000 + i)
        tr.set_stroke(INK, width=stroke, opacity=op)
        grp.add(tr)
    return grp


# ---------------------------------------------------------------------------
# The head + the 31-sensor array (mirrors scenes 05/06 of the deep dive, which
# are the "known good" reference). Same head geometry as 06-signal.py so the
# sensors land in exactly the right places.  (scene 1 end == scene 2 start)
# ---------------------------------------------------------------------------
HEAD_C = [0.0, 0.6, 0]


def head_outline(stroke=INK, w=2.2):
    head = Ellipse(width=3.2, height=4.2).set_stroke(stroke, w).move_to(HEAD_C)
    neck = VGroup(Line([-0.6, -1.4, 0], [-0.75, -2.7, 0]),
                  Line([0.6, -1.4, 0], [0.75, -2.7, 0])).set_stroke(stroke, w)
    shoulders = ArcBetweenPoints([-2.4, -3.05, 0], [2.4, -3.05, 0],
                                 angle=-0.5).set_stroke(stroke, w)
    return VGroup(head, neck, shoulders)


def face_features():
    """Eyes + nose so the head reads as a face in the opening (scene 1 & 2)."""
    eye_l = Arc(0.2, PI, PI, arc_center=[-0.55, 1.15, 0]).set_stroke(INK_DIM, 2)
    eye_r = Arc(0.2, PI, PI, arc_center=[0.55, 1.15, 0]).set_stroke(INK_DIM, 2)
    nose = VMobject().set_points_as_corners(
        [[0, 0.95, 0], [-0.13, 0.25, 0], [0.1, 0.25, 0]]).set_stroke(INK_DIM, 2)
    return VGroup(eye_l, eye_r, nose)


def mouth_closed():
    return Line([-0.34, -0.25, 0], [0.34, -0.25, 0]).set_stroke(INK, 2.4)


def mouth_open(h=0.34, w=0.5):
    return Ellipse(width=w, height=h).set_stroke(INK, 2.4).set_fill(BG, 1.0).move_to([0, -0.3, 0])


# Muscle sites that fire as the mouth silently articulates (scene 1). White
# flashes only — monochrome, like the fibre flashes in 06-signal.py.
MUSCLE_SITES = [[-0.95, 0.7, 0], [0.95, 0.7, 0], [-0.7, 0.05, 0],
                [0.7, 0.05, 0], [0.0, -1.85, 0]]


def grid31_positions():
    """The hand-placed 31-sensor layout from 06-signal.py — 4·5·5·5·4·4·2·2."""
    rows = [(0.4, np.linspace(-1.0, 1.0, 4)), (0.0, np.linspace(-1.3, 1.3, 5)),
            (-0.4, np.linspace(-1.3, 1.3, 5)), (-0.8, np.linspace(-1.2, 1.2, 5)),
            (-1.2, np.linspace(-0.95, 0.95, 4)), (-1.6, np.linspace(-0.8, 0.8, 4)),
            (-2.0, np.linspace(-0.4, 0.4, 2)), (-2.4, np.linspace(-0.4, 0.4, 2))]
    return [[x, y, 0] for y, xs in rows for x in xs]


def sensor_dot(p, r=0.1, fill=0.5):
    return Circle(r, stroke_color=INK, stroke_width=1.8).set_fill("#ffffff", fill).move_to(p)


def sensor_array(fill=0.5):
    return VGroup(*[sensor_dot(p, fill=fill) for p in grid31_positions()])


# ---------------------------------------------------------------------------
# Covariance "fingerprint" tile — a small symmetric grid (scene 3 & 4)
# ---------------------------------------------------------------------------
def fingerprint_tile(k=9, size=0.9, at=ORIGIN, seed_n=7, op=1.0):
    """A k×k symmetric heat tile: One Breath's stand-in for the 31×31 covariance."""
    rng = np.random.RandomState(seed_n)
    base = rng.uniform(0, 1, (k, k))
    m = (base + base.T) / 2
    np.fill_diagonal(m, 1.0)
    cell = size / k
    tile = VGroup()
    for i in range(k):
        for j in range(k):
            v = m[i, j]
            sq = Square(side_length=cell, stroke_width=0,
                        fill_color=INK, fill_opacity=(0.08 + 0.9 * v) * op)
            sq.move_to([at[0] + (j - k / 2 + 0.5) * cell,
                        at[1] + (k / 2 - i - 0.5) * cell, 0])
            tile.add(sq)
    return tile


def filmstrip(count=7, at=ORIGIN, tile_size=0.62, gap=0.12, seed0=20, op=1.0):
    """A row of fingerprint tiles — the filmstrip (scene 3 end == scene 4 start)."""
    strip = VGroup()
    step = tile_size + gap
    for c in range(count):
        t = fingerprint_tile(k=8, size=tile_size,
                              at=[at[0] + (c - count / 2 + 0.5) * step, at[1], 0],
                              seed_n=seed0 + c, op=op)
        frame = Square(side_length=tile_size, stroke_color=INK_GHOST,
                       stroke_width=1.0, fill_opacity=0).move_to(t.get_center())
        strip.add(VGroup(t, frame))
    return strip


# The one canonical filmstrip pose shared by scene 3's close and scene 4's open,
# so the match cut is exact. Built from one place → identical tiles + geometry.
def one_breath_filmstrip():
    return filmstrip(count=7, at=[0, -0.7, 0], tile_size=0.8, gap=0.16, seed0=20)


# ---------------------------------------------------------------------------
# The reader: a compact box of dials (scene 4)
# ---------------------------------------------------------------------------
def dial(at, angle, r=0.12, c=INK_DIM):
    face = Circle(radius=r, stroke_color=INK_GHOST, stroke_width=1.4).move_to(at)
    hand = Line(at, [at[0] + r * np.cos(angle), at[1] + r * np.sin(angle), 0]
                ).set_stroke(c, 2.0)
    return VGroup(face, hand)


def dial_box(at=ORIGIN, w=2.6, h=2.0, cols=5, rows=4, seed_n=7):
    rng = np.random.RandomState(seed_n)
    box = RoundedRectangle(width=w, height=h, corner_radius=0.12,
                           stroke_color=INK, stroke_width=2.0,
                           fill_color=BG, fill_opacity=1.0).move_to(at)
    dials = VGroup()
    for r in range(rows):
        for c in range(cols):
            x = at[0] + (c - cols / 2 + 0.5) * (w * 0.82 / cols)
            y = at[1] + (r - rows / 2 + 0.5) * (h * 0.78 / rows)
            dials.add(dial([x, y, 0], rng.uniform(0, TAU)))
    return box, dials


def phoneme_row(syms=("K", "AE", "T"), at=ORIGIN, s=34, buff=0.5, c=INK):
    row = VGroup(*[mono(x, s, c) for x in syms]).arrange(RIGHT, buff=buff).move_to(at)
    return row


# ---------------------------------------------------------------------------
# Ambient mote field — keeps every scene alive (never a dead frame)
# ---------------------------------------------------------------------------
def motes(n=54, spread_x=6.8, spread_y=3.7, seed_n=7):
    rng = np.random.RandomState(seed_n)
    g = VGroup()
    for _ in range(n):
        g.add(Dot([rng.uniform(-spread_x, spread_x), rng.uniform(-spread_y, spread_y), 0],
                  radius=rng.uniform(0.006, 0.026), color=INK
                  ).set_opacity(rng.uniform(0.04, 0.26)))
    return g


def drift(group, rate=0.05):
    """Attach a slow rotation updater so a field is never static."""
    group.add_updater(lambda m, dt: m.rotate(rate * dt, about_point=ORIGIN))
    return group
