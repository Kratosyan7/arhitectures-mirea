"""Трансляция виртуального адреса через TLB (практика 5, вариант 23)."""
VPN_TLB, PFN_TLB = 4, 10           # запись TLB: VPN = 4 → PFN = 10
PAGE = 2 * 1024                     # размер страницы 2 КБ
VA = 0x4C12                         # виртуальный адрес

offset_bits = PAGE.bit_length() - 1
vpn, offset = VA // PAGE, VA % PAGE
print(f"Размер страницы: {PAGE} Б = 2^{offset_bits} → смещение {offset_bits} бит")
print(f"VA = 0x{VA:04X} = {VA:016b}b")
print(f"VPN    = VA >> {offset_bits}    = {vpn} (0x{vpn:X})")
print(f"Offset = VA & 0x{PAGE - 1:X} = 0x{offset:04X} ({offset})")
print(f"Запись TLB: VPN = {VPN_TLB} → PFN = {PFN_TLB}")
if vpn == VPN_TLB:
    print(f"TLB hit: PA = PFN·PAGE + Offset = 0x{PFN_TLB * PAGE + offset:X}")
else:
    print(f"VPN {vpn} ≠ {VPN_TLB}: записи нет в TLB → Page Fault (исключение, обработчик подкачки)")
    print(f"Если бы страница была в TLB: PA = {PFN_TLB}·0x{PAGE:X} + 0x{offset:X} = 0x{PFN_TLB * PAGE + offset:X}")
lo, hi = VPN_TLB * PAGE, (VPN_TLB + 1) * PAGE - 1
print(f"Записи VPN = {VPN_TLB} соответствуют VA 0x{lo:X}–0x{hi:X}, например 0x{lo + offset:X} → PA 0x{PFN_TLB * PAGE + offset:X}")
