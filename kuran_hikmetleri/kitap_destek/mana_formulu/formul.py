"""Mana türetme formülü: kök = ESAS + işlem dizisi. Her işlem sabit bir yöne sahip ok olarak çizilir;
aynı formül aynı şekli verir (kökün 'mana imzası')."""
import sys, math, json, html, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'kafes_ornek'))
import kafes3_kafes as K
HERE = pathlib.Path(__file__).resolve().parent
# işlem envanteri: ad, tür (mürsel mecaz = bitişiklik; istiare = benzerlik), yön (derece), renk, tarif
OP = {
 'İLK':    ('bitişiklik', 200, '#2f6fb3', 'işin ilk safhası'),
 'NETİCE': ('bitişiklik', 270, '#1f4e8c', 'işin neticesi (fiil tamamlanınca olan)'),
 'NHAL':   ('bitişiklik', 300, '#2c8c7c', 'neticede kalan hâl'),
 'MEFUL':  ('bitişiklik', 250, '#c26a1e', 'işin üstüne düştüğü şey'),
 'AMAC':   ('bitişiklik', 305, '#a8478f', 'işin gayesine uygunluk'),
 'NVASF':  ('bitişiklik', 350, '#3f8f3a', 'neticenin vasfı'),
 'VASITA': ('bitişiklik', 40,  '#6a8f3a', 'işin aleti / vasıtası'),
 'ZAMAN':  ('bitişiklik', 340,   '#7a7a3a', 'aynı netice başka sebeple (zamanla)'),
 'HAL':    ('bitişiklik', 210, '#16a085', 'yaratılışta verilen hâl'),
 'ICE':    ('benzerlik',  150, '#8e44ad', 'maddîden manevîye geçiş'),
 'NIZAM':  ('benzerlik',  100, '#6a5acd', 'tekilden düzene, ilme'),
 'ASIRI':  ('benzerlik',  160, '#c0392b', 'hâlin taşması'),
 'TEKELLUF':('benzerlik', 60,  '#d35400', 'olmayanı kendine yüklemek'),
 'TAKLIT': ('benzerlik',  185, '#b03060', 'işi dille taklit etmek (sahtesi)'),
}
# kök formülü: (çocuk, işlem, ebeveyn(ler))
F = [('A', 'İLK', ['E']), ('B', 'NVASF', ['E']), ('C', 'MEFUL', ['E']), ('H', 'AMAC', ['E']),
     ('D', 'NETİCE', ['A']), ('N', 'NHAL', ['A', 'B']), ('F', 'ZAMAN', ['B']), ('G', 'VASITA', ['B']),
     ('J', 'MEFUL', ['D']), ('K', 'HAL', ['D']), ('L', 'TAKLIT', ['D']),
     ('U', 'ICE', ['K']), ('X', 'NIZAM', ['U']), ('Y', 'ASIRI', ['U']), ('Z', 'TEKELLUF', ['U'])]
AD = {'E': 'ESAS: ölçüp biçerek hazırlamak'} | {a: K.MANA[a]['metin'] for a in K.MANA}
# yazılı formül
satir = ['خلق ≔ ESAS(ham maddeyi murad edilen şey olsun diye ölçüp biçerek hazırlamak)']
for c, o, p in F:
    satir.append(f"  {AD[c]} = {o}({', '.join('ESAS' if q == 'E' else AD[q] for q in p)})")
(HERE / 'formul.txt').write_text('\n'.join(satir), encoding='utf-8')
# kelimeler: her kelime = vezin(mana)
W = []
for g, k in K.KELIME.items():
    for m, tr in k['anlam'].items():
        W.append((k['ar'], k['tag'], m, tr, k['kuran']))
# şekil: kaplumbağa çizimi
L = 250
P = {'E': (0.0, 0.0)}
for c, o, p in F:
    t = math.radians(OP[o][1])
    bx = sum(P[q][0] for q in p) / len(p); by = sum(P[q][1] for q in p) / len(p)
    P[c] = (bx + L * math.cos(t), by - L * math.sin(t))
xs = [v[0] for v in P.values()]; ys = [v[1] for v in P.values()]
pad = 230
ox, oy = -min(xs) + pad, -min(ys) + pad + 60
GW = max(xs) - min(xs) + 2 * pad; GH = max(ys) - min(ys) + 2 * pad + 60
esc = html.escape
# sayfa: sol şekil, sağ formül, alt pusula
TW = 760
Wt, Ht = GW + TW, max(GH, 900) + 330
b = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wt:.0f}" height="{Ht:.0f}" viewBox="0 0 {Wt:.0f} {Ht:.0f}" font-family="Inter, DejaVu Sans, sans-serif"><rect width="100%" height="100%" fill="#fffdf6"/>',
     '<defs><marker id="ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="context-stroke"/></marker></defs>',
     f'<text x="24" y="38" font-size="24" font-weight="700" fill="#2b2410">خلق kökünün mana imzası</text>',
     f'<text x="24" y="62" font-size="13" fill="#6d6650">Her işlem pusulada sabit bir yöne bakar. Aynı formülü taşıyan iki kök aynı şekli çizer; şekil formülün kendisidir.</text>']
