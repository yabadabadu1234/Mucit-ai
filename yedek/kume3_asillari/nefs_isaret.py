"""
ÇOK-KONTROLLÜ İŞARET -- her mantık manifoldunun temel taşı.

Bütün mantık kuralları (Barbara, modus ponens, nakz, tenakuzsuzluk,
Munfasıla…) tek bir şeye indirgenir: **belli bir kübit örüntüsüne ``π``
fazı vurmak.** Kural "şu hâl mantık dışıdır" der; devrede bunun karşılığı
o hâlin işaretlenmesi, sönmesinin de girişime bırakılmasıdır (kütük
H107'nin ölçülmüş dersi: *hiçbir sabit üniter kapı bir alt uzayı şartsız
söndüremez*).

===================================================================
NİÇİN MPO -- ve niçin BAĞ BOYUTU 2
===================================================================

``k`` kübitlik bir çok-kontrollü ``Z`` (``C^k Z``), ancilla ile kurulursa
``k−1`` yardımcı kübit ve bir Toffoli merdiveni ister; çöpü geri almak da
ayrı bir külfettir. Halbuki işlemci **köşegendir**::

    C^k Z = I − 2 |1…1⟩⟨1…1|

ve köşegen bir izdüşüm çarpımının MPO bağ boyutu **2**dir::

    w = 0 kanalı : birim (δ_ij)                    katsayı  +1
    w = 1 kanalı : |b_j⟩⟨b_j| (aranan bit)         katsayı  −2

Sol sınır ``(1, −2)``, sağ sınır ``(1, 1)``. Ancilla yok, çöp yok, geri
alma yok; ve `main.yazmac.mpo_uygula` bunu bütün zincire tek geçişte
uygular. Aynı yapı `nefs/qkaide.py`de ölçüldü: kesme ``~1e-16``.

===================================================================
MENFÎ KONTROL BEDAVA
===================================================================

Aranan örüntü ``|1…1⟩`` olmak zorunda değildir: her yuva için hangi bitin
arandığı ayrı verilebilir (``0`` yahut ``1``). ``X`` ile sarmaya gerek
kalmaz; MPO tensörüne doğrudan yazılır. Böylece *"tasdik uyanık FAKAT
mîzân uykuda"* gibi karışık şartlar tek geçişte işaretlenir.

===================================================================
ARADAKİ YUVALAR
===================================================================

``bas``tan ``son``a kadar bütün yuvalar taranır; örüntüde yer almayan
yuvalarda **birim** konur (iki kanalda da ``δ_ij``), yani onlara
dokunulmaz. Bu, örüntünün bitişik olmasını gerektirmez -- küllî hüküm
bloğunun herhangi bir alt kümesi işaretlenebilir.
"""
from __future__ import annotations

from typing import Dict, Mapping, Sequence

import numpy as np

__all__ = ["cok_kontrollu_isaret", "sifir_yansitmasi"]


def cok_kontrollu_isaret(q, orutu: Mapping[int, int]) -> float:
    """``orutu``daki bütün şartlar sağlanan kola ``π`` fazı vur.

    ``orutu``: ``{yuva: aranan_bit}``. Meselâ::

        {tasdik₀: 1, nakz₀: 1}          hem mühürlü hem nakzedilmiş
        {tasdik₀: 1, mizan₀: 0}         delilsiz mühür
        {kelam₀: 1, tasdik₀: 0}         mühürsüz kelâm

    Dönen: MPO sıkıştırmasında atılan ağırlık (kesme). Köşegen ve bağ
    boyutu 2 olduğu için ``~1e-16`` beklenir; büyükse **bildirilir**.
    """
    if not orutu:
        return 0.0
    yuv = sorted(int(k) for k in orutu)
    bas, son = yuv[0], yuv[-1] + 1
    W: Dict[int, np.ndarray] = {}
    for j in range(bas, son):
        T = np.zeros((2, 2, 2, 2))
        T[0, 0, 0, 0] = T[0, 1, 1, 0] = 1.0          # birim kanalı
        if j in orutu:
            b = int(orutu[j]) & 1
            T[1, b, b, 1] = 1.0                      # yalnız aranan bit
        else:
            T[1, 0, 0, 1] = T[1, 1, 1, 1] = 1.0      # aradaki yuva: birim
        W[j] = T
    return q.y.mpo_uygula(W, 2, bas=bas, son=son,
                          sol_sinir=np.array([1.0, -2.0]),
                          sag_sinir=np.array([1.0, 1.0]))


def sifir_yansitmasi(q, yuvalar: Sequence[int]) -> float:
    """``R₀ = I − 2|0…0⟩⟨0…0|`` -- verilen yuvalarda, ancillasız.

    ``cok_kontrollu_isaret``in hususî hâlidir: bütün yuvalarda aranan bit
    ``0``dır. Grover difüzyonunun orta adımı budur.
    """
    return cok_kontrollu_isaret(q, {int(j): 0 for j in yuvalar})
