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

from .olcu import (Olcum, OlcuUzayi, UZAYLAR, kulli_toplam, uzay,
                   yumusak_asgari)
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
        # Yığın ekseni **yumuşak asgarî** ile birleşir, ortalamayla
        # değil (bkz. `nefs/olcu.py::yumusak_asgari`): bir yığında tek
        # bir veride düşen parametre yakîn sayılamaz.
        if ad == "yerel":
            y = q.yereller()
            if not y:
                return None
            return yumusak_asgari(q.povm(y))
        if ad == "veri":
            y = _veri_yuvalari(q)[:VERI_ORNEK]
            if not y:
                return None
            return yumusak_asgari(q.povm(y))
        return yumusak_asgari(q.alan_degeri(ad))
    except Exception:                                    # noqa: BLE001
        return None


def olcumlu_idrak(nefs, E: np.ndarray, meleke_olcumu: bool = True,
                  sinif_olcumu: bool = True):
    """Akışı koştur ve **her melekeden sonra** onun alanını oku.

    ``QNefs.idrak_et``in aynısını yapar; farkı, melekeler arasında
    eğitim ölçütü için zayıf okuma almasıdır. Akışın kendisi bundan
    haberdar değildir ve kararları değişmez (H31 yerinde durur).

    Dönen: ``(q, okumalar, dS)``:

    * ``okumalar[no][bölge]`` -- melekenin ilan ettiği alanın okuması,
    * ``dS[no]`` -- melekenin dolaşıklığa tesiri (`nefs/nizam.py`),
      sınıf taahhüdünün yüzleştirildiği ölçü.
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

    def _entropi() -> float:
        try:
            return float(np.mean(np.asarray(q.olcumler()["entropi"], float)))
        except Exception:                                # noqa: BLE001
            return float("nan")

    okumalar: Dict[int, Dict[str, float]] = {}
    #: ``ΔS`` -- melekenin dolaşıklığa tesiri (`nefs/nizam.py`).
    dS: Dict[int, float] = {}
    for no in nefs.sira:
        onceki_sadakat = (float(q.y.sadakat_log())
                          if meleke_olcumu else 0.0)
        S_once = _entropi() if sinif_olcumu else 0.0
        nefs.s[no].kosu(q, nefs.p)
        if nefs.sadakat:
            sadakat_kapisi(q, nefs.p)
        if sinif_olcumu:
            fark = _entropi() - S_once
            # Aynı meleke sırada iki kere geçebilir; tesirleri toplanır.
            dS[int(no)] = dS.get(int(no), 0.0) + (
                0.0 if fark != fark else fark)
        if meleke_olcumu:
            ilan = SOZLESME.get(int(no), ((), ""))[0]
            d: Dict[str, float] = {}
            for ad in ilan:
                if ad in ("veri", "yerel"):
                    # **VERİ BİR HÜKÜM ALANI DEĞİLDİR.** Evvelce buranın
                    # POVM ortalaması alınıp "büyüğü iyi" sayılıyordu ve
                    # ÖLÇÜLDÜ: ``𝒪₁.veri`` her parametrede tam ``0,000``
                    # çıkıyor, yani doymuş bir en-kötü uzuv olarak
                    # yumuşak azamîyi tek başına ele geçiriyor ve kaybı
                    # yine sabitliyordu. Kusur melekede değil benim
                    # ölçümümdeydi: veri kübitleri girdiyi taşır, hüküm
                    # taşımaz; onlara "büyüğü iyi" demek keyfîdir.
                    #
                    # Doğru ölçü melekenin **ne kadar bilgi attığı**dır:
                    # kesme. Yönü tartışmasızdır (az atmak iyidir),
                    # parametreye bağlıdır, ve her meleke için tanımlıdır.
                    continue
                v = bolge_degeri(q, ad)
                if v is not None:
                    d[ad] = v
            # Veri/yerel ilan eden melekeler **kesmeden** ölçülür: o
            # geçişte sadakatin ne kadar düştüğü. Böylece 41 melekenin
            # hepsi ölçülür ve hiçbiri doymuş bir sabit değildir.
            # **LOG UZAYINDA**: ``sadakat()`` çarpımsaldır ve 1814
            # kapıdan sonra ``4e-12``ye iner, yani oranı da manasızlaşır.
            # Melekenin o geçişte attığı nispî ağırlık log farkındadır.
            # Log farkını ``[0,1]``e **kırpmak** yanlıştı ve ölçüldü:
            # düşüş çoğu melekede 1'i aştığı için kırpma doyuyor,
            # ``𝒪₁.kesme`` sabit ``0`` çıkıyor ve yumuşak azamîyi yine
            # tek başına ele geçiriyordu. Kırpma bir had değil, haddi
            # olmayan bir sayıyı hadde zorlamaktır.
            #
            # Doğru hâl melekenin **kendi tuttuğu kesir**dir:
            # ``exp(−düşüş) ∈ (0,1]``. Hiçbir keyfî üst sınır gerekmez,
            # doymaz, ve yönü tartışmasızdır -- çok tutan iyidir.
            dus = max(0.0, onceki_sadakat - float(q.y.sadakat_log()))
            d["kesme"] = float(np.exp(-dus))
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
    return q, okumalar, dS


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
            # ``kesme`` artık **tutulan kesir**tir: büyüğü iyi.
            if ad == "kesme":
                S = OlcuUzayi("tutulan_kesir", 0.0, 1.0, True)
            else:
                S = UZAYLAR.get(ad)
            if S is None:
                S = OlcuUzayi(ad, 0.0, 1.0, True, tahmini_ust=True)
            out.append(Olcum("𝒪%d.%s" % (no, ad), float(v), S, w))
    return out


def kulli_kayip(nefs, veri: Sequence[Tuple[List[int], int]],
                p: Optional[np.ndarray] = None, sozluk: int = 16,
                meleke_olcumu: bool = True,
                kademe_olcumleri: Optional[Sequence[Olcum]] = None,
                kademe_gorevleri: Optional[Sequence] = None,
                azami_veri: int = 0) -> Dict[str, object]:
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
    # =================================================================
    # VERİ **YIĞIN HÂLİNDE** KOŞULUR (kütük H151)
    # =================================================================
    #
    # Evvelce veri örnekleri tek tek döngüyle akıştan geçiriliyordu.
    # Hâlbuki `main/yazmac.py` yazmacı zaten **yığın** taşıyor
    # (``yigin`` ekseni) ve ``QNefs.idrak_et`` ``(B, n, d)`` şeklinde
    # girdi kabul ediyor. Ölçüldü (CPU, χ=16, aynı donanım):
    #
    #     B= 1  yığın  1,01 sn   tek tek  1,01 sn   hızlanma 1,00×
    #     B= 4  yığın  2,71 sn   tek tek  4,05 sn   hızlanma 1,49×
    #     B=16  yığın 10,00 sn   tek tek 16,09 sn   hızlanma 1,61×
    #     B=32  yığın 19,47 sn   tek tek 32,86 sn   hızlanma 1,69×
    #
    # Örnek başına maliyet 1,014 → 0,608 sn'ye iniyor ve B büyüdükçe
    # düşmeye devam ediyor: kapı kurulumu, MPO inşası ve süpürme yığın
    # üyeleri arasında **paylaşılıyor**. Yani B'yi büyütmek yalnız daha
    # çok veri işlemek değil, **veri başına daha ucuz** işlemektir --
    # kullanıcı hükmü buydu ve ölçüm onu doğruladı.
    #
    # Meleke ölçümü yığının tamamında **bir kere** alınır: melekenin
    # hatası melekeye aittir, tek bir veri örneğine değil. Böylece
    # ``meleke_ornegi`` kısaltmasına da lüzum kalmadı.
    veri = list(veri)
    if azami_veri:
        veri = veri[:int(azami_veri)]
    hepsi: List[Olcum] = []
    E_yigin = np.stack([belirtecleri_kodla(b, nefs.ayar.satir_kubiti,
                                           sozluk) for b, _h in veri])
    q, okumalar, dS = olcumlu_idrak(nefs, E_yigin, meleke_olcumu)
    if meleke_olcumu:
        hepsi += meleke_olcumleri(okumalar)
    # **SINIF TAAHHÜDÜ ÖĞRENİLEBİLİR KAYBA GİRER** (`nefs/nizam.py`).
    # Meleke "çözücüyüm" dediği için değil, FİİLEN çözdüğü için
    # çözücü olmalıdır. ΔS açılarla değişir, yani bu ölçü hakikaten
    # öğrenilebilir -- kesme gibi yapısal değil.
    if dS:
        from .nizam import sinif_ihlali
        from .qmeleke import qsicil
        sic = qsicil()
        for no, d in sorted(dS.items()):
            m = sic.get(int(no))
            if m is None:
                continue
            hepsi.append(Olcum(
                "𝒪%d.nizam" % no, 1.0 - sinif_ihlali(m.SINIF, d),
                OlcuUzayi("nizam_uyumu", 0.0, 1.0, True)))
    o = q.olcumler()
    for ad, _kac in q.ayar.kulli_alanlar:
        if ad in o and ad in UZAYLAR:
            hepsi.append(Olcum("alan.%s" % ad,
                               yumusak_asgari(o[ad]), UZAYLAR[ad]))
    # **Kapı başına** tutulan kesir (bkz. `main/yazmac.py::sadakat`).
    hepsi.append(Olcum(
        "kesme", float(q.y.sadakat_kapi_basina(max(q.iz.kapi, 1))),
        OlcuUzayi("kapı_başına_sadakat", 0.0, 1.0, True)))
    # =================================================================
    # KADEME ÖLÇÜLERİ DE KAYBA GİRMİYOR (kütük H156)
    # =================================================================
    #
    # H154'ün aynı hatası başka yerde tekrarlanmıştı. Altı kademe
    # (`nefs/kademeler.py`) **dalga parametrelerine hiç bağlı
    # değildir**: idrak nesne ayrıştırır, muhakeme ``kaide_ara``
    # koşturur, tasdik istikrâ hesaplar -- hiçbiri melekelerin
    # açılarını kullanmaz. O hâlde kademe ölçüleri her parametrede
    # **aynı sayıdır**.
    #
    # Ölçüldü (5 parametre, aynı kayıp):
    #
    #     kademesiz : V(p₀)=0,5758   yayılım 0,2176
    #     kademeli  : V(p₀)=0,7978   yayılım 0,0118   ← 18 kat seyreltme
    #
    # 44 uzvun 24'ü sabitse, kaybın yarısından fazlası kımıldamıyor
    # demektir; yumuşak azamî de o sabit tabana oturuyor ve arama
    # körleşiyor.
    #
    # =================================================================
    # VE BU BORÇ KAPANDI (kütük H160): kademeler artık PARAMETRELİ
    # =================================================================
    #
    # H156'nın hükmü şuydu: *"Kademelerin eğitilebilmesi için kendi
    # parametrelerinin olması ve o parametrelerin `nefs/talim.py`ye
    # verilmesi gerekir -- henüz yok ve iddia edilmiyor."*
    #
    # Artık var. `nefs/kademeler.py` altı kademenin elle konmuş
    # sayılarını (beyan eşiği, müphemlik cezası, tevâfuk, muhakeme
    # derinliği, nesne eşiği, hüküm tabanı) **melekelerin açılarıyla
    # aynı düz vektörden** alıyor. O hâlde kademe ölçüleri artık
    # parametrede sabit değildir ve öğrenilebilir kayba **girer**.
    #
    # ``kademe_gorevleri`` verilirse kademeler her kayıp çağrısında o
    # görevlerde yeniden koşar (parametre değiştiği için mecburdur).
    # ``kademe_olcumleri`` eski yoldur: bir kere hesaplanmış sabit
    # ölçüler; onlar **yalnız raporlanır**, kayba girmez -- zira
    # parametreden bağımsızdırlar ve H156'nın körlüğünü geri getirirler.
    kademe_hepsi: List[Olcum] = []
    if kademe_gorevleri:
        from .kademeler import kademeleri_kos
        for g in kademe_gorevleri:
            try:
                kademe_hepsi += list(
                    kademeleri_kos(g, p=nefs.p)["ölçümler"])
            except Exception:                            # noqa: BLE001
                continue
        hepsi += kademe_hepsi
    if kademe_olcumleri:
        kt = kulli_toplam(list(kademe_olcumleri))
        _kademe_ozet = {"kademe_kayıp": kt["kayıp"],
                        "kademe_en_zayıf": kt["en_zayıf"],
                        "kademe_uzuv": kt["uzuv"]}
    elif kademe_hepsi:
        kt = kulli_toplam(list(kademe_hepsi))
        _kademe_ozet = {"kademe_kayıp": kt["kayıp"],
                        "kademe_en_zayıf": kt["en_zayıf"],
                        "kademe_uzuv": kt["uzuv"]}
    else:
        _kademe_ozet = {}

    # =================================================================
    # ÖĞRENİLEBİLİR HATA ile YAPISAL KUSUR AYRILDI (kütük H154)
    # =================================================================
    #
    # Padişah koşturuldu ve kayıp yine kımıldamadı (0,8379 → 0,8376,
    # 170 çağrı). Sebep arandı: yumuşak azamîyi ele geçiren uzuv
    # ``𝒪₂₄.kesme``ydi (tutulan kesir 0,0046, yani eksik ~0,995).
    #
    # Fakat **bir kapının ne kadar kestiği, açı parametreleriyle
    # değişmez.** Kesme; menzilin uzunluğundan, MPO'nun zinciri baştan
    # sona sıkıştırmasından ve χ'den doğar -- yani **mimarînin
    # vasfıdır**, melekenin öğrenebileceği bir şey değil. Onu kayba
    # koymak, öğrenciye çözemeyeceği bir soruyu sorup notunu ona
    # bağlamaktır: not sabitlenir, öğrenme durur.
    #
    # O hâlde ölçüler ikiye ayrılır:
    #
    #   ÖĞRENİLEBİLİR -- hüküm alanlarının okumaları (tasdik, tenakuz,
    #       nakz, makam, sükût, kelâm, mizan, gaye) ve kademe ölçüleri.
    #       Bunlar açı parametreleriyle fiilen değişir; kayıp bunlardır.
    #
    #   YAPISAL -- kesme/sadakat. Kayba **girmez**; ayrıca raporlanır
    #       ve tamiri tasarımladır (nitekim H148/H149'da χ tavanları
    #       kaldırılarak 𝒪₂₄'ün tuttuğu 5,3e-07'den 0,0046'ya çıktı).
    #
    # Yapısalı gizlemiyoruz -- ``yapısal`` anahtarında sayılıyor ve en
    # kötüsü adıyla veriliyor. Gizleseydik, mimarî kusuru ölçüsüz
    # bırakmış olurduk.
    ogrenilebilir = [o for o in hepsi if not o.kaynak.endswith(".kesme")
                     and o.kaynak != "kesme"]
    yapisal = [o for o in hepsi if o.kaynak.endswith(".kesme")
               or o.kaynak == "kesme"]
    t = kulli_toplam(ogrenilebilir)
    t.update(_kademe_ozet)
    if yapisal:
        yt = kulli_toplam(yapisal)
        t["yapısal_kayıp"] = yt["kayıp"]
        t["yapısal_en_zayıf"] = yt["en_zayıf"]
        t["yapısal_uzuv"] = yt["uzuv"]
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
