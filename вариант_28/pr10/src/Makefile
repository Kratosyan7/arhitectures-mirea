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

# ---------- Задание №2: замена пробелов на подчёркивание (C + asm) ----------
task2: replspace_bench replspace_O0.s replspace_O2.s

replspace_bench: replspace_bench.c replspace.c replspace_asm.S
	$(CC) $(CFLAGS) -DNO_MAIN -o $@ $^

# ассемблерное представление C-функции при разных уровнях оптимизации
replspace_O0.s: replspace.c
	$(CC) -O0 -S -fno-asynchronous-unwind-tables -o $@ $<
replspace_O1.s: replspace.c
	$(CC) -O1 -S -fno-asynchronous-unwind-tables -o $@ $<
replspace_O2.s: replspace.c
	$(CC) -O2 -S -fno-asynchronous-unwind-tables -o $@ $<
replspace_O3.s: replspace.c
	$(CC) -O3 -S -fno-asynchronous-unwind-tables -o $@ $<

# бинарник для Ghidra (Задание №3) и дизассемблер
replspace_O2: replspace.c
	$(CC) -O2 -static -mno-relax -o $@ $<
replspace_O2.objdump: replspace_O2
	$(OBJDUMP) -d $< > $@

clean:
	rm -f bench_upper replspace_bench replspace_O? replspace_O?.s *.o \
	      replspace_O2.objdump *.csv
