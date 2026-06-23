/**
 * Narration metadata for the Story page.
 *
 * The spoken script itself lives in {@link ./narration.json} (id → text) — the
 * single source of truth shared with the offline generator
 * (`scripts/narrate.py`, which renders one `public/anim/<id>.mp3` per stage with
 * edge-tts). At runtime we only need to know *which* stages carry a voice clip;
 * the audio is a static asset, exactly like the Manim `.mp4`s beside it.
 *
 * Every stage carries a clip — including the final `end` card, which speaks a
 * short "The end."
 */
import { STAGES } from './stages'

/** Stage ids that have a narration clip, in story order. */
export const NARRATED_IDS: readonly string[] = STAGES.map((s) => s.id)

const NARRATED = new Set(NARRATED_IDS)

/** Does this stage carry a narration clip? */
export const hasNarration = (id: string): boolean => NARRATED.has(id)
