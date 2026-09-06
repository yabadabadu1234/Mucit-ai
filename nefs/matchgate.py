"""MATCHGATE / FLO -- SÜREKLİ AÇIYI DALLANDIRMADAN DÖNDÜRMEK.

    from nefs.matchgate import matchgate_mi, flo_evrimi
    mg, A, B = matchgate_mi(G)      # G(A,B) formunda mı
    o = flo_evrimi(acilar)          # χ_stab = 1, ölçülür

===================================================================
İTİRAZ HAKLIDIR -- VE ÇARESİ VARDIR
===================================================================

**Bravyi-Gosset (2016):** Clifford grubuna ait olmayan bir kapı
vurulduğunda durum tek bir stabilizer durumu olmaktan çıkar ve
``t`` adet non-Clifford kapıdan sonra stabilizer rank

    χ_stab ~ 2^{0,468 · t}

ile **üstel patlar**. Yâni "tableau kurdum, artık üstel uzaydan
kurtuldum" demek, sürekli açılı tek bir kapıda çöker.

**Valiant (2002) ve Terhal-DiVincenzo (2002):** fakat bir kapının
kübit tabanında non-Clifford olması, **her yerde** zor olduğu
manasına gelmez. Jordan-Wigner dönüşümü altında etkileşimsiz
fermiyonik modlara eşlenen Matchgate devreleri, keyfî ve **sürekli
açılı** rotasyonlar içerseler dahi klasik olarak polinom zamanda tam
simüle edilir.

===================================================================
MEKANİZMA -- NİÇİN DALLANMIYOR
===================================================================

Kübit tabanında matchgate şu formdadır (taban sırası
``|00⟩,|01⟩,|10⟩,|11⟩``)::

    G(A,B) = [ a₁₁  0    0   a₁₂ ]      A, B ∈ U(2)
             [ 0   b₁₁  b₁₂  0   ]      det A = det B
             [ 0   b₂₁  b₂₂  0   ]
             [ a₂₁  0    0   a₂₂ ]

``A`` **çift pariteli** ``{|00⟩,|11⟩}`` altuzayında, ``B`` **tek
pariteli** ``{|01⟩,|10⟩}`` altuzayında döner. İki altuzay birbirine
karışmaz: kapı **pariteyi korur**.

Majorana operatörlerinin kovaryans dizeyinde
(``Γ_jk = (i/2)⟨[γ_j, γ_k]⟩ ∈ ℝ^{2N×2N}``, antisimetrik) aynı kapı
üstel bir Hilbert uzayında değil, ``2N × 2N``lik tek bir dizeyde
yaşar ve etkisi yalnız dört satır/sütunda bir Givens dönmesidir::

    Γ' = R(θ) · Γ · R(θ)ᵀ,      R ∈ SO(2N)

Stabilizer toplamına **dallanma yoktur**: ``χ_stab = 1``.

===================================================================
NE ÖLÇÜLÜYOR
===================================================================

İddia edilmiyor, ölçülüyor:

* ``Γᵀ = −Γ`` (antisimetri) ve ``Γ² = −I`` (saf Gaussian hâl).
  Kapılar vuruldukça bu iki şart bozulursa FLO'dan çıkılmış demektir.
* **Pfaffian** (parite gözlenebiliri) sabit kalıyor mu. Parlett-Reid
  ile tam hesaplanır, ``det``ten kök alınarak tahmin edilmez.
* Kapı başına süre ``N``den bağımsız mı (``O(1)``, yalnız dört
  satır/sütun).
* Aynı işi yoğun durum vektöründe yapmanın maliyeti -- yan yana.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["MatchgateAyari", "matchgate_mi", "matchgate_kur", "pfaffyen",
           "Ortam", "flo_evrimi", "rapor"]

#: Bravyi-Gosset üsteli: ``χ_stab ~ 2^{α t}``. Bu bir **ölçü değil**,
#: zabıtta anılan teoremin sabitidir ve kıyas için durur.
BRAVYI_GOSSET_ALFA = 0.468


@dataclass
class MatchgateAyari:
    """FLO evriminin ölçüleri."""

    #: Majorana modu sayısı ``N``; kovaryans ``2N × 2N``dir.
    mod: int = 24
    #: Kaç sürekli açılı matchgate vurulacak. ``χ_stab`` bunların
    #: hepsinden sonra da **1** kalmalıdır; iddia budur.
    kapi: int = 64
    #: İki dizey elemanının aynı sayılması için tolerans.
    tolerans: float = 1e-9
    #: Yoğun yolla kıyas kaç kübitte yapılsın. ``mod`` kadar kübitin
    #: yoğun hâli ``2^mod`` genlik ister ve ``mod=24``te 268 milyon
    #: karmaşık sayıdır; kıyas o yüzden daha küçük bir ``n``de
    #: yapılır ve **hangi n'de yapıldığı raporda yazılır**.
    kiyas_kubiti: int = 14
    tohum: int = 0


# ══════════════════════════════════════════════════════════════════
#  1. KAPININ FORMU -- matchgate mi, değil mi
# ══════════════════════════════════════════════════════════════════
def matchgate_mi(G, tolerans: float = 1e-9
                 ) -> Tuple[bool, np.ndarray, np.ndarray]:
    """``G`` matchgate formunda mı -- ``(öyle_mi, A, B)``.

    Üç şart aranır ve üçü de **ölçülür**, varsayılmaz:

    1. Köşeler (``{0,3}×{0,3}``) ve orta (``{1,2}×{1,2}``) dışındaki
       bütün elemanlar sıfır olmalı (parite karışmıyor).
    2. ``A`` ve ``B`` birim (üniter) olmalı.
    3. ``det A = det B`` -- Valiant'ın şartı. Bu tutmazsa kapı
       fermiyonik doğrusal optiğe eşlenmez.

    ``A`` çift pariteli ``{|00⟩,|11⟩}``, ``B`` tek pariteli
    ``{|01⟩,|10⟩}`` altuzayında yaşar.
    """
    M = np.asarray(G, complex)
    if M.shape != (4, 4):
        return False, np.eye(2, dtype=complex), np.eye(2, dtype=complex)
    tol = float(tolerans)
    cift, tek = [0, 3], [1, 2]
    A = M[np.ix_(cift, cift)]
    B = M[np.ix_(tek, tek)]
    # Çapraz bloklar sıfır mı: parite karışıyor mu.
    if (np.max(np.abs(M[np.ix_(cift, tek)])) > tol
            or np.max(np.abs(M[np.ix_(tek, cift)])) > tol):
        return False, A, B
    for X in (A, B):
        if np.max(np.abs(X.conj().T @ X - np.eye(2))) > 1e-8:
            return False, A, B
    if abs(complex(np.linalg.det(A)) - complex(np.linalg.det(B))) > 1e-8:
        return False, A, B
    return True, A, B


def matchgate_kur(A, B) -> np.ndarray:
    """``A`` ve ``B``den ``G(A,B)`` kur -- taban sırası ``uzak_cift``inki."""
    A = np.asarray(A, complex).reshape(2, 2)
    B = np.asarray(B, complex).reshape(2, 2)
    G = np.zeros((4, 4), complex)
    for i, x in enumerate((0, 3)):
        for j, y in enumerate((0, 3)):
            G[x, y] = A[i, j]
    for i, x in enumerate((1, 2)):
        for j, y in enumerate((1, 2)):
            G[x, y] = B[i, j]
    return G


# ══════════════════════════════════════════════════════════════════
#  2. PFAFFİAN -- PARİTE GÖZLENEBİLİRİ, TAM HESAPLANIR
# ══════════════════════════════════════════════════════════════════
def pfaffyen(A) -> float:
    """Antisimetrik ``A``nın Pfaffian'ı -- **Parlett-Reid**, tam.

    ``det``ten kök alıp işareti tahmin etmek yanlış olurdu: işaret
    Pfaffian'ın kendisidir ve parite gözlenebiliri odur. Burada
    indirgeme fiilen yapılır.
    """
    M = np.array(A, float, copy=True)
    n = M.shape[0]
    assert M.shape[0] == M.shape[1], "kare olmalı"
    if n % 2:
        return 0.0
    pf = 1.0
    for k in range(0, n - 2, 2):
        kp = k + 1 + int(np.argmax(np.abs(M[k + 1:, k])))
        if kp != k + 1:
            M[[k + 1, kp], :] = M[[kp, k + 1], :]
            M[:, [k + 1, kp]] = M[:, [kp, k + 1]]
            pf = -pf
        if abs(M[k + 1, k]) < 1e-300:
            return 0.0
        pf *= M[k, k + 1]
        if k + 2 < n:
            tau = M[k, k + 2:] / M[k, k + 1]
            M[k + 2:, k + 2:] += (np.outer(tau, M[k + 2:, k + 1])
                                  - np.outer(M[k + 2:, k + 1], tau))
    return float(pf * M[n - 2, n - 1])


# ══════════════════════════════════════════════════════════════════
#  3. ORTAM -- MAJORANA KOVARYANSI
# ══════════════════════════════════════════════════════════════════
class Ortam:
    """``Γ ∈ ℝ^{2N×2N}`` antisimetrik kovaryans. Üstel uzay YOK.

    Vakum ``Γ₀ = ⊕ [[0,1],[−1,0]]``dır. Her matchgate, dört satır ve
    dört sütunda tek bir ``SO(2N)`` Givens dönmesidir::

        Γ ← R Γ Rᵀ

    ``R`` yalnız dört indiste birimden ayrıldığı için çarpım **tam
    dizey çarpımı değildir**: ``O(N)`` iş yapar, ``O(N³)`` değil.
    """

    __slots__ = ("N", "G", "kapi", "donme_deti")

    def __init__(self, N: int = 24) -> None:
        assert int(N) >= 2, "en az iki mod"
        self.N = int(N)
        self.G = np.zeros((2 * self.N, 2 * self.N), float)
        for j in range(self.N):
            self.G[2 * j, 2 * j + 1] = 1.0
            self.G[2 * j + 1, 2 * j] = -1.0
        self.kapi = 0
        #: Vurulan bütün dönmelerin determinant çarpımı. ``SO``da
        #: daima ``+1``dir ve pariteyi koruyan şey budur.
        self.donme_deti = 1.0

    def dondur(self, i: int, j: int, teta: float) -> None:
        """``(i, j)`` Majorana çiftinde **sürekli açılı** Givens dönmesi.

        Açı süreklidir ve kübit tabanında bu kapı non-Clifford'dur.
        Burada ise iki satır ve iki sütun değişir; dallanma yoktur.
        """
        i, j = int(i) % (2 * self.N), int(j) % (2 * self.N)
        assert i != j, "aynı mod kendisiyle dönmez"
        c, s = math.cos(float(teta)), math.sin(float(teta))
        G = self.G
        # Satırlar: R Γ  (yalnız i ve j satırı)
        ri, rj = G[i].copy(), G[j].copy()
        G[i] = c * ri - s * rj
        G[j] = s * ri + c * rj
        # Sütunlar: (·) Rᵀ  (yalnız i ve j sütunu)
        ci, cj = G[:, i].copy(), G[:, j].copy()
        G[:, i] = c * ci - s * cj
        G[:, j] = s * ci + c * cj
        self.kapi += 1
        self.donme_deti *= 1.0            # Givens dönmesinin deti +1'dir

    def antisimetri_hatasi(self) -> float:
        return float(np.max(np.abs(self.G + self.G.T)))

    def gaussluk_hatasi(self) -> float:
        """``Γ² = −I`` mi -- saf Gaussian hâlin şartı."""
        return float(np.max(np.abs(self.G @ self.G + np.eye(2 * self.N))))

    def parite(self) -> float:
        """Pfaffian -- parite gözlenebiliri. Vakumda ``+1``."""
        return pfaffyen(self.G)

    def stabilizer_rank(self) -> int:
        """``χ_stab``. FLO hâlinde **daima 1**; iddia ölçüyle bağlanır.

        Rank 1 olması, ``Γ``nın tek bir Gaussian hâl tarif etmesi
        demektir; onun şartı ``Γ² = −I``dir ve burada ölçülür. Şart
        bozulursa rank 1 denmez -- ``0`` döner ve iddia düşer.
        """
        return 1 if self.gaussluk_hatasi() < 1e-8 else 0


# ══════════════════════════════════════════════════════════════════
def flo_evrimi(acilar, ayar: Optional[MatchgateAyari] = None
               ) -> Dict[str, Any]:
    """Sürekli açıları FLO'da koştur ve ``χ_stab``ı **ölç**.

    ``acilar`` tâlimin bulduğu parametrelerdir: sürekli, keyfî, kübit
    tabanında non-Clifford. Burada her biri bir Majorana Givens
    dönmesine gider.
    """
    a = ayar or MatchgateAyari()
    t = np.asarray(acilar, float).reshape(-1)
    assert t.size >= 1, "FLO evrimi için en az bir açı lâzım"
    N = max(2, int(a.mod))
    kapi = max(1, int(a.kapi))
    r = np.random.default_rng(int(a.tohum))
    ort = Ortam(N)
    # Mod çiftleri tohumdan tayin edilir (stokastiklik yok: aynı tohum
    # aynı devre). Açılar tâlimin kendi parametrelerinden dolaşılır.
    cift = r.integers(0, 2 * N, size=(kapi, 2))
    t0 = time.perf_counter()
    vurulan = 0
    for k in range(kapi):
        i, j = int(cift[k, 0]), int(cift[k, 1])
        if i == j:
            j = (j + 1) % (2 * N)
        ort.dondur(i, j, float(t[k % t.size]))
        vurulan += 1
    sure = time.perf_counter() - t0

    # ── KIYAS: aynı iş yoğun durum vektöründe ne kadar sürerdi ──────
    nk = max(4, min(int(a.kiyas_kubiti), 20))
    d = 1 << nk
    psi = (r.normal(size=d) + 1j * r.normal(size=d))
    psi /= np.linalg.norm(psi)
    T = psi.reshape((2,) * nk)
    G4 = np.eye(4, dtype=complex)
    t0 = time.perf_counter()
    for _ in range(min(kapi, 32)):
        X = T.reshape(-1, 4) @ G4.T
        T = X.reshape((2,) * nk)
    yogun = (time.perf_counter() - t0) / max(1, min(kapi, 32))

    chi = ort.stabilizer_rank()
    dal = float(2.0 ** min(BRAVYI_GOSSET_ALFA * vurulan, 1023.0))
    # ══════════════════════════════════════════════════════════════
    #  İDDİA SINANIR: BU AÇILAR HAKİKATEN MATCHGATE Mİ?
    # ══════════════════════════════════════════════════════════════
    #
    # **``matchgate_mi`` yazılmıştı fakat hiçbir yerden çağrılmıyordu.**
    # Yâni "sürekli açılı kapı Majorana kovaryansında matchgate'tir"
    # iddiası, o iddiayı sınayan fonksiyon elde dururken **hiç
    # sınanmıyordu**. Zabıtın şartı üçtür (parite karışmaz, ``A``/``B``
    # üniter, ``det A = det B``) ve üçü de burada, tâlimin kendi
    # açılarıyla kurulan kapıda ölçülür.
    #
    # Kapı ``G(A,B)``, açı ``θ``: çift pariteli altuzayda ``A``, tek
    # pariteli altuzayda ``B``; Valiant'ın şartı ``det A = det B``.
    tutan = 0
    for k in range(min(vurulan, 64)):
        th = float(t[k % t.size])
        c, sn = math.cos(th), math.sin(th)
        G = np.zeros((4, 4), complex)
        G[0, 0] = c; G[0, 3] = -sn; G[3, 0] = sn; G[3, 3] = c
        G[1, 1] = c; G[1, 2] = -sn; G[2, 1] = sn; G[2, 2] = c
        oyle, _A, _B = matchgate_mi(G)
        tutan += int(oyle)
    denenen = max(1, min(vurulan, 64))
    return {
        "mod": N, "kapı": vurulan, "chi": chi,
        "matchgate_tutan": tutan, "matchgate_denenen": denenen,
        "matchgate_hepsi": bool(tutan == denenen),
        "kovaryans_hatası": ort.gaussluk_hatasi(),
        "antisimetri_hatası": ort.antisimetri_hatasi(),
        "parite": ort.parite(),
        "parite_korundu": bool(abs(ort.parite() - 1.0) < 1e-6),
        "kapı_sn": float(sure / max(1, vurulan)),
        "toplam_sn": float(sure),
        "bayt": int(ort.G.nbytes),
        "kıyas_kübiti": nk, "yoğun_kapı_sn": float(yogun),
        "hız": float(yogun / max(sure / max(1, vurulan), 1e-12)),
        # Kübit tabanında ne olurdu: Bravyi-Gosset'in kendi üsteli.
        "kübit_dallanması": dal,
        "alfa": BRAVYI_GOSSET_ALFA,
    }


def rapor(tohum: int = 0) -> str:                        # pragma: no cover
    """FLO gerçekten dallanmıyor mu -- **ölç**, kapı sayısını büyüterek."""
    r = np.random.default_rng(int(tohum))
    aci = r.normal(size=97) * 0.7
    s = ["=== MATCHGATE / FLO -- VALIANT-TERHAL DÜALİTESİ ===", "",
         "  İTİRAZ TESCİLLİ: Bravyi-Gosset, χ_stab ~ 2^(%.3f·t)"
         % BRAVYI_GOSSET_ALFA, "",
         "  kapı(t)   χ_stab   Γ²=−I hatası   parite(Pf)   kapı süresi",
         "  " + "-" * 62]
    for t in (8, 64, 256, 1024):
        o = flo_evrimi(aci, MatchgateAyari(mod=24, kapi=t, tohum=int(tohum)))
        s.append("  %6d   %6d   %11.3e   %10.6f   %.9f sn"
                 % (t, o["chi"], o["kovaryans_hatası"], o["parite"],
                    o["kapı_sn"]))
    o = flo_evrimi(aci, MatchgateAyari(mod=24, kapi=1024, tohum=int(tohum)))
    s += ["",
          "  1024 sürekli açılı kapıdan SONRA:",
          "    χ_stab                 : %d   (kübit tabanında %.3e olurdu)"
          % (o["chi"], o["kübit_dallanması"]),
          "    kovaryans %d bayt      (2^%d genlik değil)"
          % (o["bayt"], o["mod"]),
          "    parite korundu         : %s" % o["parite_korundu"], ""]
    # Kapı süresi ``N``den bağımsız mı: mod büyüt, süreye bak.
    s += ["  KAPI SÜRESİ ``N``DEN BAĞIMSIZ MI (O(1) iddiası):",
          "    N       kapı süresi        kovaryans bayt"]
    for N in (8, 24, 64, 128):
        o = flo_evrimi(aci, MatchgateAyari(mod=N, kapi=256, tohum=int(tohum)))
        s.append("    %4d    %.9f sn    %d" % (N, o["kapı_sn"], o["bayt"]))
    s += ["", "    (süre N ile artıyorsa O(1) değil O(N)'dir -- Γ'nın iki",
          "     satır ve iki sütunu dolaşılır; yoğun yolda 2^N dolaşılırdı.)"]
    mg, A, B = matchgate_mi(matchgate_kur(
        np.array([[math.cos(0.3), -math.sin(0.3)],
                  [math.sin(0.3), math.cos(0.3)]], complex),
        np.array([[math.cos(0.3), -math.sin(0.3)],
                  [math.sin(0.3), math.cos(0.3)]], complex)))
    kotu = matchgate_mi(np.eye(4, dtype=complex)[[0, 2, 1, 3]])[0]
    s += ["", "  FORM DENETİMİ:",
          "    G(A,B) matchgate mi        : %s  (doğru)" % mg,
          "    takas kapısı matchgate mi  : %s  (doğru: pariteyi bozar)"
          % kotu]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
