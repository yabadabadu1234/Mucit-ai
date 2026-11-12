import collections
import gzip
import json
import os
import re
import sys

import istikak as I
import turkce as T
import osmanlica_lugat as OS
import wikt

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SOZ = os.path.join(KOK, 'kaynak', 'sozluk')
ETI = os.path.join(KOK, 'kaynak', 'lugat', 'etimoloji')
HAR = os.path.join(KOK, 'veri_harici')
CIKTI = os.path.join(KOK, 'kelime_kaydi', 'KELIME_KAYDI.json.gz')

SEMA = {
    'sema': 'graf-ic-graf',
    'kok_dosyasi': 'kokler/<kök>.json: kök grafı bir kez; kelimeler = bu kökten bütün kelimeler',
    'kok_alt_grafi': 'kokler[kok].mustaklar = gruplar; her grup bir alt graf; satır = [kalıp numarası, Arapça, Latin, Türkçe, güven, tanık]; kalıp numarası kaliplar listesine işaret eder',
    'sozluk_dali': 'kokler[kok].sozlukler = kaynak adı → o kaynaktaki maddeler',
    'kelime_dali': 'kelimeler[i].morfoloji = Kur\'ân içindeki ilk geçiş ve kelime çevirileri',
    'satir_alanlari': ['kalip', 'arapca', 'latin', 'turkce', 'guven', 'tanik'],
}


def oku_json(p):
    return json.load(open(p, encoding='utf-8'))


def etimoloji():
    d = {}
    for f in os.listdir(ETI):
        if f.endswith('.md'):
            d[I.normala(f[:-3])] = open(os.path.join(ETI, f), encoding='utf-8').read()
    return d


def morfoloji():
    m = collections.defaultdict(list)
    for ln in open(os.path.join(HAR, 'eyupipler', 'quran-morphology.txt'), encoding='utf-8'):
        p = ln.rstrip('\n').split('\t')
        if len(p) < 4 or ':' not in p[0]:
            continue
        r = re.search(r'ROOT:([^|]+)', p[3])
        if r:
            m[I.normala(r.group(1))].append(p[0])
    return m


def uret():
    kel = oku_json(os.path.join(SOZ, 'kelimeler.json'))
    yuzey = oku_json(os.path.join(SOZ, 'yuzey_karsilik_bagi.json'))
    lemtr = {x['lem']: x for x in oku_json(os.path.join(SOZ, 'lemma_karsilik_uretim.json'))}
    kokdb = T.db()
    eti = etimoloji()
    wk = wikt.yukle()
    wtr = oku_json(os.path.join(HAR, 'eyupipler', 'word-translations-tr.json'))
    trw = oku_json(os.path.join(KOK, 'kitap_destek', 'turetme_motoru', 'veri', 'tr_vikisozluk.json'))
    morf = morfoloji()
    osm = OS.yukle_onbellek()
    osm_kok = collections.defaultdict(dict)
    for anahtar, v in osm.items():
        kk, ll = anahtar.split('|', 1)
        osm_kok[kk][ll] = v
    kokler_ad = sorted({I.normala(k['kok']) for k in kel if k['kok']} | set(kokdb))
    kaliplar, kidx = [], {}
    kokler = {}
    hata = collections.Counter()
    for k in kokler_ad:
        try:
            sinif, satir, red = I.tablo(k)
            bil, say = T.isle(k, satir)
            wikt.isle(k, satir)
        except Exception as e:
            hata[type(e).__name__] += 1
            kokler[k] = {'kok': k, 'durum': 'motor reddetti: %s' % type(e).__name__}
            continue
        gruplar = collections.OrderedDict()
        for s in satir:
            key = (s['grup'], s['ad'], s['etiket'], s['bab'])
            if key not in kidx:
                kidx[key] = len(kaliplar)
                kaliplar.append(list(key))
            gruplar.setdefault(s['grup'], []).append([kidx[key], s['ar'], s['lat'], s.get('tr', ''), s.get('guven', ''), s.get('tanik', '')])
        wl = wk.get(k, [])
        soz = {}
        x = kokdb.get(k)
        if x:
            soz['kok_anlamlari'] = x
        if k in eti:
            soz['etimoloji'] = eti[k]
        if wl:
            soz['vikisozluk_ingilizce'] = [{'lemma': e['l'], 'tur': e['p'], 'bab': e['f'], 'tanim': e['g']} for e in wl]
        if k in osm_kok:
            soz['osmanlica_lugatler'] = {ll: {'sorgular': v['sorgular'], 'maddeler': v['maddeler']} for ll, v in osm_kok[k].items()}
        rm = wtr.get('rootMeanings', {}).get(k)
        if rm:
            soz['eyupipler_kok_anlami'] = rm
        kokler[k] = {'kok': k, 'sinif': sinif, 'turkce_fiil': ({'sap': bil['stem'], 'kaynak': bil['kaynak'], 'guven': bil['guven']} if bil else None),
                     'mustaklar': gruplar, 'reddedilen': [list(r) for r in red], 'sozlukler': soz,
                     'kuran_gecisleri': len(morf.get(k, []))}
    kelimeler = []
    for k in kel:
        y = yuzey.get(k['kelime'], {})
        l = lemtr.get(k['lem'], {})
        e = {'kelime': k['kelime'], 'kok': I.normala(k['kok']) if k['kok'] else '', 'lemma': k['lem'], 'tur': k['tur'], 'bab': k['bab'],
             'zaman': k['zaman'], 'ilk_gecis': k['ilk'], 'adet': k['adet'],
             'turkce': {'yuzey': y.get('tr', ''), 'lemma': l.get('tr', ''), 'lemma_durum': l.get('durum', ''),
                        'eyupipler': wtr.get('translations', {}).get(k['lem'], '')}}
        kelimeler.append(e)
    sayi = {'kelime': len(kelimeler), 'kok': len(kokler), 'kalip': len(kaliplar),
            'mustak_satiri': sum(len(v) for r in kokler.values() for v in r.get('mustaklar', {}).values()),
            'etimolojili_kok': sum(1 for r in kokler.values() if 'etimoloji' in r.get('sozlukler', {})),
            'vikisozluklu_kok': sum(1 for r in kokler.values() if 'vikisozluk_ingilizce' in r.get('sozlukler', {})),
            'osmanlica_lugatli_kok': sum(1 for r in kokler.values() if any(v['maddeler'] for v in r.get('sozlukler', {}).get('osmanlica_lugatler', {}).values())),
            'osmanlica_madde': sum(len(v['maddeler']) for r in kokler.values() for v in r.get('sozlukler', {}).get('osmanlica_lugatler', {}).values()),
            'kok_anlamli_kok': sum(1 for r in kokler.values() if 'kok_anlamlari' in r.get('sozlukler', {})),
            'motorun_reddettigi_kok': sum(hata.values()), 'kokü_olmayan_kelime': sum(1 for e in kelimeler if not e['kok'])}
    return {'sema': SEMA, 'sayilar': sayi, 'kaliplar': kaliplar, 'kokler': kokler, 'kelimeler': kelimeler}


