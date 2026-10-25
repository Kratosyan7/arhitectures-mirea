// Вариант 14: множество Жюлиа, k = -0.8 + 0.156i
let K = vec2<f32>(-0.8, 0.156);
let ZOOM = 1.0;
let OFF = vec2<f32>(0.0, 0.0);
let MAX_ITER = 300i;
let BAILOUT = 4.0;
let aspect = f32(params.width) / f32(params.height);
var zx = cx * aspect / ZOOM + OFF.x;
var zy = -cy / ZOOM + OFF.y;
var r2 = zx * zx + zy * zy;
var i = 0i;
loop {                                   // z = z^2 + k
  if (i >= MAX_ITER || r2 > BAILOUT) { break; }
  let t = zx * zx - zy * zy + K.x;
  zy = 2.0 * zx * zy + K.y;
  zx = t;
  r2 = zx * zx + zy * zy;
  i = i + 1i;
}
if (i >= MAX_ITER) { return rgba(0.0, 0.0, 0.0, 1.0); }
let mu = f32(i) + 1.0 - log2(0.5 * log2(r2));
let s = log(mu + 1.0) / log(f32(MAX_ITER) + 1.0);
let col = palette(s);
let v = smoothstep1(0.0, 0.5, s);
return rgba(col.x * v, col.y * v, col.z * v, 1.0);
