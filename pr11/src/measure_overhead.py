"""
Оценка накладных расходов «OpenMP»-версии (multiprocessing.Pool) и MPI.

Запуск: python -m src.measure_overhead
Измеряет время создания пула из p процессов + раздачи пустых задач + сбора
результата и закрытия пула, т.е. ту часть parallel_integration_openmp(),
которая не зависит от объёма вычислений.
"""
import statistics
import time
from multiprocessing import Pool

from .main import THREADS_LIST, REPEATS, A, B, N, K, FUNCTION_TYPE
from .parallel_integration_openmp import _compute_partial_sum


def _empty_task(args):
    return 0.0


def _timed_partial_sum(args):
    """Та же частичная сумма, что в parallel_integration_openmp, но с отметками времени."""
    t0 = time.time()
    value = _compute_partial_sum(args)
    return value, t0, time.time()


def decompose(p):
    """Разбивает время одного запуска на запуск воркеров, счёт и завершение."""
    h = (B - A) / N
    chunk = (N - 1) // p
    tasks = [(1 + i * chunk, 1 + (i + 1) * chunk if i < p - 1 else N, A, h, K, FUNCTION_TYPE)
             for i in range(p)]
    start = time.time()
    with Pool(processes=p) as pool:
        res = pool.map(_timed_partial_sum, tasks)
    total = time.time() - start
    first_start = min(r[1] for r in res) - start
    last_start = max(r[1] for r in res) - start
    compute = [r[2] - r[1] for r in res]
    tail = total - (max(r[2] for r in res) - start)
    return total, first_start, last_start, min(compute), max(compute), tail


def main():
    print(f"Накладные расходы multiprocessing.Pool (медиана из {REPEATS * 2} замеров)")
    for p in THREADS_LIST:
        samples = []
        for _ in range(REPEATS * 2):
            start = time.time()
            with Pool(processes=p) as pool:
                pool.map(_empty_task, [(i,) for i in range(p)])
            samples.append(time.time() - start)
        print(f"  p = {p}: {statistics.median(samples) * 1000:.1f} мс")

    print(f"\nРазложение времени parallel_integration_openmp (вариант, N = {N:,}), с:")
    print(f"{'p':>3} | {'всего':>6} | {'старт 1-го':>10} | {'старт посл.':>11} | "
          f"{'счёт min':>8} | {'счёт max':>8} | {'сбор+закр.':>10}")
    for p in THREADS_LIST:
        runs = sorted((decompose(p) for _ in range(REPEATS)), key=lambda r: r[0])
        t = runs[len(runs) // 2]
        print(f"{p:>3} | {t[0]:>6.3f} | {t[1]:>10.3f} | {t[2]:>11.3f} | "
              f"{t[3]:>8.3f} | {t[4]:>8.3f} | {t[5]:>10.3f}")


if __name__ == "__main__":
    main()
