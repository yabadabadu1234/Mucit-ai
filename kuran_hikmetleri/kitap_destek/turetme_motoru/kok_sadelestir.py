import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..', '..')
KD = os.path.join(K, 'kelime_kaydi', 'kuranda_var')
KOK = os.path.join(KD, 'kokler')
AGAC = os.path.join(K, 'kitap_destek', 'kok_manalari', 'agac')
AJAN = os.path.join(K, 'kitap_destek', 'lugat_ajan')
ETIM = os.path.join(K, 'kaynak', 'lugat', 'etimoloji')
sys.path.insert(0, HERE)
import baz_fiil as BF

ESER = {'Kubbe Altı': 'Kubbealtı Lügati', 'Kubbealtı': 'Kubbealtı Lügati'}
TAS = re.compile(r'^(.*?)\s+maddesi\.\s*Sayfa:\s*(\d+)\s*$')
SEBEP = {}
VARSAYILAN_DURUM = 'model-üretimi, doğrulanmadı'
ESER_ADLARI = ('Kamus-u Türki', 'Lugat-ı Remzi', 'Kubbe Altı', 'Kubbealtı Lügati', 'Vankulu Lügati')
ONTOLOJI_ATILAN = ('kunye',)
YONTEM = {}
SABIT_METIN = ('Türkçe fiil sapı ve kök manası okunarak Claude hükmü', 'veriden: üçte bir dilimler 0.362 / 0.532; uzun metinler 350 karakterlik parçalara bölünüp vektörleri ortalandı, metin kesilmedi', "Cebel mu'cemlerinde kök yok")
VIKI_ATILAN = ('h', 'w')
VIKI_AD = {'u': 'madde', 'n': 'etim_no', 's': 'etim_sablon', 'p': 'tur', 'e': 'baslik', 'g': 'anlam', 'r': 'okunus', 'tag': 'etiket', 'fo': 'form_of', 'ds': 'torunlar', 'synonyms': 'esanlamli', 'antonyms': 'zit'}


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


def bos_at(d):
    return {k: v for k, v in d.items() if v not in (None, '', [], {})}


def metin(x):
    if isinstance(x, list):
        return ' '.join(str(i) for i in x)
    return re.sub(r'\s+', ' ', x or '').strip()


def lugat(s):
    sonuc = collections.OrderedDict()
    gor = {}
    for w, L in (s.get('mustak_lugat') or {}).items():
        for m in L:
            eser = ESER.get(m['eser'], m['eser'])
            k = bos_at({'madde': m.get('madde'), 'tur': m.get('tur'), 'koken': m.get('koken'), 'yazilis': m.get('yazilis'), 'okunus': m.get('okunus')})
            k['manalar'] = [bos_at({'no': x.get('no'), 'etiket': x.get('etiket'), 'tanim': x.get('tanim'), 'misaller': x.get('misaller')}) for x in m.get('manalar') or []]
            dy = [bos_at({'deyim': x.get('deyim'), 'etiket': x.get('etiket'), 'tanim': x.get('tanim'), 'misaller': x.get('misaller')}) for x in m.get('deyimler') or []]
            if dy:
                k['deyimler'] = dy
            anahtar = (eser, json.dumps(k, ensure_ascii=False, sort_keys=True))
            if anahtar in gor:
                gor[anahtar]['kelime'].append(w)
                continue
            k['kelime'] = [w]
            gor[anahtar] = k
            sonuc.setdefault(eser, []).append(k)
    for w, v in (s.get('osmanlica_lugatler') or {}).items():
        for m in v.get('maddeler') or []:
            eser = ESER.get(m['eser'], m['eser'])
            t = TAS.match(m.get('mana') or '')
            if t:
                k = {'madde': m['madde'], 'sayfa': int(t.group(2))}
            else:
                k = bos_at({'madde': m.get('madde'), 'metin': m.get('mana'), 'arapca': m.get('arapca')})
            k['eslesme'] = m.get('eslesme')
            anahtar = (eser, json.dumps(k, ensure_ascii=False, sort_keys=True))
            if anahtar in gor:
                if w not in gor[anahtar]['kelime']:
                    gor[anahtar]['kelime'].append(w)
                continue
            k['kelime'] = [w]
            gor[anahtar] = k
            sonuc.setdefault(eser, []).append(k)
    return sonuc


def tercume_birles(orj, tr, ana):
    o = dict(orj)
    if isinstance(tr, str):
        o[ana + '_tr'] = tr
    else:
        for k, v in (tr or {}).items():
            o[k + '_tr'] = v
    return o


