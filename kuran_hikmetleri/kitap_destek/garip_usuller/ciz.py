import html, math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
esc = html.escape
def svg(ad, W, H, b):
    (HERE / f'{ad}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, DejaVu Sans, sans-serif"><rect width="100%" height="100%" fill="#fffdf6"/>' + ''.join(b) + '</svg>', encoding='utf-8')

# ---------------- 1. Anlam asalları (NSM) ----------------
# Her mana yalnız evrensel asal kelimelerle tarif edilir. Satırlar ortak; manalar satır ekleyip çıkararak ayrılır.
S = {
 'L1': 'BİRİ, BİR ŞEY İÇİN BİR ŞEY YAPTI',
 'L2': 'ÖNCE BU KİŞİ ŞÖYLE DÜŞÜNDÜ: "BU ŞEY ŞÖYLE OLSUN İSTİYORUM"',
 'L3': 'ÖNCE BU ŞEY BÖYLE DEĞİLDİ',
 'L4': 'BU KİŞİ BU ŞEYİN NE KADAR BÜYÜK OLACAĞINI BİLMEK İÇİN BİR ŞEY YAPTI (ölçtü)',
 'L5': 'BUNUN YÜZÜNDEN, SONRA BU ŞEY BU KİŞİNİN İSTEDİĞİ GİBİ OLDU',
 'L6': 'ÖNCE BU ŞEY HİÇ YOKTU',
 'L7': 'BU YAPAN İNSAN DEĞİL; BUNU YALNIZ ALLAH YAPABİLİR',
 'L8': 'BU ŞEY ŞİMDİ VAR, ÇÜNKÜ BİRİ ONU BÖYLE YAPTI',
 'L9': 'BU ŞEY BİRİNİN İÇİNDE; BU KİŞİ ÇOK ZAMAN BÖYLE DÜŞÜNÜR, BÖYLE YAPAR',
 'L10': 'BU KİŞİ BUNU DÜŞÜNMEDEN YAPAR',
 'L11': 'BİRİ BİR ŞEY SÖYLEDİ; BU ŞEY DOĞRU DEĞİL',
 'L12': 'BU KİŞİ İNSANLARIN "BU DOĞRU" DÜŞÜNMESİNİ İSTEDİ',
 'L13': 'BU ŞEY ÇOK ZAMAN BİR ŞEYE DOKUNDU; BUNUN YÜZÜNDEN ÜSTÜ DÜZ OLDU, ESKİ OLDU',
 'L14': 'BİRİ İÇİN BİR ŞEYİN BİR PARÇASI; BU PARÇA BU KİŞİ İÇİN İYİ',
 'L15': 'BU ŞEY BİR ŞEY İÇİN İYİ, ÇÜNKÜ ONUN İÇİN BÖYLE YAPILDI',
}
M = [('ESAS: ölçüp biçerek hazırlamak', ['L1','L2','L3','L4','L5']),
     ('yaratmak (Allah için)', ['L1','L2','L6','L5','L7']),
     ('yaratılmış (mahlûk)', ['L8','L6']),
     ('huy', ['L8','L9','L10']),
     ('uydurmak', ['L1','L2','L11','L12']),
     ('eskimek', ['L13']),
     ('nasip, pay', ['L4','L14']),
     ('lâyık', ['L15','L2'])]
keys = list(S)
CW, LW, RH, T = 120, 640, 34, 210
W = LW + CW * len(M) + 40; H = T + RH * len(keys) + 140
b = [f'<text x="20" y="36" font-size="22" font-weight="700">1. Anlam asalları (Natural Semantic Metalanguage)</text>',
     f'<text x="20" y="60" font-size="13" fill="#555">Her mana yalnız ~65 evrensel "asal" kelimeyle (BİRİ, BİR ŞEY, YAPMAK, DÜŞÜNMEK, İSTEMEK, ÖNCE, SONRA, BUNUN YÜZÜNDEN…) yazılır.</text>',
     f'<text x="20" y="80" font-size="13" fill="#555">Satırlar manalar arasında ortaktır; iki mana arasındaki fark, eklenen ve düşen satırlardır. Bu tarifler benim yazdığım taslaktır.</text>']
for j, (ad, ls) in enumerate(M):
    x = LW + j * CW + CW / 2
    b.append(f'<text transform="translate({x+5},{T-12}) rotate(-50)" font-size="12.5" font-weight="700" fill="#2b2410">{esc(ad)}</text>')
