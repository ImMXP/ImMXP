"""Generate the static profile artwork (banner, headers, project cards, footer).

    python scripts/build_assets.py

Writes a ``-dark`` and ``-light`` SVG for every piece into ``assets/``.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import ASSETS, PALETTES, accent_gradient, blur, dot_grid, measure, svg, text, wrap  # noqa: E402

W = 1200

SECTIONS = [
    ("about", "01", "About me"),
    ("toolkit", "02", "Toolkit"),
    ("projects", "03", "Featured projects"),
    ("activity", "04", "GitHub activity"),
]

PROJECTS = [
    {
        "slug": "employee-management-system",
        "lang": ("Java", "#B07219"),
        "title": "Employee Management System",
        "text": "Console app that manages Managers, Engineers and Interns behind an "
        "admin login, with role-specific pay through inheritance and polymorphism.",
        "tags": ["Java", "OOP", "UML"],
        "date": "Nov 2025",
    },
    {
        "slug": "password-generator-cli",
        "lang": ("Java", "#B07219"),
        "title": "Password Generator CLI",
        "text": "Command-line tool that generates lowercase, uppercase and mixed-case "
        "passwords of 6–18 characters in one run, with input validation.",
        "tags": ["Java", "CLI", "Exceptions"],
        "date": "Dec 2025",
    },
    {
        "slug": "quran-telegram-bot",
        "lang": ("Python", "#3572A5"),
        "title": "Quran Telegram Bot",
        "text": "Arabic Telegram bot with a keyboard menu that replies with selected "
        "Quran verses, built on python-telegram-bot.",
        "tags": ["Python", "Telegram API", "asyncio"],
        "date": "Apr 2025",
    },
]


def frame(width: float, height: float, p: dict, radius: float) -> str:
    return (
        f'<rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="{radius - 0.5}" '
        f'fill="none" stroke="{p["border"]}" stroke-width="1.5"/>'
    )


def drift(dx: float, dy: float, dur: float) -> str:
    return (
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" '
        f'dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>'
    )


# ── Banner ────────────────────────────────────────────────────────────────────
def banner(theme: str) -> str:
    p = PALETTES[theme]
    H = 420
    cx, cy, tile = 976, 210, 168

    defs = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p['bg']}"/><stop offset="1" stop-color="{p['bg2']}"/></linearGradient>
{dot_grid('dots', 22, 1.3, p['dots'])}
<radialGradient id="dotFade" cx="0.8" cy="0.5" r="0.62"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="dotMask"><rect width="{W}" height="{H}" fill="url(#dotFade)"/></mask>
{accent_gradient('tileGrad', p)}
{accent_gradient('nameGrad', p, x2="1", y2="0")}
<linearGradient id="shine" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.30"/><stop offset="0.55" stop-color="#fff" stop-opacity="0"/></linearGradient>
{blur('soft', 70)}
{blur('shadow', 22)}
<clipPath id="clip"><rect width="{W}" height="{H}" rx="28"/></clipPath>
</defs>"""

    backdrop = f"""<g clip-path="url(#clip)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotMask)"/>
<g filter="url(#soft)" opacity="{p['glow']}">
<ellipse cx="1030" cy="110" rx="230" ry="150" fill="{p['accent']}">{drift(-50, 30, 18)}</ellipse>
<ellipse cx="880" cy="340" rx="210" ry="130" fill="{p['accent2']}">{drift(60, -24, 22)}</ellipse>
<ellipse cx="160" cy="-40" rx="280" ry="110" fill="{p['accent']}" opacity="0.6">{drift(40, 10, 26)}</ellipse>
</g>
</g>"""

    def orbit(r: float, dur: float, color: str, size: float, reverse: bool = False) -> str:
        sweep = 0 if reverse else 1
        path = f"M{cx + r},{cy} A{r},{r} 0 1,{sweep} {cx - r},{cy} A{r},{r} 0 1,{sweep} {cx + r},{cy}"
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{p["border"]}" stroke-width="1.2"/>'
            f'<circle r="{size}" fill="{color}"><animateMotion path="{path}" dur="{dur}s" repeatCount="indefinite"/></circle>'
        )

    h = tile / 2
    emblem = f"""{orbit(186, 26, p['status'], 4, reverse=True)}{orbit(138, 16, p['accent2'], 5)}
<rect x="{cx - h}" y="{cy - h + 18}" width="{tile}" height="{tile}" rx="44" fill="{p['accent']}" opacity="0.45" filter="url(#shadow)"/>
<rect x="{cx - h}" y="{cy - h}" width="{tile}" height="{tile}" rx="44" fill="url(#tileGrad)"/>
<rect x="{cx - h}" y="{cy - h}" width="{tile}" height="{tile}" rx="44" fill="url(#shine)"/>
<rect x="{cx - h + 0.75}" y="{cy - h + 0.75}" width="{tile - 1.5}" height="{tile - 1.5}" rx="43.5" fill="none" stroke="#fff" stroke-opacity="0.28" stroke-width="1.5"/>
{text(cx, cy + 26, '0x', 'display', 76, '#FFFFFF', anchor='middle', spacing=-2)}"""

    x = 72
    handle = "@ImMXP"
    pill_w = 44 + measure(handle, "mono", 15)
    chips, cxp = [], x
    for label in ["AI & Data", "Java", "Python", "SQL"]:
        w = measure(label, "mono", 15) + 30
        chips.append(
            f'<rect x="{cxp:.1f}" y="286" width="{w:.1f}" height="34" rx="17" fill="{p["track"]}" stroke="{p["border"]}"/>'
            + text(cxp + w / 2, 308, label, "mono", 15, p["muted"], anchor="middle")
        )
        cxp += w + 10

    name_split = x + measure("Moha", "display", 104, -3) + 1
    content = f"""
<rect x="{x}" y="112" width="{pill_w:.1f}" height="32" rx="16" fill="{p['track']}" stroke="{p['border']}"/>
<circle cx="{x + 18}" cy="128" r="5" fill="url(#tileGrad)"/>
{text(x + 32, 133, handle, 'mono', 15, p['muted'])}
{text(x - 4, 250, 'Moha', 'display', 104, p['text'], spacing=-3)}
{text(name_split - 4, 250, '0x', 'display', 104, 'url(#nameGrad)', spacing=-3)}
{''.join(chips)}"""

    title = "Moha0x"
    return svg(W, H, defs + backdrop + emblem + content + frame(W, H, p, 28), title=title)


