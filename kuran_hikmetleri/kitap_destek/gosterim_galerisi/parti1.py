from ortak import *
import random
# 16 Treemap
def treemap():
    b = []
    def kut(i, x, y, w, h, yon, d):
        n = max(1, len(alt_say(i)))
        c = RENK[dal(i)] if i != 'E' else '#b8860b'
        b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{c}" fill-opacity="{0.10+0.10*d}" stroke="#fffdf6" stroke-width="2"/>')
        if w > 60 and h > 18: b.append(T(KISA[i], x + 5, y + 14, 10.5, 'start', '#1a1a1a', 'font-weight="700"'))
        kids = [k for k in KIDS.get(i, []) if MANA[k]['ebeveyn'][0] == i]
        own = len(WORDS_OF.get(i, []))
        top = sum(max(1, len(alt_say(k))) for k in kids) + own
        if not top: return
        pos = 0; pad = 18
        for k in kids:
            f = max(1, len(alt_say(k))) / top
            if yon: kut(k, x + pos * w + 2, y + pad, f * w - 4, h - pad - 3, not yon, d + 1)
            else: kut(k, x + 3, y + pad + pos * (h - pad), w - 6, f * (h - pad) - 3, not yon, d + 1)
            pos += f
        if own and w > 40:
            ws = ' '.join(KEL[x2]['ar'] for x2 in WORDS_OF[i][:4])
            if yon: b.append(AR(ws, x + pos * w + (1 - pos) * w / 2, y + h - 8, 13))
            else: b.append(AR(ws, x + w / 2, y + pad + pos * (h - pad) + (1 - pos) * (h - pad) / 2 + 5, 13))
    kut('E', 18, 64, 864, 560, True, 0)
    kaydet('16_treemap', '16. Treemap: alan = altındaki kelime sayısı', 'Her mana bir dikdörtgen, çocukları içinde. Renk dal, koyuluk köke uzaklık.', b)
# 17 Sunburst
def sunburst():
    b = []; cx, cy = 450, 350; R0 = 50; dr = 52
    def dil(i, a0, a1, d):
        r1, r2 = R0 + (d - 1) * dr, R0 + d * dr
        c = RENK[dal(i)]
        if d > 0:
            la = 1 if a1 - a0 > math.pi else 0
            p = [(cx + r1 * math.cos(a0), cy + r1 * math.sin(a0)), (cx + r2 * math.cos(a0), cy + r2 * math.sin(a0)), (cx + r2 * math.cos(a1), cy + r2 * math.sin(a1)), (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1))]
            b.append(f'<path d="M{p[0][0]:.1f},{p[0][1]:.1f} L{p[1][0]:.1f},{p[1][1]:.1f} A{r2},{r2} 0 {la} 1 {p[2][0]:.1f},{p[2][1]:.1f} L{p[3][0]:.1f},{p[3][1]:.1f} A{r1},{r1} 0 {la} 0 {p[0][0]:.1f},{p[0][1]:.1f}Z" fill="{c}" fill-opacity="{0.25+0.12*d}" stroke="#fffdf6" stroke-width="1.5"/>')
            am = (a0 + a1) / 2; rm = (r1 + r2) / 2
            if (a1 - a0) * rm > 30: b.append(T(KISA[i], cx + rm * math.cos(am), cy + rm * math.sin(am) + 4, 9.5))
        kids = [k for k in KIDS.get(i, []) if MANA[k]['ebeveyn'][0] == i]
        tot = sum(max(1, len(alt_say(k))) for k in kids) + len(WORDS_OF.get(i, [])) or 1
        a = a0
        for k in kids:
            f = max(1, len(alt_say(k))) / tot * (a1 - a0); dil(k, a, a + f, d + 1); a += f
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R0-4}" fill="#e8c766"/>'); b.append(T('ESAS', cx, cy + 4, 12, w='font-weight="700"'))
    dil('E', -math.pi / 2, 1.5 * math.pi, 0)
    kaydet('17_sunburst', '17. Sunburst: halka = köke uzaklık, açı = kelime sayısı', 'Merkezde esas; her halka bir türeme basamağı.', b, 900, 700)
