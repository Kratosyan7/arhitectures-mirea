#!/bin/bash
# Загрузка и распаковка RISC-V-сборки Python 3.12 из архива Ubuntu (ports.ubuntu.com)
# без root-прав: пакеты .deb скачиваются напрямую и распаковываются dpkg-deb -x.
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
DST=$ROOT/.tools/pyrv; mkdir -p $DST/debs $DST/root; cd $DST/debs
M=https://ports.ubuntu.com/ubuntu-ports/pool/main
for f in p/python3.12/python3.12-minimal_3.12.3-1ubuntu0.17_riscv64.deb \
         p/python3.12/libpython3.12-minimal_3.12.3-1ubuntu0.17_riscv64.deb \
         p/python3.12/libpython3.12-stdlib_3.12.3-1ubuntu0.17_riscv64.deb \
         libf/libffi/libffi8_3.4.6-1build1_riscv64.deb \
         z/zlib/zlib1g_1.3.dfsg-3.1ubuntu2.3_riscv64.deb \
         e/expat/libexpat1_2.6.1-2ubuntu0.6_riscv64.deb; do
  curl -sSO $M/$f
  dpkg-deb -x $(basename $f) ../root
done
ls -l $DST/debs
