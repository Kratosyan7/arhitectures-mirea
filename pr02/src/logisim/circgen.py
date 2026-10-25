"""Мини-генератор файлов Logisim 2.7.1 (.circ).

Компоненты соединяются проводами (wire) и туннелями (Tunnel) по меткам.
Геометрия портов повторяет исходники Logisim 2.7.1 (AbstractGate.getInputOffset,
NotGate, Transistor, AbstractFlipFlop), корректность соединений проверяется
прогоном схем в движке Logisim (logitool.js).
"""
from xml.sax.saxutils import quoteattr

LIBS = {"wiring": 0, "gates": 1, "plexers": 2, "arith": 3, "memory": 4, "io": 5, "base": 6}


def _inputs_offsets(n, size):
    """Смещения входов по оси Y (как AbstractGate.getInputOffset, facing=east)."""
    if n <= 3:
        if size < 40:
            s0, sd, sle = -5, 10, 10
        elif size < 60 or n <= 2:
            s0, sd, sle = -10, 20, 20
        else:
            s0, sd, sle = -15, 30, 30
    elif n == 4 and size >= 60:
        s0, sd, sle = -5, 20, 0
    else:
        s0, sd, sle = -5, 10, 10
    res = []
    for i in range(n):
        if n & 1:
            dy = s0 * (n - 1) + sd * i
        else:
            dy = s0 * n + sd * i
            if i >= n // 2:
                dy += sle
        res.append(dy)
    return res


class Circuit:
    def __init__(self, name):
        self.name = name
        self.comps = []
        self.segs = []

    # ---------- низкоуровневые ----------
    def comp(self, lib, name, loc, **attrs):
        self.comps.append((LIBS[lib], name, loc, attrs))

    def wire(self, *pts):
        for p, q in zip(pts, pts[1:]):
            if p == q:
                continue
            assert p[0] == q[0] or p[1] == q[1], (p, q)
            self.segs.append((p, q))

    # ---------- компоненты ----------
    def pin_in(self, loc, label, facing="east", labelloc=None):
        a = dict(tristate="false", label=label, facing=facing)
        if labelloc:
            a["labelloc"] = labelloc
        self.comp("wiring", "Pin", loc, **a)

    def pin_out(self, loc, label, facing="west", labelloc="east", width=1):
        a = dict(output="true", label=label, facing=facing, labelloc=labelloc)
        if width != 1:
            a["width"] = str(width)
        self.comp("wiring", "Pin", loc, **a)

    def tunnel(self, loc, label, facing="west"):
        self.comp("wiring", "Tunnel", loc, label=label, facing=facing)

    def text(self, loc, text, font="SansSerif bold 14"):
        self.comp("base", "Text", loc, text=text, font=font)

    def gate(self, kind, loc, n=2, size=50, label=None):
        """kind: AND/OR/NAND/NOR/XOR. Возвращает список точек входов."""
        a = dict(inputs=str(n), size=str(size))
        if label:
            a["label"] = label
        self.comp("gates", f"{kind} Gate", loc, **a)
        axis = size + (10 if kind in ("NAND", "NOR") else 0) + (10 if kind == "XOR" else 0)
        x, y = loc
        return [(x - axis, y + dy) for dy in _inputs_offsets(n, size)]

    def not_gate(self, loc, size=30, facing="east"):
        self.comp("gates", "NOT Gate", loc, size=str(size), facing=facing)
        d = 20 if size == 20 else 30
        x, y = loc
        return {"east": (x - d, y), "west": (x + d, y), "south": (x, y - d), "north": (x, y + d)}[facing]

    def transistor(self, loc, typ, facing):
        """Возвращает (drain/output, source/input, gate)."""
        self.comp("wiring", "Transistor", loc, type=typ, facing=facing)
        dx, dy = {"north": (0, 1), "east": (-1, 0), "south": (0, -1), "west": (1, 0)}[facing]
        flip = facing in ("south", "west")  # gate = top/left (по умолчанию)
        x, y = loc
        src = (x + 40 * dx, y + 40 * dy)
        if flip:
            g = (x + 20 * (dx + dy), y + 20 * (-dx + dy))
        else:
            g = (x + 20 * (dx - dy), y + 20 * (dx + dy))
        return loc, src, g

    def dff(self, loc, label=None):
        """D-триггер Logisim: возвращает dict портов."""
        a = {}
        if label:
            a["label"] = label
        self.comp("memory", "D Flip-Flop", loc, **a)
        x, y = loc
        return dict(D=(x - 40, y + 20), C=(x - 40, y), Q=(x, y), nQ=(x, y + 20),
                    R=(x - 10, y + 30), S=(x - 30, y + 30), E=(x - 20, y + 30))

    def clock(self, loc, label="clk", facing="east"):
        self.comp("wiring", "Clock", loc, label=label, facing=facing)

    def splitter_west(self, loc, fanout=4):
        """Разветвитель, обращённый на запад: шина (loc) справа, биты слева.
        Бит i выходит в точке (x-20, y+10+10*i)."""
        self.comp("wiring", "Splitter", loc, facing="west", fanout=str(fanout), incoming=str(fanout), appear="left")
        x, y = loc
        return [(x - 20, y + 10 + 10 * i) for i in range(fanout)]

    def hex_display(self, loc):
        self.comp("io", "Hex Digit Display", loc)
        return loc

    # ---------- вывод ----------
    def _split(self):
        """Разбивает сегменты в точках Т-образных соединений (концы других сегментов)."""
        pts = set()
        for p, q in self.segs:
            pts.add(p)
            pts.add(q)
        out = set()
        for p, q in self.segs:
            (x1, y1), (x2, y2) = sorted([p, q])
            inner = []
            for (x, y) in pts:
                if x1 == x2 == x and y1 < y < y2:
                    inner.append((x, y))
                elif y1 == y2 == y and x1 < x < x2:
                    inner.append((x, y))
            chain = [(x1, y1)] + sorted(inner) + [(x2, y2)]
            for a, b in zip(chain, chain[1:]):
                out.add((a, b))
        return sorted(out)

    def xml(self):
        L = [f'  <circuit name={quoteattr(self.name)}>',
             f'    <a name="circuit" val={quoteattr(self.name)}/>',
             '    <a name="clabel" val=""/>', '    <a name="clabelup" val="east"/>',
             '    <a name="clabelfont" val="SansSerif plain 12"/>']
        for (p, q) in self._split():
            L.append(f'    <wire from="({p[0]},{p[1]})" to="({q[0]},{q[1]})"/>')
        for lib, name, loc, attrs in self.comps:
            if attrs:
                L.append(f'    <comp lib="{lib}" loc="({loc[0]},{loc[1]})" name="{name}">')
                for k, v in attrs.items():
                    L.append(f'      <a name="{k}" val={quoteattr(str(v))}/>')
                L.append('    </comp>')
            else:
                L.append(f'    <comp lib="{lib}" loc="({loc[0]},{loc[1]})" name="{name}"/>')
        L.append('  </circuit>')
        return "\n".join(L)


