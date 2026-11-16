import json
import os
import re

import istikak as I
import kuran_fiil

VOW = 'aeıioöuü'
ARKA = 'aıou'
KESIK = 'çfhkpsşt'
UN4 = {'a': 'ı', 'ı': 'ı', 'e': 'i', 'i': 'i', 'o': 'u', 'u': 'u', 'ö': 'ü', 'ü': 'ü'}
DB_YOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kaynak', 'lugat', 'kok_anlamlari.json')

ARAPCA_ET = set('emr sabr şükr kahr zikr nazar fikr ferm zann hükm affet'.split())
GECISSIZ = set('''ol gel git dur otur kalk uyu uyan öl doğ uç koş yürü gül ağla yüksel büyü küçül düş çık gir in bin yat kal geç kaç var yaşa
titre çürü sus bat piş yan ürper kork şaş sevin üz solu parla ışılda doy tüken eksil artı çoğal azal soğu ısın ısı sarar kızar ağar
uy morar yeşer sarkık tükür ak akış karar şişin inan'''.split())
GECISSIZ_EK = ('leş', 'laş', 'len', 'lan', 'ış', 'iş', 'uş', 'üş')
GECISSIZ_EK_UZUN = ('el', 'al', 'ıl', 'il', 'ul', 'ül', 'ik', 'ık', 'uk', 'ük')
DUZENSIZ_ETTIR = {'geç': 'geçir', 'kaç': 'kaçır', 'uç': 'uçur', 'düş': 'düşür', 'çık': 'çıkar', 'piş': 'pişir',
                  'doğ': 'doğur', 'kop': 'kopar', 'bat': 'batır', 'kork': 'korkut', 'otur': 'oturt', 'iç': 'içir',
                  'gel': 'getir', 'git': 'götür', 'öl': 'öldür', 'ol': 'et', 'ye': 'yedir', 'de': 'dedir'}


def son_unlu(s):
    for c in reversed(s):
        if c in VOW:
            return c
    return 'e'


def a_e(s):
    return 'a' if son_unlu(s) in ARKA else 'e'


def i4(s):
    return UN4[son_unlu(s)]


def unluyle_biter(s):
    return s[-1] in VOW


def hece(s):
    return sum(1 for c in s.split()[-1] if c in VOW)


def yum(v):
    if v == 'et' or v.endswith(' et') or v == 'git' or v.endswith(' git'):
        return v[:-1] + 'd'
    w = v.split()[-1]
    if len(w) >= 4 and w.endswith('et') and w[-3] not in VOW and w[-4] not in VOW and not w.endswith(('let', 'lat', 'ret', 'rat', 'net', 'nat')):
        return v[:-1] + 'd'
    if len(w) >= 5 and w.endswith(('ret', 'net')) and w[-4] not in VOW and w[-5] in VOW and w[:-2] in ARAPCA_ET:
        return v[:-1] + 'd'
    return v


def f_fail(v):
    w = yum(v)
    return w + ('y' if unluyle_biter(w) else '') + a_e(w) + 'n'


def f_mastar(v):
    return v + 'm' + a_e(v)


def f_pas(v):
    w = yum(v)
    if unluyle_biter(w):
        return w + 'n'
    if w.endswith('l'):
        return w + i4(w) + 'n'
    return w + i4(w) + 'l'


def f_mefp(v):
    p = f_pas(v)
    return p + 'm' + i4(p) + 'ş'


def f_pf(v):
    return v + 'm' + i4(v) + 'ş'


def f_istes(v):
    return v + 'ş' if unluyle_biter(v) else v + i4(v) + 'ş'


def f_donus(v):
    w = yum(v)
    return w + 'n' if unluyle_biter(w) else w + i4(w) + 'n'


def f_ettir(v):
    if v.endswith(' ol'):
        w = v[:-3]
        return w + ('leştir' if a_e(w) == 'e' else 'laştır') if ' ' not in w else w + ' et'
    if v in DUZENSIZ_ETTIR:
        return DUZENSIZ_ETTIR[v]
    if unluyle_biter(v) or (hece(v) > 1 and v[-1] in 'lr'):
        return v + 't'
    if v[-1] in KESIK:
        return v + 't' + i4(v) + 'r'
    return v + 'd' + i4(v) + 'r'


