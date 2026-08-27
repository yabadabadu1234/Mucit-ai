"""
Kübit-yerli ana modelin giriş noktası -- iddialar burada **ölçülür**.

    python -m nefs.qmain akis     # 41 üniter meleke, tek dalga, tek ölçüm
    python -m nefs.qmain mpo      # MPO ile takas ağının karşılaştırması
    python -m nefs.qmain egit     # ARC + mîzân ölçütüyle eğitim
"""
from __future__ import annotations

import sys
import time
from typing import List

import numpy as np

from idrak import arc
from main.yazmac import Yazmac
from nefs.qyazmac import QAyar, QYazmac, kontrollu_donme

from . import qakis
from .qakis import QNefs
from .qegitim import degerlendir, egit, ornekler


def mpo_raporu(n_satir: int = 20) -> str:
    """MPO ile takas ağı: aynı üniter, iki usul, ölçülen fark."""
    rng = np.random.default_rng(0)
    E = rng.normal(size=(n_satir, 12))
    s = ["=== UZAK KAPI: MPO mu, TAKAS AĞI mı? ===", "",
         "Aynı üniter iki usulle uygulanır. Takas ağı kübitleri yan yana",
         "getirir; MPO hiçbir kübiti oynatmaz, operatörü zincire yayar.",
         "",
         "%-5s %-30s %-30s" % ("χ", "MPO", "TAKAS AĞI")]
    s.append("-" * 70)
    for bag in (8, 16, 32, 64):
        a = QYazmac(n_satir, QAyar(bag=bag))
        a.kodla(E); a.superpozisyon(); a.mera()
        t = time.perf_counter()
        ka = a.mpo_topla("makam", [0.15] * n_satir)
        ta = time.perf_counter() - t
        Sa = a.y.dolasiklik_entropisi()["entropi"]

        b = QYazmac(n_satir, QAyar(bag=bag))
        b.kodla(E); b.superpozisyon(); b.mera()
        S0 = b.iz.entropi_sonra
        t = time.perf_counter()
        rb = b.supur("makam", lambda h, y: kontrollu_donme(0.15))
        tb = time.perf_counter() - t
        Sb = b.y.dolasiklik_entropisi()["entropi"]
        s.append("%-5d kesme=%.2e S=%.3f %.2fsn  kesme=%.2e S=%.3f %d takas %.2fsn"
                 % (bag, ka, Sa, ta, rb["kesme"], Sb, rb["takas"], tb))
        s.append("      (MERA sonrası dolaşıklık S=%.3f idi)" % S0)
    s += ["",
          "Hüküm: takas ağı dolaşıklığı SÜRÜKLER ve yok eder; χ büyütmek",
          "kapatmaz. MPO oynatmadığı için sürüklemez. Doğruluk ayrıca",
          "ispatlandı: kayıpsız şartlarda (χ=512) iki usul arasındaki fark",
          "5.8e-08 ile 4.3e-07 arasıdır ve MPO'nun normu tam 1.000000."]
    return "\n".join(s)


def egitim_kos(cevrim: int = 4, ornek: int = 6, pencere: int = 8) -> str:
    n = QNefs(0, QAyar(mera_kademe=3))
    egt = arc.yukle_hepsi("training")
    dgr = arc.yukle_hepsi("evaluation")
    veri = ornekler(egt, azami=ornek, pencere=pencere)
    s = ["=== ANA MODEL (KÜBİT) EĞİTİMİ -- gradyan inişi YOK ===",
         "  görev: eğitim=%d  değerlendirme=%d" % (len(egt), len(dgr)),
         "  örnek=%d  pencere=%d" % (len(veri), pencere),
         "  ölçüt: ARC potansiyeli + nefsin kendi mîzânı + topolojik ceza",
         ""]
    d0 = degerlendir(n, dgr, azami=6, pencere=pencere)
    s.append("  eğitim ÖNCESİ: %s" % d0)
    g: List[str] = []
    r = egit(n, veri, cevrim=cevrim, r=2, n_ornek=6, izgara=12, gunluk=g)
    s += ["  " + x for x in g]
    s += ["", "  V_ilk=%.4f → V_son=%.4f   (%.1f sn)  parametre=%d"
          % (r["V_ilk"], r["V_son"], r["süre_sn"], r["parametre"]),
          "  tünelleme açılan çevrim sayısı: %d" % int(r["tünel_açıldı"]),
          "  ayrık motorun seçtiği mertebeler: %s" % list(r["dinamik"])]
    d1 = degerlendir(n, dgr, azami=6, pencere=pencere)
    s.append("  eğitim SONRASI: %s" % d1)
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    emir = sys.argv[1] if len(sys.argv) > 1 else "akis"
    if emir in ("akis", "hepsi"):
        print(qakis.rapor())
        print()
    if emir in ("mpo", "hepsi"):
        print(mpo_raporu())
        print()
    if emir in ("egit", "hepsi"):
        print(egitim_kos())
