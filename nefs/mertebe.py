"""
Mertebe geçişi -- ``main/``ın icadının ana modele nakli (kütük H34'ün eşi).

`main/` ayrı bir modeldir (H32) ve öyle kalır: kübit, dalga, MERA, BEC
oraya aittir, buraya taşınmaz. Nakledilen şey **hesabın kendisi değil,
hükmüdür**:

    Bir hâl tek bir uzayda düşünülmez. Yirmi ayrı mertebede, her birinde
    o mertebeye mahsus bir operatörle döner ve esas uzaya geri mühürlenir.
    Mertebeler **toplanmaz** (H21); ayrı eksenlerde işler, bileşke
    **terkiptir**: ``S ← F₁₉ᵀ U₁₉ F₁₉ ⋯ F₀ᵀ U₀ F₀ S``.

Yirmi lif ``omega_kategori_nbe`` ile **fiilen kurulur** ve makine tip
denetiminden geçer -- ``idrak/kategori.py`` ile aynı usul, fakat oradan
ithal edilmez: iki model birbirine bağlanmaz, ikisi de aynı kategori
kütüphanesini çağırır. Bağlanan şey kütüphanedir, model değil.

**Mertebe nereye giriyor.** Uydurma bir etiket değildir; üç yerde
riyazî olarak iş görür ve üçü de ``kategori`` terimlerinden türer:

* ``pencere`` -- lifin dokunduğu eksen bloğunun genişliği (``m+1``, 4 ile
  sınırlı). Blok başlangıcı yuvaya göre kaydırılır: **ayrı eksenler**.
* ``adim``   -- lifin baktığı satır mesafesi ``1 + ⌊log₂(1+m)⌋``. Yüksek
  mertebe **uzak menzilli** tutarlılıktır; 1-morfizm komşuya, 1000-morfizm
  uzağa bakar.
* ``olcek``  -- dönmenin açısı ``1/(1+log(1+m))``. Yüksek mertebe daha
  küçük fakat daha geniş menzilli bir bükme yapar.

**Enine zırh** (H23) her lifte ayrı işler ve katman değildir:
``β₀ > 1`` ise mana ayrık adacıklara bölünmüş, yani ezberlenmiştir --
genlik cezalanır. Bir önceki life **dik** olup norm taşıyan bileşen
taşınamamıştır: **tıkanıklıktır** ve hükme girer.

Maliyet ``O(20·n·d²)``dir -- satır sayısında **doğrusal**. Kule (H34)
gerekmez, çünkü hiçbir yerde ``n×n`` kurulmaz.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import (TYPE_CHECKING, Dict, List, Optional, Sequence,
                    Tuple)

import numpy as np

from omega_kategori_nbe import kutuphane as L
from omega_kategori_nbe import sozdizim as S
from omega_kategori_nbe import turetimler as T
from omega_kategori_nbe.denetleyici import Baglam, denetle_t

# **``Parametreler`` yalnız TİP için lâzım (kütük H215).**
# ``mertebe_gecisi`` ``p.lie_tasarruf(...)`` çağırır; o usul yalnız
# klasik ``nefs/uzaylar.Parametreler``dedir (``QParametre``de YOKTUR --
# ölçüldü). Yani buradaki anotasyon, `nefs/qmeleke.py`dekinin aksine
# **doğrudur**. Fakat bağ çalışma anında lâzımdır, modül yüklenirken
# değil: modül seviyesinde tutulunca kuantum hattı (``qegitim`` yalnız
# ``DINAMIK``i, ``qmeleke`` yalnız ``lifleri_kur``u alır) bütün klasik
# dünyayı beraberinde sürüklüyordu.
if TYPE_CHECKING:                                    # pragma: no cover
    from .uzaylar import Parametreler

__all__ = ["Lif", "lifleri_kur", "mertebe_gecisi", "SABIT", "DINAMIK",
           "AZAMI_TAM_MERTEBE", "rapor"]

# ``morfizm_tipi(A, n)`` ağacı derindir; denetleyici özyinelemeli iner.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))

#: Sabit blok: ardışık ve değişmez zemin (kütük H22).
SABIT: Tuple[int, ...] = tuple(range(10))
#: Dinamik blok: ardışık DEĞİL; sonsuz spektrumdan seçilmiş keyfî on
#: mertebe. Aradaki mertebeler için hiçbir şey açılmaz -- seyrek Kan
#: sıçraması. Bu on sayı ana modelin sabitidir; değiştirmek serbesttir.
DINAMIK: Tuple[int, ...] = (13, 17, 19, 20, 30, 55, 1000, 1009, 58383, 60000)

#: Bu derinliğe kadar ``morfizm_tipi`` fiilen kurulup denetlenir; üstü
#: temsilci tiple denetlenir ve **öyle işaretlenir**. Sebep ölçüldü:
#: denetim süresi mertebeyle üssel büyür (n=20: 0,66 sn, n=22: 1,05 sn),
#: n=60 000 imkânsızdır.
AZAMI_TAM_MERTEBE = 20

_U = S.Evren(0)
_D = S.Deg


@dataclass(frozen=True)
class Lif:
    """Bir ∞-kategori mertebesi ve mananın orada göreceği geometri."""
    yuva: int              # 0..19
    mertebe: int
    tam_kuruldu: bool      # morfizm_tipi fiilen inşa edildi mi
    denetlendi: bool       # makine tip denetiminden geçti mi
    tip_ozeti: str
    hata: str = ""

    @property
    def pencere(self) -> int:
        """Lifin dokunduğu eksen bloğunun genişliği: ``m+1``, 4 ile sınırlı.

        Sınır zaruridir: ``m+1`` genişliğinde yerel bir kapı ``2^(m+1)``
        boyutlu bir dizey ister. Dördün üstündeki mertebe kaybolmaz,
        **adıma** taşınır (aşağıya bak).
        """
        return min(self.mertebe + 1, 4)

    @property
    def adim(self) -> int:
        """Lifin baktığı satır mesafesi -- logaritmik.

        Tabansız alınırsa 60 000 mertebe hiçbir satıra dokunmaz; zincir
        kopar. Logaritma, yüksek mertebeyi uzak fakat erişilebilir kılar.
        """
        return 1 + int(math.log2(1 + self.mertebe))

    @property
    def olcek(self) -> float:
        """Dönme açısı ``1/(1+log(1+m))``: yüksek mertebe daha az büker."""
        return 1.0 / (1.0 + math.log1p(float(self.mertebe)))


# =====================================================================
def _tam_kur(m: int) -> Tuple[object, str]:
    return T.morfizm_tipi(_D("A"), m), "morfizm_tipi(A, %d)" % m


def _temsilci_kur(m: int) -> Tuple[object, str]:
    """Yüksek mertebe için temsilci tip -- ``Ω^n(S¹)`` kulesinin bir katı.

    Bu bir taklit değil **kısıtlı bir şahittir**: aynı homotopi kulesinin
    bir katıdır, fakat ``m``inci katı değildir. Rapor bunu böyle söyler.
    """
    n = 1 + (m % AZAMI_TAM_MERTEBE)
    return (L.dongu_uzayi_n(S.Cember(), S.Taban(), n),
            "Ω^%d(S¹)  [mertebe %d için temsilci]" % (n, m))


@lru_cache(maxsize=4)
def lifleri_kur(dinamik: Tuple[int, ...] = DINAMIK) -> Tuple[Lif, ...]:
    """20 lifi kur ve **her birini makine ile tip denetiminden geçir**.

    Önbelleklidir: denetim ~2 saniye sürer ve akış her koşuda yeniden
    kurmamalıdır. Lifler donuk (``frozen``) olduğu için paylaşmak
    emniyetlidir.
    """
    if len(dinamik) != 10:
        raise ValueError("dinamik mertebe sayısı 10 olmalı (H22)")
    gA = Baglam.terimlerden({"A": _U, "a": _D("A"), "b": _D("A")})
    g0 = Baglam()

    lifler: List[Lif] = []
    for yuva, m in enumerate(tuple(SABIT) + tuple(int(x) for x in dinamik)):
        tam = m <= AZAMI_TAM_MERTEBE
        tip, ozet = _tam_kur(m) if tam else _temsilci_kur(m)
        baglam = gA if tam else g0
        hata = ""
        try:
            denetle_t(tip, _U, baglam)
            gecti = True
        except Exception as e:                       # noqa: BLE001
            gecti = False
            hata = "%s: %s" % (type(e).__name__, str(e)[:120])
        lifler.append(Lif(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                          denetlendi=gecti, tip_ozeti=ozet, hata=hata))
    return tuple(lifler)


# =====================================================================
def _betti0(v: np.ndarray, esik: float = 0.35) -> int:
    """Zincir üzerinde bağlantılı bileşen sayısı -- ``O(n)``.

    Zincirde çizge yalnız komşu kenarlardan ibarettir; bileşen sayısı,
    kopmuş komşuluk sayısının bir fazlasıdır. ``n×n`` bitişiklik dizeyi
    **hiç kurulmaz** -- 𝒪₅ Tecrit'te o dizey 65 536 düğümde 32 GiB
    istemişti; burada o hata tekrarlanmaz.
    """
    if len(v) < 2:
        return 1
    fark = np.abs(np.diff(v))
    olcek = float(np.median(fark)) + 1e-12
    return 1 + int(np.sum(fark > esik + 3.0 * olcek))


def mertebe_gecisi(S_giren: np.ndarray, p: "Parametreler",
                   dinamik: Tuple[int, ...] = DINAMIK
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """``S`` yirmi mertebeden geçip esas uzaya geri mühürlenir.

    Dönen: ``(S_yeni, tıkanıklık(20,), β₀(20,), büzülme)``.

    Terkip sıralıdır, toplam DEĞİLDİR (H21). Her lifte:

        S ← F_mᵀ · [zırh ∘ U_m ∘ uzak-menzil] · F_m · S

    ``F_m`` diktir (``lie_tasarruf``), dolayısıyla geri mühürleme
    kayıpsızdır; lifin bıraktığı tek iz, arada yapılan iştir.
    """
    A = np.asarray(S_giren, float)
    n, ds = A.shape
    lifler = lifleri_kur(tuple(dinamik))
    tikaniklik = np.zeros(len(lifler))
    betti = np.ones(len(lifler))
    onceki: Optional[np.ndarray] = None

    for lif in lifler:
        # --- F_m: life fırlatım (dik, dolayısıyla norm koruyan)
        F = p.lie_tasarruf("mertebe.F%d" % lif.yuva, ds, teta=0.25)
        B = A @ F.T

        # --- lifin dokunduğu eksen bloğu: AYRI EKSENLER (H21)
        k = min(2 ** lif.pencere, ds)
        bas = (lif.yuva * k) % ds
        sec = (bas + np.arange(k)) % ds
        blok = B[:, sec]

        # --- uzak menzilli tutarlılık: mertebe ne kadar yüksekse o kadar
        #     uzak satıra bakılır. ``roll`` ``O(n·k)``dir.
        adim = min(lif.adim, max(n - 1, 1))
        if n > 1:
            blok = blok + 0.15 * lif.olcek * (np.roll(blok, adim, axis=0) - blok)

        # --- U_m: mertebeye mahsus dönme; açı mertebeden gelir
        Um = p.lie_tasarruf("mertebe.U%d" % lif.yuva, k, teta=lif.olcek)
        blok = blok @ Um.T

        # --- enine zırh (H23), bu lifte ve yalnız bu lifte
        okuma = blok.mean(0)
        b0 = _betti0(okuma)
        betti[lif.yuva] = float(b0)
        ceza = float(np.exp(-0.25 * (b0 - 1) ** 2))
        blok = blok * ceza                      # ezber cezası

        if onceki is not None and len(onceki) == len(okuma):
            o = onceki / (float(np.linalg.norm(onceki)) + 1e-12)
            paralel = o * float(o @ okuma)
            dik = okuma - paralel
            nt = float(np.linalg.norm(okuma)) + 1e-12
            tik = float(np.linalg.norm(dik)) / nt
            tikaniklik[lif.yuva] = tik
            if tik > 0.9:
                # taşınamayan bileşen: yalnız onda biri geçsin
                blok = blok - 0.9 * (blok - blok @ np.outer(o, o))
        onceki = okuma

        B[:, sec] = blok
        # --- F_mᵀ: esas uzaya geri mühürleme
        A = B @ F

    # Yirmi lif boyunca genlik büzülür: uzak menzilli ortalama ve Betti
    # cezası ikisi de söndürücüdür (ölçüldü: 20 lif sonunda norm oranı
    # ≈ 0,52). Ölçek burada geri verilir, çünkü mertebe geçişinin işi
    # mananın YÖNÜNÜ bükmektir, şiddetini kısmak değil; kısılsaydı
    # 𝒪₂₁'den sonraki bütün melekeler sönmüş bir ``S`` görürdü. Büzülme
    # silinmez, ``mertebe.büzülme`` diye rapor edilir.
    n_giren = float(np.linalg.norm(S_giren))
    n_cikan = float(np.linalg.norm(A))
    buzulme = n_cikan / max(n_giren, 1e-12)
    if n_cikan > 1e-12 and n_giren > 1e-12:
        A = A * (n_giren / n_cikan)
    return A, tikaniklik, betti, buzulme


# =====================================================================
def rapor(dinamik: Tuple[int, ...] = DINAMIK, n: int = 24,
          ds: int = 16, tohum: int = 0) -> str:
    """20 lifin kuruluşu, denetimi ve bir geçişin ölçümü."""
    lifler = lifleri_kur(tuple(dinamik))
    s = ["=== MERTEBE GEÇİŞİ (ana model, omega_kategori_nbe ile) ===", "",
         "%-5s %-8s %-9s %-9s %-8s %-6s %s"
         % ("yuva", "mertebe", "kuruluş", "denetim", "pencere", "adım",
            "ölçek")]
    s.append("-" * 72)
    for u in lifler:
        s.append("%-5d %-8d %-9s %-9s %-8d %-6d %.4f   %s"
                 % (u.yuva, u.mertebe, "TAM" if u.tam_kuruldu else "temsilci",
                    "geçti" if u.denetlendi else "KALDI",
                    u.pencere, u.adim, u.olcek, u.tip_ozeti))
        if u.hata:
            s.append("      ! " + u.hata)

    rng = np.random.default_rng(tohum)
    A = rng.normal(size=(n, ds))
    from .uzaylar import Parametreler
    p = Parametreler(tohum)
    B, tik, b0, buz = mertebe_gecisi(A, p, tuple(dinamik))
    s += ["",
          "geçiş: ‖S‖ %.4f → %.4f   (ölçek geri verilmeden büzülme %.4f)"
          % (np.linalg.norm(A), np.linalg.norm(B), buz),
          "yön değişimi: kosinüs %.4f"
          % float(np.sum(A * B) / max(np.linalg.norm(A) * np.linalg.norm(B),
                                      1e-12)),
          "tıkanıklık: ort %.4f  âzamî %.4f (yuva %d)"
          % (tik.mean(), tik.max(), int(np.argmax(tik))),
          "β₀: ort %.2f  âzamî %d  (β₀>1 olan lif sayısı: %d)"
          % (b0.mean(), int(b0.max()), int(np.sum(b0 > 1)))]
    tam = sum(1 for u in lifler if u.tam_kuruldu)
    ok = sum(1 for u in lifler if u.denetlendi)
    s += ["",
          "hulâsa: %d/20 lif TAM kuruldu, %d/20 makine denetiminden geçti."
          % (tam, ok)]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
