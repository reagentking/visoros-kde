#!/usr/bin/env python3
"""Generate the VisorOS Plasma Style (desktoptheme) SVGs.

Every frame is a Plasma 9-slice (topleft/top/.../center) built from one small
style vocabulary: flat fill, hairline border, optional edge line, optional
chamfer. Colors come from Plasma's ColorScheme-* classes so the style follows
the active color scheme (colors/VisorOS.colors).

Usage: python3 generate.py            -> writes ./VisorOS/
"""
import json, os, shutil

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VisorOS")

STYLE = """<style id="current-color-scheme" type="text/css">
.ColorScheme-Text{color:#eef3f6}
.ColorScheme-Background{color:#1c2630}
.ColorScheme-Highlight{color:#e9f1f5}
.ColorScheme-ViewBackground{color:#121920}
.ColorScheme-NeutralText{color:#ffb547}
.ColorScheme-NegativeText{color:#ff5a52}
.ColorScheme-PositiveText{color:#7fe3b0}
</style>"""

PARTS = ["topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright"]


class Svg:
    def __init__(self):
        self.items, self.x, self.y, self.rowh, self.W = [], 0, 0, 0, 0

    def place(self, w, h):
        """Reserve a w*h slot on a loose grid so elements never overlap."""
        if self.x + w > 600:
            self.x, self.y, self.rowh = 0, self.y + self.rowh + 10, 0
        pos = (self.x, self.y)
        self.x += w + 10
        self.rowh = max(self.rowh, h)
        self.W = max(self.W, self.x)
        return pos

    def add(self, s):
        self.items.append(s)

    def write(self, path):
        H = self.y + self.rowh + 10
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{H}" viewBox="0 0 {self.W} {H}">\n')
            f.write(STYLE + "\n" + "\n".join(self.items) + "\n</svg>\n")


def rect(x, y, w, h, cls, op=1.0):
    if w <= 0 or h <= 0:
        return ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="{cls}" fill="currentColor" fill-opacity="{op}"/>'


def spacer(x, y, w, h):
    # Invisible rect that fixes the element's bounding box.
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" fill-opacity="0.002"/>'


def frame(svg, prefix, c, m=8, fill=None, border=None, edge=None, cut=0, mask=False):
    """Add one 9-slice frame.

    prefix  element prefix ("" or "focus-" or "north-hover-" ...)
    c       corner size (px), m: stretchable center size
    fill    (cls, opacity) flat fill, or None
    border  (cls, opacity, width) hairline on all sides, or None
    edge    (side, cls, opacity, thickness): a line on one edge, inset by the corners
    cut     chamfer size on the top-right corner (needs fill)
    mask    also emit mask-* elements (for blur/contrast shape)
    """
    ox, oy = svg.place(2 * c + m, 2 * c + m)
    geo = {
        "topleft": (0, 0, c, c), "top": (c, 0, m, c), "topright": (c + m, 0, c, c),
        "left": (0, c, c, m), "center": (c, c, m, m), "right": (c + m, c, c, m),
        "bottomleft": (0, c + m, c, c), "bottom": (c, c + m, m, c), "bottomright": (c + m, c + m, c, c),
    }
    for p in PARTS:
        x, y, w, h = geo[p]
        X, Y = ox + x, oy + y
        body = [spacer(X, Y, w, h)]
        if fill:
            if p == "topright" and cut:
                k = min(cut, c)
                body.append(f'<path d="M{X} {Y}H{X + w - k}L{X + w} {Y + k}V{Y + h}H{X}Z" class="{fill[0]}" fill="currentColor" fill-opacity="{fill[1]}"/>')
            else:
                body.append(rect(X, Y, w, h, *fill))
        if border:
            cls, op, b = border
            if "top" in p: body.append(rect(X, Y, w, b, cls, op))
            if "bottom" in p: body.append(rect(X, Y + h - b, w, b, cls, op))
            if p.endswith("left") or p == "left": body.append(rect(X, Y + ("top" in p) * b, b, h - ("top" in p) * b - ("bottom" in p) * b, cls, op))
            if p.endswith("right") or p == "right": body.append(rect(X + w - b, Y + ("top" in p) * b, b, h - ("top" in p) * b - ("bottom" in p) * b, cls, op))
        if edge:
            side, cls, op, t = edge
            if side == p == "top": body.append(rect(X, Y, w, t, cls, op))
            if side == p == "bottom": body.append(rect(X, Y + h - t, w, t, cls, op))
            if side == p == "left": body.append(rect(X, Y, t, h, cls, op))
            if side == p == "right": body.append(rect(X + w - t, Y, t, h, cls, op))
        svg.add(f'<g id="{prefix}{p}">{"".join(body)}</g>')
        if mask:
            svg.add(f'<g id="mask-{prefix}{p}">{spacer(X, Y, w, h)}<rect x="{X}" y="{Y}" width="{w}" height="{h}" fill="#000"/></g>')