# ── Section headers ───────────────────────────────────────────────────────────
def header(theme: str, index: str, title: str) -> str:
    p = PALETTES[theme]
    H = 72
    base = 46
    t_end = 66 + measure(title, "display", 30, -0.5)
    line_x = t_end + 24
    body = f"""<defs>
<linearGradient id="rule" gradientUnits="userSpaceOnUse" x1="{line_x:.1f}" y1="0" x2="{W}" y2="0">
<stop offset="0" stop-color="{p['accent']}"/><stop offset="0.12" stop-color="{p['accent2']}" stop-opacity="0.7"/>
<stop offset="0.35" stop-color="{p['border']}"/><stop offset="1" stop-color="{p['border']}" stop-opacity="0"/>
</linearGradient></defs>
<rect x="1" y="{base - 25}" width="48" height="28" rx="14" fill="{p['accent']}" fill-opacity="0.10" stroke="{p['accent']}" stroke-opacity="0.35"/>
{text(25, base - 6, index, 'mono', 14, p['accent_text'], anchor='middle')}
{text(66, base, title, 'display', 30, p['text'], spacing=-0.5)}
<rect x="{line_x:.1f}" y="{base - 11}" width="{W - line_x:.1f}" height="1.5" fill="url(#rule)"/>"""
    return svg(W, H, body, title=f"{index} · {title}")


# ── Project cards ─────────────────────────────────────────────────────────────
CARD_W, CARD_H = 580, 252


