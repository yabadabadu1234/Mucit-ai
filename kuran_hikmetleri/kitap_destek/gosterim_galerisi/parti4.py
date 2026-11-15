from ortak import *
from parti2 import DEF
def kel(m): return [KEL[w]['ar'] for w in WORDS_OF.get(m, [])]
def RK(m): return RENK[dal(m)] if m in MANA else m
def wrap(s, n):
    out, cur = [], ''
    for w in s.split():
        if len(cur) + len(w) + 1 > n: out.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    return out + [cur] if cur else out
def kutu(b, x, y, w, h, bas, satir=(), c='#2b2410', ar=None, dolgu='#fff', rx=6, n=None):
    b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{dolgu}" stroke="{c}" stroke-width="1.6"/>')
    if bas: b.append(T(bas, x + w / 2, y + 17, 11, fill=c, w='font-weight="700"'))
    yy = y + (34 if bas else 18)
    for s in satir:
        for l in wrap(s, n or max(10, int(w / 6.2))): b.append(T(l, x + w / 2, yy, 10)); yy += 13
    if ar: b.append(AR(ar, x + w / 2, y + h - 8, 14))
def ok(b, x1, y1, x2, y2, lab='', c='#2b2410', das=False, eg=0):
    mx, my = (x1 + x2) / 2 + eg, (y1 + y2) / 2 - abs(eg) * .3
    b.append(f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" stroke="{c}" stroke-width="1.5" fill="none" {"stroke-dasharray=\'5 3\'" if das else ""} marker-end="url(#o)"/>')
    if lab: b.append(T(lab, mx, my - 3, 9.5, fill='#b3541e', w='stroke="#fffdf6" stroke-width="3" paint-order="stroke"'))
def cizge(ad, bas, alt, N, E, W=900, H=640, bw=150, bh=50, ek=()):
    b = [DEF]
    for a, c, *r in E:
        x1, y1 = N[a][0], N[a][1]; x2, y2 = N[c][0], N[c][1]
        dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1
        k1 = min(bw / 2 / max(abs(dx), 1e-9), bh / 2 / max(abs(dy), 1e-9)) * L
        x1b, y1b = x1 + dx / L * min(k1, L / 2), y1 + dy / L * min(k1, L / 2); x2b, y2b = x2 - dx / L * min(k1, L / 2), y2 - dy / L * min(k1, L / 2)
        ok(b, round(x1b, 1), round(y1b, 1), round(x2b, 1), round(y2b, 1), r[0] if r else '', r[1] if len(r) > 1 else '#2b2410', len(r) > 2 and r[2], r[3] if len(r) > 3 else 0)
    for k, v in N.items():
        x, y, t = v[0], v[1], v[2]; c = v[3] if len(v) > 3 else '#2b2410'; ar = v[4] if len(v) > 4 else None; w = v[5] if len(v) > 5 else bw
        h = bh + (14 if ar else 0)
        kutu(b, x - w / 2, y - h / 2, w, h, None, [t], c, ar, n=int(w / 6.4))
    b += list(ek)
    kaydet(ad, bas, alt, b, W, H)
M = lambda m: KISA[m]
S = []
def usul(f): S.append(f); return f
# 81 Haspelmath semantik harita
@usul
def u81():
    P = {'A': (160, 300), 'D': (330, 220), 'J': (500, 150), 'K': (500, 300), 'U': (660, 300), 'X': (820, 220), 'Y': (820, 380), 'Z': (660, 450), 'L': (680, 90), 'B': (160, 470), 'F': (330, 560), 'G': (160, 600), 'N': (330, 400), 'C': (100, 160), 'H': (250, 120)}
    N = {m: (x, y, M(m), RK(m), (kel(m) or [''])[0]) for m, (x, y) in P.items()}
    E = [(MANA[m]['ebeveyn'][j], m) for m in P for j in range(len(MANA[m]['ebeveyn'])) if MANA[m]['ebeveyn'][j] in P]
    E = [(a, c, '', '#888') for a, c in E] + [('A', 'C', '', '#888'), ('A', 'H', '', '#888'), ('A', 'B', '', '#888')]
    cizge('81_haspelmath', '81. Semantik harita (Haspelmath): bir kelimenin taşıdığı manalar bitişik bölgede durur', 'Kenar = iki mananın aynı kelimede buluşması. Esas, A–B–C–H\'yi birbirine bağlayan merkezdir.', N, E, bw=120)
# 82 ChainNet
@usul
def u82():
    T2 = {'D': 'netice', 'J': 'mecaz-ı mürsel', 'K': 'mecaz-ı mürsel', 'U': 'istiare', 'X': 'genişleme', 'Y': 'istiare', 'Z': 'istiare', 'L': 'istiare', 'N': 'netice', 'F': 'netice', 'G': 'mecaz-ı mürsel', 'C': 'mecaz-ı mürsel', 'H': 'mecaz-ı mürsel', 'A': 'aslî', 'B': 'aslî'}
    P = {'E': (450, 80), 'A': (250, 190), 'B': (650, 190), 'C': (90, 190), 'H': (810, 190), 'D': (250, 300), 'N': (450, 300), 'F': (650, 300), 'G': (810, 300), 'J': (110, 410), 'K': (300, 410), 'L': (480, 410), 'U': (300, 510), 'X': (130, 600), 'Y': (330, 600), 'Z': (530, 600)}
    N = {m: (x, y, M(m), RK(m)) for m, (x, y) in P.items()}
    E = []
    for m in P:
        for p in MANA[m]['ebeveyn']:
            t = T2.get(m, ''); E.append((p, m, t, '#c0392b' if 'istiare' in t else '#2f6fb3' if 'mürsel' in t else '#555', 'istiare' in t))
    cizge('82_chainnet', '82. ChainNet: mana zinciri, her halkanın cinsi yazılı', 'Kırmızı kesik = istiare (benzerlik), mavi = mecaz-ı mürsel (bitişiklik), gri = netice/genişleme.', N, E, H=660, bw=120, bh=36)
# 83 Sözlük maddesi ağacı
@usul
def u83():
    b = []; y = 80
    def yaz(m, no, d):
        nonlocal y
        b.append(T(f'{no}', 40 + d * 34, y, 12, 'start', RK(m), 'font-weight="700"')); b.append(T(MANA[m]['metin'], 80 + d * 34, y, 11.5, 'start'))
        ws = ' · '.join(kel(m)[:4]); b.append(AR(ws, 870, y + 2, 13, 'end')); y += 26
        ch = [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m]
        for k, c in enumerate(ch): yaz(c, f'{no}{"abcdefg"[k] if d % 2 == 0 else ["i","ii","iii","iv"][k]}', d + 1)
    for k, m in enumerate(KIDS['E']): yaz(m, str(k + 1), 0)
    b.append(T('(kök dışı) ' + MANA['R2']['metin'], 40, y + 10, 11, 'start', '#7a7a7a'))
    kaydet('83_sozluk_maddesi', '83. Sözlük maddesi ağacı (Oxford usulü): 1 → 1a → 1a(i) numaralı mana dizini', 'Numara mananın yerini, girinti köke uzaklığı gösterir; sağda kelimeler.', b, 900, y + 30)
# 84 IBIS
@usul
def u84():
    N = {'q': (450, 80, 'SUÂL: خلق kökünün manaları tek esasa döner mi?', '#2f6fb3', None, 360),
         'p1': (220, 220, 'MEVZİ: Evet; esas ölçüp biçerek hazırlamaktır', '#3f8f3a', None, 260), 'p2': (680, 220, 'MEVZİ: Hayır; iki ayrı asıl vardır (takdîr ve imlâs)', '#c26a1e', None, 260),
         'a1': (100, 380, '+ yaratma ölçüden doğar', '#3f8f3a'), 'a2': (290, 380, '+ huy yaradılışın içe vurmasıdır', '#3f8f3a'), 'a3': (100, 500, '− koku manası ölçüyle açıklanmaz', '#c0392b'),
         'b1': (600, 380, '+ İbn Fâris iki asıl sayar', '#3f8f3a'), 'b2': (790, 380, '− düzlemek de bir hazırlamadır', '#c0392b'),
         'q2': (450, 560, 'SUÂL: koku (خَلُوق) nereye bağlanır?', '#2f6fb3', None, 300)}
    E = [('p1', 'q', 'cevap'), ('p2', 'q', 'cevap'), ('a1', 'p1', 'destek'), ('a2', 'p1', 'destek'), ('a3', 'p1', 'itiraz', '#c0392b'), ('b1', 'p2', 'destek'), ('b2', 'p2', 'itiraz', '#c0392b'), ('q2', 'a3', 'doğurur', '#2f6fb3', True)]
    cizge('84_ibis', '84. IBIS mesele haritası (Kunz ve Rittel): suâl → mevzi → lehte/aleyhte', 'Her itiraz yeni bir suâl doğurabilir; tartışma bir ağ olarak büyür.', N, E, bw=170, bh=44)
# 85 Kialo
@usul
def u85():
    b = []
    b.append(f'<rect x="250" y="70" width="400" height="56" rx="8" fill="#2b2410"/>'); b.append(T('TEZ: خلق\'ın bütün manaları "ölçüp biçerek hazırlamak"tan doğar', 450, 103, 11.5, fill='#fff', w='font-weight="700"'))
    L = [('LEHTE', '#3f8f3a', 30, ['Yaratmak, ölçülen şeyin tamamlanmasıdır', 'Huy, yaradılışa ölçülüp verilen hâldir', 'Pay (خَلَاق) iş için ölçülen paydır', 'Lâyık (خَلِيق) ölçüsüne uyan şeydir']),
         ('ALEYHTE', '#c0392b', 470, ['Eskimek (خَلِقَ) ölçüden değil aşınmadan gelir', 'Koku (خَلُوق) hiçbir ölçü bildirmez', 'Kazan (خِلْقِين) Yunancadandır'])]
    for ad, c, x, ls in L:
        b.append(T(ad, x + 200, 160, 13, fill=c, w='font-weight="700"'))
        for k, s in enumerate(ls):
            y = 180 + k * 100; b.append(f'<rect x="{x}" y="{y}" width="400" height="80" rx="6" fill="#fff" stroke="{c}" stroke-width="2" style="border-left:6px"/><rect x="{x}" y="{y}" width="8" height="80" fill="{c}"/>')
            b.append(T(s, x + 210, y + 30, 11))
            if ad == 'ALEYHTE' and k < 2: b.append(T('↳ cevap: ' + ['eskimek düzlemenin neticesidir (B dalı)', 'koku sürmek yüzeyi düzler (B dalı)'][k], x + 210, y + 56, 10, fill='#3f8f3a'))
            if ad == 'ALEYHTE' and k == 2: b.append(T('↳ kabul: kök dışı sayılır', x + 210, y + 56, 10, fill='#7a7a7a'))
    kaydet('85_kialo', '85. Kialo tartışma ağacı: tez, lehte ve aleyhte iki sütun', 'Her itirazın altında cevabı; cevaplanamayan kabul edilir.', b, 900, 600)
