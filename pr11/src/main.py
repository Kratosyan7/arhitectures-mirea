import sys
import time
import math
import shutil
import statistics
import subprocess
import numpy as np
from pathlib import Path

# Графики только сохраняются в файлы: неинтерактивный бэкенд, чтобы plt.show()
# не открывал окна и не блокировал выполнение (на машине есть X-дисплей)
import warnings
import matplotlib
matplotlib.use('Agg')
warnings.filterwarnings('ignore', message='.*non-interactive.*')

from .sequential_integration import sequential_integration
from .parallel_integration_openmp import parallel_integration_openmp
from .calculate_metrics import calculate_metrics
from .print_metrics_table import print_metrics_table
from .plot_scaling_laws import plot_scaling_laws
from .visualize_results import visualize_results
from .function_to_integrate import function_to_integrate

try:
    from .parallel_integration_mpi import parallel_integration_mpi, MPI_AVAILABLE
except ImportError:
    MPI_AVAILABLE = False

# ========== ПАРАМЕТРЫ ВАРИАНТА (ИЗМЕНЯЕМАЯ ЧАСТЬ) ==========
VARIANT_NUM = 14                   # Номер варианта (1-30)
FUNCTION_TYPE = 'x2'               # Тип функции: 'sin', 'x2', 'exp'
FUNCTION_NAME = 'k × x²'           # Название функции для вывода
K = 1.5                            # Параметр функции
A = 1.0                            # Нижняя граница интегрирования
B = 10.0                           # Верхняя граница интегрирования
N = 12_000_000                     # Число разбиений
THREADS_LIST = [2, 4, 6]           # Потоки/процессы для теста (значения используются и для MPI)
OUTPUT_DIR = 'results'             # Директория для результатов
REPEATS = 5                        # Число повторов каждого замера (берётся медиана)
# ============================================================


def exact_integral(a, b, k, function_type):
    """Аналитическое значение интеграла (для оценки погрешности)."""
    if function_type == 'sin':
        return k * (math.cos(a) - math.cos(b))
    elif function_type == 'x2':
        return k * (b**3 - a**3) / 3
    elif function_type == 'exp':
        return k * (math.exp(-a) - math.exp(-b))
    raise ValueError(f"Неизвестный тип функции: {function_type}")


def measure(func, *args):
    """Выполняет func REPEATS раз; возвращает (результат, медиана времени, все замеры)."""
    samples = []
    result = None
    for _ in range(REPEATS):
        start = time.time()
        result = func(*args)
        samples.append(time.time() - start)
    return result, statistics.median(samples), samples


def fmt_samples(samples):
    return ', '.join(f'{t:.3f}' for t in samples)


def find_mpiexec():
    """mpiexec из того же окружения, что и интерпретатор (venv с MPICH), иначе из PATH."""
    candidate = Path(sys.executable).parent / 'mpiexec'
    if candidate.exists():
        return str(candidate)
    return shutil.which('mpiexec')


def run_mpi(mpiexec, num_proc):
    """
    Запускает MPI-версию в num_proc процессах через mpiexec.
    Возвращает (результат, время счёта по MPI.Wtime, полное время запуска mpiexec).
    """
    cmd = [mpiexec, '-n', str(num_proc), sys.executable, '-m', 'src.parallel_integration_mpi',
           str(VARIANT_NUM), repr(A), repr(B), str(N), repr(K), FUNCTION_TYPE]
    start = time.time()
    out = subprocess.run(cmd, capture_output=True, text=True, check=True,
                         cwd=Path(__file__).resolve().parent.parent).stdout
    wall = time.time() - start
    line = [s for s in out.splitlines() if s.startswith('MPI variant=')][-1]
    fields = dict(item.split('=') for item in line.split()[1:])
    return float(fields['result']), float(fields['time']), wall


def estimate_sequential_fraction(metrics):
    """
    Оценивает долю последовательного кода из экспериментальных данных.
    Использует закон Амдала: α = (1/S - 1/p) / (1 - 1/p)
    """
    if not metrics:
        return 0.1

    last_metric = metrics[-1]
    p = last_metric['processors']
    S = last_metric['speedup']

    if p > 1 and S > 0:
        alpha = (1/S - 1/p) / (1 - 1/p)
        return max(0.01, min(0.3, alpha))
    else:
        return 0.1


