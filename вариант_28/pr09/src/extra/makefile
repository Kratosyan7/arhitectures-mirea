# Дополнительное задание: библиотека libup8.so с mytoupper и mytoupper_utf8
AS   = riscv64-linux-gnu-as
CC   = riscv64-linux-gnu-gcc
QEMU = qemu-riscv64

all: uppertst_utf8

%.o : %.S
	$(AS) $< -o $@

libup8.so: upper.o upper_utf8.o
	$(CC) -shared -o $@ $^

uppertst_utf8: uppertst_utf8.c libup8.so
	$(CC) -o $@ uppertst_utf8.c -L. -lup8 -Wl,-rpath,'$$ORIGIN'

run: uppertst_utf8
	$(QEMU) ./uppertst_utf8
	../task4/run_python_rv64.sh uppertst_utf8.py

clean:
	rm -f *.o libup8.so uppertst_utf8

.PHONY: all run clean
