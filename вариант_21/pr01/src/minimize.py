"""ПР1, вариант 21: F = E0E1 (16-ричный вектор).

Строит таблицу истинности, СДНФ, СКНФ, находит все простые импликанты (метод
Квайна–МакКласки) для единиц и для нулей и полным перебором выбирает минимальные
покрытия -> МДНФ и МКНФ. В варианте 21 требуются СКНФ и МДНФ. Дополнительно
рисует карты Карно (img/).
Запуск: python minimize.py [--img DIR]
"""
import itertools
import sys

VEC = 0xE0E1
N = 4
NAMES = "abcd"
F = [(VEC >> (15 - i)) & 1 for i in range(16)]   # старший бит вектора -> набор 0000
GRAY = [0b00, 0b01, 0b11, 0b10]


def bits(i):
    return [(i >> (N - 1 - k)) & 1 for k in range(N)]


def minterm(i):
    return " ∧ ".join(v if b else "¬" + v for v, b in zip(NAMES, bits(i)))


def maxterm(i):
    return "(" + " ∨ ".join("¬" + v if b else v for v, b in zip(NAMES, bits(i))) + ")"


def combine(a, b):
    diff = [k for k in range(N) if a[k] != b[k]]
    if len(diff) == 1 and "-" not in (a[diff[0]], b[diff[0]]):
        return a[:diff[0]] + "-" + a[diff[0] + 1:]
    return None


def primes(terms):
    """Квайн–МакКласки: возвращает простые импликанты в виде строк '0-1-'."""
    cur = {format(t, "04b") for t in terms}
    result = set()
    step = 0
    while cur:
        step += 1
        nxt, used = set(), set()
        groups = {}
        for t in cur:
            groups.setdefault(t.count("1"), []).append(t)
        for k in sorted(groups):
            for a in groups[k]:
                for b in groups.get(k + 1, []):
                    c = combine(a, b)
                    if c:
                        nxt.add(c)
                        used.update((a, b))
        print(f"  шаг {step}: {len(cur)} термов, склеено -> {len(nxt)}")
        result |= cur - used
        cur = nxt
    return sorted(result)


def covers(p, t):
    s = format(t, "04b")
    return all(x == "-" or x == y for x, y in zip(p, s))


def min_cover(pis, terms):
    """Полный перебор подмножеств простых импликант: минимальное число термов,
    затем минимальное число литералов. Возвращает все оптимальные покрытия."""
    best, best_cost = [], None
    for r in range(1, len(pis) + 1):
        for comb in itertools.combinations(pis, r):
            if all(any(covers(p, t) for p in comb) for t in terms):
                cost = (r, sum(4 - p.count("-") for p in comb))
                if best_cost is None or cost < best_cost:
                    best, best_cost = [comb], cost
                elif cost == best_cost:
                    best.append(comb)
        if best:
            break
    return best, best_cost


def conj(p):  # для единиц: 1 -> переменная, 0 -> с инверсией
    return " ∧ ".join(v if x == "1" else "¬" + v for v, x in zip(NAMES, p) if x != "-")


def disj(p):  # для нулей: 0 -> переменная без инверсии, 1 -> с инверсией
    return "(" + " ∨ ".join(v if x == "0" else "¬" + v for v, x in zip(NAMES, p) if x != "-") + ")"


def kmap_text(vals):
    lines = ["ab\\cd | 00 01 11 10"]
    for r in GRAY:
        row = [str(vals[(r << 2) | c]) for c in GRAY]
        lines.append(f"   {r:02b} |  " + "  ".join(row))
    return "\n".join(lines)


