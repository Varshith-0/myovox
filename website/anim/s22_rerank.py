# S22 — The chooser (LLM rerank / LIFT)
# A language model reads the candidate sentences AND the raw sounds, then picks
# the most sensible one. Qwen2.5-7B-Instruct + QLoRA (4-bit, locked, tiny adapters);
# input = ~10 candidates + detected phonemes -> one final sentence; integrity stamps.
#
# CANVAS-FILLING REBUILD — three persistent horizontal zones held the whole clip:
#   TOP strip (y~+3.2):   a left-anchored breadcrumb carried straight from S21 — a
#                         small candidate-cloud glyph + "dozens of guesses · oracle
#                         9.30% in the pool", with a thin LINE rule, and an active
#                         stage label on the right that morphs across the beats:
#                         SQUEEZE -> READ -> TIE-BREAK -> CHOOSE -> AUDIT.
#   CENTER (y~-2.0..+2.2): the star — the chooser brain squeezes + locks, then the
#                         center splits: a 10-candidate column + a bright phoneme
#                         strip both flow in; the K in the sounds physically breaks a
#                         tie between "quick" and "quiet"; the winner resolves to a
#                         serif final sentence.
#   BOTTOM ledger (y~-3.1): a persistent INTEGRITY LEDGER — a 3-row checklist that
#                         fills in left-to-right beat by beat + an audit COUNTER that
#                         ticks a ValueTracker down to a hard "0" in pure #fff
#                         ("never invents unsupported words") — the running takeaway.
# Strict monochrome (emg_style inks + pure #fff peak accent only). No LaTeX.
#
# Ground truth (§9, rerank/ training/xdecode.py):
#   Qwen2.5-7B-Instruct + QLoRA (4-bit nf4, LoRA r=16); (n-best ⊕ phonemes)->reference;
#   train-only; 2-fold cross-decoding; 6/400 duplicates quarantined (18.53/18.75);
#   verbatim-recall audit = 0.  Oracle 9.30% carried from S21.
from manim import *
from emg_style import *


WHITE = "#ffffff"


def tri(angle, c, op=1.0, s=0.08):
    """A bare triangular arrowhead (no Arrow tip mobject => no tip bug).
    Triangle points UP at angle=0; rotate by `angle` to aim it."""
    return Triangle(stroke_width=0, fill_color=c, fill_opacity=op).scale(s).rotate(angle)


def cloud_glyph(c=INK_FAINT):
    """Carried from S21: a tiny pile of stacked sentence-ticks = the candidate cloud."""
    g = VGroup()
    for k in range(4):
        w = 0.46 - 0.05 * k
        bar = RoundedRectangle(width=w, height=0.085, corner_radius=0.04,
                               stroke_width=0, fill_color=c,
                               fill_opacity=0.55 - 0.10 * k)
        bar.shift(DOWN * 0.135 * k + RIGHT * 0.05 * k)
        g.add(bar)
    return g


def lock_glyph(c=INK, s=1.0):
    """A small padlock: shackle arc + body."""
    body = RoundedRectangle(width=0.26 * s, height=0.20 * s, corner_radius=0.04 * s,
                            stroke_color=c, stroke_width=2.2, fill_color=c, fill_opacity=0.10)
    shackle = Arc(radius=0.085 * s, start_angle=0, angle=PI,
                  stroke_color=c, stroke_width=2.2)
    shackle.next_to(body, UP, buff=-0.02 * s)
    return VGroup(shackle, body)


