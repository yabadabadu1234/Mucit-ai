import collections
import gzip
import json
import os
import re
import sys

import istikak as I
import turkce as T
import mekayis as MK
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


import kaikki_suz as KS


HAM_KAIKKI = os.path.join(KOK, 'kaynak', 'lugat', 'ham', 'kaikki_arabic.jsonl.xz')


def kaikki_yukle(yol):
    yol = yol or HAM_KAIKKI
    assert os.path.exists(yol), 'ham Kaikki dökümü yok: %s' % yol
    import lzma
    liste = []
    for ln in (lzma.open(yol, 'rt', encoding='utf-8') if yol.endswith('.xz') else open(yol, encoding='utf-8')):
        d = json.loads(ln)
        e = KS.siki(d)
        k = KS.kok_bul(d)
        if k:
            e['k'] = k
        liste.append(e)
    return liste


def sade_ad(x):
    return I.normala(wikt.harekesiz(x).replace('\u0640', ''))


def kaikki_kok(e):
    k = e.get('k')
    return I.normala(k.replace(' ', '')) if k else None


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
    kuran_kokleri = {I.normala(k['kok']) for k in kel if k['kok']} | set(kokdb)
    mk = MK.yukle()
    cb = oku_json(os.path.join(KOK, 'kaynak', 'lugat', 'cebel_mihveri.json'))['kokler']
    kk = kaikki_yukle(sys.argv[1] if len(sys.argv) > 1 else '')
    kk_kokleri = {kaikki_kok(e) for e in kk if e.get('k')}
    kokler_ad = sorted(kuran_kokleri | set(mk) | kk_kokleri)
    kk_atama = [kaikki_kok(e) for e in kk]
    kk_yol = ['kök' if a else '' for a in kk_atama]
    lemma_kok = {}
    for e, a in zip(kk, kk_atama):
        if a:
            lemma_kok.setdefault(sade_ad(e['w']), a)
    for i, e in enumerate(kk):
        if not kk_atama[i] and e.get('fo'):
            for f in e['fo']:
                a = lemma_kok.get(sade_ad(f))
                if a:
                    kk_atama[i] = a
                    kk_yol[i] = 'asıl madde'
                    break
    mustak_kok = {}
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
            mustak_kok.setdefault(sade_ad(s['ar']), k)
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
        if k in osm_kok:
            soz['osmanlica_lugatler'] = {ll: {'sorgular': v['sorgular'], 'maddeler': v['maddeler']} for ll, v in osm_kok[k].items()}
        if k in mk:
            soz['mekayis'] = mk[k]
        if k in cb:
            soz['cebel_mihveri_ocr'] = cb[k]
        rm = wtr.get('rootMeanings', {}).get(k)
        if rm:
            soz['eyupipler_kok_anlami'] = rm
        kokler[k] = {'kok': k, 'sinif': sinif, 'turkce_fiil': ({'sap': bil['stem'], 'kaynak': bil['kaynak'], 'guven': bil['guven']} if bil else None),
                     'mustaklar': gruplar, 'reddedilen': [list(r) for r in red], 'sozlukler': soz,
                     'kuran_gecisleri': len(morf.get(k, [])), 'kuranda_var': k in kuran_kokleri}
    for i, e in enumerate(kk):
        if not kk_atama[i]:
            a = mustak_kok.get(sade_ad(e['w']))
            if a:
                kk_atama[i] = a
                kk_yol[i] = 'müştak'
    kelimeler = []
    for k in kel:
        y = yuzey.get(k['kelime'], {})
        l = lemtr.get(k['lem'], {})
        e = {'kelime': k['kelime'], 'kok': I.normala(k['kok']) if k['kok'] else '', 'lemma': k['lem'], 'tur': k['tur'], 'bab': k['bab'],
             'zaman': k['zaman'], 'ilk_gecis': k['ilk'], 'adet': k['adet'],
             'turkce': {'yuzey': y.get('tr', ''), 'lemma': l.get('tr', ''), 'lemma_durum': l.get('durum', ''),
                        'eyupipler': wtr.get('translations', {}).get(k['lem'], '')}}
        kelimeler.append(e)
    kk_kok = collections.defaultdict(list)
    kk_koksuz = []
    for i, e in enumerate(kk):
        e['yol'] = kk_yol[i]
        if kk_atama[i]:
            kk_kok[kk_atama[i]].append(e)
        else:
            kk_koksuz.append(e)
    for k, r in kokler.items():
        if k in kk_kok:
            r.setdefault('sozlukler', {})['kaikki_vikisozluk'] = kk_kok[k]
    sayi = {'kelime': len(kelimeler), 'kok': len(kokler), 'kalip': len(kaliplar),
            'mustak_satiri': sum(len(v) for r in kokler.values() for v in r.get('mustaklar', {}).values()),
            'etimolojili_kok': sum(1 for r in kokler.values() if 'etimoloji' in r.get('sozlukler', {})),
            'kaikkili_kok': sum(1 for r in kokler.values() if 'kaikki_vikisozluk' in r.get('sozlukler', {})),
            'osmanlica_lugatli_kok': sum(1 for r in kokler.values() if any(v['maddeler'] for v in r.get('sozlukler', {}).get('osmanlica_lugatler', {}).values())),
            'osmanlica_madde': sum(len(v['maddeler']) for r in kokler.values() for v in r.get('sozlukler', {}).get('osmanlica_lugatler', {}).values()),
            'mekayisli_kok': sum(1 for r in kokler.values() if 'mekayis' in r.get('sozlukler', {})),
            'kuranda_yok_kok': sum(1 for r in kokler.values() if not r.get('kuranda_var', True)),
            'cebel_mihverili_kok': sum(1 for r in kokler.values() if 'cebel_mihveri_ocr' in r.get('sozlukler', {})),
            'kok_anlamli_kok': sum(1 for r in kokler.values() if 'kok_anlamlari' in r.get('sozlukler', {})),
            'kaikki_girdi': len(kk), 'kaikki_koke_yerlesen': sum(len(v) for v in kk_kok.values()), 'kaikki_koksuz': len(kk_koksuz),
            'kaikki_yeni_kok': len(kk_kokleri - kuran_kokleri - set(mk)),
            'kaikki_kok_yolu': dict(collections.Counter(kk_yol)),
            'motorun_reddettigi_kok': sum(hata.values()), 'kokü_olmayan_kelime': sum(1 for e in kelimeler if not e['kok'])}
    assert sayi['kaikki_girdi'] == sayi['kaikki_koke_yerlesen'] + sayi['kaikki_koksuz'], 'kaikki maddesi yerleşmedi'
    return {'sema': SEMA, 'sayilar': sayi, 'kaliplar': kaliplar, 'kokler': kokler, 'kelimeler': kelimeler, 'kaikki_koksuz': kk_koksuz}


