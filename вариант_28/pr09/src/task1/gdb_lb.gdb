# Отладка mytoupper: почему кириллица не переводится в верхний регистр
set trace-commands on
set pagination off
set debuginfod enabled off
set sysroot ../../../.tools/root/usr/riscv64-linux-gnu
target remote :1235
break mytoupper
continue
x/s $a0
x/4xb $a0
stepi 5
x/i $pc
info registers t2
stepi 3
x/2i $pc
stepi 2
info registers t2 pc
x/i $pc
kill
