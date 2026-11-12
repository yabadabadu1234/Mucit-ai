import collections
import gzip
import json
import os
import re
import sys

import istikak as I
import turkce as T
import wikt

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SOZ = os.path.join(KOK, 'kaynak', 'sozluk')
ETI = os.path.join(KOK, 'kaynak', 'lugat', 'etimoloji')
HAR = os.path.join(KOK, 'veri_harici')
CIKTI = os.path.join(KOK, 'kelime_kaydi', 'KELIME_KAYDI.json.gz')

SEMA = {
    'sema': 'graf-ic-graf',
    'kok_dugum': 'kelimeler[i].kok → kokler[kok]',
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
            'kok_anlamli_kok': sum(1 for r in kokler.values() if 'kok_anlamlari' in r.get('sozlukler', {})),
            'motorun_reddettigi_kok': sum(hata.values()), 'kokü_olmayan_kelime': sum(1 for e in kelimeler if not e['kok'])}
    return {'sema': SEMA, 'sayilar': sayi, 'kaliplar': kaliplar, 'kokler': kokler, 'kelimeler': kelimeler}


def dosya_adi(n, kelime):
    h = re.sub(r'[^\u0621-\u064a]', '', kelime)
    return '%05d_%s.json' % (n, h or 'x')


def yaz():
    d = uret()
    klasor = os.path.join(KOK, 'kelime_kaydi', 'kelimeler')
    os.makedirs(klasor, exist_ok=True)
    for f in os.listdir(klasor):
        os.remove(os.path.join(klasor, f))
    grup_kok = collections.defaultdict(list)
    adlar = []
    for n, e in enumerate(d['kelimeler'], 1):
        adlar.append(dosya_adi(n, e['kelime']))
        if e['kok']:
            grup_kok[e['kok']].append(adlar[-1])
    fihrist = []
    toplam = 0
    for e, ad in zip(d['kelimeler'], adlar):
        kok = d['kokler'].get(e['kok']) if e['kok'] else None
        lem = e['lemma']
        kayit = dict(e)
        kayit['dosya'] = ad
        kayit['sema'] = SEMA
        kayit['kaliplar_ayrintisi'] = d['kaliplar'] if False else None
        if kok:
            kok = dict(kok)
            kok['kalip_tablosu'] = sorted({r[0] for v in kok['mustaklar'].values() for r in v})
            kok['kaliplar'] = {i: d['kaliplar'][i] for i in kok['kalip_tablosu']}
            wl = kok.get('sozlukler', {}).get('vikisozluk_ingilizce', [])
            kok['bu_lemmaya_ozel_vikisozluk'] = [x for x in wl if I.normala(x['lemma']) == I.normala(lem)]
            kok['kardes_kelimeler'] = [x for x in grup_kok[e['kok']] if x != ad]
        kayit['kok_grafi'] = kok
        del kayit['kaliplar_ayrintisi']
        yol = os.path.join(klasor, ad)
        with open(yol, 'w', encoding='utf-8') as f:
            json.dump(kayit, f, ensure_ascii=False, separators=(',', ':'))
        toplam += os.path.getsize(yol)
        fihrist.append([ad, e['kelime'], e['kok'], e['lemma'], e['tur']])
    with open(os.path.join(KOK, 'kelime_kaydi', 'FIHRIST.json'), 'w', encoding='utf-8') as f:
        json.dump({'sema': SEMA, 'sayilar': d['sayilar'], 'alanlar': ['dosya', 'kelime', 'kok', 'lemma', 'tur'], 'kelimeler': fihrist}, f, ensure_ascii=False, separators=(',', ':'))
    print(d['sayilar'], len(adlar), 'dosya', toplam // 1024 // 1024, 'MB')


if __name__ == '__main__':
    yaz()
