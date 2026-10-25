"""Скриншоты GUI Logisim для пр.11 (по SCREENSHOTS.md)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
import xshot  # noqa: E402
from gui import Logisim  # noqa: E402

IMG = os.path.join(HERE, "../../img")


def reset():
    xshot.key("ctrl+r")


with Logisim(os.path.join(HERE, "pr11.circ"), zoom=1.5) as L:
    L.open_circuit(1)                      # seq
    reset(); L.tick(32)
    L.shot(os.path.join(IMG, "logisim_seq.png"))
    L.set_zoom(1.0)
    L.open_circuit(2)                      # par
    reset(); L.tick(8)
    L.shot(os.path.join(IMG, "logisim_par_t4.png"))
    L.tick(2)
    L.shot(os.path.join(IMG, "logisim_par.png"))
    L.set_zoom(1.5)
    L.open_circuit(0)                      # main
    reset(); L.tick(10)
    L.shot(os.path.join(IMG, "logisim_main.png"))
    reset(); L.tick(32)
    L.shot(os.path.join(IMG, "logisim_main_end.png"))
