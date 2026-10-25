import matplotlib.pyplot as plt


def visualize_results(times, labels, variant_num, metrics=None,
                      save_prefix='variant', technology_type=''):
    """
    Создает графики сравнения времени выполнения и метрик производительности.

    Параметры:
    ----------
    times : list of float
        Список времен выполнения
    labels : list of str
        Список меток для каждого метода
    variant_num : int
        Номер варианта для заголовка
    metrics : list of dict, optional
        Метрики производительности из calculate_metrics()
    save_prefix : str
        Префикс для имен сохраняемых файлов
    technology_type : str
        Тип технологии ('OpenMP' или 'MPI') для отображения в заголовках
    """
    # График 1 и 2: Основное сравнение
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

    # Формирование заголовка с типом технологии
    tech_suffix = f' ({technology_type})' if technology_type else ''

    # График 1: Столбчатая диаграмма времен
    bars = ax1.bar(labels, times, color=colors, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Время выполнения (секунды)', fontsize=12)
    ax1.set_title(f'Сравнение времени выполнения (Вариант {variant_num}){tech_suffix}',
                  fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    for bar, time_val in zip(bars, times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{time_val:.4f}s',
                 ha='center', va='bottom', fontsize=10)

    # График 2: Ускорение
    speedup = [times[0] / t for t in times]
    bars2 = ax2.bar(labels, speedup, color=colors, edgecolor='black', linewidth=1.5)
    ax2.axhline(y=1, color='red', linestyle='--', label='Базовая линия')
    ax2.set_ylabel('Ускорение (раз)', fontsize=12)
    ax2.set_title('Ускорение относительно последовательной версии',
                  fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend()

    for bar, speed_val in zip(bars2, speedup):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                 f'{speed_val:.2f}x',
                 ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(f'{save_prefix}_{variant_num}_comparison.png', dpi=300)
    plt.show()

    # Дополнительная визуализация метрик
    if metrics and len(metrics) > 1:
        fig2, ((ax3, ax4), (ax5, ax6)) = plt.subplots(2, 2, figsize=(14, 10))

        processors = [m['processors'] for m in metrics]
        speedups = [m['speedup'] for m in metrics]
        efficiencies = [m['efficiency'] for m in metrics]
        overheads = [m['overhead'] for m in metrics]

        # График 3: Ускорение vs процессоры
        ax3.plot(processors, speedups, 'o-', color='#4ECDC4', linewidth=2,
                 markersize=8, label='Реальное ускорение')
        ax3.plot(processors, processors, '--', color='red', linewidth=2,
                 label='Идеальное (линейное)')
        ax3.set_xlabel('Число процессоров', fontsize=11)
        ax3.set_ylabel('Ускорение S(p)', fontsize=11)
        ax3.set_title(f'Зависимость ускорения от числа процессоров{tech_suffix}',
                      fontsize=12, fontweight='bold')
        ax3.grid(alpha=0.3)
        ax3.legend()

        # График 4: Эффективность
        ax4.plot(processors, efficiencies, 's-', color='#FF6B6B',
                 linewidth=2, markersize=8)
        ax4.axhline(y=100, color='red', linestyle='--', linewidth=2,
                    label='Идеальная (100%)')
        ax4.set_xlabel('Число процессоров', fontsize=11)
        ax4.set_ylabel('Эффективность E(p), %', fontsize=11)
        ax4.set_title(f'Зависимость эффективности от числа процессоров{tech_suffix}',
                      fontsize=12, fontweight='bold')
        ax4.grid(alpha=0.3)
        ax4.legend()

        # График 5: Избыточность
        ax5.plot(processors, overheads, '^-', color='#45B7D1',
                 linewidth=2, markersize=8)
        ax5.set_xlabel('Число процессоров', fontsize=11)
        ax5.set_ylabel('Избыточность O(p), секунды', fontsize=11)
        ax5.set_title(f'Зависимость избыточности от числа процессоров{tech_suffix}',
                      fontsize=12, fontweight='bold')
        ax5.grid(alpha=0.3)

        # График 6: Таблица метрик
        ax6.axis('tight')
        ax6.axis('off')
        table_data = [['p', 'T(p), с', 'S(p)', 'E(p), %']]
        for m in metrics:
            table_data.append([
                f"{m['processors']}",
                f"{m['time']:.3f}",
                f"{m['speedup']:.2f}",
                f"{m['efficiency']:.1f}"
            ])
        table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                          colWidths=[0.15, 0.25, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        for i in range(4):
            table[(0, i)].set_facecolor('#4ECDC4')
            table[(0, i)].set_text_props(weight='bold', color='white')

        ax6.set_title('Сводная таблица метрик', fontsize=12,
                      fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(f'{save_prefix}_{variant_num}_metrics.png', dpi=300)
        plt.show()

    print(f"\n{'='*60}")
    print(f"Результаты для варианта {variant_num}")
    print(f"{'='*60}")
    for label, t, s in zip(labels, times, speedup):
        print(f"{label:30s}: {t:.4f}s (ускорение: {s:.2f}x)")
    print(f"{'='*60}")
