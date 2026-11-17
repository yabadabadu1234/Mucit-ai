import pyarrow.parquet as pq, re, collections, functools
P = '/home/user/Mucit-ai/kaynak/ham/islamlab/train.parquet'
W = {'مقاييس': 'معجم مقاييس اللغة', 'تاج': 'تاج العروس من جواهر القاموس', 'صحاح': 'الصحاح تاج اللغة وصحاح العربية'}
H = re.compile('[ً-ْٰـ]')
def n(s): return H.sub('', s or '').replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ء','ا').replace('ؤ','ا').replace('ئ','ا').replace(' ', '').strip()
@functools.lru_cache(1)
def dizin():
    t = pq.read_table(P, columns=['title_ar','headword','root','text','page_start']).to_pylist(); I = collections.defaultdict(list)
    for r in t:
        for k, w in W.items():
            if r['title_ar'] == w:
                for x in {r['root'], r['headword']}:
                    if x: I[(k, n(re.sub(r'^(مادة|باب|فصل)\s*', '', x)))].append(r)
    return I
def maddeler(kok):
    I = dizin(); o = []
    for k in W:
        for r in I.get((k, n(kok)), [])[:3]: o.append({'eser': W[k], 'sayfa': r['page_start'], 'metin': r['text']})
    return o
import sys as _s, os as _o
_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..', 'turetme_motoru'))
@functools.lru_cache(1)
def _cebel():
    import cebel; return cebel.yukle()
_eski = maddeler
def maddeler(kok):
    o = _eski(kok); C = _cebel()
    for k in (kok, kok.replace('ي', 'ى'), kok.replace('ى', 'ي'), kok.replace('ا', 'ء')):
        if k in C:
            o.append({'eser': "المعجم الاشتقاقي المؤصل (محمد حسن جبل)", 'sayfa': None, 'metin': (C[k]['fasil_ozeti'] + '\n\n' if C[k]['fasil_ozeti'] else '') + C[k]['tam_metin']}); break
    return o
