import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time

KOKLER = os.environ.get('KOKLER_DIZIN') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kelime_kaydi', 'kuranda_var', 'kokler')
OPENCODE = os.path.expanduser('~/.opencode/bin/opencode')
MODEL = 'opencode/deepseek-v4.1-flash-free'
YEDEK = 'opencode/big-pickle'
SINIR = 4500
ISTEM = ('Aşağıdaki JSON dizisindeki her metni Osmanlıca, Mehmed Âkif ciddiyetinde, kurulu, yerli yerinde ve çeviri kokmayan bir Türkçeye tercüme et. '
         'Anlamı eksiltme, uydurma ekleme yapma, Arapça kelimeyi çevirmeden bırakma (ilk geçtiği yerde Arapçası parantez içinde kalabilir). '
         'Cevap olarak yalnızca aynı uzunlukta, aynı sırada bir JSON dizisi yaz; başka hiçbir şey yazma.\n\n')


def topla(j):
    liste = []
    yer = []
    for i, x in enumerate(j.get('mekayis') or []):
        for a in ('baslik', 'metin'):
            if x.get(a) and not x.get(a + '_tr'):
                liste.append(x[a]); yer.append(('mekayis', i, a))
    c = j.get('cebel')
    if c:
        for a in ('mihveri', 'sesler'):
            if c.get(a) and not c.get(a + '_tr'):
                liste.append(c[a]); yer.append(('cebel', 0, a))
    for i, x in enumerate(j.get('ontoloji') or []):
        for a in ('tanim', 'misal'):
            if x.get(a) and not x.get(a + '_tr'):
                liste.append(x[a]); yer.append(('onto', i, a))
    e = j.get('etymarab')
    if e and e.get('kok_maddesi') and not e.get('kok_maddesi_tr'):
        liste.append(e['kok_maddesi']); yer.append(('etym', 0, 'kok_maddesi'))
    for i, x in enumerate(j.get('vikisozluk') or []):
        if isinstance(x.get('anlam'), list) and not x.get('anlam_tr'):
            for k, g in enumerate(x['anlam']):
                liste.append(g); yer.append(('kaikki', i, k))
    return liste, yer


def cagir(metinler, model):
    istem = ISTEM + json.dumps(metinler, ensure_ascii=False)
    r = subprocess.run([OPENCODE, 'run', '-m', model, istem], capture_output=True, text=True, timeout=400, cwd='/tmp')
    cikti = r.stdout + r.stderr
    while 'usage limit' in cikti.lower():
        time.sleep(900)
        r = subprocess.run([OPENCODE, 'run', '-m', model, istem], capture_output=True, text=True, timeout=400, cwd='/tmp')
        cikti = r.stdout + r.stderr
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
    for (kaynak, i, a), v in zip(yer, tr):
        if kaynak == 'mekayis':
            j['mekayis'][i][a + '_tr'] = v
        elif kaynak == 'cebel':
            j['cebel'][a + '_tr'] = v
        elif kaynak == 'onto':
            j['ontoloji'][i][a + '_tr'] = v
        elif kaynak == 'etym':
            j['etymarab'][a + '_tr'] = v
        else:
            j['vikisozluk'][i].setdefault('anlam_tr', []).append(v)
    return j


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
    liste, yer = topla(j)
    if not liste:
        return ad, 'var'
    tr = cevir(liste)
    if tr is None:
        return ad, 'basarisiz'
    j2 = yaz(json.load(open(yol, encoding='utf-8')), yer, tr)
    with open(yol, 'w', encoding='utf-8') as f:
        f.write(okunur(j2))
    return ad, 'tamam'


def main():
    iscı = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    adlar = sorted(os.listdir(KOKLER), reverse=True)
    adlar = [a for a in adlar if topla(json.load(open(os.path.join(KOKLER, a), encoding='utf-8')))[0]]
    print(len(adlar), 'dosya sırada', flush=True)
    with concurrent.futures.ThreadPoolExecutor(iscı) as ex:
        for ad, d in ex.map(isle, adlar):
            print(ad, d, flush=True)


if __name__ == '__main__':
    main()
