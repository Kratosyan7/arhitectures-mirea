"""Автоматические замеры для ПР 12 (вариант 14, множество Жюлиа).

Требуется запущенный сервер (python3 start_server.py 8112 --no-browser) и
headless Chrome с WebGPU и удалённой отладкой на порту 9333:

  google-chrome --headless=new --remote-debugging-port=9333 \
      --enable-unsafe-webgpu --enable-features=Vulkan --use-angle=vulkan \
      --ignore-gpu-blocklist --user-data-dir=<tmp> about:blank

Для каждого разрешения стенд выполняет «Запустить CPU + GPU»
(функция benchVariant из variant14.js) несколько раз; первый прогон
считается прогревом (cold), по остальным берётся медиана.
"""
import base64
import json
import statistics
import sys
import time

import numpy as np
from PIL import Image

from cdp import Tab

URL = 'http://localhost:8112/index.html'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'results'
RESOLUTIONS = [(640, 360, 6), (1280, 720, 6), (1920, 1080, 6),
               (2560, 1440, 4), (3840, 2160, 4), (7680, 4320, 3)]
IMG = '../img'


def main():
    tab = Tab()
    tab.set_viewport(1400, 1000)
    tab.goto(URL, wait=2.0)
    adapter = tab.eval("""(async () => {
        const a = await navigator.gpu.requestAdapter();
        return { vendor: a.info.vendor, architecture: a.info.architecture,
                 ua: navigator.userAgent, cores: navigator.hardwareConcurrency };
    })()""")
    print('adapter:', adapter, flush=True)

    rows = []
    for w, h, reps in RESOLUTIONS:
        runs = []
        for r in range(reps):
            res = tab.eval(f'benchVariant({{width: {w}, height: {h}}})')
            runs.append(res)
            print(f'{w}x{h} run {r}: cpu={res["cpuMs"]:.1f} ms gpu={res["gpuMs"]:.2f} ms '
                  f'mean={res["meanDiff"]} max={res["maxDiff"]} diffpx={res["diffPixelsPct"]:.3f}%',
                  flush=True)
        warm = runs[1:]
        row = {
            'width': w, 'height': h, 'mpix': w * h / 1e6, 'reps': reps,
            'cpu_cold': runs[0]['cpuMs'], 'gpu_cold': runs[0]['gpuMs'],
            'cpu_med': statistics.median(x['cpuMs'] for x in warm),
            'gpu_med': statistics.median(x['gpuMs'] for x in warm),
            'gpu_min': min(x['gpuMs'] for x in warm),
            'meanDiff': runs[-1]['meanDiff'], 'maxDiff': runs[-1]['maxDiff'],
            'diffPixelsPct': runs[-1]['diffPixelsPct'], 'diff16Pct': runs[-1]['diff16Pct'],
            'diff64Pct': runs[-1]['diff64Pct'],
            'runs': runs,
        }
        row['speedup_med'] = row['cpu_med'] / row['gpu_med']
        rows.append(row)
        if (w, h) in ((1920, 1080), (640, 360), (3840, 2160)):
            tab.screenshot(f'{IMG}/page_{w}x{h}.png')

    # Основной скриншот: разрешение варианта 1920x1080 + сохранение полных кадров.
    res = tab.eval('benchVariant({width: 1920, height: 1080})')
    print('final 1920x1080:', res, flush=True)
    tab.screenshot(f'{IMG}/page_variant.png')
    dump_frames(tab, 'f64')

    # Доп. эксперимент: CPU с эмуляцией float32 (Math.fround).
    f32 = []
    for w, h in ((640, 360), (1920, 1080), (3840, 2160)):
        r = tab.eval(f'benchVariant({{width: {w}, height: {h}, cpuF32: true}})')
        print('cpuF32', w, h, r, flush=True)
        f32.append(r)
    tab.eval('benchVariant({width: 1920, height: 1080, cpuF32: true})')
    tab.screenshot(f'{IMG}/page_cpu_f32.png')
    dump_frames(tab, 'f32')

    with open(f'{OUT}.json', 'w', encoding='utf-8') as f:
        json.dump({'adapter': adapter, 'rows': rows, 'cpuF32': f32,
                   'console': tab.console, 'date': time.strftime('%Y-%m-%d %H:%M:%S')},
                  f, ensure_ascii=False, indent=1)
    tab.close()


def dump_frames(tab, tag):
    """Сохраняет полные кадры CPU и GPU и карту отличий (для анализа)."""
    js = """(() => {
      const enc = (u8) => { let s = ''; const CH = 0x8000;
        for (let i = 0; i < u8.length; i += CH) s += String.fromCharCode.apply(null, u8.subarray(i, i + CH));
        return btoa(s); };
      return { w: sourceWidth, h: sourceHeight,
               cpu: enc(new Uint8Array(lastCpuPixels.buffer)), gpu: enc(new Uint8Array(lastGpuPixels.buffer)) };
    })()"""
    d = tab.eval(js)
    w, h = d['w'], d['h']
    cpu = np.frombuffer(base64.b64decode(d['cpu']), np.uint8).reshape(h, w, 4)
    gpu = np.frombuffer(base64.b64decode(d['gpu']), np.uint8).reshape(h, w, 4)
    if tag == 'f64':
        Image.fromarray(cpu[..., :3]).save(f'{IMG}/julia_cpu_{w}x{h}.png')
        Image.fromarray(gpu[..., :3]).save(f'{IMG}/julia_gpu_{w}x{h}.png')
    diff = np.abs(cpu[..., :3].astype(int) - gpu[..., :3].astype(int)).max(axis=2)
    # карта отличий: белый фон, отличающиеся пиксели — тёмные (чем сильнее, тем темнее)
    vis = 255 - np.clip(diff * 4, 0, 255).astype(np.uint8)
    vis[(diff > 0) & (vis > 200)] = 200
    Image.fromarray(vis).save(f'{IMG}/diff_{tag}_{w}x{h}.png')
    hist = {'eq0': int((diff == 0).sum()), '1': int((diff == 1).sum()), '2-16': int(((diff >= 2) & (diff <= 16)).sum()),
            '17-64': int(((diff > 16) & (diff <= 64)).sum()), '>64': int((diff > 64).sum())}
    print('diff histogram', tag, hist, flush=True)
    with open(f'{OUT}_hist_{tag}.json', 'w') as f:
        json.dump(hist, f)


if __name__ == '__main__':
    main()
