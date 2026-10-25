def print_metrics_table(metrics, variant_num):
    """
    Выводит красиво отформатированную таблицу с метриками производительности.

    Параметры:
    ----------
    metrics : list of dict
        Список метрик, полученный из calculate_metrics()
    variant_num : int
        Номер варианта задания

    Вывод:
    ------
    Таблица с колонками:
    - Процессоры (p)
    - Время (Tp)
    - Ускорение (S(p))
    - Эффективность (E(p), %)
    - Избыточность (O(p), с)
    - Стоимость (C(p))

    Дополнительный анализ:
    - Максимальное ускорение
    - Максимальная эффективность
    - Оценка масштабируемости
    """
    print("\n" + "="*95)
    print(f"ТАБЛИЦА МЕТРИК ПРОИЗВОДИТЕЛЬНОСТИ (Вариант {variant_num})")
    print("="*95)

    # Заголовок таблицы
    print(f"{'Процессоры':^12} | {'Время (с)':^12} | {'Ускорение':^12} | "
          f"{'Эффективность':^15} | {'Избыточность':^15} | {'Стоимость':^12}")
    print(f"{'p':^12} | {'Tp':^12} | {'S(p)':^12} | {'E(p), %':^15} | "
          f"{'O(p), с':^15} | {'C(p)':^12}")
    print("-"*95)

    # Строки с данными
    for m in metrics:
        print(f"{m['processors']:^12} | {m['time']:^12.4f} | {m['speedup']:^12.2f} | "
              f"{m['efficiency']:^15.1f} | {m['overhead']:^15.4f} | {m['cost']:^12.4f}")

    print("="*95)

    # Дополнительный анализ
    print("\nАНАЛИЗ РЕЗУЛЬТАТОВ:")

    # Находим максимумы
    best_speedup = max(metrics, key=lambda x: x['speedup'])
    best_efficiency = max(metrics, key=lambda x: x['efficiency'])

    print(f"• Максимальное ускорение: {best_speedup['speedup']:.2f}x "
          f"на {best_speedup['processors']} процессорах")
    print(f"• Максимальная эффективность: {best_efficiency['efficiency']:.1f}% "
          f"на {best_efficiency['processors']} процессорах")

    # Оценка масштабируемости
    if len(metrics) >= 2:
        scaling_factor = metrics[-1]['speedup'] / metrics[0]['speedup']
        proc_increase = metrics[-1]['processors'] / metrics[0]['processors']

        print(f"• Масштабируемость: при увеличении процессоров в {proc_increase:.0f} раз, "
              f"ускорение выросло в {scaling_factor:.2f} раз")

        # Классификация масштабируемости
        scaling_quality = scaling_factor / proc_increase
        if scaling_quality > 0.7:
            status = "Хорошая масштабируемость"
        elif scaling_quality > 0.4:
            status = "Умеренная масштабируемость"
        else:
            status = "Слабая масштабируемость"
        print(f"  {status} (коэффициент: {scaling_quality:.2f})")

    # Оценка эффективности использования ресурсов
    avg_efficiency = sum(m['efficiency'] for m in metrics) / len(metrics)
    print(f"• Средняя эффективность использования процессоров: {avg_efficiency:.1f}%")

    if avg_efficiency > 80:
        print("  Отличное использование ресурсов")
    elif avg_efficiency > 60:
        print("  Хорошее использование ресурсов")
    else:
        print("  Требуется оптимизация")

    print("="*95)
