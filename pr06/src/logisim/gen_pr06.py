"""Модель теста FIO «случайное чтение блоков 512 Б» (вариант 14) для Logisim 2.7.1: pr06_fio.circ.

Схема «randread» — генератор нагрузки: на каждый такт генератор псевдослучайных чисел
выдаёт номер сектора (LBA) в файле 1 ГиБ (2²¹ секторов по 512 Б), смещение в байтах
= LBA · 512, счётчик считает выданные запросы.
Схема «metrics» — расчёт показателей по закону Литтла: IOPS = QD / latency,
BW = IOPS · BS (байт/с и КиБ/с) — сверка с результатами fio.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from lgen import Circuit, build  # noqa: E402

OUT = os.path.join(HERE, "pr06_fio.circ")


def ext(c, loc, src, dst, win, wout):
    return c.add("wiring", "Bit Extender", loc, {0: (dst, "east", 30), 1: (src, "west", 30)},
                 in_width=win, out_width=wout, type="zero")


def make_metrics():
    c = Circuit("metrics")
    c.text((520, 30), "Закон Литтла: IOPS = QD / latency, BW = IOPS · BS")
    c.pin_in((240, 120), "QD (iodepth)", net="QD8", width=8)
    c.pin_in((240, 200), "latency, мкс", net="LAT16", width=16)
    c.pin_in((240, 300), "BS, байт", net="BS16", width=16)
    ext(c, (440, 120), "QD8", "QD", 8, 32)
    ext(c, (440, 200), "LAT16", "LAT", 16, 32)
    ext(c, (440, 300), "BS16", "BS", 16, 32)
    c.const((660, 560), 1_000_000, "MLN", width=32)
    c.const((660, 620), 0, "Z32", width=32)
    c.const((660, 680), 10, "SH10", width=5)
    c.add("arith", "Multiplier", (640, 160), {0: "QD", 1: "MLN", 2: ("QDM", "east", 30)}, width=32)
    c.add("arith", "Divider", (720, 200), {0: "QDM", 1: "LAT", 2: ("IOPS", "east", 30),
                                            3: ("Z32", "north", 20)}, width=32)
    c.add("arith", "Multiplier", (720, 340), {0: "IOPS", 1: "BS", 2: ("BWB", "east", 30)}, width=32)
    c.add("arith", "Shifter", (720, 460), {0: "BWB", 1: "SH10", 2: ("BWK", "east", 30)}, width=32, shift="lr")
    c.pin_out((1000, 200), "IOPS", net="IOPS", width=32)
    c.pin_out((1000, 340), "BW, байт/с", net="BWB", width=32)
    c.pin_out((1000, 460), "BW, КиБ/с", net="BWK", width=32)
    for (x, y), net in [((300, 420), "QD"), ((300, 490), "LAT"), ((300, 560), "BS"), ((1200, 250), "IOPS"),
                        ((1200, 390), "BWB"), ((1200, 510), "BWK")]:
        c.add("wiring", "Probe", (x, y), {0: (net, "west", 20)}, radix="10unsigned", facing="west")
    return c


def make_randread():
    c = Circuit("randread")
    c.text((420, 30), "Генератор случайного чтения: --rw=randread --bs=512 --size=1G")
    c.add("wiring", "Clock", (80, 120), {0: "CLK"}, label="такт = 1 запрос")
    c.add("memory", "Random", (300, 140), {0: ("LBA", "east", 30), 1: ("CLK", "west", 40)},
          width=21, seed=14, label="ГПСЧ")
    c.add("memory", "Counter", (300, 300), {0: ("CNT", "east", 30), 2: ("CLK", "south", 20)},
          width=16, max="0xffff", label="Запросов выдано")
    ext(c, (480, 140), "LBA", "LBA32", 21, 32)
    c.const((480, 220), 9, "SH9", width=5)
    c.add("arith", "Shifter", (680, 160), {0: "LBA32", 1: "SH9", 2: ("OFS", "east", 30)}, width=32, shift="ll")
    c.pin_out((900, 140), "LBA (сектор)", net="LBA", width=21)
    c.pin_out((900, 220), "смещение, байт", net="OFS", width=32)
    c.pin_out((900, 320), "запросов", net="CNT", width=16)
    for (x, y), net in [((1180, 160), "LBA"), ((1180, 240), "OFS"), ((1180, 340), "CNT")]:
        c.add("wiring", "Probe", (x, y), {0: (net, "west", 20)}, radix="10unsigned", facing="west")
    return c


if __name__ == "__main__":
    build([make_metrics(), make_randread()], OUT, main="metrics")
    print("wrote", OUT)