def cogul(s):
    return s + 'l' + a_e(s) + 'r'


def datif(s):
    return s + ('y' if unluyle_biter(s) else '') + a_e(s)


def f_acc(m):
    return m + 'y' + i4(m)


def gecislilik(stem):
    if stem.endswith(' et'):
        return 'tr', True
    if stem.endswith(' ol') or stem == 'ol':
        return 'aux', True
    w = stem.split()[-1]
    if w in GECISSIZ:
        return 'intr', True
    if len(w) >= 5 and w.endswith(GECISSIZ_EK):
        return 'intr', False
    if len(w) >= 5 and hece(w) >= 2 and w.endswith(GECISSIZ_EK_UZUN):
        return 'intr', False
    return 'tr', False


def yukle():
    d = json.load(open(DB_YOL, encoding='utf-8'))
    return {I.normala(x['kok']): x for x in d}


_DB = []


def db():
    if not _DB:
        _DB.append(yukle())
    return _DB[0]


def ayristir(metin):
    seg = metin.split(';')
    fiiller, adlar = [], []
    for n, s in enumerate(seg):
        s = s.strip()
        yalniz_fiil = False
        if ':' in s:
            on, arka = s.split(':', 1)
            if n > 0 and ' ' not in on.strip():
                yalniz_fiil = True
            s = arka
        s = re.sub(r'\([^)]*\)', '', s)
        for it in re.split(r',| / | veya ', s):
            it = re.sub(r'\([^)]*\)', '', it)
            if ':' in it:
                it = it.split(':', 1)[1]
            it = re.sub(r'[()?]', '', it).strip(" '\"?.")
            if len(it) < 2:
                continue
            son = it.split()[-1]
            if son.endswith(('mek', 'mak')) and len(son) > 4:
                fiiller.append(it[:-3])
            elif not yalniz_fiil:
                adlar.append(it)
    return fiiller, adlar


def wikt_gecis(kok):
    import wikt
    g = wikt.gecislilik(kok)
    if g and len(set(g)) == 1:
        return 'tr' if g[0] == 'tr' else 'intr'
    return None


def kok_bilgisi(kok):
    x = db().get(I.normala(kok))
    if x is None:
        return None
    fiiller, adlar = ayristir(x['turkce'])
    meçhul = 'varlik' in x or '(?)' in x['turkce']
    if x.get('fiil') and not fiiller:
        stem = x['fiil']
        kaynak = 'elle'
        guven = 'orta'
    elif fiiller:
        stem = fiiller[0].lower()
        kaynak = 'fiil'
        guven = 'kural' if len(set(fiiller)) == 1 and not meçhul else 'orta'
    elif kuran_fiil.stem(kok, x['turkce']):
        stem = kuran_fiil.stem(kok, x['turkce'])
        kaynak = 'kuran-fiil'
        guven = 'orta'
    elif adlar:
        ad = adlar[0].lower()
        kaynak = 'ad'
        if len(ad) > 5 and ad.endswith(('lık', 'lik', 'luk', 'lük')) and ' ' not in ad:
            stem = ad[:-3] + ' ol'
            guven = 'orta'
        else:
            stem = ad + ' ol'
            guven = 'kontrol'
        if meçhul:
            guven = 'kontrol'
    else:
        return {'stem': '', 'tr': '?', 'trk': False, 'kaynak': 'yok', 'guven': 'kontrol', 'ham': x['turkce'], 'adlar': []}
    tr, trk = gecislilik(stem)
    wg = wikt_gecis(kok)
    if wg:
        tr, trk = wg, True
    return {'stem': stem, 'tr': tr, 'trk': trk, 'kaynak': kaynak, 'guven': guven, 'ham': x['turkce'], 'adlar': adlar}


def f_pasfail(v):
    p = f_pas(v)
    return p + a_e(p) + 'n'


