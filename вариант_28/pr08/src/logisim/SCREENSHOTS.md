# Скриншоты Logisim для практики 8

Файл схемы: `pr08/src/logisim/riscv_decoder.circ` (одна схема `riscv_decoder`, она же главная).
Открывать в Logisim 2.7.1: `java -jar .tools/logisim/logisim.jar pr08/src/logisim/riscv_decoder.circ`.
Входы выставляются инструментом «Палец» (Poke Tool): щелчок по биту пина меняет его 0/1.
Пин `rs1_val` 32-битный, биты показаны 4 строками по 8, старший бит (31) – слева вверху,
младший (0) – справа внизу. Для каждой картинки – снимок всего окна со схемой целиком
(масштаб подобрать так, чтобы влезли и «память программы» слева, и блок addi внизу).
Предпросмотры того, что должно получиться (нарисованы кодом Logisim без GUI):
`preview_sel0.png`, `preview_sel2.png`, `preview_sel6.png` в этой же папке.

| Картинка | Входы | Что должно быть видно |
|---|---|---|
| `pr08/img/logisim_decoder_li.png` | `sel` = 000, `rs1_val` = 0 (все нули) | instr = 00100513 (`li a0,1` = `addi a0,x0,1`); opcode = 0010011, rd = 01010 (x10 = a0), funct3 = 000, rs1 = 00000, imm12 = 0000 0000 0001; is_addi = 1; imm (dec) = 1; result (hex) = 00000001 |
| `pr08/img/logisim_decoder_addi.png` | `sel` = 010, `rs1_val` = 0x000110EC: строки битов сверху вниз `00000000`, `00000001`, `00010000`, `11101100` | instr = 01858593 (`addi a1,a1,24`); opcode = 0010011, rd = 01011 (x11 = a1), funct3 = 000, rs1 = 01011 (a1), imm12 = 0000 0001 1000; is_addi = 1; imm (dec) = 24; rs1_val (hex) = 000110ec; result (hex) = 00011104 – то же значение a1, что gdb показал после `addi` (рис. 5 отчёта) |
| `pr08/img/logisim_decoder_j.png` | `sel` = 110, `rs1_val` = 0 | instr = fe9ff06f (`j main_app` = `jal x0,-24`); opcode = 1101111 (JAL, не OP-IMM), rd = 00000; выходы «=» обоих компараторов равны 0 (opcode ≠ 0010011, funct3 = 111 ≠ 000), is_addi = 0 – результат сумматора не используется |
