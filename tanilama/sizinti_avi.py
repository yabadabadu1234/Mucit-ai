import os, sys, json, gc, collections, logging

MUCIT_ROOT = "/home/user/Mucit-ai/mucit_ai_esas"
for p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if p not in sys.path:
        sys.path.insert(0, p)

logging.basicConfig(level=logging.ERROR, stream=sys.stdout)

import torch
import main_egitim_dongusu as M

_orijinal = M._tekil_egitim_adimi_icra
_sayac = {'n': 0}
_gecmis = {}


def _tensor_dokumu():
    d = collections.Counter()
    bayt = collections.Counter()
    for o in gc.get_objects():
        try:
            if isinstance(o, torch.Tensor):
                anahtar = (tuple(o.shape), str(o.dtype), o.requires_grad, o.grad_fn is not None)
                d[anahtar] += 1
                bayt[anahtar] += o.element_size() * o.numel()
        except Exception:
            pass
    return d, bayt


def _sarmal(*a, **kw):
    sonuc = _orijinal(*a, **kw)
    _sayac['n'] += 1
    n = _sayac['n']
    if n in (4, 12):
        gc.collect()
        d, bayt = _tensor_dokumu()
        _gecmis[n] = (d, bayt)
        print(f"\n### adim {n}: canli tensor {sum(d.values())} adet, "
              f"{sum(bayt.values())/1024**2:.1f} MB", flush=True)
    if n == 12:
        d4, b4 = _gecmis[4]
        d12, b12 = _gecmis[12]
        artislar = []
        for k in set(d4) | set(d12):
            fark_adet = d12[k] - d4[k]
            fark_bayt = b12[k] - b4[k]
            if fark_bayt > 0:
                artislar.append((fark_bayt, fark_adet, k))
        artislar.sort(reverse=True)
        print(f"\n### 4->12 arasi buyuyen tensor gruplari (8 adim):", flush=True)
        for fb, fa, k in artislar[:15]:
            print(f"  +{fb/1024**2:8.2f} MB  +{fa:5d} adet  shape={k[0]} {k[1]} "
                  f"requires_grad={k[2]} grad_fn={k[3]}", flush=True)
        raise SystemExit(0)
    return sonuc


M._tekil_egitim_adimi_icra = _sarmal

manifest = "/home/user/Mucit-ai/local_run/verisetleri_manifest.json"
M.Main_EgitimYurutucu(konfig_yolu="/home/user/Mucit-ai/local_run/config.json",
                      manifest_yolu=manifest)
