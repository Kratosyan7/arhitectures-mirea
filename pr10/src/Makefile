# Makefile практической работы №10 (кросс-сборка под RISC-V).
# Требуется: source ../../.tools/env.sh
CC      = riscv64-linux-gnu-gcc
OBJDUMP = riscv64-linux-gnu-objdump
QEMU    = qemu-riscv64
CFLAGS  = -O2 -static -mno-relax

.PHONY: all task1 task2 clean

all: task1 task2

# ---------- Задание №1: сравнение версий uppercase ----------
task1: bench_upper

bench_upper: bench_upper.c toupper1.S toupper2.S toupper3.S
	$(CC) $(CFLAGS) -o $@ $^

# ---------- Задание №2: tolower (C + asm) ----------
task2: tolower_bench tolower_O0.s tolower_O2.s

tolower_bench: tolower_bench.c tolower.c tolower_asm.S
	$(CC) $(CFLAGS) -DNO_MAIN -o $@ $^

# ассемблерное представление C-функции при разных уровнях оптимизации
tolower_O0.s: tolower.c
	$(CC) -O0 -S -fno-asynchronous-unwind-tables -o $@ $<
tolower_O1.s: tolower.c
	$(CC) -O1 -S -fno-asynchronous-unwind-tables -o $@ $<
tolower_O2.s: tolower.c
	$(CC) -O2 -S -fno-asynchronous-unwind-tables -o $@ $<
tolower_O3.s: tolower.c
	$(CC) -O3 -S -fno-asynchronous-unwind-tables -o $@ $<

# бинарник для Ghidra (Задание №3) и дизассемблер
tolower_O2: tolower.c
	$(CC) -O2 -static -mno-relax -o $@ $<
tolower_O2.objdump: tolower_O2
	$(OBJDUMP) -d $< > $@

clean:
	rm -f bench_upper tolower_bench tolower_O? tolower_O?.s *.o \
	      tolower_O2.objdump *.csv
