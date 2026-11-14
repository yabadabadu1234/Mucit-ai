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
    """Kök dosyasını dolaşır; her çevrilecek metin için cb(tur, metin, bağlam) çağrılır, dönüşü yerine konur.
    tur 'A': bağlamsız metin; tur 'B': kök bağlamında Türkçe karşılık (düzeltilerek çevrilir)."""
    kok = d.get('kok', '')
    ka = (d.get('sozlukler') or {}).get('kok_anlamlari') or {}
    k0 = {'kok': kok, 'kok_anlami': ka.get('turkce', ''), 'fiil_sapi': (d.get('turkce_fiil') or {}).get('sap', '')}

    def B(m, ek):
        return cb('B', m, dict(k0, **ek)) if isinstance(m, str) and m.strip() else m

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
            cikti[k] = {kal: [[(B(x, {'tur': 'müştak', 'kalip': kal, 'arapca': row[1] if len(row) > 1 else ''}) if i == 3 else (r(x, ['mustaklar']) if isinstance(x, str) and i not in (2, 4) else x)) for i, x in enumerate(row)] for row in rows] for kal, rows in v.items()}
        elif k == 'kelimeler':
            ks = []
            for x in v:
                y = {}
                for kk, vv in x.items():
                    if kk == 'turkce' and isinstance(vv, dict):
                        y[kk] = {a: (B(b, {'tur': 'kelime', 'arapca': x.get('kelime', '') + ' (' + x.get('lemma', '') + ')', 'sozluk_turu': x.get('tur', '')}) if a in ('yuzey', 'lemma') else r(b, ['kelimeler', 'turkce', a])) for a, b in vv.items()}
                    else:
                        y[kk] = r(vv, ['kelimeler', kk])
                ks.append(y)
            cikti[k] = ks
        elif k == 'turkce_fiil' and isinstance(v, dict):
            cikti[k] = {a: (B(b, {'tur': 'fiil sapı'}) if a == 'sap' else r(b, [k, a])) for a, b in v.items()}
        elif k == 'sozlukler' and isinstance(v, dict):
            cikti[k] = {a: ({c: (B(e, {'tur': 'kök anlamı'}) if c == 'turkce' else r(e, [k, a, c])) for c, e in b.items()} if a == 'kok_anlamlari' and isinstance(b, dict) else r(b, [k, a])) for a, b in v.items()}
        else:
            cikti[k] = r(v, [k])
    return cikti


def metin_topla_d(d, A, Bk):
    def cb(tur, m, ctx):
        if tur == 'A':
            A.add(m)
        else:
            Bk.setdefault(ctx['kok'], {}).setdefault(m, ctx)
        return m
    gez(d, cb)


def donustur(d):
    def cb(tur, m, ctx):
        if tur == 'A':
            return hafiza.get(m, m)
        return hafiza.get('B|' + ctx['kok'] + '|' + m, m)
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


def sor(anahtar, model, grup):
    govde = json.dumps({'model': model, 'thinking': False, 'max_tokens': 8192, 'temperature': 0.2,
                        'messages': [{'role': 'system', 'content': SISTEM}, {'role': 'user', 'content': json.dumps(grup, ensure_ascii=False)}]}).encode()
    for deneme in range(6):
        try:
            r = urllib.request.Request(UC, govde, {'X-API-Key': anahtar, 'Content-Type': 'application/json'})
            d = json.load(urllib.request.urlopen(r, timeout=90))
            t = d['choices'][0]['message']['content'].strip()
            o = json.loads(t[t.index('['):t.rindex(']') + 1])
            if isinstance(o, list) and len(o) == len(grup) and all(isinstance(x, str) for x in o):
                with kilit:
                    sayac['jeton'] += d.get('usage', {}).get('total_tokens', 0)
                    sayac['istek'] += 1
                return o
        except Exception as e:
            if 'daily' in str(e).lower() or '429' in str(e):
                time.sleep(20)
            time.sleep(2 + 3 * deneme)
    with kilit:
        sayac['hata'] += 1
    return None


def grupla(metinler, sinir=6000):
    gr, cur, n = [], [], 0
    for m in sorted(metinler, key=len):
        if cur and (n + len(m) > sinir or len(cur) >= 60):
            gr.append(cur)
            cur, n = [], 0
        cur.append(m)
        n += len(m)
    if cur:
        gr.append(cur)
    return gr


