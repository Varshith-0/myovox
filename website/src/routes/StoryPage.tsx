import { useRef } from 'react'
import type { Stage } from '@/data/stages'
import { StagesProvider } from '@/story/StagesProvider'
import { StorySections } from '@/components/story/StorySections'
import { Caption } from '@/components/story/Caption'
import { ProgressRail } from '@/components/story/ProgressRail'
import { MediaLayer } from '@/components/media/MediaLayer'
import { MediaLoader } from '@/components/media/MediaLoader'
import { NarrationLayer } from '@/components/story/NarrationLayer'
import { Subtitles } from '@/components/story/Subtitles'
import { PlayButton } from '@/components/story/PlayButton'
import { EndCard } from '@/components/story/EndCard'
import { useScrollProgress } from '@/hooks/useScrollProgress'

/**
 * The scroll experience, shared by both the fifty-scene deep dive and the ten-scene
 * One Breath. The scroller (one section per stage) feeds a single ScrollTrigger that
 * publishes `progress`; the fixed Caption and ProgressRail overlays react to the
 * active stage, and the MediaLayer reads progress imperatively to scrub the active
 * stage's clip. Scrolling is free (no mandatory snap) so each clip can be scrubbed
 * through at the reader's own pace.
 *
 * The active stage list is supplied via {@link StagesProvider} so every child reads
 * the same list without prop-drilling.
 *
 * @param stages the stage list to render.
 * @param autoPlay start hands-free playback on entry (One Breath).
 * @param endCardDeepDivePath when set, mounts One Breath end-card linking here.
 */
export function StoryExperience({
  stages,
  autoPlay = false,
  endCardDeepDivePath,
}: {
  stages: readonly Stage[]
  autoPlay?: boolean
  endCardDeepDivePath?: string
}) {
  const scroller = useRef<HTMLDivElement>(null)
  useScrollProgress(scroller, stages)

  return (
    <StagesProvider stages={stages}>
      <h1 className="sr-only">EMG to Text — reading speech from the muscles of the face</h1>
      <MediaLayer />
      <MediaLoader />
      <div ref={scroller}>
        <StorySections />
      </div>
      <Caption />
      <ProgressRail />
      <NarrationLayer />
      <Subtitles />
      <PlayButton autoPlay={autoPlay} />
      {endCardDeepDivePath && <EndCard deepDivePath={endCardDeepDivePath} />}
    </StagesProvider>
  )
}
