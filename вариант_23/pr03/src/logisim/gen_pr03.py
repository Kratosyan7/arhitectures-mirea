"""Генерация модели учебного ОУ (рис. 3.4) для Logisim 2.7.1: pr03_ou.circ.

Схема «ALU» — 16-разрядное АЛУ по табл. 3.1, схема «OU» — операционное устройство:
регистры OutR, InpR, MDR, MAR, IR, AC, PC, мультиплексоры MS A / MS B / MS M,
дешифратор DC, ОЗУ 4K×16 и регистр флагов. Управляющее слово (18 бит) задаётся
входными пинами MSA, MSB, F, M, S2, S1, S0, C0, E, DC, MSM, WR; запись — фронт CLK.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../tools/logisim"))
from lgen import Circuit, build  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pr03_ou.circ")


def alt(nets, side="west", near=20, far=70):
    """Порты, идущие с шагом 10: чередуем длину отвода, чтобы туннели не налезали."""
    return {i: (n, side, near if i % 2 == 0 else far) for i, n in enumerate(nets)}


def splitter(c, loc, incoming, mapping, nets, facing="east"):
    """mapping: номер выхода для каждого бита (None — бит не выводится)."""
    fan = max(m for m in mapping if m is not None) + 1
    attrs = {"facing": facing, "fanout": fan, "incoming": incoming, "appear": "left"}
    for b, m in enumerate(mapping):
        attrs[f"bit{b}"] = "none" if m is None else m
    conns = {0: (nets[0], "west", 20)}
    for i, n in enumerate(nets[1:]):
        if n:
            conns[i + 1] = (n, "east", 20 if i % 2 == 0 else 70)
    return c.add("wiring", "Splitter", loc, conns, **attrs)


def make_alu():
    c = Circuit("ALU")
    c.text((520, 30), "АЛУ 16 разрядов (табл. 3.1): код F M S2 S1 S0 C0")
    ins = [("A", 16), ("B", 16), ("F", 1), ("M", 1), ("S2", 1), ("S1", 1), ("S0", 1), ("C0", 1)]
    for i, (n, w) in enumerate(ins):
        c.pin_in((60, 80 + 40 * i), n, width=w)
    outs = [("R", 16), ("Z", 1), ("S", 1), ("C", 1), ("V", 1)]
    for i, (n, w) in enumerate(outs):
        c.pin_out((1600, 120 + 40 * i), n, net=n if n != "S" else "SF", width=w)

    c.const((140, 470), 0, "ZERO16", 16)
    c.const((140, 510), 0xFFFF, "ONES16", 16)
    c.const((140, 550), 1, "SH1", 4)
    c.const((140, 590), 2, "SH2", 4)
    # Арифметика (схема Мано): R = A + Y + C0, Y = 0 | B | ¬B | 1…1 по S1 S0
    c.add("gates", "NOT Gate", (300, 470), {0: "nB", 1: "B"}, width=16)
    c.add("gates", "NOT Gate", (300, 530), {0: "nA", 1: "A"}, width=16)
    splitter(c, (300, 600), 2, [0, 1], ["S10", "S0", "S1"])
    c.add("plexers", "Multiplexer", (480, 160), {**alt(["ZERO16", "B", "nB", "ONES16"], far=90), 4: ("S10", "south", 20), 5: "Y"},
          select=2, width=16, enable="false")
    c.add("arith", "Adder", (640, 160), {0: "A", 1: "Y", 2: "ARITH", 3: ("C0", "north"), 4: ("CO", "south")}, width=16)
    c.add("arith", "Adder", (640, 320), {0: "B", 1: "nA", 2: "BMA", 3: ("C0", "north")}, width=16)
    # Логика
    for i, (g, net) in enumerate([("OR", "OR"), ("XOR", "XOR"), ("AND", "AND"), ("NAND", "NAND"),
                                  ("NOR", "NOR"), ("XNOR", "XNOR")]):
        y = 420 + 70 * i
        c.add("gates", f"{g} Gate", (660, y), {0: net, 1: "A", 2: "B"}, width=16, size=30, inputs=2)
    # Сдвиги
    for i, (kind, amt, net) in enumerate([("ll", "SH1", "SHL"), ("lr", "SH1", "SHR"), ("rl", "SH1", "ROL"),
                                          ("rr", "SH1", "ROR"), ("ar", "SH1", "ASR"), ("rl", "SH2", "ROL2"),
                                          ("rr", "SH2", "ROR2")]):
        y = 380 + 60 * i
        c.add("arith", "Shifter", (880, y), {0: "A", 1: amt, 2: net}, width=16, shift=kind)
    # Выбор результата. F=0 — «арифметика и стандартные логические операции»: по (M,S2) —
    # 00 арифметика, 01 логика (S1 S0: ∨ ⊕ ∧ ¬A), 1x — не используется.
    # F=1 — «расширенные логические/сдвиговые»: M=0 — B−A(−1), НЕ-И, НЕ-ИЛИ, искл. ИЛИ-НЕ;
    # M=1 — сдвиги: S2 S1 S0 = 000 ←, 001 →, 010 цикл ←, 011 цикл →, 100 ×2, 101 ÷2, 110 цикл ←2, 111 цикл →2
    splitter(c, (300, 680), 2, [0, 1], ["MS2", "S2", "M"])
    splitter(c, (300, 760), 4, [0, 1, 2, 3], ["MS210", "S0", "S1", "S2", "M"])
    c.add("plexers", "Multiplexer", (880, 120), {**alt(["OR", "XOR", "AND", "nA"]), 4: ("S10", "south", 20), 5: "LOG"},
          select=2, width=16, enable="false")
    c.add("plexers", "Multiplexer", (1120, 120), {**alt(["ARITH", "LOG", "ZERO16", "ZERO16"]), 4: ("MS2", "south", 20),
                                                  5: "R0"}, select=2, width=16, enable="false")
    c.add("plexers", "Multiplexer", (1340, 560), {**alt(["BMA", "NAND", "NOR", "XNOR"] + ["ZERO16"] * 4 +
                                                        ["SHL", "SHR", "ROL", "ROR", "SHL", "ASR", "ROL2", "ROR2"]),
                                                  16: ("MS210", "south", 20), 17: "R1"},
          select=4, width=16, enable="false")
    c.add("plexers", "Multiplexer", (1460, 250), {0: ("R0", "west", 20), 1: ("R1", "west", 70), 2: ("F", "south", 20),
                                                  3: "R"}, select=1, width=16, enable="false")
    # Флаги: Z = (R == 0), S = R[15], C и V — только для арифметики группы F=0
    c.add("arith", "Comparator", (1100, 520), {0: "R", 1: "ZERO16", 3: ("Z", "east")}, width=16)
    splitter(c, (1040, 600), 16, [0] * 15 + [1], ["R", None, "SF"])
    splitter(c, (1040, 680), 16, [0] * 15 + [1], ["A", None, "A15"])
    splitter(c, (1040, 760), 16, [0] * 15 + [1], ["Y", None, "Y15"])
    c.add("gates", "NOR Gate", (1160, 860), {0: "ARS", 1: ("F", "west", 20), 2: ("M", "west", 70), 3: ("S2", "west", 20)}, inputs=3, size=30)
    c.add("gates", "AND Gate", (1160, 940), {0: "C", 1: "CO", 2: "ARS"}, inputs=2, size=30)
    c.add("gates", "XNOR Gate", (900, 860), {0: "SGN_EQ", 1: "A15", 2: "Y15"}, inputs=2, size=30)
    c.add("gates", "XOR Gate", (900, 940), {0: "SGN_CH", 1: "A15", 2: "SF"}, inputs=2, size=30)
    c.add("gates", "AND Gate", (1160, 1020), {0: "V", 1: ("SGN_EQ", "west", 20), 2: ("SGN_CH", "west", 90), 3: ("ARS", "west", 20)}, inputs=3, size=30)
    return c


def rom_text(addr_bits, data_bits, words):
    """Содержимое ПЗУ Logisim ("addr/data: A D" + hex с RLE N*val)."""
    last = max(words) if words else 0
    vals = [words.get(a, 0) for a in range(last + 1)]
    toks, i = [], 0
    while i < len(vals):
        j = i
        while j < len(vals) and vals[j] == vals[i]:
            j += 1
        n = j - i
        if n >= 4:
            toks.append(f"{n}*{vals[i]:x}")
        else:
            toks.extend(f"{vals[i]:x}" for _ in range(n))
        i = j
    lines = [" ".join(toks[k:k + 8]) for k in range(0, len(toks), 8)]
    return f"addr/data: {addr_bits} {data_bits}\n" + "\n".join(lines) + "\n"


def make_ou(alu, c=None, dx=0, pins=True, rom=None,
            title="Учебное операционное устройство (рис. 3.4). Вариант 14: MDR ← IR ⊕ AC"):
    """ОУ по рис. 3.4. pins=False — управляющие сигналы приходят по туннелям (от УУ);
    rom — словарь {адрес: слово}: вместо ОЗУ ставится ПЗУ с этим содержимым."""
    own = c is None
    if own:
        c = Circuit("OU")
    c.text((700 + dx, 30), title)
    if pins:
        ctrl = [("MSA", 3), ("MSB", 3), ("F", 1), ("M", 1), ("S2", 1), ("S1", 1), ("S0", 1), ("C0", 1),
                ("E", 1), ("DC", 3), ("MSM", 1), ("WR", 1), ("CLK", 1)]
        c.text((150, 70), "Управляющее слово")
        y = 110
        for n, w in ctrl:
            c.pin_in((80, y), n, width=w)
            y += 40 if n not in ("MSB", "C0", "DC", "WR") else 60
        c.pin_in((140, y + 30), "Ввод", net="IN", width=16)
    else:
        c.pin_in((260 + dx, 1100), "Ввод", net="IN", width=16)
    X = lambda x, y: (x + dx, y)  # noqa: E731

    regs = ["OutR", "InpR", "MDR", "MAR", "IR", "AC", "PC"]  # выходы DC 1…7
    for i, r in enumerate(regs):
        y = 120 + 110 * i
        d = "MDRIN" if r == "MDR" else "S"
        c.add("memory", "Register", X(500, y), {0: (r, "east", 30), 1: (d, "west", 50), 2: ("CLK", "south", 20),
                                              4: (f"en{i + 1}", "west", 20, "south", 40)}, width=16, label=r)
    c.add("plexers", "Decoder", X(300, 980), {**{k: (f"en{k}", "east", 20 if k % 2 == 0 else 70) for k in range(1, 8)},
                                             8: ("DC", "south", 30), 9: ("E", "west", 30)}, select=3, enable="true", disabled="0",
          label="DC")
    # MS M: 0 — S-шина, 1 — данные из ОЗУ
    c.add("plexers", "Multiplexer", X(300, 380), {0: ("S", "west", 20), 1: ("RAMOUT", "west", 70),
                                                 2: ("MSM", "south", 20), 3: ("MDRIN", "east", 30)},
          select=1, width=16, enable="false", label="MS M")
    # Мультиплексоры операндов: 0 PC, 1 AC, 2 IR, 3 MAR, 4 MDR, 5 InpR, 6 OutR, 7 Ввод
    srcs = ["PC", "AC", "IR", "MAR", "MDR", "InpR", "OutR", "IN"]
    c.add("plexers", "Multiplexer", X(820, 620), {**alt(srcs), 8: ("MSA", "south", 20), 9: ("OPA", "east", 30)},
          select=3, width=16, enable="false", label="MS A")
    c.add("plexers", "Multiplexer", X(820, 820), {**alt(srcs), 8: ("MSB", "south", 20), 9: ("OPB", "east", 30)},
          select=3, width=16, enable="false", label="MS B")
    c.sub(alu, X(1080, 700), {"A": "OPA", "B": "OPB", "F": "F", "M": "M", "S2": "S2", "S1": "S1", "S0": "S0",
                             "C0": "C0", "R": "S", "Z": "Z", "S": "SF", "C": "CF", "V": "VF"}, stub=20, label="ALU")
    c.pin_out(X(1300, 600), "S-шина", net="S", width=16)
    # ОЗУ 4K×16: адрес — младшие 12 бит MAR
    splitter(c, X(900, 200), 16, [0] * 12 + [None] * 4, ["MAR", "A12"])
    c.const(X(1100, 420), 1, "ONE")
    if rom is None:
        c.add("memory", "RAM", X(1300, 260), {0: ("RAMOUT", "east", 30), 1: ("A12", "west", 30),
                                             3: ("ONE", "south", 30), 5: ("CLK", "south", 60),
                                             6: ("WR", "south", 30), 7: ("MDR", "west", 30)},
              addrWidth=12, dataWidth=16, bus="separate", label="RAM")
    else:
        c.add("memory", "ROM", X(1300, 260), {0: ("RAMOUT", "east", 30), 1: ("A12", "west", 30)},
              addrWidth=12, dataWidth=16, contents=rom_text(12, 16, rom), label="Память (ПЗУ)")
    # Регистр флагов Z S C V
    splitter(c, X(1060, 960), 4, [0, 1, 2, 3], ["FLAGS", "Z", "SF", "CF", "VF"])
    c.add("memory", "Register", X(1300, 990), {0: ("FL", "east", 30), 1: ("FLAGS", "west", 50),
                                              2: ("CLK", "south", 20), 4: ("E", "west", 20, "south", 40)},
          width=4, label="Flags")
    return c


if __name__ == "__main__":
    alu = make_alu()
    ou = make_ou(alu, title="Учебное операционное устройство (рис. 3.4). Вариант 23: OUTR ← AC NOR OUTR")
    build([ou, alu], OUT, main="OU")
    print("wrote", OUT)