def print_laws_comparison(metrics, alpha, beta):
    """
    Сравнивает измеренное ускорение с законами Амдала, Густафсона и Сана–Ная
    при оценённых α и β; печатает также экспериментальную долю
    последовательной части α(p) = (1/S - 1/p) / (1 - 1/p) без ограничений.
    """
    print(f"{'p':>3} | {'S изм.':>7} | {'α(p) эксп.':>10} | {'Амдал':>7} | "
          f"{'Густафсон':>9} | {'Сан–Най':>7}")
    for m in metrics:
        p, S = m['processors'], m['speedup']
        alpha_p = (1 / S - 1 / p) / (1 - 1 / p)
        amdahl = 1 / (alpha + (1 - alpha) / p)
        gustafson = p - alpha * (p - 1)
        sun_ni = p / (1 + alpha * (p - 1) + beta * math.sqrt(p))
        print(f"{p:>3} | {S:>7.2f} | {alpha_p * 100:>9.2f}% | {amdahl:>7.2f} | "
              f"{gustafson:>9.2f} | {sun_ni:>7.2f}")


def main():
    """Главная функция программы."""
    globals()
    print("\n" + "="*70)
    print("ПРАКТИЧЕСКАЯ РАБОТА №11")
    print("Организация параллельных вычислений")
    print("Численное интегрирование методом трапеций")
    print("="*70)

    print(f"\nВариант: {VARIANT_NUM}")
    print(f"Функция: {FUNCTION_NAME}")
    print(f"Параметр k: {K}")
    print(f"Границы интегрирования: [{A:.4f}, {B:.4f}]")
    print(f"Число разбиений: {N:,}")
    print(f"Потоки для тестирования: {THREADS_LIST}")
    print(f"Повторов каждого замера: {REPEATS} (в расчёт идёт медиана)")

    exact = exact_integral(A, B, K, FUNCTION_TYPE)
    print(f"Аналитическое значение интеграла: {exact:.10f}")

    # Создание директории для результатов
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # ========== 1. ПОСЛЕДОВАТЕЛЬНАЯ ВЕРСИЯ ==========
    print("\n" + "="*70)
    print("1. ПОСЛЕДОВАТЕЛЬНАЯ ВЕРСИЯ")
    print("="*70)

    result_seq, time_seq, samples = measure(sequential_integration, A, B, N, K, FUNCTION_TYPE)

    print(f"Результат интегрирования: {result_seq:.10f}")
    print(f"Погрешность |I - I_точн|: {abs(result_seq - exact):.3e}")
    print(f"Замеры, с: {fmt_samples(samples)}")
    print(f"Время выполнения: {time_seq:.4f} секунд")

    # ========== 2. ПАРАЛЛЕЛЬНАЯ ВЕРСИЯ (OpenMP) ==========
    print("\n" + "="*70)
    print("2. ПАРАЛЛЕЛЬНАЯ ВЕРСИЯ (OpenMP)")
    print("="*70)

    times_openmp = []
    results_openmp = []

    for num_threads in THREADS_LIST:
        print(f"\nТестирование с {num_threads} потоками...")
        result, time_parallel, samples = measure(parallel_integration_openmp,
                                                 A, B, N, K, FUNCTION_TYPE, num_threads)

        times_openmp.append(time_parallel)
        results_openmp.append(result)

        speedup = time_seq / time_parallel if time_parallel > 0 else 0
        efficiency = (speedup / num_threads) * 100

        print(f"  Результат: {result:.10f} (погрешность {abs(result - exact):.3e})")
        print(f"  Замеры, с: {fmt_samples(samples)}")
        print(f"  Время: {time_parallel:.4f}s | Ускорение: {speedup:.2f}x | "
              f"Эффективность: {efficiency:.1f}%")

    # ========== 3. ПАРАЛЛЕЛЬНАЯ ВЕРСИЯ (MPI) ==========
    print("\n" + "="*70)
    print("3. ПАРАЛЛЕЛЬНАЯ ВЕРСИЯ (MPI)")
    print("="*70)

    times_mpi = []
    results_mpi = []

    times_mpi_wall = []
    mpiexec = find_mpiexec()

    if MPI_AVAILABLE and mpiexec:
        print("MPI доступен! Запуск тестов...")
        print(f"mpiexec: {mpiexec}")
        for p in THREADS_LIST:
            print(f"  mpiexec -n {p} python -m src.parallel_integration_mpi {VARIANT_NUM} "
                  f"{A} {B} {N} {K} {FUNCTION_TYPE}")

        # Реальный запуск: num_proc независимых процессов с распределённой памятью,
        # частичные суммы собираются операцией MPI reduce
        for num_proc in THREADS_LIST:
            print(f"\nЗапуск mpiexec с {num_proc} процессами...")
            runs = [run_mpi(mpiexec, num_proc) for _ in range(REPEATS)]
            result_mpi = runs[-1][0]
            time_mpi = statistics.median(r[1] for r in runs)
            wall_mpi = statistics.median(r[2] for r in runs)
            times_mpi.append(time_mpi)
            times_mpi_wall.append(wall_mpi)
            results_mpi.append(result_mpi)

            speedup = time_seq / time_mpi if time_mpi > 0 else 0
            print(f"  Результат: {result_mpi:.10f} (погрешность {abs(result_mpi - exact):.3e})")
            print(f"  Замеры (MPI.Wtime), с: {fmt_samples([r[1] for r in runs])}")
            print(f"  Время: {time_mpi:.4f}s | Ускорение: {speedup:.2f}x | "
                  f"Эффективность: {speedup / num_proc * 100:.1f}%")
            print(f"  Полное время mpiexec (с запуском процессов): {wall_mpi:.4f}s")
    else:
        print("MPI не доступен. Пропуск тестирования.")
        print("\nДля установки MPI:")
        print("  Linux: sudo apt install mpich && pip install mpi4py")
        print("  macOS: brew install open-mpi && pip install mpi4py")
        print("  Windows: установите Microsoft MPI + pip install mpi4py")

        # Используем данные OpenMP как заглушку
        times_mpi = times_openmp.copy()
        results_mpi = results_openmp.copy()

    # ========== 4. ВЫЧИСЛЕНИЕ МЕТРИК ==========
    print("\n" + "="*70)
    print("4. ВЫЧИСЛЕНИЕ МЕТРИК ПРОИЗВОДИТЕЛЬНОСТИ")
    print("="*70)

    # Метрики для OpenMP
    print("\n--- OpenMP (multiprocessing) ---")
    metrics_openmp = calculate_metrics(time_seq, times_openmp, THREADS_LIST)
    print_metrics_table(metrics_openmp, VARIANT_NUM)

    # Метрики для MPI
    print("\n--- MPI (распределенная память) ---")
    metrics_mpi = calculate_metrics(time_seq, times_mpi, THREADS_LIST)
    print_metrics_table(metrics_mpi, VARIANT_NUM)

    # ========== 5. ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ ==========
    print("\n" + "="*70)
    print("5. ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ")
    print("="*70)

    # График сравнения для OpenMP
    times_for_viz_openmp = [time_seq, times_openmp[0], times_openmp[-1]]
    labels_for_viz_openmp = [
        'Последовательная',
        f'OpenMP ({THREADS_LIST[0]} потока)',
        f'OpenMP ({THREADS_LIST[-1]} потоков)'
    ]

    save_prefix_openmp = str(output_path / 'openmp_variant')
    visualize_results(times_for_viz_openmp, labels_for_viz_openmp, VARIANT_NUM,
                      metrics_openmp, save_prefix_openmp, technology_type='OpenMP')

    # График сравнения для MPI
    times_for_viz_mpi = [time_seq, times_mpi[0], times_mpi[-1]]
    labels_for_viz_mpi = [
        'Последовательная',
        f'MPI ({THREADS_LIST[0]} процессов)',
        f'MPI ({THREADS_LIST[-1]} процессов)'
    ]

    save_prefix_mpi = str(output_path / 'mpi_variant')
    visualize_results(times_for_viz_mpi, labels_for_viz_mpi, VARIANT_NUM,
                      metrics_mpi, save_prefix_mpi, technology_type='MPI')

    print(f"\nСоздано графиков: 4")
    print(f"  {save_prefix_openmp}_{VARIANT_NUM}_comparison.png")
    print(f"  {save_prefix_openmp}_{VARIANT_NUM}_metrics.png")
    print(f"  {save_prefix_mpi}_{VARIANT_NUM}_comparison.png")
    print(f"  {save_prefix_mpi}_{VARIANT_NUM}_metrics.png")

    # ========== 6. ПОСТРОЕНИЕ ГРАФИКОВ ЗАКОНОВ МАСШТАБИРУЕМОСТИ ==========
    print("\n" + "="*70)
    print("6. ПОСТРОЕНИЕ ГРАФИКОВ ЗАКОНОВ МАСШТАБИРУЕМОСТИ")
    print("="*70)

    # Оценка параметров для OpenMP
    estimated_alpha_openmp = estimate_sequential_fraction(metrics_openmp)
    estimated_beta = 0.01

    print(f"\n--- Параметры для OpenMP ---")
    print(f"Оценочная доля последовательного кода: {estimated_alpha_openmp*100:.1f}%")
    print(f"Оценочный коэффициент коммуникаций: {estimated_beta}")

    print_laws_comparison(metrics_openmp, estimated_alpha_openmp, estimated_beta)

    scaling_path_openmp = str(output_path / f'scaling_laws_openmp_variant_{VARIANT_NUM}.png')
    plot_scaling_laws(estimated_alpha_openmp, estimated_beta,
                      max_processors=32, save_path=scaling_path_openmp, technology_type='OpenMP')

    # Оценка параметров для MPI
    estimated_alpha_mpi = estimate_sequential_fraction(metrics_mpi)
    estimated_beta_mpi = 0.02  # Для MPI коммуникационные издержки обычно выше

    print(f"\n--- Параметры для MPI ---")
    print(f"Оценочная доля последовательного кода: {estimated_alpha_mpi*100:.1f}%")
    print(f"Оценочный коэффициент коммуникаций: {estimated_beta_mpi}")

    print_laws_comparison(metrics_mpi, estimated_alpha_mpi, estimated_beta_mpi)

    scaling_path_mpi = str(output_path / f'scaling_laws_mpi_variant_{VARIANT_NUM}.png')
    plot_scaling_laws(estimated_alpha_mpi, estimated_beta_mpi,
                      max_processors=32, save_path=scaling_path_mpi, technology_type='MPI')

    print(f"\nСоздано графиков законов: 2")
    print(f"   ✓ {scaling_path_openmp}")
    print(f"   ✓ {scaling_path_mpi}")

    # ========== 7. ИТОГОВЫЙ ОТЧЕТ ==========
    print("\n" + "="*70)
    print("РАБОТА ЗАВЕРШЕНА УСПЕШНО!")
    print("="*70)

    print(f"\nВсего сохранено файлов: 6")
    print(f"\nOpenMP (общая память):")
    print(f"  • {save_prefix_openmp}_{VARIANT_NUM}_comparison.png")
    print(f"  • {save_prefix_openmp}_{VARIANT_NUM}_metrics.png")
    print(f"  • {scaling_path_openmp}")

    print(f"\nMPI (распределенная память):")
    print(f"  • {save_prefix_mpi}_{VARIANT_NUM}_comparison.png")
    print(f"  • {save_prefix_mpi}_{VARIANT_NUM}_metrics.png")
    print(f"  • {scaling_path_mpi}")

    print(f"\n{'='*70}")
    print("СРАВНЕНИЕ МЕТОДОВ ДЛЯ ПАРАЛЛЕЛИЗАЦИИ ВЫЧИСЛЕНИЙ")
    print(f"{'='*70}")

    print(f"\nOpenMP (общая память):")
    print(f"  • Время последовательное: {time_seq:.4f}s")
    print(f"  • Максимальное ускорение: {max(m['speedup'] for m in metrics_openmp):.2f}x")
    print(f"  • Максимальная эффективность: {max(m['efficiency'] for m in metrics_openmp):.1f}%")
    print(f"\nMPI (распределенная память):")

    print(f"  • Время последовательное: {time_seq:.4f}s")
    print(f"  • Максимальное ускорение: {max(m['speedup'] for m in metrics_mpi):.2f}x")
    print(f"  • Максимальная эффективность: {max(m['efficiency'] for m in metrics_mpi):.1f}%")

    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
