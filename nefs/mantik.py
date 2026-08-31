"""
MANTIK -- `mizan/` külliyatının ana akışa **uzuv** olarak bağlanması.

`nefs/tertip.py` `mizan.onerme`yi bağlamıştı. Geriye yedi modül kaldı
ve hepsi 1. kademedeydi (yükleniyor, iş görmüyor). Burada ikisi
2. kademeye çıkar ve bunu yaparken **iki kusur bulunur**.

===================================================================
BULGU 1: makam kodlaması epistemik komşuluğu KIRIYOR
===================================================================

`nefs/qyazmac.py` şöyle diyordu:

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

**Açık borç, tam tarifiyle:** makam 2 kübitten 3'e çıkarılmalı; beş
mertebe Gray komşuluğuyla ``000=Vehim, 001=Şek, 011=Zan,
010=zann-ı gālib, 110=Yakîn``. Kalan üç durum isimsizdir ve
üzerlerindeki kütle ayrıca raporlanmalıdır. Tek bildirim yeri
``QAyar.kulli_alanlar``dır ve ``makam_dagilimi`` artık kübit
sayısından bağımsız olduğu için (H129) geçiş onu kırmaz.
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

#: Akıştaki dört makamın `mizan/munazara.py`deki yakîn derecesi.
MAKAM_MERTEBE: Dict[str, float] = {
    "Vehim": 0.0, "Şek": 0.25, "Zan": 0.5, "Yakîn": 1.0,
}

#: Kusurlu (evvelki) kodlama -- kıyas için saklanır, silinmez.
ESKI_SIRA: Tuple[str, ...] = ("Şek", "Zan", "Yakîn", "Vehim")

#: Tashih edilmiş kodlama: ``00=Vehim, 01=Şek, 10=Yakîn, 11=Zan``.
#: İndeks ``2·b₀ + b₁``dir (bkz. ``QYazmac.makam_dagilimi``).
GRAY_SIRA: Tuple[str, ...] = ("Vehim", "Şek", "Yakîn", "Zan")


def _kod(sira: Sequence[str]) -> Dict[str, Tuple[int, int]]:
    return {ad: (i >> 1, i & 1) for i, ad in enumerate(sira)}


def komsuluk_denetimi(sira: Sequence[str]) -> Dict[str, object]:
    """Epistemik komşular tek kübitlik dönmeyle geçilebiliyor mu?

    Şart: yakîn derecesine göre ardışık iki makam arasındaki Hamming
    mesafesi **1** olmalı. Aksi hâlde 𝒪₃₂'nin tek kübitlik kontrollü
    dönmeleri o geçişi hiç yapamaz.
    """
    kod = _kod(sira)
    duzen = sorted(MAKAM_MERTEBE, key=lambda a: MAKAM_MERTEBE[a])
    gecis = []
    for a, b in zip(duzen, duzen[1:]):
        h = sum(x != y for x, y in zip(kod[a], kod[b]))
        gecis.append((a, b, h))
    # ``makam₀ = 1`` hangi makamları topluyor?
    ust = sorted(a for a in kod if kod[a][0] == 1)
    return {
        "geçişler": gecis,
        "kırık_geçiş": sum(1 for _, _, h in gecis if h != 1),
        "makam0_1_kolu": ust,
        "kol_tutarlı": bool(
            set(ust) in ({"Zan", "Yakîn"}, {"Vehim", "Şek"})),
    }


def eksik_mertebeler() -> List[Tuple[float, str]]:
    """Klasik mîzânda olup akışın makamında **olmayan** mertebeler."""
    var = {a.lower() for a in MAKAM_MERTEBE}
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
    from .qakis import QNefs
    from .qyazmac import MAKAM_ADLARI, QAyar

    c = cech_tikanikligi(gorev)
    Y = yamalar(gorev)
    oncul = [1.0 if k is not None else 0.0 for k in Y]
    klasik = float(yakin_gazali(oncul, bool(c["kurulabilir"])))

    X, Yz = gorev_ozellikleri(gorev)
    E = np.concatenate([X, Yz], axis=1)
    q = QNefs(tohum, QAyar(bag=int(chi), tohum=tohum)).idrak_et(
        E, tikaniklik=float(c["H1"]))
    P = np.atleast_1d(np.asarray(q.makam_dagilimi(), float)).ravel()
    akis = float(sum(P[i] * MAKAM_MERTEBE[ad]
                     for i, ad in enumerate(MAKAM_ADLARI)))
    return {"klasik_yakin": klasik, "akis_yakin": akis,
            "klasik_ad": mertebe_adi(klasik), "H1": float(c["H1"])}


def rapor(n_gorev: int = 30, tohum: int = 0) -> str:
    from idrak import arc
    from .qyazmac import MAKAM_ADLARI

    s = ["=== MANTIK -- mizan/ ana akışa bağlanıyor ===", ""]
    s.append("MAKAM KODLAMASI (epistemik komşuluk tek kübitle geçilmeli):")
    for ad, sira in (("ESKİ (kusurlu)", ESKI_SIRA),
                     ("GRAY (tashih)", GRAY_SIRA),
                     ("YÜRÜRLÜKTEKİ", tuple(MAKAM_ADLARI))):
        d = komsuluk_denetimi(sira)
        g = "  ".join("%s→%s:%d" % (a, b, h) for a, b, h in d["geçişler"])
        s.append("  %-15s kırık geçiş=%d   %s" % (ad, d["kırık_geçiş"], g))
        s.append("  %-15s makam₀=1 kolu: %s  (tutarlı: %s)"
                 % ("", ", ".join(d["makam0_1_kolu"]), d["kol_tutarlı"]))
    s += ["",
          "EKSİK MERTEBE (klasik mîzânda var, akışta yok):"]
    for d, ad in eksik_mertebeler():
        s.append("  %.2f  %s" % (d, ad))
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
