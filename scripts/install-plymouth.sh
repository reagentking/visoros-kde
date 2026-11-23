#!/usr/bin/env bash
# Install / remove the VisorOS Plymouth boot theme. Needs root (re-runs itself with sudo).
#
#   scripts/install-plymouth.sh on    copy plymouth/visoros to /usr/share/plymouth/themes,
#                                     make it the default and rebuild the initramfs
#   scripts/install-plymouth.sh off   switch back to CachyOS's theme and rebuild
#
# Rebuilding the initramfs (mkinitcpio -P) takes a minute. Takes effect on next boot.
set -euo pipefail
[[ $EUID -eq 0 ]] || exec sudo "$0" "$@"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/plymouth/visoros"
DEST=/usr/share/plymouth/themes/visoros
FALLBACK=cachyos

case "${1:-}" in
  on)
    [[ -f "$SRC/visoros.script" ]] || { echo "Build it first: python3 plymouth/build.py"; exit 1; }
    rm -rf "$DEST"
    cp -r "$SRC" "$DEST"
    chmod -R a+rX "$DEST"
    plymouth-set-default-theme -R visoros
    echo "VisorOS boot theme installed. Reboot to see it."
    ;;
  off)
    plymouth-set-default-theme -R "$FALLBACK"
    echo "Switched back to the $FALLBACK boot theme."
    ;;
  *) echo "usage: $0 on|off"; exit 1 ;;
esac
