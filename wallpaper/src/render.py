#!/usr/bin/env python3
"""Render the VisorOS spanning wallpaper.

One scene is drawn in physical millimetres across the real monitor layout,
then cut per screen at native resolution so the ring arc lines up across
bezels. Usage: python3 render.py [outdir]   (default: ../out next to this file)
"""
import math, os, sys
import cairo, numpy as np
from PIL import Image

# --- Monitor layout (mm). Positions derived from kscreen geometry, sizes from EDID.
# DP-3 is primary (right 1440p). DP-2 sits above it, HDMI-A-1 is portrait to its right.
GAP = 14.0                 # visual bezel gap
REF = 597.0 / 2560         # mm per logical px on the 1440p panels
SCREENS = {
    "DP-1":     dict(x=0.0,                       y=0.0,                    w=597, h=336, px=(2560, 1440)),
    "DP-3":     dict(x=597 + GAP,                 y=0.0,                    w=597, h=336, px=(2560, 1440)),
    "DP-2":     dict(x=597 + GAP + 366 * REF,     y=-(299 + GAP),           w=531, h=299, px=(1920, 1080)),
    "HDMI-A-1": dict(x=2 * 597 + 2 * GAP,         y=(987 - 1080) * REF,     w=299, h=531, px=(1080, 1920)),
}
TOP = min(s["y"] for s in SCREENS.values())
BOTTOM = max(s["y"] + s["h"] for s in SCREENS.values())
RIGHT = max(s["x"] + s["w"] for s in SCREENS.values())

def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def ridge(x0, x1, base, amp, seed, step=4.0):
    pts = []
    x = x0
    while x <= x1:
        y = base
        for k, (f, a) in enumerate([(0.004, 1.0), (0.011, 0.45), (0.031, 0.18), (0.07, 0.06)]):
            y -= amp * a * math.sin(x * f + seed * (k + 1) * 1.7)
        pts.append((x, y)); x += step
    return pts

def draw_scene(cr):
    # Sky: lifted, cool, brighter at the top ("lighter, more uplifting").
    sky = cairo.LinearGradient(0, TOP, 0, BOTTOM)
    for off, col in [(0.0, "#56788e"), (0.30, "#36536a"), (0.55, "#22374a"), (0.80, "#172431"), (1.0, "#121920")]:
        sky.add_color_stop_rgb(off, *rgb(col))
    cr.set_source(sky); cr.paint()

    # Soft light source high on the right, behind the ring.
    glow = cairo.RadialGradient(1080, TOP + 120, 0, 1080, TOP + 120, 760)
    glow.add_color_stop_rgba(0, *rgb("#e9f1f5"), 0.16)
    glow.add_color_stop_rgba(1, *rgb("#e9f1f5"), 0.0)
    cr.set_source(glow); cr.paint()

    # Ring arc: a broad band rising from the lower left, peaking over the upper screen.
    def arc_path(dy=0.0):
        cr.move_to(-120, 330 + dy)
        cr.curve_to(380, 0 + dy, 1250, -20 + dy, RIGHT + 120, 300 + dy)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for width, alpha in [(46, 0.035), (24, 0.05), (12, 0.07)]:
        arc_path(); cr.set_source_rgba(*rgb("#e9f1f5"), alpha); cr.set_line_width(width); cr.stroke()
    arc_path(-6); cr.set_source_rgba(*rgb("#f4f9fb"), 0.55); cr.set_line_width(1.6); cr.stroke()
    arc_path(5);  cr.set_source_rgba(*rgb("#a8dcf2"), 0.28); cr.set_line_width(0.9); cr.stroke()

    # Horizon haze.
    haze = cairo.LinearGradient(0, 200, 0, 300)
    haze.add_color_stop_rgba(0, *rgb("#a8dcf2"), 0.0)
    haze.add_color_stop_rgba(1, *rgb("#a8dcf2"), 0.06)
    cr.set_source(haze); cr.rectangle(-50, 200, RIGHT + 100, 100); cr.fill()

    # Two ridge lines of distant terrain.
    for base, amp, seed, col in [(268, 26, 1.3, "#1d2c38"), (306, 18, 4.1, "#151f28"), (430, 34, 2.6, "#0e1419")]:
        pts = ridge(-50, RIGHT + 50, base, amp, seed)
        cr.move_to(-50, BOTTOM + 50)
        for x, y in pts: cr.line_to(x, y)
        cr.line_to(RIGHT + 50, BOTTOM + 50); cr.close_path()
        cr.set_source_rgb(*rgb(col)); cr.fill()

