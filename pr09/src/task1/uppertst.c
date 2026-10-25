//
// Программа на C для вызова функции mytoupper на ассемблере
// (листинг 9.14 методического пособия, вариант 14)
//
#include <stdio.h>

#define MAX_BUFFSIZE 255

extern int mytoupper(const char *in, char *out);

int main()
{
    char *str = "мирзоян_а_о_икбо_41_25_вариант_14";
    char outBuf[MAX_BUFFSIZE];
    int len;

    len = mytoupper( str, outBuf );
    printf("Before str: %s\n", str);
    printf("After str: %s\n", outBuf);
    printf("Str len = %d\n", len);
    return(0);
}
