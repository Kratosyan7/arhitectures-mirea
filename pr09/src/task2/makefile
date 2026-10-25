# Сборка функции mytoupper в статическую библиотеку libupper.a
# и программы uppertst2 (листинг 9.17) для RISC-V
AS   = riscv64-linux-gnu-as
AR   = riscv64-linux-gnu-ar
CC   = riscv64-linux-gnu-gcc
QEMU = qemu-riscv64

LIBOBJS = upper.o

ifdef DEBUG
DEBUGFLGS = -g
else
DEBUGFLGS =
endif

all: uppertst2

%.o : %.S
	$(AS) $(DEBUGFLGS) $< -o $@

libupper.a: $(LIBOBJS)
	$(AR) -cvq libupper.a upper.o

uppertst2: uppertst.c libupper.a
	$(CC) -o uppertst2 uppertst.c libupper.a

run: uppertst2
	$(QEMU) ./uppertst2

clean:
	rm -f *.o libupper.a uppertst2

.PHONY: all run clean
