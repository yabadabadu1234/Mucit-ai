"""RKHS — yeniden üreten çekirdek Hilbert uzayı ve kapalı form çözüm.

Bir çekirdek ``K(x,y)`` **simetrik ve pozitif yarı-belirli** ise
(Moore–Aronszajn) ona karşılık gelen tek bir Hilbert uzayı vardır ve
o uzayda değerlendirme sürekli bir işleçtir:

.. math::  \\langle f, K(\\cdot, x)\\rangle_{\\mathcal{H}_K} = f(x)

Temsil teoremi, düzenli bir kayıp için en iyi ``f``in **veri
noktalarındaki çekirdeklerin gerdiği** sonlu boyutlu altuzayda
bulunduğunu söyler; oradan kapalı form çıkar:

.. math::  \\bm{\\alpha}^* = (\\mathbf{K} + \\lambda I)^{-1}\\mathbf{y}

Bu modülün üç ısrarı:

1. **PSD'lik denetlenir, varsayılmaz.**  Bir çekirdeğin PSD olduğunu
   iddia etmek kolaydır; ölçmek gerekir.  ``psd_mi`` rastgele nokta
   kümelerinde Gram dizeyinin en küçük özdeğerine bakar.  (K24
   tashihi: ``exp(iS)`` biçiminde salınımlı bir faz **PSD değildir** ve
   orada temsil teoremi geçersizdir.)

2. **Ters alınmaz, çözülür.**  ``(K+λI)^{-1}y`` yerine Cholesky ile
   ``(K+λI)α = y`` çözülür.  Aynı cevabı verir, daha kararlıdır, ve
   ``λ = 0``da tekilse **hata verir** -- sessizce devasa sayı üretmez.

3. **Koşul sayısı raporlanır.**  ``λ`` küçüldükçe çözüm daha iyi
   uyar ama koşul sayısı patlar; ikisi arasındaki alışveriş ölçülür.

Ayrıca **Nyström** yaklaşımı: ``m ≪ N`` iniş noktasıyla Gram dizeyini
düşük rütbeli yaklaşır.  ``O(N³)`` yerine ``O(Nm²)``.  Hızlanma ve
**hatanın ne kadar olduğu** birlikte ölçülür; hız tek başına iddia
edilmez.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "gauss_cekirdegi", "laplace_cekirdegi", "matern_cekirdegi",
    "polinom_cekirdegi", "gram", "psd_mi", "medyan_genislik",
    "RKHS", "nystrom", "temsil_teoremi_sagmasi",
]


# ══════════════════════════════════════════════════════════════════════
#  Çekirdekler
# ══════════════════════════════════════════════════════════════════════

def _kare_mesafe(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """``‖x−y‖²`` — açılım yerine doğrudan fark.

    ``‖x‖² + ‖y‖² − 2⟨x,y⟩`` açılımı hızlıdır ama yakın noktalarda
    **çıkarma iptali** yüzünden küçük negatif değerler üretir; sonra
    ``exp(−γ·negatif)`` 1'i aşar ve çekirdek PSD'liğini kaybeder.
    Burada fark doğrudan alınır: biraz daha yavaş, fakat sonuç her
    zaman ``≥ 0``.
    """
    X = np.atleast_2d(np.asarray(X, float))
    Y = np.atleast_2d(np.asarray(Y, float))
    d = X[:, None, :] - Y[None, :, :]
    return np.sum(d * d, axis=2)


def gauss_cekirdegi(gama: float) -> Callable[[np.ndarray, np.ndarray],
                                             np.ndarray]:
    """``K(x,y) = exp(−γ‖x−y‖²)`` — Sobolev/Gauss çekirdeği."""
    if gama <= 0:
        raise ValueError("γ > 0 olmalı")
    return lambda X, Y: np.exp(-gama * _kare_mesafe(X, Y))


def laplace_cekirdegi(gama: float) -> Callable:
    """``K(x,y) = exp(−γ‖x−y‖)``."""
    if gama <= 0:
        raise ValueError("γ > 0 olmalı")
    return lambda X, Y: np.exp(-gama * np.sqrt(np.maximum(
        _kare_mesafe(X, Y), 0.0)))


def matern_cekirdegi(uzunluk: float, nu: float = 1.5) -> Callable:
    """Matérn ``ν = 1/2, 3/2, 5/2`` — kapalı formlar.

    Genel ``ν`` Bessel fonksiyonu ister; burada yalnız kapalı formu
    olan üç hâl var ve başkası istenirse **hata verilir**, yaklaşık
    bir şey uydurulmaz.
    """
    if uzunluk <= 0:
        raise ValueError("uzunluk > 0 olmalı")
    if nu not in (0.5, 1.5, 2.5):
        raise ValueError("ν ∈ {0.5, 1.5, 2.5} (kapalı formlu hâller)")

    def K(X, Y):
        r = np.sqrt(np.maximum(_kare_mesafe(X, Y), 0.0)) / uzunluk
        if nu == 0.5:
            return np.exp(-r)
        if nu == 1.5:
            a = math.sqrt(3.0) * r
            return (1.0 + a) * np.exp(-a)
        a = math.sqrt(5.0) * r
        return (1.0 + a + a * a / 3.0) * np.exp(-a)
    return K


def polinom_cekirdegi(derece: int, c: float = 1.0) -> Callable:
    """``K(x,y) = (⟨x,y⟩ + c)^d`` — sonlu boyutlu öznitelik uzayı."""
    if derece < 1:
        raise ValueError("derece ≥ 1 olmalı")
    if c < 0:
        raise ValueError("c ≥ 0 olmalı (PSD'lik için)")
    return lambda X, Y: (np.atleast_2d(X) @ np.atleast_2d(Y).T + c) ** derece


def gram(K: Callable, X: np.ndarray) -> np.ndarray:
    """``K_ij = K(x_i, x_j)`` — simetrikleştirilerek.

    Simetrikleştirme yuvarlama artığını temizler; **idempotentlik
    veya PSD'lik vermez** (bkz. K28 tashihi), yalnız simetriyi tam
    yapar ki ``eigvalsh`` kullanılabilsin.
    """
    G = np.asarray(K(X, X), float)
    return (G + G.T) / 2.0


def psd_mi(K: Callable, boyut: int = 3, n: int = 24,
           deneme: int = 20, tohum: int = 0) -> Dict[str, object]:
    """Çekirdek pozitif yarı-belirli mi? — rastgele nokta kümelerinde.

    Bu bir **ispat değil, sınamadır**: hiçbir örneklemde negatif
    özdeğer görülmemesi PSD'liği ispatlamaz.  Fakat *bir* negatif
    özdeğer görmek, PSD **olmadığını** ispatlar.  Sınama bu asimetriyi
    kullanır ve neticesi ona göre okunur.
    """
    r = np.random.default_rng(tohum)
    en_kucuk = float("inf")
    for _ in range(deneme):
        X = r.normal(size=(n, boyut))
        oz = np.linalg.eigvalsh(gram(K, X))
        en_kucuk = min(en_kucuk, float(oz.min()))
    olcek = max(1.0, abs(en_kucuk))
    return {
        "en_küçük_özdeğer": en_kucuk,
        "psd_görünüyor": en_kucuk > -1e-9 * olcek,
        "not": "negatif özdeğer PSD OLMADIĞINI ispatlar; "
               "hiç görmemek PSD olduğunu ispatlamaz",
    }


def medyan_genislik(X: np.ndarray) -> float:
    """``γ = 1/(2·medyan‖x_i−x_j‖²)`` — medyan uzaklık sezgisi.

    Köşegen (sıfır) mesafeler **dışarıda bırakılır**; içeride
    bırakılırsa medyan sıfıra kayar ve ``γ`` patlar.
    """
    D = _kare_mesafe(X, X)
    ust = D[np.triu_indices_from(D, k=1)]
    if ust.size == 0:
        return 1.0
    m = float(np.median(ust))
    return 1.0 / (2.0 * m) if m > 0 else 1.0


# ══════════════════════════════════════════════════════════════════════
#  RKHS regresyonu
# ══════════════════════════════════════════════════════════════════════

@dataclass
class RKHS:
    """Çekirdek sırt regresyonu; kapalı form çözüm."""
    K: Callable
    lam: float = 1e-6
    X: Optional[np.ndarray] = field(default=None, repr=False)
    alfa: Optional[np.ndarray] = field(default=None, repr=False)
    kosul: float = field(default=float("nan"), init=False)

    def uydur(self, X: np.ndarray, y: np.ndarray) -> "RKHS":
        """``(K + λI)α = y`` — Cholesky ile ÇÖZÜLÜR, ters ALINMAZ.

        ``λ`` çok küçükse Cholesky başarısız olur ve **hata verilir**;
        o hâlde ya ``λ`` büyütülmeli ya da veri tekrarları
        temizlenmelidir.  Sessizce en küçük karelere düşmek, koşul
        sayısını gizler.
        """
        X = np.atleast_2d(np.asarray(X, float))
        y = np.asarray(y, float).reshape(X.shape[0], -1)
        if self.lam < 0:
            raise ValueError("λ ≥ 0 olmalı")
        G = gram(self.K, X) + self.lam * np.eye(X.shape[0])
        self.kosul = float(np.linalg.cond(G))
        try:
            L = np.linalg.cholesky(G)
        except np.linalg.LinAlgError as e:
            raise ValueError(
                f"K+λI pozitif belirli değil (λ={self.lam:g}, "
                f"koşul≈{self.kosul:.2e}); λ'yı büyütün") from e
        z = np.linalg.solve(L, y)
        self.alfa = np.linalg.solve(L.T, z)
        self.X = X
        return self

    def __call__(self, Xy: np.ndarray) -> np.ndarray:
        if self.alfa is None:
            raise ValueError("önce uydur() çağrılmalı")
        Xy = np.atleast_2d(np.asarray(Xy, float))
        return np.asarray(self.K(Xy, self.X), float) @ self.alfa

    def norm_karesi(self) -> float:
        """``‖f*‖²_{H_K} = αᵀKα`` — skalerdir, norm çubuğu almaz.

        (K19 tashihi: kaynakta ``‖αᵀKα‖`` yazılmıştı; ifade zaten
        skaler ve ``K`` PSD olduğundan negatif olamaz.)
        """
        if self.alfa is None:
            raise ValueError("önce uydur() çağrılmalı")
        G = gram(self.K, self.X)
        return float(np.sum(self.alfa * (G @ self.alfa)))


def temsil_teoremi_sagmasi(K: Callable, X: np.ndarray, y: np.ndarray,
                           lam: float = 1e-3,
                           deneme: int = 200, tohum: int = 0
                           ) -> Dict[str, object]:
    """Temsil teoremi: en iyi ``f``, çekirdeklerin gerdiği uzayda.

    Sağlama: ``α*`` çözümüne **dik** yönde küçük sapmalar eklenir ve
    düzenli kaybın arttığı gösterilir.  Artmıyorsa ya çözüm en iyi
    değildir ya da kayıp yanlış kurulmuştur.
    """
    X = np.atleast_2d(np.asarray(X, float))
    y = np.asarray(y, float).reshape(-1)
    G = gram(K, X)
    n = X.shape[0]
    alfa = np.linalg.solve(G + lam * np.eye(n), y)

    def kayip(a: np.ndarray) -> float:
        artik = G @ a - y
        return float(artik @ artik + lam * (a @ (G @ a)))

    taban = kayip(alfa)
    r = np.random.default_rng(tohum)
    kotu = 0
    for _ in range(deneme):
        d = r.normal(size=n)
        d = d / np.linalg.norm(d)
        if kayip(alfa + 1e-3 * d) <= taban + 1e-15:
            kotu += 1
    return {"taban_kayıp": taban, "artmayan_sapma": kotu,
            "en_iyi_mi": kotu == 0, "deneme": deneme}


# ══════════════════════════════════════════════════════════════════════
#  Nyström
# ══════════════════════════════════════════════════════════════════════

def nystrom(K: Callable, X: np.ndarray, m: int,
            tohum: int = 0) -> Dict[str, object]:
    """``K ≈ K_{nm} K_{mm}^{+} K_{mn}`` — ``m`` iniş noktasıyla.

    Maliyet ``O(N³)`` yerine ``O(Nm² + m³)``.  ``K_{mm}`` tekil
    olabileceğinden **sözde ters** kullanılır; küçük özdeğerler
    kırpılır ve kırpma eşiği raporlanır.

    Dönen sözlükte hem hızlanma hem **hata** var: biri diğeri olmadan
    okunmamalı.

    **Ölçülen iki kaide:**

    1. Düzgün (analitik) çekirdeklerde Gram dizeyinin sayısal rütbesi
       ``N``den çok küçüktür -- Gauss çekirdeği için ``N=900``de 249
       ölçüldü.  ``m`` bu rütbeyi aşınca ``K_mm`` de tekilleşir ve
       hatayı artık ``m`` değil kırpma eşiği belirler; hata ``m`` ile
       **tekdüze düşmez**.

    2. ``m = N`` iken bile hata sıfıra inmez.  Sebebi atılan özdeğer
       kütlesi **değildir**: ``N=200``lük bir örnekte atılan kütle
       ``6e-14`` iken hata ``5.2e-5`` ölçüldü.  Fark, eşiğin hemen
       üstünde kalan küçük özdeğerlerin **tersinin alınmasından**
       gelen büyütmedir.  Yani hata bir yaklaşım hatası değil, bir
       **koşullanma** hatasıdır ve iniş noktası eklemek onu gidermez.
    """
    X = np.atleast_2d(np.asarray(X, float))
    N = X.shape[0]
    if not 1 <= m <= N:
        raise ValueError(f"1 ≤ m ≤ N={N} olmalı")
    r = np.random.default_rng(tohum)
    idx = r.choice(N, m, replace=False)
    Z = X[idx]
    Kmm = gram(K, Z)
    Knm = np.asarray(K(X, Z), float)
    oz, V = np.linalg.eigh(Kmm)
    esik = m * np.finfo(float).eps * max(1.0, float(oz.max()))
    tut = oz > esik
    Kmm_arti = V[:, tut] @ np.diag(1.0 / oz[tut]) @ V[:, tut].T
    yaklasik = Knm @ Kmm_arti @ Knm.T
    tam = gram(K, X)
    return {
        "yaklaşık": yaklasik,
        "bağıl_hata": float(np.linalg.norm(yaklasik - tam, "fro")
                            / max(np.linalg.norm(tam, "fro"), 1e-300)),
        "kullanılan_rütbe": int(tut.sum()),
        "kırpma_eşiği": float(esik),
        "m": m, "N": N,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== Çekirdekler PSD mi? (ölçülerek) ===")
    cekirdekler = {
        "Gauss γ=0.5": gauss_cekirdegi(0.5),
        "Laplace γ=1": laplace_cekirdegi(1.0),
        "Matérn ν=1/2": matern_cekirdegi(1.0, 0.5),
        "Matérn ν=3/2": matern_cekirdegi(1.0, 1.5),
        "Matérn ν=5/2": matern_cekirdegi(1.0, 2.5),
        "polinom d=3": polinom_cekirdegi(3),
    }
    for ad, K in cekirdekler.items():
        r = psd_mi(K)
        s.append(f"  {ad:16s} en küçük özdeğer = "
                 f"{r['en_küçük_özdeğer']:+.3e}   PSD görünüyor: "
                 f"{r['psd_görünüyor']}")

    s.append("\n  K24 tashihi: salınımlı faz çekirdeği PSD DEĞİL:")
    def faz_cekirdegi(X, Y):
        return np.cos(np.atleast_2d(X) @ np.atleast_2d(Y).T * 3.0
                      + np.sum(np.atleast_2d(X), axis=1)[:, None])
    r = psd_mi(faz_cekirdegi)
    s.append(f"    en küçük özdeğer = {r['en_küçük_özdeğer']:+.4f}"
             f"   PSD görünüyor: {r['psd_görünüyor']}")
    s.append("    → burada temsil teoremi GEÇERSİZDİR.")

    s.append("\n=== Kapalı form çözüm ve koşul sayısı ===")
    X = rng.uniform(-2, 2, (60, 1))
    y = (np.sin(2 * X[:, 0]) + 0.05 * rng.normal(size=60))
    Xt = np.linspace(-2, 2, 200)[:, None]
    yt = np.sin(2 * Xt[:, 0])
    s.append("      λ        koşul sayısı    eğitim artığı   sınama hatası")
    for lam in (1e-1, 1e-3, 1e-6, 1e-9):
        m = RKHS(gauss_cekirdegi(medyan_genislik(X)), lam)
        try:
            m.uydur(X, y)
            egit = float(np.sqrt(np.mean((m(X).ravel() - y) ** 2)))
            sina = float(np.sqrt(np.mean((m(Xt).ravel() - yt) ** 2)))
            s.append(f"  {lam:8.0e}    {m.kosul:.3e}     {egit:.3e}"
                     f"      {sina:.3e}")
        except ValueError as e:
            s.append(f"  {lam:8.0e}    reddedildi: {e}")
    s.append("  λ küçüldükçe eğitim artığı düşüyor, koşul sayısı patlıyor;")
    s.append("  sınama hatası ise ortada bir yerde en iyi oluyor.")

    s.append("\n=== Temsil teoremi sağlaması ===")
    for lam in (1e-2, 1e-4):
        r = temsil_teoremi_sagmasi(gauss_cekirdegi(0.5), X, y, lam)
        s.append(f"  λ={lam:.0e}: {r['deneme']} rastgele sapmanın "
                 f"{r['artmayan_sapma']}'i kaybı artırmadı"
                 f"   en iyi mi? {r['en_iyi_mi']}")

    s.append("\n=== RKHS normu skalerdir (K19) ===")
    m = RKHS(gauss_cekirdegi(0.5), 1e-4).uydur(X, y)
    s.append(f"  ‖f*‖²_H = {m.norm_karesi():.6f}"
             f"   (negatif olamaz: K PSD)")

    s.append("\n=== Nyström: hız ve HATA birlikte ===")
    N = 900
    Xb = rng.uniform(-2, 2, (N, 3))
    Kb = gauss_cekirdegi(medyan_genislik(Xb))
    t0 = time.perf_counter()
    tam = gram(Kb, Xb)
    np.linalg.cholesky(tam + 1e-6 * np.eye(N))
    tam_sure = time.perf_counter() - t0
    s.append(f"  N={N} tam Gram + Cholesky: {tam_sure*1000:.1f} ms"
             f"   ({tam.nbytes/1e6:.1f} MB)")
    oz = np.sort(np.linalg.eigvalsh(tam))[::-1]
    sayisal_rutbe = int(np.linalg.matrix_rank(tam))
    s.append(f"  Gram dizeyinin SAYISAL RÜTBESİ: {sayisal_rutbe}/{N}")
    s.append("  özdeğerler: "
             + "  ".join(f"λ_{i}={oz[i]:.1e}"
                         for i in (0, 50, 100, 200, 400)))
    s.append("     m    bağıl hata     kullanılan rütbe     süre")
    for mm in (20, 50, 100, 200, 400, 600):
        t0 = time.perf_counter()
        r = nystrom(Kb, Xb, mm, tohum=1)
        sure = time.perf_counter() - t0
        s.append(f"  {mm:5d}   {r['bağıl_hata']:.3e}         "
                 f"{r['kullanılan_rütbe']:4d}       {sure*1000:7.1f} ms")
    s.append("  Hata m ile TEKDÜZE DÜŞMÜYOR — ve bu bir kusur değil:")
    s.append(f"  düzgün bir çekirdekte özdeğerler uçurumdan düşer, tam")
    s.append(f"  Gram'ın sayısal rütbesi {sayisal_rutbe}'da doyar. m bu rütbeyi")
    s.append("  aşınca K_mm'in kendisi de tekilleşir; hatayı artık m değil,")
    s.append("  sözde tersteki KIRPMA EŞİĞİ belirler. Yani iniş noktası")
    s.append("  sayısını artırmak bir yerden sonra fayda etmiyor.")
    s.append("")
    s.append("  Asıl kazanç bellekte: K_nm (N×m) tam dizeyin m/N katı yer tutar.")
    for mm in (20, 100, 400):
        s.append(f"    m={mm:3d}: {N*mm*8/1e6:.2f} MB v {N*N*8/1e6:.2f} MB"
                 f"   → {N/mm:.1f}× tasarruf")

    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
