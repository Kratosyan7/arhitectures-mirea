"""Скриншоты GUI Logisim для ПР3 (вариант 21): выполнение INPR ← MAR + OUTR на модели ОУ."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
PINS = dict(MSA=((80, 110), 3), MSB=((80, 150), 3), F=((80, 210), 1), M=((80, 250), 1), S2=((80, 290), 1),
            S1=((80, 330), 1), S0=((80, 370), 1), C0=((80, 410), 1), E=((80, 470), 1), DC=((80, 510), 3),
            MSM=((80, 570), 1), WR=((80, 610), 1), CLK=((80, 670), 1), IN=((140, 740), 16))

with Logisim(os.path.join(HERE, "pr03_ou.circ")) as L:
    p = Panel(L, PINS)
    L.shot(os.path.join(IMG, "logisim_ou_start.png"))
    # подготовка операндов: MAR ← Ввод (0A2B), OutR ← Ввод (2C3D)
    p.set(IN=0x0A2B, MSA=7, E=1, DC=4)        # DC=100 -> MAR
    p.pulse("CLK")
    p.set(IN=0x2C3D, DC=1)                    # DC=001 -> OutR
    p.pulse("CLK")
    L.shot(os.path.join(IMG, "logisim_ou_operands.png"))
    # управляющее слово варианта 21: MSA=011 (MAR), MSB=110 (OutR),
    # АЛУ 000010 (A+B), DC=1 010 (InpR), MSM=0, WR=0
    p.set(MSA=3, MSB=6, S0=1, DC=2, MSM=0, WR=0)
    L.shot(os.path.join(IMG, "logisim_ou_word.png"))
    p.pulse("CLK")                            # фронт CLK -> INPR = 4668
    L.shot(os.path.join(IMG, "logisim_ou_result.png"))
    L.open_circuit(1)                         # подсхема ALU
    L.shot(os.path.join(IMG, "logisim_alu.png"))
