from ortak import *
MN = [i for i in ORDER if i != 'E']
DALAD = {'A': 'ölçüp biçme/yaratma', 'B': 'düzleme', 'AB': 'ikisi', 'C': 'pay', 'H': 'yakışma', 'R2': 'kök dışı', 'E': 'esas'}
def rgb(c, o): return f'fill="{c}" fill-opacity="{o}"'
def kdal(w): return sorted({dal(m) for m in KEL[w]['anlam']})[0]
def kder(w): return max(depth(m) for m in KEL[w]['anlam'])
# 28 Parallel Sets
def psets():
    b = []; ax = [('dal', kdal), ('derinlik', lambda w: f'{kder(w)}. basamak'), ('kelime türü', lambda w: KEL[w]['tag'] or '-'), ('Kur\'ân', lambda w: 'geçer' if KEL[w]['kuran'] else 'geçmez')]
    xs = [120, 340, 560, 780]; H = 520; y0 = 80; ws = list(KEL); N = len(ws)
    pos = []
    for k, (ad, f) in enumerate(ax):
        cat = collections.Counter(f(w) for w in ws); y = y0; p = {}
        for c, n in sorted(cat.items()):
            h = n / N * (H - 10 * len(cat)); p[c] = [y, y]; b.append(f'<rect x="{xs[k]-6}" y="{y:.1f}" width="12" height="{h:.1f}" fill="#2b2410"/>')
            b.append(T(f'{c} ({n})', xs[k] + (14 if k < 3 else -14), y + h / 2 + 4, 10, 'start' if k < 3 else 'end')); y += h + 10
        pos.append(p); b.append(T(ad, xs[k], y0 - 12, 12, w='font-weight="700"'))
    for k in range(3):
        f1, f2 = ax[k][1], ax[k + 1][1]
        for (a, c), n in sorted(collections.Counter((f1(w), f2(w)) for w in ws).items()):
            h = n / N * (H - 60); ya = pos[k][a][1]; yb = pos[k + 1][c][0]
            col = RENK.get(a if k == 0 else kdal(next(w for w in ws if f1(w) == a)), '#888')
            b.append(f'<path d="M{xs[k]+6},{ya:.1f} C{xs[k]+110},{ya:.1f} {xs[k+1]-110},{yb:.1f} {xs[k+1]-6},{yb:.1f} L{xs[k+1]-6},{yb+h:.1f} C{xs[k+1]-110},{yb+h:.1f} {xs[k]+110},{ya+h:.1f} {xs[k]+6},{ya+h:.1f}Z" {rgb(col,.35)}/>')
            pos[k][a][1] += h; pos[k + 1][c][0] += h
    kaydet('28_parallel_sets', '28. Paralel kümeler: 37 kelime dört vasıf ekseninde', 'Şerit kalınlığı = kelime sayısı; dal → derinlik → tür → Kur\'ân\'da geçiş.', b)
# 29 Kiriş (chord)
def chord():
    b = []; cx, cy, R = 450, 350, 250; n = len(ORDER); a = {m: 2 * math.pi * k / n - math.pi / 2 for k, m in enumerate(ORDER)}
    for m in ORDER:
        c = RENK[dal(m)]; t = a[m]; d = math.pi / n * .85
        b.append(f'<path d="M{cx+R*math.cos(t-d):.1f},{cy+R*math.sin(t-d):.1f} A{R},{R} 0 0 1 {cx+R*math.cos(t+d):.1f},{cy+R*math.sin(t+d):.1f}" stroke="{c}" stroke-width="16" fill="none"/>')
        b.append(T(KISA[m], cx + (R + 34) * math.cos(t), cy + (R + 34) * math.sin(t) + 4, 10.5))
    for m in ORDER:
        for p in MANA[m]['ebeveyn']:
            P, Q = a[p], a[m]
            b.append(f'<path d="M{cx+(R-9)*math.cos(P):.1f},{cy+(R-9)*math.sin(P):.1f} Q{cx},{cy} {cx+(R-9)*math.cos(Q):.1f},{cy+(R-9)*math.sin(Q):.1f}" stroke="{RENK[dal(m)]}" stroke-width="{1.5+len(WORDS_OF.get(m,[]))}" stroke-opacity=".45" fill="none"/>')
    kaydet('29_kiris', '29. Kiriş diyagramı: manalar çember üstünde, kirişler türeme', 'Kiriş kalınlığı = doğan mananın kelime sayısı; renk dal.', b, 900, 700)
