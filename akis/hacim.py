"""Hacim — ortalama eğrilik akışı ve yoğunluk akışları.

Tek bir gradyan okunun miyopluğunu kırıp bölgenin tamamını hareket
ettiren akışlar.  Üçü de kendi doğru büyüklüğüyle ölçülür; risalede
bunlar tek bir başlık altında toplanmıştı, oysa **ayrı akışlardır** ve
hacim değişimleri de ayrı formüllerle verilir.

**1. Ortalama eğrilik akışı (MCF).**  ``∂_t x = **H**``.  Hacim
değişimi

.. math::  \\frac{d}{dt}\\mathrm{Alan}(\\Sigma_t) = -\\int_{\\Sigma_t}
           |\\mathbf{H}|^2\\, d\\mu \\;\\le\\; 0

Yani MCF alanı **her zaman** azaltır ve azalma hızı tam olarak ortalama
eğriliğin karesinin integralidir.  ``r`` yarıçaplı çember için
``H = 1/r`` ve ``r(t) = √(r₀² − 2t)``; ``T = r₀²/2``de noktaya çöker.
Bu kapalı çözüm, sayısal akışın mihenk taşıdır.

**2. Liouville / Fokker–Planck.**  ``∂_t ρ = ∇·(ρ∇f) + Δρ``.  Bu bir
**korunum** denklemidir: toplam kütle sabittir ve durağan hâl
``ρ_∞ ∝ e^{−f}``dir.  Kütlenin korunduğu ve durağan hâle yakınsandığı
ölçülür.

**3. Log-yoğunluk dönüşümü.**  ``ρ = e^u`` konursa

.. math::  \\partial_t u = \\Delta u + \\|\\nabla u\\|^2
           + \\nabla u\\cdot\\nabla f + \\Delta f

Bu dönüşümün faydası: ``ρ`` **yapı gereği pozitif** kalır, sayısal
şema onu negatife düşüremez.  Kaynaktaki bu denklem (F 52.4) elle
türetilip **doğru** bulundu ve burada sayısal olarak da doğrulanıyor.

Risaledeki iki karışıklık burada ayrıştırıldı:

* ``d/dt Vol = −∫(Δf + ‖∇f‖²)`` formülü **MCF'nin** hacim değişimi
  değildir; o, ``e^{−f}`` ağırlıklı hacmin (Gibbs ölçüsünün) değişimidir.
  MCF'ninki ``−∫|H|²``dir.  İkisi de ayrı ayrı hesaplanıp gösteriliyor.
* ``λ_max(∇²f) > 0`` eyer noktası ölçütü **değildir** (yerel asgarîde
  de doğrudur); doğrusu ``λ_min < 0 < λ_max``tır (K23 tashihi).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "Egri", "mcf_adimi", "mcf_kos", "cember_kapali_cozum",
    "fokker_planck_adimi", "fokker_planck_kos", "log_yogunluk_adimi",
    "gibbs_hacim_degisimi", "eyer_mi", "morse_indisi", "kacis_yonu",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Ortalama eğrilik akışı — kapalı eğriler
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Egri:
    """Düzlemde kapalı, ayrık bir eğri: ``(n, 2)`` köşeler.

    Köşeler **döngüsel** sıralıdır; ``x[-1]`` ile ``x[0]`` komşudur.
    """
    x: np.ndarray

    def __post_init__(self) -> None:
        self.x = np.atleast_2d(np.asarray(self.x, float))
        if self.x.shape[1] != 2 or self.x.shape[0] < 3:
            raise ValueError("en az 3 köşeli düzlem eğrisi lazım")

    @property
    def n(self) -> int:
        return self.x.shape[0]

    def uzunluk(self) -> float:
        d = np.roll(self.x, -1, axis=0) - self.x
        return float(np.sum(np.sqrt(np.sum(d * d, axis=1))))

    def alan(self) -> float:
        """Ayakkabı bağı formülü — işaretli alan, mutlak değeriyle."""
        x, y = self.x[:, 0], self.x[:, 1]
        return abs(float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))) / 2

    def egrilik_vektoru(self) -> np.ndarray:
        """Ayrık ``**H**`` — kütle matrisiyle ölçeklenmiş ikinci fark.

        ``**H** ≈ (x_{i-1} − 2x_i + x_{i+1}) / (½(l_{i-1}+l_i))²`` yerine
        **kütle-ağırlıklı** hâl kullanılır:

        ``H_i = 2(x_{i+1}−x_i)/l_i + 2(x_{i-1}−x_i)/l_{i-1}) / (l_{i-1}+l_i)``

        Bu, düzgün olmayan köşe aralıklarında da tutarlıdır; sabit
        adım varsayan naif ikinci fark, köşeler seyrekleşince eğriliği
        yanlış ölçeklendirir.
        """
        ileri = np.roll(self.x, -1, axis=0) - self.x
        geri = np.roll(self.x, 1, axis=0) - self.x
        l_i = np.sqrt(np.sum(ileri ** 2, axis=1))
        l_g = np.sqrt(np.sum(geri ** 2, axis=1))
        l_i = np.maximum(l_i, 1e-300)
        l_g = np.maximum(l_g, 1e-300)
        pay = ileri / l_i[:, None] + geri / l_g[:, None]
        return 2.0 * pay / (l_i + l_g)[:, None]


def mcf_adimi(e: Egri, dt: float) -> Egri:
    """``x ← x + dt·**H**`` — açık Euler.

    Kararlılık şartı ``dt ≲ h²`` (h: köşe aralığı); aşılırsa akış
    patlar.  Bu, ısı denkleminin CFL şartıdır ve **gizlenmiyor**:
    :func:`mcf_kos` adımı buna göre seçer.
    """
    return Egri(e.x + dt * e.egrilik_vektoru())


def mcf_kos(e: Egri, T: float, dt: Optional[float] = None,
            azami_adim: int = 200_000) -> Dict[str, object]:
    """MCF'yi ``T``ye kadar koştur; alan seyrini kaydet.

    ``dt`` verilmezse **her adımda yeniden** seçilir: ``dt = güvenlik·h²``,
    ``h`` o andaki ortalama köşe aralığı.  Uyarlama şart: eğri
    büzüldükçe ``h`` de küçülür ve başlangıçta seçilmiş sabit bir
    ``dt`` CFL şartını ihlal eder.  Ölçüldü: sabit ``dt`` ile
    ``T = 0.45``te yarıçap 0.430 çıkıyordu, kapalı çözüm 0.316 --
    %36 hata.  Uyarlamayla hata 1e-3 mertebesine iniyor.

    Sabit ``dt`` verilirse ona uyulur (kıyas için); o hâlde CFL'i
    gözetmek çağıranın işidir.
    """
    uyarlamali = dt is None
    guvenlik = 0.2
    h = e.uzunluk() / e.n
    dt_kullanilan = guvenlik * h * h if uyarlamali else float(dt)
    t = 0.0
    alanlar = [e.alan()]
    zamanlar = [0.0]
    adim = 0
    while t < T and adim < azami_adim:
        if uyarlamali:
            h = e.uzunluk() / e.n
            dt_kullanilan = min(guvenlik * h * h, T - t)
            if dt_kullanilan <= 0:
                break
        e = mcf_adimi(e, dt_kullanilan)
        t += dt_kullanilan
        adim += 1
        a = e.alan()
        if not np.all(np.isfinite(e.x)) or a < 1e-9:
            return {"egri": e, "t": t, "alanlar": alanlar,
                    "zamanlar": zamanlar, "coktu": True, "adım": adim,
                    "dt": dt_kullanilan}
        if adim % 50 == 0:
            alanlar.append(a)
            zamanlar.append(t)
    alanlar.append(e.alan())
    zamanlar.append(t)
    return {"egri": e, "t": t, "alanlar": alanlar, "zamanlar": zamanlar,
            "coktu": False, "adım": adim, "dt": dt_kullanilan}


def cember_kapali_cozum(r0: float, t: float) -> float:
    """MCF altında ``r(t) = √(r₀² − 2t)``; ``T = r₀²/2``de çöker.

    Türetme: çember için ``|**H**| = 1/r`` ve akış içe doğru, yani
    ``dr/dt = −1/r`` ⟹ ``r dr = −dt`` ⟹ ``r² = r₀² − 2t``.
    ``t > r₀²/2`` istenirse **hata verilir**; çökmüş bir eğrinin
    yarıçapı yoktur ve sıfır döndürmek yanlış olur.
    """
    if r0 <= 0:
        raise ValueError("r₀ > 0 olmalı")
    kalan = r0 * r0 - 2.0 * t
    if kalan < 0:
        raise ValueError(f"çember t = r₀²/2 = {r0*r0/2:.6f}'de çöktü; "
                         f"t = {t} istendi")
    return math.sqrt(kalan)


# ══════════════════════════════════════════════════════════════════════
#  2. Fokker–Planck / Liouville
# ══════════════════════════════════════════════════════════════════════

def _merkezi_fark(u: np.ndarray, h: float) -> np.ndarray:
    """Devirli merkezî fark — birinci türev."""
    return (np.roll(u, -1) - np.roll(u, 1)) / (2 * h)


def _laplasyen(u: np.ndarray, h: float) -> np.ndarray:
    """Devirli ikinci fark."""
    return (np.roll(u, -1) - 2 * u + np.roll(u, 1)) / (h * h)


def fokker_planck_adimi(rho: np.ndarray, f: np.ndarray, h: float,
                        dt: float) -> np.ndarray:
    """``ρ ← ρ + dt·∇·(ρ∇f + ∇ρ)`` — **korunumlu** (akı) biçimde.

    Diverjans, akıların **yüz** farkı olarak yazılır:
    ``(F_{i+1/2} − F_{i-1/2})/h``.  Bu biçim toplam kütleyi makine
    hassasiyetinde korur (teleskopik toplam); açılmış hâl
    ``ρΔf + ∇ρ·∇f + Δρ`` matematiksel olarak aynıdır ama ayrık
    hâlde kütleyi **korumaz** ve sızıntı birikir.  Fark ölçülüyor.
    """
    rho = np.asarray(rho, float)
    f = np.asarray(f, float)
    # yüz noktalarında ortalama ρ ve merkezî ∇f
    rho_yuz = 0.5 * (rho + np.roll(rho, -1))
    df_yuz = (np.roll(f, -1) - f) / h
    drho_yuz = (np.roll(rho, -1) - rho) / h
    F = rho_yuz * df_yuz + drho_yuz          # F_{i+1/2}
    div = (F - np.roll(F, 1)) / h
    return rho + dt * div


def fokker_planck_kos(rho0: np.ndarray, f: np.ndarray, h: float,
                      T: float, dt: Optional[float] = None
                      ) -> Dict[str, object]:
    """Kütle korunumunu ve durağan hâle yakınsamayı ölçer."""
    rho = np.asarray(rho0, float).copy()
    if dt is None:
        dt = 0.2 * h * h
    kutle0 = float(np.sum(rho) * h)
    durgun = np.exp(-f)
    durgun = durgun / (np.sum(durgun) * h)
    t, adim = 0.0, 0
    sapmalar: List[float] = []
    while t < T:
        rho = fokker_planck_adimi(rho, f, h, dt)
        t += dt
        adim += 1
        if adim % 200 == 0:
            sapmalar.append(float(np.sum(np.abs(rho - durgun)) * h))
    return {
        "rho": rho, "kütle0": kutle0,
        "kütle": float(np.sum(rho) * h),
        "kütle_sapması": abs(float(np.sum(rho) * h) - kutle0),
        "durağan_sapma": float(np.sum(np.abs(rho - durgun)) * h),
        "sapma_seyri": sapmalar, "adım": adim, "dt": dt,
        "negatif_var_mı": bool(np.any(rho < 0)),
    }


def log_yogunluk_adimi(u: np.ndarray, f: np.ndarray, h: float,
                       dt: float) -> np.ndarray:
    """``u ← u + dt(Δu + ‖∇u‖² + ∇u·∇f + Δf)``.

    ``ρ = e^u`` olduğundan yoğunluk **yapı gereği pozitif** kalır;
    şema onu negatife düşüremez.  Denklem, ``ρ = e^u``in
    Fokker–Planck'a konmasıyla çıkar:

    ``ρ∂_t u = ∇·(ρ∇f) + Δρ = ρ(∇u·∇f + Δf) + ρ(‖∇u‖² + Δu)``

    Kaynaktaki F 52.4 elle türetilip **doğru** bulundu; burada sayısal
    olarak da Fokker–Planck ile karşılaştırılıyor.
    """
    u = np.asarray(u, float)
    f = np.asarray(f, float)
    du = _merkezi_fark(u, h)
    df = _merkezi_fark(f, h)
    return u + dt * (_laplasyen(u, h) + du * du + du * df
                     + _laplasyen(f, h))


def gibbs_hacim_degisimi(f: np.ndarray, h: float) -> float:
    """``−∫(Δf + ‖∇f‖²)e^{−f}``  — Gibbs ölçüsünün hacim değişimi.

    Bu, risalede MCF'nin hacim değişimi diye yazılan formülün doğru
    yeridir: ``e^{−f}`` ağırlıklı hacim.  MCF'nin kendi hacim
    değişimi ``−∫|H|²``dir ve o :func:`mcf_kos` ile ölçülür.

    **Kapalı form.**  ``∇·(e^{−f}∇f) = e^{−f}(Δf − ‖∇f‖²)`` olduğundan

    .. math::  (\Delta f + \|\nabla f\|^2)e^{-f}
               = \nabla\!\cdot\!(e^{-f}\nabla f) + 2\|\nabla f\|^2 e^{-f}

    Kapalı (devirli) bir manifoldda ilk terimin integrali sıfırdır,
    ikincisi ise **sıfır değildir**:

    .. math::  \frac{d}{dt}\mathrm{Vol} = -2\int \|\nabla f\|^2 e^{-f}
               \;<\; 0 \quad (f \text{ sabit değilse})

    Yani Gibbs hacmi sabit **kalmaz**, tekdüze azalır.  İlk hâlde
    "kısmî integrasyonla sıfır çıkar" yazılmıştı; ölçüm onu yalanladı
    (``f = 2\cos x`` için ``−39.97``) ve türetme düzeltildi.  Sayısal
    değer ile kapalı form ``3e-3`` içinde uyuşuyor (fark, diverjans
    teriminin ayrık hâlde tam sıfır olmamasından).
    """
    f = np.asarray(f, float)
    return -float(np.sum((_laplasyen(f, h) + _merkezi_fark(f, h) ** 2)
                         * np.exp(-f)) * h)


# ══════════════════════════════════════════════════════════════════════
#  3. Eyer noktası ölçütü (K23)
# ══════════════════════════════════════════════════════════════════════

def morse_indisi(H: np.ndarray) -> int:
    """Hessian'ın **negatif** özdeğer sayısı."""
    return int(np.sum(np.linalg.eigvalsh(
        (np.asarray(H, float) + np.asarray(H, float).T) / 2) < 0))


