import numpy as np


def function_to_integrate(x, k, function_type='sin'):
    """
    Вычисляет значение функции в точке x.

    Вынесена в отдельный модуль (Задание №3), чтобы последовательная,
    многопроцессная (OpenMP-аналог) и MPI-версии интегрировали одну и ту же
    функцию. Для варианта 14 используется function_type='x2': f(x) = k * x².

    Параметры:
    ----------
    x : float
        Точка, в которой вычисляется значение
    k : float
        Коэффициент функции
    function_type : str
        Тип функции: 'sin', 'x2', 'exp'
    """
    if function_type == 'sin':
        return k * np.sin(x)
    elif function_type == 'x2':        # вариант 14: f(x) = k·x², k = 1.5
        return k * x * x
    elif function_type == 'exp':
        return k * np.exp(-x)
    else:
        raise ValueError(f"Неизвестный тип функции: {function_type}")
