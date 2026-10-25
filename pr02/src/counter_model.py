"""ПР2, вариант 14 -> счётчик по строке 15 табл. 2.11.

Модель счётчика с произвольным порядком счёта по шаблонному графу рис. 2.14:
 - в узлы шаблона (позиции 0..15) подставляются значения из строки варианта;
 - развилки: поз.1 по a (a -> поз.8, ¬a -> поз.2), поз.10 по b (b -> 12, ¬b -> 11),
   поз.3 по b (b -> 4, ¬b -> 5) — как подписано на рис. 2.14.
Скрипт строит таблицу состояний (табл. 2.9), таблицу переходов (табл. 2.10),
функции newQ в форме пособия (ИЛИ от дешифрированных состояний и R1..R6),
минимизирует newQ3..newQ0 методом Квайна–МакКласки (6 переменных Q3 Q2 Q1 Q0 a b)
и проверяет всё симуляцией.
"""
import itertools
import sys

ROW15 = [11, 12, 1, 9, 2, 14, 8, 7, 6, 4, 13, 10, 15, 5, 0, 3]

# шаблон рис. 2.14: позиция -> {условие: следующая позиция}
TEMPLATE = {
    0: {None: 1},
    1: {"a": 8, "!a": 2},
    2: {None: 3},
    3: {"b": 4, "!b": 5},
    4: {None: 6}, 5: {None: 6}, 6: {None: 7},
    7: {None: 13},
    8: {None: 9}, 9: {None: 10},
    10: {"b": 12, "!b": 11},
    11: {None: 7}, 12: {None: 7},
    13: {None: 14}, 14: {None: 15}, 15: {None: 0},
}

VAL = ROW15
POS = {v: p for p, v in enumerate(VAL)}


def transitions():
    """Список строк таблицы переходов: (старое, условие, новое) в значениях счётчика."""
    rows = []
    for p in range(16):
        for cond, q in TEMPLATE[p].items():
            rows.append((VAL[p], cond, VAL[q]))
    return rows


def next_state(s, a, b):
    br = TEMPLATE[POS[s]]
    if None in br:
        return VAL[br[None]]
    var = "a" if "a" in br else "b"
    x = a if var == "a" else b
    return VAL[br[var if x else "!" + var]]


# Развилки в порядке пособия: R1/R2 — по a, R3/R4 — вторая развилка по b (поз.10),
# R5/R6 — развилка по b (поз.3)
def r_terms():
    p1, p10, p3 = VAL[1], VAL[10], VAL[3]
    return [
        ("R1", "A", p1, VAL[8]), ("R2", "¬A", p1, VAL[2]),
        ("R3", "B", p10, VAL[12]), ("R4", "¬B", p10, VAL[11]),
        ("R5", "B", p3, VAL[4]), ("R6", "¬B", p3, VAL[5]),
    ]


def manual_terms(bit):
    """Входы элемента ИЛИ для newQ<bit> (метод пособия)."""
    terms = []
    forks = {VAL[1], VAL[10], VAL[3]}
    for s in range(16):
        if s in forks:
            continue
        if (next_state(s, 0, 0) >> bit) & 1:
            terms.append(f"st{s}")
    rterms = [name for name, _, _, tgt in r_terms() if (tgt >> bit) & 1]
    return terms, rterms


def eval_manual(bit, s, a, b):
    terms, rterms = manual_terms(bit)
    v = any(s == int(t[2:]) for t in terms)
    for name, cond, st, tgt in r_terms():
        if name in rterms and s == st:
            x = a if "A" in cond else b
            if cond.startswith("¬"):
                x = 1 - x
            v = v or bool(x)
    return int(v)


# ---------- Квайн–МакКласки (6 переменных) ----------
NV = 6
VNAMES = ["Q3", "Q2", "Q1", "Q0", "a", "b"]


def idx(s, a, b):
    return (s << 2) | (a << 1) | b


