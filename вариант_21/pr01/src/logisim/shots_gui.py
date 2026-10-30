"""Скриншоты GUI Logisim для ПР1 (вариант 21): XOR на транзисторах, схемы по СКНФ и МДНФ."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "pr01.circ"), zoom=1.0) as L:
    p = Panel(L, dict(A=((40, 120), 1), B=((40, 170), 1)))
    p.set(A=1)                                   # A=1, B=0 -> XOR=1
    L.shot(os.path.join(IMG, "logisim_xor_10.png"))
    p.set(B=1)                                   # A=1, B=1 -> XOR=0
    L.shot(os.path.join(IMG, "logisim_xor_11.png"))
    SD = {k: (loc, 1, "south") for k, loc in
          dict(a=(100, 40), b=(170, 40), c=(240, 40), d=(310, 40)).items()}
    L.open_circuit(1)                            # F_sknf
    q = Panel(L, SD)
    q.set(a=1, c=1)                              # набор 1010 (#10) -> F=1
    L.shot(os.path.join(IMG, "logisim_F_sknf.png"))
    L.open_circuit(2)                            # F_mdnf
    q = Panel(L, SD)
    q.set(a=1, c=1)
    L.shot(os.path.join(IMG, "logisim_F_mdnf.png"))
