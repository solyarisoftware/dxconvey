#!/usr/bin/env python3
"""Draw a run of the tool as a terminal does: the picture of the text, not the text.

The figures are made of Braille patterns, and a page cannot be told which font to use
(GitHub strips the stylesheets): the browser falls back to a font without
`U+2800`-`U+28FF` — Consolas, on Windows — and the dots come out as boxes or as a spray
of pale specks, which is not what the tool prints.  So the runs that draw are rendered
here the way a terminal shows them, and that picture is what the README shows.

The text stays the source: this script reads a capture and draws it, so the picture
cannot say anything the run did not say.  The Braille dots are drawn as dots — two
across and four down in a cell, the geometry of the character — so the figure looks like
the terminal whatever font this machine has; every other character is text.

    python3 examples/terminal_png.py examples/images/lfo-waves.txt \
                                    examples/images/lfo-waves.png
"""

from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

#: the fonts tried in order: a monospace one is enough, the dots are drawn here
FONTS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "C:/Windows/Fonts/consola.ttf",
)
SIZE = 15
LINE = 21
PAD = 18
BACKGROUND = "#0d1117"
TEXT = "#d6deeb"
PROMPT = "#7ee787"

#: which dots of a Braille cell each bit is: (bit, column, row)
DOTS = (
    (0x01, 0, 0), (0x02, 0, 1), (0x04, 0, 2), (0x40, 0, 3),
    (0x08, 1, 0), (0x10, 1, 1), (0x20, 1, 2), (0x80, 1, 3),
)


def font_for() -> tuple[ImageFont.FreeTypeFont, str]:
    for path in FONTS:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, SIZE), path
    raise SystemExit("no monospace font found: pass one in FONTS")


def draw(lines: list[str]) -> Image.Image:
    font, _ = font_for()
    step = round(font.getlength("M"))
    dot = max(1, round(step * 0.13))  # the radius of one Braille dot
    width = max((len(line) for line in lines), default=1) * step + 2 * PAD
    height = len(lines) * LINE + 2 * PAD
    image = Image.new("RGB", (width, height), BACKGROUND)
    painter = ImageDraw.Draw(image)
    for row, line in enumerate(lines):
        y = PAD + row * LINE
        if line.startswith("$ "):
            painter.text((PAD, y), "$", font=font, fill=PROMPT)
            x = PAD + 2 * step
            line = line[2:]
        else:
            x = PAD
        for char in line:
            code = ord(char)
            if 0x2800 <= code <= 0x28FF:
                bits = code - 0x2800
                for bit, column, dot_row in DOTS:
                    if bits & bit:
                        cx = x + round(step * (0.25 + 0.5 * column))
                        cy = y + round(LINE * (0.15 + 0.233 * dot_row))
                        painter.ellipse((cx - dot, cy - dot, cx + dot, cy + dot), fill=TEXT)
            elif char != " ":
                painter.text((x, y), char, font=font, fill=TEXT)
            x += step
    return image


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    source, target = pathlib.Path(argv[1]), pathlib.Path(argv[2])
    lines = source.read_text().rstrip("\n").split("\n")
    target.parent.mkdir(parents=True, exist_ok=True)
    draw(lines).save(target)
    print(f"{target}: {target.stat().st_size:,} bytes, {len(lines)} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