for i, k in enumerate(keys):
    y = T + i * RH
    if i % 2 == 0: b.append(f'<rect x="12" y="{y}" width="{W-24}" height="{RH}" fill="#f4efe0" opacity=".6"/>')
    b.append(f'<text x="20" y="{y+22}" font-size="12" font-family="DejaVu Sans Mono, monospace" fill="#2b2410">{esc(S[k])}</text>')
    for j, (ad, ls) in enumerate(M):
        if k in ls:
            x = LW + j * CW + CW / 2
            b.append(f'<circle cx="{x}" cy="{y+RH/2}" r="9" fill="#2f6fb3"/>')
# bağlar: aynı satırı taşıyan manalar arasında yatay çizgi
for i, k in enumerate(keys):
    js = [j for j, (ad, ls) in enumerate(M) if k in ls]
    if len(js) > 1:
        y = T + i * RH + RH / 2
        b.append(f'<line x1="{LW+js[0]*CW+CW/2}" y1="{y}" x2="{LW+js[-1]*CW+CW/2}" y2="{y}" stroke="#2f6fb3" stroke-width="2" opacity=".5"/>')
b.append(f'<text x="20" y="{T+RH*len(keys)+40}" font-size="12.5" fill="#555">Okuyuş: "yaratmak" = ESAS − L3 − L4 + L6 + L7  ·  "uydurmak" = ESAS − L3 − L4 − L5 + L11 + L12  ·  "huy" = yaratılmış + L9 + L10</text>')
svg('1_anlam_asallari', W, H, b)

# ---------------- 2. Metin devresi (DisCoCirc) ----------------
# Teller = katılanlar (yapan, madde, hedef). Kutular = süreçler. Türeyen mana = devrenin bir telini ya da kutusunu değiştirmek.
def devre(x0, y0, baslik, teller, kutular, not_):
    o = [f'<text x="{x0}" y="{y0}" font-size="15" font-weight="700" fill="#2b2410">{esc(baslik)}</text>']
    ty = {t: y0 + 40 + k * 46 for k, (t, _) in enumerate(teller)}
    xe = x0 + 560
    for t, c in teller:
        o.append(f'<line x1="{x0+90}" y1="{ty[t]}" x2="{xe}" y2="{ty[t]}" stroke="{c}" stroke-width="4"/>')
        o.append(f'<text x="{x0+84}" y="{ty[t]+5}" text-anchor="end" font-size="12" font-weight="700" fill="{c}">{esc(t)}</text>')
    for k, (ad, tl, renk) in enumerate(kutular):
        x = x0 + 120 + k * 110
        ys = [ty[t] for t in tl]
        o.append(f'<rect x="{x}" y="{min(ys)-16}" width="92" height="{max(ys)-min(ys)+32}" rx="6" fill="{renk}" stroke="#2b2410" stroke-width="1.4"/>')
        o.append(f'<text x="{x+46}" y="{(min(ys)+max(ys))/2+4}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">{esc(ad)}</text>')
    o.append(f'<text x="{x0}" y="{max(ty.values())+44}" font-size="11.5" fill="#555">{esc(not_)}</text>')
    return o
Y1, Y2, Y3 = '#2f6fb3', '#c26a1e', '#3f8f3a'
b = [f'<text x="20" y="36" font-size="22" font-weight="700">2. Metin devresi (DisCoCirc): mana, katılanların tellerinde akan bir süreçtir</text>',
     f'<text x="20" y="60" font-size="13" fill="#555">Her tel bir katılan; kutu bir süreç ve dokunduğu tellerin hâlini değiştirir. Türeyen mana, ESAS devresinde bir teli ya da kutuyu değiştirmekle elde edilir.</text>']
b += devre(20, 110, 'ESAS: ölçüp biçerek hazırlamak', [('yapan', Y1), ('ham madde', Y2)],
           [('niyet', ['yapan'], '#2b2410'), ('ölç', ['yapan', 'ham madde'], Y1), ('biç', ['yapan', 'ham madde'], Y1), ('hazır', ['ham madde'], Y3)], 'Ham madde teli sonunda "murad edilen şey" hâline girer.')
b += devre(660, 110, 'yaratmak: ham madde teli YOKTAN başlar', [('yapan', Y1), ('(yok)→şey', '#999')],
           [('niyet', ['yapan'], '#2b2410'), ('takdir', ['yapan', '(yok)→şey'], Y1), ('var et', ['yapan', '(yok)→şey'], Y1), ('düzen', ['(yok)→şey'], Y3)], 'Değişen: madde teli; kalan devre aynı.')
b += devre(20, 330, 'uydurmak: madde teli SÖZ olur, hedefe DİNLEYEN eklenir', [('yapan', Y1), ('söz', Y2), ('dinleyen', '#a8478f')],
           [('niyet', ['yapan'], '#2b2410'), ('ölç', ['yapan', 'söz'], Y1), ('kur', ['yapan', 'söz'], Y1), ('inandır', ['söz', 'dinleyen'], '#a8478f')], 'Devre aynı, tel türü değişti: istiare (benzerlik).')
