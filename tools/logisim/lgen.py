"""Генератор схем Logisim 2.7.1 (.circ) с соединением через туннели.

Компоненты размещаются явно (координаты на сетке 10), а их порты соединяются
с «цепями» (net) по имени: к каждому подключённому порту автоматически
пристраивается короткий провод и туннель (Tunnel) с именем цепи. Точные
координаты портов берутся у самого Logisim (lsim.js ports), поэтому схема
всегда собрана корректно. Проверка поведения — lsim.js run.
"""
import os
import subprocess
from xml.sax.saxutils import quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
JAR = os.path.join(ROOT, ".tools", "logisim", "logisim.jar")
LSIM = os.path.join(HERE, "lsim.js")
LIBS = {"wiring": 0, "gates": 1, "plexers": 2, "arith": 3, "memory": 4, "io": 5, "base": 6}
STEP = {"east": (1, 0), "west": (-1, 0), "north": (0, -1), "south": (0, 1)}
OPPOSITE = {"east": "west", "west": "east", "north": "south", "south": "north"}


def jjs(*args):
    out = subprocess.run(["jjs", "-cp", JAR, LSIM, "--", *args], capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(out.stderr + out.stdout)
    return out.stdout


class Comp:
    sub = None  # для подсхемы: объект Circuit

    def __init__(self, lib, name, loc, attrs, conns, stub):
        self.lib, self.name, self.loc, self.attrs = lib, name, loc, attrs
        self.conns = conns  # {индекс порта: имя цепи}
        self.stub = stub


class Circuit:
    def __init__(self, name):
        self.name = name
        self.comps = []
        self.wires = []
        self.extra = []  # туннели, достроенные автоматически

    def add(self, lib, name, loc, conns=None, stub=20, **attrs):
        c = Comp(LIBS[lib], name, loc, {k: str(v) for k, v in attrs.items()}, conns or {}, stub)
        self.comps.append(c)
        return c

    def sub(self, circ, loc, conns, stub=20, **attrs):
        """Экземпляр подсхемы; conns = {метка пина подсхемы: цепь}."""
        c = Comp(None, circ.name, loc, {k: str(v) for k, v in attrs.items()}, conns, stub)
        c.sub = circ
        self.comps.append(c)
        return c

    def wire(self, *pts):
        for p, q in zip(pts, pts[1:]):
            assert p[0] == q[0] or p[1] == q[1], (p, q)
            self.wires.append((p, q))

    # --- удобные обёртки ---
    def pin_in(self, loc, label, net=None, width=1, facing="east", labelloc="west"):
        return self.add("wiring", "Pin", loc, {0: net or label}, tristate="false", label=label,
                        width=width, facing=facing, labelloc=labelloc)

    def pin_out(self, loc, label, net=None, width=1, facing="west", labelloc="east"):
        return self.add("wiring", "Pin", loc, {0: net or label}, output="true", label=label,
                        width=width, facing=facing, labelloc=labelloc)

    def const(self, loc, value, net, width=1, facing="east"):
        return self.add("wiring", "Constant", loc, {0: net}, width=width, value=hex(value), facing=facing)

    def text(self, loc, text, font="SansSerif bold 16"):
        return self.add("base", "Text", loc, text=text, font=font)

    def tunnel(self, loc, label, facing, width=1):
        self.extra.append(("wiring", "Tunnel", loc, dict(label=label, facing=facing, width=str(width))))

    def xml(self):
        L = [f'  <circuit name={quoteattr(self.name)}>',
             f'    <a name="circuit" val={quoteattr(self.name)}/>',
             '    <a name="clabel" val=""/>', '    <a name="clabelup" val="east"/>',
             '    <a name="clabelfont" val="SansSerif plain 12"/>']
        for p, q in self.wires:
            L.append(f'    <wire from="({p[0]},{p[1]})" to="({q[0]},{q[1]})"/>')
        items = [(c.lib, c.name, c.loc, c.attrs) for c in self.comps]
        items += [(LIBS[l], n, loc, a) for l, n, loc, a in self.extra]
        for lib, name, loc, attrs in items:
            libattr = "" if lib is None else f' lib="{lib}"'
            L.append(f'    <comp{libattr} loc="({loc[0]},{loc[1]})" name={quoteattr(name)}>')
            for k, v in attrs.items():
                L.append(f'      <a name="{k}" val={quoteattr(v)}/>')
            L.append('    </comp>')
        L.append('  </circuit>')
        return "\n".join(L)


def project_xml(circuits, main):
    head = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            '<project source="2.7.1" version="1.0">',
            'This file is intended to be loaded by Logisim (http://www.cburch.com/logisim/).',
            '  <lib desc="#Wiring" name="0"/>', '  <lib desc="#Gates" name="1"/>',
            '  <lib desc="#Plexers" name="2"/>', '  <lib desc="#Arithmetic" name="3"/>',
            '  <lib desc="#Memory" name="4"/>', '  <lib desc="#I/O" name="5"/>',
            '  <lib desc="#Base" name="6"/>',
            f'  <main name={quoteattr(main)}/>',
            '  <options>', '    <a name="gateUndefined" val="ignore"/>',
            '    <a name="simlimit" val="1000"/>', '    <a name="simrand" val="0"/>', '  </options>',
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
    return "\n".join(head + [c.xml() for c in circuits] + ['</project>', ''])


def _side(px, py, bx, by, bw, bh):
    d = {"west": px - bx, "east": bx + bw - px, "north": py - by, "south": by + bh - py}
    return min(d, key=d.get)


def _sub_conns(comp, ends, bds):
    """Сопоставляет метки пинов подсхемы с портами экземпляра (вид по умолчанию:
    входы — слева, выходы — справа, по возрастанию y)."""
    pins = [c for c in comp.sub.comps if c.name == "Pin"]
    ins = sorted((p for p in pins if p.attrs.get("output") != "true"), key=lambda p: (p.loc[1], p.loc[0]))
    outs = sorted((p for p in pins if p.attrs.get("output") == "true"), key=lambda p: (p.loc[1], p.loc[0]))
    idx = list(range(len(ends)))
    west = sorted((i for i in idx if _side(int(ends[i][0]), int(ends[i][1]), *bds) == "west"),
                  key=lambda i: int(ends[i][1]))
    east = sorted((i for i in idx if _side(int(ends[i][0]), int(ends[i][1]), *bds) == "east"),
                  key=lambda i: int(ends[i][1]))
    assert len(west) == len(ins) and len(east) == len(outs), (len(west), len(ins), len(east), len(outs))
    m = {}
    for p, i in list(zip(ins, west)) + list(zip(outs, east)):
        lab = p.attrs["label"]
        if lab in comp.conns:
            net = comp.conns[lab]
            if not isinstance(net, tuple):  # порты подсхемы идут с шагом 10 — чередуем отводы
                side = "west" if i in west else "east"
                pos = (west if i in west else east).index(i)
                net = (net, side, comp.stub if pos % 2 == 0 else comp.stub + 50)
            m[i] = net
    return m


def build(circuits, path, main=None):
    """Пишет .circ: сначала без туннелей, затем достраивает туннели по реальным портам."""
    main = main or circuits[0].name
    for c in circuits:
        c.extra = []
    with open(path, "w", encoding="utf-8") as f:
        f.write(project_xml(circuits, main))
    info = {}
    for line in jjs("ports", path).splitlines():
        cname, fname, loc, bds, ends = line.split("|")
        x, y = map(int, loc.split(","))
        info[(cname, fname, x, y)] = ([int(v) for v in bds.split(",")],
                                      [e.split(",") for e in ends.split(";")] if ends else [])
    names = {"Pin": "Pin", "Constant": "Constant"}
    for circ in circuits:
        for comp in circ.comps:
            if not comp.conns:
                continue
            key = (circ.name, names.get(comp.name, comp.name), comp.loc[0], comp.loc[1])
            hits = [v for k, v in info.items() if k[0] == key[0] and k[2:] == key[2:]]
            if not hits:
                raise KeyError(f"нет компонента {key}")
            bds, ends = hits[0]
            conns = comp.conns
            if comp.sub is not None:
                conns = _sub_conns(comp, ends, bds)
            for idx, net in conns.items():
                px, py, w = int(ends[idx][0]), int(ends[idx][1]), int(ends[idx][2])
                side = _side(px, py, *bds)
                s = comp.stub
                turn = None
                if isinstance(net, tuple):  # (имя, сторона[, длина[, поворот, длина2]])
                    net, side, *rest = net
                    s = rest[0] if rest else s
                    if len(rest) >= 3:
                        turn = (rest[1], rest[2])
                dx, dy = STEP[side]
                end = (px + dx * s, py + dy * s)
                circ.wire((px, py), end)
                if turn:
                    tx, ty = STEP[turn[0]]
                    end2 = (end[0] + tx * turn[1], end[1] + ty * turn[1])
                    circ.wire(end, end2)
                    end, side = end2, turn[0]
                circ.tunnel(end, net, OPPOSITE[side], w)
    with open(path, "w", encoding="utf-8") as f:
        f.write(project_xml(circuits, main))
    return path


def run(path, circuit, steps):
    return jjs("run", path, circuit, steps)
