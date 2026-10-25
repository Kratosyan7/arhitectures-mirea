/*
 * Задание №2. Вариант 14 (по табл. 10.1 - вариант 2, т.к. в таблице 12
 * вариантов: 14 - 12 = 2).
 * Входная строка: "Hello World!". Задача: перевести все буквы в НИЖНИЙ
 * регистр. Реализация на C для анализа через objdump -d.
 *
 * Правило ASCII: заглавная буква 'A'..'Z' (0x41..0x5A) переводится в
 * строчную прибавлением 0x20. Прочие символы не меняются.
 */
#include <stdio.h>

int my_tolower(const char *instr, char *outstr)
{
    char cur;
    char *orig_outstr = outstr;

    do {
        cur = *instr;
        if ((cur >= 'A') && (cur <= 'Z')) {
            cur = cur + ('a' - 'A');   /* +32 */
        }
        *outstr++ = cur;
        instr++;
    } while (cur != '\0');

    return (int)(outstr - orig_outstr);
}

#ifndef NO_MAIN
char *tstStr = "Hello World!";
char outStr[64];

int main(void)
{
    my_tolower(tstStr, outStr);
    printf("Input:  %s\nOutput: %s\n", tstStr, outStr);
    return 0;
}
#endif
