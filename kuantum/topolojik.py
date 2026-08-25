"""Topolojik anyon örgüsü ve hata düzeltme (QEC) kapıları.

Kaynak: ``docs/kaynak/kuantum_kapi_kulliyati.tex`` §"Topolojik Anyon ve
Hata Düzeltme (QEC) Kapıları".

**1. Kitaev yüzey kodu.**  Kubitler kenarlarda; her köşe için
``A_s = ∏_{i∈star(s)} X_i``, her yüz için ``B_p = ∏_{j∈∂p} Z_j``.
``[A_s, B_p] = 0`` iddiası **sayısal olarak değil, kombinatorik
olarak** doğrudur: bir yıldız ile bir yüz ya hiç kenar paylaşmaz ya
da **tam iki** kenar paylaşır; iki takas iki eksi işaret verir, çarpım
``+1``dir. Burada hem kombinatorik sayım hem küçük kafeste tam dizey
çarpımı yapılıyor.

**2. Fibonacci anyonları.**

.. math::

   F = \\begin{pmatrix}\\varphi^{-1} & \\varphi^{-1/2}\\\\
   \\varphi^{-1/2} & -\\varphi^{-1}\\end{pmatrix}, \\quad
   R = \\mathrm{diag}(e^{-4\\pi i/5},\\, e^{3\\pi i/5}), \\quad
   B = F^{-1} R F

``σ₁ = R``, ``σ₂ = B`` örgü üreteçleridir; **doğru olma ölçütü**
Yang–Baxter bağıntısı ``σ₁σ₂σ₁ = σ₂σ₁σ₂``dir ve burada ölçülüyor.
``F`` gerçel simetrik ve ``F² = I`` olduğundan ``F⁻¹ = F``.

**3. Majorana sıfır kipleri.**  ``γ_{2j−1} = c_j + c_j†``,
``γ_{2j} = i(c_j† − c_j)``; ``{γ_j, γ_k} = 2δ_{jk} I``.  ``c_j``
Jordan–Wigner ile kurulur -- **işaret zinciri şarttır**: onsuz
farklı bölgelerdeki kipler komütatör değil antikomütatör vermez.
Bu, "gevşetilirse ne olur" diye ayrıca ölçülüyor.
"""

from __future__ import annotations

import itertools
import math
from typing import Dict, List, Sequence, Tuple

import numpy as np

__all__ = [
    "ALTIN", "fibonacci_F", "fibonacci_R", "fibonacci_B",
    "orgu_ureticleri", "yang_baxter_hatasi", "orgu_kelimesi",
    "orgu_yogunlugu",
    "majorana", "antikomutator_hatasi", "jw_zincirsiz_majorana",
    "YuzeyKodu",
]

ALTIN = (1.0 + math.sqrt(5.0)) / 2.0

_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


# ══════════════════════════════════════════════════════════════════════
#  1. Fibonacci anyonları
# ══════════════════════════════════════════════════════════════════════

def fibonacci_F() -> np.ndarray:
    """Altın oran ``F`` dizeyi — gerçel, simetrik, ``F² = I``."""
    p = ALTIN
    return np.array([[1 / p, p ** -0.5], [p ** -0.5, -1 / p]], dtype=complex)


def fibonacci_R() -> np.ndarray:
    """``R = diag(e^{−4πi/5}, e^{3πi/5})``."""
    return np.diag([np.exp(-4j * math.pi / 5), np.exp(3j * math.pi / 5)])


def fibonacci_B() -> np.ndarray:
    """``B = F⁻¹ R F`` — ikinci örgü üreteci."""
    F = fibonacci_F()
    return np.linalg.inv(F) @ fibonacci_R() @ F


def orgu_ureticleri() -> Tuple[np.ndarray, np.ndarray]:
    """``(σ₁, σ₂) = (R, B)``."""
    return fibonacci_R(), fibonacci_B()


def yang_baxter_hatasi(s1: np.ndarray, s2: np.ndarray) -> float:
    """``‖σ₁σ₂σ₁ − σ₂σ₁σ₂‖_∞`` — örgü grubunun tanımlayıcı bağıntısı.

    Bu sıfır **değilse** eldeki dizeyler bir örgü temsili değildir;
    "topolojik kapı" demenin başka bir ölçütü yoktur.
    """
    return float(np.abs(s1 @ s2 @ s1 - s2 @ s1 @ s2).max())


