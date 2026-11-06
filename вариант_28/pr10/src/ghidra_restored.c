/*
 * Задание №3. "Восстановленный" (исправленный) код функции my_replspace,
 * полученный декомпилятором Ghidra из бинарника replspace_O2.
 *
 * Правки относительно вывода Ghidra, чтобы код компилировался и работал:
 *  - убрана строка-артефакт "gp = &__global_pointer_;" (служебный
 *    регистр global pointer, к логике не относится);
 *  - типы param_1/param_2 оставлены как char*, возврат сведён к int;
 *  - добавлены main/печать для проверки запуском.
 *
 * Логика сохранена дословно: Ghidra восстановил исходную проверку
 * "if (cVar1 != ' ')" и замену на '_' (*pcVar2 = '_'). Это та же функция,
 * что и в replspace.c: пробел (0x20) заменяется на '_' (0x5F), прочие
 * символы копируются без изменений.
 */
#include <stdio.h>

long my_replspace(char *param_1, char *param_2)
{
    char cVar1;
    char *pcVar2;

    pcVar2 = param_2;
    do {
        while (1) {
            cVar1 = *param_1;
            if (cVar1 != ' ')
                break;
            param_1 = param_1 + 1;
            *pcVar2 = '_';
            pcVar2 = pcVar2 + 1;
        }
        *pcVar2 = cVar1;
        param_1 = param_1 + 1;
        pcVar2 = pcVar2 + 1;
    } while (cVar1 != '\0');
    return (long)((int)(long)pcVar2 - (int)(long)param_2);
}

char *tstStr = "Lab Work 5";
char outStr[64];

int main(void)
{
    long n = my_replspace(tstStr, outStr);
    printf("Input:  %s\nOutput: %s\n(len=%ld)\n", tstStr, outStr, n);
    return 0;
}
