/**
 * The sentence the head "speaks" on the Talking stage. As each word is spoken,
 * the muscle groups that produce it activate — so the viewer sees which muscles
 * fire for which sound. We reuse the sentence that is later decoded by the
 * pipeline (the Sentence stage), tying the story's input to its output.
 *
 * Per-word activation is a lightweight rule-based phonetic estimate over the
 * spelling (not a real forced alignment) — enough to make the mapping legible:
 * bilabials/rounded → lips, spread vowels → cheeks, open vowels → jaw opening,
 * lingual/closure consonants → tongue + jaw closing, voicing → throat.
 */

import { GROUPS } from './muscles'

export const SENTENCE = 'the signal is faint but the words are there'
export const WORDS = SENTENCE.split(' ')

/** Seconds each word is "spoken" before advancing. ~2.4 words/sec. */
export const WORD_DURATION = 0.42

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

// Group order matches GROUPS: ['lip','cheek','jawClose','jawOpen','tongue','throat']
function profileFor(word: string): number[] {
  // Baselines: speech is voiced (throat), tongue & jaw are near-always engaged.
  const g = { lip: 0, cheek: 0, jawClose: 0.25, jawOpen: 0.1, tongue: 0.3, throat: 0.4 }
  for (const ch of word.toLowerCase()) {
    if ('bpmfvw'.includes(ch)) g.lip += 0.5
    else if ('ou'.includes(ch)) {
      g.lip += 0.4 // rounded vowels
      g.jawOpen += 0.25
    } else if ('eiy'.includes(ch)) {
      g.cheek += 0.5 // spread vowels
      g.jawClose += 0.2
    } else if (ch === 'a') {
      g.jawOpen += 0.6 // open vowel
    } else if ('tdnszlr'.includes(ch)) {
      g.tongue += 0.45 // coronal / lingual
      g.jawClose += 0.2
    } else if ('ckgjqx'.includes(ch)) {
      g.tongue += 0.3 // dorsal / back
      g.jawClose += 0.35
    } else if (ch === 'h') {
      g.throat += 0.4
    }
  }
  return GROUPS.map((name) => clamp01(g[name]))
}

/** Precomputed per-word group profiles, indexed by word. */
export const WORD_PROFILES: readonly number[][] = WORDS.map(profileFor)
