import collections
import json
import os
import re

from nltk.corpus import wordnet as W

KOK = os.path.dirname(os.path.abspath(__file__))

LEX_TR = {
    'noun.act': 'eylem ve davranış', 'noun.animal': 'hayvan', 'noun.artifact': 'insan yapımı nesne', 'noun.attribute': 'nitelik', 'noun.body': 'beden ve organ',
    'noun.cognition': 'bilişsel süreç ve bilgi', 'noun.communication': 'iletişim ve söz', 'noun.event': 'olay', 'noun.feeling': 'his', 'noun.food': 'yiyecek',
    'noun.group': 'topluluk', 'noun.location': 'yer', 'noun.motive': 'güdü', 'noun.object': 'doğal nesne', 'noun.person': 'insan', 'noun.phenomenon': 'doğa olayı',
    'noun.plant': 'bitki', 'noun.possession': 'mülkiyet', 'noun.process': 'süreç', 'noun.quantity': 'ölçü ve miktar', 'noun.relation': 'ilişki', 'noun.shape': 'biçim',
    'noun.state': 'durum', 'noun.substance': 'madde', 'noun.time': 'zaman', 'noun.Tops': 'en üst kavramlar', 'verb.body': 'bedensel eylem', 'verb.change': 'değişme',
    'verb.cognition': 'düşünme', 'verb.communication': 'söyleme', 'verb.competition': 'yarışma ve çatışma', 'verb.consumption': 'tüketme', 'verb.contact': 'temas ve etkileme',
    'verb.creation': 'yaratma', 'verb.emotion': 'duygulanma', 'verb.motion': 'hareket', 'verb.perception': 'algılama', 'verb.possession': 'sahip olma ve verme',
    'verb.social': 'toplumsal eylem', 'verb.stative': 'bulunma hâli', 'verb.weather': 'hava olayı', 'adj.all': 'sıfat', 'adj.pert': 'ilgi sıfatı',
    'adj.ppl': 'ortaç sıfat', 'adv.all': 'zarf',
}
MAHREC = {'halkiyye': 'ءهعحغخ', 'lehaviyye': 'قك', 'şeceriyye': 'جشض', 'esaliyye': 'صسز', 'nit‘iyye': 'طدت', 'lessiyye': 'ظذث', 'zelakiyye': 'رلن', 'şefeviyye': 'فبم', 'cevfiyye': 'ويا'}
BOLGE_HARF = {'halk': 'boğaz', 'dil': 'dil ve damak', 'dudak ve cevf': 'dudak ve ağız boşluğu'}
TUR = {'N': 'isim', 'V': 'fiil', 'ADJ': 'sıfat', 'P': 'edat', 'PN': 'özel isim', 'PRON': 'zamir', 'CONJ': 'bağlaç', 'DEM': 'işaret zamiri', 'REL': 'ilgi zamiri',
       'NEG': 'olumsuzluk edatı', 'T': 'zaman zarfı', 'LOC': 'yer zarfı', 'COND': 'şart edatı', 'ACC': 'nasb edatı', 'INTG': 'soru edatı', 'SUB': 'masdar bağlacı'}
BAB = {'II': "tef'îl", 'III': "müfâ'ale", 'IV': "if'âl", 'V': "tefa''ul", 'VI': "tefâ'ul", 'VII': "infi'âl", 'VIII': "ifti'âl", 'IX': "if'ilâl", 'X': "istif'âl", 'XI': "if'îlâl", 'XII': "if'ivvâl"}
ESIK_DERINLIK = 4


def yukle_en2tr():
    yol = os.path.join(KOK, 'kitap_destek', 'turetme_motoru', 'veri', 'tr_vikisozluk.json')
    return json.load(open(yol, encoding='utf-8'))['en2tr']


_kap = {}
_der = {}


def kapanis(ad):
    if ad not in _kap:
        s = W.synset(ad)
        k = set()
        for yol in s.hypernym_paths():
            k.update(x.name() for x in yol)
        _kap[ad] = k
    return _kap[ad]


def derinlik(ad):
    if ad not in _der:
        _der[ad] = W.synset(ad).min_depth()
    return _der[ad]


def sebep_bul(kumeler):
    """kumeler: her üye için ata kavram kümesi. En genel (kapsayıcı) ortak sebep: bütün üyeleri kapsayan en derin kavram.
    Yoksa açgözlü kapsama ile birkaç sebep döner."""
    n = len(kumeler)
    if n == 0:
        return None, []
    sayac = collections.Counter()
    for k in kumeler:
        sayac.update(k)
    tam = [g for g, c in sayac.items() if c == n and derinlik(g) >= ESIK_DERINLIK]
    if tam:
        return max(tam, key=lambda g: (derinlik(g), g)), []
    kalan = list(range(n))
    secilen = []
    while kalan:
        c = collections.Counter()
        for i in kalan:
            c.update(g for g in kumeler[i] if derinlik(g) >= ESIK_DERINLIK)
        if not c:
            break
        g = max(c, key=lambda x: (c[x], derinlik(x), x))
        kap = [i for i in kalan if g in kumeler[i]]
        secilen.append((g, len(kap)))
        kalan = [i for i in kalan if i not in set(kap)]
        if len(secilen) >= 4:
            break
    return None, secilen


