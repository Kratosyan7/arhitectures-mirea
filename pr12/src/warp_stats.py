"""Оценка нагрузки варианта 14 и эффективности SIMT (расхождение ветвей в варпе).
Workgroup стенда 16x16 = 256 потоков = 8 варпов по 32; варп — 2 строки по 16 пикселей."""
import numpy as np
from fp_check import julia, W, H, MAXIT

it = julia('f64').astype(np.float64)
# число выполненных итераций цикла: для точки множества — MAXIT
warps = it.reshape(H // 2, 2, W // 16, 16).transpose(0, 2, 1, 3).reshape(-1, 32)
mean_it = it.mean()
mean_warp_max = warps.max(axis=1).mean()
print(f'Кадр {W}x{H}: среднее число итераций на пиксель {mean_it:.1f}, '
      f'всего итераций {it.sum() / 1e6:.1f} млн')
print(f'Среднее по варпам максимальное число итераций {mean_warp_max:.1f}; '
      f'эффективность SIMT (доля активных потоков) {mean_it / mean_warp_max * 100:.1f} %')
print(f'Доля пикселей множества (300 итераций): {(it >= MAXIT).mean() * 100:.2f} %')
