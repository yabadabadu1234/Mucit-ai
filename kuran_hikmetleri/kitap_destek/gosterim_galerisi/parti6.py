from ortak import *
def kel(m): return [KEL[w]['ar'] for w in WORDS_OF.get(m, [])]
RK = lambda m: '#b8860b' if m == 'E' else RENK[dal(m)]
CH = {m: [c for c in KIDS.get(m, []) if MANA[c]['ebeveyn'][0] == m] for m in MANA}
# 154 L-sistemi
def lsistem():
    b = []
    kural = [f'{m} → {m}' + ''.join(f'[{c}]' for c in CH[m]) for m in ORDER if CH[m]]
    b.append(T('Başlangıç (aksiyom): E', 30, 80, 12, 'start', w='font-weight="700"'))
    for k, r in enumerate(kural): b.append(f'<text x="30" y="{104+k*18}" font-family="DejaVu Sans Mono, monospace" font-size="12" fill="#2b2410">{esc(r)}</text>')
    y0 = 104 + len(kural) * 18 + 10
    b.append(T('E=esas · A=ölçmek · B=düzlemek · C=pay · H=yakışmak · D=yaratmak · J=yaratılmış · K=yaradılış · L=uydurmak', 30, y0, 10, 'start', '#6d6650'))
    b.append(T('U=huy · X=ahlâk · Y=öfke · Z=huy takınmak · N=şekli belirmiş · F=eskimek · G=koku', 30, y0 + 14, 10, 'start', '#6d6650'))
    def ac(s, n):
        for _ in range(n):
            o = ''
            for ch in s:
                o += ch + ''.join(f'[{c}]' for c in CH.get(ch, [])) if ch in MANA and ch not in o[-1:] else ch
            s = o
        return s
    def tekrar(n):
        s = 'E'
        for _ in range(n):
            o = ''; i = 0
            while i < len(s):
                ch = s[i]
                if s[i:i+2] == 'R2': o += 'R2'; i += 2; continue
                o += ch
                if ch in MANA and (i + 1 >= len(s) or s[i+1] != '#'): o += '#' + ''.join(f'[{c}]' for c in CH.get(ch, []))
                i += 1
            s = o
        return s.replace('#', '')
    yy = 300
    for n in range(4):
        s = tekrar(n); b.append(f'<text x="30" y="{yy}" font-family="DejaVu Sans Mono, monospace" font-size="11" fill="#2b2410">n={n}: {esc(s[:110])}</text>'); yy += 16
    # kaplumbağa
    def ciz(x, y, a, m, L, d):
        x2, y2 = x + L * math.cos(a), y - L * math.sin(a)
        b.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{RK(m)}" stroke-width="{max(1.5,7-1.4*d)}" stroke-linecap="round"/>')
        ch = CH.get(m, [])
        if not ch:
            b.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="4" fill="{RK(m)}"/>'); b.append(T(KISA[m], x2, y2 - 8, 9.5, fill=RK(m), w='font-weight="700"'))
        else:
            b.append(T(KISA[m], x2 + 4, y2 + 3, 8.5, 'start', '#6d6650'))
        sp = 0.62
        for k, c in enumerate(ch): ciz(x2, y2, a + (k - (len(ch) - 1) / 2) * sp, c, L * 0.78, d + 1)
    ciz(620, 650, math.pi / 2, 'E', 120, 0)
    b.append(T('Kaideler üst üste işletilince ağaç kendiliğinden büyür; her dal bir kaidenin izidir.', 450, 670, 11))
    kaydet('154_lsistemi', '154. Yeniden yazma kaideleri (Lindenmayer sistemi): kaidelerden büyüyen bitki', 'Sol üstte kaideler, altta her adımda dizinin hâli, sağda kaplumbağa çizimi.', b, 900, 690)