# 86 Rationale
@usul
def u86():
    b = [DEF]
    kutu(b, 300, 70, 300, 60, 'İDDİA', ['خلق: ölçüp biçerek hazırlamak esastır'], '#2b2410', dolgu='#f3eedd')
    G = [(60, ['Öncül: ölçmek yapmanın ilk adımıdır', 'Öncül: yaratılan ölçülü olur'], 'GEREKÇE', '#3f8f3a'), (330, ['Öncül: düzlemek de hazırlamaktır', 'Öncül: eskiyen yüzey düzleşir'], 'GEREKÇE', '#3f8f3a'), (600, ['Öncül: koku bir hazırlık bildirmez'], 'İTİRAZ', '#c0392b')]
    for x, ls, ad, c in G:
        b.append(f'<rect x="{x}" y="200" width="240" height="{30+len(ls)*62}" rx="8" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-width="2"/>'); b.append(T(ad + ' (öncüller birlikte)', x + 120, 218, 10.5, fill=c, w='font-weight="700"'))
        for k, s in enumerate(ls): kutu(b, x + 12, 228 + k * 62, 216, 52, None, [s], c)
        b.append(f'<line x1="{x+120}" y1="200" x2="450" y2="132" stroke="{c}" stroke-width="2" marker-end="url(#o)"/>')
    kutu(b, 600, 360, 240, 60, 'İTİRAZA İTİRAZ', ['Koku sürmek yüzeyi düzler: B dalına girer'], '#3f8f3a')
    b.append(f'<line x1="720" y1="360" x2="720" y2="294" stroke="#3f8f3a" stroke-width="2" marker-end="url(#o)"/>')
    b.append(T('Bir gerekçenin öncülleri tek başına değil, ancak birlikte iddiayı taşır (birleşik gerekçe).', 450, 470, 11))
    kaydet('86_rationale', '86. Rationale gerekçe haritası: öncüller birlikte bir gerekçe kutusunda', 'Yeşil = destek, kırmızı = itiraz; itiraza da itiraz edilebilir.', b, 900, 500)
# 87 Kare-i tekabül
@usul
def u87():
    b = []
    C = {'A': (180, 120, 'Her yaratılan ölçülmüştür', 'küllî mûcibe'), 'E': (720, 120, 'Hiçbir yaratılan ölçülmemiştir', 'küllî sâlibe'), 'I': (180, 480, 'Bazı yaratılanlar ölçülmüştür', 'cüz\'î mûcibe'), 'O': (720, 480, 'Bazı yaratılanlar ölçülmemiştir', 'cüz\'î sâlibe')}
    for a, c, l, cc in [('A', 'E', 'tezât (ikisi birden doğru olamaz)', '#c0392b'), ('I', 'O', 'duhûl tahte\'t-tezât (ikisi birden yanlış olamaz)', '#c26a1e'), ('A', 'O', '', '#2b2410'), ('E', 'I', '', '#2b2410'), ('A', 'I', 'tedâhul', '#2f6fb3'), ('E', 'O', 'tedâhul', '#2f6fb3')]:
        x1, y1 = C[a][:2]; x2, y2 = C[c][:2]; b.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cc}" stroke-width="2"/>')
        if l: b.append(T(l, (x1 + x2) / 2, (y1 + y2) / 2 - 8, 10.5, fill=cc, w='font-weight="700" stroke="#fffdf6" stroke-width="3" paint-order="stroke"'))
    b.append(T('tenâkuz (biri doğruysa öteki yanlış)', 450, 290, 11, fill='#2b2410', w='font-weight="700" stroke="#fffdf6" stroke-width="4" paint-order="stroke"'))
    for k, (x, y, s, ad) in C.items():
        b.append(f'<rect x="{x-150}" y="{y-34}" width="300" height="68" rx="8" fill="#fff" stroke="#2b2410" stroke-width="1.6"/>'); b.append(T(f'{k}: {ad}', x, y - 12, 10, fill='#6d6650')); b.append(T(s, x, y + 10, 12, w='font-weight="700"'))
    b.append(T('Kökün iddiası A köşesidir. Kare, bu iddiayı reddeden kimin hangi köşeyi savunması gerektiğini gösterir.', 450, 590, 11))
    kaydet('87_kare_tekabul', '87. Kare-i tekabül (mantıkta karşıtlık karesi): esas iddianın dört hâli', 'Ortaçağ mantık yazmalarındaki dört köşeli şekil.', b, 900, 620)
# 88 Porphyry
@usul
def u88():
    b = [DEF]
    R = [('hazırlamak (cins)', 'ölçerek', 'düzleyerek'), ('ölçerek hazırlamak', 'tamamlanana dek', 'bir işe ayırarak'), ('yaratmak', 'eşyaya', 'nefse'), ('nefse verilen kalıp: huy', 'yerleşmiş', 'taşmış')]
    S2 = [('pay', 'C'), ('yaratılmış, yaradılış', 'J'), ('ahlâk / öfke', 'X')]
    y = 80; x = 450
    for k, (c, f1, f2) in enumerate(R):
        b.append(f'<rect x="{x-130}" y="{y}" width="260" height="40" rx="6" fill="#f3eedd" stroke="#2b2410"/>'); b.append(T(c, x, y + 25, 12, w='font-weight="700"'))
        if k < 3:
            b.append(f'<line x1="{x}" y1="{y+40}" x2="{x}" y2="{y+130}" stroke="#2b2410" stroke-width="2" marker-end="url(#o)"/>'); b.append(T('fasıl: ' + f1, x - 10, y + 80, 10.5, 'end', '#2f6fb3'))
            b.append(f'<line x1="{x+130}" y1="{y+20}" x2="{x+250}" y2="{y+20}" stroke="#2b2410" marker-end="url(#o)"/>'); b.append(T('fasıl: ' + f2, x + 190, y + 12, 10, fill='#c26a1e'))
            b.append(T(['→ düzlemek, eskimek, koku', '→ pay (C), lâyık (H)', '→ yaratılmış, yaradılış'][k], x + 260, y + 25, 11, 'start'))
        y += 130
    b.append(T('fasıl: yerleşmiş → ahlâk   ·   fasıl: taşmış → öfke', x, y - 70, 11, fill='#7a3fb3', w='font-weight="700"'))
    b.append(T('Her basamakta cins ikiye bölünür; bir kol aşağı iner, öteki yana ayrılır.', 450, 600, 11))
    kaydet('88_porphyry', '88. Porphyry ağacı (arbor porphyriana): cins ve fasıl ile ikili bölünme', 'Mantık kitaplarının tarif ağacı: en umumîden en hususîye.', b, 900, 620)
# 89 Kıyas çarkı
@usul
def u89():
    b = []; cx, cy = 450, 350
    for r in (250, 160, 70): b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2b2410" stroke-width="1.5"/>')
    K = [('Ölçülen her şey hazırlanmıştır', 'Yaratılan ölçülmüştür', 'Yaratılan hazırlanmıştır'), ('Yaradılış nefse girerse huy olur', 'Huy yaradılıştan gelir', 'Huy hazırlanmış bir hâldir'),
         ('Düzlenen yüzey aşınır', 'Elbise kullanıldıkça düzlenir', 'Elbise eskir'), ('İşe uyan şey lâyıktır', 'Ölçülen şey işine uyar', 'Ölçülen şey lâyıktır')]
    for k, (b1, k2, n) in enumerate(K):
        a = -math.pi / 4 + k * math.pi / 2; c = ['#2f6fb3', '#7a3fb3', '#3f8f3a', '#a8478f'][k]
        for r, s, w in [(205, 'büyük öncül: ' + b1, ''), (115, 'küçük: ' + k2, ''), (35, '', '')]:
            if s:
                for j, l in enumerate(wrap(s, 22)): b.append(T(l, cx + r * math.cos(a), cy + r * math.sin(a) + j * 12, 9.5, fill=c))
        b.append(T('netice: ' + n, cx + 300 * math.cos(a), cy + 300 * math.sin(a) + (10 if math.sin(a) > 0 else -4), 10.5, fill=c, w='font-weight="700"'))
    b.append(T('ESAS', cx, cy + 4, 12, w='font-weight="700"'))
    b.append(T('Dış halka büyük öncül, orta halka küçük öncül, en dışta netice. Çark döndükçe başka bir kıyas okunur.', 450, 650, 11))
    kaydet('89_kiyas_carki', '89. Kıyas çarkı (ortaçağ mantık yazmaları): her dilim bir kıyas', 'Her mana bir kıyasın neticesi olarak okunur.', b, 900, 670)
# 90 Balık kılçığı
@usul
def u90():
    b = []
    b.append('<line x1="60" y1="330" x2="740" y2="330" stroke="#2b2410" stroke-width="4"/><path d="M740,300 L860,330 L740,360Z" fill="#e8c766" stroke="#2b2410"/>'); b.append(T('خلق ailesi', 795, 335, 12, w='font-weight="700"'))
    K = [('ÖLÇMEK', 'A', ['yaratmak', 'yaratılmış', 'yaradılış', 'uydurmak'], -1, 140), ('İÇ HÂL', 'U', ['huy', 'ahlâk', 'öfke', 'huy takınmak'], -1, 440), ('DÜZLEMEK', 'B', ['eskimek', 'koku sürmek', 'şekli belirmiş'], 1, 140), ('İŞE AYIRMAK', 'C', ['pay', 'yakışmak'], 1, 440)]
    for ad, m, ls, s, x in K:
        y0 = 330 + s * 230; c = RK(m)
        b.append(f'<line x1="{x}" y1="{y0}" x2="{x+200}" y2="330" stroke="{c}" stroke-width="3"/>'); b.append(T(ad, x, y0 + (-8 if s < 0 else 20), 13, fill=c, w='font-weight="700"'))
        for j, l in enumerate(ls):
            t = (j + 1) / (len(ls) + 1); px = x + 200 * t; py = y0 + (330 - y0) * t
            b.append(f'<line x1="{px-90}" y1="{py}" x2="{px}" y2="{py}" stroke="{c}"/>'); b.append(T(l, px - 92, py + 4, 10.5, 'end'))
    kaydet('90_balik_kilcigi', '90. Balık kılçığı (Ishikawa): netice başta, sebepler kılçıkta', 'Her büyük kılçık bir ana sebep, küçük kılçıklar ondan doğanlar.', b, 900, 640)
# 91 Nedensel döngü
@usul
def u91():
    P = {'K': (200, 200), 'U': (450, 120), 'X': (700, 200), 'Z': (700, 440), 'Y': (450, 520), 'D': (200, 440)}
    N = {m: (x, y, M(m), RK(m), (kel(m) or [''])[0]) for m, (x, y) in P.items()}
    E = [('K', 'U', '+ yerleşir'), ('U', 'X', '+ çoğalır'), ('X', 'Z', '+ örnek olur'), ('Z', 'U', '+ yeni huy', '#7a3fb3', False, 60), ('U', 'Y', '+ taşar', '#c0392b'), ('Y', 'X', '− bozar', '#c0392b', True, -40), ('D', 'K', '+ kalıp verir')]
    ek = [T('D', 450, 330, 26, fill='#2f6fb3', w='font-weight="700"'), T('(pekiştiren döngü)', 450, 352, 10, fill='#2f6fb3')]
    cizge('91_nedensel_dongu', '91. Nedensel döngü diyagramı: huy, ahlâk ve huy takınma birbirini besler', '+ aynı yönde değişir, − ters yönde. D = pekiştiren döngü.', N, E, ek=ek, bw=130)
