"""Эталонная модель схемы pr12.circ в фиксированной точке (Python).

Формат Q4.12: 16 бит, дополнительный код, 12 дробных бит (шаг 1/4096,
диапазон [-8; 8)). Произведения считаются в 32 битах (Q8.24), затем
берутся биты [27..12] (для 2*zx*zy — биты [26..11]), что соответствует
арифметическому сдвигу вправо с округлением вниз и усечению до 16 бит.
Сравнение |z|^2 > 4 выполняется в Q8.24.

Запуск: python fixed.py  — печатает эталонную трассу по тактам и
сравнивает итоговое число итераций с расчётом в double (как CPU-канал стенда).
"""
FRAC = 12
K_RE, K_IM = -0.8, 0.156
W, H = 1920, 1080          # кадр варианта 14
MAXSTEP = 32               # предел шагов в схеме (halt)

# Четыре пикселя кадра 1920x1080 (одна строка y = 600), подобраны так,
# чтобы линии уходили на разных итерациях, а одна оставалась в множестве.
PIXEL_XY = [(740, 600), (1100, 600), (1180, 600), (920, 600)]


def q(v):
    """Вещественное -> Q4.12 (int, со знаком)."""
    return wrap(round(v * (1 << FRAC)), 16)


def wrap(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v


def hex16(v):
    return hex(v & 0xFFFF)


def pixel_to_z(x, y):
    cx = x / (W - 1) * 2 - 1
    cy = y / (H - 1) * 2 - 1
    return cx * W / H, -cy


K_X, K_Y = q(K_RE), q(K_IM)
PIXELS = [(x, y, q(pixel_to_z(x, y)[0]), q(pixel_to_z(x, y)[1])) for x, y in PIXEL_XY]


def lane_step(zx, zy):
    """Комбинационная часть линии: (zx', zy', esc)."""
    xx, yy, xy = wrap(zx * zx, 32), wrap(zy * zy, 32), wrap(zx * zy, 32)
    r2 = wrap(xx + yy, 32)
    esc = r2 > (4 << 24)
    re = wrap(xx - yy, 32)
    zxn = wrap(wrap(re >> 12, 16) + K_X, 16)
    zyn = wrap(wrap(xy >> 11, 16) + K_Y, 16)
    return zxn, zyn, esc


def simulate(maxstep=MAXSTEP):
    """Трасса по тактам: список состояний после каждого такта ITER (STEP = 0..)."""
    lanes = [[zx, zy, 0] for (_, _, zx, zy) in PIXELS]
    trace = []
    step = 0
    while True:
        escs = [lane_step(zx, zy)[2] for zx, zy, _ in lanes]
        trace.append((step, [tuple(l) for l in lanes], escs))
        if step == maxstep or all(escs):
            break
        for l, e in zip(lanes, escs):
            if not e:                       # маскирование ушедших линий
                zx, zy, _ = lane_step(l[0], l[1])
                l[0], l[1], l[2] = zx, zy, l[2] + 1
        step += 1
    return trace


def iters_double(x, y, maxit=MAXSTEP):
    zx, zy = pixel_to_z(x, y)
    i = 0
    while i < maxit and zx * zx + zy * zy <= 4:
        zx, zy = zx * zx - zy * zy + K_RE, 2 * zx * zy + K_IM
        i += 1
    return i


if __name__ == '__main__':
    print(f'kx = {K_X} ({hex16(K_X)}), ky = {K_Y} ({hex16(K_Y)}), MAXSTEP = {MAXSTEP}')
    for i, (x, y, zx, zy) in enumerate(PIXELS):
        print(f'lane{i}: pixel ({x},{y}) z0 = {zx / 4096:+.4f} {zy / 4096:+.4f}i'
              f' -> Q4.12 {hex16(zx)} {hex16(zy)}')
    tr = simulate()
    for step, lanes, escs in tr:
        print(f'STEP={step:2d} ' + ' | '.join(f'{hex16(zx)} {hex16(zy)} N={n:2d} {"ESC" if e else "act"}'
                                         for (zx, zy, n), e in zip(lanes, escs)))
    final = tr[-1][1]
    print('итог (фиксированная точка Q4.12 vs double):')
    for i, ((x, y, _, _), (_, _, n)) in enumerate(zip(PIXELS, final)):
        print(f'  lane{i}: N = {n:2d}, double: {iters_double(x, y)}')
