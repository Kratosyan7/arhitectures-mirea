"""Excel для ПР4 (вариант 28): табл. 4.9 (управляющее слово) и 4.10 (состояние регистров) команды NEG."""
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Практика_4_вариант_28.xlsx")
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

# --- лист 1: табл. 4.9 — управляющее слово ---
ws = wb.active
ws.title = "Табл 4.9 УС"
ws["A1"] = "Таблица 4.9 — Управляющее слово команды NEG (вариант 28): AC ← ¬M[AD] + 1"
ws["A1"].font = Font(bold=True)
hdr = ["К,Ц,Т", "Микрокоманда", "MS(A)", "MS(B)", "АЛУ", "DC", "MS(M)", "WR", "FR"]
for j, h in enumerate(hdr):
    cell(ws, f"{chr(65+j)}3", h, HEAD, True)
rows = [
    ("q8C0t0", "MAR ← PC", "000", "xxx", "000000", "1100", "x", "0", "00"),
    ("q8C0t1", "MDR ← M[MAR]", "xxx", "xxx", "xxxxxx", "1011", "1", "0", "00"),
    ("q8C0t2", "IR ← MDR", "100", "xxx", "000000", "1101", "x", "0", "00"),
    ("q8C0t3", "PC ← PC+1; F,R←1,0", "000", "xxx", "000001", "1111", "x", "0", "10"),
    ("q8C2t0", "MAR ← IR (AD=60B)", "010", "xxx", "000000", "1100", "x", "0", "10"),
    ("q8C2t1", "MDR ← M[AD]", "xxx", "xxx", "xxxxxx", "1011", "1", "0", "10"),
    ("q8C2t2", "AC ← ¬MDR", "100", "xxx", "001110", "1110", "x", "0", "10"),
    ("q8C2t3", "AC ← AC+1; F,R←0,0", "001", "xxx", "000001", "1110", "x", "0", "00"),
]
for i, r in enumerate(rows):
    for j, v in enumerate(r):
        cell(ws, f"{chr(65+j)}{i+4}", v)
ws.column_dimensions["B"].width = 22
for col in "ACEF":
    ws.column_dimensions[col].width = 9

# --- лист 2: табл. 4.10 — состояние регистров ---
ws2 = wb.create_sheet("Табл 4.10 регистры")
ws2["A1"] = "Таблица 4.10 — Состояние регистров при выполнении NEG (операнд M[60B]=CB65, AC нач.=CCAA)"
ws2["A1"].font = Font(bold=True)
hdr2 = ["К,Ц,Т", "Микрокоманда", "PC", "MAR", "IR", "MDR", "AC", "INPR", "OUTR"]
for j, h in enumerate(hdr2):
    cell(ws2, f"{chr(65+j)}3", h, HEAD, True)
rows2 = [
    ("Исходное", "—", "DF0", "—", "—", "—", "CCAA", "—", "—"),
    ("q8C0t0", "MAR ← PC", "DF0", "DF0", "—", "—", "CCAA", "—", "—"),
    ("q8C0t1", "MDR ← M[MAR]", "DF0", "DF0", "—", "860B", "CCAA", "—", "—"),
    ("q8C0t2", "IR ← MDR", "DF0", "DF0", "860B", "860B", "CCAA", "—", "—"),
    ("q8C0t3", "PC ← PC+1; F,R←1,0", "DF1", "DF0", "860B", "860B", "CCAA", "—", "—"),
    ("q8C2t0", "MAR ← IR", "DF1", "860B", "860B", "860B", "CCAA", "—", "—"),
    ("q8C2t1", "MDR ← M[AD]", "DF1", "860B", "860B", "CB65", "CCAA", "—", "—"),
    ("q8C2t2", "AC ← ¬MDR", "DF1", "860B", "860B", "CB65", "349A", "—", "—"),
    ("q8C2t3", "AC ← AC+1; F,R←0,0", "DF1", "860B", "860B", "CB65", "349B", "—", "—"),
]
for i, r in enumerate(rows2):
    for j, v in enumerate(r):
        fill = HL if (j == 6 and r[0] in ("q8C2t2", "q8C2t3")) else None
        cell(ws2, f"{chr(65+j)}{i+4}", v, fill)
ws2.column_dimensions["B"].width = 22

wb.save(OUT)
print("saved", os.path.abspath(OUT))
