"""Скриншоты GUI Logisim для пр.7: вложенное прерывание (Клавиатура, затем HDD) — вариант 14."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
PINS = {f"IRQ{k}": ((240, 110 + 50 * k), 1) for k in range(4)}
PINS.update(PC=((240, 340), 16), IRET=((240, 430), 1), CLK=((240, 480), 1))
with Logisim(os.path.join(HERE, "pr07_pic.circ"), zoom=0.75) as L:
    p = Panel(L, PINS)
    p.set(PC=0x3144, IRQ2=1)          # команда 0x3144 основной программы, запрос клавиатуры
    L.shot(os.path.join(IMG, "logisim_pic_1_irq2.png"))
    p.pulse("CLK")                    # вход в ПОП клавиатуры
    L.shot(os.path.join(IMG, "logisim_pic_2_isr_kbd.png"))
    p.set(IRQ2=0, PC=0x0137, IRQ3=1)  # в ПОП клавиатуры: запрос плоттера (ниже приоритет) не принимается
    L.shot(os.path.join(IMG, "logisim_pic_3_irq3_blocked.png"))
    p.set(IRQ3=0, IRQ0=1)             # команда 0x0137 ПОП клавиатуры, запрос HDD (выше приоритет)
    L.shot(os.path.join(IMG, "logisim_pic_4_irq0.png"))
    p.pulse("CLK")                    # вход в ПОП HDD, в стеке 0x3145 и 0x0138
    L.shot(os.path.join(IMG, "logisim_pic_5_isr_hdd.png"))
    p.set(IRQ0=0, IRET=1)
    p.pulse("CLK")                    # возврат из ПОП HDD → 0x0138
    L.shot(os.path.join(IMG, "logisim_pic_6_ret_hdd.png"))
    p.pulse("CLK")                    # возврат из ПОП клавиатуры → 0x3145
    L.shot(os.path.join(IMG, "logisim_pic_7_ret_main.png"))
