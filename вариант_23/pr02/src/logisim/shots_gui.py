"""Скриншоты GUI Logisim для ПР2 (вариант 23): мультиплексор 16→1, T-триггер, счётчик."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")

# --- мультиплексор 16→1: адрес A3A2A1A0 = 0101 (5), вход D5 = 1 -> выход Y = 1 ---
with Logisim(os.path.join(HERE, "mux.circ"), zoom=0.75) as L:
    pins = {f"D{k}": ((60, 60 + 34 * k), 1) for k in range(16)}
    pins.update({f"A{i}": ((360, 640 + 40 * i), 1) for i in range(4)})
    p = Panel(L, pins)
    p.set(D5=1, A0=1, A2=1)                  # D5=1, адрес 5 -> Y=D5=1
    L.shot(os.path.join(IMG, "logisim_mux.png"))

# --- T-триггер: T=1 переключение, затем T=0 хранение ---
with Logisim(os.path.join(HERE, "t.circ"), zoom=1.5) as L:
    p = Panel(L, dict(T=((60, 150), 1)))
    p.set(T=1)
    L.tick(1)                                # фронт -> Q переключается в 1
    L.shot(os.path.join(IMG, "logisim_t_toggle.png"))
    p.set(T=0)
    L.tick(1)                                # хранение -> Q остаётся 1
    L.shot(os.path.join(IMG, "logisim_t_hold.png"))

# --- счётчик по модулю 16 (строка 24) ---
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
