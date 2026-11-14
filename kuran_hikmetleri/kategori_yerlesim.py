import collections
import colorsys
import glob
import json
import math
import os
import pickle
import sys

import kategori_sebep as SB
import numpy as np
import torch
from scipy.sparse import csr_matrix, diags
from scipy.stats import rankdata
from sklearn.decomposition import TruncatedSVD

KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, 'kategori_yerlesim.html')
GRID_ARALIK = 2
USULLER = [
    ('ses', 'Ses: bölge › mahreç › harf › fasıl'),
    ('wordnet', 'Mana: Arabic WordNet'),
    ('gomme', 'Mana: gömme kümeleri'),
    ('muhassas', 'Konu: Muhassas kitap › bâb'),
    ('cebel', 'Ses-mana: Cebel harf › fasıl'),
    ('mecaz', 'Zemahşerî: hakîkat/mecaz'),
    ('prototip', 'Prototip: yayılım uzaklığı'),
    ('korpus', 'Korpus: tür › bâb'),
    ('kuran', "Kur'ân'da geçiş"),
    ('etymarab', 'EtymArab maddesi'),
]
HUE_SIRASI = [0, 5, 1, 6, 2, 7, 3, 8, 4, 9]


def yollar(d, prototip_esik):
    y = {}
    t = d.get('tasnif') or {}
    if t.get('bolge'):
        y['ses'] = [t['bolge'], t['mahrec'], t['harf'], 'fasıl ' + t['fasil']]
    m = d.get('mana_tasnif') or {}
    if m.get('orta'):
        y['wordnet'] = [m['ust'], m['orta'], m['ince']]
    g = d.get('mana_tasnif_gomme') or {}
    if g.get('orta'):
        y['gomme'] = ['g%d' % g['ust']['kume'], 'g%d.%d' % (g['ust']['kume'], g['orta']['kume']), 'g%d.%d.%d' % (g['ust']['kume'], g['orta']['kume'], g['ince']['kume'])]
    mh = d.get('muhassas_tasnif') or {}
    if mh.get('kitap'):
        y['muhassas'] = [mh['kitap']] + ([mh['bab']] if mh.get('bab') else [])
    c = d.get('ses_mana_tasnif') or {}
    if c.get('fasil'):
        y['cebel'] = [c['fasil'].split(' ')[0], c['fasil']]
    h = d.get('hakikat_mecaz_tasnif') or {}
    if 'mecaz_var' in h:
        y['mecaz'] = ['mecazlı' if h['mecaz_var'] else 'yalnız hakîkat']
    p = d.get('prototip_yayilim_tasnif') or {}
    if 'ortalama_benzerlik' in p:
        b = p['ortalama_benzerlik']
        y['prototip'] = ['yakın' if b >= prototip_esik[1] else ('orta' if b >= prototip_esik[0] else 'uzak')]
    kq = (d.get('sozlukler') or {}).get('kuran_korpusu')
    if isinstance(kq, list):
        kq = kq[0] if kq else None
    if kq and kq.get('tur'):
        y['korpus'] = [max(kq['tur'], key=kq['tur'].get)]
        if kq.get('bab'):
            y['korpus'].append('bâb ' + max(kq['bab'], key=kq['bab'].get))
    y['kuran'] = ["Kur'ân'da var" if d.get('kuranda_var') else "Kur'ân'da yok"]
    ea = (d.get('sozlukler') or {}).get('etymarab')
    if ea:
        y['etymarab'] = ['dolu' if ea.get('dolu') else 'yer tutucu']
    return y


