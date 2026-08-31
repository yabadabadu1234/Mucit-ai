"""
ŞAHİTLİK -- 𝒪₂₉ Teyit'in **bağımsızlık iddiası** tartılıyor.

`fitrat/tevafuk.py` ana akışa buradan bağlanır ve bağlanır bağlanmaz
bir iddiayı sınar.

===================================================================
İDDİA
===================================================================

`nefs/qmeleke.py`, 𝒪₂₉ Teyit için şöyle diyor:

> *"Bir satırın ilk kübiti ile son kübiti **ayrı kanallardır**. İkisi
> dolaştırılınca uyuşma yapıcı, uyuşmazlık yıkıcı girişim verir.
> **Bağımlı iki kanalın uyuşması yeni bilgi değildir**; burada kanallar
> satırın iki ucundan alınır ki mümkün olduğunca ayrı olsunlar."*

Son cümle bir **tedbir**tir ve tedbirin işe yarayıp yaramadığı hiç
ölçülmemişti. Halbuki iddia yanlışlanabilir: iki uç hakikaten ayrı
mı, yoksa akış onları çoktan birbirine bağlamış mı?

Mesele küçük değildir. Kütük H19/H29'un mantığı şudur: **bağımlı iki
şahidin birbirini teyidi yeni delil sayılmaz.** Kanallar bağımlıysa
𝒪₂₉ aynı delili iki kere sayıyor, yani tasdiki hak etmediği yerde
yükseltiyor demektir.

===================================================================
ÖLÇÜ
===================================================================

`fitrat/tevafuk.py` bu işi zaten yapıyordu ve beylikti:

* ``cift_uyusmasi``  -- iki delil aynı yöne mi işaret ediyor (Pearson).
* ``fazla_sayma``    -- bağımsızlık farzı ne kadar fazla saydırıyor;
  ağırlık 1'e ne kadar yakınsa yığma o kadar meşrudur.

Burada "delil", her satırın ilk ve son veri kübitinin akış boyunca
aldığı ``P(1)`` değeridir -- hakikî indirgenmiş yoğunluktan
(``tekil_yogunluklar``, kütük H121'in tashihiyle; ayara bağlı eski
okumayla ölçülseydi netice **manasız** olurdu).

===================================================================
HUDUT
===================================================================

Ölçülen şey, iki kanalın **ayrı kübit olması** değil (o zaten
malûmdur); akış onları dolaştırdıktan sonra hâlâ ayrı **bilgi** taşıyıp
taşımadıklarıdır. Bu ikisi farklı şeylerdir ve karıştırılmaz.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from fitrat.tevafuk import cift_uyusmasi, fazla_sayma, tevafuk_olcusu

__all__ = ["kanal_degerleri", "kanal_bagimsizligi", "rapor"]


def kanal_degerleri(q) -> Tuple[np.ndarray, np.ndarray]:
    """𝒪₂₉'un iki "kanalı": her satırın ilk ve son veri kübiti.

    Değerler **hakikî** indirgenmiş yoğunluktan okunur (H121). Eski
    ``yuva_yogunluklari`` ayara bağlıydı; onunla ölçülen bir bağıntı
    fizikî bir şey söylemezdi.
    """
    k = q.ayar.satir_kubiti
    ilk = [q.veri(i, 0) for i in range(q.n_satir)]
    son = [q.veri(i, k - 1) for i in range(q.n_satir)]
    R1 = np.asarray(q.y.tekil_yogunluklar(ilk), float)[0][:, 1, 1]
    R2 = np.asarray(q.y.tekil_yogunluklar(son), float)[0][:, 1, 1]
    return R1, R2


def kanal_bagimsizligi(n_kosu: int = 12, n_satir: int = 8, chi: int = 8,
                       tohum: int = 0) -> Dict[str, object]:
    """İki kanal hakikaten ayrı mı? -- `fitrat/tevafuk.py` ile tartılır.

    Her koşu bir "vaka"dır; kanal değerleri o vakadaki delildir.
    ``cift_uyusmasi`` ikisinin aynı yöne işaret edip etmediğini,
    ``fazla_sayma`` bağımsızlık farzının ne kadar fazla saydırdığını
    verir.
    """
    from .qakis import QNefs
    from .qyazmac import QAyar

    A, B = [], []
    for t in range(int(n_kosu)):
        E = np.random.default_rng(500 + t).normal(size=(n_satir, 12))
        q = QNefs(tohum, QAyar(bag=int(chi), tohum=tohum)).idrak_et(E)
        a, b = kanal_degerleri(q)
        A.append(a)                       # satır satır -- koşu ortalaması DEĞİL
        B.append(b)
    d1 = np.concatenate(A)
    d2 = np.concatenate(B)
    uyusma = float(cift_uyusmasi(d1, d2))

    # **``fazla_sayma`` İKİLİ delil ister ve bu ölçülerek anlaşıldı.**
    # İlk kullanımda sürekli değerler verildi; ölçüt hem aynı şahidi iki
    # kere verince hem bağımsız iki şahit verince **1,0** döndü, yani
    # hiç ayırt etmedi (``log`` içeride ``nan`` üretiyordu). Kusur
    # `fitrat/tevafuk.py`de değil kullanımımdaydı: o modül ikili
    # şahitlikle çalışır ve öyle beslendiğinde mükemmel ayırıyor --
    # bağımsız üç şahitte fazla sayma 1,05, ortak kaynaklıda 2,55.
    #
    # O hâlde kanal değerleri **medyanına göre ikilileştirilir**: delil
    # "bu satır tipik olandan yukarıda mı" der. Hipotez de aynı usulle
    # ikisinin ortalamasından kurulur.
    def ikili(v: np.ndarray) -> np.ndarray:
        return (v > float(np.median(v))).astype(np.int64)

    H = ikili((d1 + d2) / 2.0)
    fs = fazla_sayma([ikili(d1), ikili(d2)], H)
    return {"koşu": int(n_kosu), "delil": int(d1.size), "uyuşma": uyusma,
            "kanal1_ort": float(d1.mean()), "kanal2_ort": float(d2.mean()),
            "fazla_sayma": fs}


def rapor(n_kosu: int = 12, n_satir: int = 8, chi: int = 8) -> str:
    r = kanal_bagimsizligi(n_kosu, n_satir, chi)
    u = r["uyuşma"]
    s = ["=== ŞAHİTLİK -- 𝒪₂₉ Teyit'in bağımsızlık iddiası ===",
         "",
         "𝒪₂₉ şöyle diyor: *'Bir satırın ilk kübiti ile son kübiti AYRI",
         "kanallardır… bağımlı iki kanalın uyuşması yeni bilgi değildir.'*",
         "Bu bir tedbirdi ve hiç ölçülmemişti.",
         "",
         "  koşu / delil       : %d koşu, %d satır delili"
         % (r["koşu"], r["delil"]),
         "  kanal 1 ortalaması : %.4f" % r["kanal1_ort"],
         "  kanal 2 ortalaması : %.4f" % r["kanal2_ort"],
         "  çift uyuşması (Pearson) : %+.4f" % u,
         ""]
    fs = r["fazla_sayma"]
    oran = float(fs["fazla_sayma_oranı"])
    s += ["",
          "  FAZLA SAYMA (fitrat/tevafuk.py, ikili şahitlikle):",
          "    ortalama ağırlık      : %.4f  (1'e yakın = yığma meşru)"
          % fs["ortalama_ağırlık"],
          "    muteber şahit sayısı  : %.4f  (2'ye yakın = iki ayrı şahit)"
          % fs["muteber_şahit_sayısı"],
          "    fazla sayma oranı     : %.4f  (1 = fazla sayma yok)"
          % fs["fazla_sayma_oranı"],
          "  Kıyas için: bağımsız üç şahitte 1,05; ortak kaynaklıda 2,55.",
          ""]
    # **Hüküm İKİ ölçüte birden bakar ve ikisi aynı şeyi söylemiyor.**
    # Pearson doğrusal bağıntıyı görür; fazla sayma, bağımsızlık farzının
    # delili ne kadar şişirdiğini görür. Yalnız Pearson'a bakıp "kanallar
    # ayrı" demek, ikinci ölçütün gördüğünü örtmek olurdu.
    if abs(u) < 0.3 and oran < 1.10:
        s += ["  HÜKÜM: kanallar fiilen AYRI. 𝒪₂₉'un tedbiri tutuyor;",
              "  ikisinin uyuşması hakikaten yeni delildir."]
    elif abs(u) < 0.3:
        s += ["  HÜKÜM: KARIŞIK ve iki ölçüt ayrı düşüyor. Pearson bağıntı",
              "  görmüyor (%+.4f) fakat fazla sayma oranı %.4f -- yani" % (u, oran),
              "  doğrusal olmayan bir bağımlılık var ve 𝒪₂₉ delili bir",
              "  miktar şişiriyor. Muteber şahit sayısı 2 değil %.2f."
              % float(fs["muteber_şahit_sayısı"]),
              "  Tedbir KISMEN tutuyor; 'tamamen tutuyor' denmez."]
    elif abs(u) < 0.7:
        s += ["  HÜKÜM: kanallar KISMEN bağımlı. 𝒪₂₉ delili bir miktar",
              "  fazla sayıyor; tedbir tamamen tutmuyor."]
    else:
        s += ["  HÜKÜM: kanallar KUVVETLE bağımlı. 𝒪₂₉ aynı delili iki",
              "  kere sayıyor -- tasdiki hak etmediği yerde yükseltiyor.",
              "  Bu bir kusurdur ve gizlenmiyor."]
    s += ["",
          "HUDUT: ölçülen şey iki kanalın ayrı KÜBİT olması değil (o",
          "zaten malûm); akış onları dolaştırdıktan sonra hâlâ ayrı",
          "BİLGİ taşıyıp taşımadıklarıdır."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
