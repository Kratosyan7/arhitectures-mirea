"""Генератор схемы toupper.circ (Logisim 2.7.1) для практики 9.

Аппаратный аналог функции mytoupper (листинг 9.8) для одного байта:
  is_lower = NOT((c < 'a') OR (c > 'z'))   – два компаратора и элемент ИЛИ-НЕ;
  out = is_lower ? c - 0x20 : c             – вычитатель и мультиплексор 2:1.
Компараторы работают в дополнительном коде (знаковое сравнение), как
инструкции blt/bgt после lb, которая знаково расширяет байт.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from circlib import Circuit, save

c = Circuit("toupper")
c.text((400, 40), "Аппаратный аналог mytoupper: перевод символа в верхний регистр", 16, bold=True)
c.text((400, 65), "Практическая работа 9, вариант 14 (Мирзоян А.О., ИКБО-41-25)", 12)

# вход: 8-битный символ
c.pin_in((100, 290), 8, "c", labelloc="north")
c.wire((100, 290), (160, 290))
BX = 160
c.wire((BX, 120), (BX, 400))
c.wire((BX, 120), (200, 120))
c.probe((200, 120), "16", label="c (hex)", labelloc="east")

# c < 'a'
c.wire((BX, 160), (260, 160))
c.const((240, 180), 8, ord("a")); c.wire((240, 180), (260, 180))
c.comparator((300, 170), 8, mode="twosComplement")
c.text((205, 200), "'a' = 0x61", 11)
# c > 'z'
c.wire((BX, 240), (260, 240))
c.const((240, 260), 8, ord("z")); c.wire((240, 260), (260, 260))
c.comparator((300, 250), 8, mode="twosComplement")
c.text((205, 280), "'z' = 0x7A", 11)
# ИЛИ-НЕ: is_lower = !(c < 'a' | c > 'z')
c.wire((300, 180), (330, 180), (330, 190), (370, 190))
c.wire((300, 240), (330, 240), (330, 230), (370, 230))
c.text((350, 175), "c<'a'", 10)
c.text((350, 255), "c>'z'", 10)
c.gate("NOR Gate", (430, 210))
c.wire((430, 210), (540, 210), (640, 210))
c.pin_out((640, 210), 1, "is_lower")
c.text((700, 235), "1 – строчная латинская буква", 11, halign="left")

# путь «как есть» и вычитание 0x20
c.wire((BX, 320), (530, 320))
c.wire((BX, 390), (260, 390))
c.const((240, 410), 8, 0x20); c.wire((240, 410), (260, 410))
c.subtractor((300, 400), 8)
c.text((205, 430), "0x20 = 'a' − 'A'", 11)
c.wire((300, 400), (480, 400), (480, 340), (530, 340))
c.text((420, 415), "c − 0x20", 11)
c.text((420, 305), "c (без изменений)", 11)

# мультиплексор 2:1, управляющий вход сверху
c.add("plexers", "Multiplexer", (560, 330), facing="east", select=1, width=8, selloc="tr")
c.wire((540, 210), (540, 310))
c.text((610, 365), "0: c,  1: c − 0x20", 11, halign="left")
c.wire((560, 330), (640, 330))
c.pin_out((640, 330), 8, "out")
c.wire((600, 330), (600, 400))
c.probe((600, 400), "16", label="out (hex)", labelloc="east")

c.text((400, 480), "Сравнение знаковое (как lb + blt/bgt в листинге 9.8): байты UTF-8 кириллицы", 11)
c.text((400, 498), "(0xD0, 0xD1, 0x80..0xBF) отрицательны, меньше 'a' и проходят без изменений", 11)

save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "toupper.circ"), [c])
print("toupper.circ written")
