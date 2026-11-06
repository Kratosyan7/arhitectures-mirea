"""Скриншоты GUI Logisim для пр.10 (аппаратная замена пробела на '_', с ветвлением и без)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "pr10_replspace.circ"), zoom=1.0) as L:
    p = Panel(L, dict(c=((80, 120), 8)))
    p.set(c=ord(" "))                               # пробел (0x20) → '_' (0x5F)
    L.shot(os.path.join(IMG, "logisim_branch_space.png"))
    p.set(c=ord("L"))                               # 'L' (0x4C) — не пробел, без изменений
    L.shot(os.path.join(IMG, "logisim_branch_L.png"))
    L.open_circuit(1)                               # repl_nobranch
    q = Panel(L, dict(c=((80, 120), 8)))
    q.set(c=ord(" "))
    L.shot(os.path.join(IMG, "logisim_nobranch_space.png"))
