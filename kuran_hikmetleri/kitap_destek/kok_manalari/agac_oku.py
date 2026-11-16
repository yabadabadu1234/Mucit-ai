"""agac/*.txt türeme haritalarını okur: satır = kök|asıl{türeyen;türeyen{...}}|asıl ..."""
import pathlib, json
HERE = pathlib.Path(__file__).resolve().parent
def ayristir(s, ayrac):
    out, d, b = [], 0, ''
    for c in s:
        if c == '{': d += 1
        elif c == '}': d -= 1
        if c == ayrac and d == 0: out.append(b); b = ''
        else: b += c
    assert d == 0, s
    out.append(b); return [x.strip() for x in out if x.strip()]
def dugum(s):
    if '{' in s:
        i = s.index('{'); assert s.endswith('}'), s
        return {'mana': s[:i].strip(), 'turev': [dugum(x) for x in ayristir(s[i + 1:-1], ';')]}
    assert '}' not in s and ';' not in s, s
    return {'mana': s.strip(), 'turev': []}
def oku():
    A = {}
    for f in sorted((HERE / 'agac').glob('*.txt')):
        for n, sat in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            if not sat.strip(): continue
            k, gov = sat.split('|', 1)
            try: A[k] = [dugum(x) for x in ayristir(gov, '|')]
            except AssertionError as e: raise SystemExit(f'{f.name}:{n} {e}')
    return A
if __name__ == '__main__':
    A = oku(); VT = json.load(open(HERE / 'KOK_ESAS_MANALARI.json', encoding='utf-8'))
    say = lambda L: sum(1 + say(x['turev']) for x in L)
    print(len(A), 'kök', sum(say(v) for v in A.values()), 'düğüm; eksik', len([k for k in VT if k not in A]))
