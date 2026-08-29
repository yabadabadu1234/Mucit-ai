"""
Kaggle koşucusu: tek hücrelik başlangıç, çok cihazlı eğitim.

Kullanıcı şartı iki katlıdır ve ikisi de burada karşılanır:

1. *"Kaggle'a, yani gerçek 21×4 = 84 GB GPU'ya paralel çalışacak şekilde
   hazırla; eğitimi başlatabilmem için hücreye yazacağım bir başlangıç
   kodu istiyorum."*
2. *"Sen GPU tarafındaki çalışırlığı garanti edemezsin ama en azından
   CPU'da eğitimin çok kısa hâli çalışabilmeli."*

Onun için burada **tek** giriş noktası vardır ve donanımı kendisi
yoklar: GPU varsa ``AZAMI_KAGGLE`` ayarına, yoksa ``KISA_CPU``ya düşer.
İkisi de aynı koddur; fark yalnız ölçülerdedir.

**Paralellik nasıl kuruldu.** Gradyan olmadığı için (kütük H3) cihazlar
arası ``all_reduce`` **yoktur**. Bölünen şey iştir:

* **Kübit ileri geçişi** -- ``ℒ_Nefs(Θ)``, ``Θ`` başına bağımsızdır;
  süreçlere bölünür (``multiprocessing``). CPU çekirdeği kadar.
* **NQS genlik hesabı ve örnekleme** -- yığın hâlindedir ve cihazlara
  bölünür (``hesap/donanim.topla_paralel``). GPU başına bir dilim.
* **Grover özyinelemesi** -- ``k+1`` sayı üzerindedir; bölünmez, zaten
  bedavadır.

**84 GB nereye gidiyor?** Doğru cevap: **çoğu boşta kalır** ve bu bir
kusur değil, mimarînin neticesidir. ``2^N`` hiçbir yerde açılmaz; NQS
parametreleri megabaytlar, Grover katsayıları kilobaytlar tutar. VRAM'i
tüketen tek şey yığın büyüklüğüdür (``ornek``, ``zincir``). Onun için
``AZAMI_KAGGLE`` ayarında büyütülen şey belleğe sığdırma numarası değil,
**örnek sayısıdır** -- yani istatistikî sağlamlık. Kütük H54'ün 2. borcu
(*"8 örnekli AS-GEK istatistikî olarak imkânsız"*) ancak böyle kapanır.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Dict, Optional

import numpy as np

__all__ = ["ayar_sec", "kos", "BASLANGIC_HUCRESI"]


def ayar_sec(zorla: Optional[str] = None):
    """Donanımı yokla, ayarı **ölçüme göre** seç -- tahminle değil."""
    from hesap.donanim import donanim
    from nefs.kulli_egitim import AZAMI_KAGGLE, KISA_CPU, ORTA

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
    from hesap.donanim import rapor as donanim_raporu
    from nefs.kulli_egitim import KulliEgitim

    ayar, dh = ayar_sec(zorla)
    print(donanim_raporu(dh), flush=True)
    print("seçilen ayar: %s  (satır kübiti=%d, χ=%d, çevrim=%d, örnek=%d)"
          % (ayar.ad, ayar.satir_kubiti, ayar.bag, ayar.cevrim, ayar.ornek),
          flush=True)

    t0 = time.perf_counter()
    E = KulliEgitim(ayar, dh=dh)
    r = E.kos()
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
        m = E.as_gek_mukayesesi()
        print("AS-GEK (eski motor) V_son=%.4f  %.1f sn"
              % (m["V_son"], m["süre_sn"]), flush=True)

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


#: Kaggle defterinde **tek hücreye** yapıştırılacak kod.
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
from hesap.donanim import rapor
print(rapor())

# ── EĞİTİM ──────────────────────────────────────────────────────────
# zorla=None  → donanıma göre kendi seçer  ("kısa" / "orta" / "azamî")
from main.kaggle import kos
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


if __name__ == "__main__":   # pragma: no cover
    raise SystemExit(_ana())
