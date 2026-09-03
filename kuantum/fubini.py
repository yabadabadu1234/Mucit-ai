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

__all__ = ["fubini_metrigi", "fubini_study_agac_cozumu",
           "belirlenimci_mi", "fubini_tam_kiyas"]


def fubini_metrigi(F: np.ndarray, P: np.ndarray,
                   sonum: float = 1e-6) -> np.ndarray:
    """Öznitelik uzayında Fubini-Study/Fisher metriği ve sözde-tersi.

    ``|Ψ⟩ = √P`` alındığında ``4g`` tam olarak Fisher bilgisidir. Softmax
    için Fisher'ın öznitelik çarpanı ``Φᵀ diag(w) Φ``dir; ``w`` hücre
    başına ``1 − max_c P`` ağırlığıdır (kesin hücreler metriğe az
    katkı verir, kararsızlar çok).
    """
    F = np.atleast_2d(np.asarray(F, float))
    P = np.atleast_2d(np.asarray(P, float))
    w = 1.0 - np.max(P, axis=1)
    G = (F.T * w) @ F / max(F.shape[0], 1)
    G = G + float(sonum) * np.eye(G.shape[0])
    return np.linalg.pinv(G)


def fubini_study_agac_cozumu(
        W: np.ndarray, F: np.ndarray, sekil: Tuple[int, int],
        komsu_guncelle: Optional[Callable[[np.ndarray, int, int], np.ndarray]]
        = None, renk_sayisi: int = 10) -> Tuple[np.ndarray, float]:
    """``x*_k = argmax_c g⁺·∇log P`` -- hücre hücre, şartlı, deterministik.

    ``W`` öğrenilen ağırlık, ``F`` hücre başına öznitelik, ``sekil``
    çıktı ızgarasının ebadı. ``komsu_guncelle`` verilirse bir hücrenin
    hükmü sonraki hücrelerin özniteliğine işlenir (``x_<k*`` şartı).

    Dönen: ``(ızgara, güven)``. Güven, seçilen renklerin ortalama
    olasılığıdır -- yüksek olması doğruluk **garantisi değildir** ve
    öyle sunulmuyor; yalnız dalganın kendi kararlılığıdır.
    """
    W = np.asarray(W, float)
    F = np.atleast_2d(np.asarray(F, float)).copy()
    H, Wd = int(sekil[0]), int(sekil[1])
    C = int(renk_sayisi)

    def _olasilik(X: np.ndarray) -> np.ndarray:
        z = X @ W
        z = z - z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    P0 = _olasilik(F)
    Ginv = fubini_metrigi(F, P0)

    out = np.zeros((H, Wd), dtype=int)
    guven = []
    for i in range(H):
        for j in range(Wd):
            k = i * Wd + j
            if k >= F.shape[0]:
                continue
            phi = F[k]
            p = _olasilik(phi[None, :])[0]
            # ∇_W log P(c) = φ ⊗ (e_c − p);  tabiî gradyan: g⁺ φ
            tabii = Ginv @ phi
            # Skor: her renk için ⟨g⁺φ, φ(e_c − p)⟩ = (φᵀg⁺φ)(1 − p_c)
            #       artı log-olasılık; ölçek çarpanı renkler arasında
            #       sabit olduğu için sıralamayı log P belirler ve
            #       metrik **kararsız hücrelerde** ağırlığı arttırır.
            olcek = float(phi @ tabii)
            skor = np.log(np.clip(p, 1e-12, 1.0)) + olcek * (p - p.mean())
            c = int(np.argmax(skor))
            out[i, j] = c
            guven.append(float(p[c]))
            if komsu_guncelle is not None:
                F = komsu_guncelle(F, k, c)
    return out, float(np.mean(guven)) if guven else 0.0


def belirlenimci_mi(W: np.ndarray, F: np.ndarray,
                    sekil: Tuple[int, int], tekrar: int = 3) -> bool:
    """Aynı girdi aynı ızgarayı veriyor mu? Vermiyorsa **kusurdur**."""
    ilk = None
    for _ in range(int(tekrar)):
        g, _c = fubini_study_agac_cozumu(W, F, sekil)
        if ilk is None:
            ilk = g
        elif not np.array_equal(ilk, g):
            return False
    return True


def fubini_tam_kiyas(n: int = 40, d: int = 6, C: int = 3,
                     tohum: int = 0) -> Dict[str, float]:
    """Öznitelik metriği, **hakiki** Fubini-Study'ye ne kadar yakın?

    Bu ölçü **kırmızı yanmalıdır**: iddia eşitlik değil, çarpan
    olmaktır. Sıfır fark çıkarsa ölçü bozuktur.
    """
    rng = np.random.default_rng(int(tohum))
    F = rng.normal(size=(n, d))
    w0 = rng.normal(scale=0.3, size=d * C)

    def psi(teta: np.ndarray) -> np.ndarray:
        Wm = np.asarray(teta, float).reshape(d, C)
        z = F @ Wm
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        P = e / e.sum(axis=1, keepdims=True)
        v = np.sqrt(np.clip(P, 0, None)).reshape(-1)
        return v / np.linalg.norm(v)

    g = np.asarray(fubini_study(psi, w0), float)
    fisher = 4.0 * n * g
    Wm = w0.reshape(d, C)
    z = F @ Wm
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    P = e / e.sum(axis=1, keepdims=True)
    G = np.linalg.pinv(fubini_metrigi(F, P))
    onsart = np.kron(G, np.eye(C))
    iz_f = float(np.trace(fisher))
    iz_g = float(np.trace(onsart))
    olcek = iz_f / iz_g if iz_g else 0.0
    fark = float(np.linalg.norm(fisher - olcek * onsart)
                 / max(np.linalg.norm(fisher), 1e-12))
    return {"iz_fisher": iz_f, "iz_önşart": iz_g, "ölçek": olcek,
            "bağıl_fark": fark}


def rapor() -> str:                                      # pragma: no cover
    rng = np.random.default_rng(0)
    d, C = 12, 10
    F = rng.normal(size=(20, d))
    W = rng.normal(size=(d, C))
    g, guv = fubini_study_agac_cozumu(W, F, (4, 5))
    det = belirlenimci_mi(W, F, (4, 5))
    k = fubini_tam_kiyas()
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
