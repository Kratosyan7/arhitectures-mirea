"""Генерация pr12.circ (Logisim 2.7.1): иллюстрация SIMD/SIMT-исполнения.

Схема julia_lane — одно «ядро-линия»: регистры zx, zy (формат Q4.12,
16 бит, дополнительный код), счётчик итераций N (8 бит). За один такт
линия выполняет одну итерацию z <- z^2 + k множества Жюлиа и проверяет
условие ухода |z|^2 > 4. Если точка уже ушла (ESC = 1), линия маскируется:
регистры не обновляются (так GPU обрабатывает расхождение ветвей в варпе).

Схема simt4 (главная) — четыре одинаковые линии, общий тактовый сигнал,
общая «команда» LOAD/ITER и общие операнды kx, ky (широковещательно на все
линии), у каждой линии свой пиксель z0. Устройство управления: триггер
начального сброса (первый такт — загрузка z0), счётчик шагов STEP,
сигнал halt (все линии ушли или STEP = MAXSTEP) для режима -tty.

Запуск без GUI:  java -jar logisim.jar pr12.circ -tty table
"""
import os
from xml.sax.saxutils import quoteattr

from circgen import Circuit, project_xml
from fixed import K_X, K_Y, PIXELS, MAXSTEP, hex16

HERE = os.path.dirname(os.path.abspath(__file__))
SMALL = "SansSerif plain 11"


class Sub(Circuit):
    """Схема с собственным видом блока (appearance) для вставки в другие схемы."""

    def __init__(self, name):
        super().__init__(name)
        self.appear = []

    def xml(self):
        s = super().xml()
        if not self.appear:
            return s
        body = "\n".join("      " + a for a in self.appear)
        return s.replace("  </circuit>", f"    <appear>\n{body}\n    </appear>\n  </circuit>")


def tunnel(c, loc, label, facing):
    c.comp("wiring", "Tunnel", loc, label=label, facing=facing, width=TW.get(label, 1))


TW = {}   # разрядность туннелей по имени


def pin_in(c, loc, label, width=1, facing="east"):
    a = dict(tristate="false", label=label, facing=facing)
    if width != 1:
        a["width"] = str(width)
    c.comp("wiring", "Pin", loc, **a)


def pin_out(c, loc, label, width=1, facing="west", labelloc="east"):
    a = dict(output="true", label=label, facing=facing, labelloc=labelloc)
    if width != 1:
        a["width"] = str(width)
    c.comp("wiring", "Pin", loc, **a)


def splitter_bits(c, loc, lo, hi, incoming=32):
    """Выделение бит [lo..hi] шины (сдвиг вправо на lo + усечение)."""
    a = dict(fanout="1", incoming=str(incoming))
    for i in range(incoming):
        a[f"bit{i}"] = "0" if lo <= i <= hi else "none"
    c.comp("wiring", "Splitter", loc, **a)
    return (loc[0] + 20, loc[1] - 10)


