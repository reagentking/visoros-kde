#!/usr/bin/env bash
# Switch the running Plasma session to VisorOS (Phase 1: colors, Konsole, wallpapers).
# Roll back with: scripts/restore.sh backups/pre-visr.tar.gz
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
WP="${XDG_DATA_HOME:-$HOME/.local/share}/wallpapers/VisorOS"
# Wallpaper set: "unsc" (emblem, default) or "ring" (sky + ring arc). e.g. WALLPAPER=ring ./apply.sh
case "${WALLPAPER:-unsc}" in unsc) PFX=VisorOS-UNSC ;; ring) PFX=VisorOS ;; *) echo "WALLPAPER must be unsc or ring"; exit 1 ;; esac

echo "== Color scheme"
plasma-apply-colorscheme VisorOS

echo "== Plasma Style"
plasma-apply-desktoptheme VisorOS

echo "== Window decoration"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__VisorOS
qdbus6 org.kde.KWin /KWin reconfigure

echo "== App style (Kvantum)"
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum"
kwriteconfig6 --file "${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum/kvantum.kvconfig" --group General --key theme VisorOS
kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle kvantum
# KGlobalSettings::StyleChanged = 2
dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:2 int32:0 || true

echo "== Global theme package (OSD override via scripts/osd-override.sh on)"
kwriteconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage org.visoros.desktop

echo "== Fonts"
if [[ -n "$(fc-list 'Saira SemiCondensed')" && -n "$(fc-list 'Barlow')" ]]; then
  ui="Barlow,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kwriteconfig6 --file kdeglobals --group General --key font                 "$ui"
  kwriteconfig6 --file kdeglobals --group General --key menuFont             "$ui"
  kwriteconfig6 --file kdeglobals --group General --key toolBarFont          "$ui"
  kwriteconfig6 --file kdeglobals --group General --key smallestReadableFont "Barlow,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kwriteconfig6 --file kdeglobals --group WM      --key activeFont           "Saira SemiCondensed,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1"
  # Tell running KDE apps the fonts changed (KGlobalSettings::FontChanged = 1).
  dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:1 int32:0 || true
else
  echo "  fonts not installed; skipping (run scripts/get-fonts.sh fonts && ./install.sh)"
fi

echo "== Konsole default profile"
kwriteconfig6 --file konsolerc --group "Desktop Entry" --key DefaultProfile VisorOS.profile

echo "== Per-screen wallpapers"
# Each wallpaper is matched to a screen by its position in the layout
# (kscreen geometry), so it stays correct even if Plasma's screen numbering changes.
read -r -d '' JS <<EOF || true
var byPos = {
  "0,1080":    "$PFX-DP-1-2560x1440.png",
  "2560,1080": "$PFX-DP-3-2560x1440.png",
  "2926,0":    "$PFX-DP-2-1920x1080.png",
  "5120,987":  "$PFX-HDMI-A-1-1080x1920.png"
};
var ds = desktops();
for (var i = 0; i < ds.length; i++) {
  var d = ds[i];
  if (d.screen < 0) continue;
  var g = screenGeometry(d.screen);
  var key = Math.round(g.x) + "," + Math.round(g.y);
  var file = byPos[key] || (g.height > g.width ? "$PFX-HDMI-A-1-1080x1920.png" : "$PFX-DP-3-2560x1440.png");
  d.wallpaperPlugin = "org.kde.image";
  d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
  d.writeConfig("Image", "file://$WP/" + file);
  d.writeConfig("FillMode", 2);
  print("screen " + d.screen + " @" + key + " -> " + file + "\n");
}
EOF
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$JS"

echo "Done. Open a new Konsole window to see the back-end profile."
