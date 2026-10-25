// logitool.js — проверка и экспорт схем средствами самого Logisim 2.7.1.
// Запуск (Nashorn из JDK 8):
//   jjs -cp logisim.jar logitool.js -- <команда> <файл.circ> <схема> [аргументы]
// Команды:
//   ports  F C                      — список компонентов и координат их портов
//   table  F C in1,in2 out1,out2    — таблица истинности (движок Logisim)
//   run    F C "шаги"               — пошаговая симуляция: X=1 / tick / cycle / print / png:путь
//   export F C out.png scale [X=1,..] — картинка схемы (как File → Export Image)
var File = java.io.File;
var Loader = Java.type("com.cburch.logisim.file.Loader");
var Project = Java.type("com.cburch.logisim.proj.Project");
var CircuitState = Java.type("com.cburch.logisim.circuit.CircuitState");
var Pin = Java.type("com.cburch.logisim.std.wiring.Pin");
var Value = Java.type("com.cburch.logisim.data.Value");
var StdAttr = Java.type("com.cburch.logisim.instance.StdAttr");
var InstanceComponent = Java.type("com.cburch.logisim.instance.InstanceComponent");
var ComponentDrawContext = Java.type("com.cburch.logisim.comp.ComponentDrawContext");
var BufferedImage = Java.type("java.awt.image.BufferedImage");
var Color = Java.type("java.awt.Color");
var ImageIO = Java.type("javax.imageio.ImageIO");

var args = arguments;
var cmd = args[0], fname = args[1], cname = args[2];

