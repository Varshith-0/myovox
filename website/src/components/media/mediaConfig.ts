/** Centralized tuning knobs for the media scrubber subsystem. */

export const MEDIA_CONFIG = {
  visibilityDistance: 2,
  warmDistance: 4,
  seekEpsSeconds: 1 / 30,
  holdStart: 0.04,
  revealEnd: 0.16,
  captionRiseVh: 22,
  sceneFadeLerp: 0.26,
  stagePresenceLerp: 0.2,
} as const
