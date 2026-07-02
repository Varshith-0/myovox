#!/usr/bin/env bash
# Re-encode a Manim render for smooth scroll-scrubbing and emit a poster.
#   usage: encode.sh <scene_file.py> <SceneClass> <out-id>
# Produces website/public/anim/<out-id>.mp4 (scrub-friendly GOP: a keyframe every
# 12 frames so seeks stay cheap without the ~5-10x bloat of all-intra, no audio) +
# <out-id>.poster.webp. Run after the high-quality (`-qh` => 1080p30)
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

FFMPEG="$MENV/bin/ffmpeg"

mkdir -p "$OUT_DIR"
# -g 12 -keyint_min 12 -sc_threshold 0: a fixed keyframe every 12 frames (~0.4s at
# 30fps). Scrub seeks decode at most 11 frames from the prior keyframe (sub-frame
# on modern decoders) while P-frames shrink these B&W clips ~2-3x vs all-intra.
"$FFMPEG" -y -i "$src" -an -c:v libx264 -pix_fmt yuv420p \
  -g 12 -keyint_min 12 -sc_threshold 0 -crf 24 \
  -preset slow -movflags +faststart "$OUT_DIR/$id.mp4" >/dev/null 2>&1

# Poster = the clip's final frame as webp. Some ffmpeg builds (e.g. anaconda) ship
# without the libwebp encoder, so extract a PNG first, then encode webp with
# whichever tool is available — ffmpeg if it has libwebp, else cwebp.
poster="$OUT_DIR/$id.poster.webp"
poster_png="$(mktemp -t poster).png"
"$FFMPEG" -y -sseof -0.1 -i "$OUT_DIR/$id.mp4" -frames:v 1 "$poster_png" >/dev/null 2>&1
if "$FFMPEG" -hide_banner -encoders 2>/dev/null | grep -q libwebp; then
  "$FFMPEG" -y -i "$poster_png" "$poster" >/dev/null 2>&1
elif command -v cwebp >/dev/null 2>&1; then
  cwebp -q 82 "$poster_png" -o "$poster" >/dev/null 2>&1
else
  echo "WARN: no webp encoder (ffmpeg libwebp or cwebp) — poster not updated" >&2
fi
rm -f "$poster_png"

echo "encoded:"; du -h "$OUT_DIR/$id.mp4" "$poster"
