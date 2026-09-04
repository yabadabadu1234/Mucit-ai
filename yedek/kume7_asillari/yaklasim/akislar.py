"""
Gradyanın akış olarak okunuşu.

``x ← x − η∇f(x)`` kuralı, ``ẋ = −∇f(x)`` akışının Euler ayrıklaştırmasıdır.
Bu okuyuşun bedeli şudur: akış **tek bir noktayı** taşır, dolayısıyla
gördüğü şey yalnız yerel eğimdir. Yerel asgarîde ve eyer noktasında durur.

Daha geniş bir okuyuş, taşınanı nokta değil **ölçü** saymaktır. O zaman
akış Wasserstein uzayında bir gradyan akışıdır ve ürettiği denklem
Fokker--Planck'tır:

    ∂ρ/∂t = ∇·(ρ ∇f) + T Δρ,     durağan çözüm  ρ_∞ ∝ e^{−f/T}

Bunun serbest enerji işlevseli ``F[ρ] = ∫fρ + T∫ρ log ρ``dır ve akış
boyunca azalır. Kazanç: bir yerel çukur, ölçünün TAMAMINI tutamaz --
sıcaklık ölçüyü çukurdan sızdırır. Bedeli: yakınsama artık dağılım
mânâsındadır, tek nokta mânâsında değil, ve ``T → 0`` limitinde kazanç
kaybolur.

Üçüncü okuyuş, akışı bir YÜZEY üzerinde kurmaktır: ortalama eğrilik akışı
``∂X/∂t = −H·ν`` eğri uzunluğunun (yüzey alanının) gradyan akışıdır.
Burada ölçülen, çemberin ``r(t)² = r₀² − 2t`` kanunuyla büzülmesidir.
"""
from __future__ import annotations

from typing import Callable, Dict, Tuple

import numpy as np


# =====================================================================
#  1. Vektör akışı: tek nokta, yerel bilgi
# =====================================================================
def cift_kuyu(x: np.ndarray) -> np.ndarray:
    """``f(x) = (x²−1)² + 0.3x``: iki çukur, sağdaki daha derin değil --
    ``+0.3x`` terimi SOLDAKİNİ derinleştirir."""
    return (x * x - 1.0) ** 2 + 0.3 * x


def cift_kuyu_gradyan(x: np.ndarray) -> np.ndarray:
    return 4.0 * x * (x * x - 1.0) + 0.3


def vektor_akisi(x0: float, adim: int = 20000, eta: float = 1e-3) -> Dict[str, object]:
    """Belirlenimci gradyan inişi: başladığı çukurda kalır."""
    x = np.array([x0])
    for _ in range(adim):
        x = x - eta * cift_kuyu_gradyan(x)
    return {"x0": x0, "son_x": float(x[0]), "son_f": float(cift_kuyu(x)[0])}


def cukurlar() -> Dict[str, float]:
    """``f′(x) = 4x³ − 4x + 0.3 = 0`` köklerinden iki yerel asgarî."""
    kokler = np.sort(np.roots([4.0, 0.0, -4.0, 0.3]).real)
    sol, eyer, sag = kokler
    return {
        "sol_cukur": float(sol),
        "eyer": float(eyer),
        "sag_cukur": float(sag),
        "f_sol": float(cift_kuyu(np.array([sol]))[0]),
        "f_sag": float(cift_kuyu(np.array([sag]))[0]),
    }


def yerel_tuzak() -> Dict[str, object]:
    """Sığ çukurdan başlayan vektör akışı DERİN çukura geçemez."""
    c = cukurlar()
    sig = c["sag_cukur"] if c["f_sag"] > c["f_sol"] else c["sol_cukur"]
    derin = c["sol_cukur"] if c["f_sag"] > c["f_sol"] else c["sag_cukur"]
    a = vektor_akisi(float(sig) + 0.05)
    return {
        "sig_cukur": float(sig),
        "derin_cukur": float(derin),
        "vardigi": a["son_x"],
        "sig_cukurda_kaldi": bool(abs(a["son_x"] - sig) < 1e-3),
    }


