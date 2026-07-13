/**
 * Cache-bust the static clips/posters/caption tracks: their filenames are stable
 * (`anim/<id>.mp4`), so a re-rendered asset would otherwise keep serving from the
 * browser cache. In dev, bust per page-load (always see the latest render while
 * iterating); in prod, bust per build (cacheable, but a deploy invalidates it).
 */
import type { Stage } from '@/data/stages'

export const ASSET_VERSION = import.meta.env.DEV ? String(Date.now()) : __BUILD_ID__
const VER = ASSET_VERSION
const BASE = import.meta.env.BASE_URL

/** Resolve a BASE_URL-relative asset path to a cache-busted URL. */
export const assetUrl = (path: string): string => `${BASE}${path.replace(/^\//, '')}?v=${VER}`

/** Chapter folder under anim/ for a stage (its media src starts `anim/<chapter>/`). */
export const animDir = (stage: Stage): string => stage.media.src.split('/', 2).join('/')
