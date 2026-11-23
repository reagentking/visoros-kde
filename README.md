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
| `scripts/` | Backup/restore, panel layout | |

## Use

```bash
python3 wallpaper/src/render.py wallpaper/out                 # ring wallpaper set
python3 wallpaper/src/render.py wallpaper/out --theme unsc \
        --emblem wallpaper/private/unsc-emblem.png             # UNSC set (needs your own emblem cut-out)
scripts/backup.sh pre-visr       # snapshot the current look first
./install.sh                     # symlink everything into ~/.local/share and ~/.config
./apply.sh                       # switch the session over (WALLPAPER=ring for the ring set)
scripts/apply-panels.sh          # one top taskbar per screen, apps from that screen only
```

Roll back with `scripts/restore.sh backups/<name>.tar.gz`.

## Notes

- Monitor geometry for wallpapers and per-screen matching is hard-coded for this
  machine (DP-3 primary, DP-1 left, DP-2 above, HDMI-A-1 portrait) in
  `wallpaper/src/render.py` and `apply.sh`.
- The UNSC emblem belongs to Microsoft/343 Industries and is kept out of the repo.
  Everything else is original or OFL/GPL-licensed.
