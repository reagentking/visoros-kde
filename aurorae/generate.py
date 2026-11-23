#!/usr/bin/env python3
"""Generate the VisorOS Aurorae window decoration.

Flat raised-slate title bar, 1px hairline frame, a 2px light rule along the top
of the focused window, square buttons (close turns red on hover), and a soft
stepped shadow drawn inside the SVG padding.

Usage: python3 generate.py      -> writes ./VisorOS/
"""
import os, shutil

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VisorOS")

# Palette (matches colors/VisorOS.colors)
SLATE, RAISED, RULE, RULE_DIM = "#1c2630", "#273440", "#3a4a57", "#2b3640"
TEXT, SUB, SEL, INK, RED = "#eef3f6", "#93a4b1", "#e9f1f5", "#0e141a", "#ff5a52"

P = 14          # shadow padding around the frame
T = 28          # title bar height
B = 1           # frame border
BTN = 28        # button cell size
C = 4           # stretchable centre size in the template


def shadow(x, y, w, h, side):
    """Stepped shadow strips inside a padding cell. side: which way is 'outward'."""
    out = []
    steps = P
    for i in range(steps):
        a = 0.20 * (1 - i / steps) ** 2
        if a < 0.004:
            continue
        if side == "top":    out.append((x, y + P - 1 - i, w, 1, a))
        if side == "bottom": out.append((x, y + i, w, 1, a))
        if side == "left":   out.append((x + P - 1 - i, y, 1, h, a))
        if side == "right":  out.append((x + i, y, 1, h, a))
    return "".join(f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" fill="#000" fill-opacity="{A:.3f}"/>' for X, Y, W, H, A in out)


def corner_shadow(x, y, cx, cy):
    """Quarter-ring shadow for a padding corner; (cx,cy) is the frame corner point."""
    rings = []
    for i in range(P, 0, -1):
        a = 0.20 * (1 - (i - 1) / P) ** 2
        if a < 0.004:
            continue
        rings.append(f'<circle cx="{cx}" cy="{cy}" r="{i}" fill="#000" fill-opacity="{a / 3:.3f}"/>')
    return f'<g clip-path="url(#clip-{x}-{y})">' + "".join(rings) + "</g>", f'<clipPath id="clip-{x}-{y}"><rect x="{x}" y="{y}" width="{P}" height="{P}"/></clipPath>'


def spacer(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" fill-opacity="0.002"/>'


def decoration_frame(ox, oy, prefix, active, defs):
    """9-slice frame: top row = shadow + title bar; sides/bottom = shadow + 1px border."""
    title = RAISED if active else SLATE
    border = RULE if active else RULE_DIM
    L = P + B                 # left/right column width
    TOP = P + T               # top row height
    BOT = B + P               # bottom row height
    W = L * 2 + C
    parts = {}

    # top-left: shadow (top + left + corner) + title bar start + border
    g = [spacer(ox, oy, L, TOP)]
    cs, cd = corner_shadow(ox, oy, ox + P, oy + P); defs.append(cd); g.append(cs)
    g.append(shadow(ox, oy + P, P, T, "left"))
    g.append(f'<rect x="{ox + P}" y="{oy + P}" width="{B}" height="{T}" fill="{border}"/>')
    parts["topleft"] = g

    # top: shadow strip + title fill + top rule + bottom hairline
    x = ox + L
    g = [spacer(x, oy, C, TOP), shadow(x, oy, C, P, "top"),
         f'<rect x="{x}" y="{oy + P}" width="{C}" height="{T}" fill="{title}"/>',
         f'<rect x="{x}" y="{oy + P + T - 1}" width="{C}" height="1" fill="{border}"/>']
    g.append(f'<rect x="{x}" y="{oy + P}" width="{C}" height="2" fill="{SEL if active else border}"/>')
    parts["top"] = g

    # the title bar continues under the corner cells too
    for name in ("topleft",):
        parts[name].append(f'<rect x="{ox + P + B}" y="{oy + P}" width="0" height="0"/>')

    x = ox + L + C
    g = [spacer(x, oy, L, TOP)]
    cs, cd = corner_shadow(x + B, oy, x + B, oy + P); defs.append(cd); g.append(cs)
    g.append(shadow(x + B, oy + P, P, T, "right"))
    g.append(f'<rect x="{x}" y="{oy + P}" width="{B}" height="{T}" fill="{border}"/>')
    parts["topright"] = g

    # middle row
    y = oy + TOP
    parts["left"] = [spacer(ox, y, L, C), shadow(ox, y, P, C, "left"), f'<rect x="{ox + P}" y="{y}" width="{B}" height="{C}" fill="{border}"/>']
    # Filled, not transparent: KWin's border-size setting can widen the frame
    # beyond the 1px hairline, and that extra space is drawn from the centre.
    parts["center"] = [spacer(ox + L, y, C, C), f'<rect x="{ox + L}" y="{y}" width="{C}" height="{C}" fill="{SLATE}"/>']
    parts["right"] = [spacer(ox + L + C, y, L, C), shadow(ox + L + C + B, y, P, C, "right"), f'<rect x="{ox + L + C}" y="{y}" width="{B}" height="{C}" fill="{border}"/>']

    # bottom row
    y = oy + TOP + C
    g = [spacer(ox, y, L, BOT)]
    cs, cd = corner_shadow(ox, y + B, ox + P, y + B); defs.append(cd); g.append(cs)
    g.append(f'<rect x="{ox + P}" y="{y}" width="{B}" height="{B}" fill="{border}"/>')
    parts["bottomleft"] = g
    parts["bottom"] = [spacer(ox + L, y, C, BOT), f'<rect x="{ox + L}" y="{y}" width="{C}" height="{B}" fill="{border}"/>', shadow(ox + L, y + B, C, P, "bottom")]
    g = [spacer(ox + L + C, y, L, BOT)]
    cs, cd = corner_shadow(ox + L + C + B, y + B, ox + L + C + B, y + B); defs.append(cd); g.append(cs)
    g.append(f'<rect x="{ox + L + C}" y="{y}" width="{B}" height="{B}" fill="{border}"/>')
    parts["bottomright"] = g

    out = []
    for name, body in parts.items():
        out.append(f'<g id="{prefix}-{name}">{"".join(body)}</g>')
    return out, W, TOP + C + BOT


def maximized_frame(ox, oy, prefix, active):
    """Maximized windows: no shadow/border, only the title bar (drawn as centre)."""
    title = RAISED if active else SLATE
    rule = SEL if active else RULE_DIM
    body = [spacer(ox, oy, C, T), f'<rect x="{ox}" y="{oy}" width="{C}" height="{T}" fill="{title}"/>',
            f'<rect x="{ox}" y="{oy}" width="{C}" height="2" fill="{rule}"/>',
            f'<rect x="{ox}" y="{oy + T - 1}" width="{C}" height="1" fill="{RULE_DIM}"/>']
    out = [f'<g id="{prefix}-center">{"".join(body)}</g>']
    for side in ("topleft", "top", "topright", "left", "right", "bottomleft", "bottom", "bottomright"):
        out.append(f'<g id="{prefix}-{side}">{spacer(ox + 40, oy, 1, 1)}</g>')
    return out


def write_decoration():
    defs, items = [], []
    x = 0
    for prefix, active in (("decoration", True), ("decoration-inactive", False)):
        g, w, h = decoration_frame(x, 0, prefix, active, defs)
        items += g; x += w + 20
    # mask: the window shape without shadow
    L, TOP, BOT = P + B, P + T, B + P
    mx = x
    for name, (px, py, pw, ph) in {
        "topleft": (0, 0, L, TOP), "top": (L, 0, C, TOP), "topright": (L + C, 0, L, TOP),
        "left": (0, TOP, L, C), "center": (L, TOP, C, C), "right": (L + C, TOP, L, C),
        "bottomleft": (0, TOP + C, L, BOT), "bottom": (L, TOP + C, C, BOT), "bottomright": (L + C, TOP + C, L, BOT),
    }.items():
        X, Y = mx + px, py
        # opaque only over the frame area (inside the padding)
        ix, iy = X + (P if "left" in name else 0), Y + (P if "top" in name else 0)
        iw = pw - (P if ("left" in name or "right" in name) else 0)
        ih = ph - (P if ("top" in name or "bottom" in name) else 0)
        items.append(f'<g id="mask-{name}">{spacer(X, Y, pw, ph)}<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="#000"/></g>')
    x += 2 * L + C + 20
    items += maximized_frame(x, 0, "decoration-maximized", True); x += C + 50
    items += maximized_frame(x, 0, "decoration-maximized-inactive", False); x += C + 50
    H = P + T + C + B + P
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="{H}" viewBox="0 0 {x} {H}">'
           f'<defs>{"".join(defs)}</defs>{"".join(items)}</svg>')
    open(os.path.join(OUT, "decoration.svg"), "w").write(svg)


# ------------------------------------------------------------------ buttons
GLYPHS = {
    "minimize": '<rect x="9" y="16" width="10" height="1.6"/>',
    "maximize": '<path d="M9 9h10v10H9z" fill="none" stroke-width="1.6"/>',
    "restore":  '<path d="M11 9h8v8M9 11h8v8H9z" fill="none" stroke-width="1.6"/>',
    "close":    '<path d="M9.5 9.5l9 9M18.5 9.5l-9 9" fill="none" stroke-width="1.7"/>',
    "alldesktops": '<rect x="9" y="9" width="4" height="4"/><rect x="15" y="9" width="4" height="4"/><rect x="9" y="15" width="4" height="4"/><rect x="15" y="15" width="4" height="4"/>',
    "keepabove": '<path d="M9 16l5-5 5 5" fill="none" stroke-width="1.6"/>',
    "keepbelow": '<path d="M9 12l5 5 5-5" fill="none" stroke-width="1.6"/>',
    "shade":    '<rect x="9" y="11" width="10" height="1.6"/><path d="M9 15l5 3 5-3" fill="none" stroke-width="1.4"/>',
    "help":     '<path d="M11 12a3 3 0 1 1 4 2.8c-.8.4-1 .9-1 1.7" fill="none" stroke-width="1.6"/><rect x="13.2" y="18" width="1.6" height="1.6"/>',
}


def button(name):
    close = name == "close"
    states = [
        # prefix, background, bg opacity, glyph color
        ("active", None, 0, TEXT),
        ("hover", RED if close else SEL, 1.0 if close else 0.14, "#ffffff" if close else TEXT),
        ("pressed", RED if close else SEL, 0.75 if close else 0.28, "#ffffff" if close else TEXT),
        ("inactive", None, 0, SUB),
        ("hover-inactive", RED if close else SEL, 1.0 if close else 0.14, "#ffffff" if close else TEXT),
        ("pressed-inactive", RED if close else SEL, 0.75 if close else 0.28, "#ffffff" if close else TEXT),
        ("deactivated", None, 0, RULE),
        ("deactivated-inactive", None, 0, RULE_DIM),
    ]
    items, x = [], 0
    for prefix, bg, op, fg in states:
        g = [spacer(x, 0, BTN, BTN)]
        if bg:
            g.append(f'<rect x="{x + 2}" y="2" width="{BTN - 4}" height="{BTN - 4}" fill="{bg}" fill-opacity="{op}"/>')
        g.append(f'<g transform="translate({x} 0)" fill="{fg}" stroke="{fg}" stroke-linecap="square">{GLYPHS[name]}</g>')
        items.append(f'<g id="{prefix}-center">{"".join(g)}</g>')
        x += BTN + 6
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="{BTN}" viewBox="0 0 {x} {BTN}">{"".join(items)}</svg>'
    open(os.path.join(OUT, f"{name}.svg"), "w").write(svg)


def rc():
    open(os.path.join(OUT, "VisorOSrc"), "w").write(f"""[General]
ActiveTextColor=238,243,246
InactiveTextColor=147,164,177
TitleAlignment=Left
TitleVerticalAlignment=Center
Animation=120
UseTextShadow=false

[Layout]
BorderLeft={B}
BorderRight={B}
BorderBottom={B}
BorderLeftMaximized=0
BorderRightMaximized=0
BorderBottomMaximized=0
TitleEdgeTop=0
TitleEdgeBottom=0
TitleEdgeLeft=6
TitleEdgeRight=2
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=6
TitleEdgeRightMaximized=2
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight={T}
ButtonWidth={BTN}
ButtonHeight={BTN}
ButtonSpacing=0
ButtonMarginTop=0
ButtonMarginTopMaximized=0
ExplicitButtonSpacer=8
PaddingTop={P}
PaddingBottom={P}
PaddingLeft={P}
PaddingRight={P}
""")


def metadata():
    open(os.path.join(OUT, "metadata.desktop"), "w").write("""[Desktop Entry]
Name=VisorOS
Comment=Flat front-end window frame inspired by VISR OS
X-KDE-PluginInfo-Name=VisorOS
X-KDE-PluginInfo-Author=reagentking
X-KDE-PluginInfo-Version=0.1
X-KDE-PluginInfo-License=GPL-3.0-or-later
""")


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    write_decoration()
    for n in GLYPHS:
        button(n)
    rc(); metadata()
    print("\n".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()
