from collections import defaultdict

from veri_usul import USULLER
from veri_onerme import ONERMELER
from veri_soru import SORULAR, HUCRELER, FELSEFELER, OLUMSUZ
from veri_ispat import ISPATLAR
from kural import yapilamaz, SINIF

RANK = {'yakîn': 3, 'zan-ı gâlib': 2, 'zan': 1, 'tenbih': 0}
ADI = {3: 'yakîn', 2: 'zan-ı gâlib', 1: 'zan', 0: 'tenbih'}
TAVAN = {'U09': 1, 'U14': 1, 'U15': 1, 'U17': 2, 'U11': 2, 'U32': 0}
KABUL_USUL = [u for u in USULLER if u['grup'] != 'aday']
USUL = {u['id']: u for u in USULLER}
HUCRE = {h['id']: h for h in HUCRELER}
SORU = {s['id']: s for s in SORULAR}


def ispatlari_hazirla():
    sayac = defaultdict(int)
    sonuc = []
    for p in ISPATLAR:
        anahtar = (p['hucre'], p['usul'])
        sayac[anahtar] += 1
        kimlik = p['hucre'] + '/' + p['usul'] + ('#' + str(sayac[anahtar]) if sayac[anahtar] > 1 else '')
        q = dict(p)
        q['id'] = kimlik
        q['tur'] = 'direct'
        sonuc.append(q)
    for s in SORULAR:
        hs = [h for h in HUCRELER if h['soru'] == s['id']]
        dog = [h for h in hs if h['hukum'] == 'DOĞRU']
        yan = [h for h in hs if h['hukum'] == 'YANLIŞ']
        ihl = [h for h in hs if h['hukum'] == 'İHTİLAFLI']
        for h in hs:
            if h['alt_soru']:
                alt = [x for x in HUCRELER if x['soru'] == h['alt_soru']]
                sonuc.append(dict(id=h['id'] + '/U08#alt', hucre=h['id'], usul='U08', tur='alt',
                                  prem=['k_hasir_cevap_uzayi'] + ['D:' + x['id'] for x in alt],
                                  ozet='Alt suâlin bütün hücreleri ayrı ayrı çürütüldüğünden bu hücre çürür.', tag=None, hudut='', sarti=None, kismi=''))
        if len(dog) == 1 and not ihl and not s['ust_hucre']:
            sonuc.append(dict(id=dog[0]['id'] + '/U08#sibr', hucre=dog[0]['id'], usul='U08', tur='sibr',
                              prem=['k_hasir_cevap_uzayi'] + ['D:' + y['id'] for y in yan],
                              ozet='Kalan bütün hücreler ayrı ayrı çürütüldüğünden aklî hasırla geriye bu hücre kalır.',
                              tag=None, hudut='', sarti=None, kismi='', istikrai=(s['hasir'] == 'istikrâî')))
        if len(dog) == 1 and any(p['hucre'] == dog[0]['id'] for p in ISPATLAR):
            for y in yan:
                sonuc.append(dict(id=y['id'] + '/U08#dislama', hucre=y['id'], usul='U08', tur='dislama',
                                  prem=['k_hucre_dislama', 'D:' + dog[0]['id']],
                                  ozet='Doğru hücre ispatlandığından aynı suâlin bu hücresi onunla bir arada doğru olamaz.', tag=None, hudut='', sarti=None, kismi=''))
                for p in [x for x in sonuc if x['hucre'] == dog[0]['id'] and x['tur'] == 'direct' and not x['kismi'] and x['usul'] != 'U32']:
                    sonuc.append(dict(id=y['id'] + '/' + p['usul'] + '#dis:' + p['id'], hucre=y['id'], usul=p['usul'], tur='dislama',
                                      prem=['k_hucre_dislama', 'P:' + p['id']],
                                      ozet='Doğru kardeş ' + dog[0]['id'] + ' bu usulle ispatlandı (' + p['id'] + '); hücreler birbirini dışladığından bu hücre çürür.',
                                      tag=None, hudut='', sarti=None, kismi=''))
    return sonuc


