"""Скриншоты GUI Logisim для пр.7: вложенное прерывание (Сканер, затем SSD) — вариант 28."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
PINS = {f"IRQ{k}": ((240, 110 + 50 * k), 1) for k in range(4)}
PINS.update(PC=((240, 340), 16), IRET=((240, 430), 1), CLK=((240, 480), 1))
with Logisim(os.path.join(HERE, "pr07_pic.circ"), zoom=0.75) as L:
    p = Panel(L, PINS)
    p.set(PC=0x3C93, IRQ3=1)          # команда 0x3C93 основной программы, запрос Сканера
    L.shot(os.path.join(IMG, "logisim_pic_1_irq3.png"))
    p.pulse("CLK")                    # вход в ПОП Сканера
    L.shot(os.path.join(IMG, "logisim_pic_2_isr_scan.png"))
    p.set(IRQ3=0, PC=0x01BC, IRQ0=1)  # команда 0x01BC ПОП Сканера, запрос SSD (выше приоритет)
    L.shot(os.path.join(IMG, "logisim_pic_3_irq0.png"))
    p.pulse("CLK")                    # вход в ПОП SSD, в стеке 0x3C94 и 0x01BD
    L.shot(os.path.join(IMG, "logisim_pic_4_isr_ssd.png"))
    p.set(IRQ0=0, IRQ2=1)             # в ПОП SSD: запрос Клавиатуры (ниже приоритет) не принимается
    L.shot(os.path.join(IMG, "logisim_pic_5_blocked.png"))
    p.set(IRQ2=0, IRET=1)
    p.pulse("CLK")                    # возврат из ПОП SSD → 0x01BD (ПОП Сканера)
    L.shot(os.path.join(IMG, "logisim_pic_6_ret_ssd.png"))
    p.pulse("CLK")                    # возврат из ПОП Сканера → 0x3C94 (основная программа)
    L.shot(os.path.join(IMG, "logisim_pic_7_ret_main.png"))
