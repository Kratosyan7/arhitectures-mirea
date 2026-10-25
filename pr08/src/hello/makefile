# makefile для программы hello_world (версия 1, точка входа _start)
# make / make release – финальная версия (без отладочной информации, strip)
# make debug          – отладочная версия (-g, символы сохранены)
# make run / run-debug – запуск в эмуляторе qemu-riscv64
# make clean          – удаление результатов сборки
CROSS  ?= riscv64-linux-gnu-
AS      = $(CROSS)as
LD      = $(CROSS)ld
STRIP   = $(CROSS)strip
QEMU   ?= qemu-riscv64

PROG    = hello_world
SRC     = $(PROG).S

.PHONY: all release debug run run-debug clean

all: release

release: $(PROG)
debug:   $(PROG)_debug

# релизная сборка: объектный файл без -g, исполняемый файл после strip
$(PROG).o: $(SRC)
	$(AS) $< -o $@
$(PROG): $(PROG).o
	$(LD) -o $@ $<
	$(STRIP) $@

# отладочная сборка: -g добавляет секции .debug_* (номера строк исходника)
$(PROG)_debug.o: $(SRC)
	$(AS) -g $< -o $@
$(PROG)_debug: $(PROG)_debug.o
	$(LD) -o $@ $<

run: $(PROG)
	$(QEMU) ./$(PROG)
run-debug: $(PROG)_debug
	$(QEMU) ./$(PROG)_debug

clean:
	rm -f *.o $(PROG) $(PROG)_debug
