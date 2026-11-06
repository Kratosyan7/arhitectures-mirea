"""Скриншоты GUI Logisim для ПР3 (вариант 28): выполнение S ← AC * 2 на модели ОУ."""
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
    # загрузка операнда: AC ← Ввод (2B5C); ALU = передача A (000000)
    p.set(IN=0x2B5C, MSA=7, E=1, DC=6)        # DC=110 -> AC
    p.pulse("CLK")
    L.shot(os.path.join(IMG, "logisim_ou_operands.png"))
    # управляющее слово варианта 28: MSA=001 (AC), ALU 111000 (F=1 M=1 S2S1S0=100 -> ×2),
    # запись в регистр не выполняется (E=0, результат только на S-шине), MSM=0, WR=0
    p.set(MSA=1, MSB=0, F=1, M=1, S2=1, E=0, DC=0, MSM=0, WR=0)
    L.shot(os.path.join(IMG, "logisim_ou_word.png"))   # на S-шине 56B8 = AC·2
    L.open_circuit(1)                         # подсхема ALU
    L.shot(os.path.join(IMG, "logisim_alu.png"))
