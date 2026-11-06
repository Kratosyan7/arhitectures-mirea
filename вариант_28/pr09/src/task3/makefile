# Сборка функции mytoupper в динамическую (общую) библиотеку libup.so
# и программы uppertst3 (листинг 9.19) для RISC-V.
# Отличие от пособия: прав root (sudo) нет, поэтому вместо /usr/local/lib
# библиотека устанавливается в локальный каталог lib/ рядом с программой,
# а путь к нему прописывается в программу через -Wl,-rpath,$ORIGIN/lib
# (ldconfig не нужен; $ORIGIN – каталог исполняемого файла).
AS     = riscv64-linux-gnu-as
CC     = riscv64-linux-gnu-gcc
QEMU   = qemu-riscv64
LIBDIR = lib

LIBOBJS = upper.o

all: uppertst3 uppertst4

%.o : %.S
	$(AS) $(DEBUGFLGS) $< -o $@

libup.so.1.0: $(LIBOBJS)
	$(CC) -shared -Wl,-soname,libup.so.1 -o libup.so.1.0 $(LIBOBJS)
	mkdir -p $(LIBDIR)
	mv libup.so.1.0 $(LIBDIR)
	ln -sf libup.so.1.0 $(LIBDIR)/libup.so.1
	ln -sf libup.so.1.0 $(LIBDIR)/libup.so

uppertst3: libup.so.1.0
	$(CC) -o uppertst3 uppertst.c -L$(LIBDIR) -lup -Wl,-rpath,'$$ORIGIN/lib'

# программа из листинга 9.22 (встроенный ассемблер), собирается как обычная C-программа
uppertst4: uppertst4.c
	$(CC) -o uppertst4 uppertst4.c

run: uppertst3 uppertst4
	$(QEMU) ./uppertst3
	$(QEMU) ./uppertst4

clean:
	rm -rf *.o uppertst3 uppertst4 $(LIBDIR)

.PHONY: all run clean libup.so.1.0
