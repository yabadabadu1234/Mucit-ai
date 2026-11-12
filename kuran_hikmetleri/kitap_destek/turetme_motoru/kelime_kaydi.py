import collections
import gzip
import json
import os
import re
import sys

import istikak as I
import mana_tasnif as MT
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


def okunur(o, g=0, en=110):
    ic = '  ' * (g + 1)
    dis = '  ' * g
    if isinstance(o, dict):
        if not o:
            return '{}'
        return '{\n' + ',\n'.join('%s%s: %s' % (ic, json.dumps(k, ensure_ascii=False), okunur(v, g + 1, en)) for k, v in o.items()) + '\n' + dis + '}'
    if isinstance(o, (list, tuple)):
        if not o:
            return '[]'
        if all(not isinstance(x, (dict, list, tuple)) for x in o):
            satir = '[' + ', '.join(json.dumps(x, ensure_ascii=False) for x in o) + ']'
            if len(satir) <= en:
                return satir
        return '[\n' + ',\n'.join(ic + okunur(x, g + 1, en) for x in o) + '\n' + dis + ']'
    return json.dumps(o, ensure_ascii=False)



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
        for ek in ('kok_durumu', 'asil'):
            if k.get(ek):
                e[ek] = k[ek]
        kelimeler.append(e)
    kk_kok = collections.defaultdict(list)
    kk_koksuz = []
    kelime_dosyalari = {}

    def kd_ad(u):
        return re.sub(r'[^\w]+', '_', u, flags=re.U).strip('_')[:80] or 'adsiz'

    def kd_ekle(u, kaynak, kayit):
        d_ = kelime_dosyalari.setdefault(kd_ad(u), {'kelime': u, 'sozlukler': collections.OrderedDict()})
        d_['sozlukler'].setdefault(kaynak, []).append(kayit)
    for i, e in enumerate(kk):
        e['yol'] = kk_yol[i]
        if kk_atama[i]:
            kk_kok[kk_atama[i]].append(e)
        else:
            kk_koksuz.append(e)
            kd_ekle(e['u'], 'kaikki_vikisozluk', e)
    for k, r in kokler.items():
        if k in kk_kok:
            r.setdefault('sozlukler', {})['kaikki_vikisozluk'] = kk_kok[k]
    kel_kok = {sade_ad(x['kelime']): I.normala(x['kok']) for x in kel if x['kok']}
    kel_kok.update({sade_ad(x['lem']): I.normala(x['kok']) for x in kel if x['kok'] and x.get('lem')})

    def kok_bul_kelime(ar):
        a = sade_ad(ar)
        if a in kel_kok:
            return kel_kok[a]
        if a in mustak_kok:
            return mustak_kok[a]
        if a.startswith('ال') and a[2:] in mustak_kok:
            return mustak_kok[a[2:]]
        return None

    renk = oku_json(os.path.join(SOZ, 'renk_sozluk.json'))
    renk_yer = collections.Counter()
    for ar, tr in renk.items():
        k = kok_bul_kelime(ar)
        if k and k in kokler:
            kokler[k].setdefault('sozlukler', {}).setdefault('renk_sozluk', {})[ar] = tr
            renk_yer['kök'] += 1
        else:
            kd_ekle(sade_ad(ar), 'renk_sozluk', {'kelime': ar, 'turkce': tr})
            renk_yer['kelime'] += 1

    import csv
    ont_yol = os.path.join(KOK, 'kaynak', 'Concepts.csv')
    ont_iliski = os.path.join(KOK, 'kaynak', 'Relations.csv')
    ont = {}
    for ln in csv.DictReader(open(ont_yol, encoding='utf-8')):
        ont[ln['conceptId']] = ln
    ust = collections.defaultdict(list)
    for ln in csv.DictReader(open(ont_iliski, encoding='utf-8')):
        for alan, ad in (('subTypeOfID', 'alt_tur_of'), ('partOfID', 'parca_of'), ('instanceOfID', 'ornek_of')):
            v = ln[alan]
            if v and v != 'NULL':
                ust[ln['concept_id']].append([ad, v])
    ont_yer = collections.Counter()
    ont_kunye = 'Arabic Ontology, Birzeit University (SinaLab, Mustafa Jarrar), ücretsiz sürüm, çıkarım 09-06-2024; atıf: Jarrar 2021 Applied Ontology 16:1; Jarrar ve Amayreh 2019 NLDB'
    for cid, c in ont.items():
        kayit = {'id': cid, 'arapca': [x.strip() for x in c['arabicSynset'].split('|') if x.strip()],
                 'ingilizce': [x.strip() for x in c['englishSynset'].split('|') if x.strip() and x.strip() != 'NULL'],
                 'tanim': c['gloss'], 'misal': (c['example'] if c['example'] != 'NULL' else ''), 'veri_kaynagi': c['dataSourceId'],
                 'ust': [[ad, v, (ont[v]['englishSynset'] if v in ont and ont[v]['englishSynset'] != 'NULL' else (ont[v]['arabicSynset'] if v in ont else ''))] for ad, v in ust.get(cid, [])],
                 'kunye': ont_kunye}
        yerler = set()
        for ar in kayit['arapca']:
            k = kok_bul_kelime(ar)
            if k and k in kokler:
                yerler.add(('k', k))
            else:
                yerler.add(('w', sade_ad(ar)))
        if not yerler:
            yerler.add(('w', 'concept_' + cid))
        for t, y in yerler:
            if t == 'k':
                kokler[y].setdefault('sozlukler', {}).setdefault('arabic_ontology', []).append(kayit)
                ont_yer['kök'] += 1
            else:
                kd_ekle(y, 'arabic_ontology', kayit)
                ont_yer['kelime'] += 1

    pilot = os.path.join(KOK, 'kaynak', 'lugat', 'pilot')
    pilot_say = 0
    for alt, ad in (('kategori', 'kategori.json'), ('lean', 'صبر.json'), ('sema', 'صبر.json')):
        yol = os.path.join(pilot, alt, ad)
        if os.path.exists(yol) and 'صبر' in kokler:
            kokler['صبر'].setdefault('sozlukler', {}).setdefault('pilot', {})[alt] = oku_json(yol)
            pilot_say += 1
    yol = os.path.join(pilot, 'صبر.json')
    if os.path.exists(yol) and 'صبر' in kokler:
        kokler['صبر'].setdefault('sozlukler', {}).setdefault('pilot', {})['cebir'] = oku_json(yol)
        pilot_say += 1
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
            'renk_sozluk_girdi': len(renk), 'renk_sozluk_yer': dict(renk_yer), 'ontoloji_kavram': len(ont), 'ontoloji_yer': dict(ont_yer), 'pilot_dosya': pilot_say,
            'motorun_reddettigi_kok': sum(hata.values()), 'kokü_olmayan_kelime': sum(1 for e in kelimeler if not e['kok'])}
    assert sayi['renk_sozluk_girdi'] == sum(renk_yer.values()), 'renk sözlüğü maddesi yerleşmedi'
    assert sayi['kaikki_girdi'] == sayi['kaikki_koke_yerlesen'] + sayi['kaikki_koksuz'], 'kaikki maddesi yerleşmedi'
    return {'sema': SEMA, 'sayilar': sayi, 'kaliplar': kaliplar, 'kokler': kokler, 'kelimeler': kelimeler, 'kaikki_koksuz': kk_koksuz, 'kelime_dosyalari': kelime_dosyalari}


