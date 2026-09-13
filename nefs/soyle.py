from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from .musahede import gorev_dizisi, ortu

__all__ = ["Cevap", "soyle"]


@dataclass
class Cevap:

    gorev: str = ""
    sukut: bool = True
    sebep: str = ""
    kural: Optional[str] = None
    izgara: Optional[List[np.ndarray]] = None
    aday_sayisi: int = 0
    tikaniklik: Optional[float] = None
    belirtec: Optional[List[int]] = None
    guven: float = 0.0
    budanan: int = 0


def _buda(P: np.ndarray, hafiza) -> tuple:
    if hafiza is None:
        return P, 0
    maske = hafiza.zeno(np.sqrt(np.asarray(P, float)))
    if maske is None:
        return P, 0
    kesik = int(np.count_nonzero(~maske))
    if kesik == 0 or kesik >= P.size:
        return P, 0
    Q = np.where(maske, P, 0.0)
    top = float(Q.sum())
    assert top > 0.0, "Zeno budaması dağılımı tamamen söndürdü"
    return Q / top, kesik


def _sec(P: np.ndarray, ayna=None) -> int:
    if ayna is None:
        return int(np.argmax(P))
    from .ayna import kivilcim
    Q = kivilcim(P, ayna)
    assert Q.size == P.size and np.all(np.isfinite(Q)), "kıvılcım bozuk"
    return int(np.argmax(Q))


def _uret(nefs, baglam: List[int], n: int, pencere: int, sozluk: int,
          ayna=None, hafiza=None) -> tuple:
    from .qegitim import adayin_tuttugu
    bag = list(baglam)
    cikti: List[int] = []
    bedel = 0.0
    budanan = 0
    sukutlar: List[float] = []
    for _ in range(n):
        pen = bag[-pencere:]
        P, o = adayin_tuttugu(nefs, (), sozluk=int(sozluk), ne="koş",
                              baglam=pen)
        P = np.asarray(P, float).reshape(-1)
        P = np.clip(P, 1e-12, None)
        P = P / P.sum()
        sukutlar.append(float(o.get("sukut", 0.0)))
        P, kesik = _buda(P, hafiza)
        budanan += kesik
        t = _sec(P, ayna)
        bedel -= float(np.log(P[t]))
        cikti.append(t)
        bag.append(t)
    return cikti, bedel, sukutlar, budanan


def soyle(gorev=None, manzara=None, tikaniklik_bak: bool = False,
          nefs=None, pencere: int = 8, sozluk: int = 16,
          azami_uret: int = 0, sukut_esigi: float = 0.8,
          usul: str = "açgözlü", aday: int = 8, tohum: int = 0,
          teta=None,
          hafiza=None, ne: str = "cevap",
          hedef: int = 0, sinamadan: bool = False) -> Any:
    if gorev is None:
        raise ValueError("söylemek için bir görev lâzım")
    assert manzara is None, (
        "``soyle`` manzara ALMAZ (ferman 6): ızgaradan elle çıkarılmış "
        "nesne/kaide, motorun cevabına karışamaz. Cevap belirteç "
        "üretiminden gelir.")

    def _bitir(c: "Cevap"):
        if ne == "sukut_mu":
            return c.sukut
        if ne != "cevap":
            raise ValueError("söyleme kipi bilinmiyor: %r" % (ne,))
        return c


    if nefs is None:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True,
            sebep="motor verilmedi -- kâide cebriyle cevap vermek yasak"))

    tik = None
    if tikaniklik_bak:
        tik = float(ortu(gorev, ne="tıkanıklık")["H1"])
        assert np.isfinite(tik), "tıkanıklık ölçüsü sonlu değil"

    kaynak = gorev.sinama if sinamadan else gorev.egitim
    assert 0 <= int(hedef) < len(kaynak), (
        "%s: istenen hedef %d, fakat %s kaynağında %d örnek var"
        % (gorev.ad, int(hedef), "sınama" if sinamadan else "eğitim",
           len(kaynak)))
    dizi, hedef = gorev_dizisi(gorev, hedef_indis=int(hedef),
                               sinamadan=bool(sinamadan))
    assert len(dizi) > 0 and len(hedef) > 0, (
        "bağlam yahut hedef BOŞ döndü -- boş bir şeyle üretime girilmez")

    h = [int(x) % int(sozluk) for x in hedef]
    if 0 < int(azami_uret) < len(h):
        return _bitir(Cevap(gorev=gorev.ad, sukut=True, tikaniklik=tik,
                            sebep="hedef hadde sığmıyor (%d belirteç)"
                                  % len(h)))

    baglam = [int(x) % int(sozluk) for x in dizi]

    def _cek(ayna=None):
        return _uret(nefs, baglam, len(h), pencere, sozluk, ayna=ayna,
                     hafiza=hafiza)

    if usul == "açgözlü":
        uretilen, bedel, sukutlar, budanan = _cek()
    elif usul == "ara":
        from .ara import ara
        from .ayna import AynaAyari
        n_ad_istenen = max(1, int(aday))
        adaylar = [_cek()]
        for k in range(1, n_ad_istenen):
            adaylar.append(_cek(AynaAyari(
                teta=(np.pi / 4) * k / n_ad_istenen,
                sikma_fazi=2.0 * np.pi * k / n_ad_istenen,
                tohum=int(tohum) + k)))
        bedeller = np.array([a[1] for a in adaylar], float)
        n_ad = len(adaylar)
        tam = 1
        while tam < n_ad:
            tam *= 2
        if tam > n_ad:
            bedeller = np.concatenate(
                [bedeller, np.full(tam - n_ad, bedeller.max() + 1e3)])
        j = int(ara(bedeller, ne="en_iyi", yol="dürr")["x"])
        assert 0 <= j < len(bedeller), "arama aralık dışı indis verdi: %d" % j
        uretilen, bedel, sukutlar, budanan = adaylar[j if j < n_ad else 0]
    else:
        raise ValueError("çözme usulü bilinmiyor: %r" % (usul,))

    guvenler = [float(np.exp(-bedel / max(len(h), 1)))]

    ort_sukut = float(np.mean(sukutlar)) if sukutlar else 1.0

    from .qegitim import belirtecleri_kodla
    from .suphe import SupheAyari, suphe_manifoldu
    _E = belirtecleri_kodla(list(uretilen)[-int(pencere):] or [0],
                            nefs.ayar.veri_lifi, nefs.ayar.veri_lifi)
    _q = nefs.idrak_et(_E)
    _sp = suphe_manifoldu([np.asarray(_q.y.psi[0], complex)],
                          [1.0 - 2.0 * ort_sukut],
                          yakin=np.array([1.0 - ort_sukut]),
                          ayar=SupheAyari(acik=1))
    if int(_sp["tevakkuf"]) > 0:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=uretilen, guven=float(np.mean(guvenler or [0.0])),
            budanan=int(budanan),
            sebep="TEÂRUZ: yakîn %.3f -- tez ile antitez denk kuvvette"
                  % float(_sp["μ"][0])))

    if ort_sukut > float(sukut_esigi):
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=uretilen, guven=float(np.mean(guvenler or [0.0])),
            budanan=int(budanan),
            sebep="motorun sükût alanı %.3f > %.3f"
                  % (ort_sukut, float(sukut_esigi))))

    return _bitir(Cevap(
        gorev=gorev.ad, sukut=False, sebep="",
        kural="motor (belirteç üretimi)",
        izgara=[np.asarray(uretilen, int)],
        belirtec=uretilen,
        guven=float(np.mean(guvenler or [0.0])),
        budanan=int(budanan),
        aday_sayisi=0, tikaniklik=tik))
