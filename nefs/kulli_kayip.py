"""
KÜLLÎ KAYIP -- 41 melekenin **her birinin** hatası, müşterek uzayda.

===================================================================
NİÇİN VAR: OTUZ ALTI MELEKE HİÇ EĞİTİLMİYORDU
===================================================================

Eski ``nefs/qegitim.py::uygunluk`` şuydu::

    V(p) = −log P(doğru belirteç) + 0,25·mîzân_cezası − 0,1·entropi

ve ``mizan_cezasi`` yalnız beş sayı okuyordu: ``tenakuz``, ``nakz``,
``tasdik``, ``sukut``, ``P_Şek``. Yani:

* Kırk bir melekenin **kendi** hatası hiçbir yerde yoktu. Beş küllî
  alan, otuz altı melekenin ne yaptığını ayırt edemez; o melekeler için
  eğitim sinyali **fiilen sıfırdı**. Bir uzvun hatası kayba girmiyorsa
  o uzuv eğitilmiyor demektir -- kaç kere çağrıldığı bunu değiştirmez.
* Baştaki terim **belirteç kestirimi**ydi; yani kütük H133'te teşhis
  edilip çıkarımdan söküldüğü hâlde **eğitimde duruyordu**. Model
  çıkarımda muhakeme ediyor, eğitimde ise hâlâ sonraki belirteci
  tahmin etmeyi öğreniyordu. İkisinin ayrı düşmesi, eğitimin öğrettiği
  şeyin çıkarımda kullanılmaması demektir.

Kullanıcı hükmü: *"tüm melekelerin hatasını bu şekilde toplamalısın,
sadece senin söylediklerini değil yani, 41'in hepsini."*

===================================================================
BİR MELEKENİN HATASI NEDİR -- uydurma değil, sözleşmeden
===================================================================

`nefs/sozlesme.py` her meleke için **dokunacağı bölgeleri** ilan eder
ve bu ilan melekenin kendi tarifinden çıkarılmıştır. O hâlde bir
melekenin hatası, kendi ilan ettiği bölgenin akış sonundaki
mertebesidir:

    𝒪₁₃ Tasdik yalnız ``tasdik``e dokunur   → hatası: tasdik alanının
                                              yakînden uzaklığı
    𝒪₁₁ çelişkiyi ``tenakuz``a akıtır       → hatası: tenakuzun yüksekliği
    𝒪₃₂ makamı üç kaynaktan çevirir         → hatası: makam+sükût+…

Yani ölçüt melekenin **kendi taahhüdüdür**; dışarıdan konmuş bir hedef
değil. Bir meleke ilan ettiği alanı iyi hâle getiremiyorsa hatalıdır ve
o hata artık kayba girer.

**Cihet sözleşmeden değil ölçü uzayından gelir** (`nefs/olcu.py`):
``tasdik`` büyüdükçe iyi, ``tenakuz`` büyüdükçe kötüdür. Bu ayrım
yapılmasaydı toplam manasını yitirirdi -- nitekim eski kayıpta entropi
eksi işaretle toplanıyordu ve o eksi işaret, cihetin koda gömülmüş
hâliydi.

===================================================================
OKUMA NİÇİN BURADA, AKIŞTA DEĞİL
===================================================================

Kütük H31: **hiçbir meleke dalgayı okuyamaz.** O yasak yerinde
duruyor. Burada okuyan şey meleke değil **eğitim ölçütüdür** ve ölçüt
akışın dışındadır: okuduğu şey akışın kararlarını değiştirmez, yalnız
o akışın ne kadar iyi olduğunu söyler. Onun için akış
(``QNefs.idrak_et``) hiç değiştirilmedi; buradaki ``olcumlu_idrak``
akışı **kendisi** koşturur ve her melekeden sonra yalnız o melekenin
ilan ettiği alanı zayıf okur.

Maliyet gizlenmiyor: meleke başına en çok dört zayıf okuma, yani
geçiş başına ~%d okuma. Bu, eğitim ölçütünün bedelidir ve
``meleke_olcumu=False`` ile kapatılabilir -- kapatılamayan bir tedbirin
faydası ölçülemez (kütük H90).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .olcu import Olcum, OlcuUzayi, UZAYLAR, kulli_toplam, uzay
from .sozlesme import SOZLESME

__all__ = ["bolge_degeri", "olcumlu_idrak", "meleke_olcumleri",
           "kulli_kayip", "rapor"]


#: ``veri`` ve ``yerel`` küllî alan değildir; zayıf okumaları blok
#: dağılımından alınır. Kaç kübit örnekleneceği **hız** meselesidir ve
#: sayı burada durur, koda gömülü değildir.
VERI_ORNEK: int = 8


def _veri_yuvalari(q) -> List[int]:
    return [q.veri(i, j) for i in range(q.n_satir)
            for j in range(q.ayar.satir_kubiti)]


def bolge_degeri(q, ad: str) -> Optional[float]:
    """Bir bölgenin zayıf okuması, ``[0,1]``.

    Küllî alanlar ``alan_degeri`` ile okunur -- tek kübitlik zayıf
    ölçüm. ``yerel`` ve ``veri`` için POVM dağılımının **ortalaması**
    alınır; ikisi de bir "hüküm alanı" değil bir kübit kümesidir, o
    yüzden tek bir sayı ancak ortalamayla doğar ve bu açıkça yazılır.
    """
    try:
        if ad == "yerel":
            y = q.yereller()
            if not y:
                return None
            return float(np.mean(np.asarray(q.povm(y), float)))
        if ad == "veri":
            y = _veri_yuvalari(q)[:VERI_ORNEK]
            if not y:
                return None
            return float(np.mean(np.asarray(q.povm(y), float)))
        return float(q.alan_degeri(ad))
    except Exception:                                    # noqa: BLE001
        return None


def olcumlu_idrak(nefs, E: np.ndarray, meleke_olcumu: bool = True):
    """Akışı koştur ve **her melekeden sonra** onun alanını oku.

    ``QNefs.idrak_et``in aynısını yapar; farkı, melekeler arasında
    eğitim ölçütü için zayıf okuma almasıdır. Akışın kendisi bundan
    haberdar değildir ve kararları değişmez (H31 yerinde durur).

    Dönen: ``(q, okumalar)`` -- ``okumalar[no][bölge] = değer``.
    """
    from .gaye import gaye_kos
    from .qakis import bec_faz_kilidi
    from .qyazmac import QYazmac
    from .sadakat import sadakat_intaci, sadakat_kapisi
    from .tertip import tertip_kos

    E = np.asarray(E, float)
    B = E.shape[0] if E.ndim == 3 else 1
    ayar = nefs.ayar
    if B != ayar.yigin:
        from dataclasses import replace
        ayar = replace(ayar, yigin=B)
    q = QYazmac(E.shape[-2], ayar)
    q.kodla(E)
    q.superpozisyon()
    q.mera()

    okumalar: Dict[int, Dict[str, float]] = {}
    for no in nefs.sira:
        nefs.s[no].kosu(q, nefs.p)
        if nefs.sadakat:
            sadakat_kapisi(q, nefs.p)
        if meleke_olcumu:
            ilan = SOZLESME.get(int(no), ((), ""))[0]
            d: Dict[str, float] = {}
            for ad in ilan:
                v = bolge_degeri(q, ad)
                if v is not None:
                    d[ad] = v
            # Aynı meleke sırada iki kere geçebilir (QAKIS'te 13 böyle);
            # son okuma değil **en kötüsü** tutulur: bir melekenin iki
            # geçişinden birinde bozması, bozmadığı manasına gelmez.
            eski = okumalar.get(int(no))
            okumalar[int(no)] = d if eski is None else {
                k: min(v, eski.get(k, v)) for k, v in d.items()}
    if nefs.sadakat:
        q.iz.kesme += tertip_kos(q)
    if nefs.gaye:
        q.iz.kesme += gaye_kos(q, nefs.p)
    if nefs.sadakat:
        sadakat_intaci(q)
    bec_faz_kilidi(q)
    q.iz.kesme_hakiki = float(max(0.0, 1.0 - q.y.sadakat()))
    q.y.normalize()
    return q, okumalar


def meleke_olcumleri(okumalar: Dict[int, Dict[str, float]]
                     ) -> List[Olcum]:
    """41 melekenin hatasını ``Olcum`` listesine çevir.

    Her meleke, **ilan ettiği her bölge için** ayrı bir ölçü verir ve
    ağırlığı bölge sayısına bölünür: dört bölge ilan eden bir meleke,
    tek bölge ilan edenden dört kat ağır basmaz. Aksi hâlde sözleşmeyi
    geniş yazmak, kayıpta ağırlık kazanmanın yolu olurdu.
    """
    out: List[Olcum] = []
    for no, d in sorted(okumalar.items()):
        if not d:
            continue
        w = 1.0 / float(len(d))
        for ad, v in sorted(d.items()):
            S = UZAYLAR.get(ad)
            if S is None:
                # ``veri``/``yerel``: hükmün taşıyıcısıdır, büyüğü iyi
                # sayılır -- ölü bir bölge hüküm taşımıyor demektir.
                S = OlcuUzayi(ad, 0.0, 1.0, True)
            out.append(Olcum("𝒪%d.%s" % (no, ad), float(v), S, w))
    return out


def kulli_kayip(nefs, veri: Sequence[Tuple[List[int], int]],
                p: Optional[np.ndarray] = None, sozluk: int = 16,
                meleke_olcumu: bool = True,
                kademe_olcumleri: Optional[Sequence[Olcum]] = None,
                meleke_ornegi: int = 1) -> Dict[str, object]:
    """``ℒ`` -- bütün uzuvların hatası, funktörle müşterek uzayda.

    Toplananlar:

    1. **41 meleke**, her biri kendi sözleşmesine göre (yukarıdaki şerh),
    2. **küllî alanlar** -- akış sonundaki tenakuz/nakz/tasdik/sükût…,
    3. **kesme** -- dalganın attığı bilgi (``kesme_hakiki``),
    4. **kademeler** -- verilirse altı kademenin kendi ölçüleri
       (`nefs/kademeler.py`).

    Hepsi ``nefs/olcu.py``nin funktörüyle mertebeye iner ve orada
    toplanır. Elle konmuş ``0,25``/``0,1`` katsayıları **yoktur**:
    uzaylar arası intibak artık funktörle sağlanıyor.
    """
    from .qegitim import belirtecleri_kodla

    if p is not None:
        nefs.yukle(p)
    if not len(veri):
        return {"kayıp": 0.0, "uzuv": 0}

    # **MELEKE ÖLÇÜMÜ KAÇ VERİDE YAPILIR.** Ölçüldü: dört veri
    # örneğinde bir kayıp çağrısı 7,7 sn sürüyor ve bunun tamamına
    # yakını meleke başına zayıf okumalardır (41 meleke × ~2 alan ×
    # veri sayısı). Melekenin hatası **melekeye** aittir, veriye
    # değil; o hâlde ilk ``meleke_ornegi`` veride ölçmek yeter ve
    # kalan veriler yine küllî alan ile kesme ölçüsünü verir.
    # Bu bir kısaltmadır ve gizlenmiyor: ``meleke_ornegi`` büyütülünce
    # ölçüm zenginleşir, bedeli de doğrusal artar.
    hepsi: List[Olcum] = []
    for i, (baglam, _hedef) in enumerate(veri):
        E = belirtecleri_kodla(baglam, nefs.ayar.satir_kubiti, sozluk)
        olc = meleke_olcumu and i < int(meleke_ornegi)
        q, okumalar = olcumlu_idrak(nefs, E, olc)
        if olc:
            hepsi += meleke_olcumleri(okumalar)
        o = q.olcumler()
        for ad, _kac in q.ayar.kulli_alanlar:
            if ad in o and ad in UZAYLAR:
                hepsi.append(Olcum("alan.%s" % ad, float(o[ad]),
                                   UZAYLAR[ad]))
        hepsi.append(Olcum("kesme", float(q.iz.kesme_hakiki),
                           UZAYLAR["kesme_hakiki"]))
    if kademe_olcumleri:
        hepsi += list(kademe_olcumleri)
    t = kulli_toplam(hepsi)
    t["meleke_sayısı"] = len({o.kaynak.split(".")[0] for o in hepsi
                              if o.kaynak.startswith("𝒪")})
    return t


def rapor(n: int = 2) -> str:
    """Kaybın **fiilen** kaç uzvu saydığını göster -- iddia değil sayım."""
    from idrak import arc

    from .kulli_egitim import KISA_CPU
    from .qakis import QNefs
    from .qegitim import ornekler

    ayar = KISA_CPU
    nefs = QNefs(ayar.tohum, ayar.qayar())
    nefs.idrak_et(np.zeros((2, ayar.satir_kubiti)))
    veri = ornekler(arc.yukle_hepsi("training")[:6], azami=int(n),
                    pencere=ayar.pencere, sozluk=ayar.sozluk)
    t = kulli_kayip(nefs, veri, sozluk=ayar.sozluk)
    s = ["=== KÜLLÎ KAYIP -- 41 melekenin hepsi sayılıyor mu? ===",
         "",
         "  toplanan uzuv ölçüsü : %d" % t["uzuv"],
         "  ayrı meleke sayısı   : %d  ← 41 olmalı" % t["meleke_sayısı"],
         "  ortalama mertebe     : %.4f" % t["ortalama_mertebe"],
         "  KAYIP (1 − mertebe)  : %.4f" % t["kayıp"],
         "  en zayıf uzuv        : %s" % (t["en_zayıf"],),
         "  haddi tahminî ölçü   : %d" % t["tahminî_hadli"],
         "",
         "Eskiden kayıp BEŞ sayı okuyordu ve otuz altı melekenin eğitim",
         "sinyali sıfırdı. Yukarıdaki 'ayrı meleke sayısı' o borcun",
         "kapanıp kapanmadığının ölçüsüdür; iddia değil sayımdır."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
