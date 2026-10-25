# makefile для программы main_app (версия 2, точка входа main_app)
# make / make release – финальная версия (без отладочной информации, strip)
# make debug          – отладочная версия (-g, символы сохранены)
# make run / run-debug – запуск в эмуляторе qemu-riscv64
# make clean          – удаление результатов сборки
CROSS  ?= riscv64-linux-gnu-
AS      = $(CROSS)as
LD      = $(CROSS)ld
STRIP   = $(CROSS)strip
QEMU   ?= qemu-riscv64
GDBPORT ?= 1234
N      ?= 5

PROG    = main_app
SRC     = $(PROG).S

.PHONY: all release debug run run-debug run-head gdbserver clean

all: release

release: $(PROG)
debug:   $(PROG)_debug

# релизная сборка: объектный файл без -g, исполняемый файл после strip
$(PROG).o: $(SRC)
	$(AS) $< -o $@
$(PROG): $(PROG).o
	$(LD) -e main_app -o $@ $<
	$(STRIP) $@

# отладочная сборка: -g добавляет секции .debug_* (номера строк исходника)
$(PROG)_debug.o: $(SRC)
	$(AS) -g $< -o $@
$(PROG)_debug: $(PROG)_debug.o
	$(LD) -e main_app -o $@ $<

run: $(PROG)
	$(QEMU) ./$(PROG)
run-debug: $(PROG)_debug
	$(QEMU) ./$(PROG)_debug

clean:
	rm -f *.o $(PROG) $(PROG)_debug

# программа зациклена (j main_app), поэтому run показывает только первые N строк
run-head: $(PROG)
	timeout 2 $(QEMU) ./$(PROG) | head -n $(N)

# запуск отладочной версии под gdb-сервером qemu (подключение: target remote :$(GDBPORT))
gdbserver: $(PROG)_debug
	$(QEMU) -g $(GDBPORT) ./$(PROG)_debug
