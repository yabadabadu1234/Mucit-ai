"""akis — hacimsel akışlar, Lie cebri ve tıkızlaştırma.

Üç kısım:

* :mod:`akis.hacim` — ortalama eğrilik akışı, Fokker–Planck, log-yoğunluk,
  Gibbs hacim değişimi, eyer ölçütü.
* :mod:`akis.lie` — Lie braketi, Jacobi, ``so(n)``/``su(n)``, üslü harita,
  grup üzerinde kalan adım, kutupsal ayrışma.
* :mod:`akis.tikiz` — zorlayıcılık, alt-seviye tıkızlığı, logaritmik
  barriyer, iç nokta yolu, Morse bağıntısı, Alexandroff tıkızlaştırması.
"""

__all__ = ["hacim", "lie", "tikiz"]
