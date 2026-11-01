import sys, re
src, hedef = sys.argv[1], sys.argv[2]
JETON = {}
out = []
for l in open(src, encoding='utf-8'):
    l = l.rstrip('\n')
    p = l.split('\t')
    if p[0] == '@jeton':
        JETON[p[1]] = p[2]
        continue
    if not p[0].startswith('@'):
        s = p[1]
        def degis(m):
            b = JETON[m.group(1)]
            ek = m.group(2) or ''
            sesliler = [c for c in b if c in 'aeıioöuüâîû']
            kalin = sesliler[-1] in 'aıouâû'
            ek = {'in': 'ın' if kalin else 'in', 'e': 'a' if kalin else 'e', 'de': 'da' if kalin else 'de', 'i': 'ı' if kalin else 'i', '': ''}[ek]
            if ek and b[-1] in 'aeıioöuüâîû':
                ek = ('y' if ek in 'ıi' else 'n') + ek
            return b + ek
        s = re.sub(r'§(\w)§(in|de|e|i)?(?![a-zçğıöşüâîû])', degis, s)
        assert '§' not in s, l
        if s[0] == 'i':
            s = 'İ' + s[1:]
        else:
            s = s[0].upper() + s[1:]
        p[1] = s
    out.append('\t'.join(p))
open(hedef, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
