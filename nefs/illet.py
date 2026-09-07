from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from matematik.fitrat import Cizge, gecer_mi

__all__ = ["alan_cizgesi", "zaman_cizgesi", "cevrimler", "kelam_ayrismasi",
           "rapor"]

HUKUM_ALANLARI: Tuple[str, ...] = (
    "yerel", "makam", "mizan", "tenakuz", "tasdik", "sukut", "nakz",
    "gaye", "tertip",
)


def _melekelerin_bolgeleri() -> List[Tuple[int, Tuple[str, ...]]]:
    from .melekeler import QAKIS
    from .kulli_kayip import SOZLESME
    return [(no, SOZLESME[no][0]) for no in QAKIS]


def alan_cizgesi() -> Tuple[List[str], List[Tuple[str, str]], bool]:
    adimlar = _melekelerin_bolgeleri()
    dugumler: List[str] = []
    kenarlar: Set[Tuple[str, str]] = set()
    for _, bolg in adimlar:
        for a in bolg:
            if a not in dugumler:
                dugumler.append(a)
        for a in bolg:
            for b in bolg:
                if a != b:
                    kenarlar.add((a, b))
    ken = sorted(kenarlar)
    try:
        Cizge(tuple(dugumler), tuple(ken))
        kabul = True
    except ValueError:
        kabul = False
    return dugumler, ken, kabul


def zaman_cizgesi() -> Tuple[Cizge, Dict[str, List[str]]]:
    adimlar = _melekelerin_bolgeleri()
    alanlar = sorted({a for _, b in adimlar for a in b})
    T = len(adimlar)
    dug: List[str] = []
    yer: Dict[str, List[str]] = {a: [] for a in alanlar}
    for t in range(T + 1):
        for a in alanlar:
            ad = "%s@%d" % (a, t)
            dug.append(ad)
            yer[a].append(ad)
    ken: Set[Tuple[str, str]] = set()
    for t in range(T):
        for a in alanlar:
            ken.add(("%s@%d" % (a, t), "%s@%d" % (a, t + 1)))
        bolg = adimlar[t][1]
        for a in bolg:
            for b in bolg:
                if a != b:
                    ken.add(("%s@%d" % (a, t), "%s@%d" % (b, t + 1)))
    return Cizge(tuple(dug), tuple(sorted(ken))), yer


def cevrimler(dugumler: Sequence[str],
              kenarlar: Sequence[Tuple[str, str]]) -> List[List[str]]:
    cocuk: Dict[str, Set[str]] = {}
    for a, b in kenarlar:
        cocuk.setdefault(a, set()).add(b)
    beyaz, gri, siyah = set(dugumler), set(), set()
    bulunan: List[List[str]] = []

    def git(u: str, yol: List[str]) -> None:
        beyaz.discard(u)
        gri.add(u)
        for v in sorted(cocuk.get(u, ())):
            if v in gri:
                bulunan.append(yol[yol.index(v):] + [v] if v in yol
                               else [u, v])
            elif v in beyaz:
                git(v, yol + [v])
        gri.discard(u)
        siyah.add(u)

    for u in sorted(dugumler):
        if u in beyaz:
            git(u, [u])
    return bulunan


def kelam_ayrismasi() -> Dict[str, object]:
    g, yer = zaman_cizgesi()
    if "kelam" not in yer or "veri" not in yer:
        return {"kurulabilir": False}
    T = len(yer["kelam"]) - 1
    Z: List[str] = []
    for a in HUKUM_ALANLARI:
        Z += yer.get(a, [])
    ayrik = bool(gecer_mi(g, [yer["veri"][0]], [yer["kelam"][T]], Z))
    ayrik_sartsiz = bool(gecer_mi(g, [yer["veri"][0]],
                                    [yer["kelam"][T]], []))
    from .melekeler import QAKIS, qsicil
    from .kulli_kayip import SOZLESME
    sic = qsicil()
    dogrudan = [(no, sic[no].ad) for no in dict.fromkeys(QAKIS)
                if "veri" in SOZLESME[no][0] and "kelam" in SOZLESME[no][0]]
    return {"kurulabilir": True, "adım": T,
            "doğrudan_melekeler": dogrudan,
            "hüküm_şartıyla_ayrık": ayrik,
            "şartsız_ayrık": ayrik_sartsiz,
            "şart_kümesi": len(Z)}


