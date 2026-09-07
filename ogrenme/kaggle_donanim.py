from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Dict, Optional

from matematik.geometri import tek_iplik_zorla

_TEK_IPLIK = tek_iplik_zorla()

import numpy as np

__all__ = ["ayar_sec", "kos", "BASLANGIC_HUCRESI"]


def ayar_sec(zorla: Optional[str] = None):
    from matematik.geometri import donanim
    from main.egitim import AZAMI_KAGGLE, KISA_CPU, ORTA

    tablo = {"kısa": KISA_CPU, "orta": ORTA, "azamî": AZAMI_KAGGLE}
    if zorla:
        return tablo[zorla], donanim()
    dh = donanim()
    if dh.gpu >= 2 and dh.toplam_vram >= 40.0:
        return AZAMI_KAGGLE, dh
    if dh.gpu >= 1:
        return ORTA, dh
    return KISA_CPU, dh


def kos(zorla: Optional[str] = None, cikti: Optional[str] = None,
        mukayese: bool = False) -> Dict[str, object]:
    from matematik.geometri import rapor as donanim_raporu
    from main.egitim import kulli_kayip_talimi

    ayar, dh = ayar_sec(zorla)
    print(donanim_raporu(dh), flush=True)
    print("BLAS ipliği süreç başına 1'e sabitlendi: %s" % _TEK_IPLIK,
          flush=True)
    print("seçilen ayar: %s  (satır kübiti=%d, χ=%d, çevrim=%d, örnek=%d)"
          % (ayar.ad, ayar.veri_lifi, ayar.bag, ayar.cevrim, ayar.ornek),
          flush=True)

    t0 = time.perf_counter()
    r = kulli_kayip_talimi(ayar)
    d = r["değerlendirme"]

    print("", flush=True)
    print("V(Θ): ilk %.4f → son %.4f   (%.1f sn, %d kayıp çağrısı)"
          % (r["V_ilk"], r["V_son"], r["süre_sn"], r["kayıp_çağrısı"]),
          flush=True)
    print("tam çözülen %d/%d   ilk belirteç %d/%d   hücre isabeti %.4f   "
          "sükût %d"
          % (d["tam_çözülen"], d["deneme"], d["ilk_belirteç_isabeti"],
             d["deneme"], d["ortalama_hücre_isabeti"], d["sükût"]),
          flush=True)

    if mukayese:
        print("AS-GEK mukayesesi İLGA EDİLDİ; mukayese koşulmadı.",
              flush=True)

    if cikti:
        os.makedirs(os.path.dirname(cikti) or ".", exist_ok=True)
        np.save(cikti + ".parametre.npy", r["p"])
        with open(cikti + ".olcum.json", "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in r.items()
                       if k not in ("seyir", "p")}, f,
                      ensure_ascii=False, indent=2, default=float)
        print("kaydedildi: %s.parametre.npy" % cikti, flush=True)
    r["toplam_sn"] = time.perf_counter() - t0
    return r


BASLANGIC_HUCRESI = r'''
# ── MUCİT-AI · KAGGLE BAŞLANGIÇ HÜCRESİ ─────────────────────────────
# Ayarlar → Accelerator: GPU (4×L4 varsa azamî ayar kendiliğinden seçilir)
# Ayarlar → Internet: ON  (depoyu çekmek için)

import os, sys, subprocess, textwrap

KOK = "/kaggle/working/Mucit-ai"
DAL = "claude/project-gaps-integration-ubwi2r"

if not os.path.isdir(KOK):
    subprocess.run(["git", "clone", "--depth", "1", "-b", DAL,
                    "https://github.com/yabadabadu1234/Mucit-ai.git", KOK],
                   check=True)
sys.path.insert(0, KOK)
os.chdir(KOK)

# ARC verisi depoda: idrak/veri/arc_agi_2 . Yoksa Kaggle veri kümesini
# bağlayıp aşağıdaki yolu ona çevirin.
assert os.path.isdir(os.path.join(KOK, "idrak/veri/arc_agi_2")), \
    "ARC verisi bulunamadı: idrak/veri/arc_agi_2"

# Donanımı yokla ve raporla (torch yoksa numpy yoluna düşer, yine koşar)
from matematik.geometri import rapor
print(rapor())

# ── EĞİTİM ──────────────────────────────────────────────────────────
# zorla=None  → donanıma göre kendi seçer  ("kısa" / "orta" / "azamî")
from ogrenme.kaggle_donanim import kos
netice = kos(zorla=None,
             cikti="/kaggle/working/nefs_dalga",
             mukayese=True)

# Parametreler /kaggle/working/nefs_dalga.parametre.npy dosyasındadır.
# Sonraki oturumda:  nefs.yukle(np.load(".../nefs_dalga.parametre.npy"))
# ────────────────────────────────────────────────────────────────────
'''


def _ana() -> int:
    a = argparse.ArgumentParser(description="Mucit-AI dalga eğitimi")
    a.add_argument("--ayar", choices=("kısa", "orta", "azamî"), default=None)
    a.add_argument("--cikti", default=None)
    a.add_argument("--mukayese", action="store_true")
    a.add_argument("--hucre", action="store_true",
                   help="Kaggle başlangıç hücresini yaz ve çık")
    n = a.parse_args()
    if n.hucre:
        print(BASLANGIC_HUCRESI)
        return 0
    kos(n.ayar, n.cikti, n.mukayese)
    return 0


if __name__ == "__main__":
    raise SystemExit(_ana())
