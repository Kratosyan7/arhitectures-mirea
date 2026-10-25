import re, sys
src, dst = sys.argv[1], sys.argv[2]
L = open(src, encoding='utf-8').read().split('\n')
struct = re.compile(r'^(<!DOCTYPE|<html|<head>|</head>|<body>|</body>|</html>|fn |struct |@|\}|\$\{studentBody\}|`;)')
out = []
in_wgsl = False
for i, s in enumerate(L):
    # PDF-подстановка неразрывных/особых пробелов -> обычные
    s = s.replace(' ', ' ').replace('\t', '  ')
    if 'return `' in s and i > 0 and 'buildShader' in L[i-1]:
        in_wgsl = True
    if in_wgsl and s.startswith('`;'):
        in_wgsl = False
    is_wrap = (s and not s[0].isspace() and not struct.match(s) and not in_wgsl and out)
    if is_wrap:
        prev = out.pop().rstrip()
        sep = '' if prev.endswith('-') and not prev.endswith(' -') else ' '
        s = prev + sep + s
    out.append(s)
# убираем выравнивание по ширине (несколько пробелов внутри строки)
res = []
for s in out:
    m = re.match(r'^(\s*)(.*)$', s)
    ind, body = m.group(1), m.group(2)
    body = re.sub(r' {2,}', ' ', body)
    res.append((ind + body).rstrip())
open(dst, 'w', encoding='utf-8').write('\n'.join(res).rstrip('\n') + '\n')
