# REEL 10 — END. "That's the whole idea — in one breath. If you want to see how
# every piece really works — fifty short scenes are waiting under the hood."
# OPENS ON: three lines of text converging (== scene 9 close).
# The lines braid into one EMG trace that shatters into particles; the particles
# stream together to spell MYOVOX, which ignites with a single light-sweep and
# settles high in frame — leaving room below for the DOM end-card buttons.
from manim import *
from style import *
from reel_common import WHITE, motes, drift
import numpy as np
from random import uniform, seed as rseed


def outline_points(mob, n):
    subs = [m for m in mob.family_members_with_points() if len(m.points) >= 4]
    pts = []
    for m in subs:
        k = max(10, len(m.points) // 3)
        for t in np.linspace(0, 1, k, endpoint=False):
            pts.append(m.point_from_proportion(t))
    pts = np.array(pts)
    idx = np.random.RandomState(7).choice(len(pts), n, replace=len(pts) < n)
    return pts[idx]


def emg_y(x):
    burst = np.exp(-((x + 1.4) ** 2) / 2.0) + 0.8 * np.exp(-((x - 2.3) ** 2) / 1.1)
    fine = 0.16 * np.sin(7.0 * x) + 0.10 * np.sin(18.0 * x + 0.7) + 0.05 * np.sin(31.0 * x)
    return fine * (0.45 + 1.3 * burst)


class ReelEnd(Scene):
    def construct(self):
        seed()
        rseed(7)
        field = drift(motes(seed_n=3))
        self.add(field)
        N = 200
        CY = 0.7  # title sits high; DOM buttons live in the lower third

        # ---- OPEN: three converged lines (matched from scene 9) --------
        self.next_section("open")
        lines = VGroup(
            mono("\"meet me at eight\"", 22, INK),
            mono("\"send the file\"", 22, INK_DIM),
            mono("\"call me back\"", 22, INK_FAINT),
        ).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        self.add(lines)
        self.wait(0.1)

        # ---- BEAT 1: braid into one EMG trace --------------------------
        self.next_section("braid")
        xs = np.linspace(-6.2, 6.2, 260)
        wave_pts = [np.array([x, emg_y(x) + CY, 0]) for x in xs]
        wave = VMobject().set_points_smoothly(wave_pts).set_stroke(INK, 2.6)
        wglow = VGroup(*[wave.copy().set_stroke(width=6 + 3 * i, opacity=0.06)
                         for i in range(3)])
        self.play(FadeOut(lines, shift=UP * 0.2), run_time=0.4)
        scan = Dot(wave_pts[0], radius=0.07, color=WHITE)
        self.add(wglow)
        self.play(Create(wave), MoveAlongPath(scan, wave),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(scan), run_time=0.2)
        self.remove(scan)

        # ---- BEAT 2: shatter into particles ----------------------------
        self.next_section("shatter")
        wpts = [wave.point_from_proportion(t) for t in np.linspace(0, 1, N)]
        parts = VGroup(*[Dot(p, radius=0.02, color=INK).set_opacity(uniform(0.55, 0.95))
                         for p in wpts])
        self.add(parts)
        self.play(FadeOut(wave), FadeOut(wglow), run_time=0.4)
        self.remove(wave, wglow)
        self.play(*[p.animate.shift([uniform(-0.6, 0.6), uniform(-0.8, 0.8), 0])
                    .set_opacity(uniform(0.4, 0.7)) for p in parts],
                  run_time=0.7, rate_func=rate_functions.ease_out_quad)

        # ---- BEAT 3: reform as MYOVOX ----------------------------------
        self.next_section("reform")
        title = serif("MYOVOX", 96, INK)
        if title.width > 8.2:
            title.scale_to_fit_width(8.2)
        title.move_to([0, CY, 0]).set_opacity(0)
        targets = outline_points(title, N)
        self.play(LaggedStart(*[p.animate.move_to(t).set_opacity(0.95)
                                for p, t in zip(parts, targets)], lag_ratio=0.003),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)

        # ---- BEAT 4: ignite + light-sweep, then settle -----------------
        self.next_section("ignite")
        title.set_opacity(1.0)
        tglow = glow(title)
        self.add(tglow)
        self.play(FadeIn(title), parts.animate.set_opacity(0.0), run_time=0.4)
        self.remove(parts)
        self.play(Flash(title.get_center(), color=WHITE, line_length=0.36, num_lines=24,
                        flash_radius=2.4, time_width=0.5), run_time=0.5)
        self.play(ShowPassingFlash(title.copy().set_stroke(WHITE, 2.4).set_fill(opacity=0),
                                   time_width=0.5), run_time=0.65)
        tag = mono("in one breath", 22, INK_FAINT).next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(tag, shift=UP * 0.08), run_time=0.5)

        # ---- BEAT 5: breathe out and hold (buttons are DOM overlay) -----
        self.next_section("hold")
        self.play(VGroup(title, tag).animate.scale(0.97), run_time=0.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)
