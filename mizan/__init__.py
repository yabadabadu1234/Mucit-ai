"""mizan — mantık usulleri motoru.

Sekiz alt modül, aşağıdan yukarıya bağımlı:

===============  ====================================================
modül            ne yapar
===============  ====================================================
``onerme``       hash-consed formül düğümleri + bit-paralel doğruluk
                 tablosu (bütün 2ⁿ değerleme tek bir büyük tam sayı)
``kiyas``        kıyas darbları; 256 monadik modelle **tam** karar
``cikarim``      Hilbert denetçisi, klasik LK, sezgisel G4ip
``kiplik``       Kripke çerçeveleri, K/T/4/5/B/D karşılıkları,
                 deontik kipler, LTL
``cokdegerli``   t-normlar, kalıntılar, üç değerli mantıklar, syādvāda
``altyapisal``   yapısal kuralı açılıp kapanan ardışık hesabı,
                 relevans ölçütü, kuantum (altuzay) mantığı
``istikra``      Laplace ardışıklığı, ICP, temsil, Nyāya, Stoa, Mill
``munazara``     men'/nakz/muâraza oyunu, Gazâlî yakîn mîzânı
===============  ====================================================

Her modül ``python3 -m mizan.<ad>`` ile kendi ölçümünü basar.
Testler: ``python3 -m pytest mizan/test_mizan.py -q``
"""

__all__ = [
    "onerme", "kiyas", "cikarim", "kiplik",
    "cokdegerli", "altyapisal", "istikra", "munazara",
]
