"""
Modern yaklaşım mimarileri, sadeleştirilmiş fakat SAHİCİ hâlleriyle.

Üçü de aynı sorunun ayrı cevaplarıdır: "yaklaşımı nereye koyacaksın?"

  * **KAN** -- yaklaşımı DÜĞÜMLERE değil KENARLARA koyar. Her kenarda
    öğrenilen tek değişkenli bir fonksiyon vardır; düğümler yalnız
    toplar. Kolmogorov--Arnold temsil teoreminin biçimidir. Kazancı
    hızdan çok **okunabilirliktir**: öğrenilen kenar fonksiyonları
    doğrudan bakılabilir. Burada ölçülen de budur.

  * **Fourier işlemcisi (FNO)** -- yaklaşımı FONKSİYON UZAYLARI ARASINDA
    kurar. Çekirdek evrişimi Fourier'de çarpmadır; öğrenilen şey her kip
    için bir çarpandır. Asıl kazancı **çözünürlükten bağımsızlığıdır**:
    N=64'te öğrenilen ağırlıklar N=256'da çalışır. Zaafı, ağırlıkların
    kiplerde yaşamasıdır: eğitimde görülmemiş yüksek kipler yanlış
    ölçeklenir.

  * **DeepONet** -- işlemciyi ``G(a)(y) = Σ_k b_k(a)·t_k(y)`` diye
    ayrıştırır (dal + gövde). Dal, ``a``yı SABİT bir duyu ızgarasında
    okur; bu yüzden başka çözünürlükteki bir girdiyi OLDUĞU GİBİ kabul
    edemez, önce yeniden örneklemek gerekir. Ölçülen fark budur:
    yeniden örneklendikten sonra iki usulün hatası DENKTİR. Yani FNO'nun
    üstünlüğü bu işte doğrulukta değil, arayüzdedir.

Bütün ağırlıklar ya en küçük karelerle ya sade gradyan inişiyle
öğrenilir; hiçbir iddia ölçülmeden yazılmamıştır.
"""
from __future__ import annotations

from typing import Callable, Dict, Tuple

import numpy as np


# =====================================================================
#  1. KAN -- kenarlarda öğrenilen fonksiyonlar (RBF tabanlı)
# =====================================================================
def _rbf(x: np.ndarray, dugum: np.ndarray, h: float) -> np.ndarray:
    return np.exp(-0.5 * ((x[:, None] - dugum[None, :]) / h) ** 2)


def _drbf(x: np.ndarray, dugum: np.ndarray, h: float) -> np.ndarray:
    return -((x[:, None] - dugum[None, :]) / (h * h)) * _rbf(x, dugum, h)


