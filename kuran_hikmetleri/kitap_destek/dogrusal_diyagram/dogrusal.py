"""Doğrusal diyagram (linear diagram): her mana bir dikey çizgi, her kelime bir satır.
Kelimenin taşıdığı manaların çizgileri o satırdan geçer. Satır sırası, çizgi parçası sayısını en aza indirecek biçimde aranır."""
import sys, json, html, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'kafes_ornek'))
from kafes2_veri import nodes
import kafes3_kafes as K
HERE = pathlib.Path(__file__).resolve().parent
KEL, MANA = K.KELIME, K.MANA
# sütun sırası: türeme ağacının derinlik-öncelikli gezişi; N, A ile B arasında
SUT = ['A', 'D', 'J', 'K', 'U', 'X', 'Y', 'Z', 'L', 'N', 'B', 'F', 'G', 'C', 'H', 'R2']
assert sorted(SUT) == sorted(MANA), (sorted(SUT), sorted(MANA))
WORDS = list(KEL)
uye = {w: set(KEL[w]['anlam']) for w in WORDS}

def parca(sira):
    n = 0
    for a in SUT:
        ic = False
        for w in sira:
            if a in uye[w]:
                if not ic: n += 1; ic = True
            else: ic = False
    return n
# başlangıç: üyelik vektörüne göre sözlük sırası
sira = sorted(WORDS, key=lambda w: [0 if a in uye[w] else 1 for a in SUT])
ilk = parca(sira)
iyi = True
while iyi:
    iyi = False
    for i in range(len(sira)):
        for j in range(len(sira)):
            if i == j: continue
            s = sira[:]; w = s.pop(i); s.insert(j, w)
            if parca(s) < parca(sira): sira = s; iyi = True
son = parca(sira)
alt_sinir = sum(1 for a in SUT if any(a in uye[w] for w in WORDS))
print('çizgi parçası: ilk', ilk, 'son', son, 'alt sınır (her mana tek parça)', alt_sinir)

RENK = {'a': '#2f6fb3', 'b': '#3f8f3a', 'c': '#c26a1e', 'h': '#a8478f', 'ab': '#2c8c7c', 'dis': '#7a7a7a'}
ROW_H, COL_W, LBL_W, TOP = 34, 46, 300, 330
W = LBL_W + COL_W * len(SUT) + 40
H = TOP + ROW_H * len(sira) + 40
xc = {a: LBL_W + COL_W * k + COL_W / 2 for k, a in enumerate(SUT)}
esc = html.escape
S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, DejaVu Sans, sans-serif">',
     f'<rect width="100%" height="100%" fill="#fffdf6"/>']
# başlık: esas bandı ve türeme ağacı (sütunlar arası yaylar)
S.append(f'<rect x="{xc["A"]-COL_W/2+2}" y="14" width="{xc["H"]-xc["A"]+COL_W-4}" height="34" rx="8" fill="#f1d98a" stroke="#7a6a3c"/>')
S.append(f'<text x="{(xc["A"]+xc["H"])/2}" y="36" text-anchor="middle" font-size="13" font-weight="700" fill="#2b2410">ESAS: {esc(nodes["E"]["metin"])}</text>')
S.append(f'<rect x="{xc["R2"]-COL_W/2+2}" y="14" width="{COL_W-4}" height="34" rx="8" fill="#e3e3e3" stroke="#7a6a3c"/><text x="{xc["R2"]}" y="35" text-anchor="middle" font-size="10" fill="#333">kök dışı</text>')
# derinlik
def dp(a):
    p = [q for q in MANA[a]['ebeveyn'] if q != 'E']
    return 1 if not p else 1 + max(dp(q) for q in p)
