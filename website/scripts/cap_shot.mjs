// Canvas-free Playwright screenshot helper for the (Manim) Story page.
// Usage: node scripts/cap_shot.mjs <stageId> <local 0..1> <out.png> [port] [w] [h]
// Scrolls to a stage at a local scroll fraction and screenshots — used to verify
// the scroll-driven subtitles render (the old shoot.mjs waited for a <canvas>).
import { chromium } from 'playwright'

const [, , stageId = 'ctc', localStr = '0.5', out = '/tmp/cap.png', port = '5173', w = '1280', h = '800'] =
  process.argv
const local = Number(localStr)
const url = `http://localhost:${port}/emg2text/`

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: Number(w), height: Number(h) } })
const errs = []
page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()) })
page.on('pageerror', (e) => errs.push(String(e)))

await page.goto(url, { waitUntil: 'domcontentloaded' })
// wait for the app's dev scroll helpers to exist
await page.waitForFunction(() => typeof window.__scrollToStageLocal === 'function', { timeout: 20000 })
await page.evaluate(([id, l]) => window.__scrollToStageLocal(id, l), [stageId, local])

// poll up to ~6s for the subtitle line to render (audio metadata must load so the
// scroll-derived playhead has a duration to map onto)
let subText = ''
for (let i = 0; i < 30; i++) {
  subText = await page.evaluate(() => {
    const el = document.querySelector('[data-subtitles]')
    return el ? el.textContent.trim() : ''
  })
  if (subText) break
  await page.waitForTimeout(200)
}
// optional: click the captions toggle off, to verify subtitles hide + sub returns
if (process.argv.includes('off')) {
  await page.click('button[aria-label="Turn subtitles off"]')
  await page.waitForTimeout(500)
}
await page.waitForTimeout(400)
const subVisible = await page.evaluate(() => !!document.querySelector('[data-subtitles]'))
const subLine = await page.evaluate(() => {
  const el = document.querySelector('[data-caption-sub]')
  return el ? el.textContent.trim().slice(0, 60) : null
})
await page.screenshot({ path: out })
console.log(JSON.stringify({ stageId, local, subText, subtitleEl: subVisible, subLineShown: subLine, consoleErrors: errs.slice(0, 8) }))
await browser.close()
