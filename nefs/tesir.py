"""
Kademe 5 -- **icra izi, hassasiyet ve hata izolasyonu**.

Nizamnamenin beşinci kademesi tek bir soruyu makineye sordurur:

    Bu meleke akıştan çıkarılsa netice değişir mi?

Değişmiyorsa o meleke **bağlı değildir**. Dosyasında ne yazdığı,
kaç satır olduğu, ne kadar doğru olduğu bunu değiştirmez. Kütük H8'in
sayacı budur ve buradan okunur.

**Ölçü neden yalnız ``‖ΔN‖`` değil?**  İlk kurulumda öyleydi ve eksikti:
hüküm veren melekeler (𝒪₂₃ nakz, 𝒪₃₂ makam, 𝒪₁₃ mühür) sayı değil
**hüküm** üretir (kütük H4). Makamı Yakîn'den Şek'e çeviren bir meleke
kelamı tamamen susturur -- fakat sükût hâlinde ``N`` zaten sıfırdır, yani
``‖ΔN‖`` ölçüsü onu "tesirsiz" gösterebilirdi. Bu yüzden tesir
**bileşiktir**:

    tesir = ‖ΔN‖  ∨  makam değişti  ∨  sükût değişti  ∨  hüküm değişti
            ∨ nakz kümesi değişti

Bunlardan biri bile değiştiyse meleke tesirlidir. Hepsi aynı kaldıysa
meleke, akışta koşup hiçbir şeye dokunmuyor demektir.

**Hata izolasyonu.** Bazı melekeler düşürülünce akış kırılır (sözleşme
denetimi "şu alan boş" der). Bu bir kusur değil, **yapısal zaruret**tir:
o meleke olmadan sonrakiler koşamaz. Rapor bunları ayrı sayar.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .melekeler import AKIS, Nefs
from .melekeler import melekeler
from .melekeler import Durum

__all__ = ["Iz", "Tesir", "icra_izi", "netice_ozeti", "tesir_olc",
           "tesir_tablosu", "rapor"]


# =====================================================================
#  İcra izi
# =====================================================================
@dataclass
class Iz:
    """Bir melekenin bir koşudaki izi."""
    sira: int
    no: int
    ad: str
    sure_ms: float
    yazdigi: Tuple[str, ...]
    degisen: Tuple[str, ...]      # fiilen DEĞİŞEN alanlar (bildirdiği değil)


def _parmak_izi(d: Durum, alan: str) -> Any:
    """Bir alanın karşılaştırılabilir özeti."""
    v = getattr(d, alan, None)
    if v is None:
        return None
    if isinstance(v, np.ndarray):
        return (v.shape, float(np.sum(v * v)), float(np.sum(v)))
    if isinstance(v, (int, float, bool, str)):
        return v
    if isinstance(v, (list, tuple)):
        return repr(v)[:400]
    if isinstance(v, dict):
        return repr(sorted(v.items(), key=lambda kv: kv[0]))[:400]
    return repr(v)[:400]


_IZLENEN = ("X", "Z_hayal", "H_hayal", "Z_muhayyile", "sira", "U_k", "D",
            "S", "S_kebir", "K_vahime", "mu_mana", "parcalar",
            "tekil_degerler", "tenakuz", "G", "G_kebir", "Q_sual",
            "A_neden", "burhan", "M", "T", "P_idrak", "makam", "N",
            "sahitler", "kaideler", "kaide", "nakz", "sahit_agirliklari",
            "muteber_sahit", "tevafuk", "ispat", "hukum", "sukut",
            "tezat_kutbu", "w_kesit")


def icra_izi(E: np.ndarray, tohum: int = 0,
             sira: Sequence[int] = AKIS) -> Tuple[Durum, List[Iz]]:
    """Akışı koştur; her adımda **fiilen ne değişti** kaydet.

    Bildirilen ``yazar`` ile fiilen değişen alanın farkı mühimdir:
    sözleşme "yazacağım" der, iz "yazdı" der. İkisi ayrıştığında
    ya sözleşme dar ya meleke gizli tesir ediyor demektir.
    """
    nefs = Nefs(tohum, sira)
    d = Durum.kur(E)
    izler: List[Iz] = []
    onceki = {a: _parmak_izi(d, a) for a in _IZLENEN}
    for yer, no in enumerate(sira):
        m = nefs.s[no]
        t0 = time.perf_counter()
        m.kosu(d, nefs.p)
        dt = (time.perf_counter() - t0) * 1e3
        simdi = {a: _parmak_izi(d, a) for a in _IZLENEN}
        degisen = tuple(a for a in _IZLENEN if simdi[a] != onceki[a])
        onceki = simdi
        izler.append(Iz(yer, no, m.ad, dt, tuple(m.yazar), degisen))
    return d, izler


# =====================================================================
#  Hassasiyet: bir meleke düşünce ne değişir?
# =====================================================================
def netice_ozeti(d: Durum) -> Dict[str, Any]:
    """Neticenin, karşılaştırılabilir bütün yüzleri."""
    N = d.N if d.N is not None else np.zeros(1)
    return {
        "N": np.asarray(N, float).copy(),
        "makam": d.makam,
        "sukut": bool(d.sukut),
        "nakz": tuple(d.nakz) if d.nakz is not None else None,
        "mühür": bool((d.hukum or {}).get("mühür", False)),
        "T": float(d.T),
        "P_idrak": float(d.P_idrak),
    }


@dataclass
class Tesir:
    """Bir melekenin düşürülmesinin neticeye tesiri."""
    no: int
    ad: str
    kirildi: bool = False
    sebep: str = ""
    dN: float = 0.0
    makam_degisti: bool = False
    sukut_degisti: bool = False
    nakz_degisti: bool = False
    muhur_degisti: bool = False
    dP: float = 0.0

    @property
    def tesirli(self) -> bool:
        if self.kirildi:
            return True         # yapısal zaruret de bir tesirdir
        return (self.dN > 1e-12 or self.makam_degisti or self.sukut_degisti
                or self.nakz_degisti or self.muhur_degisti or self.dP > 1e-12)

    @property
    def hal(self) -> str:
        if self.kirildi:
            return "YAPISAL"
        return "tesirli" if self.tesirli else "TESİRSİZ"


def tesir_olc(E: np.ndarray, tohum: int = 0) -> Tuple[Dict[str, Any],
                                                      List[Tesir]]:
    """Her melekeyi sırayla düşür, neticeyi temelle karşılaştır."""
    nefs = Nefs(tohum)
    temel = netice_ozeti(nefs.idrak_et(E))

    sonuc: List[Tesir] = []
    for m in melekeler():
        eksik = tuple(x for x in AKIS if x != m.no)
        t = Tesir(no=m.no, ad=m.ad)
        try:
            d = Nefs(tohum, eksik).idrak_et(E)
        except Exception as e:                    # sözleşme denetimi vs.
            t.kirildi = True
            t.sebep = "%s: %s" % (type(e).__name__, str(e)[:90])
            sonuc.append(t)
            continue
        o = netice_ozeti(d)
        a, b = temel["N"], o["N"]
        if a.shape == b.shape:
            t.dN = float(np.linalg.norm(a - b))
        else:
            t.dN = float(np.linalg.norm(a) + np.linalg.norm(b))
        t.makam_degisti = o["makam"] != temel["makam"]
        t.sukut_degisti = o["sukut"] != temel["sukut"]
        t.nakz_degisti = o["nakz"] != temel["nakz"]
        t.muhur_degisti = o["mühür"] != temel["mühür"]
        t.dP = abs(o["P_idrak"] - temel["P_idrak"])
        sonuc.append(t)
    return temel, sonuc


def tesir_tablosu(sonuc: Sequence[Tesir]) -> Dict[str, Any]:
    tesirsiz = [t.no for t in sonuc if not t.tesirli]
    yapisal = [t.no for t in sonuc if t.kirildi]
    tesirli = [t.no for t in sonuc if t.tesirli and not t.kirildi]
    return {"toplam": len(sonuc), "tesirsiz": tesirsiz,
            "yapısal": yapisal, "tesirli": tesirli,
            "tesirsiz_oranı": len(tesirsiz) / max(len(sonuc), 1)}


# =====================================================================
def yapili_girdi(m: int = 4, t: int = 6, d_in: int = 12,
                 bozuk: Optional[int] = None, tohum: int = 0) -> np.ndarray:
    """Şahitli, **kurallı** girdi -- rastgele gürültü değil.

    Rastgele girdide bazı melekelerin yapacak işi yoktur (çelişki yok,
    kaide yok) ve "tesirsiz" ölçülürler. Bu, onların boş olduğunu değil,
    ölçünün sorduğu sorunun o girdide anlamsız olduğunu gösterir. Bu
    yüzden hassasiyet iki girdide birden ölçülür.

    ``bozuk`` verilirse o şahit başka bir kurala tâbidir; nakz onu
    yakalamalıdır.
    """
    rng = np.random.default_rng(tohum)
    R = np.linalg.qr(rng.normal(size=(d_in, d_in)))[0]
    R2 = np.linalg.qr(rng.normal(size=(d_in, d_in)))[0]
    bloklar = []
    for k in range(m):
        G = rng.normal(size=(t, d_in))
        C = G @ (R2 if k == bozuk else R).T
        bloklar.append(np.vstack([G, C + 6.0]) + 60.0 * k)
    return np.vstack(bloklar)


def rapor(tohum: int = 0, n: int = 40, d_in: int = 12,
          ayrinti: bool = True) -> str:
    # ASIL ÖLÇÜM yapılandırılmış girdide yapılır. Rastgele gürültüde
    # model -- doğru olarak -- **susar** (makam Şek → sükût), o hâlde
    # ``N`` zaten sıfırdır ve ``‖ΔN‖`` hiçbir melekeyi ayırt edemez;
    # o girdideki "tesirsiz" sayısı sükûtun gölgesidir, melekelerin
    # hâli değil. Rastgele girdi yine de raporlanır, fakat ikinci
    # sırada ve bu kayıtla.
    E = yapili_girdi(tohum=tohum)

    d, izler = icra_izi(E, tohum)
    satir = ["=== Kademe 5: icra izi ===",
             "adım: %d   şahit: %d   makam: %s   sükût: %s"
             % (len(izler), len(d.sahitler or []), d.makam, d.sukut)]
    sessiz = [iz for iz in izler if not iz.degisen]
    satir.append("hiçbir alanı değiştirmeyen adım: %d/%d  %s"
                 % (len(sessiz), len(izler), [iz.no for iz in sessiz]))
    gizli = [iz for iz in izler
             if set(iz.degisen) - set(iz.yazdigi) - {"tenakuz", "T",
                                                     "P_idrak", "makam",
                                                     "muteber_sahit",
                                                     "tevafuk", "sukut"}]
    satir.append("sözleşmesinde olmayan alanı değiştiren adım: %d  %s"
                 % (len(gizli), [(iz.no, tuple(set(iz.degisen)
                                               - set(iz.yazdigi)))
                                 for iz in gizli]))

    temel, sonuc = tesir_olc(E, tohum)
    t = tesir_tablosu(sonuc)
    satir += ["", "=== Kademe 5: hassasiyet (bir meleke düşerse) ===",
              "temel: ‖N‖=%.6f  makam=%s  sükût=%s  P=%.4f"
              % (float(np.linalg.norm(temel["N"])), temel["makam"],
                 temel["sukut"], temel["P_idrak"]),
              "tesirli: %d   yapısal zaruret: %d   TESİRSİZ: %d / %d"
              % (len(t["tesirli"]), len(t["yapısal"]),
                 len(t["tesirsiz"]), t["toplam"])]
    satir.append("tesirsiz melekeler: %s" % t["tesirsiz"])

    if ayrinti:
        satir += ["", "%-4s %-18s %-10s %10s %8s %s"
                  % ("𝒪", "ad", "hâl", "‖ΔN‖", "ΔP", "değişen hüküm")]
        satir.append("-" * 82)
        for x in sorted(sonuc, key=lambda z: (-z.dN, z.no)):
            hukumler = ",".join(
                a for a, v in (("makam", x.makam_degisti),
                               ("sükût", x.sukut_degisti),
                               ("nakz", x.nakz_degisti),
                               ("mühür", x.muhur_degisti)) if v) or "—"
            satir.append("%-4d %-18s %-10s %10.5f %8.4f %s"
                         % (x.no, x.ad, x.hal, x.dN, x.dP,
                            hukumler if not x.kirildi else x.sebep))

    # --- ikinci ölçümler
    ikinciler = [("bir şahit bozuk", yapili_girdi(bozuk=2, tohum=tohum)),
                 ("rastgele gürültü (model susar; ölçü ayırt etmez)",
                  np.random.default_rng(tohum).normal(size=(n, d_in)))]
    for etiket, E2 in ikinciler:
        d2 = Nefs(tohum).idrak_et(E2)
        temel2, sonuc2 = tesir_olc(E2, tohum)
        t2 = tesir_tablosu(sonuc2)
        satir += ["", "=== yapılandırılmış girdi: %s ===" % etiket,
                  "şahit=%d  nakz=%s  müteber=%.2f  P=%.4f  makam=%s  sükût=%s"
                  % (len(d2.sahitler or []), d2.nakz, d2.muteber_sahit,
                     d2.P_idrak, d2.makam, d2.sukut),
                  "tesirli: %d   yapısal: %d   TESİRSİZ: %d / %d  → %s"
                  % (len(t2["tesirli"]), len(t2["yapısal"]),
                     len(t2["tesirsiz"]), t2["toplam"], t2["tesirsiz"])]
    return "\n".join(satir)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
