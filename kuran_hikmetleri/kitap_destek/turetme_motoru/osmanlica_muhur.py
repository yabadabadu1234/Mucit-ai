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


def yuru(o, yol, cikti):
    if isinstance(o, dict):
        for k, v in o.items():
            yuru(v, yol + [k], cikti)
    elif isinstance(o, list):
        for v in o:
            yuru(v, yol, cikti)
    elif isinstance(o, str):
        if cevrilir(yol, o):
            cikti.add(o)


def donustur(o, yol):
    if isinstance(o, dict):
        return {k: donustur(v, yol + [k]) for k, v in o.items()}
    if isinstance(o, list):
        return [donustur(v, yol) for v in o]
    if isinstance(o, str) and cevrilir(yol, o):
        return hafiza.get(o, o)
    return o


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


def yaz(f, kume):
    d = json.load(open(f, encoding='utf-8'))
    d.pop('osmanlica', None)
    gerek = set()
    yuru(d, [], gerek)
    eksik = [m for m in gerek if m not in hafiza]
    if eksik:
        with open(os.path.join(CIKTI, '_cevrilemeyen.jsonl'), 'a', encoding='utf-8') as h:
            for m in eksik:
                h.write(json.dumps([os.path.basename(f), m], ensure_ascii=False) + '\n')
    hedef = os.path.join(CIKTI, kume, 'kokler', os.path.basename(f))
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    tmp = hedef + '.yeni'
    json.dump(donustur(d, []), open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, hedef)
    return True


def metin_topla(dosyalar):
    t = set()
    for f in dosyalar:
        d = json.load(open(f, encoding='utf-8'))
        d.pop('osmanlica', None)
        yuru(d, [], t)
    return t


if __name__ == '__main__':
    kume, komut = sys.argv[1], sys.argv[2]
    hafiza_yukle()
    dosyalar = kok_dosyalari(kume)
    if komut == 'say':
        t = metin_topla(dosyalar)
        print(kume, len(dosyalar), 'dosya; benzersiz metin', len(t), 'karakter', sum(len(x) for x in t), 'hafızada', sum(1 for x in t if x in hafiza))
    else:
        anahtar, model, paralel, parti = os.environ['EVREN_API_KEY'], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
        i = 0
        while i < len(dosyalar):
            dilim = dosyalar[i:i + parti]
            tm = metin_topla(dilim)
            for _ in range(3):
                cevir_metinler(anahtar, model, tm, paralel)
                if all(m in hafiza for m in tm):
                    break
            ok = sum(1 for f in dilim if yaz(f, kume))
            i += parti
            print('DOSYA', i, len(dosyalar), 'yazılan', ok, sayac, flush=True)
        print('bitti', sayac, flush=True)
