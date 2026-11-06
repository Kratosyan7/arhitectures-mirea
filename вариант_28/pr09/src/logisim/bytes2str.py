"""Собирает строку из таблицы check.js (столбцы c | out) и печатает вход/выход как текст UTF-8."""
import sys
rows = [l.rstrip("\n").split("\t") for l in sys.stdin if "|" in l][1:]
inp = bytes(int(r[0], 16) for r in rows)
out = bytes(int(r[-1], 16) for r in rows)
print("вход :", inp.decode("utf-8", "replace"))
print("выход:", out.decode("utf-8", "replace"))
print("изменено байт: %d из %d" % (sum(a != b for a, b in zip(inp, out)), len(inp)))
