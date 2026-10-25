"""Граф переходов счётчика (шаблон рис. 2.14 со значениями варианта 15)."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle

import counter_model as cm

XY = {0: (3, 0), 1: (3, 1), 8: (2, 2), 9: (2, 3), 10: (2, 4), 12: (1.4, 5), 11: (2.6, 5),
      2: (4, 2), 3: (4, 3), 4: (3.4, 4), 5: (4.6, 4), 6: (4, 5), 7: (3, 6), 13: (3, 7),
      14: (3, 8), 15: (3, 9)}
R = 0.28


def main(out):
    fig, ax = plt.subplots(figsize=(5.0, 9.4), dpi=150)
    ax.set_xlim(0.7, 6.0)
    ax.set_ylim(9.7, -0.7)
    ax.axis("off")
    ax.set_aspect("equal")
    for p, nxt in cm.TEMPLATE.items():
        for cond, q in nxt.items():
            (x1, y1), (x2, y2) = XY[p], XY[q]
            if p == 15:
                arr = FancyArrowPatch((x1 + R * 0.9, y1 + 0.1), (x2 + R * 0.9, y2 - 0.1),
                                      connectionstyle="arc3,rad=0.55", arrowstyle="-|>",
                                      mutation_scale=14, lw=1.3, color="black")
            else:
                arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                      lw=1.3, color="black", shrinkA=R * 72 * 1.25, shrinkB=R * 72 * 1.25)
            ax.add_patch(arr)
            if cond:
                lab = cond.replace("!", "¬")
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                dx = -0.22 if x2 < x1 else 0.22
                ax.text(mx + dx, my - 0.12, lab, fontsize=12, ha="center", va="center",
                        color="#c0392b", weight="bold")
    for p, (x, y) in XY.items():
        ax.add_patch(Circle((x, y), R, fill=True, fc="white", ec="black", lw=1.5, zorder=3))
        ax.text(x, y, str(cm.VAL[p]), ha="center", va="center", fontsize=13, zorder=4, weight="bold")
        ax.text(x - R - 0.05, y - R + 0.02, str(p), ha="right", va="center", fontsize=8, color="gray")
    fig.tight_layout()
    fig.savefig(out)
    print("saved", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "graph.png")
