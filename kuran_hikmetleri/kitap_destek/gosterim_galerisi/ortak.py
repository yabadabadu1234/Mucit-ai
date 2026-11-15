import sys, math, html, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'kafes_ornek'))
from kafes2_veri import nodes
import kafes3_kafes as K
HERE = pathlib.Path(__file__).resolve().parent
esc = html.escape
MANA = {i: n for i, n in nodes.items() if n['tur'] == 'm'}          # E dâhil
KEL = K.KELIME
KIDS = collections.defaultdict(list)
for i, n in MANA.items():
    for p in n['ebeveyn']: KIDS[p].append(i)
ORDER = ['E', 'A', 'D', 'J', 'K', 'U', 'X', 'Y', 'Z', 'L', 'N', 'B', 'F', 'G', 'C', 'H', 'R2']
def depth(i):
    p = MANA[i]['ebeveyn']
    return 0 if not p else 1 + max(depth(q) for q in p)
def dal(i):
    if i in ('E',): return 'E'
    if i == 'R2': return 'R2'
    if i == 'N': return 'AB'
    p = MANA[i]['ebeveyn']
    return i if p == ['E'] else dal(p[0])
RENK = {'A': '#2f6fb3', 'B': '#3f8f3a', 'AB': '#2c8c7c', 'C': '#c26a1e', 'H': '#a8478f', 'R2': '#7a7a7a', 'E': '#b8860b'}
AD = {i: ('ESAS: ölçüp biçerek hazırlamak' if i == 'E' else MANA[i]['metin']) for i in MANA}
KISA = {'E': 'esas', 'A': 'ölçüp biçmek', 'B': 'düzlemek', 'C': 'pay', 'H': 'yakışmak', 'D': 'yaratmak', 'N': 'şekli belirmiş',
        'F': 'eskimek', 'G': 'koku sürmek', 'J': 'yaratılmış', 'K': 'yaradılış', 'L': 'uydurmak', 'U': 'huy', 'X': 'ahlâk',
        'Y': 'öfke', 'Z': 'huy takınmak', 'R2': 'kök dışı'}
WORDS_OF = collections.defaultdict(list)
for w, k in KEL.items():
    for m in k['anlam']: WORDS_OF[m].append(w)
def alt_say(i, seen=None):
    s = set(WORDS_OF.get(i, []))
    for c in KIDS.get(i, []): s |= alt_say(c)
    return s
def AR(t, x, y, size=16, anchor='middle', fill='#1a1a1a'):
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" font-family="Amiri, Noto Naskh Arabic, serif" fill="{fill}">{esc(t)}</text>'
def T(t, x, y, size=11, anchor='middle', fill='#2b2410', w=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" {w}>{esc(t)}</text>'
def kaydet(ad, baslik, alt, body, W=900, H=640):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, DejaVu Sans, sans-serif">'
         f'<rect width="100%" height="100%" fill="#fffdf6"/>'
         f'<text x="18" y="30" font-size="19" font-weight="700" fill="#2b2410">{esc(baslik)}</text>'
         f'<text x="18" y="50" font-size="11.5" fill="#6d6650">{esc(alt)}</text>' + ''.join(body) + '</svg>')
    (HERE / f'{ad}.svg').write_text(s, encoding='utf-8')
