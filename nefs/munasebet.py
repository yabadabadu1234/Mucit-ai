"""
MÜNASEBET -- BİR VERİ, HUDUDU TEMİZLENENE KADAR

===================================================================
PADİŞAHIN HÜKMÜ (ferman 1-I)
===================================================================

    "O veri için hata sıfırlanana kadar devam etmelisin, sonra yeni veri
    getirmelisin. Böylece bir süre sonra tüm veriler için **müşterek bir
    münasebet haritası** oluşacak."

===================================================================
NE DEĞİŞTİ -- VE NİÇİN ESKİSİ YANLIŞTI
===================================================================

Evvelce tâlim şöyleydi: bütün veri (512 örnek) tek bir kayba toplanır,
eniyileyici o toplamı düşürmeye çalışırdı. Bu, **her örneği bir kere
görüp geçmektir** ve iki kusuru vardır:

1. Bir örneğin tenakuzu, öteki 511 örneğin ortalamasında kaybolur.
   Kayıp düşer, tenakuz yerinde kalır -- ölçüldü: 30 kayıp çağrısında
   eğim yalnız ``−0,32``, çünkü düşen şey ortalamaydı, hudut değil.
2. Örnekler arasında **münasebet kurulmaz**. Her biri ayrı bir sayı
   olarak toplanır; hangisinin hangisiyle çeliştiği hiç sorulmaz.

Yeni usul: örnekler **sırayla** alınır, her biri kendi hududu
temizlenene kadar üstünde durulur, sonra yenisi gelir. Ve her örnek
kapandığında, o örneğin belirteçleri arasındaki bağ **müşterek
münasebet haritasına** işlenir.

===================================================================
MÜŞTEREK MÜNASEBET HARİTASI
===================================================================

Harita ``(n_v, n_v)`` bir dizeydir ve her hücresi şudur::

    M[a,b] = Σ_örnek  keyfiyet_nispeti(örnek) · [a,b ∈ örnek]

Yâni: *"bu iki kavram, hududu temizlenmiş bir örnekte kaç kere beraber
göründü?"* Ağırlık ham sayım değil, o örnekte erişilen **keyfiyettir**:
kirli kalmış bir örnekten öğrenilen münasebet zayıf sayılır.

Harita üç yerde iş görür ve üçü de ölçülür:

* **SIRA** -- bir sonraki örnek rastgele seçilmez: haritaya en çok
  **yeni** bağ getirecek olan seçilir (münasebeti en zayıf olan).
  Böylece harita en hızlı doyar.
* **HAZİNE** -- harita hazineye yazılır; çıkarım onu okur.
* **DIŞLAMA** -- ``nefs/tenakuz.py``nin ``S_dışlama``sı ham eş-zamanlılık
  yerine bu haritayı okuyabilir: keyfiyetle ağırlıklanmış münasebet,
  ham sayımdan daha doğru bir "beraber görüldü mü" ölçüsüdür.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["MunasebetAyari", "Harita", "munasebet_kos", "munasebet_beyani",
           "munasebet_sifirla"]


@dataclass
class MunasebetAyari:
    """Münasebet döngüsünün ölçüleri."""

    #: ``0`` = kapalı: eski usul (bütün veri tek kayıp) geri gelir ve
    #: ölçü kırmızı yanar -- hudut hiç temizlenmez.
    acik: int = 1
    #: Bir turda kaç örnek üstünde durulacak. Bütün veriyi tek turda
    #: tüketmek şart değildir: harita turlar boyunca birikir.
    obek: int = 8
    #: Bir örnekte azamî kaç eniyileme turu.
    azami_tur: int = 8
    #: Belirteç lifi -- haritanın boyu.
    n_v: int = 16


@dataclass
class Harita:
    """Müşterek münasebet haritası -- ``(n_v, n_v)``, keyfiyet ağırlıklı."""

    n_v: int = 16
    M: np.ndarray = field(default_factory=lambda: np.zeros((16, 16)))
    islenen: int = 0

    def __post_init__(self) -> None:
        if self.M.shape != (int(self.n_v), int(self.n_v)):
            self.M = np.zeros((int(self.n_v), int(self.n_v)), float)

    def isle(self, baglam: Sequence[int], nispet: float) -> int:
        """Bir örneğin bağlarını haritaya **keyfiyet ağırlığıyla** işle."""
        t = np.unique(np.asarray(list(baglam), np.int64) % int(self.n_v))
        if t.size < 2:
            return 0
        self.M[np.ix_(t, t)] += float(nispet)
        np.fill_diagonal(self.M, 0.0)
        self.islenen += 1
        return int(t.size * (t.size - 1))

    def zayiflik(self, baglam: Sequence[int]) -> float:
        """Bu örnek haritaya ne kadar **yeni** bağ getirir?

        Sıra bundan çıkar: en zayıf münasebeti olan örnek öne alınır,
        böylece harita en hızlı doyar. Rastgele seçim, aynı bölgeyi
        tekrar tekrar dövmek olurdu.
        """
        t = np.unique(np.asarray(list(baglam), np.int64) % int(self.n_v))
        if t.size < 2:
            return 0.0
        alt = self.M[np.ix_(t, t)]
        # Doyma: hücre büyüdükçe yenilik azalır. ``1/(1+M)`` monotondur
        # ve doyum noktası yoktur -- eşik değil, nispet.
        return float(np.mean(1.0 / (1.0 + alt)))

    def doyma(self) -> float:
        """Harita ne kadar doldu -- ``[0,1]``."""
        toplam = float(self.M.size - self.n_v)
        if toplam <= 0:
            return 0.0
        return float(np.count_nonzero(self.M) / toplam)

    def hazineye(self) -> Dict[str, np.ndarray]:
        return {"münasebet.M": np.asarray(self.M, float)}


_SAYAC: Dict[str, float] = {
    "örnek": 0.0, "tur": 0.0, "temizlenen": 0.0, "kirli_kalan": 0.0,
    "bag": 0.0, "kayip_cagrisi": 0.0}


def munasebet_kos(veri: Sequence[Tuple[Sequence[int], int]],
                  p0: np.ndarray,
                  eniyile: Callable[[np.ndarray, Sequence], Tuple],
                  olc: Callable[[np.ndarray, Sequence], Dict[str, Any]],
                  harita: Optional[Harita] = None,
                  ayar: Optional[MunasebetAyari] = None,
                  keyfiyet_ayari=None) -> Dict[str, Any]:
    """**BİR VERİ, HUDUDU TEMİZLENENE KADAR.** Sonra yeni veri.

    ``eniyile(p, küme) -> (p_yeni, çağrı)``  bir örnek kümesi üstünde
                                             kısa bir eniyileme turu.
    ``olc(p, küme) -> döküm``                o kümenin mizan dökümü.

    Döngü::

        harita ← boş
        while örnek kaldı ve bütçe var:
            küme ← haritaya en çok YENİ bağ getiren örnekler
            tur ← 0
            while tur < azamî and not hudut_temiz(küme):
                p ← eniyile(p, küme)
                k ← keyfiyet(olc(p, küme))
                if k.nispet >= eşik(tur, azamî):   # eşik FONKSİYON
                    break
                tur += 1
            harita.işle(küme, k.nispet)
    """
    from .keyfiyet import esik, keyfiyet
    from .sadakat import sadakat_beyani

    a = ayar or MunasebetAyari()
    h = harita or Harita(n_v=int(a.n_v))
    p = np.asarray(p0, float).copy()
    if not int(a.acik):
        # **KAPALI: ESKİ USUL.** Bütün veri tek kümede, tek tur.
        p, c = eniyile(p, list(veri))
        _SAYAC["kayip_cagrisi"] += float(c)
        return {"p": p, "harita": h, "açık": False, "örnek": 0,
                "temizlenen": 0, "kirli_kalan": 0, "tur": 0}

    kalan = list(range(len(veri)))
    obek = max(1, int(a.obek))
    temizlenen = kirli = 0
    while kalan:
        # ── SIRA: haritaya en çok YENİ bağ getiren öne ─────────────
        zayif = np.asarray([h.zayiflik(veri[i][0]) for i in kalan], float)
        sira = np.argsort(-zayif)[:obek]
        kume_idx = [kalan[int(j)] for j in sira]
        kume = [veri[i] for i in kume_idx]
        for i in kume_idx:
            kalan.remove(i)

        # ── BİR KÜME, HUDUDU TEMİZLENENE KADAR ─────────────────────
        k: Dict[str, Any] = {}
        for tur in range(max(1, int(a.azami_tur))):
            p, c = eniyile(p, kume)
            _SAYAC["kayip_cagrisi"] += float(c)
            _SAYAC["tur"] += 1.0
            k = keyfiyet(olc(p, kume), sadakat_beyani(), keyfiyet_ayari)
            if k["hudut_temiz"]:
                break
            # **EŞİK BİR FONKSİYONDUR** (ferman 1-J): sabit bir sayıyla
            # değil, koşunun fiilen eriştiği keyfiyetle ve kalan
            # bütçeyle kıyaslanır.
            if k["nispet"] >= esik(tur + 1, int(a.azami_tur),
                                   keyfiyet_ayari):
                break
        assert k, "keyfiyet ölçülmeden küme kapatılamaz"
        if k["hudut_temiz"]:
            temizlenen += 1
        else:
            kirli += 1
        for bag, _hed in kume:
            _SAYAC["bag"] += float(h.isle(bag, float(k["nispet"])))
        _SAYAC["örnek"] += float(len(kume))

    _SAYAC["temizlenen"] += float(temizlenen)
    _SAYAC["kirli_kalan"] += float(kirli)
    return {"p": p, "harita": h, "açık": True,
            "örnek": int(_SAYAC["örnek"]), "temizlenen": temizlenen,
            "kirli_kalan": kirli, "tur": int(_SAYAC["tur"]),
            "doyma": h.doyma()}


def munasebet_beyani() -> Dict[str, Any]:
    k = max(1.0, _SAYAC["temizlenen"] + _SAYAC["kirli_kalan"])
    return {"örnek": int(_SAYAC["örnek"]), "tur": int(_SAYAC["tur"]),
            "temizlenen": int(_SAYAC["temizlenen"]),
            "kirli_kalan": int(_SAYAC["kirli_kalan"]),
            "temizlik_nispeti": float(_SAYAC["temizlenen"] / k),
            "bağ": int(_SAYAC["bag"]),
            "kayıp_çağrısı": int(_SAYAC["kayip_cagrisi"]),
            "küme_başına_tur": float(_SAYAC["tur"] / k)}


def munasebet_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
