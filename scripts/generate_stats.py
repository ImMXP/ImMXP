"""Render the GitHub activity card from live data (runs daily in GitHub Actions).

    GITHUB_TOKEN=... python scripts/generate_stats.py --user ImMXP --out dist
    python scripts/generate_stats.py --fixture sample.json --out dist   # offline preview

Writes ``stats-dark.svg`` and ``stats-light.svg``.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import PALETTES, accent_gradient, measure, svg, text  # noqa: E402

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

W, H = 1200, 330


def fetch(login: str, token: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def summarize(user: dict, login: str) -> dict:
    cc = user["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"]
    days = sorted((d for w in weeks for d in w["contributionDays"]), key=lambda d: d["date"])

    longest = run = 0
    for day in days:
        run = run + 1 if day["contributionCount"] else 0
        longest = max(longest, run)

    languages: dict[str, list] = {}
    projects = 0
    for repo in user["repositories"]["nodes"]:
        if repo["name"].lower() == login.lower():  # the profile repo itself
            continue
        projects += 1
        for edge in repo["languages"]["edges"]:
            entry = languages.setdefault(edge["node"]["name"], [0, edge["node"]["color"] or "#8B949E"])
            entry[0] += edge["size"]
    total = sum(size for size, _ in languages.values()) or 1
    top = sorted(languages.items(), key=lambda kv: -kv[1][0])[:5]

    return {
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "longest": longest,
        "projects": projects,
        "languages": [(name, color, size / total) for name, (size, color) in top],
        "weeks": [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks][-52:],
    }


def card(theme: str, s: dict, login: str, updated: str) -> str:
    p = PALETTES[theme]
    parts = [
        f"<defs>{accent_gradient('acc', p)}{accent_gradient('bars', p, x1='0', y1='1', x2='0', y2='0')}</defs>",
        f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="23.5" fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="1.5"/>',
        text(40, 50, "LAST 12 MONTHS", "mono", 13, p["accent_text"], spacing=1.5),
        text(W - 40, 50, f"github.com/{login} · updated {updated}", "mono", 12.5, p["faint"], anchor="end"),
    ]

    metrics = [
        (f"{s['contributions']:,}", "CONTRIBUTIONS"),
        (f"{s['commits']:,}", "COMMITS"),
        (f"{s['longest']}", "LONGEST STREAK", "days" if s["longest"] != 1 else "day"),
        (f"{s['projects']}", "PUBLIC PROJECTS"),
    ]
    tile = (W - 80) / len(metrics)
    for i, (value, label, *unit) in enumerate(metrics):
        x = 40 + i * tile + (0 if i == 0 else 28)
        if i:
            parts.append(f'<line x1="{40 + i * tile:.1f}" y1="84" x2="{40 + i * tile:.1f}" y2="160" stroke="{p["border"]}" stroke-width="1.5"/>')
        parts.append(f'<rect x="{x:.1f}" y="84" width="22" height="3" rx="1.5" fill="url(#acc)"/>')
        parts.append(text(x, 136, value, "display", 46, p["text"], spacing=-1))
        if unit:
            parts.append(text(x + measure(value, "display", 46, -1) + 8, 136, unit[0], "medium", 18, p["muted"]))
        parts.append(text(x, 160, label, "mono", 12.5, p["muted"], spacing=1.2))

    parts.append(f'<line x1="40" y1="190" x2="{W - 40}" y2="190" stroke="{p["border"]}" stroke-width="1.5"/>')

    # Languages: stacked bar + legend
    parts.append(text(40, 228, "LANGUAGES", "mono", 12.5, p["muted"], spacing=1.2))
    bar_x, bar_w = 40, 520
    parts.append(f'<defs><clipPath id="bar"><rect x="{bar_x}" y="244" width="{bar_w}" height="10" rx="5"/></clipPath></defs>')
    parts.append(f'<rect x="{bar_x}" y="244" width="{bar_w}" height="10" rx="5" fill="{p["track"]}"/>')
    seg_x, segs = bar_x, []
    for name, color, share in s["languages"]:
        w = bar_w * share
        segs.append(f'<rect x="{seg_x:.1f}" y="244" width="{max(w - 2, 1):.1f}" height="10" fill="{color}"/>')
        seg_x += w
    parts.append(f'<g clip-path="url(#bar)">{"".join(segs)}</g>')
    lx, ly = bar_x, 290
    for name, color, share in s["languages"]:
        pct = f"{share * 100:.1f}%"
        item_w = 16 + measure(name, "medium", 15) + 8 + measure(pct, "mono", 13) + 26
        if lx + item_w > bar_x + bar_w + 20:
            lx, ly = bar_x, ly + 26
        parts.append(f'<circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{color}"/>')
        parts.append(text(lx + 16, ly, name, "medium", 15, p["text"]))
        parts.append(text(lx + 16 + measure(name, "medium", 15) + 8, ly, pct, "mono", 13, p["muted"]))
        lx += item_w
    if not s["languages"]:
        parts.append(text(bar_x, 290, "No public code yet", "medium", 15, p["muted"]))

    # Weekly activity bars
    ax, aw = 640, 520
    weeks = s["weeks"] or [0]
    peak = max(weeks) or 1
    step = aw / len(weeks)
    parts.append(text(ax, 228, "WEEKLY ACTIVITY", "mono", 12.5, p["muted"], spacing=1.2))
    parts.append(text(ax + aw, 228, f"{len(weeks)} weeks", "mono", 12.5, p["faint"], anchor="end"))
    base = 300
    for i, count in enumerate(weeks):
        x = ax + i * step + 1.5
        bw = max(step - 3, 2)
        if count:
            h = 8 + 46 * count / peak
            parts.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="{min(bw / 2, 3):.1f}" fill="url(#bars)"/>')
        else:
            parts.append(f'<rect x="{x:.1f}" y="{base - 3:.1f}" width="{bw:.1f}" height="3" rx="1.5" fill="{p["track"]}"/>')

    title = (
        f"GitHub activity in the last 12 months: {s['contributions']} contributions, {s['commits']} commits, "
        f"longest streak {s['longest']} days, {s['projects']} public projects. Languages: "
        + ", ".join(f"{n} {sh * 100:.0f}%" for n, _, sh in s["languages"])
    )
    return svg(W, H, "".join(parts), title=title)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "ImMXP"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--fixture", help="JSON file with a saved GraphQL `user` object (offline preview)")
    args = ap.parse_args()

    if args.fixture:
        user = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("Set GITHUB_TOKEN or pass --fixture")
        user = fetch(args.user, token)

    stats = summarize(user, args.user)
    updated = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in PALETTES:
        (out / f"stats-{theme}.svg").write_text(card(theme, stats, args.user, updated), encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "weeks"}, indent=2))


if __name__ == "__main__":
    main()