# =====================================================================
#  2. Topluluk akışı: Langevin / Fokker--Planck
# =====================================================================
def langevin(
    n: int = 8000,
    adim: int = 60000,
    eta: float = 1e-3,
    T: float = 0.3,
    x0: float | None = None,
    tohum: int = 0,
) -> np.ndarray:
    """``dx = −∇f dt + √(2T) dW``. Bütün topluluk aynı noktadan başlar."""
    rng = np.random.default_rng(tohum)
    if x0 is None:
        x0 = float(cukurlar()["sag_cukur"])
    x = np.full(n, x0)
    sigma = np.sqrt(2.0 * T * eta)
    for _ in range(adim):
        x = x - eta * cift_kuyu_gradyan(x) + sigma * rng.normal(size=n)
    return x


def gibbs_ile_kiyas(T: float = 0.3, **kw) -> Dict[str, object]:
    """Langevin'in durağan dağılımı ``e^{−f/T}`` ile uyuşuyor mu?

    Bu, akışın 'işe yaradığı' iddiasının SINANABİLİR hâlidir: histogram
    ile analitik Gibbs yoğunluğu arasındaki toplam değişim uzaklığına
    bakılır.
    """
    ornek = langevin(T=T, **kw)
    kenar = np.linspace(-2.0, 2.0, 81)
    orta = 0.5 * (kenar[:-1] + kenar[1:])
    genislik = kenar[1] - kenar[0]

    say, _ = np.histogram(ornek, bins=kenar)
    p_amp = say / max(say.sum(), 1)

    yog = np.exp(-cift_kuyu(orta) / T)
    p_gibbs = yog / yog.sum()

    tv = 0.5 * float(np.sum(np.abs(p_amp - p_gibbs)))

    c = cukurlar()
    sinir = c["eyer"]
    sol_kutle = float(np.mean(ornek < sinir))
    gibbs_sol = float(p_gibbs[orta < sinir].sum())
    return {
        "T": T,
        "toplam_degisim_uzakligi": tv,
        "gibbs_ile_uyusuyor": bool(tv < 0.08),
        "sol_cukur_kutlesi": sol_kutle,
        "gibbs_sol_kutlesi": gibbs_sol,
        "kutle_uyusuyor": bool(abs(sol_kutle - gibbs_sol) < 0.08),
        "sinir": float(sinir),
    }


def tuzaktan_kacis(T: float = 0.3) -> Dict[str, object]:
    """Aynı başlangıç noktasından: vektör akışı sığda kalır, topluluk geçer."""
    t = yerel_tuzak()
    ornek = langevin(T=T, x0=t["sig_cukur"] + 0.05)
    sinir = cukurlar()["eyer"]
    derin_solda = t["derin_cukur"] < sinir
    kacan = float(np.mean(ornek < sinir) if derin_solda else np.mean(ornek > sinir))
    return {
        "vektor_akisi_kacti": not t["sig_cukurda_kaldi"],
        "toplulugun_kacan_kesri": kacan,
        "topluluk_kacti": bool(kacan > 0.5),
    }


def serbest_enerji_azaliyor_mu(
    T: float = 0.3, kayit_araligi: int = 5000, adim: int = 60000
) -> Dict[str, object]:
    """``F[ρ] = E_ρ[f] + T·∫ρ log ρ`` akış boyunca azalmalı.

    Wasserstein gradyan akışı iddiasının sayısal karşılığı budur.
    Entropi terimi histogramdan (kesikli tahmin) hesaplanır; kesiklilik
    sebebiyle küçük dalgalanma olur, o yüzden 'monotonluk' değil
    'kayda değer artış yok' sınanır.
    """
    rng = np.random.default_rng(1)
    n = 8000
    eta = 1e-3
    x = np.full(n, float(cukurlar()["sag_cukur"]) + 0.05)
    sigma = np.sqrt(2.0 * T * eta)
    kenar = np.linspace(-2.5, 2.5, 101)
    genislik = kenar[1] - kenar[0]

    def F(v: np.ndarray) -> float:
        say, _ = np.histogram(v, bins=kenar)
        p = say / say.sum()
        yog = p / genislik
        nz = p > 0
        entropi = float(np.sum(p[nz] * np.log(yog[nz])))
        return float(np.mean(cift_kuyu(v))) + T * entropi

    izler = [F(x)]
    for t in range(1, adim + 1):
        x = x - eta * cift_kuyu_gradyan(x) + sigma * rng.normal(size=n)
        if t % kayit_araligi == 0:
            izler.append(F(x))
    artis = max((izler[i + 1] - izler[i]) for i in range(len(izler) - 1))
    return {
        "F_izi": [round(v, 4) for v in izler],
        "toplam_dusus": izler[0] - izler[-1],
        "azaldi": bool(izler[-1] < izler[0]),
        "azami_ara_artis": float(artis),
        "kayda_deger_artis_yok": bool(artis < 0.02),
    }


