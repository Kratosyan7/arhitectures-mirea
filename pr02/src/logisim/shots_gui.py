"""Скриншоты GUI Logisim для пр.2 (по SCREENSHOTS.md)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
CODER = {f"I{k}": ((60, y), 1) for k, y in zip(range(4), (60, 100, 200, 300))}

with Logisim(os.path.join(HERE, "coder.circ"), zoom=1.5) as L:
    p = Panel(L, CODER)
    p.set(I2=1)
    L.shot(os.path.join(IMG, "logisim_coder.png"))
    L.open_circuit(1)
    p = Panel(L, CODER)
    p.set(I1=1, I2=1)
    L.shot(os.path.join(IMG, "logisim_coder_prio.png"))

with Logisim(os.path.join(HERE, "t_trigger.circ"), zoom=1.5) as L:
    p = Panel(L, dict(T=((40, 220), 1), nS=((40, 40), 1), nR=((40, 100), 1)))
    p.set(nS=1)
    p.set(nR=1)
    p.set(T=1)
    p.set(T=0)
    L.shot(os.path.join(IMG, "logisim_t_trigger.png"))

with Logisim(os.path.join(HERE, "counter.circ"), zoom=0.75) as L:
    p = Panel(L, dict(A=((40, 60), 1), B=((40, 120), 1)))
    p.set(A=1, B=1)
    L.tick(6)
    L.shot(os.path.join(IMG, "logisim_counter.png"))
    L.shot(os.path.join(IMG, "logisim_counter_logic.png"), (900, 0, 1920, 820))
    L.set_zoom(1.0)
    L.shot(os.path.join(IMG, "logisim_counter_ff.png"), (0, 0, 1300, 760))
    L.set_zoom(0.5)
    L.open_circuit(1)
    q = Panel(L, {k: ((x, 40), 1, "south") for k, x in
                  dict(Q3=80, Q2=150, Q1=220, Q0=290, a=360, b=430).items()})
    q.set(Q3=1, Q2=1, a=1)
    L.shot(os.path.join(IMG, "logisim_newq_min.png"))
