# Вызов mytoupper_utf8 из общей библиотеки libup8.so через ctypes (RISC-V Python)
import os
from ctypes import *

lib = CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libup8.so"))
for name in ("mytoupper", "mytoupper_utf8"):
    getattr(lib, name).argtypes = [c_char_p, c_char_p]
    getattr(lib, name).restype = c_int

inStr = create_string_buffer("мирзоян_а_о_икбо_41_25_вариант_14".encode("utf-8"))
outStr = create_string_buffer(250)
length = lib.mytoupper_utf8(inStr, outStr)
print(inStr.value.decode())
print(outStr.value.decode())
print(length)
