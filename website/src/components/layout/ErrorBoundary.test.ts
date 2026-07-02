import { describe, it, expect } from 'vitest'
import { isChunkLoadError } from './chunkError'

describe('isChunkLoadError', () => {
  it('matches the browser/Vite dynamic-import failure messages', () => {
    expect(isChunkLoadError(new Error('Failed to fetch dynamically imported module: /myovox/assets/CodePage-abc123.js'))).toBe(true)
    expect(isChunkLoadError(new Error('error loading dynamically imported module'))).toBe(true)
    expect(isChunkLoadError(new Error('Importing a module script failed.'))).toBe(true)
    expect(isChunkLoadError(new Error('ChunkLoadError: Loading chunk 5 failed'))).toBe(true)
  })

  it('does not match an ordinary render/runtime error', () => {
    expect(isChunkLoadError(new Error("Cannot read properties of undefined (reading 'map')"))).toBe(false)
    expect(isChunkLoadError('some non-error value')).toBe(false)
  })
})
