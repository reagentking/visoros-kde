#!/usr/bin/env bash
# Download VisorOS fonts (all SIL Open Font License) from the google/fonts repo.
# Usage: scripts/get-fonts.sh <download-dir>     (then install.sh copies them)
set -euo pipefail
out="${1:?usage: get-fonts.sh <download-dir>}"
mkdir -p "$out"
base="https://raw.githubusercontent.com/google/fonts/main/ofl"
files=(
  sairasemicondensed/SairaSemiCondensed-Regular.ttf
  sairasemicondensed/SairaSemiCondensed-Medium.ttf
  sairasemicondensed/SairaSemiCondensed-SemiBold.ttf
  sairasemicondensed/SairaSemiCondensed-Bold.ttf
  sairasemicondensed/OFL.txt
  barlow/Barlow-Regular.ttf
  barlow/Barlow-Italic.ttf
  barlow/Barlow-Medium.ttf
  barlow/Barlow-SemiBold.ttf
  barlow/Barlow-Bold.ttf
  barlow/OFL.txt
  sharetechmono/ShareTechMono-Regular.ttf
  sharetechmono/OFL.txt
)
for f in "${files[@]}"; do
  dest="$out/${f%%/*}-${f##*/}"; [[ "$f" == *.ttf ]] && dest="$out/${f##*/}"
  curl -fsSL --proto '=https' -o "$dest" "$base/$f"
  echo "  $dest"
done
