"""Генератор схемы pr11.circ (Logisim 2.7.1): параллельное суммирование.

Иллюстрация к методу трапеций: основная работа – накопление суммы значений
функции Σ f(xᵢ). Значения взяты целыми: узлы xᵢ = 1…16, yᵢ = 2·f(xᵢ) = 3·xᵢ²
(функция варианта 14, f(x) = 1.5·x²). Точная сумма Σ yᵢ = 3·1496 = 4488.

  seq  – последовательный накопитель: ROM[16] + сумматор + регистр ACC,
         один элемент за такт → 16 тактов;
  par  – P = 4 параллельных накопителя (ПЭ0…ПЭ3, блочное разбиение как у
         MPI-процессов: ПЭj обрабатывает x = 4j+1 … 4j+4) + дерево
         сумматоров (редукция частичных сумм, аналог comm.reduce / сложения
         partial_sums в Pool.map) + регистр результата → 4 + 1 = 5 тактов;
  main – обе схемы от одного тактового сигнала, выход halt = DONE_SEQ ∧ DONE_PAR
         (для прогона в режиме logisim -tty table).
"""
import sys
from circlib import Circuit, save

N, P = 16, 4
Y = [3 * (i + 1) ** 2 for i in range(N)]          # 3, 12, 27, …, 768
TOTAL = sum(Y)                                      # 4488


def rom_contents(addr_bits, values):
    vals = values + [0] * ((1 << addr_bits) - len(values))
    while vals and vals[-1] == 0:
        vals.pop()
    return "addr/data: %d 16\n%s\n" % (addr_bits, " ".join("%x" % v for v in vals))


def accumulator(c, rom_x, yc, addr_bits, values, tunnel_t, label_probe):
    """ROM → сумматор → регистр с обратной связью. Возвращает точку выхода регистра."""
    c.add("memory", "ROM", (rom_x, yc), addrWidth=addr_bits, dataWidth=16,
          contents=rom_contents(addr_bits, values))
    c.tunnel((rom_x - 160, yc), "t", width=addr_bits, facing="east")
    c.wire((rom_x - 160, yc), (rom_x - 140, yc))                 # адрес ROM ← t
    ax = rom_x + 100                                              # сумматор
    c.adder((ax, yc - 10), 16)
    c.wire((rom_x, yc), (ax - 40, yc))                            # данные ROM → b
    rx = ax + 60                                                  # регистр
    c.add("memory", "Register", (rx, yc - 10), width=16, label=label_probe)
    c.wire((ax, yc - 10), (rx - 30, yc - 10))                     # сумма → D
    c.wire((rx - 20, yc + 10), (rx - 20, yc + 30))                # такт
    c.tunnel((rx - 20, yc + 30), "CLK", facing="north")
    fx = rx + 40                                                  # обратная связь Q → a
    c.wire((rx, yc - 10), (fx, yc - 10), (fx, yc - 50), (ax - 60, yc - 50),
           (ax - 60, yc - 20), (ax - 40, yc - 20))
    c.wire((fx, yc - 10), (fx + 20, yc - 10), (fx + 20, yc + 20))
    c.probe((fx + 20, yc + 20), radix="10unsigned", facing="west")
    return (fx + 20, yc - 10)


def control(c, x, y, width, maxval):
    """Генератор тактов и счётчик тактов t (останавливается на maxval)."""
    c.add("wiring", "Clock", (x, y + 50), label="CLK", labelloc="north")
    c.wire((x, y + 50), (x + 20, y + 50))
    c.tunnel((x + 20, y + 50), "CLK", facing="west")
    cx = x + 140
    c.add("memory", "Counter", (cx, y), width=width, max=hex(maxval), ongoal="stay",
          label="t")
    c.wire((cx - 20, y + 20), (cx - 20, y + 40))
    c.tunnel((cx - 20, y + 40), "CLK", facing="north")
    c.wire((cx, y), (cx + 40, y))
    c.tunnel((cx + 40, y), "t", width=width, facing="west")
    c.wire((cx, y + 10), (cx + 20, y + 10), (cx + 20, y + 40), (cx + 40, y + 40))
    c.tunnel((cx + 40, y + 40), "DONE", facing="west")
    c.text((cx - 20, y - 40), "счётчик тактов t (стоп при t = %d)" % maxval, size=12)


def outputs(c, x, y, sum_from, t_width):
    """Выходные пины SUM, T, DONE и десятичные пробы."""
    c.wire(sum_from, (x, sum_from[1]))
    c.pin_out((x, sum_from[1]), 16, "SUM")
    c.tunnel((x - 60, y), "t", width=t_width, facing="east")
    c.wire((x - 60, y), (x, y))
    c.pin_out((x, y), t_width, "T")
    c.wire((x - 30, y), (x - 30, y + 20))
    c.probe((x - 30, y + 20), radix="10unsigned", facing="west")
    c.tunnel((x - 60, y + 60), "DONE", facing="east")
    c.wire((x - 60, y + 60), (x, y + 60))
    c.pin_out((x, y + 60), 1, "DONE")


# ---------------------------------------------------------------- seq
seq = Circuit("seq")
seq.text((330, 20), "Последовательное суммирование: N = 16 элементов, 1 элемент за такт", size=16, bold=True)
seq.text((330, 45), "ACC ← ACC + ROM[t];  yᵢ = 3·xᵢ², xᵢ = 1…16;  результат через 16 тактов", size=12)
control(seq, 40, 110, 5, N)
seq.text((420, 145), "ROM: y₀ … y₁₅", size=12)
acc_q = accumulator(seq, 460, 220, 5, Y, "t", "ACC")
seq.text((540, 280), "сумматор + регистр ACC (накопитель)", size=12)
outputs(seq, 800, 290, acc_q, 5)

