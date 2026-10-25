"""Проверка pr12.circ: симуляция в движке Logisim 2.7.1 против модели fixed.py.

1) logitool.js run — пошаговая симуляция главной схемы simt4 (такт за тактом),
   значения всех выходов сравниваются с эталонной трассой fixed.simulate();
2) java -jar logisim.jar pr12.circ -tty table — штатный консольный режим
   Logisim: схема тактируется до сигнала halt, последняя строка таблицы
   сравнивается с итоговым состоянием модели.
"""
import os
import subprocess
import sys

import fixed

HERE = os.path.dirname(os.path.abspath(__file__))
JAR = os.path.join(HERE, '..', '..', '..', '.tools', 'logisim', 'logisim.jar')
JJS = ['jjs', '-J-Djava.awt.headless=true', '-cp', JAR, os.path.join(HERE, 'logitool.js'), '--']
CIRC = os.path.join(HERE, 'pr12.circ')
OUTS = [f'{n}{i}' for i in range(4) for n in ('ZX', 'ZY', 'N', 'ESC')] + ['STEP', 'ESCMASK', 'halt']


def expected_row(step, lanes, escs, halt):
    row = {'STEP': step, 'halt': int(halt),
           'ESCMASK': sum(int(e) << i for i, e in enumerate(escs))}
    for i, ((zx, zy, n), e) in enumerate(zip(lanes, escs)):
        row.update({f'ZX{i}': zx & 0xFFFF, f'ZY{i}': zy & 0xFFFF, f'N{i}': n, f'ESC{i}': int(e)})
    return row


def parse(v):
    return int(v, 16) if v.startswith('0x') else int(v)


def main():
    trace = fixed.simulate()
    # --- 1. пошаговая симуляция
    steps = ['tick', 'print 0'] + [x for k in range(1, len(trace)) for x in ('tick', 'tick', f'print {k}')]
    out = subprocess.run(JJS + ['run', CIRC, 'simt4', ';'.join(steps), ','.join(OUTS)],
                         capture_output=True, text=True, timeout=600).stdout
    got = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == len(OUTS) + 1 and parts[0].isdigit():
            got.append({kv.split('=')[0]: parse(kv.split('=')[1]) for kv in parts[1:]})
    ok = True
    print('Такт | STEP | N0 N1 N2 N3 | ESCMASK | halt | совпадение с моделью')
    for k, (step, lanes, escs) in enumerate(trace):
        exp = expected_row(step, lanes, escs, k == len(trace) - 1)
        g = got[k] if k < len(got) else {}
        same = g == exp
        ok &= same
        if k < 3 or k % 4 == 0 or k >= len(trace) - 2 or not same:
            print(f'{k:4d} | {g.get("STEP", "?"):4} | ' + ' '.join(f'{g.get(f"N{i}", "?"):2}' for i in range(4))
                  + f' | {g.get("ESCMASK", 0):04b}    | {g.get("halt", "?")}    | {"да" if same else "НЕТ"}')
    print(f'Пошаговая симуляция: {len(got)} тактов, все совпали с моделью: {"ДА" if ok and len(got) == len(trace) else "НЕТ"}')

    # --- 2. штатный режим -tty table
    order = subprocess.run(JJS + ['pinorder', CIRC, 'simt4'], capture_output=True, text=True,
                           timeout=120).stdout.strip().split(',')
    tty = subprocess.run(['java', '-Djava.awt.headless=true', '-jar', JAR, CIRC, '-tty', 'table'],
                         capture_output=True, text=True, timeout=600)
    rows = [r.split('\t') for r in tty.stdout.strip().splitlines()]
    last = {name: int(v.replace(' ', ''), 2) for name, v in zip(order, rows[-1])}
    step, lanes, escs = trace[-1]
    exp = expected_row(step, lanes, escs, True)
    exp.pop('halt')
    same = last == exp
    print(f'-tty table: код выхода {tty.returncode}, строк {len(rows)}, '
          f'последняя строка совпадает с моделью: {"ДА" if same else "НЕТ"}')
    print('Итог по линиям (N — число итераций до ухода, Q4.12 vs double):')
    for i, ((x, y, _, _), (zx, zy, n)) in enumerate(zip(fixed.PIXELS, lanes)):
        st = 'ушла' if escs[i] else 'в множестве'
        print(f'  lane{i} пиксель ({x},{y}): N = {last[f"N{i}"]:2d} ({st}), '
              f'z = {zx / 4096:+.4f} {zy / 4096:+.4f}i, double: N = {fixed.iters_double(x, y)}')
    return 0 if ok and same else 1


if __name__ == '__main__':
    sys.exit(main())
