"""Генерация pr01.circ (вариант 21): элемент «Исключающее ИЛИ» на транзисторах
(в базисе И-НЕ, рис. 1.7а), схемы функции F=E0E1 по СКНФ и по МДНФ.

Для варианта 21 требуются СКНФ и МДНФ:
  F(МДНФ) = ¬b¬d ∨ ¬b¬c ∨ abcd  (3 конъюнкции, 8 литералов).
"""
import os
from circgen import Circuit, project_xml

HERE = os.path.dirname(os.path.abspath(__file__))
VEC = 0xE0E1
ONES = [i for i in range(16) if (VEC >> (15 - i)) & 1]   # старший бит вектора = набор 0000
ZEROS = [i for i in range(16) if not (VEC >> (15 - i)) & 1]
VARS = ["a", "b", "c", "d"]


# ---------------------------------------------------------------- КМОП И-НЕ (ячейка)
def nand_cell(c, ox, oy, a_net, b_net, y_net, label):
    """КМОП-элемент И-НЕ (4 транзистора) по рис. 1.3 со смещением (ox, oy).
    Входы берутся из цепей a_net/b_net (туннели), выход — в цепь y_net."""
    def P(x, y):
        return (ox + x, oy + y)
    c.comp("wiring", "Power", P(250, 40))
    c.wire(P(250, 40), P(250, 60))
    c.wire(P(200, 60), P(300, 60))
    d1, s1, g1 = c.transistor(P(200, 140), "p", "south")   # VT1 (p), затвор A
    d2, s2, g2 = c.transistor(P(300, 140), "p", "south")   # VT2 (p), затвор B
    c.wire(P(200, 60), s1)
    c.wire(P(300, 60), s2)
    c.wire(d1, P(200, 170))
    c.wire(d2, P(300, 170))
    c.wire(P(200, 170), P(300, 170), P(430, 170))
    c.wire(P(430, 170), P(470, 170))
    c.tunnel(P(470, 170), y_net)                           # выход Y = ¬(A·B)
    d3, s3, g3 = c.transistor(P(200, 210), "n", "north")   # VT3 (n), затвор A
    d4, s4, g4 = c.transistor(P(200, 290), "n", "north")   # VT4 (n), затвор B
    c.wire(P(200, 170), d3)
    c.wire(s3, d4)
    c.wire(s4, P(200, 350))
    c.comp("wiring", "Ground", P(200, 350))
    # вход A -> затворы VT1, VT3
    c.wire(P(80, 120), P(140, 120), g1)
    c.wire(P(140, 120), P(140, 230), g3)
    c.tunnel(P(80, 120), a_net, facing="east")
    # вход B -> затворы VT2, VT4
    c.wire(P(80, 310), P(110, 310), g4)
    c.wire(P(110, 310), P(110, 80), P(260, 80), P(260, 120), g2)
    c.tunnel(P(80, 310), b_net, facing="east")
    c.text(P(230, 25), label, font="SansSerif plain 11")


def xor_cmos():
    """XOR в базисе И-НЕ (рис. 1.7а): 4 элемента И-НЕ, каждый на КМОП-транзисторах.
       g1=A·B̄ (A nand B); g2=A nand g1; g3=B nand g1; XOR=g2 nand g3."""
    c = Circuit("xor_cmos")
    c.text((420, 0), "Элемент «Исключающее ИЛИ» на транзисторах (базис И-НЕ, 4 ячейки КМОП И-НЕ)")
    # входные пины и шины A, B
    c.pin_in((40, 120), "A"); c.wire((40, 120), (90, 120)); c.tunnel((90, 120), "A")
    c.pin_in((40, 170), "B"); c.wire((40, 170), (90, 170)); c.tunnel((90, 170), "B")
    nand_cell(c, 120, 220, "A", "B", "G1", "И-НЕ 1: G1 = A·B")      # G1 = ¬(A·B)
    nand_cell(c, 720, 220, "A", "G1", "G2", "И-НЕ 2: G2 = A·G1")    # G2 = ¬(A·G1)
    nand_cell(c, 120, 640, "B", "G1", "G3", "И-НЕ 3: G3 = B·G1")    # G3 = ¬(B·G1)
    nand_cell(c, 720, 640, "G2", "G3", "XOR", "И-НЕ 4: XOR = G2·G3")  # XOR = ¬(G2·G3)
    c.wire((1230, 450), (1300, 450)); c.tunnel((1230, 450), "XOR", facing="east")
    c.pin_out((1300, 450), "Y")
    return c


