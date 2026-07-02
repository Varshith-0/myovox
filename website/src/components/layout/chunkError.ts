import type { ErrorVariant } from './ErrorScreen'

/**
 * Browser/Vite messages for a dynamic `import()` that never arrived — a lazy
 * route chunk that 404'd (a deploy changed the hashes while the tab was open) or
 * failed on the network (offline navigation). Matched loosely because the exact
 * wording differs across browsers.
 */
export function isChunkLoadError(error: unknown): boolean {
  const msg = error instanceof Error ? error.message : String(error)
  return /dynamically imported module|Importing a module script failed|ChunkLoadError|Failed to fetch/i.test(
    msg,
  )
}

/** A failed chunk while online means the deploy moved on (reload for the new
 *  build); offline means the network dropped (retry). Anything else is a crash. */
export function variantFor(error: unknown): ErrorVariant {
  if (isChunkLoadError(error)) return navigator.onLine ? 'update' : 'offline'
  return 'crashed'
}
