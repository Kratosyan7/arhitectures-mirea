import math
import time
import numpy as np

from .function_to_integrate import function_to_integrate


def sequential_integration(a, b, n, variant_param, function_type='sin'):
    """
    Последовательная реализация метода трапеций для численного интегрирования.

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

    Возвращает:
    -----------
    float
        Приближенное значение интеграла

    Описание метода:
    ----------------
    I ≈ h * (f(x₀)/2 + f(x₁) + ... + f(xₙ₋₁) + f(xₙ)/2),
    где h = (b - a) / n, xᵢ = a + i*h. Все n + 1 значений функции
    вычисляются одним процессом в одном цикле.
    """
    h = (b - a) / n

    # Граничные точки входят с весом 1/2
    integral = 0.5 * (function_to_integrate(a, variant_param, function_type) +
                      function_to_integrate(b, variant_param, function_type))

    # Внутренние точки входят с весом 1
    for i in range(1, n):
        x = a + i * h
        integral += function_to_integrate(x, variant_param, function_type)

    # Умножаем на ширину трапеции
    integral *= h

    return integral
