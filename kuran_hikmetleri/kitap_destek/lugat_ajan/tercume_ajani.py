import sys, os, json, re, time; sys.path.insert(0, os.path.dirname(__file__))
from madde import maddeler; from istemci import sor
MODEL = os.environ.get('TERCUME_MODEL', 'deepseek-v4.1-flash'); CIK = os.path.join(os.path.dirname(__file__), 'tercume'); os.makedirs(CIK, exist_ok=True)
ISTEM = '''Sen klasik Arap lügatini Türkçeye çeviren bir mütercimsin. Sana verilen Arapça lügat metninin TAMAMINI Türkçeye çevir.
Kaideler:
- Bütün nesir cümleleri Türkçe olacak; Arapça cümle bırakmak yasaktır.
- Atlama, özetleme, yorum katma yok; her cümle, her râvi ve âlim adı, her izah sırasıyla çevrilir.
- Lügat kalıpları (meselâ نَفَاهُ يَنْفِيهِ نَفْيًا) Arapça harekeli bırakılabilir, fakat içinde bulundukları cümle Türkçe kurulur ve kalıbın yanına Latin harfli okunuşu ile manası yazılır. Râvi, âlim ve eser adları Türkçe harfle yazılır.
- Şiir beyitleri ve âyetler Arapça aynen bırakılır, ardından köşeli parantez içinde Türkçesi yazılır.
- Lügat terimlerinde yerleşmiş Osmanlıca karşılıklar kullanılır.
Yalnız tercümeyi yaz.'''
def parcala(t, n=5000):
    o, b = [], ''
    for s in re.split(r'(?<=[.\n:؛])', t):
        if len(b) + len(s) > n and b: o.append(b); b = ''
        b += s
    if b: o.append(b)
    return o
def isle(kok):
    yol = os.path.join(CIK, kok + '.json')
    D = json.load(open(yol)) if os.path.exists(yol) else {'kok': kok, 'model': MODEL, 'maddeler': []}
    M = maddeler(kok)
    if not D['maddeler']: D['maddeler'] = [{'eser': m['eser'], 'sayfa': m['sayfa'], 'parcalar': [[p, None] for p in parcala(m['metin'].replace('﴿', '').replace('﴾', ''))]} for m in M]
    for m in D['maddeler']:
        for p in m['parcalar']:
            if p[1] is None:
                p[1], _ = sor(MODEL, [{'role': 'system', 'content': ISTEM}, {'role': 'user', 'content': p[0]}], max_tokens=12000, devam=True)
                json.dump(D, open(yol + '.tmp', 'w'), ensure_ascii=False); os.replace(yol + '.tmp', yol)
    D['tamam'] = True; json.dump(D, open(yol, 'w'), ensure_ascii=False, indent=1)
    return sum(len(m['parcalar']) for m in D['maddeler'])
if __name__ == '__main__':
    K = sys.argv[1:] or sorted(f[:-5] for f in os.listdir('/home/user/Mucit-ai/kuran_hikmetleri/kelime_kaydi/kuranda_var/kokler') if f.endswith('.json'))
    for k in K:
        y = os.path.join(CIK, k + '.json')
        if os.path.exists(y) and json.load(open(y)).get('tamam'): continue
        t = time.time(); print(k, isle(k), 'parça', round(time.time() - t), 's', flush=True)
