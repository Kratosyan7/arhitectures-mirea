import sys
import time
import math
import numpy as np

try:
    from mpi4py import MPI
    MPI_AVAILABLE = True
except ImportError:
    MPI_AVAILABLE = False
    print("Warning: mpi4py не установлен. MPI-версия недоступна.")

from .function_to_integrate import function_to_integrate


def parallel_integration_mpi(a, b, n, k, function_type='sin'):
    """
    MPI-реализация метода трапеций для численного интегрирования.

    Параметры:
    ----------
    a : float
        Нижняя граница интегрирования
    b : float
        Верхняя граница интегрирования
    n : int
        Число разбиений интервала
    k : float
        Параметр функции (коэффициент k)
    function_type : str
        Тип функции: 'sin', 'x2', 'exp'

    Возвращает:
    -----------
    tuple (float, int, int)
        (результат интегрирования, ранг процесса, общее число процессов)

    Описание:
    ---------
    Каждый MPI-процесс вычисляет интеграл на своей части интервала [a, b].
    Результаты собираются на процессе с рангом 0 с помощью операции MPI.reduce.

    Алгоритм:
    1. Разбить интервал [a, b] на части по числу процессов
    2. Каждый процесс вычисляет интеграл на своей части
    3. Процесс 0 собирает результаты и суммирует их (операция reduce)
    """
    if not MPI_AVAILABLE:
        raise RuntimeError("mpi4py не установлен. Установите: pip install mpi4py")

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    h = (b - a) / n

    # Определяем локальные границы для каждого процесса
    local_n = n // size
    local_a = a + rank * local_n * h
    local_b = local_a + local_n * h

    # Исправление (Задание №3): в листинге 11.3 цикл у процесса 0 начинался
    # с i = 0, поэтому f(a) входила в сумму с весом 1 + 0.5 = 1.5 вместо 0.5
    # (ошибка ровно h·f(a)), а при n, не кратном size, последние n % size
    # точек терялись. Процесс 0 пропускает x₀ = a (её добавляем ниже с весом
    # 1/2), последний процесс забирает остаток разбиений.
    start_i = 1 if rank == 0 else 0
    end_i = local_n if rank < size - 1 else n - rank * local_n

    # Локальное интегрирование на каждом процессе
    local_integral = 0.0

    for i in range(start_i, end_i):
        x = local_a + i * h
        local_integral += function_to_integrate(x, k, function_type)

    # Обработка граничных значений
    # Только первый процесс добавляет левую границу
    if rank == 0:
        local_integral += 0.5 * function_to_integrate(a, k, function_type)

    # Только последний процесс добавляет правую границу
    if rank == size - 1:
        local_integral += 0.5 * function_to_integrate(b, k, function_type)

    # Умножаем локальный результат на шаг
    local_integral *= h

    # Сбор результатов на процессе 0 (операция редукции - суммирование)
    total_integral = comm.reduce(local_integral, op=MPI.SUM, root=0)

    return total_integral, rank, size


def _run_from_command_line():
    """
    Точка входа для запуска через mpiexec:

        mpiexec -n P python -m src.parallel_integration_mpi VARIANT [A B N K TYPE]

    Если параметры интегрирования не переданы, они берутся из src/main.py.
    Время замеряется через MPI.Wtime() от общего барьера до завершения reduce
    (берётся максимум по процессам); запуск интерпретаторов и импорт модулей
    в замер не входят. Процесс 0 печатает строку для разбора в main.py.
    """
    if len(sys.argv) >= 7:
        variant = int(sys.argv[1])
        a, b = float(sys.argv[2]), float(sys.argv[3])
        n, k, function_type = int(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
    else:
        from . import main as cfg
        variant = int(sys.argv[1]) if len(sys.argv) > 1 else cfg.VARIANT_NUM
        a, b, n, k, function_type = cfg.A, cfg.B, cfg.N, cfg.K, cfg.FUNCTION_TYPE

    comm = MPI.COMM_WORLD
    comm.Barrier()
    t_start = MPI.Wtime()
    result, rank, size = parallel_integration_mpi(a, b, n, k, function_type)
    t_local = MPI.Wtime() - t_start
    t_max = comm.reduce(t_local, op=MPI.MAX, root=0)

    if rank == 0:
        print(f"MPI variant={variant} size={size} result={result:.12f} time={t_max:.6f}",
              flush=True)


if __name__ == "__main__":
    _run_from_command_line()
