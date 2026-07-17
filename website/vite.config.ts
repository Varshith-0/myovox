import { existsSync, readFileSync, rmSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { animContentHash } from './scripts/anim-hash.mjs'

/** Production media CDN (Cloudflare R2, public bucket). Mirror of MEDIA_CDN in
 *  src/lib/asset.ts — the build plugins (strip/preconnect) need it too. Override
 *  with VITE_ASSET_BASE; set it to '' to serve media from GitHub Pages again. */
const MEDIA_CDN = 'https://pub-4fbe1a04dad243c99f4f8b006f26ed79.r2.dev/'

/**
 * Static site for GitHub Pages. `base` MUST match the repo so assets resolve
 * under https://<user>.github.io/<repo>/. Override at build time with
 * `VITE_BASE=/ npm run build` for a user-site / custom-domain deploy.
 *
 * The heavy anim/ media is served from a CDN when VITE_ASSET_BASE is set
 * (committed default in .env.production → R2). The media tree is NOT in git;
 * it lives on the render machine (public/anim) and in R2 (deploy-media.sh).
 */

/**
 * Cache-bust id for the anim assets (?v=<id> on every clip/poster/frame URL).
 * A CONTENT hash, not a per-build timestamp, so a deploy that didn't re-render
 * anything keeps every cache (browser, edge, service worker) warm. Live tree
 * when present (render machine); the committed .anim-version elsewhere (CI).
 */
function buildId(): string {
  const animDir = fileURLToPath(new URL('./public/anim', import.meta.url))
  if (existsSync(animDir)) return animContentHash(animDir)
  const versionFile = fileURLToPath(new URL('./.anim-version', import.meta.url))
  if (existsSync(versionFile)) return readFileSync(versionFile, 'utf8').trim()
  return 'dev'
}

/** With media on the CDN, public/anim must not ride along in the Pages
 *  artifact (it would blow GitHub Pages' 1GB limit): drop it after copy. */
function stripAnimWhenCdn(assetBase: string): Plugin {
  return {
    name: 'strip-anim-when-cdn',
    apply: 'build',
    closeBundle() {
      if (!assetBase) return
      rmSync(fileURLToPath(new URL('./dist/anim', import.meta.url)), {
        recursive: true,
        force: true,
      })
      console.log('\nstrip-anim-when-cdn: dist/anim removed (media served from VITE_ASSET_BASE)')
    },
  }
}

/** Open the CDN connection (DNS/TLS) before the first frame fetch needs it. */
function preconnectMedia(assetBase: string): Plugin {
  return {
    name: 'preconnect-media',
    transformIndexHtml() {
      if (!assetBase) return []
      return [
        {
          tag: 'link',
          attrs: { rel: 'preconnect', href: new URL(assetBase).origin, crossorigin: '' },
          injectTo: 'head-prepend' as const,
        },
      ]
    },
  }
}

export default defineConfig(({ command }) => {
  // Media base for the build-time plugins. Prod build → CDN unless overridden;
  // '' (empty) opts back into serving anim/ from the Pages artifact.
  const assetBase =
    process.env.VITE_ASSET_BASE ?? (command === 'build' ? MEDIA_CDN : '')
  return {
    base: process.env.VITE_BASE ?? '/myovox/',
    plugins: [react(), stripAnimWhenCdn(assetBase), preconnectMedia(assetBase)],
    define: {
      // Dev busts per page-load instead (see asset.ts) — skip the hash work.
      __BUILD_ID__: JSON.stringify(command === 'build' ? buildId() : 'dev'),
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
  }
})