MAHREC = {'halkiyye': 'ءهعحغخ', 'lehaviyye': 'قك', 'şeceriyye': 'جشض', 'esaliyye': 'صسز', 'nit‘iyye': 'طدت', 'lessiyye': 'ظذث', 'zelakiyye': 'رلن', 'şefeviyye': 'فبم', 'cevfiyye': 'ويا'}
BOLGE = {'halk': ('halkiyye',), 'dil': ('lehaviyye', 'şeceriyye', 'esaliyye', 'nit‘iyye', 'lessiyye', 'zelakiyye'), 'dudak ve cevf': ('şefeviyye', 'cevfiyye')}


def mana_agaci(mt):
    ag = {}
    ihlal = 0
    gor = {}
    for k, x in mt.items():
        u, o, i = x['ust'], x['orta'], x['ince']
        un = ag.setdefault(u['kume'], {'merkez_kok': u['merkez_kok'], 'merkez_mana': u['merkez_mana'], 'kok': 0, 'orta': {}})
        un['kok'] += 1
        on = un['orta'].setdefault(o['kume'], {'merkez_kok': o['merkez_kok'], 'merkez_mana': o['merkez_mana'], 'kok': 0, 'ince': {}})
        on['kok'] += 1
        inn = on['ince'].setdefault(i['kume'], {'merkez_kok': i['merkez_kok'], 'merkez_mana': i['merkez_mana'], 'kok': 0})
        inn['kok'] += 1
        ust_ata = gor.setdefault(('o', o['kume']), u['kume'])
        ihlal += ust_ata != u['kume']
        ihlal += gor.setdefault(('i', i['kume']), o['kume']) != o['kume']
    return {'yontem': 'çok dilli gömme (' + MT.MODEL + ') + Ward kümeleme; kök başına Türkçe/İngilizce/Arapça mana metinleri (kök anlamı, Vikisözlük, Arabic Ontology, Cebel, Mekâyîs) ayrı gömülüp ortalanır',
            'kesimler': list(MT.KESIMLER), 'ic_ice_olmayan_kok_sayisi': ihlal, 'kok': len(mt), 'agac': ag}