def yukle():
    onbellek = os.environ.get('KY_ONBELLEK')
    if onbellek and os.path.exists(onbellek):
        return pickle.load(open(onbellek, 'rb'))
    ham = []
    sys.path.insert(0, os.path.join(KOK, 'kitap_destek', 'turetme_motoru'))
    import awn_tasnif as AW
    kok_syn, lem_syn = AW.yukle()
    for f in sorted(glob.glob(os.path.join(KOK, 'kelime_kaydi', 'kuranda_*', 'kokler', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        d['_syn'] = AW.synset_adlari(d, kok_syn, lem_syn)
        p = d.get('prototip_yayilim_tasnif') or {}
        ham.append((d, p.get('ortalama_benzerlik')))
    esik = np.quantile([x[1] for x in ham if x[1] is not None], [1 / 3, 2 / 3])
    dugumler = []
    for d, _ in ham:
        ka = (d.get('sozlukler') or {}).get('kok_anlamlari') or {}
        kq = (d.get('sozlukler') or {}).get('kuran_korpusu')
        if isinstance(kq, list):
            kq = kq[0] if kq else None
        dugumler.append({'kok': d['kok'], 'syn': d['_syn'], 'yollar': yollar(d, esik), 'mana': ka.get('turkce', ''), 'kelime': len(d.get('kelimeler', [])),
                         'gecis': (kq or {}).get('gecis', 0), 'kuran': bool(d.get('kuranda_var'))})
    if onbellek:
        pickle.dump(dugumler, open(onbellek, 'wb'))
    return dugumler


def ek_bilgi(dugumler):
    from nltk.corpus import wordnet as W
    ceviri = SB.ceviri_yukle()
    ek = {}
    for dosya in glob.glob(os.path.join(KOK, 'kelime_kaydi', 'kuranda_*', 'kokler', '*.json')):
        d = json.load(open(dosya, encoding='utf-8'))
        kw = []
        for k in d.get('kelimeler', []):
            tr = (k.get('turkce') or {}).get('yuzey', '')
            kw.append([k.get('kelime', ''), tr, k.get('adet', 0)])
        ka = (d.get('sozlukler') or {}).get('kok_anlamlari') or {}
        ek[d['kok']] = (kw, ka.get('turkce', ''))
    sonuc = []
    for dg in dugumler:
        kw, mana = ek.get(dg['kok'], ([], dg['mana']))
        e = []
        for ad in dg['syn'][:3]:
            sn = W.synset(ad)
            tr = ceviri.get(ad)
            e.append([sn.lemmas()[0].name().replace('_', ' '), tr or sn.definition(), 1 if tr else 0])
        sonuc.append({'kw': kw, 'mana': mana, 'e': e, 'l': sorted({l.name().replace('_', ' ') for ad in dg['syn'] for l in W.synset(ad).lemmas()})[:12]})
    return sonuc


def kategoriler(dugumler):
    kimlik = {}
    kat = []
    uye = collections.defaultdict(list)
    u_ad = [a for a, _ in USULLER]
    for i, dg in enumerate(dugumler):
        for u, yol in dg['yollar'].items():
            ui = u_ad.index(u)
            ata = -1
            for d in range(len(yol)):
                anahtar = (ui, tuple(yol[:d + 1]))
                if anahtar not in kimlik:
                    kimlik[anahtar] = len(kat)
                    kat.append({'u': ui, 'd': d, 'ad': yol[d], 'ata': ata})
                ata = kimlik[anahtar]
                uye[ata].append(i)
    for k, c in enumerate(kat):
        c['uye'] = uye[k]
        c['cocuk'] = []
    for k, c in enumerate(kat):
        if c['ata'] >= 0:
            kat[c['ata']]['cocuk'].append(k)
    return kat, kimlik


def baslangic(n, kat):
    K = len(kat)
    satir, sutun = [], []
    for k, c in enumerate(kat):
        for i in c['uye']:
            satir.append(i)
            sutun.append(k)
    M = csr_matrix((np.ones(len(satir)), (satir, sutun)), shape=(n, K))
    sayi = np.asarray(M.sum(0)).ravel()
    w = 1 / np.maximum(sayi, 1) ** 0.75
    Mw = M @ diags(w)
    P = TruncatedSVD(2, random_state=7).fit_transform(Mw)
    rng = np.random.default_rng(7)
    P = (P - P.mean(0)) / (P.std(0) + 1e-9) + rng.normal(0, 0.05, P.shape)
    gruplar = collections.defaultdict(list)
    for k, c in enumerate(kat):
        gruplar[(c['u'], c['d'])].append(k)
    pay = np.maximum(np.asarray(Mw.sum(1)).ravel(), 1e-9)
    for _ in range(60):
        C = (M.T @ P) / np.maximum(sayi, 1)[:, None]
        for js in gruplar.values():
            if len(js) < 2 or len(js) > 1500:
                continue
            c = C[js]
            fark = c[:, None, :] - c[None, :, :]
            d2 = (fark ** 2).sum(-1) + 0.05
            it = (fark / d2[..., None]).sum(1)
            C[js] = c + 0.25 * it / (1 + np.linalg.norm(it, axis=1, keepdims=True))
        P = (Mw @ C) / pay[:, None] + rng.normal(0, 0.01, P.shape)
        P = (P - P.mean(0)) / (P.std(0) + 1e-9)
    U = np.column_stack([rankdata(P[:, 0]), rankdata(P[:, 1])]) / n
    kenar = math.sqrt(n * 1.25)
    return (U - 0.5) * kenar, M


def eniyile_tur(n, kat, P0, adim):
    torch.manual_seed(7)
    K = len(kat)
    me = np.concatenate([np.array(c['uye'], dtype=np.int64) for c in kat])
    mk = np.concatenate([np.full(len(c['uye']), k, dtype=np.int64) for k, c in enumerate(kat)])
    C0 = np.zeros((K, 2))
    R0 = np.zeros(K)
    for k, c in enumerate(kat):
        pts = P0[c['uye']]
        C0[k] = pts.mean(0)
        R0[k] = max(float(np.linalg.norm(pts - C0[k], axis=1).max()), 1.0)
    cf = [(k, c['ata']) for k, c in enumerate(kat) if c['ata'] >= 0]
    cocuk = torch.tensor([a for a, _ in cf])
    ata = torch.tensor([b for _, b in cf])
    gruplar = collections.defaultdict(list)
    for k, c in enumerate(kat):
        gruplar[(c['u'], c['d'])].append(k)
    ia, ib, iw = [], [], []
    for js in gruplar.values():
        t = torch.tensor(js)
        a, b = torch.triu_indices(len(js), len(js), 1)
        ia.append(t[a])
        ib.append(t[b])
        kard = torch.tensor([kat[j]['ata'] for j in js])
        iw.append(1.0 + 2.0 * (kard[a] == kard[b]).float())
    ia = torch.cat(ia)
    ib = torch.cat(ib)
    iw = torch.cat(iw)
    me_t, mk_t = torch.tensor(me), torch.tensor(mk)
    agirlik = torch.tensor([1.0 / max(len(c['uye']), 1) for c in kat], dtype=torch.float32)
    p = torch.tensor(P0, dtype=torch.float32, requires_grad=True)
    c = torch.tensor(C0, dtype=torch.float32, requires_grad=True)
    lr = torch.tensor(np.log(R0), dtype=torch.float32, requires_grad=True)
    opt = torch.optim.Adam([p, c, lr], lr=0.2)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, adim, eta_min=0.01)
    for t in range(adim):
        opt.zero_grad()
        r = torch.exp(lr)
        d = (p[me_t] - c[mk_t]).norm(dim=1)
        cont = torch.relu(d - r[mk_t]).pow(2).sum()
        alan = (r.pow(2) * agirlik).sum()
        yuva = torch.relu((c[cocuk] - c[ata]).norm(dim=1) + r[cocuk] - r[ata]).pow(2).sum()
        ov = (torch.relu(r[ia] + r[ib] - (c[ia] - c[ib]).norm(dim=1)).pow(2) * iw).sum()
        x = torch.randint(0, n, (400000,))
        y = torch.randint(0, n, (400000,))
        rep = torch.relu(1.6 - (p[x] - p[y]).norm(dim=1)).pow(2).sum()
        loss = 20 * cont + 6.0 * alan + 0.5 * yuva + 0.6 * ov + 0.05 * rep
        loss.backward()
        opt.step()
        sched.step()
        if t % 250 == 0:
            print(t, round(float(loss.detach()), 1), round(float(cont.detach()), 1), round(float(alan.detach()), 1), round(float(ov.detach()), 1), flush=True)
    return p.detach().numpy()


def eniyile(n, kat, P0, tur=8, adim=220):
    P = P0
    for t in range(tur):
        P = eniyile_tur(n, kat, P, adim)
        iz, kayma = izgaraya_otur(P)
        P = iz / GRID_ARALIK
        print('tur', t, 'ortalama kayma', round(float(np.mean(kayma)), 2), flush=True)
    return P


def izgaraya_otur(P):
    n = len(P)
    kenar = int(math.ceil(math.sqrt(n * 1.25)))
    P = P - (P.max(0) + P.min(0)) / 2
    olcek = (kenar - 2) / max(float(np.ptp(P[:, 0])), float(np.ptp(P[:, 1])), 1e-9)
    aday = np.rint(P * olcek).astype(int)
    dolu = {}
    sira = np.argsort(np.linalg.norm(P, axis=1))
    sonuc = np.zeros((n, 2), dtype=int)
    kayma = []
    for i in sira:
        x, y = int(aday[i][0]), int(aday[i][1])
        r = 0
        bulundu = False
        while not bulundu:
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    h = (x + dx, y + dy)
                    if h not in dolu:
                        dolu[h] = i
                        sonuc[i] = h
                        kayma.append(max(abs(dx), abs(dy)))
                        bulundu = True
                        break
                if bulundu:
                    break
            r += 1
    return sonuc * GRID_ARALIK, kayma


def sarmal_daire(cemberler, tur=150):
    c = cemberler[:, :2].mean(0)
    for i in range(1, tur + 1):
        d = np.hypot(cemberler[:, 0] - c[0], cemberler[:, 1] - c[1])
        j = int(np.argmax(d + cemberler[:, 2]))
        if d[j] < 1e-9:
            uc = cemberler[j, :2] + np.array([cemberler[j, 2], 0.0])
        else:
            uc = cemberler[j, :2] + (cemberler[j, :2] - c) / d[j] * cemberler[j, 2]
        c = c + (uc - c) / (i + 1)
    r = float(np.max(np.hypot(cemberler[:, 0] - c[0], cemberler[:, 1] - c[1]) + cemberler[:, 2]))
    return float(c[0]), float(c[1]), r


def daireler(izgara, kat):
    sonuc = [None] * len(kat)
    sira = sorted(range(len(kat)), key=lambda k: -kat[k]['d'])
    for k in sira:
        c = kat[k]
        parcalar = [np.array([izgara[i][0], izgara[i][1], 0.0]) for i in c['uye']]
        parcalar += [np.array(sonuc[j]) for j in c['cocuk']]
        arr = np.array(parcalar)
        cx, cy, r = sarmal_daire(arr)
        sonuc[k] = (cx, cy, r + GRID_ARALIK * 0.6)
    return sonuc


def olcut(izgara, kat, dai):
    ihlal = toplam = 0
    kenarda = 0
    for k, c in enumerate(kat):
        cx, cy, r = dai[k]
        d = np.hypot(izgara[c['uye'], 0] - cx, izgara[c['uye'], 1] - cy)
        ihlal += int((d > r + 1e-6).sum())
        toplam += len(c['uye'])
        kenarda += int((d >= 0.75 * r).sum())
    ayni = collections.defaultdict(list)
    for k, c in enumerate(kat):
        ayni[(c['u'], c['d'])].append(k)
    ortusme = {}
    for (u, d), js in ayni.items():
        a = np.array([dai[j] for j in js])
        alan = float((math.pi * a[:, 2] ** 2).sum())
        if len(js) < 2 or alan == 0:
            ortusme['%s/%d' % (USULLER[u][0], d + 1)] = 0.0
            continue
        ia, ib = np.triu_indices(len(js), 1)
        dist = np.hypot(a[ia, 0] - a[ib, 0], a[ia, 1] - a[ib, 1])
        r1, r2 = a[ia, 2], a[ib, 2]
        kes = np.zeros(len(ia))
        ic = dist <= np.abs(r1 - r2)
        kes[ic] = math.pi * np.minimum(r1, r2)[ic] ** 2
        orta = (dist < r1 + r2) & ~ic & (dist > 1e-9)
        d_, r1_, r2_ = dist[orta], r1[orta], r2[orta]
        a1 = np.arccos(np.clip((d_ ** 2 + r1_ ** 2 - r2_ ** 2) / (2 * d_ * r1_), -1, 1))
        a2 = np.arccos(np.clip((d_ ** 2 + r2_ ** 2 - r1_ ** 2) / (2 * d_ * r2_), -1, 1))
        kes[orta] = r1_ ** 2 * a1 + r2_ ** 2 * a2 - 0.5 * np.sqrt(np.maximum(0, (-d_ + r1_ + r2_) * (d_ + r1_ - r2_) * (d_ - r1_ + r2_) * (d_ + r1_ + r2_)))
        ortusme['%s/%d' % (USULLER[u][0], d + 1)] = round(float(kes.sum() / alan), 3)
    return ihlal, toplam, kenarda, ortusme



PITCH = GRID_ARALIK


def kume_noktalari(m):
    kenar = int(math.ceil(math.sqrt(m))) + 2
    aday = sorted(((i * PITCH, j * PITCH) for i in range(-kenar, kenar + 1) for j in range(-kenar, kenar + 1)), key=lambda t: (t[0] ** 2 + t[1] ** 2, t))[:m]
    r = max(math.hypot(x, y) for x, y in aday) + PITCH * 0.75 if m else 0.0
    return aday, r


def paketle(yaricaplar, bosluk):
    n = len(yaricaplar)
    sira = sorted(range(n), key=lambda i: -yaricaplar[i])
    konum = {}
    yerlesen = []
    for i in sira:
        r = yaricaplar[i] + bosluk / 2
        if not yerlesen:
            konum[i] = (0.0, 0.0)
            yerlesen.append((0.0, 0.0, r))
            continue
        merkez = np.mean([[a, b] for a, b, _ in yerlesen], axis=0)
        adaylar = []
        for a in range(len(yerlesen)):
            ax, ay, ar = yerlesen[a]
            for t in np.linspace(0, 2 * math.pi, 16, endpoint=False):
                adaylar.append((ax + (ar + r) * math.cos(t), ay + (ar + r) * math.sin(t)))
            for b in range(a + 1, len(yerlesen)):
                bx, by, br = yerlesen[b]
                d = math.hypot(bx - ax, by - ay)
                if d > ar + br + 2 * r or d < 1e-9:
                    continue
                l1, l2 = ar + r, br + r
                x = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
                h2 = l1 * l1 - x * x
                if h2 < 0:
                    continue
                h = math.sqrt(h2)
                ux, uy = (bx - ax) / d, (by - ay) / d
                adaylar.append((ax + ux * x - uy * h, ay + uy * x + ux * h))
                adaylar.append((ax + ux * x + uy * h, ay + uy * x - ux * h))
        arr = np.array(adaylar)
        ya = np.array(yerlesen)
        uygun = np.ones(len(arr), dtype=bool)
        for ax, ay, ar in yerlesen:
            uygun &= np.hypot(arr[:, 0] - ax, arr[:, 1] - ay) >= ar + r - 1e-6
        arr = arr[uygun]
        j = int(np.argmin(np.hypot(arr[:, 0] - merkez[0], arr[:, 1] - merkez[1])))
        konum[i] = (float(arr[j][0]), float(arr[j][1]))
        yerlesen.append((arr[j][0], arr[j][1], r))
    ys = np.array(yerlesen)
    c = ys[:, :2].mean(0)
    sar = sarmal_daire(np.column_stack([ys[:, 0], ys[:, 1], ys[:, 2] - bosluk / 2]))
    ortak = (sar[0], sar[1])
    return {i: (konum[i][0] - ortak[0], konum[i][1] - ortak[1]) for i in konum}, sar[2] + bosluk / 2


def bolge_yerlesimi(kat, dugumler):
    cocuk_uye = {}
    for k, c in enumerate(kat):
        cs = set()
        for j in c['cocuk']:
            cs.update(kat[j]['uye'])
        cocuk_uye[k] = [i for i in c['uye'] if i not in cs]
    yer = {}
    kopya = []

    def kur(k):
        c = kat[k]
        parcalar = [kur(j) for j in c['cocuk']]
        oz = cocuk_uye[k]
        pts, pr = kume_noktalari(len(oz))
        yaricaplar = [p['r'] for p in parcalar] + ([pr] if oz else [])
        if not yaricaplar:
            return {'k': k, 'r': PITCH, 'cocuk': [], 'oz': [], 'oz_r': 0.0}
        konumlar, r = paketle(yaricaplar, PITCH * 1.5)
        for a, p in enumerate(parcalar):
            p['ox'], p['oy'] = konumlar[a]
        node = {'k': k, 'r': r, 'cocuk': parcalar, 'oz': [(oz[a], pts[a][0] + (konumlar[len(parcalar)][0] if oz else 0), pts[a][1] + (konumlar[len(parcalar)][1] if oz else 0)) for a in range(len(oz))]}
        return node

    usul_dugum = {}
    for u in range(len(USULLER)):
        koklar = [k for k, c in enumerate(kat) if c['u'] == u and c['ata'] == -1]
        parcalar = [kur(k) for k in koklar]
        if not parcalar:
            continue
        konumlar, r = paketle([p['r'] for p in parcalar], PITCH * 3)
        for a, p in enumerate(parcalar):
            p['ox'], p['oy'] = konumlar[a]
        usul_dugum[u] = {'r': r, 'cocuk': parcalar}
    us = sorted(usul_dugum)
    konumlar, R = paketle([usul_dugum[u]['r'] for u in us], PITCH * 14)
    mutlak = [None] * len(kat)

    def yay(node, ax, ay, u):
        k = node.get('k')
        if k is not None:
            mutlak[k] = (ax, ay, node['r'])
        for a, i_x, i_y in node.get('oz', []):
            kopya.append((a, u, ax + i_x, ay + i_y))
        for p in node['cocuk']:
            yay(p, ax + p['ox'], ay + p['oy'], u)

    for a, u in enumerate(us):
        ox, oy = konumlar[a]
        for p in usul_dugum[u]['cocuk']:
            yay(p, ox + p['ox'], oy + p['oy'], u)
    return mutlak, kopya, [(konumlar[a][0], konumlar[a][1], usul_dugum[u]['r'], u) for a, u in enumerate(us)]


def renkler(kat):
    mertebe = max(c['d'] for c in kat) + 1
    grup = collections.defaultdict(list)
    for k, c in enumerate(kat):
        grup[(c['u'], c['d'])].append(k)
    for k, c in enumerate(kat):
        hue = (HUE_SIRASI[c['u']] * 36 + 8) / 360.0
        js = grup[(c['u'], c['d'])]
        sira = js.index(k)
        sapma = (sira / max(len(js) - 1, 1) - 0.5) * 14 / 360.0
        l = 0.27 + 0.11 * c['d']
        r, g, b = colorsys.hls_to_rgb((hue + sapma) % 1.0, min(l, 0.78), 0.66)
        c['renk'] = '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
    usul_renk = []
    for u in range(len(USULLER)):
        r, g, b = colorsys.hls_to_rgb((HUE_SIRASI[u] * 36 + 8) / 360.0, 0.45, 0.7)
        usul_renk.append('#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255)))
    return usul_renk, mertebe


def yaz():
    dugumler = yukle()
    n = len(dugumler)
    kat, kimlik = kategoriler(dugumler)
    print('kategori', len(kat), 'üyelik', sum(len(c['uye']) for c in kat), flush=True)
    sebep = SB.sebepleri_yaz(kat, dugumler, [a for a, _ in USULLER])
    sebep_ozeti = {}
    for k, c in enumerate(kat):
        o = sebep_ozeti.setdefault(USULLER[c['u']][0], {'tek_sebepli': 0, 'cok_sebepli': 0})
        o['tek_sebepli' if sebep[k]['t'] else 'cok_sebepli'] += 1
    P0, _ = baslangic(n, kat)
    P = eniyile(n, kat, P0)
    izgara, kayma = izgaraya_otur(P)
    dai = daireler(izgara, kat)
    ihlal, toplam, kenarda, ortusme = olcut(izgara, kat, dai)
    usul_renk, mertebe = renkler(kat)
    b_mutlak, b_kopya, b_bolge = bolge_yerlesimi(kat, dugumler)
    b_ihlal = 0
    for a, u, x, y in b_kopya:
        pass
    benzersiz = len(set(map(tuple, izgara.tolist()))) == n
    eksende = bool(np.all(izgara % GRID_ARALIK == 0))
    harita = max(np.ptp(izgara[:, 0]), np.ptp(izgara[:, 1])) / 2
    yar = collections.defaultdict(list)
    for k, c in enumerate(kat):
        yar[(c['u'], c['d'])].append(dai[k][2] / harita)
    ozet_yaricap = {'%s/%d' % (USULLER[u][0], d + 1): round(float(np.median(v)), 2) for (u, d), v in sorted(yar.items())}
    u_derin = {}
    for c in kat:
        u_derin[c['u']] = max(u_derin.get(c['u'], 0), c['d'] + 1)
    ek = ek_bilgi(dugumler)
    dgs = []
    leaf = {}
    for k, c in enumerate(kat):
        if not c['cocuk']:
            pass
    for i, dg in enumerate(dugumler):
        s = []
        for u, yol in dg['yollar'].items():
            ui = [a for a, _ in USULLER].index(u)
            for d in range(len(yol)):
                s.append(kimlik[(ui, tuple(yol[:d + 1]))])
        dgs.append({'k': dg['kok'], 'x': int(izgara[i][0]), 'y': int(izgara[i][1]), 's': s, 'm': ek[i]['mana'], 'kw': ek[i]['kw'], 'e': ek[i]['e'], 'l': ek[i]['l'], 'w': dg['kelime'], 'g': dg['gecis'], 'q': 1 if dg['kuran'] else 0})
    veri = {
        'usuller': [{'ad': ad, 'renk': usul_renk[i], 'derin': u_derin.get(i, 0)} for i, (a, ad) in enumerate(USULLER)],
        'mertebe': mertebe,
        'siniflar': [{'u': c['u'], 'm': c['d'] + 1, 'ad': c['ad'], 'x': round(dai[k][0], 1), 'y': round(dai[k][1], 1), 'r': round(dai[k][2], 1), 'n': len(c['uye']), 'a': c['ata'], 'c': c['renk'], 'b': sebep[k]['b'], 's': sebep[k]['s'], 't': sebep[k]['t'], 'al': sebep[k].get('alt', [])} for k, c in enumerate(kat)],
        'dugumler': dgs,
        'bolge': {'siniflar': [[round(m[0], 1), round(m[1], 1), round(m[2], 1)] for m in b_mutlak], 'kopya': [[a, u, round(x), round(y)] for a, u, x, y in b_kopya], 'usul_daireleri': [[round(x, 1), round(y, 1), round(r, 1), u] for x, y, r, u in b_bolge]},
        'olcut': {'sebep_ozeti': sebep_ozeti, 'dugum': n, 'kategori': len(kat), 'uyelik': toplam, 'daire_disinda_kalan_uyelik': ihlal, 'hudutta_duran_uyelik_orani': round(kenarda / toplam, 3),
                  'ayni_usul_ve_mertebede_ortusme_orani': ortusme, 'ortanca_daire_yaricapi_harita_yaricapina_orani': ozet_yaricap,
                  'her_dugum_ayri_hucrede': benzersiz, 'hepsi_izgara_noktasinda': eksende, 'en_az_dugum_arasi_uzaklik': GRID_ARALIK,
                  'ortalama_kayma_hucre': round(float(np.mean(kayma)), 2), 'en_buyuk_kayma_hucre': int(max(kayma))},
    }
    html = SAYFA.replace('/*VERI*/', json.dumps(veri, ensure_ascii=False, separators=(',', ':')))
    with open(CIKTI, 'w', encoding='utf-8') as f:
        f.write(html)
    print(json.dumps(veri['olcut'], ensure_ascii=False))


SAYFA = r"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kategori Yerleşimi</title>
<style>
:root{--bg:#fbf8f1;--fg:#222;--panel:#fffdf8;--line:#d8d0bd;--mut:#6b6558}
@media (prefers-color-scheme:dark){:root{--bg:#1a1814;--fg:#ece6d6;--panel:#23201a;--line:#3a352b;--mut:#a79f8b}}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font-family:Georgia,serif}
#app{display:grid;grid-template-columns:310px 1fr;grid-template-rows:minmax(0,1fr);height:100%}
#yan{min-height:0;overflow:auto;padding:12px 14px;background:var(--panel);border-right:1px solid var(--line);font-size:13px;line-height:1.5}
#yan h1{font-size:17px;margin:0 0 6px}#yan h2{font-size:12px;margin:14px 0 4px;color:var(--mut);font-weight:normal;letter-spacing:.04em}
#yan label{display:flex;align-items:center;gap:6px;margin:2px 0;cursor:pointer}
.sw{width:11px;height:11px;border-radius:50%;display:inline-block;flex:none}
#sahne{position:relative;min-width:0;min-height:0;overflow:hidden;user-select:none;-webkit-user-select:none}canvas{position:absolute;left:0;top:0;display:block;width:100%;height:100%;cursor:grab;touch-action:none}
#zum{position:absolute;right:12px;bottom:12px;display:flex;flex-direction:column;gap:6px}#zum button{font:inherit;font-size:16px;min-width:44px;height:40px;border:1px solid var(--line);background:var(--panel);color:var(--fg);border-radius:6px;cursor:pointer}
#ara{width:100%;padding:5px 7px;font:inherit;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;direction:rtl}
#bilgi{margin-top:8px;padding:8px;border:1px solid var(--line);border-radius:6px;min-height:60px}
#bilgi b.k{font-size:20px;direction:rtl;display:inline-block}
.not{color:var(--mut);font-size:12px}
#ipucu{position:absolute;display:none;max-width:380px;padding:7px 9px;border:1px solid var(--line);background:var(--panel);color:var(--fg);border-radius:6px;font-size:12px;line-height:1.45;pointer-events:none;box-shadow:0 2px 8px rgba(0,0,0,.25);z-index:5}
#sonuc{max-height:190px;overflow:auto;margin-top:4px}#sonuc div{padding:3px 4px;border-bottom:1px solid var(--line);cursor:pointer;font-size:12px}#sonuc div:hover{background:var(--bg)}#sonuc b{font-size:15px;direction:rtl;display:inline-block;margin-left:6px}
details summary{cursor:pointer;font-size:13px;color:var(--fg)}details ul li{margin:3px 0}
.kk{padding:2px 4px;margin:1px;border:1px solid var(--line);border-radius:4px;cursor:pointer;display:inline-block;font-size:12px}.kk:hover{background:var(--bg)}.kk b{font-size:14px;direction:rtl;display:inline-block}
.bag{cursor:pointer;text-decoration:underline}.bas{font-size:13px;font-weight:bold}.kutu{margin:5px 0;padding:5px 7px;border-left:3px solid var(--line);font-size:12px;line-height:1.45;color:var(--fg)}.liste{max-height:240px;overflow:auto;margin-top:4px}
#bilgi,#kart{color:var(--fg)}
select,input[type=range]{width:100%;font:inherit;background:var(--bg);color:var(--fg)}
select{padding:4px;border:1px solid var(--line);border-radius:4px}
.yol{margin:6px 0}.sebep{font-size:11px;color:var(--mut);margin:1px 0 0 14px;line-height:1.35}.yol i{font-style:normal;color:var(--mut)}
@media(max-width:700px){#app{grid-template-columns:1fr;grid-template-rows:42% 58%}#yan{border-right:0;border-bottom:1px solid var(--line)}}
</style></head><body>
<div id="app">
<div id="yan">
<p><a href="kuran_hikmetleri_kitap.html">&larr; Kitap</a> · <a href="kuran_hikmetleri_lugat.html">Lugat</a></p>
<h1>Kategori Yerleşimi</h1>
<details id="nedir" open><summary>Bu sayfa nedir, nasıl okunur?</summary>
<div class="not" style="margin-top:4px">Kur'ân'ın ve Arapça lügatlerin <b id="ozetK"></b> kökü, on ayrı usulle (sesine, anlamına, konusuna, kitapta geçişine göre…) sınıflandı. Her sınıf bir <b>daire</b>, her kök bir <b>nokta</b>. Bir kök, ait olduğu bütün dairelerin içindedir; böylece <b>hangi kökler hangi bakımdan akraba</b> bir bakışta görülür.<ul style="margin:4px 0 4px 16px;padding:0">
<li><b>Bir köke bak:</b> aşağıdaki kutuya Arapça kökü, Türkçe ya da İngilizce bir anlamı yaz (örn. <i>دكك</i>, <i>ezmek</i>, <i>crush</i>).</li>
<li><b>Bir daireyi öğren:</b> daireye gel (bilgisayar) ya da dokun; <i>neden</i> bu köklerin bir arada olduğu yazılı çıkar.</li>
<li><b>Renk</b> usulü gösterir; daire koyulaştıkça mertebe (üst başlık) yükselir. <b>⚠</b> = bu dairedeki kökler tek sebeple toplanmıyor, içinde daha fazla küme var.</li>
<li>Çift dokunuş yakınlaştırır; iki parmak/tekerlek büyütür; sürükleyerek gez. Mertebe çubuğu daireleri en ayrıntılıdan en genele doğru gösterir.</li>
<li>Anlam açıklamalarının Türkçesi makine çevirisidir, İngilizce aslı yanında yazılıdır.</li></ul></div></details>
<h2>KÖK ARA</h2><input id="ara" placeholder="Arapça kök, Türkçe veya İngilizce anlam" autocomplete="off"><div id="sonuc"></div>
<h2>SEÇİLEN KÖK</h2><div id="bilgi" class="not">Bir noktaya dokun ya da yukarıdan ara.</div>
<h2>SEÇİLEN KATEGORİ</h2><div id="kart" class="not">Bir daireye dokun: bu köklerin neden bir arada olduğu burada tam yazılır.</div>
<h2>GÖRÜNÜM</h2><select id="mod"><option value="bolge">Usul bölgeleri: ayrık, iç içe daireler</option><option value="duzlem">Tek düzlem: kökler dairelerin kesişiminde</option></select>
<h2>MERTEBE (en alttan yukarı)</h2>
<input type="range" id="mert" min="1" max="4" value="4"><div class="not" id="mertYazi"></div>
<label><input type="checkbox" id="alt"> alt mertebeleri de göster</label>
<h2>DÜĞÜM RENGİ</h2><select id="renkUsul"></select>
<h2>USULLER (daire rengi = usul tonu; koyu = üst mertebe)</h2><div id="usuller"></div>
<h2>KURALLAR</h2>
<div class="not">Düğümler yalnız dik eksenlerde izgara noktasına oturur; iki düğüm arası en az <span id="adim"></span> birim; bir hücrede bir düğüm. Her kategorinin dairesi üyelerini ve alt kategori dairelerini kuşatır (<span id="ihlal"></span> ihlâl).</div>
<div class="not" id="olcut" style="margin-top:6px"></div>
<div class="not" id="sebepOzet" style="margin-top:6px"></div>
<div class="not" id="ozet" style="margin-top:6px"></div>
</div>
<div id="sahne"><canvas id="c"></canvas><div id="ipucu"></div><div id="zum"><button id="zp" title="Yakınlaştır (+)">+</button><button id="zm" title="Uzaklaştır (-)">&minus;</button><button id="zf" title="Sığdır (0)">Sığdır</button></div></div>
</div>
<script>
const V=/*VERI*/;
const cv=document.getElementById('c'),cx=cv.getContext('2d');
const css=getComputedStyle(document.documentElement);
function renk(n){return css.getPropertyValue(n).trim()}
let W=0,H=0,dpr=Math.max(1,window.devicePixelRatio||1);
let S=1,TX=0,TY=0,mod='bolge';
const adim=V.olcut.en_az_dugum_arasi_uzaklik;
const cell=new Map();V.dugumler.forEach((d,i)=>cell.set(d.x+','+d.y,i));
const KOP=V.bolge.kopya;const kopHuc=new Map();KOP.forEach((k,i)=>kopHuc.set(k[2]+','+k[3],i));
const nodKop=new Map();KOP.forEach((k,i)=>{if(!nodKop.has(k[0]))nodKop.set(k[0],[]);nodKop.get(k[0]).push(i)});
const leaf=V.dugumler.map(n=>{const g=new Map();n.s.forEach(k=>{const c=V.siniflar[k];if(!g.has(c.u)||V.siniflar[g.get(c.u)].m<c.m)g.set(c.u,k)});return g});
document.getElementById('adim').textContent=adim;document.getElementById('ozetK').textContent=V.olcut.dugum;
const esc=t=>String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const cocuk=V.siniflar.map(()=>[]);V.siniflar.forEach((c,k)=>{if(c.a>=0)cocuk[c.a].push(k)});const uyeler=V.siniflar.map(()=>[]);V.dugumler.forEach((n,i)=>n.s.forEach(k=>uyeler[k].push(i)));let seck=-1;
const tr=t=>(t||'').toLocaleLowerCase('tr');
document.getElementById('ihlal').textContent=V.olcut.daire_disinda_kalan_uyelik;
document.getElementById('ozet').textContent=V.olcut.dugum+' kök · '+V.olcut.kategori+' kategori · '+V.olcut.uyelik+' üyelik · '+V.mertebe+' mertebe';
document.getElementById('sebepOzet').innerHTML='<b>Sebep durumu</b> (⚠ = birden çok sebep, içinde daha fazla küme var):<br>'+Object.entries(V.olcut.sebep_ozeti).map(([u,o])=>u+': '+o.tek_sebepli+' tek'+(o.cok_sebepli?', <b>'+o.cok_sebepli+' çok sebepli</b>':'')).join('<br>');
document.getElementById('olcut').textContent='Tek düzlemde üyelerin %'+Math.round(V.olcut.hudutta_duran_uyelik_orani*100)+'\'i kendi dairesinin dış çeyreğinde duruyor; usul bölgeleri görünümünde daireler iç içedir ve aynı usulde hiçbir daire kesişmez.';
const goster=new Set(V.usuller.map((_,i)=>i));let renkU=2,sec=-1,hov=-1,mert=V.mertebe,alt=false;
const ul=document.getElementById('usuller');
V.usuller.forEach((u,i)=>{const l=document.createElement('label');l.innerHTML='<input type="checkbox" checked data-u="'+i+'"><span class="sw" style="background:'+u.renk+'"></span>'+u.ad+' <span class="not">('+u.derin+' mertebe)</span>';ul.appendChild(l)});
ul.addEventListener('change',e=>{const i=+e.target.dataset.u;e.target.checked?goster.add(i):goster.delete(i);ciz()});
const rs=document.getElementById('renkUsul');rs.innerHTML=V.usuller.map((u,i)=>'<option value="'+i+'">'+u.ad+'</option>').join('');rs.value='2';rs.onchange=()=>{renkU=+rs.value;ciz()};
const mr=document.getElementById('mert');mr.max=V.mertebe;mr.value=V.mertebe;
function mertYazi(){document.getElementById('mertYazi').textContent='Mertebe '+mert+' / '+V.mertebe+(mert===V.mertebe?' (en ince)':(mert===1?' (en üst)':''))}
mr.oninput=()=>{mert=+mr.value;mertYazi();ciz()};mertYazi();
document.getElementById('alt').onchange=e=>{alt=e.target.checked;ciz()};
const ms=document.getElementById('mod');ms.value='bolge';ms.onchange=()=>{mod=ms.value;fit();ciz()};
function gorunur(c){if(!goster.has(c.u))return false;const d=V.usuller[c.u].derin;const hedef=Math.min(mert,d);return alt?c.m>=hedef:c.m===hedef}
function cd(c,k){return mod==='duzlem'?[c.x,c.y,c.r]:V.bolge.siniflar[k]}
function fit(){let a=1e9,b=-1e9,c=1e9,d=-1e9;if(mod==='duzlem'){V.dugumler.forEach(n=>{a=Math.min(a,n.x);b=Math.max(b,n.x);c=Math.min(c,n.y);d=Math.max(d,n.y)})}else{V.bolge.usul_daireleri.forEach(u=>{a=Math.min(a,u[0]-u[2]);b=Math.max(b,u[0]+u[2]);c=Math.min(c,u[1]-u[2]);d=Math.max(d,u[1]+u[2])})}
S=Math.min(W/(b-a+6),H/(d-c+6));TX=W/2-S*(a+b)/2;TY=H/2-S*(c+d)/2}
let ilkSigdir=true;function resize(){const r=cv.parentElement.getBoundingClientRect();W=r.width;H=r.height;dpr=Math.max(1,window.devicePixelRatio||1);cv.width=W*dpr;cv.height=H*dpr;if(ilkSigdir){fit();ilkSigdir=false}ciz()}
const sx=x=>x*S+TX,sy=y=>y*S+TY;
function dairesel(x,y,r){const hx=Math.abs(x-W/2),hy=Math.abs(y-H/2);const dmin=Math.hypot(Math.max(hx-W/2,0),Math.max(hy-H/2,0));const dmax=Math.hypot(hx+W/2,hy+H/2);return r>=dmin&&r<=dmax}
function leafRenk(n,u){const k=leaf[n].get(u);return k===undefined?'#bbb':V.siniflar[k].c}
let bekle=false;function ciz(){if(bekle)return;bekle=true;requestAnimationFrame(()=>{bekle=false;ciz_()})}
function ciz_(){
cx.setTransform(dpr,0,0,dpr,0,0);cx.clearRect(0,0,W,H);cx.fillStyle=renk('--bg');cx.fillRect(0,0,W,H);
if(mod==='bolge'){V.bolge.usul_daireleri.forEach(u=>{if(!goster.has(u[3]))return;const x=sx(u[0]),y=sy(u[1]),r=u[2]*S;if(!dairesel(x,y,r)&&!(r>Math.hypot(W,H)))return;cx.beginPath();cx.arc(x,y,r,0,6.2832);cx.fillStyle=V.usuller[u[3]].renk+'12';cx.fill();cx.strokeStyle=V.usuller[u[3]].renk;cx.lineWidth=2;cx.stroke();cx.fillStyle=V.usuller[u[3]].renk;cx.font='bold 13px sans-serif';cx.fillText(V.usuller[u[3]].ad,x-r*0.8,y-r-6)})}
V.siniflar.forEach((c,k)=>{if(!gorunur(c))return;const g=cd(c,k);const x=sx(g[0]),y=sy(g[1]),r=g[2]*S;if(r<(mod==='bolge'?3:5)||!dairesel(x,y,r))return;cx.beginPath();cx.arc(x,y,r,0,6.2832);cx.strokeStyle=c.c;cx.globalAlpha=.85;cx.lineWidth=c.m===mert?1.4:1;cx.stroke();cx.globalAlpha=1;if(r>46){cx.fillStyle=c.c;cx.textAlign='center';cx.font='bold 11px sans-serif';let t=(c.t?'':'⚠ ')+c.b+' ('+c.n+')',w=Math.max(r*2.2,180);while(t.length>6&&cx.measureText(t).width>w)t=t.slice(0,-2);if(t.length<((c.t?'':'⚠ ')+c.b+' ('+c.n+')').length)t+='…';cx.fillText(t,x,y-r-5);cx.textAlign='start'}});
if(seck>=0){const c=V.siniflar[seck],g=cd(c,seck);cx.beginPath();cx.arc(sx(g[0]),sy(g[1]),g[2]*S,0,6.2832);cx.strokeStyle=renk('--fg');cx.lineWidth=2.5;cx.setLineDash([7,4]);cx.stroke();cx.setLineDash([])}
const px=Math.min(16,Math.max(1.4,adim*S*0.55));
if(mod==='duzlem'){V.dugumler.forEach((n,i)=>{const x=sx(n.x),y=sy(n.y);if(x<-px||y<-px||x>W+px||y>H+px)return;cx.fillStyle=leafRenk(i,renkU);cx.fillRect(x-px/2,y-px/2,px,px)});
if(S*adim>16){cx.font=Math.max(7,Math.min(15,S*adim*0.32))+'px Georgia';cx.textAlign='center';cx.fillStyle=renk('--fg');V.dugumler.forEach(n=>{const x=sx(n.x),y=sy(n.y);if(x<0||y<0||x>W||y>H)return;cx.fillText(n.k,x,y-px/2-2)});cx.textAlign='start'}}
else{KOP.forEach(k=>{if(!goster.has(k[1]))return;const x=sx(k[2]),y=sy(k[3]);if(x<-px||y<-px||x>W+px||y>H+px)return;cx.fillStyle=leafRenk(k[0],k[1]);cx.fillRect(x-px/2,y-px/2,px,px)});
if(S*adim>16){cx.font=Math.max(7,Math.min(15,S*adim*0.32))+'px Georgia';cx.textAlign='center';cx.fillStyle=renk('--fg');KOP.forEach(k=>{if(!goster.has(k[1]))return;const x=sx(k[2]),y=sy(k[3]);if(x<0||y<0||x>W||y>H)return;cx.fillText(V.dugumler[k[0]].k,x,y-px/2-2)});cx.textAlign='start'}}
const a=hov>=0?hov:sec;if(a>=0){const n=V.dugumler[a];
if(mod==='duzlem'){cx.save();for(const k of leaf[a].values()){const c=V.siniflar[k];cx.beginPath();cx.arc(sx(c.x),sy(c.y),c.r*S,0,6.2832);cx.clip()}
cx.fillStyle='rgba(255,200,0,.32)';cx.fillRect(0,0,W,H);cx.restore();
n.s.forEach(k=>{const c=V.siniflar[k];cx.beginPath();cx.arc(sx(c.x),sy(c.y),c.r*S,0,6.2832);cx.strokeStyle=c.c;cx.lineWidth=1.8;cx.stroke()});
cx.beginPath();cx.arc(sx(n.x),sy(n.y),Math.max(6,px),0,6.2832);cx.strokeStyle=renk('--fg');cx.lineWidth=2;cx.stroke()}
else{const ks=(nodKop.get(a)||[]).map(i=>KOP[i]);n.s.forEach(k=>{const g=V.bolge.siniflar[k],c=V.siniflar[k];cx.beginPath();cx.arc(sx(g[0]),sy(g[1]),g[2]*S,0,6.2832);cx.strokeStyle=c.c;cx.lineWidth=2;cx.stroke()});
const p0=ks[0];ks.forEach(k=>{cx.beginPath();cx.arc(sx(k[2]),sy(k[3]),Math.max(6,px),0,6.2832);cx.strokeStyle=renk('--fg');cx.lineWidth=2;cx.stroke();if(p0&&k!==p0){cx.beginPath();cx.moveTo(sx(p0[2]),sy(p0[3]));cx.lineTo(sx(k[2]),sy(k[3]));cx.strokeStyle='rgba(120,120,120,.35)';cx.lineWidth=1;cx.stroke()}})}}}
function bag(k,t){return '<span class="bag" data-k="'+k+'" style="color:'+V.siniflar[k].c+'">'+esc(t)+'</span>'}
function bilgi(i){const el=document.getElementById('bilgi');if(i<0){el.innerHTML='<span class="not">Bir noktaya dokun ya da yukarıdan ara.</span>';return}
const n=V.dugumler[i];const by={};n.s.forEach(k=>{const c=V.siniflar[k];(by[c.u]=by[c.u]||[]).push(c)});
const kw=n.kw.slice().sort((a,b)=>b[2]-a[2]);
el.innerHTML='<b class="k" style="font-size:22px">'+n.k+'</b> <span class="not">'+(n.q?'Kur\'ân\'da var':'Kur\'ân\'da yok')+' · '+n.w+' kelime · '+n.g+' geçiş</span>'
+(n.m?'<div class="kutu"><b>Anlamı:</b> '+esc(n.m)+'</div>':'<div class="kutu not">Bu kök için Türkçe anlam kaydı yok.</div>')
+(n.e.length?'<div class="kutu"><b>İngilizce karşılığı (WordNet):</b>'+n.e.map(x=>'<div>• <i>'+esc(x[0])+'</i>: '+esc(x[1])+(x[2]?' <span class="not">(otomatik çeviri)</span>':'')+'</div>').join('')+'</div>':'')
+(kw.length?'<div class="kutu"><b>Kur\'ân\'daki kelimeleri:</b><div class="liste">'+kw.map(x=>'<div><span style="direction:rtl;display:inline-block;font-size:15px">'+esc(x[0])+'</span> — '+esc(x[1]||'?')+' <span class="not">('+x[2]+' yer)</span></div>').join('')+'</div></div>':'')
+'<div style="margin-top:6px"><b>Ait olduğu kategoriler</b> <span class="not">('+n.s.length+'; adına dokun, sebebini oku)</span></div>'
+Object.keys(by).map(u=>'<div class="yol"><span class="sw" style="background:'+V.usuller[u].renk+'"></span> <span class="not">'+esc(V.usuller[u].ad)+'</span><br>'+by[u].sort((a,b)=>a.m-b.m).map(c=>bag(V.siniflar.indexOf(c),(c.t?'':'⚠ ')+c.b)).join(' <i>›</i> ')+'</div>').join('')}
function kart(k,git_){seck=k;const c=V.siniflar[k],el=document.getElementById('kart');
const zincir=[];for(let a=k;a>=0;a=V.siniflar[a].a)zincir.unshift(a);
const alt=cocuk[k].slice().sort((a,b)=>V.siniflar[b].n-V.siniflar[a].n);
const uy=uyeler[k].slice().sort((a,b)=>V.dugumler[b].g-V.dugumler[a].g);
const ust=c.a>=0?V.siniflar[c.a]:null;
el.innerHTML='<div class="bas"><span class="sw" style="background:'+c.c+'"></span> '+esc((c.t?'':'⚠ ')+c.b)+'</div>'
+'<div class="not">'+esc(V.usuller[c.u].ad)+' · mertebe '+c.m+' · <b>'+c.n+'</b> kök</div>'
+'<div class="not" style="margin:3px 0">'+zincir.map(a=>bag(a,V.siniflar[a].b)).join(' <i>›</i> ')+'</div>'
+'<div class="kutu" style="border-color:'+c.c+'"><b>Bu kökler neden bir arada?</b><br>'+esc(c.s)+'</div>'
+(c.al&&c.al.length?'<div class="kutu"><b>İçindeki sebepler:</b>'+c.al.map(x=>'<div>• <b>'+x[0]+' birim:</b> '+esc(x[1])+'</div>').join('')+'</div>':'')
+(ust?'<div class="kutu not"><b>Üst kategori</b> '+bag(c.a,ust.b)+' ('+ust.n+' kök): '+esc(ust.s)+'</div>':'')
+(alt.length?'<div style="margin-top:4px"><b>Alt kategoriler</b> <span class="not">('+alt.length+')</span></div><div class="liste">'+alt.slice(0,80).map(a=>'<div>• '+bag(a,(V.siniflar[a].t?'':'⚠ ')+V.siniflar[a].b)+' <span class="not">('+V.siniflar[a].n+')</span></div>').join('')+(alt.length>80?'<div class="not">… ve '+(alt.length-80)+' tane daha</div>':'')+'</div>':'')
+'<div style="margin-top:4px"><b>Kökler</b> <span class="not">(en çok geçenden; dokun)</span></div><div class="liste">'+uy.slice(0,150).map(i=>'<span class="kk" data-i="'+i+'" title="'+esc(V.dugumler[i].m)+'"><b>'+V.dugumler[i].k+'</b> <span class="not">'+esc((V.dugumler[i].m||'').split(/[:;,.]/).slice(0,2).join(',').slice(0,28))+'</span></span>').join('')+(uy.length>150?'<div class="not">… ve '+(uy.length-150)+' kök daha (daireyi yakınlaştırınca noktalar görünür)</div>':'')+'</div>'
+'<div style="margin-top:6px"><button id="kgit" style="font:inherit;padding:4px 8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:5px;cursor:pointer">Bu daireye yakınlaş</button></div>';
document.getElementById('kgit').onclick=()=>daireGit(k);ciz()}
function daireGit(k){const g=cd(V.siniflar[k],k);const ns=Math.min(120,Math.min(W,H)/2/(g[2]*1.15));git(ns,W/2-ns*g[0],H/2-ns*g[1])}
function kokaGit(i){sec=i;const h=mod==='duzlem'?[V.dugumler[i].x,V.dugumler[i].y]:[KOP[nodKop.get(i)[0]][2],KOP[nodKop.get(i)[0]][3]];const ns=Math.max(S,14);git(ns,W/2-ns*h[0],H/2-ns*h[1]);bilgi(i);try{history.replaceState(null,'','#'+encodeURIComponent(V.dugumler[i].k))}catch(e){}}
function katAt(mx,my){const wx=(mx-TX)/S,wy=(my-TY)/S;let best=-1,br=1e18;V.siniflar.forEach((c,k)=>{if(!gorunur(c))return;const g=cd(c,k);if(Math.hypot(wx-g[0],wy-g[1])<=g[2]&&g[2]<br){br=g[2];best=k}});return best}
document.getElementById('yan').addEventListener('click',e=>{const t=e.target.closest('[data-k],[data-i]');if(!t)return;if(t.dataset.k!==undefined){const k=+t.dataset.k;kart(k);if(!window.matchMedia('(max-width:700px)').matches||true)daireGit(k)}else kokaGit(+t.dataset.i)});
const ip=document.getElementById('ipucu');
function ipucuGoster(k,mx,my){if(k<0){ip.style.display='none';return}const c=V.siniflar[k];ip.innerHTML='<b style="color:'+c.c+'">'+esc((c.t?'':'⚠ ')+c.b)+'</b> <span class="not">· '+esc(V.usuller[c.u].ad)+' · '+c.n+' kök</span><br>'+esc(c.s)+(c.al&&c.al.length?'<br>'+c.al.map(x=>'• '+x[0]+': '+esc(x[1])).join('<br>'):'')+'<br><span class="not">Tam bilgi için dokun/tıkla.</span>';ip.style.display='block';const w=ip.offsetWidth,h=ip.offsetHeight;ip.style.left=Math.max(4,Math.min(W-w-4,mx+14))+'px';ip.style.top=Math.max(4,Math.min(H-h-4,my+14))+'px'}
function ata(mx,my){const wx=(mx-TX)/S,wy=(my-TY)/S;const gx=Math.round(wx/adim)*adim,gy=Math.round(wy/adim)*adim;if(mod==='duzlem'){const i=cell.get(gx+','+gy);return i===undefined?-1:i}const ci=kopHuc.get(gx+','+gy);return ci===undefined?-1:KOP[ci][0]}
const ex=e=>e.clientX-cv.getBoundingClientRect().left,ey=e=>e.clientY-cv.getBoundingClientRect().top;
let sur=false,lx=0,ly=0,hareket=0;
let anim=0;function git(ns,ntx,nty){cancelAnimationFrame(anim);const s0=S,c0x=(W/2-TX)/S,c0y=(H/2-TY)/S,c1x=(W/2-ntx)/ns,c1y=(H/2-nty)/ns,t0=performance.now(),ls=Math.log(ns/s0);
function adimla(t){let k=Math.min(1,(t-t0)/240);k=k*k*(3-2*k);S=s0*Math.exp(ls*k);const wx=c0x+(c1x-c0x)*k,wy=c0y+(c1y-c0y)*k;TX=W/2-S*wx;TY=H/2-S*wy;ciz();if(t-t0<240)anim=requestAnimationFrame(adimla)}anim=requestAnimationFrame(adimla)}
function yakin(f,ox,oy,yumusak){cancelAnimationFrame(anim);const ns=Math.min(120,Math.max(0.03,S*f));const ntx=ox-(ox-TX)*ns/S,nty=oy-(oy-TY)*ns/S;if(yumusak){git(ns,ntx,nty)}else{TX=ntx;TY=nty;S=ns;ciz()}}
let tikZ=0;const ptr=new Map();let pdist=0,pm=[0,0];
function pdis(){const v=[...ptr.values()];return Math.hypot(v[0][0]-v[1][0],v[0][1]-v[1][1])}
function pmer(){const v=[...ptr.values()];return [(v[0][0]+v[1][0])/2,(v[0][1]+v[1][1])/2]}
cv.addEventListener('pointerdown',e=>{ip.style.display='none';cancelAnimationFrame(anim);ptr.set(e.pointerId,[ex(e),ey(e)]);if(ptr.size===2){pdist=pdis();pm=pmer();hareket=100}sur=true;lx=ex(e);ly=ey(e);hareket=0;cv.setPointerCapture(e.pointerId);cv.style.cursor='grabbing'});
cv.addEventListener('pointermove',e=>{if(ptr.has(e.pointerId))ptr.set(e.pointerId,[ex(e),ey(e)]);
if(ptr.size===2){const d=pdis(),m=pmer();TX+=m[0]-pm[0];TY+=m[1]-pm[1];if(pdist>0)yakin(d/pdist,m[0],m[1]);pdist=d;pm=m;hareket=100;return}
if(sur){const ddx=ex(e)-lx,ddy=ey(e)-ly;hareket+=Math.abs(ddx)+Math.abs(ddy);lx=ex(e);ly=ey(e);if(hareket>=4){TX+=ddx;TY+=ddy;ciz()}}else if(e.pointerType==='mouse'){const i=ata(ex(e),ey(e));if(i!==hov){hov=i;bilgi(hov>=0?hov:sec);ciz()}ipucuGoster(i>=0?-1:katAt(ex(e),ey(e)),ex(e),ey(e))}});
cv.addEventListener('pointerleave',()=>{ip.style.display='none'});
function birak(e){ptr.delete(e.pointerId);if(ptr.size<2)pdist=0;if(ptr.size===1){const v=[...ptr.values()][0];lx=v[0];ly=v[1];hareket=100}if(ptr.size===0){sur=false;cv.style.cursor='grab'}}
function daireyeGit(mx,my){const wx=(mx-TX)/S,wy=(my-TY)/S;const yar=Math.min(W,H)/2/S*0.9;let best=-1,br=-1,small=-1,sr=1e18;V.siniflar.forEach((c,k)=>{if(!goster.has(c.u))return;const g=cd(c,k);if(Math.hypot(wx-g[0],wy-g[1])<=g[2]){if(g[2]<yar*0.95&&g[2]>br){br=g[2];best=k}if(g[2]<sr){sr=g[2];small=k}}});const k=best>=0?best:small;if(k<0)return;const g=cd(V.siniflar[k],k);const ns=Math.min(120,Math.min(W,H)/2/(g[2]*1.15));git(ns,W/2-ns*g[0],H/2-ns*g[1])}
cv.addEventListener('pointerup',e=>{const h=hareket;birak(e);if(h<4){const i=ata(ex(e),ey(e));if(i>=0){sec=i;bilgi(i);ciz();try{history.replaceState(null,'','#'+encodeURIComponent(V.dugumler[i].k))}catch(_){}}else if(e.shiftKey){daireyeGit(ex(e),ey(e))}else{const k=katAt(ex(e),ey(e));if(k>=0)kart(k);else{ciz()}}ip.style.display='none'}});
cv.addEventListener('pointercancel',birak);
cv.addEventListener('wheel',e=>{e.preventDefault();clearTimeout(tikZ);const dy=e.deltaY*(e.deltaMode===1?16:(e.deltaMode===2?400:1));yakin(Math.exp(-dy*(e.ctrlKey?0.012:0.004)),ex(e),ey(e))},{passive:false});
cv.addEventListener('dblclick',e=>{e.preventDefault();clearTimeout(tikZ);yakin(2,ex(e),ey(e),true)});
let g0=1;document.addEventListener('gesturestart',e=>{e.preventDefault();g0=S;cancelAnimationFrame(anim)});document.addEventListener('gesturechange',e=>{e.preventDefault();const r=cv.getBoundingClientRect();yakin(g0*e.scale/S,e.clientX-r.left,e.clientY-r.top)});document.addEventListener('gestureend',e=>e.preventDefault());
document.getElementById('zp').onclick=()=>yakin(1.6,W/2,H/2,true);document.getElementById('zm').onclick=()=>yakin(1/1.6,W/2,H/2,true);document.getElementById('zf').onclick=()=>{let a=1e9,b=-1e9,c=1e9,d=-1e9;if(mod==='duzlem'){V.dugumler.forEach(n=>{a=Math.min(a,n.x);b=Math.max(b,n.x);c=Math.min(c,n.y);d=Math.max(d,n.y)})}else{V.bolge.usul_daireleri.forEach(u=>{a=Math.min(a,u[0]-u[2]);b=Math.max(b,u[0]+u[2]);c=Math.min(c,u[1]-u[2]);d=Math.max(d,u[1]+u[2])})}const ns=Math.min(W/(b-a+6),H/(d-c+6));git(ns,W/2-ns*(a+b)/2,H/2-ns*(c+d)/2)};
window.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT')return;if(e.key==='+'||e.key==='=')yakin(1.4,W/2,H/2,true);else if(e.key==='-')yakin(1/1.4,W/2,H/2,true);else if(e.key==='0'){fit();ciz()}});
const sn=document.getElementById('sonuc');
function ara(q){q=q.trim();if(!q){sn.innerHTML='';return[]}const ql=tr(q);const arapca=/[\u0600-\u06FF]/.test(q);const sk=[];
V.dugumler.forEach((n,i)=>{let p=0,ne='';if(arapca){if(n.k===q)p=100;else if(n.k.includes(q))p=60;else if(n.kw.some(x=>x[0].includes(q))){p=40;ne='kelime'}}else{const m=tr(n.m);
if(n.l.some(l=>tr(l)===ql)){p=90;ne=n.l.find(l=>tr(l)===ql)}else if(m.split(/[^a-zçğıöşü]+/).includes(ql)){p=80;ne=n.m}else if(n.l.some(l=>tr(l).includes(ql))){p=50;ne=n.l.find(l=>tr(l).includes(ql))}else if(m.includes(ql)){p=45;ne=n.m}else if(n.kw.some(x=>tr(x[1]).includes(ql))){p=30;const x=n.kw.find(x=>tr(x[1]).includes(ql));ne=x[0]+' — '+x[1]}else if(n.e.some(x=>tr(x[1]).includes(ql))){p=20;ne=n.e.find(x=>tr(x[1]).includes(ql))[1]}}
if(p)sk.push([p,i,ne])});sk.sort((a,b)=>b[0]-a[0]||V.dugumler[b[1]].g-V.dugumler[a[1]].g);
sn.innerHTML=sk.length?sk.slice(0,40).map(x=>'<div data-i="'+x[1]+'"><b>'+V.dugumler[x[1]].k+'</b>'+esc((x[2]||V.dugumler[x[1]].m||'').slice(0,60))+'</div>').join('')+(sk.length>40?'<div class="not">… ve '+(sk.length-40)+' sonuç daha; aramayı daralt</div>':''):'<div class="not">Sonuç yok.</div>';return sk}
const aramaK=document.getElementById('ara');aramaK.addEventListener('input',e=>ara(e.target.value));
aramaK.addEventListener('keydown',e=>{if(e.key==='Enter'){const sk=ara(aramaK.value);if(sk.length)kokaGit(sk[0][1])}});
window.addEventListener('resize',resize);new ResizeObserver(()=>resize()).observe(cv.parentElement);resize();
try{const h=decodeURIComponent((location.hash||'').slice(1));if(h){const i=V.dugumler.findIndex(n=>n.k===h);if(i>=0)setTimeout(()=>kokaGit(i),50)}}catch(e){}
try{if(localStorage.getItem('kyGordu')||window.matchMedia('(max-width:700px)').matches)document.getElementById('nedir').open=false;localStorage.setItem('kyGordu','1')}catch(e){}
</script></body></html>
"""

if __name__ == '__main__':
    yaz()
