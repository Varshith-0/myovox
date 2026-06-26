import { useRef } from 'react'
import { StorySections } from '@/components/story/StorySections'
import { Caption } from '@/components/story/Caption'
import { ProgressRail } from '@/components/story/ProgressRail'
import { SpokenSentence } from '@/components/story/SpokenSentence'
import { MediaLayer } from '@/components/media/MediaLayer'
import { NarrationLayer } from '@/components/story/NarrationLayer'
import { Subtitles } from '@/components/story/Subtitles'
import { PlayButton } from '@/components/story/PlayButton'
import { useScrollProgress } from '@/hooks/useScrollProgress'

/**
 * The scroll experience. The scroller (one section per stage) feeds a single
 * ScrollTrigger that publishes `progress`; the fixed Caption and ProgressRail
 * overlays react to the active stage, and the MediaLayer reads progress
 * imperatively to scrub the active stage's clip. Scrolling is free (no mandatory
 * snap) so each clip can be scrubbed through at the reader's own pace.
 */
export function StoryPage() {
  const scroller = useRef<HTMLDivElement>(null)
  useScrollProgress(scroller)

  return (
    <>
      <h1 className="sr-only">EMG to Text — reading speech from the muscles of the face</h1>
      <MediaLayer />
      <div ref={scroller}>
        <StorySections />
      </div>
      <Caption />
      <ProgressRail />
      <SpokenSentence />
      <NarrationLayer />
      <Subtitles />
      <PlayButton />
    </>
  )
}