def hesapla(p, goruntu, atanan, onceki):
    kats = [TAVAN.get(p['usul'], 3)]
    if p.get('istikrai'):
        kats.append(1)
    W = set()
    fam = set()
    dayanak = []
    for pr in p['prem']:
        if pr[:2] == 'P:':
            if pr[2:] not in onceki:
                return None
            en = atanan[pr[2:]]
            kats.append(en['kat'])
            W |= en['W']
            fam |= en['fam']
            dayanak.append((en['hucre'], en['id']))
        elif pr[:2] in ('H:', 'D:'):
            hucre = pr[2:]
            adaylar = []
            for x in goruntu.get(hucre, []):
                a = atanan[x]
                if a['kismi'] or a['kat'] < 1:
                    continue
                if pr[0] == 'D' and a['tur'] not in ('direct', 'alt'):
                    continue
                if p['sarti'] and a['kat'] < RANK[p['sarti']]:
                    continue
                adaylar.append(a)
            if not adaylar:
                return None
            en = max(adaylar, key=lambda a: (a['kat'], -len(a['W'])))
            kats.append(en['kat'])
            W |= en['W']
            fam |= en['fam']
            dayanak.append((hucre, en['id']))
        else:
            o = ONERMELER[pr]
            kats.append(RANK[o['kat']])
            if o['zayif']:
                W.add(pr)
                fam.add(o['aile'] or pr)
    kat = min(kats)
    return dict(id=p['id'], hucre=p['hucre'], usul=p['usul'], tur=p['tur'], kat=kat, W=W, fam=fam, kismi=p['kismi'], dayanak=dayanak)


def durum_adi(kat, W):
    if kat == 3:
        return 'KAT’Î' if not W else 'KAT’Î-ŞARTLI'
    return {2: 'ZAN-I GÂLİB', 1: 'ZANNÎ', 0: 'TENBİH'}[kat]


def degerlendir(proofs, dusen=frozenset()):
    kalan = [p for p in proofs if not (set(p['prem']) & set(dusen))]
    atanan = {}
    hucre_atanan = defaultdict(list)
    tur = 0
    while True:
        tur += 1
        goruntu = {h: list(v) for h, v in hucre_atanan.items()}
        onceki = set(atanan)
        yeni = []
        for p in kalan:
            if p['id'] in atanan:
                continue
            r = hesapla(p, goruntu, atanan, onceki)
            if r:
                r['katman'] = tur
                yeni.append(r)
        if not yeni:
            break
        for r in yeni:
            atanan[r['id']] = r
            hucre_atanan[r['hucre']].append(r['id'])
    bagsiz = [p['id'] for p in kalan if p['id'] not in atanan]
    return atanan, hucre_atanan, bagsiz


def hucre_ozeti(atanan, hucre_atanan):
    sonuc = {}
    for h in HUCRELER:
        ids = hucre_atanan.get(h['id'], [])
        tam = [atanan[i] for i in ids if not atanan[i]['kismi'] and atanan[i]['kat'] >= 1]
        kismi = [atanan[i] for i in ids if atanan[i]['kismi']]
        if tam:
            en = max(tam, key=lambda a: (a['kat'], -len(a['W'])))
            sonuc[h['id']] = dict(durum=durum_adi(en['kat'], en['W']), kat=en['kat'], W=sorted(en['W']), fam=sorted(en['fam']),
                                  en_iyi=en['id'], ispat_say=len(ids), anahtar=(en['kat'], 0 if en['W'] else 1))
        elif kismi:
            en = max(kismi, key=lambda a: a['kat'])
            sonuc[h['id']] = dict(durum='KISMÎ', kat=en['kat'], W=sorted(en['W']), fam=sorted(en['fam']), en_iyi=en['id'], ispat_say=len(ids), anahtar=(0, 0))
        elif h['hukum'] == 'İHTİLAFLI':
            sonuc[h['id']] = dict(durum='İHTİLAFLI', kat=-1, W=[], fam=[], en_iyi='', ispat_say=0, anahtar=(-1, 0))
        else:
            sonuc[h['id']] = dict(durum='İSPATSIZ', kat=-1, W=[], fam=[], en_iyi='', ispat_say=0, anahtar=(-1, 0))
    return sonuc


