// Предпросмотр схемы без GUI: рисует схему в PNG (как «Экспорт изображения» Logisim).
//   jjs -J-Djava.awt.headless=true -cp logisim.jar render.js -- file.circ out.png [circuit] [pin=value,...]
var File = Java.type("java.io.File");
var Loader = Java.type("com.cburch.logisim.file.Loader");
var Project = Java.type("com.cburch.logisim.proj.Project");
var CircuitState = Java.type("com.cburch.logisim.circuit.CircuitState");
var Analyze = Java.type("com.cburch.logisim.circuit.Analyze");
var Pin = Java.type("com.cburch.logisim.std.wiring.Pin");
var Value = Java.type("com.cburch.logisim.data.Value");
var BitWidth = Java.type("com.cburch.logisim.data.BitWidth");
var StdAttr = Java.type("com.cburch.logisim.instance.StdAttr");
var CDC = Java.type("com.cburch.logisim.comp.ComponentDrawContext");
var BufferedImage = Java.type("java.awt.image.BufferedImage");
var Color = Java.type("java.awt.Color");
var RH = Java.type("java.awt.RenderingHints");
var ImageIO = Java.type("javax.imageio.ImageIO");
var args = arguments;
var file = new Loader(null).openLogisimFile(new File(args[0]));
var circ = (args.length > 2 && args[2] != "") ? file.getCircuit(args[2]) : file.getMainCircuit();
var proj = new Project(file);
var st = new CircuitState(proj, circ);
if (args.length > 3) {
  var pins = {};
  var it = Analyze.getPinLabels(circ).entrySet().iterator();
  while (it.hasNext()) { var e = it.next(); pins[e.getValue()] = e.getKey(); }
  args[3].split(",").forEach(function (kv) {
    var p = kv.split("="); var pin = pins[p[0]];
    var w = pin.getAttributeValue(StdAttr.WIDTH).getWidth();
    Pin.FACTORY.setValue(st.getInstanceState(pin), Value.createKnown(BitWidth.create(w), parseInt(p[1])));
  });
}
st.getPropagator().propagate();
var tmp = new BufferedImage(10, 10, BufferedImage.TYPE_INT_RGB);
var bds = circ.getBounds(tmp.getGraphics()).expand(20);
var scale = 1.5;
var img = new BufferedImage(Math.round(bds.getWidth() * scale), Math.round(bds.getHeight() * scale), BufferedImage.TYPE_INT_RGB);
var base = img.getGraphics();
var g = base.create();
g.setRenderingHint(RH.KEY_ANTIALIASING, RH.VALUE_ANTIALIAS_ON);
g.setRenderingHint(RH.KEY_TEXT_ANTIALIASING, RH.VALUE_TEXT_ANTIALIAS_ON);
g.setColor(Color.white); g.fillRect(0, 0, img.getWidth(), img.getHeight()); g.setColor(Color.black);
g.scale(scale, scale); g.translate(-bds.getX(), -bds.getY());
circ.draw(new CDC(null, circ, st, base, g, false), null);
ImageIO.write(img, "png", new File(args[1]));
java.lang.System.exit(0);
