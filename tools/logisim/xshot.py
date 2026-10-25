"""Автоматизация GUI Logisim на X-дисплее (Xvfb): запуск, клики, ввод, скриншоты окна.

python tools/logisim/xshot.py shot out.png [x0 y0 x1 y1]   — снимок экрана (или области)
python tools/logisim/xshot.py click X Y [кнопка]           — клик мышью
python tools/logisim/xshot.py key  "ctrl+t" [N]            — нажатие клавиш (N раз)
python tools/logisim/xshot.py type "текст"                 — набор текста (ASCII)
Дисплей берётся из DISPLAY.
"""
import sys
import time

from PIL import Image
from Xlib import X, XK, display
from Xlib.ext import xtest

D = display.Display()
ROOT = D.screen().root


def shot(path, box=None):
    g = ROOT.get_geometry()
    x0, y0, x1, y1 = box or (0, 0, g.width, g.height)
    raw = ROOT.get_image(x0, y0, x1 - x0, y1 - y0, X.ZPixmap, 0xFFFFFFFF)
    img = Image.frombytes("RGB", (x1 - x0, y1 - y0), raw.data, "raw", "BGRX")
    img.save(path)
    return img


def move(x, y):
    xtest.fake_input(D, X.MotionNotify, x=int(x), y=int(y))
    D.sync()


def click(x, y, button=1, double=False):
    move(x, y)
    time.sleep(0.05)
    for _ in range(2 if double else 1):
        xtest.fake_input(D, X.ButtonPress, button)
        xtest.fake_input(D, X.ButtonRelease, button)
        D.sync()
        time.sleep(0.05)
    time.sleep(0.15)


def drag(x0, y0, x1, y1, button=1):
    move(x0, y0)
    xtest.fake_input(D, X.ButtonPress, button)
    D.sync()
    for i in range(1, 11):
        move(x0 + (x1 - x0) * i / 10, y0 + (y1 - y0) * i / 10)
        time.sleep(0.02)
    xtest.fake_input(D, X.ButtonRelease, button)
    D.sync()
    time.sleep(0.2)


MODS = {"ctrl": "Control_L", "shift": "Shift_L", "alt": "Alt_L"}


def key(combo, n=1):
    parts = combo.split("+")
    codes = [D.keysym_to_keycode(XK.string_to_keysym(MODS.get(p, p))) for p in parts]
    for _ in range(n):
        for c in codes:
            xtest.fake_input(D, X.KeyPress, c)
        for c in reversed(codes):
            xtest.fake_input(D, X.KeyRelease, c)
        D.sync()
        time.sleep(0.08)


def type_text(s):
    for ch in s:
        name = {" ": "space", ".": "period", "-": "minus", "_": "underscore", "/": "slash"}.get(ch, ch)
        ks = XK.string_to_keysym(name)
        code = D.keysym_to_keycode(ks)
        shift = ch.isupper() or ch in "_"
        if shift:
            xtest.fake_input(D, X.KeyPress, D.keysym_to_keycode(XK.string_to_keysym("Shift_L")))
        xtest.fake_input(D, X.KeyPress, code)
        xtest.fake_input(D, X.KeyRelease, code)
        if shift:
            xtest.fake_input(D, X.KeyRelease, D.keysym_to_keycode(XK.string_to_keysym("Shift_L")))
        D.sync()
        time.sleep(0.04)


if __name__ == "__main__":
    cmd, *a = sys.argv[1:]
    if cmd == "shot":
        shot(a[0], tuple(map(int, a[1:5])) if len(a) >= 5 else None)
    elif cmd == "click":
        click(int(a[0]), int(a[1]), int(a[2]) if len(a) > 2 else 1)
    elif cmd == "key":
        key(a[0], int(a[1]) if len(a) > 1 else 1)
    elif cmd == "type":
        type_text(a[0])


def windows():
    out = []
    for w in ROOT.query_tree().children:
        try:
            name = w.get_wm_name()
            g = w.get_geometry()
            attrs = w.get_attributes()
        except Exception:
            continue
        if attrs.map_state == X.IsViewable:
            out.append((w, name, g.x, g.y, g.width, g.height))
    return out


def maximize(width=1920, height=1200):
    for w, name, *_ in windows():
        if name and "Logisim" in name:
            w.configure(x=0, y=0, width=width, height=height)
            D.sync()
            return name
    return None


if __name__ == "__main__" and sys.argv[1] == "max":
    print(maximize())
elif __name__ == "__main__" and sys.argv[1] == "wins":
    for w, *rest in windows():
        print(rest)
