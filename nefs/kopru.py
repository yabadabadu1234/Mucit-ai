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

__all__ = ["belirtecten_aciya"]


def belirtecten_aciya(sozluk: int = 16, kubit: int = 4,
                      ne: str = "ölç"):
    """BELİRTEÇTEN AÇIYA GEÇİŞ SAĞLAM MI -- tek terkip (kütük H225).

    Küme: ``belirtec_morfizmi`` + ``kodlamayi_olc``. İkincisi birincisini
    kurup iki ölçütle sınıyordu; ayrı isim taşımaları, morfizm ile
    morfizmin sıhhatini iki ayrı şey gibi gösteriyordu.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``morfizm``     ``φ: t ↦ (±1 bitleri)`` -- sürekli uzantısıyla
    ``ölç``         H14'ün iddiası: tersinirlik **ve** izometri
    ==============  ==================================================

    ``Morfizm`` sürekli bir eşleme bekler; belirteç ayrık olduğu için
    **sürekli uzantısı** kullanılır: ``t`` reel alınır ve bitler
    ``2·frac(t/2^i) − 1``in pürüzsüz karşılığıyla yazılır (her bit kendi
    ölçeğinde bir üçgen dalgadır). Jakobi böylece tanımlıdır ve
    ``token_uzaylari`` olduğu gibi çalışır.

    **Tersinirlik ile izometri AYRI sayılardır** ve ikisi birden döner
    (H47): bir kodlama tersinir olduğu hâlde mesafeyi paramparça
    edebilir; o zaman "yakın belirteç" mefhumu kaybolur. Çarpışma sayısı
    da açıkça sayılır -- izometri bozulduğunda sessiz kalınmaz.
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

    if ne == "morfizm":
        return Morfizm(1, kubit, phi, ad="belirteç→açı")
    if ne != "ölç":
        raise ValueError("köprü kipi bilinmiyor: %r" % (ne,))
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
    m = Morfizm(1, kubit, phi, ad="belirteç→açı")
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


def rapor() -> str:                                     # pragma: no cover
    """Kendi kendini gösterme (H126): H14'ün iki ölçütü, yan yana.

    Tersinirlik ile izometri **ayrı** sayılardır ve ikisi birden yazılır
    (H47). Bir kodlama tersinir olduğu hâlde mesafeyi paramparça
    edebilir; o zaman "yakın belirteç" mefhumu kaybolur.
    """
    s = ["FUNKTÖR KÖPRÜSÜ -- belirteç → açı geçişinin sıhhati", ""]
    s.append("  %-8s %-10s %-10s %-12s %-14s %s"
             % ("sözlük", "kübit", "tersinir", "çarpışma",
                "izometri", "mesafe kor."))
    for sozluk, kubit in ((4, 2), (8, 3), (16, 4), (16, 3), (32, 4)):
        r = belirtecten_aciya(sozluk, kubit)
        s.append("  %-8d %-10d %-10s %-12d %-14s %+.4f"
                 % (sozluk, kubit, r["tersinir"], r["çarpışma"],
                    r["izometri"], r["mesafe_korelasyonu"]))
    s.append("")
    s.append("  Son iki satır mühimdir: sözlük kübit sayısının taşıyabildiği")
    s.append("  adedi aşınca çarpışma başlar ve tersinirlik KIRILIR --")
    s.append("  yani ölçü kırmızıya dönebiliyor, H14 her hâlde doğru değil.")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
