import { useEffect, useRef, useState } from 'react'
import { useStore } from '@/store/useStore'
import { TIERS } from '@/components/media/scrubEngine'
import styles from './QualityControl.module.css'

/**
 * YouTube-style animation quality control. The pill shows the tier actually in
 * use (e.g. "720p"); the menu lists the fixed ladder — no "Auto" row. The row in
 * use is marked, and carries an `auto` tag while adaptive. Picking a row pins
 * that quality absolutely (a weak connection then just shows the loader more);
 * tapping the already-pinned row unpins it, returning to adaptive.
 */
export function QualityControl() {
  const active = useStore((s) => s.activeQuality)
  const pinned = useStore((s) => s.qualityPinned)
  const setPinned = useStore((s) => s.setQualityPinned)

  const [open, setOpen] = useState(false)
  const groupRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onDown = (e: PointerEvent) => {
      if (!(e.target instanceof Node) || !groupRef.current?.contains(e.target)) {
        setOpen(false)
      }
    }
    window.addEventListener('pointerdown', onDown)
    return () => window.removeEventListener('pointerdown', onDown)
  }, [open])

  return (
    <div className={styles.group} ref={groupRef}>
      {open && (
        <div className={styles.menu} role="menu" aria-label="Animation quality">
          {TIERS.map((t) => {
            const isActive = t === active
            const isPinned = t === pinned
            return (
              <button
                key={t}
                type="button"
                role="menuitemradio"
                aria-checked={isActive}
                className={`${styles.item} ${isActive ? styles.itemActive : ''}`}
                onClick={() => {
                  // Tap the pinned quality again → back to adaptive.
                  setPinned(isPinned ? null : t)
                  setOpen(false)
                }}
              >
                <span>{t}p</span>
                {isActive && (
                  <span className={styles.note}>{isPinned ? 'pinned' : 'auto'}</span>
                )}
              </button>
            )
          })}
        </div>
      )}
      <button
        type="button"
        className={styles.pill}
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={`Animation quality ${active}p${pinned ? '' : ' (automatic)'}. Click to choose.`}
        title={
          pinned
            ? `Quality pinned to ${active}p — tap it again in the menu for automatic`
            : `Quality ${active}p, chosen automatically for your connection`
        }
      >
        <GearGlyph />
        <span className={styles.value}>{active}p</span>
      </button>
    </div>
  )
}

function GearGlyph() {
  return (
    <svg
      className={styles.icon}
      width="14"
      height="14"
      viewBox="0 0 24 24"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="3.2" />
      <path d="M19.4 15a1.6 1.6 0 0 0 .33 1.77l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.6 1.6 0 0 0-1.77-.33 1.6 1.6 0 0 0-1 1.47V21a2 2 0 1 1-4 0v-.09a1.6 1.6 0 0 0-1-1.47 1.6 1.6 0 0 0-1.77.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.6 1.6 0 0 0 .33-1.77 1.6 1.6 0 0 0-1.47-1H3a2 2 0 1 1 0-4h.09a1.6 1.6 0 0 0 1.47-1 1.6 1.6 0 0 0-.33-1.77l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.6 1.6 0 0 0 1.77.33h.01a1.6 1.6 0 0 0 1-1.47V3a2 2 0 1 1 4 0v.09a1.6 1.6 0 0 0 1 1.47 1.6 1.6 0 0 0 1.77-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.6 1.6 0 0 0-.33 1.77v.01a1.6 1.6 0 0 0 1.47 1H21a2 2 0 1 1 0 4h-.09a1.6 1.6 0 0 0-1.47 1z" />
    </svg>
  )
}
