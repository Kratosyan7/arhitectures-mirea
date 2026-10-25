#
# Задание №4. Листинг 10.13 - демонстрация атаки переполнения буфера
# на собственной учебной программе из методички.
#
# Обычный пользователь вызывает только calltoupper -> toupper, но из-за
# отсутствия проверки длины входной строки сохранённый в стеке адрес
# возврата ra перезаписывается адресом административной подпрограммы
# DownloadCreditCardNumbers, которая НЕ должна вызываться.
#
# Адрес для перезаписи задаётся константой OVERRIDE_ADDR (жёстко
# закодированный адрес, как в методичке). Значение подставляется ключом
# -DOVERRIDE_ADDR=0x... при сборке; найдено по дизассемблеру objdump.
#
#ifndef OVERRIDE_ADDR
#define OVERRIDE_ADDR 0x00000000000100e8
#endif

.global _start               # точка входа

DownloadCreditCardNumbers:
# Административная функция: печать "секретных" данных.
    li   a0, 1               # 1 = StdOut
    la   a1, getcreditcards  # строка для печати
    li   a2, 30              # длина строки
    li   a7, 64              # системный вызов write
    ecall                    # вывести строку
    ret

calltoupper:
    addi sp, sp, -16         # выделить 16 байт на стеке
    sd   ra, 0(sp)           # сохранить адрес возврата
    addi sp, sp, -16         # ещё 16 байт под выходной буфер outstr
    la   a0, instr           # начало входной строки
    mv   a1, sp              # адрес выходного буфера

    call toupper

aftertoupper:                # удобная метка для точки останова
    addi sp, sp, 16          # освободить outstr
    ld   ra, 0(sp)           # извлечь ra (уже подменённый!)
    addi sp, sp, 16          # освободить кадр стека
    ret

_start:
    call calltoupper

# Завершение программы.
    li   a0, 0               # код возврата 0
    li   a7, 93              # системный вызов exit
    ecall

.data
instr: .ascii "This is our Test"   # ровно 16 байт, без завершающего нуля
    .quad OVERRIDE_ADDR            # перезапись сохранённого ra
getcreditcards: .asciz "Downloading Credit Card Data!\n"
    .align 4
