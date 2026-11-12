import re

import numpy as np

import mana_tasnif as MT


def ilk_cumle(t, en=260):
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:en]


def prototip_ve_yayilim(r, cebel, asas):
    s = r.get('sozlukler', {})
    p = ''
    kaynak = ''
    if cebel and cebel.get('mihveri'):
        p, kaynak = ilk_cumle(cebel['mihveri']), 'Cebel mihverî mana'
    elif asas and asas.get('hakikat'):
        p, kaynak = ilk_cumle(asas['hakikat']), 'Zemahşerî hakîkat kolu'
    elif s.get('mekayis'):
        m0 = re.split(r'قَالَ|\n', s['mekayis'][0].get('metin', ''), 1)[0]
        if len(m0) > 30:
            p, kaynak = ilk_cumle(m0), 'Mekâyîs aslı'
    yay = []
    if asas and asas.get('mecaz'):
        for l in asas['mecaz'].split('\n'):
            l = l.strip()
            if len(l) >= 15 and ' ... ' not in l and not l.startswith(('قال', 'وقال', 'وأنشد', 'قد قال')):
                yay.append(l[:300])
    return p, kaynak, yay[:15]


def sinifla(kokler, cb, asas):
    from sentence_transformers import SentenceTransformer
    veri = {}
    for k, r in kokler.items():
        p, kay, yay = prototip_ve_yayilim(r, cb.get(k), asas.get(k))
        if p and yay:
            veri[k] = (p, kay, yay)
    m = SentenceTransformer(MT.MODEL)
    metinler = []
    for k, (p, kay, yay) in veri.items():
        metinler.append(p)
        metinler.extend(yay)
    e = m.encode(metinler, batch_size=128, normalize_embeddings=True, show_progress_bar=False)
    i = 0
    benzerlik = {}
    hepsi = []
    for k, (p, kay, yay) in veri.items():
        pe = e[i]
        ye = e[i + 1:i + 1 + len(yay)]
        i += 1 + len(yay)
        b = [float(x) for x in ye @ pe]
        benzerlik[k] = b
        hepsi.extend(b)
    q1, q2 = np.quantile(hepsi, [1 / 3, 2 / 3])
    sonuc = {}
    for k, (p, kay, yay) in veri.items():
        b = benzerlik[k]
        sonuc[k] = {'kaynak': 'prototip ve yayılım (radyal kategori usulü)', 'prototip_kaynagi': kay, 'prototip': p, 'yayilim_kaynagi': 'Zemahşerî mecaz kolu',
                    'yayilim': [{'cumle': c, 'prototipe_benzerlik': round(x, 3), 'halka': 'yakın' if x >= q2 else ('orta' if x >= q1 else 'uzak')} for c, x in zip(yay, b)],
                    'ortalama_benzerlik': round(float(np.mean(b)), 3), 'halka_esikleri': 'veriden: üçte bir dilimler ' + str(round(float(q1), 3)) + ' / ' + str(round(float(q2), 3))}
    return sonuc
