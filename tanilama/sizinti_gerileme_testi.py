import os
import sys
import gc
import shutil
import logging
from typing import Tuple

DEPO_KOKU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUCIT_ROOT = os.path.join(DEPO_KOKU, "mucit_ai_esas")
for _p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

logging.basicConfig(level=logging.ERROR, stream=sys.stdout)

import torch

import kulli_gpu.nvme_takas_yoneticisi as takas_modulu
import main_egitim_dongusu as egitim
from kontratlar import E3_SinirOperatorleri


ILK_OLCUM_ADIMI = 2
SON_OLCUM_ADIMI = 7


def _canli_topoloji_sayisi() -> int:
    gc.collect()
    return sum(1 for o in gc.get_objects() if isinstance(o, E3_SinirOperatorleri))


def kos() -> Tuple[int, int]:





    takas_modulu.NvmeTakasYoneticisi.kapsam_muhafizi_aktifles = (
        lambda self: torch.autograd.graph.saved_tensors_hooks(
            self.pack_hook_diske_tahliye,
            self.unpack_hook_diskten_geri_cagır,
        )
    )

    for dizin in (os.path.join(DEPO_KOKU, "checkpoints"),
                  os.path.join(DEPO_KOKU, "local_run", "checkpoints")):
        shutil.rmtree(dizin, ignore_errors=True)

    olcumler = {}
    asil_adim = egitim._tekil_egitim_adimi_icra
    sayac = {"n": 0}

    def sarmal(*args, **kwargs):
        sonuc = asil_adim(*args, **kwargs)
        sayac["n"] += 1
        if sayac["n"] in (ILK_OLCUM_ADIMI, SON_OLCUM_ADIMI):
            olcumler[sayac["n"]] = _canli_topoloji_sayisi()
        if sayac["n"] >= SON_OLCUM_ADIMI:
            raise _YeterliAdim()
        return sonuc

    egitim._tekil_egitim_adimi_icra = sarmal
    try:
        egitim.Main_EgitimYurutucu(
            konfig_yolu=os.path.join(DEPO_KOKU, "local_run", "config.json"),
            manifest_yolu=os.path.join(DEPO_KOKU, "local_run", "verisetleri_manifest.json"),
        )
    except _YeterliAdim:
        pass
    finally:
        egitim._tekil_egitim_adimi_icra = asil_adim

    return olcumler.get(ILK_OLCUM_ADIMI, -1), olcumler.get(SON_OLCUM_ADIMI, -1)


class _YeterliAdim(Exception):
    pass


def main() -> int:
    ilk, son = kos()
    if ilk < 0 or son < 0:
        print("BASARISIZ: test yeterli adim kosamadi, olcum alinamadi.")
        return 1

    buyume = son - ilk
    print(f"canli E3_SinirOperatorleri: adim {ILK_OLCUM_ADIMI}={ilk}, "
          f"adim {SON_OLCUM_ADIMI}={son}, buyume={buyume}")

    if buyume > 0:
        print(
            "BASARISIZ: adim basina topoloji nesnesi birikiyor. Sebep: takas "
            "yoneticisinin saved_tensors_hooks pack kancasi tahliye etmedigi tensoru "
            "oldugu gibi donduruyor; kaydedilen tensor kendi grad_fn'ine guclu referans "
            "tutunca Python cop toplayicisinin kiramadigi bir C++ dongusu olusuyor ve "
            "her adimin checkpoint cercevesi (D0 operatoru, sinir operatorleri, "
            "aktivasyonlar) kalici olarak yasiyor. "
            "Cozum: pack kancasi tensor.detach() dondurmeli."
        )
        return 1

    print("BASARILI: adimlar arasi topoloji nesnesi birikmiyor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
