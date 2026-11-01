import sys, re
src, hedef = sys.argv[1], sys.argv[2]
SESLI = 'aeıioöuüâîû'
KALIN = 'aıouâû'
JETON = {}
KANON = {'nin': 'in', 'nın': 'in', 'ın': 'in', 'sı': 'si', 'nde': 'de', 'nda': 'de', 'da': 'de', 'ye': 'e', 'ya': 'e', 'ne': 'e', 'na': 'e', 'a': 'e', 'yi': 'i', 'yı': 'i', 'ı': 'i'}


def ekle(b, ek):
    if not ek:
        return b
    kalin = [c for c in b if c in SESLI][-1] in KALIN
    son = b[-1]
    sesli_son = son in SESLI
    iyelikli = son in 'ıiuü'
    if ek == 'in':
        return b + ('n' if sesli_son else '') + ('ın' if kalin else 'in')
    if ek == 'si':
        return b + ('s' if sesli_son else '') + ('ı' if kalin else 'i')
    if ek in ('e', 'i'):
        govde = ('a' if kalin else 'e') if ek == 'e' else ('ı' if kalin else 'i')
        if not sesli_son:
            return b + govde
        return b + ('n' if iyelikli else 'y') + govde
    if ek == 'de':
        return b + ('n' if iyelikli else '') + ('da' if kalin else 'de')
    raise ValueError(ek)


out = []
for l in open(src, encoding='utf-8'):
    l = l.rstrip('\n')
    p = l.split('\t')
    if p[0] == '@jeton':
        JETON[p[1]] = p[2]
        continue
    if not p[0].startswith('@'):
        s = re.sub(r'§(\w)§(nin|nın|in|ın|si|sı|nde|nda|de|da|ye|ya|ne|na|e|a|yi|yı|i|ı)?(?![a-zçğıöşüâîû])', lambda m: ekle(JETON[m.group(1)], KANON.get(m.group(2), m.group(2))), p[1])
        assert '§' not in s, l
        s = ('İ' + s[1:]) if s[0] == 'i' else (s[0].upper() + s[1:])
        p[1] = s
    out.append('\t'.join(p))
open(hedef, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
