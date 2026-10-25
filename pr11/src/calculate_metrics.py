def calculate_metrics(time_seq, times_parallel, num_processors_list):
    """
    Вычисляет метрики производительности параллельных программ.

    Параметры:
    ----------
    time_seq : float
        Время выполнения последовательной программы
    times_parallel : list of float
        Список времен выполнения параллельной программы для разного числа процессоров
    num_processors_list : list of int
        Список количества процессоров/потоков

    Возвращает:
    -----------
    list of dict
        Список словарей с метриками для каждого числа процессоров.
        Каждый словарь содержит:
        - processors: int - число процессоров
        - time: float - время выполнения
        - speedup: float - ускорение S(p) = T₁ / Tₚ
        - efficiency: float - эффективность E(p) = S(p) / p × 100%
        - overhead: float - избыточность O(p) = p × Tₚ - T₁
        - cost: float - стоимость C(p) = p × Tₚ

    Формулы:
    --------
    - Ускорение: S(p) = T₁ / Tₚ
    - Эффективность: E(p) = S(p) / p
    - Избыточность: O(p) = p × Tₚ - T₁
    - Стоимость: C(p) = p × Tₚ

    Пример:
    -------
    >>> metrics = calculate_metrics(10.0, [5.2, 2.7], [2, 4])
    >>> print(metrics[0]['speedup'])
    1.92
    >>> print(metrics[0]['efficiency'])
    96.0
    """
    metrics = []

    for p, time_p in zip(num_processors_list, times_parallel):
        # Ускорение
        speedup = time_seq / time_p if time_p > 0 else 0

        # Эффективность (в процентах)
        efficiency = (speedup / p * 100) if p > 0 else 0

        # Избыточность
        overhead = p * time_p - time_seq

        # Стоимость
        cost = p * time_p

        metrics.append({
            'processors': p,
            'time': time_p,
            'speedup': speedup,
            'efficiency': efficiency,
            'overhead': overhead,
            'cost': cost
        })

    return metrics