def liste_birles(orj, tr, atilan=(), ad=None):
    orj = orj or []
    tr = tr or []
    temiz = [{k: v for k, v in e.items() if k not in atilan} for e in orj]
    if not tr:
        return temiz, None
    if len(orj) == len(tr):
        out = []
        for e, t in zip(temiz, tr):
            e = dict(e)
            for k, v in t.items():
                e[(ad or {}).get(k, k) + '_tr'] = v
            out.append(e)
        return out, None
    return temiz, tr


def vikisozluk(kk, kok):
    etim = []
    out = []
    for e in kk:
        t = e.get('t') or ''
        el = e.get('el') or []
        anahtar = (t, json.dumps(el, ensure_ascii=False))
        if anahtar not in [x[0] for x in etim]:
            etim.append((anahtar, {'metin': t, 'kognatlar': el}))
        i = [x[0] for x in etim].index(anahtar)
        y = {}
        for k, v in e.items():
            if k in VIKI_ATILAN or k in ('t', 'el'):
                continue
            if k == 'yol':
                continue
            if k == 'k':
                if v != kok:
                    y['kok_yazilis'] = v
                continue
            y[VIKI_AD.get(k, k)] = v
        if e.get('yol') and e['yol'] != 'kök':
            y['bag'] = e['yol']
        if t or el:
            y['etimoloji'] = i
        out.append(y)
    return out, [x[1] for x in etim]


def korpus(s):
    kcs = s.get('kuran_korpusu') or []
    if isinstance(kcs, dict):
        kcs = [kcs]
    if not kcs:
        return None
    o = {'gecis': 0, 'ilk': None}
    for alan in ('tur', 'bab', 'zaman_kip', 'fiil_ismi_ozellikleri', 'lemmalar', 'bicimler'):
        o[alan] = collections.Counter()
    for kc in kcs:
        o['gecis'] += kc.get('gecis', 0)
        ilk = kc.get('ilk_yer')
        if ilk and (o['ilk'] is None or [int(x) for x in ilk.split(':')] < [int(x) for x in o['ilk'].split(':')]):
            o['ilk'] = ilk
        for alan in ('tur', 'bab', 'zaman_kip', 'fiil_ismi_ozellikleri', 'lemmalar', 'bicimler'):
            o[alan].update(kc.get(alan) or {})
    for alan in ('tur', 'bab', 'zaman_kip', 'fiil_ismi_ozellikleri', 'lemmalar', 'bicimler'):
        o[alan] = dict(o[alan])
    return o


def mustak(d):
    out = collections.OrderedDict()
    for g, rows in d['mustaklar'].items():
        yeni = []
        for r in rows:
            kal = d['kaliplar'][str(r[0])]
            assert kal[0] == g
            yeni.append([kal[1], kal[2]] + r[1:])
        out[g] = yeni
    return out


def red(d):
    out = []
    for g, vez, sebep in d['reddedilen']:
        if sebep not in SEBEP:
            SEBEP[sebep] = 'r%d' % (len(SEBEP) + 1)
        out.append([g, vez, SEBEP[sebep]])
    return out


def kelimeler(d, kt, bz):
    gr = collections.OrderedDict()
    for w in d['kelimeler']:
        hal = 'fiil' if w.get('zaman') else 'isim'
        k = (w['lemma'], hal, w.get('bab') or '')
        g = gr.setdefault(k, {'lemma': w['lemma'], 'hal': hal, 'bab': w.get('bab') or '', 'bicimler': []})
        tr = w.get('turkce') or {}
        b = bos_at({'kelime': w['kelime'], 'zaman': w.get('zaman'), 'ilk': w.get('ilk_gecis'), 'adet': w.get('adet'), 'tr': tr.get('yuzey'), 'tr_eyup': tr.get('eyupipler'), 'jeffery': w.get('jeffery'), 'kok_durumu': w.get('kok_durumu'), 'asil': w.get('asil')})
        g['bicimler'].append(b)
        if tr.get('lemma') and not g.get('tr'):
            g['tr'] = tr['lemma']
            if tr.get('lemma_durum') != VARSAYILAN_DURUM:
                g['tr_durum'] = tr.get('lemma_durum')
    ind = collections.defaultdict(list)
    for gname, rows in d['mustaklar'].items():
        for r in rows:
            kal = d['kaliplar'].get(str(r[0]), [None, '', ''])
            ind[BF.norm(r[1])].append((gname, kal[1], 'aday' in (kal[2] or '')))
    out = []
    for (lemma, hal, bab), g in gr.items():
        bn, bm = BF.BABLAR.get(bab, ('', ''))
        es = ind.get(BF.norm(lemma)) if hal == 'isim' else None
        if es and kt['tur'] == 'isim':
            es = [e for e in es if e[0].startswith('cem') or 'mensûb' in e[0] or 'tasğîr' in e[0]] or None
        if es:
            kesin = [e for e in es if not e[2]]
            sec = kesin or es
            nasil = ' ; '.join(sorted({'%s · %s' % (a, b) for a, b, _ in sec})[:3]) + ('' if kesin else ' (yalnız aday eşleşme)')
        elif bn:
            nasil = 'bâb %s (%s): %s' % (bn, bab, bm)
        elif kt['tur'] == 'isim':
            nasil = 'kök isim: fiil kalıbıyla türemedi'
        else:
            nasil = 'lügat kalıbıyla eşleşmedi'
        g['bab_no'] = bn
        g['nasil'] = nasil
        g['adet'] = sum(b.get('adet') or 0 for b in g['bicimler'])
        out.append(bos_at(g))
    out.sort(key=lambda x: -x['adet'])
    return out


