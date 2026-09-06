"""ÇIKARIM -- tahtın ikinci kapısı: **cevabı motor verir.**

===================================================================
PADİŞAHIN FERMANI, İKİNCİ KISIM
===================================================================

*"ARC yalnız llm motoruyla çözülecek, başka herhangi bir şeyle
değil."*

Bu dosya evvelce 927 satırlık bir **görev başına öznitelik
mühendisliğiydi**: `baglam_cikar`, `ozellik`, `nesne_ozellikleri`,
`hendese_adaylari`, `sahit_cogalt`, `_d4`, `_tuval`, `dalga_kur`,
`KulliHukumMotoru`. Elle kurulmuş öznitelikler üstünde her görev için
ayrı bir dalga/ridge öğrenicisi koşuyor, kütük de "ARC görevlerini
fiilen çözen hat budur" diye onu gösteriyordu.

**O hat fermanla tasfiye edildi.** Öğrenilmiş olması onu meşru
kılmıyordu: öznitelikler elle kuruluyordu ve ARC'ye mahsustu; yâni
çözen yine motor değil, benim ARC hakkındaki tahminlerimdi.

Aslı **İMHA EDİLDİ.** Evvelce burada "yedek/ altında duruyor, imha yok
cevher toplama var" yazıyordu; o dizin fermanla silindi ve şerhi
düzeltmeden bırakmak, olmayan bir dosyayı işaret eden bir yalan
olurdu: *"yasaklanan ne kadar usul varsa hepsini imha edeceksin."*

===================================================================
ÇIKARIM TÂLİMİN AĞIRLIĞINI KULLANIR
===================================================================

Bu kapı evvelde ``QNefs``i **taze** kuruyordu: yâni tâlim saatlerce
koşuyor, kazandığı parametre bir dosyaya bile yazılmıyor, çıkarım da
hiç öğrenmemiş bir nefsi koşturuyordu. Ölçü "motor çözemedi" diyordu
ama koşan zaten eğitilmemiş motordu.

Artık ``main/hazine.py``den (safetensors) son ağırlık okunur ve
``nefs.yukle`` ile yerine konur. Ağırlık yoksa bu **sessizce**
geçilmez: ``ham=True`` denmedikçe hata verir, çünkü eğitilmemiş bir
motorun neticesini "çıkarım" diye raporlamak ölçüyü yalanlamaktır.

Gerisi budur: bağlamı kur, motoru koştur, belirteç belirteç üret,
sükût hakkını sakla. Hepsi `nefs/soyle.py`ye havale edilir --
burada yeni riyaziye yoktur.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys                                               # noqa: E402
import time                                              # noqa: E402
from typing import Dict, List, Optional, Sequence        # noqa: E402

import numpy as np                                       # noqa: E402

from nefs.musahede import gorevleri_getir                # noqa: E402
# **USUL FERMANI:** bu satır ``nefs/hafiza.py`` HENÜZ YOKKEN yazıldı.
# Çağrı evvel, uzuv sonra (docs/zabit/USUL_UMUMIDEN_HUSUSIYE.md).
from nefs.hafiza import Hafiza                           # noqa: E402
# **USUL FERMANI:** bu iki satır ``nefs/sadakat.py`` ve ``nefs/suphe.py``
# HENÜZ YOKKEN yazıldı.
#
# **MANTIĞA SADAKAT ÇIKARIMDA DA KOŞAR -- VE KOŞMASI ŞARTTIR.**
# Zabıt: *"Bütün melekelerin 7/24, her adımda ve HER UZAYDA uymak
# zorunda olduğu sarsılmaz kanundur."* Yalnız tâlimde koşan bir sadakat,
# 7/24 değildir: model eğitilirken mantıklı, konuşurken serbest olurdu.
# Onun için zemin ``QNefs.idrak_et``e bağlandı -- tâlimin de çıkarımın
# da tek geçtiği yer orasıdır -- ve burada **hesabı sorulur**.
#
# Şüphe manifoldu da çıkarımda iş görür: teâruz hâlinde (``P`` ile
# ``¬P`` denk kuvvette) model hüküm vermez, **susar**. Sükût hakkı
# burada bir kaide değil, bir ölçünün neticesidir.
from nefs.sadakat import sadakat_beyani                  # noqa: E402
from nefs.suphe import suphe_beyani                      # noqa: E402
# **FERMAN 1-G:** raporun yeri taht değil, kendi uzvudur.
from tanilama.beyan import cikarim_beyani                # noqa: E402

__all__ = ["padisah", "degerlendirme_kosusu", "hazineden_yukle",
           "hafizayi_yukle", "kos"]


def hafizayi_yukle(ayar, dizin: Optional[str] = None) -> "Hafiza":
    """TÂLİMDE BİRİKEN KUANTUM HAFIZASINI GERİ ÇAĞIR (``nefs/hafiza.py``).

    **AĞIRLIK HAFIZA DEĞİLDİR.** Ağırlıklar fıtrattır: gramer, refleks,
    mantık terazisi. Tâlim boyunca cerhedilen safsatalar ve tasdik edilen
    meşru teemmüller ise ayrı bir yoğunluk operatöründe (``ρ_Hafıza``)
    birikir ve hazineye ``hafıza.*`` tensörleri olarak yazılır.

    Çıkarımda bu hafıza **Zeno budaması** için lâzımdır: model daha evvel
    cerhedilmiş bir mantık koluna girmeye başladığı an, döngüyü
    tamamlamadan o kol kesilir. Hafızasız çıkarım, aynı safsataya her
    seferinde yeniden düşmektir.
    """
    from main import hazine
    from main.egitim import HAZINE_DIZINI
    d = dizin or HAZINE_DIZINI
    yol = os.path.join(d, "dimag_%s" % ayar.ad)
    agirlik, ust = hazine.al(yol)
    h = Hafiza.hazineden(agirlik, ust)
    assert h is not None, "hafıza kurulamadı -- boş bir şey dönemez"
    return h


def hazineden_yukle(nefs, ayar, dizin: Optional[str] = None,
                    ham: bool = False) -> Dict[str, object]:
    """TÂLİMİN KAZANDIĞINI YERİNE KOY (``main/hazine.py``).

    ``depo/hazine/dimag_<ayar>.safetensors`` aranır. Bulunursa
    ``p`` tensörü okunur, boyu denetlenir ve ``nefs.yukle`` ile
    parametreye basılır.

    ``ham`` doğruysa ağırlık aranmaz ve **öyle olduğu döner**; bu kip
    yalnız "eğitilmemiş motor ne yapıyor" ölçümü içindir. Varsayılan
    değildir: eğitilmemiş bir motoru çıkarım diye raporlamak, ölçüyü
    yalanlamaktır.
    """
    from main import hazine
    from main.egitim import HAZINE_DIZINI
    if ham:
        return {"yüklendi": False, "sebep": "ham kip istendi", "yol": None}
    d = dizin or HAZINE_DIZINI
    yol = os.path.join(d, "dimag_%s" % ayar.ad)
    tam = yol + hazine.UZANTI
    assert os.path.exists(tam), (
        "HAZİNE YOK: %s\n  Evvela tâlimi koşturun (``python -m main.egitim "
        "tâlim %s``). Eğitilmemiş motorla çıkarım yapıp neticeyi rapora "
        "yazmak ölçüyü yalanlamaktır; onun için burası sessizce "
        "geçilmiyor." % (tam, ayar.ad))
    agirlik, ust = hazine.al(yol)
    assert "p" in agirlik, "hazinede ``p`` tensörü yok: %r" % sorted(agirlik)
    p = np.array(agirlik["p"], dtype=float).reshape(-1)
    assert p.size == len(nefs), (
        "hazinedeki parametre %d, nefsinki %d -- ayar değişmiş olmalı"
        % (p.size, len(nefs)))
    assert np.all(np.isfinite(p)), "hazinedeki parametrede NaN/Inf var"
    nefs.yukle(p)
    return {"yüklendi": True, "yol": tam, "parametre": int(p.size),
            "üst_veri": ust}


def _motor(ayar=None, ham: bool = False):
    """Tâlim motorunu kur, **hazineyi ve hafızayı** yerine koy.

    Tek yerde; iki kapı aynı nefsi, aynı ağırlığı, aynı hafızayı
    kullansın.
    """
    from main.egitim import KISA_CPU
    from nefs.melekeler import QNefs
    a = ayar or KISA_CPU
    nefs = QNefs(a.tohum, a.qayar())
    nefs.idrak_et(np.zeros((2, a.veri_lifi)))
    # **KADEME PARAMETRELERİ BURADA DA AÇILIR.** Tâlim onları açıyor
    # (``main/egitim.py``, ``kademe_parametreleri_ac``) ve hazineye 324
    # sayı yazıyordu; çıkarım açmayınca 318 kuruyor ve yükleme
    # ``AssertionError`` veriyordu. Yâni çıkarım, eğitilmiş bir hazineyi
    # **hiç yükleyemezdi**. Ölçüldü (324 ≠ 318) ve düzeltildi: iki kapı
    # aynı nefsi kurmak zorundadır, yoksa "aynı ağırlık" iddiası boştur.
    from nefs.kulli_kayip import kademe_parametreleri_ac
    kademe_parametreleri_ac(nefs.p)
    yuk = hazineden_yukle(nefs, a, ham=ham)
    # Fıtrat (ağırlık) ile hadise (hafıza) AYRI iki şeydir; ikisi ayrı
    # yüklenir. Ham kipte ikisi de yoktur ve bu açıkça söylenir.
    haf = None if ham else hafizayi_yukle(a)
    if haf is not None:
        yuk["hafıza"] = haf.beyan()
    return nefs, a, yuk, haf


def padisah(gorev, nefs=None, ayar=None, **kw) -> Dict[str, object]:
    """Bir göreve cevap ver -- **yalnız motorla**.

    Eski ``padisah`` görev başına dalga öğrenicisi koşturuyordu ve
    ``kw`` ile ``devir``, ``azami_aday``, ``loo_devir`` gibi arama
    bütçeleri alıyordu. Onlar artık yok; imza uyumluluk için ``kw``
    yutar ve **yuttuğunu söyler**.
    """
    from nefs.soyle import soyle
    hafiza = kw.pop("hafiza", None)
    if nefs is None:
        nefs, ayar, _, hafiza = _motor(ayar)
    # **ZENO BUDAMASI ÇIKARIMDA İŞ GÖRÜR.** Üretim sırasında model daha
    # evvel cerhedilmiş (``T=0``) bir mantık koluna girerse, o kol daha
    # döngü tamamlanmadan kesilir. Hafıza verilmezse budama yoktur ve
    # ölçü bunu görür -- kapatılabilen bir tesirdir (H90).
    c = soyle(gorev, nefs=nefs, sozluk=(ayar.sozluk if ayar else 16),
              hafiza=hafiza)
    return {"görev": getattr(gorev, "ad", ""),
            "sükût": bool(c.sukut),
            "sebep": c.sebep,
            "kural": c.kural,
            "belirteç": c.belirtec,
            "güven": float(c.guven),
            "budanan": int(getattr(c, "budanan", 0)),
            "yutulan_ayar": sorted(kw) or None}


def degerlendirme_kosusu(kume: str = "training", azami: int = 24,
                         ayar=None, ham: bool = False) -> Dict[str, object]:
    """Küme üstünde **tam eşleşme** ölçümü. Ölçüt sert kalır.

    Sınama çıktısı motora hiç gösterilmez; yalnız burada, ölçüm
    anında kıyaslanır. Gösterildiği an ölçü yalan olur.
    """
    from nefs.musahede import gorev_dizisi
    nefs, a, yuk, hafiza = _motor(ayar, ham=ham)
    gorevler = list(gorevleri_getir(kume))[:int(azami)]
    assert gorevler, "değerlendirilecek görev BOŞ -- ölçü bir şey ölçmüyor"
    deneme = cozulen = konusan = budanan = 0
    hucre: List[float] = []
    t0 = time.perf_counter()
    for g in gorevler:
        r = padisah(g, nefs=nefs, ayar=a, hafiza=hafiza)
        deneme += 1
        if r["sükût"]:
            continue
        konusan += 1
        budanan += int(r.get("budanan", 0))
        # ``except`` KALDIRILDI (ferman): hedef dizisi kurulamıyorsa
        # o görev sessizce ölçüden düşüyordu, yâni ölçü kendi
        # paydasını gizlice küçültüyordu.
        _, hedef = gorev_dizisi(g)
        assert len(hedef) > 0, "görev %r için hedef BOŞ" % getattr(g, "ad", "")
        h = [int(x) % a.sozluk for x in hedef]
        u = list(r["belirteç"] or [])
        n = min(len(h), len(u))
        if n:
            hucre.append(sum(1 for i in range(n) if h[i] == u[i]) / n)
        if u[:len(h)] == h:
            cozulen += 1
    # **7/24 ZEMİNİN HESABI ÇIKARIMDA DA SORULUR.** Sayaç ``idrak_et``te
    # artar; sıfırsa sadakat bu uzayda koşmamış demektir ve o zaman
    # "her uzayda" iddiası yalan olur -- onun için burada durdurur.
    sad = sadakat_beyani()
    sup = suphe_beyani()
    assert int(sad["çağrı"]) > 0, (
        "MANTIĞA SADAKAT ÇIKARIMDA KOŞMADI -- 7/24 iddiası düşer.")
    return {"küme": kume, "deneme": deneme, "konuşan": konusan,
            "hazine": yuk, "budanan": budanan,
            "sadakat": sad, "şüphe": sup,
            "susan": deneme - konusan, "tam_çözülen": cozulen,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre)) if hucre else 0.0,
            "süre_sn": time.perf_counter() - t0}


def kos(kume: str = "training", azami: int = 24,
        ham: bool = False) -> str:                       # pragma: no cover
    """**Ferman 1-G: burada rapor metni yoktur.** Ölç, beyana havale et."""
    return cikarim_beyani(degerlendirme_kosusu(kume, azami, ham=ham))


if __name__ == "__main__":                               # pragma: no cover
    print(kos(sys.argv[1] if len(sys.argv) > 1 else "training",
              int(sys.argv[2]) if len(sys.argv) > 2 else 24))
