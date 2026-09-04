"""Dalga bükümü: WKB tünelleme, GRAPE optimal kontrol, Wilson holonomisi.

Kaynak: ``docs/kaynak/kuantum_dalga_bukum.tex``.

**M20 -- tünelleme ``O(1)`` değildir.**  Risalenin kendi WKB formülü
``T = e^{−γ}``, ``γ = (2/ħ)∫√(2m(V−E))dx`` doğrudur.  Bir sonraki
cümlede "``O(1)`` mertebesinde doğrudan geçilir" demek bu formülle
çelişir: olasılık üstel **küçük**, dolayısıyla beklenen geçiş süresi
``1/T = e^{+γ}`` üstel **büyüktür**.  Ölçüldü (``V=1, E=0.2, m=ħ=1``):
engel genişliği 1'de ``T = 7.97e-02`` (beklenen deneme 12.6), genişlik
8'de ``T = 1.62e-09`` (beklenen deneme **6.2e+08**).  Kazanç ``O(1)``e
inmek değil, klasik olarak **sıfır** olan olasılığın pozitif olmasıdır.

**M21 -- düz bağlantı trivial holonomi vermez.**  Stokes ile
``ΔΦ = ∬_Σ F`` yazmak için çevrimin bir yüzey **sınırlaması** gerekir.
Halka gibi büzülemeyen bir bölgede ``F ≡ 0`` iken bile holonomi 1
olmayabilir -- Aharonov--Bohm etkisinin tamamı budur.  Ölçüldü:
8 düğümlü çevrimde her kenarda yerel düz bağlantı, toplam akı
``0.37·2π`` iken ``|W − 1| = 1.836``.  Cümle patikaları kapalı
çevrimler olduğundan ölçüt ``F = 0`` değil ``W(γ) = 1`` olmalıdır.

**M22 -- GRAPE gradyanı yaklaşımdır.**  Kaynak eşitlik yazıyor; oysa
bağıntı ``e^{−iH_jΔt}``nin birinci mertebeden açılımından gelir ve
``[H_j, H_k] ≠ 0`` olduğu için tam değildir.  Ölçüldü: ``Δt``yi yarıya
indirdikçe sonlu farkla arasındaki fark **dörtte bire** iniyor, yani
hata ``O(Δt²)``.  Tam türev için üstelin Fréchet türevi gerekir; o da
burada kurulu ve iki yol kıyaslanıyor.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "wkb_gamma", "wkb_gecirgenlik", "beklenen_deneme",
    "tunel_maliyet_cetveli",
    "holonomi", "duz_mu", "aharonov_bohm", "cevrim_egriligi",
    "grape_gradyani", "tam_gradyan", "sonlu_fark_gradyani",
    "grape_kos", "sadakat",
]

HBAR = 1.0


# ══════════════════════════════════════════════════════════════════════
#  1. WKB tünelleme (M20)
# ══════════════════════════════════════════════════════════════════════

def wkb_gamma(V: Callable[[np.ndarray], np.ndarray], E: float,
              x1: float, x2: float, m: float = 1.0, hbar: float = HBAR,
              n: int = 4001) -> float:
    """``γ = (2/ħ)∫_{x₁}^{x₂}√(2m(V−E))dx`` — yalnız ``V > E`` bölgesi."""
    x = np.linspace(x1, x2, n)
    ic = np.clip(2.0 * m * (np.asarray(V(x), float) - E), 0.0, None)
    return float(2.0 / hbar * np.trapezoid(np.sqrt(ic), x))


def wkb_gecirgenlik(gamma: float) -> float:
    """``T = e^{−γ}``."""
    return math.exp(-gamma)


def beklenen_deneme(T: float) -> float:
    """Geçiş için beklenen bağımsız deneme sayısı ``1/T``."""
    return float("inf") if T <= 0 else 1.0 / T


def tunel_maliyet_cetveli(genislikler: Sequence[float] = (1, 2, 4, 8),
                          V0: float = 1.0, E: float = 0.2,
                          m: float = 1.0) -> List[Dict[str, float]]:
    """Engel genişliği ile geçirgenlik ve beklenen deneme sayısı."""
    out = []
    for L in genislikler:
        g = wkb_gamma(lambda x: np.full_like(x, V0), E, 0.0, float(L), m)
        T = wkb_gecirgenlik(g)
        out.append({"genişlik": float(L), "γ": g, "T": T,
                    "beklenen_deneme": beklenen_deneme(T)})
    return out


# ══════════════════════════════════════════════════════════════════════
#  2. Wilson holonomisi (M21)
# ══════════════════════════════════════════════════════════════════════

def holonomi(kenar_fazlari: Sequence[float]) -> complex:
    """``W(γ) = exp(i Σ a_e)`` — kapalı çevrim boyunca ``U(1)`` holonomisi."""
    return complex(np.exp(1j * float(np.sum(kenar_fazlari))))


def cevrim_egriligi(kenar_fazlari: Sequence[float],
                    yuz_var_mi: bool = False) -> Dict[str, object]:
    """Yerel eğrilik ve holonomi yan yana.

    Halkada (``yuz_var_mi=False``) çevrimin sınırladığı bir yüz yoktur;
    ``F`` her yerde sıfır olsa bile Stokes uygulanamaz.
    """
    W = holonomi(kenar_fazlari)
    return {"F_yerel_sıfır_mı": True, "yüz_var_mı": yuz_var_mi,
            "holonomi": W, "holonomi_trivial_mi": bool(abs(W - 1) < 1e-12),
            "faz": float(np.angle(W)),
            "toplam_akı_bölü_2pi": float(np.sum(kenar_fazlari)
                                         / (2 * math.pi))}


def duz_mu(kenar_fazlari: Sequence[float]) -> bool:
    """Bağlantı **yerel olarak** düz mü? — her yüzde eğrilik sıfır mı.

    Halkada hiç yüz yoktur, dolayısıyla cevap her zaman ``True``dur;
    mesele tam da budur.
    """
    return True


def aharonov_bohm(N: int = 8, aki_bolu_2pi: float = 0.37
                  ) -> Dict[str, object]:
    """Halka üzerinde düz bağlantı, trivial olmayan holonomi.

    Toplam akı ``N`` kenara eşit dağıtılır; her kenarın kendi
    komşuluğunda bağlantı düzdür (yüz yok), fakat çevrim holonomisi
    ``e^{2πi·akı}``dır.
    """
    a = np.full(N, 2 * math.pi * aki_bolu_2pi / N)
    d = cevrim_egriligi(a, yuz_var_mi=False)
    # kıyas: aynı akı bir DİSKTE olsaydı, Stokes uygulanır ve F ≠ 0 olurdu
    d["disk_olsaydı_F"] = 2 * math.pi * aki_bolu_2pi
    d["|W−1|"] = float(abs(d["holonomi"] - 1))
    return d


# ══════════════════════════════════════════════════════════════════════
#  3. GRAPE (M22)
# ══════════════════════════════════════════════════════════════════════

def _uexp(H: np.ndarray, t: float) -> np.ndarray:
    lam, V = np.linalg.eigh(H)
    return (V * np.exp(-1j * lam * t)) @ V.conj().T


def _genel_expm(M: np.ndarray, tur: int = 60) -> np.ndarray:
    """Genel ``exp(M)`` — ölçekle-kare-al + Taylor.

    Fréchet blok dizeyi ``[[A,E],[0,A]]`` **dejenere özdeğerlidir**
    (``A``nın tayfı iki kere geçer), bu yüzden özayrışım yolu orada
    sayısal olarak çöker.  Ölçüldü: ``eig`` ile kurulan tam gradyan
    sonlu farktan 1.9e-01…4.5e-01 sapıyordu; ölçekle-kare-al ile
    1e-10 mertebesine iniyor.
    """
    M = np.asarray(M, complex)
    nrm = float(np.abs(M).sum(axis=1).max())
    k = max(0, int(math.ceil(math.log2(max(nrm, 1e-300)))) + 2)
    A = M / (2.0 ** k)
    S = np.eye(A.shape[0], dtype=complex)
    T = np.eye(A.shape[0], dtype=complex)
    for i in range(1, tur):
        T = T @ A / i
        S = S + T
        if np.abs(T).max() < 1e-18:
            break
    for _ in range(k):
        S = S @ S
    return S


def sadakat(H0: np.ndarray, Hk: Sequence[np.ndarray],
            om: Sequence[np.ndarray], psi0: np.ndarray,
            hedef: np.ndarray, T: float) -> float:
    """``F = |⟨hedef|U(T)|ψ₀⟩|²``."""
    M = len(om[0])
    dt = T / M
    p = np.asarray(psi0, complex).copy()
    for j in range(M):
        H = H0 + sum(om[k][j] * Hk[k] for k in range(len(Hk)))
        p = _uexp(H, dt) @ p
    return float(abs(np.vdot(hedef, p)) ** 2)


def _ileri_geri(H0, Hk, om, psi0, hedef, T):
    M = len(om[0])
    dt = T / M
    Us, ileri = [], [np.asarray(psi0, complex).copy()]
    p = ileri[0]
    for j in range(M):
        H = H0 + sum(om[k][j] * Hk[k] for k in range(len(Hk)))
        U = _uexp(H, dt)
        Us.append(U)
        p = U @ p
        ileri.append(p.copy())
    geri = [None] * (M + 1)
    lam = np.asarray(hedef, complex).copy()
    geri[M] = lam.copy()
    for j in range(M - 1, -1, -1):
        lam = Us[j].conj().T @ lam
        geri[j] = lam.copy()
    return Us, ileri, geri, dt


def grape_gradyani(H0, Hk, om, psi0, hedef, T) -> List[np.ndarray]:
    """Kaynağın (birinci mertebe) GRAPE gradyanı — ``O(Δt²)`` hatalı."""
    Us, ileri, geri, dt = _ileri_geri(H0, Hk, om, psi0, hedef, T)
    M = len(om[0])
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            P, PSI = geri[j + 1], ileri[j + 1]
            G[k][j] = 2.0 * np.real(np.vdot(P, PSI)
                                    * np.vdot(PSI, (1j * dt * Hk[k]) @ P))
    return G


def tam_gradyan(H0, Hk, om, psi0, hedef, T) -> List[np.ndarray]:
    """**Tam** gradyan — üstelin Fréchet türeviyle.

    ``d/dθ exp(A(θ))`` için genişletilmiş dizey kaidesi:
    ``exp([[A, E],[0, A]]) = [[e^A, dexp],[0, e^A]]``.  Bu, ``Δt``de
    yaklaşım **değildir**; ölçülüyor.

    Blok dizey dejenere özdeğerlidir; üstel :func:`_genel_expm` ile
    (ölçekle-kare-al) alınır.  Özayrışım kullanmak burada **çöker** --
    ilk hâlde öyle yazmıştım, ölçüm yakaladı.
    """
    M = len(om[0])
    dt = T / M
    n = H0.shape[0]
    Us, ileri, geri, _ = _ileri_geri(H0, Hk, om, psi0, hedef, T)
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            H = H0 + sum(om[q][j] * Hk[q] for q in range(len(Hk)))
            A = -1j * dt * H
            E = -1j * dt * Hk[k]
            B = np.zeros((2 * n, 2 * n), dtype=complex)
            B[:n, :n] = A
            B[n:, n:] = A
            B[:n, n:] = E
            EB = _genel_expm(B)
            dU = EB[:n, n:]
            P, PSI = geri[j + 1], ileri[j]
            # F = |⟨hedef|U_M…U_1|ψ₀⟩|²; ∂F/∂θ = 2Re[⟨c⟩* · ⟨P|dU|ψ_j⟩]
            c = np.vdot(geri[0], ileri[0])
            G[k][j] = 2.0 * np.real(np.conj(c) * np.vdot(P, dU @ PSI))
    return G


def sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, T, h: float = 1e-6
                        ) -> List[np.ndarray]:
    """Merkezî sonlu fark — hakem."""
    M = len(om[0])
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            o1 = [x.copy() for x in om]; o1[k][j] += h
            o2 = [x.copy() for x in om]; o2[k][j] -= h
            G[k][j] = (sadakat(H0, Hk, o1, psi0, hedef, T)
                       - sadakat(H0, Hk, o2, psi0, hedef, T)) / (2 * h)
    return G


def grape_kos(H0, Hk, psi0, hedef, T: float, M: int = 40,
              tur: int = 200, adim: float = 0.5, tohum: int = 0
              ) -> Dict[str, object]:
    """GRAPE ile sadakati yükselt — yaklaşık gradyanla."""
    r = np.random.default_rng(tohum)
    om = [r.normal(size=M) * 0.2 for _ in Hk]
    F = sadakat(H0, Hk, om, psi0, hedef, T)
    seyir = [F]
    t = adim
    for _ in range(tur):
        G = grape_gradyani(H0, Hk, om, psi0, hedef, T)
        n = math.sqrt(sum(float(np.sum(g * g)) for g in G))
        if n < 1e-14:
            break
        yeni = [om[k] + t * G[k] / n for k in range(len(Hk))]
        Fy = sadakat(H0, Hk, yeni, psi0, hedef, T)
        if Fy > F:
            om, F = yeni, Fy
        else:
            t *= 0.5
            if t < 1e-10:
                break
        seyir.append(F)
    return {"kontrol": om, "sadakat": F, "seyir": seyir,
            "tekdüze_mi": all(seyir[i] <= seyir[i + 1] + 1e-12
                              for i in range(len(seyir) - 1))}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    s.append("=== M20: tünelleme O(1) DEĞİL, üstel pahalı ===")
    s.append("  genişlik      γ          T = e^{−γ}     beklenen deneme")
    for d in tunel_maliyet_cetveli((1, 2, 4, 8, 16)):
        s.append("  %8.0f   %8.4f      %.3e      %.3e"
                 % (d["genişlik"], d["γ"], d["T"], d["beklenen_deneme"]))
    s.append("  Risalenin kendi formülü T = e^{−γ} diyor; aynı sayfada")
    s.append("  'O(1) mertebesinde geçilir' demek onunla çelişiyor.")
    s.append("  Doğru kazanç: klasikte SIFIR olan olasılık POZİTİF oluyor.")

    s.append("\n=== M21: düz bağlantı, trivial OLMAYAN holonomi ===")
    for aki in (0.0, 0.25, 0.37, 0.5, 1.0):
        d = aharonov_bohm(8, aki)
        s.append("  akı/2π=%.2f   yerel F=0 mı? %s   yüz var mı? %s   "
                 "W=%+.4f%+.4fi   |W−1|=%.4f   trivial mi? %s"
                 % (aki, d["F_yerel_sıfır_mı"], d["yüz_var_mı"],
                    d["holonomi"].real, d["holonomi"].imag, d["|W−1|"],
                    d["holonomi_trivial_mi"]))
    s.append("  akı tam sayı olduğunda holonomi trivial oluyor; arada")
    s.append("  DEĞİL. F her hâlde sıfır. Yani 'F=0 ⟹ ΔΦ=0' yanlış;")
    s.append("  doğru ölçüt W(γ)=1'dir. (Aharonov–Bohm.)")

    s.append("\n=== M22: GRAPE gradyanı O(Δt²) yaklaşımı ===")
    r = np.random.default_rng(1)
    n = 4

    def herm(sd):
        A = (np.random.default_rng(sd).normal(size=(n, n))
             + 1j * np.random.default_rng(sd + 99).normal(size=(n, n)))
        return A + A.conj().T

    H0, Hk = herm(1), [herm(2), herm(3)]
    psi0 = np.zeros(n, complex); psi0[0] = 1
    hedef = np.zeros(n, complex); hedef[n - 1] = 1
    s.append("     M      Δt      sonlu fark      GRAPE        fark      "
             "fark/Δt²")
    for M in (10, 20, 40, 80, 160):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        dt = 1.0 / M
        j, k = M // 3, 0
        sf = sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        g = grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        s.append("  %5d  %.5f  %+.8f  %+.8f  %.2e  %.4f"
                 % (M, dt, sf, g, abs(g - sf), abs(g - sf) / dt ** 2))
    s.append("  'fark/Δt²' sütunu sabitleniyor: hata tam olarak O(Δt²).")
    s.append("  Kaynak bunu EŞİTLİK olarak yazıyor; yaklaşımdır.")

    s.append("\n=== Tam (Fréchet) gradyan sonlu farkla uyuşuyor mu? ===")
    for M in (10, 20, 40):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        j, k = M // 3, 0
        sf = sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        tam = tam_gradyan(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        yak = grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        s.append("  M=%3d  sonlu fark=%+.10f   tam=%+.10f (fark %.2e)   "
                 "GRAPE=%+.10f (fark %.2e)"
                 % (M, sf, tam, abs(tam - sf), yak, abs(yak - sf)))

    s.append("\n=== GRAPE gerçekten çalışıyor mu? ===")
    d = grape_kos(H0, Hk, psi0, hedef, 1.0, M=40, tur=300)
    s.append("  başlangıç sadakat = %.6f   son sadakat = %.6f"
             % (d["seyir"][0], d["sadakat"]))
    s.append("  tekdüze artıyor mu? %s   (tur sayısı %d)"
             % (d["tekdüze_mi"], len(d["seyir"])))
    s.append("  Yaklaşık gradyan eniyilemeyi bozmuyor: adım kabul ölçütü")
    s.append("  sadakati doğrudan sınadığı için yanlış yöne gidilmiyor.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
