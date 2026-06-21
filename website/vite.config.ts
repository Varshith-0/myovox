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
export default defineConfig({
  base: process.env.VITE_BASE ?? '/emg2text/',
  plugins: [react()],
  // Build id used to cache-bust the Act-2 clips/posters. Their filenames are
  // stable (anim/<id>.mp4), so when a clip is re-rendered the browser would
  // otherwise keep serving the cached copy; appending ?v=<build id> changes the
  // URL each build/deploy. (In dev we bust per page-load instead — see MediaLayer.)
  define: {
    __BUILD_ID__: JSON.stringify(String(Date.now())),
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
})
