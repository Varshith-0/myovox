import { describe, it, expect } from 'vitest'
import { lastBefore, needsLeadingSpace, joinWords, type CueWord } from './cues'

const at = (...times: number[]): { t: number }[] => times.map((t) => ({ t }))

describe('lastBefore (binary search for the last item with t <= time)', () => {
  it('returns -1 for an empty list', () => {
    expect(lastBefore([], 5)).toBe(-1)
  })
  it('returns -1 when time precedes the first item', () => {
    expect(lastBefore(at(1, 2, 3), 0.5)).toBe(-1)
  })
  it('returns the last index whose start has passed', () => {
    const items = at(0, 1, 2, 3)
    expect(lastBefore(items, 0)).toBe(0)
    expect(lastBefore(items, 1.5)).toBe(1)
    expect(lastBefore(items, 2)).toBe(2)
    expect(lastBefore(items, 99)).toBe(3)
  })
  it('is inclusive on an exact boundary match', () => {
    expect(lastBefore(at(0, 5, 10), 5)).toBe(1)
  })
})

describe('needsLeadingSpace', () => {
  it('never spaces the first word', () => {
    expect(needsLeadingSpace('Hello', 0)).toBe(false)
    expect(needsLeadingSpace(',', 0)).toBe(false)
  })
  it('spaces ordinary following words', () => {
    expect(needsLeadingSpace('world', 1)).toBe(true)
  })
  it('does not space words starting with closing punctuation', () => {
    for (const w of ['.', ',', '!', '?', ';', ':', '’', "'", '"', ')', ']', '…']) {
      expect(needsLeadingSpace(w, 1)).toBe(false)
    }
  })
  it('does space a standalone em-dash token', () => {
    expect(needsLeadingSpace('—', 1)).toBe(true)
  })
})

describe('joinWords', () => {
  const words = (...ws: string[]): CueWord[] => ws.map((w) => ({ w, t: 0 }))

  it('joins with single spaces', () => {
    expect(joinWords(words('the', 'quick', 'fox'))).toBe('the quick fox')
  })
  it('attaches trailing punctuation without a leading space', () => {
    expect(joinWords(words('the', 'end', '.'))).toBe('the end.')
  })
  it('spaces an em-dash on both sides', () => {
    expect(joinWords(words('A', '—', 'b'))).toBe('A — b')
  })
})
