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

/**
 * Where the heavy anim/ media lives. Production default is the Cloudflare R2
 * bucket (a PUBLIC url — it ships in this bundle by design), so the media is off
 * GitHub Pages and 4K fits. Override with VITE_ASSET_BASE at build time (another
 * CDN, or '' to serve from Pages again — then keep public/anim in the artifact).
 * Dev serves from the local BASE so `npm run dev` needs no network.
 */
export const MEDIA_CDN = 'https://pub-4fbe1a04dad243c99f4f8b006f26ed79.r2.dev/'
const envBase = (import.meta.env.VITE_ASSET_BASE as string | undefined)?.replace(/\/*$/, '/')
export const MEDIA_BASE: string =
  envBase ?? (import.meta.env.PROD ? MEDIA_CDN : BASE)

/** The media host's origin, '' when media is same-origin (used by the SW setup). */
export const MEDIA_ORIGIN: string = (() => {
  try {
    const origin = new URL(MEDIA_BASE, window.location.href).origin
    return origin === window.location.origin ? '' : origin
  } catch {
    return ''
  }
})()

/** Resolve a BASE_URL-relative asset path to a cache-busted URL. Anything under
 *  anim/ resolves against MEDIA_BASE (the CDN when configured). */
export const assetUrl = (path: string): string => {
  const clean = path.replace(/^\//, '')
  const base = clean.startsWith('anim/') ? MEDIA_BASE : BASE
  return `${base}${clean}?v=${VER}`
}

/** Chapter folder under anim/ for a stage. */
export const animDir = (stage: Stage): string => `anim/${stage.media.chapter}`