# 30 Halka (kelime dışta, mana içte)
def halka():
    b = []; cx, cy = 450, 360; ws = sorted(KEL, key=lambda w: (ORDER.index(sorted(KEL[w]['anlam'], key=ORDER.index)[0]), w))
    am = {m: 2 * math.pi * k / len(ORDER) for k, m in enumerate(ORDER)}; aw = {w: 2 * math.pi * k / len(ws) for k, w in enumerate(ws)}
    for w in ws:
        for m in KEL[w]['anlam']:
            b.append(f'<line x1="{cx+150*math.cos(am[m]):.1f}" y1="{cy+150*math.sin(am[m]):.1f}" x2="{cx+270*math.cos(aw[w]):.1f}" y2="{cy+270*math.sin(aw[w]):.1f}" stroke="{RENK[dal(m)]}" stroke-opacity=".5"/>')
        t = aw[w]; b.append(AR(KEL[w]['ar'], cx + 292 * math.cos(t), cy + 292 * math.sin(t) + 5, 13))
    for m in ORDER:
        x, y = cx + 150 * math.cos(am[m]), cy + 150 * math.sin(am[m]); b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{RENK[dal(m)]}"/>'); b.append(T(KISA[m], cx + 118 * math.cos(am[m]), cy + 118 * math.sin(am[m]) + 4, 9))
    kaydet('30_halka', '30. Halka: içte manalar, dışta kelimeler', 'Her çizgi bir kelimenin taşıdığı bir manadır.', b, 900, 720)
