/** Small pure numeric helpers shared across the scroll/media hot paths. */

/** Clamp to [0, 1]. */
export const clamp01 = (v: number): number => (v < 0 ? 0 : v > 1 ? 1 : v)

/** Smoothstep from 0→1 as x moves across [a, b]. */
export function smooth(x: number, a: number, b: number): number {
  const t = clamp01((x - a) / (b - a))
  return t * t * (3 - 2 * t)
}
