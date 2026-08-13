import os, sys, gc, logging

MUCIT_ROOT = "/home/user/Mucit-ai/mucit_ai_esas"
for p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if p not in sys.path:
        sys.path.insert(0, p)
logging.basicConfig(level=logging.ERROR, stream=sys.stdout)

import torch
import main_egitim_dongusu as M
from kontratlar import LifLaplasyenOperatoru, E3_SinirOperatorleri

_orijinal = M._tekil_egitim_adimi_icra
_sayac = {'n': 0}

def _sarmal(*a, **kw):
    sonuc = _orijinal(*a, **kw)
    _sayac['n'] += 1
    if _sayac['n'] != 5:
        return sonuc
    gc.collect()
    op_idler = set()
    for o in gc.get_objects():
        if isinstance(o, (LifLaplasyenOperatoru, E3_SinirOperatorleri)):
            op_idler.add(id(o))
    print(f"\n### canli operator/E3 nesnesi: {len(op_idler)}", flush=True)

    print("\n### bu nesneleri OZNITELIK olarak tutanlar:", flush=True)
    bulundu = 0
    for o in gc.get_objects():
        try:
            d = getattr(o, '__dict__', None)
            if not isinstance(d, dict):
                continue
            for ad, deger in list(d.items()):
                if id(deger) in op_idler:
                    print(f"  {type(o).__module__}.{type(o).__name__}.{ad}", flush=True)
                    bulundu += 1
                elif isinstance(deger, (list, tuple)) and any(id(x) in op_idler for x in deger):
                    print(f"  {type(o).__module__}.{type(o).__name__}.{ad} "
                          f"[{type(deger).__name__} icinde]", flush=True)
                    bulundu += 1
                elif isinstance(deger, dict) and any(id(x) in op_idler for x in deger.values()):
                    print(f"  {type(o).__module__}.{type(o).__name__}.{ad} [dict icinde]", flush=True)
                    bulundu += 1
        except Exception:
            pass
    if bulundu == 0:
        print("  (hicbir nesne oznitelik olarak tutmuyor)", flush=True)

    print("\n### bu nesneleri KAPANIS (closure cell) icinde tutanlar:", flush=True)
    hucreler = [o for o in gc.get_objects()
                if type(o).__name__ == 'cell' and id(getattr(o, 'cell_contents', None)) in op_idler]
    for h in hucreler:
        for r in gc.get_referrers(h):
            if hasattr(r, '__qualname__'):
                print(f"  fonksiyon: {r.__qualname__}  ({getattr(r, '__module__', '?')})", flush=True)
            elif type(r).__name__ == 'tuple':
                for rr in gc.get_referrers(r):
                    if hasattr(rr, '__qualname__'):
                        print(f"  fonksiyon(closure): {rr.__qualname__}", flush=True)
                    else:
                        print(f"  tuple <- {type(rr).__module__}.{type(rr).__name__}", flush=True)
    if not hucreler:
        print("  (kapanis yok)", flush=True)
    raise SystemExit(0)

M._tekil_egitim_adimi_icra = _sarmal
M.Main_EgitimYurutucu(konfig_yolu="/home/user/Mucit-ai/local_run/config.json",
                      manifest_yolu="/home/user/Mucit-ai/local_run/verisetleri_manifest.json")
