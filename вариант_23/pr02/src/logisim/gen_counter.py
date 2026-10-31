"""Генерация counter.circ для ПР2 (вариант 23): счётчик с произвольным порядком
счёта по строке 24 табл. 2.11 на D-триггерах (метод пособия) + подсхема newQ_min (МДНФ)."""
import os
import sys

from circgen import Circuit, project_xml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import counter_model as cm  # noqa: E402


def or_block(c, gx, gy, names, out_label):
    """ИЛИ с n входами; входы подводятся от ряда туннелей сверху (как рис. 2.19)."""
    n = len(names)
    ins = c.gate("OR", (gx, gy), n=n, size=70)
    ytop = gy - (n // 2) * 10 - 40
    for j, name in enumerate(names):
        xt = gx - 100 - 40 * j
        c.tunnel((xt, ytop), name, facing="south")
        c.wire((xt, ytop), (xt, ins[j][1]), ins[j])
    c.wire((gx, gy), (gx + 30, gy))
    c.tunnel((gx + 30, gy), out_label)


def counter():
    c = Circuit("counter")
    c.text((700, 15), "Счётчик по модулю 16 с произвольным порядком счёта (вариант 24 табл. 2.11), D-триггеры")
    # входы и тактовый генератор
    c.pin_in((40, 60), "A"); c.wire((40, 60), (80, 60)); c.tunnel((80, 60), "A")
    c.pin_in((40, 120), "B"); c.wire((40, 120), (80, 120)); c.tunnel((80, 120), "B")
    c.clock((40, 180)); c.wire((40, 180), (80, 180)); c.tunnel((80, 180), "clk")
    # D-триггеры
    for i in range(4):
        x = 260 + 200 * i
        p = c.dff((x, 80))
        c.tunnel((x - 60, 80), "clk", facing="east"); c.wire((x - 60, 80), p["C"])
        c.wire(p["D"], (x - 50, 100), (x - 50, 120), (x - 60, 120)); c.tunnel((x - 60, 120), f"newQ{i}", facing="east")
        c.wire(p["Q"], (x + 30, 80)); c.tunnel((x + 30, 80), f"Q{i}")
        c.wire(p["nQ"], (x + 20, 100), (x + 20, 130), (x + 30, 130)); c.tunnel((x + 30, 130), f"nQ{i}")
        c.text((x - 20, 155), f"разряд {i}", font="SansSerif plain 11")
    # индикатор и шина состояния
    ends = c.splitter_west((1240, 120))
    for i, e in enumerate(ends):
        xt = 1200 - 40 * i
        c.tunnel((xt, 70), f"Q{i}", facing="south")
        c.wire((xt, 70), (xt, e[1]), e)
    c.wire((1240, 120), (1270, 120), (1300, 120))
    c.hex_display((1300, 120))
    c.wire((1270, 120), (1270, 180), (1320, 180))
    c.pin_out((1320, 180), "Q", width=4)
    # дешифратор состояний st0..st15 (рис. 2.17)
    rails_order = [("Q3", 3, 1), ("nQ3", 3, 0), ("Q2", 2, 1), ("nQ2", 2, 0),
                   ("Q1", 1, 1), ("nQ1", 1, 0), ("Q0", 0, 1), ("nQ0", 0, 0)]
    for col in range(2):
        bx = 60 + 470 * col
        gx = bx + 360
        rail_x = {}
        for k, (name, bit, val) in enumerate(rails_order):
            x = bx + 30 * k
            yt = 290 if k % 2 == 0 else 260
            c.tunnel((x, yt), name, facing="south")
            c.wire((x, yt), (x, 790))
            rail_x[(bit, val)] = x
        for j in range(8):
            s = 8 * col + j
            y = 340 + 60 * j
            ins = c.gate("AND", (gx, y), n=4, size=50)
            for k, bit in enumerate([3, 2, 1, 0]):
                v = (s >> bit) & 1
                c.wire((rail_x[(bit, v)], ins[k][1]), ins[k])
            c.wire((gx, y), (gx + 30, y)); c.tunnel((gx + 30, y), f"st{s}")
    # развилки R1..R6 (рис. 2.18)
    c.tunnel((1040, 280), "A", facing="east"); c.wire((1040, 280), (1070, 280))
    c.not_gate((1100, 280)); c.wire((1100, 280), (1120, 280)); c.tunnel((1120, 280), "nA")
    c.tunnel((1040, 330), "B", facing="east"); c.wire((1040, 330), (1070, 330))
    c.not_gate((1100, 330)); c.wire((1100, 330), (1120, 330)); c.tunnel((1120, 330), "nB")
    cond_tun = {"A": "A", "¬A": "nA", "B": "B", "¬B": "nB"}
    for j, (name, cond, st, tgt) in enumerate(cm.r_terms()):
        y = 410 + 70 * j
        ins = c.gate("AND", (1200, y), n=2, size=50)
        c.tunnel((1120, ins[0][1]), cond_tun[cond], facing="east"); c.wire((1120, ins[0][1]), ins[0])
        c.tunnel((1120, ins[1][1]), f"st{st}", facing="east"); c.wire((1120, ins[1][1]), ins[1])
        c.wire((1200, y), (1230, y)); c.tunnel((1230, y), name)
    # newQ0..newQ3 (рис. 2.19–2.22)
    for bit in range(4):
        t, r = cm.manual_terms(bit)
        or_block(c, 1900, 340 + 190 * bit, t + r, f"newQ{bit}")
    return c


def newq_min():
    """Комбинационная подсхема: newQ3..newQ0 по МДНФ (вход Q3..Q0, a, b)."""
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        funcs = cm.main()
    c = Circuit("newQ_min")
    c.text((420, -10), "Функции возбуждения newQ3..newQ0 по МДНФ (проверочная подсхема)")
    names = cm.VNAMES
    xs = {}
    for k, v in enumerate(names):
        x = 80 + 70 * k
        c.pin_in((x, 40), v, facing="south", labelloc="north")
        c.wire((x, 40), (x, 60))
        c.wire((x, 60), (x + 20, 60), (x + 20, 70))
        c.not_gate((x + 20, 100), size=30, facing="south")
        xs[(k, 1)] = x
        xs[(k, 0)] = x + 20
    y = 140
    bottom = None
    gx = 580
    for bit in range(3, -1, -1):
        terms = funcs[bit]
        ys = []
        for p in terms:
            lits = [(k, int(ch)) for k, ch in enumerate(p) if ch != "-"]
            ins = c.gate("AND", (gx, y), n=len(lits), size=50)
            for (k, v), pt in zip(lits, ins):
                c.wire((xs[(k, v)], pt[1]), pt)
            ys.append(y)
            y += 60
        n = len(ys)
        from circgen import _inputs_offsets
        center = (ys[0] + ys[-1]) // 2
        center -= center % 10
        for delta in [0, 10, -10, 20, -20, 30, -30, 40, -40]:
            oy = center + delta
            yin = [oy + d for d in _inputs_offsets(n, 70)]
            if not any(ys[k] == yin[j] for k in range(n) for j in range(n) if k != j):
                break
        ors = c.gate("OR", (800, oy), n=n, size=70)
        for j, yy in enumerate(ys):
            xk = 610 + 10 * j
            c.wire((gx, yy), (xk, yy), (xk, ors[j][1]), ors[j])
        c.wire((800, oy), (860, oy)); c.pin_out((860, oy), f"newQ{bit}")
        y += 30
    bottom = y
    for (k, v), x in xs.items():
        c.wire((x, 100 if v == 0 else 60), (x, bottom))
    return c


if __name__ == "__main__":
    with open(os.path.join(HERE, "counter.circ"), "w", encoding="utf-8") as f:
        f.write(project_xml([counter(), newq_min()]))
    print("counter.circ ok")
