"""ARAMAK -- en iyiyi bulmak, kuyuya düşersen çıkmak.

Nazırlık katının üçüncü fiili (kütük H227). **Yeni riyaziye yoktur**;
hesap ``ogrenme/optimize.py``dedir, burada yalnız çağrı ve isim vardır.

    aday = ara(f)                 # asgarîyi bul
    yol  = ara(ne="kaçış", ...)   # yerel asgarîden çık

Bu nazırlık ``ogren``in **âletidir**: öğrenmek, aramanın bir sebebidir.
Ayrı bir fiil olmasının sebebi şudur -- aramak öğrenmeden **evvel** de
lâzım olur (aday kaide, aday kalıp, aday mertebe) ve o zaman hiçbir
şey öğrenilmiyordur.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from ogrenme.optimize import en_iyiyi_ara, had, kuyudan_cik

__all__ = ["ara"]


def ara(f=None, ne: str = "en_iyi", yol: str = "dürr", **kw) -> Any:
    """ARAMAK -- ``N`` aday içinden en iyisi, yahut kuyudan çıkış.

    ==============  ==================================================
    ``ne``          ne yapar
    ==============  ==================================================
    ``en_iyi``      ``f`` dizisinde asgarîyi arar. ``yol``:
                    ``dürr`` (``O(√N)``, hiçbir şey bilmeden),
                    ``grover`` (``O(√(N/K))``, ``K``yı bilerek),
                    ``adiyabatik`` (``T`` süresince taşıyarak).
    ``kaçış``       yerel asgarîde sıkışmışsa çıkış yolu: ``ısıl``
                    (``e^{−ΔE/T}``) yahut ``tünel`` (``e^{−γ}``).
    ``bedel``       kaçışın kaç deneme edeceği.
    ``had``         aramanın haddi: NFL üstten, Nesterov alttan.
    ==============  ==================================================

    **Varsayılan yol Dürr--Høyer'dir ve bu bir tercih değil ihtiyattır.**
    Grover daha hızlıdır fakat işaretli sayısı ``K``yı bilmek ister;
    ``K`` yanlış varsayılırsa en iyi tur sayısı kayar ve başarı
    **düşer** -- fazla dönmek zarardır (M18). Dürr--Høyer ``K``yı
    bilmez, dolayısıyla yanlış varsayamaz. Bilmediğini bilmek, yanlış
    bilmekten hızlıdır.
    """
    if ne == "en_iyi":
        return en_iyiyi_ara(f, ne=yol, **kw)
    if ne == "kaçış":
        return kuyudan_cik(ne=kw.pop("nasil", "ısıl"), **kw)
    if ne == "bedel":
        return kuyudan_cik(ne="bedel", **kw)
    if ne == "had":
        return had(**kw)
    raise ValueError("arama fiilinin kipi bilinmiyor: %r" % (ne,))
