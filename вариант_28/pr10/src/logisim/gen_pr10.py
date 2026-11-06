"""Аппаратная реализация функции варианта 28 (замена пробела на '_') для Logisim 2.7.1.

pr10_replspace.circ, две схемы:
  repl_branch   — «с ветвлением»: компаратор c == 0x20 + мультиплексор (0x5F либо c);
  repl_nobranch — «без ветвления»: out = c + (is_space ? 0x3F : 0), 0x20 + 0x3F = 0x5F.
Обе дают одинаковый результат для любого байта 0..255.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
sys.path.insert(0, os.path.join(HERE, "../../../pr03/src/logisim"))
from lgen import Circuit, build  # noqa: E402
from gen_pr03 import splitter  # noqa: E402

OUT = os.path.join(HERE, "pr10_replspace.circ")


def common(c):
    c.pin_in((80, 120), "c", width=8)
    c.add("wiring", "Probe", (300, 120), {0: ("c", "west", 20)}, radix="16", facing="west")
    c.const((80, 260), 0x20, "SP", width=8)        # пробел
    # c == 0x20 (беззнаковое сравнение): порт EQ=3
    c.add("arith", "Comparator", (320, 230), {0: "c", 1: "SP", 3: ("ISSP", "east", 20)},
          width=8, mode="unsigned")
    c.add("io", "LED", (520, 230), {0: ("ISSP", "west", 20)}, label="is_space", labelloc="east")


def make_branch():
    c = Circuit("repl_branch")
    c.text((520, 30), "repl с ветвлением: if c == 0x20 then '_' (0x5F) else c (вариант 28)")
    common(c)
    c.const((640, 120), 0x5F, "UND", width=8)      # '_'
    c.add("plexers", "Multiplexer", (1000, 200), {0: ("c", "west", 20), 1: ("UND", "west", 70),
                                                  2: ("ISSP", "south", 20), 3: ("OUT", "east", 30)},
          select=1, width=8, enable="false")
    c.pin_out((1180, 200), "out", net="OUT", width=8)
    c.add("wiring", "Probe", (1180, 280), {0: ("OUT", "west", 20)}, radix="16", facing="west")
    return c


def make_nobranch():
    c = Circuit("repl_nobranch")
    c.text((520, 30), "repl без ветвления: out = c + (is_space·0x3F), 0x20 + 0x3F = 0x5F (вариант 28)")
    common(c)
    # маска: is_space, расширенный знаково в 0xFF, И с 0x3F -> 0x3F для пробела, иначе 0
    c.add("wiring", "Bit Extender", (700, 360), {0: ("MASKF", "east", 30), 1: ("ISSP", "west", 30)},
          in_width=1, out_width=8, type="sign")
    c.const((700, 440), 0x3F, "M3F", width=8)
    c.add("gates", "AND Gate", (900, 390), {0: "MASK", 1: ("MASKF", "west", 20), 2: ("M3F", "west", 70)},
          size=30, inputs=2, width=8)
    c.add("arith", "Adder", (1120, 170), {0: "c", 1: "MASK", 2: ("OUT", "east", 30)}, width=8)
    c.pin_out((1320, 170), "out", net="OUT", width=8)
    c.add("wiring", "Probe", (1320, 250), {0: ("OUT", "west", 20)}, radix="16", facing="west")
    return c


if __name__ == "__main__":
    build([make_branch(), make_nobranch()], OUT, main="repl_branch")
    print("wrote", OUT)