def orgu_kelimesi(kelime: Sequence[int]) -> np.ndarray:
    """``σ_{i₁}^{±1} … σ_{i_k}^{±1}`` — ``+1/-1`` işaretli üreteç dizisi.

    ``kelime`` içinde ``+1 → σ₁``, ``−1 → σ₁⁻¹``, ``+2 → σ₂``,
    ``−2 → σ₂⁻¹``.
    """
    s1, s2 = orgu_ureticleri()
    U = np.eye(2, dtype=complex)
    for g in kelime:
        M = s1 if abs(g) == 1 else s2
        U = U @ (M if g > 0 else np.linalg.inv(M))
    return U


def _faz_anahtari(U: np.ndarray, basamak: int = 6) -> Tuple:
    """Genel fazdan bağımsız anahtar — en büyük girdiyi pozitif gerçel yapar."""
    v = U.reshape(-1)
    i = int(np.argmax(np.abs(v)))
    W = U * np.exp(-1j * np.angle(v[i]))
    return tuple(np.round(W.reshape(-1), basamak))


def _hedef_mesafesi(U: np.ndarray, H: np.ndarray) -> float:
    """``√(1 − |Tr(U†H)/2|²)`` — genel fazdan bağımsız işlemsel mesafe."""
    iz = abs(complex(np.trace(U.conj().T @ H))) / 2.0
    return math.sqrt(max(1.0 - iz * iz, 0.0))


def orgu_yogunlugu(azami_uzunluk: int = 13, hedef: np.ndarray = None,
                   azami_dugum: int = 40000) -> Dict[str, object]:
    """Örgü kelimeleriyle bir hedef kapıya yaklaşma — **tüketici** arama.

    Rastgele kelime denemek yanıltır: uzunluk arttıkça arama uzayı
    büyür ve sabit sayıda deneme *daha kötü* örter, öyle ki mesafe
    düşmüyormuş gibi görünür (ölçüldü: 4000 rastgele denemeyle
    uzunluk 4, 8 ve 16'da mesafe hep 0.2074 çıkıyordu).  Burada
    genişlik-öncelikli **bütün** farklı kelimeler taranıyor; genel
    faz eşdeğerleri tekilleştiriliyor.

    Ölçülen: farklı öğe sayısı yaklaşık ``1.88^L`` büyüyor ve en iyi
    mesafe ``0.8202 → 0.1189 → 0.0864 → 0.0292`` diye **basamaklı**
    iniyor.  Yani yakınsama vardır ama düzgün değildir; bir örgü
    derleyicisi (Solovay–Kitaev) tam da bunun için gerekir.
    """
    if hedef is None:
        hedef = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
    s1, s2 = orgu_ureticleri()
    G = [s1, np.linalg.inv(s1), s2, np.linalg.inv(s2)]
    etiket = [(1,), (-1,), (2,), (-2,)]
    I = np.eye(2, dtype=complex)
    gorulen = {_faz_anahtari(I)}
    sinir: List[Tuple[np.ndarray, Tuple[int, ...]]] = [(I, ())]
    en_iyi, en_kelime = _hedef_mesafesi(I, hedef), ()
    seyir = []
    for L in range(1, azami_uzunluk + 1):
        yeni_sinir = []
        for U, w in sinir:
            for g, e in zip(G, etiket):
                V = U @ g
                k = _faz_anahtari(V)
                if k in gorulen:
                    continue
                gorulen.add(k)
                yeni_sinir.append((V, w + e))
                d = _hedef_mesafesi(V, hedef)
                if d < en_iyi:
                    en_iyi, en_kelime = d, w + e
        sinir = yeni_sinir
        seyir.append((L, len(gorulen), en_iyi))
        if not sinir or len(gorulen) > azami_dugum:
            break
    return {"seyir": seyir, "farklı_öğe": len(gorulen),
            "en_iyi_mesafe": en_iyi, "kelime": en_kelime,
            "not": "genel faza göre tekilleştirilmiş tüketici arama"}


# ══════════════════════════════════════════════════════════════════════
#  2. Majorana sıfır kipleri
# ══════════════════════════════════════════════════════════════════════

