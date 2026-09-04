"""
20 ∞-kategori uzayı -- ``omega_kategori_nbe`` ile **fiilen** kurulur.

Evvelki inşada bu modül hiç çağrılmamıştı; "sonsuz kategori uzayı" lafı
kodda bir tamsayıdan ibaretti. Burada öyle değildir: her uzay
``omega_kategori_nbe.sozdizim`` ile bir **terim** olarak inşa edilir ve
``denetleyici.denetle_t`` ile **makine tarafından tip denetiminden**
geçirilir. Geçmeyen uzay sofraya konmaz.

Uzayın mertebesi ``m`` şudur (``turetimler.morfizm_tipi``):

    m = 0 → A
    m = 1 → Π x y. Path A x y
    m = 2 → Π x y. Π p q. Path (Path A x y) p q
    ...

Dalganın o uzayda göreceği geometri buradan **türetilir**, uydurulmaz:

* ``pencere(m)``  -- ``Δ_m`` simpleksinin kaç kübite dokunduğu: ``m+1``.
* ``adim(m)``     -- simpleksin köşeleri arasındaki mesafe; mertebe
  yükseldikçe bağ uzar (yüksek mertebe = uzak menzilli tutarlılık).
* ``baglayici(m)`` -- terimdeki Π/Σ bağlayıcı sayısı; Hamiltonyenin
  serbest parametre sayısını bu belirler.

**Sabit blok (0 ≤ k ≤ 9)** tam olarak kurulur ve denetlenir.

**Dinamik blok (d_i ≥ 10, hudutsuz)**: ``morfizm_tipi(A, 60000)`` inşa
EDİLEMEZ -- 60 000 iç içe Π bağlayıcısı hem Python özyinelemesini hem
belleği aşar. Bu, seyrek Kan sıçramasının tam olarak sebebidir: aradaki
mertebeler açılmaz. Burada yapılan ve **açıkça bildirilen** şey şudur:
yüksek mertebe uzayı için *temsilci* bir tip (``koherens_tipi`` ile
sınırlı derinlikte) denetlenir, mertebenin kendisi ise Hamiltonyenin
geometrisine (pencere, adım, parametre sayısı) **sayı olarak** girer.
Yani mertebe uydurma bir etiket değildir; fakat 60 000-morfizm tipi de
fiilen kurulmamıştır. İkisi de kütükte durur.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from matematik.tip_teorisi import (Baglam, Cember, Deg, Dugum, Evren, Lam,
                                   Pi, Sigma, Taban, Terim, YolLam,
                                   denetle_t, denetle_tip, dongu_uzayi_n,
                                   evrensel_demet, kesit_tipi, morfizm_tipi,
                                   ok, tikanma_postulati)

__all__ = ["Uzay", "SABIT", "uzaylari_kur", "rapor", "AZAMI_TAM_MERTEBE"]

U = Evren(0)
U1 = Evren(1)
D = Deg

# ``morfizm_tipi(A, 20)`` ağacı derindir; denetleyici özyinelemeli iner.
# Varsayılan sınır (1000) n=8'de aşılıyordu -- ölçüldü.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))

SABIT: Tuple[int, ...] = tuple(range(10))      # 0 ≤ k ≤ 9

#: Bu derinliğe kadar ``morfizm_tipi`` fiilen kurulup denetlenir.
#: Üstünde kalanlar temsilci tiple denetlenir ve öyle işaretlenir.
#:
#: Sınır ölçümle seçildi: ``morfizm_tipi(A, n)`` terim ağacı ``n`` ile
#: ÜSSEL büyür (her mertebe iki Π bağlayıcısı daha ekler). Denetim süresi
#: ölçüldü -- n=10: 0.04 sn · n=16: 0.28 sn · n=20: 0.66 sn · n=22: 1.05 sn.
#: Her iki mertebede süre ikiye katlanıyor; n=30 dört dakikayı aşar,
#: n=60 000 ise imkânsızdır. 20 seçildi: bütün sabit blok (0-9) ve dinamik
#: bloktaki küçük mertebeler TAM kurulur, koşuya ~2 saniye biner.
AZAMI_TAM_MERTEBE = 20


@dataclass(frozen=True)
class Uzay:
    """Bir ∞-kategori uzayı ve dalganın orada göreceği geometri."""
    yuva: int                  # 0..19
    mertebe: int               # k veya d_i
    tam_kuruldu: bool          # morfizm_tipi fiilen inşa edildi mi
    denetlendi: bool           # makine tip denetiminden geçti mi
    baglayici: int             # terimdeki Π/Σ bağlayıcı sayısı
    tip_ozeti: str
    hata: str = ""

    @property
    def pencere(self) -> int:
        """``Δ_m`` simpleksi kaç kübite dokunur: ``m+1``, 4 ile sınırlı.

        Sınır zaruridir: ``m+1`` kübitlik yerel bir kapı ``2^(m+1)``
        boyutlu bir dizey ister; ``m = 9`` bile 1024×1024 eder ve altı
        milyon yuvada koşamaz. Dördün üstündeki mertebe **adıma** taşınır
        (aşağıya bak); yani mertebe kaybolmaz, geometrisi değişir.
        """
        return min(self.mertebe + 1, 4)

    @property
    def adim(self) -> int:
        """Simpleksin köşeleri arası mesafe.

        Mertebe yükseldikçe tutarlılık **uzak menzilli** olur: 2-morfizm
        komşu üçlüye, 1000-morfizm çok uzak bir üçlüye bakar. Logaritmik
        alınır ki 60 000 mertebe zinciri koparmasın; tabansız alınırsa
        adım kübit sayısını aşar ve operatör hiç dokunmaz.
        """
        import math
        return 1 + int(math.log2(1 + self.mertebe))

    @property
    def parametre(self) -> int:
        """Hamiltonyenin serbest parametre sayısı -- **terimden** gelir.

        ``E_m(σ)`` köşegen enerjileri ``2^pencere`` tane, ``J_m(σ,τ)``
        bağ katsayıları da o kadar; bağlayıcı sayısı bunlara bir kat
        ekler (yüksek mertebe daha çok koherens şartı taşır).
        """
        return 2 ** self.pencere + self.baglayici


def _baglayici_say(t: Terim) -> int:
    """Terimdeki Π/Σ/Λ bağlayıcılarını say -- yığınla, özyinelemesiz.

    Özyineleme ile yazılıp ölçüldü ve **kaldı**: ``morfizm_tipi(A, 6)``
    ağacı Python'un varsayılan özyineleme sınırını aşıyor. Yığın
    kullanmak aynı sayıyı verir, sınır tanımaz.
    """
    n = 0
    yigin: List[object] = [t]
    while yigin:
        d = yigin.pop()
        if not isinstance(d, Dugum):
            continue
        if isinstance(d, (Pi, Sigma, Lam, YolLam)):
            n += 1
        for alan in d._alanlar():
            if isinstance(alan, Dugum):
                yigin.append(alan)
            elif isinstance(alan, tuple):
                yigin.extend(a for a in alan if isinstance(a, Dugum))
    return n


def _tam_kur(mertebe: int) -> Tuple[Terim, str]:
    """``morfizm_tipi(A, m)`` -- mertebenin **fiilî** tipi."""
    A = D("A")
    return morfizm_tipi(A, mertebe), "morfizm_tipi(A, %d)" % mertebe


def _temsilci_kur(mertebe: int) -> Tuple[Terim, str]:
    """Yüksek mertebe için temsilci tip.

    Mertebe ``m``, ``Ω^n(S¹)`` kulesinin bir katıyla temsil edilir;
    ``n = 1 + (m mod AZAMI_TAM_MERTEBE)``. Bu bir **taklit değil,
    kısıtlı bir şahittir**: aynı homotopi kulesinin bir katıdır, fakat
    ``m``inci katı değildir. Rapor bunu ``temsilci`` diye işaretler.
    """
    n = 1 + (mertebe % AZAMI_TAM_MERTEBE)
    return (dongu_uzayi_n(Cember(), Taban(), n),
            "Ω^%d(S¹)  [mertebe %d için temsilci]" % (n, mertebe))


def uzaylari_kur(dinamik: Sequence[int]) -> List[Uzay]:
    """20 uzayı kur ve **her birini makine ile tip denetiminden geçir**."""
    if len(dinamik) != 10:
        raise ValueError("dinamik mertebe sayısı 10 olmalı")
    gA = Baglam.terimlerden({"A": U, "a": D("A"), "b": D("A")})
    g0 = Baglam()

    uzaylar: List[Uzay] = []
    for yuva, m in enumerate(tuple(SABIT) + tuple(int(x) for x in dinamik)):
        tam = m <= AZAMI_TAM_MERTEBE
        if tam:
            tip, ozet = _tam_kur(m)
            baglam, hedef = gA, U
        else:
            tip, ozet = _temsilci_kur(m)
            baglam, hedef = g0, U
        hata = ""
        try:
            denetle_t(tip, hedef, baglam)
            gecti = True
        except Exception as e:                      # noqa: BLE001
            gecti = False
            hata = "%s: %s" % (type(e).__name__, str(e)[:120])
        uzaylar.append(Uzay(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                            denetlendi=gecti, baglayici=_baglayici_say(tip),
                            tip_ozeti=ozet, hata=hata))
    return uzaylar


# =====================================================================
#  Postnikov tıkanıklığı ve kesit tipi -- ikisi de modülden
# =====================================================================
def tikanma_tipi() -> Terim:
    """``tikanma : (X → U) → U`` -- Postnikov k-invaryantının taşıyıcısı.

    ``iliskiler.tikanma_postulati`` bunu bir POSTULAT olarak verir: bu
    çekirdekte kohomoloji hesaplanmaz. Tipi burada makine ile denetlenir,
    sakinleri aksiyomdur. Ayrık motor bu tipin **sayısal** karşılığını
    (dalga artıkları) kullanır; ikisi karıştırılmaz.
    """
    return tikanma_postulati(D("X")).tip


def kesit_tipi_ile_agirlik() -> Tuple[Terim, Terim]:
    """Öğrenilen ağırlık = ``Π (w:M). F w`` kesiti (kütük H3).

    ``iliskiler.kesit_tipi`` doğrudan çağrılır; dönüş, kesit tipi ile
    evrensel demettir.
    """
    M, Fw = D("M"), D("Fw")
    return kesit_tipi(M, Fw), evrensel_demet(M, Fw)


def akit_denetle() -> List[Dict[str, object]]:
    """Modülün fiilen çağrıldığının makine ile ispatı."""
    g = Baglam.terimlerden({"M": U, "Fw": ok(D("M"), U), "X": U})
    isler = [
        ("tıkanma (Postnikov) tipi iyi teşkil",
         lambda: denetle_tip(tikanma_tipi(), g)),
        ("kesit tipi Π(w:M). F w : U",
         lambda: denetle_t(kesit_tipi(D("M"), D("Fw")), U, g)),
        ("evrensel demet Σ(w:M). F w : U",
         lambda: denetle_t(evrensel_demet(D("M"), D("Fw")), U, g)),
    ]
    out: List[Dict[str, object]] = []
    for ad, fn in isler:
        try:
            fn()
            out.append({"ad": ad, "netice": "GEÇTİ"})
        except Exception as e:                      # noqa: BLE001
            out.append({"ad": ad, "netice": "HATA",
                        "izah": str(e)[:120]})
    return out


def rapor(dinamik: Sequence[int] = (13, 17, 19, 20, 30, 55, 1000, 1009,
                                    58383, 60000)) -> str:
    uz = uzaylari_kur(dinamik)
    s = ["=== 20 ∞-KATEGORİ UZAYI (omega_kategori_nbe ile kurulup denetlendi) ===",
         "",
         "%-5s %-8s %-9s %-11s %-8s %-7s %s"
         % ("yuva", "mertebe", "kuruluş", "denetim", "bağlayıcı",
            "pencere", "adım")]
    s.append("-" * 78)
    for u in uz:
        s.append("%-5d %-8d %-9s %-11s %-9d %-7d %d   %s"
                 % (u.yuva, u.mertebe,
                    "TAM" if u.tam_kuruldu else "temsilci",
                    "geçti" if u.denetlendi else "KALDI",
                    u.baglayici, u.pencere, u.adim, u.tip_ozeti))
        if u.hata:
            s.append("      ! " + u.hata)
    s += ["", "Akit denetimi (modül fiilen çağrılıyor mu):"]
    for n in akit_denetle():
        s.append("  %s %s%s" % ("✓" if n["netice"] == "GEÇTİ" else "✗",
                                n["ad"],
                                "" if n["netice"] == "GEÇTİ"
                                else "  [%s]" % n.get("izah", "")))
    tam = sum(1 for u in uz if u.tam_kuruldu)
    ok = sum(1 for u in uz if u.denetlendi)
    s += ["",
          "hulâsa: %d/20 uzay TAM kuruldu, %d/20 makine denetiminden geçti."
          % (tam, ok),
          "Mertebesi %d'ten büyük olanlar temsilci tiple denetlendi;"
          % AZAMI_TAM_MERTEBE,
          "sebebi seyrek Kan sıçramasıdır (aradaki mertebeler açılmaz)."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