function load(fname) {
    var loader = new Loader(null);
    return loader.openLogisimFile(new File(fname), new java.util.HashMap());
}
function findCircuit(lf, name) {
    var c = lf.getCircuit(name);
    if (c == null) throw "нет схемы " + name;
    return c;
}
function pins(circ) {
    var m = {};
    var it = circ.getNonWires().iterator();
    while (it.hasNext()) {
        var comp = it.next();
        if (comp.getFactory() instanceof Pin) {
            var lab = comp.getAttributeSet().getValue(StdAttr.LABEL);
            m[lab] = Java.type("com.cburch.logisim.instance.Instance").getInstanceFor(comp);
        }
    }
    return m;
}
var BitWidth = Java.type("com.cburch.logisim.data.BitWidth");
// многоразрядные значения печатаются в шестнадцатеричном виде
function v2s(v) {
    if (v.getWidth() > 1 && v.isFullyDefined()) {
        var x = v.toIntValue();
        if (x < 0) x += 4294967296;
        return "0x" + x.toString(16);
    }
    return v.toString();
}
function setPins(state, pm, assigns) {
    if (!assigns) return;
    assigns.split(",").forEach(function (a) {
        if (a.trim() == "") return;
        var kv = a.split("=");
        var inst = pm[kv[0]];
        if (inst == null) throw "нет пина " + kv[0];
        var w = inst.getAttributeValue(StdAttr.WIDTH).getWidth();
        var x = kv[1].indexOf("0x") == 0 ? parseInt(kv[1].substring(2), 16) : parseInt(kv[1], 10);
        var ist = state.getInstanceState(inst);
        Pin.FACTORY.setValue(ist, Value.createKnown(BitWidth.create(w), x));
        ist.fireInvalidated();   // без этого пропагатор не видит изменения входа
    });
}
function render(circ, state, out, scale) {
    var tmp = new BufferedImage(10, 10, BufferedImage.TYPE_INT_RGB);
    var bds = circ.getBounds(tmp.getGraphics()).expand(20);
    var w = Math.round(bds.getWidth() * scale), h = Math.round(bds.getHeight() * scale);
    var img = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
    var base = img.getGraphics();
    var g = base.create();
    g.setRenderingHint(java.awt.RenderingHints.KEY_ANTIALIASING, java.awt.RenderingHints.VALUE_ANTIALIAS_ON);
    g.setRenderingHint(java.awt.RenderingHints.KEY_TEXT_ANTIALIASING, java.awt.RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
    g.setColor(Color.white); g.fillRect(0, 0, w, h); g.setColor(Color.black);
    g.scale(scale, scale); g.translate(-bds.getX(), -bds.getY());
    var ctx = new ComponentDrawContext(new javax.swing.JPanel(), circ, state, base, g, false);
    circ.draw(ctx, null);
    ImageIO.write(img, "PNG", new File(out));
    print("saved " + out + " " + w + "x" + h);
}

if (cmd == "ports") {
    var lf = load(fname), circ = findCircuit(lf, cname);
    var it = circ.getNonWires().iterator();
    while (it.hasNext()) {
        var c = it.next();
        var ends = [];
        var e = c.getEnds().iterator();
        while (e.hasNext()) ends.push(e.next().getLocation().toString());
        print(c.getFactory().getName() + " @" + c.getLocation() + " : " + ends.join(" "));
    }
} else if (cmd == "table") {
    var lf = load(fname), circ = findCircuit(lf, cname);
    var proj = new Project(lf);
    var pm = pins(circ);
    var ins = args[3].split(","), outs = args[4].split(",");
    print(ins.join(" ") + " | " + outs.join(" "));
    var n = ins.length;
    for (var r = 0; r < (1 << n); r++) {
        var st = new CircuitState(proj, circ);
        var row = [];
        for (var j = 0; j < n; j++) {
            var bit = (r >> (n - 1 - j)) & 1;
            Pin.FACTORY.setValue(st.getInstanceState(pm[ins[j]]), bit ? Value.TRUE : Value.FALSE);
            row.push(bit);
        }
        st.getPropagator().propagate();
        var o = outs.map(function (p) { return v2s(Pin.FACTORY.getValue(st.getInstanceState(pm[p]))); });
        print(row.join(" ") + " | " + o.join(" ") + (st.getPropagator().isOscillating() ? " OSC" : ""));
    }
} else if (cmd == "run") {
    var lf = load(fname), circ = findCircuit(lf, cname);
    var proj = new Project(lf);
    var pm = pins(circ);
    var st = new CircuitState(proj, circ);
    var prop = st.getPropagator();
    prop.propagate();
    var outs = [];
    for (var k in pm) if (!Pin.FACTORY.isInputPin(pm[k])) outs.push(k);
    outs.sort();
    if (args.length > 4) outs = args[4].split(",");
    var step = 0;
    args[3].split(";").forEach(function (t) {
        t = t.trim();
        if (t == "") return;
        if (t.indexOf("png:") == 0) { render(circ, st, t.substring(4), 1.5); return; }
        if (t == "tick") { prop.tick(); prop.propagate(); return; }
        if (t == "cycle") { prop.tick(); prop.propagate(); prop.tick(); prop.propagate(); return; }
        if (t.indexOf("print") == 0) {
            var tag = t.length > 5 ? t.substring(6) : "";
            print(tag + " " + outs.map(function (p) { return p + "=" + v2s(Pin.FACTORY.getValue(st.getInstanceState(pm[p]))); }).join(" "));
            return;
        }
        setPins(st, pm, t);
        prop.propagate();
    });
} else if (cmd == "pinorder") {
    // порядок столбцов в режиме "java -jar logisim.jar F -tty table" (как в TtyInterface)
    var lf = load(fname);
    var circ = lf.getMainCircuit();
    var Analyze = Java.type("com.cburch.logisim.circuit.Analyze");
    var m = Analyze.getPinLabels(circ);
    var it = m.entrySet().iterator();
    var outs = [];
    while (it.hasNext()) {
        var e = it.next();
        if (!Pin.FACTORY.isInputPin(e.getKey()) && e.getValue() != "halt") outs.push(e.getValue());
    }
    print(outs.join(","));
} else if (cmd == "export") {
    var lf = load(fname), circ = findCircuit(lf, cname);
    var proj = new Project(lf);
    var st = new CircuitState(proj, circ);
    setPins(st, pins(circ), args[5] || "");
    st.getPropagator().propagate();
    render(circ, st, args[3], parseFloat(args[4]));
}

// Project создаёт поток симулятора, без явного выхода jjs не завершается
java.lang.System.exit(0);
