#!/usr/bin/env bash
# Re-encode a Manim render for smooth scroll-scrubbing and emit a poster.
#   usage: encode.sh <scene_file.py> <SceneClass> <out-id>
# Produces website/public/anim/<out-id>.mp4 (every frame a keyframe, -g 1, no
# audio) + <out-id>.poster.webp. Run after the high-quality (`-qh` => 1080p30)
# render. MEDIA_DIR overrides the manim media dir (default /tmp/emg_media).
set -euo pipefail

MENV="${MENV:-${CONDA_PREFIX:-$HOME/.conda/envs/emgmanim}}"
MEDIA="${MEDIA_DIR:-/tmp/emg_media}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$HERE/../public/anim"

file="$1"; cls="$2"; id="$3"
stem="$(basename "$file" .py)"
src="$MEDIA/videos/$stem/1080p30/$cls.mp4"
[ -f "$src" ] || { echo "ERROR: render not found: $src (did you run -qh?)"; exit 1; }

mkdir -p "$OUT_DIR"
"$MENV/bin/ffmpeg" -y -i "$src" -an -c:v libx264 -pix_fmt yuv420p -g 1 -crf 24 \
  -preset slow -movflags +faststart "$OUT_DIR/$id.mp4" >/dev/null 2>&1
"$MENV/bin/ffmpeg" -y -sseof -0.1 -i "$OUT_DIR/$id.mp4" -frames:v 1 \
  "$OUT_DIR/$id.poster.webp" >/dev/null 2>&1
echo "encoded:"; du -h "$OUT_DIR/$id.mp4" "$OUT_DIR/$id.poster.webp"
