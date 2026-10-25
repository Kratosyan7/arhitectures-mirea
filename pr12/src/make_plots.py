"""Графики и сводная таблица по results.json (замеры bench.py)."""
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BLUE, ORANGE = '#2a78d6', '#eb6834'
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'

d = json.load(open('results.json', encoding='utf-8'))
rows = d['rows']
labels = [f'{r["width"]}×{r["height"]}' for r in rows]
mp = [r['mpix'] for r in rows]
cpu = [r['cpu_med'] for r in rows]
gpu = [r['gpu_med'] for r in rows]
sp = [r['speedup_med'] for r in rows]

print(f'{"Разрешение":>11} {"Мпикс":>6} {"CPU, мс":>9} {"GPU, мс":>8} {"Ускор.":>7} {"Mean":>6} {"Max":>4} {"Отл.пикс,%":>10}')
for r, l in zip(rows, labels):
    print(f'{l:>11} {r["mpix"]:6.2f} {r["cpu_med"]:9.1f} {r["gpu_med"]:8.1f} {r["speedup_med"]:6.1f}x '
          f'{r["meanDiff"]:>6} {r["maxDiff"]:>4} {r["diffPixelsPct"]:10.3f}')
for r in rows:
    print(f'{r["width"]}x{r["height"]}: CPU {r["cpu_med"]/r["mpix"]:.0f} мс/Мпикс, GPU {r["gpu_med"]/r["mpix"]:.1f} мс/Мпикс')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': INK2,
                     'axes.labelcolor': INK, 'xtick.color': INK2, 'ytick.color': INK2})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for ax in (a1, a2):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)

a1.loglog(mp, cpu, '-o', color=BLUE, lw=2, ms=6, label='CPU (JavaScript, 1 поток)')
a1.loglog(mp, gpu, '-s', color=ORANGE, lw=2, ms=6, label='GPU (WebGPU, RTX 3060)')
for x, y in ((mp[-1], cpu[-1]), (mp[-1], gpu[-1])):
    a1.annotate(f'{y:.0f} мс', (x, y), textcoords='offset points', xytext=(-6, 8), ha='right', color=INK)
a1.set_xticks(mp)
a1.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
a1.minorticks_off()
a1.set_ylabel('Время, мс (медиана)')
a1.set_title('Время генерации кадра', color=INK)
a1.legend(frameon=False, loc='upper left')

xs = range(len(sp))
bars = a2.bar(xs, sp, color=BLUE, width=0.6)
for b, v in zip(bars, sp):
    a2.text(b.get_x() + b.get_width() / 2, v + 0.6, f'{v:.0f}×', ha='center', color=INK, fontsize=9)
a2.set_xticks(list(xs))
a2.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
a2.set_ylabel('Ускорение CPU / GPU, раз')
a2.set_title('Ускорение GPU относительно CPU', color=INK)
fig.tight_layout()
fig.savefig('../img/bench_plot.png', dpi=150)
print('saved ../img/bench_plot.png')