# ---------------------------------------------------------------- линия
def lane():
    c = Sub("julia_lane")
    TW.update(SX=32, SY=32, KX=16, KY=16, ZXN=16, ZYN=16, N1=8, ZX=16, ZY=16, N=8)
    c.text((520, 30), "Ядро-линия SIMT: одна итерация z <- z^2 + k за такт (Q4.12)")

    # входы
    pin_in(c, (60, 120), "Z0X", 16)
    pin_in(c, (60, 320), "Z0Y", 16)
    pin_in(c, (60, 520), "KX", 16)
    pin_in(c, (60, 570), "KY", 16)
    pin_in(c, (60, 620), "LOAD")
    pin_in(c, (60, 670), "CLK")
    for y, lab in ((520, "KX"), (570, "KY"), (620, "LOAD"), (670, "CLK")):
        c.wire((60, y), (100, y))
        tunnel(c, (100, y), lab, "west")

    # регистры zx (y=110) и zy (y=310): MUX (LOAD ? z0 : znew) -> Register -> sign-extend
    for y0, zin, zn, zout, sx in ((110, (60, 120), "ZXN", "ZX", "SX"), (310, (60, 320), "ZYN", "ZY", "SY")):
        c.comp("plexers", "Multiplexer", (200, y0), width="16", enable="false")
        c.wire(zin, (170, y0 + 10))                    # in1 = z0
        c.wire((150, y0 - 10), (170, y0 - 10))         # in0 = znew
        tunnel(c, (150, y0 - 10), zn, "east")
        c.wire((180, y0 + 20), (180, y0 + 40))         # select = LOAD
        tunnel(c, (180, y0 + 40), "LOAD", "north")
        c.comp("memory", "Register", (300, y0), width="16", label="R" + zout)
        c.wire((200, y0), (270, y0))
        c.wire((270, y0 + 10), (240, y0 + 10), (240, y0 + 50))   # enable = WE
        tunnel(c, (240, y0 + 50), "WE", "north")
        c.wire((280, y0 + 20), (280, y0 + 50))                   # clock
        tunnel(c, (280, y0 + 50), "CLK", "north")
        c.wire((300, y0), (360, y0))
        c.wire((330, y0), (330, y0 - 30))
        tunnel(c, (330, y0 - 30), zout, "south")
        c.comp("wiring", "Bit Extender", (400, y0), in_width="16", out_width="32", type="sign")
        c.wire((400, y0), (420, y0))
        tunnel(c, (420, y0), sx, "west")
    c.text((260, 195), "регистр zx", font=SMALL)
    c.text((260, 395), "регистр zy", font=SMALL)
    c.text((420, 150), "знаковое расширение 16->32", font=SMALL)

    # умножители 32x32 (младшие 32 бита = знаковое произведение, Q8.24)
    c.comp("arith", "Multiplier", (580, 100), width="32")
    c.comp("arith", "Multiplier", (580, 200), width="32")
    c.comp("arith", "Multiplier", (580, 300), width="32")
    for (y, a, b) in ((100, "SX", "SX"), (200, "SY", "SY"), (300, "SX", "SY")):
        c.wire((520, y - 10), (540, y - 10))
        c.wire((520, y + 10), (540, y + 10))
        tunnel(c, (520, y - 10), a, "east")
        tunnel(c, (520, y + 10), b, "east")
    c.text((580, 60), "zx*zx", font=SMALL)
    c.text((580, 160), "zy*zy", font=SMALL)
    c.text((580, 260), "zx*zy", font=SMALL)

    # |z|^2 = zx^2 + zy^2 (Q8.24) и сравнение с 4.0
    c.comp("arith", "Adder", (700, 150), width="32")
    c.wire((580, 100), (620, 100), (620, 140), (660, 140))
    c.wire((580, 200), (630, 200), (630, 160), (660, 160))
    c.comp("arith", "Comparator", (820, 150), width="32")
    c.wire((700, 150), (740, 150), (740, 140), (780, 140))
    c.comp("wiring", "Constant", (750, 200), width="32", value="0x4000000")
    c.wire((750, 200), (770, 200), (770, 160), (780, 160))
    c.wire((820, 140), (860, 140))
    tunnel(c, (860, 140), "ESC", "west")
    c.text((700, 115), "|z|^2", font=SMALL)
    c.text((830, 110), "|z|^2 > 4.0 ?", font=SMALL)
    c.text((700, 225), "4.0 (Q8.24)", font=SMALL)

    # Re: zx^2 - zy^2 -> биты [12..27] (Q4.12) + kx
    c.comp("arith", "Subtractor", (700, 270), width="32")
    c.wire((620, 140), (620, 260), (660, 260))
    c.wire((630, 200), (630, 280), (660, 280))
    c.wire((700, 270), (720, 270))
    o = splitter_bits(c, (720, 270), 12, 27)
    c.comp("arith", "Adder", (840, 270), width="16")
    c.wire(o, (800, 260))
    c.wire((780, 280), (800, 280))
    tunnel(c, (780, 280), "KX", "east")
    c.wire((840, 270), (870, 270))
    tunnel(c, (870, 270), "ZXN", "west")
    c.text((730, 300), "биты 27..12", font=SMALL)
    c.text((840, 235), "zx' = zx^2 - zy^2 + kx", font=SMALL)

    # Im: 2*zx*zy -> биты [11..26] (умножение на 2 = сдвиг) + ky
    c.wire((580, 300), (600, 300), (600, 370), (720, 370))
    o = splitter_bits(c, (720, 370), 11, 26)
    c.comp("arith", "Adder", (840, 370), width="16")
    c.wire(o, (800, 360))
    c.wire((780, 380), (800, 380))
    tunnel(c, (780, 380), "KY", "east")
    c.wire((840, 370), (870, 370))
    tunnel(c, (870, 370), "ZYN", "west")
    c.text((730, 400), "биты 26..11 (x2)", font=SMALL)
    c.text((840, 335), "zy' = 2*zx*zy + ky", font=SMALL)

    # маска: ACT = NOT ESC, WE = LOAD OR ACT
    tunnel(c, (190, 480), "ESC", "east")
    c.wire((190, 480), (210, 480))
    c.not_gate((240, 480), size=30)
    c.gate("OR", (330, 500), n=2, size=30)
    c.wire((240, 480), (270, 480), (270, 490), (300, 490))
    tunnel(c, (280, 520), "LOAD", "east")
    c.wire((280, 520), (290, 520), (290, 510), (300, 510))
    c.wire((330, 500), (360, 500))
    tunnel(c, (360, 500), "WE", "west")
    c.text((270, 450), "маска: линия активна, пока |z|^2 <= 4", font=SMALL)

    # счётчик итераций N: LOAD ? 0 : N+1, запись при WE
    c.comp("plexers", "Multiplexer", (520, 520), width="8", enable="false")
    tunnel(c, (470, 510), "N1", "east")
    c.wire((470, 510), (490, 510))                 # in0 = N + 1
    c.comp("wiring", "Constant", (470, 530), width="8", value="0x0")
    c.wire((470, 530), (490, 530))                 # in1 = 0
    c.wire((500, 540), (500, 560))                 # select = LOAD
    tunnel(c, (500, 560), "LOAD", "north")
    c.comp("memory", "Register", (600, 520), width="8", label="RN")
    c.wire((520, 520), (570, 520))
    c.wire((570, 530), (550, 530), (550, 570))
    tunnel(c, (550, 570), "WE", "north")
    c.wire((580, 540), (580, 570))
    tunnel(c, (580, 570), "CLK", "north")
    c.wire((600, 520), (680, 520))
    c.wire((640, 520), (640, 490))
    tunnel(c, (640, 490), "N", "south")
    c.comp("arith", "Adder", (720, 530), width="8")
    c.comp("wiring", "Constant", (660, 540), width="8", value="0x1")
    c.wire((660, 540), (680, 540))
    c.wire((720, 530), (750, 530))
    tunnel(c, (750, 530), "N1", "west")
    c.text((640, 620), "счётчик итераций N (8 бит)", font=SMALL)

    # выходы
    for y, lab, w in ((120, "ZX", 16), (220, "ZY", 16), (320, "N", 8), (420, "ESC", 1)):
        tunnel(c, (960, y), lab, "east")
        c.wire((960, y), (1000, y))
        pin_out(c, (1000, y), lab, w)

    # вид блока: входы слева с шагом 30, выходы справа
    ins = [((60, 120), "Z0X"), ((60, 320), "Z0Y"), ((60, 520), "KX"), ((60, 570), "KY"),
           ((60, 620), "LOAD"), ((60, 670), "CLK")]
    outs = [((1000, 120), "ZX"), ((1000, 220), "ZY"), ((1000, 320), "N"), ((1000, 420), "ESC")]
    X0, Y0, BW, BH = 50, 50, 140, 180
    ap = [f'<rect fill="#f2f6ff" height="{BH + 10}" stroke="#000000" stroke-width="2" width="{BW}" x="{X0}" y="{Y0 - 30}"/>',
          f'<text font-family="SansSerif" font-size="12" font-weight="bold" text-anchor="middle" x="{X0 + BW // 2}" y="{Y0 - 13}">линия (ядро)</text>']
    for i, (p, lab) in enumerate(ins):
        y = Y0 + 10 + 30 * i - 10
        ap.append(f'<text font-family="SansSerif" font-size="11" text-anchor="start" x="{X0 + 5}" y="{y + 4}">{lab}</text>')
        ap.append(f'<circ-port height="8" pin="{p[0]},{p[1]}" width="8" x="{X0 - 4}" y="{y - 4}"/>')
    for i, (p, lab) in enumerate(outs):
        y = Y0 + 40 * i
        ap.append(f'<text font-family="SansSerif" font-size="11" text-anchor="end" x="{X0 + BW - 5}" y="{y + 4}">{lab}</text>')
        ap.append(f'<circ-port height="10" pin="{p[0]},{p[1]}" width="10" x="{X0 + BW - 5}" y="{y - 5}"/>')
    ap.append(f'<circ-anchor facing="east" height="6" width="6" x="{X0 - 3}" y="{Y0 - 3}"/>')
    c.appear = ap
    return c


