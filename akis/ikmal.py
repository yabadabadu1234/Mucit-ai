"""Ceridenin İkmâl Fıkraları -- kodda **eksik olan** üçü.

`docs/ceride/TERKIP_LAYIHASI.md`nin "Kararnâme Eki: İkmâl ve İlhâk
Fıkraları" dört şart koyar. Depo yoklandı (iddia değil, ``dir()`` ile
sayıldı) ve netice şudur:

* **İKMÂL I (RKHS: PSD + Cholesky + κ + Nyström hatası)** --
  `ogrenme/rkhs.py`de **zaten tam**: ``psd_mi`` en küçük özdeğere
  bakıyor, ``RKHS.uydur`` açık ters almıyor Cholesky çözüyor ve tekilde
  ``ValueError`` fırlatıyor (fail-safe), ``kosul`` raporlanıyor,
  ``nystrom`` Frobenius bağıl hatasını döndürüyor. Yeni koda ihtiyaç
  yoktur; bu bir borç değil, kapanmış bir maddedir.
* **İKMÂL II (Alexandroff + alt-seviye + log-bariyer)** --
  `akis/tikiz.py`de var (``kure_izdusumu``, ``alt_seviye_tikiz_mi``,
  ``barriyer``); fakat **Lions konsantrasyon-tıkızlığı yoktu**.
* **İKMÂL III (Morse-Euler katı eşitliği + RCD(K,N) Bochner)** --
  ``morse_bagintisi`` katı eşitliği zaten arıyor; fakat **Bochner
  süzgeci yoktu**.
* **İKMÂL IV (Postnikov k-invaryantı + Cayley çekilmesi)** --
  `ogrenme/grassmann.py`de exp/log haritaları var; **Cayley çekilmesi
  de, tıkanıklık sınıfı da yoktu**.

Bu dosya o üç eksiği kapatır. Her birinin ölçüsü **kırmızıya
dönebilir** (H90) ve gösterimde fiilen döndürülür.

**Bir haddin peşinen ilanı (kullanıcı hükmü C).** ``postnikov_indisi``
hakikî bir ``[c] ∈ H^{n+1}(X; π_n(Y))`` sınıfı hesaplamaz; homotopi
gruplarını hesaplamak sonlu bir algoritmayla umumiyetle mümkün
değildir. Burada yapılan, kalıcı kohomoloji Betti sayılarından
**tıkanıklığın hangi mertebede olduğunu** okumaktır: bu bir vekildir,
sınıfın kendisi değildir, ve öyle adlandırılır.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["lions_konsantrasyonu", "bochner_artigi", "bochner_suzgeci",
           "cayley_cekilmesi", "cayley_hatasi", "postnikov_indisi"]


# ══════════════════════════════════════════════════════════════════════
#  İKMÂL II'nin eksiği: Lions konsantrasyon-tıkızlığı
# ══════════════════════════════════════════════════════════════════════

def lions_konsantrasyonu(nokta: np.ndarray, agirlik: np.ndarray,
                         yaricaplar: Sequence[float] = (0.25, 0.5, 1.0,
                                                        2.0, 4.0, 8.0),
                         esik: float = 0.9) -> Dict[str, object]:
    """Lions'un üçlemesi: **tıkızlık / dağılma (vanishing) / ikilenme**.

    Konsantrasyon fonksiyonu

    .. math::  Q(t) = \\sup_y \\int_{B(y,t)} |u(x)|^p\\,dx

    kütlenin ``t`` yarıçaplı bir yuvarda ne kadar toplanabildiğini
    ölçer. Kütle ``1``e normalize edilir ve üç hâl ayrılır:

    * ``Q(t) → 1``  ise **tıkızlık**: alt-seviye kümesi toplanıyor,
      asgarî kaçmıyor.
    * ``Q(t) → 0``  ise **dağılma**: kütle sonsuza yayılıyor, hiçbir
      yuvarda toplanmıyor; asgarî yoktur.
    * ``Q(t) → α ∈ (0,1)`` ise **ikilenme**: kütle en az iki uzak
      yığına bölünmüş; dizi tek bir limite gitmiyor.

    Süpremum, **veri noktalarının kendileri merkez alınarak** aranır.
    Bu bir yaklaşımdır ve haddi bilinerek yazılır: hakikî süpremum
    bütün ``y ∈ ℝ^d`` üzerindedir. Fakat kütle noktalarda toplandığı
    için en yoğun yuvarın merkezi bir noktanın yakınındadır; ölçü bu
    yüzden **alttan** sınırdır, yani "dağılma" hükmü verirse hakikaten
    dağılma vardır (yanlış kırmızı vermez), "tıkızlık" hükmü ise
    gevşek olabilir.
    """
    X = np.atleast_2d(np.asarray(nokta, float))
    w = np.abs(np.asarray(agirlik, float)).ravel()
    if w.size != X.shape[0]:
        raise ValueError("ağırlık ve nokta sayısı uyuşmuyor")
    top = float(w.sum())
    if top <= 0:
        raise ValueError("kütle sıfır; Q(t) tanımsız")
    w = w / top
    d = np.sqrt(np.maximum(
        np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2), 0.0))
    Q: Dict[float, float] = {}
    for t in yaricaplar:
        icinde = (d <= float(t))
        Q[float(t)] = float(np.max(icinde @ w))
    tler = sorted(Q)
    son = Q[tler[-1]]
    ilk = Q[tler[0]]
    if son >= esik:
        hal = "tıkız"
    elif son <= 1.0 - esik:
        hal = "dağılma"
    else:
        hal = "ikilenme"
    return {"Q": Q, "hâl": hal, "Q_son": son, "Q_ilk": ilk,
            "tıkız": hal == "tıkız",
            "not": "Q noktalar merkez alınarak ALTTAN sınırdır; "
                   "'dağılma' hükmü kat'î, 'tıkız' hükmü gevşektir"}


# ══════════════════════════════════════════════════════════════════════
#  İKMÂL III'ün eksiği: RCD(K,N) Bochner süzgeci
# ══════════════════════════════════════════════════════════════════════

def _turevler(f: Callable[[np.ndarray], float], x: np.ndarray,
              h: float) -> Tuple[np.ndarray, float]:
    """``(∇f, Δf)`` -- merkezî sonlu farkla, ``O(h²)`` hatayla."""
    x = np.asarray(x, float)
    n = x.size
    g = np.empty(n)
    lap = 0.0
    f0 = float(f(x))
    for k in range(n):
        e = np.zeros(n)
        e[k] = h
        fp, fm = float(f(x + e)), float(f(x - e))
        g[k] = (fp - fm) / (2.0 * h)
        lap += (fp - 2.0 * f0 + fm) / (h * h)
    return g, float(lap)


def bochner_artigi(f: Callable[[np.ndarray], float], x: np.ndarray,
                   K: float = 0.0, N: Optional[float] = None,
                   h: float = 1e-3) -> Dict[str, float]:
    """Bochner eşitsizliğinin **artığı**: ``sol − sağ``.

    .. math::

       \\tfrac12 \\Delta |\\nabla f|^2 \\;\\ge\\;
       \\langle \\nabla f, \\nabla \\Delta f\\rangle
       + \\tfrac1N (\\Delta f)^2 + K |\\nabla f|^2

    Artık ``≥ 0`` ise havza hakikî bir manifold havzasıdır (Ricci
    eğriliği ``K`` ile alttan sınırlı); ``< 0`` ise bulunan çukur
    sayısal bir kırışıklıktır ve intâc **reddedilir**.

    ``N`` verilmezse uzayın kendi boyutu alınır. ``N``i boyuttan küçük
    seçmek eşitsizliği kasten kırar ve ölçünün kırmızıya dönebildiğini
    gösterir: ``f = ½‖x‖²``de ``n = N`` iken artık tam **sıfırdır**
    (Bochner burada keskindir), ``N < n`` iken **negatiftir**.
    """
    x = np.asarray(x, float)
    n = int(x.size)
    N = float(n) if N is None else float(N)
    if N <= 0:
        raise ValueError("N > 0 olmalı")

    def gkare(z: np.ndarray) -> float:
        g, _ = _turevler(f, z, h)
        return float(g @ g)

    def laplasyen(z: np.ndarray) -> float:
        return _turevler(f, z, h)[1]

    g0, lap0 = _turevler(f, x, h)
    _, lap_gkare = _turevler(gkare, x, h)
    grad_lap, _ = _turevler(laplasyen, x, h)

    sol = 0.5 * lap_gkare
    sag = float(g0 @ grad_lap) + (lap0 * lap0) / N + float(K) * float(g0 @ g0)
    return {"sol": float(sol), "sağ": float(sag),
            "artık": float(sol - sag),
            "‖∇f‖²": float(g0 @ g0), "Δf": float(lap0),
            "N": N, "K": float(K)}


def bochner_suzgeci(f: Callable[[np.ndarray], float], x: np.ndarray,
                    K: float = 0.0, N: Optional[float] = None,
                    h: float = 1e-3, tolerans: float = 1e-3
                    ) -> Dict[str, object]:
    """Bochner artığına göre havzayı **kabul et yahut reddet**.

    ``tolerans`` sonlu fark gürültüsü içindir ve **ölçekle** birlikte
    okunur: artık, terimlerin büyüklüğüne nispetle değerlendirilir;
    mutlak bir eşik büyük ``Δf``de her şeyi geçirirdi.
    """
    r = bochner_artigi(f, x, K=K, N=N, h=h)
    olcek = max(abs(r["sol"]), abs(r["sağ"]), 1e-12)
    nispi = r["artık"] / olcek
    r2: Dict[str, object] = dict(r)
    r2["nispî_artık"] = float(nispi)
    r2["kabul"] = bool(nispi >= -abs(tolerans))
    return r2


# ══════════════════════════════════════════════════════════════════════
#  İKMÂL IV'ün eksiği: Cayley çekilmesi ve tıkanıklık indisi
# ══════════════════════════════════════════════════════════════════════

def cayley_cekilmesi(X: np.ndarray, xi: np.ndarray) -> np.ndarray:
    """Stiefel/Grassmann üzerinde **Cayley** çekilmesi ``R_X(ξ)``.

    ``X`` sütunları dik (``XᵀX = I``) bir ``n×p`` çerçeve, ``ξ`` ona
    teğet bir yön olsun. Eğik-simetrik

    .. math::  A = W X^T - X W^T,\\quad W = \\xi + \\tfrac12 X X^T \\xi

    kurulup Cayley dönüşümü uygulanır:

    .. math::  R_X(\\xi) = \\big(I - \\tfrac12 A\\big)^{-1}
                            \\big(I + \\tfrac12 A\\big) X

    ``A`` eğik-simetrik olduğu için ``(I−A/2)^{-1}(I+A/2)`` **tam
    ortogonaldir** (Cayley dönüşümünün özdeşliği); dolayısıyla dikliği
    makine hassasiyetinde korur. Üstel harita (``expm``) ile aynı işi
    görür, fakat özdeğer ayrışımı gerektirmez: yalnız bir doğrusal
    sistem çözülür ve **belirlenimcidir** (ceride Bab VIII).

    ``exp`` yerine Cayley kullanmanın bedeli, ikinci mertebeden
    sapmadır: Cayley bir **çekilmedir** (retraction), jeodezik değil.
    Bu bir kusur değildir -- eniyilemede çekilme yeterlidir -- fakat
    "jeodezik" diye anılamaz ve burada anılmıyor.
    """
    X = np.asarray(X, float)
    xi = np.asarray(xi, float)
    if X.shape != xi.shape:
        raise ValueError("ξ, X ile aynı şekilde olmalı")
    n = X.shape[0]
    W = xi + 0.5 * (X @ (X.T @ xi))
    A = W @ X.T - X @ W.T
    I = np.eye(n)
    return np.linalg.solve(I - 0.5 * A, (I + 0.5 * A) @ X)


def cayley_hatasi(X: np.ndarray, xi: np.ndarray) -> Dict[str, float]:
    """Cayley dikliği koruyor mu, ve ``ξ→0``da kimliğe gidiyor mu?

    İki şart birden aranır; biri olmadan öteki yeter değildir:

    * ``‖R(ξ)ᵀR(ξ) − I‖`` makine hassasiyetinde olmalı (**diklik**).
    * ``‖R(tξ) − (X + tξ)‖ / t² `` sınırlı kalmalı (**birinci mertebe
      teğetlik**): çekilme, küçük adımda teğet yönle örtüşmeli.
    """
    R = cayley_cekilmesi(X, xi)
    p = R.shape[1]
    diklik = float(np.linalg.norm(R.T @ R - np.eye(p)))
    t = 1e-4
    Rt = cayley_cekilmesi(X, t * np.asarray(xi, float))
    teget = float(np.linalg.norm(Rt - (X + t * np.asarray(xi, float)))
                  / (t * t))
    return {"diklik_hatası": diklik, "teğetlik_katsayısı": teget}


def postnikov_indisi(betti: Sequence[Sequence[float]],
                     esik: float = 0.5) -> Dict[str, object]:
    """Tıkanıklığın **hangi mertebede** olduğunu Betti sayılarından oku.

    Ceride der ki: ``[c] ∈ H^{n+1}(X; π_n(Y))`` sıfırdan farklı olduğu
    indis, modelin tıkandığı mantık mertebesini gösterir ve oraya
    Cayley çekilmesiyle sıçranır.

    **Burada hesaplanan o sınıf DEĞİLDİR** ve öyle iddia edilmez:
    homotopi gruplarını sonlu bir algoritmayla hesaplamak umumiyetle
    mümkün değildir. Hesaplanan, kalıcı homolojinin verdiği Betti
    sayılarından okunan bir **vekildir**: mertebe ``m``de ``H^{n+1}``in
    boyutu eşiği aşıyorsa orada kapanmamış bir çevrim -- yani bir
    tıkanıklık -- vardır.

    ``betti`` ``(mertebe, derece)`` dizisidir. Dönen ``mertebe`` en
    küçük tıkanık mertebedir; hiçbiri tıkanık değilse ``None``dır ve
    **sıçrama yapılmaz** (ölçü burada yeşildir ve yeşil kalmalıdır --
    her koşuda bir sıçrama üretmek, ölçünün hiçbir şey ölçmediğinin
    işareti olurdu).
    """
    B = np.atleast_2d(np.asarray(betti, float))
    tikanik: List[Tuple[int, int, float]] = []
    for m in range(B.shape[0]):
        for n in range(1, B.shape[1]):          # H^{n+1} → sütun n
            if B[m, n] > float(esik):
                tikanik.append((int(m), int(n), float(B[m, n])))
    if not tikanik:
        return {"mertebe": None, "derece": None, "tıkanık": False,
                "hepsi": []}
    m, n, v = min(tikanik, key=lambda t: (t[0], t[1]))
    return {"mertebe": m, "derece": n, "değer": v, "tıkanık": True,
            "hepsi": tikanik}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim -- H126: modül kendi şahidini taşır
# ══════════════════════════════════════════════════════════════════════

def rapor() -> str:                                     # pragma: no cover
    s: List[str] = ["CERİDENİN İKMÂL FIKRALARI -- eksik olan üçü", ""]
    rng = np.random.default_rng(0)

    s.append("=== İKMÂL II: Lions konsantrasyon-tıkızlığı ===")
    tek = rng.normal(size=(80, 2)) * 0.3
    s.append("  tek yığın        : %s" %
             lions_konsantrasyonu(tek, np.ones(80))["hâl"])
    iki = np.vstack([rng.normal(size=(40, 2)) * 0.3,
                     rng.normal(size=(40, 2)) * 0.3 + 40.0])
    s.append("  iki uzak yığın   : %s   ← İKİLENME (kırmızı)" %
             lions_konsantrasyonu(iki, np.ones(80))["hâl"])
    yayik = rng.normal(size=(200, 2)) * 200.0
    s.append("  yayılmış kütle   : %s   ← DAĞILMA (kırmızı)" %
             lions_konsantrasyonu(yayik, np.ones(200))["hâl"])

    s.append("")
    s.append("=== İKMÂL III: RCD(K,N) Bochner süzgeci ===")

    def kare(z):
        return 0.5 * float(np.asarray(z, float) @ np.asarray(z, float))

    x = np.array([0.7, -0.3, 0.5])
    r = bochner_suzgeci(kare, x, K=0.0, N=None)
    s.append("  f=½‖x‖², n=N=3 : artık %+.3e  nispî %+.2e  kabul=%s"
             % (r["artık"], r["nispî_artık"], r["kabul"]))
    r = bochner_suzgeci(kare, x, K=0.0, N=1.0)
    s.append("  aynı f, N=1     : artık %+.3e  nispî %+.2e  kabul=%s"
             "   ← KIRMIZI" % (r["artık"], r["nispî_artık"], r["kabul"]))

    s.append("")
    s.append("=== İKMÂL IV: Cayley çekilmesi ===")
    A = rng.normal(size=(8, 3))
    X = np.linalg.qr(A)[0]
    xi = rng.normal(size=(8, 3))
    xi = xi - X @ (X.T @ xi)                 # teğet uzaya izdüşür
    h = cayley_hatasi(X, xi)
    s.append("  diklik hatası      : %.3e" % h["diklik_hatası"])
    s.append("  teğetlik katsayısı : %.3e  (ξ→0'da sınırlı)"
             % h["teğetlik_katsayısı"])

    s.append("")
    s.append("=== İKMÂL IV: Postnikov tıkanıklık indisi (VEKİL) ===")
    temiz = [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
    s.append("  tıkanıksız Betti : %s" % postnikov_indisi(temiz)["tıkanık"])
    tikali = [[1, 0, 0], [1, 2, 0], [1, 0, 0]]
    t = postnikov_indisi(tikali)
    s.append("  tıkalı Betti     : mertebe %s, derece %s   ← sıçrama buraya"
             % (t["mertebe"], t["derece"]))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