# 92 Etki diyagramı
@usul
def u92():
    N = {'k': (130, 150, 'KARAR: hangi manayı seçeyim?', '#2f6fb3', None, 200), 'b': (130, 420, 'belirsizlik: fâil kim?', '#c26a1e', None, 180), 'c': (420, 420, 'belirsizlik: nesne eşya mı insan mı?', '#c26a1e', None, 200),
         'z': (700, 420, 'belirsizlik: zaman geçti mi?', '#c26a1e', None, 180), 'd': (560, 150, 'DEĞER: doğru mana', '#3f8f3a', None, 200)}
    E = [('b', 'k', 'bilgi'), ('c', 'k', 'bilgi'), ('z', 'k', 'bilgi'), ('k', 'd'), ('c', 'd'), ('z', 'd')]
    ek = [T('fâil Allah → yaratmak · nesne nefs → huy · zaman geçti ve nesne elbise → eskimek', 450, 560, 11)]
    cizge('92_etki_diyagrami', '92. Etki diyagramı: mana seçimi bir karar, bağlam bilgileri belirsizlik düğümleri', 'Dikdörtgen = karar, oval yerine turuncu = belirsizlik, yeşil = değer.', N, E, ek=ek)
# 93 Minto piramidi
@usul
def u93():
    b = [DEF]
    kutu(b, 300, 70, 300, 56, 'ANA FİKİR', ['خلق: bir şeyi bir maksada göre ölçüp hazırlamak'], '#b8860b', dolgu='#f3eedd')
    A = [('Ölçmek yaratır', 'A', ['ölçülen tamamlanınca yaratılır', 'yaratılanın kalıbı yaradılıştır', 'kalıp nefse girince huydur']), ('Düzlemek aşındırır', 'B', ['düzlenen yüzey kayar', 'kullanılan eşya eskir', 'sürülen koku yüzeyi düzler']), ('Ayırmak yakıştırır', 'C', ['işe ayrılan paydır', 'işe uyan lâyıktır'])]
    for k, (ad, m, ls) in enumerate(A):
        x = 40 + k * 285; kutu(b, x, 200, 250, 46, ad, [], RK(m)); b.append(f'<line x1="{x+125}" y1="200" x2="450" y2="128" stroke="#2b2410" marker-end="url(#o)"/>')
        for j, s in enumerate(ls): kutu(b, x + 15, 290 + j * 70, 220, 52, None, [s], RK(m)); b.append(f'<line x1="{x+125}" y1="{290+j*70}" x2="{x+125}" y2="{246 if j==0 else 290+j*70-18}" stroke="#bbb"/>')
    b.append(T('Yukarıdaki her cümle aşağıdakileri özetler; aşağıdakiler yukarıdakini ispat eder (Minto, "Piramit Prensibi").', 450, 560, 11))
    kaydet('93_minto', '93. Minto piramidi: önce hüküm, altında gerekçeleri, onların altında delilleri', 'Okuyan istediği katta durabilir.', b, 900, 590)
# 94 Mantık modeli
@usul
def u94():
    b = [DEF]
    C = [('GİRDİ', ['ham madde (deri, toprak)', 'ölçü aleti', 'yapan']), ('FAALİYET', ['ölçmek', 'biçmek', 'düzlemek']), ('ÇIKTI', ['yaratılmış (مَخْلُوق)', 'şekli belirmiş (مُخَلَّق)', 'düz yüzey (خَلْقَاء)']),
         ('NETİCE', ['yaradılış, kalıp (خِلْقَة)', 'işe yakışma (خَلِيق)', 'pay (خَلَاق)']), ('UZUN VADE', ['huy (خُلُق)', 'ahlâk (أَخْلَاق)', 'eskime (خَلِقَ)'])]
    for k, (ad, ls) in enumerate(C):
        x = 20 + k * 176; b.append(f'<rect x="{x}" y="90" width="160" height="320" rx="8" fill="#fff" stroke="#2b2410" stroke-width="1.6"/><rect x="{x}" y="90" width="160" height="34" rx="8" fill="#2b2410"/>'); b.append(T(ad, x + 80, 112, 12, fill='#fff', w='font-weight="700"'))
        for j, s in enumerate(ls):
            for i, l in enumerate(wrap(s, 22)): b.append(T(l, x + 80, 160 + j * 80 + i * 14, 10.5))
        if k < 4: b.append(f'<line x1="{x+160}" y1="250" x2="{x+176}" y2="250" stroke="#2b2410" stroke-width="2" marker-end="url(#o)"/>')
    b.append(T('Usul: soldan sağa bir işin girdisinden uzun vadeli neticesine. Kökün manaları bu işin safhalarıdır.', 450, 450, 11))
    kaydet('94_mantik_modeli', '94. Mantık modeli: girdi → faaliyet → çıktı → netice → uzun vade', 'Her safhanın altında o safhada doğan manalar.', b, 900, 480)
# 95 Kulvar
@usul
def u95():
    b = [DEF]; L = [('YAPAN', '#2f6fb3'), ('MADDE / EŞYA', '#3f8f3a'), ('İNSANIN İÇİ', '#7a3fb3'), ('ZAMAN', '#7a7a7a')]
    for k, (ad, c) in enumerate(L): b.append(f'<rect x="20" y="{70+k*130}" width="860" height="126" fill="{c}" fill-opacity=".06" stroke="{c}"/>'); b.append(f'<text transform="translate(40,{70+k*130+90}) rotate(-90)" font-size="11" font-weight="700" fill="{c}">{ad}</text>')
    A = [(0, 140, 'ölçer, biçer', 'خَلَقَ'), (1, 290, 'şekli belirir', 'مُخَلَّق'), (0, 430, 'tamamlar: yaratır', 'خَالِق'), (1, 570, 'yaratılmış olur', 'مَخْلُوق'), (2, 570, 'yaradılışa bürünür', 'خِلْقَة'), (2, 720, 'huy olur', 'خُلُق'), (3, 430, 'zaman geçer', ''), (1, 720, 'eskir', 'خَلِقَ')]
    for i, (l, x, t, a) in enumerate(A):
        y = 70 + l * 130 + 30; kutu(b, x - 60, y, 120, 66, None, [t], L[l][1], a)
    for i, j in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (6, 7), (3, 7)]:
        (l1, x1, *_), (l2, x2, *_) = A[i], A[j]; ok(b, x1 + 60 if x2 > x1 else x1, 70 + l1 * 130 + 63 + (33 if l2 > l1 else 0), x2 - 60 if x2 > x1 else x2, 70 + l2 * 130 + 63 - (33 if l2 > l1 else 0))
    kaydet('95_kulvar', '95. Kulvar şeması: her kulvar bir fâil, iş kulvarlar arasında akar', 'Hangi mananın kimin elinde doğduğu kulvarından okunur.', b, 900, 610)
# 96 Çiçek ızgarası
@usul
def u96():
    b = []; cx, cy = 450, 350
    P = [('TARİF', ['ölçüp biçerek bir maksada göre hazırlamak']), ('ÇEKİRDEK KELİME', ['خَلَقَ']), ('EŞ MANALI', ['فَطَرَ  بَرَأَ  قَدَّرَ']), ('ZIDDI', ['بَعْثَرَ (dağıtmak), أَفْسَدَ (bozmak)']),
         ('AİLESİ', ['خَالِق  مَخْلُوق  خُلُق  أَخْلَاق']), ('MİSAL CÜMLE', ['خَلَقَ السَّمَاوَاتِ وَالْأَرْضَ']), ('İNCELİK', ['yokluktan değil, ölçüyle düzen vermek vurgulanır']), ('YANLIŞ ANLAMA', ['خَلْق ile خُلُق karıştırılır: yaratma ↔ huy'])]
    for k, (ad, ls) in enumerate(P):
        a = -math.pi / 2 + k * 2 * math.pi / len(P); x, y = cx + 300 * math.cos(a), cy + 245 * math.sin(a)
        b.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="112" ry="50" fill="#e8c766" fill-opacity="{.15+.05*(k%2)}" stroke="#b8860b"/>'); b.append(T(ad, x, y - 22, 11, fill='#8a5a00', w='font-weight="700"'))
        s = ls[0]
        if any('؀' <= ch <= 'ۿ' for ch in s) and ad != 'YANLIŞ ANLAMA' and ad != 'ZIDDI': b.append(AR(s, x, y + 10, 15))
        else:
            for j, l in enumerate(wrap(s, 26)): b.append(T(l, x, y + 2 + j * 13, 10))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="70" fill="#fff" stroke="#b8860b" stroke-width="3"/>'); b.append(AR('خ ل ق', cx, cy + 9, 26))
    kaydet('96_cicek_izgarasi', '96. Çiçek ızgarası: kelimenin etrafında sabit sekiz yaprak', 'Her yaprağın sorusu her kelimede aynıdır; okuyan neyi nerede bulacağını bilir.', b, 900, 680)
