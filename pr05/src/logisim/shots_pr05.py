"""Скриншоты GUI Logisim для пр.5: трансляция VA через TLB (вариант 14)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "pr05_tlb.circ")) as L:
    p = Panel(L, dict(VA=((200, 120), 20)))
    p.set(VA=0x0B345)          # адрес варианта: VPN = 5 → в TLB нет → Page Fault
    L.shot(os.path.join(IMG, "logisim_tlb_fault.png"))
    p.set(VA=0x17345)          # для сравнения: адрес из страницы VPN = 11 → попадание
    L.shot(os.path.join(IMG, "logisim_tlb_hit.png"))
