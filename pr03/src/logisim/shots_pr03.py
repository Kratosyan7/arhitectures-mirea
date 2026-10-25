"""Скриншоты GUI Logisim для отчёта пр.3 (выполнение MDR ← IR ⊕ AC на модели ОУ)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
PINS = dict(MSA=((80, 110), 3), MSB=((80, 150), 3), F=((80, 210), 1), M=((80, 250), 1), S2=((80, 290), 1),
            S1=((80, 330), 1), S0=((80, 370), 1), C0=((80, 410), 1), E=((80, 470), 1), DC=((80, 510), 3),
            MSM=((80, 570), 1), WR=((80, 610), 1), CLK=((80, 670), 1), IN=((140, 740), 16))

with Logisim(os.path.join(HERE, "pr03_ou.circ")) as L:
    p = Panel(L, PINS)
    L.shot(os.path.join(IMG, "logisim_ou_start.png"))
    # подготовка операндов: IR ← Ввод (5A3C), AC ← Ввод (0FF0)
    p.set(IN=0x5A3C, MSA=7, E=1, DC=5)
    p.pulse("CLK")
    p.set(IN=0x0FF0, DC=6)
    p.pulse("CLK")
    L.shot(os.path.join(IMG, "logisim_ou_operands.png"))
    # управляющее слово варианта 14: MSA=010 (IR), MSB=001 (AC), АЛУ 001010 (XOR), DC=1 011 (MDR), MSM=0
    p.set(MSA=2, MSB=1, S2=1, S0=1, DC=3, MSM=0)
    L.shot(os.path.join(IMG, "logisim_ou_word.png"))
    p.pulse("CLK")
    L.shot(os.path.join(IMG, "logisim_ou_result.png"))
    L.open_circuit(1)
    L.shot(os.path.join(IMG, "logisim_alu.png"))
