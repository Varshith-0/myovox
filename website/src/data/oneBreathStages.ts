/**
 * "In One Breath". Ten short scenes that tell the whole Myovox story
 * in ~100 seconds, built from the SAME machinery as the fifty-scene deep dive
 * ({@link ./stages.ts}): each is a scrubbed Manim clip with a matching narration
 * clip. The two lists are interchangeable because both are `Stage[]`; the active
 * one is supplied to the story components through {@link StagesProvider}.
 *
 * Every scene OPENS on the composition the previous scene CLOSED on (a match cut),
 * so scrubbing through One Breath reads as one continuous film.
 */
import type { Stage } from './stages'

/** A One Breath Manim stage — same shape as the deep dive's `act2`, top caption. */
function oneBreath(id: string, rail: string, caption: string, alt: string, sub?: string): Stage {
  return {
    id,
    rail,
    caption,
    sub,
    media: {
      chapter: 'one-breath',
      poster: `anim/one-breath/posters/${id}.webp`,
      fit: 'contain',
      alt,
    },
    scrollVh: 165,
    captionPosition: 'top',
  }
}

export const ONE_BREATH_STAGES: readonly Stage[] = [
  oneBreath(
    'spark', 'Spark',
    'It begins as movement.',
    'A face draws on in white line-art and silently mouths a word; faint pulses ripple across the jaw, cheeks and throat, then condense into thirty-one sensor points resting on the skin.',
    'Every word begins as movement — and every moving muscle leaks a faint pulse of electricity onto the skin.',
  ),
  oneBreath(
    'sensors', 'Sensors',
    'Thirty-one sensors. No microphone.',
    'The sensor points brighten and each unspools a live wiggly trace; the face slides away as a full thirty-one-line waterfall fills the frame; a microphone is struck out.',
    'Thirty-one skin sensors catch those pulses, five thousand readings a second — no microphone, no sound.',
  ),
  oneBreath(
    'fingerprints', 'Fingerprints',
    'A fingerprint, fifty times a second.',
    'A window sweeps across the waterfall; each pass stamps a small symmetric grid below; the grids stack into a filmstrip that glides to the right.',
    'Fifty times a second we ask one question — which muscles move together? — and each answer is a fingerprint.',
  ),
  oneBreath(
    'reader', 'The reader',
    'A reader that learns.',
    'The filmstrip feeds a compact box of turning dials that settle as it learns; a ghost voice waveform pours light into the box then evaporates; the sounds K, AE, T emerge.',
    'A small neural network learns to read the fingerprints, taught by the real voice — a teacher it then never needs.',
  ),
  oneBreath(
    'words', 'The word map',
    'Sounds become words.',
    'The sounds arc onto a constellation of word-nodes; candidate paths flicker and die; the cheapest route ignites end to end and its words lift into a sentence.',
    'It guesses sounds, not spelling; a map of 34,546 words turns them into sentences via the cheapest path.',
  ),
  oneBreath(
    'chooser', 'The chooser',
    'The best sentence wins.',
    'Five candidate sentences stack in a column; a scanning band reads each against the detected sounds; four fade to gray and one blooms to white and re-types itself.',
    'A language model reads every candidate and the detected sounds together, and picks the one that makes most sense.',
  ),
  oneBreath(
    'score', 'The score',
    'Four words in five — 81% accurate.',
    'The chosen sentence bursts into particles that reform as the number 51, which falls 51 to 40 to 26 to 18.5 as a bar shrinks; five word-slots draw and four light up.',
    'From a baseline of half the words wrong down to four in five correct — 18.5% word error, from muscles alone.',
  ),
  oneBreath(
    'foundation', 'Foundation',
    'Built on UC Davis.',
    'A small "this pipeline" block rests on two large foundation stones — the corpus and the approach — beneath a UC Davis nameplate; borrowed-method tags orbit and tether in.',
    'A UC Davis lab built the sensors, data and approach; I built upward from it — composition, not invention.',
  ),
  oneBreath(
    'silent', 'Silent speech',
    'For silent speech.',
    'A triptych of use-cases: a silent mouth in a loud cafe typing text, a private no-voice dictation, and a hands-free case; the panels compress into three lines of typed text.',
    'Mouth the words and they become text — in a crowd, in a meeting, anywhere a voice can’t go.',
  ),
  oneBreath(
    'end', 'In one breath',
    'In one breath.',
    'Three lines of text braid into one EMG trace that shatters into particles; the particles stream together to spell MYOVOX, which ignites with a light-sweep and settles.',
    'That’s the whole idea, in one breath.',
  ),
] as const