# 97 Frayer
@usul
def u97():
    b = []
    Q = [('TARİF', ['Bir şeyi bir maksada göre ölçüp biçerek', 'hazırlamak; buradan yaratmak doğar.']), ('VASIFLARI', ['• bir ölçü vardır', '• bir maksat vardır', '• bir yapan vardır', '• netice bir şekildir']),
         ('MİSALLER', ['terzinin deriyi ölçüp biçmesi', 'Allah\'ın gökleri yaratması', 'insanın huyu (içe verilen kalıp)']), ('MİSAL OLMAYANLAR', ['rastgele dağıtmak', 'yıkmak, bozmak', 'sözü uydurmak (sahte yaratma)'])]
    for k, (ad, ls) in enumerate(Q):
        x = 40 + (k % 2) * 420; y = 80 + (k // 2) * 270
        b.append(f'<rect x="{x}" y="{y}" width="400" height="250" fill="#fff" stroke="#2b2410" stroke-width="1.6"/>'); b.append(T(ad, x + 200, y + 26, 13, fill='#b3541e', w='font-weight="700"'))
        for j, s in enumerate(ls): b.append(T(s, x + 200, y + 70 + j * 24, 12))
    b.append(f'<ellipse cx="440" cy="340" rx="110" ry="46" fill="#e8c766" stroke="#2b2410" stroke-width="2"/>'); b.append(AR('خَلَقَ', 440, 350, 26))
    kaydet('97_frayer', '97. Frayer modeli: tarif, vasıflar, misaller, misal olmayanlar', 'Misal olmayanlar sınırı çizer; kavram ancak hududuyla öğrenilir.', b, 900, 640)
# 98 Çift kabarcık
@usul
def u98():
    b = []
    L, R = (250, 330), (650, 330)
    for (x, y), ar, tr in [(L, 'خَلَقَ', 'yarattı'), (R, 'خَلِقَ', 'eskidi')]: b.append(f'<circle cx="{x}" cy="{y}" r="64" fill="#e8c766" stroke="#2b2410" stroke-width="2"/>'); b.append(AR(ar, x, y + 4, 26)); b.append(T(tr, x, y + 30, 11))
    O = ['aynı üç harf', 'yüzeyle ilgili', 'işin neticesi', 'ölçü/düzlük esası']
    for k, s in enumerate(O):
        y = 150 + k * 120; b.append(f'<line x1="{L[0]}" y1="{L[1]}" x2="450" y2="{y}" stroke="#999"/><line x1="{R[0]}" y1="{R[1]}" x2="450" y2="{y}" stroke="#999"/>')
        b.append(f'<ellipse cx="450" cy="{y}" rx="80" ry="26" fill="#fff" stroke="#2b2410"/>'); b.append(T(s, 450, y + 4, 10.5))
    for k, s in enumerate(['fâili bir yapan', 'yokluktan varlığa', 'fethalı (فَعَلَ)']):
        y = 170 + k * 130; b.append(f'<line x1="{L[0]}" y1="{L[1]}" x2="80" y2="{y}" stroke="#999"/><ellipse cx="80" cy="{y}" rx="70" ry="24" fill="#fff" stroke="#2f6fb3"/>'); b.append(T(s, 80, y + 4, 10))
    for k, s in enumerate(['fâili zaman', 'varlıktan aşınmaya', 'esreli (فَعِلَ)']):
        y = 170 + k * 130; b.append(f'<line x1="{R[0]}" y1="{R[1]}" x2="820" y2="{y}" stroke="#999"/><ellipse cx="820" cy="{y}" rx="70" ry="24" fill="#fff" stroke="#3f8f3a"/>'); b.append(T(s, 820, y + 4, 10))
    kaydet('98_cift_kabarcik', '98. Çift kabarcık haritası: iki kelimenin ortağı ortada, farkı kenarda', 'Bir harekenin değişmesiyle zıt yöne giden iki mana.', b, 900, 640)
# 99 T-cetveli
@usul
def u99():
    b = []
    b.append('<line x1="450" y1="80" x2="450" y2="600" stroke="#2b2410" stroke-width="3"/><line x1="40" y1="120" x2="860" y2="120" stroke="#2b2410" stroke-width="3"/>')
    b.append(T('خَلْق  (fethalı): DIŞTAKİ ŞEKİL', 245, 108, 13, fill='#2f6fb3', w='font-weight="700"')); b.append(T('خُلُق  (ötreli): İÇTEKİ ŞEKİL', 655, 108, 13, fill='#7a3fb3', w='font-weight="700"'))
    R = [('göze görünen suret', 'göze görünmeyen huy'), ('bedenin yaradılışı', 'nefsin yaradılışı'), ('ölçü dışta belli', 'ölçü davranışta belli'), ('güzelliği: hüsn-i halk', 'güzelliği: hüsn-i hulk'), ('çoğulu: خَلَائِق', 'çoğulu: أَخْلَاق'), ('ilmi: anatomi, tabiat', 'ilmi: ahlâk')]
    for k, (l, r) in enumerate(R): b.append(T(l, 245, 160 + k * 60, 12.5)); b.append(T(r, 655, 160 + k * 60, 12.5))
    kaydet('99_t_cetveli', '99. T-cetveli: yan yana iki şeyin karşılıklı vasıfları', 'Aynı satırdaki iki hücre birbirinin karşılığıdır.', b, 900, 620)
# 100 KWL
@usul
def u100():
    b = []
    C = [('BİLİYORUM', '#2f6fb3', ['خلق = yaratmak', 'خالق = yaratan', 'ahlâk kelimesi Türkçede var']), ('MERAK EDİYORUM', '#c26a1e', ['ahlâk neden yaratmakla aynı kökten?', 'eskimek bu köke nasıl girdi?', 'koku neden buradan?']),
         ('ÖĞRENDİM', '#3f8f3a', ['esas: ölçüp biçerek hazırlamak', 'huy = nefse ölçülüp verilen kalıp', 'eskimek = düzlenen yüzeyin aşınması', 'koku = yüzeyi düzleyen sürme'])]
    for k, (ad, c, ls) in enumerate(C):
        x = 30 + k * 290; b.append(f'<rect x="{x}" y="80" width="270" height="480" rx="8" fill="#fff" stroke="{c}" stroke-width="2"/><rect x="{x}" y="80" width="270" height="40" rx="8" fill="{c}"/>'); b.append(T(ad, x + 135, 106, 13, fill='#fff', w='font-weight="700"'))
        for j, s in enumerate(ls):
            for i, l in enumerate(wrap(s, 36)): b.append(T(l, x + 15, 160 + j * 60 + i * 15, 11, 'start'))
    kaydet('100_kwl', '100. KWL cetveli: bildiğim, merak ettiğim, öğrendiğim', 'Okuyan önce kendi bilgisini yazar; öğrendiği, merakının cevabı olarak yerleşir.', b, 900, 590)
# 101 Zaman şeridi (türeme sırası)
@usul
def u101():
    b = []; y0 = 330
    b.append(f'<line x1="40" y1="{y0}" x2="870" y2="{y0}" stroke="#2b2410" stroke-width="3"/>')
    A = ['E', 'A', 'B', 'C', 'H', 'D', 'N', 'F', 'G', 'J', 'K', 'L', 'U', 'X', 'Y', 'Z']
    for k, m in enumerate(A):
        x = 60 + k * 52; s = -1 if k % 2 else 1; c = RK(m)
        b.append(f'<circle cx="{x}" cy="{y0}" r="7" fill="{c}"/><line x1="{x}" y1="{y0}" x2="{x}" y2="{y0+s*(60+depth(m)*30)}" stroke="{c}"/>')
        yy = y0 + s * (70 + depth(m) * 30); b.append(T(M(m), x, yy + (12 if s > 0 else -4), 10, fill=c, w='font-weight="700"')); b.append(AR((kel(m) or [''])[0], x, yy + (28 if s > 0 else -18), 12))
    b.append(T('soldan sağa: mantıkî türeme sırası (tarihî sıra iddia edilmez)', 450, 620, 11))
    kaydet('101_zaman_seridi', '101. Zaman şeridi: manalar türeme sırasıyla bir çizgi üzerinde', 'Çubuğun boyu köke uzaklık.', b, 900, 640)
# 102 Çember haritası
@usul
def u102():
    b = []; cx, cy = 450, 350
    b.append(f'<rect x="40" y="70" width="820" height="560" rx="14" fill="#f3eedd" stroke="#2b2410" stroke-width="2"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="230" fill="#fff" stroke="#2b2410" stroke-width="2"/><circle cx="{cx}" cy="{cy}" r="70" fill="#e8c766" stroke="#2b2410" stroke-width="2"/>'); b.append(AR('خلق', cx, cy + 8, 30))
    I = ['ölçüp biçmek', 'yaratmak', 'yaradılış', 'huy', 'ahlâk', 'düz yüzey', 'eskimek', 'pay', 'lâyık', 'uydurmak', 'koku']
    for k, s in enumerate(I): a = 2 * math.pi * k / len(I); b.append(T(s, cx + 150 * math.cos(a), cy + 150 * math.sin(a) + 4, 11.5))
    F = ['Kaynak: İbn Fâris, Mekâyîs', 'Kaynak: Lisânü\'l-Arab', 'Bağlam: terzilik, marangozluk', 'Bağlam: Kur\'ân\'da 261 yer']
    for k, s in enumerate(F): b.append(T(s, [120, 780, 120, 780][k], [110, 110, 610, 610][k], 10.5, ['start', 'end', 'start', 'end'][k], '#6d6650'))
    kaydet('102_cember_haritasi', '102. Çember haritası (Thinking Maps): içte bildiklerimiz, dış çerçevede nereden bildiğimiz', 'Ortadaki kelime, iç çember mana, dış çerçeve kaynak ve bağlam.', b, 900, 650)
# 103 Köprü haritası
@usul
def u103():
    b = []
    P = [('ölçülen deri', 'elbise'), ('yaradılış', 'huy'), ('elbise', 'eskimek'), ('olmayan şey', 'uydurmak'), ('işe ayrılan', 'pay')]
    R = ['ölçülüp biçilince olur', 'nefse girince olur', 'zamanla olur', 'söze girince olur', 'ölçülünce olur']
    x = 40
    for k, ((a, c), r) in enumerate(zip(P, R)):
        b.append(T(a, x + 75, 290, 12, w='font-weight="700"')); b.append(f'<line x1="{x}" y1="300" x2="{x+150}" y2="300" stroke="#2b2410" stroke-width="2"/>'); b.append(T(c, x + 75, 325, 12, w='font-weight="700"'))
        b.append(f'<line x1="{x+75}" y1="304" x2="{x+75}" y2="308" stroke="#2b2410"/>')
        if k < 4: b.append(f'<path d="M{x+150},300 L{x+170},250 L{x+190},300" stroke="#b3541e" stroke-width="2" fill="none"/>'); b.append(T('gibi', x + 170, 240, 10, fill='#b3541e'))
        x += 170
    b.append(T('İlişki: "üstteki, ' + ' / '.join(R[:2]) + ' … alttakini doğurur"', 450, 400, 11))
    b.append(T('Köprü ilişkisi: üstteki şey bir işlemden geçince alttaki olur. Her ayakta işlem aynıdır: ölçüyle şekil alma.', 450, 430, 11))
    kaydet('103_kopru', '103. Köprü haritası (benzetme): aynı ilişki bütün çiftlerde', 'Bir çifti anlayan ötekileri ilişkinin aynılığıyla anlar.', b, 900, 470)
# 104 Parça-bütün parantezi
@usul
def u104():
    b = []
    def br(x, y1, y2): b.append(f'<path d="M{x+16},{y1} Q{x},{y1} {x},{(y1+y2)/2-10} L{x-10},{(y1+y2)/2} L{x},{(y1+y2)/2+10} Q{x},{y2} {x+16},{y2}" stroke="#2b2410" stroke-width="2" fill="none"/>')
    b.append(AR('خَلَقَ', 80, 350, 28)); b.append(T('kelime', 80, 375, 10)); br(140, 120, 580)
    P = [('ف (fâ): خ', ['boğazdan çıkan sert ses', 'kesme, yarma çağrışımı']), ('ع (ayn): ل', ['dil ucu, yumuşak geçiş', 'uzanma, düzlük']), ('ل (lâm): ق', ['dilkökünden derin ses', 'sağlamlık, sabitlik']), ('vezin: فَعَلَ', ['fiil, geçişli', 'bir defalık iş'])]
    for k, (ad, ls) in enumerate(P):
        y = 130 + k * 115; b.append(T(ad, 170, y + 30, 13, 'start', w='font-weight="700"')); br(330, y, y + 70)
        for j, s in enumerate(ls): b.append(T(s, 360, y + 22 + j * 30, 11.5, 'start'))
    b.append(T('Harf manaları çağrışımdır, kesin hüküm değildir (iştikâk-ı ekber tartışması).', 450, 610, 10.5, fill='#6d6650'))
    kaydet('104_parca_butun', '104. Parça–bütün parantezi (brace map): kelime, harfleri ve vezni', 'Sol bütün, sağ parçaları; her parantez bir alt bölme.', b, 900, 630)
# 105 Çok akışlı harita
@usul
def u105():
    b = [DEF]
    kutu(b, 350, 280, 200, 70, 'ÖLÇÜP BİÇMEK', [], '#b8860b', 'خَلَقَ', '#f3eedd')
    for k, s in enumerate(['bir maksat var', 'ham madde var', 'yapanın bilgisi var', 'ölçü aleti var']): kutu(b, 40, 120 + k * 110, 200, 50, None, [s], '#2b2410'); ok(b, 240, 145 + k * 110, 350, 315)
    for k, (s, m) in enumerate([('yaratılmış bir şey', 'J'), ('o şeyin kalıbı', 'K'), ('içe verilen huy', 'U'), ('işe yakışma', 'H'), ('pay', 'C')]):
        kutu(b, 660, 90 + k * 100, 200, 56, None, [s], RK(m), (kel(m) or [''])[0]); ok(b, 550, 315, 660, 118 + k * 100)
    b.append(T('SEBEPLER', 140, 95, 12, w='font-weight="700"')); b.append(T('NETİCELER', 760, 75, 12, w='font-weight="700"'))
    kaydet('105_cok_akisli', '105. Çok akışlı harita: solda sebepler, ortada iş, sağda neticeler', 'Bir işin bütün sebepleri ve bütün neticeleri tek bakışta.', b, 900, 600)
# 106 Değişmeli diyagram
@usul
def u106():
    N = {'E': (150, 120, 'hazırlamak', '#b8860b'), 'A': (450, 120, 'ölçüp biçmek', RK('A')), 'B': (150, 400, 'düzlemek', RK('B')), 'N': (450, 400, 'şekli belirmiş', RK('N'), 'مُخَلَّق'), 'D': (750, 120, 'yaratmak', RK('D')), 'J': (750, 400, 'yaratılmış', RK('J'), 'مَخْلُوق')}
    E = [('E', 'A', 'ölçerek'), ('E', 'B', 'düzleyerek'), ('A', 'N', 'yüzey verilir'), ('B', 'N', 'ölçü verilir'), ('A', 'D', 'tamamlanır'), ('D', 'J', 'neticesi'), ('N', 'J', 'eser olur')]
    ek = [T('↻', 300, 270, 34, fill='#b3541e'), T('↻', 600, 270, 34, fill='#b3541e'), T('Her kare değişmelidir: iki yoldan gidilen yer aynıdır.', 450, 520, 11), T('Önce ölçüp sonra düzlemek ile önce düzleyip sonra ölçmek aynı neticeyi (şekli belirmiş) verir.', 450, 540, 11)]
    cizge('106_degismeli', '106. Değişmeli diyagram (kategori teorisi): iki yol aynı yere varır', 'Okun adı işlemdir; ↻ işaretli kare "hangi yoldan gidersen git" demektir.', N, E, H=570, ek=ek)
# 107 Soru ağacı
@usul
def u107():
    N = {'q': (450, 80, 'Bu yerde خلق ne demek?', '#2b2410', None, 220), 'a': (190, 210, 'Nesne bir eşya mı?', '#2b2410', None, 180), 'b': (710, 210, 'Nesne bir insan mı?', '#2b2410', None, 180),
         'a1': (80, 360, 'Yeni mi yapıldı?', '#2f6fb3', None, 150), 'a2': (300, 360, 'Kullanıldı mı?', '#3f8f3a', None, 150), 'b1': (600, 360, 'Dış şekli mi?', '#2f6fb3', None, 150), 'b2': (820, 360, 'İç hâli mi?', '#7a3fb3', None, 150),
         'r1': (80, 500, 'yaratmak', RK('D'), 'خَلَقَ', 140), 'r2': (300, 500, 'eskimek', RK('F'), 'خَلِقَ', 140), 'r3': (600, 500, 'yaradılış', RK('K'), 'خِلْقَة', 140), 'r4': (820, 500, 'huy', RK('U'), 'خُلُق', 140)}
    E = [('q', 'a'), ('q', 'b'), ('a', 'a1'), ('a', 'a2'), ('b', 'b1'), ('b', 'b2'), ('a1', 'r1', 'evet'), ('a2', 'r2', 'evet'), ('b1', 'r3', 'evet'), ('b2', 'r4', 'evet')]
    cizge('107_soru_agaci', '107. Soru ağacı (birbirini dışlayan, hepsini kaplayan kollar)', 'Her düğüm bir sorudur; kollar örtüşmez ve boşluk bırakmaz.', N, E, H=600)
# 108 Karar ağacı
@usul
def u108():
    b = [DEF]
    R = [('Kelimenin harekesi nedir?', [('خَلَقَ', 'fetha'), ('خَلِقَ', 'esre'), ('خَلُقَ', 'ötre')]), ]
    kutu(b, 330, 70, 240, 40, None, ['Fiilin ortasındaki hareke?'], '#2b2410')
    O = [(150, 'fetha: خَلَقَ', ['Mef\'ûlü var mı?'], [('var', 'yarattı / ölçtü'), ('ifti\'âl babında', 'uydurdu')]), (450, 'esre: خَلِقَ', ['fâil elbise mi?'], [('evet', 'eskidi')]), (750, 'ötre: خَلُقَ', ['fâil kimse mi?'], [('evet', 'yaraştı, lâyık oldu')])]
    for x, ad, q, ls in O:
        ok(b, 450, 110, x, 170); kutu(b, x - 110, 170, 220, 64, ad, q, '#2f6fb3')
        for j, (k, s) in enumerate(ls): ok(b, x, 234, x - 70 + j * 140, 330, k); kutu(b, x - 130 + j * 140, 330, 120, 50, None, [s], '#3f8f3a')
    b.append(T('Okuyan, kelimeyi gördüğünde ağacı yukarıdan aşağı izler ve tek bir yaprağa varır.', 450, 450, 11))
    kaydet('108_karar_agaci', '108. Karar ağacı: bir kelimenin manasını sorulara cevap vererek bulmak', 'Hareke ve fâile göre dallanır.', b, 900, 480)
# 109 Akış şeması
@usul
def u109():
    b = [DEF]
    def adim(x, y, s, sekil='k', c='#2b2410'):
        if sekil == 'e': b.append(f'<path d="M{x},{y-30} L{x+110},{y} L{x},{y+30} L{x-110},{y}Z" fill="#fff" stroke="{c}" stroke-width="1.6"/>')
        elif sekil == 'o': b.append(f'<rect x="{x-100}" y="{y-20}" width="200" height="40" rx="20" fill="#e8c766" stroke="{c}"/>')
        else: b.append(f'<rect x="{x-110}" y="{y-22}" width="220" height="44" fill="#fff" stroke="{c}" stroke-width="1.6"/>')
        b.append(T(s, x, y + 4, 10.5))
    adim(300, 90, 'BAŞLA: kelimeyi oku', 'o'); adim(300, 180, 'kökü bul: خ ل ق'); adim(300, 280, 'vezni bilinen mi?', 'e'); adim(300, 380, 'vezin manasını al (fâil, mef\'ûl…)'); adim(300, 470, 'bağlamda fâil/nesne kim?', 'e'); adim(300, 570, 'BİT: manayı yaz', 'o')
    adim(650, 280, 'harekeye bak (karar ağacı)'); adim(650, 470, 'esasa dön: ölçüp biçmek')
    for a, c in [(112, 158), (202, 250), (310, 358), (402, 440), (500, 548)]: ok(b, 300, a, 300, c)
    ok(b, 410, 280, 540, 280, 'hayır'); ok(b, 650, 302, 410, 375); ok(b, 410, 470, 540, 470, 'belirsiz'); ok(b, 650, 492, 400, 565)
    kaydet('109_akis_semasi', '109. Akış şeması: bir kelimenin manasını bulma usulü adım adım', 'Baklava = soru, dikdörtgen = iş, oval = baş ve son.', b, 900, 610)
# 110 Durum makinesi
@usul
def u110():
    N = {'h': (120, 300, 'HAM MADDE', '#7a7a7a'), 'o': (330, 160, 'ÖLÇÜLMÜŞ', RK('A'), 'مَخْلُوق?'.replace('?', '')[:0] or None), 'd': (330, 440, 'DÜZLENMİŞ', RK('B'), 'خَلْقَاء'), 's': (540, 300, 'ŞEKLİ BELİRMİŞ', RK('N'), 'مُخَلَّق'),
         'y': (740, 160, 'YARATILMIŞ', RK('J'), 'مَخْلُوق'), 'e': (740, 440, 'ESKİMİŞ', RK('F'), 'خَلَق'), 'u': (540, 570, 'UYGUN (LÂYIK)', RK('H'), 'خَلِيق')}
    E = [('h', 'o', 'ölçmek'), ('h', 'd', 'düzlemek'), ('o', 's', 'düzlemek'), ('d', 's', 'ölçmek'), ('s', 'y', 'tamamlamak'), ('y', 'e', 'zaman'), ('d', 'e', 'aşınmak', '#3f8f3a', False, 80), ('s', 'u', 'işe koymak')]
    cizge('110_durum_makinesi', '110. Durum makinesi: madde hangi işle hangi hâle geçer', 'Kutu = hâl (ve o hâlin kelimesi), ok = hâli değiştiren iş.', N, E, H=640, bw=150)
# 111 Ontoloji
@usul
def u111():
    N = {'f': (450, 80, 'Sınıf: Fiil (iş)', '#2b2410'), 'o': (220, 210, 'Sınıf: Ölçmek', RK('A')), 'd': (680, 210, 'Sınıf: Düzlemek', RK('B')), 'y': (100, 360, 'Sınıf: Yaratmak', RK('D')), 'u': (330, 360, 'Sınıf: Uydurmak', RK('L')),
         'e': (680, 360, 'Sınıf: Eskimek', RK('F')), 'n': (220, 510, 'Sınıf: Nefs', '#7a3fb3'), 'h': (470, 510, 'Sınıf: Huy', RK('U')), 'x': (720, 510, 'Sınıf: Elbise', '#7a7a7a')}
    E = [('o', 'f', 'alt sınıf'), ('d', 'f', 'alt sınıf'), ('y', 'o', 'alt sınıf'), ('u', 'y', 'benzer (sahte)', '#c0392b', True), ('e', 'd', 'alt sınıf'), ('h', 'n', 'özellik: sahibi'), ('h', 'y', 'netice', '#2f6fb3', True), ('e', 'x', 'özellik: nesnesi')]
    cizge('111_ontoloji', '111. Ontoloji çizgesi: sınıflar, alt sınıflar ve özellikler', 'Düz ok = "bir türüdür", kesik ok = diğer münasebetler (adıyla).', N, E, H=580)
# 112 Quillian
@usul
def u112():
    b = [DEF]
    L = [('HAZIRLAMAK', 450, 90, ['maksadı vardır', 'yapanı vardır']), ('ÖLÇMEK', 250, 240, ['ölçüsü vardır']), ('DÜZLEMEK', 650, 240, ['yüzeyi vardır']), ('YARATMAK', 150, 390, ['eseri vardır']), ('HUY', 440, 390, ['nefiste durur']), ('ESKİMEK', 650, 390, ['zaman ister'])]
    P = {}
    for ad, x, y, ls in L:
        P[ad] = (x, y); b.append(f'<ellipse cx="{x}" cy="{y}" rx="80" ry="26" fill="#f3eedd" stroke="#2b2410" stroke-width="1.6"/>'); b.append(T(ad, x, y + 4, 11.5, w='font-weight="700"'))
        for j, s in enumerate(ls): b.append(f'<line x1="{x+80}" y1="{y}" x2="{x+110}" y2="{y-20+j*20}" stroke="#999"/>'); b.append(T(s, x + 114, y - 16 + j * 20, 10, 'start', '#6d6650'))
    for a, c in [('ÖLÇMEK', 'HAZIRLAMAK'), ('DÜZLEMEK', 'HAZIRLAMAK'), ('YARATMAK', 'ÖLÇMEK'), ('HUY', 'YARATMAK'), ('ESKİMEK', 'DÜZLEMEK')]:
        ok(b, P[a][0], P[a][1] - 26, P[c][0], P[c][1] + 26, 'bir türüdür')
    b.append(T('Özellik bir kere yukarıda yazılır, aşağıdakiler onu miras alır: "huy"un maksadı ve ölçüsü de vardır.', 450, 520, 11))
    kaydet('112_quillian', '112. Quillian anlam ağı: "bir türüdür" bağları ve miras alınan özellikler', 'Her özellik en umumî yerinde bir kere yazılır.', b, 900, 550)
# 113 Konu haritası
@usul
def u113():
    N = {'t1': (200, 150, 'KONU: yaratmak', RK('D')), 't2': (700, 150, 'KONU: huy', RK('U')), 't3': (450, 330, 'KONU: Allah', '#b8860b'), 't4': (200, 480, 'KONU: elbise', '#7a7a7a'), 't5': (700, 480, 'KONU: ahlâk ilmi', RK('X')),
         'o1': (60, 290, 'geçtiği yer: En\'âm 6:1', '#999', None, 140), 'o2': (840, 290, 'geçtiği yer: Kalem 68:4', '#999', None, 140)}
    E = [('t3', 't1', 'yapan (fâil)'), ('t1', 't2', 'yaradılışla huy verir'), ('t2', 't5', 'ilmi'), ('t4', 't1', 'eskime (zıt yön)', '#3f8f3a', True), ('t1', 'o1', 'geçiş', '#999', True), ('t2', 'o2', 'geçiş', '#999', True)]
    cizge('113_konu_haritasi', '113. Konu haritası (ISO 13250): konular, aralarındaki münasebet ve metinde geçtikleri yer', 'Konu düğümleri; gri kutular konunun belgede geçtiği yer.', N, E, H=580, bw=160)
# 114 Soyutlama merdiveni
@usul
def u114():
    b = []
    R = [('kazandaki koku sürülmüş deri parçası', 'en somut', '#7a7a7a'), ('ölçülüp biçilmiş deri', '', RK('A')), ('yaratılmış her şey', '', RK('J')), ('her şeyin yaradılışı, kalıbı', '', RK('K')), ('insanın huyu', '', RK('U')), ('ahlâk ilmi', '', RK('X')), ('"ölçüyle hazırlamak" fikri', 'en soyut', '#b8860b')]
    for k, (s, e, c) in enumerate(R):
        y = 590 - k * 78; x = 180 + k * 40
        b.append(f'<rect x="{x}" y="{y-26}" width="420" height="44" fill="{c}" fill-opacity=".15" stroke="{c}" stroke-width="2"/>'); b.append(T(s, x + 210, y + 2, 12, w='font-weight="700"'))
        if e: b.append(T(e, x + 430, y + 2, 11, 'start', '#b3541e'))
    b.append('<line x1="120" y1="620" x2="120" y2="90" stroke="#2b2410" stroke-width="3"/><line x1="160" y1="620" x2="160" y2="90" stroke="#2b2410" stroke-width="3"/>')
    for k in range(8): b.append(f'<line x1="120" y1="{610-k*75}" x2="160" y2="{610-k*75}" stroke="#2b2410" stroke-width="3"/>')
    kaydet('114_soyutlama_merdiveni', '114. Soyutlama merdiveni (Hayakawa): somuttan soyuta basamak basamak', 'Aynı kökün manaları elle tutulandan düşünceye doğru dizilir.', b, 900, 640)
# 115 Anlam üçgeni
@usul
def u115():
    b = []
    for k, (ar, mana, masadak, x) in enumerate([('خَلْق', 'yaratma fiili', 'gök, yer, insan', 160), ('خُلُق', 'huy', 'cömertlik, sabır', 450), ('خَلَق', 'eski', 'yırtık bir elbise', 740)]):
        A, B_, C = (x, 120), (x - 95, 420), (x + 95, 420)
        b.append(f'<path d="M{A[0]},{A[1]} L{B_[0]},{B_[1]}" stroke="#2b2410" stroke-width="2"/><path d="M{A[0]},{A[1]} L{C[0]},{C[1]}" stroke="#2b2410" stroke-width="2"/><path d="M{B_[0]},{B_[1]} L{C[0]},{C[1]}" stroke="#2b2410" stroke-width="2" stroke-dasharray="6 4"/>')
        b.append(T('MANA (zihindeki)', A[0], A[1] - 30, 10, fill='#6d6650')); b.append(T(mana, A[0], A[1] - 12, 12, w='font-weight="700"'))
        b.append(T('LAFIZ', B_[0], B_[1] + 22, 10, fill='#6d6650')); b.append(AR(ar, B_[0], B_[1] + 46, 20))
        b.append(T('MASADAK (dıştaki)', C[0], C[1] + 22, 10, fill='#6d6650')); b.append(T(masadak, C[0], C[1] + 42, 11.5, w='font-weight="700"'))
    b.append(T('Kesik kenar: lafız ile dıştaki şey arasında doğrudan bağ yoktur; bağ zihindeki mana üzerinden kurulur (Ogden ve Richards).', 450, 560, 11))
    kaydet('115_anlam_ucgeni', '115. Anlam üçgeni: lafız, mana, masadak', 'Aynı kökten üç kelime, üç ayrı üçgen.', b, 900, 590)
# 116 Greimas karesi
@usul
def u116():
    b = []
    C = {'S1': (200, 130, 'ÖLÇÜLÜ', 'yaratılmış, lâyık'), 'S2': (700, 130, 'BOZUK', 'eskimiş'), 'nS2': (200, 470, 'BOZUK OLMAYAN', 'yeni, düz'), 'nS1': (700, 470, 'ÖLÇÜSÜZ', 'uydurma')}
    for a, c, l, cc in [('S1', 'S2', 'zıtlık', '#c0392b'), ('nS2', 'nS1', 'alt zıtlık', '#c26a1e'), ('S1', 'nS1', 'çelişki', '#2b2410'), ('S2', 'nS2', 'çelişki', '#2b2410'), ('nS2', 'S1', 'gerektirme', '#2f6fb3'), ('nS1', 'S2', 'gerektirme', '#2f6fb3')]:
        x1, y1 = C[a][:2]; x2, y2 = C[c][:2]; b.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cc}" stroke-width="2"/>')
        b.append(T(l, (x1 + x2) / 2 + (40 if a in ('S1',) and c == 'nS1' else 0), (y1 + y2) / 2 - 6, 10.5, fill=cc, w='font-weight="700" stroke="#fffdf6" stroke-width="3" paint-order="stroke"'))
    for k, (x, y, s, w) in C.items(): b.append(f'<rect x="{x-110}" y="{y-30}" width="220" height="60" rx="8" fill="#fff" stroke="#2b2410" stroke-width="1.6"/>'); b.append(T(s, x, y - 6, 13, w='font-weight="700"')); b.append(T(w, x, y + 14, 10.5, fill='#6d6650'))
    b.append(T('Kökün manaları dört köşeye dağılır; uydurmak, ölçülü yaratmanın çelişiği olarak yerini bulur.', 450, 590, 11))
    kaydet('116_greimas', '116. Greimas göstergebilim karesi: zıt, çelişik ve gerektiren dört köşe', 'Bir mananın neyin karşıtı, neyin inkârı olduğu aynı şekilde görünür.', b, 900, 620)
