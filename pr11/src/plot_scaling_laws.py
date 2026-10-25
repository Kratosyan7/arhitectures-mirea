import numpy as np
import matplotlib.pyplot as plt


def plot_scaling_laws(sequential_fraction, comm_overhead=0.01, max_processors=32,
                      save_path='scaling_laws_comparison.png', technology_type=''):
    """
    Строит графики законов Амдала, Густафсона и Сан-Ная.

    Параметры:
    ----------
    sequential_fraction : float
        Доля последовательного кода (α), 0 ≤ α ≤ 1
    comm_overhead : float
        Коэффициент коммуникационных издержек (β)
    max_processors : int
        Максимальное число процессоров для графика
    save_path : str
        Путь для сохранения графика
    technology_type : str
        Тип технологии ('OpenMP' или 'MPI') для отображения в заголовке

    Законы:
    -------
    1. Закон Амдала: S(p) = 1 / (f + (1-f)/p)
        - Пессимистичная модель для фиксированного размера задачи
        - Максимальное ускорение ограничено 1/f

    2. Закон Густафсона: S(p) = p - α(p - 1)
        - Оптимистичная модель для масштабируемых задач
        - Почти линейное ускорение

    3. Закон Сан-Ная: S(p) = p / (1 + α(p-1) + β√p)
        - Реалистичная модель с учетом коммуникаций
        - Учитывает накладные расходы на обмен данными
    """
    processors = np.arange(1, max_processors + 1)

    # Закон Амдала
    speedup_amdahl = 1 / (sequential_fraction + (1 - sequential_fraction) / processors)

    # Закон Густафсона
    speedup_gustafson = processors - sequential_fraction * (processors - 1)

    # Закон Сан-Ная
    speedup_sunni = processors / (1 + sequential_fraction * (processors - 1) +
                                  comm_overhead * np.sqrt(processors))

    # Идеальное линейное ускорение
    speedup_ideal = processors

    # Построение графика
    plt.figure(figsize=(12, 7))
    plt.plot(processors, speedup_ideal, 'k--', linewidth=2.5,
             label='Идеальное ускорение (линейное)', alpha=0.7)
    plt.plot(processors, speedup_amdahl, 'r-', linewidth=2.5,
             label=f'Закон Амдала (α={sequential_fraction:.3f})', marker='o', markersize=4)
    plt.plot(processors, speedup_gustafson, 'g-', linewidth=2.5,
             label=f'Закон Густафсона (α={sequential_fraction:.3f})', marker='s', markersize=4)
    plt.plot(processors, speedup_sunni, 'b-', linewidth=2.5,
             label=f'Закон Сан-Ная (α={sequential_fraction:.3f}, β={comm_overhead})',
             marker='^', markersize=4)

    # Формирование заголовка с типом технологии
    tech_suffix = f' ({technology_type})' if technology_type else ''

    plt.xlabel('Число процессоров (p)', fontsize=13, fontweight='bold')
    plt.ylabel('Ускорение S(p)', fontsize=13, fontweight='bold')
    plt.title(f'Сравнение законов масштабируемости параллельных вычислений{tech_suffix}',
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11, loc='upper left')

    # Добавляем аннотации для ключевых точек
    p_16 = 15  # индекс для 16 процессоров
    if p_16 < len(processors):
        plt.annotate(f'Амдал: {speedup_amdahl[p_16]:.1f}x',
                     xy=(processors[p_16], speedup_amdahl[p_16]),
                     xytext=(processors[p_16] + 3, speedup_amdahl[p_16] - 2),
                     fontsize=9, color='red',
                     arrowprops=dict(arrowstyle='->', color='red', lw=1))
        plt.annotate(f'Густафсон: {speedup_gustafson[p_16]:.1f}x',
                     xy=(processors[p_16], speedup_gustafson[p_16]),
                     xytext=(processors[p_16] - 8, speedup_gustafson[p_16] + 2),
                     fontsize=9, color='green',
                     arrowprops=dict(arrowstyle='->', color='green', lw=1))

    # Добавляем информацию о пределах
    max_amdahl = 1 / sequential_fraction
    y_top = min(max_processors + 5, max(speedup_gustafson) + 5)
    plt.axhline(y=max_amdahl, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
    # Если предел Амдала выше области графика (малая α), подпись ставим у верхней
    # границы, иначе текст уходит за пределы осей и ломает компоновку рисунка
    plt.text(max_processors * 0.7, min(max_amdahl + 1, y_top - 2),
             f'Предел Амдала: {max_amdahl:.1f}x',
             fontsize=10, color='red', fontweight='bold')
    plt.xlim(1, max_processors)
    plt.ylim(0, y_top)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"График законов масштабируемости сохранен: {save_path}")

    return {
        'amdahl': speedup_amdahl[-1],
        'gustafson': speedup_gustafson[-1],
        'sunni': speedup_sunni[-1],
        'ideal': speedup_ideal[-1],
        'max_amdahl': max_amdahl
    }
