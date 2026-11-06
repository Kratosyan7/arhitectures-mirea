"""Скриншоты GUI Logisim для пр.6: расчёт IOPS/BW по закону Литтла и генератор randwrite."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../../tools/logisim"))
from gui import Logisim, Panel  # noqa: E402

IMG = os.path.join(HERE, "../../img")
with Logisim(os.path.join(HERE, "pr06_fio.circ")) as L:
    p = Panel(L, dict(QD=((240, 120), 8), LAT=((240, 200), 16), BS=((240, 300), 16)))
    p.set(QD=1, LAT=8593, BS=8192)   # iodepth=1, полная задержка цикла (запись+fsync) ~8593 мкс, bs=8 КиБ
    L.shot(os.path.join(IMG, "logisim_fio_metrics.png"))
    L.open_circuit(1)
    L.shot(os.path.join(IMG, "logisim_fio_rand0.png"))
    L.tick(10)                       # 5 полных периодов генератора = 5 запросов
    L.shot(os.path.join(IMG, "logisim_fio_rand5.png"))
