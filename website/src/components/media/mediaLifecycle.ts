/** Stage visibility for the scroll-scrub hot path (frame drawing lives in scrubEngine). */

/** Hide distant stages so the compositor can skip them. */
export function updateStageVisibility(el: HTMLElement, distance: number, maxDistance = 2): boolean {
  if (distance > maxDistance) {
    if (el.style.display !== 'none') el.style.display = 'none'
    return false
  }
  if (el.style.display === 'none') el.style.display = ''
  // Deferred poster: the URL waits in data-src until the stage is near, so a
  // fifty-poster story doesn't race the scrub frames for bandwidth on first load.
  const src = el.dataset.src
  if (src) {
    el.setAttribute('src', src)
    delete el.dataset.src
  }
  return true
}
