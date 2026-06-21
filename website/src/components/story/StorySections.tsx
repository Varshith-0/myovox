import { STAGES, stageScrollVh } from '@/data/stages'
import styles from './StorySections.module.css'

/**
 * The scrollable DOM spine. One section per stage provides the scroll height the
 * ScrollTrigger measures; each carries a screen-reader-only heading so the
 * narrative is navigable and indexable without the visuals. Act-2 (Manim) stages
 * declare a taller `scrollVh` so their clip has room to scrub.
 */
export function StorySections() {
  return (
    <div className={styles.sections}>
      {STAGES.map((stage) => {
        const vh = stageScrollVh(stage)
        return (
          <section
            key={stage.id}
            id={stage.id}
            className={styles.section}
            style={vh !== 100 ? { height: `${vh}svh` } : undefined}
          >
            <h2 className="sr-only">
              {stage.rail}. {stage.caption} {stage.sub ?? ''}
            </h2>
          </section>
        )
      })}
      {/* One extra viewport so the final section can scroll fully out — lets the
          last Act-2 clip reach the end of its scrub (local progress 1). */}
      <div aria-hidden="true" style={{ height: '100svh' }} />
    </div>
  )
}
