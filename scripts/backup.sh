#!/usr/bin/env bash
# Snapshot the current Plasma look so VisorOS can be rolled back.
# Usage: scripts/backup.sh [name]     -> backups/<name>.tar.gz (default: pre-visr-<timestamp>)
set -euo pipefail
cd "$(dirname "$0")/.."
name="${1:-pre-visr-$(date +%Y%m%d-%H%M%S)}"
out="backups/$name.tar.gz"

files=(
  .config/kdeglobals
  .config/plasmarc
  .config/plasmashellrc
  .config/plasma-org.kde.plasma.desktop-appletsrc
  .config/kwinrc
  .config/kscreenlockerrc
  .config/ksplashrc
  .config/konsolerc
  .config/Kvantum
  .config/gtk-3.0/settings.ini
  .config/gtk-4.0/settings.ini
  .config/gtkrc
  .config/gtkrc-2.0
  .local/share/konsole
  .local/share/color-schemes
)
existing=()
for f in "${files[@]}"; do [[ -e "$HOME/$f" ]] && existing+=("$f"); done

tar -czf "$out" -C "$HOME" "${existing[@]}"
echo "Saved ${#existing[@]} items to $out"
