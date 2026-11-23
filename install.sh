#!/usr/bin/env bash
# Symlink VisorOS theme files into the user's KDE data dirs so edits in this
# repo show up live. Safe to re-run. Does not change any settings: see apply.sh.
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"

link() {  # link <repo-relative source> <absolute target>
  mkdir -p "$(dirname "$2")"
  ln -sfn "$REPO/$1" "$2"
  echo "  $2 -> $1"
}

echo "Installing VisorOS from $REPO"
link colors/VisorOS.colors                 "$DATA/color-schemes/VisorOS.colors"
link konsole/VisorOS-Backend.colorscheme   "$DATA/konsole/VisorOS-Backend.colorscheme"
link konsole/VisorOS.profile               "$DATA/konsole/VisorOS.profile"
link wallpaper/out                         "$DATA/wallpapers/VisorOS"
link desktoptheme/VisorOS                  "$DATA/plasma/desktoptheme/VisorOS"
link aurorae/VisorOS                       "$DATA/aurorae/themes/VisorOS"
link kvantum/VisorOS                       "${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum/VisorOS"
if compgen -G "$REPO/fonts/*.ttf" >/dev/null; then
  link fonts                               "$DATA/fonts/VisorOS"
  fc-cache -f "$DATA/fonts" >/dev/null
else
  echo "  (no fonts yet: run scripts/get-fonts.sh fonts)"
fi
echo "Done. Run ./apply.sh to switch to it."
