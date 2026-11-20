import concurrent.futures
import json
import os
import re
import subprocess
import sys

KOKLER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kelime_kaydi', 'kuranda_var', 'kokler')
OPENCODE = os.path.expanduser('~/.opencode/bin/opencode')
MODEL = 'opencode/deepseek-v4.1-flash-free'
YEDEK = 'opencode/big-pickle'
SINIR = 4500
ISTEM = ('Aşağıdaki JSON dizisindeki her metni Osmanlıca, Mehmed Âkif ciddiyetinde, kurulu, yerli yerinde ve çeviri kokmayan bir Türkçeye tercüme et. '
         'Anlamı eksiltme, uydurma ekleme yapma, Arapça kelimeyi çevirmeden bırakma (ilk geçtiği yerde Arapçası parantez içinde kalabilir). '
         'Cevap olarak yalnızca aynı uzunlukta, aynı sırada bir JSON dizisi yaz; başka hiçbir şey yazma.\n\n')


def topla(j):
    s = j.get('sozlukler', {})
    liste = []
    yer = []
    for i, x in enumerate(s.get('mekayis', [])):
        for a in ('baslik', 'metin'):
            if x.get(a):
                liste.append(x[a]); yer.append(('mekayis', i, a))
    c = s.get('cebel_mihveri')
    if c:
        for a in ('mihveri', 'sesler'):
            if c.get(a):
                liste.append(c[a]); yer.append(('cebel', 0, a))
    for i, x in enumerate(s.get('arabic_ontology', [])):
        for a in ('tanim', 'misal'):
            if x.get(a):
                liste.append(x[a]); yer.append(('onto', i, a))
    e = s.get('etymarab')
    if e and e.get('kok_maddesi'):
        liste.append(e['kok_maddesi']); yer.append(('etym', 0, 'kok_maddesi'))
    for i, x in enumerate(s.get('kaikki_vikisozluk', [])):
        for k, g in enumerate(x.get('g', []) if isinstance(x.get('g'), list) else []):
            liste.append(g); yer.append(('kaikki', i, k))
    return liste, yer


def cagir(metinler, model):
    istem = ISTEM + json.dumps(metinler, ensure_ascii=False)
    r = subprocess.run([OPENCODE, 'run', '-m', model, istem], capture_output=True, text=True, timeout=400, cwd='/tmp')
    cikti = r.stdout
    m = re.search(r'\[.*\]', cikti, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None
    if len(d) != len(metinler) or not all(isinstance(x, str) for x in d):
        return None
    return d


def parcala(liste):
    parcalar, mevcut, boy = [], [], 0
    for m in liste:
        if mevcut and boy + len(m) > SINIR:
            parcalar.append(mevcut); mevcut, boy = [], 0
        mevcut.append(m); boy += len(m)
    if mevcut:
        parcalar.append(mevcut)
    return parcalar


def cevir(liste):
    sonuc = []
    for p in parcala(liste):
        d = None
        for model in (MODEL, MODEL, YEDEK):
            try:
                d = cagir(p, model)
            except Exception:
                d = None
            if d:
                break
        if not d:
            return None
        sonuc += d
    return sonuc


def yaz(j, yer, tr):
    t = {}
    for (kaynak, i, a), v in zip(yer, tr):
        if kaynak == 'mekayis':
            lst = t.setdefault('mekayis', [{} for _ in j['sozlukler']['mekayis']])
            lst[i][a] = v
        elif kaynak == 'cebel':
            t.setdefault('cebel_mihveri', {})[a] = v
        elif kaynak == 'onto':
            lst = t.setdefault('arabic_ontology', [{} for _ in j['sozlukler']['arabic_ontology']])
            lst[i][a] = v
        elif kaynak == 'etym':
            t.setdefault('etymarab', {})[a] = v
        else:
            lst = t.setdefault('kaikki_vikisozluk', [{} for _ in j['sozlukler']['kaikki_vikisozluk']])
            lst[i].setdefault('g', []).append(v)
    return t


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


def isle(ad):
    yol = os.path.join(KOKLER, ad)
    j = json.load(open(yol, encoding='utf-8'))
    if 'tercume' in j.get('sozlukler', {}):
        return ad, 'var'
    liste, yer = topla(j)
    tr = cevir(liste) if liste else []
    if tr is None:
        return ad, 'basarisiz'
    j2 = json.load(open(yol, encoding='utf-8'))
    if 'tercume' in j2.get('sozlukler', {}):
        return ad, 'var'
    j2['sozlukler']['tercume'] = yaz(j2, yer, tr)
    with open(yol, 'w', encoding='utf-8') as f:
        f.write(okunur(j2))
    return ad, 'tamam'


def main():
    iscı = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    adlar = sorted(os.listdir(KOKLER), reverse=True)
    adlar = [a for a in adlar if 'tercume' not in json.load(open(os.path.join(KOKLER, a), encoding='utf-8')).get('sozlukler', {})]
    print(len(adlar), 'dosya sırada', flush=True)
    with concurrent.futures.ThreadPoolExecutor(iscı) as ex:
        for ad, d in ex.map(isle, adlar):
            print(ad, d, flush=True)


if __name__ == '__main__':
    main()
