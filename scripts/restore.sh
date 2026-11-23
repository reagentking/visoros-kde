#!/usr/bin/env bash
# Restore a snapshot made by backup.sh, then restart plasmashell.
# Usage: scripts/restore.sh backups/<name>.tar.gz
set -euo pipefail
archive="${1:?usage: restore.sh backups/<name>.tar.gz}"
echo "Restoring $archive into $HOME ..."
tar -xzf "$archive" -C "$HOME"
# Re-apply the restored color scheme so running apps pick it up.
scheme=$(kreadconfig6 --file kdeglobals --group General --key ColorScheme || true)
[[ -n "$scheme" ]] && plasma-apply-colorscheme "$scheme" || true
systemctl --user restart plasma-plasmashell.service
echo "Done. Log out and back in if anything still looks off."
