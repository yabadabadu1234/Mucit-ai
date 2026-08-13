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

def _etiket(o):
    t = type(o)
    ad = t.__name__
    if ad == 'dict':
        anahtarlar = [k for k in list(o.keys())[:6] if isinstance(k, str)]
        return f"dict(len={len(o)}, ornek_anahtar={anahtarlar})"
    if ad == 'cell':
        return "cell(closure)"
    if ad == 'frame':
        return f"frame({o.f_code.co_name} @ {os.path.basename(o.f_code.co_filename)}:{o.f_lineno})"
    if ad in ('list', 'tuple', 'set'):
        return f"{ad}(len={len(o)})"
    return f"{t.__module__}.{ad}"

def _yol_bul(nesne, azami_derinlik=6):
    gorulen = {id(nesne)}
    sinir = [(nesne, [])]
    for _ in range(azami_derinlik):
        yeni = []
        for o, yol in sinir:
            for r in gc.get_referrers(o):
                if id(r) in gorulen:
                    continue
                if isinstance(r, (type(_yol_bul), type(sys))):
                    continue
                gorulen.add(id(r))
                e = _etiket(r)
                y = yol + [e]
                if e.startswith('frame(') or 'Module' in e or 'N3_' in e or 'N6_' in e \
                        or 'N7_' in e or 'Riyazi_' in e or 'SMW' in e or 'Bellek' in e:
                    return y
                yeni.append((r, y))
        sinir = yeni
        if not sinir:
            break
    return sinir[0][1] if sinir else []

def _sarmal(*a, **kw):
    sonuc = _orijinal(*a, **kw)
    _sayac['n'] += 1
    if _sayac['n'] != 5:
        return sonuc
    gc.collect()
    ops = [o for o in gc.get_objects() if isinstance(o, LifLaplasyenOperatoru)]
    e3s = [o for o in gc.get_objects() if isinstance(o, E3_SinirOperatorleri)]
    print(f"\n### canli LifLaplasyenOperatoru: {len(ops)} | E3_SinirOperatorleri: {len(e3s)}", flush=True)
    for i, op in enumerate(ops):
        print(f"\n-- operator {i}: sahiplik zinciri", flush=True)
        for adim in _yol_bul(op):
            print(f"     <- {adim}", flush=True)
    raise SystemExit(0)

M._tekil_egitim_adimi_icra = _sarmal
M.Main_EgitimYurutucu(konfig_yolu="/home/user/Mucit-ai/local_run/config.json",
                      manifest_yolu="/home/user/Mucit-ai/local_run/verisetleri_manifest.json")
