"""
Проверка исправления MPI-версии: исходный листинг 11.3 против исправленной.

Запуск: mpiexec -n 6 python -m src.check_mpi_fix
"""
from .main import A, B, K, FUNCTION_TYPE, exact_integral
from .function_to_integrate import function_to_integrate
from .parallel_integration_mpi_listing import parallel_integration_mpi as listing_version
from .parallel_integration_mpi import parallel_integration_mpi as fixed_version


def main():
    exact = exact_integral(A, B, K, FUNCTION_TYPE)
    for n in (12_000_000, 12_000_001):
        r_listing, rank, size = listing_version(A, B, n, K, FUNCTION_TYPE)
        r_fixed, _, _ = fixed_version(A, B, n, K, FUNCTION_TYPE)
        if rank == 0:
            h = (B - A) / n
            print(f"size = {size}, n = {n:,}, h·f(a) = {h * function_to_integrate(A, K, FUNCTION_TYPE):.3e}")
            print(f"  листинг 11.3 : {r_listing:.12f}  ошибка {r_listing - exact:+.3e}")
            print(f"  исправленная : {r_fixed:.12f}  ошибка {r_fixed - exact:+.3e}")


if __name__ == "__main__":
    main()
