#!/usr/bin/env bash
# Render the Story clips listed in render.manifest.json.
#
#   ./render.sh         # render all 50 scenes
#   ./render.sh <id>    # render one scene by clip id  (e.g. ./render.sh hero)
#   ./render.sh og      # render the social card -> ../public/og.png
#
# Each scene runs:  manim -qh <file> <class>  ->  encode.sh <file> <class> <id>,
# producing ../public/anim/<id>.mp4 + <id>.poster.webp. Narration (<id>.mp3 +
# <id>.captions.json) is generated separately by ../scripts/narrate.py.
#
# Env (defaults match a base anaconda install holding manim + ffmpeg; the scenes
# `from style import *`, so PYTHONPATH must include this dir — handled below):
#   MENV=/opt/anaconda3        python env with manim + ffmpeg
#   MEDIA_DIR=/tmp/emg_media   manim scratch media dir
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MENV="${MENV:-/opt/anaconda3}"
export MEDIA_DIR="${MEDIA_DIR:-/tmp/emg_media}"
MANIM="$MENV/bin/manim"
PY="$MENV/bin/python"
FFMPEG="$MENV/bin/ffmpeg"
MANIFEST="$HERE/render.manifest.json"
target="${1:-all}"

render_scene() { # file class id
  local file="$1" cls="$2" id="$3"
  echo ">> $id  ($file :: $cls)"
  PYTHONPATH="$HERE" "$MANIM" -qh --media_dir "$MEDIA_DIR" "$HERE/$file" "$cls"
  MENV="$MENV" MEDIA_DIR="$MEDIA_DIR" "$HERE/encode.sh" "$file" "$cls" "$id"
}

# Social card: a single still flattened onto the site's near-black -> public/og.png.
if [ "$target" = "og" ]; then
  read -r og_file og_cls < <("$PY" -c \
    'import json,sys;o=json.load(open(sys.argv[1]))["og"];print(o["file"],o["class"])' "$MANIFEST")
  PYTHONPATH="$HERE" "$MANIM" -s -r 1200,630 --media_dir "$MEDIA_DIR" "$HERE/$og_file" "$og_cls"
  shopt -s nullglob
  shots=("$MEDIA_DIR"/images/og-card/"$og_cls"*.png)
  [ "${#shots[@]}" -gt 0 ] || { echo "ERROR: og still not found under $MEDIA_DIR/images/og-card/"; exit 1; }
  "$FFMPEG" -y -f lavfi -i color=c=0x050505:s=1200x630 -i "${shots[0]}" \
    -filter_complex "[0][1]overlay=format=auto" -frames:v 1 "$HERE/../public/og.png" >/dev/null 2>&1
  echo "wrote public/og.png"
  exit 0
fi

matched=0
while IFS=$'\t' read -r file cls id; do
  [ -z "$file" ] && continue
  render_scene "$file" "$cls" "$id"
  matched=$((matched + 1))
done < <("$PY" - "$MANIFEST" "$target" <<'PYEOF'
import json, sys
m = json.load(open(sys.argv[1]))
target = sys.argv[2]
for s in m["scenes"]:
    if target in ("all", s["id"]):
        print(f'{s["file"]}\t{s["class"]}\t{s["id"]}')
PYEOF
)
[ "$matched" -gt 0 ] || { echo "no scene matched '$target' (use a clip id from render.manifest.json, 'all', or 'og')"; exit 1; }
echo "done ($matched scene(s))."
