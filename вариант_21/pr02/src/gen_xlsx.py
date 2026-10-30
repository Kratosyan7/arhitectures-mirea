"""Excel для ПР2 (вариант 21): таблицы дешифратора 4→16, JK-триггера и счётчика (строка 22)."""
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import counter_model as cm  # noqa: E402

OUT = os.path.join(HERE, "..", "Практика_2_вариант_21.xlsx")
HEAD = PatternFill("solid", fgColor="DDEBF7")
HL = PatternFill("solid", fgColor="E2EFDA")       # активная строка/значение
BORD = Border(*[Side(style="thin")] * 4)
CEN = Alignment(horizontal="center", vertical="center")


def cell(ws, coord, val, fill=None, bold=False):
    c = ws[coord]
    c.value = val
    if fill:
        c.fill = fill
    if bold:
        c.font = Font(bold=True)
    c.border = BORD
    c.alignment = CEN
    return c


wb = Workbook()

# ---- лист 1: дешифратор 4→16 ----
ws = wb.active
ws.title = "Дешифратор 4-16"
ws["A1"] = "Дешифратор с 4 входными сигналами (4→16): адрес A3A2A1A0 активирует один выход Y0..Y15"
ws["A1"].font = Font(bold=True)
hdr = ["A3", "A2", "A1", "A0", "Активный выход"]
for j, h in enumerate(hdr):
    cell(ws, f"{chr(65+j)}3", h, HEAD, True)
for a in range(16):
    r = a + 4
    bits = [(a >> (3 - k)) & 1 for k in range(4)]
    for k in range(4):
        cell(ws, f"{chr(65+k)}{r}", bits[k])
    cell(ws, f"E{r}", f"Y{a} = 1", HL)
ws.column_dimensions["E"].width = 16

# ---- лист 2: JK-триггер ----
jk = wb.create_sheet("JK-триггер")
jk["A1"] = "JK-триггер: характеристическая таблица Q(n+1) = J·¬Q ∨ ¬K·Q"
jk["A1"].font = Font(bold=True)
for j, h in enumerate(["J", "K", "Qn", "Q(n+1)", "Режим"]):
    cell(jk, f"{chr(65+j)}3", h, HEAD, True)
rows = [(0, 0, "Qn", "хранение"), (0, 1, "0", "сброс"), (1, 0, "1", "установка"), (1, 1, "¬Qn", "счёт (toggle)")]
for i, (J, K, q, mode) in enumerate(rows):
    r = i + 4
    cell(jk, f"A{r}", J); cell(jk, f"B{r}", K); cell(jk, f"C{r}", q)
    cell(jk, f"D{r}", q, HL); cell(jk, f"E{r}", mode)
jk["A9"] = "Таблица возбуждения (из Qn в Q(n+1)):"
jk["A9"].font = Font(bold=True)
for j, h in enumerate(["Qn", "Q(n+1)", "J", "K"]):
    cell(jk, f"{chr(65+j)}10", h, HEAD, True)
exc = [(0, 0, 0, "x"), (0, 1, 1, "x"), (1, 0, "x", 1), (1, 1, "x", 0)]
for i, (q, q1, J, K) in enumerate(exc):
    r = i + 11
    cell(jk, f"A{r}", q); cell(jk, f"B{r}", q1); cell(jk, f"C{r}", J); cell(jk, f"D{r}", K)
jk.column_dimensions["E"].width = 16

# ---- лист 3: счётчик (строка 22) ----
ct = wb.create_sheet("Счётчик")
ct["A1"] = "Счётчик по модулю 16, строка 22 табл. 2.11 (вариант 21)"
ct["A1"].font = Font(bold=True)
ct["A2"] = "Таблица состояний"; ct["A2"].font = Font(bold=True)
for j, h in enumerate(["Позиция", "Значение", "Код Q3Q2Q1Q0"]):
    cell(ct, f"{chr(65+j)}3", h, HEAD, True)
for p, v in enumerate(cm.VAL):
    r = p + 4
    cell(ct, f"A{r}", p); cell(ct, f"B{r}", v); cell(ct, f"C{r}", f"{v:04b}")
# таблица переходов справа
ct["E2"] = "Таблица переходов"; ct["E2"].font = Font(bold=True)
for j, h in enumerate(["Текущее", "Условие", "Следующее"]):
    cell(ct, f"{chr(69+j)}3", h, HEAD, True)
for i, (s, cond, n) in enumerate(cm.transitions()):
    r = i + 4
    cell(ct, f"E{r}", f"{s} ({s:04b})"); cell(ct, f"F{r}", cond or "—"); cell(ct, f"G{r}", f"{n} ({n:04b})")
# функции возбуждения
base = 4 + len(cm.transitions()) + 1
ct[f"E{base}"] = "Функции возбуждения newQ (метод пособия):"; ct[f"E{base}"].font = Font(bold=True)
for bit in range(3, -1, -1):
    t, r_ = cm.manual_terms(bit)
    ct[f"E{base + (3 - bit) + 1}"] = f"newQ{bit} = " + " ∨ ".join(t + r_)
for col, w in dict(A=9, B=9, C=13, E=12, F=10, G=12).items():
    ct.column_dimensions[col].width = w

wb.save(OUT)
print("saved", os.path.abspath(OUT))
