"""
L_TENAKUZ -- SAYISAL OLARAK KARARLI LOG-BARİYER × EŞ-ZAMANLI DIŞLAMA

===================================================================
MESELE: HAM LOG-BARİYER IRAKSAR
===================================================================

Muhakeme çevriminin holonomisi ``U_C``dir. Çevrim kendi başladığı
aksiyomu inkâr ediyorsa ``U_C → −I`` olur ve ``Tr(I + Re U_C) → 0``.
Ham biçimde::

    L = −ln Tr(I + Re U_C)          →  +∞

Tek bir tam taklalı çevrim bütün mizanı yutar; gradyan patlar ve tâlim
o çevrimden başka hiçbir şeyi görmez. Kat'î hüküm (**Sayısal Olarak
Kararlı Log-Bariyer ve Eş-zamanlı Dışlama Matrisi**)::

    L_Tenakuz = −ln( (Tr(I + Re U_C) + ε) / (2d + ε) ) · S_dışlama(A,B)

    S_dışlama(A,B) = exp( −(Birlikte_Görülme(A,B) + 10⁻⁴) / τ_pencere )

İki ameliye vardır ve ikisi ayrı işe yarar:

1. **PAYDA ``2d + ε``.** ``Tr(I + Re U_C)`` en çok ``2d``dir (``U_C =
   I`` hâli). Paydaya bölününce argüman ``(0, 1]`` aralığına iner ve
   logaritma daima ``≥ 0`` olur: ceza ödüle dönemez. ``ε`` ise tabanı
   sıfırdan ayırır, o hâlde ceza **sonlu bir tavana** bağlanır::

       tavan = ln( (2d + ε) / ε )

   ``ε = 10⁻⁵`` ve ``d = 16`` için tavan ``≈ 14,98``dir. Ölçülen azamî
   ceza bu tavana çarpıyorsa rapor onu yazar.

2. **``S_dışlama``.** Ceza her tenakuza aynı ağırlığı vermez. Zabıtın
   manası şudur: iki kavram veride sık sık **beraber** geçiyorsa
   aralarındaki gerilim tabiîdir (dil zaten öyle kurulmuştur); hiç
   beraber görülmemiş iki kavramın çelişmesi ise hakiki bir yırtıktır.
   Birlikte görülme büyüdükçe ``S`` sıfıra iner, ceza hafifler.
   ``10⁻⁴`` payı, hiç görülmemiş çiftte bile ``S``yi ``1``in **altında**
   tutar (tam ``1`` olsaydı sınır hâli ölçülemezdi).

===================================================================
FERMAN 7-D: TAŞIYICI
===================================================================

``U_C`` burada ``n × n`` bir dizeydir ve ``n`` **belirteç lifidir (16)**,
quditin tamamı (4096) değil. ``nefs/kulli_mizan.py:holonomi_yigin``
bunu zaten ``(C, 16, 16)`` bloğunda toplu kuruyor; bu dosya o bloğun
izini alır. Yoğun ``4096²`` dizey **kurulmaz** (ferman 7).

``Birlikte_Görülme`` ise tamsayı sayımıdır: bağlam penceresi içinde
hangi belirteç çifti kaç kere beraber geçmiş. Kayan nokta yalnız son
``exp``tedir ve o da ``C`` çevrim için ``n²`` elemanlık tek tabloda,
ana akış döngüsünde değil.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

import numpy as np

__all__ = ["TenakuzAyari", "birlikte_gorulme", "dislama_dizeyi",
           "log_bariyer", "tenakuz_tavani"]


@dataclass
class TenakuzAyari:
    """Log-bariyerin ve dışlamanın ölçüleri."""

    #: ``λ`` -- kefenin mizandaki ağırlığı.
    lam: float = 0.4
    #: ``ε`` -- ıraksama freni. ``0`` YASAKTIR: tavan sonsuza gider.
    eps: float = 1e-5
    #: ``τ_pencere`` -- dışlamanın sönüm boyu.
    tau: float = 8.0

    def __post_init__(self) -> None:
        assert float(self.eps) > 0.0, (
            "ε sıfır olamaz: log-bariyerin tavanı sonsuza gider ve tek "
            "bir çevrim bütün mizanı yutar -- ıraksamayı önlemek için "
            "konmuştu")
        assert float(self.tau) > 0.0, (
            "τ_pencere sıfır olamaz: sıfıra bölme")


def birlikte_gorulme(baglamlar: Sequence[Sequence[int]], n: int
                     ) -> np.ndarray:
    """``Birlikte_Görülme(A,B)`` -- bağlam penceresi içi eş-zamanlılık.

    **TAMSAYI SAYIMIDIR.** Her bağlamda geçen belirteçlerin bütün
    ikilileri sayılır; köşegen (``A``nın kendisiyle) sayılmaz, çünkü
    bir kavramın kendisiyle "beraber görülmesi" dışlama hakkında hiçbir
    şey söylemez.

    Netice simetriktir ve ``(n, n)``dir; ``n`` belirteç lifidir (16),
    o hâlde tablo 256 hücredir.
    """
    n = int(n)
    C = np.zeros((n, n), np.int64)
    for bag in baglamlar:
        t = np.unique(np.asarray(list(bag), np.int64) % n)
        if t.size < 2:
            continue
        C[np.ix_(t, t)] += 1
    np.fill_diagonal(C, 0)
    return C


def dislama_dizeyi(baglamlar: Sequence[Sequence[int]], n: int,
                   ayar: Optional[TenakuzAyari] = None) -> np.ndarray:
    """``S_dışlama(A,B) = exp(−(Birlikte_Görülme(A,B) + 10⁻⁴)/τ_pencere)``.

    ``1``e yakın: bu iki kavram hiç beraber görülmemiş -- çelişmeleri
    hakiki bir yırtıktır, ceza ağır.
    ``0``a yakın: sürekli beraber geçiyorlar -- gerilim tabiîdir,
    ceza hafif.
    """
    a = ayar or TenakuzAyari()
    C = birlikte_gorulme(baglamlar, n).astype(float)
    S = np.exp(-(C + 1e-4) / float(a.tau))
    assert np.all(np.isfinite(S)), "dışlama dizeyi sonlu değil"
    assert float(S.max()) < 1.0, (
        "S_dışlama tam 1 çıktı -- 10⁻⁴ payı düşmüş demektir; sınır hâli "
        "o pay olmadan ölçülemez")
    return S


def tenakuz_tavani(d: int, ayar: Optional[TenakuzAyari] = None) -> float:
    """``ln((2d + ε)/ε)`` -- cezanın **sonlu** tavanı.

    Bu sayı raporda ölçülen azamînin yanında durur: ölçülen tavana
    çarpıyorsa bariyer doymuş demektir ve o da bir haberdir.
    """
    a = ayar or TenakuzAyari()
    e = float(a.eps)
    return float(math.log((2.0 * float(d) + e) / e))


def log_bariyer(U: np.ndarray, S_cifti: np.ndarray,
                ayar: Optional[TenakuzAyari] = None) -> Dict[str, Any]:
    """Çevrim başına ``L_Tenakuz``. ``U`` ``(C, n, n)``, ``S_cifti`` ``(C,)``.

    ``S_cifti[c]``, ``c``inci çevrimin köşelerinin dışlama ortalamasıdır
    ve ``dislama_dizeyi``den okunur; burada yeniden hesaplanmaz.
    """
    a = ayar or TenakuzAyari()
    U = np.asarray(U, complex)
    assert U.ndim == 3 and U.shape[1] == U.shape[2], (
        "holonomi bloğu (C, n, n) olmalı; verilen %r" % (U.shape,))
    C, n, _ = U.shape
    e = float(a.eps)
    # ``Tr(I + Re U_C)`` -- iz, matrisin kendisini ister ve o da zaten
    # ``(C, 16, 16)`` bloğundadır; yoğun 4096² kurulmaz.
    iz = float(n) + np.real(np.einsum('cii->c', U))
    iz = np.maximum(iz, 0.0)
    arg = (iz + e) / (2.0 * float(n) + e)
    assert np.all(arg > 0.0) and np.all(arg <= 1.0 + 1e-12), (
        "log-bariyerin argümanı (0,1] dışına çıktı -- normalizasyon "
        "bozuk demektir; ceza ödüle dönerdi")
    ham = np.maximum(-np.log(np.minimum(arg, 1.0)), 0.0)
    S = np.asarray(S_cifti, float).reshape(-1)
    assert S.size == C, "dışlama vektörü %d, çevrim %d" % (S.size, C)
    ceza = ham * S
    tavan = tenakuz_tavani(n, a)
    assert np.all(np.isfinite(ceza)), "L_Tenakuz sonlu değil -- IRAKSADI"
    assert float(np.max(ham, initial=0.0)) <= tavan + 1e-9, (
        "ham bariyer tavanı aştı (%.6f > %.6f) -- ε freni tutmuyor"
        % (float(np.max(ham, initial=0.0)), tavan))
    return {"ceza": float(np.mean(ceza)) if C else 0.0,
            "azamî": float(np.max(ceza)) if C else 0.0,
            "ham_azamî": float(np.max(ham)) if C else 0.0,
            "tavan": tavan,
            "dışlama_ortalama": float(np.mean(S)) if C else 0.0,
            "çevrim": int(C)}