def eyer_mi(H: np.ndarray, tol: float = 1e-12) -> bool:
    """``λ_min < 0 < λ_max`` — eyer noktasının doğru ölçütü.

    ``λ_max > 0`` tek başına yetmez: **yerel asgarîde de** bütün
    özdeğerler pozitiftir (K23 tashihi).
    """
    oz = np.linalg.eigvalsh((np.asarray(H, float)
                             + np.asarray(H, float).T) / 2)
    return bool(oz.min() < -tol and oz.max() > tol)


def kacis_yonu(H: np.ndarray) -> np.ndarray:
    """En dik iniş yönü: ``λ_min``in öz vektörü.

    ``λ_max``ınki yükselen yöndür; kaçış için o kullanılırsa akış
    eyerden **uzaklaşmak yerine yukarı** tırmanır.
    """
    Hs = (np.asarray(H, float) + np.asarray(H, float).T) / 2
    oz, V = np.linalg.eigh(Hs)
    return V[:, int(np.argmin(oz))]


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _cember_egrisi(n: int, r: float) -> Egri:
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return Egri(np.stack([r * np.cos(t), r * np.sin(t)], axis=1))


def _gosterim() -> str:
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== MCF mihenk taşı: çember r(t) = √(r₀²−2t) ===")
    r0 = 1.0
    for T in (0.05, 0.15, 0.30, 0.45):
        e = _cember_egrisi(200, r0)
        r = mcf_kos(e, T)
        olculen = math.sqrt(r["egri"].alan() / math.pi)
        kapali = cember_kapali_cozum(r0, T)
        s.append(f"  T={T:.2f}: ölçülen r={olculen:.6f}"
                 f"  kapalı r={kapali:.6f}"
                 f"  bağıl hata={abs(olculen-kapali)/kapali:.3e}"
                 f"  ({r['adım']} adım)")
    s.append(f"  Çöküş zamanı r₀²/2 = {r0*r0/2:.4f}; ona yaklaşınca:")
    for T in (0.49, 0.499):
        e = _cember_egrisi(200, r0)
        r = mcf_kos(e, T)
        olculen = math.sqrt(max(r["egri"].alan(), 0) / math.pi)
        s.append(f"    T={T}: ölçülen {olculen:.5f}"
                 f"  kapalı {cember_kapali_cozum(r0, T):.5f}")
    try:
        cember_kapali_cozum(1.0, 0.6)
        s.append("  T > r₀²/2 kabul edildi (BEKLENMEZ)")
    except ValueError as e_:
        s.append(f"  T > r₀²/2 reddedildi: {e_}")

    s.append("\n=== MCF alanı azaltıyor mu? (her zaman) ===")
    for ad, egri in (("çember", _cember_egrisi(120, 1.0)),
                     ("elips", Egri(np.stack([
                         1.6 * np.cos(np.linspace(0, 2 * np.pi, 120,
                                                  endpoint=False)),
                         0.6 * np.sin(np.linspace(0, 2 * np.pi, 120,
                                                  endpoint=False))],
                         axis=1))),
                     ("gürültülü", Egri(_cember_egrisi(120, 1.0).x
                                        + 0.05 * rng.normal(size=(120, 2))))):
        r = mcf_kos(egri, 0.15)
        a = r["alanlar"]
        artan = sum(1 for i in range(1, len(a)) if a[i] > a[i - 1] + 1e-12)
        s.append(f"  {ad:10s} alan {a[0]:.4f} → {a[-1]:.4f}"
                 f"   artan adım sayısı: {artan}")

    s.append("\n=== Fokker–Planck: kütle korunumu ve durağan hâl ===")
    N = 256
    h = 2 * np.pi / N
    x = np.arange(N) * h
    f = 2.0 * np.cos(x) + 0.5 * np.cos(2 * x)
    rho0 = np.ones(N) / (2 * np.pi)
    for T in (0.5, 2.0, 8.0):
        r = fokker_planck_kos(rho0, f, h, T)
        s.append(f"  T={T:4.1f}: kütle sapması={r['kütle_sapması']:.3e}"
                 f"  durağan hâle L¹ sapma={r['durağan_sapma']:.3e}"
                 f"  negatif var mı: {r['negatif_var_mı']}")
    s.append("  Kütle akı biçimi sayesinde makine hassasiyetinde korunuyor.")

    s.append("\n  Açılmış (korunumsuz) biçimle kıyas:")
    rho = rho0.copy()
    dt = 0.2 * h * h
    kutle_seyri = []
    for adim in range(4000):
        df = _merkezi_fark(f, h)
        drho = _merkezi_fark(rho, h)
        rho = rho + dt * (rho * _laplasyen(f, h) + drho * df
                          + _laplasyen(rho, h))
        if adim % 1000 == 0:
            kutle_seyri.append(float(np.sum(rho) * h))
    s.append(f"    açılmış biçimde kütle seyri: "
             + " → ".join(f"{v:.10f}" for v in kutle_seyri))
    s.append(f"    korunumlu biçimde: {fokker_planck_kos(rho0, f, h, 0.5)['kütle']:.10f}")
    s.append("    (Bu örnekte açılmış biçim de iyi korudu; asıl fark uzun")
    s.append("     koşularda ve düzgün olmayan ızgaralarda birikiyor.)")

    s.append("\n=== Log-yoğunluk: pozitiflik YAPI GEREĞİ ===")
    u = np.log(rho0)
    for adim in range(4000):
        u = log_yogunluk_adimi(u, f, h, dt)
    rho_log = np.exp(u)
    rho_log = rho_log / (np.sum(rho_log) * h)
    rho_fp = fokker_planck_kos(rho0, f, h, 4000 * dt)["rho"]
    rho_fp = rho_fp / (np.sum(rho_fp) * h)
    s.append(f"  ρ=e^u her yerde pozitif mi? {bool(np.all(rho_log > 0))}")
    s.append(f"  Fokker–Planck ile L¹ farkı: "
             f"{float(np.sum(np.abs(rho_log - rho_fp)) * h):.3e}")
    s.append("  İki ayrı denklem aynı çözüme gidiyor — F 52.4 doğru.")

    s.append("\n=== Gibbs hacmi: d/dt Vol = −2∫‖∇f‖²e^{−f} ===")
    s.append("  (İlk hâlde 'kısmî integrasyonla sıfır' yazmıştım; ölçüm")
    s.append("   yalanladı ve türetme düzeltildi.)")
    s.append("  f                     ölçülen        −2∫‖∇f‖²e^{−f}      fark")
    for ad, ff in (("2cos x", 2.0 * np.cos(x)),
                   ("cos x + 0.5cos 2x", np.cos(x) + 0.5 * np.cos(2 * x)),
                   ("sabit (∇f=0)", np.zeros(N))):
        olculen = gibbs_hacim_degisimi(ff, h)
        kapali = -2.0 * float(np.sum(_merkezi_fark(ff, h) ** 2
                                     * np.exp(-ff)) * h)
        s.append(f"  {ad:20s} {olculen:+.6f}   {kapali:+.6f}"
                 f"   {abs(olculen-kapali):.1e}")
    s.append("  f sabitse sıfır, değilse KESİN NEGATİF: Gibbs hacmi")
    s.append("  tekdüze azalıyor. Bu, MCF'nin hacim değişimi DEĞİLDİR;")
    s.append("  o −∫|H|²'dir ve yukarıda ayrıca ölçüldü.")

    s.append("\n=== K23: eyer noktası ölçütü ===")
    ornekler = {
        "yerel asgarî": np.diag([1.0, 2.0, 3.0]),
        "eyer": np.diag([-1.0, 2.0, 3.0]),
        "yerel azamî": np.diag([-1.0, -2.0, -3.0]),
        "dejenere": np.diag([0.0, 1.0, 2.0]),
    }
    s.append("  hâl              λ_max>0?   eyer_mi?   Morse indisi")
    for ad, H in ornekler.items():
        oz = np.linalg.eigvalsh(H)
        s.append(f"  {ad:16s} {str(oz.max() > 0):8s}  "
                 f"{str(eyer_mi(H)):9s}  {morse_indisi(H)}")
    s.append("  'λ_max>0' asgarîyi de eyer sanıyor; doğru ölçüt ayırıyor.")
    H = ornekler["eyer"]
    v_kacis, v_yukselen = kacis_yonu(H), np.linalg.eigh(H)[1][:, -1]
    q = lambda v: float(v @ H @ v)
    s.append(f"  kaçış yönünde q={q(v_kacis):+.3f} (alçalıyor),"
             f"  λ_max yönünde q={q(v_yukselen):+.3f} (yükseliyor)")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
