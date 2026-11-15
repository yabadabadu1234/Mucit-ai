import sys, json, html, math, pathlib, itertools, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'kafes_ornek'))
from kafes2_veri import nodes
import kafes3_kafes as K
HERE = pathlib.Path(__file__).resolve().parent
KEL, MANA = K.KELIME, K.MANA
SUT = ['A', 'D', 'J', 'K', 'U', 'X', 'Y', 'Z', 'L', 'N', 'B', 'F', 'G', 'C', 'H', 'R2']
rap = json.load(open(HERE.parent / 'dogrusal_diyagram' / 'dogrusal_rapor.json', encoding='utf-8'))
ar2k = {KEL[w]['ar']: w for w in KEL}
SIRA = [ar2k[a] for a in rap['sira']]
uye = {w: set(KEL[w]['anlam']) for w in KEL}
def dp(a):
    p = [q for q in MANA[a]['ebeveyn'] if q != 'E']
    return 1 if not p else 1 + max(dp(q) for q in p)
DP = {a: (dp(a) if a != 'R2' else 1) for a in SUT}
def dal(a):
    if a == 'R2': return 'dış'
    if a == 'N': return 'A·B'
    p = [q for q in MANA[a]['ebeveyn'] if q != 'E']
    return a if not p else dal(p[0])
DAL = {a: dal(a) for a in SUT}
DALAD = {'A': 'ölçüp biçme → yaratma dalı', 'B': 'düzleme dalı', 'A·B': 'ölçüp düzleme (iki dal)', 'C': 'pay dalı', 'H': 'yakışma dalı', 'dış': 'kök dışı'}
RENK = {'A': '#2f6fb3', 'B': '#3f8f3a', 'A·B': '#2c8c7c', 'C': '#c26a1e', 'H': '#a8478f', 'dış': '#7a7a7a'}
esc = html.escape
AR = 'font-family="Amiri, Noto Naskh Arabic, serif"'
def svg(W, H, body, ad):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, DejaVu Sans, sans-serif"><rect width="100%" height="100%" fill="#fffdf6"/>' + ''.join(body) + '</svg>'
    (HERE / f'{ad}.svg').write_text(s, encoding='utf-8')
def baslik(t, alt):
    return [f'<text x="20" y="34" font-size="22" font-weight="700" fill="#2b2410">{esc(t)}</text>', f'<text x="20" y="58" font-size="13" fill="#6d6650">{esc(alt)}</text>']
MN = {a: MANA[a]['metin'] for a in SUT}
EDGES = [(w, a) for w in SIRA for a in SUT if a in uye[w]]

# ---------- 1. BioFabric ----------
rows = SUT + SIRA
RH, CW, LW, T = 22, 16, 330, 90
ri = {n: i for i, n in enumerate(rows)}
# kenar sırası: önce küçük satırlı ucu
E1 = sorted(EDGES, key=lambda e: (min(ri[e[0]], ri[e[1]]), max(ri[e[0]], ri[e[1]])))
W = LW + CW * len(E1) + 40; H = T + RH * len(rows) + 30
b = baslik('BioFabric: her düğüm bir yatay çizgi, her kenar bir dikey çizgi', 'Üstte 16 mana, altta 37 kelime. Her dikey çizgi bir "kelime şu manayı taşır" bağı. Çizgi kesişmesi olmaz.')
span = {n: [None, None] for n in rows}
for k, (w, a) in enumerate(E1):
    x = LW + CW * k + CW / 2
    for n in (w, a):
        s = span[n]; s[0] = x if s[0] is None else min(s[0], x); s[1] = x if s[1] is None else max(s[1], x)
for n in rows:
    y = T + ri[n] * RH + RH / 2
    if n in MANA:
        c = RENK[DAL[n]]
        b.append(f'<text x="{LW-8}" y="{y+4}" text-anchor="end" font-size="11.5" font-weight="700" fill="{c}">{esc(MN[n])}</text>')
    else:
        c = '#444'
        b.append(f'<text x="{LW-8}" y="{y+6}" text-anchor="end" font-size="16" {AR} direction="rtl">{esc(KEL[n]["ar"])}</text>')
        b.append(f'<text x="12" y="{y+4}" font-size="10" fill="#555">{esc(" / ".join(dict.fromkeys(KEL[n]["anlam"].values()))[:42])}</text>')
    if span[n][0] is not None:
        b.append(f'<line x1="{span[n][0]-4}" y1="{y}" x2="{span[n][1]+4}" y2="{y}" stroke="{c}" stroke-width="2"/>')