def hints(svg, prefix, top, right=None, bottom=None, left=None, kind="margin"):
    right = top if right is None else right
    bottom = top if bottom is None else bottom
    left = top if left is None else left
    ox, oy = svg.place(max(left, right, 1) * 4 + 8, max(top, bottom, 1) + 2)
    for side, v in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        w, h = ((1, v) if side in ("top", "bottom") else (v, 1))
        svg.add(f'<rect id="{prefix}hint-{side}-{kind}" x="{ox}" y="{oy}" width="{w}" height="{h}" fill="#000" fill-opacity="0.002"/>')
        ox += max(left, right, 1) + 2


# ---------------------------------------------------------------- surfaces
def surface(path, c, margin, alpha, accent=False, rule=0.16):
    s = Svg()
    frame(s, "", c, fill=("ColorScheme-Background", alpha), border=("ColorScheme-Text", rule, 1),
          edge=("top", "ColorScheme-Highlight", 0.9, 2) if accent else None, mask=True)
    hints(s, "", margin)
    s.write(os.path.join(OUT, path))


def panel(path, alpha):
    s = Svg()
    frame(s, "", 4, fill=("ColorScheme-Background", alpha), border=("ColorScheme-Text", 0.14, 1), mask=True)
    hints(s, "", 3)
    hints(s, "thick-", 4)
    s.write(os.path.join(OUT, path))


def tasks():
    s = Svg()
    EDGE = {"": "bottom", "south-": "bottom", "north-": "top", "west-": "left", "east-": "right"}
    for pre, side in EDGE.items():
        # open, not focused: short line on the screen-edge side
        frame(s, pre + "normal-", 8, edge=(side, "ColorScheme-Text", 0.45, 2))
        # hover: faint light tint + brighter line
        frame(s, pre + "hover-", 8, fill=("ColorScheme-Highlight", 0.12), edge=(side, "ColorScheme-Text", 0.75, 2))
        # focused: the front-end selection chip (solid light fill, one cut corner)
        frame(s, pre + "focus-", 8, fill=("ColorScheme-Highlight", 1.0), cut=6)
        # needs attention: amber tint + amber line (shape + color)
        frame(s, pre + "attention-", 8, fill=("ColorScheme-NeutralText", 0.16), edge=(side, "ColorScheme-NeutralText", 1.0, 3))
        # minimized: dim line
        frame(s, pre + "minimized-", 8, edge=(side, "ColorScheme-Text", 0.22, 2))
        # progress overlay
        frame(s, pre + "progress-", 8, fill=("ColorScheme-PositiveText", 0.30))
    hints(s, "normal-", 3)
    # group expander triangles
    for side, d in (("top", "M0 6L4 1L8 6Z"), ("bottom", "M0 2L4 7L8 2Z"), ("left", "M6 0L1 4L6 8Z"), ("right", "M2 0L7 4L2 8Z")):
        ox, oy = s.place(8, 8)
        s.add(f'<g id="group-expander-{side}" transform="translate({ox} {oy})">{spacer(0, 0, 8, 8)}<path d="{d}" class="ColorScheme-Text" fill="currentColor" fill-opacity="0.7"/></g>')
    s.write(os.path.join(OUT, "widgets/tasks.svg"))


