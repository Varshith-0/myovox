#!/usr/bin/env bash
# Re-encode a Manim render for smooth scroll-scrubbing and emit a poster.
#   usage: encode.sh <scene_file.py> <SceneClass> <out-id>
# Produces website/anim/masters/<chapter>/<out-id>.mp4 (the 1080p master encode-scrub.sh
# samples into webp scrub frames — never shipped to the site, so it lives outside public/)
# + public/anim/<chapter>/posters/<out-id>.webp. Run after the high-quality (`-qh` =>
# 1080p30) render. MEDIA_DIR overrides the manim media dir (default /tmp/emg_media).
set -euo pipefail

MENV="${MENV:-${CONDA_PREFIX:-$HOME/.conda/envs/emgmanim}}"
MEDIA="${MEDIA_DIR:-/tmp/emg_media}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

file="$1"; cls="$2"; id="$3"
chapter="$(basename "$(dirname "$file")")"   # scenes live in anim/<chapter>/
VIDEO_DIR="$HERE/masters/$chapter"
POSTER_DIR="$HERE/../public/anim/$chapter/posters"
stem="$(basename "$file" .py)"
# Prefer the highest-res render present (manim -qk → 2160p60, -qp → 1440p60,
# -qh → 1080p30/60 depending on config). encode-scrub.sh then emits exactly the
# quality tiers the chosen master can fill — never upscaled.
src=""
for q in 2160p60 2160p30 1440p60 1440p30 1080p60 1080p30; do
  cand="$MEDIA/videos/$stem/$q/$cls.mp4"
  [ -f "$cand" ] && { src="$cand"; break; }
done
[ -n "$src" ] || { echo "ERROR: no render under $MEDIA/videos/$stem/ (did you run -qh, or -qk for 4K?)"; exit 1; }

FFMPEG="$MENV/bin/ffmpeg"

mkdir -p "$VIDEO_DIR" "$POSTER_DIR"
# -g 12 -keyint_min 12 -sc_threshold 0: a fixed keyframe every 12 frames (~0.4s at
# 30fps). Scrub seeks decode at most 11 frames from the prior keyframe (sub-frame
# on modern decoders) while P-frames shrink these B&W clips ~2-3x vs all-intra.
"$FFMPEG" -y -i "$src" -an -c:v libx264 -pix_fmt yuv420p \
  -g 12 -keyint_min 12 -sc_threshold 0 -crf 24 \
  -preset slow -movflags +faststart "$VIDEO_DIR/$id.mp4" >/dev/null 2>&1

# Poster = the clip's final frame as webp. Some ffmpeg builds (e.g. anaconda) ship
# without the libwebp encoder, so extract a PNG first, then encode webp with
# whichever tool is available — ffmpeg if it has libwebp, else cwebp.
poster="$POSTER_DIR/$id.webp"
poster_png="$(mktemp -t poster).png"
"$FFMPEG" -y -sseof -0.1 -i "$VIDEO_DIR/$id.mp4" -frames:v 1 "$poster_png" >/dev/null 2>&1
if "$FFMPEG" -hide_banner -encoders 2>/dev/null | grep -q libwebp; then
  "$FFMPEG" -y -i "$poster_png" "$poster" >/dev/null 2>&1
elif command -v cwebp >/dev/null 2>&1; then
  cwebp -q 82 "$poster_png" -o "$poster" >/dev/null 2>&1
else
  echo "WARN: no webp encoder (ffmpeg libwebp or cwebp) — poster not updated" >&2
fi
# Pre-blurred fallback poster (posters/blur/<id>.webp): the site fades it in as
# ambience while scrub frames load. Blur + darken are baked here, offline — a
# runtime CSS blur() cost a full-viewport GPU blur on every frame of the fade.
blur_dir="$POSTER_DIR/blur"
mkdir -p "$blur_dir"
blur_png="$(mktemp -t posterblur).png"
"$FFMPEG" -y -i "$poster_png" \
  -vf "scale=96:-2,gblur=sigma=2,colorchannelmixer=rr=0.85:gg=0.85:bb=0.85" \
  "$blur_png" >/dev/null 2>&1
if "$FFMPEG" -hide_banner -encoders 2>/dev/null | grep -q libwebp; then
  "$FFMPEG" -y -i "$blur_png" "$blur_dir/$id.webp" >/dev/null 2>&1
elif command -v cwebp >/dev/null 2>&1; then
  cwebp -quiet -q 62 "$blur_png" -o "$blur_dir/$id.webp" >/dev/null 2>&1
fi
rm -f "$poster_png" "$blur_png"

echo "encoded:"; du -h "$VIDEO_DIR/$id.mp4" "$poster"
