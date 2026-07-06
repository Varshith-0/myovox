#!/usr/bin/env bash
# encode-scrub.sh — the offline half of the "scrub with images, not video-seek" fix.
#
# For every existing 1080 clip it produces, alongside your current MP4/poster:
#   scrub/<id>/hi/0001.webp …   crisp scrub frames, retina tier   (L1)
#   scrub/<id>/lo/0001.webp …   crisp scrub frames, phone tier    (L1)
#   scrub/<id>/strip.webp        ONE tiny 12-frame sheet           (L0, the anti-spinner)
# and writes public/anim/<chapter>/scrub.manifest.json (id -> {frames, fps, tiers, strip}).
#
# It reads the clips straight off disk, so it needs no knowledge of your render.manifest
# schema, and it drops everything under public/ so `vite build` ships it verbatim.
#
# Run from the repo root:
#   bash website/anim/encode-scrub.sh --dry-run   # probe + project exact byte budget, encode nothing
#   bash website/anim/encode-scrub.sh             # generate (idempotent: skips finished clips)
#   bash website/anim/encode-scrub.sh --force     # regenerate everything
#
set -euo pipefail

# ---- config (tune, then re-run) -------------------------------------------
SCRUB_FPS=12          # sampled frames/sec; 10–15 is visually identical to 30 WHILE dragging
HI_W=960              # retina scrub tier width (px). True-HD on huge displays is the optional WebCodecs tier.
LO_W=540              # phone scrub tier width (px)
STRIP_N=12            # frames in the tiny always-loaded baseline strip
STRIP_W=240           # per-cell width of that strip (px)
WEBP_Q=72             # libwebp quality (0–100)
WEBP_PRESET=drawing   # libwebp preset tuned for line-art / high-contrast diagrams (Manim on black)
WEBP_CL=6             # compression_level 0–6 (slower encode, smaller files; fine offline)
# ---------------------------------------------------------------------------

ROOT="website/public/anim"
FORCE=0; DRY=0
for a in "${@:-}"; do
  case "$a" in
    --force) FORCE=1 ;;
    --dry-run) DRY=1 ;;
    "") ;;
    *) echo "unknown arg: $a" >&2; exit 2 ;;
  esac
done

