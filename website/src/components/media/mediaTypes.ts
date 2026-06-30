import type { MutableRefObject } from 'react'
import { type Stage, type StageMedia } from '@/data/stages'

export type VideoStage = {
  stage: Stage
  index: number
  media: Extract<StageMedia, { kind: 'video' }>
}

export type MediaUrl = (path: string) => string

export interface MediaScrubberRefs {
  posters: MutableRefObject<Map<string, HTMLImageElement>>
  videos: MutableRefObject<Map<string, HTMLVideoElement>>
  baseOp: MutableRefObject<Map<string, number>>
  shownOnce: MutableRefObject<Map<string, boolean>>
  sceneRoot: MutableRefObject<HTMLElement | null>
  captionWrap: MutableRefObject<HTMLElement | null>
  canvasFade: MutableRefObject<number>
}
