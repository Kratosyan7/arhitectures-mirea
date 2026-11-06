/*
 * Задание №2. Вариант 28 (по табл. 10.1 — вариант 4, т.к. в таблице 12
 * вариантов: 28 − 12 − 12 = 4).
 * Входная строка: "Lab Work 5". Задача: заменить все пробелы на '_'.
 * Реализация на C для анализа через objdump -d.
 *
 * Правило: символ пробела ' ' (0x20) заменяется на '_' (0x5F). Прочие
 * символы не меняются.
 */
#include <stdio.h>

int my_replspace(const char *instr, char *outstr)
{
    char cur;
    char *orig_outstr = outstr;

    do {
        cur = *instr;
        if (cur == ' ') {
            cur = '_';                 /* 0x20 -> 0x5F */
        }
        *outstr++ = cur;
        instr++;
    } while (cur != '\0');

    return (int)(outstr - orig_outstr);
}

#ifndef NO_MAIN
char *tstStr = "Lab Work 5";
char outStr[64];

int main(void)
{
    my_replspace(tstStr, outStr);
    printf("Input:  %s\nOutput: %s\n", tstStr, outStr);
    return 0;
}
#endif
