# Вызов функции mytoupper на ассемблере из Python через ctypes
# (листинг 9.23 методического пособия, вариант 14).
# Скрипт выполняется RISC-V-сборкой интерпретатора python3.12 под qemu-riscv64.
import os
from ctypes import *

# Загрузка общей библиотеки, собранной в задании 3
# (в пособии – /usr/local/lib/libup.so; у нас она лежит в ../task3/lib)
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "task3", "lib", "libup.so")
libupper = CDLL(LIB)

# Определение типов аргументов и возвращаемого значения
libupper.mytoupper.argtypes = [c_char_p, c_char_p]
libupper.mytoupper.restype = c_int

# Подготовка входных и выходных буферов
# (литерал b"..." может содержать только ASCII, поэтому кириллическая
#  строка явно кодируется в байты UTF-8)
inStr = create_string_buffer("мирзоян_а_о_икбо_41_25_вариант_14".encode("utf-8"))
outStr = create_string_buffer(250)

# Вызов функции
length = libupper.mytoupper(inStr, outStr)

# Вывод результата
print(inStr.value.decode())
print(outStr.value.decode())
print(length)
