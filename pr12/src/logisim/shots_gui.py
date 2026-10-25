"""Скриншоты GUI Logisim для пр.12 (по SCREENSHOTS.md)."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
import xshot  # noqa: E402
from gui import Logisim  # noqa: E402

IMG = os.path.join(HERE, "../../img")
LANE0 = (640, 80)   # loc экземпляра lane0 в схеме simt4
CLICK = (LANE0[0] + int(os.environ.get("DX", "20")), LANE0[1] + int(os.environ.get("DY", "40")))

with Logisim(os.path.join(HERE, "pr12.circ")) as L:
    L.tick(41)
    L.shot(os.path.join(IMG, "logisim_simt4.png"))
    xshot.key("ctrl+r"); L.tick(65)
    L.shot(os.path.join(IMG, "logisim_simt4_final.png"))
    xshot.key("ctrl+r"); L.tick(3)
    sx, sy = L.to_screen(*CLICK)
    xshot.click(round(sx), round(sy), button=3)
    time.sleep(0.8)
    xshot.click(round(sx) + 59, round(sy) + 50)   # пункт меню «View julia_lane»
    time.sleep(1.0)
    L.shot(os.path.join(IMG, "logisim_lane.png"))
