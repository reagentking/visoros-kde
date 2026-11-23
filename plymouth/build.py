#!/usr/bin/env python3
"""Build the VisorOS Plymouth theme (back-end green boot log).

Plymouth runs before user fonts are available, so every piece of text is
pre-rendered to PNG here with the theme fonts. Sizes are for a 2560px-wide
screen; visoros.script scales them to the actual display.

Usage: python3 build.py      -> writes ./visoros/
Install (root):  sudo cp -r visoros /usr/share/plymouth/themes/
                 sudo plymouth-set-default-theme -R visoros
"""
import os, shutil
import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "visoros")
GREEN, DIM = (0x6d / 255, 0xff / 255, 0x8f / 255), (0x2e / 255, 0x7a / 255, 0x45 / 255)

LOG = [  # (label, detail) — revealed one by one as boot progress advances
    ("systemd", "INIT"),
    ("udev", "DEVICES"),
    ("amdgpu / kms", "DISPLAY"),
    ("filesystems", "MOUNTED"),
    ("network", "LINK"),
    ("plasmalogin", "GREETER"),
]


def text_png(path, text, size, face, rgb, bold=False, spacing=0.0, pad=4):
    """Render one line of text to a tight PNG with optional letter spacing."""
    weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
    probe = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1))
    probe.select_font_face(face, cairo.FONT_SLANT_NORMAL, weight); probe.set_font_size(size)
    widths = [probe.text_extents(c).x_advance for c in text]
    fe = probe.font_extents()
    w = int(sum(widths) + spacing * max(0, len(text) - 1) + 2 * pad)
    h = int(fe[0] + fe[1] + 2 * pad)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, max(w, 1), max(h, 1))
    cr = cairo.Context(surf)
    cr.select_font_face(face, cairo.FONT_SLANT_NORMAL, weight); cr.set_font_size(size)
    x = pad
    for c, adv in zip(text, widths):
        cr.set_source_rgb(*rgb); cr.move_to(x, pad + fe[0]); cr.show_text(c)
        x += adv + spacing
    surf.write_to_png(path)


def rect_png(path, w, h, rgb, alpha=1.0):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(surf); cr.set_source_rgba(*rgb, alpha); cr.paint()
    surf.write_to_png(path)


def main():
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    mono, disp = "Share Tech Mono", "Saira SemiCondensed"
    text_png(f"{OUT}/title.png", "VISR OS", 150, disp, GREEN, bold=True, spacing=34)
    text_png(f"{OUT}/header.png", "VISR OS  //  CACHYOS  //  BOOT", 26, mono, GREEN, spacing=4)
    for i, (label, detail) in enumerate(LOG, 1):
        dots = "." * max(3, 30 - len(label))
        text_png(f"{OUT}/ok{i}.png", "[ OK ]", 24, mono, DIM)
        text_png(f"{OUT}/line{i}.png", f"{label} {dots} {detail}", 24, mono, GREEN)
    rect_png(f"{OUT}/seg_on.png", 64, 16, GREEN)
    rect_png(f"{OUT}/seg_off.png", 64, 16, DIM, 0.45)
    shutil.copy(os.path.join(HERE, "visoros.script"), OUT)
    shutil.copy(os.path.join(HERE, "visoros.plymouth"), OUT)
    print("\n".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()
