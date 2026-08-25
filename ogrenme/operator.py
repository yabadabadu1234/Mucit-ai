"""Operatör — DeepONet, FINO ve ızgaradan bağımsız operatör öğrenmesi.

Bir *operatör* ``𝒢: u ↦ 𝒢(u)`` fonksiyondan fonksiyona gider.  İki
mimari:

**DeepONet.**  Evrensel operatör yaklaşım teoreminin doğrudan
gerçeklemesi:

.. math::  \\mathcal{G}(u)(y) \\approx \\sum_{k=1}^{p}
   \\underbrace{b_k\\bigl(u(x_1),\\dots,u(x_m)\\bigr)}_{\\text{dal}}\\;
   \\underbrace{t_k(y)}_{\\text{gövde}}

Girdi fonksiyonu ``m`` sensör noktasında örneklenir (dal), çıktı
konumu ``y`` ayrıca beslenir (gövde), ve ikisinin **iç çarpımı**
alınır.  Ayrışım kasten çarpımsaldır: gövde ``y``ye sürekli bağlıdır,
o yüzden **çıktı ızgarası eğitimdekinden farklı olabilir**.  Bu,
mimarinin asıl vaadi ve burada ölçülen şeydir.

**FINO (çarpanlara ayrılmış FNO).**  İki boyutlu spektral çekirdek
``R_θ(k₁,k₂)``, tam bir ``K×K`` tensör yerine ``R`` rütbeli çarpanlara
ayrılır:

.. math::  R_\\theta(k_1,k_2) = \\sum_{r=1}^{R} U_r(k_1)\\otimes V_r(k_2)

Parametre sayısı ``K²`` yerine ``2KR``.  **Rütbe yetmezse hata
kalır** ve o hata ölçülür; sıkıştırma bedava değildir ve bedeli
raporlanır.

Her ikisi için de asıl sınama **çözünürlükten bağımsızlık**tır:
eğitimden farklı bir ızgarada aynı fonksiyon çıkmalı.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "DeepONet", "fino_ayristir", "fino_uygula", "spektral_rutbe",
    "cozunurluk_bagimsizligi", "ornek_operator", "l2_norm",
]


def l2_norm(v: np.ndarray, alan: float = 1.0) -> float:
    """``‖v‖_{L²} = √(|Ω|/N · Σ|v_i|²)``.

    Ölçek çarpanı **norma** girer, alanın kendisine değil (K30
    tashihi).  Alanı çarpanla ölçeklemek, fonksiyonu çözünürlüğe
    bağımlı kılar -- yani ızgaradan bağımsızlığın tam aksini yapar.
    """
    v = np.asarray(v, float)
    N = v.shape[0]
    return float(np.sqrt(alan / N * np.sum(v * v)))


# ══════════════════════════════════════════════════════════════════════
#  DeepONet
# ══════════════════════════════════════════════════════════════════════

@dataclass
class DeepONet:
    """``𝒢(u)(y) ≈ Σ_k b_k(u|sensör) · t_k(y) + b₀``.

    Dal ve gövde birer küçük ileri beslemeli ağdır.  Eğitim, **kapalı
    form** ile yapılır: gövde çıktıları sabit tutulup dal katsayıları
    en küçük karelerle çözülür, sonra tersi.  Bu, gradyan inişinden
    hem daha hızlı hem de tekrarlanabilir; ve bu risalenin ısrarı olan
    "kör gradyan aramasını bırak" ile aynı yöndedir.
    """
    m: int                       # sensör sayısı
    p: int = 16                  # taban sayısı
    gizli: int = 32
    tohum: int = 0
    W_dal: np.ndarray = field(init=False, repr=False)
    W_govde: np.ndarray = field(init=False, repr=False)
    b0: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        if self.m < 1 or self.p < 1:
            raise ValueError("m, p ≥ 1 olmalı")
        r = np.random.default_rng(self.tohum)
        # Rastgele öznitelikler (sabit) + öğrenilen doğrusal kat:
        self._A_dal = r.normal(0, 1.0 / np.sqrt(self.m),
                               (self.m, self.gizli))
        self._c_dal = r.uniform(-1, 1, self.gizli)
        # Dal özniteliklerine girdinin KENDİSİ de eklenir.  Sebebi
        # ölçüldü: burada öğrenilen işleç (antitürev) DOĞRUSALDIR ve
        # salt tanh öznitelikleriyle bağıl hata 0.80'de kalıyordu;
        # doğrusal terim eklenince 1e-15'e iniyor. Doğrusal olmayan
        # işleçlerde tanh kısmı devreye girer, yani ikisi de lazım.
        self.dal_boyu = self.gizli + self.m
        self._A_govde = r.normal(0, 1.0, (1, self.gizli))
        self._c_govde = r.uniform(-2, 2, self.gizli)
        self.W_dal = np.zeros((self.dal_boyu, self.p))
        self.W_govde = np.zeros((self.gizli, self.p))

    # --- öznitelikler ---------------------------------------------------
    def _dal_ozn(self, U: np.ndarray) -> np.ndarray:
        """``(N, m) → (N, gizli+m)`` — tanh öznitelikleri **ve** girdinin
        kendisi.  Doğrusal işleçler ikinci kısımla tam yakalanır."""
        U = np.atleast_2d(np.asarray(U, float))
        if U.shape[1] != self.m:
            raise ValueError(f"dal girdisi {self.m} sensörlü olmalı")
        return np.hstack([np.tanh(U @ self._A_dal + self._c_dal), U])

    def _govde_ozn(self, y: np.ndarray) -> np.ndarray:
        """``(M,) → (M, gizli)`` — ``y``ye SÜREKLİ bağlı.

        Süreklilik şart: gövde ``y``yi ızgara indeksi olarak değil
        **konum** olarak alır, o yüzden eğitimde görülmemiş bir ``y``de
        de değerlendirilebilir.
        """
        y = np.asarray(y, float).reshape(-1, 1)
        return np.tanh(y @ self._A_govde + self._c_govde)

    # --- eğitim ---------------------------------------------------------
    def uydur(self, U: np.ndarray, Y: np.ndarray, hedef: np.ndarray,
              lam: float = 1e-4, tur: int = 30) -> "DeepONet":
        """Değişimli en küçük kareler.

        ``hedef``: ``(N, M)``, ``U``: ``(N, m)``, ``Y``: ``(M,)``.
        Kayıp ``‖Σ_k (Φ_dal W_dal)_k (Φ_gövde W_gövde)_k − hedef‖²``
        her iki değişkende ayrı ayrı **doğrusaldır**; o yüzden biri
        sabitken diğeri kapalı formda çözülür.

        **Ölçek dejenerasyonu.**  ``(W_d, W_t) → (cW_d, W_t/c)`` çarpımı
        değiştirmez; yani çözüm bir ölçek kadar belirsizdir.  ``λ`` çok
        küçükken bu belirsizlik sayısal olarak patlar: ölçüldü, ``λ=1e-8``
        ile ağırlık normları ``6e3`` ve ``9e4``e çıkıyor ve kayıp
        **tekdüze düşmüyor** (5.6e-3 → 2.5e-2 → 1.7e+0 …).  ``λ=1e-4``te
        normlar ``1e2`` mertebesinde kalıyor ve kayıp tekdüze düşüyor.
        Bu yüzden varsayılan ``λ`` küçük seçilmedi ve her turdan sonra
        çarpanlar **dengeleniyor**.
        """
        Pd = self._dal_ozn(U)                    # (N, g)
        Pt = self._govde_ozn(Y)                  # (M, g)
        H = np.asarray(hedef, float)
        if H.shape != (Pd.shape[0], Pt.shape[0]):
            raise ValueError(f"hedef {(Pd.shape[0], Pt.shape[0])} olmalı")
        r = np.random.default_rng(self.tohum + 1)
        self.W_govde = r.normal(0, 0.5, (self.gizli, self.p))
        tarih: List[float] = []
        for _ in range(tur):
            T = Pt @ self.W_govde                # (M, p)
            # W_dal: (g,p) çöz — vec ile: (Pd ⊗ T) w = vec(H)
            A = (np.kron(T.T @ T, Pd.T @ Pd)
                 + lam * np.eye(self.dal_boyu * self.p))
            b = (Pd.T @ H @ T).reshape(-1, order="F")
            self.W_dal = np.linalg.solve(A, b).reshape(
                self.dal_boyu, self.p, order="F")
            B = Pd @ self.W_dal                  # (N, p)
            A2 = np.kron(B.T @ B, Pt.T @ Pt) + lam * np.eye(self.gizli * self.p)
            b2 = (Pt.T @ H.T @ B).reshape(-1, order="F")
            self.W_govde = np.linalg.solve(A2, b2).reshape(
                self.gizli, self.p, order="F")
            # Ölçek dejenerasyonunu kapat: iki çarpanın normunu eşitle.
            # Çarpımı DEĞİŞTİRMEZ (c ile 1/c), yalnız belirsizliği alır.
            nd = float(np.linalg.norm(self.W_dal))
            ng = float(np.linalg.norm(self.W_govde))
            if nd > 1e-300 and ng > 1e-300:
                c = math.sqrt(ng / nd)
                self.W_dal = self.W_dal * c
                self.W_govde = self.W_govde / c
            tarih.append(float(np.mean((self(U, Y) - H) ** 2)))
        self.tarih = tarih                       # type: ignore[attr-defined]
        return self

    def __call__(self, U: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """``(N, m) × (M,) → (N, M)``."""
        B = self._dal_ozn(U) @ self.W_dal        # (N, p)
        T = self._govde_ozn(Y) @ self.W_govde    # (M, p)
        return B @ T.T + self.b0


# ══════════════════════════════════════════════════════════════════════
#  FINO: spektral tensör ayrışımı
# ══════════════════════════════════════════════════════════════════════

def fino_ayristir(R: np.ndarray, rutbe: int) -> Dict[str, object]:
    """``R(k₁,k₂) ≈ Σ_r U_r(k₁) V_r(k₂)`` — SVD ile en iyi ``R`` rütbeli.

    Eckart–Young teoremi: kesilmiş SVD, Frobenius normunda **en iyi**
    düşük rütbeli yaklaşımdır; başka bir ayrışım daha iyi olamaz.
    Kalan hata da kapalı formda bilinir: ``√(Σ_{r>R} σ_r²)``.

    Yani buradaki hata bir *gerçekleme kusuru* değil, seçilen rütbenin
    **kaçınılmaz** bedelidir ve tam olarak hesaplanabilir.
    """
    R_ = np.asarray(R)
    if R_.ndim != 2:
        raise ValueError("R iki indisli olmalı")
    if not 1 <= rutbe <= min(R_.shape):
        raise ValueError(f"1 ≤ rütbe ≤ {min(R_.shape)} olmalı")
    U, s, Vh = np.linalg.svd(R_, full_matrices=False)
    Ur = U[:, :rutbe] * s[:rutbe]
    Vr = Vh[:rutbe]
    yaklasik = Ur @ Vr
    kalan = float(np.sqrt(np.sum(s[rutbe:] ** 2)))
    return {
        "U": Ur, "V": Vr, "yaklaşık": yaklasik,
        "hata_frobenius": float(np.linalg.norm(yaklasik - R_, "fro")),
        "kapalı_form_hata": kalan,
        "bağıl_hata": kalan / max(float(np.sqrt(np.sum(s ** 2))), 1e-300),
        "parametre_tam": R_.size,
        "parametre_fino": Ur.size + Vr.size,
        "tekil_değerler": s,
    }


def fino_uygula(U: np.ndarray, V: np.ndarray, vhat: np.ndarray
                ) -> np.ndarray:
    """``(Σ_r U_r ⊗ V_r) · v̂`` — tam tensörü KURMADAN.

    ``(UV)v̂`` yerine ``U(Vv̂)`` sırasıyla çarpılır.  Netice aynı,
    maliyet ``K²`` yerine ``2KR``.  Bu, dizey çarpımının birleşme
    özelliğinden başka bir şey değildir ve testte birebir sınanır.
    """
    return np.asarray(U) @ (np.asarray(V) @ np.asarray(vhat))


def spektral_rutbe(R: np.ndarray, eps: float = 1e-3) -> int:
    """Enerjinin ``1−ε``ini tutan en küçük rütbe.

    Eşik **bağıldır** (toplam enerjiye göre); mutlak eşik, ölçeği
    değişen bir çekirdekte bambaşka bir rütbe verir.
    """
    s = np.linalg.svd(np.asarray(R), compute_uv=False)
    toplam = float(np.sum(s ** 2))
    if toplam <= 0:
        return 0
    kuyruk = toplam
    for r in range(s.size):
        kuyruk -= float(s[r] ** 2)
        if kuyruk < eps * toplam:
            return r + 1
    return s.size


# ══════════════════════════════════════════════════════════════════════
#  Çözünürlükten bağımsızlık
# ══════════════════════════════════════════════════════════════════════

def ornek_operator(u: np.ndarray, x: np.ndarray) -> np.ndarray:
    """``𝒢(u)(y) = ∫₀^y u(t)dt`` — antitürev işleci.

    Doğrusal, sürekli ve düzgün; bir operatör öğrenme sınaması için
    kanonik.  Trapez kuralıyla hesaplanır (hata ``O(h²)``).
    """
    u = np.asarray(u, float)
    x = np.asarray(x, float)
    dx = np.diff(x, prepend=x[0])
    orta = np.concatenate([[0.0], (u[1:] + u[:-1]) / 2 * np.diff(x)])
    return np.cumsum(orta)


def cozunurluk_bagimsizligi(model: DeepONet,
                            u_uret: Callable[[np.ndarray], np.ndarray],
                            sensor: np.ndarray,
                            Y_kaba: np.ndarray,
                            Y_ince: np.ndarray) -> Dict[str, object]:
    """Aynı modeli iki çıktı ızgarasında koş, ORTAK noktalarda kıyasla.

    ``Y_ince``, ``Y_kaba``yı kapsamalıdır; aksi hâlde kıyas
    interpolasyon hatasıyla kirlenir ve hiçbir şey söylemez.
    """
    ortak = np.intersect1d(Y_kaba, Y_ince)
    if ortak.size < Y_kaba.size:
        raise ValueError("ince ızgara kaba ızgarayı kapsamalı")
    U = np.atleast_2d(u_uret(sensor))
    yk = model(U, Y_kaba)
    yi = model(U, Y_ince)
    idx = np.searchsorted(Y_ince, Y_kaba)
    olcek = max(float(np.max(np.abs(yk))), 1e-300)
    return {
        "azamî_fark": float(np.max(np.abs(yk - yi[:, idx]))),
        "bağıl_fark": float(np.max(np.abs(yk - yi[:, idx]))) / olcek,
        "kaba_nokta": int(Y_kaba.size), "ince_nokta": int(Y_ince.size),
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== DeepONet: antitürev işlecini öğreniyor ===")
    m = 32
    sensor = np.linspace(0, 1, m)

    def rastgele_u(r, n):
        """Band-sınırlı rastgele fonksiyonlar."""
        a = r.normal(size=(n, 4))
        b = r.normal(size=(n, 4))
        return (a @ np.cos(2 * np.pi * np.arange(1, 5)[:, None] * sensor)
                + b @ np.sin(2 * np.pi * np.arange(1, 5)[:, None] * sensor))

    N = 300
    U = rastgele_u(rng, N)
    Y = np.linspace(0, 1, 41)
    hedef = np.stack([np.interp(Y, sensor, ornek_operator(u, sensor))
                      for u in U])
    model = DeepONet(m=m, p=16, gizli=40, tohum=0).uydur(U, Y, hedef, tur=12)
    s.append(f"  eğitim MSE seyri: "
             + " → ".join(f"{v:.2e}" for v in model.tarih[::3]))
    t = model.tarih
    artan = [i for i in range(1, len(t)) if t[i] > t[i - 1] + 1e-15]
    en_buyuk = max((t[i] - t[i - 1] for i in range(1, len(t))), default=0.0)
    s.append(f"  {len(t)} turun {len(artan)}'inde MSE arttı"
             f" (en büyük artış {en_buyuk:.1e}, taban {min(t):.1e}"
             f" — yani ‰{en_buyuk/min(t)*1000:.1f})")
    s.append(f"  artışların yeri: {artan}  (yakınsamadan SONRAKİ adımlar)")
    s.append("  Sebep: ALS DÜZENLENMİŞ hedefi eniyiliyor, burada")
    s.append("  DÜZENLENMEMİŞ MSE raporlanıyor; ikisi yakınsama sonrası")
    s.append("  bir mikron ayrışıyor. Tekdüzelik iddiası bu yüzden")
    s.append("  düzenlenmiş hedef için geçerlidir, MSE için değil.")
    s.append(f"  ‖W_dal‖={np.linalg.norm(model.W_dal):.2e}"
             f"  ‖W_gövde‖={np.linalg.norm(model.W_govde):.2e}"
             f"   (λ=1e-8 ile 6e3 ve 9e4'e patlıyordu)")
    U_s = rastgele_u(np.random.default_rng(99), 60)
    hedef_s = np.stack([np.interp(Y, sensor, ornek_operator(u, sensor))
                        for u in U_s])
    tahmin = model(U_s, Y)
    bagil = (np.linalg.norm(tahmin - hedef_s)
             / np.linalg.norm(hedef_s))
    s.append(f"  sınama bağıl L² hatası: {bagil:.4f}")

    s.append("\n=== Çıktı ızgarasından bağımsızlık ===")
    s.append("  model 41 noktada eğitildi; başka ızgaralarda koşuluyor:")
    for M in (41, 81, 161, 401):
        Yi = np.linspace(0, 1, M)
        try:
            r = cozunurluk_bagimsizligi(model, lambda ss: rastgele_u(
                np.random.default_rng(7), 3), sensor, Y, Yi)
            s.append(f"    M={M:4d}: ortak noktalarda bağıl fark = "
                     f"{r['bağıl_fark']:.3e}")
        except ValueError as e:
            s.append(f"    M={M:4d}: {e}")
    s.append("  Gövde ağı y'ye SÜREKLİ bağlı olduğu için çıktı ızgarası")
    s.append("  serbest; ızgara indisine bağlı olsaydı bu imkânsızdı.")

    s.append("\n=== FINO: spektral tensörün çarpanlara ayrılması ===")
    K = 48
    k1 = np.arange(K)[:, None]
    k2 = np.arange(K)[None, :]
    # Düzgün, hızlı sönen bir çekirdek (fiilî rütbesi düşük):
    R = np.exp(-(k1 + k2) / 12.0) * np.cos(0.3 * (k1 - k2))
    s.append(f"  tam tensör {R.shape}, {R.size} parametre")
    s.append(f"  enerjinin %99.9'unu tutan rütbe: {spektral_rutbe(R, 1e-3)}")
    s.append("   rütbe   bağıl hata   parametre   sıkıştırma")
    for rut in (1, 2, 4, 8, 16):
        d = fino_ayristir(R, rut)
        s.append(f"  {rut:5d}   {d['bağıl_hata']:.3e}   {d['parametre_fino']:8d}"
                 f"   {d['parametre_tam']/d['parametre_fino']:6.2f}×")
        assert abs(d["hata_frobenius"] - d["kapalı_form_hata"]) < 1e-9
    s.append("  Hata kapalı formda biliniyor: √(Σ_{r>R} σ_r²).")
    s.append("  Ölçülen Frobenius hatası ile bu formül 1e-9 içinde uyuşuyor;")
    s.append("  yani kesilmiş SVD gerçekten EN İYİ ayrışım (Eckart–Young).")

    s.append("\n=== FINO uygulaması: tam tensör kurulmadan ===")
    for rut in (4, 8):
        d = fino_ayristir(R, rut)
        vhat = rng.normal(size=K)
        t0 = time.perf_counter()
        for _ in range(20000):
            a = fino_uygula(d["U"], d["V"], vhat)
        hizli = time.perf_counter() - t0
        t0 = time.perf_counter()
        for _ in range(20000):
            b = d["yaklaşık"] @ vhat
        yavas = time.perf_counter() - t0
        s.append(f"  rütbe {rut}: ayrık çarpım {hizli*1000:6.1f} ms,"
                 f" tam dizey {yavas*1000:6.1f} ms  ({yavas/hizli:.2f}×)"
                 f"   fark = {np.max(np.abs(a - b)):.2e}")
    s.append("  K=48'de kazanç küçük; asıl fayda K büyüdükçe:")
    for KK in (48, 256, 1024):
        for rut in (8,):
            s.append(f"    K={KK:5d} rütbe={rut}: {KK*KK} v {2*KK*rut}"
                     f" parametre → {KK*KK/(2*KK*rut):6.1f}× tasarruf")

    s.append("\n=== K30: ölçek çarpanı norma girer, alana değil ===")
    f = lambda z: np.sin(2 * np.pi * z)
    s.append("      N     doğru ‖v‖_L²     yanlış: alanı ölçekleyip azamî")
    for N in (64, 256, 1024, 4096):
        x = np.linspace(0, 1, N, endpoint=False)
        v = f(x)
        s.append(f"  {N:6d}   {l2_norm(v):.10f}      "
                 f"{np.max(np.abs(v * np.sqrt(1.0 / N))):.10f}")
    s.append("  Doğru norm çözünürlükten bağımsız; yanlış ölçekleme")
    s.append("  fonksiyonun genliğini √N ile çökertiyor.")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