for k, (w, a) in enumerate(E1):
    x = LW + CW * k + CW / 2
    y1 = T + ri[a] * RH + RH / 2; y2 = T + ri[w] * RH + RH / 2
    b.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{RENK[DAL[a]]}" stroke-width="3" stroke-opacity=".75"/>')
    b += [f'<circle cx="{x}" cy="{y1}" r="3" fill="{RENK[DAL[a]]}"/>', f'<circle cx="{x}" cy="{y2}" r="3" fill="{RENK[DAL[a]]}"/>']
svg(W, H, b, '1_biofabric')

# ---------- 2. Kovan çizimi (hive plot) ----------
W, H = 1500, 1300; cx, cy = 750, 700
ax = {'mana': -90, 'tek': 30, 'cok': 150}
b = baslik('Kovan çizimi: düğüm, estetiğe göre değil kurala göre eksene konur', 'Yukarı eksen: manalar (merkezden uzaklık = köke uzaklık). Sağ alt: tek manalı kelimeler. Sol alt: çok manalı kelimeler. Bağlar eksenler arasında yay.')
def pt(axn, r):
    t = math.radians(ax[axn]); return cx + r * math.cos(t), cy + r * math.sin(t)
pos = {}
# manalar: köke uzaklığa göre, aynı derinlikte yan yana küçük kaydırma
by = collections.defaultdict(list)
for a in SUT: by[DP[a]].append(a)
for d, lst in by.items():
    for k, a in enumerate(lst): pos[a] = ('mana', 90 + d * 95 + k * 20)
tek = [w for w in SIRA if len(uye[w]) == 1]; cok = [w for w in SIRA if len(uye[w]) > 1]
for k, w in enumerate(tek): pos[w] = ('tek', 90 + k * 19)
for k, w in enumerate(cok): pos[w] = ('cok', 90 + k * 60)
for n in ax:
    x2, y2 = pt(n, 700 if n == 'tek' else (620 if n == 'mana' else 560))
    b.append(f'<line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="#bbb" stroke-width="3"/>')
