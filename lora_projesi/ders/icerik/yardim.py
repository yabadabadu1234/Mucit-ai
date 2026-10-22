import html, math
import cizim as CZ
import pano as PN


def sayi(x, n=4):
    if x is None:
        return '?'
    s = ('%.' + str(n) + 'g') % x
    if 'e' in s:
        return s.replace('.', ',')
    return s.replace('.', ',')


def kutu(tur, metin, baslik=None):
    cls = {'not': 'not', 'uyari': 'uyari', 'ipucu': 'ipucu', 'hesap': 'hesapkutu', 'alistirma': 'alistirma'}[tur]
    b = '<b>%s</b> ' % baslik if baslik else ''
    return '<div class="%s">%s%s</div>' % (cls, b, metin)


def formul(t):
    return '<div class="formul">%s</div>' % t


def hesap(ad, varsayilan=None):
    import json
    v = ' data-varsayilan="%s"' % html.escape(json.dumps(varsayilan)) if varsayilan is not None else ''
    return '<div class="hesap hesapkutu" data-hesap="%s"%s></div>' % (ad, v)


def alistirma(soru, cevap):
    return '<div class="alistirma"><b>Alıştırma.</b> %s<details><summary>Cevabı göster</summary>%s</details></div>' % (soru, cevap)


def isaretli(maddeler):
    return '<ol class="isaretli">%s</ol>' % ''.join('<li>%s</li>' % m for m in maddeler)


def sema_kutusu(c):
    return '<div class="semakap">%s</div>' % c.svg()


def ag_tablosu(ver, aglar, aciklamalar=None):
    aciklamalar = aciklamalar or {}
    s = ['<table><tr><th>Ağ (tel) adı</th><th>Bağlı ayaklar</th><th>Ne taşır?</th></tr>']
    for ag in aglar:
        pins = ver.ag_pinleri(ag)
        txt = ', '.join('%s.%s' % (r, n) for r, n in pins)
        s.append('<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>' % (html.escape(ag), txt, aciklamalar.get(ag, '')))
    s.append('</table>')
    return ''.join(s)


def mesafe(ver, a, b):
    ka, kb = ver.d['konum'][a], ver.d['konum'][b]
    return math.hypot(ka['x'] - kb['x'], ka['y'] - kb['y'])


def pano_kutusu(ver, refs, isaretler=None, not_=None, pay=6, arka=False):
    d = ver.d
    kon = [d['konum'][r] for r in refs if r in d['konum']]
    x0 = min(k['x'] - k['g'] / 2 for k in kon) - pay
    x1 = max(k['x'] + k['g'] / 2 for k in kon) + pay
    y0 = min(k['y'] - k['y_'] / 2 for k in kon) - pay
    y1 = max(k['y'] + k['y_'] / 2 for k in kon) + pay
    w, h = x1 - x0, y1 - y0
    oran = 1.35
    if w / h < oran:
        nw = h * oran; x0 -= (nw - w) / 2; w = nw
    else:
        nh = w / oran; y0 -= (nh - h) / 2; h = nh
    svg = PN.pano_svg(d, vurgu=set(refs), kimlik='pano-' + str(abs(hash(tuple(refs))) % 99999), isaretler=isaretler, baslangic=(x0, y0, w, h))
    tam = (d['kart']['x'] - 3, d['kart']['y'] - 3, d['kart']['g'] + 6, d['kart']['y_'] + 6)
    kontrol = ('<div class="panokontrol"><label><input type="checkbox" data-katman="FCu" checked> Üst bakır</label>'
               '<label><input type="checkbox" data-katman="BCu" checked> Alt bakır</label>'
               '<label><input type="checkbox" data-katman="ipek" checked> Serigrafi</label>'
               '<label><input type="checkbox" data-katman="viya" checked> Delikli geçitler</label>'
               '<label><input type="checkbox" data-katman="ref" checked> Parça adları</label>'
               '<button data-sifirla>Tüm kart</button>'
               '<button data-git="%s,%s,%s,%s">Bu bölüm</button></div>') % tuple(round(v, 2) for v in (x0, y0, w, h))
    return ('<div class="panokap">' + kontrol + '<div class="panoalan">' + svg.replace('class="k-ipek"', 'class="k-ipek"') + '</div>'
            '<div class="panobilgi">Tekerlekle yaklaş, sürükleyerek kaydır. Bir bakır izine, ayağa ya da yazıya tıkla: o ağ vurgulanır ve hangi ayaklara gittiği yazılır.</div></div>'
            + ('<p class="kaynak">%s</p>' % not_ if not_ else ''))


def iz_uzunlugu(ver, ag):
    t = 0.0
    for i in ver.d['izler']:
        if i['ag'] == ag:
            x1, y1, x2, y2 = i['p']
            t += math.hypot(x2 - x1, y2 - y1)
    return t


def viya_sayisi(ver, ag):
    return sum(1 for v in ver.d['viyalar'] if v['ag'] == ag)


def mikroserit(w, h, t, er):
    """Hammerstad yaklasimi, mikroserit karakteristik empedansi (ohm)."""
    we = w + (t / math.pi) * (1 + math.log(2 * h / t))
    u = we / h
    if u <= 1:
        ee = (er + 1) / 2 + (er - 1) / 2 * ((1 + 12 / u) ** -0.5 + 0.04 * (1 - u) ** 2)
        z = 60 / math.sqrt(ee) * math.log(8 / u + u / 4)
    else:
        ee = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 / u) ** -0.5
        z = 120 * math.pi / (math.sqrt(ee) * (u + 1.393 + 0.667 * math.log(u + 1.444)))
    return z, ee


def iz_genislikleri(ver, ag):
    return sorted({i['w'] for i in ver.d['izler'] if i['ag'] == ag})


