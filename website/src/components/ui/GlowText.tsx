import { createElement, type ElementType, type ReactNode } from 'react'

interface GlowTextProps {
  /** Element to render (defaults to span). */
  as?: ElementType
  /** Use the brighter glow. */
  strong?: boolean
  className?: string
  children: ReactNode
}

/** Renders text with the white CSS glow, in any tag. Keeps glow usage consistent. */
export function GlowText({ as: tag = 'span', strong = false, className, children }: GlowTextProps) {
  const cls = [strong ? 'glow-strong' : 'glow', className].filter(Boolean).join(' ')
  return createElement(tag, { className: cls }, children)
}