def cevir_metinler(anahtar, model, metinler, paralel):
    gerek = [m for m in metinler if m not in hafiza]
    korunmus = {m: koru(m) for m in gerek}
    gr = grupla([korunmus[m][0] for m in gerek])
    ters = collections.defaultdict(list)
    for m in gerek:
        ters[korunmus[m][0]].append(m)
    dosya = open(HAFIZA, 'a', encoding='utf-8')

    def is_(g):
        o = sor(anahtar, model, g)
        if o is None and len(g) > 1:
            o = []
            for m in g:
                x = sor(anahtar, model, [m])
                o.append(x[0] if x else None)
            return g, o
        return g, o

    bitti = 0
    with concurrent.futures.ThreadPoolExecutor(paralel) as ex:
        for g, o in ex.map(is_, gr):
            if o:
                with kilit:
                    for a, b in zip(g, o):
                        if b is None:
                            continue
                        for m in ters[a]:
                            pc = korunmus[m][1]
                            if sorted(re.findall(r'⟦\d+⟧', b)) != sorted(re.findall(r'⟦\d+⟧', a)):
                                sayac['koruma_hatasi'] = sayac.get('koruma_hatasi', 0) + 1
                                continue
                            c = ac(b, pc)
                            hafiza[m] = c
                            dosya.write(json.dumps([m, c], ensure_ascii=False) + '\n')
                    dosya.flush()
            bitti += 1
            if bitti % 20 == 0:
                print('grup', bitti, len(gr), 'hafıza', len(hafiza), sayac, flush=True)
    dosya.close()


def kok_dosyalari(kume):
    fs = glob.glob(os.path.join(GIRDI, kume, 'kokler', '*.json'))

    def gecis(f):
        try:
            return -json.load(open(f, encoding='utf-8')).get('kuran_gecisleri', 0)
        except Exception:
            return 0
    return sorted(fs, key=lambda f: (gecis(f), f))


SISTEM_B = ("Sen Arapça kök sözlüğünün Türkçe karşılıklarını Osmanlı Türkçesine (Latin harfli; Ömer Seyfettin ve Mehmed Âkif nesri, yerleşik Arapça-Fârisî asıllı kelimelerle) tercüme eden mütercimsin. "
            "Girdi bir köke bağlı satırlardır: kök, kökün mânâsı, fiil sapı ve her satır için Arapça kelime, kalıp adı ve makine üretimi Türkçe karşılık. "
            "GÖREV: her 'turkce' satırını AYNI MÂNÂ ve AYNI DİLBİLGİSİ VAZİFESİYLE Osmanlıcaya çevir. Satır bir fâil ise fâil, mef'ûl ise mef'ûl, masdar ise masdar mânâsı verir: "
            "'ayağa kalktıran' → 'ayağa kaldıran' (kıyâm ettiren); 'terbiye edilme' → 'terbiye olunma'. Satırı Arapça kelimenin kendisiyle DEĞİŞTİRME (ör. 'ayağa kalktıran' için 'Müstakîm' yazma); "
            "yalnız sade Türkçe kelimeleri yerleşik Osmanlı karşılığıyla değiştir, cümle kuruluşunu koru. "
            "TASHİH: Türkçe satır makine üretimidir; açıkça bozuk, mânâsız veya var olmayan Türkçe kelime ihtiva ediyorsa (ör. 'ayağa kalklaşan', 'terbiye etleşme', isim kökten 'yeryüzü olunmuş') "
            "kökün mânâsına ve Arapça kelimeye bakarak yalnız o kısmı düzelt; bozuk olmayanı değiştirme. Aynı kökün bütün satırlarında kök mânâsı için hep aynı Osmanlıca kelimeyi kullan (tutarlılık). "
            "'(dişi)' → '(müennes)', '(yeri/zamanı)' → '(mekânı/zamanı)' gibi ek parantezleri tercüme et ve koru. Yeni bilgi, izah veya not ekleme. ⟦0⟧ gibi işaretleri aynen koru. "
            "Girdi: {\"kok\":..., \"kok_anlami\":..., \"fiil_sapi\":..., \"satirlar\":[{\"arapca\":..., \"kalip\":..., \"turkce\":...}]}. Çıktı: satırlarla AYNI uzunlukta ve sırada yalnız bir JSON dizisi (her öğe Osmanlıca metin). JSON dışında hiçbir şey yazma.")


def sor_b(anahtar, model, kok, ctx0, satirlar):
    yuk = {'kok': kok, 'kok_anlami': ctx0['kok_anlami'], 'fiil_sapi': ctx0['fiil_sapi'], 'satirlar': satirlar}
    govde = json.dumps({'model': model, 'thinking': False, 'max_tokens': 8192, 'temperature': 0.2,
                        'messages': [{'role': 'system', 'content': SISTEM_B}, {'role': 'user', 'content': json.dumps(yuk, ensure_ascii=False)}]}).encode()
    for deneme in range(6):
        try:
            r = urllib.request.Request(UC, govde, {'X-API-Key': anahtar, 'Content-Type': 'application/json'})
            d = json.load(urllib.request.urlopen(r, timeout=90))
            t = d['choices'][0]['message']['content'].strip()
            o = json.loads(t[t.index('['):t.rindex(']') + 1])
            if isinstance(o, list) and len(o) == len(satirlar) and all(isinstance(x, str) for x in o):
                with kilit:
                    sayac['jeton'] += d.get('usage', {}).get('total_tokens', 0)
                    sayac['istek'] += 1
                return o
        except Exception:
            time.sleep(2 + 3 * deneme)
    with kilit:
        sayac['hata'] += 1
    return None


