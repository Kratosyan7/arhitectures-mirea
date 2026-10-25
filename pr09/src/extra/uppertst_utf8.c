// Сравнение mytoupper (листинг 9.8, только ASCII) и mytoupper_utf8
// (дополнительно кириллица UTF-8) на нескольких строках.
#include <stdio.h>

#define MAX_BUFFSIZE 255

extern int mytoupper(const char *in, char *out);
extern int mytoupper_utf8(const char *in, char *out);

int main()
{
    const char *tests[] = {
        "мирзоян_а_о_икбо_41_25_вариант_14",
        "This is a test.",
        "ёжик в тумане, Ёлка; abc-xyz {|}",
    };
    char out1[MAX_BUFFSIZE], out2[MAX_BUFFSIZE];

    for (int i = 0; i < 3; i++) {
        int len1 = mytoupper(tests[i], out1);
        int len2 = mytoupper_utf8(tests[i], out2);
        printf("Before str:     %s\n", tests[i]);
        printf("mytoupper:      %s (len = %d)\n", out1, len1);
        printf("mytoupper_utf8: %s (len = %d)\n\n", out2, len2);
    }
    return 0;
}
