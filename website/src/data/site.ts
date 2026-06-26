/** Site-wide constants: brand, repo link, navigation. One place to edit. */

export const SITE = {
  brand: 'MYOVOX',
  title: 'Myovox',
  repoUrl: 'https://github.com/Varshith-0/myovox',
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