# 155 Grup yörüngesi
def grup():
    b = []; cx, cy = 450, 360
    O = [('id', 'kök (fiil, I)', 'خَلَقَ', '#b8860b'), ('φ', 'fâil: فَاعِل', 'خَالِق', '#2f6fb3'), ('μ', 'mef\'ûl: مَفْعُول', 'مَخْلُوق', '#2f6fb3'), ('σ', 'masdar: فَعْل', 'خَلْق', '#2f6fb3'),
         ('τ', 'II. bâb: فَعَّلَ', 'خَلَّقَ', '#3f8f3a'), ('τμ', 'II. bâbın mef\'ûlü', 'مُخَلَّق', '#2c8c7c'), ('ε', 'V. bâb: تَفَعَّلَ', 'تَخَلَّقَ', '#7a3fb3'), ('ι', 'VIII. bâb: اِفْتَعَلَ', 'اِخْتَلَقَ', '#c0392b'),
         ('ισ', 'VIII. bâbın masdarı', 'اِخْتِلَاق', '#c0392b'), ('ιμ', 'VIII. bâbın mef\'ûlü', 'مُخْتَلَق', '#c0392b'), ('ιφ', 'VIII. bâbın fâili', 'مُخْتَلِق', '#c0392b'), ('ψ', 'fu\'ul: فُعُل', 'خُلُق', '#7a3fb3'), ('ψπ', 'cem\'i: أَفْعَال', 'أَخْلَاق', '#7a3fb3'), ('ρ', 'fe\'îl: فَعِيل', 'خَلِيق', '#a8478f')]
    n = len(O) - 1
    for k, (s, ad, ar, c) in enumerate(O[1:]):
        a = -math.pi / 2 + 2 * math.pi * k / n; L = 230 if len(s) == 1 else 290
        x, y = cx + L * math.cos(a), cy + L * math.sin(a)
        px, py = -math.sin(a) * 26, math.cos(a) * 26
        b.append(f'<path d="M{cx},{cy} Q{cx+L*.55*math.cos(a)+px:.1f},{cy+L*.55*math.sin(a)+py:.1f} {x:.1f},{y:.1f} Q{cx+L*.55*math.cos(a)-px:.1f},{cy+L*.55*math.sin(a)-py:.1f} {cx},{cy}" fill="{c}" fill-opacity=".18" stroke="{c}" stroke-width="1.5"/>')
        b.append(AR(ar, x + 30 * math.cos(a), y + 30 * math.sin(a) + 6, 16, fill=c)); b.append(T(s, cx + L * .6 * math.cos(a), cy + L * .6 * math.sin(a) + 4, 12, fill=c, w='font-weight="700" font-style="italic"'))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="38" fill="#e8c766"/>'); b.append(AR('خلق', cx, cy + 8, 24))
    b.append(T('Kelime = dönüşüm(kök). Bileşik dönüşüm: ιμ = μ∘ι (önce VIII. bâb, sonra mef\'ûl). ψπ = cem\'∘fu\'ul.', 450, 680, 11.5, w='font-weight="700"'))
    b.append(T('Kısa yaprak tek dönüşüm, uzun yaprak iki dönüşümün bileşkesi. Aynı dönüşümler başka köke uygulanınca aynı desen çıkar.', 450, 700, 10.5, fill='#6d6650'))
    kaydet('155_grup_yorungesi', '155. Cebir: vezinler kök üstünde işleyen dönüşümler, kelimeler kökün yörüngesi', 'Harfler dönüşümün adı (φ fâil, μ mef\'ûl, ι ifti\'âl…).', b, 900, 720)
# 156 Fourier
def fourier():
    b = []
    H = {'E': 1, 'A': 2, 'B': 3, 'C': 4, 'H': 5}
    def dalga(fn, x0, y0, w, h, c, sw=2):
        pts = ' '.join(f'{x0+i*w/200:.1f},{y0-h*fn(2*math.pi*i/200):.1f}' for i in range(201))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{sw}"/>'); b.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+w}" y2="{y0}" stroke="#ddd"/>')
    yy = 100
    for m, k in H.items():
        a = 1 if m == 'E' else 0.3 + 0.07 * len(alt_say(m))
        dalga(lambda t, k=k, a=a: a * math.sin(k * t), 200, yy, 280, 22, RK(m)); b.append(T(f'{KISA[m]}  =  {a:.2f}·sin({k}x)', 30, yy + 4, 11, 'start', RK(m), 'font-weight="700"')); yy += 70
    b.append(T('TEMEL DALGA VE HARMONİKLER', 340, 70, 12, w='font-weight="700"')); b.append(T('KELİME = TOPLAM', 720, 70, 12, w='font-weight="700"'))
    W2 = [('خَلَقَ', ['E', 'A']), ('خُلُق', ['E', 'A']), ('خَلِقَ', ['E', 'B']), ('مُخَلَّق', ['E', 'A', 'B']), ('خَلَاق', ['E', 'C']), ('خَلِيق', ['E', 'H'])]
    for j, (ar, ms) in enumerate(W2):
        y = 100 + j * 92
        fn = lambda t, ms=ms: sum((1 if m == 'E' else 0.6) * math.sin(H[m] * t) for m in ms) / 1.6
        dalga(fn, 560, y, 280, 26, '#2b2410', 2.2); b.append(AR(ar, 870, y + 6, 15, 'start')); b.append(T(' + '.join(KISA[m] for m in ms), 700, y + 40, 9.5, fill='#6d6650'))
    b.append(T('Esas her kelimede temel dalga olarak vardır; dal, kelimeye kendi harmoniğini ekler. Aynı daldaki kelimelerin dalga şekli birbirine benzer.', 450, 670, 11))
    b.append(T('Frekans ve genlik tayini bu levha için yapılmıştır. Zaaf: خَلَقَ ile خُلُق aynı dalga çıkar; aynı daldaki kelimeleri ayırmak için ikinci bir harmonik lazım.', 450, 688, 10, fill='#6d6650'))
    kaydet('156_fourier', '156. Harmonik açılım (Fourier): esas temel dalga, her dal bir harmonik, kelime toplam dalga', 'Kelimeyi duymak, ona karışan harmonikleri duymaktır.', b, 900, 700)
