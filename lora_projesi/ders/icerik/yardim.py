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