b += devre(660, 330, 'huy: biçilen şey KİŞİNİN KENDİSİDİR', [('yaratan', Y1), ('kişi', Y2), ('kişinin işleri', Y3)],
           [('takdir', ['yaratan', 'kişi'], Y1), ('biç', ['yaratan', 'kişi'], Y1), ('yerleş', ['kişi'], Y3), ('çıkar', ['kişi', 'kişinin işleri'], Y3)], 'Biçilen madde insanın içi; çıktısı düşünmeden yapılan işler.')
svg('2_metin_devresi', 1300, 600, b)

# ---------------- 3. Kipu (düğümlü ip) ----------------
# Ana ip = kök. Sarkan ip = dal. Düğüm konumu = köke uzaklık. Düğüm türü: tek düğüm bitişiklik, uzun düğüm benzerlik. Yan ip = alt dal.
D = [('ölçüp biçme', '#2f6fb3', [('yaratmak', 1, 'b', [('yaratılmış', 2, 'b', []), ('yaradılış', 2, 'b', [('huy', 3, 'u', [('ahlâk', 4, 'u', []), ('öfke', 4, 'u', []), ('takınmak', 4, 'u', [])])]), ('uydurmak', 2, 'u', [])])]),
     ('düzleme', '#3f8f3a', [('eskimek', 1, 'b', []), ('koku sürmek', 1, 'b', []), ('şekli belirmiş', 1, 'b', [])]),
     ('pay', '#c26a1e', []), ('yakışmak', '#a8478f', [])]
W, H = 1520, 900
b = [f'<text x="20" y="36" font-size="22" font-weight="700">3. Kipu: kökün manaları düğümlü iplere işlenir</text>',
     f'<text x="20" y="60" font-size="13" fill="#555">Ana ip = kök. Sarkan ip = dal. Düğümün ipteki yüksekliği = köke uzaklık. Yuvarlak düğüm: bitişiklikle türeyen mana; uzun düğüm: benzerlikle (istiare).</text>',
     f'<text x="20" y="80" font-size="13" fill="#555">Yan ipler alt dallardır. Bir kere düğüm dili öğrenilince ip elle de okunur (İnka kipuları sayıları böyle saklardı).</text>']
b.append(f'<path d="M60,130 C400,110 1000,150 1460,125" fill="none" stroke="#8a6d3b" stroke-width="10" stroke-linecap="round"/>')
b.append(f'<text x="640" y="112" text-anchor="middle" font-size="24" font-family="Amiri, serif">خلق</text>')
def ip(x, y, renk, kollar, derin=0):
    o = []
    L = 140 + 120 * max([1] + [k[1] for k in kollar]) if kollar else 160
    o.append(f'<path d="M{x},{y} C{x-8},{y+L*0.4} {x+8},{y+L*0.7} {x},{y+L}" fill="none" stroke="{renk}" stroke-width="5" stroke-linecap="round"/>')
    return o, L
def dugum(x, y, tur, renk, ad):
    if tur == 'b':
        return [f'<circle cx="{x}" cy="{y}" r="9" fill="{renk}" stroke="#2b2410" stroke-width="1.5"/>', f'<text x="{x+14}" y="{y+4}" font-size="11" fill="#2b2410">{esc(ad)}</text>']
    return [f'<rect x="{x-7}" y="{y-16}" width="14" height="32" rx="7" fill="{renk}" stroke="#2b2410" stroke-width="1.5"/>', f'<text x="{x+14}" y="{y+4}" font-size="11" fill="#2b2410">{esc(ad)}</text>']
xs = [180, 640, 1230, 1400]
for (dad, renk, kollar), x in zip(D, xs):
    y = 135
    b.append(f'<path d="M{x},{y} L{x},{y+700}" fill="none" stroke="{renk}" stroke-width="5"/>')
    b.append(f'<text x="{x+10}" y="{y+22}" font-size="12.5" font-weight="700" fill="{renk}">{esc(dad)}</text>')
    def isle(xx, kollar, yan):
        for k, (ad, d, t, alt) in enumerate(kollar):
            yy = 135 + 60 + d * 130
            xk = xx + k * yan
            if xk != xx:
                b.append(f'<path d="M{xx},{yy-60} C{xx+yan*0.2},{yy-40} {xk},{yy-50} {xk},{yy}" fill="none" stroke="{renk}" stroke-width="3"/>')
            b.extend(dugum(xk, yy, t, renk, ad))
            if alt: isle(xk, alt, 120)
    isle(x, kollar, 150)
svg('3_kipu', W, H, b)
print('tamam')