# 157 Fonksiyon eğrisi
def fonksiyon():
    b = []; x0, y0, W, H = 90, 600, 760, 480
    b.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+W}" y2="{y0}" stroke="#2b2410" stroke-width="2"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0-H}" stroke="#2b2410" stroke-width="2"/>')
    b.append(T('x: dıştan içe (eşyadan nefse)  →', x0 + W, y0 + 30, 11.5, 'end', w='font-weight="700"')); b.append(f'<text transform="translate({x0-50},{y0-H/2}) rotate(-90)" text-anchor="middle" font-size="11.5" font-weight="700" fill="#2b2410">y = f(x): kökten uzaklık (türeme basamağı)</text>')
    P1 = [(0.0, 'E'), (0.14, 'A'), (0.3, 'D'), (0.45, 'J'), (0.6, 'K'), (0.78, 'U'), (0.95, 'X')]
    P2 = [(0.0, 'E'), (0.08, 'B'), (0.18, 'N'), (0.12, 'F')]
    def pt(x, m): return x0 + x * W, y0 - depth(m) * (H / 5.4)
    for P, c, ad in [(P1, '#2f6fb3', 'ölçme kolu: f₁(x)'), ([(0.0, 'E'), (0.06, 'B'), (0.1, 'F')], '#3f8f3a', 'düzleme kolu: f₂(x)')]:
        pts = [pt(x, m) for x, m in P]
        d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}' + ''.join(f' C{(pa[0]+pb[0])/2:.1f},{pa[1]:.1f} {(pa[0]+pb[0])/2:.1f},{pb[1]:.1f} {pb[0]:.1f},{pb[1]:.1f}' for pa, pb in zip(pts, pts[1:]))
        b.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="3"/>')
        for (x, y), (_, m) in zip(pts, P):
            sol = c == '#3f8f3a' and m != 'E'; dx = -8 if sol else 8; an = 'end' if sol else 'start'
            b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{RK(m)}"/>'); b.append(T(KISA[m], x + dx, y - 8, 10.5, an, RK(m), 'font-weight="700"')); b.append(AR((kel(m) or [''])[0], x + dx, y + 14, 13, an))
        b.append(T(ad, pts[-1][0] + (10 if c != '#3f8f3a' else -10), pts[-1][1] - 30, 11, 'start' if c != '#3f8f3a' else 'end', c, 'font-style="italic"'))
    for x, m in [(0.82, 'Y'), (0.88, 'Z'), (0.36, 'L'), (0.2, 'C'), (0.25, 'H'), (0.17, 'G')]:
        px, py = pt(x, m); b.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="none" stroke="{RK(m)}" stroke-width="2"/>'); b.append(T(KISA[m], px + 7, py + 4, 9.5, 'start', RK(m)))
    b.append(T('Eğri boyunca ilerlemek hem içe girmek hem kökten uzaklaşmaktır: f₁ artandır. Düzleme kolu (f₂) eşya tarafında kalır, içe girmez.', 450, 650, 11))
    b.append(T('Boş halkalar eğrinin dışında kalan ayrık noktalar (dallanma). x değerleri kıyas içindir, ölçülmemiştir.', 450, 668, 10, fill='#6d6650'))
    kaydet('157_fonksiyon', '157. Fonksiyon eğrisi: mana = f(dıştan içe değişkeni)', 'Tek değişken seçilir; manalar o değişkenin fonksiyonu olarak bir eğri üstüne düşer.', b, 900, 690)
for f in (lsistem, grup, fourier, fonksiyon): f()
print('tamam')
