"""Build the small WOFF font subsets embedded in the profile artwork.

The source fonts are the variable TTFs from https://github.com/google/fonts
(SIL Open Font License 1.1). Run once:

    python scripts/make_fonts.py <folder with the downloaded TTFs>
"""
from __future__ import annotations

import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import FONT_DIR  # noqa: E402

LATIN = (
    [*range(0x20, 0x7F), *range(0xA0, 0x100)]
    + [0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026]
    + [0x2190, 0x2191, 0x2192, 0x2193, 0x2197, 0x25B8, 0x2726]
)

# (source file, weight, output file, unicodes, text)
TARGETS = [
    ("SpaceGrotesk[wght].ttf", 700, "SpaceGrotesk-Bold.woff", LATIN, None),
    ("SpaceGrotesk[wght].ttf", 500, "SpaceGrotesk-Medium.woff", LATIN, None),
    ("JetBrainsMono[wght].ttf", 500, "JetBrainsMono-Medium.woff", LATIN, None),
]


def build(src_dir: Path) -> None:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for src, weight, out, unicodes, text in TARGETS:
        font = TTFont(src_dir / src)
        font = instancer.instantiateVariableFont(font, {"wght": weight})
        options = subset.Options()
        options.flavor = "woff"
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        options.notdef_outline = True
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=unicodes, text=text or "")
        subsetter.subset(font)
        font.flavor = "woff"
        font.save(FONT_DIR / out)
        print(f"{out}: {(FONT_DIR / out).stat().st_size:,} bytes")


if __name__ == "__main__":
    build(Path(sys.argv[1]))
