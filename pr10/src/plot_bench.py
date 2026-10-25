#!/usr/bin/env python3
"""Строит столбчатые диаграммы по CSV-замерам (Задания №1 и №2)."""
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot(csv_path, png_path, title, name_col):
    names, ns = [], []
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            names.append(row[name_col])
            ns.append(float(row["ns_per_call"]))

    fig, ax = plt.subplots(figsize=(8, 4.2))
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2"]
    bars = ax.bar(range(len(names)), ns, color=colors[: len(names)])
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=12, ha="right", fontsize=9)
    ax.set_ylabel("нс на один вызов (меньше — быстрее)")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)
    for b, val in zip(bars, ns):
        ax.text(b.get_x() + b.get_width() / 2, val, f"{val:.1f}",
                ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(png_path, dpi=130)
    print("saved", png_path)


if __name__ == "__main__":
    plot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
