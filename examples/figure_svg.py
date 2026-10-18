#!/usr/bin/env python3
"""Turn a figure printed by `dxconvey` into an SVG, so it stays aligned anywhere.

The tool draws its curves with the Braille patterns (`U+2800`–`U+28FF`): two dots
across and four down in one character cell, eight times the resolution of the block
characters, and they join into a continuous line.  That works in a terminal, whose
font has them.  It does not work on a page: the monospace font a browser picks for code
usually has no Braille glyph, the fallback font draws them at another size and with
another advance, and the figure breaks — the dots drift apart and the labels slide.

So the figures on the page are this SVG instead: every dot is a rectangle at a known
coordinate and every other character is a text element at a known coordinate, so the
grid is exact whatever font the reader has.  The SVG is built from the text the tool
prints, so the picture and the terminal output cannot disagree.

    python3 examples/figure_svg.py examples/figures/lfo-waves.txt \
                                  examples/figures/lfo-waves.svg
"""

from __future__ import annotations

import sys
from pathlib import Path

#: the geometry of one character cell, in SVG units
CELL_W, CELL_H = 8, 16
#: the side of one Braille dot: a full quarter of the cell, so that two neighbouring
#: dots touch and the curve is one line, which is what the Braille cell means
DOT = CELL_H // 4
#: the baseline of a character, from the top of its cell
BASELINE = 12

#: Braille dot bits, in reading order: dot 1 is the top left, dot 8 the bottom right
DOTS = (
    (0x01, 0, 0), (0x02, 0, 1), (0x04, 0, 2), (0x40, 0, 3),
    (0x08, 1, 0), (0x10, 1, 1), (0x20, 1, 2), (0x80, 1, 3),
)

HEAD = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"
     role="img" aria-label="{label}">
<style>
  .ink {{ fill: #24292f; }}
  @media (prefers-color-scheme: dark) {{ .ink {{ fill: #c9d1d9; }} }}
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
         font-size: 12px; }}
</style>
"""


def escape(char: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(char, char)


def figure(text: str, label: str) -> str:
    lines = text.rstrip("\n").split("\n")
    width = max((len(line) for line in lines), default=0)
    w, h = width * CELL_W + 2, len(lines) * CELL_H + 2
    out = [HEAD.format(w=w, h=h, label=escape(label))]
    dots, glyphs = [], []
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            code = ord(char)
            if char == " ":
                continue
            x, y = 1 + col * CELL_W, 1 + row * CELL_H
            if 0x2800 <= code <= 0x28FF:
                bits = code - 0x2800
                for bit, dx, dy in DOTS:
                    if bits & bit:
                        dots.append(
                            f'<rect x="{x + dx * CELL_W // 2}" y="{y + dy * CELL_H // 4}"'
                            f' width="{DOT}" height="{DOT}" class="ink"/>'
                        )
            else:
                glyphs.append(
                    f'<text x="{x}" y="{y + BASELINE}" class="ink">{escape(char)}</text>'
                )
    out.append("<g>")
    out.extend(glyphs)
    out.append("</g>")
    out.append("<g>")
    out.extend(dots)
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    source, target = Path(argv[1]), Path(argv[2])
    label = source.stem.replace("-", " ")
    target.write_text(figure(source.read_text(), label))
    print(f"{target}: {target.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