def ekler():
    esas = {}
    for f in sorted(glob.glob(os.path.join(AGAC, '*.txt'))):
        for sat in open(f, encoding='utf-8').read().splitlines():
            if sat.strip():
                k, gov = sat.split('|', 1)
                esas[k] = gov.strip()
    ek_lugat = {}
    for alt in ('tercume', 'kirp'):
        for f in glob.glob(os.path.join(AJAN, alt, '*.json')):
            j = json.load(open(f, encoding='utf-8'))
            k = os.path.basename(f)[:-5]
            icerik = {a: b for a, b in j.items() if a not in ('kok', 'model', 'tamam') and b not in (None, '', [], {}, 0)}
            if icerik:
                ek_lugat.setdefault(k, {})[alt] = icerik
    etim = {}
    for f in glob.glob(os.path.join(ETIM, '*.md')):
        etim[BF.norm(os.path.basename(f)[:-3])] = open(f, encoding='utf-8').read()
    return esas, ek_lugat, etim


def donustur(d, esas, ek_lugat, etim):
    s = d['sozlukler']
    kt = BF.kok_turu(d)
    bz = BF.baz_fiil(d, kt)
    tf = d.get('turkce_fiil') or {}
    ka = s.get('kok_anlamlari') or {}
    tc = s.get('tercume') or {}
    y = collections.OrderedDict()
    y['kok'] = d['kok']
    y['tur'] = kt['tur']
    y['tur_guven'] = kt['guven']
    y['tur_dayanak'] = kt['dayanak']
    y['lugat_fiil'] = kt['lugat_fiil']
    if bz and bz.get('ad'):
        y['baz_fiil'] = bz['ad']
        y['baz_ayrim'] = bz.get('ayrim')
    y['tur_kuran'] = kt.get('kuran')
    y['fiil'] = tf.get('sap')
    y['fiil_kaynak'] = tf.get('kaynak')
    y['fiil_guven'] = tf.get('guven')
    y['sinif'] = d.get('sinif')
    t = d.get('tasnif') or {}
    y['ses'] = bos_at({'harf': t.get('harf'), 'fasil': t.get('fasil'), 'mahrec': t.get('mahrec'), 'bolge': t.get('bolge')})
    y['anlam'] = ka.get('turkce')
    y['anlam_ihtimal'] = ka.get('ihtimaller')
    y['anlam_varlik'] = ka.get('varlik')
    y['anlam_eyup'] = s.get('eyupipler_kok_anlami')
    y['esas_manalar'] = esas.get(d['kok'])
    y['lugat'] = lugat(s)
    mk, mk_ayri = liste_birles(s.get('mekayis'), tc.get('mekayis'))
    y['mekayis'] = mk
    cb = s.get('cebel_mihveri')
    if cb:
        cb = {k: v for k, v in cb.items() if k not in ('kaynak', 'sesler') or (k == 'sesler' and v)}
        y['cebel'] = tercume_birles(cb, tc.get('cebel_mihveri'), 'mihveri')
    hm = d.get('hakikat_mecaz_tasnif') or {}
    y['zemahseri'] = bos_at({k: v for k, v in hm.items() if k != 'kaynak'})
    ao, ao_ayri = liste_birles(s.get('arabic_ontology'), tc.get('arabic_ontology'), ONTOLOJI_ATILAN)
    y['ontoloji'] = ao
    y['ontoloji_tr'] = ao_ayri
    vk, etl = vikisozluk(s.get('kaikki_vikisozluk') or [], d['kok'])
    vk, vk_ayri = liste_birles(vk, tc.get('kaikki_vikisozluk'), (), VIKI_AD)
    y['vikisozluk'] = vk
    y['vikisozluk_tr'] = vk_ayri
    y['vikisozluk_etimolojiler'] = etl
    ea = s.get('etymarab') or {}
    if ea.get('dolu') or tc.get('etymarab'):
        y['etymarab'] = tercume_birles(dict({k: v for k, v in ea.items() if k not in ('kaynak', 'dolu')}, **({} if ea.get('dolu') else {'yer_tutucu': True})), tc.get('etymarab'), 'kok_maddesi')
    y['etimoloji'] = s.get('etimoloji')
    y['ek_lugat'] = ek_lugat.get(d['kok'])
    y['kuran'] = korpus(s)
    if d.get('kuran_gecisleri') is not None:
        y['kuran'] = dict(y['kuran'] or {}, morfoloji_gecis=d['kuran_gecisleri'])
    y['kelimeler'] = kelimeler(d, kt, bz)
    ys = collections.defaultdict(list)
    for w in d['kelimeler']:
        ys[BF.norm(w['kelime'])].append((w.get('turkce') or {}).get('yuzey'))
    y['tr_ek'] = {k: v for k, v in (s.get('renk_sozluk') or {}).items() if v not in ys.get(BF.norm(k), [])}
    y['mustak'] = mustak(d)
    y['reddedilen'] = red(d)
    mt = d.get('mana_tasnif') or {}
    y['mana'] = bos_at({k: v for k, v in mt.items() if k != 'yontem'})
    if mt.get('yontem'):
        y['mana_yontem'] = YONTEM.setdefault(mt['yontem'], 'm%d' % (len(YONTEM) + 1))
    y['gomme'] = d.get('mana_tasnif_gomme')
    y['wordnet'] = d.get('kolekzifikasyon_kavramlari')
    mh = d.get('muhassas_tasnif') or {}
    y['muhassas'] = bos_at({k: v for k, v in mh.items() if k not in ('kaynak',)})
    pr = d.get('prototip_yayilim_tasnif') or {}
    y['prototip'] = bos_at({k: v for k, v in pr.items() if k not in ('kaynak', 'prototipler', 'halka_esikleri')})
    y['pilot'] = s.get('pilot')
    return bos_at(y)


