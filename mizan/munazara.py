"""Münâzara — âdâbü'l-bahs kaideleri ve yakîn derecesinin hesabı.

Klasik cedel usulünde bir *müddeî* (dâvâ sahibi) ile *muteriz* (îtiraz
eden) arasındaki alışverişin izin verilen hamleleri sayılıdır.  Bu modül
o hamleleri bir **oyun** olarak kurar; her hamlenin meşru olup olmadığını
ve dâvânın hangi hâlde sâkıt olduğunu hesaplar.

Üç îtiraz nev'i:

* **men'** (منع) — bir öncülün *doğruluğunu* men etmek.  Muteriz burhan
  getirmez, sadece "bunu kabul etmiyorum" der; ispat yükü müddeîdedir.
* **nakz** (نقض) — aynı delili, aynı sûrette, neticesi *bâtıl* olan bir
  yerde işletip delilin küllî olmadığını göstermek (karşı-örnek).
* **muâraza** (معارضة) — dâvânın *aksini* ispat eden müstakil bir delil
  getirmek.  Bu, îtiraz değil karşı-dâvâdır; muteriz ispat yükünü üstlenir.

Ayrıca **Gazâlî mîzânı**: bir kıyasın neticesinin yakîni,

.. math::

   \\mathrm{Yak\\hat{i}n}(Q) = \\Bigl(\\min_i \\mathrm{Yak\\hat{i}n}(P_i)\\Bigr)
                              \\cdot \\mathbb{1}[\\text{şekil geçerli}]

Yani netice **en zayıf öncülden** kuvvetli olamaz (zincir en zayıf
halkası kadardır) ve şekil bozuksa yakîn sıfırdır — geçersiz şekil
öncüllerin kuvvetinden hiçbir şey taşımaz.  Çarpım değil *minimum*
alınması kasıtlıdır: bu Gödel t-normudur ve idempotenttir; aynı öncülü
iki kere saymak neticeyi zayıflatmaz.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .kiyas import DARB_ADI, gecerli_mi as kiyas_gecerli_mi
from .onerme import Onerme, deg, degil, gecerli_mi, karsi_ornek

__all__ = [
    "yakin_gazali", "yakin_zinciri", "MERTEBELER", "mertebe_adi",
    "ItirazNevi", "Hamle", "Munazara",
    "men_mesru_mu", "nakz_gecerli_mi", "muaraza_gecerli_mi",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Gazâlî mîzânı — yakîn derecesi
# ══════════════════════════════════════════════════════════════════════

#: Klasik bilgi mertebeleri; eşikler alt sınırdır (dâhil).
MERTEBELER: Tuple[Tuple[float, str], ...] = (
    (1.00, "yakîn"),        # kat'î — aksi muhal
    (0.75, "zann-ı gālib"),  # kuvvetli zan
    (0.50, "zan"),
    (0.25, "şek"),           # iki taraf müsâvî veya altı
    (0.00, "vehim"),         # mercûh taraf
)


def mertebe_adi(y: float) -> str:
    """Yakîn derecesine karşılık gelen klasik mertebe adı."""
    if not 0.0 <= y <= 1.0:
        raise ValueError("yakîn ∈ [0,1] olmalı")
    for esik, ad in MERTEBELER:
        if y >= esik:
            return ad
    return "vehim"


def yakin_gazali(oncul_yakinleri: Sequence[float],
                 sekil_gecerli: bool) -> float:
    """``min_i Yakîn(P_i) · 𝟙[şekil geçerli]``.

    Öncül yoksa (boş liste) netice öncülsüz iddiadır: yakîn 0.  Bu,
    ``min(∅)=+∞`` matematiksel kabulünden kasten ayrılır — burada mîzân
    delil tartar, delilsizlik en yüksek derece olamaz.
    """
    if not sekil_gecerli:
        return 0.0
    if not oncul_yakinleri:
        return 0.0
    for y in oncul_yakinleri:
        if not 0.0 <= y <= 1.0:
            raise ValueError("her yakîn ∈ [0,1] olmalı")
    return min(oncul_yakinleri)


def yakin_zinciri(halkalar: Sequence[Tuple[Sequence[float], bool]]) -> float:
    """Sorites/zincirleme kıyasta yakînin seyri.

    Her halka bir kıyastır; bir öncekinin neticesi sonrakinin öncülüdür.
    Minimum idempotent olduğundan zincir uzunluğu **tek başına** yakîni
    düşürmez — düşüren, araya giren zayıf öncüllerdir.  (Çarpım t-normu
    seçilseydi zincir uzadıkça yakîn kaçınılmaz olarak sıfıra giderdi;
    bu, kat'î öncüllerden kurulu uzun bir ispatı da değersizleştirirdi.)
    """
    tasinan = 1.0
    for onculler, gecerli in halkalar:
        tasinan = yakin_gazali(list(onculler) + [tasinan], gecerli)
        if tasinan == 0.0:
            return 0.0
    return tasinan


# ══════════════════════════════════════════════════════════════════════
#  2. Münâzara oyunu
# ══════════════════════════════════════════════════════════════════════

class ItirazNevi(Enum):
    MEN = "men'"
    NAKZ = "nakz"
    MUARAZA = "muâraza"


@dataclass(frozen=True)
class Hamle:
    """Bir münâzara hamlesi.

    ``sahip``: "müddeî" veya "muteriz".
    ``nevi``: îtiraz nev'i (müddeî hamlelerinde ``None``).
    ``hedef``: men'/nakz edilen öncülün sırası (men' ve nakz için şart).
    ``delil``: muâraza veya ispat için getirilen öncüller.
    """
    sahip: str
    nevi: Optional[ItirazNevi]
    hedef: Optional[int] = None
    delil: Tuple[Onerme, ...] = ()
    netice: Optional[Onerme] = None
    aciklama: str = ""


def men_mesru_mu(hedef: Optional[int], n_oncul: int,
                 daha_once_men_edilenler: Set[int]) -> Tuple[bool, str]:
    """Men' ancak *mevcut* ve *henüz men edilmemiş* bir öncüle yapılır.

    Aynı öncülü tekrar men etmek "tekrâr-ı men'"dir ve münâzarayı
    sonlandırmaz — usulen reddedilir; yoksa muteriz aynı hamleyi
    sonsuza kadar tekrarlayıp mağlubiyetten kaçınabilirdi.
    """
    if hedef is None:
        return False, "men' bir öncüle taalluk etmeli"
    if not 0 <= hedef < n_oncul:
        return False, "böyle bir öncül yok"
    if hedef in daha_once_men_edilenler:
        return False, "tekrâr-ı men' — bu öncül zaten men edilmişti"
    return True, ""


def nakz_gecerli_mi(onculler: Sequence[Onerme], netice: Onerme
                    ) -> Tuple[bool, Optional[Dict[str, bool]]]:
    """Nakz: delil sûreti aynı kalırken neticenin bâtıl olduğu bir hâl.

    Hesaplanabilir karşılığı doğrudandır — kıyas geçerli **değilse**
    öncülleri doğru, neticeyi yanlış kılan bir değerlendirme vardır ve
    o değerlendirme nakzın ta kendisidir.  Geçerliyse nakz imkânsızdır.

    Dönen: ``(nakz mümkün mü, şâhit değerlendirme)``.
    """
    if gecerli_mi(list(onculler), netice):
        return False, None
    return True, karsi_ornek(list(onculler), netice)


def muaraza_gecerli_mi(karsi_onculler: Sequence[Onerme],
                       davanin_aksi: Onerme) -> bool:
    """Muâraza ancak getirilen delil dâvânın aksini **ispat ederse** sahih.

    Muteriz burada ispat yükünü üstlenmiştir; delilinin geçerliliği
    müddeîninkiyle aynı ölçütle tartılır — çifte standart yoktur.
    """
    return gecerli_mi(list(karsi_onculler), davanin_aksi)


@dataclass
class Munazara:
    """Bir münâzaranın hâli ve hükmü.

    ``onculler`` ile ``netice`` müddeînin dâvâsıdır.  ``yakinler``
    öncüllerin başlangıç yakîn dereceleridir; men' edilen bir öncülün
    yakîni, müddeî onu ispat edene kadar **sıfır** sayılır — çünkü
    münâzarada müsellem olmayan öncül delil olarak kullanılamaz.
    """
    onculler: Tuple[Onerme, ...]
    netice: Onerme
    yakinler: Tuple[float, ...]
    tarih: List[Hamle] = field(default_factory=list)
    men_edilenler: Set[int] = field(default_factory=set)
    ispat_edilenler: Set[int] = field(default_factory=set)
    muaraza_kazandi: bool = False

    def __post_init__(self) -> None:
        if len(self.onculler) != len(self.yakinler):
            raise ValueError("her öncül için bir yakîn derecesi lazım")

    # --- hamleler -----------------------------------------------------
    def men_et(self, hedef: int) -> Tuple[bool, str]:
        ok, sebep = men_mesru_mu(hedef, len(self.onculler),
                                 self.men_edilenler)
        if ok:
            self.men_edilenler.add(hedef)
            self.ispat_edilenler.discard(hedef)
            self.tarih.append(Hamle("muteriz", ItirazNevi.MEN, hedef,
                                    aciklama="öncül müsellem değil"))
        return ok, sebep

    def ispat_et(self, hedef: int, delil: Sequence[Onerme]) -> bool:
        """Müddeî men edilen öncülü müstakil delille ispat eder."""
        if hedef not in self.men_edilenler:
            return False
        if not gecerli_mi(list(delil), self.onculler[hedef]):
            return False
        self.ispat_edilenler.add(hedef)
        self.tarih.append(Hamle("müddeî", None, hedef, tuple(delil),
                                aciklama="men edilen öncül ispat edildi"))
        return True

    def nakz_et(self) -> Tuple[bool, Optional[Dict[str, bool]]]:
        mumkun, sahit = nakz_gecerli_mi(self.onculler, self.netice)
        self.tarih.append(Hamle("muteriz", ItirazNevi.NAKZ,
                                aciklama=f"nakz {'tuttu' if mumkun else 'tutmadı'}"))
        return mumkun, sahit

    def muaraza_et(self, karsi_onculler: Sequence[Onerme]) -> bool:
        aks = degil(self.netice)
        tuttu = muaraza_gecerli_mi(karsi_onculler, aks)
        self.muaraza_kazandi = self.muaraza_kazandi or tuttu
        self.tarih.append(Hamle("muteriz", ItirazNevi.MUARAZA,
                                delil=tuple(karsi_onculler), netice=aks,
                                aciklama=f"muâraza {'tuttu' if tuttu else 'tutmadı'}"))
        return tuttu

    # --- hüküm --------------------------------------------------------
    def gecerli_yakinler(self) -> List[float]:
        """Men edilip ispat edilmemiş öncülün yakîni sıfırdır."""
        return [0.0 if (i in self.men_edilenler
                        and i not in self.ispat_edilenler) else y
                for i, y in enumerate(self.yakinler)]

    def hukum(self) -> Dict[str, object]:
        sekil = gecerli_mi(list(self.onculler), self.netice)
        y = yakin_gazali(self.gecerli_yakinler(), sekil)
        if self.muaraza_kazandi:
            y = 0.0
        galip = "müddeî" if y > 0.0 else "muteriz"
        return {
            "şekil_geçerli": sekil,
            "yakîn": y,
            "mertebe": mertebe_adi(y),
            "gālip": galip,
            "men_edilen": sorted(self.men_edilenler),
            "ispat_edilen": sorted(self.ispat_edilenler),
            "muâraza_kazandı": self.muaraza_kazandi,
            "hamle_sayısı": len(self.tarih),
        }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    from .onerme import ise, ve
    s: List[str] = []

    s.append("=== Gazâlî mîzânı: yakîn en zayıf öncül kadardır ===")
    for onc, gec in (((1.0, 1.0, 1.0), True), ((1.0, 0.6, 0.9), True),
                     ((1.0, 1.0, 1.0), False), ((), True)):
        y = yakin_gazali(onc, gec)
        s.append(f"  öncüller={str(onc):22s} şekil={str(gec):5s}"
                 f" → yakîn={y:.2f}  ({mertebe_adi(y)})")
    s.append("  zincir [kat'î halkalar ×5]      → "
             f"{yakin_zinciri([((1.0, 1.0), True)] * 5):.2f}"
             "   (uzunluk yakîni düşürmez)")
    s.append("  zincir [ortada 0.6'lık bir halka] → "
             f"{yakin_zinciri([((1.0,), True), ((0.6,), True), ((1.0,), True)]):.2f}")

    s.append("\n=== Münâzara: men' → ispat ===")
    A, B, C = deg("A"), deg("B"), deg("C")
    m = Munazara((ise(A, B), A), B, (0.9, 0.8))
    s.append(f"  başlangıç: {m.hukum()['yakîn']:.2f} ({m.hukum()['mertebe']})")
    ok, sbp = m.men_et(1)
    s.append(f"  muteriz P1'i men' etti (meşru={ok}) → yakîn={m.hukum()['yakîn']:.2f}"
             f"  gālip={m.hukum()['gālip']}")
    ok2, sbp2 = m.men_et(1)
    s.append(f"  aynı öncülü tekrar men': meşru={ok2}  sebep={sbp2!r}")
    ispat = m.ispat_et(1, [ve(A, C)])
    s.append(f"  müddeî A'yı (A∧C)'den ispat etti: {ispat}"
             f" → yakîn={m.hukum()['yakîn']:.2f} gālip={m.hukum()['gālip']}")

    s.append("\n=== Nakz: geçerli kıyas nakzedilemez ===")
    saglam = Munazara((ise(A, B), A), B, (1.0, 1.0))
    bozuk = Munazara((ise(A, B), B), A, (1.0, 1.0))   # tâlîyi vaz' etmek
    for ad, mn in (("modus ponens", saglam), ("tâlîyi vaz'", bozuk)):
        mum, sahit = mn.nakz_et()
        s.append(f"  {ad:14s} nakz mümkün={mum}  şâhit={sahit}")

    s.append("\n=== Muâraza: aksini ispat eden müstakil delil ===")
    mn = Munazara((ise(A, B), A), B, (1.0, 1.0))
    s.append(f"  boş muâraza tuttu mu? {mn.muaraza_et([C])}")
    s.append(f"  ¬B'yi veren delille?  {mn.muaraza_et([degil(B)])}")
    h = mn.hukum()
    s.append(f"  hüküm: yakîn={h['yakîn']:.2f} mertebe={h['mertebe']}"
             f" gālip={h['gālip']} hamle={h['hamle_sayısı']}")
    s.append("  not: muâraza tuttuğunda dâvâ sâkıt olur — çünkü aynı anda"
             " hem B hem ¬B ispatlanmış olur, bu ise öncüllerin"
             " tenâkuzunu gösterir.")
    return "\n".join(s)


if __name__ == "__main__":
    print(_gosterim())