def qm_primes(ones):
    cur = {format(t, f"0{NV}b") for t in ones}
    primes = set()
    while cur:
        nxt, used = set(), set()
        lst = sorted(cur)
        for x, y in itertools.combinations(lst, 2):
            d = [k for k in range(NV) if x[k] != y[k]]
            if len(d) == 1 and x[d[0]] != "-" and y[d[0]] != "-":
                nxt.add(x[:d[0]] + "-" + x[d[0] + 1:])
                used.update((x, y))
        primes |= cur - used
        cur = nxt
    return sorted(primes)


def cov(p, t):
    s = format(t, f"0{NV}b")
    return all(c == "-" or c == d for c, d in zip(p, s))


def min_cover(primes, ones):
    """Существенные импликанты + перебор оставшихся (точный минимум по числу термов,
    затем по числу литералов)."""
    ones = set(ones)
    ess = set()
    for t in ones:
        c = [p for p in primes if cov(p, t)]
        if len(c) == 1:
            ess.add(c[0])
    rest = {t for t in ones if not any(cov(p, t) for p in ess)}
    cand = [p for p in primes if p not in ess and any(cov(p, t) for t in rest)]
    best = None
    for r in range(0, len(cand) + 1):
        for comb in itertools.combinations(cand, r):
            if all(any(cov(p, t) for p in comb) for t in rest):
                cost = (r, sum(NV - p.count("-") for p in comb))
                if best is None or cost < best[0]:
                    best = (cost, comb)
        if best:
            break
    return sorted(ess), sorted(best[1])


def term_str(p):
    lits = [(n if c == "1" else "¬" + n) for n, c in zip(VNAMES, p) if c != "-"]
    return "∧".join(lits) if lits else "1"


def main():
    print("Таблица 2.9 — состояния счётчика (вариант 15):")
    print(" поз | знач | код")
    for p, v in enumerate(VAL):
        print(f" {p:3} | {v:4} | {v:04b}")
    print()
    print("Таблица 2.10 — переходы:")
    for s, cond, n in transitions():
        print(f"  {s:2} ({s:04b}) --{cond or '  ':>2}--> {n:2} ({n:04b})")
    print()
    print("Развилки (R-термы):")
    for name, cond, st, tgt in r_terms():
        print(f"  {name} = {cond} ∧ st{st}  -> {tgt}")
    print()
    funcs = {}
    for bit in range(3, -1, -1):
        t, r = manual_terms(bit)
        print(f"newQ{bit} = " + " ∨ ".join(t + r))
    print()
    for bit in range(3, -1, -1):
        ones = [idx(s, a, b) for s in range(16) for a in (0, 1) for b in (0, 1)
                if (next_state(s, a, b) >> bit) & 1]
        pr = qm_primes(ones)
        ess, add = min_cover(pr, ones)
        cover = ess + add
        funcs[bit] = cover
        lits = sum(NV - p.count("-") for p in cover)
        print(f"МДНФ newQ{bit} = " + " ∨ ".join(term_str(p) for p in cover)
              + f"   [простых имп.: {len(pr)}, сущ.: {len(ess)}, термов: {len(cover)}, литералов: {lits}]")
    print()
    # проверки
    ok = True
    for s in range(16):
        for a in (0, 1):
            for b in (0, 1):
                n = next_state(s, a, b)
                m = sum(eval_manual(k, s, a, b) << k for k in range(4))
                q = sum(int(any(cov(p, idx(s, a, b)) for p in funcs[k])) << k for k in range(4))
                ok &= (n == m == q)
    print("Проверка 16×4 наборов (граф = схема пособия = МДНФ):", "OK" if ok else "ОШИБКА")
    for a in (0, 1):
        for b in (0, 1):
            s, seq = 0, [0]
            for _ in range(12):
                s = sum(int(any(cov(p, idx(s, a, b)) for p in funcs[k])) << k for k in range(4))
                seq.append(s)
            print(f"  a={a} b={b}: " + " ".join(map(str, seq)))
    return funcs


if __name__ == "__main__":
    main()