ATILAN = {'sema', 'kaynak', 'kunye', 'sorgular', 's', 'h', 'yol', 'u', 'k', 'n', 'w', 'halka_esikleri', 'ses_mana_tasnif', 'kuranda_var', 'kaliplar', 'reddedilen', 'turetim', 'prototipler', 'id', 'dolu', 'kok'}


def dizgiler(o, cikti, atla=True):
    if isinstance(o, dict):
        for k, v in o.items():
            if atla and k in ATILAN:
                continue
            dizgiler(v, cikti, atla)
    elif isinstance(o, list):
        for v in o:
            dizgiler(v, cikti, atla)
    elif isinstance(o, str) and len(o) >= 12:
        cikti.append(re.sub(r'\s+', ' ', o))


def dogrula(d, y):
    eski = []
    dizgiler(d, eski)
    yeni = []
    dizgiler(y, yeni, False)
    havuz = '\n'.join(yeni)
    return [x for x in dict.fromkeys(eski) if x not in havuz and not TAS.match(x) and x not in ESER_ADLARI and x != VARSAYILAN_DURUM and ' := ' not in x and x not in YONTEM and x not in SABIT_METIN]


def calis(yaz=False, kaynak=None):
    esas, ek_lugat, etim = ekler()
    dosyalar = sorted(glob.glob(os.path.join(kaynak or KOK, '*.json')))
    kayip = {}
    eski_bayt = yeni_bayt = atlanan = 0
    for f in dosyalar:
        ham = open(f, encoding='utf-8').read()
        d = json.loads(ham)
        if 'sozlukler' not in d:
            atlanan += 1
            continue
        y = donustur(d, esas, ek_lugat, etim)
        k = dogrula(d, y)
        if k:
            kayip[os.path.basename(f)] = k
        cikti = okunur(y) + '\n'
        eski_bayt += len(ham.encode('utf-8'))
        yeni_bayt += len(cikti.encode('utf-8'))
        if yaz and not k:
            open(os.path.join(KOK, os.path.basename(f)), 'w', encoding='utf-8').write(cikti)
    return len(dosyalar), atlanan, eski_bayt, yeni_bayt, kayip


