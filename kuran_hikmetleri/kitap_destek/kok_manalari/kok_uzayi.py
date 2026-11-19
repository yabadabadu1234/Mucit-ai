"""Kur'ân kök haritasının yerleşimi (F 3-I 382). Yalnız yeni kök gelen âyetler uzayda yer alır; kök gelmemiş âyet, boş kısım ve boş sûre uzaydan atılır.
Her kök hücresi lügat sayfasının (A5, 148×210) görüntüsünü taşır; hücre sayfa oranında dikdörtgendir."""
import math
from yerlesim import kare
ORAN = 148 / 210
def izgara_dik(n, x, y, w, h):
    en = None
    for co in range(1, n + 1):
        ro = math.ceil(n / co); cw = min(w / co, h / ro * ORAN)
        if en is None or cw > en[0]: en = (cw, co, ro)
    cw, co, ro = en; ch = cw / ORAN; ox = x + (w - co * cw) / 2; oy = y + (h - ro * ch) / 2
    return [(ox + (co - 1 - j % co) * cw, oy + (j // co) * ch, cw, ch) for j in range(n)]
def yerlesim(SUR, KOKA, NO, SAYFA, X, Y, W, H):
    S_ = []
    for s, adi, na, KIS in SUR:
        ks = []
        for kad, ay in KIS:
            a2 = [(a, KOKA.get('%d:%d' % (s, a), [])) for a in ay]; a2 = [(a, r) for a, r in a2 if r]
            if a2: ks.append((kad, a2))
        if ks: S_.append((s, adi, ks))
    ag = lambda ay: sum(len(r) for _, r in ay)
    SR = kare([(s, sum(ag(ay) for _, ay in ks)) for s, adi, ks in S_], X, Y, W, H, True)
    GS, GK, GA, GP = [], [], [], []
    for s, adi, ks in S_:
        x, y, w, h = SR[s]; x += 3; y += 3; w -= 6; h -= 6; tb = min(30.0, max(3.0, min(w, h) * 0.12))
        GS.append([round(x, 2), round(y, 2), round(w, 2), round(h, 2), '%d · %s' % (s, adi), round(tb, 2)])
        KR = kare([(j, ag(ay)) for j, (_, ay) in enumerate(ks)], x + 1, y + tb, w - 2, h - tb - 1, True)
        for j, (kad, ay) in enumerate(ks):
            kx, ky, kw, kh = KR[j]; kx += 0.8; ky += 0.8; kw -= 1.6; kh -= 1.6; kt = min(14.0, max(1.0, min(kw, kh) * 0.1))
            GK.append([round(kx, 3), round(ky, 3), round(kw, 3), round(kh, 3), kad, round(kt, 3), s])
            AR = kare([(i, len(r)) for i, (_, r) in enumerate(ay)], kx, ky + kt, kw, kh - kt, True)
            for i, (a, r) in enumerate(ay):
                ax, ay_, aw, ah = AR[i]; g = min(aw, ah) * 0.03; ax += g; ay_ += g; aw -= 2 * g; ah -= 2 * g; at = min(aw, ah) * 0.14
                GA.append([round(ax, 3), round(ay_, 3), round(aw, 3), round(ah, 3), '%d:%d' % (s, a), round(at, 3)])
                for (cx, cy, cw, ch), (k, fl) in zip(izgara_dik(len(r), ax, ay_ + at, aw, ah - at), r):
                    no = NO[(k, fl)]; GP.append([round(cx + cw * 0.02, 3), round(cy + ch * 0.02, 3), round(cw * 0.96, 3), round(ch * 0.96, 3), no, SAYFA.get(str(no), 0), k, fl])
    return GS, GK, GA, GP
