"""Shared palette, fonts and SVG helpers for the profile artwork.

Every image in this profile comes in a dark and a light variant so it follows
the viewer's GitHub theme. Fonts are embedded as small WOFF subsets so the
artwork renders identically everywhere (GitHub serves SVGs as images, which
cannot load external fonts).
"""
from __future__ import annotations

import base64
import functools
import io
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT_DIR = ASSETS / "fonts"

# Graphite surfaces with a blue → cyan gradient accent.
PALETTES = {
    "dark": {
        "bg": "#0B0F17",
        "bg2": "#111827",
        "border": "#1F2937",
        "text": "#E6EAF2",
        "muted": "#8B95A7",
        "faint": "#566173",
        "accent": "#4F8CFF",
        "accent2": "#22D3EE",
        "accent_text": "#7AA8FF",
        "status": "#34D399",
        "track": "#161E2C",
        "dots": "#263044",
        "glow": "0.30",
    },
    "light": {
        "bg": "#FFFFFF",
        "bg2": "#F4F7FB",
        "border": "#E2E8F0",
        "text": "#0F172A",
        "muted": "#526075",
        "faint": "#94A3B8",
        "accent": "#2563EB",
        "accent2": "#06B6D4",
        "accent_text": "#1D4ED8",
        "status": "#059669",
        "track": "#EEF2F7",
        "dots": "#D3DAE5",
        "glow": "0.16",
    },
}

# key: (file, CSS family, fallback stack)
FONTS = {
    "display": ("SpaceGrotesk-Bold.woff", "MA Display", "'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif"),
    "medium": ("SpaceGrotesk-Medium.woff", "MA Text", "'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif"),
    "mono": ("JetBrainsMono-Medium.woff", "MA Mono", "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"),
}


def family(key: str) -> str:
    _, name, fallback = FONTS[key]
    return f"'{name}', {fallback}"


# Characters drawn with each font since the last svg() call, so every file
# embeds only the glyphs it needs.
_used: dict[str, set[str]] = {}


def use(key: str, content: str) -> None:
    _used.setdefault(key, set()).update(content)


@functools.cache
def _font_data(key: str, chars: str) -> bytes:
    path = FONT_DIR / FONTS[key][0]
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:  # no fontTools: embed the whole (already small) subset
        return path.read_bytes()
    font = TTFont(path)
    options = subset.Options()
    options.flavor = "woff"
    options.layout_features = ["*"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=chars + " ")
    subsetter.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff"
    font.save(buf)
    return buf.getvalue()


def font_css(*keys: str) -> str:
    rules = []
    for key in keys:
        chars = "".join(sorted(_used.get(key, ())))
        if not chars:
            continue
        data = base64.b64encode(_font_data(key, chars)).decode()
        rules.append(
            f"@font-face{{font-family:'{FONTS[key][1]}';"
            f"src:url(data:font/woff;base64,{data}) format('woff');}}"
        )
    return "".join(rules)


@functools.cache
def _metrics(key: str):
    from fontTools.ttLib import TTFont

    font = TTFont(FONT_DIR / FONTS[key][0])
    cmap = font.getBestCmap()
    hmtx = font["hmtx"].metrics
    upm = font["head"].unitsPerEm
    default = hmtx[".notdef"][0] if ".notdef" in hmtx else upm // 2
    return cmap, hmtx, upm, default


def measure(text: str, key: str, size: float, letter_spacing: float = 0.0) -> float:
    """Approximate advance width of ``text`` in px (no kerning or shaping)."""
    try:
        cmap, hmtx, upm, default = _metrics(key)
    except Exception:  # fonts not built yet: rough fallback
        return len(text) * size * 0.56
    units = 0
    for ch in text:
        glyph = cmap.get(ord(ch))
        units += hmtx[glyph][0] if glyph in hmtx else default
    return units * size / upm + letter_spacing * max(len(text) - 1, 0)


def wrap(text: str, key: str, size: float, width: float) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and measure(trial, key, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def esc(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def accent_gradient(gid: str, p: dict, x1="0", y1="0", x2="1", y2="1", units: str = "") -> str:
    u = f' gradientUnits="{units}"' if units else ""
    return (
        f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>'
        f'<stop offset="0" stop-color="{p["accent"]}"/><stop offset="1" stop-color="{p["accent2"]}"/>'
        f"</linearGradient>"
    )


def dot_grid(pid: str, gap: float, radius: float, fill: str) -> str:
    """<pattern> of small dots on a square grid."""
    h = gap / 2
    return (
        f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
        f'<circle cx="{h}" cy="{h}" r="{radius}" fill="{fill}"/></pattern>'
    )


def blur(fid: str, std: float) -> str:
    return (
        f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feGaussianBlur stdDeviation="{std}"/></filter>'
    )


def text(x, y, content, key, size, fill, *, anchor="start", spacing=0, extra=""):
    use(key, content)
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{esc(family(key))}" font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}"{ls}{extra}>{esc(content)}</text>'
    )


def svg(width: int, height: int, body: str, *, title: str, css: str = "") -> str:
    style = font_css(*FONTS) + css
    _used.clear()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
        f"<style>{style}</style>"
        f"{body}</svg>\n"
    )
