"""Скриншоты GUI Logisim для пр.9 (по SCREENSHOTS.md)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "toupper.circ"), zoom=1.5) as L:
    p = Panel(L, dict(c=((100, 290), 8)))
    for val, name in ((0x6D, "m"), (0x7B, "brace"), (0xD0, "cyr")):
        p.set(c=val)
        L.shot(os.path.join(IMG, f"logisim_toupper_{name}.png"))
