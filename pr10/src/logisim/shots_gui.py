"""Скриншоты GUI Logisim для пр.10 (аппаратный tolower, с ветвлением и без)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "pr10_tolower.circ"), zoom=1.0) as L:
    p = Panel(L, dict(c=((80, 120), 8)))
    p.set(c=ord("H"))                               # 'H' (0x48) → 'h' (0x68)
    L.shot(os.path.join(IMG, "logisim_branch_H.png"))
    p.set(c=ord("!"))                               # '!' (0x21) — не буква, без изменений
    L.shot(os.path.join(IMG, "logisim_branch_excl.png"))
    L.open_circuit(1)                               # tolower_nobranch
    q = Panel(L, dict(c=((80, 120), 8)))
    q.set(c=ord("H"))
    L.shot(os.path.join(IMG, "logisim_nobranch_H.png"))