def yaz():
    d = uret()
    taban = os.path.join(KOK, 'kelime_kaydi')
    import shutil
    for eski in ('kokler', 'kelimeler', 'koksuz.json', 'FIHRIST.json', 'kuranda_var', 'kuranda_yok'):
        yol = os.path.join(taban, eski)
        if os.path.isdir(yol):
            shutil.rmtree(yol)
        elif os.path.exists(yol):
            os.remove(yol)
    gruplar = collections.defaultdict(list)
    koksuz = []
    for e in d['kelimeler']:
        (gruplar[e['kok']] if e['kok'] else koksuz).append(e)
    fih = {'kuranda_var': [], 'kuranda_yok': []}
    kelime_kok = {}
    toplam = collections.Counter()
    for k, r in d['kokler'].items():
        ad = 'kuranda_var' if r.get('kuranda_var') else 'kuranda_yok'
        klasor = os.path.join(taban, ad, 'kokler')
        os.makedirs(klasor, exist_ok=True)
        dugum = dict(r)
        dugum['sema'] = SEMA
        used = sorted({x[0] for v in r.get('mustaklar', {}).values() for x in v})
        dugum['kaliplar'] = {str(i): d['kaliplar'][i] for i in used}
        dugum['kelimeler'] = gruplar.get(k, [])
        yol = os.path.join(klasor, k + '.json')
        with open(yol, 'w', encoding='utf-8') as f:
            json.dump(dugum, f, ensure_ascii=False, separators=(',', ':'))
        toplam[ad] += os.path.getsize(yol)
        fih[ad].append([k + '.json', k, len(dugum['kelimeler']), sum(len(v) for v in r.get('mustaklar', {}).values())])
        for e in dugum['kelimeler']:
            kelime_kok[e['kelime']] = k
    with open(os.path.join(taban, 'kuranda_var', 'koksuz.json'), 'w', encoding='utf-8') as f:
        json.dump({'aciklama': 'Kökü olmayan kelimeler (harf, zamir, özel ad vb.)', 'kelimeler': koksuz}, f, ensure_ascii=False, separators=(',', ':'))
    kd = os.path.join(taban, 'kuranda_yok', 'kelimeler')
    os.makedirs(kd, exist_ok=True)
    kw = collections.defaultdict(list)
    for e in d['kaikki_koksuz']:
        ad_ = re.sub(r'[^\w]+', '_', e['u'], flags=re.U).strip('_')[:80] or 'adsiz'
        kw[ad_].append(e)
    for ad_, liste in kw.items():
        with open(os.path.join(kd, ad_ + '.json'), 'w', encoding='utf-8') as f:
            json.dump({'kelime': liste[0]['u'], 'maddeler': liste}, f, ensure_ascii=False, separators=(',', ':'))
    d['sayilar']['kaikki_koksuz_kelime_dosyasi'] = len(kw)
    for ad in ('kuranda_var', 'kuranda_yok'):
        with open(os.path.join(taban, ad, 'FIHRIST.json'), 'w', encoding='utf-8') as f:
            json.dump({'sema': SEMA, 'sayilar': d['sayilar'], 'alanlar_kokler': ['dosya', 'kok', 'kelime_sayisi', 'mustak_satiri'], 'kokler': fih[ad],
                       'kelime_kok': kelime_kok if ad == 'kuranda_var' else {}}, f, ensure_ascii=False, separators=(',', ':'))
    print(d['sayilar'], {k: len(v) for k, v in fih.items()}, {k: v // 1024 // 1024 for k, v in toplam.items()}, 'MB')


if __name__ == '__main__':
    yaz()
