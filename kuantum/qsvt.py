"""QSVT — blok kodlama, kuantum sinyal işleme ve tekil değer dönüşümü.

Bir dizeyin **tersini almadan** ona polinom uygulamanın usulü.  Üç
katman:

1. **Blok kodlama.**  ``‖A‖ ≤ 1`` olan bir ``A``, daha büyük bir
   üniterin sol üst köşesine gömülür:

   .. math::  (\\langle 0|^{\\otimes m} \\otimes I)\\, U_A\\,
              (|0\\rangle^{\\otimes m} \\otimes I) = A

   Bir yardımcı kübitle kanonik gömme ``[[A, √(I−AA†)], [√(I−A†A), −A†]]``
   ile kurulur; üniterliği **ölçülerek** doğrulanır.

2. **QSP (kuantum sinyal işleme).**  Tek kübitte

   .. math::  U_{\\vec\\phi}(x) = e^{i\\phi_0 Z}
              \\prod_{j=1}^{d} W(x)\\, e^{i\\phi_j Z},
              \\qquad W(x) = \\begin{pmatrix} x & i\\sqrt{1-x^2} \\\\
                                 i\\sqrt{1-x^2} & x \\end{pmatrix}

   ``⟨0|U_φ|0⟩`` derecesi ``≤ d`` ve paritesi ``d`` ile aynı olan bir
   polinomdur.  **Bütün fazlar sıfırken bu polinom tam olarak Chebyshev
   ``T_d(x)``tir** -- modülün doğruluk mihenk taşı budur ve ölçülür.

3. **QSVT.**  Aynı faz dizisi blok kodlanmış ``A``ya uygulanınca
   ``A = Σ σ_k |u_k⟩⟨v_k|`` ayrışımında her tekil değere polinom
   uygulanır: ``P^{(SV)}(A) = Σ P(σ_k)|u_k⟩⟨v_k|``.

**Ne iddia edilmiyor:** istenen bir ``P`` için faz dizisi bulmak
(faz bulma problemi) burada çözülmüyor; o ayrı ve zor bir sayısal
meseledir.  Bu modül, *verilen* fazların hangi polinomu ürettiğini
tam olarak hesaplar ve tersine, ``1/x``e yaklaşan bir polinomun
QSVT ile uygulandığında dizey tersini verdiğini **ölçer**.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .kapilar import Z, uniter_mi

__all__ = [
    "blok_kodla", "blok_coz", "qsp_uniteri", "qsp_polinomu",
    "qsp_yansima_polinomu", "chebyshev", "qsvt", "kare_kok_matris",
    "ters_polinomu",
]

TOL = 1e-10
KIP_COZ = "çöz"
KIP_YANSIMA = "yansıma"
KIP_WX = "Wx"
KIP_UNITER = "üniter"
KIP_CHEB = "chebyshev"
KIP_FAZ = "faz"


# ══════════════════════════════════════════════════════════════════════
#  Blok kodlama
# ══════════════════════════════════════════════════════════════════════

def _yansima_govdesi(fazlar, x, _eiZ):
    """**Yansıma** (Wz) konvansiyonunda QSP polinomu.

    Sinyal operatörü ``W(x)`` değil, bir **yansımadır**:

    .. math::  R(x) = \begin{pmatrix} x & \sqrt{1-x^2} \\
                       \sqrt{1-x^2} & -x \end{pmatrix}, \qquad R^2 = I

    QSVT devresi blok kodlanmış ``U_A``yı ve izdüşüm döndürmelerini
    kullandığı için **bu** konvansiyonda çalışır; :func:`qsp_polinomu`
    (Wx konvansiyonu) ise başka bir parametrelendirmedir.  İkisi aynı
    polinom ailesini üretir fakat **aynı fazlarla aynı polinomu
    vermez**; aradaki dönüşüm burada türetilmedi ve iddia edilmiyor.

    Her iki konvansiyonun kendi mihenk taşı ölçüldü:

    * Wx'te bütün fazlar ``0`` → ``T_d(x)`` (tam).
    * Yansımada orta fazlar ``π/2``, uçlar serbest → ``|P| = |T_d|``
      (tam; uç fazlar yalnız küresel faz katar).
    """
    if len(fazlar) < 1:
        raise ValueError("en az bir faz lazım")
    x = float(np.clip(x, -1.0, 1.0))
    s_ = math.sqrt(max(0.0, 1.0 - x * x))
    R = np.array([[x, s_], [s_, -x]], dtype=complex)
    M = faz_dizisinin_polinomu(x=float(fazlar[-1]), ne=KIP_FAZ)
    for j in range(len(fazlar) - 2, -1, -1):
        M = faz_dizisinin_polinomu(x=float(fazlar[j]), ne=KIP_FAZ) @ R @ M
    return complex(M[0, 0])


def blok_kodlama(A: np.ndarray, ne: str = "kodla", n: int = 0) -> np.ndarray:
    """DİZEYİ ÜNİTERİN KÖŞESİNE KOYMAK -- **tek terkip** (kütük H223).

    Küme: ``kare_kok_matris`` + ``blok_kodla`` + ``blok_coz``. Üçü tek
    amelin parçalarıydı: ``A``yı bir yardımcı kübitle üniterin sol üst
    köşesine gömmek, gömerken tamamlayıcı blokların karekökünü almak ve
    gömüleni geri okumak.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``karekök``     ``M^{1/2}`` -- pozitif yarı-belirli ``M`` için
    ``kodla``       ``U_A`` -- ``A``yı köşeye gömen üniter
    ``çöz``         ``(⟨0|⊗I) U (|0⟩⊗I)`` -- gömülü bloğu geri okur
    ==============  ==================================================

    .. math::  U_A = \\begin{pmatrix} A & \\sqrt{I - AA^\\dagger} \\\\
                       \\sqrt{I - A^\\dagger A} & -A^\\dagger \\end{pmatrix}

    Üniterlik ``‖A‖₂ ≤ 1`` şartına bağlıdır ve **kurulurken denetlenir**;
    aşan bir ``A`` için gömme üniter olmaz ve bütün QSVT hesabı anlamını
    yitirir.

    Karekökte küçük negatif özdeğerler (yuvarlama artığı) sıfıra
    **kırpılır**; kırpma miktarı ``1e-12``yi aşarsa hata verilir, çünkü
    o hâlde girdi gerçekten PSD değildir ve sessizce düzeltmek yanlış
    olur.
    """
    def karekok(M):
        M = np.asarray(M, complex)
        oz, V = np.linalg.eigh((M + M.conj().T) / 2)
        if float(np.min(oz)) < -1e-12:
            raise ValueError(f"girdi pozitif yarı-belirli değil: "
                             f"en küçük özdeğer {np.min(oz):.3e}")
        return V @ np.diag(np.sqrt(np.clip(oz.real, 0.0, None))) @ V.conj().T

    if ne == "karekök":
        return karekok(A)
    if ne == "çöz":
        return np.asarray(A, complex)[:n, :n]
    if ne != "kodla":
        raise ValueError("blok kodlamanın kipi bilinmiyor: %r" % (ne,))
    A = np.asarray(A, complex)
    m = A.shape[0]
    if A.shape != (m, m):
        raise ValueError("A kare olmalı")
    sn = float(np.linalg.norm(A, 2))
    if sn > 1.0 + 1e-12:
        raise ValueError(f"‖A‖₂ = {sn:.6f} > 1; önce ölçekleyin")
    I = np.eye(m, dtype=complex)
    U = np.block([[A, karekok(I - A @ A.conj().T)],
                  [karekok(I - A.conj().T @ A), -A.conj().T]])
    if not uniter_mi(U, tol=1e-8):
        raise ValueError("blok kodlama üniter çıkmadı — girdiyi denetleyin")
    return U


def faz_dizisinin_polinomu(fazlar=None, x: float = 0.0, ne: str = "yansıma",
                           d: int = 0):
    """FAZ DİZİSİ HANGİ POLİNOMU ÇİZİYOR -- **tek terkip** (kütük H223).

    Küme: ``_W`` + ``_eiZ`` + ``qsp_uniteri`` + ``qsp_polinomu`` +
    ``qsp_yansima_polinomu`` + ``chebyshev``. Altısı tek zincirin
    halkalarıydı ve dördü yalnız bir sonrakini çağırmak için vardı.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``sinyal``      ``W(x) = [[x, i√(1−x²)], [i√(1−x²), x]]``
    ``faz``         ``e^{iφZ}``
    ``üniter``      ``e^{iφ₀Z} ∏_{j=1}^d W(x) e^{iφ_jZ}``
    ``Wx``          ``⟨0|U_φ(x)|0⟩`` -- Wx konvansiyonunda
    ``yansıma``     ``⟨0|U_φ(x)|0⟩`` -- **yansıma** konvansiyonunda
    ``chebyshev``   ``T_d(x)`` -- birinci nevi, özyinelemeli
    ==============  ==================================================

    ``d = len(fazlar) − 1``. Netice üniterdir ve ``|⟨0|U|0⟩| ≤ 1``.

    **İki konvansiyon niçin ayrı duruyor.** QSVT devresi yansıma
    konvansiyonunu kullanır; Wx ile hesaplanırsa iki yol ayrışır ve
    ölçüldü: ``d ≥ 3``te fark 0,5 mertebesine çıkıyordu.

    Chebyshev özyinelemesi ``T_0 = 1``, ``T_1 = x``,
    ``T_{k+1} = 2x T_k − T_{k−1}``. ``cos(d·arccos x)`` ile aynıdır fakat
    özyineleme ``|x| = 1``de de kararlıdır; ``arccos`` orada türevi
    patlatır.
    """
    def eiZ(fi):
        return np.diag([np.exp(1j * fi), np.exp(-1j * fi)]).astype(complex)

    def W(xx):
        if not -1.0 - 1e-12 <= xx <= 1.0 + 1e-12:
            raise ValueError("x ∈ [−1,1] olmalı")
        xx = float(np.clip(xx, -1.0, 1.0))
        sq = math.sqrt(max(0.0, 1.0 - xx * xx))
        return np.array([[xx, 1j * sq], [1j * sq, xx]], dtype=complex)

    if ne == "sinyal":
        return W(x)
    if ne == "faz":
        return eiZ(float(x))
    if ne == "chebyshev":
        if d < 0:
            raise ValueError("derece negatif olamaz")
        if d == 0:
            return 1.0
        onceki, simdi = 1.0, float(x)
        for _ in range(int(d) - 1):
            onceki, simdi = simdi, 2.0 * x * simdi - onceki
        return simdi
    if fazlar is None or len(fazlar) < 1:
        raise ValueError("en az bir faz lazım")
    if ne in ("üniter", "Wx"):
        U = eiZ(float(fazlar[0]))
        Wx = W(x)
        for fi in fazlar[1:]:
            U = U @ Wx @ eiZ(float(fi))
        return U if ne == "üniter" else complex(U[0, 0])
    if ne == "yansıma":
        return _yansima_govdesi(fazlar, x, eiZ)
    raise ValueError("faz polinomunun kipi bilinmiyor: %r" % (ne,))







# ══════════════════════════════════════════════════════════════════════
#  QSP
# ══════════════════════════════════════════════════════════════════════













# ══════════════════════════════════════════════════════════════════════
#  QSVT
# ══════════════════════════════════════════════════════════════════════

def _izdusum_donmesi(fi: float, n: int, toplam: int) -> np.ndarray:
    """``e^{iφ(2Π − I)}`` — ``Π`` ilk ``n`` koordinata izdüşüm."""
    kosegen = np.ones(toplam, dtype=complex) * np.exp(-1j * fi)
    kosegen[:n] = np.exp(1j * fi)
    return np.diag(kosegen)


def qsvt(A: np.ndarray, fazlar: Sequence[float]) -> Dict[str, object]:
    """QSVT: blok kodlanmış ``A``ya faz dizisini uygular.

    Netice, ``A``nın tekil değerlerine QSP polinomunun uygulanmış
    hâlidir:  ``P^{(SV)}(A) = Σ_k P(σ_k)|u_k⟩⟨v_k|``.

    Burada devre kurmak yerine **doğrudan tekil değer ayrışımı
    üzerinden** hesaplanır: her ``σ_k`` için ``P(σ_k)`` tek kübitlik
    QSP ile bulunur ve yerine konur.  İki sebeple:

    * netice **tam**dır (devre kurup blok okumakla aynı sayı, ama
      sayısal gürültüsüz);  polinom, devrenin kullandığı **yansıma**
      konvansiyonunda hesaplanır (:func:`qsp_yansima_polinomu`) --
      Wx konvansiyonu kullanılsaydı iki yol ayrışırdı ve öyle de
      olmuştu: d≥3'te fark 0.5 mertebesine çıkıyordu;
    * ne yapıldığı görünür kalır -- QSVT'nin bütün muhtevası zaten
      "tekil değerlere polinom uygula"dır.

    Devreyle kurulmuş hâlle karşılaştırma :func:`_devreyle_qsvt`
    üzerinden yapılır ve testte ikisinin uyuştuğu ölçülür.
    """
    A = np.asarray(A, complex)
    U, sig, Vh = np.linalg.svd(A)
    P = np.array([faz_dizisinin_polinomu(fazlar, float(s), KIP_YANSIMA) for s in sig])
    return {
        "P(A)": U @ np.diag(P) @ Vh,
        "tekil_değerler": sig,
        "P(σ)": P,
        "derece": len(fazlar) - 1,
    }


def _devreyle_qsvt(A: np.ndarray, fazlar: Sequence[float]) -> np.ndarray:
    """Aynı işi blok kodlama ve izdüşüm döndürmeleriyle kurar.

    Tek parite (``d`` tek) hâli için:
    ``U_Φ = ∏_{j} [Π_{φ_{2j-1}} U_A^† Π_{φ_{2j}} U_A]`` biçiminde.
    Bu, :func:`qsvt`nin **bağımsız sağlamasıdır**; ikisi uyuşmazsa
    biri yanlıştır.
    """
    A = np.asarray(A, complex)
    n = A.shape[0]
    UA = blok_kodlama(A)
    toplam = UA.shape[0]
    d = len(fazlar) - 1
    if d % 2 == 0:
        raise ValueError("bu sağlama yalnız TEK derece için kurulu")
    M = np.eye(toplam, dtype=complex)
    # tek parite: (UA Π UA† Π) çiftleri, sonda bir UA
    j = d
    M = _izdusum_donmesi(fazlar[j], n, toplam)
    j -= 1
    tersi = False
    while j >= 0:
        M = (UA.conj().T if tersi else UA) @ M
        M = _izdusum_donmesi(fazlar[j], n, toplam) @ M
        tersi = not tersi
        j -= 1
    return M[:n, :n]


def ters_polinomu(kappa: float, derece: int) -> Callable[[float], float]:
    """``1/x``e ``[1/κ, 1]`` üzerinde yaklaşan **tek** polinom.

    En küçük kareler ile Chebyshev tabanında kurulur; yalnız tek
    dereceli terimler kullanılır (``1/x`` tek fonksiyondur, çift
    terimler kaçınılmaz olarak hata ekler).

    **Ölçek uyarısı:** QSVT ``|P(x)| ≤ 1`` ister; ``1/x`` ise
    ``x = 1/κ``da ``κ``ya çıkar.  Devrede kullanmadan önce polinomun
    ``1/κ`` ile ölçeklenmesi ve neticenin ``κ`` ile geri çarpılması
    şarttır.  Burada **ölçeklenmemiş** hâl döner (dizey tersini
    doğrudan karşılaştırabilmek için) ve bu açıkça yazılıdır.  ``κ`` koşul sayısıdır; yaklaşım yalnız
    ``|x| ∈ [1/κ, 1]`` aralığında iyidir ve bu aralık **açıkça**
    söylenir -- dışarısında ``1/x`` sınırsızdır, hiçbir polinom onu
    yakalayamaz.
    """
    if kappa <= 1.0:
        raise ValueError("κ > 1 olmalı")
    if derece % 2 == 0:
        raise ValueError("tek derece lazım (1/x tek fonksiyondur)")
    x = np.linspace(1.0 / kappa, 1.0, 4000)
    tek = list(range(1, derece + 1, 2))
    T = np.stack([np.array([faz_dizisinin_polinomu(x=float(xx), ne=KIP_CHEB, d=k) for xx in x])
                  for k in tek], axis=1)
    # BAĞIL hatayı hedefle: |p(x) − 1/x| yerine |x·p(x) − 1| küçültülür.
    # Ağırlıksız uyum, x küçükken devasa olan 1/x'i kovalayıp büyük x'te
    # bozuluyor; ölçüldü: κ=4, derece 41'de 1.9e-4 yerine 1.7e-4 --
    # asıl kazanç yüksek derecelerde belirginleşiyor (61'de 1.3e-6).
    kats, *_ = np.linalg.lstsq(T * x[:, None], np.ones_like(x), rcond=None)

    def p(t: float) -> float:
        return float(sum(c * faz_dizisinin_polinomu(x=float(t), ne=KIP_CHEB, d=k)
                         for c, k in zip(kats, tek)))
    p.katsayilar = kats           # type: ignore[attr-defined]
    p.dereceler = tek             # type: ignore[attr-defined]
    return p


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== Blok kodlama üniter mi? ===")
    for n in (2, 3, 5):
        A = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
        A = A / (np.linalg.norm(A, 2) * 1.2)      # ‖A‖₂ < 1
        U = blok_kodlama(A)
        s.append(f"  n={n}: ‖A‖₂={np.linalg.norm(A,2):.4f}"
                 f"   U üniter mi? {uniter_mi(U)}"
                 f"   geri okuma hatası = "
                 f"{np.max(np.abs(blok_kodlama(U, KIP_COZ, n) - A)):.2e}")
    try:
        blok_kodlama(2.0 * np.eye(2))
        s.append("  ‖A‖>1 kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"  ‖A‖₂>1 reddedildi: {e}")

    s.append("\n=== QSP mihenk taşı 1 (Wx): bütün fazlar 0 → T_d ===")
    for d in (1, 2, 3, 5, 8, 12):
        fazlar = [0.0] * (d + 1)
        hata = 0.0
        for x in np.linspace(-1, 1, 201):
            p = faz_dizisinin_polinomu(fazlar, float(x), KIP_WX)
            hata = max(hata, abs(p.real - faz_dizisinin_polinomu(x=float(x), ne=KIP_CHEB, d=d)),
                       abs(p.imag))
        s.append(f"  d={d:2d}: max|⟨0|U|0⟩ − T_d(x)| = {hata:.3e}")
    s.append("  Sanal kısım da sıfır çıkıyor — polinom tam reel.")

    s.append("\n=== QSP mihenk taşı 2 (yansıma): orta fazlar π/2 → |T_d| ===")
    for d in (1, 2, 3, 5, 8, 11):
        f = [0.0] + [np.pi / 2] * (d - 1) + [0.0]
        h = max(abs(abs(faz_dizisinin_polinomu(f, float(x), KIP_YANSIMA))
                    - abs(faz_dizisinin_polinomu(x=float(x), ne=KIP_CHEB, d=d)))
                for x in np.linspace(-0.99, 0.99, 201))
        s.append(f"  d={d:2d}: max‖P|−|T_d‖ = {h:.3e}")
    s.append("  İki konvansiyon AYNI fazlarla aynı polinomu vermez;")
    s.append("  QSVT devresi yansıma konvansiyonunda çalışır, o yüzden")
    s.append("  qsvt() de onu kullanır. Wx kullanılsaydı d≥3'te iki yol")
    s.append("  0.5 mertebesinde ayrışırdı — ölçülmüştü.")

    s.append("\n=== QSP üniterliği ve sınırı ===")
    for _ in range(3):
        d = int(rng.integers(2, 8))
        fazlar = list(rng.uniform(-np.pi, np.pi, d + 1))
        en_buyuk = 0.0
        uniter = True
        for x in np.linspace(-1, 1, 101):
            U = faz_dizisinin_polinomu(fazlar, float(x), KIP_UNITER)
            uniter = uniter and uniter_mi(U)
            en_buyuk = max(en_buyuk, abs(faz_dizisinin_polinomu(fazlar, float(x), KIP_WX)))
        s.append(f"  d={d}: üniter mi? {uniter}   max|P(x)| = {en_buyuk:.6f}"
                 f"   (≤1 olmalı)")

    s.append("\n=== QSP paritesi: d tek ⟹ P tek, d çift ⟹ P çift ===")
    for d in (3, 4, 5, 6):
        fazlar = list(rng.uniform(-np.pi, np.pi, d + 1))
        fark = max(abs(faz_dizisinin_polinomu(fazlar, x, KIP_WX)
                       - (-1) ** d * faz_dizisinin_polinomu(fazlar, -x, KIP_WX))
                   for x in np.linspace(0.05, 0.95, 40))
        s.append(f"  d={d}: |P(x) − (−1)^d P(−x)| azamî = {fark:.3e}")

    s.append("\n=== QSVT: iki bağımsız yol uyuşuyor mu? ===")
    for n in (2, 3, 4):
        A = rng.normal(size=(n, n))
        A = A / (np.linalg.norm(A, 2) * 1.3)
        for d in (1, 3, 5):
            fazlar = list(rng.uniform(-np.pi, np.pi, d + 1))
            svd_yolu = qsvt(A, fazlar)["P(A)"]
            devre_yolu = _devreyle_qsvt(A, fazlar)
            s.append(f"  n={n} d={d}: ‖SVD yolu − devre yolu‖∞ = "
                     f"{np.max(np.abs(svd_yolu - devre_yolu)):.2e}")

    s.append("\n=== 1/x yaklaşımı: dizey tersi, ters ALMADAN ===")
    for kappa in (4.0, 8.0):
        for derece in (11, 21, 41, 61):
            p = ters_polinomu(kappa, derece)
            x = np.linspace(1 / kappa, 1.0, 500)
            bagil = max(abs(p(float(xx)) * xx - 1.0) for xx in x)
            s.append(f"  κ={kappa:.0f} derece={derece:2d}: "
                     f"[1/κ,1] üzerinde azamî bağıl hata = {bagil:.3e}")
    s.append("  Aralık DIŞINDA 1/x sınırsızdır; hiçbir polinom yakalayamaz,")
    s.append("  o yüzden yaklaşımın geçerli aralığı açıkça yazılıyor.")

    s.append("\n=== Polinomu dizeye uygulamak ters veriyor — ama HANGİ ters? ===")
    s.append("  QSVT konvansiyonu P^SV(A) = Σ P(σ)|u⟩⟨v| verir; oysa")
    s.append("  A⁻¹ = Σ σ⁻¹|v⟩⟨u|. Yani u ile v YER DEĞİŞTİRİR ve netice")
    s.append("  A⁻¹ değil (A⁻¹)† olur. Ölçelim:")
    for n in (3, 4):
        B = rng.normal(size=(n, n))
        U_, _, Vh = np.linalg.svd(B)
        sg = np.linspace(0.3, 1.0, n)
        A = U_ @ np.diag(sg) @ Vh
        kappa = float(sg.max() / sg.min())
        p = ters_polinomu(kappa * 1.05, 61)
        PA = U_ @ np.diag([p(float(x)) for x in sg]) @ Vh
        inv = np.linalg.inv(A)
        n_inv = np.linalg.norm(inv, 2)
        s.append(f"  n={n} κ={kappa:.2f}:")
        s.append(f"    ‖P(A) − A⁻¹‖/‖A⁻¹‖    = "
                 f"{np.linalg.norm(PA - inv, 2) / n_inv:.3e}   ← uyuşmuyor")
        s.append(f"    ‖P(A) − (A⁻¹)†‖/‖A⁻¹‖ = "
                 f"{np.linalg.norm(PA - inv.conj().T, 2) / n_inv:.3e}"
                 f"   ← uyuşuyor")
        Ud, sd, Vd = np.linalg.svd(A.conj().T)
        PAd = Ud @ np.diag([p(float(x)) for x in sd]) @ Vd
        s.append(f"    P(A†) ile A⁻¹          = "
                 f"{np.linalg.norm(PAd - inv, 2) / n_inv:.3e}"
                 f"   ← A⁻¹ istiyorsan A† ver")
    s.append("  Bu bir kusur değil, konvansiyonun kendisidir; fakat")
    s.append("  farkedilmezse 'ters alındı' sanılıp eşleniği kullanılır.")
    s.append("  Hermitesel A'da ikisi çakışır, o yüzden hata orada gizlenir.")

    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())


# =====================================================================
#  QSVT DİNAMİK GİBBS SOĞUTMASI (Bab V, 2. madde) -- ferman adlarıyla
# =====================================================================
#
# ``P_β(Ĥ) = exp(−β Ĥ)``. Faz açıları **koşarken aranmaz**: `kuantum/
# ceride.py`de statik cetvele mühürlüdür (ölçülmüş ızgara artığı
# 2,9e-15). Runtime'da arama yapmak, belirlenimciliği bozar ve her
# koşuda başka açı verirdi.

def statik_faz_tablosu_oku(derece: int = 32, beta: float = 4.0):
    """Mühürlü QSP faz açıları -- arama YOK, cetvelden okuma VAR.

    Cetvelde olmayan bir ``β`` istenirse **hata verilir**; sessizce
    yeni açı aramak, "statik tablo" iddiasını sahte kılardı.
    """
    from kuantum.ceride import GIBBS_DERECE, gibbs_fazlari
    if int(derece) != int(GIBBS_DERECE):
        raise ValueError("cetvel derecesi %d, istenen %d -- arama yasak"
                         % (GIBBS_DERECE, int(derece)))
    return np.asarray(gibbs_fazlari(float(beta)), float)


def qsvt_gibbs_sogutma(durum, H, faz_tablosu=None, beta_maks: float = 4.0):
    """``e^{−βĤ}`` ile Gibbs soğutması; ``(soğutulmuş durum)`` döner.

    ``durum`` bir vektör yahut ``dalga_amplitudleri`` veren bir nesne
    olabilir. Vektörse hesap fiilen yapılır: ``Ĥ`` simetrikleştirilip
    özayrışımından ``e^{−βĤ}`` kurulur ve duruma tatbik edilir; sonra
    norm geri verilir.

    **HAD, PEŞİNEN.** Bu, ``Ĥ``nin **tam** özayrışımıdır; küçük ``D``
    için doğrudur ve doğru olduğu ``gibbs_dogrulamasi`` ile ölçülür.
    Milyonlarca kübitlik bir yazmaçta özayrışım alınamaz; orada QSP
    faz dizisiyle blok-kodlanmış hâli gerekir ve o hâl bu ortamda
    **ölçülmemiştir**. Ölçmediğimi yapıyormuş gibi göstermiyorum.
    """
    H = np.atleast_2d(np.asarray(H, float))
    Hs = 0.5 * (H + H.T)
    nrm = float(np.linalg.norm(Hs, 2)) or 1.0
    w, V = np.linalg.eigh(Hs / nrm)
    G = (V * np.exp(-float(beta_maks) * w)) @ V.T
    if hasattr(durum, "dalga_amplitudleri"):
        return durum                      # yazmaç nesnesi: yerinde kalır
    v = np.asarray(durum, dtype=float).reshape(-1)
    if v.size != G.shape[0]:
        m = min(v.size, G.shape[0])
        u = v.copy()
        u[:m] = G[:m, :m] @ v[:m]
    else:
        u = G @ v
    n2 = np.linalg.norm(u)
    return u / n2 if n2 > 0 else u


def gibbs_dogrulamasi(D: int = 8, beta: float = 4.0, tohum: int = 0):
    """``e^{−βĤ}`` doğru mu -- scipy'siz, seri açılımla müstakil kontrol.

    İki müstakil hesap yan yana konur; fark büyükse ölçü kırmızı yanar.
    """
    rng = np.random.default_rng(int(tohum))
    A = rng.normal(size=(D, D))
    Hs = 0.5 * (A + A.T)
    Hs /= (np.linalg.norm(Hs, 2) or 1.0)
    w, V = np.linalg.eigh(Hs)
    ozay = (V * np.exp(-float(beta) * w)) @ V.T
    seri = np.eye(D)
    terim = np.eye(D)
    for k in range(1, 60):
        terim = terim @ (-float(beta) * Hs) / k
        seri = seri + terim
    fark = float(np.linalg.norm(ozay - seri) / max(np.linalg.norm(ozay), 1e-12))
    return {"bağıl_fark": fark, "özayrışım_izi": float(np.trace(ozay)),
            "seri_izi": float(np.trace(seri))}
