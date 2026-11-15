from ortak import *
from parti2 import DEF, kutu, ok, DALAD
MN = [m for m in ORDER if m != 'E']
WS = list(KEL)
def kel(m): return [KEL[w]['ar'] for w in WORDS_OF.get(m, [])]
def chain(m):
    z = [m]
    while MANA[z[-1]]['ebeveyn']: z.append(MANA[z[-1]]['ebeveyn'][0])
    return list(reversed(z))
def tablo(b, x, y, cols, rows, cw, rh=24, bas_renk='#2b2410', ar_cols=()):
    xx = x
    for j, c in enumerate(cols):
        b.append(f'<rect x="{xx}" y="{y}" width="{cw[j]}" height="{rh}" fill="{bas_renk}"/>'); b.append(T(c, xx + 5, y + 16, 10.5, 'start', '#fff', 'font-weight="700"')); xx += cw[j]
    for i, r in enumerate(rows):
        xx = x; yy = y + rh * (i + 1)
        for j, v in enumerate(r):
            b.append(f'<rect x="{xx}" y="{yy}" width="{cw[j]}" height="{rh}" fill="{"#fbf6e6" if i%2 else "#fff"}" stroke="#e2d9bd"/>')
            b.append(AR(v, xx + cw[j] - 5, yy + 17, 13, 'end') if j in ar_cols else T(v, xx + 5, yy + 16, 10, 'start')); xx += cw[j]
