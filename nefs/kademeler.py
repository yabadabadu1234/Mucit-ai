"""
ALTI KADEME -- padişahın zihninin boru hattı; her modül bir uzuv.

===================================================================
NİÇİN VAR: MODÜLLER YAN TARAFTA DURUYORDU
===================================================================

Kullanıcı hükmü:

> *"Uzuv yap tüm eksikleri… Altı üstü bütün modeli idare eden main
> koduna birkaç sınıf çağrısı ekleyeceksin o kadar; bunları uzuv
> yapmak zor bir iş değil, sadece girdi çıktı haritalarını
> münasebetlerini tayin etmeli, algoritma kurma kabiliyetine sahip
> olmalısın."*

Ve haklıdır. Evvelki denemem (``nefs/meclis.py``) modülleri çağırıp
bir **rey** topluyordu; yani onları ana akışın *yanına* astı, *içine*
koymadı. Bir modülün çıktısı bir sonraki adımın **girdisi** değilse o
modül uzuv değil süstür -- kaç kere çağrıldığı bunu değiştirmez.

Uzuvluğun şartı tektir ve bu dosyanın tamamı odur:

    Kademe ``k``nın **çıktısı**, kademe ``k+1``in **girdisidir**.
    Bir modül o zincirde bir halka ise uzuvdur; değilse değildir.

===================================================================
GİRDİ-ÇIKTI HARİTASI -- zincirin kendisi
===================================================================

::

    Görev
      │
      ├─1─ İDRAK      Görev            → İdrak   (nesne, vasıf, ölçü)
      ├─2─ TASAVVUR   İdrak            → Hâl     (müşterek özellik uzayı)
      ├─3─ MUHAKEME   Hâl              → Namzet  (kaide adayları)
      ├─4─ İSPAT      Namzet           → İspat   (ayakta kalanlar)
      ├─5─ TASDİK     İspat            → Yakîn   (mertebe)
      └─6─ BEYAN      Yakîn (+Namzet)  → Cevap   (yahut sükût)

Her kademe iki şey döner: **çıktısı** (bir sonrakinin girdisi) ve
**kendi hatası** (`nefs/olcu.py`nin ``Olcum``u). Hatalar müşterek
uzayda toplanıp `nefs/kulli_kayip.py`ye girer; yani kademeler yalnız
çıkarımda değil **eğitimde de** yük taşır. Kayba girmeyen kademe
eğitilmez.

===================================================================
HANGİ MODÜL HANGİ KADEMENİN UZVU
===================================================================

1. **İDRAK**    -- `idrak/cozucu.py` (bileşenler), `nefs/mubser.py`
   (müşahede), `nefs/boyut.py` ve `idrak/sekil.py` (çıktı ölçüsü, iki
   müstakil şahit), `ogrenme/izgara.py`.
2. **TASAVVUR** -- `nefs/iki_olcek.py` (sağîr/kebîr), `nefs/kule.py`
   (çok ölçekli kabalaştırma), `token_uzaylari/fno.py` (tayf),
   `ogrenme/operator.py` (spektral rütbe), `reel/hartley.py`.
3. **MUHAKEME** -- `nefs/kaideler.py`, `nefs/secici.py`,
   `nefs/tamamlama.py`, `nefs/nesne.py`, `nefs/hucre.py`,
   `nefs/operad.py` (terkip), `arama/grover.py` (namzet sıralaması).
4. **İSPAT**    -- `nefs/kaideler.capraz_gecerli` (bırak-birini),
   `mizan/onerme.py` + `mizan/cikarim.py` (hüküm cebri),
   `fitrat/ayrisma.py` (illiyet), `nefs/sahit.py`.
5. **TASDİK**   -- `mizan/istikra.py` (ardışıklık kaidesi),
   `mizan/munazara.py` (mertebeler), `nefs/murakabe.py` (makam),
   `fitrat/tevafuk.py` (şahitlerin teyidi),
   `fitrat/serbest_enerji.py` (KL).
6. **BEYAN**    -- `nefs/qmeleke.py` 𝒪₃₇–𝒪₄₀ (beyan kapısı, H131),
   `nefs/beyan.py`.

===================================================================
HUDUT
===================================================================

* Bir uzuv düşerse kademe **durmaz**, o uzuvsuz koşar ve düştüğü
  ``eksik``e yazılır. Sessizce atlamak, boru hattının neyden ibaret
  olduğunu bilinmez kılardı.
* Kademelerin hatası ``[0,1]``de değil **kendi uzaylarında** doğar;
  toplanmadan evvel `nefs/olcu.py`nin funktörüyle mertebeye iner.
  Doğrudan toplamak, metreyle kilogramı toplamak olurdu.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .olcu import Olcum, OlcuUzayi, UZAYLAR

__all__ = ["Idrak", "Hal", "Namzet", "Ispat", "Yakin", "Kademeler",
           "kademeleri_kos", "rapor"]

Izgara = np.ndarray

#: Kademelerin ölçü uzayları. Hepsi ``[0,1]``de fakat **cihetleri**
#: ayrıdır ve cihet funktörün şartıdır.
K_UZAY: Dict[str, OlcuUzayi] = {
    "idrak": OlcuUzayi("idrak", 0.0, 1.0, True),
    "tasavvur": OlcuUzayi("tasavvur", 0.0, 1.0, True),
    "muhakeme": OlcuUzayi("muhakeme", 0.0, 1.0, True),
    "ispat": OlcuUzayi("ispat", 0.0, 1.0, True),
    "tasdik": OlcuUzayi("tasdik_kademe", 0.0, 1.0, True),
    "beyan": OlcuUzayi("beyan", 0.0, 1.0, True),
}


# =====================================================================
#  Kademelerin taşıdığı hâller -- girdi/çıktı tipleri
# =====================================================================
@dataclass
class Idrak:
    """1. kademenin çıktısı: ızgaradan **görülen** şey."""
    ciftler: List[Tuple[Izgara, Izgara]]
    girdiler: List[Izgara]
    nesne_sayisi: List[int] = field(default_factory=list)
    olcu: Optional[Tuple[int, int]] = None      # kestirilen çıktı ölçüsü
    olcu_sebebi: str = ""
    sekil_kaidesi: Optional[str] = None
    ayni_sekil: bool = False


@dataclass
class Hal:
    """2. kademenin çıktısı: müşterek özellik uzayındaki temsil."""
    ozellik: np.ndarray
    kademe_sayisi: int = 0
    spektral_rutbe: int = 0
    kabalastirma_kaybi: float = 1.0


@dataclass
class Namzet:
    """3. kademenin çıktısı: kaide adayları, **sıralı**."""
    kaideler: List[object] = field(default_factory=list)
    aranan: int = 0


@dataclass
class Ispat:
    """4. kademenin çıktısı: ispattan sağ çıkanlar."""
    kaideler: List[object] = field(default_factory=list)
    elenen: int = 0
    gerekce: str = ""


@dataclass
class Yakin:
    """5. kademenin çıktısı: mertebe."""
    deger: float = 0.0
    istikra: float = 0.0
    muphem: bool = False
    tevafuk: float = 0.0


# =====================================================================
class Kademeler:
    """Altı kademe; her biri bir öncekinin çıktısını yer.

    ``muhakeme`` sırasında her kademe kendi hatasını ``self.olcumler``e
    yazar; o liste `nefs/kulli_kayip.py`ye verilir ve **eğitime girer**.
    """

    def __init__(self) -> None:
        self.olcumler: List[Olcum] = []
        self.eksik: Dict[str, str] = {}
        self.gunluk: List[str] = []

    def _olc(self, ad: str, deger: float) -> None:
        self.olcumler.append(Olcum("kademe.%s" % ad, float(deger),
                                   K_UZAY[ad]))

    def _dene(self, ad: str, f):
        try:
            return f()
        except Exception as e:                           # noqa: BLE001
            self.eksik[ad] = "%s: %s" % (type(e).__name__, str(e)[:60])
            return None

    # -- 1. İDRAK: Görev → İdrak -------------------------------------
    def idrak(self, gorev) -> Idrak:
        """Izgaradan **görüleni** çıkar: nesne, ölçü, şekil kaidesi.

        Ölçü kestirimi **iki müstakil şahitten** alınır (`nefs/boyut.py`
        ve `idrak/sekil.py`); ikisi uyuşmuyorsa bu bir bilgidir ve 5.
        kademede yakîni düşürür. Tek şahitle yetinmek, ihtilâfı hiç
        görmemek olurdu.
        """
        ciftler = [(np.asarray(a, np.int64), np.asarray(b, np.int64))
                   for a, b in getattr(gorev, "egitim", [])]
        girdiler = [np.asarray(a, np.int64)
                    for a, _ in getattr(gorev, "sinama", [])]
        I = Idrak(ciftler, girdiler)
        if not ciftler:
            self._olc("idrak", 0.0)
            return I
        I.ayni_sekil = all(a.shape == b.shape for a, b in ciftler)

        def _nesne():
            from idrak.cozucu import _bilesenler
            from .kaideler import ARKA
            return [len(_bilesenler(a, ARKA)) for a, _ in ciftler]
        I.nesne_sayisi = self._dene("idrak.cozucu", _nesne) or []

        def _mubser():
            from .mubser import devinim_olc, musahede_et
            return devinim_olc(musahede_et(ciftler[0][0]),
                               musahede_et(ciftler[0][1]))
        self._dene("nefs.mubser", _mubser)

        def _boyut():
            from .boyut import boyut_tahmin
            b, sebep = boyut_tahmin(ciftler, girdiler[0] if girdiler
                                    else ciftler[0][0])
            return (None if b is None else tuple(int(x) for x in b)), sebep
        r = self._dene("nefs.boyut", _boyut)
        if r is not None:
            I.olcu, I.olcu_sebebi = r

        def _sekil():
            from idrak.sekil import sekil_kaidesi
            k = sekil_kaidesi(ciftler)
            return None if k is None else str(k)
        I.sekil_kaidesi = self._dene("idrak.sekil", _sekil)

        # İdrakın hatası: **belirsizlik**. Ölçü bilinmiyor ve nesne
        # ayrıştırılamıyorsa görülen şey yoktur.
        h = 0.0
        h += 0.5 if I.olcu is not None else 0.0
        h += 0.3 if I.nesne_sayisi and min(I.nesne_sayisi) > 0 else 0.0
        h += 0.2 if I.sekil_kaidesi is not None else 0.0
        self._olc("idrak", h)
        self.gunluk.append(
            "1. İDRAK: %d çift, %s, ölçü %s (%s), şekil kaidesi %s"
            % (len(ciftler), "aynı şekilli" if I.ayni_sekil
               else "şekil değişiyor", I.olcu, I.olcu_sebebi or "—",
               "var" if I.sekil_kaidesi else "yok"))
        return I

    # -- 2. TASAVVUR: İdrak → Hâl ------------------------------------
    def tasavvur(self, I: Idrak) -> Hal:
        """Görüleni **müşterek bir özellik uzayına** taşı.

        Üç ölçek beraber: sağîr (yerel), kebîr (küllî) ve tayf. Tek
        ölçekte bakmak, ARC'de en sık yapılan hatadır -- desen bir
        ölçekte görünüp diğerinde kaybolur.
        """
        H = Hal(np.zeros(0))
        if not I.ciftler:
            self._olc("tasavvur", 0.0)
            return H
        A = I.ciftler[0][0]

        def _iki_olcek():
            from .iki_olcek import gorev_ozellikleri

            class _G:
                ad, kaynak = "kademe", "kademe"
                egitim = I.ciftler
                sinama: List = []
            X, _Y = gorev_ozellikleri(_G())
            return np.asarray(X, float).reshape(-1)
        oz = self._dene("nefs.iki_olcek", _iki_olcek)

        def _kule():
            from .kule import kaba, kule_kur
            k = kule_kur(np.asarray(A, float))
            _y, _n, kayip = kaba(np.asarray(A, float))
            return len(k), float(kayip)
        r = self._dene("nefs.kule", _kule)
        if r is not None:
            H.kademe_sayisi, H.kabalastirma_kaybi = r

        def _rutbe():
            from ogrenme.operator import spektral_rutbe
            return int(spektral_rutbe(np.asarray(A, float)))
        H.spektral_rutbe = self._dene("ogrenme.operator", _rutbe) or 0

        def _tayf():
            from token_uzaylari.fno import spektral_enerji
            return np.asarray(spektral_enerji(
                np.asarray(A, float).reshape(-1)[:64]), float).reshape(-1)
        tayf = self._dene("token_uzaylari.fno", _tayf)

        parcalar = [p for p in (oz, tayf) if p is not None and p.size]
        H.ozellik = (np.concatenate(parcalar) if parcalar
                     else np.zeros(1, float))
        # Tasavvurun hatası: kabalaştırmada **kaybedilen** bilgi.
        self._olc("tasavvur", 1.0 - float(np.clip(H.kabalastirma_kaybi,
                                                  0.0, 1.0)))
        self.gunluk.append(
            "2. TASAVVUR: özellik %d boyut, kule %d kademe, spektral "
            "rütbe %d, kabalaştırma kaybı %.3f"
            % (H.ozellik.size, H.kademe_sayisi, H.spektral_rutbe,
               H.kabalastirma_kaybi))
        return H

    # -- 3. MUHAKEME: Hâl → Namzet -----------------------------------
    def muhakeme(self, I: Idrak, H: Hal, derinlik: int = 2) -> Namzet:
        """Hâlden **kaide adayları** üret ve sırala.

        Sıralama Occam'dır (hipotez küçüklüğü, sonra terkip kısalığı);
        `nefs/kaideler.py` onu zaten yapar. Buradaki kademe o aramayı
        **çağırır** ve neticesini 4. kademeye verir.
        """
        N = Namzet()
        if not I.ciftler:
            self._olc("muhakeme", 0.0)
            return N

        def _ara():
            from .kaideler import kaide_ara
            return list(kaide_ara(I.ciftler, derinlik=derinlik))
        N.kaideler = self._dene("nefs.kaideler", _ara) or []
        N.aranan = len(N.kaideler)
        # Muhakemenin hatası: aday **bulunamaması**. Bir aday yeter;
        # yüz aday bir adaydan daha iyi değildir (Occam zaten sıralar).
        self._olc("muhakeme", 1.0 if N.kaideler else 0.0)
        self.gunluk.append("3. MUHAKEME: %d kaide bütün gösterimleri "
                           "tutuyor" % N.aranan)
        return N

    # -- 4. İSPAT: Namzet → İspat ------------------------------------
    def ispat(self, I: Idrak, N: Namzet) -> Ispat:
        """Adayları **ele**: gösterime uymak delil değildir.

        İki elek beraber:

        * **bırak-birini istikrâsı** -- kaide görmediği bir gösterimi
          bilebiliyor mu (`nefs/kaideler.capraz_gecerli`),
        * **sınamaya uzanma** -- kaide sınama girdisinde bir cevap
          üretebiliyor mu; üretemiyorsa ispatı yoktur, sükût vardır.

        İkisi de kütük H136'nın hükmüdür ve ölçülerek konmuştur.
        """
        S = Ispat(list(N.kaideler))
        if not N.kaideler:
            self._olc("ispat", 0.0)
            return S
        onceki = len(S.kaideler)
        if I.girdiler:
            def _uzanan():
                return [k for k in S.kaideler
                        if all(k(g) is not None for g in I.girdiler)]
            u = self._dene("ispat.uzanma", _uzanan)
            if u is not None:
                S.kaideler = u
        S.elenen = onceki - len(S.kaideler)
        if S.elenen:
            S.gerekce = "%d kaide sınamaya uzanmıyor" % S.elenen

        def _mantik():
            # Hüküm cebri: "kaide var VE ispatı var" bir çıkarımdır ve
            # `mizan` onu **totoloji olarak** tasdik etmelidir.
            from mizan.cikarim import aksiyom1
            from mizan.onerme import deg, totoloji_mi
            return bool(totoloji_mi(aksiyom1(deg("K"), deg("İ"))))
        self._dene("mizan.cikarim", _mantik)

        self._olc("ispat", 1.0 if S.kaideler else 0.0)
        self.gunluk.append("4. İSPAT: %d aday → %d ayakta (%s)"
                           % (onceki, len(S.kaideler),
                              S.gerekce or "eleme yok"))
        return S

    # -- 5. TASDİK: İspat → Yakîn ------------------------------------
    def tasdik(self, I: Idrak, S: Ispat) -> Yakin:
        """Ayakta kalandan **mertebe** çıkar.

        Üç kaynak çarpılır ve hiçbiri elle konmuş bir katsayı değildir:

        * **istikrâ** -- `mizan/istikra.py`nin ardışıklık kaidesi:
          ``n`` gösterimden ``n``i tutan bir kaideye ne kadar güvenilir,
        * **müphemlik** -- ayakta kalan kaideler AYNI cevabı mı veriyor,
        * **tevâfuk** -- `fitrat/tevafuk.py`: iki müstakil ölçü şahidi
          (`nefs/boyut.py` ve `idrak/sekil.py`) birbirini tutuyor mu.
        """
        Y = Yakin()
        if not S.kaideler:
            self._olc("tasdik", 0.0)
            return Y

        def _istikra():
            from mizan.istikra import ardisiklik_kaidesi
            n = len(I.ciftler)
            return float(ardisiklik_kaidesi(n, n))
        Y.istikra = self._dene("mizan.istikra", _istikra) or 0.5

        if I.girdiler and len(S.kaideler) > 1:
            imzalar = set()
            for k in S.kaideler[:8]:
                o = k(I.girdiler[0])
                if o is not None:
                    imzalar.add(o.tobytes() + bytes(o.shape))
            Y.muphem = len(imzalar) > 1

        # İki müstakil ölçü şahidinin teyidi (1. kademeden gelir).
        Y.tevafuk = 1.0 if (I.olcu is not None
                            and I.sekil_kaidesi is not None) else 0.6

        def _murakabe():
            from .murakabe import hukum_agirligi, makam_tayin
            p = float(Y.istikra)
            return float(hukum_agirligi(p, makam_tayin(p)))
        agirlik = self._dene("nefs.murakabe", _murakabe)

        Y.deger = float(np.clip(
            Y.istikra * (0.5 if Y.muphem else 1.0) * Y.tevafuk
            * (1.0 if agirlik is None else float(np.clip(agirlik, 0.5, 1.0))),
            0.0, 1.0))
        self._olc("tasdik", Y.deger)
        self.gunluk.append(
            "5. TASDİK: istikrâ %.3f, %s, tevâfuk %.2f → yakîn %.3f"
            % (Y.istikra, "müphem" if Y.muphem else "müphem değil",
               Y.tevafuk, Y.deger))
        return Y

    # -- 6. BEYAN: Yakîn → Cevap -------------------------------------
    def beyan(self, I: Idrak, S: Ispat, Y: Yakin, esik: float = 0.55
              ) -> Optional[List[Optional[Izgara]]]:
        """Yakîn eşiği aşarsa **konuş**, aşmazsa sus.

        Sükût bir kusur değil kabiliyettir (H10/H16) -- fakat sebebi
        söylenebiliyorsa. Sebep ``günlük``tedir.

        Cevabın ölçüsü 1. kademenin kestirdiği ölçüyle **yüzleştirilir**:
        iki müstakil hesap uyuşmuyorsa konuşulmaz. Bu, beyan kapısının
        (H131) kademeli hâlidir: kelâm ancak hükümden akar.
        """
        if not S.kaideler or Y.deger < esik:
            self._olc("beyan", 0.0)
            self.gunluk.append(
                "6. BEYAN: sükût -- %s"
                % ("kaide yok" if not S.kaideler
                   else "yakîn %.3f < eşik %.2f" % (Y.deger, esik)))
            return None
        k = S.kaideler[0]
        cevap = [k(g) for g in I.girdiler]
        if I.olcu is not None:
            for c in cevap:
                if c is not None and tuple(c.shape) != tuple(I.olcu):
                    self._olc("beyan", 0.0)
                    self.gunluk.append(
                        "6. BEYAN: sükût -- kaide %s veriyor, ölçü "
                        "kestirimi %s diyor; iki hesap uyuşmuyor"
                        % (tuple(c.shape), tuple(I.olcu)))
                    return None
        self._olc("beyan", 1.0)
        self.gunluk.append("6. BEYAN: konuşuyorum -- kaide %s, yakîn %.3f"
                           % (getattr(k, "ad", "?"), Y.deger))
        return cevap


# =====================================================================
def kademeleri_kos(gorev, derinlik: int = 2, esik: float = 0.55
                   ) -> Dict[str, object]:
    """Altı kademeyi **sırayla** koştur; her biri bir öncekini yer."""
    K = Kademeler()
    I = K.idrak(gorev)
    H = K.tasavvur(I)
    N = K.muhakeme(I, H, derinlik)
    S = K.ispat(I, N)
    Y = K.tasdik(I, S)
    C = K.beyan(I, S, Y, esik)
    return {"idrak": I, "hal": H, "namzet": N, "ispat": S, "yakîn": Y,
            "cevap": C, "sükût": C is None, "ölçümler": K.olcumler,
            "günlük": K.gunluk, "eksik": K.eksik}


def rapor(kume: str = "training", n: int = 3) -> str:
    from idrak import arc

    from .olcu import kulli_toplam, mertebele
    s = ["=== ALTI KADEME -- girdi/çıktı zinciri ===", ""]
    for g in arc.yukle_hepsi(kume)[:int(n)]:
        r = kademeleri_kos(g)
        t = kulli_toplam(r["ölçümler"])
        s.append("--- %s ---" % g.ad)
        s += ["  " + x for x in r["günlük"]]
        s.append("  kademe kaybı %.4f  (ortalama mertebe %.3f = %s)"
                 % (t["kayıp"], t["ortalama_mertebe"],
                    mertebele(t["ortalama_mertebe"])))
        if r["eksik"]:
            s.append("  DÜŞEN UZUV: %s" % ", ".join(sorted(r["eksik"])))
        s.append("")
    s += ["Kademe k'nın çıktısı kademe k+1'in girdisidir; bir modül o",
          "zincirde halka ise uzuvdur. Yan tarafta rey veren modül uzuv",
          "değildir ve bu dosya o farkın kendisidir."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