# ---------------------------------------------------------------- par
par = Circuit("par")
par.text((520, 20), "Параллельное суммирование: P = 4 накопителя по N/P = 4 элемента + дерево редукции",
         size=16, bold=True)
par.text((520, 45), "ПЭj: Sj ← Sj + ROMj[t] (такты 1–4);  такт 5: RES ← (S0 + S1) + (S2 + S3)", size=12)
control(par, 40, 110, 3, P + 1)
# сравнение t = 4 → разрешение записи в регистр результата (такт редукции)
par.tunnel((320, 110), "t", width=3, facing="east")
par.wire((320, 110), (360, 110))
par.const((340, 130), 3, P)
par.wire((340, 130), (360, 130))
par.comparator((400, 120), 3)
par.wire((400, 120), (420, 120))
par.tunnel((420, 120), "RED", facing="west")
par.text((390, 80), "t = 4 → такт редукции", size=12)

rows = [230, 380, 530, 680]
s_out = []
for j, yc in enumerate(rows):
    par.text((320, yc - 60), "ПЭ%d: x = %d…%d" % (j, 4 * j + 1, 4 * j + 4), size=13, bold=True)
    s_out.append(accumulator(par, 360, yc, 3, Y[4 * j:4 * j + 4], "t", "S%d" % j))

# дерево редукции: два уровня сумматоров
tx = 720
par.text((tx + 120, 180), "дерево редукции (reduce)", size=13, bold=True)
def tree_adder(loc, src_a, src_b, bus_x):
    ax, ay = loc
    par.adder(loc, 16)
    par.wire(src_a, (bus_x, src_a[1]), (bus_x, ay - 10), (ax - 40, ay - 10))
    par.wire(src_b, (bus_x, src_b[1]), (bus_x, ay + 10), (ax - 40, ay + 10))
    return loc

r01 = tree_adder((tx + 60, (rows[0] + rows[1]) // 2 - 10), s_out[0], s_out[1], tx)
r23 = tree_adder((tx + 60, (rows[2] + rows[3]) // 2 - 10), s_out[2], s_out[3], tx)
par.text((tx + 40, r01[1] + 40), "S0 + S1", size=12)
par.text((tx + 40, r23[1] + 40), "S2 + S3", size=12)
rt = tree_adder((tx + 180, (r01[1] + r23[1]) // 2), r01, r23, tx + 120)
# регистр результата RES, запись только в такт редукции
rx = rt[0] + 80
par.add("memory", "Register", (rx, rt[1]), width=16, label="RES")
par.wire(rt, (rx - 30, rt[1]))
par.wire((rx - 30, rt[1] + 10), (rx - 50, rt[1] + 10), (rx - 50, rt[1] + 50))
par.tunnel((rx - 50, rt[1] + 50), "RED", facing="north")
par.wire((rx - 20, rt[1] + 20), (rx - 20, rt[1] + 60))
par.tunnel((rx - 20, rt[1] + 60), "CLK", facing="north")
par.wire((rx, rt[1]), (rx + 40, rt[1]), (rx + 40, rt[1] + 30))
par.probe((rx + 40, rt[1] + 30), radix="10unsigned", facing="west")
outputs(par, rx + 160, rt[1] + 100, (rx + 40, rt[1]), 3)

# ---------------------------------------------------------------- main
main = Circuit("main")
main.text((300, 30), "Сравнение: последовательное (seq) и параллельное (par) суммирование", size=16, bold=True)
main.text((300, 55), "Σ yᵢ = 4488;  seq: 16 тактов,  par: 16/4 + 1 = 5 тактов", size=12)
for name, y0, tw in (("seq", 140, 5), ("par", 340, 3)):
    sfx = name.upper()
    main.sub(name, (200, y0))
    main.text((150, y0 - 30), name, size=13, bold=True)
    # выходы подсхемы: SUM (y0), T (y0+10), DONE (y0+20)
    main.wire((200, y0), (400, y0))
    main.pin_out((400, y0), 16, "SUM_" + sfx)
    main.wire((300, y0), (300, y0 - 25), (320, y0 - 25))
    main.probe((320, y0 - 25), radix="10unsigned", facing="west")
    main.wire((200, y0 + 10), (220, y0 + 10), (220, y0 + 50), (400, y0 + 50))
    main.pin_out((400, y0 + 50), tw, "T_" + sfx)
    main.wire((300, y0 + 50), (300, y0 + 75), (320, y0 + 75))
    main.probe((320, y0 + 75), radix="10unsigned", facing="west")
    main.wire((200, y0 + 20), (210, y0 + 20), (210, y0 + 100), (400, y0 + 100))
    main.pin_out((400, y0 + 100), 1, "DONE_" + sfx)
    main.wire((360, y0 + 100), (360, y0 + 120))
    main.tunnel((360, y0 + 120), "D_" + sfx, facing="north")
# halt = DONE_SEQ ∧ DONE_PAR – останавливает прогон logisim -tty
main.tunnel((260, 510), "D_SEQ", facing="east")
main.tunnel((260, 530), "D_PAR", facing="east")
main.wire((260, 510), (290, 510))
main.wire((260, 530), (290, 530))
main.gate("AND Gate", (320, 520), inputs=2, size=30)
main.wire((320, 520), (400, 520))
main.pin_out((400, 520), 1, "halt")
main.text((330, 555), "halt = DONE_SEQ ∧ DONE_PAR", size=12)

if __name__ == "__main__":
    save(sys.argv[1] if len(sys.argv) > 1 else "pr11.circ", [main, seq, par], main="main")
