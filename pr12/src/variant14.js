// Практическая работа 12, вариант 14: множество Жюлиа (формула 12.3).
// Подключается к стенду index.html последним <script>. Все параметры
// варианта задаются в одном объекте VARIANT, из него генерируется код
// для обоих редакторов: CPU (JavaScript) и GPU (WGSL).

const VARIANT = {
  number: 14,
  mode: 'Julia set (smooth coloring)',
  width: 1920,          // разрешение по варианту
  height: 1080,
  kRe: -0.8,            // комплексная константа k = kRe + i*kIm
  kIm: 0.156,
  zoom: 1.0,            // масштаб: видимая полуширина по Im равна 1/zoom
  offsetX: 0.0,         // смещение центра кадра (Re)
  offsetY: 0.0,         // смещение центра кадра (Im)
  maxIter: 300,         // предел итераций
  bailout: 4.0,         // условие ухода |z|^2 > 4
};

// Число -> литерал f32 для WGSL (обязательно с точкой).
function wgslFloat(v) {
  const s = String(v);
  return /[.eE]/.test(s) ? s : s + '.0';
}

// Тело CPU-ядра. f32 = true — "эмуляция" одинарной точности через
// Math.fround (используется только в дополнительном эксперименте).
function makeCpuCode(p = VARIANT, f32 = false) {
  const w = f32 ? (e) => `Math.fround(${e})` : (e) => e;   // округление до float32
  const pre = f32
    ? `const fcx = ${w(`${w(`${w('uvx')} * 2.0`)} - 1.0`)}, fcy = ${w(`${w(`${w('uvy')} * 2.0`)} - 1.0`)};\n`
    : '';
  const X = f32 ? 'fcx' : 'cx', Y = f32 ? 'fcy' : 'cy';
  return `// Вариант ${p.number}: множество Жюлиа, k = ${p.kRe} + ${p.kIm}i${f32 ? ' (эмуляция float32)' : ''}
const K_RE = ${w(p.kRe)}, K_IM = ${w(p.kIm)};
const ZOOM = ${p.zoom}, OFF_X = ${p.offsetX}, OFF_Y = ${p.offsetY};
const MAX_ITER = ${p.maxIter}, BAILOUT = ${p.bailout};
const aspect = ${w('width / height')};
${pre}// пиксель -> комплексная плоскость (ось Im направлена вверх)
let zx = ${w(`${w(`${w(`${X} * aspect`)} / ZOOM`)} + OFF_X`)};
let zy = ${w(`${w(`-${Y} / ZOOM`)} + OFF_Y`)};
let r2 = ${w(`${w('zx * zx')} + ${w('zy * zy')}`)};
let i = 0;
while (i < MAX_ITER && r2 <= BAILOUT) {   // z = z^2 + k
  const t = ${w(`${w(`${w('zx * zx')} - ${w('zy * zy')}`)} + K_RE`)};
  zy = ${w(`${w(`${w('2.0 * zx')} * zy`)} + K_IM`)};
  zx = t;
  r2 = ${w(`${w('zx * zx')} + ${w('zy * zy')}`)};
  i++;
}
if (i >= MAX_ITER) return rgba(0.0, 0.0, 0.0, 1.0);   // точка множества
// гладкая окраска: дробное число итераций
const mu = i + 1.0 - Math.log2(0.5 * Math.log2(r2));
const s = Math.log(mu + 1.0) / Math.log(MAX_ITER + 1.0);
const col = palette(s);
const v = smoothstep(0.0, 0.5, s);
return rgba(col[0] * v, col[1] * v, col[2] * v, 1.0);`;
}

// Тело GPU-ядра (WGSL). Переменные x, y, uvx, uvy, cx, cy и
// params.width/height объявлены в шаблоне стенда (studentKernel).
function makeGpuCode(p = VARIANT) {
  return `// Вариант ${p.number}: множество Жюлиа, k = ${p.kRe} + ${p.kIm}i
let K = vec2<f32>(${wgslFloat(p.kRe)}, ${wgslFloat(p.kIm)});
let ZOOM = ${wgslFloat(p.zoom)};
let OFF = vec2<f32>(${wgslFloat(p.offsetX)}, ${wgslFloat(p.offsetY)});
let MAX_ITER = ${p.maxIter}i;
let BAILOUT = ${wgslFloat(p.bailout)};
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
return rgba(col.x * v, col.y * v, col.z * v, 1.0);`;
}

// Загрузить вариант в стенд: разрешение, источник, код в редакторы.
function loadVariant(p = VARIANT, opts = {}) {
  const width = opts.width || p.width;
  const height = opts.height || p.height;
  resolutionWidthEl.value = String(width);
  resolutionHeightEl.value = String(height);
  if (sourcePixels) applyRequestedResolutionToCurrentSource();
  else prepareInitialSource();
  cpuCodeEl.value = makeCpuCode(p, !!opts.cpuF32);
  gpuCodeEl.value = makeGpuCode(p);
  log(`Загружен вариант ${p.number}: ${p.mode}, ${width} × ${height}, k = ${p.kRe} + ${p.kIm}i, maxIter = ${p.maxIter}${opts.cpuF32 ? ', CPU: эмуляция float32' : ''}.`);
}

// Один прогон CPU + GPU (кнопка «Запустить CPU + GPU») и сбор метрик
// со страницы; используется скриптом автоматических замеров.
async function benchVariant(opts = {}) {
  loadVariant(VARIANT, opts);
  await runBoth();
  const a = lastCpuPixels, b = lastGpuPixels;
  let px = 0, px16 = 0, px64 = 0;
  for (let i = 0; i < a.length; i += 4) {
    const d = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2]));
    if (d > 0) px++;
    if (d > 16) px16++;
    if (d > 64) px64++;
  }
  const n = a.length / 4;
  return {
    width: sourceWidth, height: sourceHeight, cpuF32: !!opts.cpuF32,
    cpuMs: parseFloat(cpuTimeEl.dataset.value), gpuMs: parseFloat(gpuTimeEl.dataset.value),
    speedup: speedupEl.textContent, meanDiff: meanDiffEl.textContent, maxDiff: maxDiffEl.textContent,
    diffPixelsPct: 100 * px / n, diff16Pct: 100 * px16 / n, diff64Pct: 100 * px64 / n,
  };
}

// Кнопка «Загрузить вариант 14» рядом с кнопками запуска.
(function addVariantButton() {
  const btn = document.createElement('button');
  btn.id = 'variantBtn';
  btn.className = 'btn-primary';
  btn.textContent = `Загрузить вариант ${VARIANT.number}`;
  btn.addEventListener('click', () => loadVariant());
  document.getElementById('bothBtn').after(btn);
})();
