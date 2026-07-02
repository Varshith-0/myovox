import type { ReactNode } from 'react'
import type { Stage } from '@/data/stages'
import { StagesContext } from './StagesContext'

/** Supplies the active stage list (deep dive or reel) to the story components. */
export function StagesProvider({
  stages,
  children,
}: {
  stages: readonly Stage[]
  children: ReactNode
}) {
  return <StagesContext.Provider value={stages}>{children}</StagesContext.Provider>
}