# 18 UpSet
def upset():
    b = []; S = ['A', 'B', 'C', 'H', 'R2']; ad = {'A': 'ölçüp biçme/yaratma', 'B': 'düzleme', 'C': 'pay', 'H': 'yakışma', 'R2': 'kök dışı'}
    dl = {}
    for w, k in KEL.items():
        s = set()
        for m in k['anlam']:
            d = dal(m); s |= ({'A', 'B'} if d == 'AB' else {d})
        dl[w] = frozenset(s)
    grp = collections.Counter(dl.values())
    cols = sorted(grp.items(), key=lambda x: -x[1])
    x0, y0 = 260, 330
    for j, (s, n) in enumerate(cols):
        x = x0 + j * 70
        b.append(f'<rect x="{x-14}" y="{y0-n*12}" width="28" height="{n*12}" fill="#2b2410"/>'); b.append(T(str(n), x, y0 - n * 12 - 5, 11))
        ws = [KEL[w]['ar'] for w in dl if dl[w] == s][:3]
        for i2, a in enumerate(S):
            y = y0 + 30 + i2 * 30
            b.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{RENK[a] if a in s else "#ddd"}"/>')
        ys = [y0 + 30 + S.index(a) * 30 for a in s]
        if len(ys) > 1: b.append(f'<line x1="{x}" y1="{min(ys)}" x2="{x}" y2="{max(ys)}" stroke="#2b2410" stroke-width="3"/>')
        for k2, wv in enumerate(ws): b.append(AR(wv, x, y0 + 200 + k2 * 22, 13))
    for i2, a in enumerate(S): b.append(T(ad[a], x0 - 30, y0 + 34 + i2 * 30, 12, 'end', RENK[a], 'font-weight="700"'))
    kaydet('18_upset', '18. UpSet: dalların kesişimi sütun, büyüklüğü çubuk', 'Her sütun bir kesişim (dolu noktalar); altında o kesişimdeki kelimeler.', b)
