"""
Kara kutu eniyilemenin sınırları.

İki ayrı imkânsızlık var ve bunları karıştırmamak gerekir:

  1) **No Free Lunch** (Wolpert--Macready 1997). SONLU bir arama uzayında,
     BÜTÜN hedef fonksiyonlar üzerinde ortalama alındığında her arama
     usulü aynıdır. Bu bir "eniyileme zordur" iddiası değildir; "hedef
     sınıfı hakkında hiçbir kabul yapmazsan usul seçmenin ANLAMI yoktur"
     iddiasıdır. Yani bütün kazanç, hedef hakkındaki ön kabullerden gelir.

  2) **Nemirovski--Yudin / Nesterov alt sınırı**. Hedef sınıfı hakkında
     kuvvetli kabullerin (pürüzsüz, dışbükey) OLDUĞU hâlde bile, yalnız
     birinci mertebe bilgiye (f ve ∇f) bakan usuller belli bir hızdan
     daha hızlı olamaz. Bu, NFL'in aksine, bir "bilgi türü" sınırıdır:
     usul akıllı olsa dahi göremediği yer vardır.

Bu modüldeki iddiaların hepsi ya tam sayım ya da yapısal özdeşlikle
DOĞRULANIR; hiçbiri "genelde böyledir" diye bırakılmaz.
"""
from __future__ import annotations

from itertools import permutations, product
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np


# =====================================================================
#  1. No Free Lunch -- tam sayımla
# =====================================================================
def _iz(
    sira: Sequence[int],
    f: Sequence[int],
) -> Tuple[int, ...]:
    """``sira`` düzeninde noktaları gezen usulün gördüğü değerler dizisi."""
    return tuple(f[x] for x in sira)


def nfl_tam_sayim(m: int = 3, n: int = 3) -> Dict[str, object]:
    """``m`` noktalı uzay, ``n`` değerli kodalan; BÜTÜN ``n**m`` fonksiyon.

    Tekrarsız (non-repeating) belirlenimci (deterministic) bir arama
    usulü, burada noktaların bir sıralamasıdır. İddia: bütün fonksiyonlar
    üzerinde ortalama alındığında, gözlenen değer dizilerinin ÇOKLU
    KÜMESİ her sıralama için aynıdır.

    Bu, tam sayımla sınanır -- yaklaşık değil, kesin.
    """
    noktalar = list(range(m))
    fonksiyonlar = list(product(range(n), repeat=m))
    dagilimlar: Dict[Tuple[int, ...], Dict[Tuple[int, ...], int]] = {}
    for sira in permutations(noktalar):
        sayac: Dict[Tuple[int, ...], int] = {}
        for f in fonksiyonlar:
            iz = _iz(sira, f)
            sayac[iz] = sayac.get(iz, 0) + 1
        dagilimlar[sira] = sayac

    ilk = next(iter(dagilimlar.values()))
    hepsi_ayni = all(d == ilk for d in dagilimlar.values())

    # ortalama "en iyi bulunan" değer de aynı olmalı (asgarî arıyoruz)
    ortalama_en_iyi = {
        sira: float(np.mean([min(_iz(sira, f)) for f in fonksiyonlar]))
        for sira in dagilimlar
    }
    return {
        "nokta": m,
        "deger": n,
        "fonksiyon_sayisi": len(fonksiyonlar),
        "usul_sayisi": len(dagilimlar),
        "iz_dagilimlari_ayni": hepsi_ayni,
        "ortalama_en_iyi": ortalama_en_iyi,
        "ortalamalar_ayni": len(set(round(v, 12) for v in ortalama_en_iyi.values())) == 1,
    }


