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
