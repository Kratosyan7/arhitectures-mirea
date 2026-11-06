/*
 * Задание №1. Общий драйвер: собирает три реализации перевода строки в
 * верхний регистр (toupper1 - ветвления, toupper2 - одно беззнаковое
 * сравнение, toupper3 - маска 0xDF без ветвлений) в один цикл и замеряет
 * время их работы через gettimeofday на большом числе итераций.
 *
 * Запуск: bench_upper <итераций> <прогонов>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

extern unsigned long toupper1(const char *in, char *out);
extern unsigned long toupper2(const char *in, char *out);
extern unsigned long toupper3(const char *in, char *out);

static double now_sec(void)
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (double)tv.tv_sec + (double)tv.tv_usec / 1e6;
}

typedef unsigned long (*upfn)(const char *, char *);

struct variant {
    const char *name;
    upfn fn;
};

int main(int argc, char **argv)
{
    long iters = (argc > 1) ? atol(argv[1]) : 3000000;
    int runs = (argc > 2) ? atoi(argv[2]) : 3;

    /* Входная строка из одних букв: все три версии делают одинаковую
     * работу и переводят её корректно -> сравнение времени честное. */
    const char *in =
        "ThisIsRatherALargeVariableNameForTheUppercaseBenchmark";
    char out[256];

    struct variant v[] = {
        { "toupper1 (2 ветвления)",      toupper1 },
        { "toupper2 (1 сравн. bgeu)",    toupper2 },
        { "toupper3 (маска 0xDF)",       toupper3 },
    };
    int nv = sizeof(v) / sizeof(v[0]);

    /* Проверка корректности на буквенной строке. */
    printf("Входная строка : %s\n", in);
    for (int i = 0; i < nv; i++) {
        memset(out, 0, sizeof(out));
        v[i].fn(in, out);
        printf("  %-26s -> %s\n", v[i].name, out);
    }
    printf("Итераций в прогоне: %ld, прогонов: %d\n\n", iters, runs);

    printf("%-28s %10s %12s %12s\n",
           "Версия", "прогон", "время, с", "нс/вызов");
    printf("--------------------------------------------------------------\n");

    /* CSV для построения графика. */
    FILE *csv = fopen("bench_upper.csv", "w");
    if (csv) fprintf(csv, "variant,best_time_s,ns_per_call\n");

    for (int i = 0; i < nv; i++) {
        double best = 1e18;
        for (int r = 0; r < runs; r++) {
            double t0 = now_sec();
            volatile unsigned long acc = 0;
            for (long k = 0; k < iters; k++)
                acc += v[i].fn(in, out);
            double dt = now_sec() - t0;
            if (dt < best) best = dt;
            printf("%-28s %10d %12.4f %12.2f\n",
                   v[i].name, r + 1, dt, dt / iters * 1e9);
        }
        if (csv)
            fprintf(csv, "%s,%.6f,%.3f\n",
                    v[i].name, best, best / iters * 1e9);
        printf("--------------------------------------------------------------\n");
    }
    if (csv) fclose(csv);
    return 0;
}