class Chooser(Scene):
    def construct(self):
        seed()

        # ============================================================== #
        #  PERSISTENT FRAME — three zones fade in together               #
        # ============================================================== #
        self.next_section("frame")

        # ---- TOP strip: breadcrumb carried from S21 (the pooled cloud) ----
        glyph = cloud_glyph(INK_FAINT)
        crumb = mono("dozens of guesses · oracle 9.30% in the pool", 19, INK_FAINT)
        crumb_grp = VGroup(glyph, crumb).arrange(RIGHT, buff=0.30)
        crumb_grp.to_edge(LEFT, buff=0.7).to_edge(UP, buff=0.50)

        stage = mono("SQUEEZE", 24, INK_DIM, w=BOLD).to_edge(RIGHT, buff=0.8)
        stage.set_y(crumb_grp.get_y())
        rule = Line(LEFT * 6.6, RIGHT * 6.6, stroke_color=LINE, stroke_width=1.2)
        rule.set_y(crumb_grp.get_y() - 0.40)

        # ---- BOTTOM strip: the integrity ledger skeleton (lives all clip) ----
        LY = -3.02              # ledger baseline
        led_title = mono("integrity ledger", 15, INK_GHOST)
        led_title.move_to([-6.55 + 0.0, LY + 0.62, 0]).align_to(LEFT * 6.55, LEFT)

        # three empty checklist rows on the LEFT half of the bottom strip
        check_texts = [
            "trained on training data only",
            "cross-decoded  →  realistically messy guesses",
            "6 duplicate test sentences quarantined   18.53 / 18.75",
        ]
        check_rows = VGroup()
        for t in check_texts:
            box = mono("[ ]", 16, INK_GHOST)
            txt = mono(t, 15, INK_GHOST)
            check_rows.add(VGroup(box, txt).arrange(RIGHT, buff=0.22))
        check_rows.arrange(DOWN, aligned_edge=LEFT, buff=0.165)
        check_rows.move_to([-3.55, LY - 0.10, 0])
        check_rows.align_to(LEFT * 6.55, LEFT)

        # the audit line + counter on the RIGHT half of the bottom strip
        audit_lbl = mono("verbatim-recall audit", 16, INK_FAINT)
        audit_dots = mono("counting…", 16, INK_GHOST)
        audit_grp = VGroup(audit_lbl, audit_dots).arrange(RIGHT, buff=0.26)
        audit_grp.move_to([3.9, LY + 0.34, 0])
        audit_sub = mono("never invents unsupported words", 14, INK_GHOST)
        audit_sub.next_to(audit_grp, DOWN, buff=0.16).align_to(audit_grp, LEFT)

        led_rule = Line(LEFT * 6.6, RIGHT * 6.6, stroke_color=LINE, stroke_width=1.0)
        led_rule.set_y(LY + 0.86)

        self.play(
            FadeIn(crumb_grp, shift=DOWN * 0.16),
            FadeIn(stage, shift=DOWN * 0.16),
            Create(rule),
            Create(led_rule),
            FadeIn(led_title),
            LaggedStartMap(FadeIn, check_rows, lag_ratio=0.15, run_time=0.55),
            FadeIn(audit_grp), FadeIn(audit_sub),
            run_time=0.6,
        )

        CY = 0.45   # vertical centre of the center mechanism zone

        # ============================================================== #
        #  BEAT 1 — SQUEEZE: a 7-billion-pattern model, 4-bit + locked    #
        # ============================================================== #
        self.next_section("squeeze")
        brain = RoundedRectangle(
            width=3.3, height=2.05, corner_radius=0.18,
            stroke_color=INK, stroke_width=2.2, fill_color=INK, fill_opacity=0.04,
        ).move_to([0, CY, 0])
        name = mono("Qwen2.5-7B", 26, INK).move_to(brain.get_center() + UP * 0.30)
        sub = mono("language model", 17, INK_FAINT).next_to(name, DOWN, buff=0.13)
        scale_cue = mono("7 billion learned patterns", 15, INK_GHOST).next_to(sub, DOWN, buff=0.15)

        self.play(Create(brain), FadeIn(name, shift=UP * 0.1), FadeIn(sub),
                  FadeIn(scale_cue), run_time=0.5)

        # QLoRA: squeeze to 4-bit, lock the model, train tiny add-on adapters.
        qlora = mono("QLoRA", 18, INK_DIM, w=BOLD).next_to(brain, UP, buff=0.52)
        lock = mono("4-bit   +   locked   +   tiny adapters", 16, INK_FAINT).next_to(qlora, DOWN, buff=0.13)
        self.play(FadeIn(qlora, shift=DOWN * 0.08), Write(lock), run_time=0.45)

        # squeeze pulse: the whole model compresses as "4-bit + locked" lands,
        # a lock-glyph stamps onto it, then it eases back slightly smaller.
        brain_grp = VGroup(brain, name, sub, scale_cue)
        padlock = lock_glyph(INK, 1.0).move_to(brain.get_center())
        padlock.set_opacity(0)
        self.play(
            brain_grp.animate.scale(0.78),
            Indicate(lock, scale_factor=1.05, color=INK),
            run_time=0.4,
        )
        # the lock stamp lands on the now-compressed model, then it eases back up.
        padlock.move_to(brain.get_right() + LEFT * 0.40 + DOWN * 0.50).set_opacity(1)
        fits = mono("so it fits on one modest GPU", 15, INK_FAINT)
        self.play(
            GrowFromCenter(padlock),
            Flash(padlock, color=INK, line_length=0.10, num_lines=8, flash_radius=0.28),
            brain_grp.animate.scale(0.85 / 0.78),
            run_time=0.4,
        )
        padlock.scale(0.85 / 0.78).move_to(brain.get_center() + RIGHT * 1.08 + DOWN * 0.62)
        fits.next_to(brain_grp, DOWN, buff=0.32)
        self.play(FadeIn(fits, shift=UP * 0.08), run_time=0.3)

        # ============================================================== #
        #  BEAT 2 — READ: ~10 candidates + detected sounds flow in        #
        # ============================================================== #
        self.next_section("read")
        stage2 = mono("READ", 24, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage2), run_time=0.32)
        stage = stage2

        # slide the compact chooser to the right-of-center anchor; drop QLoRA labels.
        chooser = VGroup(brain, name, sub)
        scale_cue_grp = scale_cue
        self.play(
            VGroup(chooser, padlock).animate.scale(0.92).move_to([3.45, CY, 0]),
            FadeOut(qlora), FadeOut(lock), FadeOut(fits), FadeOut(scale_cue_grp),
            run_time=0.5,
        )
        # re-anchor padlock neatly relative to the moved brain
        padlock.next_to(brain, RIGHT, buff=-0.05).align_to(brain, DOWN).shift(UP * 0.18 + LEFT * 0.16)
        chooser_tag = mono("the chooser", 15, INK_FAINT).next_to(brain, UP, buff=0.20)
        self.add(chooser_tag)

        # ---- LEFT inputs: candidate column (top) + phoneme strip (bottom) ----
        # two look-alikes bright on top; the rest ghosted; "...10 guesses".
        cands_txt = [
            "the quick brown fox",
            "the quiet brown fox",
            "the quick brown box",
            "a quick brown fox",
            "the quick brow fox",
        ]
        cand_lines = VGroup(*[
            mono(c, 17, INK if i < 2 else INK_GHOST) for i, c in enumerate(cands_txt)
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.155)
        more = mono("... 10 guesses", 14, INK_GHOST)
        more.next_to(cand_lines, DOWN, aligned_edge=LEFT, buff=0.16)
        cand_box = VGroup(cand_lines, more)
        cand_box.move_to([-4.15, CY + 0.88, 0])
        cand_label = mono("candidates", 16, INK_FAINT).next_to(cand_box, UP, aligned_edge=LEFT, buff=0.18)

        phon = mono("DH  AH  K  W  IH  K  ...", 18, INK).move_to([-4.15, CY - 1.55, 0])
        phon_label = mono("detected sounds", 16, INK_FAINT)
        phon_label.next_to(phon, UP, aligned_edge=LEFT, buff=0.16)

        self.play(FadeIn(cand_label),
                  LaggedStartMap(FadeIn, cand_lines, lag_ratio=0.10, run_time=0.5))
        self.play(FadeIn(more), FadeIn(phon_label), Write(phon), run_time=0.45)

        # arrows: both input clusters flow into the chooser (heads aim into brain).
        a1_start = cand_box.get_right() + RIGHT * 0.20
        a1_end = brain.get_left() + UP * 0.42 + LEFT * 0.14
        a1 = Line(a1_start, a1_end, stroke_width=2.0, color=INK_FAINT)
        a2_start = VGroup(phon, phon_label).get_right() + RIGHT * 0.20
        a2_end = brain.get_left() + DOWN * 0.42 + LEFT * 0.14
        a2 = Line(a2_start, a2_end, stroke_width=2.0, color=INK_FAINT)
        # head points along the line direction (Triangle points up at 0 -> rotate by angle - PI/2)
        a1h = tri(a1.get_angle() - PI / 2, INK_FAINT, 1.0, 0.075).move_to(a1.get_end())
        a2h = tri(a2.get_angle() - PI / 2, INK_FAINT, 1.0, 0.075).move_to(a2.get_end())
        self.play(Create(a1), Create(a2), FadeIn(a1h), FadeIn(a2h), run_time=0.45)

        # traveling pulses arrive together -> the brain reads them as one.
        p1 = Dot(color=INK, radius=0.055).move_to(a1.get_start())
        p2 = Dot(color=INK, radius=0.055).move_to(a2.get_start())
        self.add(p1, p2)
        self.play(p1.animate.move_to(a1.get_end()), p2.animate.move_to(a2.get_end()),
                  run_time=0.45, rate_func=linear)
        self.remove(p1, p2)
        read_lbl = mono("it reads the guesses and the sounds together", 16, INK_FAINT)
        read_lbl.move_to([0.0, CY - 2.05, 0])
        self.play(Indicate(brain, scale_factor=1.06, color=INK),
                  FadeIn(read_lbl), run_time=0.45)

        # --- TICK bottom checklist row 1 -> [x] trained on training data only ---
        self._tick(check_rows[0])

        # ============================================================== #
        #  BEAT 3 — TIE-BREAK: the sounds settle quick vs quiet (the wow) #
        # ============================================================== #
        self.next_section("tiebreak")
        stage3 = mono("TIE-BREAK", 24, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage3), FadeOut(read_lbl), run_time=0.32)
        stage = stage3

        # dim candidates 3-5 + "...10 guesses" to ghost; only the look-alikes stay.
        self.play(
            cand_lines[2].animate.set_opacity(0.14),
            cand_lines[3].animate.set_opacity(0.14),
            cand_lines[4].animate.set_opacity(0.14),
            more.animate.set_opacity(0.10),
            run_time=0.35,
        )
        # underline the disputed 2nd word in each look-alike (quick / quiet).
        u0 = Line(ORIGIN, RIGHT, stroke_color=INK, stroke_width=2.2).set_width(0.92)
        u0.next_to(cand_lines[0], DOWN, buff=0.04).align_to(cand_lines[0], LEFT).shift(RIGHT * 0.80)
        u1 = u0.copy().set_stroke(INK_FAINT)
        u1.next_to(cand_lines[1], DOWN, buff=0.04).align_to(cand_lines[1], LEFT).shift(RIGHT * 0.80)
        tie_q = mono("two look-alike guesses", 15, INK_FAINT).move_to([-4.15, CY - 0.30, 0])
        self.play(Create(u0), Create(u1), FadeIn(tie_q), run_time=0.4)

        # the deciding evidence: the hard K in the detected sounds.
        kmark = mono("K = hard 'k', not soft 't'", 15, INK)
        kmark.next_to(phon, DOWN, aligned_edge=LEFT, buff=0.22)
        self.play(Indicate(phon, scale_factor=1.04, color=INK),
                  FadeIn(kmark, shift=UP * 0.12), run_time=0.45)

        # the single bright evidence Dot launches OUT of the K, arcs UP to "quick".
        evid = Dot(color=WHITE, radius=0.07).move_to(phon.get_center() + LEFT * 0.55)
        evid_g = glow(evid)
        self.add(evid_g)
        up_path = ArcBetweenPoints(
            phon.get_center() + LEFT * 0.55,
            cand_lines[0].get_left() + LEFT * 0.18,
            angle=-PI / 2.4,
        )
        self.play(MoveAlongPath(evid_g, up_path), run_time=0.6, rate_func=smooth)

        # the instant it lands: "quick" ignites to pure #fff, "quiet" dims to a ghost.
        win_mark = mono("matches the sounds", 14, WHITE).next_to(cand_lines[0], RIGHT, buff=0.40)
        self.play(
            cand_lines[0].animate.set_color(WHITE).set_opacity(1.0),
            u0.animate.set_stroke(WHITE, width=3.2),
            FadeIn(win_mark, shift=LEFT * 0.1),
            cand_lines[1].animate.set_opacity(0.16),
            u1.animate.set_opacity(0.14),
            FadeOut(evid_g),
            run_time=0.45,
        )
        self.play(Circumscribe(cand_lines[0], color=WHITE, stroke_width=2.4,
                               buff=0.12, time_width=0.5), run_time=0.5)

        # --- TICK bottom checklist row 2 -> [x] cross-decoded -> messy guesses ---
        self._tick(check_rows[1])

        # ============================================================== #
        #  BEAT 4 — CHOOSE: the winner resolves to one final sentence     #
        # ============================================================== #
        self.next_section("choose")
        stage4 = mono("CHOOSE", 24, INK_DIM, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage4), run_time=0.32)
        stage = stage4

        # output line drops from the brain, arrowhead aiming down.
        out_arrow = Line(brain.get_bottom() + DOWN * 0.06, brain.get_bottom() + DOWN * 0.78,
                         stroke_width=2.4, color=INK_DIM)
        out_h = tri(PI, INK_DIM, 1.0, 0.10).move_to(out_arrow.get_end())
        # the final sentence resolves below-center, clear of the left input clutter
        # and tucked under the brain's output, well above the bottom ledger.
        final = serif("the quick brown fox", 32, INK)
        final.move_to([2.0, CY - 1.85, 0])
        final_g = glow(final)
        self.play(Create(out_arrow), FadeIn(out_h), run_time=0.32)
        # the chosen candidate morphs down into the serif final sentence.
        self.play(TransformFromCopy(cand_lines[0], final), run_time=0.6)
        self.add(final_g)
        self.play(Flash(final, color=WHITE, line_length=0.18, num_lines=14,
                        flash_radius=1.7, time_width=0.4), run_time=0.45)
        tie = mono("the sounds break ties between look-alike guesses", 15, INK_FAINT)
        tie.next_to(final_g, DOWN, buff=0.22)
        self.play(FadeIn(tie), run_time=0.3)

        # --- TICK bottom checklist row 3 -> [x] 6 duplicates quarantined ---
        self._tick(check_rows[2])

        # ============================================================== #
        #  BEAT 5 — AUDIT + poster: the audit ticks to a hard 0           #
        # ============================================================== #
        self.next_section("audit")
        stage5 = mono("AUDIT", 24, INK, w=BOLD).move_to(stage).align_to(stage, RIGHT)
        self.play(ReplacementTransform(stage, stage5), run_time=0.32)
        stage = stage5

        # fade the input clutter; keep the brain (small, dimmed, upper) + final sentence.
        keep_brain = VGroup(brain, name, sub, padlock)
        self.play(
            FadeOut(cand_box), FadeOut(cand_label),
            FadeOut(phon), FadeOut(phon_label),
            FadeOut(u0), FadeOut(u1), FadeOut(tie_q), FadeOut(kmark),
            FadeOut(win_mark), FadeOut(chooser_tag),
            FadeOut(a1), FadeOut(a2), FadeOut(a1h), FadeOut(a2h),
            FadeOut(out_arrow), FadeOut(out_h), FadeOut(tie),
            keep_brain.animate.scale(0.62).move_to([0, CY + 1.55, 0]).set_opacity(0.55),
            VGroup(final_g, final).animate.move_to([0, CY - 0.05, 0]),
            run_time=0.6,
        )
        small_tag = mono("the chooser", 13, INK_GHOST).next_to(keep_brain, DOWN, buff=0.16)
        self.add(small_tag)

        # bring the bottom ledger forward: the audit COUNTER ticks down to a hard 0.
        # Build a fresh bright audit line in place of the faint skeleton. We anchor
        # the live digit at a FIXED world point next to the "=" (the counter() helper
        # forces its own move_to each frame, so we drive a manual updater instead and
        # keep the digit LEFT-aligned so it doesn't wobble as it ticks).
        led_anchor = audit_grp.get_left()                 # left edge of the old line
        new_audit_lbl = mono("verbatim-recall audit", 16, INK)
        new_audit_lbl.move_to(led_anchor, aligned_edge=LEFT)
        eq = mono("=", 18, INK_FAINT).next_to(new_audit_lbl, RIGHT, buff=0.24)
        digit_x = eq.get_right()[0] + 0.30                # left edge for the digit

        audit_val = ValueTracker(7.0)   # ticks 7 -> 0 (counts down the candidate "misses")
        cnt = num("7", 34, INK)
        cnt.move_to([digit_x, eq.get_y(), 0], aligned_edge=LEFT)
        cnt.add_updater(lambda m: m.become(
            num(str(round(audit_val.get_value())), 34, INK)
            .move_to([digit_x, eq.get_y(), 0], aligned_edge=LEFT)))

        self.play(FadeOut(audit_grp), FadeIn(new_audit_lbl), FadeIn(eq), run_time=0.3)
        self.add(cnt)
        self.play(audit_val.animate.set_value(0.0), run_time=0.85, rate_func=smooth)
        cnt.clear_updaters()
        # snap the final 0 to pure #fff and glow it (the only white accent of the beat)
        zero = num("0", 34, WHITE).move_to([digit_x, eq.get_y(), 0], aligned_edge=LEFT)
        zero_g = glow(zero)
        self.remove(cnt)
        self.add(zero_g)
        audit_row = VGroup(new_audit_lbl, eq, zero)
        new_audit_sub = mono("never invents unsupported words", 14, INK_DIM)
        new_audit_sub.next_to(new_audit_lbl, DOWN, buff=0.16).align_to(new_audit_lbl, LEFT)
        self.play(FadeOut(audit_sub), FadeIn(new_audit_sub),
                  Flash(zero, color=WHITE, line_length=0.12, num_lines=10,
                        flash_radius=0.30), run_time=0.45)
        self.play(Circumscribe(audit_row, color=WHITE,
                               stroke_width=2.0, buff=0.16, time_width=0.5), run_time=0.5)

        # final serif punchline, balanced beneath the chosen sentence.
        closing = serif("it reasons, it doesn't recite", 24, INK)
        closing.move_to([0, CY - 1.15, 0])
        self.play(Write(closing), run_time=0.5)

        # poster hold — top breadcrumb + AUDIT, center the chosen sentence under the
        # small chooser, bottom the completed 4-line ledger with audit = 0 glowing.
        self.wait(0.6)

    # -------------------------------------------------------------------- #
    def _tick(self, row):
        """Flip a ledger checklist row from a faint '[ ]' to a lit '[x]' and brighten
        its text — a left-to-right checklist that fills in beat by beat."""
        box, txt = row[0], row[1]
        new_box = mono("[x]", 16, INK).move_to(box.get_center()).align_to(box, LEFT)
        self.play(
            ReplacementTransform(box, new_box),
            txt.animate.set_color(INK_DIM),
            run_time=0.32,
        )
        row.submobjects[0] = new_box


if __name__ == "__main__":
    pass
