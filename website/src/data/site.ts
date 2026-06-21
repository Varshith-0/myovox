/** Site-wide constants: brand, repo link, navigation. One place to edit. */

export const SITE = {
  brand: 'EMG → TEXT',
  title: 'EMG → Text',
  repoUrl: 'https://github.com/Varshith-0/emg2text',
  tagline: 'Reading speech from the muscles of the face.',
} as const

export interface NavLinkDef {
  readonly to: string
  readonly label: string
  /** Exact-match active state (only the index route). */
  readonly end?: boolean
}

export const NAV_LINKS: readonly NavLinkDef[] = [
  { to: '/', label: 'Story', end: true },
  { to: '/technical', label: 'Technical' },
  { to: '/code', label: 'Code' },
] as const