def rapor() -> str:
    dug, ken, kabul = alan_cizgesi()
    ac = cevrimler(dug, ken)
    zg, yer = zaman_cizgesi()
    zc = cevrimler(zg.dugumler, zg.kenarlar)
    ka = kelam_ayrismasi()

    s = ["=== İLLET -- akışın sebep çizgesi (fitrat/ayrisma.py ile) ===",
         "",
         "Çizge `nefs/sozlesme.py`nin ÖLÇÜLMÜŞ bölge ilanlarından ve",
         "``QAKIS`` sırasından kuruldu; uydurulmadı.",
         "",
         "𝒪₂₂'nin iddiası: *'Asiklik şartı inşa gereği sağlanır.'*",
         "Bu tek bir meleke için doğrudur. Bütün akış için iki ayrı",
         "sual vardır ve ikisi de ölçülür:",
         "",
         "  ALAN seviyesinde (hangi alan hangisini etkiliyor):",
         "    düğüm %d, kenar %d, çevrim: %d"
         % (len(dug), len(ken), len(ac)),
         "    fitrat/ayrisma.Cizge kabul etti mi: %s" % kabul,
         "    → çevrim VAR ve olması normaldir: akış aynı alana",
         "      defalarca döner. 'Akış asikliktir' demek burada YANLIŞ",
         "      olurdu." if ac else
         "    → çevrim yok.",
         "",
         "  ZAMAN açılımında (her adımda alanın ayrı düğümü):",
         "    düğüm %d, kenar %d, çevrim: %d"
         % (len(zg.dugumler), len(zg.kenarlar), len(zc)),
         "    → asiklik CEBREN sağlanır (zaman ileri akar); bu bir",
         "      ispat değil bir tariftir ve öyle sayılır.",
         ""]

    s.append("KELAM AYRIŞMASI -- mimarînin gerekçesi tutuyor mu?")
    if not ka.get("kurulabilir"):
        s.append("  çizge kurulamadı")
    else:
        s += ["  `kelam` ayrı bir alandır çünkü veri kübitlerinin",
              "  marjinali dolaşıklık yüzünden düzgündür (H43). Şart:",
              "  beyan, veriden HÜKÜM ÜZERİNDEN beslensin.",
              "",
              "    adım sayısı              : %d" % ka["adım"],
              "    şart kümesi (hüküm@t)    : %d düğüm" % ka["şart_kümesi"],
              "    hüküm şartıyla d-ayrık   : %s" % ka["hüküm_şartıyla_ayrık"],
              "    şartsız d-ayrık          : %s  (False olmalı -- ölçüt kör değil)"
              % ka["şartsız_ayrık"],
              ""]
        if ka["hüküm_şartıyla_ayrık"]:
            s += ["  NETİCE: veriden kelama giden her yol hükümden geçiyor;",
                  "  beyan hükmü atlayamıyor."]
        else:
            s += ["  NETİCE: veriden kelama, hüküm alanlarını ATLAYAN bir",
                  "  yol var. Sebebi tek tek izlenebilir:"]
            for no, ad in ka.get("doğrudan_melekeler", ()):
                s.append("    𝒪%-3d %s -- aynı ünitede hem veri hem kelam"
                         % (no, ad))
            s += ["",
                  "  **Bu bir KUSUR değildir ve öyle denmiyor.** Mimarînin",
                  "  kelam hakkındaki iddiası *'yalnız beyan melekeleri",
                  "  yazar'*dır ve o iddia DOĞRU. 'Yol hükümden geçmeli'",
                  "  şartını ben koydum; mimarî onu iddia etmemişti.",
                  "  Ölçüm tasarım hakikatini görünür kılar, hükmü vermez --",
                  "  beyanın hükme uğramadan veriden beslenmesi istenir mi,",
                  "  bu kullanıcının kararıdır."]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
