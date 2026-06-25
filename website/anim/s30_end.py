# S30 — THE END — the finale.
# One last decode: a glowing EMG signal traces across the dark, shatters into a
# cloud of particles, and those particles stream together to spell THE END — which
# ignites with a flash and a single light-sweep along the letters, then holds.
# Thematically it is the project itself, one final time: signal -> particles -> text.
#
# ART DIRECTION — full-canvas, cinematic, NOT the ledger style of the earlier
# scenes. Strict monochrome; depth from opacity/size; the single pure-#fff accents
# are the ignition flash and the shimmer along the letters.
#
# Six beats — one spoken sentence each (re-paced; same four visuals):
#   1 trace      "watch a whisper of muscle turn into light"   (2.27s)
#   2 shatter    "it breaks apart ... a scatter of tiny pieces" (3.25s)
#   3 reform     "those pieces find each other and become words" (3.45s)
#   4 ignite     "from silent muscle to readable text"          (1.55s)
#   5 hold       "that was the whole idea"                       (0.93s)
#   6 settle     "the end"                                       (0.60s)
from manim import *
from emg_style import *
import numpy as np
from random import uniform, seed as rseed

WHITE = "#ffffff"


def outline_points(mob, n):
    """Sample ~n points evenly along the outline of a text mobject's glyphs."""
    subs = [m for m in mob.family_members_with_points() if len(m.points) >= 4]
    pts = []
    for m in subs:
        k = max(10, len(m.points) // 3)
        for t in np.linspace(0, 1, k, endpoint=False):
            pts.append(m.point_from_proportion(t))
    pts = np.array(pts)
    idx = np.random.choice(len(pts), n, replace=len(pts) < n)
    return pts[idx]


def emg_y(x):
    """A plausible bursty bio-signal: low ripple with two activation bursts."""
    burst = np.exp(-((x + 1.4) ** 2) / 2.0) + 0.8 * np.exp(-((x - 2.3) ** 2) / 1.1)
    fine = 0.16 * np.sin(7.0 * x) + 0.10 * np.sin(18.0 * x + 0.7) + 0.05 * np.sin(31.0 * x)
    return fine * (0.45 + 1.3 * burst)


class End(Scene):
    def construct(self):
        seed()
        rseed(7)
        N = 210
        CY = 0.25  # vertical centre of the title / signal

        # ---- the hidden target text + its outline sample points --------
        end = serif("THE END", 110, INK)
        if end.width > 9.8:
            end.scale_to_fit_width(9.8)
        end.move_to([0, CY, 0]).set_opacity(0)
        targets = outline_points(end, N)

        # ---- atmosphere: a slowly rotating mote field (ambient calm) ----
        bg = VGroup()
        for _ in range(72):
            bg.add(Dot([uniform(-6.8, 6.8), uniform(-3.7, 3.7), 0],
                       radius=uniform(0.008, 0.03), color=INK).set_opacity(uniform(0.05, 0.32)))
        self.play(LaggedStart(*[FadeIn(d) for d in bg], lag_ratio=0.008), run_time=0.9)
        bg.add_updater(lambda m, dt: m.rotate(0.05 * dt, about_point=ORIGIN))

        # ===============================================================
        # BEAT 1 (2.27s) — "watch a whisper of muscle turn into light"
        # the last signal traces across, glowing, a scan dot riding its crest
        # ===============================================================
        self.next_section("trace")
        xs = np.linspace(-6.2, 6.2, 260)
        wave_pts = [np.array([x, emg_y(x) + CY, 0]) for x in xs]
        wave = VMobject().set_points_smoothly(wave_pts).set_stroke(INK, 2.6)
        # explicit glow copies so we can remove them for certain later.
        wglow = VGroup(*[wave.copy().set_stroke(width=6 + 3 * i, opacity=0.06) for i in range(3)])
        scan = Dot(wave_pts[0], radius=0.07, color=WHITE)
        self.add(wglow)
        self.play(Create(wave), MoveAlongPath(scan, wave),
                  run_time=1.7, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(scan), run_time=0.25)
        self.remove(scan)
        self.wait(0.3)

        # ===============================================================
        # BEAT 2 (3.25s) — "it breaks apart ... a scatter of tiny pieces"
        # the wave shatters and scatters outward into a faint particle cloud
        # ===============================================================
        self.next_section("shatter")
        wpts = [wave.point_from_proportion(t) for t in np.linspace(0, 1, N)]
        parts = VGroup(*[Dot(p, radius=0.02, color=INK).set_opacity(uniform(0.55, 0.95))
                         for p in wpts])
        self.add(parts)
        self.play(FadeOut(wave), FadeOut(wglow), run_time=0.5)
        self.remove(wave, wglow)
        # a slow outward scatter — the signal breaking into pieces
        self.play(*[p.animate.shift([uniform(-0.6, 0.6), uniform(-0.85, 0.85), 0])
                    .set_opacity(uniform(0.4, 0.7))
                    for p in parts],
                  run_time=1.5, rate_func=rate_functions.ease_out_quad)
        self.wait(1.1)

        # ===============================================================
        # BEAT 3 (3.45s) — "those pieces find each other and become words"
        # particles stream together and settle onto the THE END letterforms
        # ===============================================================
        self.next_section("reform")
        self.play(
            LaggedStart(*[p.animate.move_to(t).set_opacity(0.95)
                          for p, t in zip(parts, targets)], lag_ratio=0.0032),
            run_time=2.9, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # ===============================================================
        # BEAT 4 (1.55s) — "from silent muscle to readable text"
        # THE END ignites: the letters reveal, flash, then a single light-sweep
        # ===============================================================
        self.next_section("ignite")
        end.set_opacity(1.0)
        end_g = glow(end)
        self.add(end_g)
        self.play(FadeIn(end), parts.animate.set_opacity(0.0), run_time=0.4)
        self.remove(parts)
        self.play(Flash(end.get_center(), color=WHITE, line_length=0.42, num_lines=26,
                        flash_radius=2.6, time_width=0.5), run_time=0.5)
        self.play(ShowPassingFlash(end.copy().set_stroke(WHITE, 2.6).set_fill(opacity=0),
                                   time_width=0.5), run_time=0.65)

        # ===============================================================
        # BEAT 5 (0.93s) — "that was the whole idea"
        # the sweep finishes; THE END holds steady and bright
        # ===============================================================
        self.next_section("hold")
        self.wait(0.93)

        # ===============================================================
        # BEAT 6 (0.6s) — "the end"
        # everything settles; the title rests alone on the dark, motes drifting
        # ===============================================================
        self.next_section("settle")
        self.wait(0.6)


if __name__ == "__main__":
    pass
