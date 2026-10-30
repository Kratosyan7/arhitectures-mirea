#!/bin/bash
# Проверка схем pr01.circ в движке Logisim 2.7.1 (таблицы истинности).
# LOGISIM — путь к logisim-generic-2.7.1.jar
cd "$(dirname "$0")"
LOGISIM=${LOGISIM:-../../../.tools/logisim/logisim.jar}
t() { jjs -cp "$LOGISIM" logitool.js -- table pr01.circ "$1" "$2" "$3"; }
echo "> nand_cmos (КМОП И-НЕ):"
t nand_cmos A,B Y
echo "> F_sdnf и F_mknf (F=55AA), вектор-эталон 0101010110101010:"
paste -d'|' <(t F_sdnf a,b,c,d F) <(t F_mknf a,b,c,d F | cut -d'|' -f2) \
  | awk -F'|' 'NR==1{print "a b c d | F_sdnf | F_mknf"; next} {gsub(/ /,"",$2); gsub(/ /,"",$3); printf "%s|   %s    |   %s\n", $1, $2, $3}'
s=$(t F_sdnf a,b,c,d F | tail -16 | cut -d'|' -f2 | tr -d ' \n')
m=$(t F_mknf a,b,c,d F | tail -16 | cut -d'|' -f2 | tr -d ' \n')
echo "> F_sdnf = $s, F_mknf = $m, эталон 0101010110101010"
[ "$s" = 0101010110101010 ] && [ "$m" = 0101010110101010 ] && echo "> OK: обе схемы реализуют F=55AA"