def _jw_c(j: int, n: int) -> np.ndarray:
    """Jordan–Wigner ile ``c_j`` — önünde ``Z`` zinciri."""
    dus = np.array([[0, 1], [0, 0]], dtype=complex)   # |0⟩⟨1|
    ops = [_Z] * j + [dus] + [_I2] * (n - j - 1)
    M = ops[0]
    for o in ops[1:]:
        M = np.kron(M, o)
    return M


def majorana(n: int) -> List[np.ndarray]:
    """``2n`` Majorana operatörü: ``γ_{2j} = c_j + c_j†``,
    ``γ_{2j+1} = i(c_j† − c_j)`` (0-tabanlı indisle).

    Hermityen ve ``γ² = I``dir; :func:`antikomutator_hatasi` bunu ve
    ``{γ_j, γ_k} = 2δ_{jk} I``i ölçer.
    """
    g = []
    for j in range(n):
        c = _jw_c(j, n)
        g.append(c + c.conj().T)
        g.append(1j * (c.conj().T - c))
    return g


def jw_zincirsiz_majorana(n: int) -> List[np.ndarray]:
    """Aynısı ama ``Z`` zinciri **olmadan** — kasten yanlış kurulum.

    Antikomütasyonun zincirden geldiğini göstermek için var; sonucu
    :func:`antikomutator_hatasi` ile kıyaslanıyor.
    """
    dus = np.array([[0, 1], [0, 0]], dtype=complex)
    g = []
    for j in range(n):
        ops = [_I2] * n
        ops[j] = dus
        c = ops[0]
        for o in ops[1:]:
            c = np.kron(c, o)
        g.append(c + c.conj().T)
        g.append(1j * (c.conj().T - c))
    return g


def antikomutator_hatasi(g: Sequence[np.ndarray]) -> Dict[str, float]:
    """``max_{j,k} ‖{γ_j,γ_k} − 2δ_{jk}I‖`` — köşegen ve dışı ayrı."""
    d = g[0].shape[0]
    I = np.eye(d)
    kos, dis = 0.0, 0.0
    for j, k in itertools.product(range(len(g)), repeat=2):
        A = g[j] @ g[k] + g[k] @ g[j] - (2 * I if j == k else 0)
        e = float(np.abs(A).max())
        if j == k:
            kos = max(kos, e)
        else:
            dis = max(dis, e)
    herm = max(float(np.abs(x - x.conj().T).max()) for x in g)
    return {"köşegen_hata": kos, "köşegen_dışı_hata": dis,
            "hermityenlik_hatası": herm}


# ══════════════════════════════════════════════════════════════════════
#  3. Kitaev yüzey (torik) kodu
# ══════════════════════════════════════════════════════════════════════