def project_xml(circuits, main=None):
    main = main or circuits[0].name
    head = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            '<project source="2.7.1" version="1.0">',
            'This file is intended to be loaded by Logisim (http://www.cburch.com/logisim/).',
            '  <lib desc="#Wiring" name="0"/>', '  <lib desc="#Gates" name="1"/>',
            '  <lib desc="#Plexers" name="2"/>', '  <lib desc="#Arithmetic" name="3"/>',
            '  <lib desc="#Memory" name="4"/>', '  <lib desc="#I/O" name="5"/>',
            '  <lib desc="#Base" name="6">',
            '    <tool name="Text Tool">',
            '      <a name="text" val=""/>', '      <a name="font" val="SansSerif plain 12"/>',
            '      <a name="halign" val="center"/>', '      <a name="valign" val="base"/>',
            '    </tool>', '  </lib>',
            f'  <main name={quoteattr(main)}/>',
            '  <options>', '    <a name="gateUndefined" val="ignore"/>',
            '    <a name="simlimit" val="1000"/>', '    <a name="simrand" val="0"/>',
            '  </options>',
            '  <mappings>', '    <tool lib="6" map="Button2" name="Menu Tool"/>',
            '    <tool lib="6" map="Button3" name="Menu Tool"/>',
            '    <tool lib="6" map="Ctrl Button1" name="Menu Tool"/>', '  </mappings>',
            '  <toolbar>', '    <tool lib="6" name="Poke Tool"/>', '    <tool lib="6" name="Edit Tool"/>',
            '    <tool lib="6" name="Text Tool"/>', '    <sep/>',
            '    <tool lib="0" name="Pin"><a name="tristate" val="false"/></tool>',
            '    <tool lib="0" name="Pin"><a name="facing" val="west"/><a name="output" val="true"/>'
            '<a name="labelloc" val="east"/></tool>',
            '    <tool lib="1" name="NOT Gate"/>', '    <tool lib="1" name="AND Gate"/>',
            '    <tool lib="1" name="OR Gate"/>', '  </toolbar>']
    body = [c.xml() for c in circuits]
    return "\n".join(head + body + ['</project>', ''])
