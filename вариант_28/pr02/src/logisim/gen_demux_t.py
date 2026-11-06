"""ПР2 (вариант 28): демультиплексор с 2 адресными входами (1→4) и T-триггер.

demux.circ — демультиплексор 1→4 (Logisim Demultiplexer, select=2): один вход D
             по 2-разрядному адресу A1A0 направляется на один из выходов Y0..Y3.
t.circ     — T-триггер (Logisim T Flip-Flop): при T=0 хранит состояние, при T=1 по
             фронту синхросигнала переключается (счётный режим).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from lgen import Circuit, build  # noqa: E402


def demux_1_4():
    c = Circuit("demux_1_4")
    c.text((240, 10), "Демультиплексор 1→4: вход D по адресу A1A0 попадает на выход Y<номер>")
    c.pin_in((60, 200), "D", net="D")                  # информационный вход
    # 2 адресных входа -> разветвитель -> 2-разрядная шина адреса (вход выбора)
    for i in range(2):
        c.pin_in((160, 360 + 40 * i), f"A{i}", net=f"A{i}")
    c.add("wiring", "Splitter", (300, 380), {0: "SEL", 1: "A0", 2: "A1"},
          facing="north", fanout=2, incoming=2, appear="right")
    # Demultiplexer: 4 выхода Y0..Y3, порт 4 — 2-битный выбор (SEL), порт 5 — вход данных D
    conns = {4: ("SEL", "south", 20), 5: "D"}
    for k in range(4):
        conns[k] = f"Y{k}"
    c.add("plexers", "Demultiplexer", (340, 200), conns, select=2, facing="east", enable="false")
    for k in range(4):
        c.pin_out((620, 120 + 60 * k), f"Y{k}", net=f"Y{k}")
        c.add("io", "LED", (680, 120 + 60 * k), {0: (f"Y{k}", "west", 20)}, label=f"Y{k}")
    return c


def t_trigger():
    c = Circuit("t_trigger")
    c.text((240, 10), "T-триггер: T — счётный вход, CLK — синхросигнал, Q/¬Q — выходы")
    c.pin_in((60, 150), "T", net="T")
    c.add("wiring", "Clock", (60, 210), {0: "CLK"}, facing="east", label="CLK")
    # T Flip-Flop: 0=T, 1=Clock, 2=Q, 3=¬Q
    c.add("memory", "T Flip-Flop", (300, 180),
          {0: ("T", "west", 30), 1: ("CLK", "west", 30),
           2: ("Q", "east", 30), 3: ("NQ", "east", 30)})
    c.pin_out((460, 160), "Q", net="Q")
    c.pin_out((460, 210), "nQ", net="NQ")
    c.add("io", "LED", (520, 160), {0: ("Q", "west", 20)}, label="Q")
    return c


if __name__ == "__main__":
    build([demux_1_4()], os.path.join(HERE, "demux.circ"), main="demux_1_4")
    build([t_trigger()], os.path.join(HERE, "t.circ"), main="t_trigger")
    print("demux.circ, t.circ ok")