def cevir_b(anahtar, model, Bk, paralel):
    isler = []
    for kok, d in Bk.items():
        gerek = [(m, c) for m, c in d.items() if 'B|' + kok + '|' + m not in hafiza]
        for i in range(0, len(gerek), 60):
            isler.append((kok, gerek[i:i + 60]))
    dosya = open(HAFIZA, 'a', encoding='utf-8')

    def is_(j):
        kok, parca = j
        kor = [koru(m) for m, _ in parca]
        satir = [{'arapca': c.get('arapca', ''), 'kalip': c.get('kalip', c.get('tur', '')), 'turkce': k[0]} for (m, c), k in zip(parca, kor)]
        return j, kor, sor_b(anahtar, model, kok, parca[0][1], satir)

    with concurrent.futures.ThreadPoolExecutor(paralel) as ex:
        for (kok, parca), kor, o in ex.map(is_, isler):
            if not o:
                continue
            with kilit:
                for (m, _), k, b in zip(parca, kor, o):
                    if sorted(re.findall(r'⟦\d+⟧', b)) != sorted(re.findall(r'⟦\d+⟧', k[0])):
                        sayac['koruma_hatasi'] = sayac.get('koruma_hatasi', 0) + 1
                        continue
                    c = ac(b, k[1])
                    hafiza['B|' + kok + '|' + m] = c
                    dosya.write(json.dumps(['B|' + kok + '|' + m, c], ensure_ascii=False) + '\n')
                dosya.flush()
    dosya.close()


def guven_topla(c, d):
    """Satır başına güven ve durum etiketlerini dosya başına tek yerde toplar (padişah emri); satırlardaki etiket boşaltılır."""
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


def yaz(f, kume):
    d = json.load(open(f, encoding='utf-8'))
    d.pop('osmanlica', None)
    A, Bk = set(), {}
    metin_topla_d(d, A, Bk)
    eksik = [m for m in A if m not in hafiza] + ['B|' + k + '|' + m for k, x in Bk.items() for m in x if 'B|' + k + '|' + m not in hafiza]
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


def topla(dosyalar):
    A, Bk = set(), {}
    for f in dosyalar:
        d = json.load(open(f, encoding='utf-8'))
        d.pop('osmanlica', None)
        metin_topla_d(d, A, Bk)
    return A, Bk


SISTEM_C = ("Sen bir Arapça kök sözlük dosyasını Osmanlı Türkçesine (Latin harfli; Ömer Seyfettin ve Mehmed Âkif nesri, yerleşik Arapça-Fârisî asıllı kelimelerle) tercüme eden ve aynı anda tashih eden mütercimsin. "
            "Sana bir kök dosyasının TÜM çevrilecek metinleri verilir: önce dosyanın kimliği (kök, kökün mânâsı, fiil sapı), sonra öğeler. Dosyayı bütün olarak gözeterek tutarlı çevir: aynı kök mânâsı için hep aynı Osmanlıca kelime. "
            "İki tür öğe vardır. (1) {\"t\":\"karsilik\",...}: kelimenin makine üretimi TÜRKÇE karşılığı. Çıktı yine bir TÜRKÇE İFADE olmalı: aynı cümle yapısı, aynı mânâ, aynı dilbilgisi vazifesi (fâil/mef'ûl/masdar); yalnız tek tek sade Türkçe kelimeleri yerleşik Osmanlı karşılığıyla değiştir. "
            "ASLA tek başına bir Arapça kelime, Arapça okunuş veya kelimenin Arapçası döndürme (ör. 'yaratma' için 'halk' DEĞİL 'halk eyleme'; 'yaratan' için 'muhallik' DEĞİL 'halk eden'; 'bir kere yaratma' için 'tehlîke' DEĞİL 'bir kerre halk eyleme'). "
            "Örnekler: 'geldi, verdi'→'geldi, verdi' veya 'vürûd eyledi, i'tâ eyledi'; 'gelme'→'gelme, vürûd'; 'getirme'→'getirme, îsâl'; 'getiren'→'getiren, îsâl eden'; 'nun harfi'→'nûn harfi'; 'yarattı'→'halk eyledi'; 'yaratılmış (dişi)'→'halk olunmuş (müennes)'; 'ayağa kalkan'→'ayağa kalkan, kıyâm eden'; 'terbiye edilme'→'terbiye olunma'. "
            "açıkça bozuk, mânâsız veya var olmayan Türkçe kelime (ör. 'ayağa kalklaşan', isim kökten 'yeryüzü olunmuş') varsa kökün mânâsına ve Arapça kelimeye bakıp yalnız o kısmı düzelt; '(dişi)'→'(müennes)', '(yeri/zamanı)'→'(mekânı/zamanı)'. "
            "(2) {\"t\":\"metin\",\"m\":...}: serbest metin, sözlük maddesi, İngilizce veya Türkçe tanım, etimoloji; BİREBİR tercüme et, kaynakta bariz kırık veya yanlış olan kelime ve cümleyi düzelt, yeni bilgi ve izah ekleme. "
            "DEĞİŞTİRME: ⟦0⟧ gibi işaretleri aynen koru, kod ve kimlikleri, bâb numaralarını, özel adları, satır sonlarını (\\n), Markdown işaretlerini. "
            "Çıktı: öğelerle AYNI uzunlukta ve sırada yalnız bir JSON dizisi; her öğe Osmanlıca metin. JSON dışında hiçbir şey yazma.")