def main():
    ones = [i for i in range(16) if F[i]]
    zeros = [i for i in range(16) if not F[i]]
    print(f"F = {VEC:04X}h = {VEC:016b}b")
    print("Наборы с F=1:", ones)
    print("Наборы с F=0:", zeros)
    print()
    print("Карта Карно:")
    print(kmap_text(F))
    print()
    print("СДНФ: F =", " ∨ ".join("(" + minterm(i) + ")" for i in ones))
    print("СКНФ: F =", " ∧ ".join(maxterm(i) for i in zeros))
    print()
    print("Квайн–МакКласки по единицам (минтермы):")
    po = primes(ones)
    print("  простые импликанты единиц:", po, "->", ", ".join(conj(p) for p in po))
    co, cost1 = min_cover(po, ones)
    for c in co:
        print(f"  МДНФ: F = {' ∨ '.join(conj(p) for p in c)}   (термов: {cost1[0]}, литералов: {cost1[1]})")
    print("Квайн–МакКласки по нулям (макстермы):")
    pz = primes(zeros)
    print("  простые импликанты нулей:", pz, "->", ", ".join(disj(p) for p in pz))
    cz, cost = min_cover(pz, zeros)
    for c in cz:
        print(f"  МКНФ: F = {' ∧ '.join(disj(p) for p in c)}   (скобок: {cost[0]}, литералов: {cost[1]})")
    # проверка МДНФ на всех 16 наборах
    ok = all(F[i] == int(any(covers(p, i) for p in co[0])) for i in range(16))
    print("Проверка МДНФ на всех 16 наборах:", "OK" if ok else "ОШИБКА")
    return po, co, pz, cz


def draw_kmap(path, groups, title=None):
    """Карта Карно 4×4 с подсветкой единиц и прямоугольными группами (для МДНФ)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(5.4, 4.8), dpi=150)
    ax.set_xlim(-1, 4.3)
    ax.axis("off")
    for k, g in enumerate(GRAY):
        ax.text(k + 0.5, -0.35, f"{g:02b}", ha="center", va="center", fontsize=13)
        ax.text(-0.45, k + 0.5, f"{g:02b}", ha="center", va="center", fontsize=13)
    ax.text(-0.45, -0.35, "ab\\cd", ha="center", va="center", fontsize=12, style="italic")
    for r, rg in enumerate(GRAY):
        for c, cg in enumerate(GRAY):
            v = F[(rg << 2) | cg]
            ax.add_patch(plt.Rectangle((c, r), 1, 1, fill=False, lw=1.2))
            ax.text(c + 0.5, r + 0.5, str(v), ha="center", va="center", fontsize=16,
                    color="black" if v == 1 else "#999999", weight="bold" if v == 1 else "normal")
    colors = ["#2ca02c", "#1f77b4", "#d62728", "#9467bd"]
    for k, (cells, label) in enumerate(groups):
        col = colors[k % len(colors)]
        for (r0, c0, r1, c1) in cells:
            ax.add_patch(FancyBboxPatch((c0 + 0.12, r0 + 0.12), c1 - c0 + 1 - 0.24, r1 - r0 + 1 - 0.24,
                                        boxstyle="round,pad=0.02,rounding_size=0.25",
                                        fill=False, ec=col, lw=2.6))
        ax.text(-0.9 + 1.9 * k, 4.62, label, color=col, fontsize=12, weight="bold")
    if title:
        ax.set_title(title, fontsize=12)
    ax.set_ylim(4.95, -1)
    fig.tight_layout()
    fig.savefig(path)
    print("saved", path)


if __name__ == "__main__":
    main()
    if "--img" in sys.argv:
        d = sys.argv[sys.argv.index("--img") + 1]
        # Единицы F: ¬b¬d -> четыре угла (b=0,d=0); ¬b¬c -> строки ab=00,10 столбцы cd=00,01;
        #            abcd -> одна клетка ab=11,cd=11.
        draw_kmap(f"{d}/karnaugh_ones.png",
                  groups=[([(0, 0, 0, 0), (0, 3, 0, 3), (3, 0, 3, 0), (3, 3, 3, 3)], "¬b ∧ ¬d"),
                          ([(0, 0, 0, 1), (3, 0, 3, 1)], "¬b ∧ ¬c"),
                          ([(2, 2, 2, 2)], "a∧b∧c∧d")])
