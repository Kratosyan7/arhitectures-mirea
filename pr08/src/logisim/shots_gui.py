"""Скриншоты GUI Logisim для пр.8 (по SCREENSHOTS.md)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "riscv_decoder.circ")) as L:
    p = Panel(L, dict(sel=((560, 320), 3, "north"), rs1=((760, 900), 32)))
    p.set(sel=0)
    L.shot(os.path.join(IMG, "logisim_decoder_li.png"))
    p.set(sel=2, rs1=0x000110EC)
    L.shot(os.path.join(IMG, "logisim_decoder_addi.png"))
    p.set(sel=6, rs1=0)
    L.shot(os.path.join(IMG, "logisim_decoder_j.png"))
