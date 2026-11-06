"""Excel для ПР4 (вариант 23): табл. 4.9 (управляющее слово) и 4.10 (состояние регистров) команды XOR."""
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Практика_4_вариант_23.xlsx")
HEAD = PatternFill("solid", fgColor="DDEBF7")
HL = PatternFill("solid", fgColor="E2EFDA")
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
ws = wb.active
ws.title = "Табл 4.9 УС"
ws["A1"] = "Таблица 4.9 — Управляющее слово команды XOR (вариант 23): AC ← AC ⊕ M[AD]"
ws["A1"].font = Font(bold=True)
hdr = ["К,Ц,Т", "Микрокоманда", "MS(A)", "MS(B)", "АЛУ", "DC", "MS(M)", "WR", "FR"]
for j, h in enumerate(hdr):
    cell(ws, f"{chr(65+j)}3", h, HEAD, True)
rows = [
    ("q6C0t0", "MAR ← PC", "000", "xxx", "000000", "1100", "x", "0", "00"),
    ("q6C0t1", "MDR ← M[MAR]", "xxx", "xxx", "xxxxxx", "1011", "1", "0", "00"),
    ("q6C0t2", "IR ← MDR", "100", "xxx", "000000", "1101", "x", "0", "00"),
    ("q6C0t3", "PC ← PC+1; F,R←1,0", "000", "xxx", "000001", "1111", "x", "0", "10"),
    ("q6C2t0", "MAR ← IR (AD=50D)", "010", "xxx", "000000", "1100", "x", "0", "10"),
    ("q6C2t1", "MDR ← M[AD]", "xxx", "xxx", "xxxxxx", "1011", "1", "0", "10"),
    ("q6C2t2", "AC ← AC ⊕ MDR", "001", "100", "001010", "1110", "x", "0", "10"),
    ("q6C2t3", "NOP; F,R←0,0", "xxx", "xxx", "xxxxxx", "0xxx", "x", "0", "00"),
]
for i, r in enumerate(rows):
    for j, v in enumerate(r):
        cell(ws, f"{chr(65+j)}{i+4}", v)
ws.column_dimensions["B"].width = 22
for col in "ACEF":
    ws.column_dimensions[col].width = 9

ws2 = wb.create_sheet("Табл 4.10 регистры")
ws2["A1"] = "Таблица 4.10 — Состояние регистров при выполнении XOR (M[50D]=AB46, AC нач.=FF35)"
ws2["A1"].font = Font(bold=True)
hdr2 = ["К,Ц,Т", "Микрокоманда", "PC", "MAR", "IR", "MDR", "AC", "INPR", "OUTR"]
for j, h in enumerate(hdr2):
    cell(ws2, f"{chr(65+j)}3", h, HEAD, True)
rows2 = [
    ("Исходное", "—", "8F5", "—", "—", "—", "FF35", "—", "—"),
    ("q6C0t0", "MAR ← PC", "8F5", "8F5", "—", "—", "FF35", "—", "—"),
    ("q6C0t1", "MDR ← M[MAR]", "8F5", "8F5", "—", "650D", "FF35", "—", "—"),
    ("q6C0t2", "IR ← MDR", "8F5", "8F5", "650D", "650D", "FF35", "—", "—"),
    ("q6C0t3", "PC ← PC+1; F,R←1,0", "8F6", "8F5", "650D", "650D", "FF35", "—", "—"),
    ("q6C2t0", "MAR ← IR", "8F6", "650D", "650D", "650D", "FF35", "—", "—"),
    ("q6C2t1", "MDR ← M[AD]", "8F6", "650D", "650D", "AB46", "FF35", "—", "—"),
    ("q6C2t2", "AC ← AC ⊕ MDR", "8F6", "650D", "650D", "AB46", "5473", "—", "—"),
    ("q6C2t3", "NOP; F,R←0,0", "8F6", "650D", "650D", "AB46", "5473", "—", "—"),
]
for i, r in enumerate(rows2):
    for j, v in enumerate(r):
        fill = HL if (j == 6 and r[0] in ("q6C2t2", "q6C2t3")) else None
        cell(ws2, f"{chr(65+j)}{i+4}", v, fill)
ws2.column_dimensions["B"].width = 22
wb.save(OUT)
print("saved", os.path.abspath(OUT))
