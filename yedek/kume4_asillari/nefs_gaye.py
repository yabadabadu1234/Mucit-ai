"""
GAYE -- muhtar gayenin doğuşu, Landauer darboğazı ve sükût eşiği.

Dosya 4'ün üç teklifi: (1) muhtar gaye doğuşu ``G_t``, (2) Landauer
darboğazı, (3) ``ε_durgun`` sükût eşiği.

===================================================================
EVVELÂ BİR NAKZ: `gaye` ALANI ÖLÜYDÜ
===================================================================

Kütük H108 *"gaye alanı buraya konur ve hükümle DOLAŞTIRILIR"* diyor.
**Bu doğru değildi ve ölçüldü.** Tam bir akış koşturulup küllî bloğun
her alanı hakikî indirgenmiş yoğunlukla okundu::

    alan       P(1) ortalama
    makam        0,551137
    mizan        0,389035
    tenakuz      0,033918
    tasdik       0,531855
    sukut        0,426830
    nakz         0,329497
    kelam        0,445535
    kaide        0,000000   ← hiç yazılmamış
    orak         0,000000   ← hiç yazılmamış
    gaye         0,000000   ← hiç yazılmamış
    tertip       0,500439

``gaye`` tam olarak ``|0⟩``da duruyor. 41 melekenin hiçbiri ona
dokunmuyor (`nefs/sozlesme.py` de bunu söylüyor: gaye'yi ilan eden
meleke yok). Alan **tahsis edilmiş fakat yazılmamıştı**; H108'in
"dolaştırılır" ibaresi bir niyetti, bir icra değil. Burada nakzedilir
ve icra edilir.

(``kaide`` ve ``orak`` da ``|0⟩``dadır, fakat onlar ölü değildir:
`nefs/qkaide.py` onları kendi çözücüsünde kullanır -- ana akışta
değil. Bu ayrı bir borçtur ve öyle kaydedilir.)

===================================================================
GAYE NASIL DOĞAR -- dışarıdan konmaz
===================================================================

Dosya 4'ün asıl fikri budur: gaye **verilmez, doğar**. Onun için
buradaki sıra kasıtlıdır ve tersi yapılmaz:

1. **Doğuş.** ``gaye`` süperpozisyona sokulmaz ve dışarıdan da
   yazılmaz; hükmün kendisinden **akar**. ``tasdik``, ``tenakuz`` ve
   ``nakz`` alanları MPO ile ``gaye``ye toplanır. Yani "neyi
   isteyeceğim" sorusunun cevabı "şu ana kadar neye kanaat getirdim"den
   çıkar.

   **BU BORÇ KAPANDI (H122 → H159).** Uzun zaman şöyle yazıyordu:
   *"Niyet 'tasdik doğursun, nakz zayıflatsın' idi; ölçüldü, olmadı…
   şu an gaye hükmün faaliyetinden doğar, hangi hüküm olduğuna
   bakmadan."* Sebebini yanlış teşhis etmişim: kolun işaretinde değil,
   **çalışma noktasında** imiş. ``gaye`` ``|0⟩``da duruyordu ve
   ``sin²`` orada çift; ``π/4``e çevrilince tek oluyor ve işaret iş
   görüyor.

   Müdahaleli ölçüm (her şey sabit, tek kaynak ``|0⟩ → |1⟩``)::

       tasdik   açılınca gaye₀ : 0,5000 → 0,5403   (+0,0403)  ✓
       tenakuz  açılınca gaye₀ : 0,5000 → 0,4079   (−0,0921)  ✓
       nakz     açılınca gaye₀ : 0,5000 → 0,4836   (−0,0164)  ✓

   Korelasyonla değil **müdahaleyle** ölçüldü ve sebebi budur: üç
   kaynak girdiler arasında birbiriyle oynadığı için korelasyon
   confounded'dır; "hangisi hangisini oynatıyor" sorusunun cevabı
   ancak öbürleri sabitken alınır.
2. **Tesir.** Doğan gaye ``mizan``a geri dağıtılır: gaye, tartının
   yönünü büker. Teleolojik çekici tam olarak budur.
3. **Sükût eşiği (``ε_durgun``).** Gaye zayıfsa -- yani takip etmeye
   değer bir şey doğmamışsa -- ``sukut`` uyanır. Susmak burada bir
   kabiliyettir (H10/H16) ve gayenin yokluğundan doğar.

**Hiçbir yerde okuma yoktur.** Üçü de MPO'dur; hangi gayenin uyandığı
veriye bağlıdır fakat bu bağlılık hiçbir yerde sayıya dökülmez
(H31, ve kullanıcı hükmü: *"kalp seçmez, dolaştırır"*).

===================================================================
LANDAUER DARBOĞAZI -- ölçülür, iddia edilmez
===================================================================

Dosya 4 Landauer haddini gaye motorunun darboğazı sayıyor. Bu mimaride
o haddin **fiilî** karşılığı bellidir ve zaten kayıtlıdır: akıştaki tek
tersinmez adım **kesmedir**. Bütün kapılar diktir (tersinir); yalnız
SVD budaması bilgi atar.

Atılan bilgi ``Yazmac.sadakat()`` ile zabıtlıdır (``Π tutulan/tam``).
Silinen bit sayısı::

    bit = −log₂ F        (F = sadakat)

ve Landauer'a göre bunun bedeli ``kT ln2`` başına bittir. Sayı burada
**hesaplanır ve raporlanır**; "gaye motoru Landauer haddine dayanıyor"
diye bir iddia edilmez -- edilirse ölçülmeden edilmiş olurdu.
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence

import numpy as np

from .zihin_durumu import QYazmac, donme

__all__ = ["EPSILON_DURGUN", "gaye_kos", "odenen_bedel", "rapor"]


#: Sükût eşiği ``ε_durgun`` -- gaye bu kuvvetin altındaysa sükût uyanır.
#:
#: Bir dönme açısıdır, bir okuma eşiği DEĞİLDİR: hiçbir yerde "gaye
#: küçük mü?" diye sorulmaz. Kontrollü dönme şartı cebren icra eder --
#: gaye ``|1⟩``e ne kadar yakınsa sükût o kadar **bastırılır**; gaye
#: ``|0⟩``da ise sükût serbest kalır. Yani eşik bir karar değil, bir
#: kapının kendisidir.
EPSILON_DURGUN: float = 0.45


def gaye_kos(q: QYazmac, p) -> float:
    """Gayeyi **doğur**, mîzâna sirayet ettir, sükût eşiğini kur.

    Akışta 41 melekeden sonra, `tertip` ile `sadakat_intaci` arasında
    koşar. Kesme miktarını döndürür.
    """
    kesme = 0.0

    # --- 1) DOĞUŞ: hüküm alanları ``gaye``ye akar.
    # ``mpo_topla`` durakların hedefin SOLUNDA olmasını ister; küllî
    # blokta ``gaye`` zaten tasdik/tenakuz/nakz'ın sağındadır.
    kaynaklar = [q.kulli("tasdik", 0), q.kulli("tasdik", 1),
                 q.kulli("tenakuz", 0), q.kulli("nakz", 0)]
    # --- 1a) ÇALIŞMA NOKTASI: gaye evvelâ ``π/4``e çevrilir.
    #
    # **H122'NİN KÜNHÜ BURADAYDI VE EVVELCE BULAMAMIŞTIM.** Aşağıdaki
    # şerh "işaretle bastırma olmaz, zira ``P(1) = sin²θ`` çifttir"
    # diyor. Teşhis doğru, fakat **eksikti**: mesele işaretin değil,
    # **çalışma noktasının** meselesiymiş.
    #
    # ``gaye`` ``|0⟩``da, yani ``θ = 0``da duruyordu. Orada ``sin²``in
    # türevi **sıfır** ve fonksiyon çifttir; ``−θ`` ile ``+θ`` aynı
    # nüfusu verir. Yani nakz tek başına geldiğinde gayeyi
    # **yükseltiyordu** -- ölçülen ``+0,871`` tam olarak budur.
    #
    # ``θ₀ = π/4``te ise ``sin²(π/4 + x) = (1 + sin 2x)/2``: türev
    # âzamî, fonksiyon x'te **tek**, yani müsbet açı yükseltir, menfî
    # açı **düşürür**. Aynı MPO, aynı işaretler; yalnız kolun
    # duracağı yer değişti.
    #
    # Bu bir okuma değildir: sabit bir tek kübitlik dönmedir, veriye
    # bakmaz (H31 yerinde durur).
    q.tek(q.kulli("gaye", 0), donme(0.25 * math.pi))
    # --- EVVELKİ ŞERH, NAKZEDİLMİŞ HÂLİYLE DURUYOR (silinmiyor):
    #
    #   > "Bu satır evvelce ``işaret = [+1,+1,−1,−1]`` taşıyordu…
    #   >  ölçüldü ve çalışmadı -- korelasyon ``+0,871``. Sebep bir
    #   >  kodlama hatası değil, kendi kütüğümde yazılı bir
    #   >  imkânsızlıktır (H107): ``P(1) = sin²θ`` çift fonksiyondur…
    #   >  **İşaretle bastırma olmaz.**"
    #
    # Son cümle **fazla genelleştirilmiş bir hükümdü ve nakzedildi**
    # (H159). İşaretle bastırma ``θ = 0``da olmaz; ``θ = π/4``te
    # **olur**. O zaman "mutlak açı al, sönmeyi girişime bırak" diye
    # kurduğum çare de gereksizdi: derdi çözmüyordu (ölçüldü, +0,887)
    # çünkü dert kolda değil çalışma noktasındaydı.
    #
    # İşaretler artık İŞ GÖRÜYOR (yukarıdaki çalışma noktası sayesinde):
    # tasdik gayeyi doğurur, tenakuz ve nakz **zayıflatır**.
    #
    # Açılar ``(π/16)·tanh`` ile sınırlanır ve sebebi cebridir: dört
    # kaynak var, her biri en çok ``π/16`` katkı verirse toplam ``π/4``i
    # aşamaz ve kol ``[0, π/2]`` penceresinden **çıkmaz**. Çıksaydı
    # ``sin²`` sarılır, tek olmaktan çıkar ve az evvel kurulan işaret
    # duyarlılığı geri kaybolurdu -- yani had bir ihtiyat değil,
    # tashihin şartıdır.
    # ``abs`` ŞARTTIR ve müdahaleli ölçümle bulundu: ``_aci`` müsbet
    # değil, **işaretli** bir parametre döndürür. ``tanh``ın işareti
    # sınıfın işaretini yiyordu -- tohum 0'da tasdik açıları menfî
    # çıkmış ve tasdik gayeyi ``−0,000991`` kadar **düşürmüştü**.
    # Yani sınıf taahhüdü, öğrenilen sayının rastgele işaretine
    # tâbiydi. Cihet **yapısaldır** (sınıftan gelir), şiddet
    # **öğrenilir** (parametreden); ikisi karıştırılmaz.
    isaret = np.array([+1.0, +1.0, -1.0, -1.0])
    ham = np.asarray(_aci(p, "gaye.dogus", 4, 0.8), float)
    a = isaret * (math.pi / 16.0) * np.abs(np.tanh(ham))
    kesme += q.mpo_topla("gaye", a, duraklar=kaynaklar, j=0)

    # --- 1b) YASAK TERKİPLER: nakzedilmiş yahut çelişkili bir hükümden
    # doğan gaye **mantık dışıdır** ve işaretlenir. Sönmesi akışın
    # sonundaki ``sadakat_intaci`` yansıtmasına bırakılır -- yansıtma
    # ``gaye`` ve ``nakz``ı zaten kapsıyor.
    #
    # **VE BU DA İSTENEN NETİCEYİ VERMEDİ -- ölçüldü, saklanmıyor.**
    # 14 ayrı girdide gaye-nakz korelasyonu ``+0,871``den ``+0,887``ye
    # gitti, yani hiç değişmedi. İşaret duruyor (meşrudur ve bedeli
    # yoktur) fakat derdi **çözmüyor** ve çözdüğü iddia edilmiyor.
    #
    # Sebebi anlaşıldı: bu bir kol meselesi değil, **inşa seviyesinde**
    # bir bağımlılıktır. ``mpo_topla`` gayeye ``R(Σθᵢnᵢ)`` uygular ve
    # bütün ``θᵢ`` müsbet olduğu için ``P(gaye=1)``, tasdik + tenakuz +
    # nakz **faaliyetinin toplamıyla** büyür. Bu girdilerde en çok
    # değişen alan nakz olduğu için korelasyonu da o götürüyor. Tek bir
    # işaretli kolu ``2¹⁵`` kol arasında tek turluk bir yansıtmayla
    # söndürmek, marjinali bu kadar oynatamaz.
    #
    # Yani "nakz gayeyi zayıflatır" **hâlâ icra edilmiş değildir** ve
    # kütükte borç olarak durur (H122). Şu an fiilen olan şudur ve
    # dürüstçe böyle yazılır: *gaye, hükmün faaliyetinden doğar* --
    # hangi hükmün olduğuna bakmadan.
    CZ = np.eye(4)
    CZ[3, 3] = -1.0
    gay0 = q.kulli("gaye", 0)
    q.uzak_cift(q.kulli("nakz", 0), gay0, CZ)        # |nakz=1, gaye=1⟩
    q.uzak_cift(q.kulli("tenakuz", 0), gay0, CZ)     # |tenakuz=1, gaye=1⟩

    # --- 2) TESİR: gaye mîzânı büker (teleolojik çekici).
    b = _aci(p, "gaye.mizan", 4, 0.6)
    kesme += q.mpo_dagit("gaye", b,
                         duraklar=[q.kulli("mizan", j) for j in range(4)],
                         j=0)

    # --- 3) SÜKÛT EŞİĞİ: gaye uyanıksa sükût BASTIRILIR.
    # İşaret menfîdir ve sebebi budur: takip edilecek bir gaye doğduysa
    # susmak yanlıştır; gaye doğmadıysa (``|0⟩``) kontrol kapalıdır ve
    # sükût evvelki hâlinde kalır -- yani susmak varsayılan olur.
    #
    # **ÖLÇÜLEN VE DÜZELTİLEN KUSUR.** Bu satır ``j=1`` yazıyordu, yani
    # kapıyı ``gaye₁``e kontrol ediyordu -- halbuki doğuş yalnız
    # ``gaye₀``a yazıyor; ``gaye₁`` ``|0⟩``da kalıyor. Kontrolü ``|0⟩``
    # olan kontrollü dönme **hiçbir şey yapmaz**, yani sükût eşiği hiç
    # ateşlenmiyordu. Sessizdi: 6 satırlık bir ölçümde korelasyon
    # ``−0,63`` çıkıp "çalışıyor" görünüyordu, 5 satırda ``+0,77``ye
    # dönüyordu -- yani gördüğüm şey eşik değil gürültüydü.
    #
    # **VE AYNI KUSUR SÜKÛT UCUNDA DA VARDI (H159, müdahaleli ölçüm).**
    # Kapı düzeltildikten sonra ölçüldü::
    #
    #     tenakuz+nakz açık : gaye₀=0,3918  sükût=0,0741
    #     tasdik açık       : gaye₀=0,4990  sükût=0,0944
    #
    # Yani gaye **düşünce** sükût da düşüyordu -- taahhüdün tam tersi.
    # Sebep gayedeki ile aynı: ``sukut`` küçük bir açıda duruyor,
    # ``sin²`` orada çift, ve ``R(−ε)`` nüfusu düşürmek yerine
    # yükseltebiliyor. Çare de aynı: sükûtu evvelâ ``π/4``e çevir,
    # kapıyı **oradan** vur.
    q.tek(q.kulli("sukut", 0), donme(0.25 * math.pi))
    kesme += q.mpo_dagit("gaye", [-abs(EPSILON_DURGUN)],
                         duraklar=[q.kulli("sukut", 0)], j=0)
    return float(kesme)


def _aci(p, anahtar: str, n: int, olcek: float) -> np.ndarray:
    """Öğrenilen açı dilimi -- melekelerinkiyle aynı defterden."""
    from .melekeler import QParametre
    if isinstance(p, QParametre):
        return olcek * p.al(anahtar, n)
    return olcek * p.v(anahtar, n)


# =====================================================================
#  ÖLÇÜM -- akışın dışında
# =====================================================================
def odenen_bedel(q: QYazmac, ne: str = "landauer") -> Dict[str, float]:
    """AKIŞTA NE ÖDENDİ -- **tek terkip** (kütük H223).

    Küme: ``landauer_defteri`` + ``serbest_enerji_olcumu``. İkisi de tek
    suali soruyor: **bu akış neye mal oldu?** Biri bedeli termodinamik
    (silinen bit, Landauer), öteki bilgi-geometrik (serbest enerji)
    cinsten okur; ikisi de ``q``nun aynı marjinallerinden çıkar.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``landauer``    silinen bit ve ``kT ln2`` bedeli
    ``serbest``     ``F = kesinsizlik + karmaşıklık`` ayrışımı
    ==============  ==================================================

    **Landauer.** Bütün kapılar dik, yani tersinirdir; tek tersinmez
    adım kesmedir. ``F = Π (tutulan/tam)`` olduğuna göre silinen bit
    ``−log₂F``dir. ``kT ln2`` bir birim seçimidir; burada ``kT = 1``
    alınır ve sayı **nat** cinsinden de verilir ki birim tartışması
    hükmü değiştirmesin.

    **Serbest enerji.** Gayeyi bir gizli değişken ``z``, hükmü gözlem
    ``x`` sayarız::

        p(z) = gaye alanının marjinali
        q(z) = tasdik alanının marjinali   (hükmün "istediği")

    Ayrışım `fitrat`ın kendi koduyla hesaplanır -- yani bu ölçüm ana
    hattı **beylik bir kütüphaneyle** denetler, tıpkı `nefs/golge.py`
    gibi. **Bu bir hüküm değil bir ölçüdür**: "gaye serbest enerjiyi
    düşürüyor" diye bir iddia burada YOKTUR; sayı çıkar, hüküm
    `tanilama` tarafında iki koşu kıyaslanarak verilir.
    """
    if ne == "landauer":
        F = float(q.y.sadakat())
        bit = -math.log2(max(F, 1e-300))
        return {
            "sadakat": F,
            "silinen_bit": bit,
            "landauer_nat": bit * math.log(2.0),      # kT=1 iken enerji
            "kübit": float(q.n),
            "kübit_başına_bit": bit / max(q.n, 1),
        }
    if ne != "serbest":
        raise ValueError("bedel kipi bilinmiyor: %r" % (ne,))
    from fitrat.serbest_enerji import AyrikModel, kl, serbest_enerji_ayrisimi

    def marjinal(ad: str) -> np.ndarray:
        _, kac = q._alan[ad]
        yuv = [q.kulli(ad, j) for j in range(kac)]
        R = np.asarray(q.y.tekil_yogunluklar(yuv), float)[0]
        v = np.clip(R[:, 1, 1], 1e-9, 1.0 - 1e-9)
        v = np.concatenate([v, [1e-9]])          # sıfır ihtimali kapat
        return v / v.sum()

    pz = marjinal("gaye")
    qz = marjinal("tasdik")
    k = min(pz.size, qz.size)
    pz, qz = pz[:k] / pz[:k].sum(), qz[:k] / qz[:k].sum()

    # ``p(x|z)``: hükmün gaye şartındaki olabilirliği. Elde tek bir
    # durum olduğu için köşegen-ağırlıklı bir tablo kurulur; maksat
    # `fitrat`ın ayrışım kimliğini bu sayılar üzerinde İŞLETMEKtir.
    N = k
    pxz = np.full((k, N), 1.0 / N)
    np.fill_diagonal(pxz, 0.0)
    pxz = pxz + np.eye(k, N) * 0.5
    pxz = pxz / pxz.sum(axis=1, keepdims=True)

    m = AyrikModel(pz=pz, pxz=pxz)
    a = serbest_enerji_ayrisimi(m, qz, 0)
    return {
        "F": float(a["F"]),
        "kesinsizlik": float(a["kesinsizlik"]),
        "karmaşıklık": float(a["karmaşıklık"]),
        "ayrışım_sapması": float(a["ayrışım_sapması"]),
        "KL(tasdik‖gaye)": float(kl(qz, pz)),
    }


def rapor(tohum: int = 0, n: int = 6, d_in: int = 12) -> str:
    """Gaye açık ve kapalı: alan yaşıyor mu, ne değişiyor?"""
    from .melekeler import QNefs
    from .zihin_durumu import QAyar

    E = np.random.default_rng(tohum).normal(size=(n, d_in))
    s = ["=== GAYE (Dosya 4) -- muhtar gaye, Landauer, sükût eşiği ===",
         "",
         "H108 'gaye alanı hükümle dolaştırılır' diyordu. ÖLÇÜLDÜ:",
         "alan tam olarak |0⟩'daydı, yani hiç yazılmamıştı. Burada",
         "nakzedilir ve icra edilir.",
         ""]
    satirlar = []
    for acik in (False, True):
        q = QNefs(tohum, QAyar(bag=16, tohum=tohum), gaye=acik).idrak_et(E)
        alanlar = {}
        for ad, kac in q.ayar.kulli_alanlar:
            yuv = [q.kulli(ad, j) for j in range(kac)]
            R = np.asarray(q.y.tekil_yogunluklar(yuv), float)[0]
            alanlar[ad] = float(R[:, 1, 1].mean())
        satirlar.append((acik, alanlar, odenen_bedel(q, "landauer"),
                         odenen_bedel(q, "serbest")))

    adlar = [ad for ad, _ in satirlar[0][1].items()]
    s.append("  %-10s %12s %12s" % ("alan", "gaye KAPALI", "gaye AÇIK"))
    for ad in adlar:
        s.append("  %-10s %12.6f %12.6f"
                 % (ad, satirlar[0][1][ad], satirlar[1][1][ad]))

    s += ["", "LANDAUER DEFTERİ (akıştaki tek tersinmez adım: kesme):"]
    for acik, _, L, _ in satirlar:
        s.append("  gaye %-7s sadakat=%.3e  silinen bit=%.1f  "
                 "kübit başına %.3f"
                 % ("AÇIK" if acik else "KAPALI", L["sadakat"],
                    L["silinen_bit"], L["kübit_başına_bit"]))

    s += ["", "SERBEST ENERJİ (fitrat/serbest_enerji.py ile):"]
    for acik, _, _, F in satirlar:
        s.append("  gaye %-7s F=%.6f  kesinsizlik=%.6f  karmaşıklık=%.6f"
                 "  ayrışım sapması=%.1e"
                 % ("AÇIK" if acik else "KAPALI", F["F"], F["kesinsizlik"],
                    F["karmaşıklık"], F["ayrışım_sapması"]))
    s += ["",
          "Ayrışım sapması, `fitrat`ın F = kesinsizlik + karmaşıklık",
          "kimliğinin bu sayılarda fiilen tuttuğunun şahididir; sıfıra",
          "yakın olmalıdır. Gayenin faydası bu tabloda İDDİA EDİLMEZ --",
          "sayılar konur, hüküm ölçüme bırakılır."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
