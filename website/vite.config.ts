import { createHash } from 'node:crypto'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Static site for GitHub Pages. `base` MUST match the repo so assets resolve
 * under https://<user>.github.io/<repo>/. Override at build time with
 * `VITE_BASE=/ npm run build` for a user-site / custom-domain deploy.
 * Every asset reference in code uses `import.meta.env.BASE_URL`, never a
 * hard-coded leading-slash path, so it stays correct under any base.
 */

/**
 * Cache-bust id for the anim assets (?v=<id> on every clip/poster/frame URL).
 * A CONTENT hash of public/anim, not a per-build timestamp: the renders are
 * immutable, so a deploy that didn't re-render anything keeps the same id —
 * the media service worker's cache (hundreds of MB of scrub frames) survives
 * the deploy instead of being pruned and re-downloaded on every visit. Any
 * re-render changes the hash and invalidates cleanly.
 */
function animContentHash(dir: string): string {
  const h = createHash('sha1')
  const walk = (d: string) => {
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

export default defineConfig(({ command }) => ({
  base: process.env.VITE_BASE ?? '/myovox/',
  plugins: [react()],
  define: {
    // Dev busts per page-load instead (see asset.ts), so skip hashing ~0.5GB
    // of frames on every dev-server start.
    __BUILD_ID__: JSON.stringify(
      command === 'build'
        ? animContentHash(fileURLToPath(new URL('./public/anim', import.meta.url)))
        : 'dev',
    ),
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    target: 'es2022',
    sourcemap: false,
    chunkSizeWarningLimit: 1200,
  },
}))
