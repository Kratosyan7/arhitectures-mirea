/*
 * Задание №3. "Восстановленный" (исправленный) код функции my_tolower,
 * полученный декомпилятором Ghidra из бинарника tolower_O2.
 *
 * Правки относительно вывода Ghidra, чтобы код компилировался и работал:
 *  - убрана строка-артефакт "gp = &__global_pointer_;" (служебный
 *    регистр global pointer, к логике не относится);
 *  - типы param_1/param_2 оставлены как char*, возврат сведён к int;
 *  - добавлены main/печать для проверки запуском.
 *
 * Логика сохранена дословно: Ghidra восстановил ОПТИМИЗИРОВАННУЮ форму
 * проверки диапазона "(byte)(c + 0xbf) < 0x1a", то есть
 * (unsigned char)(c - 'A') < 26 - одно беззнаковое сравнение вместо двух,
 * и перевод "c + ' '" (+0x20). Это та же функция, что и в tolower.c,
 * но в виде, к которому её привела оптимизация -O2.
 */
#include <stdio.h>

long my_tolower(char *param_1, char *param_2)
{
    char *pcVar1;
    char cVar2;
    int iVar3;

    iVar3 = (int)(long)param_2;
    while (1) {
        cVar2 = *param_1;
        while ((unsigned char)(cVar2 + 0xbfU) < 0x1a) {
            *param_2 = cVar2 + ' ';
            pcVar1 = param_1 + 1;
            param_2 = param_2 + 1;
            param_1 = param_1 + 1;
            cVar2 = *pcVar1;
        }
        *param_2 = cVar2;
        param_2 = param_2 + 1;
        if (cVar2 == '\0')
            break;
        param_1 = param_1 + 1;
    }
    return (long)((int)(long)param_2 - iVar3);
}

char *tstStr = "Hello World!";
char outStr[64];

int main(void)
{
    long n = my_tolower(tstStr, outStr);
    printf("Input:  %s\nOutput: %s\n(len=%ld)\n", tstStr, outStr, n);
    return 0;
}