# 117 Haşiyeli sayfa
@usul
def u117():
    b = []
    b.append('<rect x="60" y="70" width="780" height="560" fill="#fbf6e6" stroke="#8a5a2b" stroke-width="2"/>')
    b.append('<rect x="290" y="250" width="320" height="200" fill="#fff" stroke="#8a5a2b" stroke-width="1.5"/>')
    b.append(T('MATN', 450, 270, 11, fill='#8a5a2b', w='font-weight="700"')); b.append(AR('خَلَقَ: قَدَّرَ وَهَيَّأَ', 450, 320, 22)); b.append(T('ölçüp biçerek hazırladı', 450, 350, 11))
    b.append(AR('ثُمَّ: أَوْجَدَ، وَمِنْهُ الخُلُق', 450, 395, 17)); b.append(T('sonra: var etti; huy da buradandır', 450, 420, 10.5))
    H = [(450, 110, 'ŞERH (üst): ölçmek, bir şeyi yapmadan önce sınırlarını tayin etmektir; terzi böyle yapar.'), (450, 200, 'Bu yüzden Allah\'a "Hâlık" denir: her şeyi ölçüsüyle var eden.'),
         (175, 290, 'HÂŞİYE (sol):'), (175, 310, 'eskimek manası'), (175, 330, 'düzlenmiş yüzeyden'), (175, 350, 'gelir: خَلِقَ الثَّوْبُ'),
         (725, 290, 'HÂŞİYE (sağ):'), (725, 310, 'huy, yaradılışın'), (725, 330, 'nefse vurmasıdır;'), (725, 350, 'çoğulu أَخْلَاق'),
         (450, 500, 'TA\'LÎKA (alt): koku manası (خَلُوق) yüzeye sürülen şeyden; kazan (خِلْقِين) yabancı kelimedir.'), (450, 600, 'Matn ortada, şerh etrafını sarar; okuyan önce matnı, ihtiyaç olunca kenarı okur.')]
    for x, y, s in H: b.append(T(s, x, y, 10.5 if y != 600 else 10, fill='#2b2410' if y != 600 else '#6d6650', w='font-weight="700"' if ':' in s and len(s) < 16 else ''))
    kaydet('117_hasiyeli_sayfa', '117. Haşiyeli sayfa (matn–şerh–hâşiye): ortada asıl, etrafında açıklamalar', 'Medrese kitaplarının sayfa tertibi.', b, 900, 650)
