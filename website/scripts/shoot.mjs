// Headless screenshots of the Story page at several scroll fractions, so we can
// see the muscles stage (the solid head) render. Logs console/page errors too.
/* global document, window, getComputedStyle */
import { chromium } from 'playwright'

const BASE = process.env.URL || 'http://localhost:5173/myovox/'
const FRACS = process.env.FRACS ? process.env.FRACS.split(',').map(Number) : [0.0, 0.1, 0.13, 0.16, 0.2, 0.26]

const browser = await chromium.launch()
const page = await browser.newPage({
  viewport: { width: 1600, height: 900 },
  deviceScaleFactor: 1,
})
const errors = []
const logs = []
page.on('console', (m) => {
  const t = m.type()
  if (t === 'error') errors.push(m.text())
  else if (m.text().includes('[FaceHead]')) logs.push(m.text())
})
page.on('pageerror', (e) => errors.push('PAGEERR: ' + e.message))

await page.goto(BASE, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForSelector('canvas', { timeout: 30000 })
await page.waitForTimeout(4000) // loader overlay + GLB decode

for (const f of FRACS) {
  await page.evaluate((frac) => {
    const h = document.body.scrollHeight - window.innerHeight
    window.scrollTo(0, h * frac)
  }, f)
  await page.waitForTimeout(5200) // scene easing is slow — let it fully settle
  const caption = await page.evaluate(() => {
    const vh = window.innerHeight
    const out = []
    for (const e of document.querySelectorAll('h1,h2,h3,p')) {
      const r = e.getBoundingClientRect()
      const o = parseFloat(getComputedStyle(e).opacity)
      const txt = (e.textContent || '').trim()
      if (txt && r.top > 0 && r.top < vh * 0.95 && o > 0.45) out.push(txt.slice(0, 48))
    }
    return out.slice(0, 3)
  })
  const path = `/tmp/shot_${String(f).replace('.', '_')}.png`
  await page.screenshot({ path })
  console.log(`${f}  ${path}  ${JSON.stringify(caption)}`)
  if (process.env.TWICE) {
    await page.waitForTimeout(650)
    const path2 = `/tmp/shot_${String(f).replace('.', '_')}_b.png`
    await page.screenshot({ path: path2 })
    console.log(`${f}b ${path2}`)
  }
}

console.log('\nLOGS:')
for (const l of logs.slice(0, 5)) console.log('  ' + l)
console.log('\nERRORS (' + errors.length + '):')
for (const e of errors.slice(0, 25)) console.log('  ' + e)
await browser.close()