for w, a in EDGES:
    p1 = pt(*pos[a]); p2 = pt(*pos[w])
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    qx, qy = cx + (mx - cx) * 1.35, cy + (my - cy) * 1.35
    b.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} Q{qx:.1f},{qy:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{RENK[DAL[a]]}" stroke-width="1.6" stroke-opacity=".7"/>')
for n, (axn, r) in pos.items():
    x, y = pt(axn, r)
    if n in MANA:
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{RENK[DAL[n]]}"/><text x="{x+10:.1f}" y="{y+4:.1f}" font-size="10.5" font-weight="700" fill="{RENK[DAL[n]]}">{esc(MN[n])}</text>')
    else:
        anc = 'start' if axn == 'tek' else 'end'; dx = 8 if axn == 'tek' else -8
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#333"/><text x="{x+dx:.1f}" y="{y+5:.1f}" text-anchor="{anc}" font-size="14" {AR}>{esc(KEL[n]["ar"])}</text>')
svg(W, H, b, '2_kovan')

# ---------- 3. Anlamsal zemin (semantic substrates) ----------
dallar = ['A', 'A·B', 'B', 'C', 'H', 'dış']
W = 1500; RGH = {'A': 470, 'A·B': 110, 'B': 230, 'C': 80, 'H': 120, 'dış': 70}
H = 90 + sum(RGH.values()) + 20 * len(dallar) + 30
b = baslik('Anlamsal zemin: düğüm, vasfına göre bölgeye konur', 'Her bölge bir dal. Bölge içinde soldan sağa köke uzaklık (1–5). Kelime, manalarından ilkinin bölgesine konur; başka daldaki manasına çizgi uzanır.')
y0 = 80; ry = {}
for d in dallar:
    ry[d] = (y0, RGH[d])
    b.append(f'<rect x="20" y="{y0}" width="{W-40}" height="{RGH[d]}" rx="10" fill="{RENK[d]}" fill-opacity=".08" stroke="{RENK[d]}"/>')
    b.append(f'<text x="30" y="{y0+18}" font-size="13" font-weight="700" fill="{RENK[d]}">{esc(DALAD[d])}</text>')
    y0 += RGH[d] + 20
for k in range(1, 6):
    x = 200 + (k - 1) * 260
    b.append(f'<text x="{x}" y="76" font-size="11" fill="#7a6a3c">köke uzaklık {k}</text>')
mpos = {}; cnt = collections.Counter()
for a in SUT:
    d = DAL[a]; y, h = ry[d]
    x = 200 + (DP[a] - 1) * 260
    yy = y + 40 + cnt[(d, DP[a])] * 120; cnt[(d, DP[a])] += 1
    mpos[a] = (x, min(yy, y + h - 20))
wpos = {}; wc = collections.Counter()
for w in SIRA:
    ana = [a for a in SUT if a in uye[w]][0]
    x, y = mpos[ana]
    k = wc[ana]; wc[ana] += 1
    wpos[w] = (x + 30 + (k % 3) * 70, y + 26 + (k // 3) * 26)
for w in SIRA:
    for a in SUT:
        if a in uye[w]:
            b.append(f'<line x1="{mpos[a][0]}" y1="{mpos[a][1]}" x2="{wpos[w][0]}" y2="{wpos[w][1]-5}" stroke="{RENK[DAL[a]]}" stroke-width="{1.2 if DAL[a]==DAL[[q for q in SUT if q in uye[w]][0]] else 2.4}" stroke-opacity=".6"/>')
for a, (x, y) in mpos.items():
    b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{RENK[DAL[a]]}"/><text x="{x+9}" y="{y-6}" font-size="11" font-weight="700" fill="{RENK[DAL[a]]}">{esc(MN[a])}</text>')
for w, (x, y) in wpos.items():
    b.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="15" {AR}>{esc(KEL[w]["ar"])}</text>')
svg(W, H, b, '3_anlamsal_zemin')

# ---------- 4. İç içe çizgi diyagramı (nested line diagram) ----------
def kafes(objs, attrs, inc):
    exts = {frozenset(objs)} | {frozenset(o for o in objs if a in inc[o]) for a in attrs}
    ch = True
    while ch:
        ch = False
        for x, y in itertools.combinations(list(exts), 2):
            z = x & y
            if z not in exts: exts.add(z); ch = True
    exts = [e for e in exts if e]
    cov = [(b2, a2) for a2 in exts for b2 in exts if a2 < b2 and not any(a2 < c < b2 for c in exts)]
    return exts, cov
dal_inc = {w: {DAL[a] for a in uye[w]} for w in SIRA}
dis_ext, dis_cov = kafes(SIRA, dallar, dal_inc)
derin_inc = {w: {DP[a] for a in uye[w]} for w in SIRA}
def own_attr(e, attrs, inc, objs):
    I = set(attrs)
    for o in e: I &= inc[o]
    return I
H = 1150
b = baslik('İç içe çizgi diyagramı: kafes çarpanlara bölünür, biri öbürünün içine çizilir',
           'Dış kafes: dal (hangi daldan mana taşıyor). Her dış kutunun içinde iç kafes: köke uzaklık. Kelime en alttaki kavramına yazılır.')
rank = {}
def rk(e):
    if e in rank: return rank[e]
    ups = [u for u, a2 in dis_cov if a2 == e]
    rank[e] = 0 if not ups else 1 + max(rk(u) for u in ups)
    return rank[e]
for e in dis_ext: rk(e)
lv = collections.defaultdict(list)
for e in dis_ext: lv[rank[e]].append(e)
BW, BH = 300, 230
W = max(1100, max(len(v) for v in lv.values()) * (BW + 30) + 60)
box = {}
for L, lst in lv.items():
    lst.sort(key=lambda e: sorted(own_attr(e, dallar, dal_inc, SIRA)))
    tw = len(lst) * BW + (len(lst) - 1) * 30
    for k, e in enumerate(lst):
        box[e] = (W / 2 - tw / 2 + k * (BW + 30), 90 + L * (BH + 60))
for u, a2 in dis_cov:
    x1, y1 = box[u]; x2, y2 = box[a2]
    b.append(f'<line x1="{x1+BW/2}" y1="{y1+BH}" x2="{x2+BW/2}" y2="{y2}" stroke="#8d7f4f" stroke-width="3"/>')
for e, (x, y) in box.items():
    I = own_attr(e, dallar, dal_inc, SIRA)
    ttl = ' + '.join(DALAD[d].split(' ')[0] if d not in ('A·B', 'dış') else DALAD[d] for d in sorted(I)) or 'hepsi'
    b.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="12" fill="#fbf5e3" stroke="#8d7f4f" stroke-width="2"/>')
    b.append(f'<text x="{x+10}" y="{y+18}" font-size="11.5" font-weight="700" fill="#2b2410">{esc(ttl)}  ({len(e)})</text>')
    # iç kafes: köke uzaklık
    ie, ic = kafes(list(e), [1, 2, 3, 4, 5], derin_inc)
    irk = {}
    def irk_f(z):
        if z in irk: return irk[z]
        ups = [u for u, a3 in ic if a3 == z]
        irk[z] = 0 if not ups else 1 + max(irk_f(u) for u in ups)
        return irk[z]
    for z in ie: irk_f(z)
    ilv = collections.defaultdict(list)
    for z in ie: ilv[irk[z]].append(z)
    ip = {}
    nl = max(ilv) + 1 if ilv else 1
    for L2, lst2 in ilv.items():
        lst2.sort(key=lambda z: sorted(own_attr(z, [1, 2, 3, 4, 5], derin_inc, e)))
        for k, z in enumerate(lst2):
            ip[z] = (x + BW * (k + 1) / (len(lst2) + 1), y + 40 + L2 * ((BH - 70) / max(1, nl - 1) if nl > 1 else 0))
    for u, a3 in ic:
        b.append(f'<line x1="{ip[u][0]:.1f}" y1="{ip[u][1]:.1f}" x2="{ip[a3][0]:.1f}" y2="{ip[a3][1]:.1f}" stroke="#b9a96d" stroke-width="1.4"/>')
    for z, (px, py) in ip.items():
        I2 = own_attr(z, [1, 2, 3, 4, 5], derin_inc, e)
        sub = [o for o in z if derin_inc[o] == I2]
        b.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#2f6fb3"/>')
        b.append(f'<text x="{px+7:.1f}" y="{py-5:.1f}" font-size="9" fill="#7a6a3c">uzaklık {",".join(map(str, sorted(I2)))}</text>')
        if sub:
            b.append(f'<text x="{px:.1f}" y="{py+18:.1f}" text-anchor="middle" font-size="13" {AR}>{esc(" ".join(KEL[o]["ar"] for o in sub[:4]))}{"…" if len(sub) > 4 else ""}</text>')
svg(W, H, b, '4_ic_ice_cizgi')

# ---------- 5. Tablolu Euler diyagramı (Priss, yaklaşık) ----------
# sütunlar = bölgeler (aynı mana kümesini taşıyan kelimeler), sıra doğrusal diyagramın sırası; her mana bir dikdörtgen
zon = []
for w in SIRA:
    k = frozenset(uye[w])
    if zon and zon[-1][0] == k: zon[-1][1].append(w)
    else: zon.append((k, [w]))
ZW, LH, T = 92, 30, 110
W = 60 + ZW * len(zon) + 40
H = T + LH * len(SUT) + 230
b = baslik('Tablolu Euler diyagramı (yaklaşık): her mana bir dikdörtgen, her sütun bir bölge',
           'Bir sütundaki kelimeler aynı manaları taşır. Dikdörtgenlerin üst üste geldiği sütun, birden çok mananın ortak bölgesidir.')
for k, (s, ws) in enumerate(zon):
    x = 60 + k * ZW
    b.append(f'<rect x="{x}" y="{T}" width="{ZW}" height="{LH*len(SUT)}" fill="{"#f4efe0" if k % 2 == 0 else "#fffdf6"}"/>')
    for j, w in enumerate(ws):
        b.append(f'<text x="{x+ZW/2}" y="{T+LH*len(SUT)+26+j*24}" text-anchor="middle" font-size="16" {AR}>{esc(KEL[w]["ar"])}</text>')
for i, a in enumerate(SUT):
    y = T + i * LH
    k = 0
    while k < len(zon):
        if a in zon[k][0]:
            j = k
            while j + 1 < len(zon) and a in zon[j + 1][0]: j += 1
            x1 = 60 + k * ZW + 4; x2 = 60 + (j + 1) * ZW - 4
            b.append(f'<rect x="{x1}" y="{y+4}" width="{x2-x1}" height="{LH-8}" rx="7" fill="{RENK[DAL[a]]}" fill-opacity=".28" stroke="{RENK[DAL[a]]}" stroke-width="1.6"/>')
            b.append(f'<text x="{x1+6}" y="{y+20}" font-size="10.5" font-weight="700" fill="{RENK[DAL[a]]}">{esc(MN[a][:int((x2-x1)/6.2)])}</text>')
            k = j + 1
        else: k += 1
svg(W, H, b, '5_tablolu_euler')
print('tamam', len(EDGES), 'bağ;', len(dis_ext), 'dış kavram;', len(zon), 'bölge')
