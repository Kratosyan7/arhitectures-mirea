"""Анализ расхождений CPU/GPU для варианта 14 (множество Жюлиа, 1920x1080).

Повторяет вычисление в numpy в трёх арифметических моделях:
  f64  — двойная точность, как в JavaScript (CPU-канал стенда);
  f32  — одинарная точность, каждая операция округляется отдельно;
  gpu  — одинарная точность так, как её фактически компилирует драйвер:
         деление на (W-1) заменено умножением на обратную величину
         x * (1/(W-1)), а выражения a*b+c слиты в FMA (одно округление):
         t = fma(zx, zx, -(zy*zy)) + kx,  zy = fma(2*zx, zy, ky).
Сравнивает маску «точка множества» (чёрные пиксели) с реальными кадрами
CPU и GPU, сохранёнными bench.py (../img/julia_*_1920x1080.png).
"""
import numpy as np
from PIL import Image

W, H, MAXIT, KR, KI = 1920, 1080, 300, -0.8, 0.156
f32, f64 = np.float32, np.float64


def fma(a, b, c):
    # произведение f32*f32 точно представимо в f64 -> одно округление (как FMA)
    return (a.astype(f64) * b.astype(f64) + np.asarray(c, f64)).astype(f32)


def julia(mode):
    dt = f64 if mode == 'f64' else f32
    x = np.arange(W, dtype=dt)
    y = np.arange(H, dtype=dt)[:, None]
    if mode == 'gpu':
        uvx, uvy = x * (dt(1) / dt(W - 1)), y * (dt(1) / dt(H - 1))
    else:
        uvx, uvy = x / dt(W - 1), y / dt(H - 1)
    cx, cy = uvx * dt(2) - dt(1), uvy * dt(2) - dt(1)
    zx = (cx * (dt(W) / dt(H)) + 0 * cy).astype(dt)
    zy = (-cy + 0 * cx).astype(dt)
    kr, ki = dt(KR), dt(KI)
    it = np.zeros((H, W), np.int32)
    r2 = zx * zx + zy * zy
    alive = r2 <= 4
    for _ in range(MAXIT):
        if mode == 'gpu':
            t = fma(zx, zx, -(zy * zy)) + kr
            nzy = fma(dt(2) * zx, zy, ki)
        else:
            t = zx * zx - zy * zy + kr
            nzy = dt(2) * zx * zy + ki
        zx = np.where(alive, t, zx)
        zy = np.where(alive, nzy, zy)
        it += alive
        r2 = zx * zx + zy * zy
        alive &= (r2 <= 4) & (it < MAXIT)
    return it


def main():
    res = {m: julia(m) for m in ('f64', 'f32', 'gpu')}
    gpu = np.asarray(Image.open('../img/julia_gpu_1920x1080.png')).astype(int)
    cpu = np.asarray(Image.open('../img/julia_cpu_1920x1080.png')).astype(int)
    gin, cin = gpu.sum(2) == 0, cpu.sum(2) == 0
    print('Доля пикселей с разным числом итераций между моделями:')
    names = list(res)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            print(f'  {names[i]:4s} vs {names[j]:4s}: {100 * (res[names[i]] != res[names[j]]).mean():6.3f} %')
    print('Отличие маски множества (чёрные пиксели) модели от реального кадра:')
    for m, it in res.items():
        ins = it >= MAXIT
        print(f'  модель {m:4s}: от GPU {100 * (ins != gin).mean():6.3f} %,'
              f' от CPU (JS) {100 * (ins != cin).mean():6.3f} %')
    print(f'  кадр CPU (JS) vs кадр GPU: {100 * (cin != gin).mean():6.3f} %')
    print(f'Точек множества в кадре GPU: {100 * gin.mean():.2f} %')


if __name__ == '__main__':
    main()
