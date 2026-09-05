"""
NİZAM -- kod tabanının **padişah bakışı**: kime kimin eli uzanıyor.

Kullanıcı hükmü: *"Sığ perspektiften çıkıp bir padişah gibi nizamlama
açısından baktığın zaman kodların asla bütünlüklü olmadığını,
birbiriyle kenetlenmeyen çokça kod bulunduğunu, birçok başıboş
padişahlık taslayan bulunduğunu... tek modelde tek padişah olması
gerektiğini ve padişahın elinin tüm kodlara uzanması gerektiğini
anlarsın."*

Bu dosya o bakışı **ölçer**, iddia etmez. Yaptığı üç şeydir:

1. **Tabiiyet haritası** -- her Python modülünün hangi modülleri içe
   aktardığı, ``ast`` ile (çalıştırmadan, tahminsiz).
2. **Padişahın eli** -- ana giriş noktalarından başlayarak *fiilen
   ulaşılabilen* modüller. Ulaşılamayan her modül **başıboş beyliktir**:
   kod tabanında durur, bakım ister, fakat ana modelin hiçbir icrasına
   girmez.
3. **Çok başlılık** -- aynı işi yapan ayrı hatlar (birden çok "akış",
   birden çok "eğitim", birden çok "yazmaç") tespit edilir.

Ölçü açıktır: bir modül ancak ana giriş noktasından bir içe aktarma
zinciriyle erişiliyorsa **tebaadır**; erişilmiyorsa beyliktir.
"""
from __future__ import annotations

import ast
import os
from typing import Dict, List, Optional, Sequence, Set, Tuple

__all__ = ["KOK", "GIRISLER", "modulleri_tara", "tabiiyet", "padisahin_eli",
           "rapor"]

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Ana giriş noktaları -- padişahın tahtı. Buradan erişilemeyen her şey
#: beyliktir. Liste kasten KISADIR: model tektir, girişi de tek olmalıdır.
#:
#: **ÖLÇÜLEN VE DÜZELTİLEN BAYATLIK (kütük H206).** ``main.kaggle`` bu
#: oturumda ``ogrenme.kaggle_donanim``a taşındı ve ``nefs.kulli_egitim``
#: silindi; varsayılan hâlâ eskiyi gösteriyordu. Bayat bir giriş
#: noktası, o noktadan erişilen her şeyi sessizce beylik sayardı.
#: **KÜME 9 -- ALTI TAHT BİRE İNDİ.** Buraya kadar liste altı girişliydi
#: ve bu, ölçüyü **kendi lehine** bozuyordu: ``main.kaggle_*``,
#: ``nefs.melekeler`` ve ``nefs.hukum_denetimi`` ayrı birer giriş
#: sayıldığı için, yalnız o ağaçlardan erişilen modüller de "tebaa"
#: görünüyordu. Padişahın hükmü sarihtir: **main tek hâkim.** O hâlde
#: giriş de ``main/`` olmalıdır; kaggle koşumu ve hüküm denetimi artık
#: ``main/egitim.py:taht`` kipleridir, ayrı taht değil.
GIRISLER: Tuple[str, ...] = (
    "main.egitim",           # taht: tâlim / kaggle / teftiş kipleri
    "main.cikarim",          # taht: çıkarım ve hüküm motoru
)


def _modul_adi(yol: str) -> str:
    bagil = os.path.relpath(yol, KOK)
    if bagil.endswith("__init__.py"):
        bagil = os.path.dirname(bagil)
    else:
        bagil = bagil[:-3]
    return bagil.replace(os.sep, ".")


#: **VERİ dizinleri -- kod sayılmaz.** Kullanıcı hükmü: *"ARC veri
#: dosyalarını zaten koddan sayman hata, onlar kalacak, senin onlarla
#: işin yok."* Haklıdır: ``idrak/veri/soyutlamalar`` altındaki
#: ``solution.py``ler ARC görevlerinin **tarifidir**, ana modelin
#: uzvu değildir. Onları "beylik" diye saymak, 45 933 satırlık sahte
#: bir borç göstermek olurdu.
VERI_DIZINLERI: Tuple[str, ...] = (
    os.path.join("idrak", "veri"),
)