# смещения портов блока линии относительно точки вставки (якорь = порт Z0X)
LANE_IN = {lab: (0, 30 * i) for i, lab in enumerate(["Z0X", "Z0Y", "KX", "KY", "LOAD", "CLK"])}
LANE_OUT = {lab: (140, 40 * i) for i, lab in enumerate(["ZX", "ZY", "N", "ESC"])}


# ---------------------------------------------------------------- 4 линии
def simt4():
    c = Circuit("simt4")
    TW.update(KX=16, KY=16, STEP=8, STEP1=8)
    c.text((520, 20), "SIMT: 4 линии выполняют одну общую команду над 4 пикселями (вариант 14, k = -0.8 + 0.156i)")

    # ---- устройство управления (общий поток команд)
    c.text((170, 60), "Устройство управления", font="SansSerif bold 12")
    c.comp("wiring", "Clock", (60, 100), label="CLK")
    c.wire((60, 100), (100, 100))
    tunnel(c, (100, 100), "CLK", "west")
    # триггер «начало»: после первого такта Q=1, nQ (=LOAD) = 0
    tunnel(c, (140, 150), "CLK", "east")          # вход тактов D-триггера
    c.wire((140, 150), (160, 150))
    c.comp("wiring", "Constant", (140, 170))      # D = 1
    c.wire((140, 170), (160, 170))
    c.comp("memory", "D Flip-Flop", (200, 150), label="START")
    pin_in(c, (60, 230), "RESTART")
    c.gate("OR", (300, 180), n=2, size=30)
    c.wire((200, 170), (270, 170))
    c.wire((60, 230), (250, 230), (250, 190), (270, 190))
    c.wire((300, 180), (330, 180))
    tunnel(c, (330, 180), "LOAD", "west")
    c.text((210, 255), "LOAD = 1 на первом такте (загрузка z0), далее ITER", font=SMALL)

    # общие операнды kx, ky
    c.comp("wiring", "Constant", (100, 320), width="16", value=hex16(K_X))
    c.wire((100, 320), (130, 320))
    tunnel(c, (130, 320), "KX", "west")
    c.comp("wiring", "Constant", (100, 360), width="16", value=hex16(K_Y))
    c.wire((100, 360), (130, 360))
    tunnel(c, (130, 360), "KY", "west")
    c.text((110, 295), "kx, ky (Q4.12), общие для всех линий", font=SMALL)

    # счётчик шагов STEP и halt
    c.comp("plexers", "Multiplexer", (120, 460), width="8", enable="false")
    tunnel(c, (80, 450), "STEP1", "east")
    c.wire((80, 450), (90, 450))
    c.comp("wiring", "Constant", (80, 470), width="8", value="0x0")
    c.wire((80, 470), (90, 470))
    c.wire((100, 480), (100, 500))
    tunnel(c, (100, 500), "LOAD", "north")
    c.comp("memory", "Register", (200, 460), width="8", label="STEP")
    c.wire((120, 460), (170, 460))
    c.wire((180, 480), (180, 500))
    tunnel(c, (180, 500), "CLK", "north")
    c.wire((200, 460), (240, 460))
    tunnel(c, (240, 460), "STEP", "west")
    c.comp("arith", "Adder", (300, 420), width="8")
    tunnel(c, (240, 410), "STEP", "east")
    c.wire((240, 410), (260, 410))
    c.comp("wiring", "Constant", (240, 430), width="8", value="0x1")
    c.wire((240, 430), (260, 430))
    c.wire((300, 420), (330, 420))
    tunnel(c, (330, 420), "STEP1", "west")
    c.comp("arith", "Comparator", (300, 530), width="8", mode="unsigned")
    tunnel(c, (240, 520), "STEP", "east")
    c.wire((240, 520), (260, 520))
    c.comp("wiring", "Constant", (240, 540), width="8", value=hex(MAXSTEP))
    c.wire((240, 540), (260, 540))
    c.gate("OR", (380, 580), n=2, size=30)
    c.wire((300, 530), (330, 530), (330, 570), (350, 570))
    tunnel(c, (330, 590), "ALLESC", "east")
    c.wire((330, 590), (350, 590))
    c.wire((380, 580), (420, 580))
    pin_out(c, (420, 580), "halt")
    tunnel(c, (380, 660), "STEP", "east")
    c.wire((380, 660), (420, 660))
    pin_out(c, (420, 660), "STEP", 8)
    c.comp("wiring", "Probe", (390, 700), radix="10unsigned")
    c.wire((390, 660), (390, 700))
    c.text((440, 625), f"halt: STEP = {MAXSTEP} или все линии ушли", font=SMALL)
    # маска ушедших линий (бит i = ESCi), туннели разнесены с шагом 30
    c.comp("wiring", "Splitter", (330, 820), fanout="4", incoming="4", appear="center", facing="west")
    for i, (sy, xb) in enumerate(((770, 300), (800, 290), (830, 290), (860, 300))):
        tunnel(c, (220, sy), f"ESC{i}", "east")
        c.wire((220, sy), (xb, sy), (xb, 800 + 10 * i), (310, 800 + 10 * i))
    c.wire((330, 820), (360, 820), (460, 820))
    pin_out(c, (460, 820), "ESCMASK", 4)
    c.text((300, 750), "маска ушедших линий", font=SMALL)
    # все линии ушли: ESCMASK = 1111
    c.comp("arith", "Comparator", (420, 880), width="4", mode="unsigned")
    c.wire((360, 820), (360, 870), (380, 870))
    c.comp("wiring", "Constant", (360, 890), width="4", value="0xf")
    c.wire((360, 890), (380, 890))
    c.wire((420, 880), (450, 880))
    tunnel(c, (450, 880), "ALLESC", "west")
    c.text((420, 920), "все линии ушли?", font=SMALL)

    # ---- 4 линии
    LX = 640
    for i, (px, py, zx, zy) in enumerate(PIXELS):
        ly = 80 + 220 * i
        c.comp("wiring", "Constant", (LX - 60, ly), width="16", value=hex16(zx))
        c.wire((LX - 60, ly), (LX, ly))
        c.comp("wiring", "Constant", (LX - 60, ly + 30), width="16", value=hex16(zy))
        c.wire((LX - 60, ly + 30), (LX, ly + 30))
        for lab in ("KX", "KY", "LOAD", "CLK"):
            dx, dy = LANE_IN[lab]
            tunnel(c, (LX - 30, ly + dy), lab, "east")
            c.wire((LX - 30, ly + dy), (LX, ly + dy))
        c.comp(None, "julia_lane", (LX, ly), label=f"lane{i}")
        c.text((LX - 150, ly + 5), f"пиксель {i}", font="SansSerif bold 11")
        c.text((LX - 150, ly + 20), f"({px}, {py})", font=SMALL)
        ox = LX + 140
        for lab, w in (("ZX", 16), ("ZY", 16), ("N", 8), ("ESC", 1)):
            dx, dy = LANE_OUT[lab]
            y = ly + dy
            xe = ox + 220
            c.wire((ox, y), (xe, y))
            pin_out(c, (xe, y), f"{lab}{i}", w)
            if lab == "N":
                c.comp("wiring", "Probe", (ox + 100, y - 20), radix="10unsigned")
                c.wire((ox + 100, y), (ox + 100, y - 20))
            elif lab in ("ZX", "ZY"):
                c.comp("wiring", "Probe", (ox + 100, y - 20), radix="16")
                c.wire((ox + 100, y), (ox + 100, y - 20))
            else:
                c.wire((ox + 40, y), (ox + 40, y + 20))
                tunnel(c, (ox + 40, y + 20), f"ESC{i}", "north")
    return c


def main():
    lane_c = lane()
    main_c = simt4()
    xml = project_xml([main_c, lane_c], main="simt4")
    with open(os.path.join(HERE, "pr12.circ"), "w", encoding="utf-8") as f:
        f.write(xml)
    print("pr12.circ written")


if __name__ == "__main__":
    main()
