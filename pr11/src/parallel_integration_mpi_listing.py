# Исходная версия листинга 11.3 (без исправления границ) — для сравнения в check_mpi_fix.py
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

    # Локальное интегрирование на каждом процессе
    local_integral = 0.0

    for i in range(local_n):
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
