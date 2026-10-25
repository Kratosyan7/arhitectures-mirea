"""Скриншоты GUI Logisim для пр.1 (по SCREENSHOTS.md)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "pr01.circ"), zoom=2.0) as L:
    p = Panel(L, dict(A=((60, 120), 1), B=((60, 310), 1)))
    p.set(A=1, B=1)
    L.shot(os.path.join(IMG, "logisim_nand_11.png"))
    p.set(A=0)
    L.shot(os.path.join(IMG, "logisim_nand_01.png"))
    L.set_zoom(1.5)
    for row, name in ((1, "F_sdnf"), (2, "F_mknf")):
        L.open_circuit(row)
        q = Panel(L, {k: (loc, 1, "south") for k, loc in
                      dict(a=(100, 40), b=(170, 40), c=(240, 40), d=(310, 40)).items()})
        q.set(a=1, c=1)
        L.shot(os.path.join(IMG, f"logisim_{name}.png"))
