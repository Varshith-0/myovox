#!/usr/bin/env bash
# Extract each rendered clip into preloadable WebP frame sequences for the canvas
# scrubber (frame-perfect scroll-scrubbing — no video decoder on the hot path).
# Reads the already-encoded clips in public/anim/<id>.mp4, so it needs no
# manim/render env — just ffmpeg + a webp encoder (ffmpeg libwebp or cwebp).
#
#   ./frames.sh            # all clips in public/anim/*.mp4
#   ./frames.sh hero ctc   # only these ids
#
# Produces, per clip and per DPR tier:
#   public/anim/frames/<tier>/<id>/0001.webp ... NNNN.webp
# and a single public/anim/frames/manifest.json:
#   { fps, tiers: {"1x":540,"2x":1080}, clips: {id:count} }
# consumed once at runtime to pick a tier by screen density, size preloading, and
# map scroll -> frame index. Standard/phone screens load 1x; large/retina load 2x.
#
# Knobs (env): FPS (12), TIERS ("1x:540 2x:1080"), Q (cwebp quality 80). Higher FPS
# = smoother slow-scrub but more frames/memory; tier heights trade crispness/bytes.
set -euo pipefail

FPS="${FPS:-12}"
TIERS="${TIERS:-1x:540 2x:1080}"
Q="${Q:-80}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANIM="$HERE/../public/anim"
OUT="$ANIM/frames"
FFMPEG="${FFMPEG:-ffmpeg}"

# Detect a webp path once: ffmpeg-native (fast) if it has libwebp, else cwebp.
if "$FFMPEG" -hide_banner -encoders 2>/dev/null | grep -q libwebp; then
  WEBP=ffmpeg
elif command -v cwebp >/dev/null 2>&1; then
  WEBP=cwebp
else
  echo "ERROR: need ffmpeg with libwebp or the cwebp binary" >&2; exit 1
fi

mkdir -p "$OUT"

if [ "$#" -gt 0 ]; then ids=("$@"); else
  ids=(); for f in "$ANIM"/*.mp4; do ids+=("$(basename "$f" .mp4)"); done
fi

# One tier's frame extraction for one clip -> echoes the frame count.
extract_tier() { # src dir height
  local src="$1" dir="$2" h="$3"
  rm -rf "$dir"; mkdir -p "$dir"
  if [ "$WEBP" = ffmpeg ]; then
    "$FFMPEG" -y -i "$src" -vf "fps=$FPS,scale=-2:$h" -q:v 3 "$dir/%04d.webp" >/dev/null 2>&1
  else
    local tmp; tmp="$(mktemp -d)"
    "$FFMPEG" -y -i "$src" -vf "fps=$FPS,scale=-2:$h" "$tmp/%04d.png" >/dev/null 2>&1
    ls "$tmp"/*.png | xargs -P 8 -I{} sh -c 'cwebp -quiet -q "$0" "$1" -o "$2/$(basename "${1%.png}").webp"' "$Q" {} "$dir"
    rm -rf "$tmp"
  fi
  find "$dir" -name '*.webp' | wc -l | tr -d ' '
}

manifest_pairs=()
for id in "${ids[@]}"; do
  src="$ANIM/$id.mp4"
  [ -f "$src" ] || { echo "skip $id (no $src)"; continue; }
  count=""
  for tier in $TIERS; do
    name="${tier%%:*}"; height="${tier##*:}"
    n="$(extract_tier "$src" "$OUT/$name/$id" "$height")"
    [ "$n" -gt 0 ] || { echo "ERROR: no frames for $id ($name)" >&2; exit 1; }
    count="$n"  # frame count is identical across tiers (same fps)
  done
  manifest_pairs+=("$id=$count")
  echo "frames $id: $count x [${TIERS}]"
done

FPS="$FPS" TIERS="$TIERS" python3 - "$OUT/manifest.json" "${manifest_pairs[@]}" <<'PY'
import json, os, sys
out = sys.argv[1]
clips = {}
for pair in sys.argv[2:]:
    cid, n = pair.rsplit("=", 1)
    clips[cid] = int(n)
tiers = {t.split(":")[0]: int(t.split(":")[1]) for t in os.environ["TIERS"].split()}
# Merge into any existing manifest so a partial run doesn't drop the rest.
if os.path.exists(out):
    try:
        clips = {**json.load(open(out)).get("clips", {}), **clips}
    except Exception:
        pass
json.dump({"fps": int(os.environ["FPS"]), "tiers": tiers, "clips": clips},
          open(out, "w"), indent=0)
print(f"manifest: {len(clips)} clips, tiers={tiers} -> {out}")
PY