# 31 Küçük katlar
def kucuk():
    b = []; D = ['A', 'B', 'C', 'H', 'R2']
    for k, d in enumerate(D):
        x0 = 18 + (k % 3) * 290; y0 = 70 + (k // 3) * 290
        b.append(f'<rect x="{x0}" y="{y0}" width="280" height="280" fill="none" stroke="#d8cfb0"/>'); b.append(T(DALAD[d], x0 + 140, y0 + 18, 12, w=f'font-weight="700" fill="{RENK[d]}"'))
        ms = [m for m in ORDER if dal(m) in (d, 'AB' if d in 'AB' else '-')]
        for j, m in enumerate(ms):
            y = y0 + 40 + j * 24; x = x0 + 14 + depth(m) * 26
            b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{RENK[d]}"/>'); b.append(T(KISA[m], x + 9, y + 4, 10, 'start'))
            ws = ' '.join(KEL[w]['ar'] for w in WORDS_OF.get(m, [])[:3]); b.append(AR(ws, x0 + 272, y + 5, 12, 'end'))
    kaydet('31_kucuk_katlar', '31. Küçük katlar: her dal aynı ölçekte ayrı levha', 'Girinti = köke uzaklık; sağda o mananın kelimeleri.', b, 900, 660)
# 32 Zihin haritası
def zihin():
    b = []; cx, cy = 450, 350; L = {}
    top = [m for m in KIDS['E']]
    def yer(m, a0, a1, r):
        a = (a0 + a1) / 2; L[m] = (cx + r * math.cos(a), cy + r * math.sin(a))
        ch = [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m]
        wt = [1 + len(alt_say(c)) for c in ch]; t = sum(wt) or 1; a = a0
        for c, w in zip(ch, wt): yer(c, a, a + (a1 - a0) * w / t, r + 75); a += (a1 - a0) * w / t
    wt = [1 + len(alt_say(m)) for m in top]; t = sum(wt); a = -math.pi / 2
    for m, w in zip(top, wt): yer(m, a, a + 2 * math.pi * w / t, 95); a += 2 * math.pi * w / t
    L['E'] = (cx, cy)
    for m, (x, y) in L.items():
        for p in MANA[m]['ebeveyn'][:1]:
            px, py = L[p]; b.append(f'<path d="M{px:.1f},{py:.1f} Q{(px+x)/2:.1f},{py:.1f} {x:.1f},{y:.1f}" stroke="{RENK[dal(m)]}" stroke-width="{max(2,9-3*depth(m))}" fill="none" stroke-linecap="round"/>')
    for m, (x, y) in L.items():
        b.append(T(KISA[m], x, y - 6, 11 if m != 'E' else 15, w='font-weight="700" stroke="#fffdf6" stroke-width="3" paint-order="stroke"'))
        ws = ' '.join(KEL[w]['ar'] for w in WORDS_OF.get(m, [])[:2]); b.append(AR(ws, x, y + 12, 12))
    kaydet('32_zihin_haritasi', '32. Zihin haritası: esas ortada, dallar kalınlıkla incelir', 'Kalınlık köke yakınlıktır; dalın ucunda kelimeler.', b, 900, 700)
# 33 Toulmin
def kutu(b, x, y, w, h, bas, satir, c='#2b2410'):
    b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{c}" stroke-width="1.6"/>'); b.append(T(bas, x + 8, y + 16, 10.5, 'start', c, 'font-weight="700"'))
    for k, s in enumerate(satir): b.append(T(s, x + 8, y + 33 + k * 15, 10, 'start'))
def ok(b, x1, y1, x2, y2): b.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2b2410" stroke-width="1.6" marker-end="url(#o)"/>')
DEF = '<defs><marker id="o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#2b2410"/></marker></defs>'
def toulmin():
    b = [DEF]
    kutu(b, 20, 90, 250, 120, 'VERİ (müşahede)', ['خَلَقَ: yarattı', 'خُلُق: huy, ahlâk', 'خَلِقَ: eskidi', 'خَلَاق: pay'])
    kutu(b, 620, 90, 260, 120, 'HÜKÜM', ['Bütün bu manalar tek esastan', 'doğar: ölçüp biçerek', 'hazırlamak.'], '#b3541e')
    kutu(b, 330, 90, 230, 60, 'KAYIT (derece)', ['ekseriyetle; bir kelime müstesna'])
    kutu(b, 330, 250, 250, 105, 'TEMİNAT (köprü)', ['Ölçülüp biçilen şey yaratılır,', 'yaratılan bir huy kazanır;', 'düzlenen şey eskir ve yıpranır.'])
    kutu(b, 330, 400, 250, 75, 'DAYANAK', ['İbn Fâris, Mekâyîs: iki asıl', '(takdîr ve imlâs)'])
    kutu(b, 620, 260, 260, 90, 'İTİRAZ (istisna)', ['خَلُوق (koku) türemeyle', 'açıklanamıyor: kök dışı (R2)'], '#7a7a7a')
    ok(b, 270, 150, 620, 150); ok(b, 455, 250, 455, 158); ok(b, 455, 400, 455, 357); ok(b, 750, 260, 750, 212)
    kaydet('33_toulmin', '33. Toulmin delil şeması: kökün tek esasa irca edilmesi', 'Veri → (teminat, dayanak) → kayıtlı hüküm; itiraz ayrı kutuda.', b)
# 34 Wigmore
def wigmore():
    b = [DEF]; P = {'E': (450, 90)}; lv = collections.defaultdict(list)
    for m in MN: lv[min(depth(m), 3)].append(m)
    for d, ms in lv.items():
        for k, m in enumerate(ms): P[m] = (60 + (k + .5) * 780 / len(ms), 90 + d * 135)
    for m in MN:
        x, y = P[m]
        for p in MANA[m]['ebeveyn']:
            px, py = P[p]; b.append(f'<line x1="{x}" y1="{y-14}" x2="{px}" y2="{py+14}" stroke="{RENK[dal(m)]}" stroke-width="1.4" marker-end="url(#o)"/>')
    for m, (x, y) in P.items():
        if m == 'R2': b.append(f'<path d="M{x-13},{y+12} L{x},{y-13} L{x+13},{y+12}Z" fill="#fff" stroke="#7a7a7a" stroke-width="2"/>')
        elif WORDS_OF.get(m): b.append(f'<rect x="{x-12}" y="{y-12}" width="24" height="24" fill="#fff" stroke="{RENK[dal(m)]}" stroke-width="2"/>')
        else: b.append(f'<circle cx="{x}" cy="{y}" r="13" fill="#fff" stroke="{RENK[dal(m)]}" stroke-width="2"/>')
        b.append(T(str(ORDER.index(m)), x, y + 4, 10, w='font-weight="700"')); b.append(T(KISA[m], x, y + 28, 9.5))
    b.append(T('□ kelimeyle şahitli mana   ○ ara çıkarım   △ itiraz (kök dışı)   ok: "şunu destekler"', 450, 620, 11))
    kaydet('34_wigmore', '34. Wigmore delil cetveli: her mana esası destekleyen bir önerme', 'Numaralı semboller; okun ucu desteklenen önermeye gider.', b)
# 35 Isotype
def isotype():
    b = []; ms = [m for m in ORDER if WORDS_OF.get(m)]
    for j, m in enumerate(ms):
        y = 80 + j * 40; b.append(T(KISA[m], 170, y + 5, 11, 'end'))
        for k in range(len(WORDS_OF[m])):
            x = 190 + k * 34; c = RENK[dal(m)]
            b.append(f'<g transform="translate({x},{y-14})"><rect x="3" y="4" width="22" height="22" rx="3" fill="{c}"/><text x="14" y="21" text-anchor="middle" font-size="12" fill="#fff" font-family="Amiri,serif">خ</text></g>')
        b.append(AR('  '.join(KEL[w]['ar'] for w in WORDS_OF[m]), 870, y + 6, 13, 'end'))
    kaydet('35_isotype', '35. Isotype: bir işaret = bir kelime', 'Satır uzunluğu, o mananın kaç kelimeye yayıldığını sayısız gösterir.', b, 900, 80 + 40 * len(ms))
# 36 Bliss tarzı terkibî işaret
def bliss():
    b = []; ms = ORDER
    def isaret(m, x, y):
        s = [f'<line x1="{x-18}" y1="{y+18}" x2="{x+18}" y2="{y+18}" stroke="#2b2410" stroke-width="2"/>']   # zemin: esas
        d = dal(m); c = RENK[d]
        if d in ('A', 'AB'): s.append(f'<path d="M{x-14},{y+18} L{x},{y-10} L{x+14},{y+18}" stroke="{c}" fill="none" stroke-width="2.5"/>')  # ölçü: üçgen
        if d in ('B', 'AB'): s.append(f'<line x1="{x-16}" y1="{y+6}" x2="{x+16}" y2="{y+6}" stroke="{c}" stroke-width="2.5"/>')        # düz yüzey
        if d == 'C': s.append(f'<circle cx="{x}" cy="{y+4}" r="9" stroke="{c}" fill="none" stroke-width="2.5"/><line x1="{x}" y1="{y-5}" x2="{x}" y2="{y+13}" stroke="{c}" stroke-width="2"/>')
        if d == 'H': s.append(f'<path d="M{x-12},{y+4} Q{x},{y+16} {x+12},{y+4}" stroke="{c}" fill="none" stroke-width="2.5"/>')
        if d == 'R2': s.append(f'<path d="M{x-10},{y-6} Q{x},{y-20} {x+10},{y-6}" stroke="{c}" fill="none" stroke-width="2" stroke-dasharray="3 2"/>')
        for k in range(depth(m) - 1): s.append(f'<circle cx="{x+22}" cy="{y-8+k*8}" r="2.5" fill="#2b2410"/>')  # türeme basamağı
        return ''.join(s)
    for k, m in enumerate(ms):
        x = 70 + (k % 6) * 140; y = 110 + (k // 6) * 150
        b.append(isaret(m, x, y)); b.append(T(KISA[m], x, y + 44, 10.5))
    b.append(T('Zemin çizgisi = esas · üçgen = ölçmek · yatay çizgi = düz yüzey · daire = pay · kavis = yakışmak · noktalar = türeme basamağı', 450, 600, 10.5))
    kaydet('36_bliss', '36. Bliss tarzı terkibî işaret: her mana parçalardan kurulur', 'Parçaların manası kaynaktan değildir; bu levha için tayin edildi.', b, 900, 630)
# 37 I Ching (altı çizgilik kod)
def iching():
    b = []
    F = [('ölçmek kanadı', lambda m: dal(m) in ('A', 'AB')), ('düzleme kanadı', lambda m: dal(m) in ('B', 'AB')), ('pay/yakışma', lambda m: dal(m) in ('C', 'H')),
         ('2+ basamak', lambda m: depth(m) >= 2), ('insana dair', lambda m: m in ('U', 'X', 'Y', 'Z', 'H', 'C')), ('kelimesi var', lambda m: bool(WORDS_OF.get(m)))]
    for k, m in enumerate(ORDER):
        x = 60 + (k % 9) * 92; y = 80 + (k // 9) * 250
        for j, (ad, f) in enumerate(F):
            yy = y + 120 - j * 18; c = RENK[dal(m)]
            if f(m): b.append(f'<rect x="{x-24}" y="{yy}" width="48" height="10" fill="{c}"/>')
            else: b.append(f'<rect x="{x-24}" y="{yy}" width="20" height="10" fill="{c}"/><rect x="{x+4}" y="{yy}" width="20" height="10" fill="{c}"/>')
        b.append(T(KISA[m], x, y + 150, 10))
    for j, (ad, f) in enumerate(F): b.append(T(f'{j+1}. çizgi (alttan): {ad}', 60 + (j % 3) * 280, 590 + (j // 3) * 18, 10.5, 'start'))
    kaydet('37_iching', '37. I Ching tarzı altı çizgi: her mana altı evet/hayır vasfıyla', 'Bütün çizgi = evet, kırık çizgi = hayır. Vasıflar bu levha için seçildi.', b, 900, 640)
# 38 Peirce varoluş çizgesi
def peirce():
    b = []
    def cut(x, y, w, h): b.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="none" stroke="#2b2410" stroke-width="1.6"/>')
    pairs = [('A', 'D'), ('D', 'J'), ('J', 'K'), ('K', 'U'), ('U', 'X'), ('B', 'F'), ('B', 'N')]
    for k, (p, q) in enumerate(pairs):
        x = 30 + (k % 4) * 215; y = 80 + (k // 4) * 230
        cut(x, y, 200, 190); cut(x + 70, y + 80, 115, 90)
        b.append(T(KISA[p], x + 50, y + 100, 11, w='font-weight="700"')); b.append(T(KISA[q], x + 127, y + 130, 11, w=f'font-weight="700" fill="{RENK[dal(q)]}"'))
    x, y = 675, 310; b.append(T(KISA['R2'], x + 95, y + 100, 11, w='font-weight="700" fill="#7a7a7a"')); cut(x, y, 190, 180); b.append(T('خَلُوق', x + 95, y + 80, 12)); b.append(T('(esastan türemez)', x + 95, y + 125, 10))
    b.append(T('Kâğıt = doğru kabul edilen. Bir halka = değil. İç içe iki halka "p ise q" demektir: "p olup q olmaması değil".', 450, 560, 11))
    b.append(T('Misal: ilk çizge "ölçüp biçmek varsa yaratmak vardır" der. Son halka "koku manası esastan türer değil" der.', 450, 580, 11))
    kaydet('38_peirce', '38. Peirce varoluş çizgesi (alfa): türemeler şartlı önerme olarak', 'Halkalar (cut) olumsuzluktur; iç içe ikisi şart bildirir.', b, 900, 610)
# 39 Frege Begriffsschrift
def frege():
    b = []; y = 80
    for m in MN:
        if m == 'R2': continue
        p = MANA[m]['ebeveyn']; x0 = 40
        b.append(f'<line x1="{x0}" y1="{y-8}" x2="{x0}" y2="{y+8}" stroke="#2b2410" stroke-width="2"/>')  # hüküm çizgisi
        b.append(f'<line x1="{x0}" y1="{y}" x2="{x0+60}" y2="{y}" stroke="#2b2410" stroke-width="1.5"/>')
        b.append(T(KISA[m], x0 + 66, y + 4, 11, 'start', RENK[dal(m)], 'font-weight="700"'))
        for k, q in enumerate(p):
            yy = y + 16 * (k + 1); b.append(f'<line x1="{x0+30}" y1="{y}" x2="{x0+30}" y2="{yy}" stroke="#2b2410" stroke-width="1.5"/><line x1="{x0+30}" y1="{yy}" x2="{x0+60}" y2="{yy}" stroke="#2b2410" stroke-width="1.5"/>')
            b.append(T(KISA[q], x0 + 66, yy + 4, 10.5, 'start'))
        b.append(T(MANA[m]['sebep'][:70], 330, y + 4, 10, 'start', '#6d6650'))
        y += 16 * (len(p) + 1) + 8
    b.append(T('Dikey kısa çizgi: "hükmolunur". Aşağı inen kol: şart. Okunuşu: alttaki varsa üstteki vardır.', 450, y + 20, 11))
    kaydet('39_frege', '39. Frege kavram yazısı: her türeme bir şart hükmü', 'Sağda türemenin sebebi.', b, 900, y + 40)
# 40 Laws of Form
def lof():
    b = []
    def mark(x, y, w, h): b.append(f'<path d="M{x},{y+h} L{x+w},{y+h} L{x+w},{y}" stroke="#2b2410" stroke-width="1.8" fill="none"/>')
    def zincir(m):
        z = [m]
        while MANA[z[-1]]['ebeveyn']: z.append(MANA[z[-1]]['ebeveyn'][0])
        return z
    for k, m in enumerate(MN):
        z = list(reversed(zincir(m))); x0 = 30 + (k % 2) * 440; y0 = 74 + (k // 2) * 62
        b.append(T(' → '.join(KISA[q] for q in z), x0, y0 + 10, 10, 'start', RENK[dal(m)], 'font-weight="700"'))
        n = len(z)
        for j in range(n):
            mark(x0 + 4 * j, y0 + 16 + 5 * j, 40 + 60 * (n - j), 34 - 5 * j)
    b.append(T('Her köşe işareti (Spencer-Brown "cross") bir ayırım çizer; içteki, dıştakinin içinde ayırt edilmiştir.', 450, 630, 11))
    kaydet('40_laws_of_form', '40. Laws of Form: her türeme bir ayırımın içinde yeni ayırım', 'İşaretin iç içeliği = esastan o manaya kadar basamak sayısı.', b, 900, 650)
if __name__ == "__main__":
    for f in (psets, chord, halka, kucuk, zihin, toulmin, wigmore, isotype, bliss, iching, peirce, frege, lof): f()
print('tamam')
