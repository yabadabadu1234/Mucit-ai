"""FAZLALIK -- terkipten sonra artakalan asıllar (kütük H221).

Bu dosya çalışmaz, çağrılmaz; yalnız terkibin neyi yuttuğunu

gösteren şahittir. Aslı: nefs/melekeler.py, 4fe86e9.
"""

from __future__ import annotations
import numpy as np
from typing import Tuple


def softmax(x: np.ndarray, eksen: int = -1) -> np.ndarray:
    z = x - np.max(x, axis=eksen, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=eksen, keepdims=True)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))


def gelu(x: np.ndarray) -> np.ndarray:
    """Tam (hata fonksiyonlu) GELU değil, tanh yaklaşığı -- kaynak metnin
    ``GELU`` yazdığı her yerde bu kullanılır."""
    return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * x ** 3)))


def kat_norm(x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """LayerNorm (öğrenilen ölçek/kayma yok)."""
    mu = np.mean(x, axis=-1, keepdims=True)
    sd = np.std(x, axis=-1, keepdims=True)
    return (x - mu) / (sd + eps)


def kosinus(a: np.ndarray, b: np.ndarray) -> float:
    pay = float(np.sum(a * b))
    payda = float(np.linalg.norm(a) * np.linalg.norm(b))
    return pay / payda if payda > 1e-12 else 0.0


def nicele(x: np.ndarray, adim: float) -> np.ndarray:
    """``Quantize(·, Δ_ızgara)``."""
    return np.round(x / adim) * adim


def guvenli_bol(a: float, b: float, eps: float = 1e-9) -> float:
    return float(a / (b + eps))


def _betti0(v: np.ndarray, esik: float = 0.35) -> int:
    """Zincir üzerinde bağlantılı bileşen sayısı -- ``O(n)``.

    Zincirde çizge yalnız komşu kenarlardan ibarettir; bileşen sayısı,
    kopmuş komşuluk sayısının bir fazlasıdır. ``n×n`` bitişiklik dizeyi
    **hiç kurulmaz** -- 𝒪₅ Tecrit'te o dizey 65 536 düğümde 32 GiB
    istemişti; burada o hata tekrarlanmaz.
    """
    if len(v) < 2:
        return 1
    fark = np.abs(np.diff(v))
    olcek = float(np.median(fark)) + 1e-12
    return 1 + int(np.sum(fark > esik + 3.0 * olcek))


def normalize_laplasyen(A: np.ndarray) -> np.ndarray:
    """``Δ = I − D^{-1/2} A D^{-1/2}``. Yalıtık düğümlerde ``D=0``;
    orada ``D^{-1/2}`` yerine 0 alınır (kanonik ihtiyat)."""
    derece = A.sum(1)
    inv = np.where(derece > 0, 1.0 / np.sqrt(np.maximum(derece, 1e-12)), 0.0)
    return np.eye(len(A)) - (inv[:, None] * A * inv[None, :])


def betti_1iskelet(A: np.ndarray) -> Tuple[int, int]:
    """Basit çizgenin (1-iskelet) Betti sayıları.

    ``β₀`` = bağlantılı bileşen sayısı,
    ``β₁ = |E| − |V| + β₀`` (devir uzayının boyutu).
    """
    n = len(A)
    gorulen = np.zeros(n, dtype=bool)
    b0 = 0
    for s in range(n):
        if gorulen[s]:
            continue
        b0 += 1
        yigin = [s]
        gorulen[s] = True
        while yigin:
            u = yigin.pop()
            for v in np.nonzero(A[u])[0]:
                if not gorulen[v]:
                    gorulen[v] = True
                    yigin.append(int(v))
    kenar = int(np.sum(A > 0) // 2)
    return b0, kenar - n + b0


def hsic(x: np.ndarray, y: np.ndarray, olcek: float | None = None) -> float:
    """Hilbert--Schmidt Bağımsızlık Ölçütü, Gauss çekirdeğiyle.

    ``HSIC = Tr(K H L H)/(n−1)²``. Bağımsızlıkta 0'a yakınsar.
    """
    n = len(x)
    if n < 4:
        return 0.0
    # Gram dizeyleri ``n×n``dir; uzun pencerede tek başına akışı yer
    # (ölçüldü: 4096 satırda 𝒪₈ Tahlil 4,1 sn). HSIC bir ORAN ölçüsüdür;
    # düzgün aralıklı bir alt örneklem aynı bağımsızlık hükmünü verir.
    TAVAN = 512
    if n > TAVAN:
        idx = np.linspace(0, n - 1, TAVAN).astype(int)
        x, y, n = x[idx], y[idx], TAVAN

    def gram(v: np.ndarray) -> np.ndarray:
        d2 = (v[:, None] - v[None, :]) ** 2
        s = olcek if olcek is not None else np.sqrt(0.5 * np.median(d2[d2 > 0])) if np.any(d2 > 0) else 1.0
        return np.exp(-0.5 * d2 / max(s * s, 1e-12))

    H = np.eye(n) - np.ones((n, n)) / n
    K, L = gram(x), gram(y)
    return float(np.trace(K @ H @ L @ H) / (n - 1) ** 2)


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a0, b0 = a - a.mean(), b - b.mean()
    payda = float(np.linalg.norm(a0) * np.linalg.norm(b0))
    return float(a0 @ b0 / payda) if payda > 1e-12 else 0.0


def asiklik_ihlali(A: np.ndarray) -> float:
    """NOTEARS ölçütü ``h(A) = Tr(exp(A∘A)) − d``.

    ``A`` bir DAG'ın ağırlık dizeyi ise **tam olarak 0**'dır; herhangi bir
    devir varsa kesin pozitiftir.
    """
    d = len(A)
    M = A * A
    # matris üsteli (Taylor; M ≥ 0 ve küçük normlu tutulur)
    olcek = max(float(np.max(np.sum(M, axis=1))), 1.0)
    Mn = M / olcek
    toplam = np.eye(d)
    terim = np.eye(d)
    for k in range(1, 40):
        terim = terim @ Mn / k
        toplam = toplam + terim
    # exp(M) = exp(Mn)^olcek  --  iz için doğrudan seri kullan
    toplam = np.eye(d)
    terim = np.eye(d)
    for k in range(1, 60):
        terim = terim @ M / k
        toplam = toplam + terim
        if np.max(np.abs(terim)) < 1e-16:
            break
    return float(np.trace(toplam) - d)


def pearson_cok(A: np.ndarray, B: np.ndarray) -> float:
    a, b = A.ravel(), B.ravel()
    a0, b0 = a - a.mean(), b - b.mean()
    payda = float(np.linalg.norm(a0) * np.linalg.norm(b0))
    return float(a0 @ b0 / payda) if payda > 1e-12 else 0.0


def _sik(x: float) -> float:
    """``[0,∞) → [0,1)``; ``x/(1+x)``. Monoton ve tersinir."""
    return float(x / (1.0 + x))


def simetrik_harmoni(Y: np.ndarray) -> float:
    """``1 − ‖Y − Yᵀ‖_F / (2‖Y‖_F)``.

    Metindeki hâl ``1 − ‖Y − Yᵀ‖_F``dir; iki düzeltme yapıldı ve ikisi de
    ölçümden çıktı:

    * **Payda**: paydasız ölçü ``Y``nin BÜYÜKLÜĞÜNE bağlı olur, oysa
      harmoni bir orandır -- aynı şekilli iki dizeden büyük olanı "daha
      ahenksiz" görünürdü.
    * **2 katsayısı**: ``‖Y−Yᵀ‖² = 2‖Y‖² − 2⟨Y,Yᵀ⟩ ≤ 4‖Y‖²`` olduğundan
      yalnız ``‖Y‖``a bölmek ölçüyü ``[1−2, 1]``e taşır. Nitekim ölçüldü:
      harmoni −0.351 çıktı, yani "ahenk" negatif oldu. ``2‖Y‖`` ile
      bölünce ölçü ``[0,1]``dedir; ters simetrik dizede tam 0, simetrik
      dizede tam 1.
    """
    payda = float(np.linalg.norm(Y))
    if payda < 1e-12:
        return 1.0
    return float(1.0 - np.linalg.norm(Y - Y.T) / (2.0 * payda))



# ==== küme: melekelerin tek döndürücüsü ====

def meleke_mertebeleri(cetvel: Optional[Dict[int, int]] = None
                       ) -> Dict[int, int]:
    """Kanonik cetveli döndür -- **inşa yok, tablo var**.

    Evvelki hâli 41 melekeyi "en boş mertebeye" yerleştiriyordu ve bu
    bir tercihti. Artık divanın cetveli statik bağlıdır; yalnız
    cetvelde bulunmayan iki meleke (``𝒪₉``, ``𝒪₂₁``) gerekçeli
    yerlerine konur ve bu **ayrıca işaretlidir**.
    """
    out = dict(KANONIK_CETVEL if cetvel is None else cetvel)
    for no, m in EKSIK_MELEKELER.items():
        out.setdefault(no, m)
    eksik = [n for n in range(1, MELEKE_SAYISI + 1) if n not in out]
    if eksik:                                        # pragma: no cover
        raise ValueError("cetvelde olmayan meleke: %s" % eksik)
    return out

def so_ureteci(D: int, a: int) -> np.ndarray:
    """``T^a = E_{pq} − E_{qp}`` -- ``so(D)``nin temel üreteci.

    Antisimetriktir, dolayısıyla ``exp(θT)`` **tam ortogonaldir** ve
    normu korur (ceridenin reel ``SO(D)`` hükmü). ``a`` indisi
    ``(p, q)`` çiftini sözlük sırasında belirler; belirlenimcidir,
    rastgele seçim yoktur.
    """
    D = int(D)
    ciftler = D * (D - 1) // 2
    if ciftler <= 0:
        raise ValueError("D ≥ 2 olmalı")
    a = int(a) % ciftler
    p = 0
    k = a
    while k >= D - 1 - p:
        k -= D - 1 - p
        p += 1
    q = p + 1 + k
    T = np.zeros((D, D))
    T[p, q] = 1.0
    T[q, p] = -1.0
    return T

def mertebe_hamiltonyeni(m: int, teta: np.ndarray, D: int,
                         cetvel: Optional[Dict[int, int]] = None
                         ) -> Tuple[np.ndarray, List[int]]:
    """``Ĥ_m = Σ_{i ∈ Meleke_m} θ_i T_i`` -- **tek** antisimetrik dizey.

    Döner ``(Ĥ_m, o mertebedeki meleke numaraları)``. 41 meleke ayrı
    ayrı çarpılmaz; hepsi tek bir üretece toplanır -- padişahın küllî
    esası budur ve maliyet farkı buradan doğar.
    """
    cet = meleke_mertebeleri() if cetvel is None else cetvel
    teta = np.asarray(teta, float).ravel()
    if teta.size < MELEKE_SAYISI:
        teta = np.resize(teta, MELEKE_SAYISI)
    H = np.zeros((int(D), int(D)))
    uyeler: List[int] = []
    for no in range(1, MELEKE_SAYISI + 1):
        if cet[no] != int(m):
            continue
        uyeler.append(no)
        H = H + float(teta[no - 1]) * so_ureteci(int(D), no - 1)
    return H, uyeler

def muvazene_matrisi(cetvel: Optional[Dict[int, int]] = None
                     ) -> np.ndarray:
    """``M_ij`` -- hangi iki melekenin çatışması ne kadar ağır sayılır.

    **Aynı mertebedeki melekeler ağır, farklı mertebedekiler hafif
    cezalanır** ve sebebi cebridir: aynı mertebede çalışan iki meleke
    aynı alt uzayı paylaşır, biri ötekinin dalgasını doğrudan söndürür.
    Farklı mertebedekiler zaten ayrı eksenlerdedir (H21: mertebeler
    toplanmaz), çatışmaları dolaylıdır.

    Köşegen sıfırdır: bir melekenin kendisiyle komütatörü zaten sıfır.
    """
    cet = meleke_mertebeleri() if cetvel is None else cetvel
    M = np.zeros((MELEKE_SAYISI, MELEKE_SAYISI))
    for i in range(1, MELEKE_SAYISI + 1):
        for j in range(1, MELEKE_SAYISI + 1):
            if i == j:
                continue
            M[i - 1, j - 1] = 1.0 if cet[i] == cet[j] else 0.1
    return M

def bgcm_kaybi(teta: np.ndarray, D: int,
               M: Optional[np.ndarray] = None,
               cetvel: Optional[Dict[int, int]] = None) -> Dict[str, float]:
    """``Ĥ_BGCM = Σ_ij M_ij ‖[𝒪_i, 𝒪_j]‖²_F`` -- **41 melekenin muvazenesi**.

    İki meleke sıra değiştirebiliyorsa (``[𝒪_i,𝒪_j] = 0``) birbirinin
    işini bozmaz: hangi sırada koşarlarsa koşsunlar netice aynıdır.
    Komütatör büyükse sıra mühimdir ve biri ötekini **eziyor** demektir.

    Ölçü kırmızıya döner: bütün melekeler aynı Cartan alt cebrinde
    (sıra değiştiren) seçilirse kayıp tam sıfırdır; rastgele seçilirse
    büyük çıkar. ``rapor_dimag`` ikisini de gösterir.
    """
    teta = np.asarray(teta, float).ravel()
    if teta.size < MELEKE_SAYISI:
        teta = np.resize(teta, MELEKE_SAYISI)
    Mm = muvazene_matrisi(cetvel) if M is None else np.asarray(M, float)
    O = [float(teta[i]) * so_ureteci(int(D), i)
         for i in range(MELEKE_SAYISI)]
    top = 0.0
    en_kotu = 0.0
    cift: Tuple[int, int] = (0, 0)
    for i in range(MELEKE_SAYISI):
        for j in range(i + 1, MELEKE_SAYISI):
            C = O[i] @ O[j] - O[j] @ O[i]
            v = float(np.sum(C * C))
            w = float(Mm[i, j] + Mm[j, i])
            top += w * v
            if w * v > en_kotu:
                en_kotu, cift = w * v, (i + 1, j + 1)
    # **NORMALİZASYON (padişahın 3. hükmü).** Komütatör ``θ²`` ile,
    # izi ``θ⁴`` ile büyür; ölçüldü: ``λ = 1``de kuvvetli ``θ``da
    # BGCM = 680,86 iken ARC = 1,20 idi -- muvazene terimi gayeyi
    # eziyordu. Payda ``1 + Σ‖O_k‖_F⁴``tür ve aynı mertebeden büyüdüğü
    # için netice **analitik olarak [0,1]e hapsedilir**:
    #
    #     Ĥ_BGCM^norm = Σ M_ij ‖[O_i,O_j]‖²_F / (1 + Σ_k ‖O_k‖_F⁴)
    #
    # Cauchy-Schwarz: ``‖[A,B]‖_F ≤ 2‖A‖_F‖B‖_F`` olduğundan pay,
    # ``4 max(M) (Σ‖O_k‖²)²`` ile sınırlıdır; payda aynı kuvvettedir.
    payda = 1.0 + float(sum(float(np.sum(o * o)) ** 2 for o in O))
    norm = top / payda
    return {"kayıp": float(top), "kayıp_norm": float(norm),
            "payda": float(payda),
            "en_kötü_çift_şiddeti": float(en_kotu),
            "en_kötü_i": float(cift[0]), "en_kötü_j": float(cift[1]),
            "muvazeneli": bool(top <= 1e-12)}

