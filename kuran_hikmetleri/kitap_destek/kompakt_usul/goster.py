import sys, json, html, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'kafes_ornek'))
import kafes3_kafes as K
HERE = pathlib.Path(__file__).resolve().parent
r = json.load(open(HERE / 'faktor_rapor.json', encoding='utf-8'))
ar2g = {K.KELIME[g]['ar']: g for g in K.KELIME}; t2m = {K.MANA[m]['metin']: m for m in K.MANA}
G0, M0 = list(K.KELIME), list(K.MANA)
I = {(g, m) for g in G0 for m in M0 if m in K.KELIME[g]['anlam']}
F = [([ar2g[a] for a in f['kelimeler']], [t2m[t] for t in f['manalar']]) for f in r['faktorler']]
# sıralama: çarpan sırasına göre satır ve sütun
G1, M1 = [], []
for A, B in F:
    for g in A:
        if g not in G1: G1.append(g)
    for m in B:
        if m not in M1: M1.append(m)
PAL = ['#2f6fb3','#3f8f3a','#c26a1e','#a8478f','#2c8c7c','#b8860b','#6a5acd','#c0392b','#16a085','#8e44ad','#d35400','#27ae60','#2980b9','#7f8c8d','#e67e22']
C, LW, T = 26, 260, 250
esc = html.escape
def matris(x0, G, M, faktorlu):
    s = []
    for j, m in enumerate(M):
        s.append(f'<text transform="translate({x0+LW+j*C+C/2+4},{T-6}) rotate(-60)" font-size="11" fill="#333">{esc(K.MANA[m]["metin"][:26])}</text>')
    for i, g in enumerate(G):
        y = T + i * C
        if i % 2 == 0: s.append(f'<rect x="{x0}" y="{y}" width="{LW+len(M)*C}" height="{C}" fill="#f4efe0" opacity=".5"/>')
        s.append(f'<text x="{x0+LW-8}" y="{y+19}" text-anchor="end" font-size="17" font-family="Amiri, serif">{esc(K.KELIME[g]["ar"])}</text>')
        s.append(f'<text x="{x0+6}" y="{y+17}" font-size="10" fill="#666">{esc(" / ".join(dict.fromkeys(K.KELIME[g]["anlam"].values()))[:30])}</text>')
    s.append(f'<rect x="{x0+LW}" y="{T}" width="{len(M)*C}" height="{len(G)*C}" fill="none" stroke="#bbb"/>')
    if faktorlu:
        for k, (A, B) in enumerate(F):
            col = PAL[k % len(PAL)]
            for g in A:
                for m in B:
                    i, j = G.index(g), M.index(m)
                    s.append(f'<rect x="{x0+LW+j*C+2}" y="{T+i*C+2}" width="{C-4}" height="{C-4}" rx="4" fill="{col}" opacity=".85"/>')
            ii = sorted(G.index(g) for g in A); jj = sorted(M.index(m) for m in B)
            def kos(v):
                out=[[v[0],v[0]]]
                for x in v[1:]:
                    if x==out[-1][1]+1: out[-1][1]=x
                    else: out.append([x,x])
                return out
            for a1,a2 in kos(ii):
                for b1,b2 in kos(jj):
                    s.append(f'<rect x="{x0+LW+b1*C}" y="{T+a1*C}" width="{(b2-b1+1)*C}" height="{(a2-a1+1)*C}" fill="none" stroke="{col}" stroke-width="2.4" rx="5"/>')
            if len(B)>1:
                s.append(f'<line x1="{x0+LW+jj[0]*C+C/2}" y1="{T+ii[0]*C+C/2}" x2="{x0+LW+jj[-1]*C+C/2}" y2="{T+ii[0]*C+C/2}" stroke="{col}" stroke-width="2" stroke-dasharray="4 3"/>')
    else:
        for (g, m) in I:
            i, j = G.index(g), M.index(m)
            s.append(f'<circle cx="{x0+LW+j*C+C/2}" cy="{T+i*C+C/2}" r="7" fill="#444"/>')
    return s
W = 2 * (LW + len(M0) * C) + 140; H = T + len(G0) * C + 60
b = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, DejaVu Sans, sans-serif"><rect width="100%" height="100%" fill="#fffdf6"/>']
b.append(f'<text x="20" y="34" font-size="20" font-weight="700">Önce: ham tablo (sözlük sırası) — 47 nokta, 433 bit</text>')
x2 = LW + len(M0) * C + 100
b.append(f'<text x="{x2}" y="34" font-size="20" font-weight="700">Sonra: 15 kavram dikdörtgeni, yan yana dizilmiş — 316 bit</text>')
b.append(f'<text x="{x2}" y="58" font-size="12" fill="#555">Her renkli dikdörtgen bir cümle: "bu kelimeler bu manaların hepsini taşır". Kesikli çizgi: birden çok manalı kelimenin dikdörtgeni.</text>')
b += matris(20, sorted(G0, key=lambda g: K.KELIME[g]['ar']), M0, False)
b += matris(x2, G1, M1, True)
b.append('</svg>')
(HERE / 'once_sonra.svg').write_text(''.join(b), encoding='utf-8')
