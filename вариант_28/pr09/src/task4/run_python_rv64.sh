#!/bin/bash
# Запуск RISC-V-интерпретатора Python 3.12 (пакеты Ubuntu 24.04 riscv64,
# распакованы в .tools/pyrv/root) в эмуляторе qemu-riscv64.
# Библиотеки glibc берутся из sysroot ($QEMU_LD_PREFIX), libffi/zlib/expat – из pyrv.
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
PY=$ROOT/.tools/pyrv/root
exec qemu-riscv64 -E LD_LIBRARY_PATH=$PY/usr/lib/riscv64-linux-gnu \
     $PY/usr/bin/python3.12 "$@"
