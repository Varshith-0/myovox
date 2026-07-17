import { useEffect, useRef, useState } from 'react'
import { useStore } from '@/store/useStore'
import styles from './QualityControl.module.css'

/**
 * YouTube-style animation quality control. The pill shows the tier actually in
 * use (e.g. "720p" — never the word "auto"). The menu leads with an Auto row
 * whose note shows what auto resolves to right now, followed by the fixed
 * ladder; the selection carries a tick. Picking a tier pins it absolutely
 * (a weak connection then just shows the loader more); Auto is the default.
 */
export function QualityControl() {
  const active = useStore((s) => s.activeQuality)
  const auto = useStore((s) => s.autoQuality)
  const pinned = useStore((s) => s.qualityPinned)
  const setPinned = useStore((s) => s.setQualityPinned)
  // Only tiers the current chapter's renders provide — no upscaled fake options.
  const tiers = useStore((s) => s.availableTiers)

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
          <button
            type="button"
            role="menuitemradio"
            aria-checked={pinned === null}
            className={`${styles.item} ${pinned === null ? styles.itemActive : ''}`}
            onClick={() => {
              setPinned(null)
              setOpen(false)
            }}
          >
            <span>Auto</span>
            <span className={styles.side}>
              <span className={styles.note}>{auto}p</span>
              {pinned === null && <Tick />}
            </span>
          </button>
          {tiers.map((t) => (
            <button
              key={t}
              type="button"
              role="menuitemradio"
              aria-checked={t === pinned}
              className={`${styles.item} ${t === pinned ? styles.itemActive : ''}`}
              onClick={() => {
                setPinned(t)
                setOpen(false)
              }}
            >
              <span>{t}p</span>
              {t === pinned && <Tick />}
            </button>
          ))}
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
            ? `Quality set to ${active}p`
            : `Quality ${active}p, chosen automatically for your connection`
        }
      >
        <GearGlyph />
        <span className={styles.value}>{active}p</span>
      </button>
    </div>
  )
}

function Tick() {
  return (
    <svg
      className={styles.tick}
      width="12"
      height="12"
      viewBox="0 0 24 24"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M4 12.5 10 18.5 20 6" />
    </svg>
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