def felsefe_durumlari(ozet):
    sonuc = {}
    for f in FELSEFELER:
        satirlar = []
        for c in f['hucreler']:
            h = HUCRE[c]
            satirlar.append(dict(hucre=c, hukum=h['hukum'], durum=ozet[c]['durum'], kat=ozet[c]['kat'], W=ozet[c]['W']))
        if all(s['hukum'] == 'DOĞRU' for s in satirlar):
            sonuc[f['id']] = dict(durum='UYUMLU', guc=-2, satirlar=satirlar, kalan=[])
            continue
        curuyen = [s for s in satirlar if s['hukum'] == 'YANLIŞ' and s['durum'] not in ('KISMÎ', 'İSPATSIZ')]
        kismi = [s for s in satirlar if s['hukum'] == 'YANLIŞ' and s['durum'] == 'KISMÎ']
        ihl = [s for s in satirlar if s['hukum'] == 'İHTİLAFLI']
        ispatsiz = [s for s in satirlar if s['hukum'] == 'YANLIŞ' and s['durum'] == 'İSPATSIZ']
        kalan = [s['hucre'] + ' (' + s['durum'] + ')' for s in satirlar if s['hukum'] != 'DOĞRU' and s not in curuyen]
        if curuyen:
            en = max(curuyen, key=lambda s: (s['kat'], -len(s['W'])))
            ad = {3: 'ÇÜRÜTÜLDÜ (kat’î)' if not en['W'] else 'ÇÜRÜTÜLDÜ (kat’î, şartlı)', 2: 'ZANNÎ ÇÜRÜTÜLDÜ (zan-ı gâlib)', 1: 'ZANNÎ ÇÜRÜTÜLDÜ (zan)'}.get(en['kat'], 'TENBİH')
            sonuc[f['id']] = dict(durum=ad, guc=en['kat'] * 2 + (0 if en['W'] else 1), satirlar=satirlar, kalan=kalan)
        elif kismi:
            sonuc[f['id']] = dict(durum='KISMEN ÇÜRÜTÜLDÜ (kısmî delil)', guc=0, satirlar=satirlar, kalan=kalan)
        elif ihl and not ispatsiz:
            sonuc[f['id']] = dict(durum='İHTİLAFLI (iddia edilmez)', guc=-1, satirlar=satirlar, kalan=kalan)
        else:
            sonuc[f['id']] = dict(durum='ÇÜRÜMEDİ', guc=-1, satirlar=satirlar, kalan=kalan)
    return sonuc


def kombinasyonlar(h, ids, atanan):
    gruplar = defaultdict(list)
    for i in ids:
        gruplar[atanan[i]['usul']].append(i)
    usuller = sorted(gruplar)
    n = len(usuller)
    sonuc = []
    skorlar = {}
    for mask in range(1, 1 << n):
        uyeler = [usuller[b] for b in range(n) if mask >> b & 1]
        pl = [atanan[i] for u in uyeler for i in gruplar[u]]
        guclu = [a for a in pl if a['kat'] >= 1 and not a['kismi']]
        kismi = [a for a in pl if a['kismi']]
        tenbih = [a for a in pl if a['kat'] == 0 and not a['kismi']]
        if guclu:
            en = max(a['kat'] for a in guclu)
            en_liste = [a for a in guclu if a['kat'] == en]
            kesin = any(a['kat'] == 3 and not a['W'] for a in en_liste)
            ortak = set.intersection(*[set(a['fam']) for a in en_liste])
            bagimsiz = len(en_liste) >= 2 and not ortak and not kesin
            zayiflar = sorted(set().union(*[a['W'] for a in en_liste]))
            durum = 'KAT’Î' if kesin else ('KAT’Î-ŞARTLI' if en == 3 else durum_adi(en, {'x'}))
            if kesin:
                bag = 'zayıf halka yok'
            elif bagimsiz:
                bag = 'hiçbir tek zayıf aile hepsini düşürmez'
            elif ortak:
                bag = 'ortak zayıf halka: ' + ', '.join(sorted(ortak))
            else:
                bag = 'tek delil'
        else:
            en = 0
            kesin = False
            ortak = set()
            bagimsiz = False
            zayiflar = []
            durum = 'KISMÎ' if kismi else ('TENBİH' if tenbih else 'YOK')
            bag = 'yalnız kısmî kapsam' if kismi else ('delil değil, tenbih' if tenbih else '-')
        skor = (en if guclu else -1, 1 if kesin else 0, 1 if bagimsiz else 0)
        skorlar[mask] = skor
        sonuc.append(dict(hucre=h, mask=mask, usuller=uyeler, boyut=len(uyeler), ispat_say=len(pl), kismi_say=len(kismi),
                          kat=ADI[en] if guclu else ('kısmî' if kismi else ('tenbih' if tenbih else '-')), durum=durum, bagimlilik=bag, zayiflar=zayiflar, skor=skor))
    if sonuc:
        en_skor = max(skorlar.values())
        yeter = {m for m, s in skorlar.items() if s == en_skor}
        for r in sonuc:
            m = r['mask']
            r['yeterli'] = m in yeter
            alt = (m - 1) & m
            asgari = m in yeter
            while alt and asgari:
                if alt in yeter:
                    asgari = False
                alt = (alt - 1) & m
            r['asgari'] = asgari
            r['azami'] = m == (1 << n) - 1
            r['en_skor'] = en_skor == r['skor']
    for r in sonuc:
        r['skor'] = list(r['skor'])
    return sonuc


