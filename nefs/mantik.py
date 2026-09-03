"""
MANTIK -- `mizan/` külliyatının ana akışa **uzuv** olarak bağlanması.

`nefs/tertip.py` `mizan.onerme`yi bağlamıştı. Geriye yedi modül kaldı
ve hepsi 1. kademedeydi (yükleniyor, iş görmüyor). Burada ikisi
2. kademeye çıkar ve bunu yaparken **iki kusur bulunur**.

===================================================================
BULGU 1: makam kodlaması epistemik komşuluğu KIRIYOR
===================================================================

`nefs/zihin_durumu.py` şöyle diyordu:

> *"Sıra kasıtlıdır: Şek ve Vehim uçlardadır, Zan ile Yakîn ortadadır;
> tek kübitlik bir dönme Şek'ten Zan'a, Zan'dan Yakîn'e geçirir."*

**Ölçüldü ve iddianın yarısı yanlış.** Eski kodlama
``Şek=00, Zan=01, Yakîn=10, Vehim=11`` idi; epistemik sıra ise
``Vehim < Şek < Zan < Yakîn``. Komşular arası Hamming mesafesi::

    Vehim → Şek    2   ✗  iki kübit gerekiyor
    Şek   → Zan    1   ✓
    Zan   → Yakîn  2   ✗  iki kübit gerekiyor

Yani üç geçişin **ikisi** tek kübitlik dönmeyle yapılamıyordu. Bu bir
şerh hatası değil, **fiilî** bir kusurdur: 𝒪₃₂ Şek-Zan-Yakîn makama
tek kübitlik kontrollü dönmeler vuruyor ve o dönmeler Zan'dan Yakîn'e
hiç geçiremiyordu.

===================================================================
BULGU 2: makam₀ en yüksek ile en düşük dereceyi aynı kola koyuyordu
===================================================================

Eski kodlamada ``makam₀ = 1`` demek ``{Yakîn(10), Vehim(11)}`` demekti
-- yani **yakînin en yükseği ile en düşüğü aynı kolda**. 𝒪₃₂'nin
``tasdik → makam₀`` müsbet dönmesi, Yakîn'i kuvvetlendirirken Vehim'i
de kuvvetlendiriyordu. Bir hüküm melekesinin yapabileceği en ters şey.

===================================================================
TASHİH: Gray sırası -- ve niçin keyfî değil
===================================================================

``Vehim=00, Şek=01, Zan=11, Yakîn=10``. Üç geçiş de Hamming 1'dir ve
``makam₀ = 1`` artık **tam olarak** ``{Zan, Yakîn}``, yani "müsbete
meyilli" demektir. Sıra `mizan/munazara.py`nin ``MERTEBELER``inden
alınmıştır, benim tercihimden değil::

    yakîn 1,00 | zann-ı gālib 0,75 | zan 0,50 | şek 0,25 | vehim 0,00

===================================================================
BULGU 3: bir mertebe EKSİK -- zann-ı gālib
===================================================================

Klasik mîzânda beş mertebe var; akışın makamı iki kübit, yani dört
taban durumu. **Zann-ı gālib (0,75) akışta yok.**

Bunu evvelâ *"bir kusur değil bütçe sınırıdır"* diye yazmıştım.
**Kendime fazla müsamaha göstermişim ve `mizan/istikra.py` bağlanınca
ölçümle nakzedildi (kütük H129).** Ardışıklık kaidesi, ``n`` gösterimin
hepsi uyumluyken yakîni ``(n+1)/(n+2)`` verir::

    n = 2 → 0,7500      n = 3 → 0,8000      n = 4 → 0,8333

ARC training ilk 200 görevde gösterim çifti ortalaması **3,21**;
istikrâ yakîni ortalaması **0,8025**. Hepsi tek bir mertebeye düşüyor:
**zann-ı gālib** -- yani akışın taşıyamadığı tam o dereceye.
``tam_istikra_mi`` hiçbirinde ``True`` değil; eksik istikrâ hiçbir
sonlu ``n`` için yakîn vermez.

O hâlde akış, ARC'de doğru dereceyi **hiç** gösteremiyor: ya Yakîn
(1,0) deyip fazla iddia ediyor, ya Zan (0,5) deyip eksik. Bu bir bütçe
sınırı değil **yapısal bir yanlışlıktır**.

**BU BORÇ KAPANDI (kütük H158).** Makam artık 3 kübittir
(``QAyar.kulli_alanlar``); ``zann-ı gālib`` temsil ediliyor ve
``eksik_mertebeler()`` boş dönüyor.

**Fakat icra, yukarıdaki tarifin AYNISI DEĞİL** ve fark saklanmıyor.
Tarif şöyleydi: *"beş mertebe ``000=Vehim, 001=Şek, 011=Zan,
010=zann-ı gālib, 110=Yakîn``; kalan üç durum isimsizdir ve
üzerlerindeki kütle ayrıca raporlanmalıdır."* İcra edilmedi, zira
yazarken görülmeyen bir kusuru vardı:

* İsimsiz üç durum bir **genlik kuyusudur**: mertebe dağılımı 1'e
  toplanmaz, kütlenin bir kısmı manasız yerde birikir.
* Daha kötüsü, Gray sırasında ``100`` (8. basamak) tam da
  ``110``ın (Yakîn) komşusudur. Yani makamı "bir basamak yukarı"
  itmek Yakîn'den **isimsizliğe** düşürürdü.

Yerine geçen icra: sekiz basamağın **hepsinin** bir derecesi var
(``derece(k) = k/7``) ve mertebe o dereceye mîzânın kendi
eşiklerinden düşüyor -- Vehim 2, Şek 2, Zan 2, zann-ı gālib 1,
Yakîn 1 basamak. Dağılım eşit değil ve **eşitlenmedi**: eşikler
cetvelden geliyor, cetvel icraya uydurulmuyor.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from mizan.istikra import ardisiklik_kaidesi, tam_istikra_mi
from mizan.munazara import MERTEBELER, mertebe_adi, yakin_gazali

__all__ = ["MAKAM_MERTEBE", "GRAY_SIRA", "ESKI_SIRA", "komsuluk_denetimi",
           "eksik_mertebeler", "istikra_mertebesi", "yakin_yuzlestirmesi",
           "rapor"]


def istikra_mertebesi(n_gorev: int = 200) -> Dict[str, object]:
    """ARC görevlerinin **istikrâ yakîni** hangi mertebeye düşüyor?

    `mizan/istikra.py`nin ardışıklık kaidesi: ``k`` gösterimin hepsi
    uyumluysa yakîn ``(k+α)/(n+α+β)``dir. ARC'de ``k = n`` (bütün
    gösterimler görevin kendi kaidesine uyar), yani yakîn ``(n+1)/(n+2)``.

    **Ölçülen netice ve niçin mühim (kütük H129).** Her ARC görevi
    ``zann-ı gālib``e düşüyor -- akışın makamının **taşıyamadığı** tam o
    mertebeye. ``tam_istikra_mi`` hepsinde ``False``: eksik istikrâ
    hiçbir sonlu ``n`` için yakîn vermez.
    """
    from idrak import arc
    g = arc.yukle_hepsi("training")[:int(n_gorev)]
    k = np.array([len(x.egitim) for x in g], dtype=int)
    y = np.array([ardisiklik_kaidesi(int(v), int(v)) for v in k], float)
    adlar = sorted({mertebe_adi(float(v)) for v in y})
    return {"görev": int(k.size), "çift_ortalama": float(k.mean()),
            "yakîn_ortalama": float(y.mean()),
            "mertebe_ortalama": mertebe_adi(float(y.mean())),
            "düşülen_mertebeler": adlar,
            "tam_istikrâ_olan": int(sum(tam_istikra_mi(int(v), int(v))
                                        for v in k))}

#: Akıştaki makamların `mizan/munazara.py`deki yakîn derecesi.
#: Cetvelin **tamamı** buradadır; evvelce dördü vardı ve eksik olan
#: ``zann-ı gālib``ti (kütük H129 → H158).
MAKAM_MERTEBE: Dict[str, float] = {
    "Vehim": 0.0, "Şek": 0.25, "Zan": 0.5,
    "Zann-ı gālib": 0.75, "Yakîn": 1.0,
}

#: Kusurlu (evvelki) kodlama -- kıyas için saklanır, silinmez.
#: İki kübitlik yazmaçta beş mertebe zaten sığmaz; bu sıra dörttür ve
#: ``komsuluk_denetimi`` onu **kırmızı** yakar.
ESKI_SIRA: Tuple[str, ...] = ("Şek", "Zan", "Yakîn", "Vehim")

#: İki kübitlik tashih edilmiş kodlama (H127). Komşulukları sağlamdı
#: fakat ``zann-ı gālib``i taşıyamıyordu; tarih olarak duruyor.
GRAY_SIRA: Tuple[str, ...] = ("Vehim", "Şek", "Yakîn", "Zan")


def _kod(sira: Sequence[str], bit: int) -> Dict[str, Tuple[int, ...]]:
    """Sıradaki her adı, **taban durumu indeksinin** bitlerine eşle.

    ``sira``nın ``i``inci ögesi ``i`` numaralı taban durumunun adıdır;
    kod, ``i``nin ikilik yazılışıdır (ilk kübit en anlamlı). Burada
    Gray'e çevirmek **hata olurdu**: Gray sırası bu listelerde zaten
    ad dizilişinin içine gömülüdür (``GRAY_SIRA`` tam da odur), tekrar
    çevirmek onu bozar.
    """
    return {ad: tuple((i >> (bit - 1 - b)) & 1 for b in range(bit))
            for i, ad in enumerate(sira)}


def komsuluk_denetimi(sira: Optional[Sequence[str]] = None,
                      bit: Optional[int] = None) -> Dict[str, object]:
    """Epistemik komşular tek kübitlik dönmeyle geçilebiliyor mu?

    ``sira`` verilirse **o kodlama** (elle yazılmış bir sıra, meselâ
    ``ESKI_SIRA``) denetlenir; verilmezse yazmacın **yürürlükteki**
    makam alanı okunur ve merdiveni denetlenir.

    İki şart aranır:

    1. Derecesi ardışık iki basamak arasındaki Hamming mesafesi **1**
       olmalı; aksi hâlde 𝒪₃₂'nin tek kübitlik kontrollü dönmeleri o
       geçişi hiç yapamaz.
    2. ``makam₀ = 1`` kolu **üst yarı** olmalı: en yüksek ile en düşük
       derece aynı kola düşerse, tasdikin makamı yukarı iten dönmesi
       vehmi de kuvvetlendirir.

    Ayrıca merdivenin mertebe dizisi **monoton** olmalıdır: yukarı
    gitmek mertebeyi asla düşürmemeli.
    """
    from .zihin_durumu import (MAKAM_ADLARI, QAyar, makam_derecesi,
                          makam_kubit_manasi, makam_merdiveni,
                          makam_mertebeleri)

    if sira is None:
        kac = int(bit if bit is not None
                  else dict(QAyar().kulli_alanlar)["makam"])
        merd = makam_merdiveni(kac)
        adlar = list(makam_mertebeleri(kac))
        derece = list(makam_derecesi(kac))
        ust_kolu = sorted({adlar[k] for k in makam_kubit_manasi(kac)[0]})
        ad_kod = None
    else:
        adlar = list(sira)
        kac = int(bit if bit is not None
                  else max(1, (len(adlar) - 1).bit_length()))
        ad_kod = _kod(adlar, kac)
        # elle verilen sırada basamak dereceleri cetvelden okunur
        duzen = sorted((a for a in adlar if a in MAKAM_MERTEBE),
                       key=lambda a: MAKAM_MERTEBE[a])
        adlar = duzen
        derece = [MAKAM_MERTEBE[a] for a in duzen]
        merd = [int("".join(str(x) for x in ad_kod[a]), 2) for a in duzen]
        ust_kolu = sorted(a for a in ad_kod if ad_kod[a][0] == 1)

    gecis = []
    for i in range(len(merd) - 1):
        h = bin(int(merd[i]) ^ int(merd[i + 1])).count("1")
        gecis.append((adlar[i], adlar[i + 1], h))
    ust_derece = [d for k, d in enumerate(derece)
                  if (sira is None and k in makam_kubit_manasi(kac)[0])
                  or (sira is not None and ad_kod[adlar[k]][0] == 1)]
    monoton = all(derece[i] <= derece[i + 1] + 1e-12
                  for i in range(len(derece) - 1))
    return {
        "geçişler": gecis,
        "kırık_geçiş": sum(1 for _, _, h in gecis if h != 1),
        "makam0_1_kolu": ust_kolu,
        # üst kol tutarlıdır ⟺ derecelerin ÜST yarısını topluyor
        "kol_tutarlı": bool(ust_derece) and bool(
            min(ust_derece) > min(derece) + 1e-12),
        "monoton": bool(monoton),
        "basamak": len(merd),
        "mertebe_sayısı": len(set(adlar)),
    }


def eksik_mertebeler(bit: Optional[int] = None) -> List[Tuple[float, str]]:
    """Klasik mîzânda olup akışın makam **yazmacında** olmayan mertebeler.

    Evvelce ``MAKAM_MERTEBE`` sözlüğüne bakıyordu, yani bir **listeye**;
    liste ile yazmacın fiilî genişliği ayrı düşebilir ve o zaman ölçüt
    yalan söyler. Şimdi yazmacın kendi ``makam`` alanı okunur: hangi
    mertebe fiilen bir basamağa düşüyorsa o vardır.

    ``bit`` ile başka bir genişlik sınanabilir; iki kübitte ``zann-ı
    gālib`` yine eksik çıkar ve ölçütün kör olmadığı böyle gösterilir.
    """
    from .zihin_durumu import QAyar, makam_mertebeleri

    kac = int(bit if bit is not None
              else dict(QAyar().kulli_alanlar)["makam"])
    var = {a.lower() for a in makam_mertebeleri(kac)}
    return [(d, ad) for d, ad in MERTEBELER if ad.lower() not in var]


def yakin_yuzlestirmesi(gorev, tohum: int = 0, chi: int = 8
                        ) -> Dict[str, float]:
    """Akışın makamı ile **klasik** yakîn hesabı yüzleştirilir.

    Klasik taraf `mizan/munazara.py`nin ``yakin_gazali``sıdır::

        Yakîn(netice) = min_i Yakîn(öncül_i) · 𝟙[şekil geçerli]

    Öncüller görevin gösterim çiftleridir; her çiftin "yakîni",
    `nefs/operad.py`nin Čech yamalarından gelir -- mahallî kâidesi
    olan yama tam yakîn (1,0), olmayan sıfır. Şeklin geçerliliği ise
    yamaların yapışmasıdır (``H¹ = 0``).

    Akış tarafı ``makam_dagilimi``nin **beklenen derecesidir**:
    ``Σ P(makam) · Yakîn(makam)``.

    İkisi ayrı düşerse bu bir kusur DEĞİLDİR -- akış eğitilmemiştir.
    Ölçülen şey **aynı yöne bakıp bakmadıklarıdır**.
    """
    from .operad import cech_tikanikligi, yamalar
    from .iki_olcek import gorev_ozellikleri
    from .melekeler import QNefs
    from .zihin_durumu import MAKAM_ADLARI, QAyar

    c = cech_tikanikligi(gorev)
    Y = yamalar(gorev)
    oncul = [1.0 if k is not None else 0.0 for k in Y]
    klasik = float(yakin_gazali(oncul, bool(c["kurulabilir"])))

    X, Yz = gorev_ozellikleri(gorev)
    E = np.concatenate([X, Yz], axis=1)
    q = QNefs(tohum, QAyar(bag=int(chi), tohum=tohum)).idrak_et(
        E, tikaniklik=float(c["H1"]))
    P = np.atleast_1d(np.asarray(q.makam_dagilimi(), float)).ravel()
    # ``MAKAM_ADLARI``yı taban durumu indeksi sanmak bir hataydı: Gray
    # sırasında basamak ile indeks aynı değildir ve makam artık 3
    # kübittir. Beklenen derece yazmacın kendi derece vektöründen alınır.
    akis = float(P @ q.makam_derece_vektoru())
    return {"klasik_yakin": klasik, "akis_yakin": akis,
            "klasik_ad": mertebe_adi(klasik), "H1": float(c["H1"])}


def rapor(n_gorev: int = 30, tohum: int = 0) -> str:
    from idrak import arc
    from .zihin_durumu import MAKAM_ADLARI

    s = ["=== MANTIK -- mizan/ ana akışa bağlanıyor ===", ""]
    s.append("MAKAM KODLAMASI (epistemik komşuluk tek kübitle geçilmeli):")
    for ad, sira, bit in (("ESKİ (kusurlu)", ESKI_SIRA, 2),
                          ("GRAY 2 kübit", GRAY_SIRA, 2),
                          ("YÜRÜRLÜKTEKİ", None, None)):
        d = komsuluk_denetimi(sira, bit)
        g = "  ".join("%s→%s:%d" % (a, b, h) for a, b, h in d["geçişler"])
        s.append("  %-15s kırık geçiş=%d  basamak=%d  monoton=%s"
                 % (ad, d["kırık_geçiş"], d["basamak"], d["monoton"]))
        s.append("  %-15s %s" % ("", g))
        s.append("  %-15s makam₀=1 kolu: %s  (tutarlı: %s)"
                 % ("", ", ".join(d["makam0_1_kolu"]), d["kol_tutarlı"]))
    s += ["",
          "EKSİK MERTEBE (klasik mîzânda var, akışın yazmacında yok):"]
    eks = eksik_mertebeler()
    for d, ad in eks:
        s.append("  %.2f  %s" % (d, ad))
    if not eks:
        s.append("  (yok -- H129'un borcu kapandı, makam 3 kübit)")
        s.append("  Kör değil: 2 kübitte hâlâ eksik çıkıyor → %s"
                 % ", ".join(a for _, a in eksik_mertebeler(2)))
    i = istikra_mertebesi()
    s += ["",
          "  VE BU EKSİK ZARARSIZ DEĞİL (kütük H129):",
          "    ARC %d görev, ortalama %.2f gösterim çifti"
          % (i["görev"], i["çift_ortalama"]),
          "    istikrâ yakîni ortalaması : %.4f  →  %s"
          % (i["yakîn_ortalama"], i["mertebe_ortalama"]),
          "    düşülen mertebeler        : %s" % ", ".join(i["düşülen_mertebeler"]),
          "    tam istikrâ olan görev    : %d  (eksik istikrâ yakîn vermez)"
          % i["tam_istikrâ_olan"],
          "    → ARC'nin HER görevi, makamın taşıyamadığı mertebeye",
          "      düşüyor. Akış ya Yakîn deyip fazla iddia ediyor, ya",
          "      Zan deyip eksik. Bütçe sınırı değil, YAPISAL yanlışlık."]

    s += ["", "YAKÎN YÜZLEŞTİRMESİ (klasik hesap ↔ akışın makamı):"]
    gorevler = arc.yukle_hepsi("training")[:int(n_gorev)]
    K, A = [], []
    for gv in gorevler:
        try:
            r = yakin_yuzlestirmesi(gv, tohum)
        except Exception:                                # noqa: BLE001
            continue
        K.append(r["klasik_yakin"])
        A.append(r["akis_yakin"])
    if len(K) >= 4 and len(set(K)) > 1:
        kor = float(np.corrcoef(K, A)[0, 1])
        s += ["  görev              : %d" % len(K),
              "  klasik yakîn ort.  : %.4f" % float(np.mean(K)),
              "  akış yakîni ort.   : %.4f" % float(np.mean(A)),
              "  korelasyon         : %+.4f" % kor,
              ""]
        if kor > 0.15:
            s.append("  HÜKÜM: aynı yöne bakıyorlar.")
        elif kor < -0.15:
            s.append("  HÜKÜM: TERS yöne bakıyorlar -- kusurdur, gizlenmiyor.")
        else:
            s.append("  HÜKÜM: bağ yok. Akışın makamı klasik yakîn hesabıyla")
            s.append("  alâkasız; akış eğitilmemiştir ve bu borç yazılır.")
    else:
        s.append("  yeterli çeşitlilik yok (%d görev)" % len(K))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
