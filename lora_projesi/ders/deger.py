import re

ONEK = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, 'k': 1e3, 'K': 1e3, 'M': 1e6, 'G': 1e9}


def sayi(metin):
    """'31,6k 1%' -> 31600.0 ; '10uF 6,3V' -> 1e-5 ; '4,7uH 5A' -> 4.7e-6 ; '5,1k' -> 5100."""
    m = re.match(r'\s*([0-9]+(?:[.,][0-9]+)?)\s*([pnuµmkKMG]?)\s*([A-Za-zΩ]*)', metin)
    if not m:
        return None
    v = float(m.group(1).replace(',', '.'))
    return v * ONEK.get(m.group(2), 1.0)


def tolerans(metin):
    m = re.search(r'([0-9]+(?:[.,][0-9]+)?)\s*%', metin)
    return float(m.group(1).replace(',', '.')) if m else None


def bicim(x, birim='', basamak=4):
    if x is None:
        return '?'
    for ek, k in (('G', 1e9), ('M', 1e6), ('k', 1e3), ('', 1.0), ('m', 1e-3), ('µ', 1e-6), ('n', 1e-9), ('p', 1e-12)):
        if abs(x) >= k * 0.9999 or ek == 'p':
            s = ('%.' + str(basamak) + 'g') % (x / k)
            return s.replace('.', ',') + ' ' + ek + birim
    return str(x)
