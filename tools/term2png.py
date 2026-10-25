"""Рендер текстового вывода терминала в PNG («скриншот» консоли для отчёта).

Использование:
    python tools/term2png.py input.txt output.png [--title "ashot@linux: ~/pr08"]
    some_cmd | python tools/term2png.py - output.png
"""
import argparse
import re
import sys

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG = (30, 30, 30)
FG = (220, 220, 220)
PROMPT = (110, 200, 110)
BAR = (60, 60, 60)
MAX_COLS = 120
PROMPT_RE = re.compile(r"^(\S+@\S+:[^$]*)?\$ ")


def wrap(lines):
    out = []
    for line in lines:
        line = line.rstrip("\n").expandtabs(8)
        while len(line) > MAX_COLS:
            out.append(line[:MAX_COLS])
            line = line[MAX_COLS:]
        out.append(line)
    return out


def render(text, path, title="ashot@linux: ~", size=15):
    font = ImageFont.truetype(FONT, size)
    bold = ImageFont.truetype(FONT_BOLD, size)
    lines = wrap(text.splitlines()) or [""]
    cw = font.getbbox("M")[2]
    lh = int(size * 1.35)
    cols = max(80, max(len(s) for s in lines))
    pad, bar_h = 12, 28
    w = pad * 2 + cw * cols
    h = bar_h + pad * 2 + lh * len(lines)
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, bar_h], fill=BAR)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([10 + i * 20, 8, 22 + i * 20, 20], fill=c)
    d.text((w // 2, bar_h // 2), title, font=font, fill=(200, 200, 200), anchor="mm")
    y = bar_h + pad
    for s in lines:
        if PROMPT_RE.match(s):
            head, _, cmd = s.partition("$ ")
            d.text((pad, y), head + "$ ", font=bold, fill=PROMPT)
            d.text((pad + cw * (len(head) + 2), y), cmd, font=font, fill=FG)
        else:
            d.text((pad, y), s, font=font, fill=FG)
        y += lh
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--title", default="ashot@linux: ~")
    a = ap.parse_args()
    text = sys.stdin.read() if a.src == "-" else open(a.src, encoding="utf-8").read()
    render(text, a.dst, a.title)


if __name__ == "__main__":
    main()
