"""Мини-генератор файлов Logisim 2.7.1 (.circ).

Компоненты задаются координатами их точки привязки (как в Logisim),
провода – ломаными из горизонтальных/вертикальных отрезков.
Перед записью отрезки проводов разбиваются в точках, где на них
попадают концы других проводов (T-образные соединения), – так же,
как это делает редактор Logisim.
"""
from xml.sax.saxutils import escape, quoteattr

LIBS = {"wiring": 0, "gates": 1, "plexers": 2, "arith": 3, "memory": 4, "io": 5, "base": 6}
LIB_DESC = ["#Wiring", "#Gates", "#Plexers", "#Arithmetic", "#Memory", "#I/O", "#Base"]


class Circuit:
    def __init__(self, name):
        self.name = name
        self.comps = []   # (lib, name, (x, y), attrs)
        self.wires = []   # ((x1, y1), (x2, y2))

    # --- провода -----------------------------------------------------
    def wire(self, *pts):
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            assert a[0] == b[0] or a[1] == b[1], ("diagonal wire", a, b)
            self.wires.append((tuple(a), tuple(b)))

    # --- компоненты --------------------------------------------------
    def add(self, lib, name, loc, **attrs):
        self.comps.append((LIBS[lib], name, tuple(loc), attrs))

    def pin_in(self, loc, width, label, facing="east", labelloc="west"):
        self.add("wiring", "Pin", loc, facing=facing, width=width, tristate="false",
                 label=label, labelloc=labelloc)

    def pin_out(self, loc, width, label, facing="west", labelloc="east"):
        self.add("wiring", "Pin", loc, facing=facing, output="true", width=width,
                 tristate="false", label=label, labelloc=labelloc)

    def const(self, loc, width, value, facing="east"):
        self.add("wiring", "Constant", loc, facing=facing, width=width, value=hex(value))

    def probe(self, loc, radix="16", facing="west", label="", labelloc="north"):
        a = dict(facing=facing, radix=radix)
        if label:
            a.update(label=label, labelloc=labelloc)
        self.add("wiring", "Probe", loc, **a)

    def splitter(self, loc, incoming, fanout, bitmap, facing="east", appear="center"):
        """bitmap[i] = номер выхода для бита i или None."""
        a = dict(facing=facing, fanout=fanout, incoming=incoming, appear=appear)
        for i in range(incoming):
            a["bit%d" % i] = "none" if bitmap[i] is None else bitmap[i]
        self.add("wiring", "Splitter", loc, **a)

    def bitext(self, loc, win, wout, kind="sign"):
        self.add("wiring", "Bit Extender", loc, in_width=win, out_width=wout, type=kind)

    def mux(self, loc, width, select, facing="east"):
        self.add("plexers", "Multiplexer", loc, facing=facing, select=select, width=width)

    def comparator(self, loc, width, mode="unsigned"):
        self.add("arith", "Comparator", loc, width=width, mode=mode)

    def adder(self, loc, width):
        self.add("arith", "Adder", loc, width=width)

    def subtractor(self, loc, width):
        self.add("arith", "Subtractor", loc, width=width)

    def gate(self, kind, loc, inputs=2, size=50, facing="east", width=1):
        self.add("gates", kind, loc, facing=facing, size=size, inputs=inputs, width=width)

    def tunnel(self, loc, label, width=1, facing="west"):
        self.add("wiring", "Tunnel", loc, facing=facing, width=width, label=label)

    def sub(self, name, loc, facing="east"):
        """Экземпляр подсхемы этого же проекта."""
        self.comps.append((None, name, tuple(loc), {"facing": facing}))

    def text(self, loc, text, size=12, bold=False, halign="center", valign="center"):
        font = "SansSerif %s %d" % ("bold" if bold else "plain", size)
        self.add("base", "Text", loc, text=text, font=font, halign=halign, valign=valign)

    # --- сериализация ------------------------------------------------
    def _split_wires(self):
        ends = set()
        for a, b in self.wires:
            ends.add(a); ends.add(b)
        out = []
        for a, b in self.wires:
            pts = [a, b]
            for p in ends:
                if p in (a, b):
                    continue
                if a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1]):
                    pts.append(p)
                elif a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0]):
                    pts.append(p)
            pts = sorted(set(pts))
            out += list(zip(pts, pts[1:]))
        return sorted(set(out))

    def xml(self):
        s = ['  <circuit name=%s>' % quoteattr(self.name),
             '    <a name="circuit" val=%s/>' % quoteattr(self.name)]
        for a, b in self._split_wires():
            s.append('    <wire from="(%d,%d)" to="(%d,%d)"/>' % (a + b))
        for lib, name, loc, attrs in self.comps:
            if lib is None:
                s.append('    <comp loc="(%d,%d)" name=%s>' % (loc[0], loc[1], quoteattr(name)))
            else:
                s.append('    <comp lib="%d" loc="(%d,%d)" name=%s>' % (lib, loc[0], loc[1], quoteattr(name)))
            for k, v in attrs.items():
                if "\n" in str(v):   # многострочное значение (содержимое ROM) – текстом элемента
                    s.append('      <a name=%s>%s</a>' % (quoteattr(k), escape(str(v))))
                else:
                    s.append('      <a name=%s val=%s/>' % (quoteattr(k), quoteattr(str(v))))
            s.append('    </comp>')
        s.append('  </circuit>')
        return "\n".join(s)


def save(path, circuits, main=None):
    main = main or circuits[0].name
    s = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
         '<project source="2.7.1" version="1.0">',
         'This file is intended to be loaded by Logisim (http://www.cburch.com/logisim/).']
    for i, d in enumerate(LIB_DESC):
        s.append('  <lib desc="%s" name="%d"/>' % (d, i))
    s.append('  <main name=%s/>' % quoteattr(main))
    s.append('  <options>\n    <a name="gateUndefined" val="ignore"/>\n'
             '    <a name="simlimit" val="1000"/>\n    <a name="simrand" val="0"/>\n  </options>')
    s.append('  <mappings>\n    <tool lib="6" map="Button2" name="Menu Tool"/>\n'
             '    <tool lib="6" map="Ctrl Button1" name="Menu Tool"/>\n'
             '    <tool lib="6" map="Button3" name="Menu Tool"/>\n  </mappings>')
    s.append('  <toolbar>\n    <tool lib="6" name="Poke Tool"/>\n    <tool lib="6" name="Edit Tool"/>\n'
             '    <tool lib="6" name="Text Tool"/>\n    <sep/>\n    <tool lib="0" name="Pin"/>\n'
             '    <tool lib="0" name="Pin">\n      <a name="facing" val="west"/>\n'
             '      <a name="output" val="true"/>\n    </tool>\n  </toolbar>')
    for c in circuits:
        s.append(c.xml())
    s.append('</project>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s) + "\n")
