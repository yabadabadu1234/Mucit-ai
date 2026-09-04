"""
İLLET -- akışın **sebep çizgesi** kurulur ve `fitrat/ayrisma.py` ile tartılır.

===================================================================
NİÇİN KURULABİLİYOR
===================================================================

`nefs/sozlesme.py` (kütük H119) her melekenin dokunacağı bölgeleri
**ilan** ettirir ve ölçüm o ilanı dalgayla yüzleştirir -- 41 melekede
sıfır ihlâl. O hâlde elimizde bir şey var: akışın hangi adımının hangi
alana dokunduğu, **iddia değil ölçülmüş** bir bilgi.

``QAKIS`` sırası da bellidir. İkisi birleşince akışın **sebep çizgesi**
çıkar:

    meleke_t bir alana dokunuyorsa, o alanın SONRAKİ hâli
    meleke_t'nin dokunduğu bütün alanların ÖNCEKİ hâline bağlıdır.

Bu bir benzetme değil, akışın fiilî bağımlılık yapısıdır.

===================================================================
𝒪₂₂'NİN İDDİASI
===================================================================

`nefs/qmeleke.py`, 𝒪₂₂ İllet Keşfi için şöyle diyor:

> *"Nedensellik simetrik değildir; sebep sonuçtan öncedir… **Asiklik
> şartı inşa gereği sağlanır** -- kapı hep soldan sağadır."*

Son cümle bir **iddia**dır ve tek bir meleke için doğrudur. Fakat
sorulmayan sual şudur: **bütün akışın** sebep çizgesi asiklik mi?
41 meleke sırayla koşuyor ve aynı alana defalarca dönüyor; zaman
açılımında (her adım ayrı düğüm) asiklik cebren sağlanır, fakat
**alan seviyesinde** -- yani "hangi alan hangi alanı etkiliyor" --
çevrim pekâlâ olabilir ve olması da normaldir.

İkisi ayrı sualdir ve burada **ikisi de** ölçülür. Birini ötekinin
yerine koymak, iddiayı ispatlanmış göstermek olurdu.

===================================================================
ASIL KIYMET: d-AYRIŞMASI
===================================================================

`fitrat/ayrisma.py` beylikti ve tam da bunu ölçer: ``X ⫫_d Y | Z``.
Zaman açılımlı çizgede mimarî bir şart sınanabilir:

    ``kelam``, ``veri``den **yalnız hüküm üzerinden** mi besleniyor?

**Ve burada kendi hükmümü daraltmam gerekti.** Ölçüm "hükmü atlayan
yol var" dedi ve ilk yazdığım şerh *"mimarînin gerekçesi delinmiş"*
diyordu. **Bu fazla söylemekti.** `nefs/zihin_durumu.py`nin kelam hakkındaki
iddiası şudur: *"kelam ``|0⟩``dan başlayıp yalnız beyan melekelerinin
yazdığı bir alandır"* -- ve o iddia **doğrudur** (kelama yalnız
𝒪₃₇–𝒪₄₁ dokunuyor). Mimarî, "veriden kelama giden yol hükümden
geçmelidir" diye bir şey **iddia etmemişti**; o şartı ben koydum.

O hâlde burada ölçülen şey bir kusur değil, bir **tasarım
hakikatidir** ve karar kullanıcınındır:

    𝒪₃₇ Fesâhat, 𝒪₃₈ Talâkat ve 𝒪₄₀ Sanat, aynı üniter içinde hem
    ``veri``ye hem ``kelam``a dokunuyor -- yani beyan, hükme uğramadan
    da veriden besleniyor.

Bunun istenip istenmediği mimarî bir tercihtir. Ölçüm onu görünür
kılar; hükmü vermez.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from matematik.fitrat import Cizge, tesir_kapali_mi

__all__ = ["alan_cizgesi", "zaman_cizgesi", "cevrimler", "kelam_ayrismasi",
           "rapor"]

#: Hüküm taşıyan alanlar -- ``veri``den ``kelam``a giden yolun geçmesi
#: **beklenen** yer. ``yerel`` de hükümdür (satır hakkındaki hüküm).
HUKUM_ALANLARI: Tuple[str, ...] = (
    "yerel", "makam", "mizan", "tenakuz", "tasdik", "sukut", "nakz",
    "gaye", "tertip",
)


def _melekelerin_bolgeleri() -> List[Tuple[int, Tuple[str, ...]]]:
    """``QAKIS`` sırasında her adımın dokunduğu bölgeler -- sözleşmeden."""
    from .melekeler import QAKIS
    from .kulli_kayip import SOZLESME
    return [(no, SOZLESME[no][0]) for no in QAKIS]


def alan_cizgesi() -> Tuple[List[str], List[Tuple[str, str]], bool]:
    """**Alan seviyesinde** sebep çizgesi: hangi alan hangisini etkiliyor.

    ``(düğümler, kenarlar, Cizge_kabul_etti_mi)`` döner.

    **Niçin ``Cizge`` değil.** `fitrat/ayrisma.py`nin ``Cizge`` tipi
    çevrimli bir çizgeyi **reddeder** (*"çizge çevrimli -- d-ayrışması
    tanımsız"*) ve haklıdır: d-ayrışması yönlü **asiklik** çizgede
    tanımlıdır. Bu red, bizzat aradığımız ölçümün makine teyididir --
    akışın alan seviyesindeki sebep yapısı **çevrimlidir**. Kurulmaya
    çalışılır, reddedilirse o red raporlanır.
    """
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
        kabul = False          # çevrimli: d-ayrışması tanımsız
    return dugumler, ken, kabul


def zaman_cizgesi() -> Tuple[Cizge, Dict[str, List[str]]]:
    """**Zaman açılımlı** sebep çizgesi -- her adımda alanın ayrı düğümü.

    ``alan@t`` düğümü, ``t``inci adımdan **sonraki** hâlidir. Kenarlar:

    * ``alan@t → alan@t+1``      -- kendi geçmişi (bütün alanlar için),
    * ``a@t → b@t+1``            -- ``t+1``inci meleke ikisine de
      dokunuyorsa (aynı üniter içinde dolaşırlar).

    Bu çizge **cebren asikliktir** (zaman ileri akar) ve o yüzden
    "asiklik ispatlandı" diye bir hüküm çıkarılmaz; asıl kıymeti
    d-ayrışması sorulabilmesidir.
    """
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
    """Çizgede çevrim var mı? -- derinlik önce arama ile."""
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
    """``kelam``, ``veri``den **yalnız hüküm üzerinden** mi besleniyor?

    Zaman açılımlı çizgede sorulur: ``veri@0`` ile ``kelam@T``,
    hüküm alanlarının bütün zaman dilimlerine şart koşulduğunda
    d-ayrık mı?

    Ayrıksa mimarînin gerekçesi tutuyor: beyan, hükümden geçmeden
    veriden beslenmiyor. Ayrık değilse **hükmü atlayan bir yol** var
    demektir ve kelamı ayırma gerekçesi delinmiştir.
    """
    g, yer = zaman_cizgesi()
    if "kelam" not in yer or "veri" not in yer:
        return {"kurulabilir": False}
    T = len(yer["kelam"]) - 1
    Z: List[str] = []
    for a in HUKUM_ALANLARI:
        Z += yer.get(a, [])
    ayrik = bool(tesir_kapali_mi(g, [yer["veri"][0]], [yer["kelam"][T]], Z))
    # Şartsız hâl: hüküm alanlarına şart koşulmazsa elbette bağlıdır;
    # bu, ölçütün kör olmadığının şahididir.
    ayrik_sartsiz = bool(tesir_kapali_mi(g, [yer["veri"][0]],
                                    [yer["kelam"][T]], []))
    # Doğrudan yolu açan melekeler: aynı ilanda hem ``veri`` hem ``kelam``.
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


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
