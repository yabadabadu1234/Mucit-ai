"""
MÜDRİKE ÇEVRİMİ -- modelin **iç muhakemesi**, icra edilebilir hâlde.

===================================================================
KULLANICININ TARİFİ
===================================================================

> *"Modelin iç muhakeme ile şunu becerebilmesi gerek: acaba bunlar
> benden ne istiyor, acaba burada konuşurken sanatlı mı konuşmalıyım
> bir şey mi çözmeliyim, hmmm, sürekli bir girdi var bir de çıktı var,
> herhalde bu bir bulmaca, hmmm, burada bir sürü renk rastgele
> dizilmiş gibi duruyor, hmm, rastgele olsa ben nasıl cevap bulacağım,
> demek ki rastgele değil hmmm… Modele bu kabiliyeti katmalısın ki ARC
> ile normal vazifeler arasında ayrım yapmak zorunda kalmayalım."*

Bu bir üslûp tarifi değil, **bir hüküm zinciridir** ve her halkası
ölçülebilir. Buradaki altı adım o zincirin ta kendisidir; hiçbiri
ARC'ye mahsus değildir, birincisi vazifenin nevini kendi tayin eder.

===================================================================
ÇEVRİM
===================================================================

    1. VAZİFE NEVİ   "benden ne isteniyor?"
       Girdi–çıktı çifti var mı → BULMACA;  yoksa → KELÂM.
       Bu bir bayrak değil, verinin şeklinden okunan bir hükümdür.

    2. TESADÜF MÜ?   "rastgele olsa ben nasıl cevap bulurdum?"
       Çıktı girdiden kestirilebiliyor mu? Ölçü: renk dağılımının
       düzgünden sapması + çıktının girdiye göre şartlı belirliliği.
       Tam tesadüfse çözülecek bir şey **yoktur** ve sükût doğrudur.

    3. ÖRTÜ KAPANIYOR MU?   "bütün örnekler aynı kaideye mi bakıyor?"
       Čech tıkanıklığı (`nefs/operad.py`, kütük H125). ``H¹ ≠ 0`` ise
       küllî kaide **yoktur**; sükût.

    4. KÂİDE NEDİR?
       `nefs/kaideler.py` -- atom ve terkip, gösterimlerin hepsinde
       ispatlanır. Bulunmazsa sükût.

    5. YAKÎN NE MERTEBEDE?
       `mizan/istikra.py` ardışıklık kaidesi (``n`` gösterimden çıkan
       yakîn) **ve** müphemlik: tutan kaideler sınama girdisinde ayrı
       cevap veriyorsa yakîn düşer. Eşiğin altındaysa sükût.

    6. BEYAN.
       Yalnız 5'ten geçerse. Hükümsüz kelâm yasaktır (kütük H131).

===================================================================
NİÇİN BU BİR "MUHAKEME", BİR BORU HATTI DEĞİL
===================================================================

Her adım bir **hüküm** üretir ve hükmün gerekçesi kayda geçer
(``muhakeme`` listesi). Model sonunda yalnız cevabı değil, **niçin o
cevabı verdiğini** de söyleyebilir; susuyorsa **niçin sustuğunu**.
Kütük H10/H16: susmak bir kusur değil kabiliyettir -- fakat sebebi
söylenebiliyorsa.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from mizan.istikra import ardisiklik_kaidesi
from mizan.munazara import mertebe_adi

__all__ = ["VAZIFE_NEVILERI", "vazife_nevi", "tesaduf_olcusu",
           "YAKIN_ESIGI", "mudrike", "rapor"]

#: Vazife nevileri -- birinci adımın verebileceği hükümler.
VAZIFE_NEVILERI: Tuple[str, ...] = ("bulmaca", "kelâm", "boş")

#: Beyan için asgarî yakîn. `mizan/munazara.py`nin cetvelinde
#: ``zan = 0,50``; onun **üstü** aranır, yani en az zann-ı gālib'e
#: meyilli olmak. Eşik keyfî değil o cetvelden alınmıştır.
YAKIN_ESIGI: float = 0.5


def vazife_nevi(gorev) -> Dict[str, object]:
    """1. ADIM -- *"benden ne isteniyor?"*

    Bayrağa bakılmaz; **verinin şekline** bakılır. Ardışık girdi–çıktı
    çiftleri varsa bu bir bulmacadır: birileri bana bir dönüşüm
    gösteriyor ve aynısını istiyor. Yoksa vazife kelâmdır.
    """
    ciftler = list(getattr(gorev, "egitim", []) or [])
    sinama = list(getattr(gorev, "sinama", []) or [])
    if not ciftler:
        return {"nev": "boş", "gerekçe": "gösterim çifti yok",
                "çift": 0}
    ikili = all(hasattr(a, "shape") and hasattr(b, "shape")
                for a, b in ciftler)
    if ikili and len(ciftler) >= 2:
        return {"nev": "bulmaca", "çift": len(ciftler),
                "sınama": len(sinama),
                "gerekçe": "%d gösterim çifti var: bir dönüşüm "
                           "gösteriliyor ve aynısı isteniyor"
                           % len(ciftler)}
    return {"nev": "kelâm", "çift": len(ciftler), "sınama": len(sinama),
            "gerekçe": "girdi–çıktı çifti yok; vazife söz söylemek"}


def tesaduf_olcusu(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                   ) -> Dict[str, float]:
    """2. ADIM -- *"rastgele olsa ben nasıl cevap bulurdum?"*

    İki ölçü, ikisi de ``[0,1]``de ve ikisi de **yüksek = yapılı**:

    * ``renk_yapısı`` -- renk dağılımının düzgünden sapması. Tam
      düzgün bir ızgarada hiçbir renk bir şey söylemez.
    * ``şekil_bağı``  -- çıktı şekli girdi şeklinden kestirilebiliyor
      mu (aynı, sabit, yahut tam kat). Kestirilemiyorsa bağ zayıftır.

    **Bu bir "rastgele mi" testi DEĞİLDİR ve öyle olduğu iddia
    edilmiyor.** Hakikî rastgelelik ispatlanamaz (Kolmogorov). Ölçülen
    şey daha mütevazıdır: *elimde bu ızgaradan cevap çıkarmaya yetecek
    bir düzen var mı?* Yoksa cevap aramak beyhudedir.
    """
    if not ciftler:
        return {"renk_yapısı": 0.0, "şekil_bağı": 0.0, "yapı": 0.0}
    sapmalar = []
    for a, b in ciftler:
        for g in (a, b):
            g = np.asarray(g)
            if g.size == 0:
                continue
            _v, s = np.unique(g, return_counts=True)
            p = s / s.sum()
            k = max(len(p), 2)
            # düzgünden toplam değişinti; ``k`` renkli düzgün = 0
            sapmalar.append(0.5 * float(np.abs(p - 1.0 / k).sum())
                            + (1.0 - len(p) / 10.0) * 0.5)
    renk = float(np.clip(np.mean(sapmalar) if sapmalar else 0.0, 0, 1))

    ayni = sum(1 for a, b in ciftler if a.shape == b.shape)
    sabit = len({b.shape for _a, b in ciftler}) == 1
    kat = sum(1 for a, b in ciftler
              if a.shape[0] and a.shape[1]
              and (b.shape[0] % a.shape[0] == 0
                   and b.shape[1] % a.shape[1] == 0))
    n = len(ciftler)
    sekil = max(ayni / n, kat / n, 1.0 if sabit else 0.0)
    return {"renk_yapısı": renk, "şekil_bağı": float(sekil),
            "yapı": float(0.5 * renk + 0.5 * sekil)}


def dalga_hukmu(gorev, nefs=None, chi: int = 8,
                tohum: int = 0) -> Optional[Dict[str, float]]:
    """41 melekenin bu göreve dair **hükmü**: sükût ve makam.

    **Niçin var: dalga cevaba fiilen girmeliydi, girmiyordu.**
    Padişahın çıkarımı evvelce yalnız ``beyan``ın ``argmax``ıydı;
    41 melekenin kurduğu hüküm alanları (``sukut``, ``makam``,
    ``tasdik``) cevaba **hiç dokunmuyordu**. Kütük H92: paralel hat
    yasak -- dalga ile kaide cebri iki ayrı motor olamaz.

    Buradaki bağ şudur: dalga **kaideyi bulmaz** (onu cebir bulur),
    fakat **yakîni tartar**. Akış susmaya meyilliyse müdrikenin yakîni
    düşer; makam yüksekse yükselir. Yani dalga, hükmün mertebesini
    tayin eden meclistir -- tam da 𝒪₃₂ ve 𝒪₃₃'ün tarifi.
    """
    try:
        from .iki_olcek import gorev_ozellikleri
        from .operad import cech_tikanikligi
        from .qakis import QNefs
        from .qyazmac import MAKAM_ADLARI, QAyar

        X, Y = gorev_ozellikleri(gorev)
        if len(X) == 0:
            return None
        E = np.concatenate([X, Y], axis=1)
        c = cech_tikanikligi(gorev)
        q = (nefs or QNefs(tohum, QAyar(bag=int(chi), tohum=tohum))
             ).idrak_et(E, tikaniklik=float(c["H1"]))
        _, ks = q._alan["sukut"]
        sk = float(np.asarray(q.y.tekil_yogunluklar(
            [q.kulli("sukut", j) for j in range(ks)]), float)[0][:, 1, 1].mean())
        from .mantik import MAKAM_MERTEBE
        P = np.atleast_1d(np.asarray(q.makam_dagilimi(), float)).ravel()
        mk = float(sum(P[i] * MAKAM_MERTEBE[ad]
                       for i, ad in enumerate(MAKAM_ADLARI)))
        return {"sukut": sk, "makam_yakini": mk}
    except Exception:                                    # noqa: BLE001
        return None


def mudrike(gorev, yakin_esigi: float = YAKIN_ESIGI,
            derinlik: int = 2, dalga: bool = False,
            nefs=None) -> Dict[str, object]:
    """Altı adımlık müdrike çevrimi -- ya cevap ya **sebebi yazılı** sükût.

    Dönen sözlükte ``muhakeme`` listesi vardır: modelin kendi kendine
    ne düşündüğü, adım adım. Cevap verilmediğinde de doludur; susmanın
    sebebi orada yazar.
    """
    from .kaideler import kaide_ara
    from .operad import cech_tikanikligi

    dusunce: List[str] = []

    # --- 1. VAZİFE NEVİ
    v = vazife_nevi(gorev)
    dusunce.append("Benden ne isteniyor? %s → bu bir %s."
                   % (v["gerekçe"], v["nev"]))
    if v["nev"] != "bulmaca":
        return {"nev": v["nev"], "cevap": None, "sükût": True,
                "sebep": "bulmaca değil", "muhakeme": dusunce,
                "yakîn": 0.0}

    ciftler = list(gorev.egitim)

    # --- 2. TESADÜF MÜ?
    t = tesaduf_olcusu(ciftler)
    dusunce.append("Renkler rastgele dizilmiş gibi mi? renk yapısı %.3f, "
                   "şekil bağı %.3f → yapı %.3f."
                   % (t["renk_yapısı"], t["şekil_bağı"], t["yapı"]))
    if t["yapı"] < 0.15:
        dusunce.append("Rastgele olsaydı cevabı nereden bulacaktım? "
                       "Bulamazdım. Yapı yok; sormak beyhude.")
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "yapı yok", "muhakeme": dusunce, "yakîn": 0.0,
                "tesadüf": t}
    dusunce.append("Demek ki rastgele değil: bir düzen var, "
                   "o hâlde bir kaide de olmalı.")

    # --- 3. ÖRTÜ KAPANIYOR MU?  (**VETO DEĞİL, İŞARET**)
    #
    # **ÖLÇÜLEN VE DÜZELTİLEN TASARIM HATASI (kütük H132).** Bu adım
    # evvelce bir **kapı**ydı: ``H¹ ≠ 0`` ise hemen susuluyordu.
    # Ölçüldü ve ZARAR VERİYORDU: tıkanık sayılan 17 görevin **3'ünde**
    # kaide arama bir kaide buluyor ve o kaide sınamayı **tam** çözüyordu.
    # Yani veto, çözülebilen görevleri atıyordu.
    #
    # Hata mantıkîdir: benim Čech'im tam kohomoloji değil onun **sonlu
    # gölgesidir** (yamaların mahallî ŞEKİL kaidesi uyuşuyor mu). O
    # gölge kaba; şekil kaidesi ayrı düşen iki gösterim pekâlâ aynı
    # küllî kaideye tâbi olabilir.
    #
    # Doğrusu şudur ve daha kuvvetlidir: **bütün gösterimleri tutan bir
    # kaide bulmak, örtünün kapandığının kendisidir** -- küllî kesit
    # fiilen elde edilmiştir. O hâlde tıkanıklık bir veto değil, bir
    # **ihtiyat işareti**dir: yakîni düşürür, sözü kesmez.
    c = cech_tikanikligi(gorev)
    dusunce.append("Bütün örnekler aynı kaideye mi bakıyor? "
                   "yama %d, uyuşmayan çift %d (H¹=%d)."
                   % (c["yama"], c.get("uyuşmayan_çift", 0), c["H1"]))
    if c["H1"]:
        dusunce.append("Yamaların şekil kaidesi ayrı düşüyor. Bu beni "
                       "susturmaz -- bütün gösterimleri tutan bir kaide "
                       "bulursam örtü zaten kapanmış olur; fakat "
                       "ihtiyatlı olurum.")

    # --- 4. KÂİDE -- artık **kademelerden** geliyor
    #
    # **MİMARÎ DEĞİŞİKLİĞİ.** Evvelce burada doğrudan ``kaide_ara``
    # çağrılıyordu; yani çıkarım kendi boru hattını kuruyor, eğitim
    # başka bir şey eniyiliyordu. İkisinin ayrı düşmesi, eğitimin
    # öğrettiği şeyin çıkarımda kullanılmaması demektir.
    #
    # Şimdi ikisi de `nefs/kademeler.py`nin **aynı** altı kademesini
    # koşturur: idrak → tasavvur → muhakeme → ispat → tasdik → beyan.
    # Kademelerin ölçüleri `nefs/kulli_kayip.py` yoluyla eğitime de
    # girer; yani bu boru hattı hem konuşur hem öğrenir.
    from .kademeler import kademeleri_kos
    kad = kademeleri_kos(gorev, derinlik=derinlik, esik=yakin_esigi)
    dusunce += kad["günlük"]
    K = list(kad["ispat"].kaideler)
    kademe_olcumleri = kad["ölçümler"]
    if kad["eksik"]:
        dusunce.append("Kademelerde düşen uzuv: %s"
                       % ", ".join(sorted(kad["eksik"])))
    if not K:
        dusunce.append("Hiçbir kaide bütün gösterimleri tutmuyor. "
                       "Tutmayan bir kaideyle cevap vermek, tam eşleşme "
                       "ölçütünü sahte kılardı.")
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "kaide bulunamadı", "muhakeme": dusunce,
                "yakîn": 0.0, "tesadüf": t,
                "ölçümler": kademe_olcumleri}

    # **SÖZ VEREBİLİR MİYİM?** Bir kaide gösterimleri tutup sınama
    # girdisinde ``None`` dönebilir (görülmemiş bağlam). Evvelce ilk
    # kaide alınır ve ``None`` cevap olarak **söylenirdi**; ölçüldü:
    # ``0ca9ddb6`` ve ``025d127b`` böyle "konuşup boş" çıkıyordu. Susmak
    # kabiliyettir, boş konuşmak değil. Onun için cevap üretebilen ilk
    # kaide öne alınır; hiçbiri üretemiyorsa sükût **sebebiyle** edilir.
    girdiler_on = [np.asarray(a, np.int64)
                   for a, _ in getattr(gorev, "sinama", [])] or []
    if girdiler_on:
        konusabilen = [k for k in K
                       if all(k(g) is not None for g in girdiler_on)]
        if not konusabilen:
            dusunce.append(
                "%d kaide gösterimleri tutuyor fakat hiçbiri sınama "
                "girdisinde cevap üretmiyor -- görmediğim bir hâl var. "
                "Ezberlediğim tablo oraya uzanmıyor; susuyorum." % len(K))
            return {"nev": "bulmaca", "cevap": None, "sükût": True,
                    "sebep": "kaide sınamaya uzanmıyor",
                    "muhakeme": dusunce, "yakîn": 0.0, "tesadüf": t}
        if len(konusabilen) < len(K):
            dusunce.append("%d kaidenin %d'i sınama girdisinde cevap "
                           "üretebiliyor; yalnız onları tartıyorum."
                           % (len(K), len(konusabilen)))
        K = konusabilen

    # --- 5. YAKÎN
    n = len(ciftler)
    istikra = float(ardisiklik_kaidesi(n, n))
    girdiler = [a for a, _ in getattr(gorev, "sinama", [])] or []
    muphem = False
    if girdiler and len(K) > 1:
        for g in girdiler:
            cevaplar = []
            for k in K[:8]:
                r = k(np.asarray(g, np.int64))
                cevaplar.append(None if r is None else r.tobytes()
                                + bytes(r.shape))
            if len({c for c in cevaplar if c is not None}) > 1:
                muphem = True
                break
    # **DELİL / HİPOTEZ ORANI (kütük H134).** Öğrenilen bir tablo,
    # delilden büyükse istikrâ değil ezberdir. Delil = gösterimlerde
    # görülen hücre sayısı; hipotez = tablonun girdi sayısı. Oran
    # küçüldükçe yakîn düşer ve model susar.
    delil = sum(int(np.asarray(a).size) for a, _ in ciftler)
    hip = int(getattr(K[0], "hipotez", 0))
    kanit = 1.0 if hip <= 0 else float(
        np.clip(delil / (4.0 * hip), 0.25, 1.0))
    # Tıkanıklık **ihtiyat** olarak girer: sözü kesmez, yakîni düşürür.
    ihtiyat = 0.8 if c["H1"] else 1.0
    yakin = istikra * (0.5 if muphem else 1.0) * ihtiyat * kanit

    # **MECLİS.** Kod tabanının bütün modülleri burada padişahın
    # hükmüne fiilen girer (`nefs/meclis.py`). İki mertebe ayrı ayrı
    # hesaplanır -- görevin verisiyle hesap yapan **uzuv**lar ve kendi
    # varsayımını sınayan **hakem**ler -- ve neticeleri tek bir ihtiyat
    # çarpanına iner. Bu, "içe aktardım" demenin değil, modülün hükmü
    # **değiştirmesi**nin yeridir: bir modülün hesabı bozulursa buradan
    # yakîn düşer ve padişah susar.
    try:
        from .meclis import meclis
        mec = meclis(ciftler, girdiler)
        yakin *= float(mec["ihtiyat"])
        dusunce.append(
            "Meclisi topluyorum: %d uzuv (rey %.3f), %d hakem (rey %.3f), "
            "%d düşen → ihtiyat %.3f, yakînim %.3f."
            % (len(mec["uzuv_rey"]), mec["uzuv"], len(mec["hakem_rey"]),
               mec["hakem"], len(mec["eksik"]), mec["ihtiyat"], yakin))
        # **Ölçü hükmü uzuvdan geliyor**: `nefs/boyut.py` çıktı ölçüsünü
        # kestirdiyse ve kaidenin verdiği cevap ona uymuyorsa, iki
        # müstakil hesap birbirini yalanlıyor demektir; yakîn düşer.
        kes = mec["bilgi"].get("kestirilen_ölçü")
        if kes is not None and girdiler:
            deneme = K[0](np.asarray(girdiler[0], np.int64))
            if deneme is not None and tuple(deneme.shape) != tuple(kes):
                yakin *= 0.5
                dusunce.append(
                    "Fakat ölçü kestirimi %s diyor, kaidem %s veriyor -- "
                    "iki müstakil hesap uyuşmuyor; yakînimi yarıya "
                    "indiriyorum." % (tuple(kes), tuple(deneme.shape)))
    except Exception as exc:                             # noqa: BLE001
        dusunce.append("Meclis toplanamadı (%s); ihtiyatsız devam "
                       "ediyorum." % type(exc).__name__)
    if hip > 0:
        dusunce.append("Bu kaide %d girdilik bir tablo öğrendi; "
                       "delilim %d hücre → delil/hipotez sağlamlığı %.3f."
                       % (hip, delil, kanit))
    # **DALGA HÜKMÜ.** 41 meleke kaideyi bulmaz fakat yakîni tartar
    # (𝒪₃₂ Şek-Zan-Yakîn, 𝒪₃₃ Muhakeme). Akış susmaya meyilliyse yakîn
    # düşer. Bu, dalganın cevaba FİİLEN girdiği yerdir; evvelce hiç
    # girmiyordu ve o bir paralel hat kusuruydu (H92).
    dh = dalga_hukmu(gorev, nefs) if dalga else None
    if dh is not None:
        yakin *= float(np.clip(1.0 - 0.5 * dh["sukut"], 0.3, 1.0))
        dusunce.append("Dalganın hükmü: sükût eğilimi %.3f, makam yakîni "
                       "%.3f → yakînim %.3f'e ayarlandı."
                       % (dh["sukut"], dh["makam_yakini"], yakin))
    dusunce.append("Yakînim ne mertebede? %d gösterimden ardışıklık "
                   "kaidesi %.3f; tutan kaideler %s%s → yakîn %.3f (%s)."
                   % (n, istikra,
                      "AYRI cevaplar veriyor (müphem)" if muphem
                      else "aynı cevabı veriyor",
                      "; örtü tıkanıklığı ihtiyatı" if c["H1"] else "",
                      yakin, mertebe_adi(yakin)))
    if yakin < yakin_esigi:
        dusunce.append("Yakîn eşiğin (%.2f) altında; susuyorum."
                       % yakin_esigi)
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "yakîn eşiğin altında", "muhakeme": dusunce,
                "yakîn": yakin, "tesadüf": t, "kaide": K[0].ad}

    # --- 6. BEYAN
    kural = K[0]
    cevap = [kural(np.asarray(g, np.int64)) for g in girdiler]
    dusunce.append("Kaide: %s. Yakînim %s; konuşuyorum."
                   % (kural.ad, mertebe_adi(yakin)))
    return {"nev": "bulmaca", "cevap": cevap, "sükût": False,
            "sebep": None, "muhakeme": dusunce, "yakîn": yakin,
            "kaide": kural.ad, "kaide_sayısı": len(K),
            "müphem": muphem, "tesadüf": t}


# =====================================================================
def rapor(kume: str = "training", n: int = 120, derinlik: int = 2,
          dalga: bool = False) -> str:
    from idrak import arc

    g = arc.yukle_hepsi(kume)[:int(n)]
    coz = cevap = yanlis = 0
    sebepler: Dict[str, int] = {}
    ornek_muhakeme: List[str] = []
    for gv in g:
        r = mudrike(gv, derinlik=derinlik, dalga=dalga)
        if r["sükût"]:
            sebepler[r["sebep"]] = sebepler.get(r["sebep"], 0) + 1
            if not ornek_muhakeme and r["sebep"] == "kaide bulunamadı":
                ornek_muhakeme = list(r["muhakeme"])
            continue
        cevap += 1
        ok = True
        for (a, b), c in zip(gv.sinama, r["cevap"]):
            if c is None or c.shape != b.shape or not np.array_equal(c, b):
                ok = False
        coz += ok
        yanlis += (not ok)
        if ok and len(ornek_muhakeme) < 2:
            ornek_muhakeme = list(r["muhakeme"])

    s = ["=== MÜDRİKE ÇEVRİMİ -- %s (%d görev) ===" % (kume, len(g)),
         "",
         "  konuştu      : %d" % cevap,
         "  TAM ÇÖZDÜ    : %d  (%%%.1f)" % (coz, 100.0 * coz / max(len(g), 1)),
         "  yanlış cevap : %d" % yanlis,
         "  sustu        : %d" % (len(g) - cevap),
         "",
         "  SÜKÛT SEBEPLERİ:"]
    for k, v in sorted(sebepler.items(), key=lambda x: -x[1]):
        s.append("    %-26s %d" % (k, v))
    if ornek_muhakeme:
        s += ["", "  BİR MUHAKEME ÖRNEĞİ (modelin kendi kendine düşündüğü):"]
        s += ["    " + x for x in ornek_muhakeme]
    s += ["",
          "Cevap verince isabet: %s"
          % ("%.1f%%" % (100.0 * coz / cevap) if cevap else "—"),
          "Susmak bir kusur değil kabiliyettir (H10/H16) -- fakat",
          "sebebi söylenebiliyorsa. Yukarıdaki döküm o sebeplerdir."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
