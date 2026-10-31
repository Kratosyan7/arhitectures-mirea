"""ПР2 (вариант 23): мультиплексор с 4 адресными входами (16→1) и T-триггер.

mux.circ — мультиплексор 16→1 (Logisim Multiplexer, select=4): 4-разрядный адрес
           A3A2A1A0 выбирает один из 16 информационных входов D0..D15 на выход Y.
t.circ   — T-триггер (Logisim T Flip-Flop): при T=0 хранит состояние, при T=1 по
           фронту синхросигнала переключается (счётный режим).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from lgen import Circuit, build  # noqa: E402


def mux_16_1():
    c = Circuit("mux_16_1")
    c.text((300, 10), "Мультиплексор 16→1: адрес A3A2A1A0 выбирает вход D<номер> на выход Y")
    # 16 информационных входов D0..D15
    for k in range(16):
        c.pin_in((60, 60 + 34 * k), f"D{k}", net=f"D{k}")
    # 4 адресных входа -> разветвитель -> 4-разрядная шина адреса (вход выбора)
    for i in range(4):
        c.pin_in((360, 640 + 40 * i), f"A{i}", net=f"A{i}")
    c.add("wiring", "Splitter", (520, 670), {0: "ADDR", 1: "A0", 2: "A1", 3: "A2", 4: "A3"},
          facing="north", fanout=4, incoming=4, appear="right")
    # Multiplexer: порты 0..15 — входы, 16 — выбор (ADDR), 17 — выход Y
    conns = {16: ("ADDR", "south", 20), 17: "Y"}
    for k in range(16):
        conns[k] = f"D{k}"
    c.add("plexers", "Multiplexer", (560, 360), conns, select=4, facing="east", enable="false")
    c.pin_out((760, 360), "Y", net="Y")
    c.add("io", "LED", (820, 360), {0: ("Y", "west", 20)}, label="Y")
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
    build([mux_16_1()], os.path.join(HERE, "mux.circ"), main="mux_16_1")
    build([t_trigger()], os.path.join(HERE, "t.circ"), main="t_trigger")
    print("mux.circ, t.circ ok")