# --- UNSC variant -----------------------------------------------------------
# Emblem placement in mm: centred on the primary screen (DP-3), a bit above middle.
P = SCREENS["DP-3"]
EMB_H = P["h"] * 0.56
EMB_CY = P["y"] + P["h"] * 0.46
EMB_CX = P["x"] + P["w"] / 2

def emblem_box(aspect):
    w = EMB_H * aspect
    return EMB_CX - w / 2, EMB_CY - EMB_H / 2, w, EMB_H

def draw_unsc(cr, aspect=1239 / 2006):
    bg = cairo.LinearGradient(0, TOP, 0, BOTTOM)
    for off, col in [(0.0, "#223445"), (0.45, "#16222d"), (1.0, "#0a0f14")]:
        bg.add_color_stop_rgb(off, *rgb(col))
    cr.set_source(bg); cr.paint()

    glow = cairo.RadialGradient(EMB_CX, EMB_CY, 0, EMB_CX, EMB_CY, 300)
    glow.add_color_stop_rgba(0, *rgb("#a8dcf2"), 0.10)
    glow.add_color_stop_rgba(1, *rgb("#a8dcf2"), 0.0)
    cr.set_source(glow); cr.paint()

    # Fine dot grid across the whole wall.
    cr.set_source_rgba(*rgb("#a8dcf2"), 0.08)
    gy = math.floor(TOP / 20) * 20
    while gy < BOTTOM:
        gx = 0.0
        while gx < RIGHT:
            cr.arc(gx, gy, 0.35, 0, 2 * math.pi); cr.fill()
            gx += 20
        gy += 20

    # Corner brackets around the emblem.
    x, y, w, h = emblem_box(aspect)
    pad, L = 16, 14
    x0, y0, x1, y1 = x - pad, y - pad, x + w + pad, y + h + pad
    cr.set_source_rgba(*rgb("#a8dcf2"), 0.45); cr.set_line_width(0.6)
    for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        cr.move_to(cx + dx * L, cy); cr.line_to(cx, cy); cr.line_to(cx, cy + dy * L); cr.stroke()

    # Stencil labels.
    cr.select_font_face("Share Tech Mono")
    cr.set_font_size(4.2); cr.set_source_rgba(*rgb("#e9f1f5"), 0.42)
    label = "VISR OS  //  FLEETCOM  //  NODE 01"
    ext = cr.text_extents(label)
    cr.move_to(EMB_CX - ext.width / 2, y1 + 11); cr.show_text(label)
    cr.set_font_size(3.2)
    for i, (name, s) in enumerate([("DP-3", SCREENS["DP-3"]), ("DP-1", SCREENS["DP-1"]),
                                   ("DP-2", SCREENS["DP-2"]), ("HDMI-A-1", SCREENS["HDMI-A-1"])], 1):
        pw, ph = s["px"]
        cr.set_source_rgba(*rgb("#a8dcf2"), 0.28)
        cr.move_to(s["x"] + 10, s["y"] + s["h"] - 10)
        cr.show_text(f"NODE {i:02d}  ·  {name}  ·  {pw}x{ph}")

    detail_orbital(cr, SCREENS["DP-1"])
    detail_sector(cr, SCREENS["DP-2"])
    detail_portrait(cr, SCREENS["HDMI-A-1"])

def _text(cr, x, y, txt, size, alpha, face="Share Tech Mono", bold=False, color="#a8dcf2", anchor="start"):
    cr.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size)
    ext = cr.text_extents(txt)
    dx = {"start": 0, "middle": -ext.width / 2, "end": -ext.width}[anchor]
    cr.set_source_rgba(*rgb(color), alpha)
    cr.move_to(x + dx, y); cr.show_text(txt); cr.new_path()
    return ext.width

def _line(cr, pts, alpha, width=0.4, color="#a8dcf2", dash=None):
    cr.set_source_rgba(*rgb(color), alpha); cr.set_line_width(width)
    cr.set_dash(dash or [])
    cr.move_to(*pts[0])
    for pt in pts[1:]: cr.line_to(*pt)
    cr.stroke(); cr.set_dash([])