def card_base(p: dict, pid: str, glow_color: str, strength: float) -> str:
    return f"""<defs>
{dot_grid(pid + 'd', 18, 1.1, p['dots'])}
<radialGradient id="{pid}f" cx="1" cy="0" r="0.75"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="{pid}m"><rect width="{CARD_W}" height="{CARD_H}" fill="url(#{pid}f)"/></mask>
<linearGradient id="{pid}t" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p['accent']}"/><stop offset="0.45" stop-color="{p['accent2']}" stop-opacity="0.6"/><stop offset="1" stop-color="{p['accent2']}" stop-opacity="0"/></linearGradient>
{blur(pid + 'b', 46)}
<clipPath id="{pid}c"><rect width="{CARD_W}" height="{CARD_H}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#{pid}c)">
<rect width="{CARD_W}" height="{CARD_H}" fill="{p['bg']}"/>
<circle cx="{CARD_W - 30}" cy="0" r="120" fill="{glow_color}" opacity="{float(p['glow']) * strength:.2f}" filter="url(#{pid}b)"/>
<rect width="{CARD_W}" height="{CARD_H}" fill="url(#{pid}d)" mask="url(#{pid}m)"/>
<rect width="{CARD_W}" height="2" fill="url(#{pid}t)"/>
</g>
{frame(CARD_W, CARD_H, p, 20)}
<circle cx="{CARD_W - 46}" cy="46" r="20" fill="{p['bg']}" stroke="{p['border']}" stroke-width="1.5"/>
<path d="M{CARD_W - 52} 52 L{CARD_W - 40} 40 M{CARD_W - 49} 40 H{CARD_W - 40} V49" fill="none" stroke="{p['accent_text']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>"""


def project_card(theme: str, proj: dict, index: int) -> str:
    p = PALETTES[theme]
    lang, lang_color = proj["lang"]
    lines = wrap(proj["text"], "medium", 16.5, CARD_W - 72)[:3]
    desc = "".join(text(36, 126 + i * 24, line, "medium", 16.5, p["muted"]) for i, line in enumerate(lines))
    chips, x = [], 36
    for tag in proj["tags"]:
        w = measure(tag, "mono", 13) + 24
        chips.append(
            f'<rect x="{x:.1f}" y="194" width="{w:.1f}" height="28" rx="14" fill="{p["track"]}"/>'
            + text(x + w / 2, 212.5, tag, "mono", 13, p["muted"], anchor="middle")
        )
        x += w + 8
    glow = p["accent"] if index % 2 == 0 else p["accent2"]
    body = (
        card_base(p, "pc", glow, 1.0)
        + f'<circle cx="41" cy="47" r="5" fill="{lang_color}"/>'
        + text(54, 52, lang.upper(), "mono", 13, p["muted"], spacing=1.5)
        + text(36, 92, proj["title"], "display", 27, p["text"], spacing=-0.4)
        + desc
        + "".join(chips)
        + text(CARD_W - 36, 213, proj["date"], "mono", 13, p["faint"], anchor="end")
    )
    return svg(CARD_W, CARD_H, body, title=f"{proj['title']} — {proj['text']}")


def all_repos_card(theme: str) -> str:
    p = PALETTES[theme]
    body = (
        card_base(p, "ac", p["accent"], 1.8)
        + f'<circle cx="41" cy="47" r="5" fill="url(#acg)"/>'
        + f"<defs>{accent_gradient('acg', p)}</defs>"
        + text(54, 52, "MORE", "mono", 13, p["muted"], spacing=1.5)
        + text(36, 92, "Explore all repositories", "display", 27, p["text"], spacing=-0.4)
        + text(36, 126, "Coursework, experiments and whatever", "medium", 16.5, p["muted"])
        + text(36, 150, "I am building next.", "medium", 16.5, p["muted"])
        + text(36, 213, "github.com/ImMXP?tab=repositories  →", "mono", 13.5, p["accent_text"])
    )
    return svg(CARD_W, CARD_H, body, title="Explore all repositories")


# ── About console ─────────────────────────────────────────────────────────────
CONSOLE_LINES = [
    "Hello, everyone!",
    "I'm Mohammed.",
    "Passionate about software development, AI, and other stuff.",
]
TYPE_S, DELETE_S, HOLD_S, GAP_S = 0.075, 0.03, 1.9, 0.5


def typing_timeline(lines: list[str]) -> tuple[list[list[tuple[float, int]]], float]:
    """Per line, the (time, visible chars) steps of typing it, holding, then deleting it."""
    t, timelines = 0.0, []
    for i, line in enumerate(lines):
        n = len(line)
        steps = [(t + k * TYPE_S, k) for k in range(n + 1)]
        hold_end = t + n * TYPE_S + HOLD_S + (0.8 if i == len(lines) - 1 else 0)
        steps += [(hold_end + (n - k) * DELETE_S, k) for k in range(n - 1, -1, -1)]
        timelines.append(steps)
        t = hold_end + n * DELETE_S + GAP_S
    return timelines, t


