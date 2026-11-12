import re
import numpy as np

MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
KESIMLER = (9, 45, 300)
ATLA = ('verbal noun of', 'plural of', 'active participle', 'passive participle', 'inflection', 'alternative', 'singular of', 'dual of', 'defective spelling', 'diminutive of', 'comparative', 'elative', 'form of', 'nisba')


def metinler(r):
    s = r.get('sozlukler', {})
    t = []
    ka = s.get('kok_anlamlari')
    if ka and ka.get('turkce'):
        t.append(ka['turkce'][:200])
    g = []
    for x in s.get('kaikki_vikisozluk') or []:
        for y in x.get('g', [])[:3]:
            y0 = y.strip().lower()
            if y0.startswith(ATLA) or re.match(r'.{0,25}\b(of|form) [^\s]*[؀-ۿ]', y0):
                continue
            g.append(re.sub(r'\([^)]*\)', '', y).strip())
    if g:
        t.append('; '.join(dict.fromkeys(g))[:250])
    for o in (s.get('arabic_ontology') or [])[:3]:
        if o.get('tanim'):
            t.append(o['tanim'][:200])
    c = s.get('cebel_mihveri')
    if c and c.get('mihveri'):
        t.append(c['mihveri'][:250])
    for m in (s.get('mekayis') or [])[:1]:
        m0 = m.get('metin', '')
        m0 = re.split(r'قَالَ|قَالَ|\n', m0, 1)[0] if m0 else ''
        if len(m0) > 30:
            t.append(m0[:250])
    return t


def etiket(r):
    s = r.get('sozlukler', {})
    ka = s.get('kok_anlamlari')
    if ka and ka.get('turkce'):
        return ka['turkce'][:70]
    for x in s.get('kaikki_vikisozluk') or []:
        for y in x.get('g', [])[:2]:
            if not y.lower().startswith(ATLA):
                return y[:70]
    return ''


def sinifla(kokler):
    from sentence_transformers import SentenceTransformer
    from scipy.cluster.hierarchy import linkage, fcluster
    ad, parca, sahip = [], [], []
    for k, r in kokler.items():
        t = metinler(r)
        if t:
            ad.append(k)
            for x in t:
                parca.append(x)
                sahip.append(len(ad) - 1)
    m = SentenceTransformer(MODEL)
    e = m.encode(parca, batch_size=128, normalize_embeddings=True, show_progress_bar=False)
    v = np.zeros((len(ad), e.shape[1]), dtype='float32')
    for i, j in enumerate(sahip):
        v[j] += e[i]
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    z = linkage(v, 'ward')
    et = {n: fcluster(z, n, 'maxclust') for n in KESIMLER}
    sonuc = {}
    for n in KESIMLER:
        for c in set(et[n]):
            idx = np.where(et[n] == c)[0]
            mrk = v[idx].mean(0)
            merkez = idx[int(np.argmax(v[idx] @ mrk))]
            for i in idx:
                sonuc.setdefault(ad[i], {})[n] = {'kume': int(c), 'merkez_kok': ad[merkez], 'merkez_mana': etiket(kokler[ad[merkez]]), 'boy': int(len(idx))}
    return {k: {'ust': x[KESIMLER[0]], 'orta': x[KESIMLER[1]], 'ince': x[KESIMLER[2]]} for k, x in sonuc.items()}
