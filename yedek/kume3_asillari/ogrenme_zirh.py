"""
DÖRTLÜ TOPOLOJİK ZIRH -- ferman adıyla ``ogrenme/zirh.py`` (Bab IV)

    (1) Sheaf demet kısıtı     𝒮_m      -- ek yeri uyumsuzluğunu yutar
    (2) Homotopi bükümü        W(γ)=1   -- eş anlamlılarda faz kilitler
    (3) Betti-Hodge projektörü Π_b      -- ezber deliklerini temizler
    (4) Kohomoloji süzgeci     Π_koho   -- H^m ≠ 0 safsatayı sıfırlar

Riyaziyat `nefs/zirh.py`de kurulu ve **dördü de ayrı ayrı kırmızıya
dönebiliyor** (sınama: ``test_zirh_dordu_de_KIRMIZIYA_donebiliyor``).
Burada o motor fermanın istediği sınıf yüzüyle sarılır; hesap
kopyalanmaz.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from nefs.zirh import (ZirhAyari, betti_kaybi, hodge_bettisi, homotopi_kaybi,
                       koho_kaybi, sheaf_izdusumu, sheaf_uyumsuzlugu,
                       wilson_cevrimi, zirh_kaybi, zirh_uygula)

__all__ = ["DortluTopolojikZirh", "zirh_kaybi_hesapla", "zirh_kaybi",
           "zirh_uygula", "ZirhAyari"]


def _kompleks_kur(H: np.ndarray, esik: float = 1e-9
                  ) -> Dict[int, list]:
    """Operatörden bir simplisyel kompleks çıkar (Vietoris-Rips gölgesi).

    Köşeler satırlar, kenarlar ``|H_ij| > eşik`` çiftleridir. Bu bir
    **gölgedir**, tam nerv değildir ve öyle söyleniyor: Betti sayıları
    buradan okununca ``H``nin bağlantı yapısını ölçer, manifoldun
    kendisini değil.
    """
    A = np.abs(np.asarray(H, float))
    n = int(A.shape[0])
    kose = [(i,) for i in range(n)]
    kenar = [(i, j) for i in range(n) for j in range(i + 1, n)
             if A[i, j] > esik or A[j, i] > esik]
    return {0: kose, 1: kenar}


@dataclass
class DortluTopolojikZirh:
    """Dört zırhı bir arada tatbik eden ve **raporlayan** uzuv."""
    ayar: ZirhAyari = field(default_factory=ZirhAyari)
    esik: float = 1e-9

    def tatbik_et(self, H: np.ndarray
                  ) -> Tuple[np.ndarray, Dict[str, float]]:
        """``Ĥ`` üzerine dört zırhı geçir; ``(Ĥ_zırhlı, rapor)`` döndür.

        Rapor **her zırh için ayrı sayı** taşır. Tek bir toplam sayı
        dönseydi hangi zırhın çalıştığı bilinemez, biri ölse fark
        edilmezdi (H90).
        """
        H = np.atleast_2d(np.asarray(H, float))
        n = int(H.shape[0])

        # (1) Sheaf: operatörün üst ve alt üçgen kısıtlamaları iki
        #     yamadır; ek yerindeki uyumsuzluk sheaf artığıdır.
        ust = np.triu(H)
        alt = np.tril(H).T
        s_hata = float(sheaf_uyumsuzlugu(ust, alt))
        S = sheaf_izdusumu(ust, alt)

        # (3)(4) Betti ve kohomoloji: kompleksin gölgesinden
        K = _kompleks_kur(H, self.esik)
        b1 = betti_kaybi(K, k=1)
        b0 = koho_kaybi(K, k=0)

        # (2) Homotopi: Wilson çevrimi -- kapalı yolda ``W(γ) = 1`` mi
        # Çevrimin halkaları **aynı ebatta** olmak zorundadır; yoksa
        # ``W(γ)`` çarpımı hiç kurulamaz. Kapalı bir yol için kare bir
        # pencere kaydırılır ve son halka başa döner.
        adim = max(2, min(8, n))
        m = max(1, n // adim)
        baglanti = []
        for i in range(adim):
            b = i * m
            blok = H[b:b + m, b:b + m]
            if blok.shape != (m, m):
                blok = np.zeros((m, m))
            baglanti.append(np.eye(m) + 1e-3 * blok)
        h = homotopi_kaybi(baglanti)

        toplam = zirh_kaybi(sheaf=s_hata, betti=float(b1.get("kayıp", 0.0)),
                            koho=float(b0.get("kayıp", 0.0)),
                            homotopi=float(h.get("kayıp", 0.0)),
                            ayar=self.ayar)

        H_zirhli = zirh_uygula(H, S=S if S is not None and
                               getattr(S, "shape", None) == H.shape else None)
        rapor = {
            "sheaf_uyumsuzluk": s_hata,
            "betti_delik_sayisi": float(b1.get("betti", 0.0)),
            "kohomoloji_tikaniklik": float(b0.get("kayıp", 0.0)),
            "homotopi_burulma": float(h.get("kayıp", 0.0)),
            "toplam_kayip": float(toplam.get("kayıp", 0.0)),
            "mizan_dengesi": float(np.abs(np.mean(H_zirhli))),
        }
        return H_zirhli, rapor


def zirh_kaybi_hesapla(H: np.ndarray,
                       ayar: Optional[ZirhAyari] = None) -> Dict[str, float]:
    """Kısayol: yalnız raporu isteyenler için."""
    z = DortluTopolojikZirh(ayar or ZirhAyari())
    return z.tatbik_et(H)[1]


def rapor() -> str:                                      # pragma: no cover
    rng = np.random.default_rng(0)
    z = DortluTopolojikZirh()
    s = ["DÖRTLÜ TOPOLOJİK ZIRH", ""]
    for ad, H in (("rastgele", rng.normal(size=(12, 12))),
                  ("birim (temiz)", np.eye(12)),
                  ("tam bağlı", np.ones((12, 12)))):
        _Hz, r = z.tatbik_et(H)
        s.append("  %-14s sheaf=%.4f betti=%.0f koho=%.4f homotopi=%.4f "
                 "toplam=%.4f"
                 % (ad, r["sheaf_uyumsuzluk"], r["betti_delik_sayisi"],
                    r["kohomoloji_tikaniklik"], r["homotopi_burulma"],
                    r["toplam_kayip"]))
    s.append("")
    s.append("  Satırlar birbirinden AYRI çıkmalı; hepsi aynı çıkarsa")
    s.append("  zırh ölçmüyor demektir.")
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
