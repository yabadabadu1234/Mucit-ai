"""
omega_kategori -- (∞,∞)-kategori / kübik tip teorisi çekirdeği.

Alt katmanlar:
  aralik      : De Morgan aralık cebri + yüz (kofibrasyon) kafesi
  sozdizim    : terimler
  cekirdek    : ikame, indirgeme, Kan işlemleri (asli: comp)
  denklik     : denklik (equivalence) yapısı, Glue'nun hesap kuralları
  denetleyici : iki yönlü tip denetleyici
  kutuphane   : nesne dilinde yazılmış temel kütüphane
  turetimler  : uzayların türetilmesi ve postulat kütüğü
"""
from .aralik import Aralik, Kofibrasyon, SIFIR, BIR, DOGRU, YANLIS
from . import sozdizim
from . import cekirdek

__all__ = ["Aralik", "Kofibrasyon", "SIFIR", "BIR", "DOGRU", "YANLIS",
           "sozdizim", "cekirdek"]
