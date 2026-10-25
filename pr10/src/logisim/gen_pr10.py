"""Аппаратная реализация функции варианта 14 (перевод буквы в нижний регистр) для Logisim 2.7.1.

pr10_tolower.circ, две схемы:
  tolower_branch   — «с ветвлением»: компараторы 'A' ≤ c ≤ 'Z' + мультиплексор (c | 0x20 либо c);
  tolower_nobranch — «без ветвления»: битовая маска out = c | (is_upper << 5).
Обе дают одинаковый результат для любого байта 0..255.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
sys.path.insert(0, os.path.join(HERE, "../../../pr03/src/logisim"))
from lgen import Circuit, build  # noqa: E402
from gen_pr03 import splitter  # noqa: E402

OUT = os.path.join(HERE, "pr10_tolower.circ")


def common(c):
    c.pin_in((80, 120), "c", width=8)
    c.add("wiring", "Probe", (300, 120), {0: ("c", "west", 20)}, radix="16", facing="west")
    c.const((80, 220), ord("A"), "A", width=8)
    c.const((80, 280), ord("Z"), "Z", width=8)
    # 'A' ≤ c  и  c ≤ 'Z'  (беззнаковое сравнение)
    # индексы портов компаратора: GT=2, EQ=3, LT=4
    c.add("arith", "Comparator", (320, 220), {0: "c", 1: "A", 2: ("GE_GT", "east", 20), 3: ("GE_EQ", "east", 70)},
          width=8, mode="unsigned")
    c.add("arith", "Comparator", (320, 320), {0: "c", 1: "Z", 4: ("LE_LT", "east", 20), 3: ("LE_EQ", "east", 70)},
          width=8, mode="unsigned")
    c.add("gates", "OR Gate", (480, 210), {0: "GE", 1: ("GE_GT", "west", 20), 2: ("GE_EQ", "west", 60)},
          size=30, inputs=2)   # c ≥ 'A'
    c.add("gates", "OR Gate", (480, 330), {0: "LE", 1: ("LE_LT", "west", 20), 2: ("LE_EQ", "west", 60)},
          size=30, inputs=2)   # c ≤ 'Z'
    c.add("gates", "AND Gate", (640, 270), {0: "UP", 1: ("GE", "west", 30), 2: ("LE", "west", 30)}, size=30, inputs=2)
    c.add("io", "LED", (760, 270), {0: ("UP", "west", 20)}, label="is_upper", labelloc="east")


def make_branch():
    c = Circuit("tolower_branch")
    c.text((520, 30), "tolower с ветвлением: if 'A' ≤ c ≤ 'Z' then c + 0x20 else c (вариант 14)")
    common(c)
    c.const((640, 120), 0x20, "SP", width=8)
    c.add("arith", "Adder", (820, 150), {0: "c", 1: "SP", 2: ("CLOW", "east", 30)}, width=8)
    c.add("plexers", "Multiplexer", (1000, 200), {0: ("c", "west", 20), 1: ("CLOW", "west", 70),
                                                  2: ("UP", "south", 20), 3: ("OUT", "east", 30)},
          select=1, width=8, enable="false")
    c.pin_out((1180, 200), "out", net="OUT", width=8)
    c.add("wiring", "Probe", (1180, 280), {0: ("OUT", "west", 20)}, radix="16", facing="west")
    return c


def make_nobranch():
    c = Circuit("tolower_nobranch")
    c.text((520, 30), "tolower без ветвления: out = c | (is_upper << 5) (вариант 14)")
    common(c)
    # маска: is_upper даёт бит 5 (0x20), если буква заглавная
    c.add("wiring", "Bit Extender", (820, 270), {0: ("MASKX", "east", 30), 1: ("UP", "west", 30)},
          in_width=1, out_width=8, type="zero")
    c.const((820, 360), 5, "SH5", width=3)
    c.add("arith", "Shifter", (1000, 290), {0: "MASKX", 1: "SH5", 2: ("MASK", "east", 30)}, width=8, shift="ll")
    c.add("gates", "OR Gate", (1160, 180), {0: "OUT", 1: ("c", "west", 20), 2: ("MASK", "west", 70)},
          size=30, inputs=2, width=8)
    c.pin_out((1320, 180), "out", net="OUT", width=8)
    c.add("wiring", "Probe", (1320, 260), {0: ("OUT", "west", 20)}, radix="16", facing="west")
    return c


if __name__ == "__main__":
    build([make_branch(), make_nobranch()], OUT, main="tolower_branch")
    print("wrote", OUT)
