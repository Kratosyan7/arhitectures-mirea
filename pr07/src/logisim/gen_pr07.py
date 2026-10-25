"""Модель приоритетного контроллера прерываний со стеком (вариант 14) для Logisim 2.7.1: pr07_pic.circ.

Линии: IRQ0 — HDD, IRQ1 — Тачпад, IRQ2 — Клавиатура, IRQ3 — Плоттер (IRQ0 — высший приоритет).
Векторы (начала ПОП): 0x0065, 0x00C9, 0x012D, 0x0191.
LVL — уровень обслуживаемого прерывания: 0 — основная программа, k+1 — выполняется ПОП IRQk.
Запрос принимается (INT = 1), если LVL = 0 или его уровень выше (номер меньше) текущего.
По фронту CLK при INT = 1: в стек заносится {LVL, PC + 1}, LVL ← уровень запроса, переход по вектору.
По фронту CLK при IRET = 1: из стека восстанавливаются адрес возврата и LVL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
sys.path.insert(0, os.path.join(HERE, "../../../pr03/src/logisim"))
from lgen import Circuit, build  # noqa: E402
from gen_pr03 import splitter  # noqa: E402

OUT = os.path.join(HERE, "pr07_pic.circ")
DEVICES = ["HDD", "Тачпад", "Клавиатура", "Плоттер"]
VECTORS = [0x0065, 0x00C9, 0x012D, 0x0191]


def probe(c, loc, net, radix="16"):
    return c.add("wiring", "Probe", loc, {0: (net, "west", 20)}, radix=radix, facing="west")


def make():
    c = Circuit("PIC")
    c.text((640, 30), "Приоритетный контроллер прерываний и стек возвратов (вариант 14)")
    for k, dev in enumerate(DEVICES):
        c.pin_in((240, 110 + 50 * k), f"IRQ{k} {dev}", net=f"IRQ{k}")
    c.pin_in((240, 340), "PC (текущая команда)", net="PC", width=16)
    c.pin_in((240, 430), "IRET", net="IRET")
    c.pin_in((240, 480), "CLK", net="CLK")
    # Приоритетный шифратор Logisim выбирает старший номер входа, поэтому линии подаются в обратном порядке
    c.add("plexers", "Priority Encoder", (440, 160), {0: ("IRQ3", "west", 20), 1: ("IRQ2", "west", 70),
                                                      2: ("IRQ1", "west", 20), 3: ("IRQ0", "west", 70),
                                                      4: ("PRI", "east", 30), 7: ("ANY", "east", 70)},
          select=2, disabled="0")
    c.const((560, 280), 3, "THREE", width=2)
    c.add("arith", "Subtractor", (720, 180), {0: ("THREE", "west", 70), 1: ("PRI", "west", 20), 2: ("REQ", "east", 30)}, width=2)
    c.const((300, 330), 0, "ZERO1")
    c.add("arith", "Adder", (560, 330), {0: ("REQ3", "west", 30), 1: ("ONE3", "west", 30), 2: ("RQLV", "east", 30)},
          width=3)
    splitter(c, (420, 400), 3, [0, 0, 1], ["REQ3", "REQ", "ZERO1"])  # REQ, расширенный до 3 бит
    c.const((420, 460), 1, "ONE3", width=3)
    # INT = ANY ∧ (LVL = 0 ∨ RQLV < LVL)
    c.const((640, 580), 0, "ZERO3", width=3)
    c.add("arith", "Comparator", (780, 400), {0: "RQLV", 1: "LVL", 4: ("HIGHER", "east", 20)}, width=3,
          mode="unsigned")
    c.add("arith", "Comparator", (780, 480), {0: "LVL", 1: "ZERO3", 3: ("IDLE", "east", 20)}, width=3,
          mode="unsigned")
    c.add("gates", "OR Gate", (920, 440), {0: "ALLOW", 1: ("HIGHER", "west", 20), 2: ("IDLE", "west", 70)},
          size=30, inputs=2)
    c.add("gates", "AND Gate", (1060, 420), {0: "INT", 1: ("ANY", "west", 20), 2: ("ALLOW", "west", 70)},
          size=30, inputs=2)
    c.add("gates", "NOT Gate", (920, 540), {0: "NINT", 1: "INT"}, size=30)
    c.add("gates", "AND Gate", (1060, 540), {0: "POP", 1: ("IRET", "west", 20), 2: ("NINT", "west", 70)},
          size=30, inputs=2)
    c.add("gates", "OR Gate", (1060, 620), {0: "STEP", 1: ("INT", "west", 20), 2: ("POP", "west", 70)},
          size=30, inputs=2)
    # Таблица векторов (IDT)
    for k, v in enumerate(VECTORS):
        c.const((460, 620 + 40 * k), v, f"VEC{k}", width=16)
    c.add("plexers", "Multiplexer", (760, 660), {0: ("VEC0", "west", 20), 1: ("VEC1", "west", 70),
                                                 2: ("VEC2", "west", 20), 3: ("VEC3", "west", 70),
                                                 4: ("REQ", "south", 20), 5: ("ANY", "south", 20, "east", 30),
                                                 6: ("VEC", "east", 30)},
          select=2, width=16, enable="true", disabled="0", label="IDT")
    # Стек возвратов: RAM 4×19 (уровень 3 бита + адрес 16 бит), указатель стека SP
    c.const((1200, 120), 1, "ONE16", width=16)
    c.add("arith", "Adder", (1360, 120), {0: "PC", 1: "ONE16", 2: ("NEXT", "east", 30)}, width=16)
    splitter(c, (1240, 230), 19, [0] * 16 + [1] * 3, ["SDIN", "NEXT", "LVL"])
    c.const((1200, 330), 1, "ONE2", width=2)
    c.add("arith", "Adder", (1360, 330), {0: "SP", 1: "ONE2", 2: ("SPINC", "east", 30)}, width=2)
    c.add("arith", "Subtractor", (1360, 410), {0: "SP", 1: "ONE2", 2: ("SPDEC", "east", 30)}, width=2)
    c.add("plexers", "Multiplexer", (1520, 370), {0: ("SPDEC", "west", 20), 1: ("SPINC", "west", 70),
                                                  2: ("INT", "south", 20), 3: ("SPN", "east", 30)},
          select=1, width=2, enable="false")
    c.add("memory", "Register", (1680, 370), {0: ("SP", "east", 30), 1: ("SPN", "west", 50),
                                              2: ("CLK", "south", 20), 4: ("STEP", "west", 20, "south", 40)},
          width=2, label="SP")
    c.add("plexers", "Multiplexer", (1520, 500), {0: ("SPDEC", "west", 20), 1: ("SP", "west", 70),
                                                  2: ("INT", "south", 20), 3: ("SADDR", "east", 30)},
          select=1, width=2, enable="false")
    c.add("memory", "RAM", (1820, 620), {0: ("STOP", "east", 30), 1: ("SADDR", "west", 30),
                                         3: ("ONE1", "south", 30), 5: ("CLK", "south", 60),
                                         6: ("INT", "south", 30), 7: ("SDIN", "west", 30)},
          addrWidth=2, dataWidth=19, bus="separate", label="Стек")
    c.const((1700, 720), 1, "ONE1")
    splitter(c, (1240, 800), 19, [0] * 16 + [1] * 3, ["STOP", "RET", "RLVL"])
    # Регистр уровня обслуживания
    c.add("plexers", "Multiplexer", (1520, 800), {0: ("RLVL", "west", 20), 1: ("RQLV", "west", 70),
                                                  2: ("INT", "south", 20), 3: ("LVLN", "east", 30)},
          select=1, width=3, enable="false")
    c.add("memory", "Register", (1680, 800), {0: ("LVL", "east", 30), 1: ("LVLN", "west", 50),
                                              2: ("CLK", "south", 20), 4: ("STEP", "west", 20, "south", 40)},
          width=3, label="LVL")
    # Индикация
    c.add("io", "LED", (200, 600), {0: ("INT", "west", 20)}, label="INT (запрос принят)", labelloc="east")
    probe(c, (200, 680), "REQ", "10unsigned")
    c.text((140, 660), "IRQ запроса")
    probe(c, (200, 760), "VEC")
    c.text((140, 740), "Вектор (адрес ПОП)")
    probe(c, (200, 840), "NEXT")
    c.text((140, 820), "Адрес возврата")
    probe(c, (200, 920), "RET")
    c.text((140, 900), "Вершина стека")
    probe(c, (200, 1000), "LVL", "10unsigned")
    c.text((140, 980), "LVL (0 — осн. программа)")
    c.pin_out((1000, 760), "INT", net="INT")
    c.pin_out((1000, 820), "VEC", net="VEC", width=16)
    c.pin_out((1000, 880), "RET", net="RET", width=16)
    c.pin_out((1000, 940), "LVL", net="LVL", width=3)
    c.pin_out((1000, 1000), "SP", net="SP", width=2)
    return c


if __name__ == "__main__":
    build([make()], OUT)
    print("wrote", OUT)