# --------------------------------------------- шины литералов через туннели
def lit_rails(c, top=40, x0=100, step=70, rail_bottom=120):
    """Входные пины a,b,c,d; публикует литералы как цепи-туннели v и n<v>.
    Соединения с вентилями делаются туннелями, поэтому шорты-пересечения исключены."""
    x = x0
    for v in VARS:
        c.pin_in((x, top), v, facing="south", labelloc="north")
        c.wire((x, top), (x, 60)); c.tunnel((x, 60), v, facing="north")
        c.wire((x, 60), (x + 20, 60), (x + 20, 70))
        c.not_gate((x + 20, 100), size=30, facing="south")
        c.wire((x + 20, 100), (x + 20, rail_bottom)); c.tunnel((x + 20, rail_bottom), "n" + v, facing="south")
        x += step


def net_of(v, want_one):
    """Цепь-литерал: want_one=1 -> прямой v, иначе ¬v (nv)."""
    return v if want_one else "n" + v


def feed(c, pt, net, dx=40):
    """Короткий горизонтальный стаб из туннеля net к входу вентиля pt."""
    x0 = pt[0] - dx
    c.tunnel((x0, pt[1]), net, facing="east")
    c.wire((x0, pt[1]), pt)


def f_sknf():
    """Схема по СКНФ: по макстерму на каждый ноль функции, произведение дизъюнкций."""
    c = Circuit("F_sknf")
    c.text((330, 0), "F = E0E1: схема по СКНФ (9 конституент нуля)")
    lit_rails(c)
    gx = 440
    ys = [200 + 70 * k for k in range(len(ZEROS))]
    and_loc = (760, 480)
    and_in = c.gate("AND", and_loc, n=len(ZEROS), size=70)
    for k, (m, y) in enumerate(zip(ZEROS, ys)):
        ins = c.gate("OR", (gx, y), n=4, size=50)     # дизъюнкция: 1 -> инверсия
        for j, v in enumerate(VARS):
            bit = (m >> (3 - j)) & 1
            feed(c, ins[j], net_of(v, 1 - bit))       # 1 -> ¬v, 0 -> v
        xk = 500 + 12 * k
        c.wire((gx, y), (xk, y), (xk, and_in[k][1]), and_in[k])
        c.text((gx - 36, y - 26), f"M{m}", font="SansSerif plain 10")
    c.wire(and_loc, (830, 480))
    c.pin_out((830, 480), "F")
    return c


def f_mdnf():
    """Схема по МДНФ: F = ¬b¬d ∨ ¬b¬c ∨ abcd."""
    c = Circuit("F_mdnf")
    c.text((240, 0), "F = E0E1: схема по МДНФ  F = ¬b·¬d ∨ ¬b·¬c ∨ a·b·c·d")
    lit_rails(c)
    t1 = c.gate("AND", (520, 200), n=2, size=50)   # ¬b ∧ ¬d
    feed(c, t1[0], "nb"); feed(c, t1[1], "nd")
    t2 = c.gate("AND", (520, 320), n=2, size=50)   # ¬b ∧ ¬c
    feed(c, t2[0], "nb"); feed(c, t2[1], "nc")
    t3 = c.gate("AND", (520, 460), n=4, size=50)   # a ∧ b ∧ c ∧ d
    for pt, v in zip(t3, VARS):
        feed(c, pt, v)
    o = c.gate("OR", (720, 330), n=3, size=50)
    c.wire((520, 200), (600, 200), (600, o[0][1]), o[0])
    c.wire((520, 320), (620, 320), (620, o[1][1]), o[1])
    c.wire((520, 460), (640, 460), (640, o[2][1]), o[2])
    c.wire((720, 330), (780, 330))
    c.pin_out((780, 330), "F")
    return c


if __name__ == "__main__":
    circs = [xor_cmos(), f_sknf(), f_mdnf()]
    with open(os.path.join(HERE, "pr01.circ"), "w", encoding="utf-8") as f:
        f.write(project_xml(circs))
    print("ones:", ONES, "zeros:", ZEROS)
