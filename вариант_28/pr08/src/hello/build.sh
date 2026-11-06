#!/bin/bash
# Файл сборки проекта (аналог листинга 8.5) для кросс-тулчейна RISC-V
riscv64-linux-gnu-as -o hello_world.o hello_world.S
riscv64-linux-gnu-ld -o hello_world hello_world.o
