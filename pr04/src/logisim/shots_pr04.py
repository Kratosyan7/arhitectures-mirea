"""Скриншоты GUI Logisim для отчёта пр.4: выполнение INCA (адрес EBC) на модели УУ + ОУ."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
STEPS = ["C0t0", "C0t1", "C0t2", "C0t3", "C2t0", "C2t1", "C2t2", "C2t3"]

with Logisim(os.path.join(HERE, "pr04_cu.circ"), zoom=1.0) as L:
    p = Panel(L, dict(SE=((140, 170), 1)))
    # исходное состояние: PC = EBC, AC = F23F (ввод значений в регистры инструментом Poke)
    L.poke_register((1200, 780), "EBC")
    L.poke_register((1200, 670), "F23F")
    L.click(40, 1150)  # снять фокус с регистра
    p.set(SE=1)
    L.shot(os.path.join(IMG, "logisim_vm_start.png"))
    for name in STEPS:
        L.tick(2)  # полный период генератора = один такт ВМ
        L.shot(os.path.join(IMG, f"logisim_vm_{name}.png"))
    L.set_zoom(0.75)
    L.shot(os.path.join(IMG, "logisim_vm_overview.png"))