# 19 Euler
def euler():
    b = []
    C = {'A': (360, 330, 200), 'B': (560, 330, 170), 'H': (650, 470, 95), 'C': (180, 540, 55), 'R2': (790, 140, 50)}
    for a, (x, y, r) in C.items():
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{RENK[a]}" fill-opacity=".12" stroke="{RENK[a]}" stroke-width="2"/>')
    b += [T('ölçüp biçme → yaratma', 250, 150, 12, fill=RENK['A'], w='font-weight="700"'), T('düzleme', 620, 175, 12, fill=RENK['B'], w='font-weight="700"'), T('yakışma', 690, 560, 12, fill=RENK['H'], w='font-weight="700"'), T('pay', 180, 600, 12, fill=RENK['C'], w='font-weight="700"'), T('kök dışı', 790, 205, 11, fill=RENK['R2'])]
    yer = collections.defaultdict(list)
    for w, k in KEL.items():
        s = set()
        for m in k['anlam']:
            d = dal(m); s |= ({'A', 'B'} if d == 'AB' else {d})
        yer[frozenset(s)].append(k['ar'])
    pos = {frozenset({'A'}): (330, 260), frozenset({'B'}): (620, 280), frozenset({'A', 'B'}): (460, 330), frozenset({'B', 'H'}): (640, 430), frozenset({'H'}): (690, 495), frozenset({'C'}): (180, 545), frozenset({'R2'}): (790, 145)}
    for s, ws in yer.items():
        x, y = pos.get(s, (450, 600))
        cols = 3 if len(ws) > 6 else 1
        for k2, wv in enumerate(ws): b.append(AR(wv, x + (k2 % cols - (cols - 1) / 2) * 70, y + (k2 // cols) * 20 - (len(ws) // cols) * 8, 13))
    kaydet('19_euler', '19. Euler çizgesi: her dal bir daire, kesişimde iki dala giren kelimeler', 'Ortadaki kesişim: hem ölçüp biçme hem düzleme dalından mana taşıyanlar.', b, 900, 660)
# 20 Sankey
def sankey():
    b = []
    cols = [['E'], ['A', 'B', 'C', 'H'], ['D', 'N', 'F', 'G'], ['J', 'K', 'L'], ['U'], ['X', 'Y', 'Z']]
    pos = {}; xs = [60, 210, 360, 510, 640, 770]
    for ci, col in enumerate(cols):
        tot = sum(max(1, len(alt_say(i))) for i in col); y = 70
        for i in col:
            h = max(1, len(alt_say(i))) / max(tot, 1) * (520 if ci else 520)
            h = max(1, len(alt_say(i))) * 13
            pos[i] = (xs[ci], y, h); y += h + 14
    for i, (x, y, h) in pos.items():
        b.append(f'<rect x="{x}" y="{y}" width="16" height="{h}" fill="{RENK[dal(i)] if i!="E" else "#b8860b"}"/>')
        b.append(T(KISA[i] + f' ({len(alt_say(i))})', x + 20, y + h / 2 + 4, 10.5, 'start'))
    off = collections.defaultdict(float)
    for i, (x, y, h) in pos.items():
        for p in MANA[i]['ebeveyn']:
            if p not in pos: continue
            px, py, ph = pos[p]; w = max(1, len(alt_say(i))) * 13 / len(MANA[i]['ebeveyn'])
            y1 = py + off[p]; off[p] += w
            b.append(f'<path d="M{px+16},{y1} C{(px+x)/2},{y1} {(px+x)/2},{y} {x},{y} L{x},{y+w} C{(px+x)/2},{y+w} {(px+x)/2},{y1+w} {px+16},{y1+w} Z" fill="{RENK[dal(i)]}" fill-opacity=".3"/>')
    kaydet('20_sankey', '20. Sankey: esastan manalara akış, genişlik = kelime sayısı', 'Soldan sağa türeme basamakları; şerit kalınlığı o koldaki kelime sayısı.', b, 900, 680)
# 21 Arc
def arc():
    b = []; seq = ORDER; x = {i: 50 + k * 50 for k, i in enumerate(seq)}; y0 = 360
    for i in seq:
        b.append(f'<circle cx="{x[i]}" cy="{y0}" r="7" fill="{RENK[dal(i)] if i!="E" else "#b8860b"}"/>')
        b.append(f'<text transform="translate({x[i]+4},{y0+16}) rotate(55)" font-size="11" fill="#2b2410">{esc(KISA[i])}</text>')
    for i in seq:
        for p in MANA[i]['ebeveyn']:
            a, c = sorted([x[p], x[i]]); r = (c - a) / 2
            b.append(f'<path d="M{a},{y0} A{r},{r} 0 0 1 {c},{y0}" fill="none" stroke="{RENK[dal(i)]}" stroke-width="2"/>')
    for w, k in KEL.items():
        ms = list(k['anlam'])
        for m1 in range(len(ms)):
            for m2 in range(m1 + 1, len(ms)):
                a, c = sorted([x[ms[m1]], x[ms[m2]]]); r = (c - a) / 2
                b.append(f'<path d="M{a},{y0} A{r},{r} 0 0 0 {c},{y0}" fill="none" stroke="#c0392b" stroke-width="1.6" stroke-dasharray="4 3"/>')
                b.append(AR(k['ar'], (a + c) / 2, y0 + r + 16, 12, fill='#c0392b'))
    kaydet('21_arc', '21. Yay diyagramı: üstte türeme, altta ortak kelime', 'Manalar bir hatta; üst yay = "şundan türedi", alt kesikli yay = iki manayı taşıyan kelime.', b, 900, 640)
# 22 Force
def force():
    random.seed(3)
    N = list(MANA) + list(KEL); E = []
    for i in MANA:
        for p in MANA[i]['ebeveyn']: E.append((p, i))
    for w, k in KEL.items():
        for m in k['anlam']: E.append((m, w))
    P = {n: [450 + 300 * math.cos(k * 2.399), 350 + 250 * math.sin(k * 2.399)] for k, n in enumerate(N)}
    for it in range(400):
        F = {n: [0, 0] for n in N}
        for a in N:
            for c in N:
                if a == c: continue
                dx = P[a][0] - P[c][0]; dy = P[a][1] - P[c][1]; d2 = dx * dx + dy * dy + 0.01
                F[a][0] += 260 * dx / d2; F[a][1] += 260 * dy / d2
        for a, c in E:
            dx = P[c][0] - P[a][0]; dy = P[c][1] - P[a][1]; d = math.hypot(dx, dy) + .01
            f = (d - 45) * 0.05; F[a][0] += f * dx / d; F[a][1] += f * dy / d; F[c][0] -= f * dx / d; F[c][1] -= f * dy / d
        for n in N:
            P[n][0] = min(870, max(30, P[n][0] + max(-8, min(8, F[n][0])))); P[n][1] = min(620, max(70, P[n][1] + max(-8, min(8, F[n][1]))))
    b = []
    for a, c in E: b.append(f'<line x1="{P[a][0]:.1f}" y1="{P[a][1]:.1f}" x2="{P[c][0]:.1f}" y2="{P[c][1]:.1f}" stroke="#bbb"/>')
    for n in N:
        if n in MANA: b += [f'<circle cx="{P[n][0]:.1f}" cy="{P[n][1]:.1f}" r="8" fill="{RENK[dal(n)] if n!="E" else "#b8860b"}"/>', T(KISA[n], P[n][0], P[n][1] - 11, 10, w='font-weight="700"')]
        else: b.append(AR(KEL[n]['ar'], P[n][0], P[n][1] + 5, 12, fill='#444'))
    kaydet('22_kuvvet', '22. Kuvvet yönlü çizge: bağlı olan yakına çekilir', 'Manalar renkli nokta, kelimeler Arapça; yerleşim fizik benzetmesiyle bulunur (kural yok).', b, 900, 640)
# 23 Kavram haritası
def kavram_haritasi():
    b = []; lev = collections.defaultdict(list)
    for i in ORDER: lev[depth(i)].append(i)
    P = {}
    for d, lst in lev.items():
        for k, i in enumerate(lst): P[i] = (60 + (k + .5) * 780 / len(lst), 90 + d * 105)
    for i in ORDER:
        for p in MANA[i]['ebeveyn']:
            x1, y1 = P[p]; x2, y2 = P[i]
            b.append(f'<line x1="{x1}" y1="{y1+12}" x2="{x2}" y2="{y2-12}" stroke="#8d7f4f" stroke-width="1.4" marker-end="url(#o)"/>')
            s = MANA[i].get('sebep', '').replace('çünkü ', '')
            s = ' '.join(s.split()[:4]) + ('…' if len(s.split()) > 4 else '')
            b.append(T(s, (x1 + x2) / 2, (y1 + y2) / 2, 8.5, fill='#b3541e'))
    for i, (x, y) in P.items():
        b.append(f'<rect x="{x-58}" y="{y-12}" width="116" height="24" rx="12" fill="#fffdf6" stroke="{RENK[dal(i)] if i!="E" else "#b8860b"}" stroke-width="2"/>')
        b.append(T(KISA[i], x, y + 4, 10.5, w='font-weight="700"'))
    b.insert(0, '<defs><marker id="o" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0L8,4L0,8z" fill="#8d7f4f"/></marker></defs>')
    kaydet('23_kavram_haritasi', '23. Kavram haritası: oklar üzerinde bağlayıcı cümle (sebep)', 'Novak tarzı: kavram – bağlayıcı – kavram önermeleri.', b, 900, 680)
# 24 Poincaré diski
def poincare():
    b = []; cx, cy, R = 450, 360, 290
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#f4efe0" stroke="#8d7f4f"/>')
    ang = {}
    def yer(i, a0, a1):
        ang[i] = (a0 + a1) / 2
        kids = [k for k in KIDS.get(i, []) if MANA[k]['ebeveyn'][0] == i]
        for k2, c in enumerate(kids): yer(c, a0 + (a1 - a0) * k2 / len(kids), a0 + (a1 - a0) * (k2 + 1) / len(kids))
    yer('E', 0, 2 * math.pi)
    NN = [i for i in MANA if i in ang]
    def p(i):
        r = R * math.tanh(depth(i) * 0.55); return cx + r * math.cos(ang[i]), cy + r * math.sin(ang[i])
    for i in NN:
        for q in MANA[i]['ebeveyn']:
            x1, y1 = p(q); x2, y2 = p(i); b.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{RENK[dal(i)]}" stroke-width="1.6"/>')
    for i in NN:
        x, y = p(i); s = 1 - math.tanh(depth(i) * 0.55) ** 2
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3+7*s:.1f}" fill="{RENK[dal(i)] if i!="E" else "#b8860b"}"/>')
        b.append(T(KISA[i], x, y - 8, 8 + 4 * s))
    kaydet('24_poincare', '24. Hiperbolik disk: umumî merkezde, hususî kenara sıkışır', 'Köke uzaklık arttıkça yazı küçülür ve kenara yaklaşır; ağacın tamamı tek diske sığar.', b, 900, 680)
# 25 Leibniz
def leibniz():
    b = []; pr = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
    seq = [i for i in ORDER if i != 'E']; P = dict(zip(seq, pr))
    def kod(i):
        v = P[i]
        for q in MANA[i]['ebeveyn']:
            if q != 'E': v *= kod(q)
        return v
    b.append(T('Basit mana = asal sayı; türeyen mana = atalarının asallarının çarpımı', 18, 80, 12, 'start'))
    for k, i in enumerate(seq):
        y = 105 + k * 22
        b += [T(f'{KISA[i]}', 30, y, 11.5, 'start', RENK[dal(i)], 'font-weight="700"'), T(f'asal {P[i]}', 200, y, 11, 'start'), T(f'kod = {kod(i)}', 290, y, 11, 'start', '#2b2410', 'font-family="DejaVu Sans Mono"')]
    x0 = 520
    b.append(T('Kelimelerin kodu (manalarının kodlarının e.k.o.k.\'u):', x0, 105, 11.5, 'start', '#2b2410', 'font-weight="700"'))
    def ekok(a, c): return a * c // math.gcd(a, c)
    for k, (w, kk) in enumerate(list(KEL.items())[:18]):
        v = 1
        for m in kk['anlam']: v = ekok(v, kod(m))
        b += [AR(kk['ar'], x0 + 40, 132 + k * 22, 14), T(str(v), x0 + 80, 132 + k * 22, 10.5, 'start', '#2b2410', 'font-family="DejaVu Sans Mono"')]
    b.append(T('Sınama: "ahlâk huydur" mu? kod(ahlâk) ÷ kod(huy) tam bölünürse evet: ' + f'{kod("X")} ÷ {kod("U")} = {kod("X")//kod("U")}', 18, 600, 12, 'start', '#b3541e', 'font-weight="700"'))
    kaydet('25_leibniz', '25. Leibniz asal kodu: mana sayıdır, türeme çarpmadır', 'Bir mana ötekinden türemiş mi? Kodu bölünüyorsa türemiştir.', b, 900, 640)
# 26 Wilkins
def wilkins():
    b = []; harf = {'A': 'ka', 'B': 'du', 'C': 'pe', 'H': 'li', 'R2': 'xo'}
    seq = [i for i in ORDER if i not in ('E',)]
    def kod(i):
        if i == 'R2': return 'xo'
        p = [q for q in MANA[i]['ebeveyn'] if q != 'E']
        if not p: return harf[i]
        sib = [c for c in KIDS[p[0]]]
        return kod(p[0]) + 'bcdfgmnrst'[sib.index(i)]
    b.append(T('Kelimenin harfleri tasnif yolunu taşır: ilk hece dal, her sonraki harf bir basamak', 18, 80, 12, 'start'))
    for k, i in enumerate(seq):
        y = 108 + k * 30
        b += [T(kod(i), 40, y, 18, 'start', RENK[dal(i)], 'font-weight="700" font-family="DejaVu Sans Mono"'), T('= ' + KISA[i], 200, y, 12, 'start')]
        ws = ' '.join(KEL[w]['ar'] for w in WORDS_OF.get(i, [])[:4]); b.append(AR(ws, 600, y, 14))
    b.append(T(f'Okuma: "{kod("X")}" = ka (ölçüp biçme) → b (yaratmak) → c (yaradılış) → b (huy) → b (ahlâk)', 18, 620, 12, 'start', '#b3541e', 'font-weight="700"'))
    kaydet('26_wilkins', '26. Wilkins tarzı harf kodu (1668): adı okuyan yerini okur', 'Her mananın adı, ağaçtaki yolunun harflerinden yapılır.', b, 900, 650)
# 27 Lull çarkı
def lull():
    b = []; cx, cy = 450, 355
    halkalar = [(90, ['ölçmek', 'düzlemek', 'ayırmak', 'yakıştırmak'], '#b8860b'),
                (170, ['netice', 'hâl', 'nesne', 'vasıta', 'zaman', 'içe geçiş', 'düzen', 'taşma', 'taklit', 'tekellüf'], '#2f6fb3'),
                (250, ['fâil', 'mef‘ûl', 'masdar', 'mübalağa', 'sıfat', 'çoğul', 'tafdîl', 'mensûb'], '#3f8f3a')]
    for r, el, c in halkalar:
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-width="2"/>')
        for k, t in enumerate(el):
            a = -math.pi / 2 + 2 * math.pi * k / len(el)
            b.append(T(t, cx + (r - 30) * math.cos(a), cy + (r - 30) * math.sin(a) + 4, 10.5, fill=c, w='font-weight="700"'))
    b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-260}" stroke="#c0392b" stroke-width="3"/>')
    b.append(T('Kırmızı hattın üstünde okunan: ölçmek + netice + fâil = yaratan (خَالِق)', 450, 640, 13, fill='#c0392b', w='font-weight="700"'))
    kaydet('27_lull', '27. Lull çarkı: üç dönen halka, her dönüş yeni bir türev', 'İç halka esasın yönleri, orta halka türeme işlemleri, dış halka vezinler.', b, 900, 660)
for f in (treemap, sunburst, upset, euler, sankey, arc, force, kavram_haritasi, poincare, leibniz, wilkins, lull): f()
print('tamam')