def matris(h, ozet, atanan, hucre_atanan, proofs_by_id, felsefe_say):
    hh = HUCRE[h]
    ids = hucre_atanan.get(h, [])
    sonuc = []
    q = SORU[hh['soru']]
    hs = [x for x in HUCRELER if x['soru'] == hh['soru']]
    ihtilafli_var = any(x['hukum'] == 'İHTİLAFLI' for x in hs)
    dogru_var = any(x['hukum'] == 'DOĞRU' for x in hs)
    for u in KABUL_USUL:
        uid = u['id']
        kullanan = [i for i in ids if atanan[i]['usul'] == uid]
        kayitli = [p['id'] for p in proofs_by_id.values() if p['hucre'] == h and p['usul'] == uid]
        etiketli = [i for i in ids if proofs_by_id[i]['tag'] and uid in tagli(proofs_by_id[i]['tag'])]
        durum = ''
        sebep = ''
        if uid in SINIF:
            if etiketli:
                durum, sebep = 'KULLANILDI', 'ispat sınıfı: ' + ', '.join(etiketli)
            else:
                s = yapilamaz(uid, hh['tur'], hh['soru'], hh['hukum'], felsefe_say, False)
                if s:
                    durum, sebep = 'YAPILAMAZ', s
                else:
                    durum, sebep = 'SINIFLANMADI', 'Bu hücrenin ispatlarından hiçbiri bu sınıfa etiketlenmedi.'
        elif uid == 'U16':
            if len(ids) >= 2:
                durum, sebep = 'KOMBİNE', str(len(ids)) + ' ispat; ayrıntı kombinasyon tablosundadır.'
            else:
                durum, sebep = 'YAPILAMAZ', 'Birleştirilecek ikinci ispat yok (ispat sayısı ' + str(len(ids)) + ').'
        elif uid == 'U30':
            en = ozet[h]
            if en['W'] or any(atanan[i]['kismi'] for i in ids):
                durum, sebep = 'HUDUT', 'Zayıf halkalar: ' + (', '.join(en['W']) if en['W'] else '-') + '; kısmî kapsam: ' + str(sum(1 for i in ids if atanan[i]['kismi']))
            else:
                durum, sebep = 'YAPILAMAZ', 'Hudut gerektiren zayıf halka veya kısmî kapsam yok.'
        elif kullanan:
            durum = 'KULLANILDI'
            sebep = ', '.join(kullanan)
        elif uid == 'U12' and any(ONERMELER[p]['tur'] == 'musahede' for i in ids for p in proofs_by_id[i]['prem'] if p in ONERMELER):
            durum, sebep = 'ÖNCÜL', 'Müşâhede öncülleri: ' + ', '.join(sorted({p for i in ids for p in proofs_by_id[i]['prem'] if p in ONERMELER and ONERMELER[p]['tur'] == 'musahede'}))
        elif uid == 'U13' and any(p in ('m_nizam', 'm_ihkam') for i in ids for p in proofs_by_id[i]['prem']):
            durum, sebep = 'ÖNCÜL', 'Kanun düzeni öncülü (tecrübe temelli) kullanıldı.'
        elif uid == 'U08':
            if hh['hukum'] == 'İHTİLAFLI' or (hh['hukum'] == 'DOĞRU' and ihtilafli_var):
                durum, sebep = 'YAPILAMAZ', 'İHTİLAFLI hücre aklî hasırı kapatmaz; kitap o hücreyi iddia etmez.'
            elif not dogru_var and not hh['alt_soru']:
                durum, sebep = 'YAPILAMAZ', 'Bu suâlde doğru hücre yok (alt suâl); hasır dışlaması kurulamaz.'
            else:
                durum, sebep = 'AÇIK', 'Kardeş hücrelerden en az biri henüz ispatsız veya bağsız; hasır kapanmadı.'
        elif kayitli:
            durum, sebep = 'KURULAMADI', 'Kayıtlı ispat bağlanamadı: ' + ', '.join(kayitli)
        else:
            s = yapilamaz(uid, hh['tur'], hh['soru'], hh['hukum'], felsefe_say, False)
            if s:
                durum, sebep = 'YAPILAMAZ', s
            else:
                durum, sebep = 'YAPILMADI', 'Usulün şartı bu hücrede mümkündür; ispat kaydı henüz yazılmadı (açık iş).'
        sonuc.append(dict(hucre=h, usul=uid, durum=durum, sebep=sebep))
    return sonuc


def tagli(tag):
    f, o = tag
    sonuc = []
    sonuc.append({'enne': 'U19', 'lime': 'U20', 'mutlak': 'U21'}[f])
    sonuc.append({'madde': 'U22', 'suret': 'U23', 'fail': 'U24', 'gaye': 'U25'}[o])
    return sonuc
