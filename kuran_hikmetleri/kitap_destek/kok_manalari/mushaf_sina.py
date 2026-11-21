"""Mushaf dizgisi: metinsiz (maskeli) geri okuma imtihanı (F 3-I 407).
Komutlar:  python3 mushaf_sina.py sanat DEV|TEST     -> maskeli iskeletler (okuyucuya verilecek metin)
           python3 mushaf_sina.py oto                 -> otomatik çözücüyle puan, ablasyon, V
           python3 mushaf_sina.py puan okuyucu.json DEV|TEST  -> insan/ajan okuyucusunun puanı
           python3 mushaf_sina.py kararlilik          -> iki ayrı süreçte aynı yerleşim mi"""
import sys, json, pathlib, hashlib, subprocess, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mushaf_dizgi as M
AN = json.load(open(HERE / 'mushaf' / 'anahtar.json', encoding='utf-8'))
WREF = 26.0; SUT = 4; COLS = int(WREF * SUT)
def ayet(k):
    s, a = map(int, k.split(':'))
    return json.load(open(M.HERE.parent.parent / 'kaynak' / 'sure' / ('%d.json' % s), encoding='utf-8'))['verses'][a - 1]['arabic'].strip(), a

def tokenler(arapca, sayi):   # yerleşimdeki jeton dizisi (âyet sonu işareti son kelimeye yapışık)
    return arapca.split()

def kutu(tok): return '█' * max(1, round(M.gen(tok) * SUT))

def iskelet(arapca, sayi, kurallar):
    """Maskeli satırlar: [(belirteç_kutuları, yatay_boşluk_bayrakları, girinti_kademe, yaslama, boş_satır_önce, [belirteç indisleri])]"""
    sat, h = M.yerles(arapca, sayi, WREF, kurallar); out = []; py = -1.0
    for (tk, fl, ins, sd, y, ix) in sat:
        ekstra = round(y - py - 1.0, 2)
        bos = 0 if ekstra < 0.3 else (1 if ekstra < 1.0 else 3)
        out.append(([kutu(t) for t in tk], fl, round(ins / M.INS), sd, bos, list(ix))); py = y
    son = round(h - (sat[-1][4] + 1.0), 2)
    return out, (1 if 0.3 <= son < 1.0 else (3 if son >= 1.0 else 0))