class KAN211:
    """``[2,1,1]`` KAN: ``f(x,y) = Φ( φ₁(x) + φ₂(y) )``.

    Hedef ``exp(sin(πx) + y²)`` tam olarak bu biçimdedir; dolayısıyla
    sınanabilir bir iddia doğar: eğitimden sonra ``φ₁`` ``sin(πx)`` ile,
    ``φ₂`` ``y²`` ile -- bir afin yeniden ölçeklemeye kadar -- uyuşmalıdır.

    Kenar fonksiyonları RBF tabanındadır (FastKAN'ın yaptığı gibi; B-spline
    yerine Gauss tabanı, kurgusu aynıdır). Dış ızgara ``s``in fiilî
    aralığına göre periyodik olarak YENİLENİR -- yenilenmezse ``s`` sabit
    ızgaranın dışına çıkar ve model çöker (bu, ölçüm sırasında görüldü:
    kalıntı 0.58'den 0.99'a, yani hiç öğrenmemeye çıktı).
    """

    def __init__(self, ic_dugum: int = 32, dis_dugum: int = 32, tohum: int = 0) -> None:
        rng = np.random.default_rng(tohum)
        self.gx = np.linspace(-1, 1, ic_dugum)
        self.hx = (self.gx[1] - self.gx[0]) * 1.5
        self.c1 = rng.normal(scale=0.8, size=ic_dugum)
        self.c2 = rng.normal(scale=0.8, size=ic_dugum)
        self.K = dis_dugum
        self.gs = np.linspace(-1, 1, dis_dugum)
        self.hs = (self.gs[1] - self.gs[0]) * 1.5
        self.c3 = np.zeros(dis_dugum)

    def kenar(self, t: np.ndarray, hangi: int) -> np.ndarray:
        return _rbf(t, self.gx, self.hx) @ (self.c1 if hangi == 1 else self.c2)

    def ic(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return self.kenar(x, 1) + self.kenar(y, 2)

    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return _rbf(self.ic(x, y), self.gs, self.hs) @ self.c3

    def _izgara_yenile(self, s: np.ndarray, hedef: np.ndarray, lam: float) -> None:
        lo, hi = float(s.min()), float(s.max())
        pay = 0.15 * (hi - lo) + 1e-6
        self.gs = np.linspace(lo - pay, hi + pay, self.K)
        self.hs = (self.gs[1] - self.gs[0]) * 1.5
        B = _rbf(s, self.gs, self.hs)
        self.c3 = np.linalg.solve(B.T @ B + lam * np.eye(self.K), B.T @ hedef)

    def egit(
        self, x: np.ndarray, y: np.ndarray, hedef: np.ndarray,
        tur: int = 8000, eta0: float = 0.01, lam: float = 1e-6,
    ) -> float:
        """Adam ile ortak eğitim; her 200 turda dış ızgara yenilenir.

        Gradyanda dikkat edilecek yer: ``∂s/∂c₁`` kenar tabanının KENDİSİDİR
        (``_rbf``), TÜREVİ (``_drbf``) değil. Türev yalnız ``∂f/∂s``de geçer.
        Bu ikisi yazarken karıştırıldı ve model hiç öğrenmedi; ölçüm
        gösterdi.
        """
        m1x, m1y = _rbf(x, self.gx, self.hx), _rbf(y, self.gx, self.hx)
        n = len(x)
        P = [self.c1, self.c2, self.c3]
        M = [np.zeros_like(p) for p in P]
        V = [np.zeros_like(p) for p in P]
        art = np.zeros(n)
        for t in range(1, tur + 1):
            s = m1x @ P[0] + m1y @ P[1]
            if t % 200 == 1:
                self._izgara_yenile(s, hedef, lam)
                P[2] = self.c3
                M[2] = np.zeros_like(P[2])
                V[2] = np.zeros_like(P[2])
            B = _rbf(s, self.gs, self.hs)
            art = B @ P[2] - hedef
            ds = _drbf(s, self.gs, self.hs) @ P[2]
            g = (2.0 / n) * (art * ds)
            G = [m1x.T @ g, m1y.T @ g, (2.0 / n) * (B.T @ art)]
            eta = eta0 * (1 - t / tur) + 1e-5
            for i in range(3):
                M[i] *= 0.9
                M[i] += 0.1 * G[i]
                V[i] *= 0.999
                V[i] += 0.001 * G[i] ** 2
                P[i] -= eta * (M[i] / (1 - 0.9 ** t)) / (np.sqrt(V[i] / (1 - 0.999 ** t)) + 1e-8)
        self.c1, self.c2, self.c3 = P
        return float(np.sqrt(np.mean(art ** 2)))


def _afin_uyum(a: np.ndarray, b: np.ndarray) -> float:
    """``a``yı ``b``ye afin uydurduktan sonra kalan bağıl hata.

    Afin serbestlik ZORUNLUDUR: ``φ₁ + φ₂`` ayrışması ancak bir sabit
    kayma ve ortak ölçekleme belirsizliğine kadar tektir.
    """
    A = np.stack([a, np.ones_like(a)], axis=1)
    kat, *_ = np.linalg.lstsq(A, b, rcond=None)
    return float(np.sqrt(np.mean((A @ kat - b) ** 2)) / (np.std(b) + 1e-12))


def kan_sinamasi(n: int = 2000, restart: int = 6, tohum: int = 0) -> Dict[str, object]:
    """KAN'ın iki yüzü birlikte ölçülür: okunabilirlik VE dışbükey olmayışı.

    Aynı hedefte birkaç ayrı rastgele başlangıç koşulur. Bir kısmı ``φ₁``in
    monoton kaldığı yerel bir çukura düşer ve kalıntı orada takılır; iyi
    havzaya düşenler kalıntıyı ~0.005'e indirir VE kenar fonksiyonlarını
    ``sin(πx)``, ``y²`` olarak geri verir.

    Yani "KAN okunabilir" iddiası ŞARTLIDIR: okunabilirlik ancak doğru
    havzada doğar, ve hangi havzada olduğun ancak EĞİTİM kalıntısından
    anlaşılır.
    """
    rng = np.random.default_rng(tohum)
    hedef = lambda x, y: np.exp(np.sin(np.pi * x) + y * y)
    x = rng.uniform(-1, 1, n)
    y = rng.uniform(-1, 1, n)
    z = hedef(x, y)
    mu, sd = float(z.mean()), float(z.std())
    zn = (z - mu) / sd

    xt, yt = rng.uniform(-1, 1, 800), rng.uniform(-1, 1, 800)
    zt = (hedef(xt, yt) - mu) / sd

    izgara = np.linspace(-1, 1, 300)
    denemeler = []
    en_iyi = None
    for tekrar in range(restart):
        ag = KAN211(tohum=100 + tekrar)
        kalinti = ag.egit(x, y, zn)
        d = {
            "kalinti": kalinti,
            "sinama": float(np.sqrt(np.mean((ag(xt, yt) - zt) ** 2))),
            "u1": _afin_uyum(ag.kenar(izgara, 1), np.sin(np.pi * izgara)),
            "u2": _afin_uyum(ag.kenar(izgara, 2), izgara ** 2),
        }
        denemeler.append(d)
        if en_iyi is None or d["kalinti"] < en_iyi["kalinti"]:
            en_iyi = d

    basarili = [d for d in denemeler if d["kalinti"] < 0.05]
    return {
        "restart": restart,
        "en_iyi_egitim_kalintisi": en_iyi["kalinti"],
        "en_iyi_bagil_sinama_hatasi": en_iyi["sinama"],
        "iyi_uyduruyor": bool(en_iyi["sinama"] < 0.05),
        "phi1_sin_ile_uyum_hatasi": en_iyi["u1"],
        "phi2_kare_ile_uyum_hatasi": en_iyi["u2"],
        "kenarlar_okunabilir": bool(en_iyi["u1"] < 0.05 and en_iyi["u2"] < 0.05),
        "basarili_restart_sayisi": len(basarili),
        "cukura_dusen_var": bool(len(basarili) < restart),
        "kalintilar": [round(d["kalinti"], 4) for d in denemeler],
    }


# =====================================================================
#  2. Fourier işlemcisi
# =====================================================================
def poisson_ornekleri(
    n: int, N: int, azami_kip: int = 8, tohum: int = 0
) -> Tuple[np.ndarray, np.ndarray]:
    """``−u'' = a`` (periyodik, ortalama sıfır). Çözüm Fourier'de ``û_k = â_k/k²``."""
    rng = np.random.default_rng(tohum)
    k = np.fft.rfftfreq(N, d=1.0 / N)
    a_hat = np.zeros((n, len(k)), dtype=complex)
    kip = np.arange(1, azami_kip + 1)
    a_hat[:, kip] = (rng.normal(size=(n, azami_kip)) + 1j * rng.normal(size=(n, azami_kip))) / kip
    a = np.fft.irfft(a_hat, n=N) * N
    u_hat = np.zeros_like(a_hat)
    u_hat[:, 1:] = a_hat[:, 1:] / (k[1:] ** 2)
    u = np.fft.irfft(u_hat, n=N) * N
    return a, u


class FourierIslemci:
    """Tek katmanlı spektral işlemci: her kip için bir karmaşık çarpan."""

    def __init__(self, kip_sayisi: int = 16) -> None:
        self.kip_sayisi = kip_sayisi
        self.R = np.zeros(kip_sayisi, dtype=complex)

    def egit(self, a: np.ndarray, u: np.ndarray) -> None:
        N = a.shape[1]
        A = np.fft.rfft(a, axis=1)
        U = np.fft.rfft(u, axis=1)
        for j in range(self.kip_sayisi):
            pay = np.vdot(A[:, j], U[:, j])
            payda = np.vdot(A[:, j], A[:, j])
            self.R[j] = pay / payda if abs(payda) > 1e-12 else 0.0

    def __call__(self, a: np.ndarray) -> np.ndarray:
        """**Çözünürlükten bağımsız**: ağırlıklar KİPLERDE yaşar, ızgarada değil."""
        N = a.shape[1]
        A = np.fft.rfft(a, axis=1)
        U = np.zeros_like(A)
        j = min(self.kip_sayisi, A.shape[1])
        U[:, :j] = A[:, :j] * self.R[:j]
        return np.fft.irfft(U, n=N)


def _bagil(v: np.ndarray, d: np.ndarray) -> float:
    return float(np.linalg.norm(v - d) / np.linalg.norm(d))


def fno_sinamasi() -> Dict[str, object]:
    a, u = poisson_ornekleri(400, 64, azami_kip=8, tohum=0)
    f = FourierIslemci(kip_sayisi=16)
    f.egit(a, u)

    a1, u1 = poisson_ornekleri(200, 64, azami_kip=8, tohum=1)
    ayni = _bagil(f(a1), u1)

    # ÇÖZÜNÜRLÜK AKTARIMI: N=64'te öğrenildi, N=256'da sınanıyor
    a2, u2 = poisson_ornekleri(200, 256, azami_kip=8, tohum=2)
    baska = _bagil(f(a2), u2)

    # ZAAF: eğitimde görülmemiş yüksek kipler
    a3, u3 = poisson_ornekleri(200, 256, azami_kip=24, tohum=3)
    yuksek = _bagil(f(a3), u3)
    return {
        "ayni_cozunurluk_hatasi": ayni,
        "farkli_cozunurluk_hatasi": baska,
        "cozunurluk_aktarimi_calisiyor": bool(baska < 0.02),
        "yuksek_kip_hatasi": yuksek,
        "yuksek_kipte_bozuluyor": bool(yuksek > 10 * max(baska, 1e-12)),
    }


# =====================================================================
#  3. DeepONet (doğrusal dal + Fourier gövdesi)
# =====================================================================
class DeepONet:
    """``G(a)(y) ≈ Σ_k b_k(a)·t_k(y)``; dal SABİT duyu ızgarasında okur."""

    def __init__(self, duyu: int = 64, taban: int = 32) -> None:
        self.duyu = duyu
        self.taban = taban
        self.W = np.zeros((taban, duyu))

    def _govde(self, y: np.ndarray) -> np.ndarray:
        k = np.arange(1, self.taban // 2 + 1)
        return np.concatenate(
            [np.cos(2 * np.pi * k[None, :] * y[:, None]),
             np.sin(2 * np.pi * k[None, :] * y[:, None])], axis=1
        )

    def egit(self, a: np.ndarray, u: np.ndarray, lam: float = 1e-8) -> None:
        y = np.arange(a.shape[1]) / a.shape[1]
        T = self._govde(y)                       # (N, taban)
        # u ≈ T @ W @ aᵀ  ⇒  her örnek için katsayı hedefi
        C = np.linalg.lstsq(T, u.T, rcond=None)[0].T          # (n, taban)
        self.W = np.linalg.solve(
            a.T @ a + lam * np.eye(self.duyu), a.T @ C
        ).T                                                   # (taban, duyu)

    def __call__(self, a: np.ndarray, N: int | None = None) -> np.ndarray:
        N = N or a.shape[1]
        y = np.arange(N) / N
        return (self._govde(y) @ (self.W @ a.T)).T


def deeponet_sinamasi() -> Dict[str, object]:
    a, u = poisson_ornekleri(400, 64, azami_kip=8, tohum=0)
    d = DeepONet(duyu=64, taban=32)
    d.egit(a, u)

    a1, u1 = poisson_ornekleri(200, 64, azami_kip=8, tohum=1)
    ayni = _bagil(d(a1), u1)

    # aynı işlemci, ama girdi N=256 ızgarasında: dal artık uymuyor
    a2, u2 = poisson_ornekleri(200, 256, azami_kip=8, tohum=2)
    try:
        _ = d(a2)
        aktarilabilir = True
        aktarim_hatasi = _bagil(d(a2), u2)
    except ValueError:
        aktarilabilir = False
        aktarim_hatasi = float("inf")

    # dürüst kıyas: a2 duyu ızgarasına örneklenirse çıktı N=256'da alınabilir
    a2_duyu = a2[:, :: a2.shape[1] // 64]
    ornekli = _bagil(d(a2_duyu, N=256), u2)

    f = FourierIslemci(kip_sayisi=16)
    f.egit(a, u)
    fno_aktarim = _bagil(f(a2), u2)
    return {
        "ayni_cozunurluk_hatasi": ayni,
        "iyi_ogreniyor": bool(ayni < 0.02),
        "ham_aktarim_mumkun": aktarilabilir,
        "ham_aktarim_hatasi": aktarim_hatasi,
        "yeniden_ornekleyerek_hata": ornekli,
        "fno_ayni_iste_hatasi": fno_aktarim,
        # ÖLÇÜLDÜ: yeniden örnekledikten sonra ikisi de aynı hatayı verir.
        # "FNO daha doğru" diye bir iddia bu ölçümde DESTEKLENMEDİ; fark
        # doğrulukta değil, girdiyi olduğu gibi kabul edebilmektedir.
        "yeniden_ornekleyince_denk": bool(abs(ornekli - fno_aktarim) < 0.01),
        "fark_dogrulukta_degil_arayuzde": bool(
            (not aktarilabilir) and abs(ornekli - fno_aktarim) < 0.01
        ),
    }


def rapor() -> str:
    s = ["=== modern ==="]
    k = kan_sinamasi()
    s.append("KAN       en iyi: eğitim kalıntısı=%.4f  bağıl sınama=%.4f (iyi=%s)"
             % (k["en_iyi_egitim_kalintisi"], k["en_iyi_bagil_sinama_hatasi"],
                k["iyi_uyduruyor"]))
    s.append("          okunabilirlik: φ₁~sin(πx) hata=%.4f, φ₂~y² hata=%.4f → %s"
             % (k["phi1_sin_ile_uyum_hatasi"], k["phi2_kare_ile_uyum_hatasi"],
                k["kenarlar_okunabilir"]))
    s.append("          %d/%d başlangıç iyi havzaya düştü; kalıntılar=%s"
             % (k["basarili_restart_sayisi"], k["restart"], k["kalintilar"]))
    f = fno_sinamasi()
    s.append("FNO       N=64 hata=%.2e | N=256'ya aktarım=%.2e (çalışıyor=%s)"
             % (f["ayni_cozunurluk_hatasi"], f["farkli_cozunurluk_hatasi"],
                f["cozunurluk_aktarimi_calisiyor"]))
    s.append("          zaaf: görülmemiş yüksek kipte hata=%.4f (bozuluyor=%s)"
             % (f["yuksek_kip_hatasi"], f["yuksek_kipte_bozuluyor"]))
    d = deeponet_sinamasi()
    s.append("DeepONet  N=64 hata=%.2e (iyi=%s) | ham aktarım mümkün=%s"
             % (d["ayni_cozunurluk_hatasi"], d["iyi_ogreniyor"], d["ham_aktarim_mumkun"]))
    s.append("          yeniden örnekleyerek=%.2e  vs  FNO aynı işte=%.2e → denk=%s"
             % (d["yeniden_ornekleyerek_hata"], d["fno_ayni_iste_hatasi"],
                d["yeniden_ornekleyince_denk"]))
    s.append("          fark doğrulukta değil arayüzde=%s" % d["fark_dogrulukta_degil_arayuzde"])
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
