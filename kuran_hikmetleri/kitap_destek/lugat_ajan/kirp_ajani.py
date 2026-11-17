import sys, os, json, re, time; sys.path.insert(0, os.path.dirname(__file__))
from madde import maddeler; from istemci import sor
MODEL = 'glm-5.3'; CIK = os.path.join(os.path.dirname(__file__), 'kirp'); os.makedirs(CIK, exist_ok=True)
ISTEM = '''Sana bir Arapça kökün klasik lügatlerdeki maddeleri TAMAMEN, numaralı olarak veriliyor. Hepsini baştan sona oku.
Senden yorum, tercüme, özet İSTENMİYOR. Yalnız şu iki cins yeri bulup, onları metinden otomatik kesecek KIRPMA KODUNU vereceksin:
 "gecis": bir mananın başka bir manaya nasıl geçtiğini, asıl manadan türemiş manaya giden yolu anlatan yerler.
 "adlandirma": bir şeye bu adın niçin verildiğini, kökün ilk hangi vakaya/nesneye ad olduğunu anlatan yerler.
Kırpma kodu: her yer için {"madde": numara, "tur": "gecis" | "adlandirma", "bas": "...", "son": "..."}.
"bas" o yerin ilk 4-8 kelimesi, "son" son 4-8 kelimesidir; ikisi de metinde HARFİ HARFİNE, harekesiyle aynen bulunmalıdır. Kesilen yer bas'ın başından son'un sonuna kadardır.
Bir yer başka yerle iç içe ise ayrı ayrı ver. Hiç yer yoksa boş liste ver.
Çıktı yalnız şu JSON'dur: {"kirpma": [ ... ]}'''
import unicodedata
AT = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0640﴿﴾()[]«»"\'')
def norm(t):
    o, ix = [], []
    for i, ch in enumerate(t):
        if ch in AT: continue
        ch = {'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ى':'ي','ة':'ه'}.get(ch, ch)
        if ch.isspace():
            if o and o[-1] == ' ': continue
            ch = ' '
        o.append(ch); ix.append(i)
    return ''.join(o), ix
def bul(t, bas, son):
    a = t.find(bas); b = t.find(son, max(a, 0))
    if a >= 0 and b >= 0: return t[a:b + len(son)]
    nt, ix = norm(t); nb = norm(bas)[0].strip(); ns = norm(son)[0].strip()
    a = nt.find(nb)
    if a < 0: return None
    b = nt.find(ns, a)
    if b < 0: return None
    return t[ix[a]:ix[b + len(ns) - 1] + 1]
def uygula(M, K):
    o = []
    for k in K:
        try:
            t = M[int(k['madde']) - 1]['metin']
            o.append(dict(k, eser=M[int(k['madde'])-1]['eser'], sayfa=M[int(k['madde'])-1]['sayfa'], metin=bul(t, k['bas'], k['son'])))
        except Exception as e: o.append(dict(k, metin=None, hata=str(e)))
    return o
def isle(kok):
    yol = os.path.join(CIK, kok + '.json')
    if os.path.exists(yol): return 'var'
    M = maddeler(kok)
    if not M: json.dump({'kok': kok, 'maddeler': 0, 'kirpma': []}, open(yol, 'w'), ensure_ascii=False); return 'maddesiz'
    girdi = '\n\n'.join(f"[MADDE {i+1}] {m['eser']} (s.{m['sayfa']})\n{m['metin']}" for i, m in enumerate(M))
    for d in range(3):
        c, f = sor(MODEL, [{'role': 'system', 'content': ISTEM}, {'role': 'user', 'content': 'KÖK: ' + kok + '\n\n' + girdi}], max_tokens=8000, sicaklik=0.1)
        m = re.search(r'\{.*\}', c, re.S)
        try: K = json.loads(m.group(0))['kirpma']; break
        except Exception: K = None
    if K is None: return 'çözülemedi'
    S = uygula(M, K)
    json.dump({'kok': kok, 'model': MODEL, 'maddeler': [{'eser': m['eser'], 'sayfa': m['sayfa']} for m in M], 'kod': K, 'kirpma': S}, open(yol, 'w'), ensure_ascii=False, indent=1)
    return f"{len(S)} yer, {sum(1 for s in S if s.get('metin'))} kesildi"
if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor
    K = sys.argv[1:] or sorted(f[:-5] for f in os.listdir('/home/user/Mucit-ai/kuran_hikmetleri/kelime_kaydi/kuranda_var/kokler') if f.endswith('.json'))
    K = [k for k in K if not os.path.exists(os.path.join(CIK, k + '.json'))]
    def tek(k):
        t = time.time()
        try: print(k, isle(k), round(time.time() - t), 's', flush=True)
        except Exception as e: print(k, 'HATA', e, flush=True)
    with ThreadPoolExecutor(int(os.environ.get('KOL', '3'))) as ex: list(ex.map(tek, K))
