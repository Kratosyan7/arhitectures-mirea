"""Модель учебной ВМ (УУ + ОУ) для Logisim 2.7.1: pr04_cu.circ.

УУ микропрограммное (рис. 4.1): генератор + схема совпадения (SE), счётчик тактов t,
триггеры циклов F,R, дешифраторы циклов/тактов/команд и ПЗУ микрокоманд.
Адрес ПЗУ микрокоманд = КОП(4) · F R(2) · t(2); слово (20 бит) =
MS(A) MS(B) АЛУ(F M S2 S1 S0 C0) DC(E x2 x1 x0) MS(M) WR FR — как в табл. 4.7/4.9.
ОУ — из pr03 (рис. 3.4), память команд/данных — ПЗУ с программой варианта 14.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
sys.path.insert(0, os.path.join(HERE, "../../../pr03/src/logisim"))
from lgen import Circuit, build  # noqa: E402
from gen_pr03 import alt, make_alu, make_ou, rom_text, splitter  # noqa: E402

OUT = os.path.join(HERE, "pr04_cu.circ")

# Коды входов MS A / MS B (рис. 3.4) и выходов DC
MS = dict(PC=0, AC=1, IR=2, MAR=3, MDR=4, InpR=5, OutR=6, IN=7)
DC = dict(OutR=1, InpR=2, MDR=3, MAR=4, IR=5, AC=6, PC=7)
# Коды АЛУ: F M S2 S1 S0 C0 (табл. 3.1)
ALU = dict(A=0b000000, INC=0b000001, ADD=0b000010, SUB=0b000101, DEC=0b000110,
           OR=0b001000, XOR=0b001010, AND=0b001100, NOT=0b001110)
C0_, C1_, C2_, C3_ = 0, 1, 2, 3


def word(msa=0, msb=0, alu=0, dc=None, msm=0, wr=0, fr=0):
    """Микрокоманда (20 бит). dc=None — запись в регистры запрещена (E=0)."""
    e, x = (0, 0) if dc is None else (1, DC[dc])
    return (MS.get(msa, msa) << 17) | (MS.get(msb, msb) << 14) | (alu << 8) | (e << 7) | (x << 4) | \
        (msm << 3) | (wr << 2) | fr


def microprogram():
    fetch = [word("PC", 0, ALU["A"], "MAR", fr=C0_),       # C0t0 MAR ← PC
             word(0, 0, 0, "MDR", msm=1, fr=C0_),          # C0t1 MDR ← M[MAR]
             word("MDR", 0, ALU["A"], "IR", fr=C0_),       # C0t2 IR ← MDR
             word("PC", 0, ALU["INC"], "PC", fr=C2_)]      # C0t3 PC ← PC+1; F,R ← 1,0 (сразу в C2)
    nop = word(fr=C2_)
    end = word(fr=C0_)                                    # C2t3 F,R ← 0,0
    rd = [word("IR", 0, ALU["A"], "MAR", fr=C2_), word(0, 0, 0, "MDR", msm=1, fr=C2_)]
    ex = {
        0: rd + [word("MDR", 0, ALU["A"], "AC", fr=C2_), end],          # LDA  AC ← M[AD]
        1: [nop, nop, nop, end],                                        # STA  (память — ПЗУ)
        2: rd + [word("AC", "MDR", ALU["ADD"], "AC", fr=C2_), end],     # ADD
        3: rd + [word("AC", "MDR", ALU["SUB"], "AC", fr=C2_), end],     # SUB
        4: rd + [word("AC", "MDR", ALU["AND"], "AC", fr=C2_), end],     # AND
        5: rd + [word("AC", "MDR", ALU["OR"], "AC", fr=C2_), end],      # OR
        6: rd + [word("AC", "MDR", ALU["XOR"], "AC", fr=C2_), end],     # XOR
        7: rd + [word("MDR", 0, ALU["NOT"], "AC", fr=C2_), end],        # COM  AC ← ¬M[AD]
        8: rd + [word("MDR", 0, ALU["NOT"], "AC", fr=C2_),              # NEG  AC ← ¬M[AD] + 1
                 word("AC", 0, ALU["INC"], "AC", fr=C0_)],
        9: rd + [word("MDR", 0, ALU["INC"], "AC", fr=C2_), end],        # INC  AC ← M[AD] + 1
        10: rd + [word("MDR", 0, ALU["DEC"], "AC", fr=C2_), end],       # DEC  AC ← M[AD] − 1
        11: [word("IR", 0, ALU["A"], "PC", fr=C2_), nop, nop, end],     # JMP  PC ← AD
        12: [word("AC", "AC", ALU["XOR"], "AC", fr=C2_), nop, nop, end],  # CLEA AC ← 0
        13: [word("AC", 0, ALU["INC"], "AC", fr=C2_), nop, nop, end],   # INCA AC ← AC + 1
        14: [word("InpR", 0, ALU["A"], "AC", fr=C2_), nop, nop, end],   # INP  AC ← INPR
        15: [word("AC", 0, ALU["A"], "OutR", fr=C2_), nop, nop, end],   # OUT  OUTR ← AC
    }
    rom = {}
    for q in range(16):
        for t in range(4):
            rom[(q << 4) | (C0_ << 2) | t] = fetch[t]
            rom[(q << 4) | (C2_ << 2) | t] = ex[q][t]
            rom[(q << 4) | (C1_ << 2) | t] = word(fr=C2_ if t == 3 else C1_)  # C1 не используется
            rom[(q << 4) | (C3_ << 2) | t] = word(fr=C0_ if t == 3 else C3_)
    return rom


# Программа варианта 14: по адресу EBC — INCA (КОП 1101) с адресом FFF, по FFF — операнд FFFD.
# После INCA по адресу EBD стоит JMP EBD — «останов» (зацикливание на месте).
MEMORY = {0xEBC: 0xDFFF, 0xEBD: 0xBEBD, 0xFFF: 0xFFFD}


def make_cu(alu):
    c = Circuit("VM")
    c.text((330, 30), "Устройство управления (рис. 4.1)")
    c.add("wiring", "Clock", (140, 110), {0: "GEN"}, label="Генератор")
    c.pin_in((140, 170), "SE")
    c.add("gates", "AND Gate", (320, 140), {0: "CLK", 1: ("GEN", "west", 40), 2: ("SE", "west", 40)},
          size=30, inputs=2)
    c.text((300, 100), "схема совпадения")
    c.add("memory", "Counter", (220, 260), {0: ("T", "east", 30), 2: ("CLK", "south", 20)},
          width=2, max="0x3", label="Счётчик тактов")
    # Триггеры циклов F и R (D-триггеры), код цикла FR = F·R
    c.add("memory", "D Flip-Flop", (420, 200), {0: ("FN", "west", 30), 1: ("CLK", "west", 80), 2: ("Fq", "east", 20)},
          label="F")
    c.add("memory", "D Flip-Flop", (420, 290), {0: ("RN", "west", 30), 1: ("CLK", "west", 80), 2: ("Rq", "east", 20)},
          label="R")
    splitter(c, (500, 250), 2, [0, 1], ["FR", "Rq", "Fq"])
    # Дешифраторы тактов, циклов и команд
    c.add("plexers", "Decoder", (120, 400), {**{k: (f"t{k}", "east", 20 if k % 2 == 0 else 60) for k in range(4)},
                                             4: ("T", "south", 30)}, select=2, enable="false", label="DC t")
    c.add("plexers", "Decoder", (320, 400), {**{k: (f"cyc{k}", "east", 20 if k % 2 == 0 else 60) for k in range(4)},
                                             4: ("FR", "south", 30)}, select=2, enable="false", label="DC C")
    splitter(c, (520, 330), 16, [0] * 12 + [1] * 4, ["IR", None, "OP"])
    c.add("plexers", "Decoder", (560, 520), {**{k: (f"q{k}", "east", 20 if k % 2 == 0 else 60) for k in range(16)},
                                             16: ("OP", "south", 30)}, select=4, enable="false", label="DC КОП")
    for k in range(4):
        c.add("io", "LED", (60 + 50 * k, 520), {0: (f"t{k}", "north", 20)}, label=f"t{k}", labelloc="south")
        c.add("io", "LED", (260 + 50 * k, 520), {0: (f"cyc{k}", "north", 20)}, label=f"C{k}", labelloc="south")
    for k in range(16):
        c.add("io", "LED", (60 + 40 * (k % 8), 620 + 70 * (k // 8)), {0: (f"q{k}", "north", 20)},
              label=f"q{k}", labelloc="south")
    # ПЗУ микрокоманд: адрес = КОП · F R · t
    splitter(c, (140, 800), 8, [0, 0, 1, 1, 2, 2, 2, 2], ["UADDR", "T", "FR", "OP"])
    c.add("memory", "ROM", (460, 860), {0: ("CW", "east", 30), 1: ("UADDR", "west", 30)},
          addrWidth=8, dataWidth=20, contents=rom_text(8, 20, microprogram()), label="ПЗУ микрокоманд")
    c.pin_out((300, 980), "Управляющее слово", net="CW", width=20, facing="north", labelloc="south")
    # Поля управляющего слова: MSA MSB F M S2 S1 S0 C0 E DC MSM WR FR (старшие биты — слева)
    fields = [("RN", 1), ("FN", 1), ("WR", 1), ("MSM", 1), ("DC", 3), ("E", 1), ("C0", 1), ("S0", 1), ("S1", 1),
              ("S2", 1), ("M", 1), ("F", 1), ("MSB", 3), ("MSA", 3)]
    mapping, order = [], [f for f, _ in reversed(fields)]
    for name, w in fields:
        mapping += [order.index(name)] * w
    splitter(c, (560, 1000), 20, mapping, ["CW"] + order)
    return c


if __name__ == "__main__":
    alu = make_alu()
    vm = make_cu(alu)
    make_ou(alu, c=vm, dx=700, pins=False, rom=MEMORY,
            title="Операционное устройство (рис. 3.4) с памятью программы варианта 14")
    build([vm, alu], OUT, main="VM")
    print("wrote", OUT)
