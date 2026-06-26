// Reproduce the "Play jumps forward several stages" report. Scrolls to a stage,
// presses Play, and measures how far the view advances in a short window.
// Usage: node scripts/play_test.mjs <stageId> <port> <waitMs>
import { chromium } from 'playwright'

const [, , stageId = 'wfst', port = '5173', waitMs = '1600', localStr = '0.3'] = process.argv
const url = `http://localhost:${port}/myovox/`
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })
const errs = []
page.on('pageerror', (e) => errs.push(String(e)))

await page.goto(url, { waitUntil: 'domcontentloaded' })
await page.waitForFunction(() => typeof window.__scrollToStageLocal === 'function', { timeout: 20000 })

const railNum = () =>
  page.evaluate(() => {
    const el = document.querySelector('[data-caption-wrap]')
    const m = el && el.textContent.match(/(\d+)\s*\/\s*50/)
    return m ? Number(m[1]) : null
  })
const narr = () =>
  page.evaluate(() => {
    // the narration hot-state isn't on window; infer from the visible subtitle
    const el = document.querySelector('[data-subtitles]')
    return el ? el.textContent.trim().slice(0, 40) : null
  })

await page.evaluate(([id, l]) => window.__scrollToStageLocal(id, Number(l)), [stageId, localStr])
await page.waitForTimeout(900)
const before = { stage: await railNum(), y: Math.round(await page.evaluate(() => window.scrollY)), sub: await narr() }

await page.click('button[aria-label="Play the story hands-free"]')
// sample the stage number a few times to see motion
const samples = []
for (let i = 0; i < Number(waitMs) / 200; i++) {
  await page.waitForTimeout(200)
  samples.push(await railNum())
}
const after = { stage: await railNum(), y: Math.round(await page.evaluate(() => window.scrollY)), sub: await narr() }

console.log(
  JSON.stringify({
    stageId,
    before,
    after,
    jumpStages: (after.stage ?? 0) - (before.stage ?? 0),
    stageSamples: samples,
    errs: errs.slice(0, 5),
  }),
)
await browser.close()
