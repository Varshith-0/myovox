/**
 * Which stage list the story components render — the fifty-scene deep dive
 * ({@link module:data/stages}) or the ten-scene One Breath ({@link module:data/oneBreathStages}).
 *
 * The context + hook live here; the {@link StagesProvider} component lives in its
 * own file so React Fast Refresh stays happy. The value is static for a route's
 * lifetime, so reading it at render is enough — the hot-path RAF loops close over it.
 */
import { createContext, useContext } from 'react'
import type { Stage } from '@/data/stages'

export const StagesContext = createContext<readonly Stage[] | null>(null)

/** The active stage list. Throws if used outside a StoryExperience. */
export function useStages(): readonly Stage[] {
  const stages = useContext(StagesContext)
  if (!stages) throw new Error('useStages must be used within a <StagesProvider>')
  return stages
}
