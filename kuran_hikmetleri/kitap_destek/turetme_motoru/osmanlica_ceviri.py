import concurrent.futures
import glob
import json
import os
import sys
import time
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UC = 'https://evren-llmapi.ssyz.org.tr/v1/chat/completions'
SISTEM = ("Sen Türkçe metinleri Osmanlı Türkçesine (Latin harfli) çeviren mütercimsin. Her öğeyi MUTLAKA Osmanlı kelime dağarcığıyla yeniden yaz: sade Türkçe kelimelerin yerine yerleşik Arapça-Fârisî asıllı karşılıkları kullan "
          "(yıkılmak→inhidâm etmek, harâb olmak; düz→müstevî, hamvâr; Rab→Rabb, Mevlâ; efendi→seyyid, sâhib). Üslûp Ömer Seyfettin ve Mehmed Âkif nesri: canlı ve sade; mânâ eksilmez, artmaz, izah ve misal eklenmez; kelime uydurma. "
          "Arap harfi kullanma. Başta Latin harfle yazılmış Arapça kök adlarını ('Dekk:' gibi) olduğu gibi bırak. Girdi JSON'dur: {\"anlam\": metin, \"kelimeler\": [metin, ...]}; çıktı aynı şekilde yalnız JSON olsun, "
          "kelimeler öğesi sayısı ve sırası aynı kalsın, boş öğe boş kalsın.\n"
          "Örnek girdi: {\"anlam\":\"Zalem: zulmetmek, haksızlık etmek\",\"kelimeler\":[\"zulmetti\",\"zâlimler\",\"karanlık\"]}\n"
          "Örnek çıktı: {\"anlam\":\"Zalem: zulmetmek, hakkı çiğnemek\",\"kelimeler\":[\"zulmetti\",\"zâlimler\",\"zulmet, karanlık\"]}")


def sor_ham(anahtar, model, yuk):
    govde = json.dumps({'model': model, 'thinking': False, 'max_tokens': 4096, 'temperature': 0.3,
                        'messages': [{'role': 'system', 'content': SISTEM}, {'role': 'user', 'content': json.dumps(yuk, ensure_ascii=False)}]}).encode()
    for deneme in range(7):
        try:
            r = urllib.request.Request(UC, govde, {'X-API-Key': anahtar, 'Content-Type': 'application/json'})
            d = json.load(urllib.request.urlopen(r, timeout=60))
            t = d['choices'][0]['message']['content'].strip()
            o = json.loads(t[t.index('{'):t.rindex('}') + 1])
            if isinstance(o.get('kelimeler'), list) and len(o['kelimeler']) == len(yuk['kelimeler']) and isinstance(o.get('anlam'), str):
                return o
        except Exception:
            time.sleep(2 + 3 * deneme)
    return None


def sor(anahtar, model, yuk):
    ozgun = list(dict.fromkeys(x for x in yuk['kelimeler'] if x))
    sonuc = {'anlam': '', 'kelimeler': []}
    parcalar = [ozgun[i:i + 60] for i in range(0, len(ozgun), 60)] or [[]]
    esle = {}
    for n, pc in enumerate(parcalar):
        o = sor_ham(anahtar, model, {'anlam': yuk['anlam'] if n == 0 else '', 'kelimeler': pc})
        if o is None:
            return None
        if n == 0:
            sonuc['anlam'] = o['anlam']
        esle.update(dict(zip(pc, o['kelimeler'])))
    sonuc['kelimeler'] = [esle.get(x, '') if x else '' for x in yuk['kelimeler']]
    return sonuc


def kok_yukle(f):
    d = json.load(open(f, encoding='utf-8'))
    ka = (d.get('sozlukler') or {}).get('kok_anlamlari') or {}
    kel = [(k.get('turkce') or {}).get('yuzey', '') for k in d.get('kelimeler', [])]
    return d, {'anlam': ka.get('turkce', ''), 'kelimeler': kel}


def isle(anahtar, model, f):
    d, yuk = kok_yukle(f)
    if d.get('osmanlica') or not (yuk['anlam'] or any(yuk['kelimeler'])):
        return f, 'atla'
    o = sor(anahtar, model, yuk)
    if o is None:
        return f, 'hata'
    d['osmanlica'] = {'anlam': o['anlam'], 'kelimeler': o['kelimeler'], 'yontem': 'EVREN ' + model + ' ile Osmanlıcaya çevrildi (Ömer Seyfettin ve Mehmed Âkif üslûbu istemi); doğrulanmadı'}
    tmp = f + '.yeni'
    json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, f)
    return f, 'tamam'


if __name__ == '__main__':
    anahtar = os.environ['EVREN_API_KEY']
    model = sys.argv[1]
    sinir = int(sys.argv[2])
    kume = sys.argv[3] if len(sys.argv) > 3 else 'kuranda_var'
    paralel = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    dosyalar = sorted(glob.glob(os.path.join(KOK, 'kelime_kaydi', kume, 'kokler', '*.json')))[:sinir]
    say = {'tamam': 0, 'hata': 0, 'atla': 0}
    with concurrent.futures.ThreadPoolExecutor(paralel) as ex:
        for i, (f, s) in enumerate(ex.map(lambda f: isle(anahtar, model, f), dosyalar)):
            say[s] += 1
            if s == 'hata':
                print('HATA', os.path.basename(f), flush=True)
            if i % 25 == 0:
                print(i, len(dosyalar), say, flush=True)
    print('bitti', say, flush=True)
