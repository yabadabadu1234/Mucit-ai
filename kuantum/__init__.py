"""kuantum — kapılar, devreler, spektral işleçler ve topolojik mizan.

Yedi modül:

* ``kapilar``    — tek/çok kübitli üniter kapılar, küresel faz ayrımı
* ``devre``      — durum vektörü simülatörü, QFT, QPE, Trotter–Suzuki
* ``tda``        — kombinatoryal Laplasyen, Betti, barkod, bottleneck, Kahan
* ``qsvt``       — blok kodlama, QSP, tekil değer dönüşümü
* ``surekli``    — sürekli değişkenli (CV) fotonik operatörler, kesme bedeli
* ``topolojik``  — Fibonacci anyon örgüsü, Majorana, Kitaev yüzey kodu
* ``eniyileme``  — adiyabatik geçiş, QAOA, parametre-kaydırma kuralı
"""

__all__ = ["kapilar", "devre", "tda", "qsvt", "surekli", "topolojik",
           "eniyileme"]
