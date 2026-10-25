# Сценарий пошаговой отладки main_app_debug в gdb-multiarch
# (qemu-riscv64 запущен с gdb-сервером: qemu-riscv64 -g 1234 ./main_app_debug)
set trace-commands on
set pagination off
target remote :1234
info registers pc
break main_app
disassemble main_app
info registers
stepi
info registers a0 pc
stepi
info registers a1 pc
stepi
info registers a1 pc
x/s $a1
x/8xb $a1
x/4xg $sp
stepi
info registers a2 pc
stepi
info registers a7 pc
x/i $pc
stepi
info registers a0 pc
x/i $pc
stepi
info registers pc
x/i $pc
continue
info registers a0 a1 a2 a7 pc
info breakpoints
kill