def yaz():
    d = uret()
    taban = os.path.join(KOK, 'kelime_kaydi')
    klasor = os.path.join(taban, 'kokler')
    eski = os.path.join(taban, 'kelimeler')
    for kl in (klasor, eski):
        if os.path.isdir(kl):
            for f in os.listdir(kl):
                os.remove(os.path.join(kl, f))
    if os.path.isdir(eski):
        os.rmdir(eski)
    os.makedirs(klasor, exist_ok=True)
    gruplar = collections.defaultdict(list)
    koksuz = []
    for e in d['kelimeler']:
        (gruplar[e['kok']] if e['kok'] else koksuz).append(e)
    fihrist = {'kokler': [], 'kelime_kok': {}}
    toplam = 0
    for k, r in d['kokler'].items():
        dugum = dict(r)
        dugum['sema'] = SEMA
        used = sorted({x[0] for v in r.get('mustaklar', {}).values() for x in v})
        dugum['kaliplar'] = {str(i): d['kaliplar'][i] for i in used}
        dugum['kelimeler'] = gruplar.get(k, [])
        yol = os.path.join(klasor, k + '.json')
        with open(yol, 'w', encoding='utf-8') as f:
            json.dump(dugum, f, ensure_ascii=False, separators=(',', ':'))
        toplam += os.path.getsize(yol)
        fihrist['kokler'].append([k + '.json', k, len(dugum['kelimeler']), sum(len(v) for v in r.get('mustaklar', {}).values())])
        for e in dugum['kelimeler']:
            fihrist['kelime_kok'][e['kelime']] = k
    with open(os.path.join(taban, 'koksuz.json'), 'w', encoding='utf-8') as f:
        json.dump({'aciklama': 'Kökü olmayan kelimeler (harf, zamir, özel ad vb.)', 'kelimeler': koksuz}, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(taban, 'FIHRIST.json'), 'w', encoding='utf-8') as f:
        json.dump({'sema': SEMA, 'sayilar': d['sayilar'], 'alanlar_kokler': ['dosya', 'kok', 'kelime_sayisi', 'mustak_satiri'], **fihrist}, f, ensure_ascii=False, separators=(',', ':'))
    print(d['sayilar'], len(fihrist['kokler']), 'kök dosyası', toplam // 1024 // 1024, 'MB')


if __name__ == '__main__':
    yaz()
