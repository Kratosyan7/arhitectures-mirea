// Вариант 14: множество Жюлиа, k = -0.8 + 0.156i
const K_RE = -0.8, K_IM = 0.156;
const ZOOM = 1, OFF_X = 0, OFF_Y = 0;
const MAX_ITER = 300, BAILOUT = 4;
const aspect = width / height;
// пиксель -> комплексная плоскость (ось Im направлена вверх)
let zx = cx * aspect / ZOOM + OFF_X;
let zy = -cy / ZOOM + OFF_Y;
let r2 = zx * zx + zy * zy;
let i = 0;
while (i < MAX_ITER && r2 <= BAILOUT) {   // z = z^2 + k
  const t = zx * zx - zy * zy + K_RE;
  zy = 2.0 * zx * zy + K_IM;
  zx = t;
  r2 = zx * zx + zy * zy;
  i++;
}
if (i >= MAX_ITER) return rgba(0.0, 0.0, 0.0, 1.0);   // точка множества
// гладкая окраска: дробное число итераций
const mu = i + 1.0 - Math.log2(0.5 * Math.log2(r2));
const s = Math.log(mu + 1.0) / Math.log(MAX_ITER + 1.0);
const col = palette(s);
const v = smoothstep(0.0, 0.5, s);
return rgba(col[0] * v, col[1] * v, col[2] * v, 1.0);