def sanat(arapca, sayi, kurallar, numara=True):
    rows = []; no = 0; ara = lambda fl: (' ' + '·' * round(M.HG * SUT)) if fl else ' '
    L_, son_ = iskelet(arapca, sayi, kurallar)
    for kut, fl, kad, sd, bos, idx in L_:
        for _ in range(bos): rows.append('   |' + ' ' * COLS + '|')
        no += 1; parcalar = []; pos = {}; cur = 0
        for q in range(len(kut) - 1, -1, -1):
            pos[q] = cur; parcalar.append(kut[q]); cur += len(kut[q])
            if q > 0: g = ara(fl[q]); parcalar.append(g); cur += len(g)
        ters = ''.join(parcalar); pad = COLS - len(ters)
        bas = round(M.HG * SUT) if fl[0] else 0
        pay = '·' * bas
        if sd == 'R': off = max(0, pad - kad * 6 - bas); s = ' ' * off + ters + pay + ' ' * (kad * 6)
        else: off = kad * 6; s = ' ' * off + ters + pay + ' ' * max(0, pad - kad * 6 - bas)
        rows.append('%02d |%s| (%d kutu)' % (no, s[:COLS].ljust(COLS), len(kut)))
        if numara:
            nr = [' '] * COLS
            for q in pos:
                t = str(q + 1); st = off + pos[q] + max(0, (len(kut[q]) - len(t)) // 2)
                for z, ch in enumerate(t):
                    if st + z < COLS: nr[st + z] = ch
            rows.append('   |%s|' % ''.join(nr))
    for _ in range(son_): rows.append('   |' + ' ' * COLS + '|')
    return '\n'.join(rows), len(rows)

def alan(arapca, sayi, kurallar):
    """Sınır kutusu alanı (genişlik × yükseklik), en dar uygun genişlikte aranır."""
    en = 1e18
    for W in (8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0, 28.0, 32.0, 40.0):
        sat, h = M.yerles(arapca, sayi, W, kurallar); used = 0.0
        for tk, fl, ins, sd, y, ix in sat:
            wd = sum(M.gen(t) for t in tk) + (len(tk) - 1) * M.gen(' ') + sum(fl) * M.HG + ins; used = max(used, wd)
        en = min(en, used * h)
    return en

def cozucu(arapca, sayi, kurallar):
    """Maskeli iskeletin geometrisini SIRF kod defterine göre okur (kelimelere bakmaz)."""
    L, SON = iskelet(arapca, sayi, kurallar); n = len(L); B = []
    def idxler(a, b): return sorted({i for q in range(a, b + 1) for i in L[q][5]})
    def kosu(pred):
        q = 0
        while q < n:
            if pred(L[q]):
                a = q
                while q + 1 < n and pred(L[q + 1]): q += 1
                yield a, q
            q += 1
    for a, b in kosu(lambda l: l[2] == 1 and l[3] == 'R'): B.append(('NAKIL', idxler(a, b)))
    for a, b in kosu(lambda l: l[2] >= 2 and l[3] == 'R'): B.append(('ARA', idxler(a, b)))
    for a, b in kosu(lambda l: l[3] == 'L'): B.append(('CEVAP', idxler(a, b)))
    for a, b in kosu(lambda l: l[3] == 'M'): B.append(('ISTISNA', idxler(a, b)))
    q = 0; bl = []
    while q < n:
        a = q
        while q + 1 < n and L[q + 1][4] == 0: q += 1
        bl.append((a, q)); q += 1
    for bi, (a, b) in enumerate(bl):
        alt = (L[bl[bi + 1][0]][4] if bi + 1 < len(bl) else SON)
        if L[a][4] == 3 and alt == 3: B.append(('HITAP', idxler(a, b)))
    q = 0
    while q < n:
        if L[q][4] == 1:
            a = q
            while q + 1 < n and L[q + 1][4] == 0 and (L[q + 1][2], L[q + 1][3]) == (L[a][2], L[a][3]): q += 1
            B.append(('ZITLIK', idxler(a, q)))
        q += 1
    # paralel: aynı imzalı ardışık (boşluksuz) satırlardan oluşan blokta yatay boşluklar kalemleri ayırır
    q = 0
    while q < n:
        r = q
        while r + 1 < n and (L[r + 1][2], L[r + 1][3]) == (L[q][2], L[q][3]) and L[r + 1][4] == 0: r += 1
        its = []; cur = []
        for z in range(q, r + 1):
            for t, i in enumerate(L[z][5]):
                if L[z][1][t] and cur: its.append(cur); cur = []
                cur.append(i)
        if cur: its.append(cur)
        z = r + 1
        while its and z < n and ((L[z][3] == 'R' and L[z][2] > L[q][2] and L[q][3] == 'R') or (L[z][3] == 'M' and L[q][3] == 'R')):
            its[-1] = its[-1] + list(L[z][5]); z += 1
        if len(its) >= 2:
            for it in its: B.append(('PARALEL', it))
        q = r + 1
    return B

def esles(anahtar, okunan, eşik=0.5):
    """anahtar: [(tip, a, b)], okunan: [(tip, [indisler])]; isâbet: tip aynı ve işaretsiz kelime kümelerinin IoU'su >= eşik."""
    T = None
    kul = set(); hit = 0; ok = []
    for tip, idx in okunan:
        S = set(idx)
        for ki, (kt, a, b) in enumerate(anahtar):
            if ki in kul or kt != tip: continue
            K = set(range(a, b + 1)); iou = len(K & S) / max(1, len(K | S))
            if iou >= eşik: kul.add(ki); hit += 1; ok.append((tip, ki)); break
    return hit, len(anahtar), len(okunan)

def isaretsiz(arapca, idx):
    T = arapca.split(); return [i for i in idx if i < len(T) and not M.isaret(T[i])]

def olc(kume, kurallar, okuyucu=None):
    hit = tot = oku = 0; alanlar = 0.0; duz = 0.0; ayrinti = {}
    for k, ban in AN[kume].items():
        ar, a = ayet(k); ban = [tuple(b) for b in ban]
        if okuyucu is None: okunan = [(t, isaretsiz(ar, idx)) for t, idx in cozucu(ar, a, kurallar)]
        else: okunan = okuyucu[k]
        h, t, o = esles([(x, y, z) for x, y, z in ban], okunan)
        hit += h; tot += t; oku += o; alanlar += alan(ar, a, kurallar); duz += alan(ar, a, ())
        ayrinti[k] = (h, t, o)
    return dict(hit=hit, tot=tot, oku=oku, recall=hit / max(1, tot), prec=hit / max(1, oku), alan=alanlar / duz, ayr=ayrinti)

def V(r, nk): return r['recall'] / (max(1, nk) * r['alan'])

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'sanat':
        for k in AN[sys.argv[2].lower()]:
            ar, a = ayet(k); print('### PASAJ %d' % list(AN[sys.argv[2].lower()]).index(k)); print(sanat(ar, a, M.KURALLAR)[0]); print()
    elif c == 'oto':
        for kume in ('dev', 'test', 'test2', 'test3', 'test4'):
            print('==', kume)
            for ad, kur in [('düz (kuralsız)', ()), ('7 kural', M.KURALLAR)] + [('-%s' % x, tuple(y for y in M.KURALLAR if y != x)) for x in M.KURALLAR] + [('yalnız %s' % x, (x,)) for x in M.KURALLAR]:
                r = olc(kume, kur)
                print('%-18s kural=%d  isabet=%d/%d (%%%.1f)  kesinlik=%%%.1f  alan×%.2f  V=%.3f' % (ad, len(kur), r['hit'], r['tot'], 100 * r['recall'], 100 * r['prec'], r['alan'], V(r, len(kur)) if kur else 0))
            r = olc(kume, M.KURALLAR)
            for k, (h, t, o) in r['ayr'].items(): print('   ', k, 'isabet %d/%d, okunan %d' % (h, t, o))
    elif c == 'puan':
        ok = json.load(open(sys.argv[2], encoding='utf-8')); kume = sys.argv[3].lower(); ks = list(AN[kume])
        haric = {int(x) for x in sys.argv[4:]}
        for hx in haric: ks_ = ks[hx]; AN[kume][ks_] = []
        okuyucu = {}
        for i, k in enumerate(ks):
            ar, a = ayet(k); It, _s = iskelet(ar, a, M.KURALLAR)
            okuyucu[k] = []
            for b in ok.get(str(i), []):
                if b.get('k1') and b.get('k2') and b['a'] == b['b'] and b['k1'] > b['k2']: b = dict(b, k1=b['k2'], k2=b['k1'])
                satirlar = range(b['a'] - 1, b['b']); idx = []
                for q in satirlar:
                    if 0 <= q < len(It):
                        li = list(It[q][5])
                        if q == b['a'] - 1 and b.get('k1'): li = li[b['k1'] - 1:]
                        if q == b['b'] - 1 and b.get('k2'): li = li[:b['k2']] if q != b['a'] - 1 or not b.get('k1') else li[:max(0, b['k2'] - b['k1'] + 1)]
                        idx += li
                idx = sorted(set(idx))
                okuyucu[k].append((b['tip'], isaretsiz(ar, idx)))
        r = olc(kume, M.KURALLAR, okuyucu)
        print('isabet=%d/%d (%%%.1f) kesinlik=%%%.1f alan×%.2f V=%.3f' % (r['hit'], r['tot'], 100 * r['recall'], 100 * r['prec'], r['alan'], V(r, 7)))
        for k, (h, t, o) in r['ayr'].items(): print('  ', k, h, t, o)
    elif c == 'kararlilik':
        h = []
        for _ in range(2):
            o = subprocess.run([sys.executable, '-I', str(HERE / 'mushaf_sina.py'), 'ozet'], capture_output=True, text=True, cwd='/').stdout; h.append(hashlib.sha256(o.encode()).hexdigest())
        print(h, 'ÖRTÜŞTÜ' if h[0] == h[1] else 'ÖRTÜŞMEDİ')
    elif c == 'ozet':
        for kume in ('dev', 'test', 'test2', 'test3', 'test4'):
            for k in AN[kume]:
                ar, a = ayet(k)
                for W in (18.0, 26.0, 40.0): print(k, W, M.yerles(ar, a, W, M.KURALLAR))
