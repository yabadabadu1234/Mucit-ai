"""ogrenme — operatör öğrenmesi: RKHS, DeepONet/FINO, ızgara, Grassmann.

Dört modül:

* ``rkhs``      — çekirdek Hilbert uzayı, kapalı form çözüm, Nyström
* ``operator``  — DeepONet, FINO spektral ayrışımı, çözünürlük bağımsızlığı
* ``izgara``    — adaptif B-spline düğümleri, bükülme enerjisi, sembolik kapanış
* ``grassmann`` — asal açılar, geodezik Exp/Log (K26), Karcher ortalaması,
  Tikhonov'un çekirdeği yok etmesi (K25)
"""

__all__ = ["rkhs", "operator", "izgara", "grassmann"]
