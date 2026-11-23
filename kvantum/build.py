#!/usr/bin/env python3
"""Build the VisorOS Kvantum theme by recoloring KvAdaptaDark (flat, small radii).

The cyan accent becomes the VisorOS light selection fill, the blue-greys become
the VisorOS slates, and every state that ends up on a light fill gets dark text.

Usage: python3 build.py     (reads base/KvAdaptaDark.*, writes VisorOS/)
"""
import configparser, io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "base")
OUT = os.path.join(HERE, "VisorOS")

SEL, INK, TEXT, SUB, ICE = "#e9f1f5", "#0e141a", "#eef3f6", "#93a4b1", "#a8dcf2"

COLOR_MAP = {
    # accent family -> light selection / ice
    "#00bcd4": SEL, "#4db6ac": SEL, "#00c3dc": SEL, "#008dd4": ICE, "#b74aff": ICE,
    "#2d4c4f": "#3a4f60", "#275f59": "#3a4f60",
    # marks drawn on the accent (radio dot etc.) -> dark ink
    "#fbfbfc": INK, "#f6feff": INK,
    # blue-greys -> VisorOS slates
    "#263238": "#1c2630", "#29353b": "#121920", "#2d393f": "#273440", "#314047": "#2f3f4d",
    "#1e282d": "#151d25", "#212c31": "#18212a", "#212b30": "#18212a", "#222d32": "#19222b",
    "#28343a": "#22303b", "#3e4a50": "#3a4a57", "#3d494f": "#3a4a57", "#39444a": "#34434f",
    "#304048": "#2c3b48", "#293439": "#1f2a35", "#252f35": "#1a242d", "#192023": "#10161c",
    "#141b1e": "#0c1116", "#556165": "#4a5a68", "#60727c": "#5c7080", "#6c787d": "#6b7d8b",
    "#717b81": "#7a8a97", "#7f898f": SUB, "#a6afb4": "#b8c6d0", "#acb1bc": "#b8c6d0",
    "#cfd8dc": "#dce6ec", "#e4e5e8": SEL, "#fafafa": TEXT,
    # neutral greys -> tinted
    "#969696": SUB, "#828282": "#7f909d", "#7b7b7b": "#788896", "#7d7d7d": "#788896",
    "#646464": "#5f6f7c", "#565b5e": "#53636f", "#141414": INK,
    # status colors -> VisorOS status
    "#f44336": "#ff5a52", "#f04a50": "#ff5a52", "#ff7a00": "#ffb547",
    "#00c867": "#7fe3b0", "#0cb400": "#7fe3b0",
}

GENERAL = {
    "window.color": "#1c2630", "base.color": "#121920", "alt.base.color": "#172029",
    "button.color": "#273440", "light.color": "#3a4a57", "mid.light.color": "#2f3f4d",
    "dark.color": "#0a0f14", "mid.color": "#151d25",
    "highlight.color": SEL, "inactive.highlight.color": "#b8c6d0",
    "text.color": TEXT, "window.text.color": TEXT, "button.text.color": TEXT,
    "disabled.text.color": "#eef3f660", "tooltip.text.color": TEXT,
    "highlight.text.color": INK, "link.color": ICE, "link.visited.color": "#c7b8ff",
    "progress.indicator.text.color": INK,
}

# Per-section text colors. Light-fill states (toggle/press on selection) -> INK.
SECTIONS = {
    "ItemView": {"text.normal.color": TEXT, "text.focus.color": TEXT, "text.press.color": INK, "text.toggle.color": INK},
    "MenuItem": {"text.normal.color": TEXT, "text.focus.color": INK},
    "MenuBarItem": {"text.normal.color": TEXT, "text.focus.color": INK},
    "PanelButtonCommand": {"text.normal.color": TEXT, "text.focus.color": TEXT, "text.press.color": TEXT, "text.toggle.color": INK},
    "ToolbarButton": {"text.normal.color": TEXT, "text.focus.color": TEXT, "text.press.color": TEXT, "text.toggle.color": INK},
    "HeaderSection": {"text.normal.color": SUB, "text.focus.color": TEXT, "text.press.color": INK, "text.toggle.color": INK},
    "Tab": {"text.normal.color": SUB, "text.focus.color": TEXT, "text.toggle.color": TEXT},
    "Progressbar": {"text.normal.color": TEXT, "text.focus.color": TEXT, "text.press.color": TEXT, "text.toggle.color": TEXT},
    "ComboBox": {"text.normal.color": TEXT, "text.focus.color": TEXT, "text.press.color": TEXT, "text.toggle.color": TEXT},
    "Toolbar": {"text.normal.color": TEXT, "text.focus.color": TEXT},
    "TitleBar": {"text.normal.color": SUB, "text.focus.color": TEXT},
    "GroupBox": {"text.normal.color": SUB, "text.focus.color": TEXT},
}

HACKS = {"respect_darkness": "true"}
GENERAL_SECTION = {
    "comment": "VisorOS: recolor of KvAdaptaDark by Tsu Jan (GPL)",
    "translucent_windows": "false", "blurring": "false", "popup_blurring": "true",
    "menu_blur_radius": "0", "tooltip_blur_radius": "0", "animate_states": "true",
}


def recolor_svg(src, dst):
    s = open(src).read()
    pat = re.compile("|".join(re.escape(k) for k in COLOR_MAP), re.I)
    s, n = pat.subn(lambda m: COLOR_MAP[m.group(0).lower()], s)
    open(dst, "w").write(s)
    return n


def build_kvconfig(src, dst):
    cp = configparser.RawConfigParser(strict=False, interpolation=None)
    cp.optionxform = str
    cp.read(src)
    for k, v in GENERAL.items():
        cp["GeneralColors"][k] = v
    for sec, kv in SECTIONS.items():
        if not cp.has_section(sec):
            cp.add_section(sec)
        for k, v in kv.items():
            cp[sec][k] = v
    for k, v in GENERAL_SECTION.items():
        cp["%General"][k] = v
    for k, v in HACKS.items():
        cp["Hacks"][k] = v
    # Any leftover pure-white text colors elsewhere -> VisorOS text.
    for sec in cp.sections():
        for k, v in cp[sec].items():
            if k.startswith("text.") and v.lower() in ("white", "#ffffff") and sec not in SECTIONS:
                cp[sec][k] = TEXT
    buf = io.StringIO(); cp.write(buf, space_around_delimiters=False)
    open(dst, "w").write(buf.getvalue())


def main():
    os.makedirs(OUT, exist_ok=True)
    n = recolor_svg(os.path.join(BASE, "KvAdaptaDark.svg"), os.path.join(OUT, "VisorOS.svg"))
    build_kvconfig(os.path.join(BASE, "KvAdaptaDark.kvconfig"), os.path.join(OUT, "VisorOS.kvconfig"))
    left = sorted(set(c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}", open(os.path.join(OUT, "VisorOS.svg")).read())) - set(v.lower() for v in COLOR_MAP.values()))
    print(f"recolored {n} color uses; unmapped colors left: {left}")


if __name__ == "__main__":
    main()