def bab_v(bab, grup, bil):
    v, tr, trk = bil['stem'], bil['tr'], bil['trk']
    gecisli = tr in ('tr', 'aux')
    if 'Rubâ' in grup:
        return v, gecisli, 'ardı ardına ', 'orta', 'aktif'
    if bab in ('', None):
        return v, gecisli, '', 'kural', 'aktif'
    if bab == 'II':
        return (v, True, 'çokça ', 'orta', 'aktif') if gecisli else (f_ettir(v), True, '', 'orta', 'aktif')
    if bab == 'IV':
        return f_ettir(v), True, '', 'orta', 'aktif'
    if bab == 'III':
        return v, gecisli, 'biriyle karşılıklı ', 'orta', 'aktif'
    if bab == 'VI':
        return v, False, ('birbirine ' if gecisli else 'hep birlikte '), 'orta', 'aktif'
    if bab == 'V':
        return v, False, 'kendini zorlayarak ', 'orta', 'aktif'
    if bab == 'VII':
        return (v, False, '', 'orta', 'edilgen') if gecisli else (v, False, 'kendiliğinden ', 'orta', 'aktif')
    if bab == 'VIII':
        return v, gecisli, 'kendisi için ', 'orta', 'aktif'
    if bab == 'X':
        return v, gecisli, '', 'orta', 'istek'
    if bab == 'IX':
        return v, False, 'iyiden iyiye ', 'kontrol', 'aktif'
    if bab == 'XI':
        return v, False, 'büsbütün ', 'kontrol', 'aktif'
    return v, gecisli, 'aşırı ', 'orta', 'aktif'


MASDAR_VEZNI = {}
MUBALAGA_VEZNI = {"fa''āl": 'işi {M} olan', "fa''āle": 'pek çok {F}', "fa''ūl": 'pek çok {F}', "fi''īl": '{M}de aşırı giden',
                  "fu''āl": 'son derece {F}', "mif'āl": '{M}yi âdet edinmiş', "mif'īl": '{M}ye düşkün'}
MEKAN_VEZNI = {"maf'ale": '{M}nin bol olduğu yer', "maf'ile": '{M}nin bol olduğu yer'}


def temel(grup, ad, v, gecisli, pre, kip):
    vez = ad.split(' + ')[0].strip()
    m = f_mastar(v)
    if kip == 'edilgen':
        M, F, PF = pre + f_mastar(f_pas(v)), pre + f_pasfail(v), pre + f_pasfail(v)
    elif kip == 'istek':
        M, F, PF = f_acc(m) + ' isteme', f_acc(m) + ' isteyen', m + 's' + i4(m) + ' istenen'
    else:
        M, F, PF = pre + m, pre + f_fail(v), pre + f_pasfail(v)
    sub = lambda t: t.format(M=M, F=F, PF=PF)
    ek = lambda s, ekler: s + ('y' if unluyle_biter(s) else '') + ekler
    g = grup
    if g.startswith('masdar-ı sınâî'):
        return F + 'l' + i4(F) + 'k', 'orta'
    if g.startswith('masdar · sülâsî'):
        t = MASDAR_VEZNI.get(vez)
        if t:
            t = t.replace('{M}den', ek(M, 'den' if a_e(M) == 'e' else 'dan')[len(M):].join([M, ''])) if False else t
            return sub(t.replace('{M}den', M + ('den' if a_e(M) == 'e' else 'dan'))), 'orta'
        return M, 'kural'
    if g.startswith('masdar') or g.startswith('ism-i masdar'):
        return M, 'kural'
    if g.startswith('ism-i merre'):
        return 'bir kere ' + M, 'kural'
    if g.startswith("ism-i hey'et"):
        return M + ' tarzı', 'orta'
    if g.startswith('ism-i fâil'):
        return F, 'kural'
    if g.startswith('ism-i mef'):
        return PF, ('kural' if gecisli else 'orta')
    if g.startswith('mekân/zaman') and not g.startswith('mekân/zaman/masdar'):
        t = MEKAN_VEZNI.get(vez)
        return (sub(t.replace('{M}nin', M + 'n' + i4(M) + 'n')) if t else M + ' yeri, vakti'), 'orta'
    if g.startswith('mekân/zaman/masdar'):
        return M + ' yeri, vakti', 'orta'
    if g.startswith('masdar-ı mîmî'):
        return M, 'orta'
    if g.startswith('âlet'):
        return M + ' âleti', 'orta'
    if g.startswith('tafdîl'):
        return 'daha çok ' + F, 'orta'
    if g.startswith('tasğîr'):
        return 'azıcık ' + M, 'orta'
    if g.startswith('sıfat-ı müşebbehe'):
        return 'her daim ' + F, 'orta'
    if g.startswith('mübalağa'):
        t = MUBALAGA_VEZNI.get(vez, 'çok {F}')
        t = t.replace('{M}de', M + ('de' if a_e(M) == 'e' else 'da')).replace('{M}yi', M + 'y' + i4(M)).replace('{M}ye', M + 'y' + a_e(M))
        return sub(t), 'orta'
    if g.startswith('mensûb'):
        return M + ' ile ilgili', 'orta'
    if g.startswith('ism-i cins'):
        return M + ' türünden şey', 'orta'
    if g.startswith('cem‘-i mükesser'):
        return cogul(M), 'orta'
    if g.startswith('cem‘u’l-cem‘'):
        return cogul(M) + ' topluluğu', 'orta'
    return M, 'orta'


