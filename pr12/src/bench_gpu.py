"""Доп. замер: только GPU-канал, 15 запусков подряд без пауз на CPU-расчёт
(видеокарта не успевает сбросить частоты). Время — как в стенде:
от queue.submit до получения результата в JS (mapAsync).
Для сравнения тот же замер с «пустым» ядром (return rgba(0,0,0,1)):
его время — накладные расходы передачи буферов и синхронизации."""
import json
import statistics

from cdp import Tab

RES = [(640, 360), (1280, 720), (1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320)]
tab = Tab()
tab.goto('http://localhost:8112/index.html', wait=2.0)
out = []
for w, h in RES:
    res = tab.eval(f"""(async () => {{
        loadVariant(VARIANT, {{width: {w}, height: {h}}});
        const run = async () => {{ const t = [];
            for (let i = 0; i < 15; i++) t.push((await processGpu(sourcePixels, sourceWidth, sourceHeight)).timeMs);
            return t.slice(3); }};
        const julia = await run();
        gpuCodeEl.value = 'return rgba(0.0, 0.0, 0.0, 1.0);';
        const empty = await run();
        return {{julia, empty}};
    }})()""")
    r = {'width': w, 'height': h, 'median': statistics.median(res['julia']), 'min': min(res['julia']),
         'max': max(res['julia']), 'empty_median': statistics.median(res['empty'])}
    out.append(r)
    print(f'{w}x{h}: Julia median {r["median"]:6.1f} ms (min {r["min"]:6.1f}, max {r["max"]:6.1f}) | '
          f'пустое ядро {r["empty_median"]:6.1f} ms | разность {r["median"] - r["empty_median"]:6.1f} ms', flush=True)
json.dump(out, open('results_gpu_only.json', 'w'), indent=1)
tab.close()
