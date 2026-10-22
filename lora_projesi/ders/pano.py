import math
from html import escape

RENK = {'F.Cu': '#c8423b', 'B.Cu': '#3f78d6', 'pad': '#d8b24a', 'ipek': '#e8e8e8', 'avlu': '#6b7a6b', 'kenar': '#f2d64b', 'viya': '#9fd3a8'}


def pano_svg(d, vurgu=(), kimlik='pano', isaretler=None, arka=False, baslangic=None, ipek=True, etiket=True):
    """d: veri JSON. vurgu: ref kumesi. isaretler: [(no, ref)] pano uzerinde numarali isaret."""
    vurgu = set(vurgu)
    kx, ky, kw, kh = d['kart']['x'], d['kart']['y'], d['kart']['g'], d['kart']['y_']
    pay = 3
    vb = baslangic or (kx - pay, ky - pay, kw + 2 * pay, kh + 2 * pay)
    s = []
    s.append('<svg class="pano" id="%s" viewBox="%s %s %s %s" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Kart gorunumu">' % ((kimlik,) + tuple(round(v, 2) for v in vb)))
    s.append('<rect x="%s" y="%s" width="%s" height="%s" fill="#12301f" />' % (kx - 50, ky - 50, kw + 100, kh + 100))
    # kart govdesi
    yol = []
    for e in d['kenar']:
        p = e['p']
        if e['t'] == 's':
            yol.append('M%s %sL%s %s' % tuple(p))
        else:
            yol.append(_yay(p))
    s.append('<path d="%s" fill="#1c5a35" stroke="%s" stroke-width="0.25" class="kenar"/>' % (''.join(yol), RENK['kenar']))
    kat = [('B.Cu', 'k-B'), ('F.Cu', 'k-F')]
    for ad, sinif in kat:
        s.append('<g class="k-%s" opacity="0.88">' % ad.replace('.', ''))
        for t in d['izler']:
            if t['k'] != ad:
                continue
            x1, y1, x2, y2 = t['p']
            dim = '' if not vurgu else ''
            s.append('<line class="iz" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" data-ag="%s"/>' % (x1, y1, x2, y2, RENK[ad], t['w'], escape(t['ag'])))
        s.append('</g>')
    s.append('<g class="k-viya">')
    for v in d['viyalar']:
        s.append('<circle cx="%s" cy="%s" r="%s" fill="%s" data-ag="%s"/><circle cx="%s" cy="%s" r="%s" fill="#111"/>' % (v['x'], v['y'], v['w'] / 2, RENK['viya'], escape(v['ag']), v['x'], v['y'], v['d'] / 2))
    s.append('</g>')
    if ipek:
        s.append('<g class="k-ipek" stroke="%s" stroke-width="0.12" fill="none" opacity="0.9">' % RENK['ipek'])
        for c in d['cizgiler']:
            if c['k'] != ('B.Silkscreen' if arka else 'F.Silkscreen'):
                continue
            if 'p' in c:
                x1, y1, x2, y2 = c['p']
                s.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (x1, y1, x2, y2))
            else:
                s.append('<circle cx="%s" cy="%s" r="%s"/>' % tuple(c['c']))
        s.append('</g>')
    s.append('<g class="k-pad">')
    for p in d['padler']:
        dim = ' opacity="0.35"' if vurgu and p['ref'] not in vurgu else ''
        attr = 'data-ref="%s" data-no="%s" data-ag="%s"' % (escape(p['ref']), escape(str(p['no'])), escape(p['ag'] or ''))
        fill = '#f4d36b' if (not vurgu or p['ref'] in vurgu) else RENK['pad']
        if p['t'] == 'c':
            s.append('<circle cx="%s" cy="%s" r="%s" fill="%s" %s%s/>' % (p['x'], p['y'], p['w'] / 2, fill, attr, dim))
        elif p['t'] == 'o':
            rx, ry = p['w'] / 2, p['h'] / 2
            s.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" transform="rotate(%s %s %s)" %s%s/>' % (p['x'] - rx, p['y'] - ry, p['w'], p['h'], min(rx, ry), fill, -p['a'], p['x'], p['y'], attr, dim))
        else:
            s.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" transform="rotate(%s %s %s)" %s%s/>' % (p['x'] - p['w'] / 2, p['y'] - p['h'] / 2, p['w'], p['h'], fill, -p['a'], p['x'], p['y'], attr, dim))
        if p['d'] > 0:
            s.append('<circle cx="%s" cy="%s" r="%s" fill="#0b0b0b"/>' % (p['x'], p['y'], p['d'] / 2))
    s.append('</g>')
    if etiket:
        s.append('<g class="k-ref" font-family="Inter,sans-serif" font-size="1.6" fill="#fff" text-anchor="middle">')
        for ref, k in d['konum'].items():
            if ref.startswith('H') or ref.startswith('TP'):
                continue
            ek = ' font-weight="700" fill="#ffe27a"' if ref in vurgu else (' opacity="0.45"' if vurgu else '')
            s.append('<text x="%s" y="%s" data-ref="%s"%s>%s</text>' % (k['x'], k['y'] + 0.55, escape(ref), ek, escape(ref)))
        s.append('</g>')
    if isaretler:
        s.append('<g class="k-isaret" font-family="Inter,sans-serif" text-anchor="middle">')
        for no, ref in isaretler:
            k = d['konum'].get(ref)
            if not k:
                continue
            s.append('<g transform="translate(%s,%s)"><circle r="1.9" fill="#e53935" stroke="#fff" stroke-width="0.25"/><text y="0.7" font-size="2.1" fill="#fff" font-weight="700">%s</text></g>' % (k['x'], k['y'] - 2.2, no))
        s.append('</g>')
    s.append('</svg>')
    return ''.join(s)


def _yay(p):
    # uc nokta ile yay -> SVG yay (daire)
    x1, y1, x2, y2, x3, y3 = p
    a = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2
    if abs(a) < 1e-9:
        return 'M%s %sL%s %s' % (x1, y1, x3, y3)
    b = (x1 ** 2 + y1 ** 2) * (y3 - y2) + (x2 ** 2 + y2 ** 2) * (y1 - y3) + (x3 ** 2 + y3 ** 2) * (y2 - y1)
    c = (x1 ** 2 + y1 ** 2) * (x2 - x3) + (x2 ** 2 + y2 ** 2) * (x3 - x1) + (x3 ** 2 + y3 ** 2) * (x1 - x2)
    cx, cy = -b / (2 * a) * -1, -c / (2 * a) * -1
    # dairenin merkezi
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    ux = ((x1 ** 2 + y1 ** 2) * (y2 - y3) + (x2 ** 2 + y2 ** 2) * (y3 - y1) + (x3 ** 2 + y3 ** 2) * (y1 - y2)) / d
    uy = ((x1 ** 2 + y1 ** 2) * (x3 - x2) + (x2 ** 2 + y2 ** 2) * (x1 - x3) + (x3 ** 2 + y3 ** 2) * (x2 - x1)) / d
    r = math.hypot(x1 - ux, y1 - uy)
    cross = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
    sweep = 1 if cross > 0 else 0
    return 'M%s %sA%s %s 0 0 %d %s %s' % (x1, y1, r, r, sweep, x3, y3)
