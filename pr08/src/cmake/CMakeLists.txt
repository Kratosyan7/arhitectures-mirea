cmake_minimum_required(VERSION 3.16)
# Кросс-сборка под RISC-V: компилятор задаётся до project()
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR riscv64)
set(CMAKE_ASM_COMPILER riscv64-linux-gnu-gcc)
project(hello_world ASM)
# Добавляем исполняемый файл из исходника на ассемблере
add_executable(hello_world hello_world.S)
# Указать линкеру не использовать стандартные стартовые файлы и библиотеку C
target_link_options(hello_world PRIVATE -nostartfiles -nostdlib -static)
# Release – без отладочной информации и со strip (-s), Debug – с -g
set(CMAKE_ASM_FLAGS_DEBUG "-g")
set(CMAKE_ASM_FLAGS_RELEASE "")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "-s")
