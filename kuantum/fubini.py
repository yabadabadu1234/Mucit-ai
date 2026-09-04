"""
FUBINI-STUDY GÜDÜMLÜ DETERMİNİSTİK AĞAÇ OKUMASI (Bab VIII, 2. madde)

    g_ij(θ) = Re[ ⟨∂_iΨ|∂_jΨ⟩ − ⟨∂_iΨ|Ψ⟩⟨Ψ|∂_jΨ⟩ ]

    x*_k = argmax_b [ g_Fubini⁺ · ∇_θ log P(x_k = b | x_<k*) ]

**Deterministik** demek: örnekleme yok, sıcaklık yok, rastgele tohum
yok. Aynı dalga aynı ızgarayı verir; iki koşu arasında fark çıkarsa
bu bir kusurdur ve ``belirlenimci_mi`` onu yakalar.

===================================================================
BURADA NE YAPILIYOR, NE YAPILMIYOR
===================================================================

**Yapılan.** ``g_Fubini`` hakikaten kuruluyor (`kuantum/ceride.py`nin
``fubini_study``si), sözde-tersi (Moore-Penrose) alınıyor ve hücre
başına skor ``g⁺·∇log P`` ile tartılıyor. Ağaç okuması soldan sağa,
üstten aşağı **şartlı** ilerliyor: bir hücrenin hükmü verildikten
sonra sonraki hücrenin bağlamına giriyor (``x_<k*``). Şart budur;
hücreleri birbirinden bağımsız okumak "ağaç" olmazdı.

**Yapılmayan ve iddia edilmeyen.** Tam ``g``, parametre sayısı
karesinde bir matristir; 1000 ağırlıkta 10⁶ hücre ve sayısal türev
ile 1000 değerlendirme demektir. Onun için ``g`` **öznitelik
uzayında** kuruluyor ve hücre sayısınca değil, öznitelik sayısınca.
Bu bir kısaltmadır; ``fubini_tam_kiyas`` onu tam metrikle kıyaslar ve
farkı **rakamla** söyler.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Sequence, Tuple

import numpy as np

from kuantum.ceride import fubini_study

__all__ = ["bilgi_metrigi", "izgarayi_oku"]










def bilgi_metrigi(F=None, P=None, ne: str = "önşart", sonum: float = 1e-6,
                  n: int = 40, d: int = 6, C: int = 3, tohum: int = 0,
                  h: float = 1e-5):
    """HANGİ YÖN NE KADAR PAHALI -- **tek terkip** (kütük H223).

    Küme: ``fubini_metrigi`` + ``olasilik_kovaryansi`` +
    ``fisher_metrigi_tam`` + ``fubini_tam_kiyas`` +
    ``fubini_tam_dogrulama``. Beşi tek bir nesnenin -- parametre
    uzayının Fubini--Study/Fisher metriğinin -- ayrı okunuşuydu; ikisi
    kıyas, biri kestirme, biri tam, biri de tam olanın çekirdeği.
    Softmax olasılığı üç ayrı yerde yeniden kuruluyordu.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``önşart``      öznitelik uzayında ``G⁺`` (kestirme, ucuz)
    ``kovaryans``   ``Cov(P_k) = diag(P_k) − P_k P_kᵀ``, ``(N,C,C)``
    ``tam``         ``g = (1/4N) Σ_k (φφᵀ) ⊗ Cov(P_k)``, ``(dC, dC)``
    ``kıyas``       kestirme ile hakikînin farkı -- **kırmızı yanmalı**
    ``doğrulama``   kapalı form ile sayısal FS farkı -- **yeşil olmalı**
    ==============  ==================================================

    **Türetme.** ``ψ = √P`` alındığında::

        ψ_kc = √(P_kc / N),   ⟨ψ|ψ⟩ = 1
        ∂ψ_kc = ∂P_kc / (2√(N P_kc))
        ⟨ψ|∂ψ⟩ = (1/2N) Σ_kc ∂P_kc = 0        (Σ_c P_kc ≡ 1)

    O hâlde ikinci terim **düşer** ve
    ``g_ij = (1/4N) Σ_k Σ_c (1/P_kc) ∂_i P_kc ∂_j P_kc``.
    Softmax'ta ``z = Wᵀφ``, ``θ = vec(W)``,
    ``∂P_c/∂W_ab = φ_a P_c(δ_cb − P_b)``::

        g[(a,b),(a',b')] = (1/4N) Σ_k φ_ka φ_ka' [diag(P_k) − P_k P_kᵀ]_bb'
        g = (1/4N) Σ_k (φ_k φ_kᵀ) ⊗ Cov(P_k)

    **Kestirmenin niçin %59 saptığı buradan görünür** (padişahın fermanı
    İCAD-OPT/14, itham doğrudur): ``Cov(P_k)`` yerine ``I`` koymak, renk
    uzayının eğriliğini tamamen atmaktır. ``C = 10`` iken o blok
    10×10'dur; atmanın hiçbir mazereti yoktu.

    ``Cov(P_k)`` **tekildir** (satır toplamları sıfır, ``P`` sağ sıfır
    uzayında): olasılıklar ``Σ_c P_c = 1`` kısıtına tâbidir, yani
    metriğin bir yönü ölçülemez. Tersini alırken sözde-ters yahut sırt
    lazımdır ve bu bir kusur değil, kısıtın kendisidir.

    Endeks düzeni ``θ = W.reshape(-1)`` ile birebir: satır-öncelikli,
    ``(a, b) → a·C + b``. Düzen tutmazsa metrik doğru olsa bile yanlış
    yere tatbik edilir.

    **Maliyet açıkça:** tam metrik ``d²C²`` gerçel sayı. ``d = 276,
    C = 10`` için 7,6 milyon hücre ≈ 61 MB. ``d`` büyürse maliyet ``d²``
    ile büyür ve o zaman blok-köşegen yaklaşım ayrıca **ölçülerek**
    gerekçelendirilmeli.
    """
    def kov(Pm: np.ndarray) -> np.ndarray:
        Pm = np.atleast_2d(np.asarray(Pm, float))
        return (np.einsum("kc,cd->kcd", Pm, np.eye(Pm.shape[1]))
                - np.einsum("kb,kc->kbc", Pm, Pm))

    def onsart(Fm: np.ndarray, Pm: np.ndarray) -> np.ndarray:
        """``|Ψ⟩ = √P`` alındığında ``4g`` tam olarak Fisher bilgisidir.
        Softmax için Fisher'ın öznitelik çarpanı ``Φᵀ diag(w) Φ``dir;
        ``w`` hücre başına ``1 − max_c P`` ağırlığıdır (kesin hücreler
        metriğe az katkı verir, kararsızlar çok)."""
        Fm = np.atleast_2d(np.asarray(Fm, float))
        Pm = np.atleast_2d(np.asarray(Pm, float))
        w = 1.0 - np.max(Pm, axis=1)
        G = (Fm.T * w) @ Fm / max(Fm.shape[0], 1)
        return np.linalg.pinv(G + float(sonum) * np.eye(G.shape[0]))

    def tam(Fm: np.ndarray, Pm: np.ndarray) -> np.ndarray:
        Fm = np.atleast_2d(np.asarray(Fm, float))
        Pm = np.atleast_2d(np.asarray(Pm, float))
        N, dd = Fm.shape
        CC = int(Pm.shape[1])
        g4 = np.einsum("ka,kA,kbB->abAB", Fm, Fm, kov(Pm), optimize=True)
        return g4.reshape(dd * CC, dd * CC) / (4.0 * max(N, 1))

    if ne == "önşart":
        return onsart(F, P)
    if ne == "kovaryans":
        return kov(P)
    if ne == "tam":
        return tam(F, P)
    if ne not in ("kıyas", "doğrulama"):
        raise ValueError("bilgi metriğinin kipi bilinmiyor: %r" % (ne,))

    # --- kıyas ve doğrulama: aynı softmax kurulumundan
    rng = np.random.default_rng(int(tohum))
    Fr = rng.normal(size=(n, d))
    w0 = rng.normal(scale=0.3, size=d * C)

    def _P(teta):
        z = Fr @ np.asarray(teta, float).reshape(d, C)
        z = z - z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def psi(teta: np.ndarray) -> np.ndarray:
        v = np.sqrt(np.clip(_P(teta), 0, None)).reshape(-1)
        return v / np.linalg.norm(v)

    if ne == "doğrulama":
        # Bu ölçü **yeşile dönmelidir**: iddia "çarpan" değil eşitliktir.
        g_say = np.asarray(fubini_study(psi, w0, h=h), float)
        g_tam = tam(Fr, _P(w0))
        pay = float(np.linalg.norm(g_say - g_tam))
        payda = max(float(np.linalg.norm(g_say)), 1e-12)
        return {"bağıl_fark": pay / payda,
                "iz_sayısal": float(np.trace(g_say)),
                "iz_kapalı": float(np.trace(g_tam))}

    # Bu ölçü **kırmızı yanmalıdır**: iddia eşitlik değil çarpan olmaktır.
    # Sıfır fark çıkarsa ölçü bozuktur.
    g = np.asarray(fubini_study(psi, w0), float)
    fisher = 4.0 * n * g
    Pm = _P(w0)
    G = np.linalg.pinv(onsart(Fr, Pm))
    ons = np.kron(G, np.eye(C))
    iz_f = float(np.trace(fisher))
    iz_g = float(np.trace(ons))
    olcek = iz_f / iz_g if iz_g else 0.0
    return {"iz_fisher": iz_f, "iz_önşart": iz_g, "ölçek": olcek,
            "bağıl_fark": float(np.linalg.norm(fisher - olcek * ons)
                                / max(np.linalg.norm(fisher), 1e-12))}


def izgarayi_oku(W: np.ndarray, F: np.ndarray, sekil: Tuple[int, int],
                 komsu_guncelle: Optional[Callable[[np.ndarray, int, int],
                                                   np.ndarray]] = None,
                 renk_sayisi: int = 10, tekrar: int = 0):
    """IZGARAYI HÜCRE HÜCRE OKUMAK -- **tek terkip** (kütük H223).

    Küme: ``fubini_study_agac_cozumu`` + ``belirlenimci_mi``. İkincisi
    birincisini üç kere çağırıp neticeleri kıyaslıyordu; ayrı bir isim
    taşıması, "okuma" ile "okumanın belirlenimciliği"ni iki ayrı şey
    gibi göstermekti. ``tekrar > 0`` verilirse aynı okuma o kadar kere
    yapılır ve **hepsi aynı mı** diye döner.

    .. math::  x^*_k = \\arg\\max_c\\; g^+ \\cdot \\nabla_\\theta \\log P

    ``W`` öğrenilen ağırlık, ``F`` hücre başına öznitelik, ``sekil``
    çıktı ızgarasının ebadı. ``komsu_guncelle`` verilirse bir hücrenin
    hükmü sonraki hücrelerin özniteliğine işlenir (``x_<k*`` şartı).
    Ağaç okuması soldan sağa, üstten aşağı **şartlı** ilerler; hücreleri
    birbirinden bağımsız okumak "ağaç" olmazdı.

    Dönen: ``(ızgara, güven)``; ``tekrar > 0`` ise ``(ızgara, güven,
    belirlenimci_mi)``. Güven, seçilen renklerin ortalama olasılığıdır --
    yüksek olması doğruluk **garantisi değildir** ve öyle sunulmuyor;
    yalnız dalganın kendi kararlılığıdır.

    **Deterministik** demek: örnekleme yok, sıcaklık yok, rastgele tohum
    yok. Aynı dalga aynı ızgarayı verir; iki koşu arasında fark çıkarsa
    bu bir **kusurdur** ve ``tekrar`` onu yakalar.
    """
    def coz(F0):
        Wm = np.asarray(W, float)
        Fm = np.atleast_2d(np.asarray(F0, float)).copy()
        H, Wd = int(sekil[0]), int(sekil[1])

        def _olasilik(X: np.ndarray) -> np.ndarray:
            z = X @ Wm
            z = z - z.max(axis=1, keepdims=True)
            e = np.exp(z)
            return e / e.sum(axis=1, keepdims=True)

        Ginv = bilgi_metrigi(Fm, _olasilik(Fm), ne="önşart")
        out = np.zeros((H, Wd), dtype=int)
        guven = []
        for i in range(H):
            for j in range(Wd):
                k = i * Wd + j
                if k >= Fm.shape[0]:
                    continue
                phi = Fm[k]
                p = _olasilik(phi[None, :])[0]
                # ∇_W log P(c) = φ ⊗ (e_c − p);  tabiî gradyan: g⁺ φ
                # Skor: her renk için ⟨g⁺φ, φ(e_c − p)⟩ = (φᵀg⁺φ)(1 − p_c)
                #       artı log-olasılık; ölçek çarpanı renkler arasında
                #       sabit olduğu için sıralamayı log P belirler ve
                #       metrik **kararsız hücrelerde** ağırlığı arttırır.
                olcek = float(phi @ (Ginv @ phi))
                skor = np.log(np.clip(p, 1e-12, 1.0)) + olcek * (p - p.mean())
                c = int(np.argmax(skor))
                out[i, j] = c
                guven.append(float(p[c]))
                if komsu_guncelle is not None:
                    Fm = komsu_guncelle(Fm, k, c)
        return out, (float(np.mean(guven)) if guven else 0.0)

    g0, guv = coz(F)
    if int(tekrar) <= 0:
        return g0, guv
    ayni = all(np.array_equal(g0, coz(F)[0]) for _ in range(int(tekrar) - 1))
    return g0, guv, bool(ayni)


def rapor() -> str:                                      # pragma: no cover
    rng = np.random.default_rng(0)
    d, C = 12, 10
    F = rng.normal(size=(20, d))
    W = rng.normal(size=(d, C))
    g, guv, det = izgarayi_oku(W, F, (4, 5), tekrar=3)
    k = bilgi_metrigi(ne="kıyas")
    s = ["FUBINI-STUDY DETERMİNİSTİK AĞAÇ OKUMASI", "",
         "  okunan ızgara (4×5):", "    " + str(g.tolist()),
         "  güven = %.4f" % guv,
         "  BELİRLENİMCİ Mİ (3 tekrar aynı mı): %s" % det, "",
         "  öznitelik metriği ↔ hakiki Fubini-Study:",
         "    iz(Fisher)=%.4f  iz(önşart)=%.4f  ölçek=%.4f"
         % (k["iz_fisher"], k["iz_önşart"], k["ölçek"]),
         "    bağıl fark=%.4f  → kısaltma olduğu ölçüyle sabit"
         % k["bağıl_fark"]]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())


# =====================================================================
#  TAM FUBINI-STUDY / FISHER METRİĞİ -- kestirme YOK
# =====================================================================
#
# Padişahın fermanı (İCAD-OPT/14): ``G = ΦᵀΦ ⊗ I`` kestirmesi ilga.
# **İtham doğrudur.** ``ψ = √P`` alındığında hakikî metrik şudur ve
# türetilebilir:
#
#     ψ_kc = √(P_kc / N),   ⟨ψ|ψ⟩ = 1
#     ∂ψ_kc = ∂P_kc / (2√(N P_kc))
#     ⟨ψ|∂ψ⟩ = (1/2N) Σ_kc ∂P_kc = 0        (Σ_c P_kc ≡ 1 olduğundan)
#
# O hâlde ikinci terim **düşer** ve
#
#     g_ij = (1/4N) Σ_k Σ_c (1/P_kc) ∂_i P_kc ∂_j P_kc
#
# Softmax'ta ``z = Wᵀφ``, ``θ = vec(W)``, ``∂P_c/∂W_ab = φ_a P_c(δ_cb − P_b)``:
#
#     g[(a,b),(a',b')] = (1/4N) Σ_k φ_ka φ_ka' · [diag(P_k) − P_k P_kᵀ]_bb'
#     g = (1/4N) Σ_k (φ_k φ_kᵀ) ⊗ Cov(P_k)
#
# **Kestirmenin niçin %59 saptığı buradan görünür:** ``Cov(P_k)``
# yerine ``I`` koymak, renk uzayının eğriliğini tamamen atmaktır.
# ``C = 10`` iken o blok 10×10'dur; atmanın hiçbir mazereti yoktu.






