#!/usr/bin/env bash
# Apply the VisorOS panel layout and make sure there are at least 2 virtual desktops.
# Restarts plasmashell so the widget order takes effect (panels blink briefly).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RC=plasma-org.kde.plasma.desktop-appletsrc

count=$(qdbus6 org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Get org.kde.KWin.VirtualDesktopManager count)
if (( count < 2 )); then
  qdbus6 org.kde.KWin /VirtualDesktopManager org.kde.KWin.VirtualDesktopManager.createDesktop 1 "Desktop 2"
  echo "Added a second virtual desktop"
fi

out=$(qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$(cat "$HERE/panels.js")")

# plasmashell saves its in-memory widget order on exit, so stop it first,
# then write the order, then start it again.
systemctl --user stop plasma-plasmashell.service
while read -r tag id order; do
  [[ "$tag" == ORDER ]] || continue
  kwriteconfig6 --file "$RC" --group Containments --group "$id" --group General --key AppletOrder "$order"
  echo "panel $id: $order"
done <<< "$out"
systemctl --user start plasma-plasmashell.service
echo "Panels updated."