for c, o, p in F:
    for q in p:
        x1, y1 = P[q][0] + ox, P[q][1] + oy; x2, y2 = P[c][0] + ox, P[c][1] + oy
        col = OP[o][2]; dash = '' if OP[o][0] == 'bitişiklik' else ' stroke-dasharray="9 5"'
        b.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="4"{dash} marker-end="url(#ok)" style="stroke:{col}"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        b.append(f'<text x="{mx:.1f}" y="{my-6:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="{col}" paint-order="stroke" stroke="#fffdf6" stroke-width="3">{o}</text>')
for n, (x, y) in P.items():
    r = 11 if n == 'E' else 7
    b.append(f'<circle cx="{x+ox:.1f}" cy="{y+oy:.1f}" r="{r}" fill="{"#e8c766" if n=="E" else "#2b2410"}" stroke="#2b2410"/>')
    lab = AD[n] if n != 'E' else 'ESAS'
    b.append(f'<text x="{x+ox+12:.1f}" y="{y+oy+18:.1f}" font-size="12.5" fill="#2b2410" paint-order="stroke" stroke="#fffdf6" stroke-width="3">{esc(lab)}</text>')
    ws = [w for w in W if w[2] == n]
    for k, w in enumerate(ws[:3]):
        b.append(f'<text x="{x+ox+12:.1f}" y="{y+oy+36+k*18:.1f}" font-size="15" font-family="Amiri, serif" fill="#555" paint-order="stroke" stroke="#fffdf6" stroke-width="3">{esc(w[0])} <tspan font-size="9.5" font-family="Inter, sans-serif">{esc(w[1])}</tspan></text>')
    if len(ws) > 3:
        b.append(f'<text x="{x+ox+12:.1f}" y="{y+oy+36+3*18:.1f}" font-size="10" fill="#888">+{len(ws)-3} kelime</text>')
# sağ: yazılı formül
x0 = GW + 10
b.append(f'<text x="{x0}" y="110" font-size="16" font-weight="700" fill="#2b2410">Formül (her satır bir mana)</text>')
for k, s in enumerate(satir):
    b.append(f'<text x="{x0}" y="{140+k*24}" font-size="12.5" font-family="DejaVu Sans Mono, monospace" fill="#2b2410">{esc(s)}</text>')
b.append(f'<text x="{x0}" y="{150+len(satir)*24+20}" font-size="12.5" fill="#6d6650">Kelime = vezin(mana). Örnek: خَالِق = ism-i fâil(yaratmak); مَخْلُوق = ism-i mef‘ûl(yaratmak) = yaratılmış.</text>')
b.append(f'<text x="{x0}" y="{150+len(satir)*24+42}" font-size="12.5" fill="#6d6650">Böylece 16 mana ve 37 kelime: 1 esas + 15 işlem + kelime başına 1 vezin ile türetilir.</text>')
# alt: pusula
cx, cy, R = 220, max(GH, 900) + 150, 115
b.append(f'<text x="24" y="{cy-R-30}" font-size="16" font-weight="700" fill="#2b2410">İşlem pusulası (yön = işlem; düz çizgi bitişiklik / mürsel mecaz, kesikli çizgi benzerlik / istiare)</text>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#d9cfa8"/>')
lx = cx + R + 60
for k, (o, (tur, ang, col, tarif)) in enumerate(OP.items()):
    t = math.radians(ang); dash = '' if tur == 'bitişiklik' else ' stroke-dasharray="7 4"'
    b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+R*math.cos(t):.1f}" y2="{cy-R*math.sin(t):.1f}" stroke="{col}" stroke-width="3"{dash}/>')
    b.append(f'<text x="{cx+(R+16)*math.cos(t):.1f}" y="{cy-(R+16)*math.sin(t)+4:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="{col}">{o}</text>')
    col2 = k // 7; row = k % 7
    b.append(f'<text x="{lx+col2*420}" y="{cy-R+row*30}" font-size="12" fill="{col}"><tspan font-weight="700">{o}</tspan> <tspan fill="#2b2410">{esc(tarif)} ({tur})</tspan></text>')
b.append('</svg>')
(HERE / 'mana_imzasi.svg').write_text(''.join(b), encoding='utf-8')
# ölçü: bit
import math as m2
n_mana = len(F); n_op = len(OP)
bit_formul = n_mana * (m2.log2(n_op) + m2.log2(n_mana + 1))
print('formül satırı', n_mana, 'işlem türü', n_op, 'formül biti ~', round(bit_formul))
print('\n'.join(satir))
