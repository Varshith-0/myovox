#!/usr/bin/env bash
# Produce the scrubbable video tiers for the MediaLayer:
#   - reels re-encoded to all-keyframe 1080p (they shipped with sparse keyframes;
#     frame-exact currentTime scrubbing needs every frame independently seekable)
#   - a 540p tier of every clip under anim/540/ for phones & standard displays
# The story clips are the original all-keyframe 1080p renders and are left untouched.
set -euo pipefail
cd "$(dirname "$0")/../public/anim"

INTRA_FLAGS=(-c:v libx264 -preset slow -tune animation -g 1 -pix_fmt yuv420p -movflags +faststart -an)

for f in reel-*.mp4; do
  ffmpeg -hide_banner -loglevel error -y -i "$f" "${INTRA_FLAGS[@]}" -crf 18 "tmp-$f"
  mv "tmp-$f" "$f"
  echo "reel  $f"
done

mkdir -p 540
for f in *.mp4; do
  ffmpeg -hide_banner -loglevel error -y -i "$f" -vf scale=-2:540 "${INTRA_FLAGS[@]}" -crf 20 "540/$f"
  echo "540p  $f"
done

echo "done"