def sor_c(anahtar, model, kimlik, ogeler):
    yuk = {'dosya': kimlik, 'ogeler': ogeler}
    govde = json.dumps({'model': model, 'thinking': False, 'max_tokens': 16384, 'temperature': 0.2,
                        'messages': [{'role': 'system', 'content': SISTEM_C}, {'role': 'user', 'content': json.dumps(yuk, ensure_ascii=False)}]}).encode()
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


def cevir_dosya(anahtar, model, f, dosya_h):
    d = json.load(open(f, encoding='utf-8'))
    d.pop('osmanlica', None)
    A, Bk = set(), {}
    metin_topla_d(d, A, Bk)
    kok = d.get('kok', '')
    kimlik = {'kok': kok, 'kok_anlami': (d.get('sozlukler', {}).get('kok_anlamlari') or {}).get('turkce', ''), 'fiil_sapi': (d.get('turkce_fiil') or {}).get('sap', ''),
              }
    birim = []
    for m, c in Bk.get(kok, {}).items():
        if 'B|' + kok + '|' + m not in hafiza:
            birim.append(('B|' + kok + '|' + m, m, {'t': 'karsilik', 'kalip': c.get('kalip', c.get('tur', '')), 'turkce': None}))
    for m in A:
        if m not in hafiza:
            birim.append((m, m, {'t': 'metin', 'm': None}))
    birim.sort(key=lambda b: (b[2]['t'] != 'karsilik', len(b[1])))
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
        kor = [koru(b[1]) for b in pc]
        ogeler = []
        for b, k in zip(pc, kor):
            o = dict(b[2])
            if o['t'] == 'karsilik':
                o['turkce'] = k[0]
            else:
                o['m'] = k[0]
            ogeler.append(o)
        o = None
        for _ in range(2):
            o = sor_c(anahtar, model, kimlik, ogeler)
            if o:
                break
        if not o:
            continue
        with kilit:
            for b, k, y in zip(pc, kor, o):
                if sorted(re.findall(r'⟦\d+⟧', y)) != sorted(re.findall(r'⟦\d+⟧', k[0])):
                    sayac['koruma_hatasi'] = sayac.get('koruma_hatasi', 0) + 1
                    continue
                c = ac(y, k[1])
                hafiza[b[0]] = c
                dosya_h.write(json.dumps([b[0], c], ensure_ascii=False) + '\n')
            dosya_h.flush()


if __name__ == '__main__':
    kume, komut = sys.argv[1], sys.argv[2]
    hafiza_yukle()
    dosyalar = kok_dosyalari(kume)
    if komut == 'say':
        A, Bk = topla(dosyalar)
        print(kume, len(dosyalar), 'A', len(A), sum(len(x) for x in A), 'B', sum(len(x) for x in Bk.values()))
    else:
        anahtar, model, paralel = os.environ['EVREN_API_KEY'], sys.argv[3], int(sys.argv[4])
        dosya_h = open(HAFIZA, 'a', encoding='utf-8')

        def is_(f):
            for _ in range(3):
                cevir_dosya(anahtar, model, f, dosya_h)
                A, Bk = topla([f])
                if all(m in hafiza for m in A) and all('B|' + k + '|' + m in hafiza for k, x in Bk.items() for m in x):
                    break
            yaz(f, kume)
            return f

        bitti = 0
        with concurrent.futures.ThreadPoolExecutor(paralel) as ex:
            for f in ex.map(is_, dosyalar):
                bitti += 1
                if bitti % 5 == 0:
                    print('DOSYA', bitti, len(dosyalar), sayac, flush=True)
        print('bitti', sayac, flush=True)
