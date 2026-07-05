#!/usr/bin/env bash
# Build the 540p scrub tier: every clip in public/anim/<chapter>/video/1080/ is
# encoded all-keyframe (every frame independently seekable — frame-exact currentTime
# scrubbing in one decode) into public/anim/<chapter>/video/540/. Screens whose clip
# band spans ≤960 device pixels are served this tier; it is pixel-for-pixel identical
# to 1080p there. Run after render.sh whenever clips change.
#   ./encode-videos.sh            # all clips
#   ./encode-videos.sh hero ctc   # only these ids
set -euo pipefail
cd "$(dirname "$0")/../public/anim"

INTRA_FLAGS=(-c:v libx264 -preset slow -tune animation -g 1 -pix_fmt yuv420p -movflags +faststart -an)

ids=("$@")
if [ ${#ids[@]} -eq 0 ]; then
  for f in {one-breath,under-the-hood}/video/1080/*.mp4; do ids+=("$(basename "$f" .mp4)"); done
fi

for id in "${ids[@]}"; do
  case "$id" in one-breath-*) chapter=one-breath;; *) chapter=under-the-hood;; esac
  mkdir -p "$chapter/video/540"
  ffmpeg -hide_banner -loglevel error -y -i "$chapter/video/1080/$id.mp4" \
    -vf scale=-2:540 "${INTRA_FLAGS[@]}" -crf 20 "$chapter/video/540/$id.mp4"
  echo "540p  $id"
done

echo "done"