def nfl_kacamagi(m: int = 64) -> Dict[str, object]:
    """NFL'in NEREDE geçersizleştiği: hedef sınıfı daraltıldığında.

    Bütün fonksiyonlar yerine yalnız **tek tepeli** (unimodal) olanları
    alırsak, ikili arama benzeri bir usul rastgele aramayı kesin olarak
    yener. Yani NFL bir yasak değil, bir muhasebedir: kazanç ön kabulden
    gelir ve ön kabul daraldıkça kazanç görünür olur.
    """
    # tek tepeli: v biçimli diziler (kesin azalıp sonra kesin artan)
    tekil: List[Tuple[int, ...]] = []
    for dip in range(m):
        f = tuple(abs(x - dip) for x in range(m))
        tekil.append(f)

    def rastgele_arama(f: Sequence[int], butce: int, rng: np.random.Generator) -> int:
        idx = rng.permutation(len(f))[:butce]
        return int(min(f[i] for i in idx))

    def ucdurum_arama(f: Sequence[int], butce: int) -> int:
        """Tek tepeli dizide üçlü bölme (ternary search)."""
        lo, hi = 0, len(f) - 1
        gorulen = [f[lo], f[hi]]
        kalan = butce - 2
        while kalan >= 2 and hi - lo >= 2:
            a = lo + (hi - lo) // 3
            b = hi - (hi - lo) // 3
            if a == b:
                b = min(a + 1, hi)
            gorulen += [f[a], f[b]]
            kalan -= 2
            if f[a] <= f[b]:
                hi = b
            else:
                lo = a
        return int(min(gorulen))

    rng = np.random.default_rng(0)
    butce = 12
    r_top = np.mean([rastgele_arama(f, butce, rng) for f in tekil for _ in range(20)])
    u_top = np.mean([ucdurum_arama(f, butce) for f in tekil])
    return {
        "sinif": "tek tepeli",
        "nokta": m,
        "butce": butce,
        "rastgele_ortalama": float(r_top),
        "ucdurum_ortalama": float(u_top),
        "yapili_usul_daha_iyi": bool(u_top < r_top),
    }


# =====================================================================
#  2. Nemirovski--Yudin: sıfır zinciri (zero-chain) yapısı
# =====================================================================
class NesterovEnKotu:
    """Nesterov'un en kötü pürüzsüz dışbükey fonksiyonu.

    ``f(x) = (L/8)·[ x₁² + Σ_{i<k}(xᵢ − x_{i+1})² + x_k² − 2x₁ ]``

    Bu fonksiyonun **sıfır zinciri** hususiyeti vardır: ``x``in yalnız ilk
    ``j`` bileşeni sıfırdan farklıysa ``∇f(x)``in de yalnız ilk ``j+1``
    bileşeni sıfırdan farklıdır. Dolayısıyla 0'dan başlayan ve iterasyonu
    geçmiş gradyanların gerdiği uzayda tutan HER birinci mertebe usul,
    ``k`` adımda çözümün ancak ilk ``k`` koordinatına dokunabilir.

    Alt sınır buradan çıkar: usul akıllı olsun olmasın, göremediği
    koordinatlar vardır.
    """

    def __init__(self, k: int, L: float = 1.0, boyut: int | None = None) -> None:
        self.k = k
        self.L = L
        self.n = boyut if boyut is not None else 2 * k + 1

    def deger(self, x: np.ndarray) -> float:
        k = self.k
        s = x[0] ** 2 + float(np.sum((x[: k - 1] - x[1:k]) ** 2)) + x[k - 1] ** 2
        return self.L / 8.0 * (s - 2.0 * x[0])

    def gradyan(self, x: np.ndarray) -> np.ndarray:
        k = self.k
        g = np.zeros_like(x)
        A = np.zeros((k, k))
        for i in range(k):
            A[i, i] = 2.0
            if i + 1 < k:
                A[i, i + 1] = -1.0
                A[i + 1, i] = -1.0
        e1 = np.zeros(k)
        e1[0] = 1.0
        g[:k] = self.L / 8.0 * (2.0 * A @ x[:k] - 2.0 * e1)
        return g

    def en_iyi(self) -> Tuple[np.ndarray, float]:
        """``A x = e₁`` çözümü: ``x*ᵢ = 1 − i/(k+1)``."""
        k = self.k
        x = np.zeros(self.n)
        x[:k] = np.array([1.0 - (i + 1) / (k + 1) for i in range(k)])
        return x, self.deger(x)


def sifir_zinciri_sinamasi(k: int = 8, adim: int = 5) -> Dict[str, object]:
    """Gradyan inişinin sıfırdan başlayarak destek genişlemesini ölçer.

    ``t`` adım sonra desteğin en fazla ``t`` koordinat olması **yapısal**
    bir olgudur; usul ne kadar iyi ayarlanırsa ayarlansın değişmez.
    """
    f = NesterovEnKotu(k=k)
    x = np.zeros(f.n)
    h = 1.0 / (f.L)  # adım boyu; hangi değer olursa olsun destek aynı
    destekler = []
    for t in range(adim):
        x = x - h * f.gradyan(x)
        destekler.append(int(np.count_nonzero(np.abs(x) > 1e-15)))
    _, fmin = f.en_iyi()
    return {
        "k": k,
        "destek_dizisi": destekler,
        "destek_adimla_sinirli": all(d <= t + 1 for t, d in enumerate(destekler)),
        "f_son": f.deger(x),
        "f_en_iyi": fmin,
        "bosluk": f.deger(x) - fmin,
    }


