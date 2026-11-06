# Сборка программы uppertst (листинг 9.15) кросс-компилятором RISC-V
CC   = riscv64-linux-gnu-gcc
QEMU = qemu-riscv64

uppertst: uppertst.c upper.S
	$(CC) -o uppertst uppertst.c upper.S

run: uppertst
	$(QEMU) ./uppertst

clean:
	rm -f uppertst

.PHONY: run clean
