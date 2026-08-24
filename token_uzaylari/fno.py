"""FNO — Fourier Nöral Operatörü ve ızgaradan bağımsızlık.

Bir *operatör* öğrenmek, bir fonksiyondan fonksiyona giden eşlemeyi
öğrenmektir.  FNO bunu spektral uzayda yapar:

.. math::

   v^{(l+1)}(x) = \\sigma\\Bigl( W v^{(l)}(x)
       + \\mathcal{F}^{-1}\\bigl( R_\\theta \\cdot \\mathcal{F}v^{(l)} \\bigr)(x)
       \\Bigr)

``R_θ`` yalnız ``|k| ≤ k_kesme`` kiplerinde sıfırdan farklıdır.  Bu
kesme bir *yaklaşıklık kabulü* değil, operatörün **tanımının parçası**:
öğrenilen çekirdek düzgün (band-sınırlı) bir çekirdektir ve ızgara
sıklaştıkça aynı sürekli operatöre yakınsar.

Bu modülün asıl iddiası ve asıl ölçümü **ızgaradan bağımsızlıktır**:
aynı ``R_θ`` ile farklı çözünürlüklerde koşulan operatör, ortak
noktalarda *aynı* fonksiyonu vermelidir.  Sıradan bir evrişim ağı bunu
yapamaz; çünkü onun çekirdeği piksel cinsindendir, FNO'nunki ise kip
cinsinden.  İkisi de burada koşulur ve fark ölçülür.

Ayrıca:

* **Parseval sağlaması** — ``Σ|v|² = Σ|v̂|²/N``; spektral yolun enerjiyi
  kaybetmediğinin bağımsız şahidi.
* **Kesme eşiği** — ``k_kesme``, spektral enerjinin ``1−ε``ini tutan en
  küçük kiptir; elle seçilmez, veriden **hesaplanır**.
* **Reel sinyalde eşlenik simetri** — ``v̂(−k) = conj(v̂(k))``.  ``rfft``
  kullanmak bunu yapı gereği sağlar ve hem yarı hafıza hem yarı iş
  demektir; netice birebir aynıdır ve öyle olduğu ölçülür.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "spektral_enerji", "kesme_kipi", "SpektralKatman", "FNO",
    "parseval_sapmasi", "izgaradan_bagimsizlik", "yeniden_ornekle",
]


# ══════════════════════════════════════════════════════════════════════
#  Spektral yardımcılar
# ══════════════════════════════════════════════════════════════════════

def spektral_enerji(v: np.ndarray) -> np.ndarray:
    """Kip başına enerji ``‖v̂(k)‖²`` — kanallar üzerinden toplanmış.

    ``v``: ``(N, c)``.  Dönen: ``(N//2+1,)``.
    """
    v = np.atleast_2d(np.asarray(v, float))
    V = np.fft.rfft(v, axis=0)
    return np.sum(np.abs(V) ** 2, axis=1)


def kesme_kipi(v: np.ndarray, eps: float = 1e-3) -> int:
    """Enerjinin ``1−ε``ini tutan en küçük ``k``.

    Tanım: ``k_kesme = min{k : Σ_{|k'|>k} E(k') < ε·Σ E}``.  Yani kesme
    veriden hesaplanır, elle seçilmez.  ``ε`` ne kadar küçükse o kadar
    çok kip tutulur; ``ε=0`` bütün kipleri tutar.
    """
    E = spektral_enerji(v)
    toplam = float(E.sum())
    if toplam <= 0:
        return 0
    kuyruk = float(E.sum())
    for k in range(E.size):
        kuyruk -= float(E[k])
        if kuyruk < eps * toplam:
            return k
    return E.size - 1


def parseval_sapmasi(v: np.ndarray) -> float:
    """``|Σ|v|² − Σ|v̂|²/N|`` bağıl sapması.

    ``rfft`` yalnız yarı spektrumu tuttuğu için, orta kipler iki kere
    sayılmalıdır; ``k=0`` ve (çift ``N``de) ``k=N/2`` ise bir kere.
    Bu ayrım yapılmazsa sapma ~2 kat çıkar ve yanlışlıkla "Parseval
    bozuluyor" sanılır.
    """
    v = np.atleast_2d(np.asarray(v, float))
    N = v.shape[0]
    V = np.fft.rfft(v, axis=0)
    agirlik = np.full(V.shape[0], 2.0)
    agirlik[0] = 1.0
    if N % 2 == 0:
        agirlik[-1] = 1.0
    sag = float(np.sum(agirlik[:, None] * np.abs(V) ** 2)) / N
    sol = float(np.sum(v ** 2))
    return abs(sol - sag) / max(abs(sol), 1e-30)


def yeniden_ornekle(f: Callable[[np.ndarray], np.ndarray], N: int
                    ) -> np.ndarray:
    """``[0,1)`` üzerinde ``N`` düzgün noktada örnekle."""
    x = np.linspace(0.0, 1.0, N, endpoint=False)
    return np.asarray(f(x), float).reshape(N, -1)


# ══════════════════════════════════════════════════════════════════════
#  Spektral katman
# ══════════════════════════════════════════════════════════════════════

@dataclass
class SpektralKatman:
    """Tek FNO katmanı: ``σ(Wv + ℱ⁻¹(R_θ·ℱv))``.

    ``R`` şekli ``(k_kesme+1, c_giris, c_cikis)`` karmaşık.  Kip sayısı
    **ızgaradan bağımsızdır**: aynı ``R`` her ``N`` için kullanılır,
    ``N``den fazla kip istenirse mevcut olanlarla yetinilir (ve bu
    sessizce değil, ``kullanilan_kip`` ile bildirilir).
    """
    c_giris: int
    c_cikis: int
    k_kesme: int
    tohum: int = 0
    aktivasyon: Optional[Callable[[np.ndarray], np.ndarray]] = None
    R: np.ndarray = field(init=False)
    W: np.ndarray = field(init=False)
    b: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        if self.k_kesme < 0:
            raise ValueError("k_kesme ≥ 0 olmalı")
        r = np.random.default_rng(self.tohum)
        olcek = 1.0 / np.sqrt(self.c_giris * max(self.k_kesme, 1))
        self.R = (r.normal(0, olcek, (self.k_kesme + 1, self.c_giris,
                                      self.c_cikis))
                  + 1j * r.normal(0, olcek, (self.k_kesme + 1, self.c_giris,
                                             self.c_cikis)))
        self.W = r.normal(0, 1.0 / np.sqrt(self.c_giris),
                          (self.c_giris, self.c_cikis))
        self.b = np.zeros(self.c_cikis)
        if self.aktivasyon is None:
            self.aktivasyon = lambda z: np.tanh(z)

    @property
    def parametre_sayisi(self) -> int:
        return 2 * self.R.size + self.W.size + self.b.size

    def kullanilan_kip(self, N: int) -> int:
        """Bu çözünürlükte fiilen kullanılabilen kip sayısı."""
        return min(self.k_kesme + 1, N // 2 + 1)

    def ileri(self, v: np.ndarray) -> np.ndarray:
        """``(N, c_giris) → (N, c_cikis)``.

        Yerel terim ``Wv`` nokta bazındadır; spektral terim ise
        ``rfft`` ile alınır, ilk ``k_kesme+1`` kipte ``R`` ile çarpılır,
        kalan kipler **sıfırlanır** ve ``irfft`` ile geri dönülür.
        ``irfft``e ``n=N`` verilmesi şart: yoksa tek uzunluklu ızgaralar
        sessizce bir örnek kaybeder.
        """
        v = np.atleast_2d(np.asarray(v, float))
        if v.shape[1] != self.c_giris:
            raise ValueError(f"girdi {self.c_giris} kanallı olmalı")
        N = v.shape[0]
        V = np.fft.rfft(v, axis=0)                      # (N//2+1, c_giris)
        kip = self.kullanilan_kip(N)
        Y = np.zeros((V.shape[0], self.c_cikis), dtype=complex)
        Y[:kip] = np.einsum("kab,ka->kb", self.R[:kip], V[:kip])
        spektral = np.fft.irfft(Y, n=N, axis=0)
        return self.aktivasyon(v @ self.W + self.b + spektral)


@dataclass
class FNO:
    """Katman yığını; giriş ve çıkış yükseltmeleriyle."""
    kanallar: Sequence[int]
    k_kesme: int = 8
    tohum: int = 0
    katmanlar: List[SpektralKatman] = field(init=False)

    def __post_init__(self) -> None:
        if len(self.kanallar) < 2:
            raise ValueError("en az giriş ve çıkış kanalı lazım")
        self.katmanlar = [
            SpektralKatman(a, b, self.k_kesme, self.tohum * 100 + i)
            for i, (a, b) in enumerate(zip(self.kanallar[:-1],
                                           self.kanallar[1:]))
        ]

    @property
    def parametre_sayisi(self) -> int:
        return sum(k.parametre_sayisi for k in self.katmanlar)

    def ileri(self, v: np.ndarray) -> np.ndarray:
        for kat in self.katmanlar:
            v = kat.ileri(v)
        return v

    def __call__(self, v: np.ndarray) -> np.ndarray:
        return self.ileri(v)


# ══════════════════════════════════════════════════════════════════════
#  Kıyas: piksel cinsinden evrişim
# ══════════════════════════════════════════════════════════════════════

@dataclass
class EvrisimKatmani:
    """Aynı işi *piksel* cinsinden yapan dairesel evrişim.

    FNO ile tek farkı çekirdeğin nerede yaşadığıdır: burada sabit
    genişlikte bir pencere (``2w+1`` örnek), FNO'da ise sabit sayıda
    **kip**.  Izgara sıklaştığında pencere fiziksel olarak daralır;
    kip ise daralmaz.  Aşağıdaki ölçüm tam olarak bunu gösterir.
    """
    c_giris: int
    c_cikis: int
    yari_genislik: int = 4
    tohum: int = 0
    K: np.ndarray = field(init=False)
    W: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        r = np.random.default_rng(self.tohum)
        g = 2 * self.yari_genislik + 1
        self.K = r.normal(0, 1.0 / np.sqrt(self.c_giris * g),
                          (g, self.c_giris, self.c_cikis))
        self.W = r.normal(0, 1.0 / np.sqrt(self.c_giris),
                          (self.c_giris, self.c_cikis))

    def ileri(self, v: np.ndarray) -> np.ndarray:
        v = np.atleast_2d(np.asarray(v, float))
        N = v.shape[0]
        cikti = np.zeros((N, self.c_cikis))
        for j, kaydir in enumerate(range(-self.yari_genislik,
                                         self.yari_genislik + 1)):
            cikti += np.roll(v, kaydir, axis=0) @ self.K[j]
        return np.tanh(v @ self.W + cikti)


# ══════════════════════════════════════════════════════════════════════
#  Izgaradan bağımsızlık ölçümü
# ══════════════════════════════════════════════════════════════════════

def izgaradan_bagimsizlik(kat, f: Callable[[np.ndarray], np.ndarray],
                          N_kaba: int, N_ince: int) -> Dict[str, object]:
    """Aynı işleci iki çözünürlükte koş, **ortak noktalarda** karşılaştır.

    ``N_ince`` ``N_kaba``nın tam katı olmalıdır ki kaba ızgaranın her
    noktası ince ızgarada da bulunsun; aksi hâlde karşılaştırma
    interpolasyon hatasıyla kirlenir ve ölçüm hiçbir şey söylemez.
    """
    if N_ince % N_kaba != 0:
        raise ValueError("N_ince, N_kaba'nın tam katı olmalı")
    adim = N_ince // N_kaba
    v_kaba = yeniden_ornekle(f, N_kaba)
    v_ince = yeniden_ornekle(f, N_ince)
    y_kaba = kat.ileri(v_kaba)
    y_ince = kat.ileri(v_ince)[::adim]
    olcek = max(float(np.max(np.abs(y_kaba))), 1e-30)
    return {
        "N_kaba": N_kaba, "N_ince": N_ince,
        "azamî_fark": float(np.max(np.abs(y_kaba - y_ince))),
        "bağıl_fark": float(np.max(np.abs(y_kaba - y_ince))) / olcek,
        "çıktı_büyüklüğü": olcek,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _ornek_alan(x: np.ndarray) -> np.ndarray:
    """Band-sınırlı iki kanallı bir alan — kipleri bilinerek seçildi."""
    return np.stack([
        np.sin(2 * np.pi * x) + 0.5 * np.cos(6 * np.pi * x),
        np.cos(4 * np.pi * x) - 0.3 * np.sin(2 * np.pi * x),
    ], axis=1)


def _gosterim() -> str:
    import time
    s: List[str] = []

    s.append("=== Parseval: spektral yol enerji kaybetmiyor mu? ===")
    for N in (16, 17, 64, 128, 257):
        v = yeniden_ornekle(_ornek_alan, N)
        s.append(f"  N={N:<4} bağıl sapma = {parseval_sapmasi(v):.3e}")
    s.append("  (tek ve çift N ayrı ayrı: rfft'te uç kiplerin ağırlığı farklı)")

    s.append("\n=== Kesme kipi veriden hesaplanıyor ===")
    x = np.linspace(0, 1, 256, endpoint=False)
    for ad, g in (("sin(2πx)", lambda z: np.sin(2 * np.pi * z)[:, None]),
                  ("2 kipli alan", _ornek_alan),
                  ("gürültü", lambda z: np.random.default_rng(0)
                   .normal(0, 1, (z.size, 1)))):
        v = np.asarray(g(x), float).reshape(256, -1)
        satir = f"  {ad:14s}"
        for eps in (1e-2, 1e-6, 1e-12):
            satir += f"  ε={eps:.0e}: k={kesme_kipi(v, eps):3d}"
        s.append(satir)
    s.append("  Band-sınırlı alanlarda k küçük ve ε'a DUYARSIZ (bütün enerji")
    s.append("  birkaç kipte; ε'u trilyonda bire indirmek k'yı oynatmıyor).")
    s.append("  Gürültüde ise k daha ε=1e-2'de bütün spektrumu istiyor:")
    s.append("  beyaz gürültünün kesilebilecek bir kuyruğu yoktur.")

    s.append("\n=== Izgaradan bağımsızlık: FNO v evrişim ===")
    fno_kat = SpektralKatman(2, 3, k_kesme=8, tohum=1)
    evr_kat = EvrisimKatmani(2, 3, yari_genislik=4, tohum=1)
    s.append("  ölçüm: aynı işleç iki çözünürlükte, ORTAK noktalarda")
    s.append("  N_kaba  N_ince    FNO bağıl fark    evrişim bağıl fark")
    for Nk, Ni in ((32, 64), (32, 128), (64, 256), (128, 512)):
        a = izgaradan_bagimsizlik(fno_kat, _ornek_alan, Nk, Ni)
        b = izgaradan_bagimsizlik(evr_kat, _ornek_alan, Nk, Ni)
        s.append(f"   {Nk:4d}    {Ni:4d}     {a['bağıl_fark']:.3e}"
                 f"        {b['bağıl_fark']:.3e}")
    s.append("  FNO'nun çekirdeği KİP cinsinden olduğu için ızgara")
    s.append("  sıklaşınca değişmiyor; evrişiminki PİKSEL cinsinden,")
    s.append("  o yüzden pencere fiziksel olarak daralıyor ve netice kayıyor.")

    s.append("\n=== Kesme kip sayısından fazlası istenirse ===")
    kat = SpektralKatman(2, 2, k_kesme=40, tohum=0)
    for N in (8, 16, 64, 128):
        s.append(f"  N={N:<4} istenen kip=41, kullanılabilen="
                 f"{kat.kullanilan_kip(N)}"
                 f"  → çıktı sonlu mu? "
                 f"{bool(np.all(np.isfinite(kat.ileri(yeniden_ornekle(_ornek_alan, N)))))}")

    s.append("\n=== Çok katmanlı FNO ===")
    ag = FNO([2, 8, 8, 1], k_kesme=12, tohum=2)
    v = yeniden_ornekle(_ornek_alan, 128)
    y = ag(v)
    s.append(f"  FNO([2,8,8,1]) çıktı {y.shape}, parametre {ag.parametre_sayisi}")
    a = izgaradan_bagimsizlik(ag, _ornek_alan, 64, 256)
    s.append(f"  yığının ızgaradan bağımsızlığı: bağıl fark ="
             f" {a['bağıl_fark']:.3e}")
    s.append("  Tek katmanda 1e-16 idi, yığında 1e-06. Bu bir kusur değil,")
    s.append("  ÖRTÜŞME (aliasing): tanh yüksek kipler üretiyor, kaba")
    s.append("  ızgarada bunlar düşük kiplere katlanıyor. Sebebi ölçelim —")
    dogrusal = FNO([2, 8, 8, 1], k_kesme=12, tohum=2)
    for kat in dogrusal.katmanlar:
        kat.aktivasyon = lambda z: z
    b = izgaradan_bagimsizlik(dogrusal, _ornek_alan, 64, 256)
    tek = izgaradan_bagimsizlik(SpektralKatman(2, 3, 8, 1),
                                _ornek_alan, 64, 256)
    s.append(f"    tek katman (tanh)      : {tek['bağıl_fark']:.3e}")
    s.append(f"    yığın, aktivasyon = id : {b['bağıl_fark']:.3e}")
    s.append(f"    yığın, aktivasyon= tanh: {a['bağıl_fark']:.3e}")
    s.append("  Aktivasyon doğrusal yapılınca fark makine hassasiyetine")
    s.append("  iniyor; suçlu tam olarak doğrusal-olmayanlıktır.")

    s.append("\n=== rfft ile tam fft aynı neticeyi veriyor mu? ===")
    v = yeniden_ornekle(_ornek_alan, 128)
    V_r = np.fft.rfft(v, axis=0)
    V_f = np.fft.fft(v, axis=0)[:V_r.shape[0]]
    s.append(f"  ilk yarı spektrumda azamî fark = "
             f"{np.max(np.abs(V_r - V_f)):.3e}")
    s.append(f"  rfft bellek = {V_r.nbytes} bayt,"
             f" fft = {np.fft.fft(v, axis=0).nbytes} bayt"
             f"  → {np.fft.fft(v, axis=0).nbytes / V_r.nbytes:.2f}× tasarruf")
    t0 = time.perf_counter()
    for _ in range(2000):
        np.fft.rfft(v, axis=0)
    t_r = time.perf_counter() - t0
    t0 = time.perf_counter()
    for _ in range(2000):
        np.fft.fft(v, axis=0)
    t_f = time.perf_counter() - t0
    s.append(f"  2000 dönüşüm: rfft {t_r*1000:.1f} ms, fft {t_f*1000:.1f} ms"
             f"  → {t_f/t_r:.2f}×")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