def discrete(attr: str, steps: list[tuple[float, float]], total: float, idle: float) -> str:
    """Discrete SMIL animation stepping through (time, value) pairs over one cycle.

    ``idle`` is the value before the first step and after the last one."""
    steps = [(0.0, idle)] + steps + [(total, idle)]
    times, values = [], []
    for t, v in steps:
        if times and t / total <= times[-1]:
            values[-1] = v
            continue
        times.append(t / total)
        values.append(v)
    return (
        f'<animate attributeName="{attr}" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="{";".join(f"{k:.4f}" for k in times)}" values="{";".join(f"{v:.1f}" for v in values)}"/>'
    )


def console(theme: str) -> str:
    p = PALETTES[theme]
    H, bar = 200, 46
    size = 26
    cw = measure("M", "mono", size)
    x0, base = 76, 158
    timelines, total = typing_timeline(CONSOLE_LINES)

    keep_spaces = ' xml:space="preserve"'
    lines_svg = []
    for i, (line, steps) in enumerate(zip(CONSOLE_LINES, timelines)):
        widths = [(t, n * cw + 1) for t, n in steps]
        lines_svg.append(
            f'<clipPath id="type{i}"><rect x="{x0 - 1}" y="{base - size}" height="{size * 1.5}" width="0">'
            f'{discrete("width", widths, total, 0)}</rect></clipPath>'
            + f'<g clip-path="url(#type{i})">{text(x0, base, line, "mono", size, p["text"], extra=keep_spaces)}</g>'
        )
    cursor_steps = sorted((t, x0 + n * cw + 3) for steps in timelines for t, n in steps)
    cursor = (
        f'<g><animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/>'
        f'<rect x="{x0 + 3}" y="{base - size + 4}" width="{cw * 0.62:.1f}" height="{size + 2}" rx="2" fill="url(#cg)">'
        f'{discrete("x", cursor_steps, total, x0 + 3)}</rect></g>'
    )
    dots = "".join(
        f'<circle cx="{30 + i * 22}" cy="{bar / 2}" r="6.5" fill="{c}"/>'
        for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"])
    )
    body = f"""<defs>{accent_gradient('cg', p)}
<clipPath id="win"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{p['bg']}"/>
<rect width="{W}" height="{bar}" fill="{p['bg2']}"/>
<rect y="{bar}" width="{W}" height="1.5" fill="{p['border']}"/>
</g>
{frame(W, H, p, 18)}
{dots}
{text(W / 2, bar / 2 + 5, 'moha0x — about.sh', 'mono', 14, p['faint'], anchor='middle')}
{text(40, 100, '~', 'mono', 18, p['accent_text'])}{text(62, 100, '$ ./about.sh', 'mono', 18, p['muted'])}
{text(40, base, '>', 'mono', size, p['accent_text'])}
{''.join(lines_svg)}
{cursor}"""
    return svg(W, H, body, title=" · ".join(CONSOLE_LINES))


# ── Footer ────────────────────────────────────────────────────────────────────
def footer(theme: str) -> str:
    p = PALETTES[theme]
    H = 110
    body = f"""<defs>
<linearGradient id="hair" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{p['accent']}" stop-opacity="0"/><stop offset="0.35" stop-color="{p['accent']}"/>
<stop offset="0.65" stop-color="{p['accent2']}"/><stop offset="1" stop-color="{p['accent2']}" stop-opacity="0"/>
</linearGradient></defs>
<rect x="{W / 2 - 300}" y="28" width="600" height="1.5" fill="url(#hair)"/>
{text(W / 2, 72, 'Thanks for stopping by', 'medium', 17, p['muted'], anchor='middle')}
{text(W / 2, 96, '@ImMXP', 'mono', 13, p['faint'], anchor='middle')}"""
    return svg(W, H, body, title="Thanks for stopping by")


def main() -> None:
    for theme in PALETTES:
        write(f"banner-{theme}.svg", banner(theme))
        write(f"footer-{theme}.svg", footer(theme))
        write(f"about-console-{theme}.svg", console(theme))
        write(f"projects/all-repositories-{theme}.svg", all_repos_card(theme))
        for slug, index, title in SECTIONS:
            write(f"headers/{slug}-{theme}.svg", header(theme, index, title))
        for i, proj in enumerate(PROJECTS):
            write(f"projects/{proj['slug']}-{theme}.svg", project_card(theme, proj, i))


def write(rel: str, content: str) -> None:
    path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"{rel:48} {len(content.encode()):>8,} bytes")


if __name__ == "__main__":
    main()
