"""Скриншоты GUI Logisim для ПР2 (вариант 28): демультиплексор 1→4, T-триггер, счётчик."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")

# --- демультиплексор 1→4: вход D = 1, адрес A1A0 = 01 (1) -> выход Y1 = 1 ---
with Logisim(os.path.join(HERE, "demux.circ"), zoom=1.0) as L:
    p = Panel(L, dict(D=((60, 200), 1), A0=((160, 360), 1), A1=((160, 400), 1)))
    p.set(D=1, A0=1)                         # D=1, адрес 1 -> Y1=1
    L.shot(os.path.join(IMG, "logisim_demux.png"))

# --- T-триггер: T=1 переключение, затем T=0 хранение ---
with Logisim(os.path.join(HERE, "t.circ"), zoom=1.5) as L:
    p = Panel(L, dict(T=((60, 150), 1)))
    p.set(T=1)
    L.tick(1)                                # фронт -> Q переключается в 1
    L.shot(os.path.join(IMG, "logisim_t_toggle.png"))
    p.set(T=0)
    L.tick(1)                                # хранение -> Q остаётся 1
    L.shot(os.path.join(IMG, "logisim_t_hold.png"))

# --- счётчик по модулю 16 (строка 29) ---
with Logisim(os.path.join(HERE, "counter.circ"), zoom=0.75) as L:
    p = Panel(L, dict(A=((40, 60), 1), B=((40, 120), 1)))
    p.set(A=1, B=1)
    L.tick(6)
    L.shot(os.path.join(IMG, "logisim_counter.png"))
    L.shot(os.path.join(IMG, "logisim_counter_logic.png"), (900, 0, 1920, 820))
    L.set_zoom(1.0)
    L.shot(os.path.join(IMG, "logisim_counter_ff.png"), (0, 0, 1300, 760))
    L.set_zoom(0.5)
    L.open_circuit(1)                        # newQ_min
    q = Panel(L, {k: ((x, 40), 1, "south") for k, x in
                  dict(Q3=80, Q2=150, Q1=220, Q0=290, a=360, b=430).items()})
    q.set(Q3=1, Q2=1, a=1)
    L.shot(os.path.join(IMG, "logisim_newq_min.png"))