def fihrist():
    yol = os.path.join(KD, 'FIHRIST.json')
    f = json.load(open(yol, encoding='utf-8'))
    f['sema'] = {
        'kok_dosyasi': 'kokler/<kök>.json: köke ait bütün malumat tek dosyada, her bilgi bir kez',
        'alanlar': {
            'tur': 'isim veya fiil kökü; tur_guven ve tur_dayanak delili', 'baz_fiil': 'köke tekabül eden on dört baz fiilden biri',
            'fiil': 'Türkçe fiil sapı', 'anlam': 'kökün Türkçe manası', 'lugat': 'eser adına göre madde listesi; kelime = maddenin bağlandığı Kur\'ân kelimeleri',
            'mekayis': 'İbn Fâris', 'cebel': 'Cebel', 'zemahseri': 'hakîkat ve mecâz', 'ontoloji': 'Arabic Ontology; _tr tercüme',
            'vikisozluk': 'Vikisözlük maddeleri; etimoloji = vikisozluk_etimolojiler dizinindeki sıra', 'kuran': 'Kur\'ân korpusu sayımları',
            'kelimeler': 'lemma, hal ve bâba göre gruplu Kur\'ân kelimeleri; bicimler yüzey biçimleridir', 'mustak': 'müştak grupları: [vezin, durum, ...]',
            'reddedilen': 'motorun reddettiği [grup, vezin, sebep kodu]; kodlar red_sebepleri\'nde'},
        'tr_durum': 'yazılmadıysa: ' + VARSAYILAN_DURUM}
    f['red_sebepleri'] = {v: k for k, v in SEBEP.items()}
    f['mana_yontemleri'] = {v: k for k, v in YONTEM.items()}
    f['sabitler'] = {'baz_fiil_guven': 'orta', 'baz_fiil_dayanak': 'Türkçe fiil sapı ve kök manası okunarak Claude hükmü', 'prototip_halka_esikleri': 'veriden: üçte bir dilimler 0.362 / 0.532; uzun metinler 350 karakterlik parçalara bölünüp vektörleri ortalandı, metin kesilmedi', 'cebel_yok': "kökte cebel anahtarı yoksa: Cebel mu'cemlerinde kök yok", 'vikisozluk_bag': 'yazılmadıysa: kökün kendi maddesi; kök dışı: asıl madde veya müştak'}
    f['kaynaklar'] = {
        'kuran_korpusu': 'Quranic Arabic Corpus 0.4 (Kais Dukes, Leeds Üniversitesi; GNU GPL; http://corpus.quran.com)',
        'cebel': "Muhammed Hasan Hasan Cebel, el-Mu'cemü'l-İştikâkıyyü'l-Mü'asssal li-Elfâzi'l-Kur'âni'l-Kerîm (Şâmile, yazıya geçirilmiş metin)",
        'etymarab': 'EtymArab, Oslo Üniversitesi (Bibliotheca Polyglotta)',
        'zemahseri': "Zemahşerî, Esâsü'l-Belâğa (tahkik: Muhammed Bâsil Uyûnü's-Sûd, Dâru'l-Kütübi'l-İlmiyye 1998; Şâmile, yazıya geçirilmiş metin)",
        'muhassas': 'İbn Sîde, el-Muhassas (konu sıralı lügat; Şâmile)',
        'prototip': 'prototip ve yayılım (radyal kategori usulü)',
        'mana': 'Arabic WordNet v2 → Princeton WordNet; AWN kaydı yoksa Vikisözlük/Arabic Ontology İngilizce karşılığı → Princeton WordNet ilk anlam (makine eşlemesi)',
        'ontoloji': 'Arabic Ontology, Birzeit University (SinaLab, Mustafa Jarrar), ücretsiz sürüm, çıkarım 09-06-2024; atıf: Jarrar 2021 Applied Ontology 16:1; Jarrar ve Amayreh 2019 NLDB'}
    open(yol, 'w', encoding='utf-8').write(okunur(f) + '\n')


if __name__ == '__main__':
    kay = sys.argv[sys.argv.index('--kaynak') + 1] if '--kaynak' in sys.argv else None
    n, a, e, y, k = calis('--yaz' in sys.argv, kay)
    if '--yaz' in sys.argv and not k:
        fihrist()
    print(n, a, e, y, len(k))
    for ad, L in list(k.items())[:5]:
        print(ad, L[:2])