# 41 Talmy
def talmy():
    b = [DEF]
    S = [('madde (agonist)', 'ölçen el (antagonist)', 'güçlü', 'madde kendi hâlinde kalmaya meyleder; el ölçüp biçer, şekil verir', 'ölçüp biçmek / yaratmak'),
         ('elbise (agonist)', 'zaman ve sürtünme', 'güçlü', 'elbise dayanmaya meyleder; sürtünme galip gelir, yüzü düzleşir', 'eskimek'),
         ('nefis (agonist)', 'yaradılıştaki hâl', 'güçlü', 'yaradılış iç hâli nefse yerleştirir, sabit kılar', 'huy'),
         ('huy (agonist)', 'öfke sebebi', 'zayıf', 'huy dengeye meyleder; sebep galip gelince taşar', 'öfke'),
         ('kişi (agonist)', 'başkasının huyu', 'kişi', 'kişi kendi huyunu bırakıp başkasınınkini kendi gücüyle giyer', 'huy takınmak'),
         ('söz (agonist)', 'uyduran', 'güçlü', 'aslı olmayan söz yokluğa meyleder; uyduran onu var gösterir', 'uydurmak')]
    for k, (ag, an, g, ac, m) in enumerate(S):
        x = 30 + (k % 3) * 290; y = 90 + (k // 3) * 260
        b.append(f'<circle cx="{x+70}" cy="{y+70}" r="38" fill="#e8c766" stroke="#2b2410" stroke-width="1.5"/>'); b.append(T('●' if g != 'zayıf' else '', x + 70, y + 75, 14))
        b.append(f'<path d="M{x+200},{y+32} A40,40 0 1,0 {x+200},{y+108} A26,40 0 1,1 {x+200},{y+32}Z" fill="#9db8d9" stroke="#2b2410" stroke-width="1.5"/>'); b.append(T('+' if g == 'güçlü' else '−', x + 192, y + 76, 16, w='font-weight="700"'))
        b.append(f'<line x1="{x+165}" y1="{y+70}" x2="{x+115}" y2="{y+70}" stroke="#b3541e" stroke-width="3" marker-end="url(#o)"/>')
        b.append(T(ag, x + 70, y + 130, 10)); b.append(T(an, x + 200, y + 130, 10))
        for j, s in enumerate([ac[i:i + 46] for i in range(0, len(ac), 46)]): b.append(T(s, x + 130, y + 152 + j * 14, 9.5, fill='#6d6650'))
        b.append(T('netice: ' + m, x + 130, y + 200, 11, fill=RENK[dal([q for q in MANA if KISA[q] == m.split(' /')[0]][0])], w='font-weight="700"'))
    b.append(T('Daire = agonist (kendi meylinde duran), yarım ay = antagonist (ona kuvvet veren); + daha güçlü olan, ok kuvvetin yönü.', 450, 620, 10.5))
    kaydet('41_talmy', '41. Kuvvet dinamiği (Talmy): her mana bir kuvvet çekişmesinin neticesi', 'Meyiller ve galibiyet bu levha için yorumlandı.', b)
# 42 Langacker
def langacker():
    b = []; sec = ['A', 'D', 'J', 'K', 'U', 'L']
    for k, m in enumerate(sec):
        x = 25 + (k % 3) * 290; y = 80 + (k // 3) * 270; ch = chain('X') if m != 'L' else chain('L')
        b.append(f'<rect x="{x}" y="{y}" width="270" height="240" rx="10" fill="#f3eedd" stroke="#c9bd94"/>'); b.append(T('zemin (base): ölçüp biçme olayı', x + 135, y + 18, 10, fill='#6d6650'))
        for j, q in enumerate(ch):
            xx = x + 30 + j * (220 / max(1, len(ch) - 1)); yy = y + 120
            on = q == m
            b.append(f'<circle cx="{xx:.1f}" cy="{yy}" r="{14 if on else 8}" fill="{RENK[dal(q)] if on else "#fff"}" stroke="#2b2410" stroke-width="{3 if on else 1}"/>')
            b.append(T(KISA[q], xx, yy + (34 if j % 2 else -24), 9.5, w='font-weight="700"' if on else ''))
            if j: b.append(f'<line x1="{xx-220/(len(ch)-1)+9:.1f}" y1="{yy}" x2="{xx-9:.1f}" y2="{yy}" stroke="#999"/>')
        b.append(AR(' · '.join(kel(m)[:3]), x + 135, y + 205, 14)); b.append(T('profil: ' + KISA[m], x + 135, y + 228, 11, fill=RENK[dal(m)], w='font-weight="700"'))
    kaydet('42_langacker', '42. Profil ve zemin (Langacker): aynı olay, başka yeri aydınlatılmış', 'Bütün kelimeler aynı zemini çağırır; her biri zincirin bir halkasını kalın çizer.', b, 900, 640)
# 43 Voronoi
def voronoi():
    from scipy.spatial import Voronoi
    import numpy as np
    b = []; P = {}
    top = KIDS['E']; cx, cy = 450, 360
    def yer(m, a0, a1, r):
        a = (a0 + a1) / 2; P[m] = (cx + r * math.cos(a), cy + r * 0.8 * math.sin(a))
        ch = [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m]
        for k, c in enumerate(ch): yer(c, a0 + (a1 - a0) * k / len(ch), a0 + (a1 - a0) * (k + 1) / len(ch), r + 70)
    wt = [1 + len(alt_say(m)) for m in top]; t = sum(wt); a = 0
    for m, w in zip(top, wt): yer(m, a, a + 2 * math.pi * w / t, 70); a += 2 * math.pi * w / t
    P['E'] = (cx, cy); P['R2'] = (840, 620)
    ks = list(P); pts = np.array([P[k] for k in ks] + [(-2000, -2000), (3000, -2000), (-2000, 3000), (3000, 3000)])
    V = Voronoi(pts)
    b.append('<clipPath id="c"><rect x="10" y="60" width="880" height="600"/></clipPath><g clip-path="url(#c)">')
    for i, k in enumerate(ks):
        reg = V.regions[V.point_region[i]]
        if -1 in reg or not reg: continue
        d = ' '.join(f'{V.vertices[v][0]:.1f},{V.vertices[v][1]:.1f}' for v in reg)
        b.append(f'<polygon points="{d}" fill="{RENK[dal(k)]}" fill-opacity="{0.12+0.07*depth(k) if k!="R2" else .15}" stroke="#fffdf6" stroke-width="2"/>')
    b.append('</g>')
    for k, (x, y) in P.items():
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#2b2410"/>'); b.append(T(KISA[k], x, y - 6, 10, w='font-weight="700"')); b.append(AR(' '.join(kel(k)[:2]), x, y + 14, 12))
    kaydet('43_voronoi', '43. Kavram uzayı (Gärdenfors): her mana kendisine en yakın noktaların bölgesi', 'Komşu bölge = komşu mana; bölgeler arasında boşluk yoktur. Noktaların yeri türeme ağacından.', b, 900, 680)
# 44 Kutu gömmesi
def kutugom():
    b = []
    def kut(m, x, y, w, h, d=0):
        b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="{RENK[dal(m)]}" fill-opacity=".10" stroke="{RENK[dal(m)]}" stroke-width="1.6"/>')
        b.append(T(KISA[m], x + 6, y + 14, 10, 'start', RENK[dal(m)], 'font-weight="700"'))
        ch = [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m and c != 'N']
        if not ch: b.append(AR(' '.join(kel(m)[:3]), x + w / 2, y + h - 8, 12)); return
        n = len(ch); gap = 6
        for k, c in enumerate(ch):
            if d % 2 == 0: kut(c, x + gap + k * (w - gap) / n, y + 22, (w - gap) / n - gap, h - 28, d + 1)
            else: kut(c, x + gap, y + 22 + k * (h - 26) / n, w - 2 * gap, (h - 26) / n - 4, d + 1)
    b.append(f'<rect x="20" y="66" width="860" height="560" rx="8" fill="#e8c766" fill-opacity=".15" stroke="#b8860b" stroke-width="2"/>'); b.append(T('esas', 28, 82, 11, 'start', '#b8860b', 'font-weight="700"'))
    kut('A', 30, 90, 470, 520); kut('B', 520, 90, 170, 300); kut('C', 700, 90, 80, 160); kut('H', 790, 90, 80, 160); kut('R2', 700, 520, 170, 90)
    b.append(f'<rect x="440" y="350" width="130" height="80" rx="6" fill="#2c8c7c" fill-opacity=".25" stroke="#2c8c7c" stroke-width="2" stroke-dasharray="5 3"/>'); b.append(T('şekli belirmiş', 505, 385, 10.5, w='font-weight="700"')); b.append(AR('مُخَلَّق', 505, 412, 13))
    b.append(T('Kesik çizgili kutu iki kutunun kesişimindedir: hem ölçülüp biçilmiş hem düzlenmiş. Kök dışı kutu esasın dışına taşar.', 450, 645, 10.5))
    kaydet('44_kutu_gommesi', '44. Kutu gömmesi: her mana bir kutu, çocuk kutu ebeveyninin içinde', 'İçinde olmak = ondan türemek; kesişim = iki asla birden bağlı olmak.', b, 900, 660)
# 45 Mapper
def mapper():
    b = []; cl = collections.defaultdict(list)
    for w in WS:
        for m in KEL[w]['anlam']: cl[(dal(m) if dal(m) != 'AB' else 'AB', min(depth(m), 4))].append(w)
    P = {}; ds = ['A', 'AB', 'B', 'C', 'H', 'R2']
    for (d, l) in cl: P[(d, l)] = (110 + l * 170, 90 + ds.index(d) * 95)
    ks = list(cl)
    for i, a in enumerate(ks):
        for c in ks[i + 1:]:
            o = len(set(cl[a]) & set(cl[c]))
            if o: b.append(f'<line x1="{P[a][0]}" y1="{P[a][1]}" x2="{P[c][0]}" y2="{P[c][1]}" stroke="#555" stroke-width="{1+2*o}" stroke-opacity=".5"/>')
    for k in ks:
        x, y = P[k]; r = 8 + 3 * len(set(cl[k]))
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{RENK[k[0]]}" fill-opacity=".7"/>'); b.append(T(str(len(set(cl[k]))), x, y + 4, 10, fill='#fff', w='font-weight="700"'))
    for l in range(5): b.append(T(f'{l}. basamak', 110 + l * 170, 640, 10.5))
    for i, d in enumerate(ds): b.append(T(DALAD[d], 20, 94 + i * 95, 10, 'start'))
    kaydet('45_mapper', '45. Mapper çizgesi: kelimeler (dal, basamak) dilimlerine kümelenir', 'Daire = küme, sayı = kelime adedi; çizgi iki kümenin ortak kelimesi, kalınlık ortaklık sayısı.', b, 900, 660)
# 46 AMR
def amr():
    b = [DEF]
    N = {'y': (450, 110, 'yaratmak-01'), 'a': (200, 260, 'Allah'), 'i': (450, 260, 'insan'), 'h': (700, 260, 'hazırlamak-01'), 'ö': (620, 410, 'ölçmek-01'), 'ş': (800, 410, 'şekil'), 'n': (450, 410, 'nutfe')}
    E2 = [('y', 'a', ':ARG0'), ('y', 'i', ':ARG1'), ('y', 'h', ':manner'), ('h', 'ö', ':ARG1-of'), ('h', 'ş', ':ARG2'), ('y', 'n', ':source')]
    for s, t, l in E2:
        x1, y1, _ = N[s]; x2, y2, _ = N[t]; b.append(f'<line x1="{x1}" y1="{y1+16}" x2="{x2}" y2="{y2-18}" stroke="#2b2410" stroke-width="1.5" marker-end="url(#o)"/>'); b.append(T(l, (x1 + x2) / 2 + 8, (y1 + y2) / 2, 10.5, 'start', '#b3541e'))
    for k, (x, y, t) in N.items():
        b.append(f'<rect x="{x-70}" y="{y-16}" width="140" height="32" rx="16" fill="#fff" stroke="#2b2410"/>'); b.append(T(f'{k} / {t}', x, y + 4, 11, w='font-weight="700"'))
    pen = ['(y / yaratmak-01', '   :ARG0 (a / Allah)', '   :ARG1 (i / insan)', '   :source (n / nutfe)', '   :manner (h / hazırlamak-01', '      :ARG1-of (ö / ölçmek-01)', '      :ARG2 (ş / şekil)))']
    for k, s in enumerate(pen): b.append(f'<text x="40" y="{490+k*17}" font-family="DejaVu Sans Mono, monospace" font-size="12" fill="#2b2410" xml:space="preserve">{esc(s)}</text>')
    b.append(AR('خَلَقَ الإِنسَانَ مِن نُّطْفَةٍ (Nahl 16:4)', 860, 520, 18, 'end')); b.append(T('Cümle mana çizgesine dökülür; "ölçüp biçerek" yaratmanın tarzı olarak kenarla girer.', 860, 550, 10.5, 'end'))
    kaydet('46_amr', '46. AMR (soyut mana gösterimi): cümlenin manası düğüm ve rol kenarları', 'Alt kısım aynı çizgenin PENMAN yazısıdır. Rol adları bu levha için seçildi.', b, 900, 640)
# 47 FrameNet
def framenet():
    b = [DEF]
    kutu(b, 300, 70, 300, 70, 'ÜST ÇERÇEVE: Hazırlama', ['bir şeyi bir maksada uygun hâle getirmek'], '#b8860b')
    fr = [('Yaratma', ['Yaratan', 'Yaratılan', 'Madde', 'Tarz (ölçüyle)'], 'D', ['خَلَقَ', 'خَالِق', 'خَلْق', 'تَخْلِيق']),
          ('Düzleme / Aşınma', ['Fâil', 'Yüzey', 'Sebep (zaman)'], 'B', ['خَلِقَ', 'أَخْلَقَ', 'خَلَق']),
          ('Mizaç', ['Sahip', 'Hâl', 'Derece'], 'U', ['خُلُق', 'خَلِيقَة', 'أَخْلَاق']),
          ('Uydurma', ['Uyduran', 'Söz', 'Muhatap'], 'L', ['اِخْتَلَقَ', 'اِخْتِلَاق', 'مُخْتَلَق'])]
    for k, (ad, fe, m, lu) in enumerate(fr):
        x = 20 + k * 220; y = 220; c = RENK[dal(m)]
        b.append(f'<rect x="{x}" y="{y}" width="205" height="330" rx="6" fill="#fff" stroke="{c}" stroke-width="2"/>'); b.append(T('ÇERÇEVE: ' + ad, x + 8, y + 20, 11, 'start', c, 'font-weight="700"'))
        b.append(T('Çerçeve unsurları', x + 8, y + 46, 10, 'start', '#6d6650'))
        for j, f in enumerate(fe): b.append(f'<rect x="{x+8}" y="{y+54+j*26}" width="189" height="21" rx="10" fill="{c}" fill-opacity=".15"/>'); b.append(T(f, x + 16, y + 69 + j * 26, 10.5, 'start'))
        b.append(T('Sözlük birimleri', x + 8, y + 196, 10, 'start', '#6d6650'))
        for j, l in enumerate(lu): b.append(AR(l, x + 195, y + 222 + j * 24, 15, 'end'))
        ok(b, x + 102, y, 450, 142)
    b.append(T('Ok: "çerçeve mirası" (alt çerçeve üst çerçeveden unsur alır).', 450, 600, 10.5))
    kaydet('47_framenet', '47. FrameNet: her mana bir olay çerçevesi, unsurları ve onu çağıran kelimeler', 'Çerçeve ve unsur adları bu levha için kuruldu.', b)
# 48 Mel'čuk
def melcuk():
    b = []
    R = [('S0 (fiilin ismi)', 'خَلْق', 'yaratma'), ('S1 (birinci rol: fâil)', 'خَالِق', 'yaratan'), ('S2 (ikinci rol: mef‘ûl)', 'مَخْلُوق', 'yaratılmış'), ('Sres (netice)', 'خِلْقَة', 'yaradılış'),
         ('Magn (şiddet)', 'خَلَّاق', 'çok yaratan'), ('Sing (tek birim)', 'خَلِيقَة', 'bir mahlûk'), ('Mult (topluluk)', 'مَخْلُوقَات', 'mahlûkat'), ('A0 (sıfat)', 'خِلْقِيّ', 'yaradılıştan'),
         ('Caus·Fact (yaptırmak)', 'تَخْلِيق', 'birleştirip yapma'), ('Perm·Fict (sahte yapmak)', 'اِخْتَلَقَ', 'uydurdu'), ('Able2 (yapılmaya elverişli)', 'خَلِيق', 'lâyık'), ('Degrad (bozulmak)', 'خَلِقَ', 'eskidi')]
    tablo(b, 60, 80, ['sözlük fonksiyonu', 'değeri', 'Türkçesi'], [list(r) for r in R], [300, 220, 260], 34, ar_cols=(1,))
    b.append(T('f(خلق) = değer. Fonksiyon adı bütün dillerde aynıdır; değer her kelimede başkadır.', 450, 610, 11))
    kaydet('48_melcuk', "48. Mel'čuk sözlük fonksiyonları: kökten türeyenler evrensel fonksiyonların değeri", 'Eşleşmeler bu levha için tayin edildi; fonksiyon adları Anlam-Metin nazariyesindendir.', b, 900, 640)
# 49 Kuale
def kuale():
    b = []; cx, cy = 450, 350
    b.append(AR('خَلْق', cx, cy + 8, 30)); b.append(f'<circle cx="{cx}" cy="{cy}" r="60" fill="none" stroke="#b8860b" stroke-width="2"/>')
    Q = [('SURÎ (formal): nedir?', ['ölçülüp biçilmiş, şekli belirmiş bir varlık', 'مَخْلُوق · خِلْقَة'], -1, -1), ('MADDÎ (constitutive): neden yapılmış?', ['ham madde: deri, toprak, nutfe', 'düzlenmiş yüzey: خَلْقَاء'], 1, -1),
         ('GAÎ (telic): ne için?', ['bir işe yakışmak, lâyık olmak', 'خَلِيق · أَخْلَق'], -1, 1), ('FÂİLÎ (agentive): nasıl meydana geldi?', ['ölçüp biçen bir yapanın fiiliyle', 'خَالِق · خَلَّاق'], 1, 1)]
    for t, ls, sx, sy in Q:
        x = cx + sx * 220 - 160; y = cy + sy * 170 - 50
        b.append(f'<rect x="{x}" y="{y}" width="320" height="100" rx="8" fill="#fff" stroke="#2b2410"/>'); b.append(f'<line x1="{cx+sx*45}" y1="{cy+sy*40}" x2="{x+160-sx*120}" y2="{y+50-sy*50}" stroke="#999"/>')
        b.append(T(t, x + 160, y + 22, 11.5, w='font-weight="700"')); b.append(T(ls[0], x + 160, y + 50, 10.5)); b.append(AR(ls[1], x + 160, y + 80, 15))
    b.append(T('Pustejovsky\'nin dört kualesi Aristo\'nun dört illetidir: surî, maddî, gaî, fâilî.', 450, 630, 11))
    kaydet('49_kuale', '49. Dört illet (kuale yapısı): bir kelimenin dört yüzü', 'Her köşe bir illet ve onu taşıyan kelimeler.', b, 900, 650)
# 50 Sparkline
def spark():
    b = []; y = 80
    for m in MN:
        ch = chain(m) if m != 'R2' else ['R2']; v = [len(WORDS_OF.get(q, [])) for q in ch]
        b.append(T(KISA[m], 160, y + 5, 11, 'end'))
        pts = ' '.join(f'{180+k*30},{y+8-4*vv}' for k, vv in enumerate(v)); b.append(f'<polyline points="{pts}" fill="none" stroke="{RENK[dal(m)]}" stroke-width="1.8"/>')
        b.append(f'<circle cx="{180+(len(v)-1)*30}" cy="{y+8-4*v[-1]}" r="3" fill="#b3541e"/>'); b.append(T(str(v[-1]), 195 + (len(v) - 1) * 30, y + 6, 10, 'start', '#b3541e'))
        b.append(T(' → '.join(KISA[q] for q in ch), 400, y + 5, 9.5, 'start', '#6d6650')); y += 34
    kaydet('50_sparkline', '50. Kıvılcım çizgisi: esastan bu manaya giden yolda her basamağın kelime adedi', 'Kırmızı nokta = bu mananın kendi kelime sayısı. Satır içine sığan küçük grafik.', b, 900, y + 20)
# 51 Chernoff
def chernoff():
    b = []
    for k, m in enumerate(ORDER):
        x = 80 + (k % 6) * 145; y = 130 + (k // 6) * 190; c = RENK[dal(m)]
        nw = len(WORDS_OF.get(m, [])); nk = len(KIDS.get(m, [])); d = depth(m)
        rx = 34 + 4 * nk; ry = 44
        b.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" fill-opacity=".2" stroke="{c}" stroke-width="2"/>')
        er = 3 + 1.2 * nw
        for s in (-1, 1): b.append(f'<circle cx="{x+s*14}" cy="{y-10}" r="{er}" fill="#fff" stroke="#2b2410"/><circle cx="{x+s*14}" cy="{y-10}" r="2" fill="#2b2410"/>')
        cv = 14 - 6 * d; b.append(f'<path d="M{x-16},{y+18} Q{x},{y+18+cv} {x+16},{y+18}" stroke="#2b2410" fill="none" stroke-width="2"/>')
        if any(KEL[w]['kuran'] for w in WORDS_OF.get(m, [])): b.append(f'<path d="M{x-14},{y-32} L{x-4},{y-28} M{x+4},{y-28} L{x+14},{y-32}" stroke="#2b2410" stroke-width="2"/>')
        b.append(T(KISA[m], x, y + 64, 10.5))
    b.append(T('Yüz genişliği = çocuk mana sayısı · göz = kelime sayısı · ağız: gülen köke yakın, asık kökten uzak · kaş = Kur\'ân\'da geçen kelimesi var', 450, 620, 10.5))
    kaydet('51_chernoff', '51. Chernoff yüzleri: her mana bir yüz, yüzün çizgileri vasıflarıdır', 'İnsan gözü yüz farkını sayılardan hızlı seçer diye kurulmuş usul.', b, 900, 640)
# 52 Metro
def metro():
    b = []
    L = {'A': [('E', 80, 330), ('A', 200, 330), ('D', 320, 330), ('K', 440, 330), ('U', 560, 330), ('X', 700, 330)],
         'A2': [('D', 320, 330), ('J', 400, 250), ('L', 400, 430)], 'U2': [('U', 560, 330), ('Y', 640, 250), ('Z', 640, 430)],
         'B': [('E', 80, 330), ('B', 200, 470), ('N', 300, 470), ('F', 420, 560), ('G', 500, 470)], 'AB': [('A', 200, 330), ('N', 300, 470)],
         'C': [('E', 80, 330), ('C', 140, 160), ('H', 260, 130)]}
    col = {'A': '#2f6fb3', 'A2': '#2f6fb3', 'U2': '#2f6fb3', 'B': '#3f8f3a', 'AB': '#2c8c7c', 'C': '#c26a1e'}
    st = {}
    for k, s in L.items():
        b.append(f'<polyline points="{" ".join(f"{x},{y}" for _,x,y in s)}" fill="none" stroke="{col[k]}" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"/>')
        for m, x, y in s: st.setdefault(m, (x, y, 0)); st[m] = (x, y, st[m][2] + 1)
    for m, (x, y, n) in st.items():
        b.append(f'<circle cx="{x}" cy="{y}" r="{11 if n>1 else 7}" fill="#fff" stroke="#2b2410" stroke-width="{3 if n>1 else 2}"/>')
        b.append(T(KISA[m], x, y - 18, 11, w='font-weight="700"')); b.append(AR(' '.join(kel(m)[:2]), x, y + 28, 12))
    b.append(T('Hat = dal · durak = mana · kalın halka = aktarma (birden çok hattın geçtiği mana)', 450, 620, 11))
    kaydet('52_metro', '52. Metro haritası: dallar birer hat, manalar durak', 'Esas merkez istasyondur; şekli belirmiş iki hattın aktarma durağıdır.', b, 900, 640)
# 53 Periyodik
def periyodik():
    b = []; cols = ['A', 'AB', 'B', 'C', 'H', 'R2']
    for j, c in enumerate(cols): b.append(T(DALAD[c], 120 + j * 125 + 55, 80, 11, w=f'font-weight="700" fill="{RENK[c]}"'))
    for l in range(6): b.append(T(f'{l}', 90, 120 + l * 85 + 40, 13, w='font-weight="700"'))
    yer = collections.defaultdict(int)
    for m in ORDER:
        d = 'E' if m == 'E' else dal(m); j = cols.index(d) if d in cols else 0; l = depth(m) if m != 'R2' else 1
        n = sum(1 for q in ORDER if ('E' if q == 'E' else dal(q)) == d and (depth(q) if q != 'R2' else 1) == l); cw = 110 / n
        x = 120 + j * 125 + yer[(j, l)] * cw; y = 100 + l * 85; yer[(j, l)] += 1
        b.append(f'<rect x="{x}" y="{y}" width="{cw-2}" height="78" fill="{RENK[d]}" fill-opacity=".18" stroke="{RENK[d]}" stroke-width="1.5"/>')
        b.append(T(str(ORDER.index(m)), x + 4, y + 13, 8, 'start')); b.append(T(m, x + cw / 2, y + 38, 20, w='font-weight="700"'))
        b.append(T(KISA[m] if cw > 60 else KISA[m][:7], x + cw / 2, y + 56, 8.5)); b.append(T(f'{len(WORDS_OF.get(m,[]))} kel.', x + cw / 2, y + 71, 8, fill='#6d6650'))
    b.append(T('Sütun = dal (grup), satır = türeme basamağı (devre). Aynı hücreye düşenler yan yana kayar.', 450, 630, 11))
    kaydet('53_periyodik', '53. Periyodik cetvel: dal sütun, basamak satır', 'Yeri belli olan boş hücre, henüz bulunmamış bir mananın yeridir.', b, 900, 650)
# 54 Zwicky
def zwicky():
    b = []
    D = [('dal', ['ölçmek', 'düzlemek', 'pay', 'yakışmak']), ('basamak', ['1', '2', '3', '4', '5']), ('vezin türü', ['fiil', 'masdar', 'fâil', 'mef‘ûl', 'sıfat', 'çoğul']), ('insana dair mi', ['evet', 'hayır']), ('Kur\'ân\'da', ['geçer', 'geçmez'])]
    for j, (ad, ops) in enumerate(D):
        x = 40 + j * 168; b.append(T(ad, x + 75, 82, 11.5, w='font-weight="700"'))
        for i, o in enumerate(ops): b.append(f'<rect x="{x}" y="{95+i*42}" width="150" height="36" fill="#fff" stroke="#2b2410"/>'); b.append(T(o, x + 75, 118 + i * 42, 11))
    yol = [([0, 1, 2, 0, 0], '#2f6fb3', 'خَالِق'), ([0, 3, 0, 0, 1], '#7a3fb3', 'تَخَلَّقَ (huy takınmak)'), ([1, 1, 5, 1, 1], '#3f8f3a', 'خُلْقَان'), ([3, 0, 4, 1, 1], '#a8478f', 'خَلِيق')]
    for k, (y_, c, ad) in enumerate(yol):
        pts = ' '.join(f'{40+j*168+75+(k-1.5)*8},{95+i*42+18}' for j, i in enumerate(y_))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="3" stroke-opacity=".8"/>'); b.append(T(ad, 450, 390 + k * 22, 12, fill=c, w='font-weight="700"'))
    b.append(T('Her sütun bir eksen, her kutu bir seçenek. Bir kelime = her sütundan bir kutu seçen yol. 4×5×6×2×2 = 480 hücreden 37\'si dolu.', 450, 500, 11))
    kaydet('54_zwicky', '54. Zwicky morfolojik kutusu: bütün ihtimallerin cetveli', 'Doldurulmamış yollar, kökün henüz kullanmadığı terkiplerdir.', b, 900, 530)
# 55 Işınsal
def isinsal():
    b = []; cx, cy = 450, 350
    b.append(f'<circle cx="{cx}" cy="{cy}" r="58" fill="#e8c766"/>'); b.append(T('MERKEZ ÜYE', cx, cy - 8, 11, w='font-weight="700"')); b.append(T('ölçüp biçerek hazırlamak', cx, cy + 10, 9.5))
    tip = {'A': 'özelleşme', 'B': 'özelleşme', 'C': 'mecaz-ı mürsel (sonuç)', 'H': 'mecaz-ı mürsel (gaye)', 'D': 'kemal', 'J': 'mef‘ûl', 'K': 'netice', 'U': 'istiare (iç suret)', 'X': 'çoğalma', 'Y': 'taşma', 'Z': 'giyinme istiaresi', 'L': 'istiare (sözde yaratma)', 'N': 'iki yolun buluşması', 'F': 'zamanla süreç', 'G': 'yüzeye sürme'}
    P = {'E': (cx, cy)}; top = KIDS['E']
    def yer(m, a0, a1, r):
        a = (a0 + a1) / 2; P[m] = (cx + r * math.cos(a), cy + r * .85 * math.sin(a))
        ch = [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m]
        for k, c in enumerate(ch): yer(c, a0 + (a1 - a0) * k / len(ch), a0 + (a1 - a0) * (k + 1) / len(ch), r + 85)
    wt = [1 + len(alt_say(m)) for m in top]; t = sum(wt); a = -math.pi / 2
    for m, w in zip(top, wt): yer(m, a, a + 2 * math.pi * w / t, 120); a += 2 * math.pi * w / t
    for m, (x, y) in P.items():
        if m == 'E': continue
        px, py = P[MANA[m]['ebeveyn'][0]]; b.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{RENK[dal(m)]}" stroke-width="2"/>')
        b.append(T(tip.get(m, ''), (px + x) / 2, (py + y) / 2 - 3, 8.5, fill='#b3541e'))
    for m, (x, y) in P.items():
        if m == 'E': continue
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{RENK[dal(m)]}"/>'); b.append(T(KISA[m], x, y - 10, 10.5, w='font-weight="700"'))
    kaydet('55_isinsal', '55. Işınsal kategori (Brugman, Lakoff): merkez üyeden ışınlar', 'Kenar üstündeki kırmızı yazı, uzantının cinsi (mecaz, istiare, netice…).', b, 900, 700)
# 56 İlk sahne
def ilksahne():
    b = [DEF]
    S = [('MARANGOZ / TERZİ SAHNESİ', ['deriyi, tahtayı ölçer', 'keser, düzler', 'parçayı işe uydurur', 'ortaya bir eser çıkar', 'eser zamanla aşınır']),
         ]
    kutu(b, 30, 80, 300, 160, 'İLK SAHNE (beden tecrübesi)', S[0][1], '#b8860b')
    H = [('ölçmek = tayin etmek', 'A', 'خَلَقَ'), ('ortaya çıkan eser = yaratılmış', 'J', 'مَخْلُوق'), ('eserin kalıbı = yaradılış', 'K', 'خِلْقَة'), ('içe verilen kalıp = huy', 'U', 'خُلُق'), ('işe uymak = lâyık olmak', 'H', 'خَلِيق'), ('aşınmak = eskimek', 'F', 'خَلِق'), ('sözde eser yapmak = uydurmak', 'L', 'اِخْتَلَقَ')]
    for k, (t, m, w) in enumerate(H):
        y = 80 + k * 76; c = RENK[dal(m)]
        b.append(f'<rect x="520" y="{y}" width="350" height="62" rx="8" fill="#fff" stroke="{c}" stroke-width="1.8"/>'); b.append(T(t, 535, y + 26, 11.5, 'start', c, 'font-weight="700"')); b.append(AR(w, 860, y + 50, 15, 'end'))
        ok(b, 330, 160, 520, y + 31)
    b.append(T('Soldaki sahne bir kere görülünce sağdaki mecazlar ayrıca ezberlenmez.', 180, 300, 10.5, fill='#6d6650'))
    kaydet('56_ilk_sahne', '56. İlk sahne (Tyler ve Evans): bütün manalar tek bir beden sahnesinden', 'Sahnenin her anı bir manaya dönüşür.', b, 900, 640)
# 57 Halliday
def halliday():
    b = []
    def kol(x, y, ad, ops, h=26):
        b.append(T(ad, x, y + len(ops) * h / 2 + 4, 11, 'end', w='font-weight="700"'))
        b.append(f'<line x1="{x+8}" y1="{y+len(ops)*h/2}" x2="{x+22}" y2="{y+len(ops)*h/2}" stroke="#2b2410" stroke-width="1.5"/><line x1="{x+22}" y1="{y+6}" x2="{x+22}" y2="{y+len(ops)*h-6}" stroke="#2b2410" stroke-width="1.5"/>')
        for i, o in enumerate(ops): b.append(f'<line x1="{x+22}" y1="{y+i*h+h/2}" x2="{x+38}" y2="{y+i*h+h/2}" stroke="#2b2410"/>'); b.append(T(o, x + 42, y + i * h + h / 2 + 4, 10.5, 'start'))
    tags = collections.Counter(KEL[w]['tag'] for w in WS)
    kol(110, 260, 'KELİME', ['fiil', 'isim'], 60)
    fi = ['mücerred (خَلَقَ خَلِقَ خَلُقَ)', 'mezîd tef‘îl (خَلَّقَ)', 'mezîd if‘âl (أَخْلَقَ)', 'tefe‘‘ul (تَخَلَّقَ)', 'ifti‘âl (اِخْتَلَقَ)', 'if‘av‘ale (اِخْلَوْلَقَ)']
    kol(240, 80, 'fiil', fi)
    isim = [f'{t} ({n})' for t, n in tags.items() if t != 'fiil']
    kol(240, 290, 'isim', isim, 24)
    b.append(T('{ = "ya bu ya şu" seçimi. Her yol sondan başa okununca bir kelime türü ortaya çıkar.', 450, 630, 11))
    kaydet('57_halliday', '57. Halliday seçim ağı: kelime türü bir dizi "ya … ya …" seçimidir', 'Parantez içinde bu kökteki kelime adedi.', b, 900, 650)
# 58 ± matris
def bilesen():
    b = []
    F = [('+ölçü', lambda m: dal(m) in ('A', 'AB') or m == 'C'), ('+yüzey', lambda m: dal(m) in ('B', 'AB')), ('+canlı', lambda m: m in ('U', 'X', 'Y', 'Z', 'J', 'K')), ('+iç', lambda m: m in ('U', 'X', 'Y', 'Z')),
         ('+sonuç', lambda m: m in ('J', 'K', 'N', 'F')), ('+zaman', lambda m: m in ('F',)), ('+söz', lambda m: m in ('L',)), ('+değer', lambda m: m in ('H', 'C', 'X'))]
    x0, y0 = 170, 80
    for j, (f, _) in enumerate(F): b.append(T(f, x0 + j * 80 + 40, y0, 11, w='font-weight="700"'))
    for i, m in enumerate(ORDER):
        y = y0 + 12 + i * 32; b.append(T(KISA[m], x0 - 10, y + 20, 10.5, 'end'))
        for j, (f, fn) in enumerate(F):
            v = fn(m); b.append(f'<rect x="{x0+j*80+4}" y="{y+2}" width="72" height="28" fill="{RENK[dal(m)] if v else "#fff"}" fill-opacity="{.7 if v else 1}" stroke="#e2d9bd"/>'); b.append(T('+' if v else '−', x0 + j * 80 + 40, y + 21, 14, fill='#fff' if v else '#aaa', w='font-weight="700"'))
    kaydet('58_bilesen', '58. Bileşen çözümlemesi: her mana bir artı-eksi dizisi', 'İki mananın farkı, satırlarının farklı olduğu sütunlardır. Bileşenler bu levha için seçildi.', b, 900, y0 + 30 + 32 * len(ORDER))
# 59 OT
def ot():
    b = []
    C = ['VEZNE-SADIK', 'BAĞLAMA-UYGUN', 'KÖKE-YAKIN', 'İKTİSAT']
    for k, (ar, ctx, cand, win) in enumerate([('خُلُق', 'إِنَّكَ لَعَلَىٰ خُلُقٍ عَظِيمٍ', [('huy', [0, 0, 1, 0]), ('yaradılış', [1, 1, 0, 0]), ('yaratma', [1, 1, 0, 0]), ('eski', [1, 1, 1, 0])], 0),
                                              ('خَلَق', 'ثَوْبٌ خَلَقٌ', [('eski, yıpranmış', [0, 0, 1, 0]), ('yaratma', [1, 1, 0, 0]), ('huy', [1, 1, 1, 0])], 0)]):
        y = 80 + k * 280; b.append(AR(ar + '   ←   ' + ctx, 860, y, 18, 'end'))
        x0 = 40; cw = [170] + [150] * 4
        b.append(f'<rect x="{x0}" y="{y+14}" width="{sum(cw)}" height="28" fill="#2b2410"/>'); b.append(T('aday mana', x0 + 8, y + 33, 11, 'start', '#fff', 'font-weight="700"'))
        for j, c in enumerate(C): b.append(T(c, x0 + 170 + j * 150 + 75, y + 33, 10.5, fill='#fff', w='font-weight="700"'))
        for i, (ad, v) in enumerate(cand):
            yy = y + 42 + i * 30
            for j in range(5): b.append(f'<rect x="{x0+sum(cw[:j])}" y="{yy}" width="{cw[j]}" height="30" fill="{"#fbf6e6" if i==win else "#fff"}" stroke="#e2d9bd"/>')
            b.append(T(('☞ ' if i == win else '   ') + ad, x0 + 8, yy + 20, 11, 'start', w='font-weight="700"' if i == win else ''))
            for j, n in enumerate(v):
                if n: b.append(T('*' + ('!' if j == v.index(1) and i != win else ''), x0 + 170 + j * 150 + 75, yy + 21, 14, fill='#b3541e'))
    b.append(T('Kaideler soldan sağa önem sırasıdır. * = çiğneme, *! = adayı eleyen çiğneme, ☞ = kazanan mana.', 450, 620, 11))
    kaydet('59_ot', '59. Eniyilik tablosu (Optimality Theory): bir yerde hangi mananın kazandığı', 'Kaideler ve sırası bu levha için kuruldu.', b, 900, 640)
# 60 Feynman
def feynman():
    b = [DEF]
    R = [('fiil kalıbı', 'خَلَقَ', 'yarattı'), ('فَاعِل', 'خَالِق', 'yaratan'), ('مَفْعُول', 'مَخْلُوق', 'yaratılmış'), ('فِعْلَة', 'خِلْقَة', 'yaradılış'), ('فُعُل', 'خُلُق', 'huy'), ('اِفْتَعَلَ', 'اِخْتَلَقَ', 'uydurdu')]
    for k, (vz, w, tr) in enumerate(R):
        y = 90 + k * 88
        b.append(f'<line x1="60" y1="{y}" x2="330" y2="{y+30}" stroke="#2b2410" stroke-width="2.5" marker-end="url(#o)"/>'); b.append(T('kök: خ ل ق', 200, y + 2, 10.5, 'start'))
        b.append(f'<path d="M60,{y+60} q20,-10 40,0 t40,0 t40,0 t40,0 t40,0 t40,0 t30,-30" stroke="#b3541e" stroke-width="2" fill="none"/>'); b.append(T('vezin:', 200, y + 66, 10.5, 'start', '#b3541e')); b.append(AR(vz, 245, y + 68, 13, 'start', '#b3541e'))
        b.append(f'<circle cx="340" cy="{y+30}" r="6" fill="#2b2410"/>')
        b.append(f'<line x1="346" y1="{y+30}" x2="620" y2="{y+30}" stroke="{RENK[dal([m for m in MANA if KISA[m]==tr or (tr=="yarattı" and m=="D") or (tr=="yaradılış" and m=="K") or (tr=="uydurdu" and m=="L") or (tr=="yaratılmış" and m=="J") or (tr=="yaratan" and m=="D")][0])]}" stroke-width="4" marker-end="url(#o)"/>')
        b.append(AR(w, 680, y + 36, 18, 'start')); b.append(T(tr, 780, y + 35, 11, 'start'))
    b.append(T('Düz çizgi = kök (harfler), dalgalı çizgi = vezin, nokta = birleşme, kalın çizgi = doğan kelime (renk dal).', 450, 625, 11))
    kaydet('60_feynman', '60. Tel diyagramı (Feynman tarzı): kök ile vezin bir noktada çarpışır, kelime doğar', 'Her satır bir türeme tepkimesi.', b, 900, 640)
# 61 Laban
def laban():
    b = []; cols = ['A', 'AB', 'B', 'C', 'H']
    for j, c in enumerate(cols):
        x = 160 + j * 140; b.append(f'<line x1="{x}" y1="70" x2="{x}" y2="600" stroke="#ccc"/>'); b.append(T(DALAD[c], x + 60, 620, 11, w=f'font-weight="700" fill="{RENK[c]}"'))
    for l in range(6): b.append(f'<line x1="150" y1="{580-l*85}" x2="870" y2="{580-l*85}" stroke="#2b2410" stroke-width="{2 if l==0 else .5}"/>'); b.append(T(f'{l}. basamak', 140, 584 - l * 85 - 40, 10, 'end'))
    yer = collections.defaultdict(int)
    for m in MN:
        if m == 'R2': continue
        d = dal(m); j = cols.index(d); l = depth(m)
        x = 166 + j * 140 + yer[(j, l)] * 42; yer[(j, l)] += 1
        h = 30 + 10 * len(WORDS_OF.get(m, [])); y = 580 - l * 85 + 4 - h
        fill = 'url(#t1)' if l % 3 == 0 else 'url(#t2)' if l % 3 == 1 else RENK[d]
        b.append(f'<rect x="{x}" y="{y}" width="36" height="{h}" fill="{RENK[d]}" fill-opacity="{.25+.15*l}" stroke="{RENK[d]}" stroke-width="2"/>')
        b.append(f'<text transform="translate({x+22},{y+h-4}) rotate(-90)" font-size="10" fill="#1a1a1a">{esc(KISA[m])}</text>')
    kaydet('61_laban', '61. Labanotasyon tarzı şerit: zaman aşağıdan yukarı, sütun dal', 'Blok boyu = kelime sayısı, koyuluk = derinlik. Raks yazısı gibi aşağıdan yukarı okunur.', b, 900, 640)
# 62 Nota
def nota():
    b = []
    yol = [chain('X'), chain('Y'), chain('L'), chain('F'), chain('G'), chain('N')]
    for k, ch in enumerate(yol):
        y0 = 90 + k * 90
        for l in range(5): b.append(f'<line x1="40" y1="{y0+l*10}" x2="860" y2="{y0+l*10}" stroke="#999"/>')
        b.append(T('𝄞', 52, y0 + 38, 40, fill='#2b2410'))
        for j, m in enumerate(ch):
            x = 130 + j * 140; y = y0 + 40 - depth(m) * 8; n = len(WORDS_OF.get(m, []))
            b.append(f'<ellipse cx="{x}" cy="{y}" rx="8" ry="6" fill="{RENK[dal(m)] if n else "#fff"}" stroke="#2b2410" transform="rotate(-20 {x} {y})"/>')
            b.append(f'<line x1="{x+7}" y1="{y}" x2="{x+7}" y2="{y-32}" stroke="#2b2410"/>')
            for f in range(min(n, 3)): b.append(f'<path d="M{x+7},{y-32+f*7} q10,6 6,14" stroke="#2b2410" fill="none"/>')
            b.append(T(KISA[m], x, y0 + 64, 9.5))
    b.append(T('Notanın yüksekliği = köke uzaklık · dolu nota = kelimesi var · bayrak sayısı = kelime adedi (en çok 3). Her porte bir türeme yolu.', 450, 640, 10.5))
    kaydet('62_nota', '62. Nota tarzı: her türeme yolu bir ezgi', 'Soldan sağa esastan uca; inen ezgi, kökten uzaklaşmaktır.', b, 900, 660)
# 63 İskelet formül
def iskelet():
    b = []
    W2 = [('خَالِق', 'fâil', [('خ', 0), ('ا', 'e'), ('ل', 0), ('ق', 0)]), ('مَخْلُوق', 'mef‘ûl', [('م', 'e'), ('خ', 0), ('ل', 0), ('و', 'e'), ('ق', 0)]), ('تَخْلِيق', 'tef‘îl masdarı', [('ت', 'e'), ('خ', 0), ('ل', 0), ('ي', 'e'), ('ق', 0)]),
          ('اِخْتَلَقَ', 'ifti‘âl', [('ا', 'e'), ('خ', 0), ('ت', 'e'), ('ل', 0), ('ق', 0)]), ('أَخْلَاق', 'cem‘', [('أ', 'e'), ('خ', 0), ('ل', 0), ('ا', 'e'), ('ق', 0)]), ('خُلْقَان', 'cem‘', [('خ', 0), ('ل', 0), ('ق', 0), ('ا', 'e'), ('ن', 'e')])]
    for k, (w, ad, hs) in enumerate(W2):
        x0 = 60 + (k % 2) * 430; y0 = 120 + (k // 2) * 170; kok = [h for h in hs if h[1] == 0]
        pts = [(x0 + 60 + j * 90, y0 + (0 if j % 2 else 40)) for j in range(3)]
        b.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" stroke="#2b2410" stroke-width="3" fill="none"/>')
        for (x, y), (h, _) in zip(pts, kok): b.append(f'<circle cx="{x}" cy="{y}" r="15" fill="#e8c766" stroke="#2b2410"/>'); b.append(AR(h, x, y + 6, 17))
        ki = 0; ek = 0
        for i, (h, t) in enumerate(hs):
            if t == 0: ki += 1; continue
            j = min(ki, 2); x, y = pts[j]; dx = -40 if ki == 0 else 40 if ki == 3 else 0; dy = -50 if (j % 2 == 0) else 50
            if ki not in (0, 3): x = (pts[ki - 1][0] + pts[ki][0]) / 2; y = (pts[ki - 1][1] + pts[ki][1]) / 2; dy = 55 if ek % 2 == 0 else -55
            b.append(f'<line x1="{x}" y1="{y}" x2="{x+dx}" y2="{y+dy}" stroke="#b3541e" stroke-width="2"/>'); b.append(f'<circle cx="{x+dx}" cy="{y+dy}" r="12" fill="#fff" stroke="#b3541e"/>'); b.append(AR(h, x + dx, y + dy + 5, 15, fill='#b3541e')); ek += 1
        b.append(AR(w, x0 + 360, y0 + 20, 22)); b.append(T(ad, x0 + 360, y0 + 46, 11))
    b.append(T('Sarı halka = kök harfi (iskelet), kırmızı dal = vezinin eklediği harf (fonksiyonel grup).', 450, 630, 11))
    kaydet('63_iskelet', '63. İskelet formül tarzı: kök harfleri omurga, vezin harfleri yan grup', 'Kimyada aynı iskelete farklı grup takılınca başka madde olur.', b, 900, 650)
# 64 SMILES
def smiles():
    b = []
    def yaz(m):
        ch = [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m]
        s = m
        for c in ch[:-1]: s += '(' + yaz(c) + ')'
        if ch: s += yaz(ch[-1])
        return s
    s = yaz('E') + '.R2'; s2 = s
    for m in ORDER: pass
    b.append(f'<text x="450" y="130" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-size="26" font-weight="700" fill="#2b2410">{esc(s)}</text>')
    b.append(T('Okunuşu: harf = mana; peş peşe = türeme; parantez = yan dal; nokta = bağsız parça (kök dışı).', 450, 175, 12))
    for k, m in enumerate(ORDER): b.append(T(f'{m} = {KISA[m]}', 90 + (k % 4) * 200, 230 + (k // 4) * 26, 11.5, 'start', RENK[dal(m)]))
    kel_s = 'خلق' + ''.join('(' + '|'.join(kel(m)[:2]) + ')' for m in ['D', 'U', 'F', 'L'])
    b.append(T('Kelimelerle (kısmî):', 450, 400, 12, w='font-weight="700"')); b.append(AR(kel_s, 450, 440, 20))
    b.append(T(f'Bütün yapı {len(s)} işarete sığar. Aynı yazıdan ağaç geri çizilebilir.', 450, 500, 12))
    kaydet('64_smiles', '64. SMILES tarzı tek satır: bütün türeme ağacı bir satırda', 'Kimyada molekül böyle tek satıra yazılır.', b, 900, 540)
# 65 Belirleyici
def belirleyici():
    b = []
    D = {'A': ('📏', 'ölçü'), 'D': ('✨', 'var etme'), 'J': ('🧍', 'varlık'), 'K': ('🧬', 'kalıp'), 'U': ('❤️', 'iç hâl'), 'X': ('⚖️', 'düzen'), 'Y': ('🔥', 'taşma'), 'Z': ('🎭', 'giyinme'), 'L': ('🗣️', 'söz'), 'N': ('🏹', 'şekil'),
         'B': ('🪨', 'yüzey'), 'F': ('👕', 'eşya/zaman'), 'G': ('🌸', 'koku'), 'C': ('🍰', 'pay'), 'H': ('🎯', 'uygunluk'), 'R2': ('🍲', 'kap')}
    for k, m in enumerate(MN):
        x = 70 + (k % 4) * 210; y = 110 + (k // 4) * 130; e, ad = D[m]; w = kel(m)[0] if kel(m) else 'خلق'
        b.append(AR(w, x + 70, y + 10, 26)); b.append(f'<text x="{x+10}" y="{y+14}" font-size="34" font-family="Noto Color Emoji">{e}</text>')
        b.append(T(f'belirleyici: {ad}', x + 50, y + 44, 10.5, fill='#6d6650')); b.append(T(KISA[m], x + 50, y + 62, 11, fill=RENK[dal(m)], w='font-weight="700"'))
    b.append(T('Hiyeroglifte okunmayan bir işaret, kelimenin hangi sınıftan olduğunu gösterir. Burada kökün yanına mana sınıfı işareti konuldu.', 450, 640, 10.5))
    kaydet('65_belirleyici', '65. Belirleyici işaret (Mısır yazısı, Çince bileşen tarzı)', 'Ses kökten, sınıf işaretten okunur. İşaretleri bu levha için seçtim.', b, 900, 660)
# 66 Emoji
def emoji():
    b = []
    E3 = [('A', '📏✂️'), ('D', '📏✂️➡️✨'), ('J', '✨➡️🧍'), ('K', '🧍➡️🧬'), ('U', '🧬➡️❤️'), ('X', '❤️❤️❤️➡️⚖️'), ('Y', '❤️💥➡️😠'), ('Z', '🧍👕❤️'), ('L', '✨🗣️❌'),
          ('B', '🪵➡️🪨'), ('N', '📏+🪨➡️🏹'), ('F', '👕⏳➡️🩹'), ('G', '🌸🖐️➡️🪨'), ('C', '📏➡️🍰'), ('H', '📏➡️🎯✅'), ('R2', '🇬🇷➡️🍲')]
    for k, (m, e) in enumerate(E3):
        x = 60 + (k % 2) * 430; y = 100 + (k // 2) * 66
        b.append(f'<text x="{x}" y="{y}" font-size="30" font-family="Noto Color Emoji">{e}</text>'); b.append(T(KISA[m], x + 250, y - 8, 12, 'start', RENK[dal(m)], 'font-weight="700"'))
    kaydet('66_emoji', '66. Emoji dizisi: her mana resimli bir cümle', 'Ok sebep-netice, artı birleşme. Resimler bu levha için seçildi.', b, 900, 640)
# 67 Takvim
def takvim():
    b = []
    rows = []
    for m in MN:
        if m == 'R2': continue
        p = MANA[m]['ebeveyn']; s = MANA[m]['sebep'].replace('çünkü ', '')
        kar = {'U': 'yaradılış', 'K': 'huy', 'J': 'yaratma', 'D': 'uydurma', 'L': 'yaratma', 'F': 'yaratılmış', 'C': 'yakışma', 'H': 'pay'}.get(m, '—')
        rows.append([KISA[m], DALAD[dal(m)] if dal(m) != 'AB' else 'ikisi', str(depth(m)), (kel(m) or ['—'])[0], s[:42], kar])
    tablo(b, 20, 70, ['mana', 'tabiatı (dal)', 'derece', 'en iyisi', 'menfaati (neden doğdu)', 'karıştığı'], rows, [110, 120, 55, 110, 345, 120], 34, ar_cols=(3,))
    kaydet('67_takvim', "67. Takvîmü's-sıhha tablosu (İbn Butlân usulü): her mana bir satır, sabit sütunlar", 'Ortaçağ sağlık cetvelinin sütun tertibi manaya uygulandı: tabiat, derece, en iyisi, menfaati, mazarratı.', b, 900, 70 + 34 * (len(rows) + 1) + 20)
# 68 Teşcîr
def tescir():
    b = []; P = {'E': (450, 520)}
    top = KIDS['E']
    def yer(m, a0, a1, r):
        a = (a0 + a1) / 2; P[m] = (450 + r * math.cos(a), 520 + r * math.sin(a))
        ch = [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m]
        for k, c in enumerate(ch): yer(c, a0 + (a1 - a0) * k / len(ch), a0 + (a1 - a0) * (k + 1) / len(ch), r + 80)
    wt = [1 + len(alt_say(m)) for m in top]; t = sum(wt); a = -math.pi * .95
    for m, w in zip(top, wt): yer(m, a, a + math.pi * .9 * w / t, 110); a += math.pi * .9 * w / t
    b.append('<path d="M430,640 Q440,580 445,520 L455,520 Q460,580 470,640Z" fill="#8a5a2b"/>')
    for k in range(5): b.append(f'<path d="M{450-k*8},640 q{-20-k*10},10 {-40-k*15},20" stroke="#8a5a2b" stroke-width="3" fill="none"/>')
    b.append(AR('خ ل ق', 450, 662, 16, fill='#8a5a2b'))
    for m, (x, y) in P.items():
        if m == 'E': continue
        px, py = P[MANA[m]['ebeveyn'][0]]; b.append(f'<path d="M{px:.1f},{py:.1f} Q{(px+x)/2:.1f},{max(py,y)+10:.1f} {x:.1f},{y:.1f}" stroke="#8a5a2b" stroke-width="{max(2,10-2.5*depth(m))}" fill="none" stroke-linecap="round"/>')
    for m, (x, y) in P.items():
        b.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="44" ry="20" fill="{RENK[dal(m)]}" fill-opacity=".85"/>'); b.append(T(KISA[m], x, y + 4, 9.5, fill='#fff', w='font-weight="700"'))
        for j, w in enumerate(kel(m)[:2]): b.append(AR(w, x - 20 + j * 40, y - 24, 12))
    kaydet('68_tescir', '68. Teşcîr: kök bir ağacın kökü, manalar dallar, kelimeler meyve', 'İslâm ilimler tasnifinde ilimler böyle ağaç olarak çizilirdi.', b, 900, 680)
# 69 Lull ağacı
def lull():
    b = []
    P = [('RADICES (kökler)', 'kök harfleri خ ل ق', 600), ('TRUNCUS (gövde)', 'esas: ölçüp biçerek hazırlamak', 510), ('RAMI (büyük dallar)', 'ölçmek · düzlemek · pay · yakışmak', 420), ('RAMUSCULI (küçük dallar)', 'yaratmak · eskimek · koku · şekil', 330),
         ('FOLIA (yapraklar)', 'yaratılmış · yaradılış · uydurmak', 240), ('FLORES (çiçekler)', 'huy · huy takınmak · öfke', 150), ('FRUCTUS (meyve)', 'ahlâk (أَخْلَاق)', 75)]
    for k, (ad, ic, y) in enumerate(P):
        w = 120 + k * 0 if k < 2 else 120 + (7 - k) * 50
        c = ['#6b3e1d', '#8a5a2b', '#3f8f3a', '#5aa04f', '#7bbf6a', '#d07fb0', '#c0392b'][k]
        if k == 0: b.append(f'<path d="M380,{y} Q450,{y+50} 520,{y} M400,{y} l-50,40 M500,{y} l50,40" stroke="{c}" stroke-width="6" fill="none"/>')
        elif k == 1: b.append(f'<rect x="430" y="{y-50}" width="40" height="140" fill="{c}"/>')
        else: b.append(f'<ellipse cx="450" cy="{y}" rx="{w}" ry="30" fill="{c}" fill-opacity=".8"/>')
        b.append(T(ad, 40, y + 4, 11.5, 'start', '#2b2410', 'font-weight="700"')); b.append(T(ic, 860, y + 4, 11, 'end'))
    kaydet('69_lull_agaci', '69. Lull bilgi ağacı: yedi parçalı ağaç (kök, gövde, dal, yaprak, çiçek, meyve)', 'Her parça bir mertebe; meyve en son ve en çok emek isteyen manadır.', b, 900, 660)
# 70 Vücûh
def vucuh():
    b = []
    V = [('vech 1: yaratmak', 'D', ['خَلَقَ السَّمَاوَاتِ وَالْأَرْضَ', 'En‘âm 6:1'], ['فَطَرَ', 'بَرَأَ', 'جَعَلَ']),
         ('vech 2: ölçüp biçmek / şekil vermek', 'A', ['وَإِذْ تَخْلُقُ مِنَ الطِّينِ كَهَيْئَةِ الطَّيْرِ', 'Mâide 5:110'], ['صَوَّرَ', 'قَدَّرَ']),
         ('vech 3: uydurmak', 'L', ['إِنْ هَٰذَا إِلَّا اخْتِلَاقٌ', 'Sâd 38:7'], ['افْتَرَىٰ', 'تَقَوَّلَ']),
         ('vech 4: huy, ahlâk', 'U', ['وَإِنَّكَ لَعَلَىٰ خُلُقٍ عَظِيمٍ', 'Kalem 68:4'], ['دِين', 'عَادَة']),
         ('vech 5: din, âdet (yaratılış yolu)', 'K', ['إِنْ هَٰذَا إِلَّا خُلُقُ الْأَوَّلِينَ', 'Şuarâ 26:137'], ['سُنَّة']),
         ('vech 6: pay, nasip', 'C', ['مَا لَهُ فِي الْآخِرَةِ مِنْ خَلَاقٍ', 'Bakara 2:102'], ['نَصِيب'])]
    for k, (ad, m, (ay, yer), nz) in enumerate(V):
        y = 80 + k * 90; c = RENK[dal(m)]
        b.append(f'<rect x="20" y="{y}" width="860" height="80" rx="6" fill="#fff" stroke="{c}" stroke-width="1.5"/>'); b.append(T(ad, 32, y + 22, 12, 'start', c, 'font-weight="700"'))
        b.append(AR(ay, 860, y + 30, 17, 'end')); b.append(T(yer, 860, y + 54, 10, 'end', '#6d6650'))
        b.append(T('nezâiri (aynı manada başka kökler):', 32, y + 48, 10, 'start', '#6d6650')); b.append(AR(' · '.join(nz), 32, y + 70, 15, 'start'))
    kaydet('70_vucuh', '70. Vücûh ve nezâir: Kur\'ân\'da bir kelimenin manaları (vücûh) ve benzerleri (nezâir)', 'Klasik müfessirlerin sözlük usulü. Âyet yerleri hafızadandır; vech tasnifi bu levha için yapıldı.', b, 900, 640)
# 71 İzutsu
def izutsu():
    b = []; cx, cy = 450, 360
    for r in (110, 200, 285): b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e2d9bd" stroke-width="1.5"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="48" fill="#e8c766"/>'); b.append(AR('خَلْق', cx, cy + 8, 24))
    A = [('YARATMA ALANI', ['بَرَأَ', 'فَطَرَ', 'بَدَأَ', 'صَوَّرَ', 'جَعَلَ', 'أَنْشَأَ'], -math.pi / 2, '#2f6fb3'), ('AHLÂK ALANI', ['خُلُق', 'دِين', 'حِلْم', 'كَرَم'], math.pi / 6, '#7a3fb3'), ('ÖLÇÜ ALANI', ['قَدَرَ', 'مِيزَان', 'حِسَاب'], math.pi * 5 / 6, '#c26a1e')]
    for ad, ws, a0, c in A:
        b.append(T(ad, cx + 320 * math.cos(a0), cy + 300 * math.sin(a0) + 4, 12, fill=c, w='font-weight="700"'))
        for j, w in enumerate(ws):
            a = a0 + (j - len(ws) / 2 + .5) * 0.32; r = 160 if j % 2 else 240
            x, y = cx + r * math.cos(a), cy + r * math.sin(a); b.append(f'<line x1="{cx+48*math.cos(a):.1f}" y1="{cy+48*math.sin(a):.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{c}" stroke-opacity=".4"/>'); b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="#fff" stroke="{c}"/>'); b.append(AR(w, x, y + 6, 14))
    b.append(T('Odak kelime ortada; aynı anlam alanını paylaşan anahtar kelimeler kümelenir (İzutsu, "Kur\'ân\'da Allah ve İnsan").', 450, 690, 11))
    kaydet('71_izutsu', '71. İzutsu anlam alanı: odak kelime ve onu kuşatan anahtar kelimeler', 'Bir kelime tek başına değil, alanındaki komşularıyla manalanır. Alanlar bu levha için seçildi.', b, 900, 710)
# 72 Heisig
def heisig():
    b = []
    C = [('خلق', 'ölçüp biçmek', 'خ (hendek) · ل (değnek) · ق (kanca)', 'Terzi hendeğin başında değneğiyle ölçer, kancayla deriyi tutup keser.'),
         ('خَالِق', 'yaratan', 'خلق + ا (uzatma elifi)', 'Ölçüp biçeni değneği uzayıp dikilmiş görürsün: işi yapan odur.'),
         ('مَخْلُوق', 'yaratılmış', 'م (önündeki kap) + خلق + و', 'Ölçülüp biçilen şey bir kabın (م) içine konup sunulur.'),
         ('خُلُق', 'huy', 'خلق, ötreli', 'Ölçülüp biçilen kalıp insanın içine dikilir; dudaklar büzülür (ötre): içte kalan şekil.'),
         ('خَلِق', 'eskidi', 'خلق, esreli', 'Esre aşağı çeker: elbise aşağı sarkar, yıpranır.'),
         ('اِخْتَلَقَ', 'uydurdu', 'ا + خ + ت + لق', 'Araya bir ت (tuhaf bir harf) sıkıştırılmış: gerçek eserin içine sahte parça.')]
    for k, (w, kw, pr, st) in enumerate(C):
        x = 25 + (k % 3) * 290; y = 80 + (k // 3) * 280
        b.append(f'<rect x="{x}" y="{y}" width="270" height="260" rx="10" fill="#fff" stroke="#2b2410"/>'); b.append(AR(w, x + 135, y + 60, 36))
        b.append(T('ANAHTAR: ' + kw, x + 135, y + 98, 12.5, fill='#b3541e', w='font-weight="700"')); b.append(T('parçalar: ' + pr, x + 135, y + 122, 9.5, fill='#6d6650'))
        for j, s in enumerate([st[i:i + 40] for i in range(0, len(st), 40)]): b.append(T(s, x + 135, y + 155 + j * 16, 10.5))
    kaydet('72_heisig', '72. Heisig hikâyesi: her kelime bir anahtar mana, parçaları ve kısa bir sahne', 'Hikâyeler hafıza için uyduruldu; harflerin bu manaları taşıdığı iddia edilmez.', b, 900, 640)
# 73 Hafıza sarayı
def saray():
    b = []
    O = [('Ölçüm odası', 'A', 30, 70, 280, 260), ('Atölye (yaratma)', 'D', 310, 70, 280, 260), ('Sergi salonu', 'J', 590, 70, 280, 130), ('Kalıphane', 'K', 590, 200, 280, 130),
         ('Avlu (düzleme)', 'B', 30, 330, 280, 300), ('Gönül odası', 'U', 310, 330, 280, 300), ('Hazine (pay)', 'C', 590, 330, 140, 150), ('Kapı (yakışma)', 'H', 730, 330, 140, 150), ('Mahzen (kök dışı)', 'R2', 590, 480, 280, 150)]
    for ad, m, x, y, w, h in O:
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{RENK[dal(m)]}" fill-opacity=".08" stroke="#2b2410" stroke-width="3"/>'); b.append(T(ad, x + 10, y + 20, 11.5, 'start', RENK[dal(m)], 'font-weight="700"'))
        es = [m] + [c for c in KIDS.get(m, []) if c not in [o[1] for o in O]]
        for j, q in enumerate(es[:4]):
            xx = x + 20 + (j % 2) * (w / 2 - 10); yy = y + 50 + (j // 2) * 70
            b.append(f'<circle cx="{xx}" cy="{yy}" r="5" fill="#b3541e"/>'); b.append(T(KISA[q], xx + 10, yy + 4, 10, 'start', w='font-weight="700"'))
            b.append(AR(' '.join(kel(q)[:2]), xx + 10, yy + 24, 12, 'start'))
    b.append(T('Kapıdan girip odaları sırayla dolaşan kişi, her köşede bir manayı ve kelimesini görür.', 450, 655, 11))
    kaydet('73_saray', '73. Hafıza sarayı: her dal bir oda, her mana odada bir köşe', 'Kırmızı nokta = köşe. Odaların yerleşimi bu levha için yapıldı.', b, 900, 670)
# 74 Uzatılabilir metin
def stretch():
    b = []
    S = [('1. kat (tek satır)', ['خلق: ölçüp biçerek hazırlamak; buradan yaratma, huy, eskime, pay ve yakışma doğar.']),
         ('2. kat (paragraf)', ['خلق: ölçüp biçerek hazırlamak. Ölçülen şey yaratılır (خَلَقَ), yaratılanın kalıbı yaradılış (خِلْقَة),',
                               'yaradılışın içe vuranı huydur (خُلُق); huylar çoğalınca ahlâk (أَخْلَاق) olur. Düzlenen şey eskir (خَلِقَ),',
                               'işe ayrılan şey paydır (خَلَاق), işe uyan şey lâyıktır (خَلِيق). Söz yaratılırsa uydurmadır (اِخْتَلَقَ).']),
         ('3. kat (tam metin)', ['Her cümlenin sonundaki ▸ işaretine basılınca o mananın sebebi ve kelimeleri açılır:',
                                 '▸ yaratmak: ' + MANA['D']['sebep'], '▸ huy: ' + MANA['U']['sebep'], '▸ eskimek: ' + MANA['F']['sebep'], '▸ uydurmak: ' + MANA['L']['sebep'], '… (her mana için aynı şekilde)'])]
    y = 80
    for ad, ls in S:
        h = 36 + len(ls) * 20
        b.append(f'<rect x="30" y="{y}" width="840" height="{h}" rx="6" fill="#fff" stroke="#2b2410"/>'); b.append(T(ad, 42, y + 20, 11.5, 'start', '#b3541e', 'font-weight="700"'))
        for j, s in enumerate(ls): b.append(T(s, 42, y + 42 + j * 20, 11, 'start'))
        y += h + 30
        if ad != S[-1][0]: b.append(T('▼ aç', 450, y - 10, 11, fill='#2f6fb3'))
    kaydet('74_uzatilabilir', '74. Uzatılabilir metin (stretchtext): aynı metin üç uzunlukta', 'Okuyan, ihtiyacı kadar açar; kısa hâl her vakit uzunun özüdür.', b, 900, y + 10)
# 75 Anlamsal yakınlaştırma
def zoom():
    b = []
    for k, (ad, sc) in enumerate([('uzak', 0), ('orta', 1), ('yakın', 2)]):
        x0 = 20 + k * 293; b.append(f'<rect x="{x0}" y="70" width="280" height="540" rx="8" fill="#fff" stroke="#2b2410"/>'); b.append(T(f'{ad} bakış', x0 + 140, 92, 12, w='font-weight="700"'))
        if sc == 0:
            for j, d in enumerate(['A', 'B', 'C', 'H']):
                b.append(f'<circle cx="{x0+140}" cy="{160+j*110}" r="{20+3*len(alt_say(d))}" fill="{RENK[d]}" fill-opacity=".6"/>'); b.append(T(DALAD[d], x0 + 140, 164 + j * 110, 11, fill='#fff', w='font-weight="700"'))
        elif sc == 1:
            for j, m in enumerate(chain('X') + ['L', 'J']):
                b.append(f'<rect x="{x0+20+depth(m)*12}" y="{120+j*58}" width="190" height="44" rx="6" fill="{RENK[dal(m)]}" fill-opacity=".2"/>'); b.append(T(KISA[m], x0 + 30 + depth(m) * 12, 146 + j * 58, 11, 'start', w='font-weight="700"'))
        else:
            for j, w in enumerate(WORDS_OF['U'] + WORDS_OF['X']):
                k2 = KEL[w]; yy = 130 + j * 85
                b.append(AR(k2['ar'], x0 + 260, yy, 22, 'end')); b.append(T(' / '.join(k2['anlam'].values()), x0 + 20, yy + 24, 10.5, 'start')); b.append(T(f'{k2["tag"]} {k2["kuran"]}', x0 + 20, yy + 42, 9.5, 'start', '#6d6650'))
        if k < 2: b.append(T('⟶', x0 + 286, 340, 18))
    kaydet('75_yakinlastirma', '75. Anlamsal yakınlaştırma: yaklaştıkça şekil değil muhteva değişir', 'Uzakta dallar, ortada manalar (ahlâk yolu), yakında kelimeler ve manaları.', b, 900, 630)
# 76 Cornell
def cornell():
    b = []
    b.append('<rect x="30" y="70" width="840" height="560" fill="#fff" stroke="#2b2410"/><line x1="250" y1="70" x2="250" y2="520" stroke="#c0392b" stroke-width="2"/><line x1="30" y1="520" x2="870" y2="520" stroke="#2b2410" stroke-width="2"/>')
    Q = ['Esas nedir?', 'Yaratmak nereden?', 'Huy nereden?', 'Eskimek nereden?', 'Pay ve lâyık?', 'Uydurmak?', 'İstisna?']
    N = [('ölçüp biçerek hazırlamak (İbn Fâris: takdîr ve imlâs)', ['خَلَقَ']), ('ölçülen şey tamamlanınca var olur', ['خَالِق', 'خَلْق', 'مَخْلُوق']), ('yaradılışın içe verdiği kalıp', ['خُلُق', 'أَخْلَاق', 'تَخَلَّقَ']),
         ('düzlenen yüzey zamanla aşınır', ['خَلِقَ', 'خَلَق', 'خُلْقَان']), ('bir işe ayrılan şey pay, işe uyan şey lâyık', ['خَلَاق', 'خَلِيق']), ('yaratmanın sözle taklidi', ['اِخْتَلَقَ', 'اِخْتِلَاق']), ('kazan: Yunancadan, kökten değil', ['خِلْقِين'])]
    for k, (q, (n, ws)) in enumerate(zip(Q, N)):
        y = 100 + k * 60; b.append(T(q, 40, y + 10, 11.5, 'start', '#c0392b', 'font-weight="700"')); b.append(T(n, 265, y + 10, 11, 'start')); b.append(AR(' · '.join(ws), 860, y + 30, 14, 'end'))
    b.append(T('ÖZET:', 40, 545, 12, 'start', w='font-weight="700"'))
    b.append(T('Bir terzinin ölçüp biçmesi: ölçülen yaratılır, yaratılanın kalıbı huy olur; düzlenen eskir; ayrılan pay olur, uyan lâyık olur.', 40, 570, 11, 'start'))
    b.append(T('Sol sütun suâl, sağ sütun not, alt kutu özet. Tekrar ederken sağ kapatılıp soldaki suâle cevap verilir.', 40, 600, 10.5, 'start', '#6d6650'))
    kaydet('76_cornell', '76. Cornell notu: suâl sütunu, not sütunu, özet kutusu', 'Ders notu tutmanın üç bölmeli usulü.', b, 900, 650)
# 77 Çizgi roman
def comic():
    b = []
    P = [('Terzi deriyi ölçüp biçer.', 'خَلَقَ', 'A'), ('Ölçülen parçalar birleşir, eser ortaya çıkar.', 'خَلْق', 'D'), ('Eserin bir kalıbı, bir yaradılışı vardır.', 'خِلْقَة', 'K'),
         ('İnsanda bu kalıp içe yerleşir: huy.', 'خُلُق', 'U'), ('Elbise yıllarca giyilir, yüzü düzleşir.', 'خَلِق', 'F'), ('Biri olmayan sözü eser gibi diker.', 'اِخْتَلَقَ', 'L')]
    def adam(x, y, c):
        return f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{c}" stroke-width="2.5"/><line x1="{x}" y1="{y+12}" x2="{x}" y2="{y+52}" stroke="{c}" stroke-width="2.5"/><line x1="{x-18}" y1="{y+28}" x2="{x+18}" y2="{y+28}" stroke="{c}" stroke-width="2.5"/><path d="M{x-14},{y+80} L{x},{y+52} L{x+14},{y+80}" stroke="{c}" stroke-width="2.5" fill="none"/>'
    for k, (cap, w, m) in enumerate(P):
        x = 20 + (k % 3) * 290; y = 70 + (k // 3) * 285; c = RENK[dal(m)]
        b.append(f'<rect x="{x}" y="{y}" width="275" height="270" fill="#fff" stroke="#2b2410" stroke-width="3"/>'); b.append(f'<rect x="{x}" y="{y}" width="275" height="44" fill="#f3eedd" stroke="#2b2410"/>')
        b.append(T(cap, x + 137, y + 26, 10.5, w='font-weight="700"')); b.append(adam(x + 60, y + 100, '#2b2410'))
        if m == 'A': b.append(f'<rect x="{x+110}" y="{y+150}" width="120" height="50" fill="#d9b382"/><line x1="{x+110}" y1="{y+140}" x2="{x+230}" y2="{y+140}" stroke="#2b2410" stroke-width="2"/>')
        if m == 'D': b.append(f'<path d="M{x+130},{y+200} l40,-70 l40,70z" fill="#d9b382" stroke="#2b2410"/><text x="{x+170}" y="{y+120}" font-size="22">✨</text>')
        if m == 'K': b.append(f'<rect x="{x+130}" y="{y+120}" width="80" height="90" fill="none" stroke="{c}" stroke-dasharray="6 3" stroke-width="2"/>')
        if m == 'U': b.append(f'<path d="M{x+60},{y+125} c-8,-10 -18,0 0,14 c18,-14 8,-24 0,-14" fill="#c0392b"/>' + adam(x + 180, y + 100, '#2b2410') + f'<path d="M{x+180},{y+125} c-8,-10 -18,0 0,14 c18,-14 8,-24 0,-14" fill="#c0392b"/>')
        if m == 'F': b.append(f'<path d="M{x+130},{y+120} h80 v90 h-80z" fill="#b5b5b5"/><path d="M{x+150},{y+150} l10,10 M{x+180},{y+180} l12,-6" stroke="#fff" stroke-width="3"/><text x="{x+210}" y="{y+120}" font-size="20">⏳</text>')
        if m == 'L': b.append(f'<rect x="{x+100}" y="{y+80}" width="150" height="50" rx="20" fill="#fff" stroke="#2b2410"/><text x="{x+175}" y="{y+111}" text-anchor="middle" font-size="12">"Gördüm, oldu!"</text><text x="{x+175}" y="{y+170}" font-size="30" text-anchor="middle">❌</text>')
        b.append(AR(w, x + 137, y + 252, 20, fill=c))
    kaydet('77_cizgi_roman', '77. Veri çizgi romanı: türeme altı kare bir hikâye', 'Her kare bir mana, alt yazısı kelimesi.', b, 900, 650)
# 78 Mekânsal hipermetin
def hiper():
    b = [DEF]
    C = [('A', 60, 90), ('D', 330, 80), ('J', 620, 70), ('K', 600, 200), ('U', 640, 340), ('X', 650, 480), ('L', 340, 250), ('B', 60, 330), ('F', 80, 480), ('G', 310, 500), ('N', 330, 380), ('C', 60, 200), ('H', 360, 600 - 40)]
    pos = {m: (x, y) for m, x, y in C}
    for m, x, y in C:
        for p in MANA[m]['ebeveyn']:
            if p in pos: px, py = pos[p]; b.append(f'<line x1="{px+110}" y1="{py+30}" x2="{x+110}" y2="{y+30}" stroke="#bbb" stroke-dasharray="4 3" marker-end="url(#o)"/>')
    for m, x, y in C:
        c = RENK[dal(m)]; b.append(f'<rect x="{x}" y="{y}" width="220" height="62" rx="4" fill="#fffef8" stroke="{c}" stroke-width="2" filter="drop-shadow(2px 2px 2px #0002)"/>')
        b.append(f'<rect x="{x}" y="{y}" width="220" height="16" fill="{c}"/>'); b.append(T(KISA[m], x + 6, y + 12, 9.5, 'start', '#fff', 'font-weight="700"'))
        s = MANA[m]['sebep'].replace('çünkü ', ''); b.append(T(s[:38], x + 6, y + 32, 9, 'start')); b.append(T(s[38:76], x + 6, y + 44, 9, 'start')); b.append(AR(' '.join(kel(m)[:2]), x + 214, y + 58, 11, 'end'))
    kaydet('78_hiper_metin', '78. Mekânsal hipermetin (Tinderbox tarzı): notlar sayfaya serpilir, yakınlık münasebettir', 'Kartın yeri elle seçilir; kesik ok türeme bağıdır.', b, 900, 650)
# 79 Glif
def glif():
    b = []
    F = [('mana sayısı', lambda w: len(KEL[w]['anlam']) / 2), ('basamak', lambda w: kder(w) / 5), ('Kur\'ân geçişi', lambda w: min(1, (int(KEL[w]['kuran'][1:]) if KEL[w]['kuran'][1:].isdigit() else 0) / 50)),
         ('harf sayısı', lambda w: len([c for c in KEL[w]['ar'] if 'ء' <= c <= 'ي']) / 8), ('insana dair', lambda w: 1 if any(m in ('U', 'X', 'Y', 'Z', 'H') for m in KEL[w]['anlam']) else .15), ('fiil mi', lambda w: 1 if KEL[w]['tag'] == 'fiil' else .15)]
    def kder(w): return max(depth(m) for m in KEL[w]['anlam'])
    for k, w in enumerate(WS):
        x = 60 + (k % 8) * 108; y = 120 + (k // 8) * 108; c = RENK[dal(list(KEL[w]['anlam'])[0])]
        pts = []
        for j, (_, f) in enumerate(F):
            a = -math.pi / 2 + 2 * math.pi * j / len(F); r = 8 + 32 * max(.05, min(1, f(w))); pts.append(f'{x+r*math.cos(a):.1f},{y+r*math.sin(a):.1f}')
            b.append(f'<line x1="{x}" y1="{y}" x2="{x+40*math.cos(a):.1f}" y2="{y+40*math.sin(a):.1f}" stroke="#eee"/>')
        b.append(f'<polygon points="{" ".join(pts)}" fill="{c}" fill-opacity=".45" stroke="{c}" stroke-width="1.5"/>'); b.append(AR(KEL[w]['ar'], x, y + 54, 12))
    b.append(T('Yıldızın kolları (saat yönünde, yukarıdan): ' + ' · '.join(a for a, _ in F), 450, 660, 10.5))
    kaydet('79_glif', '79. Glif: her kelime altı kollu bir yıldız, şekli vasıflarından', 'Benzer yıldızlar benzer kelimelerdir; renk ilk mananın dalı.', b, 900, 680)
# 80 Kalıp dili
def kalip():
    b = [DEF]
    K2 = [(1, 'ÖLÇÜLÜ HAZIRLIK', 'Bir şey bir iş için hazırlanacak.', 'Ölç, biç, sonra yap.', [2, 5, 6], 'A'), (2, 'ESERİN DOĞUŞU', 'Ölçülen parçalar hazır.', 'Birleştir; eser var olur.', [3, 7], 'D'),
          (3, 'İÇ KALIP', 'Eser yaşayan bir şey.', 'Kalıbı içine yerleştir: huy.', [4], 'U'), (4, 'YERLEŞİK DÜZEN', 'Huylar çoğaldı.', 'Onları bir ilme bağla: ahlâk.', [], 'X'),
          (5, 'DÜZ YÜZEY', 'Madde pürüzlü.', 'Düzle; zamanla aşınır.', [8], 'B'), (6, 'PAY VE LİYAKAT', 'Hazırlanan bir işe ayrılacak.', 'Payını ver, işe uyanı seç.', [], 'C'),
          (7, 'SAHTE ESER', 'Eser yokken var denmesi.', 'Bunu ayırt et: uydurmadır.', [], 'L'), (8, 'EŞYANIN YAŞLANMASI', 'Yüzey kullanılıyor.', 'Kabul et; eskilik de bir haldir.', [], 'F')]
    P = {}
    for k, (n, ad, ba, ce, ln, m) in enumerate(K2):
        x = 25 + (k % 4) * 218; y = 90 + (k // 4) * 270; P[n] = (x, y); c = RENK[dal(m)]
        b.append(f'<rect x="{x}" y="{y}" width="200" height="200" fill="#fff" stroke="{c}" stroke-width="2"/>'); b.append(T(f'{n}. {ad}', x + 100, y + 22, 11, fill=c, w='font-weight="700"'))
        b.append(T('bağlam:', x + 10, y + 50, 9.5, 'start', '#6d6650')); b.append(T(ba, x + 10, y + 66, 10, 'start'))
        b.append(T('çözüm:', x + 10, y + 96, 9.5, 'start', '#6d6650')); b.append(T(ce, x + 10, y + 112, 10, 'start', w='font-weight="700"'))
        b.append(AR(' '.join(kel(m)[:2]), x + 190, y + 150, 15, 'end')); b.append(T('sonraki: ' + (', '.join(map(str, ln)) or '—'), x + 10, y + 188, 10, 'start', '#b3541e'))
    for k, (n, *_r, ln, m) in enumerate(K2):
        for t in ln:
            x1, y1 = P[n]; x2, y2 = P[t]; b.append(f'<path d="M{x1+100},{y1+200} C{x1+100},{y1+240} {x2+100},{y2-40} {x2+100},{y2}" stroke="#b3541e" stroke-opacity=".5" fill="none" marker-end="url(#o)"/>' if y2 > y1 else f'<line x1="{x1+200}" y1="{y1+100}" x2="{x2}" y2="{y2+100}" stroke="#b3541e" stroke-opacity=".5" marker-end="url(#o)"/>')
    kaydet('80_kalip_dili', '80. Kalıp dili (Alexander): her mana numaralı bir kalıp, kalıplar birbirini çağırır', 'Bağlam → çözüm → sonraki kalıplar. Kalıpların ifadesi bu levha için yazıldı.', b, 900, 650)
F = [talmy, langacker, voronoi, kutugom, mapper, amr, framenet, melcuk, kuale, spark, chernoff, metro, periyodik, zwicky, isinsal, ilksahne, halliday, bilesen, ot, feynman, laban, nota, iskelet, smiles, belirleyici, emoji, takvim, tescir, lull, vucuh, izutsu, heisig, saray, stretch, zoom, cornell, comic, hiper, glif, kalip]
for f in F: f()
print('tamam', len(F))