import json as _json, os as _os
_K = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def sim_veri(ad):
    return _json.load(open(_os.path.join(_K, 'veri', ad + '.json')))


def _guzel(a, b, n=5):
    aralik = b - a or 1
    adim = 10 ** math.floor(math.log10(aralik / n))
    for m in (1, 2, 2.5, 5, 10):
        if aralik / (adim * m) <= n:
            adim *= m
            break
    t = math.ceil(a / adim) * adim
    out = []
    while t <= b + 1e-9:
        out.append(round(t, 10)); t += adim
    return out


def grafik(x, seriler, xetiket, yetiket, genislik=760, yukseklik=300, cizgiler=(), ymin=None, ymax=None):
    """seriler: [(ad, [y...], renk)]; cizgiler: [(deger, metin)] yatay referans cizgileri."""
    L, R, T, B = 62, 150, 16, 46
    W, H = genislik, yukseklik
    xs0, xs1 = min(x), max(x)
    tum = [v for _, ys, _ in seriler for v in ys] + [c[0] for c in cizgiler]
    y0 = min(tum) if ymin is None else ymin
    y1 = max(tum) if ymax is None else ymax
    pad = (y1 - y0) * 0.06 or 1
    y0 -= pad if ymin is None else 0; y1 += pad if ymax is None else 0
    def X(v): return L + (v - xs0) / ((xs1 - xs0) or 1) * (W - L - R)
    def Y(v): return T + (1 - (v - y0) / ((y1 - y0) or 1)) * (H - T - B)
    s = ['<svg class="grafik" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" style="width:100%%;height:auto;font-family:Inter,sans-serif">' % (W, H)]
    s.append('<rect x="%d" y="%d" width="%d" height="%d" fill="var(--panel)" stroke="var(--cizgi)"/>' % (L, T, W - L - R, H - T - B))
    for t in _guzel(y0, y1):
        s.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="var(--cizgi)" stroke-width="0.7"/><text x="%d" y="%.1f" text-anchor="end" font-size="11" fill="var(--soluk)">%s</text>' % (L, W - R, Y(t), Y(t), L - 6, Y(t) + 4, sayi(t, 4)))
    for t in _guzel(xs0, xs1):
        s.append('<line y1="%d" y2="%d" x1="%.1f" x2="%.1f" stroke="var(--cizgi)" stroke-width="0.7"/><text y="%d" x="%.1f" text-anchor="middle" font-size="11" fill="var(--soluk)">%s</text>' % (T, H - B, X(t), X(t), H - B + 16, X(t), sayi(t, 4)))
    for deger, metin in cizgiler:
        s.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="var(--vurgu)" stroke-dasharray="5 4"/><text x="%d" y="%.1f" font-size="11" fill="var(--vurgu)">%s</text>' % (L, W - R, Y(deger), Y(deger), W - R + 6, Y(deger) + 4, escape_(metin)))
    ly = T + 12
    for ad, ys, renk in seriler:
        pts = ' '.join('%.1f,%.1f' % (X(a), Y(b)) for a, b in zip(x, ys))
        s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, renk))
        s.append('<line x1="%d" x2="%d" y1="%d" y2="%d" stroke="%s" stroke-width="3"/><text x="%d" y="%d" font-size="12" fill="var(--yazi)">%s</text>' % (W - R + 6, W - R + 26, ly + 20 * len(cizgiler) + 14 * 0, ly + 20 * len(cizgiler), renk, W - R + 30, ly + 4 + 20 * len(cizgiler), escape_(ad)))
        ly += 18
    s.append('<text x="%d" y="%d" text-anchor="middle" font-size="12" fill="var(--yazi)">%s</text>' % ((L + W - R) / 2, H - 6, escape_(xetiket)))
    s.append('<text transform="rotate(-90 14 %d)" x="14" y="%d" text-anchor="middle" font-size="12" fill="var(--yazi)">%s</text>' % ((T + H - B) / 2, (T + H - B) / 2, escape_(yetiket)))
    s.append('</svg>')
    return '<div class="semakap">' + ''.join(s) + '</div>'


def escape_(t):
    return html.escape(t)


def ipc_genislik(akim, dT=10.0, dis=True, t_um=35.0):
    """IPC-2221 yaklasimi: gereken iz genisligi (mm)."""
    k = 0.048 if dis else 0.024
    alan_mil2 = (akim / (k * dT ** 0.44)) ** (1 / 0.725)
    return alan_mil2 / (t_um / 25.4) * 0.0254


def iz_taramasi(ver, satirlar):
    """satirlar: [(ag, akim_A, aciklama)] -> HTML tablo; kartta olculen en dar iz genisligiyle IPC gereksinimini kiyaslar."""
    s = ['<table><tr><th>Ağ</th><th>Beklenen akım</th><th>Dayanak</th><th>Gereken iz (10 °C artış, 35 µm dış)</th><th>Kartta ölçülen</th><th>Sonuç</th></tr>']
    for ag, akim, ac in satirlar:
        ws = iz_genislikleri(ver, ag)
        gerek = ipc_genislik(akim)
        if ws:
            en = min(ws)
            ok = en + 1e-9 >= gerek
            durum = '<b style="color:var(--yesil)">yeterli</b>' if ok else '<b style="color:var(--vurgu)">YETERSİZ</b>'
            olc = ', '.join(sayi(w) for w in ws) + ' mm'
        else:
            durum = 'iz yok (döküm/ped)'; olc = '—'
        s.append('<tr><td><code>%s</code></td><td>%s A</td><td>%s</td><td>≈ %s mm</td><td>%s</td><td>%s</td></tr>' % (ag, sayi(akim, 3), ac, sayi(gerek, 3), olc, durum))
    s.append('</table>')
    return ''.join(s)
