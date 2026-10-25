"""Работа с настоящим GUI Logisim 2.7.1 на X-дисплее (Xvfb :77): открыть схему, выставить входы
кликами инструментом «Poke», потактировать, снять скриншот окна.

    from gui import Logisim
    with Logisim("pr03/src/logisim/pr03_ou.circ") as L:
        L.set_pin((80, 110), 3, 0b010)     # пин MSA (loc и разрядность из .circ)
        L.click_pin((80, 650))             # однобитный пин CLK
        L.shot("pr03/img/logisim_ou.png")
"""
import math
import os
import subprocess
import time

os.environ.setdefault("DISPLAY", ":77")
import xshot  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JAR = os.path.join(ROOT, ".tools", "logisim", "logisim.jar")
XVFB = os.path.join(ROOT, ".tools", "xvfb", "root", "usr", "bin", "Xvfb")
W, H = 1920, 1200
EXPLORER = 260          # ширина панели проводника после перетаскивания разделителя
ZOOMS = [0.2, 0.5, 0.75, 1.0, 1.33, 1.5, 2.0, 2.5, 3.0, 4.0]


def ensure_xvfb():
    if os.path.exists("/tmp/.X11-unix/X77"):
        return
    subprocess.Popen([XVFB, ":77", "-screen", "0", f"{W}x{H}x24", "-nolisten", "tcp"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)


class Logisim:
    def __init__(self, circ, zoom=1.0):
        ensure_xvfb()
        self.proc = subprocess.Popen(["java", "-Dawt.useSystemAAFontSettings=on", "-Dswing.aatext=true",
                                      "-jar", JAR, os.path.abspath(circ)],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            time.sleep(0.5)
            if any(n and "Logisim" in n for _, n, *_ in xshot.windows()):
                break
        time.sleep(2)
        xshot.maximize(W, H)
        time.sleep(1.5)
        # сузить панель проводника: тянем разделитель
        xshot.drag(481, 600, EXPLORER, 600)
        time.sleep(1)
        self.zoom = 1.0
        self.scroll = (0, 0)
        self.set_zoom(zoom)

    # --- геометрия ---
    def origin(self):
        return EXPLORER + 2, 50

    def to_screen(self, x, y):
        ox, oy = self.origin()
        return ox + (x - self.scroll[0]) * self.zoom, oy + (y - self.scroll[1]) * self.zoom

    # --- действия ---
    def set_zoom(self, z):
        """Масштаб через счётчик в левом нижнем углу (шаги списка Logisim)."""
        if z == self.zoom:
            return
        cur, want = ZOOMS.index(self.zoom), ZOOMS.index(z)
        arrow = (EXPLORER - 24, H - 16) if want > cur else (EXPLORER - 24, H - 6)
        for _ in range(abs(want - cur)):
            xshot.click(*arrow)
            time.sleep(0.3)
        self.zoom = z
        time.sleep(0.8)

    def click(self, x, y, double=False):
        sx, sy = self.to_screen(x, y)
        xshot.click(round(sx), round(sy), double=double)

    @staticmethod
    def pin_bounds(loc, width, facing="east"):
        """Границы пина (как Probe.getOffsetBounds в Logisim 2.7.1)."""
        cols = min(width, 8) if width > 1 else 2
        rows = max(1, math.ceil(width / 8))
        w, h = 10 * cols, 20 * rows
        if width >= 9:
            w = 80
        x, y = loc
        if facing == "east":
            return x - w, y - h // 2 if rows == 1 else y - 10 * rows, w, h
        if facing == "west":
            return x, y - h // 2 if rows == 1 else y - 10 * rows, w, h
        if facing == "south":
            return x - w // 2, y - h, w, h
        return x - w // 2, y, w, h  # north

    def click_pin(self, loc, facing="east"):
        """Однобитный входной пин: щелчок по центру квадрата."""
        bx, by, bw, bh = self.pin_bounds(loc, 1, facing)
        self.click(bx + bw / 2, by + bh / 2)

    def set_pin(self, loc, width, value, old=0, facing="east"):
        """Входной пин разрядности width: переключаем отличающиеся биты."""
        if width == 1:
            if (value ^ old) & 1:
                self.click_pin(loc, facing)
            return
        bx, by, bw, bh = self.pin_bounds(loc, width, facing)
        right, bottom = bx + bw, by + bh
        for b in range(width):
            if ((value ^ old) >> b) & 1:
                i, j = b % 8, b // 8
                self.click(right - 10 * i - 5, bottom - 20 * j - 10)
                time.sleep(0.05)

    def pulse(self, loc, facing="east"):
        """Фронт тактового пина: 0 → 1 → 0."""
        self.click_pin(loc, facing)
        time.sleep(0.2)
        self.click_pin(loc, facing)
        time.sleep(0.2)

    def tick(self, n=1):
        xshot.key("ctrl+t", n)
        time.sleep(0.3)

    def poke_register(self, loc, hexval):
        """Ввести значение регистра (Poke): щелчок по регистру и набор hex-цифр."""
        self.click(loc[0] - 15, loc[1] - 5)
        time.sleep(0.2)
        xshot.type_text(hexval.lower())
        xshot.key("Return")
        time.sleep(0.3)

    def open_circuit(self, row):
        """Открыть подсхему двойным щелчком по строке row (0, 1, …) в проводнике проекта."""
        xshot.click(60, 122 + 20 * row, double=True)
        time.sleep(1)

    def shot(self, path, box="auto"):
        """Скриншот экрана. box="auto" — окно Logisim, обрезанное справа и снизу по схеме на холсте."""
        time.sleep(0.8)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        if box != "auto":
            xshot.shot(path, box)
            return path
        img = xshot.shot(path)
        x0, y0 = EXPLORER + 4, 52
        from PIL import ImageChops
        canvas = img.crop((x0, y0, W - 20, H - 20)).convert("RGB")
        r, g, b = canvas.split()
        mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
        mn = ImageChops.darker(ImageChops.darker(r, g), b)
        colored = ImageChops.subtract(mx, mn).point(lambda v: 255 if v > 60 else 0)
        black = mx.point(lambda v: 255 if v < 70 else 0)
        bb = ImageChops.lighter(colored, black).getbbox()  # серые точки сетки не учитываются
        if bb:
            right = min(W, x0 + bb[2] + 40)
            bottom = min(H, max(y0 + bb[3] + 40, 640))
            img.crop((0, 0, max(right, 900), bottom)).save(path)
        return path

    def close(self):
        self.proc.terminate()
        try:
            self.proc.wait(5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        time.sleep(0.5)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class Panel:
    """Набор входных пинов {имя: (loc, разрядность)} с запоминанием текущих значений."""

    def __init__(self, L, pins):
        self.L, self.pins, self.cur = L, pins, {k: 0 for k in pins}

    def set(self, **kw):
        for k, v in kw.items():
            loc, w, *f = self.pins[k]
            self.L.set_pin(loc, w, v, self.cur[k], f[0] if f else "east")
            self.cur[k] = v

    def pulse(self, name):
        loc, w, *f = self.pins[name]
        self.L.pulse(loc, f[0] if f else "east")
