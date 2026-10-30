"""Скриншоты GUI Logisim для ПР2 (вариант 21): дешифратор 4→16, JK-триггер, счётчик."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")

# --- дешифратор 4→16: адрес A3A2A1A0 = 0101 (5) -> активен выход Y5 ---
with Logisim(os.path.join(HERE, "decoder.circ"), zoom=1.0) as L:
    p = Panel(L, {f"A{i}": ((60, 80 + 40 * i), 1) for i in range(4)})
    p.set(A0=1, A2=1)                       # адрес 5
    L.shot(os.path.join(IMG, "logisim_decoder.png"))

# --- JK-триггер: режим счёта J=K=1, один фронт -> Q переключается в 1 ---
with Logisim(os.path.join(HERE, "jk.circ"), zoom=1.5) as L:
    p = Panel(L, dict(J=((60, 120), 1), K=((60, 220), 1)))
    p.set(J=1, K=1)
    L.tick(1)                               # фронт синхросигнала -> toggle
    L.shot(os.path.join(IMG, "logisim_jk_toggle.png"))
    p.set(J=0, K=1)                         # сброс
    L.tick(1)
    L.shot(os.path.join(IMG, "logisim_jk_reset.png"))

# --- счётчик по модулю 16 (строка 22) ---
with Logisim(os.path.join(HERE, "counter.circ"), zoom=0.75) as L:
    p = Panel(L, dict(A=((40, 60), 1), B=((40, 120), 1)))
    p.set(A=1, B=1)
    L.tick(6)
    L.shot(os.path.join(IMG, "logisim_counter.png"))
    L.shot(os.path.join(IMG, "logisim_counter_logic.png"), (900, 0, 1920, 820))
    L.set_zoom(1.0)
    L.shot(os.path.join(IMG, "logisim_counter_ff.png"), (0, 0, 1300, 760))
    L.set_zoom(0.5)
    L.open_circuit(1)                       # newQ_min
    q = Panel(L, {k: ((x, 40), 1, "south") for k, x in
                  dict(Q3=80, Q2=150, Q1=220, Q0=290, a=360, b=430).items()})
    q.set(Q3=1, Q2=1, a=1)
    L.shot(os.path.join(IMG, "logisim_newq_min.png"))
