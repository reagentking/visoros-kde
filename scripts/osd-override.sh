#!/usr/bin/env bash
# Enable/disable the VisorOS OSD for plasmashell.
#
# Plasma 6.8 builds the OSD from the QML module org.kde.plasma.workspace.osd
# (compiled into plasmashell), so a global theme can no longer override it.
# This shadows that module: qml/org/kde/plasma/workspace/osd holds our
# Osd.qml/OsdItem.qml plus links to Plasma's own plugin, and a systemd
# drop-in puts our qml/ dir first on plasmashell's QML_IMPORT_PATH.
#
# Usage: scripts/osd-override.sh on|off
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
MOD="$REPO/qml/org/kde/plasma/workspace/osd"
SYS=/usr/lib/qt6/qml/org/kde/plasma/workspace/osd
DROPIN="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/plasma-plasmashell.service.d/visoros-osd.conf"

case "${1:-}" in
  on)
    # Module definition: same as Plasma's, minus "prefer" (which would send
    # the engine back to the copy compiled into plasmashell).
    grep -v '^prefer ' "$SYS/qmldir" > "$MOD/qmldir"
    ln -sfn "$SYS/libplasmashell_osd.so" "$MOD/libplasmashell_osd.so"
    ln -sfn "$SYS/plasmashell_osd.qmltypes" "$MOD/plasmashell_osd.qmltypes"
    mkdir -p "$(dirname "$DROPIN")"
    printf '[Service]\nEnvironment=QML_IMPORT_PATH=%s\n' "$REPO/qml" > "$DROPIN"
    ;;
  off)
    rm -f "$DROPIN"
    ;;
  *) echo "usage: $0 on|off"; exit 1 ;;
esac
systemctl --user daemon-reload
systemctl --user restart plasma-plasmashell.service
echo "VisorOS OSD $1"
