"""Модель трансляции виртуального адреса через TLB (вариант 14) для Logisim 2.7.1: pr05_tlb.circ.

Страница 8 КБ → смещение 13 бит; виртуальный адрес 20 бит (VPN — 7 бит).
TLB на 4 записи (V, VPN, PFN) задан константами: запись 0 — VPN = 11 → PFN = 25 (вариант 14),
остальные записи недействительны (V = 0). Физический адрес = PFN · 2¹³ + Offset.
Выходы: HIT, Page Fault, номер сработавшей записи, физический адрес (21 бит).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
sys.path.insert(0, os.path.join(HERE, "../../../pr03/src/logisim"))
from lgen import Circuit, build  # noqa: E402
from gen_pr03 import splitter  # noqa: E402

OUT = os.path.join(HERE, "pr05_tlb.circ")
OFFSET_BITS, VA_BITS, PFN_BITS = 13, 20, 8
TLB = [(1, 11, 25), (0, 0, 0), (0, 0, 0), (0, 0, 0)]  # (V, VPN, PFN)


def make():
    c = Circuit("TLB")
    c.text((560, 30), "Трансляция адреса через TLB: VPN = 11 → PFN = 25, страница 8 КБ (вариант 14)")
    c.pin_in((200, 120), "VA", width=VA_BITS)
    c.text((200, 70), "Виртуальный адрес (20 бит)")
    splitter(c, (340, 120), VA_BITS, [0] * OFFSET_BITS + [1] * (VA_BITS - OFFSET_BITS), ["VA", "OFFSET", "VPN"])
    c.text((520, 170), "TLB (V, VPN, PFN)")
    for i, (v, vpn, pfn) in enumerate(TLB):
        y = 230 + 110 * i
        c.const((400, y), v, f"V{i}")
        c.const((400, y + 30), vpn, f"TVPN{i}", width=VA_BITS - OFFSET_BITS)
        c.const((400, y + 60), pfn, f"PFN{i}", width=PFN_BITS)
        c.add("arith", "Comparator", (620, y + 20), {0: "VPN", 1: f"TVPN{i}", 3: (f"EQ{i}", "east", 20)},
              width=VA_BITS - OFFSET_BITS, mode="unsigned")
        c.add("gates", "AND Gate", (840, y + 30), {0: f"H{i}", 1: (f"EQ{i}", "west", 30), 2: (f"V{i}", "west", 30)},
              size=30, inputs=2)
    c.add("plexers", "Priority Encoder", (960, 300), {0: ("H0", "west", 20), 1: ("H1", "west", 70),
                                                      2: ("H2", "west", 20), 3: ("H3", "west", 70),
                                                      4: ("IDX", "east", 30), 7: ("HIT", "east", 60)},
          select=2, disabled="0", label="шифратор")
    c.add("plexers", "Multiplexer", (1080, 520), {0: ("PFN0", "west", 20), 1: ("PFN1", "west", 70),
                                                  2: ("PFN2", "west", 20), 3: ("PFN3", "west", 70),
                                                  4: ("IDX", "south", 20), 5: ("PFN", "east", 30)},
          select=2, width=PFN_BITS, enable="false")
    splitter(c, (1240, 620), OFFSET_BITS + PFN_BITS, [0] * OFFSET_BITS + [1] * PFN_BITS, ["PA", "OFFSET", "PFN"])
    c.add("gates", "NOT Gate", (1120, 360), {0: ("PF", "east", 20), 1: "HIT"}, size=30)
    c.pin_out((1400, 200), "HIT", net="HIT")
    c.pin_out((1400, 260), "Page Fault", net="PF")
    c.add("io", "LED", (1300, 320), {0: ("PF", "west", 20)}, label="Page Fault", labelloc="east", color="#f01010")
    c.pin_out((1400, 420), "VPN", net="VPN", width=VA_BITS - OFFSET_BITS)
    c.pin_out((1400, 480), "Offset", net="OFFSET", width=OFFSET_BITS)
    c.pin_out((1400, 540), "PFN", net="PFN", width=PFN_BITS)
    c.pin_out((1400, 760), "PA", net="PA", width=OFFSET_BITS + PFN_BITS)
    c.text((1430, 720), "Физический адрес (21 бит)")
    for (x, y), net, txt in [((300, 220), "VA", "VA (hex)"), ((1560, 840), "PA", "PA (hex)"),
                             ((1560, 540), "PFN", "PFN (dec)"), ((1560, 420), "VPN", "VPN (dec)")]:
        c.add("wiring", "Probe", (x, y), {0: (net, "west", 20)}, radix="16" if "hex" in txt else "10unsigned",
              facing="west", label=txt, labelloc="north")
    return c


if __name__ == "__main__":
    build([make()], OUT)
    print("wrote", OUT)
