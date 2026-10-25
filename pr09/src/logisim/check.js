// Проверка схемы Logisim 2.7.1 «подбором входов» без GUI (Nashorn, Java 8):
//   jjs -J-Djava.awt.headless=true -cp logisim.jar check.js -- file.circ vectors.json [circuit]
// vectors.json: {"inputs": [...метки входных пинов...], "outputs": [...метки выходных пинов...],
//                "vectors": [[v1, v2, ...], ...]}
// Для каждого набора входов значения выставляются на входные пины, схема
// пересчитывается (propagate), и печатается строка таблицы: входы | выходы (hex).
var File = Java.type("java.io.File");
var Loader = Java.type("com.cburch.logisim.file.Loader");
var Project = Java.type("com.cburch.logisim.proj.Project");
var CircuitState = Java.type("com.cburch.logisim.circuit.CircuitState");
var Analyze = Java.type("com.cburch.logisim.circuit.Analyze");
var Pin = Java.type("com.cburch.logisim.std.wiring.Pin");
var Value = Java.type("com.cburch.logisim.data.Value");
var BitWidth = Java.type("com.cburch.logisim.data.BitWidth");
var StdAttr = Java.type("com.cburch.logisim.instance.StdAttr");
var Files = Java.type("java.nio.file.Files");
var Paths = Java.type("java.nio.file.Paths");
var JString = Java.type("java.lang.String");

var args = arguments;
var file = new Loader(null).openLogisimFile(new File(args[0]));
var spec = JSON.parse(new JString(Files.readAllBytes(Paths.get(args[1])), "UTF-8"));
var circ = args.length > 2 ? file.getCircuit(args[2]) : file.getMainCircuit();
var proj = new Project(file);
var st = new CircuitState(proj, circ);
st.getPropagator().propagate();

var pins = {};
var it = Analyze.getPinLabels(circ).entrySet().iterator();
while (it.hasNext()) { var e = it.next(); pins[e.getValue()] = e.getKey(); }

function width(name) { return pins[name].getAttributeValue(StdAttr.WIDTH).getWidth(); }
function fmt(v, w) {
  if (!v.isFullyDefined()) return v.toString();
  var n = v.toIntValue() >>> 0;
  if (w == 1) return "" + n;
  var s = n.toString(16); var d = Math.ceil(w / 4);
  while (s.length < d) s = "0" + s;
  return s;
}
var head = spec.inputs.join("\t") + "\t|\t" + spec.outputs.join("\t");
print(head);
for (var r = 0; r < spec.vectors.length; r++) {
  var vec = spec.vectors[r];
  st = new CircuitState(proj, circ);   // как в Analyze: новое состояние на каждый набор
  for (var i = 0; i < spec.inputs.length; i++) {
    var p = pins[spec.inputs[i]];
    if (!p) throw "no input pin " + spec.inputs[i];
    Pin.FACTORY.setValue(st.getInstanceState(p),
        Value.createKnown(BitWidth.create(width(spec.inputs[i])), vec[i]));
    st.getInstanceState(p).fireInvalidated();
  }
  st.getPropagator().propagate();
  var row = [];
  for (var i = 0; i < spec.inputs.length; i++) row.push(fmt(Value.createKnown(BitWidth.create(width(spec.inputs[i])), vec[i]), width(spec.inputs[i])));
  row.push("|");
  for (var j = 0; j < spec.outputs.length; j++) {
    var q = pins[spec.outputs[j]];
    if (!q) throw "no output pin " + spec.outputs[j];
    row.push(fmt(Pin.FACTORY.getValue(st.getInstanceState(q)), width(spec.outputs[j])));
  }
  print(row.join("\t"));
}
java.lang.System.exit(0);