#: **KOD OLMAYAN yahut ANA MODELİN UZVU OLMAYAN dizinler** (kullanıcı
#: hükmü H113). Bunları beylik saymak, olmayan bir borç göstermektir:
#:
#: * ``docs`` -- vesikalardır, kod değil. İçindeki ``.py``ler örnek ve
#:   izahtır; ana akışın uzvu olmaları beklenmez.
#: * ``mucit_ai_esas`` -- **ilham kaynağıdır**, uzuv değil. Kullanıcı
#:   hükmü: *"o ilham kaynağı, en son bakılacak ama kendisi beylik
#:   değil."* Ondan fikir devşirilecek, kendisi bağlanmayacak.
#: * ``yedek`` -- **terkibin şahididir**, uzuv değil. Usul gereği bir
#:   küme tek fonksiyona yükseltilirken artakalan asıllar imha
#:   edilmez, buraya konur (kütük H221) ki terkibin neyi yuttuğu elle
#:   görülebilsin. Çalıştırılmaz, çağrılmaz; bağlanması beklenmez.
HARİÇ_DIZINLER: Tuple[str, ...] = (
    "docs",
    "mucit_ai_esas",
    "yedek",
)


def _veri_mi(yol: str) -> bool:
    b = os.path.relpath(yol, KOK)
    return (any(b.startswith(v + os.sep) for v in VERI_DIZINLERI)
            or any(b == d or b.startswith(d + os.sep)
                   for d in HARİÇ_DIZINLER))


def modulleri_tara(kok: str = KOK) -> Dict[str, str]:
    """Bütün Python modülleri: ``ad → yol``. **Veri dizinleri hariç.**"""
    out: Dict[str, str] = {}
    for dizin, altlar, dosyalar in os.walk(kok):
        altlar[:] = [d for d in altlar
                     if d not in (".git", "__pycache__", ".ipynb_checkpoints")]
        if _veri_mi(os.path.join(dizin, "x")):
            continue
        for d in dosyalar:
            if d.endswith(".py"):
                y = os.path.join(dizin, d)
                out[_modul_adi(y)] = y
    return out


def _ice_aktarilanlar(yol: str, kendi: str) -> Set[str]:
    try:
        with open(yol, encoding="utf-8") as f:
            agac = ast.parse(f.read(), filename=yol)
    except Exception:
        return set()
    paket = kendi.rsplit(".", 1)[0] if "." in kendi else ""
    out: Set[str] = set()
    for d in ast.walk(agac):
        if isinstance(d, ast.Import):
            for a in d.names:
                out.add(a.name)
        elif isinstance(d, ast.ImportFrom):
            if d.level:                       # göreli içe aktarma
                kok_p = paket
                for _ in range(d.level - 1):
                    kok_p = kok_p.rsplit(".", 1)[0] if "." in kok_p else ""
                tam = "%s.%s" % (kok_p, d.module) if d.module else kok_p
            else:
                tam = d.module or ""
            if tam:
                out.add(tam)
                for a in d.names:
                    out.add("%s.%s" % (tam, a.name))
    return out


def tabiiyet(moduller: Optional[Dict[str, str]] = None
             ) -> Dict[str, Set[str]]:
    """``ad → içe aktardığı YEREL modüller``."""
    moduller = moduller or modulleri_tara()
    kume = set(moduller)
    out: Dict[str, Set[str]] = {}
    for ad, yol in moduller.items():
        ham = _ice_aktarilanlar(yol, ad)
        yerel = {x for x in ham if x in kume}
        # ``a.b.c`` biçiminde gelen ve ``a.b`` modülü olan hâller
        for x in ham:
            p = x
            while "." in p:
                p = p.rsplit(".", 1)[0]
                if p in kume:
                    yerel.add(p)
                    break
        out[ad] = yerel - {ad}
    return out


