#!/usr/bin/env node
/**
 * Content hash of public/anim — the site's ?v= cache-bust id.
 *
 * Shared by vite.config.ts (computes it live when the media tree is present)
 * and deploy-media.sh (writes it to website/.anim-version, the committed
 * fallback CI builds read — the media tree itself is not in git; it lives in
 * R2 and on the render machine).
 */
import { createHash } from 'node:crypto'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

export function animContentHash(dir) {
  const h = createHash('sha1')
  const walk = (d) => {
    const entries = readdirSync(d, { withFileTypes: true }).sort((a, b) =>
      a.name < b.name ? -1 : 1,
    )
    for (const e of entries) {
      const p = join(d, e.name)
      if (e.isDirectory()) walk(p)
      else {
        h.update(p.slice(dir.length))
        h.update(readFileSync(p))
      }
    }
  }
  walk(dir)
  return h.digest('hex').slice(0, 12)
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(animContentHash(fileURLToPath(new URL('../public/anim', import.meta.url))))
}