CEVIRI_YOL = os.path.join(KOK, 'kitap_destek', 'turetme_motoru', 'veri', 'wordnet_tanim_tr.json')


def ceviri_yukle():
    return json.load(open(CEVIRI_YOL, encoding='utf-8')) if os.path.exists(CEVIRI_YOL) else {}


class Etiket:
    istenen = set()

    def __init__(self):
        self.ceviri = ceviri_yukle()

    def tanim(self, ad):
        en = W.synset(ad).definition()
        tr = self.ceviri.get(ad)
        if not tr:
            Etiket.istenen.add(ad)
        return tr, en

    def lem(self, ad):
        return W.synset(ad).lemmas()[0].name().replace('_', ' ')

    def tr(self, ad):
        s = W.synset(ad)
        ad_ = s.lemmas()[0].name().replace('_', ' ')
        return ad_ if s.lexname() == 'noun.Tops' else ad_ + ' (' + LEX_TR.get(s.lexname(), s.lexname()) + ')'

    def tam(self, ad):
        tr, en = self.tanim(ad)
        return '«' + self.tr(ad) + '»: ' + (tr + ' (İngilizce: ' + en + ')' if tr else en)


def cebel_ozetleri():
    import sys
    sys.path.insert(0, os.path.join(KOK, 'kitap_destek', 'turetme_motoru'))
    import cebel as CB
    oz = {}
    for k, v in CB.yukle().items():
        if v.get('fasil_ozeti') and v['fasil'] not in oz:
            t = v['fasil_ozeti']
            t = re.sub(r'^°?\s*معنى الفصل المعجمي[^:]*:', '', t).strip()
            oz[v['fasil']] = t
    return oz


