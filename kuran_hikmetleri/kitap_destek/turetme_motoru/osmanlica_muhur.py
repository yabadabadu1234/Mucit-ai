import collections
import concurrent.futures
import glob
import json
import os
import re
import sys
import threading
import time
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GIRDI = os.path.join(KOK, 'kelime_kaydi')
CIKTI = os.path.join(GIRDI, 'osmanlica')
HAFIZA = os.path.join(CIKTI, '_hafiza.jsonl')
UC = 'https://evren-llmapi.ssyz.org.tr/v1/chat/completions'
ARAP = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
LATIN_KELIME = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşüÂÎÛâîû][A-Za-zÇĞİÖŞÜçğıöşüÂÎÛâîû'’‘\-]{2,}")
TRANSLIT = re.compile(r'[ḍṣṭẓḥšġḫʔʕʿʾāīūēōṯḏǧŝñ]')
ATLA_ANAHTAR = {'r', 'u', 'w', 'k', 'yol', 'kok', 'kelime', 'lemma', 'merkez_kok', 'ilk_gecis', 'dayanak_synset', 'ince', 'orta', 'zaman'}

SISTEM = ("Sen Türkçe ve İngilizce metinleri Osmanlı Türkçesine (Latin harfli) tercüme eden mütercimsin. Üslûp: Ömer Seyfettin ve Mehmed Âkif nesri; sade, canlı, yerleşik Arapça-Fârisî asıllı kelimelerle. "
          "Tercüme birebirdir: mânâ eksilmez, artmaz, izah ve misal eklenmez, sıra ve noktalama aynı kalır; hiçbir şey uydurma. Ne varsa tercüme et. "
          "DEĞİŞTİRME: ⟦0⟧ gibi işaretleri (yerlerini ve sayılarını aynen koru, tercüme edilen cümlenin içinde uygun yere yerleştir), Arap harfli her metin, Latin harfli Arapça okunuş (naḍada, yanḍidu gibi), IPA (/ju.biː.nu/), kök harfleri, sayılar, kod ve kimlikler (noun.act, g3.1), bâb numaraları, "
          "köşeli/yuvarlak parantez ve işaretler, satır sonları (\\n), Markdown işaretleri (#, **), özel adlar, kitap adları, sayfa ve âyet numaraları. "
          "Girdi bir JSON dizisidir; çıktı AYNI uzunlukta ve sırada yalnız bir JSON dizisi olsun. Tercüme edilecek bir şey yoksa öğeyi aynen döndür. JSON dışında hiçbir şey yazma.")

KORU = re.compile(r"(?:[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\u200c\u200d](?:[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\u200c\u200d\u0640 ]*[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\u200c\u200d])?)"
                  r"|/[^/\n]{1,80}/|[A-Za-zÇĞİÖŞÜçğıöşüÂÎÛâîû'’‘\-]*[ḍṣṭẓḥšġḫʔʕʿʾāīūēōṯḏǧŝñḍṣṭẓḥ][A-Za-zÇĞİÖŞÜçğıöşüÂÎÛâîû'’‘\-ḍṣṭẓḥšġḫʔʕʿʾāīūēōṯḏǧŝñ]*")


def koru(s):
    parca = []

    def al(m):
        parca.append(m.group(0))
        return '⟦%d⟧' % (len(parca) - 1)
    return KORU.sub(al, s), parca


def ac(s, parca):
    return re.sub(r'⟦(\d+)⟧', lambda m: parca[int(m.group(1))], s)


kilit = threading.Lock()
hafiza = {}
sayac = {'jeton': 0, 'istek': 0, 'hata': 0}


def cevrilir(yol, s):
    if not LATIN_KELIME.search(ARAP.sub(' ', s)):
        return False
    govde = ARAP.sub(' ', s).strip()
    belirtec = govde.split()
    if len(belirtec) >= 2:
        return True
    if yol and yol[-1] in ATLA_ANAHTAR:
        return False
    if TRANSLIT.search(s):
        return False
    return True


def gez(d, cb):
    """cb(tur, metin, bağlam): 'A' bağlamsız metin; 'M' müştak satırı; 'K' kelime biçimi; 'S' fiil sapı; 'KA' kök anlamı.
    M, K, S, KA için metindeki makine üretimi Türkçe karşılık modele VERİLMEZ; çeviri Arapça ve İngilizce kaynaktan yapılır."""
    kok = d.get('kok', '')
    ka = (d.get('sozlukler') or {}).get('kok_anlamlari') or {}
    k0 = {'kok': kok}

    def X(tur, m, **ek):
        return cb(tur, m, dict(k0, **ek)) if isinstance(m, str) and m.strip() else m

    def r(o, yol):
        if isinstance(o, dict):
            return {k: r(v, yol + [k]) for k, v in o.items()}
        if isinstance(o, list):
            return [r(v, yol) for v in o]
        if isinstance(o, str) and cevrilir(yol, o):
            return cb('A', o, None)
        return o
    cikti = {}
    for k, v in d.items():
        if k == 'mustaklar':
            cikti[k] = {kal: [[(X('M', x, kalip=kal, arapca=row[1] if len(row) > 1 else '') if i == 3 else (r(x, ['mustaklar']) if isinstance(x, str) and i not in (2, 4) else x)) for i, x in enumerate(row)] for row in rows] for kal, rows in v.items()}
        elif k == 'kelimeler':
            ks = []
            for x in v:
                y = {}
                for kk, vv in x.items():
                    if kk == 'turkce' and isinstance(vv, dict):
                        y[kk] = {a: (X('K', b, tip=a, arapca=x.get('kelime', '') if a == 'yuzey' else x.get('lemma', ''), sozluk_turu=x.get('tur', ''), bab=x.get('bab', ''), zaman=x.get('zaman', '')) if a in ('yuzey', 'lemma') else r(b, ['kelimeler', 'turkce', a])) for a, b in vv.items()}
                    else:
                        y[kk] = r(vv, ['kelimeler', kk])
                ks.append(y)
            cikti[k] = ks
        elif k == 'turkce_fiil' and isinstance(v, dict):
            cikti[k] = {a: (X('S', b) if a == 'sap' else r(b, [k, a])) for a, b in v.items()}
        elif k == 'sozlukler' and isinstance(v, dict):
            cikti[k] = {a: ({c: (X('KA', e, adlar=[t.strip() for t in re.findall(r'(?:^|;\s*)([^:;]{1,30}):', e)]) if c == 'turkce' else r(e, [k, a, c])) for c, e in b.items()} if a == 'kok_anlamlari' and isinstance(b, dict) else r(b, [k, a])) for a, b in v.items()}
        else:
            cikti[k] = r(v, [k])
    return cikti


def anahtar_(tur, m, ctx):
    if tur == 'A':
        return m
    if tur == 'M':
        return 'M|' + ctx['kok'] + '|' + ctx['arapca'] + '|' + ctx['kalip']
    if tur == 'K':
        return 'K|' + ctx['kok'] + '|' + ctx['arapca'] + '|' + ctx['tip'] + '|' + ctx['sozluk_turu'] + '|' + ctx['bab'] + '|' + ctx['zaman']
    return tur + '|' + ctx['kok']


def toplama(d):
    A, U = set(), {}

    def cb(tur, m, ctx):
        if tur == 'A':
            A.add(m)
        else:
            U.setdefault(anahtar_(tur, m, ctx), (tur, ctx))
        return m
    gez(d, cb)
    return A, U


def donustur(d):
    def cb(tur, m, ctx):
        return hafiza.get(m if tur == 'A' else anahtar_(tur, m, ctx), m)
    return gez(d, cb)


def hafiza_yukle():
    os.makedirs(CIKTI, exist_ok=True)
    if os.path.exists(HAFIZA):
        for satir in open(HAFIZA, encoding='utf-8'):
            try:
                a, b = json.loads(satir)
                hafiza[a] = b
            except Exception:
                pass


SISTEM = ("Sen Arapça kök sözlüğünü Osmanlı Türkçesine (Latin harfli; Ömer Seyfettin ve Mehmed Âkif nesri, yerleşik Arapça-Fârisî asıllı kelimelerle) tercüme eden mütercimsin. "
          "Sana bir kök dosyasının kimliği (kök; İngilizce sözlük tanımları; Arapça lügat metni) ve çevrilecek öğeler verilir. Dosyayı bütün olarak gözeterek TUTARLI çevir. Öğelerde makine üretimi Türkçe karşılık YOKTUR; mânâyı Arapça kelimeden ve İngilizce/Arapça sözlük tanımlarından sen çıkar. "
          "Öğe türleri: "
          "(a) kelime_formu: Kur'ân'daki bir Arapça kelime biçimi (arapca, tür, bâb, zaman). O BİÇİMİN mânâsını (zaman, şahıs, çoğul, bitişik zamir, 've' gibi ön ekler dâhil) Osmanlı Türkçesiyle kısa bir ifadeyle yaz; farklı biçimler farklı olmalı "
          "(ör. 'sizi halk eyledi', 'halk eder', 've halk olundu', 'hâlık, halk eden'). "
          "(b) mustak_formu: kökten türeyen bir müştak (arapca, kalıp adı: masdar/ism-i fâil/ism-i mef'ûl/ism-i merre/mekân-zaman-masdar-ı mîmî/mübalağa/sıfat-ı müşebbehe…, bâb, '(dişi)' gibi). Kalıbın vazifesine uygun kısa Osmanlıca mânâ yaz: masdar 'halk eyleme', ism-i fâil 'halk eden', ism-i mef'ûl 'halk olunmuş', ism-i merre 'bir kerre halk eyleme', iki/çoğul ve dişil ekleri için 'iki halk eden', 'halk edenler', '(müennes)'. "
          "(c) fiil_sapi: kökün Türkçe fiil sapı, tek mastar (ör. 'halk eylemek'). (d) kok_anlami: 'adlar' içindeki Latin başlıklarla 'Halk: yaratmak, halk eylemek; halk: ahlâk' biçiminde kök anlamı satırı; başlıkları aynen koru, mânâları Osmanlıca yaz. "
          "(e) metin: serbest metin, sözlük maddesi, İngilizce veya Türkçe tanım, etimoloji; BİREBİR tercüme et, bariz kırık yeri düzelt, yeni bilgi ekleme. "
          "Cevaplar TÜRKÇE ifade olsun; Arapça okunuş, bilimsel işaret (ḥ ʿ) ve uydurma Arapça kalıp (mûsıl gibi) YAZMA. ⟦0⟧ gibi işaretleri, kod ve kimlikleri, özel adları, satır sonlarını aynen koru. "
          "Çıktı: öğelerle AYNI uzunlukta ve sırada yalnız bir JSON dizisi; her öğe Osmanlıca metin. JSON dışında hiçbir şey yazma.")


def sor(anahtar, model, kimlik, ogeler):
    yuk = {'dosya': kimlik, 'ogeler': ogeler}
    govde = json.dumps({'model': model, 'thinking': False, 'max_tokens': 16384, 'temperature': 0.2,
                        'messages': [{'role': 'system', 'content': SISTEM}, {'role': 'user', 'content': json.dumps(yuk, ensure_ascii=False)}]}).encode()
    for deneme in range(6):
        try:
            r = urllib.request.Request(UC, govde, {'X-API-Key': anahtar, 'Content-Type': 'application/json'})
            d = json.load(urllib.request.urlopen(r, timeout=240))
            t = d['choices'][0]['message']['content'].strip()
            o = json.loads(t[t.index('['):t.rindex(']') + 1])
            if isinstance(o, list) and len(o) == len(ogeler) and all(isinstance(x, str) for x in o):
                with kilit:
                    sayac['jeton'] += d.get('usage', {}).get('total_tokens', 0)
                    sayac['istek'] += 1
                return o
        except Exception:
            time.sleep(2 + 3 * deneme)
    with kilit:
        sayac['hata'] += 1
    return None


def kimlik_kur(d):
    s = d.get('sozlukler') or {}
    ing = []
    for e in s.get('kaikki_vikisozluk') or []:
        for g in e.get('g') or []:
            if g not in ing:
                ing.append(g)
    ar = (d.get('ses_mana_tasnif') or {}).get('mihveri', '')
    return {'kok': d.get('kok', ''), 'ingilizce_tanimlar': ing[:40], 'wordnet_dayanagi': (d.get('mana_tasnif') or {}).get('dayanak_tanim', ''), 'arapca_lugat': ar[:500]}


def cevir_dosya(anahtar, model, f, dosya_h):
    d = json.load(open(f, encoding='utf-8'))
    d.pop('osmanlica', None)
    A, U = toplama(d)
    kimlik = kimlik_kur(d)
    birim = []
    for k, (tur, c) in U.items():
        if k in hafiza:
            continue
        if tur == 'K':
            o = {'t': 'kelime_formu', 'arapca': c['arapca'], 'tur': c['sozluk_turu'], 'bab': c['bab'], 'zaman': c['zaman'], 'lemma_mi': c['tip'] == 'lemma'}
        elif tur == 'M':
            o = {'t': 'mustak_formu', 'arapca': c['arapca'], 'kalip': c['kalip']}
        elif tur == 'S':
            o = {'t': 'fiil_sapi', 'kok': c['kok']}
        else:
            o = {'t': 'kok_anlami', 'adlar': c['adlar']}
        birim.append((k, json.dumps(o, ensure_ascii=False), o))
    for m in A:
        if m not in hafiza:
            kor = koru(m)
            birim.append((m, m, {'t': 'metin', 'm': kor[0]}))
    sira = {'fiil_sapi': 0, 'kok_anlami': 0, 'kelime_formu': 1, 'mustak_formu': 2, 'metin': 3}
    birim.sort(key=lambda b: (sira[b[2]['t']], len(b[1])))
    parcalar, cur, n = [], [], 0
    for b in birim:
        if cur and (n + len(b[1]) > 20000 or len(cur) >= 120):
            parcalar.append(cur)
            cur, n = [], 0
        cur.append(b)
        n += len(b[1])
    if cur:
        parcalar.append(cur)
    for pc in parcalar:
        o = None
        for _ in range(2):
            o = sor(anahtar, model, kimlik, [b[2] for b in pc])
            if o:
                break
        if not o:
            continue
        with kilit:
            for b, y in zip(pc, o):
                if b[2]['t'] == 'metin':
                    k = koru(b[0])
                    if sorted(re.findall(r'⟦\d+⟧', y)) != sorted(re.findall(r'⟦\d+⟧', k[0])):
                        sayac['koruma_hatasi'] = sayac.get('koruma_hatasi', 0) + 1
                        continue
                    y = ac(y, k[1])
                hafiza[b[0]] = y
                dosya_h.write(json.dumps([b[0], y], ensure_ascii=False) + '\n')
            dosya_h.flush()


def tamam_mi(d):
    A, U = toplama(d)
    return all(m in hafiza for m in A) and all(k in hafiza for k in U)


def yaz(f, kume):
    d = json.load(open(f, encoding='utf-8'))
    d.pop('osmanlica', None)
    A, U = toplama(d)
    eksik = [m for m in A if m not in hafiza] + [k for k in U if k not in hafiza]
    if eksik:
        with open(os.path.join(CIKTI, '_cevrilemeyen.jsonl'), 'a', encoding='utf-8') as h:
            for m in eksik:
                h.write(json.dumps([os.path.basename(f), m], ensure_ascii=False) + '\n')
    hedef = os.path.join(CIKTI, kume, 'kokler', os.path.basename(f))
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    tmp = hedef + '.yeni'
    json.dump(guven_topla(donustur(d), d), open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, hedef)
    return True


def guven_topla(c, d):
    """Satır başına güven ve durum etiketleri dosya başına tek bölümde toplanır (padişah emri)."""
    say = collections.OrderedDict()
    for kal, rows in d.get('mustaklar', {}).items():
        for row in rows:
            if len(row) > 4 and row[4]:
                say.setdefault('müştak', collections.Counter())[row[4]] += 1
    for x in d.get('kelimeler', []):
        ld = (x.get('turkce') or {}).get('lemma_durum')
        if ld:
            say.setdefault('kelime', collections.Counter())[ld] += 1
    fg = (d.get('turkce_fiil') or {}).get('guven')
    if fg:
        say['fiil sapı'] = collections.Counter({fg: 1})
    for kal, rows in c.get('mustaklar', {}).items():
        for row in rows:
            if len(row) > 4:
                row[4] = ''
    for x in c.get('kelimeler', []):
        if isinstance(x.get('turkce'), dict) and 'lemma_durum' in x['turkce']:
            x['turkce']['lemma_durum'] = ''
    if isinstance(c.get('turkce_fiil'), dict) and 'guven' in c['turkce_fiil']:
        c['turkce_fiil']['guven'] = ''
    c['guven_etiketi'] = {k: dict(v) for k, v in say.items()}
    return c


def kok_dosyalari(kume):
    fs = glob.glob(os.path.join(GIRDI, kume, 'kokler', '*.json'))

    def gecis(f):
        try:
            return -json.load(open(f, encoding='utf-8')).get('kuran_gecisleri', 0)
        except Exception:
            return 0
    return sorted(fs, key=lambda f: (gecis(f), f))


if __name__ == '__main__':
    kume, komut = sys.argv[1], sys.argv[2]
    hafiza_yukle()
    anahtar, model = os.environ['EVREN_API_KEY'], sys.argv[3]
    dosya_h = open(HAFIZA, 'a', encoding='utf-8')
    if komut == 'tek':
        f = os.path.join(GIRDI, kume, 'kokler', sys.argv[4] + '.json')
        for _ in range(3):
            cevir_dosya(anahtar, model, f, dosya_h)
            if tamam_mi(json.load(open(f, encoding='utf-8'))):
                break
        yaz(f, kume)
        print('tamam', f, sayac, flush=True)
