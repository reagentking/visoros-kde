# VisorOS for Plasma

A KDE Plasma 6 theme inspired by Halo Infinite's VISR OS design language:
flat, cool **front-end** surfaces with light-fill selection, and a neon-green
**back-end** for terminals and boot. Built for a four-monitor CachyOS desktop.
The concept and full build plan are in `docs/visoros-kde-concept.html`.

## Layout

| Folder | What | Built by |
|---|---|---|
| `colors/` | Plasma color scheme | hand-written |
| `konsole/` | Back-end Konsole scheme + profile | hand-written |
| `desktoptheme/` | Plasma Style (panels, popups, taskbar states) | `desktoptheme/generate.py` |
| `aurorae/` | Window decoration | `aurorae/generate.py` |
| `kvantum/` | Qt app style (recolor of KvAdaptaDark) | `kvantum/build.py` |
| `wallpaper/` | Spanning wallpapers, cut per monitor | `wallpaper/src/render.py` |
| `fonts/` | Saira SemiCondensed, Barlow, Share Tech Mono (OFL) | `scripts/get-fonts.sh` |
| `look-and-feel/` | Global theme package: defaults + green boot-log splash (logout borrowed from CachyOS-Nord) | hand-written |
| `qml/` | Ammo-counter OSD, shadowing Plasma's `org.kde.plasma.workspace.osd` module | `scripts/osd-override.sh on` |
| `plasmoids/` | Workspace Tabs widget (virtual desktops as menu tabs) | hand-written |
| `sensorfaces/` | VisorOS Dashboard face for System Monitor / sensor widgets | hand-written |
| `plymouth/` | Boot theme (green back-end log), text pre-rendered | `plymouth/build.py` |
| `scripts/` | Backup/restore, panel layout, OSD override, Plymouth install | |

## Use

```bash
python3 wallpaper/src/render.py wallpaper/out                 # ring wallpaper set
python3 wallpaper/src/render.py wallpaper/out --theme unsc \
        --emblem wallpaper/private/unsc-emblem.png             # UNSC set (needs your own emblem cut-out)
scripts/backup.sh pre-visr       # snapshot the current look first
./install.sh                     # symlink everything into ~/.local/share and ~/.config
./apply.sh                       # switch the session over (WALLPAPER=ring for the ring set)
scripts/apply-panels.sh          # one top taskbar per screen, apps from that screen only
scripts/osd-override.sh on       # ammo-counter volume/brightness OSD (off to revert)
python3 plymouth/build.py && scripts/install-plymouth.sh on   # boot theme (sudo; off to revert)
```

Roll back with `scripts/restore.sh backups/<name>.tar.gz`.

## Notes

- Monitor geometry for wallpapers and per-screen matching is hard-coded for this
  machine (DP-3 primary, DP-1 left, DP-2 above, HDMI-A-1 portrait) in
  `wallpaper/src/render.py` and `apply.sh`.
- The UNSC emblem belongs to Microsoft/343 Industries and is kept out of the repo.
  Everything else is original or OFL/GPL-licensed.

## Lock and login screens

Plasma 6.8 takes the lock screen layout from the Plasma shell package and Plasma
Login Manager compiles its greeter, so neither accepts a custom layout from a theme.
`apply.sh` sets the lock screen wallpaper (render `--lock` for a version that keeps
the clock clear); for the login screen use **System Settings → Login Screen** and
apply your Plasma settings and wallpaper there.

## Using it on another machine

`install.sh`, `apply.sh` and the Plasma Style, window frame, app style, OSD, workspace
tabs and dashboard face work anywhere with Plasma 6. Two things are specific to the
original four-monitor setup:

- **Wallpapers:** edit the `SCREENS` table at the top of `wallpaper/src/render.py`
  (physical size in mm, resolution, position) and re-render. On a single monitor the
  primary-screen image alone is enough.
- **Per-screen wallpaper matching:** the `byPos` table in `apply.sh` maps screen
  positions (from `kscreen-doctor -o`) to image files. Unknown screens fall back to
  the primary image.

## License

GPL-3.0-or-later (see `LICENSE`). The Kvantum theme is a recolor of Tsu Jan's
KvAdaptaDark (GPL). Fonts in `fonts/` are under the SIL Open Font License; each
family's `*-OFL.txt` is included. Halo, UNSC and VISR are trademarks of Microsoft;
this is an unofficial fan theme and ships none of their artwork.
