"""Kur'ân kök haritasının yerleşimi (F 3-I 382, 389). Yalnız yeni kök gelen âyetler uzayda yer alır; her oda içindeki hücrelere TAM sığar (boş oda yoktur).
Hücre = kökün kapak sayfası, A5 oranında dikdörtgen; âyet odası = kök hücrelerinin ızgarası; kısım odası = âyet odaları; sûre odası = kısım odaları (sırayla, sağdan sola, yukarıdan aşağı)."""
import math
ORAN = 148 / 210; HU = 1 / ORAN
PAD, AHDR, KHDR, SHDR, GAP = 0.03, 0.22, 0.34, 0.48, 0.03
def raf(secimler, en):
    satir, cur, cw = [], [], 0.0
    for i, (w, h, _) in enumerate(secimler):
        if cur and cw + GAP + w > en: satir.append(cur); cur = []; cw = 0.0
        cw += (GAP if cur else 0) + w; cur.append(i)
    satir.append(cur); pos = [None] * len(secimler); y = 0.0; ws = [sum(secimler[i][0] for i in r) + GAP * (len(r) - 1) for r in satir]; Wm = max(ws)
    for r in satir:
        x = Wm; rh = max(secimler[i][1] for i in r)
        for i in r: x -= secimler[i][0]; pos[i] = (x, y); x -= GAP
        y += rh + GAP
    return pos, Wm, y - GAP
def adaylar(opts, hedef=None, top=False, say=10):
    """opts: her öğe için [(w,h,veri)...]. Sıra korunur. Satır yüksekliği T ve en Wcap taranır; her biçim oranı kovasında en küçük alanlı paket döner: [(W,H,[(seçim,pos)...])]"""
    Hs = sorted({o[1] for os_ in opts for o in os_}); Ts = Hs[::max(1, len(Hs) // 24)] + [Hs[-1]]
    lo = max(min(o[0] for o in os_) for os_ in opts); hi = sum(min(o[0] for o in os_) for os_ in opts) + GAP * len(opts); K = {}
    for T in Ts:
        ch = []
        for os_ in opts:
            ok = [o for o in os_ if o[1] <= T]; ch.append(max(ok, key=lambda o: (o[1], -o[0])) if ok else min(os_, key=lambda o: o[1]))
        for i in range(25):
            pos, Wm, Ht = raf(ch, lo * (hi / lo) ** (i / 24)); sk = Wm * Ht
            kova = round(math.log2(Wm / Ht) * 2) if not top else 0
            if not top and abs(kova) > 2: continue
            if top: sk = max(Wm, Ht * hedef) ** 2
            if kova not in K or sk < K[kova][0]: K[kova] = (sk, Wm, Ht, list(zip(ch, pos)))
    return [(v[1], v[2], v[3]) for v in sorted(K.values(), key=lambda v: v[0])[:say]] or [(v[1], v[2], v[3]) for v in sorted(K.values(), key=lambda v: abs(math.log(v[1] / v[2])))[:1]]
def ayet_secenek(n):
    return [(c + 2 * PAD, AHDR + r * HU + 2 * PAD, (c, r)) for r in range(1, min(n, 14) + 1) for c in [math.ceil(n / r)]]
def yerlesim(SUR, KOKA, NO, SAYFA, KAPAK, X, Y, W, H):
    S_ = []
    for s, adi, na, KIS in SUR:
        ks = []
        for kad, ay in KIS:
            a2 = [(a, KOKA.get('%d:%d' % (s, a), [])) for a in ay]; a2 = [(a, r) for a, r in a2 if r]
            if a2: ks.append((kad, a2))
        if ks: S_.append((s, adi, ks))
    SO = []
    for s, adi, ks in S_:
        KO = []
        for kad, ay in ks:
            A_ = adaylar([ayet_secenek(len(r)) for a, r in ay])
            KO.append({'kad': kad, 'ay': ay, 'opts': [(Wi + 2 * GAP, KHDR + Hi + 2 * GAP, (Wi, Hi, dz)) for Wi, Hi, dz in A_]})
        B_ = adaylar([k['opts'] for k in KO])
        SO.append({'s': s, 'adi': adi, 'KO': KO, 'opts': [(Wi + 2 * GAP, SHDR + Hi + 2 * GAP, (Wi, Hi, dz)) for Wi, Hi, dz in B_]})
    T_ = adaylar([o['opts'] for o in SO], W / H, True, 1); Wt, Ht, dz = T_[0]; sc = min(W / Wt, H / Ht); ox = X + W - Wt * sc; oy = Y
    GS, GK, GA, GP = [], [], [], []
    for o, (sec, (sx_, sy_)) in zip(SO, dz):
        sx = ox + sx_ * sc; sy = oy + sy_ * sc; sw, sh, (_, _, kdz) = sec
        GS.append([round(sx, 3), round(sy, 3), round(sw * sc, 3), round(sh * sc, 3), '%d · %s' % (o['s'], o['adi']), round(SHDR * sc, 3)])
        for k, (ksec, (kx_, ky_)) in zip(o['KO'], kdz):
            kx = sx + (GAP + kx_) * sc; ky = sy + (SHDR + GAP + ky_) * sc; kw, kh, (_, _, adz) = ksec
            GK.append([round(kx, 3), round(ky, 3), round(kw * sc, 3), round(kh * sc, 3), k['kad'], round(KHDR * sc, 3), o['s']])
            for (a, r), (asec, (ax_, ay_)) in zip(k['ay'], adz):
                ax = kx + (GAP + ax_) * sc; ay = ky + (KHDR + GAP + ay_) * sc; aw_, ah_, (c, rr) = asec
                GA.append([round(ax, 3), round(ay, 3), round(aw_ * sc, 3), round(ah_ * sc, 3), '%d:%d' % (o['s'], a), round(AHDR * sc, 3)])
                for j, (kk, fl) in enumerate(r):
                    no = NO[(kk, fl)]; cx = ax + (PAD + (c - 1 - j % c)) * sc; cy = ay + (AHDR + PAD + (j // c) * HU) * sc; nc = KAPAK.get(str(no), 0)
                    GP.append([round(cx + sc * 0.02, 3), round(cy + sc * 0.02, 3), round(sc * 0.96, 3), round(sc * HU * 0.96, 3), no, nc + SAYFA.get(str(no), 0), kk, fl, nc])
    return GS, GK, GA, GP