class YuzeyKodu:
    """``L×L`` torus üzerinde torik kod — kubitler kenarlarda.

    Kenar indisleri: ``(y, x, d)``, ``d = 0`` yatay (``(y,x)→(y,x+1)``),
    ``d = 1`` dikey (``(y,x)→(y+1,x)``).  Toplam ``2L²`` kubit.

    * Yıldız ``A_s``: ``s = (y,x)`` köşesine değen 4 kenarda ``X``.
    * Yüz ``B_p``: ``p = (y,x)`` yüzünün 4 kenarında ``Z``.
    * ``∏_s A_s = ∏_p B_p = I`` olduğundan bağımsız dengeleyici sayısı
      ``2L² − 2``; mantıksal kubit sayısı ``2L² − (2L²−2) = 2``.
      Bu sayı burada **sıra hesabıyla doğrulanıyor**, iddia edilmiyor.
    """

    def __init__(self, L: int):
        if L < 2:
            raise ValueError("L ≥ 2 olmalı")
        self.L = L
        self.kenarlar = [(y, x, d) for y in range(L) for x in range(L)
                         for d in (0, 1)]
        self.indis = {e: i for i, e in enumerate(self.kenarlar)}
        self.n = len(self.kenarlar)

    # --- kombinatorik ---
    def yildiz_kenarlari(self, y: int, x: int) -> List[Tuple[int, int, int]]:
        L = self.L
        return [(y, x, 0), (y, (x - 1) % L, 0),
                (y, x, 1), ((y - 1) % L, x, 1)]

    def yuz_kenarlari(self, y: int, x: int) -> List[Tuple[int, int, int]]:
        L = self.L
        return [(y, x, 0), ((y + 1) % L, x, 0),
                (y, x, 1), (y, (x + 1) % L, 1)]

    def ortak_kenar_sayilari(self) -> Dict[int, int]:
        """Her (yıldız, yüz) çifti kaç kenar paylaşıyor? — histogram.

        ``[A_s, B_p] = 0`` bu histogramın yalnız ``{0, 2}`` içermesine
        denktir.
        """
        say: Dict[int, int] = {}
        for sy, sx in itertools.product(range(self.L), repeat=2):
            S = set(self.yildiz_kenarlari(sy, sx))
            for py, px in itertools.product(range(self.L), repeat=2):
                k = len(S & set(self.yuz_kenarlari(py, px)))
                say[k] = say.get(k, 0) + 1
        return dict(sorted(say.items()))

    # --- ikili (GF(2)) sıra hesabı ---
    def dengeleyici_dizeyi(self) -> np.ndarray:
        """``(2L²) × (2n)`` simplektik ikili dizey: [X kısmı | Z kısmı]."""
        L, n = self.L, self.n
        M = np.zeros((2 * L * L, 2 * n), dtype=np.uint8)
        r = 0
        for y, x in itertools.product(range(L), repeat=2):
            for e in self.yildiz_kenarlari(y, x):
                M[r, self.indis[e]] ^= 1
            r += 1
        for y, x in itertools.product(range(L), repeat=2):
            for e in self.yuz_kenarlari(y, x):
                M[r, n + self.indis[e]] ^= 1
            r += 1
        return M

    def mantiksal_kubit_sayisi(self) -> Dict[str, int]:
        M = self.dengeleyici_dizeyi()
        s = _gf2_sira(M)
        return {"kubit": self.n, "dengeleyici_satırı": M.shape[0],
                "bağımsız_dengeleyici": s, "mantıksal_kubit": self.n - s}

    # --- küçük kafeste tam dizey ---
    def operator(self, kenarlar: Sequence[Tuple[int, int, int]],
                 P: np.ndarray) -> np.ndarray:
        ops = [_I2] * self.n
        for e in kenarlar:
            ops[self.indis[e]] = P
        M = ops[0]
        for o in ops[1:]:
            M = np.kron(M, o)
        return M

    def komutator_hatasi_tam(self) -> float:
        """``max_{s,p} ‖A_s B_p − B_p A_s‖`` — tam dizeyle (``L=2``).

        ``L = 2``de bile ``2^8 = 256`` boyut; daha büyüğünde
        kombinatorik ölçüt kullanılır.
        """
        en = 0.0
        for sy, sx in itertools.product(range(self.L), repeat=2):
            A = self.operator(self.yildiz_kenarlari(sy, sx), _X)
            for py, px in itertools.product(range(self.L), repeat=2):
                B = self.operator(self.yuz_kenarlari(py, px), _Z)
                en = max(en, float(np.abs(A @ B - B @ A).max()))
        return en