# 118 Satırarası tercüme
@usul
def u118():
    b = []
    S = [[('خَلَقَ', 'yarattı', 'fiil, mâzî'), ('الْإِنسَانَ', 'insanı', 'mef\'ûl'), ('مِن', '-den', 'harf'), ('نُّطْفَةٍ', 'bir damla su', 'mecrûr')],
         [('وَإِنَّكَ', 've şüphesiz sen', ''), ('لَعَلَىٰ', 'üzerindesin', ''), ('خُلُقٍ', 'bir huy', 'isim'), ('عَظِيمٍ', 'büyük', 'sıfat')]]
    y = 120
    for s in S:
        x = 850
        for ar, tr, g in s:
            w = 190; b.append(AR(ar, x - w / 2, y, 24, fill='#b3541e' if 'خ' in ar and 'ل' in ar else '#1a1a1a')); b.append(T(tr, x - w / 2, y + 30, 12)); b.append(T(g, x - w / 2, y + 48, 9.5, fill='#6d6650')); x -= w
        y += 150
    b.append(T('Nahl 16:4 ve Kalem 68:4. Her kelimenin altında karşılığı ve görevi; kökün kelimeleri kırmızı.', 450, 440, 11))
    kaydet('118_satirarasi', '118. Satırarası tercüme: kelimenin hemen altında manası', 'Okuyan Arapça sırayı bozmadan anlar.', b, 900, 470)
