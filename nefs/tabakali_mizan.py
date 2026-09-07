"""
TABAKALI MİZANIN İKİ YENİ KEFESİ -- KATEGORİ VE NOKTA

===================================================================
ZABIT: KÖR NLL İNTİHARDIR
===================================================================

Zabıt (*Quditte Negatif Olabilirlik Yanılgısı ve Tabakalı Mizan*):

    "Siz NLL aldığınızda formül sadece Born kuralının köşegen elemanına
    bakar... Durum vektörünün faz açısı ister 0 olsun, ister π olsun,
    kare alındığında faz tamamen buharlaşır... sistem kör bir genlik
    sayacına döner."

Yerine dört mertebeli mizan::

    L_toplam = L_nokta + α·L_uzay + β·L_kategori + γ·L_tip

===================================================================
TERKİP, TABELA DEĞİLDİR (FERMAN 3)
===================================================================

Dört mertebenin **ikisi mizanda zaten vardır**. Yeni dosya açıp aynı
şeyi ikinci kere yazmak terkip değil, ikilemedir. Aynı olduklarının
ispatı:

* ``L_uzay = 1 − |⟨Φ_hedef|Ψ_uzay⟩|²``.
  ``nefs/kulli_mizan.py`` ``L_rez = 1 − F(ρ_veri, ρ_model)`` hesaplar;
  ``F`` Uhlmann sadakatidir. Uhlmann sadakati **saf durumlar için**
  ``|⟨Φ|Ψ⟩|²``ye tam eşittir (``F(|Φ⟩⟨Φ|, |Ψ⟩⟨Ψ|) = |⟨Φ|Ψ⟩|²``); karışık
  durumda ise onun yegâne meşru genellemesidir. O hâlde ``L_uzay``
  yazmak, ``L_rez``i başka isimle yazmaktır. **Yazılmadı.**

* ``L_tip = ⟨Ψ|Δ_Hodge|Ψ⟩``.
  ``kulli_mizan``daki ``L_hod`` **tam olarak budur** (üstelik QSVT
  süzgeciyle harmonik bileşen ayrılmış hâlidir). **Yazılmadı.**

Hakikaten yeni olan iki kefe burada:

===================================================================
1. L_KATEGORİ -- FUNKTÖR KOMPOZİSYONU (ETİKETSİZ)
===================================================================

    L_kategori = ‖ M_{g∘f} − M_g · M_f ‖²_F

Kategori teorisinin temel şartı: ``g∘f`` geçişi, tek tek geçişlerin
bileşkesine eşit olmalıdır. **Bu kayıp dışarıdan etiket istemez**;
sistemin kendi morfizmlerinin kendini denetlemesidir.

Morfizm nereden gelir? Uydurulmaz: ``nefs/kulli_mizan.py:givens`` iki
hâl arasındaki **kanonik** geçişi (düzlem içi SU(2) dönmesi) verir. Üç
ardışık hâl ``a → b → c`` için::

    M_f     = givens(a, b)
    M_g     = givens(b, c)
    M_{g∘f} = givens(a, c)

Kompozisyon şartı tutuyorsa fark sıfırdır. Tutmuyorsa sistem "a'dan
c'ye giderken b'den geçmek" ile "doğrudan gitmek" arasında ayrım
yapıyor demektir ve bu, kategori aksiyomunun ihlâlidir.

===================================================================
2. L_NOKTA -- KISMÎ BORN HİZALAMASI
===================================================================

    L_nokta = −ln Tr( P_{x_hedef} · ρ_çıktı )

**Bu kör NLL DEĞİLDİR ve olmasına izin verilmez.** Farkı üç maddede:

* Kör NLL sözlük üstünde softmax kurup hedefin logitini iter; burada
  ``ρ`` **quditin kendi indirgenmiş yoğunluğudur** ve ``P_hedef``
  o uzayın izdüşüm operatörüdür. Faz köşegen dışında yaşamaya devam
  eder; bu terim yalnız köşegenin bir hücresini okur, ötekini silmez.
* Zabıtın şartı: *"üstteki üç geometrik zırh kilitlendikten sonra,
  sıfırıncı mertebedeki baz durumu için NLL benzeri bir terim
  kullanılabilir; fakat bu terim tek başına değil, sadece son basamak
  olarak devreye girer."* Ağırlığı (``lam_nokta``) tahtta, görünürde
  ve küçüktür.
* Tek başına koşturulamaz: ``kulli_mizan`` onu daima öteki kefelerle
  toplar.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional, Sequence

import numpy as np

__all__ = ["kategori_kaybi", "nokta_kaybi"]


def kategori_kaybi(haller: Sequence[np.ndarray], azami: int = 32,
                   tohum: int = 0) -> Dict[str, Any]:
    """``‖M_{g∘f} − M_g·M_f‖²_F`` -- funktör kompozisyonunun ihlâli.

    ``haller`` ileri geçişin verdiği hâllerdir. ``azami`` kaç üçlü
    denenecektir; hepsini denemek ``O(m³)`` olurdu ve ana akışta
    Python döngüsü fermanla yasaktır -- üçlüler **tek hamlede** seçilir
    ve bütün Givens dönmeleri toplu kurulur.
    """
    from .kulli_mizan import givens
    m = len(haller)
    if m < 3:
        return {"kayıp": 0.0, "ihlâl": 0, "deneme": 0, "azamî": 0.0}
    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    H = H / np.maximum(np.linalg.norm(H, axis=-1, keepdims=True), 1e-300)
    r = np.random.default_rng(int(tohum))
    k = int(min(int(azami), m))
    ucluler = np.stack([r.choice(m, size=3, replace=False)
                        for _ in range(k)])
    toplam = 0.0
    ihlal = 0
    azami_fark = 0.0
    for idx in ucluler:
        a, b, c = (H[int(idx[0])], H[int(idx[1])], H[int(idx[2])])
        M_f = givens(a, b)
        M_g = givens(b, c)
        M_gf = givens(a, c)
        fark = M_gf - (M_g @ M_f)
        # Frobenius normunun **karesi**: ``Σ|·|²``. Karekök alınmaz --
        # zabıt ``‖·‖²_F`` yazıyor ve karekök gradyanı sıfırda tekil
        # yapardı.
        d2 = float(np.sum(np.abs(fark) ** 2))
        toplam += d2
        azami_fark = max(azami_fark, d2)
        if d2 > 1e-9:
            ihlal += 1
    n = float(len(ucluler))
    kayip = toplam / n
    assert math.isfinite(kayip), "kategori kaybı sonlu değil"
    assert kayip >= 0.0, "Frobenius normunun karesi negatif çıkamaz"
    return {"kayıp": float(kayip), "ihlâl": int(ihlal),
            "deneme": int(len(ucluler)), "azamî": float(azami_fark)}


def nokta_kaybi(lifliler: Sequence[np.ndarray], hedefler: Sequence[int],
                n_v: int, eps: float = 1e-12,
                cinsler: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """``−ln Tr(P_hedef · ρ)`` -- kısmî Born, **son basamak**.

    ``lifliler`` her örneğin ``(n_veri, n_hüküm)`` lifli görünümüdür.
    Belirteç lifi üstündeki indirgenmiş yoğunluk ``ρ = M Mᵀ*/Tr``;
    ``P_hedef`` ise ``|x_hedef⟩⟨x_hedef|``dir, o hâlde
    ``Tr(P ρ) = ρ_{hh}`` -- köşegenin **tek hücresi**.

    Köşegen dışı bütün faz bilgisi burada **okunmaz ama silinmez de**:
    bu terim öteki kefelerin yanında, küçük ağırlıkla toplanır.
    """
    assert len(lifliler) == len(hedefler), (
        "lifli sayısı %d, hedef sayısı %d -- örnek kayboldu"
        % (len(lifliler), len(hedefler)))
    if not lifliler:
        return {"kayıp": 0.0, "isabet": 0.0, "örnek": 0}
    M = np.stack([np.asarray(x, complex) for x in lifliler])   # (S, n_v, h)
    guc = np.einsum('svh,svh->sv', M, M.conj()).real           # (S, n_v)
    iz = np.maximum(guc.sum(axis=1), 1e-300)
    rho_kosegen = guc / iz[:, None]
    h = np.asarray(list(hedefler), np.int64) % int(n_v)
    p = rho_kosegen[np.arange(h.size), h]
    tekil = -np.log(np.maximum(p, float(eps)))
    tepe = np.argmax(rho_kosegen, axis=1) == h
    # ══════════════════════════════════════════════════════════════
    #  İKİ VERİ CİNSİ, TEK FORMÜL (ferman 1-R)
    # ══════════════════════════════════════════════════════════════
    #
    # Padişahın hükmü: *"iki farklı motor kurmuyoruz asla, sadece
    # motora girecek verinin cinsine göre bir ayrım yapıyoruz."*
    #
    # Formül **aynıdır** (``−ln P(hedef)``); değişen tek şey ağırlıktır
    # ve o da elle yazılmaz (ferman 1-J):
    #
    #   ARC       hedef **hariçten** gelir (bulmacanın test çıkışı) ve
    #             yüzde yüz uyum aranır → ağırlık ``1``.
    #   SÖZLÜ     hedef **kendindendir**: model okuduğunu yeniden
    #             üretir. Padişah *"tamamen çıktıyla ayniyet olmasa da
    #             bir nebze aynılık olmalı"* dedi; o "nebze" bir sabit
    #             olamaz. Ölçülen keyfiyet şudur: modelin sözlü
    #             örneklerde **fiilen tutturduğu nispet**. İyi
    #             ürettikçe terim ağırlık kazanır, üretemedikçe
    #             ötekileri ezmez -- kendi kendini ölçekler.
    if cinsler is None:
        agirlik = np.ones(h.size, float)
        pay = {"arc": int(h.size), "sözlü": 0}
    else:
        c = np.asarray([str(x) for x in cinsler])
        arc = np.char.startswith(c, "arc")
        soz = ~arc
        nebze = float(tepe[soz].mean()) if bool(soz.any()) else 0.0
        agirlik = np.where(arc, 1.0, nebze)
        pay = {"arc": int(arc.sum()), "sözlü": int(soz.sum()),
               "sözlü_nebze": nebze,
               "arc_isabet": (float(tepe[arc].mean())
                              if bool(arc.any()) else 0.0),
               "sözlü_isabet": (float(tepe[soz].mean())
                                if bool(soz.any()) else 0.0)}
    top = float(agirlik.sum())
    kayip = float((tekil * agirlik).sum() / max(top, 1e-300))
    assert math.isfinite(kayip), "nokta kaybı sonlu değil"
    # Tepe hücre hedefe düşüyor mu -- gradyansız bir teftiş sayısı.
    isabet = float(np.mean(tepe))
    return {"kayıp": kayip, "isabet": isabet, "örnek": int(h.size),
            "ortalama_born": float(np.mean(p)), "cins": pay}
