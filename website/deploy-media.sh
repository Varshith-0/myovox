#!/usr/bin/env bash
# Sync the anim media to the R2 bucket behind VITE_ASSET_BASE.
#
# Run after any render/encode, BEFORE pushing the site: the site's ?v= content
# hash is computed from public/anim at build time, so the frames must be on the
# CDN when the new build goes live. Incremental — only changed files upload.
#
# Needs the `r2-myovox` rclone remote (~/.config/rclone/rclone.conf).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

rclone sync public/anim r2-myovox:myovox-media/anim \
  --fast-list --transfers 32 --checkers 32 \
  --header-upload "Cache-Control: public, max-age=31536000, immutable"

# CI builds don't have public/anim (not in git) — they read this committed
# hash instead, so the site's ?v= matches what was just synced. COMMIT IT.
node scripts/anim-hash.mjs > .anim-version
echo "media synced to r2-myovox:myovox-media/anim"
echo "wrote .anim-version=$(cat .anim-version) — commit this file with your changes"