# 119 Zettelkasten
@usul
def u119():
    b = [DEF]
    K = [('1', 'ölçüp biçerek hazırlamak (esas)', 60, 90), ('1a', 'ölçmek → yaratmak', 60, 220), ('1a1', 'yaratılmış, mahlûk', 60, 350), ('1a2', 'yaradılış → huy', 280, 350), ('1a2a', 'huy → ahlâk', 280, 480),
         ('1b', 'düzlemek', 500, 220), ('1b1', 'eskimek', 500, 350), ('1b2', 'koku sürmek', 720, 350), ('2', 'kazan (kök dışı)', 720, 90)]
    for no, s, x, y in K:
        b.append(f'<rect x="{x}" y="{y}" width="200" height="90" fill="#fffef0" stroke="#2b2410" filter="drop-shadow(2px 3px 2px #0003)"/>'); b.append(T(no, x + 10, y + 20, 13, 'start', '#b3541e', 'font-weight="700"')); b.append(T(s, x + 100, y + 52, 11))
    for a, c, l in [('1a2', '1b1', 'bkz: aşınan huy?'), ('1b2', '1a1', 'bkz: kokulanmış (مُخَلَّق)')]:
        P = {no: (x, y) for no, s, x, y in K}; ok(b, P[a][0] + 200, P[a][1] + 30, P[c][0], P[c][1] + 30, l, '#2f6fb3', True)
    b.append(T('Numara, kartın yerini söyler: 1a2a, 1a2\'nin devamıdır. Kesik ok, ağacın dışından kurulan bağdır.', 450, 610, 11))
    kaydet('119_zettelkasten', '119. Zettelkasten (Luhmann fiş kutusu): numaralı kartlar ve çapraz göndermeler', 'Yeni bir fikir, kendisini doğuran kartın numarasına harf eklenerek yerleşir.', b, 900, 630)
# 120 Soy kütüğü
@usul
def u120():
    b = []
    G = [[('E', 'ESAS')], [('A', ''), ('B', ''), ('C', ''), ('H', '')], [('D', ''), ('N', ''), ('F', ''), ('G', '')], [('J', ''), ('K', ''), ('L', '')], [('U', '')], [('X', ''), ('Y', ''), ('Z', '')]]
    P = {}
    for g, row in enumerate(G):
        for k, (m, _) in enumerate(row): P[m] = (450 + (k - (len(row) - 1) / 2) * 190, 90 + g * 100)
    for m, (x, y) in P.items():
        ps = MANA[m]['ebeveyn']
        if len(ps) == 2:
            (x1, y1), (x2, y2) = P[ps[0]], P[ps[1]]; b.append(f'<line x1="{x1}" y1="{y1+18}" x2="{x1}" y2="{y1+40}" stroke="#2b2410"/><line x1="{x2}" y1="{y2+18}" x2="{x2}" y2="{y2+40}" stroke="#2b2410"/><line x1="{x1}" y1="{y1+40}" x2="{x2}" y2="{y2+40}" stroke="#c0392b" stroke-width="2"/><line x1="{(x1+x2)/2}" y1="{y1+40}" x2="{x}" y2="{y-18}" stroke="#2b2410"/>')
        elif ps:
            px, py = P[ps[0]]; b.append(f'<path d="M{px},{py+18} V{(py+y)/2} H{x} V{y-18}" stroke="#2b2410" fill="none"/>')
    for m, (x, y) in P.items():
        b.append(f'<rect x="{x-80}" y="{y-18}" width="160" height="36" rx="18" fill="{RK(m) if m!="E" else "#b8860b"}" fill-opacity=".2" stroke="{RK(m) if m!="E" else "#b8860b"}" stroke-width="2"/>'); b.append(T(M(m), x, y - 1, 11, w='font-weight="700"')); b.append(AR((kel(m) or [''])[0], x, y + 13, 11))
    b.append(T('Kırmızı çizgi iki ebeveynin birleşmesidir: şekli belirmiş, hem ölçmenin hem düzlemenin evladıdır.', 450, 640, 11))
    kaydet('120_soy_kutugu', '120. Soy kütüğü: her nesil bir satır, birleşmeler ayrıca çizilir', 'Aynı nesildekiler kardeştir.', b, 900, 660)
# 121 Anlam skalası
@usul
def u121():
    b = []
    for k, (sol, sag, ls) in enumerate([('SOMUT (elle tutulur)', 'SOYUT (akılla bilinir)', [('خَلْقَاء', 0.05), ('خَلَق', 0.15), ('خَلُوق', 0.2), ('مُخَلَّق', 0.3), ('مَخْلُوق', 0.45), ('خِلْقَة', 0.55), ('خُلُق', 0.72), ('أَخْلَاق', 0.88), ('اِخْتِلَاق', 0.95)]),
                                     ('YENİ', 'ESKİ', [('خَلَقَ', 0.05), ('مَخْلُوق', 0.3), ('خِلْقَة', 0.5), ('خَلِقَ', 0.85), ('خُلْقَان', 0.97)]),
                                     ('DIŞ', 'İÇ', [('خَلْق', 0.1), ('خِلْقَة', 0.4), ('خَلِيقَة', 0.6), ('خُلُق', 0.85), ('أَخْلَاق', 0.95)])]):
        y = 130 + k * 180
        b.append(f'<defs><linearGradient id="g{k}"><stop offset="0" stop-color="#e8c766"/><stop offset="1" stop-color="#7a3fb3"/></linearGradient></defs><rect x="80" y="{y}" width="740" height="12" rx="6" fill="url(#g{k})"/>')
        b.append(T(sol, 80, y - 12, 11, 'start', w='font-weight="700"')); b.append(T(sag, 820, y - 12, 11, 'end', w='font-weight="700"'))
        for j, (ar, v) in enumerate(ls): x = 80 + v * 740; b.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+30+(j%2)*26}" stroke="#2b2410"/>'); b.append(AR(ar, x, y + 48 + (j % 2) * 26, 15))
    kaydet('121_anlam_skalasi', '121. Anlam skalası: kelimeler bir uçtan öbür uca bir çizgi üzerinde', 'Üç ayrı eksen: somut–soyut, yeni–eski, dış–iç. Yerleri kıyas içindir, ölçüm değildir.', b, 900, 640)
# 122 Beş neden
@usul
def u122():
    b = [DEF]
    S = ['Ahlâk neden bu köktendir?', 'Çünkü huyların düzenidir. Huy neden bu köktendir?', 'Çünkü yaradılışın nefse vurmasıdır. Yaradılış neden?', 'Çünkü yaratılanın kalıbıdır. Yaratmak neden?', 'Çünkü ölçülen şeyin tamamlanmasıdır. Ölçmek neden?', 'Çünkü hazırlamanın ilk işidir: ESAS']
    for k, s in enumerate(S):
        y = 80 + k * 90; c = '#b8860b' if k == 5 else '#2b2410'
        b.append(f'<rect x="{150+k*30}" y="{y}" width="560" height="56" rx="8" fill="{"#f3eedd" if k==5 else "#fff"}" stroke="{c}" stroke-width="1.6"/>'); b.append(T(f'{k}. ' + s, 430 + k * 30, y + 33, 12, w='font-weight="700"' if k in (0, 5) else ''))
        if k < 5: ok(b, 430 + k * 30, y + 56, 460 + k * 30, y + 90)
    kaydet('122_bes_neden', '122. Beş neden: en uzak manadan "neden?" diye sorarak esasa inmek', 'Her cevap bir sonraki suâli doğurur.', b, 900, 640)
# 123 Mana değişmesi türleri
@usul
def u123():
    b = [DEF]
    T3 = [('GENİŞLEME', 'ölçüp biçmek → her türlü yaratmak', '#2f6fb3'), ('DARALMA', 'yaratılmış her şey → insanlar (خَلْق = halk)', '#c26a1e'), ('SOYUTLAŞMA', 'yaradılış (beden) → huy (nefs)', '#7a3fb3'),
          ('İYİLEŞME', 'huy → güzel ahlâk (أَخْلَاق)', '#3f8f3a'), ('KÖTÜLEŞME', 'yaratmak → uydurmak (اِخْتَلَقَ)', '#c0392b'), ('BİTİŞİKLİK', 'yüzey → yüzeye sürülen koku', '#a8478f'), ('NETİCE', 'düzlemek → eskimek', '#7a7a7a')]
    for k, (ad, s, c) in enumerate(T3):
        y = 80 + k * 76; b.append(f'<rect x="40" y="{y}" width="200" height="56" rx="28" fill="{c}"/>'); b.append(T(ad, 140, y + 33, 12.5, fill='#fff', w='font-weight="700"'))
        a, z = s.split(' → '); b.append(T(a, 360, y + 33, 12)); ok(b, 470, y + 28, 560, y + 28); b.append(T(z, 700, y + 33, 12, w='font-weight="700"'))
    kaydet('123_mana_degismesi', '123. Mana değişmesi türleri (Bréal, Ullmann): her türeme bir değişme türüne konur', 'Sol: değişmenin adı, sağ: kökte onun örneği.', b, 900, 630)