def pager():
    s = Svg()
    frame(s, "normal-", 3, border=("ColorScheme-Text", 0.22, 1))
    frame(s, "hover-", 3, fill=("ColorScheme-Highlight", 0.10), border=("ColorScheme-Text", 0.4, 1))
    frame(s, "active-", 3, fill=("ColorScheme-Highlight", 0.18), border=("ColorScheme-Highlight", 0.9, 1),
          edge=("bottom", "ColorScheme-Highlight", 1.0, 3))
    s.write(os.path.join(OUT, "widgets/pager.svg"))


def viewitem():
    s = Svg()
    frame(s, "normal-", 3)
    frame(s, "hover-", 3, fill=("ColorScheme-Highlight", 0.10))
    frame(s, "selected-", 3, fill=("ColorScheme-Highlight", 0.20), edge=("left", "ColorScheme-Highlight", 1.0, 3))
    frame(s, "selected+hover-", 3, fill=("ColorScheme-Highlight", 0.26), edge=("left", "ColorScheme-Highlight", 1.0, 3))
    s.write(os.path.join(OUT, "widgets/viewitem.svg"))


def listitem():
    s = Svg()
    frame(s, "normal-", 3)
    frame(s, "hover-", 3, fill=("ColorScheme-Highlight", 0.10))
    frame(s, "pressed-", 3, fill=("ColorScheme-Highlight", 0.22))
    frame(s, "section-", 3, edge=("bottom", "ColorScheme-Text", 0.2, 1))
    for pre in ("normal-", "pressed-", "section-"):
        hints(s, pre, 4, 6, 4, 6)
    s.write(os.path.join(OUT, "widgets/listitem.svg"))


def tabbar():
    s = Svg()
    # The bar sits on the side of the tab that faces the content.
    for pre, side in (("north-", "bottom"), ("south-", "top"), ("west-", "right"), ("east-", "left")):
        frame(s, pre + "active-tab-", 4, fill=("ColorScheme-Highlight", 0.16), edge=(side, "ColorScheme-Highlight", 1.0, 2))
        hints(s, pre + "active-tab-", 4, 8, 4, 8)
    s.write(os.path.join(OUT, "widgets/tabbar.svg"))


def heading():
    s = Svg()
    frame(s, "header-", 4, fill=("ColorScheme-Text", 0.04), edge=("bottom", "ColorScheme-Text", 0.16, 1))
    frame(s, "footer-", 4, fill=("ColorScheme-Text", 0.04), edge=("top", "ColorScheme-Text", 0.16, 1))
    hints(s, "", 6)
    s.write(os.path.join(OUT, "widgets/plasmoidheading.svg"))


def meta():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "metadata.json"), "w") as f:
        json.dump({
            "KPlugin": {
                "Id": "VisorOS",
                "Name": "VisorOS",
                "Description": "Flat front-end Plasma Style inspired by VISR OS",
                "Authors": [{"Name": "reagentking"}],
                "License": "GPL-3.0-or-later",
                "Version": "0.1",
            },
            "X-Plasma-API-Minimum-Version": "6.0",
        }, f, indent=2)
    with open(os.path.join(OUT, "plasmarc"), "w") as f:
        f.write("[ContrastEffect]\nenabled=true\ncontrast=0.25\nintensity=1.0\nsaturation=1.4\n\n"
                "[BlurBehindEffect]\nenabled=true\n\n[AdaptiveTransparency]\nenabled=false\n")


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    meta()
    # Translucent (blur on) and opaque variants of every surface, so Plasma never
    # falls back to Breeze's versions.
    for base, alpha in (("", 0.90), ("translucent/", 0.82), ("opaque/", 1.0), ("solid/", 1.0)):
        panel(base + "widgets/panel-background.svg", alpha)
        surface(base + "dialogs/background.svg", 4, 8, min(1.0, alpha + 0.06), accent=True)
        surface(base + "widgets/tooltip.svg", 3, 6, min(1.0, alpha + 0.06))
        surface(base + "widgets/background.svg", 4, 8, alpha)
    tasks(); pager(); viewitem(); listitem(); tabbar(); heading()
    for root, _, files in sorted(os.walk(OUT)):
        for fn in sorted(files):
            print(os.path.relpath(os.path.join(root, fn), OUT))


if __name__ == "__main__":
    main()