def tasnif_ozeti(agac):
    def say(x):
        return sum(say(v) for v in x.values()) if isinstance(x, dict) else len(x)
    d = {}
    for b, ms in sorted(agac.items()):
        d[b] = {'kok': say(ms), 'mahrec_sayisi': len(ms), 'mahrec': {}}
        for m, hs in sorted(ms.items()):
            d[b]['mahrec'][m] = {'kok': say(hs), 'harf_sayisi': len(hs), 'harf': {h: {'kok': say(fs), 'fasil_sayisi': len(fs), 'fasil': {f: len(v) for f, v in sorted(fs.items())}} for h, fs in sorted(hs.items())}}
    return {'seviyeler': 'bölge → mahreç → harf → fasıl (ilk iki illetsiz harf) → kök → kelime', 'kok': say(agac), 'bolge': len(agac),
            'mahrec': sum(len(v) for v in agac.values()), 'harf': sum(len(h) for v in agac.values() for h in v.values()),
            'fasil': sum(len(f) for v in agac.values() for h in v.values() for f in h.values()), 'agac': d}


def tasnif(kok):
    k = I.normala(kok)
    ilk = k[0]
    mahrec = next((m for m, h in MAHREC.items() if ilk in h), 'diğer')
    bolge = next((b for b, ms in BOLGE.items() if mahrec in ms), 'diğer')
    sade = ''.join(c for c in k if c not in 'ويا' + 'ء') or k
    fasil = (sade + sade[-1:])[:2]
    return {'fasil': fasil, 'harf': ilk, 'mahrec': mahrec, 'bolge': bolge}


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
    mt = MT.sinifla(d['kokler'])
    agac = {}
    kelime_kok = {}
    toplam = collections.Counter()
    for k, r in d['kokler'].items():
        ad = 'kuranda_var' if r.get('kuranda_var') else 'kuranda_yok'
        klasor = os.path.join(taban, ad, 'kokler')
        os.makedirs(klasor, exist_ok=True)
        dugum = dict(r)
        dugum['sema'] = SEMA
        dugum['tasnif'] = tasnif(k)
        dugum['mana_tasnif'] = mt.get(k) or {'durum': 'tasnif edilemedi (köke ait mana metni yok)'}
        used = sorted({x[0] for v in r.get('mustaklar', {}).values() for x in v})
        dugum['kaliplar'] = {str(i): d['kaliplar'][i] for i in used}
        dugum['kelimeler'] = gruplar.get(k, [])
        yol = os.path.join(klasor, k + '.json')
        with open(yol, 'w', encoding='utf-8') as f:
            f.write(okunur(dugum))
        toplam[ad] += os.path.getsize(yol)
        fih[ad].append([k + '.json', k, len(dugum['kelimeler']), sum(len(v) for v in r.get('mustaklar', {}).values())])
        t = dugum['tasnif']
        agac.setdefault(t['bolge'], {}).setdefault(t['mahrec'], {}).setdefault(t['harf'], {}).setdefault(t['fasil'], []).append(k)
        for e in dugum['kelimeler']:
            kelime_kok[e['kelime']] = k
    with open(os.path.join(taban, 'kuranda_var', 'koksuz.json'), 'w', encoding='utf-8') as f:
        f.write(okunur({'aciklama': 'Kökü olmayan kelimeler (harf, zamir, özel ad vb.)', 'kelimeler': koksuz}))
    kd = os.path.join(taban, 'kuranda_yok', 'kelimeler')
    os.makedirs(kd, exist_ok=True)
    for ad_, dugum in d['kelime_dosyalari'].items():
        with open(os.path.join(kd, ad_ + '.json'), 'w', encoding='utf-8') as f:
            f.write(okunur(dugum))
    d['sayilar']['kelime_dosyasi'] = len(d['kelime_dosyalari'])
    for ad in ('kuranda_var', 'kuranda_yok'):
        with open(os.path.join(taban, ad, 'FIHRIST.json'), 'w', encoding='utf-8') as f:
            f.write(okunur({'sema': SEMA, 'sayilar': d['sayilar'], 'alanlar_kokler': ['dosya', 'kok', 'kelime_sayisi', 'mustak_satiri'], 'kokler': fih[ad],
                            'tasnif_agaci': tasnif_ozeti(agac), 'mana_tasnif_agaci': mana_agaci(mt), 'kelime_kok': kelime_kok if ad == 'kuranda_var' else {}}))
    print(d['sayilar'], {k: len(v) for k, v in fih.items()}, {k: v // 1024 // 1024 for k, v in toplam.items()}, 'MB')


if __name__ == '__main__':
    yaz()