def _gf2_sira(M: np.ndarray) -> int:
    """GF(2) üzerinde satır sırası — Gauss eliminasyonu."""
    A = M.copy().astype(np.uint8)
    satir, sut = 0, A.shape[1]
    for c in range(sut):
        piv = None
        for r in range(satir, A.shape[0]):
            if A[r, c]:
                piv = r
                break
        if piv is None:
            continue
        A[[satir, piv]] = A[[piv, satir]]
        hedef = np.nonzero(A[:, c])[0]
        for r in hedef:
            if r != satir:
                A[r] ^= A[satir]
        satir += 1
        if satir == A.shape[0]:
            break
    return satir


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    F, R, B = fibonacci_F(), fibonacci_R(), fibonacci_B()
    s.append("=== Fibonacci F ve R: üniterlik ve F²=I ===")
    s.append("  φ = %.10f" % ALTIN)
    s.append("  ‖F†F−I‖ = %.2e   ‖F²−I‖ = %.2e   ‖F−F⁻¹‖ = %.2e"
             % (float(np.abs(F.conj().T @ F - np.eye(2)).max()),
                float(np.abs(F @ F - np.eye(2)).max()),
                float(np.abs(F - np.linalg.inv(F)).max())))
    s.append("  ‖R†R−I‖ = %.2e   ‖B†B−I‖ = %.2e"
             % (float(np.abs(R.conj().T @ R - np.eye(2)).max()),
                float(np.abs(B.conj().T @ B - np.eye(2)).max())))

    s.append("\n=== Yang–Baxter: örgü temsili olmanın ÖLÇÜTÜ ===")
    s1, s2 = orgu_ureticleri()
    s.append("  ‖σ₁σ₂σ₁ − σ₂σ₁σ₂‖ = %.2e" % yang_baxter_hatasi(s1, s2))
    s.append("  Şahit: keyfî üniterler bunu SAĞLAMAZ —")
    r = np.random.default_rng(0)
    for _ in range(3):
        A = r.normal(size=(2, 2)) + 1j * r.normal(size=(2, 2))
        Q, _q = np.linalg.qr(A)
        A2 = r.normal(size=(2, 2)) + 1j * r.normal(size=(2, 2))
        Q2, _q2 = np.linalg.qr(A2)
        s.append("    rastgele çift: %.4f" % yang_baxter_hatasi(Q, Q2))
    s.append("  R'nin faz üsleri değiştirilirse de bozulur:")
    for a, b in ((-4, 3), (-3, 3), (-4, 2)):
        Rb = np.diag([np.exp(a * 1j * math.pi / 5), np.exp(b * 1j * math.pi / 5)])
        Bb = np.linalg.inv(F) @ Rb @ F
        s.append("    (e^{%dπi/5}, e^{%dπi/5}): %.4f" % (a, b,
                                                         yang_baxter_hatasi(Rb, Bb)))

    s.append("\n=== Örgü evrenselliği: Hadamard'a yaklaşma ===")
    r2 = orgu_yogunlugu(13)
    s.append("  uzunluk   farklı öğe   en iyi mesafe")
    for L, n_, d_ in r2["seyir"]:
        s.append("     %2d      %8d      %.4f" % (L, n_, d_))
    s.append("  en iyi kelime: %s" % (r2["kelime"],))
    s.append("  Grup SONLU DEĞİL (farklı öğe sayısı ~1.88^L büyüyor) ve")
    s.append("  mesafe iniyor -- ama BASAMAKLI iniyor. Rastgele arama")
    s.append("  bunu göremiyordu: 4000 denemeyle uzunluk 4, 8 ve 16'da")
    s.append("  mesafe hep 0.2074 çıkıyor, düşmüyormuş gibi görünüyordu.")
    s.append("  Bu bir yakınsama ŞAHİDİDİR, ispat değil.")

    s.append("\n=== Majorana: {γ_j,γ_k} = 2δ_{jk} I ===")
    for n in (2, 3, 4):
        h = antikomutator_hatasi(majorana(n))
        s.append("  n=%d (2n=%d kip): köşegen=%.2e  köşegen dışı=%.2e  "
                 "hermityenlik=%.2e"
                 % (n, 2 * n, h["köşegen_hata"], h["köşegen_dışı_hata"],
                    h["hermityenlik_hatası"]))
    s.append("  Jordan–Wigner Z zinciri KALDIRILIRSA:")
    for n in (2, 3, 4):
        h = antikomutator_hatasi(jw_zincirsiz_majorana(n))
        s.append("  n=%d: köşegen=%.2e  köşegen dışı=%.2e   ← bozuluyor"
                 % (n, h["köşegen_hata"], h["köşegen_dışı_hata"]))

    s.append("\n=== Kitaev yüzey kodu: [A_s, B_p] = 0 ===")
    for L in (2, 3, 4, 5):
        k = YuzeyKodu(L)
        h = k.ortak_kenar_sayilari()
        m = k.mantiksal_kubit_sayisi()
        s.append("  L=%d  ortak kenar histogramı=%s  → yalnız {0,2}: %s"
                 % (L, h, set(h) <= {0, 2}))
        s.append("       kubit=%d  bağımsız dengeleyici=%d  "
                 "mantıksal kubit=%d (beklenen 2)"
                 % (m["kubit"], m["bağımsız_dengeleyici"],
                    m["mantıksal_kubit"]))
    s.append("  L=2'de tam dizeyle (256×256) doğrudan sağlama:")
    s.append("    max ‖A_s B_p − B_p A_s‖ = %.2e"
             % YuzeyKodu(2).komutator_hatasi_tam())
    s.append("  Bir yıldızla bir yüz ya 0 ya 2 kenar paylaşır; iki takas")
    s.append("  iki eksi verir, çarpım +1'dir. Sayısal sonuç bunu tutuyor.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
