"""Генератор схемы riscv_decoder.circ (Logisim 2.7.1) для практики 8.

Схема: «память программы» из 8 реальных машинных кодов (objdump программы
main_app/hello_world) -> мультиплексор 8:1 (вход sel – номер инструкции) ->
32-битная шина instr -> разветвители выделяют поля opcode/rd/funct3/rs1/rs2/
funct7/imm[11:0]. Исполнительный блок: is_addi = (opcode == 0010011) & (funct3 == 000),
imm знакорасширяется до 32 бит и складывается с rs1_val (вход) -> result.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from circlib import Circuit, save

PROG = [  # (адрес, машинный код, мнемоника) – из riscv64-linux-gnu-objdump -d
    (0x100e8, 0x00100513, "li a0,1  (addi a0,x0,1)"),
    (0x100ec, 0x00001597, "auipc a1,0x1"),
    (0x100f0, 0x01858593, "addi a1,a1,24"),
    (0x100f4, 0x02800613, "li a2,40  (addi a2,x0,40)"),
    (0x100f8, 0x04000893, "li a7,64  (addi a7,x0,64)"),
    (0x100fc, 0x00000073, "ecall"),
    (0x10100, 0xfe9ff06f, "j main_app  (jal x0,-24)"),
    (0x10104, 0x05d00893, "li a7,93  (hello_world, exit)"),
]

c = Circuit("riscv_decoder")
c.text((660, 30), "Дешифратор полей инструкции RISC-V и сумматор для addi", 16, bold=True)
c.text((660, 55), "Практическая работа 8, вариант 14 (Мирзоян А.О., ИКБО-41-25)", 12)

# ---- память программы: 8 констант + мультиплексор 8:1 ----------------
CX, Y0, DY = 400, 120, 40
MX, MY = 580, 260
c.text((250, 95), "Память программы: машинные коды из objdump", 12, bold=True)
xs = [530, 510, 490, 470, 470, 490, 510, 530]   # абсциссы вертикальных отводов
for i, (addr, code, asm) in enumerate(PROG):
    y = Y0 + DY * i
    c.const((CX, y), 32, code)
    c.text((315, y), "%d:  %05x  %s" % (i, addr, asm), 12, halign="right")
    yin = MY - 40 + 10 * i
    c.wire((CX, y), (xs[i], y), (xs[i], yin), (MX - 40, yin))
c.mux((MX, MY), 32, 3)
c.wire((MX - 20, MY + 40), (MX - 20, MY + 60))
c.pin_in((MX - 20, MY + 60), 3, "sel", facing="north", labelloc="south")
c.text((MX + 5, MY + 72), "← номер инструкции (0–7)", 11, halign="left")

# ---- шина instr и дешифратор полей ------------------------------------
BX = 640
c.wire((MX, MY), (BX, MY))
c.wire((BX, 130), (BX, 780))
c.wire((BX, 130), (760, 130))
c.probe((760, 130), "16", label="instr", labelloc="east")
c.text((820, 100), "Поля инструкции", 12, bold=True)

FIELDS = [  # (метка, младший бит, старший бит, y, пояснение)
    ("opcode", 0, 6, 180, "opcode = instr[6:0]  (тип/класс команды)"),
    ("rd", 7, 11, 230, "rd = instr[11:7]  (регистр-приёмник)"),
    ("funct3", 12, 14, 280, "funct3 = instr[14:12]"),
    ("rs1", 15, 19, 330, "rs1 = instr[19:15]  (1-й источник)"),
    ("rs2", 20, 24, 380, "rs2 = instr[24:20]  (2-й источник, R/S/B)"),
    ("funct7", 25, 31, 430, "funct7 = instr[31:25]"),
    ("imm12", 20, 31, 490, "imm[11:0] = instr[31:20]  (I-тип)"),
]


def field_splitter(x, y, lo, hi):
    c.splitter((x, y), 32, 1, [0 if lo <= b <= hi else None for b in range(32)])


for name, lo, hi, y, desc in FIELDS:
    c.wire((BX, y), (680, y))
    field_splitter(680, y, lo, hi)
    c.wire((700, y), (760, y))
    c.pin_out((760, y), hi - lo + 1, name)
    c.text((910, y), desc, 12, halign="left")

# ---- исполнительный блок addi ----------------------------------------
c.text((BX + 20, 565), "Исполнение addi:  is_addi = (opcode = 0010011) ∧ (funct3 = 000),"
       "  result = rs1_val + sext(imm)", 12, bold=True, halign="left")
# opcode == 0x13
c.wire((BX, 600), (680, 600)); field_splitter(680, 600, 0, 6)
c.wire((700, 600), (780, 600))
c.const((760, 620), 7, 0x13); c.wire((760, 620), (780, 620))
c.comparator((820, 610), 7)
c.text((720, 640), "OP-IMM = 0x13", 11)
# funct3 == 0
c.wire((BX, 680), (680, 680)); field_splitter(680, 680, 12, 14)
c.wire((700, 680), (780, 680))
c.const((760, 700), 3, 0); c.wire((760, 700), (780, 700))
c.comparator((820, 690), 3)
c.text((720, 720), "ADDI: funct3 = 000", 11)
# И
c.wire((820, 610), (850, 610), (850, 630), (870, 630))
c.wire((820, 690), (850, 690), (850, 670), (870, 670))
c.gate("AND Gate", (920, 650))
c.wire((920, 650), (980, 650))
c.pin_out((980, 650), 1, "is_addi")
# imm: знаковое расширение 12 -> 32 бит
c.wire((BX, 780), (680, 780)); field_splitter(680, 780, 20, 31)
c.wire((700, 780), (740, 780))
c.bitext((780, 780), 12, 32, "sign")
c.text((760, 815), "sext 12→32", 11)
c.wire((780, 780), (820, 780), (960, 780))
c.probe((960, 780), "10signed", label="imm (dec)", labelloc="east")
# сумматор rs1_val + imm
c.wire((820, 780), (820, 850), (860, 850))
c.pin_in((760, 900), 32, "rs1_val")
c.wire((760, 900), (800, 900), (800, 870), (860, 870))
c.adder((900, 860), 32)
c.wire((900, 860), (1060, 860))
c.pin_out((1060, 860), 32, "result")
c.wire((940, 860), (940, 960))
c.probe((940, 960), "16", label="result (hex)", labelloc="east")
c.wire((800, 900), (800, 990))
c.probe((800, 990), "16", label="rs1_val (hex)", labelloc="east")

save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "riscv_decoder.circ"), [c])
print("riscv_decoder.circ written")
