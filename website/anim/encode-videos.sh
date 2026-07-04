#!/usr/bin/env bash
# Build the 540p scrub tier: every clip in public/anim/video/1080/ is encoded
# all-keyframe (every frame independently seekable — frame-exact currentTime
# scrubbing in one decode) into public/anim/video/540/. Screens whose clip band
# spans ≤960 device pixels are served this tier; it is pixel-for-pixel identical
# to 1080p there. Run after render.sh whenever clips change.
#   ./encode-videos.sh            # all clips
#   ./encode-videos.sh hero ctc   # only these ids
set -euo pipefail
cd "$(dirname "$0")/../public/anim"

INTRA_FLAGS=(-c:v libx264 -preset slow -tune animation -g 1 -pix_fmt yuv420p -movflags +faststart -an)

mkdir -p video/540
ids=("$@")
if [ ${#ids[@]} -eq 0 ]; then
  for f in video/1080/*.mp4; do ids+=("$(basename "$f" .mp4)"); done
fi

for id in "${ids[@]}"; do
  ffmpeg -hide_banner -loglevel error -y -i "video/1080/$id.mp4" \
    -vf scale=-2:540 "${INTRA_FLAGS[@]}" -crf 20 "video/540/$id.mp4"
  echo "540p  $id"
done

echo "done"
