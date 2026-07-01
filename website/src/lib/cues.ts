/** Caption-cue types and the pure logic the {@link Subtitles} overlay runs each frame. */

export interface CueWord {
  w: string
  t: number
}
export interface Cue {
  t: number
  end: number | null
  words: CueWord[]
}

/** Index of the last item whose start time has passed `time` (binary search), or -1. */
export function lastBefore<T extends { t: number }>(items: T[], time: number): number {
  let lo = 0
  let hi = items.length - 1
  let found = -1
  while (lo <= hi) {
    const mid = (lo + hi) >> 1
    if (items[mid].t <= time) {
      found = mid
      lo = mid + 1
    } else {
      hi = mid - 1
    }
  }
  return found
}

/** No leading space before a word that begins with closing punctuation. (A
 *  standalone em-dash token IS spaced — "word — next" — so it is excluded.) */
const NO_LEAD = /^[.,!?;:’'")\]…]/

/** Whether word `i` needs a leading space when joined to the previous word. */
export const needsLeadingSpace = (word: string, i: number): boolean => i > 0 && !NO_LEAD.test(word)

/** Join cue words into one sentence with punctuation-aware spacing. */
export const joinWords = (words: CueWord[]): string =>
  words.map((word, i) => (needsLeadingSpace(word.w, i) ? ' ' : '') + word.w).join('')