def ek_uygula(ad, t, grup=''):
    tekil_kisi = not (grup.startswith('mekân') or grup.startswith('âlet') or grup.startswith('masdar') or grup.startswith('ism-i merre') or grup.startswith("ism-i hey'et"))
    if ' + müennes tesniye' in ad:
        return t + ', iki, müennes'
    if ' + müennes' in ad and 'cem' not in ad:
        return t + ', müennes'
    if ' + tesniye' in ad:
        return t + ', iki'
    if 'cem‘-i sâlim müennes' in ad:
        return (cogul(t) if tekil_kisi and ',' not in t else t + ', çoğul') + ', müennes'
    if 'cem‘-i sâlim müzekker' in ad:
        return cogul(t) if tekil_kisi and ',' not in t else t + ' (çoğul)'
    if ad.endswith(' + tâ (tekili)'):
        return t.replace(' türünden şey', ' türünden bir tane')
    if grup.startswith('ism-i cins · cem'):
        return t.replace(' türünden şey', ' türünden şeyler')
    return t


def isle(kok, satir):
    bil = kok_bilgisi(kok)
    sayac = {'kural': 0, 'orta': 0, 'kontrol': 0, 'veri yok': 0}
    for s in satir:
        if bil is None or not bil['stem']:
            s['tr'], s['guven'] = '', 'veri yok'
            sayac['veri yok'] += 1
            continue
        v, gecisli, pre, cap, kip = bab_v(s['bab'], s['grup'], bil)
        t, k = temel(s['grup'], s['ad'], v, gecisli, pre, kip)
        if s['grup'].startswith('masdar · sülâsî') and bil['kaynak'] == 'ad' and bil['adlar']:
            t, k = bil['adlar'][0], 'orta'
        t = ek_uygula(s['ad'], t, s['grup'])
        sira = {'kural': 0, 'orta': 1, 'kontrol': 2}
        son = max([bil['guven'], cap, k], key=lambda z: sira[z])
        if 'aday' in s['etiket'] and son == 'kural':
            son = 'orta'
        s['tr'], s['guven'] = t, son
        sayac[son] += 1
    return bil, sayac


def olc():
    d = db()
    n = len(d)
    fiil = ad_orta = ad_kontrol = yok = 0
    for k in d:
        b = kok_bilgisi(k)
        if b['kaynak'] in ('fiil', 'kuran-fiil'):
            fiil += 1
        elif b['kaynak'] == 'ad' and b['guven'] == 'orta':
            ad_orta += 1
        elif b['kaynak'] == 'ad':
            ad_kontrol += 1
        else:
            yok += 1
    return n, fiil, ad_orta, ad_kontrol, yok


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        k = I.normala(sys.argv[1])
        sinif, satir, red = I.tablo(k)
        bil, say = isle(k, satir)
        print(bil, say)
        for s in satir[:40]:
            print(s['grup'], '|', s['ad'], '|', s['ar'], '|', s['tr'], '|', s['guven'])
    else:
        print(olc())
