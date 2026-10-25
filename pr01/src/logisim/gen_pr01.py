"""Генерация pr01.circ: КМОП-элемент И-НЕ, схемы функции F=55AA по СДНФ и по МКНФ."""
import os
from circgen import Circuit, project_xml

HERE = os.path.dirname(os.path.abspath(__file__))
VEC = 0x55AA
ONES = [i for i in range(16) if (VEC >> (15 - i)) & 1]   # старший бит вектора = набор 0000


def nand_cmos():
    c = Circuit("nand_cmos")
    c.text((250, 15), "КМОП-элемент И-НЕ (NAND)")
    c.comp("wiring", "Power", (250, 40))
    c.wire((250, 40), (250, 60))
    c.wire((200, 60), (300, 60))
    d1, s1, g1 = c.transistor((200, 140), "p", "south")   # VT1 (p), затвор A
    d2, s2, g2 = c.transistor((300, 140), "p", "south")   # VT2 (p), затвор B
    c.wire((200, 60), s1)
    c.wire((300, 60), s2)
    c.wire(d1, (200, 170))
    c.wire(d2, (300, 170))
    c.wire((200, 170), (300, 170), (420, 170))
    c.pin_out((420, 170), "Y")
    d3, s3, g3 = c.transistor((200, 210), "n", "north")   # VT3 (n), затвор A
    d4, s4, g4 = c.transistor((200, 290), "n", "north")   # VT4 (n), затвор B
    c.wire((200, 170), d3)
    c.wire(s3, d4)
    c.wire(s4, (200, 350))
    c.comp("wiring", "Ground", (200, 350))
    # вход A -> VT1, VT3
    c.pin_in((60, 120), "A")
    c.wire((60, 120), (140, 120), g1)
    c.wire((140, 120), (140, 230), g3)
    # вход B -> VT2, VT4
    c.pin_in((60, 310), "B")
    c.wire((60, 310), (110, 310), g4)
    c.wire((110, 310), (110, 80), (260, 80), (260, 120), g2)
    c.text((225, 108), "VT1", font="SansSerif plain 11")
    c.text((325, 108), "VT2", font="SansSerif plain 11")
    c.text((225, 255), "VT3", font="SansSerif plain 11")
    c.text((225, 335), "VT4", font="SansSerif plain 11")
    return c


VARS = ["a", "b", "c", "d"]


def rails(c, used, top=40, bottom=700, x0=100, step=70):
    """Вертикальные шины x и ¬x для переменных; возвращает {('a',1):x, ('a',0):x}"""
    pos = {}
    x = x0
    for v in VARS:
        c.pin_in((x, top), v, facing="south", labelloc="north")
        if v in used:
            c.wire((x, top), (x, 60), (x, bottom))
            c.wire((x, 60), (x + 20, 60), (x + 20, 70))
            out = c.not_gate((x + 20, 100), size=30, facing="south")
            c.wire((x + 20, 100), (x + 20, bottom))
            pos[(v, 1)] = x
            pos[(v, 0)] = x + 20
        x += step
    return pos


def f_sdnf():
    c = Circuit("F_sdnf")
    c.text((330, 0), "F = 55AA: схема по СДНФ (8 конституент единицы)")
    pos = rails(c, VARS, bottom=650)
    gx = 440
    ys = [130 + 70 * k for k in range(len(ONES))]
    or_loc = (680, 400)
    or_in = c.gate("OR", or_loc, n=8, size=70)
    for k, (m, y) in enumerate(zip(ONES, ys)):
        ins = c.gate("AND", (gx, y), n=4, size=50)
        for j, v in enumerate(VARS):
            bit = (m >> (3 - j)) & 1
            c.wire((pos[(v, bit)], ins[j][1]), ins[j])
        xk = 470 + 10 * k
        c.wire((gx, y), (xk, y), (xk, or_in[k][1]), or_in[k])
        c.text((gx - 25, y - 28), f"m{m}", font="SansSerif plain 10")
    c.wire(or_loc, (740, 400))
    c.pin_out((740, 400), "F")
    return c


def f_mknf():
    c = Circuit("F_mknf")
    c.text((260, 0), "F = 55AA: схема по МКНФ  F = (a ∨ d)(¬a ∨ ¬d)")
    pos = rails(c, ["a", "d"], bottom=280)
    o1 = c.gate("OR", (440, 160), n=2, size=50)
    o2 = c.gate("OR", (440, 260), n=2, size=50)
    c.wire((pos[("a", 1)], o1[0][1]), o1[0])
    c.wire((pos[("d", 1)], o1[1][1]), o1[1])
    c.wire((pos[("a", 0)], o2[0][1]), o2[0])
    c.wire((pos[("d", 0)], o2[1][1]), o2[1])
    a = c.gate("AND", (560, 210), n=2, size=50)
    c.wire((440, 160), (480, 160), (480, a[0][1]), a[0])
    c.wire((440, 260), (480, 260), (480, a[1][1]), a[1])
    c.wire((560, 210), (620, 210))
    c.pin_out((620, 210), "F")
    c.text((210, 330), "входы b и c в МКНФ не входят (функция от них не зависит)",
           font="SansSerif plain 11")
    return c


if __name__ == "__main__":
    circs = [nand_cmos(), f_sdnf(), f_mknf()]
    with open(os.path.join(HERE, "pr01.circ"), "w", encoding="utf-8") as f:
        f.write(project_xml(circs))
    print("ones:", ONES)
