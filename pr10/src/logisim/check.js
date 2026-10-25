// Проверка эквивалентности двух схем tolower на всех 256 байтах (один запуск JVM).
// jjs -cp .tools/logisim/logisim.jar pr10/src/logisim/check.js -- pr10/src/logisim/pr10_tolower.circ
var File = java.io.File, Loader = Java.type("com.cburch.logisim.file.Loader"),
    Project = Java.type("com.cburch.logisim.proj.Project"),
    CircuitState = Java.type("com.cburch.logisim.circuit.CircuitState"),
    Pin = Java.type("com.cburch.logisim.std.wiring.Pin"),
    Value = Java.type("com.cburch.logisim.data.Value"),
    BitWidth = Java.type("com.cburch.logisim.data.BitWidth"),
    StdAttr = Java.type("com.cburch.logisim.instance.StdAttr"),
    Instance = Java.type("com.cburch.logisim.instance.Instance"),
    InstanceComponent = Java.type("com.cburch.logisim.instance.InstanceComponent");
var lf = new Loader(null).openLogisimFile(new File(arguments[0]), new java.util.HashMap());
function pins(cn) {
    var c = lf.getCircuit(cn), m = {}, it = c.getNonWires().iterator();
    while (it.hasNext()) {
        var k = it.next();
        if (!(k instanceof InstanceComponent)) continue;
        var l = k.getAttributeSet().getValue(StdAttr.LABEL);
        if (k.getFactory() instanceof Pin && l) m[l] = Instance.getInstanceFor(k);
    }
    return { c: c, m: m };
}
function run(cn, val) {
    var p = pins(cn), st = new CircuitState(new Project(lf), p.c);
    var is = st.getInstanceState(p.m["c"]);
    Pin.FACTORY.setValue(is, Value.createKnown(BitWidth.create(8), val));
    is.fireInvalidated();
    st.getPropagator().propagate();
    return Pin.FACTORY.getValue(st.getInstanceState(p.m["out"])).toIntValue();
}
var bad = 0;
for (var c = 0; c < 256; c++) {
    var exp = (c >= 0x41 && c <= 0x5A) ? c + 0x20 : c;
    var b = run("tolower_branch", c), n = run("tolower_nobranch", c);
    if (b != exp || n != exp) {
        bad++;
        if (bad <= 5) print("FAIL c=" + c.toString(16) + " b=" + b.toString(16) + " n=" + n.toString(16));
    }
}
print(bad == 0 ? "OK: обе схемы (с ветвлением и без) совпали с эталоном на всех 256 байтах"
                : "НЕ СОВПАЛО: " + bad);
java.lang.System.exit(0);