def padisahin_eli(girisler: Sequence[str] = GIRISLER,
                  tab: Optional[Dict[str, Set[str]]] = None,
                  gecilmez: Sequence[str] = ()) -> Set[str]:
    """Giriş noktalarından **fiilen erişilen** modüller (geçişli kapanış).

    ``gecilmez``: bu önekteki modüller kapanışa **girer ama üzerinden
    geçilmez**. Niçin lâzım (KÜME 9'da ölçülen tuzak): ``tanilama/``
    hekimdir ve ``divan.py`` bütün tebaayı içe aktarır. Taht hekimi
    çağırır çağırmaz, hekimin ithal ettiği HER modül "tahttan erişilir"
    görünür ve ölçü 94'te 91 der -- yani hiçbir şey demez. Muayene
    edilmek, ana akışta iş görmek değildir. O hâlde hekim bir **yaprak**
    sayılır: kendisi tebaadır, tanıdıkları değil.
    """
    tab = tab or tabiiyet()
    gecilmez = tuple(gecilmez)

    def durak(x: str) -> bool:
        return any(x == g or x.startswith(g + ".") for g in gecilmez)

    goruldu: Set[str] = set()
    yigin = [g for g in girisler if g in tab]
    while yigin:
        x = yigin.pop()
        if x in goruldu:
            continue
        goruldu.add(x)
        if durak(x):
            continue
        yigin.extend(tab.get(x, set()) - goruldu)
    return goruldu


def _satir(yol: str) -> int:
    try:
        with open(yol, encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def rapor() -> str:
    mod = modulleri_tara()
    tab = tabiiyet(mod)
    tebaa = padisahin_eli(GIRISLER, tab)
    beylik = sorted(set(mod) - tebaa)

    t_satir = sum(_satir(mod[m]) for m in tebaa)
    b_satir = sum(_satir(mod[m]) for m in beylik)

    s = ["=== NİZAM: padişahın eli nereye uzanıyor? ===", "",
         "toplam modül : %d   (%d satır)" % (len(mod), t_satir + b_satir),
         "TEBAA        : %d   (%d satır, %%%.0f)"
         % (len(tebaa), t_satir, 100 * t_satir / max(t_satir + b_satir, 1)),
         "BEYLİK       : %d   (%d satır, %%%.0f)  ← ana modelin eli"
         " UZANMIYOR"
         % (len(beylik), b_satir,
            100 * b_satir / max(t_satir + b_satir, 1)),
         "",
         "Giriş noktaları (taht): " + ", ".join(GIRISLER),
         ""]

    # beylikleri üst dizine göre topla
    obek: Dict[str, List[str]] = {}
    for m in beylik:
        ust = m.split(".")[0]
        obek.setdefault(ust, []).append(m)
    s.append("BEYLİKLER (üst dizine göre, satır sayısıyla):")
    for ust in sorted(obek, key=lambda u: -sum(_satir(mod[m])
                                               for m in obek[u])):
        n = sum(_satir(mod[m]) for m in obek[ust])
        s.append("  %-22s %3d modül  %6d satır" % (ust, len(obek[ust]), n))

    # çok başlılık: aynı isimli/işlevli modüller
    s += ["", "ÇOK BAŞLILIK (aynı işi yapan ayrı hatlar):"]
    anahtar = ("akis", "egitim", "yazmac", "meleke", "model", "main",
               "kubit", "arc", "optimize")
    for a in anahtar:
        ayni = sorted(m for m in mod if m.split(".")[-1] == a
                      or m.split(".")[-1].startswith(a))
        if len(ayni) > 1:
            isaret = ["%s%s" % (m, "" if m in tebaa else " (beylik)")
                      for m in ayni]
            s.append("  %-10s → %s" % (a, ", ".join(isaret)))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
