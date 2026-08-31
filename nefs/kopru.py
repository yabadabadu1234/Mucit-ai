"""
FUNKTÖR KÖPRÜSÜ -- uzaylar arası geçişin **ölçülen** sıhhati.

Dosya 3'ün hükmü: *"Bir Öklid tensörü ile bir Hilbert durumu doğrudan
çarpılamaz; aradaki geçiş mutlaka açıkça tanımlanmış bir funktör
üzerinden yapılmak zorundadır."* Ve o funktörün ölçüsü şudur: **mesafeyi
koruyor mu?**

`token_uzaylari/morfizm.py` bu ölçüyü zaten yazmıştı ve **beylikti**:
itme (``dφ``), çekme (``φ^*``), metrik çekme (``φ^*h``), funktoryellik
denetimi (zincir kaidesi) ve ``izometri_mi``.

===================================================================
BU PROJEDEKİ FİİLÎ GEÇİŞ HANGİSİDİR
===================================================================

Ana akıştaki tek hakikî uzay geçişi ``belirtecleri_kodla``dır::

    belirteç  t ∈ {0..15}   ──φ──►   açı vektörü  E ∈ ℝ^k   (±1 bitleri)

Kütük H14 bunun **kayıpsız** olduğunu söylüyordu (*"tersinirdir ve
hiçbir bit kaybolmaz"*). Fakat o güne kadar **ölçülmedi**. Burada
ölçülür ve iki ayrı ölçütle:

1. **Tersinirlik** -- kodlanan her belirteç geri çözülebiliyor mu?
2. **İzometri** -- ``φ`` mesafeleri koruyor mu? Yani sözlükte birbirine
   yakın iki belirteç, açı uzayında da yakın mı? ``token_uzaylari``
   bunu ``φ^*h = g`` şartıyla ölçer.

**İkincisi mühimdir ve birincisinden bağımsızdır.** Bir eşleme tersinir
olduğu hâlde mesafeyi paramparça edebilir; o zaman "yakın belirteç"
mefhumu kaybolur ve model genelleyemez. H14 yalnız birinciyi iddia
ediyordu; ikincisi burada ilk defa ölçülüyor.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from token_uzaylari.manifold import Metrik, duz_metrik
from token_uzaylari.morfizm import Morfizm, izometri_mi, jakobi

__all__ = ["belirtec_morfizmi", "kodlamayi_olc"]


def belirtec_morfizmi(sozluk: int = 16, kubit: int = 4) -> Morfizm:
    """``φ: t ↦ (±1 bitleri)`` -- belirteçten açı uzayına geçiş.

    ``Morfizm`` sürekli bir eşleme bekler; belirteç ayrık olduğu için
    **sürekli uzantısı** kullanılır: ``t`` reel alınır ve bitler
    ``2·frac(t/2^i) − 1``in pürüzsüz karşılığıyla yazılır. Jakobi böylece
    tanımlıdır ve ``token_uzaylari`` olduğu gibi çalışır.
    """
    def phi(x: np.ndarray) -> np.ndarray:
        t = np.asarray(x, float).reshape(-1)[0]
        # ``belirtecleri_kodla``nın sürekli karşılığı: her bit, kendi
        # ölçeğindeki bir üçgen dalgadır ve ``±1``e ölçeklenir.
        out = []
        for i in range(kubit):
            u = (t / (1 << i)) % 2.0            # [0,2)
            out.append(2.0 * (1.0 - abs(u - 1.0)) - 1.0)
        return np.asarray(out, float)

    return Morfizm(1, kubit, phi, ad="belirteç→açı")


def kodlamayi_olc(sozluk: int = 16, kubit: int = 4) -> Dict[str, object]:
    """H14'ün iddiasını **iki ölçütle** sına: tersinirlik ve izometri."""
    from nefs.qegitim import belirtecleri_kodla

    # --- 1) TERSİNİRLİK: her belirteç geri çözülüyor mu?
    T = np.arange(sozluk)
    E = belirtecleri_kodla(T, kubit, sozluk)             # (sozluk, kubit)
    bit = (E > 0).astype(np.int64)
    geri = (bit * (1 << np.arange(kubit))[None, :]).sum(axis=1)
    tersinir = bool(np.array_equal(geri % sozluk, T % sozluk))
    carpisma = int(sozluk - len(set(map(tuple, bit.tolist()))))

    # --- 2) İZOMETRİ: mesafe korunuyor mu?
    # ``token_uzaylari.morfizm`` ile ölçülür; hedef metrik birimdir.
    m = belirtec_morfizmi(sozluk, kubit)
    g = duz_metrik(1)                    # kaynak: sözlük ekseni
    h = duz_metrik(kubit)                # hedef: açı uzayı
    noktalar = [[float(x)] for x in np.linspace(0.3, sozluk - 0.7, 24)]
    izo = izometri_mi(m, g, h, noktalar, tol=1e-6)

    # Ham mesafe kıyası: sözlükteki komşuluk açı uzayında korunuyor mu?
    D_soz = np.abs(T[:, None] - T[None, :]).astype(float)
    D_aci = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=2)
    ust = np.triu_indices(sozluk, 1)
    korelasyon = float(np.corrcoef(D_soz[ust], D_aci[ust])[0, 1])

    return {
        "tersinir": tersinir,
        "çarpışma": carpisma,
        "izometri": bool(izo["izometri"]),
        "izometri_azamî_sapma": float(izo["azamî_sapma"]),
        "mesafe_korelasyonu": korelasyon,
        "hüküm": ("H14 doğrulandı: kodlama tersinir."
                  if tersinir else
                  "H14 YANLIŞ: kodlama tersinir değil."),
    }