def alt_sinir_ihlal_var_mi(azami_adim: int = 8) -> Dict[str, object]:
    """Nesterov alt sınırı (Teorem 2.1.7): ``t`` adım için ``k = 2t+1``.

    ``f(x_t) − f* ≥ 3L‖x₀−x*‖² / (32(t+1)²)``.

    Sınırın *hangi* fonksiyonda geçerli olduğu mühimdir: her ``t`` için
    en kötü fonksiyon AYRIDIR (``k = 2t+1``). Sabit bir ``k`` alıp ``t``yi
    küçük tutarsan sınır kırılmış görünür -- bu, usulün hızlı olduğunu
    değil, iddianın yanlış kurulduğunu gösterir. (Bu tuzağa bu dosyayı
    yazarken bizzat düşüldü ve ölçüm düzeltti.)

    Burada birkaç birinci mertebe usul koşturulur ve hiçbirinin sınırı
    kırmadığı doğrulanır.
    """
    kayitlar: List[Tuple[str, int, float, float]] = []
    for t in range(1, azami_adim + 1):
        k = 2 * t + 1
        f = NesterovEnKotu(k=k)
        xs, fmin = f.en_iyi()
        R2 = float(np.sum(xs ** 2))
        sinir = 3.0 * f.L * R2 / (32.0 * (t + 1) ** 2)

        # (a) sabit adımlı gradyan inişi, t adım
        x = np.zeros(f.n)
        for _ in range(t):
            x = x - (1.0 / f.L) * f.gradyan(x)
        kayitlar.append(("gradyan", t, f.deger(x) - fmin, sinir))

        # (b) Nesterov hızlandırması, t adım
        x = np.zeros(f.n)
        y = x.copy()
        lam = 0.0
        for _ in range(t):
            lam_yeni = (1 + np.sqrt(1 + 4 * lam * lam)) / 2
            gamma = (1 - lam) / lam_yeni
            x_yeni = y - (1.0 / f.L) * f.gradyan(y)
            y = (1 - gamma) * x_yeni + gamma * x
            x, lam = x_yeni, lam_yeni
        kayitlar.append(("hizlandirilmis", t, f.deger(x) - fmin, sinir))

    ihlaller = [r for r in kayitlar if r[2] < r[3] - 1e-12]
    return {
        "azami_adim": azami_adim,
        "kayit_sayisi": len(kayitlar),
        "kayitlar": kayitlar,
        "ihlal": ihlaller,
        "ihlal_yok": not ihlaller,
    }


def rapor() -> str:
    satirlar = ["=== kara_kutu ==="]
    a = nfl_tam_sayim(3, 3)
    satirlar.append(
        "NFL tam sayım  m=%d n=%d  fonksiyon=%d usul=%d  izler aynı=%s  ortalamalar aynı=%s"
        % (a["nokta"], a["deger"], a["fonksiyon_sayisi"], a["usul_sayisi"],
           a["iz_dagilimlari_ayni"], a["ortalamalar_ayni"])
    )
    b = nfl_kacamagi()
    satirlar.append(
        "NFL kaçamağı   tek tepeli sınıfta  rastgele=%.3f  üçdurum=%.3f  yapılı iyi=%s"
        % (b["rastgele_ortalama"], b["ucdurum_ortalama"], b["yapili_usul_daha_iyi"])
    )
    c = sifir_zinciri_sinamasi()
    satirlar.append(
        "Sıfır zinciri  destek=%s  adımla sınırlı=%s"
        % (c["destek_dizisi"], c["destek_adimla_sinirli"])
    )
    d = alt_sinir_ihlal_var_mi()
    satirlar.append("Nesterov alt sınırı  ihlal yok=%s" % d["ihlal_yok"])
    return "\n".join(satirlar)


if __name__ == "__main__":
    print(rapor())