# =====================================================================
#  3. Ortalama eğrilik akışı (eğri kısaltma)
# =====================================================================
def egri_kisaltma(
    n: int = 400, r0: float = 1.0, dt: float = 1e-5, adim: int = 20000
) -> Dict[str, object]:
    """Kapalı düzlem eğrisi için ``∂X/∂t = κ·ν``; çember için ``r² = r₀² − 2t``.

    Bu, alanın (burada uzunluğun) gradyan akışıdır. Ölçülen: sayısal
    yarıçapın analitik kanunla uyuşması.
    """
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    X = np.stack([r0 * np.cos(th), r0 * np.sin(th)], axis=1)
    for _ in range(adim):
        ileri = np.roll(X, -1, axis=0)
        geri = np.roll(X, 1, axis=0)
        h = np.linalg.norm(ileri - X, axis=1)[:, None]
        # ayrık Laplace-Beltrami ≈ κν
        lap = (ileri - 2 * X + geri) / (h * h)
        X = X + dt * lap
    t_son = dt * adim
    r_sayisal = float(np.mean(np.linalg.norm(X, axis=1)))
    r_kuram = float(np.sqrt(max(r0 * r0 - 2.0 * t_son, 0.0)))
    return {
        "t": t_son,
        "r_sayisal": r_sayisal,
        "r_kuram": r_kuram,
        "bagil_hata": abs(r_sayisal - r_kuram) / r_kuram,
        "kanunla_uyusuyor": bool(abs(r_sayisal - r_kuram) / r_kuram < 5e-3),
        "buzuldu": bool(r_sayisal < r0),
    }


def rapor() -> str:
    s = ["=== akislar ==="]
    c = cukurlar()
    s.append("çift kuyu   sol=%.4f (f=%.4f)  eyer=%.4f  sağ=%.4f (f=%.4f)"
             % (c["sol_cukur"], c["f_sol"], c["eyer"], c["sag_cukur"], c["f_sag"]))
    t = yerel_tuzak()
    s.append("vektör akışı  sığ=%.4f → vardığı=%.4f  sığda kaldı=%s"
             % (t["sig_cukur"], t["vardigi"], t["sig_cukurda_kaldi"]))
    k = tuzaktan_kacis()
    s.append("topluluk akışı  kaçan kesir=%.3f  kaçtı=%s"
             % (k["toplulugun_kacan_kesri"], k["topluluk_kacti"]))
    g = gibbs_ile_kiyas()
    s.append("Gibbs kıyası  TV=%.4f uyuşuyor=%s   sol kütle: ampirik=%.3f gibbs=%.3f"
             % (g["toplam_degisim_uzakligi"], g["gibbs_ile_uyusuyor"],
                g["sol_cukur_kutlesi"], g["gibbs_sol_kutlesi"]))
    f = serbest_enerji_azaliyor_mu()
    s.append("serbest enerji  düşüş=%.4f azaldı=%s  azamî ara artış=%.4f"
             % (f["toplam_dusus"], f["azaldi"], f["azami_ara_artis"]))
    e = egri_kisaltma()
    s.append("eğri kısaltma  r_sayısal=%.6f  r_kuram=%.6f  bağıl hata=%.2e  uyuşuyor=%s"
             % (e["r_sayisal"], e["r_kuram"], e["bagil_hata"], e["kanunla_uyusuyor"]))
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
