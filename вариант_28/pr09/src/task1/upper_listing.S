# Функция на языке ассемблера для конвертации строки
# в верхний регистр (листинг 9.8 методического пособия).
#
# a1 – адрес выходной строки
# a0 – адрес входной строки
# s0 – исходный адрес выходной строки (для вычисления длины)
# t2 – текущий обрабатываемый символ
# t3 – временный регистр для сравнений
#

.global mytoupper            # Allow other files to call this routine

toupper:
      addi sp, sp, -16     # allocate 16 bytes on stack
      sd   ra, 8(sp)       # push return address
      sd   s0, 0(sp)       # push s0 register
      mv   s0, a1          # save original outstr for len calc
# The loop is until null (zero) character is encountered.
loop: lb   t2, 0(a0)       # load character
      addi a0, a0, 1       # increment buffer pointer
# If x7 > 'z' then goto cont
      li   t3, 'z'         # load 'z' for comparison
      bgt  t2, t3, cont    # branch if letter > 'z'?
# Else if x7 < 'a' then goto end if
      li   t3, 'a'         # load 'a' for comparison
      blt  t2, t3, cont    # goto to end if not lowercase
# If we got here then the letter is lower case, so convert it.
      addi t2, t2, ('A'-'a')
cont: # end if
      sb   t2, 0(a1)       # store character to output str
      addi a1, a1, 1       # increment buffer for next char
      li   t3, 0           # load 0 char for comparison
      bne  t2, t3, loop    # loop if character isn't null

      sub  a0, a1, s0      # get the len by sub'ing the pointers

      ld   s0, 0(sp)       # pop s0
      ld   ra, 8(sp)       # pop ra
      addi sp, sp, 16      # deallocate stack space
      ret                  # Return to caller
