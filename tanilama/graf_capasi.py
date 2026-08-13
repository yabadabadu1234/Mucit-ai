import os, sys, gc, logging

MUCIT_ROOT = "/home/user/Mucit-ai/mucit_ai_esas"
for p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if p not in sys.path:
        sys.path.insert(0, p)
logging.basicConfig(level=logging.ERROR, stream=sys.stdout)

import torch
import main_egitim_dongusu as M

_orijinal = M._tekil_egitim_adimi_icra
_sayac = {'n': 0}

def _tara(kok, ad, derinlik=0, gorulen=None, cikti=None):
    if gorulen is None:
        gorulen = set()
    if cikti is None:
        cikti = []
    if derinlik > 4 or id(kok) in gorulen:
        return cikti
    gorulen.add(id(kok))
    if isinstance(kok, torch.Tensor):
        if kok.grad_fn is not None:
            cikti.append((ad, tuple(kok.shape), type(kok.grad_fn).__name__,
                          kok.element_size() * kok.numel()))
        return cikti
    if isinstance(kok, dict):
        for k, v in list(kok.items()):
            _tara(v, f"{ad}[{k!r}]", derinlik + 1, gorulen, cikti)
        return cikti
    if isinstance(kok, (list, tuple)):
        for i, v in enumerate(kok[:64]):
            _tara(v, f"{ad}[{i}]", derinlik + 1, gorulen, cikti)
        return cikti
    d = getattr(kok, '__dict__', None)
    if isinstance(d, dict):
        for k, v in list(d.items()):
            if k.startswith('__'):
                continue
            _tara(v, f"{ad}.{k}", derinlik + 1, gorulen, cikti)
    return cikti

def _sarmal(*a, **kw):
    sonuc = _orijinal(*a, **kw)
    _sayac['n'] += 1
    if _sayac['n'] != 4:
        return sonuc
    gc.collect()
    tum_moduller = kw.get('tum_moduller') or a[2]
    opt = kw.get('optimizer')
    bulgular = []
    for ad, mod in tum_moduller.items():
        bulgular += _tara(mod, f"tum_moduller[{ad!r}]")
    if opt is not None:
        bulgular += _tara(opt, "optimizer")
    print(f"\n### adim sonunda hala grad_fn tasiyan uzun omurlu tensorler: {len(bulgular)}", flush=True)
    for ad, sekil, gf, bayt in bulgular:
        print(f"  {ad}  shape={sekil}  grad_fn={gf}  {bayt/1024**2:.2f} MB", flush=True)
    raise SystemExit(0)

M._tekil_egitim_adimi_icra = _sarmal
M.Main_EgitimYurutucu(konfig_yolu="/home/user/Mucit-ai/local_run/config.json",
                      manifest_yolu="/home/user/Mucit-ai/local_run/verisetleri_manifest.json")
