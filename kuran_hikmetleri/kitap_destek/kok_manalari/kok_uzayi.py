"""Kur'ân kök haritasının yerleşimi (F 3-I 382, 389, 391, 392). Yalnız yeni kök gelen âyetler uzayda yer alır.
Sûre odası ⊃ kısım odası ⊃ âyet odası ⊃ kök hücresi. Her oda, içindeki odalarla TAM dolar (bej boş alan yok): üst odanın içi kesişen kılavuz bölmelerle (guillotine) paylanır;
bölme noktası ve yönü, hücre alanının toplamını azamîleştirecek şekilde taranır. Hücre A5 oranından en çok TAU kat sapabilir (sayfa görüntüsü hücreye oturur).
Sıra: sağdan sola, yukarıdan aşağı (kök haritası sonunda ayna çevrilir)."""
import math, functools
ORAN = 148 / 210; TAU = 1.22; ADIM = 6.0
def kur(SUR_, KOKA, NO, SAYFA, KAPAK, X, Y, W, H):
    S_ = []
    for s, adi, na, KIS in SUR_:
        ks = []
        for kad, ay in KIS:
            a2 = [(a, KOKA.get('%d:%d' % (s, a), [])) for a in ay]; a2 = [(a, r) for a, r in a2 if r]
            if a2: ks.append((kad, a2))
        if ks: S_.append((s, adi, ks))
    N = sum(len(r) for s, adi, ks in S_ for kad, ay in ks for a, r in ay)
    Ast = 0.62 * W * H / N; hc = math.sqrt(Ast / ORAN)
    AH, KH, SH, G = 0.17 * hc, 0.30 * hc, 0.42 * hc, 0.04 * hc
    AMAX = ORAN * TAU; AMIN = ORAN / TAU
    # düğümler: ('a', n, ref) · ('k'|'s', [çocuklar], ref); tahmini alan
    def tah(d):
        if d[0] == 'a': return d[1] * Ast + (AH + 2 * G) * math.sqrt(d[1] * Ast / ORAN * ORAN) * 1.0
        h_ = KH if d[0] == 'k' else SH
        return sum(tah(c) for c in d[1]) + (h_ + 2 * G) * math.sqrt(sum(tah(c) for c in d[1]))
    A_ = lambda s, kad, a, r: ('a', len(r), (s, a, r))
    SD = [('s', [('k', [('a', len(r), (s, a, r)) for a, r in ay], (s, kad)) for kad, ay in ks], (s, adi)) for s, adi, ks in S_]
    TAH = {}
    def t(d):
        k = id(d)
        if k not in TAH: TAH[k] = tah(d)
        return TAH[k]
    sys_setrecursion = __import__('sys').setrecursionlimit(10000)
    def satirlar_(n, r):
        q, m = divmod(n, r); return [q + 1] * m + [q] * (r - m)
    @functools.lru_cache(maxsize=None)
    def yaprak(n, wk, hk):
        w = wk * ADIM - 2 * G; h = hk * ADIM - AH - 2 * G
        if w <= 0 or h <= 0: return (-1.0, 0)
        en = (-1.0, 0)
        for r in range(1, min(n, 14) + 1):
            tp = 0.0; mc = 1e9
            for k in satirlar_(n, r):
                sw, sh = w / k, h / r; a = sw / sh; a2 = min(max(a, AMIN), AMAX)
                cw = min(sw, sh * a2); ch = cw / a2; tp += k * cw * ch; mc = min(mc, cw)
            if mc < 0.55 * math.sqrt(Ast * ORAN): tp *= 0.04
            if tp > en[0]: en = (tp, r)
        return en
    memo = {}
    def uyar(d, w, h):
        wk, hk = int(w / ADIM), int(h / ADIM); key = (id(d), wk, hk)
        if key in memo: return memo[key]
        if d[0] == 'a': r = yaprak(d[1], wk, hk); res = (r[0], ('a', r[1]))
        else:
            hd = KH if d[0] == 'k' else SH; iw, ih = wk * ADIM - 2 * G, hk * ADIM - hd - 2 * G
            if iw <= 0 or ih <= 0: res = (-1.0, None)
            else:
                sc, pl = bol(d[1], 0, len(d[1]), iw, ih); res = (sc, (d[0], pl))
        memo[key] = res; return res
    bm = {}
    def bol(ch, lo, hi, w, h):
        wk, hk = int(w / ADIM), int(h / ADIM); key = (id(ch), lo, hi, wk, hk)
        if key in bm: return bm[key]
        if hi - lo == 1: sc, pl = uyar(ch[lo], w, h); res = (sc, ('y', lo, pl))
        else:
            ws = [t(c) for c in ch[lo:hi]]; tot = sum(ws); acc = 0.0; ad = []
            for i in range(lo + 1, hi):
                acc += ws[i - lo - 1]; ad.append((abs(acc / tot - 0.5), i, acc / tot))
            ad.sort(); res = (-1.0, None); mn = 0.75 * math.sqrt(Ast * ORAN) + 2 * G
            for _, i, f in ad[:5]:
                for yon in 'vh':
                    d1 = (w * f, h) if yon == 'v' else (w, h * f); d2 = (w * (1 - f), h) if yon == 'v' else (w, h * (1 - f))
                    if min(d1) < mn or min(d2) < mn: continue
                    if yon == 'v': a1 = bol(ch, lo, i, w * f, h); a2 = bol(ch, i, hi, w * (1 - f), h)
                    else: a1 = bol(ch, lo, i, w, h * f); a2 = bol(ch, i, hi, w, h * (1 - f))
                    if a1[0] < 0 or a2[0] < 0: continue
                    sc = a1[0] + a2[0]
                    if sc > res[0]: res = (sc, ('c', yon, f, a1[1], a2[1]))
        if res[0] < 0 and hi - lo > 1:
            i = lo + 1; f = t(ch[lo]) / sum(t(c) for c in ch[lo:hi]); a1 = bol(ch, lo, i, w * f, h); a2 = bol(ch, i, hi, w * (1 - f), h)
            if a1[0] >= 0 and a2[0] >= 0: res = (a1[0] + a2[0], ('c', 'v', f, a1[1], a2[1]))
        bm[key] = res; return res
    sc, pl = bol(SD, 0, len(SD), W, H)
    GS, GK, GA, GP = [], [], [], []
    def yerles(d, plan, x, y, w, h):
        if d[0] == 'a':
            s, a, r = d[2]; GA.append([x, y, w, h, '%d:%d' % (s, a), AH]); iw, ih = w - 2 * G, h - AH - 2 * G; r_ = plan[1]; rows = satirlar_(d[1], r_); j = 0
            for ri, k in enumerate(rows):
                sw, sh = iw / k, ih / r_; a_ = sw / sh; a2 = min(max(a_, AMIN), AMAX); cw = min(sw, sh * a2); ch = cw / a2
                for c in range(k):
                    kk, fl = r[j]; no = NO[(kk, fl)]; nc = KAPAK.get(str(no), 0)
                    GP.append([x + G + c * sw + (sw - cw) / 2, y + AH + G + ri * sh + (sh - ch) / 2, cw, ch, no, nc + SAYFA.get(str(no), 0), kk, fl, nc]); j += 1
            return
        hd = KH if d[0] == 'k' else SH; (GK if d[0] == 'k' else GS).append([x, y, w, h, d[2][1] if d[0] == 'k' else '%d · %s' % d[2], hd] + ([d[2][0]] if d[0] == 'k' else []))
        yer_bol(d[1], plan[1], x + G, y + hd + G, w - 2 * G, h - hd - 2 * G)
    def yer_bol(ch, pl, x, y, w, h):
        if pl[0] == 'y': yerles(ch[pl[1]], pl[2], x, y, w, h); return
        _, yon, f, p1, p2 = pl
        if yon == 'v': yer_bol(ch, p1, x, y, w * f, h); yer_bol(ch, p2, x + w * f, y, w * (1 - f), h)
        else: yer_bol(ch, p1, x, y, w, h * f); yer_bol(ch, p2, x, y + h * f, w, h * (1 - f))
    yer_bol(SD, pl, 0, 0, W, H)
    return GS, GK, GA, GP, sc, N
def yerlesim(SUR, KOKA, NO, SAYFA, KAPAK, X, Y, W, H):
    GS, GK, GA, GP, sc, N = kur(SUR, KOKA, NO, SAYFA, KAPAK, X, Y, W, H)
    # ayna: sağdan sola
    def ay(r): r[0] = round(X + W - r[0] - r[2] + X - X, 3); r[1] = round(Y + r[1], 3); return r
    for L in (GS, GK, GA):
        for r in L: ay(r); r[2] = round(r[2], 3); r[3] = round(r[3], 3); r[5] = round(r[5], 3)
    for r in GP: ay(r); r[2] = round(r[2], 3); r[3] = round(r[3], 3)
    print('yerleşim: hücre alanı %.1f%% · hücre sayısı %d' % (100 * sc / (W * H), N))
    return GS, GK, GA, GP
