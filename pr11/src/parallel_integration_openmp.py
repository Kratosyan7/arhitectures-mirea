import math
import time
import numpy as np
from multiprocessing import Pool

from .function_to_integrate import function_to_integrate


def _compute_partial_sum(args):
    """
    Вспомогательная функция для вычисления частичной суммы.
    Используется для параллельного выполнения через multiprocessing.

    Параметры:
    ----------
    args : tuple
        (start_idx, end_idx, a, h, variant_param, function_type)

    Возвращает:
    -----------
    float
        Частичная сумма значений функции
    """
    start_idx, end_idx, a, h, variant_param, function_type = args
    partial_sum = 0.0

    for i in range(start_idx, end_idx):
        x = a + i * h
        partial_sum += function_to_integrate(x, variant_param, function_type)

    return partial_sum


def parallel_integration_openmp(a, b, n, variant_param, function_type='sin', num_threads=4):
    """
    Параллельная реализация метода трапеций с использованием многопоточности.
    Имитирует OpenMP через multiprocessing.

    Параметры:
    ----------
    a : float
        Нижняя граница интегрирования
    b : float
        Верхняя граница интегрирования
    n : int
        Число разбиений интервала
    variant_param : float
        Параметр функции (коэффициент k)
    function_type : str
        Тип функции: 'sin', 'x2', 'exp'
    num_threads : int
        Число параллельных потоков/процессов

    Возвращает:
    -----------
    float
        Приближенное значение интеграла

    Описание:
    ---------
    Задача разбивается на num_threads частей, каждая из которых
    обрабатывается отдельным процессом. Результаты объединяются.
    Используется модель fork-join параллелизма.
    """
    h = (b - a) / n

    # Вычисляем граничные значения (выполняется в главном потоке)
    integral = 0.5 * (function_to_integrate(a, variant_param, function_type) +
                      function_to_integrate(b, variant_param, function_type))

    # Разбиваем работу между потоками
    chunk_size = (n - 1) // num_threads
    tasks = []

    for i in range(num_threads):
        start_idx = 1 + i * chunk_size
        end_idx = 1 + (i + 1) * chunk_size if i < num_threads - 1 else n
        tasks.append((start_idx, end_idx, a, h, variant_param, function_type))

    # Параллельное вычисление частичных сумм
    with Pool(processes=num_threads) as pool:
        partial_sums = pool.map(_compute_partial_sum, tasks)

    # Объединение результатов
    integral += sum(partial_sums)
    integral *= h

    return integral
