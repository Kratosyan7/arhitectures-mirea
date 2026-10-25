// sim.js — потактовый прогон схемы pr11.circ без GUI (Nashorn, Java 8):
//   jjs -J-Djava.awt.headless=true -cp logisim.jar sim.js -- pr11.circ [схема]
// Печатает значения выходных пинов в десятичном виде после каждого такта
// (такт = два переключения генератора CLK, запись по переднему фронту),
// пока выход halt не станет 1 (или 40 тактов).
var File = java.io.File;
var Loader = Java.type("com.cburch.logisim.file.Loader");
var Project = Java.type("com.cburch.logisim.proj.Project");
var CircuitState = Java.type("com.cburch.logisim.circuit.CircuitState");
var Analyze = Java.type("com.cburch.logisim.circuit.Analyze");
var Pin = Java.type("com.cburch.logisim.std.wiring.Pin");

var lf = new Loader(null).openLogisimFile(new File(arguments[0]), new java.util.HashMap());
var circ = arguments.length > 1 ? lf.getCircuit(arguments[1]) : lf.getMainCircuit();
var st = new CircuitState(new Project(lf), circ);
var prop = st.getPropagator();
prop.propagate();

var names = [], pins = {};
var it = Analyze.getPinLabels(circ).entrySet().iterator();
while (it.hasNext()) {
    var e = it.next();
    if (!Pin.FACTORY.isInputPin(e.getKey())) { names.push(e.getValue()); pins[e.getValue()] = e.getKey(); }
}
// регистры с метками (ACC, S0…S3, RES): значение на выходе Q = в точке привязки
var StdAttr = Java.type("com.cburch.logisim.instance.StdAttr");
var regs = [];
var ci = circ.getNonWires().iterator();
while (ci.hasNext()) {
    var c = ci.next();
    if (c.getFactory().getName() == "Register") {
        var lab = c.getAttributeSet().getValue(StdAttr.LABEL);
        if (lab && lab != "") regs.push([lab, c.getLocation()]);
    }
}
regs.sort(function (a, b) { return a[0] < b[0] ? -1 : 1; });
function regval(r) {
    var v = st.getValue(r[1]);
    return v.isFullyDefined() ? "" + (v.toIntValue() >>> 0) : v.toString();
}
function val(n) {
    var v = Pin.FACTORY.getValue(st.getInstanceState(pins[n]));
    return v.isFullyDefined() ? "" + (v.toIntValue() >>> 0) : v.toString();
}
function pad(s, w) { s = "" + s; while (s.length < w) s = " " + s; return s; }
var shown = names.filter(function (n) { return n != "halt"; });
var cols = shown.map(function (n) { return pad(n, 9); }).concat(regs.map(function (r) { return pad(r[0], 5); }));
print(pad("такт", 4) + " | " + cols.join(" | "));
for (var cyc = 0; cyc <= 40; cyc++) {
    var row = shown.map(function (n) { return pad(val(n), 9); }).concat(regs.map(function (r) { return pad(regval(r), 5); }));
    print(pad(cyc, 4) + " | " + row.join(" | "));
    if (pins["halt"] && val("halt") == "1") { print("halt = 1: оба вычисления завершены"); break; }
    if (!pins["halt"] && pins["DONE"] && val("DONE") == "1") { print("DONE = 1"); break; }
    prop.tick(); prop.propagate(); prop.tick(); prop.propagate();
}
java.lang.System.out.flush(); java.lang.Runtime.getRuntime().halt(0);
