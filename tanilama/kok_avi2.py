import os, sys, gc, logging

MUCIT_ROOT = "/home/user/Mucit-ai/mucit_ai_esas"
for p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if p not in sys.path:
        sys.path.insert(0, p)
logging.basicConfig(level=logging.ERROR, stream=sys.stdout)

import torch
import main_egitim_dongusu as M
from kontratlar import E3_SinirOperatorleri

_orijinal = M._tekil_egitim_adimi_icra
_sayac = {'n': 0}


def _etiket(o):
    t = type(o)
    ad = t.__name__
    if ad == 'frame':
        return f"FRAME {o.f_code.co_name} @ {os.path.basename(o.f_code.co_filename)}:{o.f_lineno}"
    if ad == 'traceback':
        return "TRACEBACK"
    if ad == 'cell':
        return "cell"
    if ad == 'dict':
        return f"dict(len={len(o)})"
    if ad in ('list', 'tuple', 'set'):
        try:
            return f"{ad}(len={len(o)})"
        except Exception:
            return ad
    return f"{t.__module__}.{ad}"


def _sarmal(*a, **kw):
    sonuc = _orijinal(*a, **kw)
    _sayac['n'] += 1
    if _sayac['n'] != 5:
        return sonuc
    gc.collect()
    hedef = None
    for o in gc.get_objects():
        if isinstance(o, E3_SinirOperatorleri):
            hedef = o
            break
    if hedef is None:
        print("E3 bulunamadi", flush=True)
        raise SystemExit(0)

    benim_id = {id(sys._getframe()), id(sys._getframe().f_locals)}
    gorulen = {id(hedef)}
    sinir = [(hedef, [_etiket(hedef)])]
    bulunan = []
    for derinlik in range(10):
        yeni = []
        for o, yol in sinir:
            for r in gc.get_referrers(o):
                if id(r) in gorulen or id(r) in benim_id:
                    continue
                gorulen.add(id(r))
                e = _etiket(r)
                y = yol + [e]
                if e.startswith('FRAME') or e == 'TRACEBACK':
                    bulunan.append(y)
                    if len(bulunan) >= 8:
                        break
                    continue
                yeni.append((r, y))
            if len(bulunan) >= 8:
                break
        if len(bulunan) >= 8:
            break
        sinir = yeni
        if not sinir:
            break

    print(f"\n### E3 -> koke giden zincirler ({len(bulunan)} adet):", flush=True)
    for y in bulunan:
        print("   " + "\n     <- ".join(y), flush=True)
        print("   ---", flush=True)
    raise SystemExit(0)


M._tekil_egitim_adimi_icra = _sarmal
M.Main_EgitimYurutucu(konfig_yolu="/home/user/Mucit-ai/local_run/config.json",
                      manifest_yolu="/home/user/Mucit-ai/local_run/verisetleri_manifest.json")
