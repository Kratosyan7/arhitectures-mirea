"""Схема последовательности обработки прерываний (шаблон рис. 7.1 / 7.2), вариант 28.

Устройства: IRQ0 — SSD, IRQ1 — Тачпад, IRQ2 — Клавиатура, IRQ3 — Сканер.
При выполнении команды 0x3C93 основной программы приходит прерывание от Сканера,
при выполнении команды 0x01BC ПОП Сканера — прерывание от SSD (более высокий приоритет).
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "interrupts_v28.png")
GREEN, BLUE, RED = "#16a34a", "#1d4ed8", "#dc2626"

fig, ax = plt.subplots(figsize=(13, 9.6), dpi=150)
ax.set_xlim(0, 1300)
ax.set_ylim(960, 0)
ax.axis("off")


def cells(x, y, w, h, texts, bold=(), colors=None, size=9):
    for i, t in enumerate(texts):
        ax.add_patch(Rectangle((x, y + i * h), w, h, fill=False, lw=1.2))
        c = (colors or {}).get(i, "black")
        ax.text(x + w / 2, y + i * h + h / 2, t, ha="center", va="center", fontsize=size,
                fontweight="bold" if i in bold else "normal", color=c)
    return {t: (x, y + i * h, w, h) for i, t in enumerate(texts)}


def path(pts, color, num=None, at=None, head=True):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1] + (xs[-1],), ys, color=color, lw=1.8)
    if head:
        ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8))
    if num is not None:
        tx, ty = at if at else pts[len(pts) // 2]
        ax.text(tx, ty, str(num), color=color, fontsize=11, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))


# --- Таблица векторов прерываний (IDT) ---
ax.text(205, 30, "Interruption\nDescriptor Table", ha="center", va="center", fontsize=10, fontweight="bold")
idt_x, idt_y = 70, 70
rows = [("IRQ0", "SSD", "0x0065", RED), ("IRQ1", "Тачпад", "0x00C9", "black"),
        ("IRQ2", "Клавиатура", "0x012D", "black"), ("IRQ3", "Сканер", "0x0191", BLUE)]
for i, (irq, dev, vec, col) in enumerate(rows):
    y = idt_y + 32 * i
    ax.add_patch(Rectangle((idt_x, y), 270, 32, fill=False, lw=1.2))
    ax.add_patch(Rectangle((idt_x, y + 16), 42, 16, fill=False, lw=0.8))
    ax.add_patch(Rectangle((idt_x + 228, y + 16), 42, 16, fill=False, lw=0.8))
    ax.text(idt_x + 21, y + 24, irq, fontsize=7, ha="center", va="center")
    ax.text(idt_x + 249, y + 24, vec, fontsize=7, ha="center", va="center")
    ax.text(idt_x + 135, y + 14, dev, fontsize=10, ha="center", va="center", fontweight="bold", color=col)

# --- Регистр IDT ---
ax.text(440, 72, "Регистр IDT", ha="center", fontsize=10, fontweight="bold")
cells(385, 82, 110, 34, ["Вектор адреса\nпрерывания"], size=8)

# --- Основная программа ---
ax.text(640, 95, "Осн. программа", ha="center", fontsize=10, fontweight="bold")
main = ["0x1000", "", "", "", "0x3C93", "0x3C94", "", "", "", "", "0x8000"]
mx, my, mw, mh = 575, 105, 130, 24
cells(mx, my, mw, mh, main, bold=(0, 4, 5, 10))

# --- Стек ---
ax.text(450, 590, "СТЕК", ha="center", fontsize=10, fontweight="bold")
stack = ["...", "...", "...", "...", "0x01BD", "0x3C94"]
sx, sy, sw, sh = 385, 600, 130, 24
cells(sx, sy, sw, sh, stack, bold=(4, 5))
ax.text(sx - 6, sy + 8, "Вершина", fontsize=7, ha="right")
ax.text(sx - 6, sy + 6 * sh - 6, "Дно", fontsize=7, ha="right")

# --- Память ПОП ---
ax.text(1155, 30, "ПОП", ha="center", fontsize=10, fontweight="bold")
px, pw, ph = 1090, 130, 21
blocks = [("0x0065", "0x00C8", "SSD"), ("0x00C9", "0x012C", "Тачпад"),
          ("0x012D", "0x0190", "Клавиатура"), ("0x0191", "0x01F4", "Сканер")]
py = 42
pos = {}
for start, end, dev in blocks:
    if dev == "Сканер":
        texts = [start, "...", "0x01BC", "0x01BD", "...", "...", "...", end]
    elif dev == "SSD":
        texts = [start, "...", "...", "...", "...", "...", end]
    else:
        texts = [start, "...", "...", "...", end]
    r = cells(px, py, pw, ph, texts, bold=(0, len(texts) - 1) + ((2, 3) if dev == "Сканер" else ()))
    pos[dev] = (py, texts)
    ax.text(px + pw + 50, py + len(texts) * ph / 2, dev, rotation=90, va="center", fontsize=9, color="gray")
    py += len(texts) * ph + 10


def prow(dev, label):
    y0, texts = pos[dev]
    i = texts.index(label)
    return y0 + i * ph + ph / 2


def mrow(i):
    return my + i * mh + mh / 2


# 1: выполнение основной программы 0x1000 → 0x3C93
path([(mx + mw / 2, mrow(0) + 10), (mx + mw / 2, mrow(4) - 10)], GREEN, 1, at=(mx + mw / 2 + 14, mrow(2)))
# 2: сохранение адреса 0x3C94 в стек
path([(mx, mrow(4)), (545, mrow(4)), (545, sy + 5 * sh + 8), (sx + sw, sy + 5 * sh + 8)], GREEN, 2,
     at=(545, 420))
# 3: запрос от Сканера (IRQ3) → IDT
path([(sx + 10, sy + 5 * sh + 16), (130, sy + 5 * sh + 16), (130, idt_y + 32 * 3 + 16), (idt_x, idt_y + 32 * 3 + 16)],
     GREEN, 3, at=(130, 450))
# 4: из IDT вектор 0x0191 через регистр IDT → начало ПОП Сканера
sc_start = prow("Сканер", "0x0191")
path([(440, 116), (440, 470), (1030, 470), (1030, sc_start), (px, sc_start)], BLUE, 4, at=(800, 470))
# 5: выполнение ПОП Сканера до 0x01BC
y1bc = prow("Сканер", "0x01BC")
path([(px + pw - 12, sc_start + 6), (px + pw - 12, y1bc - 6)], BLUE, 5, at=(px + pw + 24, sc_start + 22))
# 6: сохранение адреса 0x01BD в стек
path([(px, y1bc), (1060, y1bc), (1060, 820), (sx + sw + 30, 820), (sx + sw + 30, sy + 4 * sh + 12),
      (sx + sw, sy + 4 * sh + 12)], BLUE, 6, at=(800, 820))
# 7: запрос от SSD (IRQ0) → IDT
path([(sx + 20, sy + 4 * sh + 6), (100, sy + 4 * sh + 6), (100, idt_y + 16), (idt_x, idt_y + 16)], BLUE, 7,
     at=(100, 400))
# 8: вектор 0x0065 → начало ПОП SSD
ssd_start = prow("SSD", "0x0065")
path([(495, 99), (560, 99), (560, 60), (1050, 60), (1050, ssd_start), (px, ssd_start)], RED, 8, at=(800, 60))
# 9: выполнение ПОП SSD до 0x00C8
ssd_end = prow("SSD", "0x00C8")
path([(px + pw - 12, ssd_start + 6), (px + pw - 12, ssd_end - 6)], RED, 9, at=(px + pw + 24, ssd_start + 60))
# 10: возврат — чтение адреса 0x01BD из стека
path([(px, ssd_end), (1070, ssd_end), (1070, 840), (sx + sw + 50, 840), (sx + sw + 50, sy + 4 * sh + 4),
      (sx + sw, sy + 4 * sh + 4)], RED, 10, at=(800, 840))
# 11: переход по адресу 0x01BD
y1bd = prow("Сканер", "0x01BD")
path([(sx, sy + 4 * sh + 18), (360, sy + 4 * sh + 18), (360, 870), (1080, 870), (1080, y1bd), (px, y1bd)], RED, 11,
     at=(800, 870))
# 12: выполнение ПОП Сканера до 0x01F4
sc_end = prow("Сканер", "0x01F4")
path([(px + pw - 12, y1bd + 6), (px + pw - 12, sc_end - 6)], BLUE, 12, at=(px + pw + 24, y1bd + 40))
# 13: возврат — чтение адреса 0x3C94 из стека
path([(px, sc_end), (1060, sc_end), (1060, 895), (sx + sw + 70, 895), (sx + sw + 70, sy + 5 * sh + 18),
      (sx + sw, sy + 5 * sh + 18)], BLUE, 13, at=(800, 895))
# 14: переход по адресу 0x3C94
path([(sx, sy + 5 * sh + 4), (340, sy + 5 * sh + 4), (340, 520), (560, 520), (560, mrow(5)), (mx, mrow(5))], GREEN,
     14, at=(450, 520))
# 15: выполнение основной программы до 0x8000
path([(mx + mw / 2, mrow(5) + 10), (mx + mw / 2, mrow(10) - 10)], GREEN, 15, at=(mx + mw / 2 + 14, mrow(8)))

ax.text(650, 935, "Вариант 28: Сканер (IRQ3) при команде 0x3C93 основной программы; "
        "SSD (IRQ0, более высокий приоритет) при команде 0x01BC ПОП Сканера",
        ha="center", fontsize=10, style="italic")
plt.savefig(OUT, bbox_inches="tight", facecolor="white")
print("saved", OUT)