def detail_orbital(cr, s):
    """Left 1440p: orbital plot around a planet limb."""
    X, Y, W, H = s["x"], s["y"], s["w"], s["h"]
    cx, cy, R = X + 110, Y + H + 95, 175
    cr.save(); cr.rectangle(X, Y, W, H); cr.clip()
    limb = cairo.RadialGradient(cx, cy - 40, R * 0.3, cx, cy, R)
    limb.add_color_stop_rgba(0, *rgb("#1f3242"), 0.0)
    limb.add_color_stop_rgba(1, *rgb("#2a4458"), 0.55)
    cr.set_source(limb); cr.arc(cx, cy, R, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(*rgb("#a8dcf2"), 0.38); cr.set_line_width(0.6); cr.arc(cx, cy, R, 0, 2 * math.pi); cr.stroke()
    cr.set_source_rgba(*rgb("#a8dcf2"), 0.10); cr.set_line_width(5); cr.arc(cx, cy, R + 3, 0, 2 * math.pi); cr.stroke()
    stations = [(235, -58, "ORBITAL DEFENSE PLATFORM 04"), (300, -38, "FLEET ANCHORAGE // DRYDOCK 2"), (380, -24, "L2 RELAY BUOY")]
    for r, deg, label in stations:
        cr.set_source_rgba(*rgb("#a8dcf2"), 0.16); cr.set_line_width(0.35); cr.set_dash([2.5, 2.0])
        cr.new_path(); cr.arc(cx, cy, r, 0, 2 * math.pi); cr.stroke(); cr.set_dash([])
        a = math.radians(deg); px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        cr.set_source_rgba(*rgb("#e9f1f5"), 0.55)
        cr.move_to(px, py - 2.2); cr.line_to(px + 2.2, py); cr.line_to(px, py + 2.2); cr.line_to(px - 2.2, py); cr.close_path(); cr.fill()
        _line(cr, [(px + 3, py - 3), (px + 14, py - 14), (px + 22, py - 14)], 0.3)
        _text(cr, px + 24, py - 13, label, 3.0, 0.42)
    _text(cr, X + W - 18, Y + 40, "SOL  //  EARTH  ·  ORBITAL PLOT", 4.2, 0.42, anchor="end")
    _text(cr, X + W - 18, Y + 47, "EPOCH 2560.327  ·  TRACKING 3 OBJECTS", 3.0, 0.28, anchor="end")
    sx, sy = X + W - 118, Y + H - 22
    _line(cr, [(sx, sy), (sx + 100, sy)], 0.3)
    for i in range(11):
        _line(cr, [(sx + i * 10, sy), (sx + i * 10, sy - (3 if i % 5 == 0 else 1.5))], 0.3)
    _text(cr, sx, sy + 5, "0", 2.6, 0.3); _text(cr, sx + 100, sy + 5, "10 000 KM", 2.6, 0.3, anchor="end")
    cr.restore()

def detail_sector(cr, s):
    """Upper 1080p: FLEETCOM sector map + roster."""
    X, Y, W, H = s["x"], s["y"], s["w"], s["h"]
    cr.save(); cr.rectangle(X, Y, W, H); cr.clip()
    _text(cr, X + 18, Y + 34, "FLEETCOM  //  SECTOR OVERVIEW", 4.4, 0.45)
    _text(cr, X + 18, Y + 41, "LAST SYNC 2560-11-23 21:47 UTC  ·  CLEARANCE: BRAVO", 3.0, 0.28)
    roster = [("FFG-201", 5, "ON STATION"), ("FFG-117", 4, "PATROL"), ("DDG-045", 3, "RESUPPLY"),
              ("CVN-009", 5, "ON STATION"), ("FFG-340", 2, "DRYDOCK")]
    for i, (hull, bars, status) in enumerate(roster):
        y = Y + 62 + i * 9
        _text(cr, X + 18, y, hull, 3.2, 0.38)
        for b in range(5):
            cr.set_source_rgba(*rgb("#a8dcf2"), 0.40 if b < bars else 0.10)
            cr.rectangle(X + 40 + b * 3.4, y - 2.6, 2.4, 2.8); cr.fill()
        _text(cr, X + 62, y, status, 3.0, 0.40 if status != "DRYDOCK" else 0.55,
              color="#a8dcf2" if status != "DRYDOCK" else "#ffb547")
    r = 13.0; hw = math.sqrt(3) * r
    ox, oy = X + W * 0.47, Y + H * 0.30
    hot = {(3, 2), (4, 2), (4, 3)}; secure = (5, 3)
    for row in range(7):
        for col in range(10):
            hx = ox + col * hw + (hw / 2 if row % 2 else 0); hy = oy + row * r * 1.5
            if hx > X + W - 10 or hy > Y + H - 18: continue
            cr.move_to(hx + r * math.cos(math.radians(30)), hy + r * math.sin(math.radians(30)))
            for k in range(1, 7):
                a = math.radians(30 + 60 * k); cr.line_to(hx + r * math.cos(a), hy + r * math.sin(a))
            cr.close_path()
            if (col, row) in hot:
                cr.set_source_rgba(*rgb("#a8dcf2"), 0.07); cr.fill_preserve()
            if (col, row) == secure:
                cr.set_source_rgba(*rgb("#e9f1f5"), 0.12); cr.fill_preserve()
                cr.set_source_rgba(*rgb("#e9f1f5"), 0.55); cr.set_line_width(0.5); cr.stroke()
                for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                    bx, by = hx + dx * (r + 4), hy + dy * (r + 2)
                    _line(cr, [(bx, by + -dy * 4), (bx, by), (bx + -dx * 4, by)], 0.5, 0.45, "#e9f1f5")
                _line(cr, [(hx + r + 5, hy - 6), (hx + r + 18, hy - 18), (hx + r + 30, hy - 18)], 0.35)
                _text(cr, hx + r + 32, hy - 17, "SECTOR 7-G  //  SECURE", 3.2, 0.5, color="#e9f1f5")
            else:
                cr.set_source_rgba(*rgb("#a8dcf2"), 0.09); cr.set_line_width(0.35); cr.stroke()
    cr.restore()

def detail_portrait(cr, s):
    """Portrait 1080p: range rail, vertical watermark, property decal."""
    X, Y, W, H = s["x"], s["y"], s["w"], s["h"]
    cr.save(); cr.rectangle(X, Y, W, H); cr.clip()
    # vertical watermark
    cr.save(); cr.translate(X + 44, Y + H - 40); cr.rotate(-math.pi / 2)
    _text(cr, 0, 0, "UNITED NATIONS SPACE COMMAND", 21, 0.06, face="Saira SemiCondensed", bold=True, color="#e9f1f5")
    cr.restore()
    # range rail on the right
    rx = X + W - 16
    _line(cr, [(rx, Y + 30), (rx, Y + H - 30)], 0.22)
    t, i = Y + 30, 0
    while t <= Y + H - 30:
        major = i % 5 == 0
        _line(cr, [(rx, t), (rx - (5 if major else 2), t)], 0.24)
        if major: _text(cr, rx - 7, t + 1, f"{i * 10:03d}", 2.6, 0.26, anchor="end")
        t += 10; i += 1
    _line(cr, [(rx - 9, Y + H * 0.42 - 2.5), (rx - 4, Y + H * 0.42), (rx - 9, Y + H * 0.42 + 2.5)], 0.6, 0.5, "#e9f1f5")
    # property decal plate
    px, py, pw, ph = X + 70, Y + H - 120, 150, 62
    cr.set_source_rgba(*rgb("#a8dcf2"), 0.04); cr.rectangle(px, py, pw, ph); cr.fill()
    cr.set_source_rgba(*rgb("#a8dcf2"), 0.30); cr.set_line_width(0.4); cr.rectangle(px, py, pw, ph); cr.stroke()
    cr.set_source_rgba(*rgb("#e9f1f5"), 0.45); cr.rectangle(px, py, 30, ph); cr.fill()
    cr.save(); cr.translate(px + 20, py + ph - 6); cr.rotate(-math.pi / 2)
    _text(cr, 0, 0, "UNSC", 11, 0.95, face="Saira SemiCondensed", bold=True, color="#0e141a")
    cr.restore()
    _text(cr, px + 36, py + 10, "PROPERTY OF THE UNSC", 3.6, 0.55, color="#e9f1f5")
    _text(cr, px + 36, py + 16, "WORKSTATION // VISR OS NODE 04", 2.8, 0.38)
    _text(cr, px + 36, py + 21, "UNAUTHORIZED ACCESS IS A FEDERAL OFFENSE", 2.4, 0.28)
    import random
    rnd = random.Random(117); bx = px + 36
    while bx < px + pw - 6:
        w = rnd.choice([0.4, 0.4, 0.8, 1.2])
        cr.set_source_rgba(*rgb("#e9f1f5"), 0.42); cr.rectangle(bx, py + 27, w, 20); cr.fill()
        bx += w + rnd.choice([0.4, 0.8, 1.2])
    _text(cr, px + 36, py + 54, "SN 0117-ACX-2557   LOT 34-B", 2.8, 0.4)
    cr.restore()

def composite_emblem(img, scale, ox, oy, emblem):
    """Paste the light emblem (with a soft glow) where it falls on this screen."""
    from PIL import ImageFilter
    aspect = emblem.width / emblem.height
    x, y, w, h = emblem_box(aspect)
    px, py = round((x - ox) * scale), round((y - oy) * scale)
    pw, ph = round(w * scale), round(h * scale)
    if px > img.width or py > img.height or px + pw < 0 or py + ph < 0:
        return img
    a = emblem.getchannel("A").resize((pw, ph), Image.LANCZOS)
    base = img.convert("RGBA")
    for color, strength, blur in (((168, 220, 242), 0.35, max(2, pw // 40)), ((233, 241, 245), 0.82, 0)):
        layer = Image.new("RGBA", (pw, ph), color + (0,))
        m = a.filter(ImageFilter.GaussianBlur(blur)) if blur else a
        layer.putalpha(m.point(lambda v: int(v * strength)))
        base.alpha_composite(layer, (px, py)) if px >= 0 and py >= 0 else base.paste(layer, (px, py), layer)
    return base.convert("RGB")

def render(scale_px_per_mm, ox, oy, w, h, draw=draw_scene):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    cr = cairo.Context(surf)
    cr.scale(scale_px_per_mm, scale_px_per_mm)
    cr.translate(-ox, -oy)
    draw(cr)
    surf.flush()
    buf = np.ndarray((h, w, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))
    rgbarr = buf[:, :, 2::-1].astype(np.float32)       # BGRx -> RGB
    rng = np.random.default_rng(7)
    rgbarr += rng.uniform(-1.2, 1.2, rgbarr.shape)        # dither to hide gradient banding
    return Image.fromarray(np.clip(rgbarr, 0, 255).astype(np.uint8), "RGB")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=os.path.join(os.path.dirname(__file__), "..", "out"))
    ap.add_argument("--theme", choices=["ring", "unsc"], default="ring")
    ap.add_argument("--emblem", help="RGBA emblem PNG for --theme unsc")
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)
    emblem = Image.open(args.emblem).convert("RGBA") if args.theme == "unsc" else None
    draw = (lambda cr: draw_unsc(cr, emblem.width / emblem.height)) if emblem else draw_scene
    prefix = "VisorOS-UNSC" if emblem else "VisorOS"

    for name, s in SCREENS.items():
        pw, ph = s["px"]
        sc = pw / s["w"]
        img = render(sc, s["x"], s["y"], pw, ph, draw)
        if emblem: img = composite_emblem(img, sc, s["x"], s["y"], emblem)
        path = os.path.join(out, f"{prefix}-{name}-{pw}x{ph}.png")
        img.save(path, optimize=True); print(path)

    # Preview of the whole wall with screen outlines (for docs).
    k = 1.0
    pw, ph = int((RIGHT + 40) * k), int((BOTTOM - TOP + 40) * k)
    prev = render(k, -20, TOP - 20, pw, ph, draw)
    if emblem: prev = composite_emblem(prev, k, -20, TOP - 20, emblem)
    from PIL import ImageDraw
    d = ImageDraw.Draw(prev)
    for n, s in SCREENS.items():
        x0, y0 = (s["x"] + 20) * k, (s["y"] - TOP + 20) * k
        d.rectangle([x0, y0, x0 + s["w"] * k, y0 + s["h"] * k], outline=(43, 52, 60), width=4)
    p = os.path.join(out, f"preview-{'unsc' if emblem else 'wall'}.png"); prev.save(p); print(p)

if __name__ == "__main__":
    main()
