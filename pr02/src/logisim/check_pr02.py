"""Проверка схем ПР2 в движке Logisim 2.7.1 (через logitool.js) и сравнение с моделью.
Запуск: python check_pr02.py   (переменная LOGISIM — путь к logisim-generic-2.7.1.jar)"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import counter_model as cm  # noqa: E402

JAR = os.environ.get("LOGISIM", os.path.join(HERE, "../../../.tools/logisim/logisim.jar"))


def lt(*args):
    out = subprocess.run(["jjs", "-cp", JAR, "logitool.js", "--", *args], cwd=HERE,
                         capture_output=True, text=True, check=True).stdout
    return out.strip().splitlines()


def section(t):
    print(f"> {t}")


section("coder.circ / coder_4_2: допустимые наборы (одна активная линия)")
rows = lt("table", "coder.circ", "coder_4_2", "I3,I2,I1,I0", "a1,a0")
print("  I3 I2 I1 I0 | a1 a0")
for r in rows[1:]:
    i, o = r.split("|")
    if i.split().count("1") == 1:
        print("   " + "  ".join(i.split()) + "  |  " + "  ".join(o.split()))

section("coder.circ / coder_4_2_prio: старшая активная линия -> код")
rows = lt("table", "coder.circ", "coder_4_2_prio", "I3,I2,I1,I0", "a1,a0")
ok = True
for r in rows[1:]:
    i, o = r.split("|")
    bits = [int(x) for x in i.split()]       # I3 I2 I1 I0
    hi = next((3 - k for k, b in enumerate(bits) if b), 0)
    ok &= o.split() == [str(hi >> 1), str(hi & 1)]
print(f"  16 наборов, код = номер старшей единицы: {'OK' if ok else 'ОШИБКА'}")

section("t_trigger.circ: сброс nR=0, затем импульсы на входе T")
steps = ("nS=1;print nS=1,nR=0 (сброс);nR=1;print nS=1,nR=1 (хранение);"
         "T=1;print T:0->1;T=0;print T:1->0;T=1;print T:0->1;T=0;print T:1->0;"
         "T=1;print T:0->1;T=0;print T:1->0")
for line in lt("run", "t_trigger.circ", "t_trigger", steps, "Q,nQ"):
    print("  " + line)

section("counter.circ / newQ_min (МДНФ): 64 набора Q3 Q2 Q1 Q0 a b")
rows = lt("table", "counter.circ", "newQ_min", "Q3,Q2,Q1,Q0,a,b", "newQ3,newQ2,newQ1,newQ0")
bad = 0
for r in rows[1:]:
    i, o = r.split("|")
    v = [int(x) for x in i.split()]
    s = v[0] * 8 + v[1] * 4 + v[2] * 2 + v[3]
    n = cm.next_state(s, v[4], v[5])
    bad += o.split() != [str((n >> k) & 1) for k in (3, 2, 1, 0)]
print(f"  совпадает с графом переходов: {64 - bad}/64")

section("counter.circ / counter: 12 тактов из состояния 0 при постоянных A, B")
seen = set()
allok = True
for a in (0, 1):
    for b in (0, 1):
        steps = f"A={a};B={b};print" + ";cycle;print" * 12
        seq = [int(line.split("=")[1], 2) for line in lt("run", "counter.circ", "counter", steps, "Q")]
        exp = [0]
        for _ in range(12):
            exp.append(cm.next_state(exp[-1], a, b))
        seen |= set(zip(seq, seq[1:]))
        allok &= seq == exp
        print(f"  A={a} B={b}: {' '.join(map(str, seq))}  {'OK' if seq == exp else 'ОШИБКА'}")
need = {(s, n) for s, _, n in cm.transitions()}
print(f"  пройдено переходов графа: {len(need & seen)}/{len(need)}, состояний: "
      f"{len({s for s, _ in seen})}/16 -> {'OK' if allok and need <= seen else 'ОШИБКА'}")
