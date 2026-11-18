import math, re, json, pathlib
KH = pathlib.Path(__file__).resolve().parent.parent.parent
def kare(oge, x, y, w, h, sag=False):
    X0, W0 = x, w
    oge = [o for o in oge if o[1] > 0]; top = sum(a for _, a in oge); o = {}
    oge = [(k, a * w * h / top) for k, a in oge]
    def kotu(sira, kenar):
        s_ = sum(a for _, a in sira); return max(max(kenar * kenar * a / s_ / s_, s_ * s_ / kenar / kenar / a) for _, a in sira)
    while oge:
        kenar = min(w, h); sira = [oge.pop(0)]
        while oge and kotu(sira + [oge[0]], kenar) <= kotu(sira, kenar): sira.append(oge.pop(0))
        s_ = sum(a for _, a in sira)
        if w >= h:
            ew = s_ / h; yy = y
            for k, a_ in sira: o[k] = (x, yy, ew, a_ / ew); yy += a_ / ew
            x += ew; w -= ew
        else:
            eh = s_ / w; xx = x
            for k, a_ in sira: o[k] = (xx, y, a_ / eh, eh); xx += a_ / eh
            y += eh; h -= eh
    if sag: o = {k: (2 * X0 + W0 - v[0] - v[2], v[1], v[2], v[3]) for k, v in o.items()}
    return o
def satirlar(oge, x, y, w, h):
    oge = [o for o in oge if o[1] > 0]; top = sum(a for _, a in oge); oge = [(k, a * w * h / top) for k, a in oge]; o = {}; yy = y; i = 0
    def kotu(sira):
        rh = sum(a for _, a in sira) / w; return max(max(a / rh / rh, rh * rh / a) for _, a in sira)
    while oge:
        sira = [oge.pop(0)]
        while oge and kotu(sira + [oge[0]]) <= kotu(sira): sira.append(oge.pop(0))
        rh = sum(a for _, a in sira) / w; xx = x + w if i % 2 == 0 else x
        for k, a in sira:
            lw = a / rh
            if i % 2 == 0: xx -= lw; o[k] = (xx, yy, lw, rh)
            else: o[k] = (xx, yy, lw, rh); xx += lw
        yy += rh; i += 1
    return o
def izgara(n, x, y, w, h, sag=False):
    if n == 0: return []
    best = None
    for co in range(1, n + 1):
        ro = math.ceil(n / co); cs = min(w / co, h / ro)
        if best is None or cs > best[0]: best = (cs, co, ro)
    cs, co, ro = best; ox = x + (w - co * cs) / 2; oy = y + (h - ro * cs) / 2
    return [((ox + (co - 1 - j % co) * cs) if sag else (ox + (j % co) * cs), oy + (j // co) * cs, cs) for j in range(n)]
def sureler():
    BT = (KH / 'kaynak' / 'sure_bolumlemeleri' / 'sure_bolumlemeleri.md').read_text(encoding='utf-8')
    BK = {}
    for m in re.finditer(r'^## (\d+)\. .*?$(.*?)(?=^## \d+\. |\Z)', BT, re.M | re.S):
        z = re.search(r'\*\*A\. Kitap verisi.*?\*\*(.*?)(?=\n\*\*B\.|\Z)', m.group(2), re.S)
        BK[int(m.group(1))] = [(x.strip(), int(b), int(c or b)) for x, b, c in re.findall(r'^- (.*?) \(Âyet (\d+)(?:-(\d+))?\)\s*$', z.group(1), re.M)]
    SUR = []
    for s in range(1, 115):
        d = next(KH.glob('sureler/%03d-*/sure.md' % s)); t = d.read_text(encoding='utf-8')
        adi = re.search(r'^# S\d+ · (.*)$', t, re.M).group(1); na = len(json.load(open(KH / 'kaynak' / 'sure' / f'{s}.json', encoding='utf-8'))['verses'])
        KIS = [(x + (' (%d)' % b if b == c else ' (%d-%d)' % (b, c)), list(range(b, c + 1))) for x, b, c in BK[s]]
        assert sorted(a for _, L in KIS for a in L) == list(range(1, na + 1)), s
        SUR.append((s, adi, na, KIS))
    return SUR
