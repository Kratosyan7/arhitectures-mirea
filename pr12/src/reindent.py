import re, sys
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
def strip_strings(s):
    s = re.sub(r"'(?:\\.|[^'\\])*'", "''", s)
    s = re.sub(r'"(?:\\.|[^"\\])*"', '""', s)
    s = re.sub(r'`[^`]*`', '``', s)
    s = re.sub(r'//.*$', '', s)
    return s
out = []
mode = None; depth = 0; base = 0
for s in L:
    t = s.strip()
    if t.startswith('<style>'): out.append('  ' + t); mode = 'code'; depth = 0; base = 2; continue
    if t.startswith('</style>'): out.append('  ' + t); mode = None; continue
    if t.startswith('<script>'): out.append('  ' + t); mode = 'code'; depth = 0; base = 2; continue
    if t.startswith('</script>'): out.append('  ' + t); mode = None; continue
    if mode is None:
        out.append(s); continue
    if mode == 'wgsl':
        if t.startswith('`;'):
            out.append(' ' * (base + 2 * depth_js) + t); mode = 'code'; depth = depth_js; continue
        lead = len(re.match(r'^[\)\]\}]*', t).group(0))
        out.append(('  ' * (wdepth - lead) + t) if t else '')
        c = strip_strings(t)
        wdepth += c.count('{') + c.count('(') + c.count('[') - c.count('}') - c.count(')') - c.count(']')
        continue
    lead = min(1, len(re.match(r'^[\)\]\}]*', t).group(0)))
    out.append((' ' * (base + 2 * (depth - lead)) + t) if t else '')
    if t.endswith('return `'):
        mode = "wgsl"; wdepth = 0; depth_js = depth; continue
    c = strip_strings(t)
    net = c.count('{') + c.count('(') + c.count('[') - c.count('}') - c.count(')') - c.count(']')
    depth += max(-1, min(1, net))
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out))