# 124 WordNet
@usul
def u124():
    N = {'s': (450, 300, '{خَلَقَ, فَطَرَ, بَرَأَ}: yaratmak', RK('D'), None, 230), 'h': (450, 100, 'üst kavram: {صَنَعَ}: yapmak', '#2b2410', None, 220), 'h1': (180, 480, 'alt: {صَوَّرَ}: şekil vermek', '#2f6fb3', None, 200),
         'h2': (450, 520, 'alt: {أَنْشَأَ}: inşa etmek', '#2f6fb3', None, 200), 'h3': (720, 480, 'alt: {اِخْتَلَقَ}: sözle uydurmak', RK('L'), None, 200), 'z': (800, 250, 'zıt: {أَفْنَى}: yok etmek', '#c0392b', None, 180), 'p': (100, 250, 'neticesi: {مَخْلُوق}', RK('J'), None, 160)}
    E = [('s', 'h', 'üst kavram'), ('h1', 's', 'alt kavram'), ('h2', 's', 'alt kavram'), ('h3', 's', 'alt kavram'), ('s', 'z', 'zıt', '#c0392b', True), ('s', 'p', 'netice', '#3f8f3a', True)]
    cizge('124_wordnet', '124. WordNet ağı: eş manalılar bir küme (synset), kümeler ilişki adlarıyla bağlı', 'Süslü parantez içindekiler eş manalıdır; oklar üst-alt, zıt ve netice.', N, E, H=600)
# 125 Döngü diyagramı
@usul
def u125():
    b = [DEF]; cx, cy = 450, 350
    A = [('ham madde', '', '#7a7a7a'), ('ölçülür', 'خَلَقَ', RK('A')), ('yaratılır', 'مَخْلُوق', RK('J')), ('kullanılır, işe yakışır', 'خَلِيق', RK('H')), ('eskir', 'خَلِقَ', RK('F')), ('yeniden ham madde olur', 'خُلْقَان', '#7a7a7a')]
    for k, (s, ar, c) in enumerate(A):
        a = -math.pi / 2 + k * 2 * math.pi / len(A); x, y = cx + 230 * math.cos(a), cy + 230 * math.sin(a)
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="62" fill="{c}" fill-opacity=".15" stroke="{c}" stroke-width="2"/>'); b.append(T(s, x, y - 4, 11, w='font-weight="700"')); b.append(AR(ar, x, y + 22, 15))
        a2 = a + 2 * math.pi / len(A); ok(b, round(cx + 230 * math.cos(a + .3), 1), round(cy + 230 * math.sin(a + .3), 1), round(cx + 230 * math.cos(a2 - .3), 1), round(cy + 230 * math.sin(a2 - .3), 1), '', c, False, 0)
    b.append(T('eşyanın ömrü', cx, cy + 4, 14, w='font-weight="700"'))
    kaydet('125_dongu', '125. Döngü diyagramı: kökün manaları bir eşyanın ömür devridir', 'Yapılır, kullanılır, eskir, yeniden yapılır.', b, 900, 660)
# 126 KWIC
@usul
def u126():
    b = []
    L = [('خَلَقَ السَّمَاوَاتِ', 'الْحَمْدُ لِلَّهِ الَّذِي', 'وَالْأَرْضَ', 'En\'âm 6:1', 'yaratmak'), ('خُلُقٍ', 'وَإِنَّكَ لَعَلَىٰ', 'عَظِيمٍ', 'Kalem 68:4', 'huy'), ('خُلُقُ', 'إِنْ هَٰذَا إِلَّا', 'الْأَوَّلِينَ', 'Şuarâ 26:137', 'âdet, yol'),
         ('خَلَاقٍ', 'مَا لَهُ فِي الْآخِرَةِ مِنْ', '', 'Bakara 2:102', 'pay'), ('اخْتِلَاقٌ', 'إِنْ هَٰذَا إِلَّا', '', 'Sâd 38:7', 'uydurma'), ('مُّخَلَّقَةٍ', 'مِن مُّضْغَةٍ', 'وَغَيْرِ مُخَلَّقَةٍ', 'Hac 22:5', 'şekli belirmiş'), ('تَخْلُقُ', 'وَإِذْ', 'مِنَ الطِّينِ', 'Mâide 5:110', 'şekil vermek')]
    b.append('<line x1="450" y1="70" x2="450" y2="560" stroke="#b3541e" stroke-dasharray="3 3"/>')
    for k, (kw, sol, sag, yer, m) in enumerate(L):
        y = 110 + k * 64
        b.append(AR(sag, 380, y, 17, 'end')); b.append(AR(kw, 450, y, 20, fill='#b3541e')); b.append(AR(sol, 520, y, 17, 'start'))
        b.append(T(m, 60, y - 3, 11, 'start', w='font-weight="700"')); b.append(T(yer, 860, y - 3, 10, 'end', '#6d6650'))
    b.append(T('Kök ortada hizalı; sağında öncesi, solunda sonrası (Arapça sağdan okunur). Âyet yerleri hafızadan.', 450, 600, 10.5))
    kaydet('126_kwic', '126. Bağlamlı dizin (KWIC): her geçişte kelime ortada, çevresi iki yanda', 'Manayı bağlam söyler; aynı kelime farklı komşularla farklı manaya gelir.', b, 900, 620)
# 127 Sual-cevap
@usul
def u127():
    b = []
    Q = [('Sual: خلق kökünün aslı nedir?', 'Cevap: Bir şeyi bir maksada göre ölçüp biçerek hazırlamaktır.'), ('Sual: Allah\'a niçin Hâlık denir?', 'Cevap: Her şeyi ölçüsüyle tamamlayıp var ettiği için.'),
         ('Sual: Huy (خُلُق) bu köke nasıl girer?', 'Cevap: Yaradılışta nefse verilen kalıp, insanın huyu olur.'), ('Sual: Ahlâk nedir?', 'Cevap: Huyların yerleşip bir düzene girmesidir.'),
         ('Sual: Eskimek (خَلِقَ) nereden gelir?', 'Cevap: Düzlenen yüzey kullanıldıkça aşınır ve eskir.'), ('Sual: Uydurmak (اِخْتَلَقَ) niçin bu köktendir?', 'Cevap: Olmayan sözü var göstermek, yaratmanın sahtesidir.'), ('Sual: Kazan (خِلْقِين) da bu kökten mi?', 'Cevap: Hayır; Yunancadan gelmiştir.')]
    for k, (q, c) in enumerate(Q):
        y = 90 + k * 76; b.append(T(q, 60, y, 12.5, 'start', '#b3541e', 'font-weight="700"')); b.append(T(c, 90, y + 24, 12, 'start'))
    kaydet('127_sual_cevap', '127. Sual-cevap (ilmihal usulü): her mana bir suâlin cevabı', 'Okuyan suâli okuyup cevabı kapatarak kendini yoklar.', b, 900, 640)
# 128 Manzume
@usul
def u128():
    b = []
    B2 = [('Halk ölçüp biçmektir, aslı budur,', 'Hâlık her şeyi ölçüyle kurar.'), ('Ölçülen tamamlanınca mahlûk olur,', 'Mahlûkun kalıbına hilkat denir.'), ('Hilkat nefse girince huy (hulk) olur,', 'Huylar çoğalınca ahlâk bilinir.'),
          ('Düzlenen yüzey aşınır, eskir (halika),', 'Koku sürülen şey düzlenir.'), ('İşe ayrılan şey pay (halâk) olur,', 'İşine uyan şeye halîk denir.'), ('Olmayanı var etmek ihtilâktır,', 'Kazan (hılkîn) yabancıdır, bu köke girmez.')]
    for k, (m1, m2) in enumerate(B2):
        y = 110 + k * 80; b.append(T(m1, 430, y, 14, 'end', '#2b2410', 'font-style="italic"')); b.append(T(m2, 470, y, 14, 'start', '#2b2410', 'font-style="italic"'))
        b.append(f'<circle cx="450" cy="{y-5}" r="3" fill="#b3541e"/>')
    b.append(T('Elfiye ve tuhfe usulü: ilim beyitle öğretilir, ezberlenen beyit manayı taşır. Beyitler bu levha için yazıldı, vezinli değildir.', 450, 610, 10.5, fill='#6d6650'))
    kaydet('128_manzume', '128. Manzume (öğretici şiir): kökün bütün manaları altı beyitte', 'Klasik eğitimde nahiv, sarf, ferâiz böyle ezberletilirdi.', b, 900, 640)
# 129 Öğrenme yolu
@usul
def u129():
    N = {'E': (450, 80, '1. esas: ölçüp biçerek hazırlamak', '#b8860b', None, 260), 'A': (220, 190, '2. ölçmek', RK('A')), 'B': (680, 190, '2. düzlemek', RK('B')), 'D': (220, 300, '3. yaratmak', RK('D')), 'C': (450, 300, '3. pay, lâyık', RK('C')),
         'F': (680, 300, '3. eskimek', RK('F')), 'K': (220, 410, '4. yaradılış', RK('K')), 'L': (450, 410, '4. uydurmak', RK('L')), 'U': (220, 520, '5. huy', RK('U')), 'X': (450, 520, '6. ahlâk', RK('X')), 'G': (680, 410, '4. koku', RK('G'))}
    E = [('E', 'A'), ('E', 'B'), ('A', 'D'), ('A', 'C', 'önce bilinmeli'), ('B', 'F'), ('D', 'K'), ('D', 'L'), ('K', 'U'), ('U', 'X'), ('B', 'G')]
    cizge('129_ogrenme_yolu', '129. Öğrenme yolu (önşart haritası): hangi mana hangisinden önce öğrenilmeli', 'Ok, "önce bunu bil" demektir; numara öğrenme sırasıdır.', N, E, H=600)
# 130 Yapı eşlemesi
@usul
def u130():
    b = [DEF]
    S = [('terzi', 'Allah (Hâlık)'), ('deriyi ölçer', 'her şeyi ölçüyle takdir eder'), ('elbise biçer', 'mahlûku yaratır'), ('elbisenin kalıbı', 'yaradılış (خِلْقَة)'), ('elbise bedene uyar', 'huy nefse yerleşir (خُلُق)'), ('elbise eskir', 'eşya eskir (خَلِقَ)')]
    b.append(T('KAYNAK SAHA: terzilik', 220, 80, 13, fill='#c26a1e', w='font-weight="700"')); b.append(T('HEDEF SAHA: yaratma ve nefs', 680, 80, 13, fill='#2f6fb3', w='font-weight="700"'))
    for k, (a, c) in enumerate(S):
        y = 110 + k * 82; kutu(b, 90, y, 260, 54, None, [a], '#c26a1e'); kutu(b, 550, y, 260, 54, None, [c], '#2f6fb3')
        b.append(f'<line x1="350" y1="{y+27}" x2="550" y2="{y+27}" stroke="#999" stroke-dasharray="4 3"/>')
        if k: b.append(f'<line x1="220" y1="{y-28}" x2="220" y2="{y}" stroke="#c26a1e"/><line x1="680" y1="{y-28}" x2="680" y2="{y}" stroke="#2f6fb3"/>')
    b.append(T('Eşlenen tek tek nesneler değil, aralarındaki münasebetlerdir (Gentner, yapı eşleme nazariyesi).', 450, 620, 11))
    kaydet('130_yapi_eslemesi', '130. Yapı eşlemesi: iki sahanın münasebetleri satır satır karşılaştırılır', 'Sol sütundaki zincir sağ sütundaki zincirle aynı şekildedir.', b, 900, 640)
if __name__ == '__main__':
    for f in S: f()
    print(len(S))
