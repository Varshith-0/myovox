import { describe, it, expect } from 'vitest'
import { clamp01, smooth } from './num'

describe('clamp01', () => {
  it('passes values already inside [0,1] through', () => {
    expect(clamp01(0)).toBe(0)
    expect(clamp01(0.5)).toBe(0.5)
    expect(clamp01(1)).toBe(1)
  })
  it('clamps out-of-range values to the nearest bound', () => {
    expect(clamp01(-0.001)).toBe(0)
    expect(clamp01(-99)).toBe(0)
    expect(clamp01(1.001)).toBe(1)
    expect(clamp01(99)).toBe(1)
  })
})

describe('smooth (smoothstep across [a,b])', () => {
  it('is 0 at or below the low edge and 1 at or above the high edge', () => {
    expect(smooth(0, 0, 1)).toBe(0)
    expect(smooth(-5, 0, 1)).toBe(0)
    expect(smooth(1, 0, 1)).toBe(1)
    expect(smooth(5, 0, 1)).toBe(1)
  })
  it('is 0.5 at the midpoint and monotonically increasing', () => {
    expect(smooth(0.5, 0, 1)).toBeCloseTo(0.5, 10)
    expect(smooth(0.25, 0, 1)).toBeLessThan(smooth(0.75, 0, 1))
  })
  it('respects a non-zero, non-unit range', () => {
    expect(smooth(10, 10, 20)).toBe(0)
    expect(smooth(15, 10, 20)).toBeCloseTo(0.5, 10)
    expect(smooth(20, 10, 20)).toBe(1)
  })
})
