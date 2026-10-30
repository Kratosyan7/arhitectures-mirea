"""ПР2 (вариант 21): дешифратор с 4 входными сигналами (4→16) и JK-триггер.

decoder.circ — дешифратор 4→16 (Logisim Decoder, select=4): 4-разрядный адрес
               A3A2A1A0 активирует один из 16 выходов Y0..Y15 (при EN=1).
jk.circ      — JK-триггер (Logisim J-K Flip-Flop): режимы хранения/сброса/
               установки/счёта по входам J, K и синхросигналу.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from lgen import Circuit, build  # noqa: E402


def decoder_4_16():
    c = Circuit("decoder_4_16")
    c.text((240, 10), "Дешифратор 4→16: адрес A3A2A1A0 активирует выход Y<номер> (EN=1)")
    # 4 отдельных входных сигнала -> разветвитель -> 4-разрядная шина адреса
    for i in range(4):
        c.pin_in((60, 80 + 40 * i), f"A{i}", net=f"A{i}")
    c.add("wiring", "Splitter", (240, 110), {0: "ADDR", 1: "A0", 2: "A1", 3: "A2", 4: "A3"},
          facing="east", fanout=4, incoming=4, appear="right")
    c.const((140, 300), 1, "EN")                       # разрешение дешифратора
    # Decoder: порт 16 — 4-разрядный выбор (ADDR), порт 17 — разрешение (EN), 0..15 — выходы
    conns = {16: ("ADDR", "west", 20), 17: ("EN", "south", 20)}
    for k in range(16):
        conns[k] = f"Y{k}"
    c.add("plexers", "Decoder", (360, 360), conns, select=4, facing="north")
    for k in range(16):
        c.pin_out((760, 60 + 34 * k), f"Y{k}", net=f"Y{k}")
    return c


def jk_trigger():
    c = Circuit("jk_trigger")
    c.text((240, 10), "JK-триггер: J,K — входы, CLK — синхросигнал, Q/¬Q — выходы")
    c.pin_in((60, 120), "J", net="J")
    c.pin_in((60, 220), "K", net="K")
    c.add("wiring", "Clock", (60, 170), {0: "CLK"}, facing="east", label="CLK")
    # J-K Flip-Flop: 0=J, 1=K, 2=Clock, 3=Q, 4=¬Q
    c.add("memory", "J-K Flip-Flop", (300, 170),
          {0: ("J", "west", 40), 1: ("K", "west", 40), 2: ("CLK", "west", 20),
           3: ("Q", "east", 40), 4: ("NQ", "east", 40)})
    c.pin_out((460, 150), "Q", net="Q")
    c.pin_out((460, 210), "nQ", net="NQ")
    c.add("io", "LED", (520, 150), {0: ("Q", "west", 20)}, label="Q")
    return c


if __name__ == "__main__":
    build([decoder_4_16()], os.path.join(HERE, "decoder.circ"), main="decoder_4_16")
    build([jk_trigger()], os.path.join(HERE, "jk.circ"), main="jk_trigger")
    print("decoder.circ, jk.circ ok")
