/*
 * Задание №2. Проверка и замер времени: C-реализация my_tolower против
 * двух ассемблерных (tolower_branch, tolower_nobranch) на строке
 * "Hello World!". Сравнение результата и времени работы.
 *
 * Запуск: tolower_bench <итераций> <прогонов>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

extern int my_tolower(const char *in, char *out);
extern unsigned long tolower_branch(const char *in, char *out);
extern unsigned long tolower_nobranch(const char *in, char *out);

static double now_sec(void)
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (double)tv.tv_sec + (double)tv.tv_usec / 1e6;
}

/* Обёртка над C-функцией под общий тип (int -> unsigned long). */
static unsigned long c_wrap(const char *in, char *out)
{
    return (unsigned long)my_tolower(in, out);
}

typedef unsigned long (*fn_t)(const char *, char *);

int main(int argc, char **argv)
{
    long iters = (argc > 1) ? atol(argv[1]) : 5000000;
    int runs = (argc > 2) ? atoi(argv[2]) : 3;

    const char *in = "Hello World!";
    char out[64];

    struct { const char *name; fn_t fn; } v[] = {
        { "my_tolower (C)",          c_wrap },
        { "tolower_branch (asm)",    tolower_branch },
        { "tolower_nobranch (asm)",  tolower_nobranch },
    };
    int nv = sizeof(v) / sizeof(v[0]);

    printf("Входная строка : \"%s\"\n", in);
    for (int i = 0; i < nv; i++) {
        memset(out, 0, sizeof(out));
        v[i].fn(in, out);
        printf("  %-24s -> \"%s\"\n", v[i].name, out);
    }
    printf("Итераций в прогоне: %ld, прогонов: %d\n\n", iters, runs);

    printf("%-24s %8s %12s %12s\n", "Реализация", "прогон", "время, с", "нс/вызов");
    printf("----------------------------------------------------------\n");

    FILE *csv = fopen("tolower_bench.csv", "w");
    if (csv) fprintf(csv, "impl,best_time_s,ns_per_call\n");

    for (int i = 0; i < nv; i++) {
        double best = 1e18;
        for (int r = 0; r < runs; r++) {
            double t0 = now_sec();
            volatile unsigned long acc = 0;
            for (long k = 0; k < iters; k++)
                acc += v[i].fn(in, out);
            double dt = now_sec() - t0;
            if (dt < best) best = dt;
            printf("%-24s %8d %12.4f %12.2f\n",
                   v[i].name, r + 1, dt, dt / iters * 1e9);
        }
        if (csv)
            fprintf(csv, "%s,%.6f,%.3f\n", v[i].name, best, best / iters * 1e9);
        printf("----------------------------------------------------------\n");
    }
    if (csv) fclose(csv);
    return 0;
}