command -v ffprobe >/dev/null || { echo "ffprobe not found" >&2; exit 1; }
command -v ffmpeg  >/dev/null || { echo "ffmpeg not found"  >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 not found" >&2; exit 1; }
command -v cwebp   >/dev/null || { echo "cwebp not found (brew install webp)" >&2; exit 1; }

# ponytail: homebrew/conda ffmpeg ship without libwebp, so encode PNG then cwebp
webp() { cwebp -quiet -q "$WEBP_Q" -preset "$WEBP_PRESET" -m "$WEBP_CL" "$1" -o "${1%.png}.webp" && rm "$1"; }
webp_dir() { local p; for p in "$1"/*.png; do webp "$p"; done; }

fsize() { stat -f%z "$1" 2>/dev/null || stat -c%s "$1"; }
probe() { ffprobe -v quiet -show_entries "$1" -of csv=p=0 "$2"; }   # single-stream files -> single line
mb()    { python3 -c "print(f'{$1/1048576:.2f}')"; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
: > "$tmp/manifest.tsv"   # chapter \t id \t frames \t fps \t hi_w \t lo_w \t strip_n \t cw \t ch

tot_hi=0; tot_lo=0; tot_frames=0; nclips=0

shopt -s nullglob
clips=("$ROOT"/*/video/1080/*.mp4)
[ ${#clips[@]} -gt 0 ] || { echo "no 1080 mp4s under $ROOT (run from repo root)" >&2; exit 1; }

for f in "${clips[@]}"; do
  chapter="$(basename "$(dirname "$(dirname "$(dirname "$f")")")")"
  id="$(basename "$f" .mp4)"
  dur="$(probe format=duration "$f")"
  w="$(probe stream=width "$f")"
  h="$(probe stream=height "$f")"
  n="$(python3 -c "import math;print(math.ceil(float('$dur')*$SCRUB_FPS))")"
  ch="$(python3 -c "print(round($STRIP_W*$h/$w))")"
  out="$ROOT/$chapter/scrub/$id"

  if [ "$DRY" = 1 ]; then
    # encode ONE mid-clip frame per tier, measure real bytes, project to n frames
    mid="$(python3 -c "print(max(0.0, float('$dur')/2))")"
    ffmpeg -v quiet -ss "$mid" -i "$f" -vf "scale=$HI_W:-2" -frames:v 1 -y "$tmp/h.png"; webp "$tmp/h.png"
    ffmpeg -v quiet -ss "$mid" -i "$f" -vf "scale=$LO_W:-2" -frames:v 1 -y "$tmp/l.png"; webp "$tmp/l.png"
    ph=$(( $(fsize "$tmp/h.webp") * n ))
    pl=$(( $(fsize "$tmp/l.webp") * n ))
    tot_hi=$((tot_hi+ph)); tot_lo=$((tot_lo+pl)); tot_frames=$((tot_frames+n)); nclips=$((nclips+1))
    printf "%-30s %6.1fs  n=%3d  hi~%7sMB  lo~%7sMB\n" "$chapter/$id" "$dur" "$n" "$(mb $ph)" "$(mb $pl)"
    continue
  fi

  if [ "$FORCE" = 0 ] && [ -f "$out/strip.webp" ] && [ -d "$out/hi" ] \
     && [ "$(ls -1 "$out/hi" 2>/dev/null | wc -l | tr -d ' ')" -ge "$n" ]; then
    echo "skip (done): $chapter/$id"
  else
    rm -rf "$out"; mkdir -p "$out/hi" "$out/lo"
    strip_fps="$(python3 -c "print(($STRIP_N+2)/float('$dur'))")"   # oversample so tile always fills
    ffmpeg -v error -i "$f" -vf "fps=$SCRUB_FPS,scale=$HI_W:-2" -y "$out/hi/%04d.png"
    ffmpeg -v error -i "$f" -vf "fps=$SCRUB_FPS,scale=$LO_W:-2" -y "$out/lo/%04d.png"
    ffmpeg -v error -i "$f" -vf "fps=$strip_fps,scale=$STRIP_W:-2,tile=${STRIP_N}x1" -frames:v 1 -y "$out/strip.png"
    webp_dir "$out/hi"; webp_dir "$out/lo"; webp "$out/strip.png"
    echo "done: $chapter/$id  (n=$n)"
  fi
  printf "%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" \
    "$chapter" "$id" "$n" "$SCRUB_FPS" "$HI_W" "$LO_W" "$STRIP_N" "$STRIP_W" "$ch" >> "$tmp/manifest.tsv"
done

if [ "$DRY" = 1 ]; then
  printf "\n== projected scrub budget ==\n%d clips, %d frames total\n  hi (%dpx): ~%s MB\n  lo (%dpx): ~%s MB\ncurrent MP4s for comparison: 275 MB (1080) / 183 MB (540)\n" \
    "$nclips" "$tot_frames" "$HI_W" "$(mb $tot_hi)" "$LO_W" "$(mb $tot_lo)"
  exit 0
fi

# one scrub.manifest.json per chapter (built with python to avoid hand-rolling JSON)
python3 - "$tmp/manifest.tsv" "$ROOT" <<'PY'
import sys, os, json, collections
tsv, root = sys.argv[1], sys.argv[2]
ch = collections.defaultdict(dict)
for line in open(tsv):
    chapter, cid, n, fps, hi, lo, sn, cw, cch = line.rstrip("\n").split("\t")
    ch[chapter][cid] = {
        "frames": int(n), "fps": int(fps),
        "tiers": {"hi": int(hi), "lo": int(lo)},
        "strip": {"n": int(sn), "cols": int(sn), "rows": 1, "cw": int(cw), "ch": int(cch)},
    }
for chapter, clips in ch.items():
    p = os.path.join(root, chapter, "scrub.manifest.json")
    with open(p, "w") as fh:
        json.dump(clips, fh, indent=2)
    print(f"wrote {p} ({len(clips)} clips)")
PY

echo "done."
