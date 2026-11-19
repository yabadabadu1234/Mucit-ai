"""Kapak sayfalarını mertebeli atlaslara birleştirir (F 3-I 391: veri inişi). Tek komut: python3 lugat_atlas.py (kavram_uzayi.py kendiliğinden çağırır).
Kaynak dosyalar (lugat_kapak/*.webp) aynen durur, hiçbiri silinmez; atlaslar ek bir görünümdür.
Mertebe 0: 112×159 px, atlas başına 256 hücre (16×16) · Mertebe 1: 224×318 px, atlas başına 64 hücre (8×8). Hücrenin atlas sırası = harita sırası (GP dizisinin sırası): görünür kısım birkaç atlastan gelir."""
import json, hashlib, pathlib
from concurrent.futures import ProcessPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent
KAPAK = HERE / 'lugat_kapak'; CIKTI = HERE / 'lugat_atlas'
M = [dict(w=112, h=159, c=16, r=16, q=58), dict(w=224, h=318, c=8, r=8, q=62)]
def bir(a):
    from PIL import Image
    mi, ai, liste = a; m = M[mi]; n = m['c'] * m['r']
    A = Image.new('RGB', (m['w'] * m['c'], m['h'] * m['r']), (255, 253, 246))
    for j, (no, nc) in enumerate(liste):
        if not nc: continue
        f = KAPAK / ('%d_1.webp' % no)
        if not f.exists(): continue
        im = Image.open(f).convert('RGB').resize((m['w'], m['h']), Image.LANCZOS)
        A.paste(im, ((j % m['c']) * m['w'], (j // m['c']) * m['h']))
    A.save(CIKTI / ('a%d_%d.webp' % (mi, ai)), 'WEBP', quality=m['q'], method=6)
    return mi, ai
def uret(nolar, ncler):
    CIKTI.mkdir(exist_ok=True)
    liste = list(zip(nolar, ncler)); h = hashlib.md5(json.dumps(liste).encode()).hexdigest()[:10]; mj = CIKTI / 'ATLAS.json'
    meta = {'hash': h, 'M': [dict(w=m['w'], h=m['h'], c=m['c'], r=m['r'], n=-(-len(liste) // (m['c'] * m['r']))) for m in M]}
    if mj.exists() and json.load(open(mj)).get('hash') == h and all((CIKTI / ('a%d_%d.webp' % (mi, ai))).exists() for mi in range(2) for ai in range(meta['M'][mi]['n'])): return meta
    isler = [(mi, ai, liste[ai * M[mi]['c'] * M[mi]['r']:(ai + 1) * M[mi]['c'] * M[mi]['r']]) for mi in range(2) for ai in range(meta['M'][mi]['n'])]
    with ProcessPoolExecutor(4) as ex: list(ex.map(bir, isler))
    json.dump(meta, open(mj, 'w')); return meta
