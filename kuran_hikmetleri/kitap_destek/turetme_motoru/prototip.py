import re

import numpy as np

import mana_tasnif as MT

PARCA = 350


def prototipler(r, cebel, asas):
    s = r.get('sozlukler', {})
    p = []
    if cebel and cebel.get('mihveri'):
        p.append({'kaynak': 'Cebel mihverî mana', 'metin': cebel['mihveri']})
    if asas and asas.get('hakikat'):
        p.append({'kaynak': 'Zemahşerî hakîkat kolu', 'metin': asas['hakikat']})
    for m in s.get('mekayis') or []:
        if m.get('metin'):
            p.append({'kaynak': 'Mekâyîs: ' + m.get('baslik', ''), 'metin': m['metin']})
    return p


def yayilimlar(asas):
    y = []
    if asas:
        for kol, ad in (('mecaz', 'Zemahşerî mecaz kolu'), ('kinaye', 'Zemahşerî kinâye kolu')):
            for l in asas.get(kol, '').split('\n'):
                l = l.strip()
                if l:
                    y.append({'kaynak': ad, 'metin': l})
    return y


def parcala(t):
    t = re.sub(r'\s+', ' ', t).strip()
    return [t[i:i + PARCA] for i in range(0, len(t), PARCA)] or ['']


def sinifla(kokler, cb, asas):
    from sentence_transformers import SentenceTransformer
    veri = {}
    for k, r in kokler.items():
        p = prototipler(r, cb.get(k), asas.get(k))
        y = yayilimlar(asas.get(k))
        if p and y:
            veri[k] = (p, y)
    metinler = []
    sinir = []
    for k, (p, y) in veri.items():
        for x in p + y:
            ps = parcala(x['metin'])
            sinir.append((len(metinler), len(metinler) + len(ps)))
            metinler.extend(ps)
    m = SentenceTransformer(MT.MODEL)
    e = m.encode(metinler, batch_size=128, normalize_embeddings=True, show_progress_bar=False)
    i = 0
    vek = {}
    for k, (p, y) in veri.items():
        v = []
        for _ in p + y:
            a, b = sinir[i]
            i += 1
            u = e[a:b].mean(0)
            v.append(u / np.linalg.norm(u))
        vek[k] = v
    benz = {}
    hepsi = []
    for k, (p, y) in veri.items():
        v = vek[k]
        pv = v[0]
        b = [float(x @ pv) for x in v[len(p):]]
        benz[k] = b
        hepsi.extend(b)
    q1, q2 = np.quantile(hepsi, [1 / 3, 2 / 3])
    sonuc = {}
    for k, (p, y) in veri.items():
        b = benz[k]
        sonuc[k] = {'kaynak': 'prototip ve yayılım (radyal kategori usulü); bütün prototip kaynakları ve bütün mecaz/kinâye satırları',
                    'prototipler': p, 'karsilastirma_prototipi': p[0]['kaynak'],
                    'yayilim': [dict(x, prototipe_benzerlik=round(s, 3), halka='yakın' if s >= q2 else ('orta' if s >= q1 else 'uzak')) for x, s in zip(y, b)],
                    'ortalama_benzerlik': round(float(np.mean(b)), 3),
                    'halka_esikleri': 'veriden: üçte bir dilimler ' + str(round(float(q1), 3)) + ' / ' + str(round(float(q2), 3)) + '; uzun metinler 350 karakterlik parçalara bölünüp vektörleri ortalandı, metin kesilmedi'}
    return sonuc
