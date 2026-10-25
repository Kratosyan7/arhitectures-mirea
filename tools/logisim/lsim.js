// lsim.js — служебный скрипт для движка Logisim 2.7.1 (Nashorn, JDK 8).
//   jjs -cp logisim.jar lsim.js -- ports F            — компоненты: имя, loc, bounds, порты (x,y,ширина,in/out)
//   jjs -cp logisim.jar lsim.js -- run F C "шаги"     — симуляция: PIN=знач (hex 0x.. / bin 0b.. / dec), tick, cycle,
//                                                      print[:тег] (все выходные пины + регистры), reg (значения регистров)
var File = java.io.File;
var Loader = Java.type("com.cburch.logisim.file.Loader");
var Project = Java.type("com.cburch.logisim.proj.Project");
var CircuitState = Java.type("com.cburch.logisim.circuit.CircuitState");
var Pin = Java.type("com.cburch.logisim.std.wiring.Pin");
var Value = Java.type("com.cburch.logisim.data.Value");
var BitWidth = Java.type("com.cburch.logisim.data.BitWidth");
var StdAttr = Java.type("com.cburch.logisim.instance.StdAttr");
var Instance = Java.type("com.cburch.logisim.instance.Instance");
var InstanceComponent = Java.type("com.cburch.logisim.instance.InstanceComponent");
var args = arguments;
function load(f) { return new Loader(null).openLogisimFile(new File(f), new java.util.HashMap()); }

if (args[0] == "ports") {
    var lf = load(args[1]);
    var cs = lf.getCircuits().iterator();
    while (cs.hasNext()) {
        var circ = cs.next();
        var it = circ.getNonWires().iterator();
        while (it.hasNext()) {
            var c = it.next();
            var b = c.getBounds();
            var ends = [];
            var e = c.getEnds().iterator();
            while (e.hasNext()) {
                var en = e.next();
                var l = en.getLocation();
                ends.push(l.getX() + "," + l.getY() + "," + en.getWidth().getWidth() + "," + (en.isInput() ? "i" : "") + (en.isOutput() ? "o" : ""));
            }
            print(circ.getName() + "|" + c.getFactory().getName() + "|" + c.getLocation().getX() + "," + c.getLocation().getY()
                + "|" + b.getX() + "," + b.getY() + "," + b.getWidth() + "," + b.getHeight() + "|" + ends.join(";"));
        }
    }
} else if (args[0] == "run") {
    var lf = load(args[1]);
    var circ = lf.getCircuit(args[2]);
    var proj = new Project(lf);
    var st = new CircuitState(proj, circ);
    var prop = st.getPropagator();
    var pins = {}, regs = {};
    var it = circ.getNonWires().iterator();
    while (it.hasNext()) {
        var c = it.next();
        if (!(c instanceof InstanceComponent)) continue;
        var lab = c.getAttributeSet().getValue(StdAttr.LABEL);
        if (lab == null || lab == "") continue;
        var inst = Instance.getInstanceFor(c);
        if (c.getFactory() instanceof Pin) pins[lab] = inst;
        else if (c.getFactory().getName() == "Register" || c.getFactory().getName() == "Counter") regs[lab] = inst;
    }
    prop.propagate();
    function hex(v) { return v.isFullyDefined() ? java.lang.Integer.toHexString(v.toIntValue()).toUpperCase() : v.toString(); }
    function outs() {
        var r = [];
        Object.keys(pins).sort().forEach(function (k) {
            if (!Pin.FACTORY.isInputPin(pins[k])) r.push(k + "=" + hex(Pin.FACTORY.getValue(st.getInstanceState(pins[k]))));
        });
        return r.join(" ");
    }
    function regvals() {
        var r = [];
        Object.keys(regs).sort().forEach(function (k) {
            var d = st.getInstanceState(regs[k]).getData();
            var v = 0;
            if (d != null) {
                var fld = d.getClass().getDeclaredField("value");
                fld.setAccessible(true);
                v = fld.getInt(d);
            }
            r.push(k + "=" + java.lang.Integer.toHexString(v).toUpperCase());
        });
        return r.join(" ");
    }
    args[3].split(";").forEach(function (t) {
        t = t.trim();
        if (t == "") return;
        if (t == "tick") { prop.tick(); prop.propagate(); return; }
        if (t == "cycle") { prop.tick(); prop.propagate(); prop.tick(); prop.propagate(); return; }
        if (t.indexOf("reg:") == 0) {  // reg:PC=0xEBC — записать значение в регистр (как Poke в GUI)
            var kv2 = t.substring(4).split("=");
            var ri = regs[kv2[0]];
            if (ri == null) throw "нет регистра " + kv2[0];
            var rs = st.getInstanceState(ri);
            var dd = rs.getData();
            var f2 = dd.getClass().getDeclaredField("value");
            f2.setAccessible(true);
            f2.setInt(dd, parseInt(kv2[1].replace("0x", ""), 16));
            rs.fireInvalidated();
            prop.propagate();
            return;
        }
        if (t.indexOf("net:") == 0) {
            var want = t.substring(4).split(",");
            var res = [];
            var it2 = circ.getNonWires().iterator();
            var seen = {};
            while (it2.hasNext()) {
                var c2 = it2.next();
                if (c2.getFactory().getName() != "Tunnel") continue;
                var lab2 = c2.getAttributeSet().getValue(StdAttr.LABEL);
                if (want.indexOf(lab2) < 0 || seen[lab2]) continue;
                seen[lab2] = 1;
                res.push(lab2 + "=" + hex(st.getValue(c2.getLocation())));
            }
            print(res.join(" "));
            return;
        }
        if (t.indexOf("print") == 0) { print((t.length > 6 ? t.substring(6) + ": " : "") + outs() + " | " + regvals() + (prop.isOscillating() ? " [OSC]" : "")); return; }
        var kv = t.split("=");
        var inst = pins[kv[0]];
        if (inst == null) throw "нет пина " + kv[0];
        var w = inst.getAttributeValue(StdAttr.WIDTH);
        var s = kv[1], v;
        if (s.indexOf("0x") == 0) v = parseInt(s.substring(2), 16);
        else if (s.indexOf("0b") == 0) v = parseInt(s.substring(2), 2);
        else v = parseInt(s, 10);
        var ist = st.getInstanceState(inst);
        Pin.FACTORY.setValue(ist, Value.createKnown(w, v));
        ist.fireInvalidated();
        prop.propagate();
    });
}
java.lang.System.exit(0);
