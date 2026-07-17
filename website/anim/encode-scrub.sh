#!/usr/bin/env bash
# encode-scrub.sh — the offline half of the "scrub with images, not video-seek" fix.
#
# For every 1080p master in website/anim/masters/<chapter>/ it produces
# one directory of crisp scrub frames per quality tier (the YouTube-style ladder):
#   scrub/<id>/1080/0001.webp …  1920px wide
#   scrub/<id>/720/0001.webp …   1280px
#   scrub/<id>/540/0001.webp …    960px
#   scrub/<id>/360/0001.webp …    640px
#   scrub/<id>/240/0001.webp …    426px
#   scrub/<id>/strip.webp         ONE tiny 12-frame sheet (L0, the anti-spinner)
# and writes public/anim/<chapter>/scrub.manifest.json
#   (id -> {frames, fps, tiers: {"1080":1920,…}, strip}).
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
# Quality ladder: "label:width". Labels are the height names the site shows (…p);
# widths assume 16:9. The masters are 1080p, so 1080 is the top (no upscaled 2160).
TIERS="1080:1920 720:1280 540:960 360:640 240:426"
STRIP_N=12            # frames in the tiny always-loaded baseline strip
STRIP_W=240           # per-cell width of that strip (px)
WEBP_Q=72             # libwebp quality (0–100)
WEBP_PRESET=drawing   # libwebp preset tuned for line-art / high-contrast diagrams (Manim on black)
WEBP_CL=6             # compression_level 0–6 (slower encode, smaller files; fine offline)
# ---------------------------------------------------------------------------

ROOT="website/public/anim"
MASTERS="website/anim/masters"
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
: > "$tmp/manifest.tsv"   # chapter \t id \t frames \t fps \t tiers("l:w,l:w,…") \t strip_n \t cw \t ch

# macOS ships bash 3.2 (no associative arrays): accumulate dry-run bytes in a tsv
: > "$tmp/dry.tsv"     # label \t projected_bytes
tot_frames=0; nclips=0

shopt -s nullglob
clips=("$MASTERS"/*/*.mp4)
[ ${#clips[@]} -gt 0 ] || { echo "no 1080 mp4s under $MASTERS (run from repo root)" >&2; exit 1; }

# the top tier's frame dir doubles as the "is this clip done?" marker
top_label="${TIERS%%:*}"

for f in "${clips[@]}"; do
  chapter="$(basename "$(dirname "$f")")"
  id="$(basename "$f" .mp4)"
  dur="$(probe format=duration "$f")"
  w="$(probe stream=width "$f")"
  h="$(probe stream=height "$f")"
  ch="$(python3 -c "print(round($STRIP_W*$h/$w))")"
  out="$ROOT/$chapter/scrub/$id"

  if [ "$DRY" = 1 ]; then
    # encode ONE mid-clip frame per tier, measure real bytes, project to ~n frames
    n="$(python3 -c "import math;print(math.ceil(float('$dur')*$SCRUB_FPS))")"
    mid="$(python3 -c "print(max(0.0, float('$dur')/2))")"
    line="$(printf '%-30s %6.1fs  n=%3d ' "$chapter/$id" "$dur" "$n")"
    for t in $TIERS; do
      lbl="${t%%:*}"; tw="${t##*:}"
      ffmpeg -v quiet -ss "$mid" -i "$f" -vf "scale=$tw:-2" -frames:v 1 -y "$tmp/s.png"; webp "$tmp/s.png"
      p=$(( $(fsize "$tmp/s.webp") * n ))
      printf "%s\t%d\n" "$lbl" "$p" >> "$tmp/dry.tsv"
      line+="$(printf ' %s~%sMB' "$lbl" "$(mb $p)")"
    done
    tot_frames=$((tot_frames+n)); nclips=$((nclips+1))
    echo "$line"
    continue
  fi

  # strip.webp is generated LAST (after every tier), so its presence after the
  # up-front rm -rf marks a fully finished clip — no frame-count guess needed.
  if [ "$FORCE" = 0 ] && [ -f "$out/strip.webp" ]; then
    echo "skip (done): $chapter/$id"
  else
    rm -rf "$out"; mkdir -p "$out"
    strip_fps="$(python3 -c "print(($STRIP_N+2)/float('$dur'))")"   # oversample so tile always fills
    for t in $TIERS; do
      lbl="${t%%:*}"; tw="${t##*:}"
      mkdir -p "$out/$lbl"
      ffmpeg -v error -i "$f" -vf "fps=$SCRUB_FPS,scale=$tw:-2" -y "$out/$lbl/%04d.png"
      webp_dir "$out/$lbl"
    done
    ffmpeg -v error -i "$f" -vf "fps=$strip_fps,scale=$STRIP_W:-2,tile=${STRIP_N}x1" -frames:v 1 -y "$out/strip.png"
    webp "$out/strip.png"
    echo "done: $chapter/$id"
  fi
  # frames = what ffmpeg actually emitted (ceil(dur*fps) projects one too many,
  # which made the site request a missing last frame per clip)
  n="$(ls -1 "$out/$top_label" | wc -l | tr -d ' ')"
  tiers_field="$(echo "$TIERS" | tr ' ' ',')"
  printf "%s\t%s\t%d\t%d\t%s\t%d\t%d\t%d\n" \
    "$chapter" "$id" "$n" "$SCRUB_FPS" "$tiers_field" "$STRIP_N" "$STRIP_W" "$ch" >> "$tmp/manifest.tsv"
done

if [ "$DRY" = 1 ]; then
  printf "\n== projected scrub budget ==\n%d clips, %d frames total\n" "$nclips" "$tot_frames"
  python3 - "$tmp/dry.tsv" "$TIERS" <<'PY'
import sys, collections
tot = collections.defaultdict(int)
for line in open(sys.argv[1]):
    lbl, b = line.split("\t")
    tot[lbl] += int(b)
for pair in sys.argv[2].split():
    lbl, w = pair.split(":")
    print(f"  {lbl}p ({w}px): ~{tot[lbl]/1048576:.1f} MB")
print(f"  all tiers: ~{sum(tot.values())/1048576:.1f} MB")
PY
  exit 0
fi

# one scrub.manifest.json per chapter (built with python to avoid hand-rolling JSON)
python3 - "$tmp/manifest.tsv" "$ROOT" <<'PY'
import sys, os, json, collections
tsv, root = sys.argv[1], sys.argv[2]
ch = collections.defaultdict(dict)
for line in open(tsv):
    chapter, cid, n, fps, tiers_field, sn, cw, cch = line.rstrip("\n").split("\t")
    tiers = {}
    for pair in tiers_field.split(","):
        lbl, w = pair.split(":")
        tiers[lbl] = int(w)
    ch[chapter][cid] = {
        "frames": int(n), "fps": int(fps),
        "tiers": tiers,
        "strip": {"n": int(sn), "cols": int(sn), "rows": 1, "cw": int(cw), "ch": int(cch)},
    }
for chapter, clips in ch.items():
    p = os.path.join(root, chapter, "scrub.manifest.json")
    with open(p, "w") as fh:
        json.dump(clips, fh, indent=2)
    print(f"wrote {p} ({len(clips)} clips)")
PY

echo "done."
