import os, sys, gc, logging, collections

MUCIT_ROOT = "/home/user/Mucit-ai/mucit_ai_esas"
for p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if p not in sys.path:
        sys.path.insert(0, p)
logging.basicConfig(level=logging.ERROR, stream=sys.stdout)

import torch
import main_egitim_dongusu as M

_orijinal = M._tekil_egitim_adimi_icra
_sayac = {'n': 0}


def _tanit(o, derinlik=0):
    t = type(o).__name__
    if isinstance(o, dict):
        return f"dict(len={len(o)})"
    if isinstance(o, (list, tuple)):
        return f"{t}(len={len(o)})"
    return t


def _sarmal(*a, **kw):
    sonuc = _orijinal(*a, **kw)
    _sayac['n'] += 1
    if _sayac['n'] != 6:
        return sonuc
    gc.collect()
    hedefler = []
    for o in gc.get_objects():
        try:
            if isinstance(o, torch.Tensor) and tuple(o.shape) == (127, 16, 16) \
                    and o.dtype == torch.float32:
                hedefler.append(o)
        except Exception:
            pass
    print(f"\n### (127,16,16) canli tensor sayisi: {len(hedefler)}", flush=True)
    zincir = collections.Counter()
    for t in hedefler[:60]:
        for r1 in gc.get_referrers(t):
            e1 = _tanit(r1)
            for r2 in gc.get_referrers(r1):
                zincir[f"{e1}  <-  {_tanit(r2)}"] += 1
    for k, v in zincir.most_common(20):
        print(f"  {v:5d}  {k}", flush=True)

    print("\n### nesne turu sayimlari (ilgili siniflar):", flush=True)
    turler = collections.Counter()
    for o in gc.get_objects():
        try:
            ad = type(o).__name__
            if 'Laplasyen' in ad or 'Operator' in ad or 'Lif' in ad or 'E3_' in ad or 'E4_' in ad:
                turler[ad] += 1
        except Exception:
            pass
    for k, v in turler.most_common(20):
        print(f"  {v:6d}  {k}", flush=True)
    raise SystemExit(0)


M._tekil_egitim_adimi_icra = _sarmal
M.Main_EgitimYurutucu(konfig_yolu="/home/user/Mucit-ai/local_run/config.json",
                      manifest_yolu="/home/user/Mucit-ai/local_run/verisetleri_manifest.json")
