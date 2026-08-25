"""ogrenme — operatör öğrenmesi: RKHS, DeepONet/FINO, adaptif ızgara.

Üç modül:

* ``rkhs``     — çekirdek Hilbert uzayı, kapalı form çözüm, Nyström
* ``operator`` — DeepONet, FINO spektral ayrışımı, çözünürlük bağımsızlığı
* ``izgara``   — adaptif B-spline düğümleri, bükülme enerjisi, sembolik kapanış
"""

__all__ = ["rkhs", "operator", "izgara"]
