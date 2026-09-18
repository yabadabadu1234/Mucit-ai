from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from .hafiza import TASDIK
from .musahede import gorev_dizisi, ortu

__all__ = ["Cevap", "soyle"]


@dataclass
class Cevap:

    gorev: str = ""
    sukut: bool = True
    sebep: str = ""
    kural: Optional[str] = None
    izgara: Optional[List[np.ndarray]] = None
    tikaniklik: Optional[float] = None
    belirtec: Optional[List[int]] = None
    guven: float = 0.0
    budanan: int = 0
    uzunluk: int = 0


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


def _sec(P: np.ndarray) -> int:
    Q = np.clip(np.asarray(P, float).reshape(-1), 1e-300, None)
    Q = Q / Q.sum()
    egim = np.log(Q)
    g_fs = Q * (1.0 - Q)
    artik = g_fs > np.finfo(float).eps
    assert bool(artik.any()), (
        "Fubini-Study metriği tamamen söndü -- determinist okuma "
        "yapılamaz (ferman 2-Ĵ)")
    skor = np.where(artik, egim / np.where(artik, g_fs, 1.0),
                    -np.inf)
    return int(np.argmax(skor))


def _acilis(nefs, baglam: List[int], pencere: int) -> tuple:
    from .qegitim import belirtecleri_kodla
    taban = nefs.ayar.veri_lifi
    pen = max(1, int(pencere))
    kesitler = [baglam[i:i + pen] for i in range(0, len(baglam), pen)]
    kesitler = [k for k in kesitler if k] or [list(baglam) or [0]]
    haller: List[np.ndarray] = []
    sukutlar: List[float] = []
    for k in kesitler:
        q = nefs.idrak_et(belirtecleri_kodla(k, taban, taban))
        haller.append(np.asarray(q.y.psi[0], complex).reshape(-1))
        sukutlar.append(float(q.olcumler().get("sukut", 0.0)))
    return haller, sukutlar


def _cumle(nefs, baglam: List[int], pencere: int, sozluk: int,
           vecihler, hafiza=None) -> tuple:
    from .qegitim import belirtecleri_kodla
    dizi = list(baglam)
    cikti: List[int] = []
    sukutlar: List[float] = []
    bedel = 0.0
    budanan = 0
    q = None
    while True:
        pen = dizi[-int(pencere):]
        E = belirtecleri_kodla(pen, nefs.ayar.veri_lifi,
                               nefs.ayar.veri_lifi)
        q = nefs.idrak_et(E)
        sukut = float(q.olcumler().get("sukut", 0.0))
        sukutlar.append(sukut)
        if cikti and q.durma_hukmu(len(cikti) - 1):
            break
        P = np.clip(np.asarray(
            q.beyan_vecihle(int(sozluk), vecihler), float)[0],
            1e-12, None)
        P = P / P.sum()
        P, kesik = _buda(P, hafiza)
        budanan += kesik
        t = _sec(P)
        bedel -= float(np.log(P[t]))
        cikti.append(int(t))
        dizi.append(int(t))
    assert cikti, (
        "üretim tek belirteç dahi vermeden durdu -- alt hudut yoktur "
        "fakat sıfır da bir cevap değildir (ferman 2-Ó-B)")
    if hafiza is not None:
        hafiza.yaz(np.asarray(q.y.psi[0], complex),
                   omega=float(np.exp(-bedel / max(len(cikti), 1))),
                   hukum=TASDIK)
    return cikti, bedel, sukutlar, budanan


def _uret(nefs, baglam: List[int], pencere: int, sozluk: int,
          hafiza=None) -> tuple:
    from .mukayese import merakla_coz
    from .suphe import SupheAyari, suphe_manifoldu
    haller, sukutlar = _acilis(nefs, baglam, pencere)
    sp = suphe_manifoldu(
        haller, [1.0 - 2.0 * s for s in sukutlar],
        yakin=np.asarray([1.0 - s for s in sukutlar], float),
        ayar=SupheAyari(acik=1))
    return merakla_coz(
        haller, sp["merak"],
        lambda vs: _cumle(nefs, baglam, pencere, sozluk, vs,
                          hafiza=hafiza))


def soyle(gorev=None, manzara=None, tikaniklik_bak: bool = False,
          nefs=None, pencere: int = 8, sozluk: int = 16,
          azami_uret: int = 0,
          usul: str = "açgözlü",
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

    from .belirtec import basamak_sayisi, tip_vektoru, tipten
    taban = int(nefs.ayar.veri_lifi)
    assert int(sozluk) >= 2, (
        "sözlük %d -- belirteç uzayı yok (ferman 1-N: sözlük tiktoken "
        "n_vocab'ından yoklanır)" % int(sozluk))
    basamak = int(basamak_sayisi(int(sozluk), taban))
    h = [int(x) for x in np.asarray(
        tip_vektoru(list(hedef), taban, basamak), int).reshape(-1)]
    if 0 < int(azami_uret) < len(h):
        return _bitir(Cevap(gorev=gorev.ad, sukut=True, tikaniklik=tik,
                            sebep="hedef hadde sığmıyor (%d basamak)"
                                  % len(h)))

    baglam = [int(x) for x in np.asarray(
        tip_vektoru(list(dizi), taban, basamak), int).reshape(-1)]

    def _cek():
        return _uret(nefs, baglam, pencere, taban, hafiza=hafiza)

    assert usul == "açgözlü", (
        "çözme usulü %r -- aday çoğaltan ``ara`` kolu KESİLDİ: okuma "
        "determinist olduğu için (ferman 2-Ĵ) ayna ile çoğaltılan "
        "adaylar birbirinin aynısı çıkıyordu; çeşitlilik zardan değil "
        "vecih spektrumundan gelir" % (usul,))
    uretilen, bedel, sukutlar, budanan = _cek()

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
            budanan=int(budanan), uzunluk=len(uretilen),
            sebep="TEÂRUZ: yakîn %.3f -- tez ile antitez denk kuvvette"
                  % float(_sp["μ"][0])))

    duz = 1.0 / float(taban)
    kesinlik = float(np.clip(
        (float(np.mean(guvenler)) - duz) / max(1.0 - duz, 1e-300),
        0.0, 1.0))
    if ort_sukut > kesinlik:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=uretilen, guven=float(np.mean(guvenler or [0.0])),
            budanan=int(budanan), uzunluk=len(uretilen),
            sebep="motorun sükût alanı %.3f, cevabın kesinlik nispeti "
                  "%.3f -- söylenecek şey susmak kadar bile kat'î değil"
                  % (ort_sukut, kesinlik)))

    kirp = (len(uretilen) // basamak) * basamak
    kimlik = ([int(t) for t in np.asarray(
        tipten(uretilen[:kirp], taban, basamak), int).reshape(-1)]
        if kirp else [])
    if not kimlik:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=[], guven=float(np.mean(guvenler or [0.0])),
            budanan=int(budanan), uzunluk=len(uretilen),
            sebep="üretilen %d basamak tek belirteç tamamlamadı "
                  "(basamak haddi %d)" % (len(uretilen), basamak)))

    return _bitir(Cevap(
        gorev=gorev.ad, sukut=False, sebep="",
        kural="motor (belirteç üretimi)",
        izgara=[np.asarray(kimlik, int)],
        belirtec=kimlik, uzunluk=len(uretilen),
        guven=float(np.mean(guvenler or [0.0])),
        budanan=int(budanan),
        tikaniklik=tik))
