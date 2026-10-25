# Скриншоты Logisim для ПР2

Logisim 2.7.1: `java -jar .tools/logisim/logisim.jar pr02/src/logisim/<файл>.circ`.
Подсхема выбирается двойным щелчком в дереве слева. Входы переключаются инструментом
«Poke» (рука) щелчком по контакту. После открытия все входы = 0, триггеры = 0.
Один такт генератора: меню Simulate → Tick Once (Ctrl+T) переключает clk один раз,
т.е. полный такт (передний фронт, по которому срабатывают D-триггеры) = 2 нажатия.
Автотактирование (Ticks Enabled, Ctrl+K) не включать.

| Файл картинки | .circ / подсхема | Что сделать перед снимком | Что должно быть видно |
|---|---|---|---|
| `pr02/img/logisim_coder.png` | `coder.circ` / `coder_4_2` (главная) | I2=1 | два ИЛИ; a1=1, a0=0 |
| `pr02/img/logisim_coder_prio.png` | `coder.circ` / `coder_4_2_prio` | I1=1, I2=1 | И, НЕ, два ИЛИ; a1=1, a0=0 (приоритет у I2) |
| `pr02/img/logisim_t_trigger.png` | `t_trigger.circ` / `t_trigger` | по порядку: nS=1 (сброс, Q=0), nR=1, T=1, затем T=0 | 9 элементов И-НЕ G1…G9, подписи ступеней; T=0, Q=1, nQ=0 (триггер переключился по спаду T) |
| `pr02/img/logisim_counter.png` | `counter.circ` / `counter` (главная) | A=1, B=1, затем Ctrl+T 6 раз (3 полных такта) | вся схема целиком (уменьшить масштаб, примерно 40–50 %): триггеры, дешифратор st0…st15, R1…R6, ИЛИ newQ0…newQ3; индикатор показывает «C», выход Q=1100 |
| `pr02/img/logisim_counter_ff.png` | `counter.circ` / `counter` | то же состояние, что выше | крупно (100 %) верхняя часть: входы A, B, генератор clk, 4 D-триггера с туннелями newQk/clk/Qk/nQk, разветвитель и индикатор «C» |
| `pr02/img/logisim_counter_logic.png` | `counter.circ` / `counter` | то же состояние | крупно (70–100 %) правая часть: инверторы nA/nB, элементы И R1…R6 и четыре ИЛИ newQ0…newQ3 с туннелями входов |
| `pr02/img/logisim_newq_min.png` | `counter.circ` / `newQ_min` | Q3=1, Q2=1, Q1=0, Q0=0, a=1, b=0 | вся подсхема (масштаб ~50–60 %): 26 элементов И, 4 ИЛИ; newQ3=0, newQ2=1, newQ1=1, newQ0=0 |

Проверка логики без GUI: `python pr02/src/logisim/check_pr02.py` (нужен `jjs` из JDK 8);
штатный консольный режим: `java -jar logisim.jar counter.circ -tty table | head -14`.