YH = {a: 70 + dp(a) * 34 for a in SUT if a != 'R2'}; YH['R2'] = 70 + 34
# türeme kenarları (yay)
sebepler = []
for a in SUT:
    for q in MANA[a]['ebeveyn']:
        x2, y2 = xc[a], YH[a]
        if q == 'E' or q not in xc:
            x1, y1 = x2, 48
        else:
            x1, y1 = xc[q], YH[q]
        col = RENK.get(MANA[a]['renk'], '#555')
        S.append(f'<path d="M{x1},{y1+6} C{x1},{(y1+y2)/2+6} {x2},{(y1+y2)/2} {x2},{y2-8}" fill="none" stroke="{col}" stroke-width="1.6" stroke-opacity=".8"/>')
        if MANA[a].get('sebep'):
            sebepler.append((q if q != 'E' else 'ESAS', a, MANA[a]['sebep']))
    S.append(f'<circle cx="{xc[a]}" cy="{YH[a]}" r="6" fill="{RENK.get(MANA[a]["renk"], "#555")}"/>')
# mana adları: eğik yazı, köke uzaklık başlığın altında
for a in SUT:
    S.append(f'<text transform="translate({xc[a]+4},{TOP-10}) rotate(-58)" font-size="12" font-weight="700" fill="{RENK.get(MANA[a]["renk"], "#555")}">{esc(MANA[a]["metin"])}</text>')
    S.append(f'<text x="{xc[a]}" y="{YH[a]-10}" text-anchor="middle" font-size="9" fill="#7a6a3c">{a}</text>')
# satırlar
for i, w in enumerate(sira):
    y = TOP + i * ROW_H
    if i % 2 == 0: S.append(f'<rect x="8" y="{y}" width="{W-16}" height="{ROW_H}" fill="#f4efe0" opacity=".55"/>')
    k = KEL[w]
    tr = ' / '.join(dict.fromkeys(k['anlam'].values()))
    S.append(f'<text x="{LBL_W-10}" y="{y+23}" text-anchor="end" font-size="20" font-family="Amiri, Noto Naskh Arabic, serif" direction="rtl">{esc(k["ar"])}</text>')
    S.append(f'<text x="14" y="{y+15}" font-size="10.5" fill="#2b2410">{esc(tr[:46])}</text>')
    S.append(f'<text x="14" y="{y+27}" font-size="9" fill="#7a7a7a">{esc(k["tag"] + (" " + k["kuran"] if k["kuran"] else ""))}</text>')
# kılavuz çizgileri (sütun boyunca soluk) ve mana çizgileri (parça parça)
for a in SUT:
    S.append(f'<line x1="{xc[a]}" y1="{TOP}" x2="{xc[a]}" y2="{TOP+ROW_H*len(sira)}" stroke="#d9cfa8" stroke-width="1" stroke-dasharray="2 4"/>')
    col = RENK.get(MANA[a]['renk'], '#555')
    i = 0
    while i < len(sira):
        if a in uye[sira[i]]:
            j = i
            while j + 1 < len(sira) and a in uye[sira[j + 1]]: j += 1
            S.append(f'<line x1="{xc[a]}" y1="{TOP+i*ROW_H+7}" x2="{xc[a]}" y2="{TOP+(j+1)*ROW_H-7}" stroke="{col}" stroke-width="5" stroke-linecap="round"/>')
            i = j + 1
        else: i += 1
# kesişim kılavuzu: birden çok manalı satırda yatay ince çizgi
for i, w in enumerate(sira):
    if len(uye[w]) > 1:
        xs = [xc[a] for a in SUT if a in uye[w]]
        y = TOP + i * ROW_H + ROW_H / 2
        S.append(f'<line x1="{min(xs)}" y1="{y}" x2="{max(xs)}" y2="{y}" stroke="#555" stroke-width="1" stroke-dasharray="3 3"/>')
S.append('</svg>')
(HERE / 'dogrusal.svg').write_text('\n'.join(S), encoding='utf-8')
(HERE / 'sebepler.json').write_text(json.dumps(sebepler, ensure_ascii=False, indent=1), encoding='utf-8')
json.dump(dict(satir=len(sira), sutun=len(SUT), cizgi_parcasi_ilk=ilk, cizgi_parcasi=son, alt_sinir=alt_sinir, sira=[KEL[w]['ar'] for w in sira]),
          open(HERE / 'dogrusal_rapor.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