def sebepleri_yaz(kat, dugumler, anahtar):
    et = Etiket()
    cebel = cebel_ozetleri()
    sonuc = [None] * len(kat)
    syn = [d['syn'] for d in dugumler]
    kok_kap = {}

    def uye_kapanisi(i):
        if i not in kok_kap:
            k = set()
            for s in syn[i]:
                k |= kapanis(s)
            kok_kap[i] = k
        return kok_kap[i]

    gomme_u = anahtar.index('gomme')
    # sıra: derinden sığa
    sira = sorted(range(len(kat)), key=lambda k: -kat[k]['d'])
    for k in sira:
        c = kat[k]
        u = anahtar[c['u']]
        ad = c['ad']
        s, t, b = None, 1, ad
        if u == 'ses':
            if c['d'] == 0:
                s = 'kökün ilk harfi ' + BOLGE_HARF.get(ad, ad) + ' bölgesinden çıkar'
            elif c['d'] == 1:
                s = 'kökün ilk harfi «' + MAHREC.get(ad, '') + '» harflerinden biridir (' + ad + ' mahreci)'
            elif c['d'] == 2:
                s = 'kökün ilk harfi «' + ad + '»'
            else:
                s = 'kökün ilk iki illetsiz harfi «' + ad.replace('fasıl ', '') + '»'
        elif u == 'wordnet':
            if c['d'] == 0:
                s = 'kökün kelimeleri WordNet\'te «' + ad + '» başlığı altındaki kavramlara bağlanır'
            elif c['d'] == 1:
                s = 'kökün kelimeleri WordNet\'te «' + LEX_TR.get(ad, ad) + '» (' + ad + ') türü kavramlara bağlanır'
                b = LEX_TR.get(ad, ad)
            else:
                try:
                    s = et.tam(ad)
                    b = et.tr(ad)
                except Exception:
                    s = ad
        elif u == 'gomme':
            birimler = []
            kaynak = []
            for j in c['cocuk']:
                r = sonuc[j]
                if r['tek_g']:
                    birimler.append(kapanis(r['tek_g']))
                    kaynak.append(j)
                else:
                    for g, n in r['coklu']:
                        birimler.append(kapanis(g))
            cocuk_uye = set()
            for j in c['cocuk']:
                cocuk_uye.update(kat[j]['uye'])
            oz = [i for i in c['uye'] if i not in cocuk_uye]
            bilinen = [i for i in oz if syn[i]]
            birimler += [uye_kapanisi(i) for i in bilinen]
            bilinmeyen = len(oz) - len(bilinen)
            g, liste = sebep_bul(birimler)
            ek = (' (' + str(bilinmeyen) + ' kökün WordNet karşılığı yok)') if bilinmeyen else ''
            if not birimler:
                s, t = 'sebep belirlenemedi: üyelerin WordNet karşılığı yok', 0
                sonuc[k] = {'s': s, 't': 0, 'tek_g': None, 'coklu': [], 'b': 'sebebi belirsiz küme'}
                continue
            if g:
                s = 'ortak sebep: ' + et.tam(g) + ek
                sonuc[k] = {'s': s, 't': 1, 'tek_g': g, 'coklu': [], 'b': et.tr(g)}
                continue
            t = 0
            s = 'çok sebepli, içinde daha fazla küme var: ' + '; '.join('«' + et.tr(x) + '» (' + str(n) + ' birim)' for x, n in liste)
            sonuc[k] = {'s': s, 't': 0, 'tek_g': None, 'coklu': liste, 'b': ('çok sebepli: «' + et.lem(liste[0][0]) + '»' + (' ve ' + str(len(liste) - 1) + ' sebep daha' if len(liste) > 1 else '')) if liste else 'çok sebepli küme', 'alt': [[n, et.tam(x)] for x, n in liste]}
            continue
        elif u == 'muhassas':
            s = 'el-Muhassas\'ın «' + ad + '» ' + ('kitabında' if c['d'] == 0 else 'bâbında') + ' bu kökün biçimleri, kitabın boyuna göre en çok burada geçer'
        elif u == 'cebel':
            if c['d'] == 0:
                s = 'Cebel kökleri ilk harfe göre «' + ad + '» kitabında toplar'
            else:
                s = ('Cebel\'e göre ortak mana: ' + cebel[ad]) if ad in cebel else 'Cebel kökleri ilk iki harfe göre «' + ad + '» faslında toplar'
        elif u == 'mecaz':
            s = 'Zemahşerî, Esâsü\'l-Belâğa\'da bu kök için mecaz kolu verir' if ad == 'mecazlı' else 'Zemahşerî, Esâsü\'l-Belâğa\'da bu kök için yalnız hakîkat anlamı verir'
        elif u == 'prototip':
            s = 'Zemahşerî\'nin mecaz cümleleri, kökün prototip anlamına benzerlik bakımından «' + ad + '» dilimde (benzerlik üçe bölünür, sınırlar veriden çıkar)'
        elif u == 'korpus':
            if c['d'] == 0:
                s = 'kök Kur\'ân\'da en çok ' + TUR.get(ad, ad) + ' olarak geçer (Quranic Arabic Corpus 0.4)'
            else:
                b = ad.replace('bâb ', '')
                s = 'kökün Kur\'ân\'daki fiilleri en çok «' + b + '» bâbındadır (' + BAB.get(b, '') + ')'
        elif u == 'kuran':
            s = 'kök Kur\'ân\'da geçiyor' if 'var' in ad else 'kök Kur\'ân\'da geçmiyor; başka lügatlerden alındı'
        elif u == 'etymarab':
            s = 'EtymArab\'da bu kökün maddesi ' + ('dolu' if ad == 'dolu' else 'yalnız yer tutucu')
        sonuc[k] = {'s': s, 't': t, 'tek_g': None, 'coklu': [], 'b': b}
    return sonuc


def ceviri_uret():
    import sys
    sys.path.insert(0, KOK)
    import kategori_yerlesim as KY
    from transformers import MarianMTModel, MarianTokenizer
    dugumler = KY.yukle()
    kat, _ = KY.kategoriler(dugumler)
    sebepleri_yaz(kat, dugumler, [a for a, _ in KY.USULLER])
    et = Etiket()
    for d in dugumler:
        for ad in d['syn'][:3]:
            et.tanim(ad)
    gerek = sorted(Etiket.istenen, key=lambda a: len(W.synset(a).definition()))
    print('çevrilecek tanım', len(gerek), flush=True)
    ad_ = 'Helsinki-NLP/opus-mt-tc-big-en-tr'
    tok = MarianTokenizer.from_pretrained(ad_)
    m = MarianMTModel.from_pretrained(ad_)
    sonuc = dict(et.ceviri)
    for i in range(0, len(gerek), 24):
        grup = gerek[i:i + 24]
        b = tok([W.synset(a).definition() for a in grup], return_tensors='pt', padding=True, truncation=True, max_length=256)
        o = m.generate(**b, max_new_tokens=160, num_beams=4)
        for a, t in zip(grup, tok.batch_decode(o, skip_special_tokens=True)):
            sonuc[a] = t
        if (i // 24) % 20 == 0:
            tmp = CEVIRI_YOL + '.yeni'
            json.dump(sonuc, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
            os.replace(tmp, CEVIRI_YOL)
            print(i, len(gerek), flush=True)
    tmp = CEVIRI_YOL + '.yeni'
    json.dump(sonuc, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    os.replace(tmp, CEVIRI_YOL)
    print('bitti', len(sonuc), flush=True)


if __name__ == '__main__':
    ceviri_uret()
