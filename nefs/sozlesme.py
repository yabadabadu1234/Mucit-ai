"""
SADAKAT SÖZLEŞMESİ -- 41 melekenin neye dokunup neyi koruduğu.

Dosya 2 her meleke için üç şey istiyor: **neyi soyar**, **neyi korur**,
ve **çöküş şartı** nedir. Bu dosya o sözleşmeyi bir nesir tablosu
olarak değil, **icra edilebilir** bir taahhüt olarak kurar.

===================================================================
NİÇİN NESİR TABLO DEĞİL
===================================================================

Bir tabloya "𝒪₁₃ Tasdik yalnız tasdik alanına dokunur" yazmak kolaydır
ve **hiçbir şey ispat etmez**. H88'in dersi tam buydu: ``beyan``
aylarca yanlış çevreden okudu, çünkü iddiayı denetleyen bir şey yoktu.
İddia denetlenmiyorsa iddia değildir.

Burada her meleke dokunabileceği **bölgeleri** ilan eder ve ölçüm o
ilanı yüzleştirir. Yüzleştirmenin dayanağı bir cebir hakikatidir:

    ``S`` kübitlerine etki eden bir üniter ``U``, ``S``ye ayrık her
    ``A`` bölgesinin indirgenmiş yoğunluğunu **aynen bırakır**::

        ρ_A' = Tr_kalan U|Ψ⟩⟨Ψ|U†  =  Tr_kalan |Ψ⟩⟨Ψ|  =  ρ_A

    çünkü ``U`` iz alınan tarafta yaşar ve iz döngüseldir.

O hâlde: bir meleke koştuktan sonra ``ρ_A`` değişmişse, o meleke ``A``ya
**dokunmuştur** -- ne yazdığından, ne iddia ettiğinden bağımsız olarak.
Bu ölçüm melekenin şerhine değil, dalganın kendisine bakar.

===================================================================
ÇÖKÜŞ ŞARTI
===================================================================

Dosya 2'nin üçüncü sütunu "çöküş şartı"dır: melekenin ameliyesinin
geçersiz sayılacağı hâl. Burada iki şekilde ölçülür:

1. **Hudut ihlâli** -- ilan edilmemiş bir bölgeye dokunmak.
2. **Sadakat düşüşü** -- melekenin kendi kesmesinin, sınıfının bütçesini
   aşması. Bir "koruyucu"nun bir "kurucu"dan fazla bilgi atması
   sözleşmenin ruhuna aykırıdır.

İkisi de kırmızı yanabilir ve `test_nefs.py` ikisini de koşturur.

===================================================================
HUDUT -- açıkça
===================================================================

Ölçüm **kesme yüzünden gürültülüdür**: SVD budaması üniter değildir ve
dokunulmayan bölgelerin yoğunluğunu da bir parça oynatır. Onun için
eşik sıfır değil, ölçülmüş bir sayıdır (``ESIK``) ve nasıl seçildiği
aşağıda yazılıdır. Sıfır eşikle çalışıyormuş gibi yapılmaz.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .melekeler import QParametre, qmelekeler, qsicil
from .qyazmac import QAyar, QYazmac, donme

__all__ = ["BOLGELER", "SOZLESME", "dokunulan_bolgeler", "sozlesmeyi_olc",
           "rapor"]


#: Yüzleştirme eşiği -- ``|ρ' − ρ|``ın sonsuz normu.
#:
#: **Nasıl seçildi.** Sıfır olamaz: kesme üniter değildir ve
#: dokunulmayan bölgeleri de oynatır. Ölçüldü (χ=32, 4 satır): hiç
#: kapı vurmayan bir "boş meleke"de âzamî sapma 1e-16 mertebesinde,
#: hakikî dokunuşlarda ise 1e-3 ile 1e-1 arasında. Aradaki uçurum dört
#: mertebeden geniştir; eşik ortasına konur.
ESIK: float = 1e-6

#: Zincirdeki bölgeler. ``veri`` ve ``yerel`` satır başına tekrarlar;
#: kalanı küllî hüküm bloğunun alanlarıdır.
BOLGELER: Tuple[str, ...] = (
    "veri", "yerel", "makam", "mizan", "tenakuz", "tasdik", "sukut",
    "nakz", "kelam", "kaide", "orak", "gaye", "tertip",
    # --- ceride taksimatı (kütük H213). 𝒪₄₄ Tahsil ``parametre``
    # bölgesine dokunur; bu üçü listede olmadığı sürece sözleşme
    # ölçüsü oraya **kör**dü: meleke yazıyor, ölçü görmüyordu.
    "meleke_b", "parametre", "ancilla",
)


#: 41 melekenin sözleşmesi: ``no -> (dokunabileceği bölgeler, gerekçe)``.
#:
#: **Bu satırlar melekelerin kendi tariflerinden çıkarıldı, ölçümden
#: değil.** Yani burası taahhüttür; ölçüm onu YÜZLEŞTİRİR. İkisi
#: karışırsa sözleşme kendi kendini onaylar ve hiçbir şey ispat etmez.
SOZLESME: Dict[int, Tuple[Tuple[str, ...], str]] = {
    1:  (("veri",), "öz-dikkat: yalnız veri kübitleri"),
    2:  (("veri",), "hayal: satırın son veri kübitini aralar"),
    3:  (("veri",), "muhayyile: satır içi atlamalı çiftler"),
    4:  (("veri", "yerel"), "satırı kendi yerel hükmüne bağlar"),
    5:  (("veri",), "tecrit: fırça katmanının tersi"),
    6:  (("veri", "yerel"),
         "MERA kademesi satır bölgesine vurur; küllî bloğa DOKUNMAZ (H119)"),
    7:  (("yerel", "tasdik"), "mana: yerel hükümler tasdike akar"),
    8:  (("veri",), "tahlil: kübit başına dönme"),
    9:  (("veri",), "terkip: ters yönlü fırça"),
    10: (("veri",), "tezat: işaret çevirme"),
    11: (("yerel", "tenakuz"), "çelişki küllî tenakuz alanına akar"),
    12: (("yerel",), "tenkit: yerel hükmü bastırır"),
    13: (("tasdik",), "tasdik mührü: yalnız tasdik alanı"),
    14: (("tasdik", "mizan"), "gaye: tasdiki mîzâna bağlar"),
    15: (("nakz",), "merak: nakz alanını süperpozisyona sokar"),
    16: (("veri",), "keşif hamleleri"),
    17: (("mizan",), "önsel mîzâna yazılır"),
    18: (("veri",), "kıyas: komşu satırların veri kübitleri"),
    19: (("veri",), "temsil: dik ve tersinir"),
    20: (("veri",), "teşbih: ilk iki satır"),
    21: (("veri", "yerel", "makam"), "tefekkür: 20 mertebe, makama akar"),
    22: (("veri",), "illet: yönlü, satırdan satıra"),
    23: (("yerel", "nakz"), "mantık: nakz birikimi"),
    24: (("yerel",), "ispat: yerel hükümler zinciri"),
    25: (("veri",), "teemmül: aynı fırça, birkaç tur"),
    26: (("yerel",), "temkin: küçük açı"),
    27: (("veri",), "tetkik"),
    28: (("veri",), "tashih: tetkikin tersi"),
    29: (("veri",), "teyit: satırın iki ucu"),
    30: (("yerel", "tasdik"), "tahkik: ikinci yoldan tasdike"),
    31: (("veri", "mizan"), "tedebbür: ileri sarım + mîzân"),
    32: (("nakz", "tenakuz", "tasdik", "makam", "sukut"),
         "makam üç kaynaktan çevrilir, sükût kapısı açılır"),
    33: (("tasdik", "tenakuz", "nakz", "mizan"), "muhakeme: meclis"),
    34: (("yerel", "makam"), "tafsil: makam yerellere dağılır"),
    35: (("veri",), "tefsir: siyak ve sibak"),
    36: (("tenakuz", "tasdik"), "te'vil: çelişki şartıyla"),
    # --- BEYAN KAPISI (kullanıcı kat'î kararı / kütük H131):
    # dördü de ham veriden KOPARILDI; mana yalnız hükümden akar.
    37: (("yerel", "tasdik", "kelam"),
         "fesâhat: mana YEREL HÜKÜMden kelama akar; tasdik mührü şart"),
    38: (("tasdik", "kelam"), "talâkat: akıcılık tasdikten, veriden değil"),
    39: (("makam", "tasdik", "kelam"), "belâgat: makam ve tasdik kelama"),
    40: (("makam", "kelam"), "sanat: altın açı, yalnız hüküm ve kelamda"),
    41: (("mizan", "makam", "sukut", "kelam"), "münazara + sükût kapısı"),
    # --- 𝒪₄₂–𝒪₄₄ TEŞKİLÂT (kütük H213). Üçü de akışa yeni girdi;
    # sözleşmeleri kendi tariflerinden çıkarıldı, ölçümden değil.
    42: (("yerel", "mizan", "tenakuz"),
         "umumileştirme: bütün duraklardan AYNI açıyla mîzâna (kesişim), "
         "araz tenakuza"),
    43: (("kelam",),
         "talim: kelamı kademe kademe keskinleştirir (τ monoton azalan)"),
    44: (("mizan", "parametre"),
         "tahsil: mîzân kontrollü Gibbs sönümü + γ kimlik payı, "
         "parametre bölgesine"),
}


def _bolge_yuvalari(q: QYazmac) -> Dict[str, List[int]]:
    """Her bölgenin zincirdeki kübit yerleri."""
    d: Dict[str, List[int]] = {
        "veri": [q.veri(i, j) for i in range(q.n_satir)
                 for j in range(q.ayar.satir_kubiti)],
        "yerel": q.yereller(),
    }
    for ad, kac in q.ayar.kulli_alanlar:
        d[ad] = [q.kulli(ad, j) for j in range(kac)]
    # ceride taksimatı: bölge açıksa yuvaları da ölçüye girer.
    for ad, anahtar in (("meleke", "meleke_b"), ("parametre", "parametre"),
                        ("ancilla", "ancilla")):
        if q.bolge_var(ad):
            bas, kac = q.taksimat.bolge[ad]
            d[anahtar] = list(range(bas, bas + kac))
    return d


def _guzergah(q: QYazmac, ilan: Sequence[str]) -> set:
    """İlan edilen bölgelerin zincirde **kapladığı aralık**.

    **Ölçülen ve anlaşılan şey budur.** İlk yüzleştirmede 41 melekenin
    16'sı "ihlâl" verdi ve hepsinin sebebi tekti: MPS bir **zincirdir**;
    uzak iki kübite dokunmanın iki yolu vardır ve ikisi de aradan
    geçer --

    * **takas ağı** kübitleri fiilen yürütür; geçtiği her kesitte SVD
      budaması yapılır,
    * **MPO** kübit oynatmaz fakat ``bas``tan ``son``a bütün aralığı
      yeniden sıkıştırır.

    İkisi de cebren kimliktir; fakat **kesme üniter değildir**, o yüzden
    aradaki kübitlerin yoğunluğu bir parça oynar. Yani meleke o
    bölgelere *manen* dokunmaz, *fiilen* dokunur.

    Bu bir kusur değil MPS'in tabiatıdır ve gizlenmemelidir. O hâlde
    sözleşme iki şeyi ayırır: **hedef** (melekenin kastı) ve
    **güzergâh** (zincirin ona mecbur ettiği yol). İhlâl, güzergâhın da
    dışına çıkmaktır -- ve o hâlâ kırmızı yanabilir: mesela zincirin sağ
    ucundaki ``tertip``e dokunan bir veri melekesi yakalanır.

    Güzergâh **ilandan** türetilir, ölçümden değil. Ölçümden türetilseydi
    sözleşme kendi kendini onaylar ve hiçbir şey ispat etmezdi.
    """
    yuv = _bolge_yuvalari(q)
    hepsi: List[int] = []
    for ad in ilan:
        hepsi += yuv.get(ad, [])
    if not hepsi:
        return set(ilan)
    bas, son = min(hepsi), max(hepsi)
    return {ad for ad, y in yuv.items()
            if y and any(bas <= i <= son for i in y)}


def _yogunluklar(q: QYazmac) -> np.ndarray:
    """Bütün kübitlerin ``2×2`` indirgenmiş yoğunlukları."""
    return np.asarray(q.y.tekil_yogunluklar(list(range(q.n))), float)[0]


def _hazirla(n_satir: int, chi: int, tohum: int) -> Tuple[QYazmac, QParametre]:
    """Melekenin üzerinde koşacağı **dolaşık** bir başlangıç durumu.

    Çarpım durumunda ölçüm iş görmez: bir çok kapı ``|0⟩`` üzerinde
    hiçbir şey yapmaz ve meleke dokunduğu hâlde dokunmamış görünür.
    Onun için gerçek akışın başlangıcı kurulur: kodla → süperpozisyon →
    MERA.
    """
    rng = np.random.default_rng(tohum)
    q = QYazmac(n_satir, QAyar(bag=int(chi), tohum=tohum))
    q.kodla(rng.normal(size=(n_satir, 12)))
    q.superpozisyon()
    q.mera()
    # **KÜLLÎ BLOK UYANDIRILIR -- ve sebebi ölçülmüştür.**
    #
    # İlk yüzleştirmede 𝒪₃₂, 𝒪₃₃, 𝒪₃₄ ve 𝒪₃₉ ilan ettikleri küllî
    # alanlara "hiç dokunmamış" göründü. Sebep melekeler değil, ölçümün
    # kendisiydi: akışın başında küllî blok ``|0⟩``dadır (``superpozisyon``
    # ve artık ``mera`` oraya kasten dokunmaz), ve **kontrolü ``|0⟩``
    # olan bir kontrollü dönme hiçbir şey yapmaz**. Yani meleke atıl
    # değildi, ölçüm onu hiç ateşlememişti.
    #
    # Sözleşme melekenin DAYANAĞINI (support) tarif eder, filanca
    # koşudaki tesirini değil. O hâlde blok, hiçbir alanı ``|0⟩``da
    # bırakmayan cüzî bir dönmeyle uyandırılır. Bu, akışın davranışını
    # değiştirmez -- yalnız ölçüm burada yapılır.
    for ad, kac in q.ayar.kulli_alanlar:
        for j in range(kac):
            q.tek(q.kulli(ad, j), donme(0.4))
    return q, QParametre(tohum)


def dokunulan_bolgeler(no: int, n_satir: int = 4, chi: int = 32,
                       tohum: int = 0, esik: float = ESIK
                       ) -> Dict[str, object]:
    """``𝒪no`` fiilen hangi bölgelere dokundu? -- **ölçüm**, iddia değil."""
    q, p = _hazirla(n_satir, chi, tohum)
    once = _yogunluklar(q)
    qsicil()[int(no)].kosu(q, p)
    sonra = _yogunluklar(q)
    sapma = np.max(np.abs(sonra - once), axis=(1, 2))     # kübit başına

    yuv = _bolge_yuvalari(q)
    olculen, en_buyuk = [], {}
    for ad in BOLGELER:
        if not yuv.get(ad):
            continue
        s = float(np.max(sapma[np.asarray(yuv[ad], np.intp)]))
        en_buyuk[ad] = s
        if s > esik:
            olculen.append(ad)

    ilan = set(SOZLESME[int(no)][0])
    guz = _guzergah(q, ilan)
    return {
        "no": int(no),
        "ilan": tuple(sorted(ilan)),
        "güzergâh": tuple(sorted(guz - ilan)),
        "ölçülen": tuple(sorted(olculen)),
        "ihlâl": tuple(sorted(set(olculen) - guz)),
        "kullanılmayan": tuple(sorted(ilan - set(olculen))),
        "sapma": en_buyuk,
        "sadakat": float(q.y.sadakat()),
    }


def sozlesmeyi_olc(n_satir: int = 4, chi: int = 32, tohum: int = 0
                   ) -> List[Dict[str, object]]:
    """41 melekenin hepsini tek tek yüzleştir."""
    return [dokunulan_bolgeler(m.no, n_satir, chi, tohum)
            for m in qmelekeler()]


def rapor(n_satir: int = 4, chi: int = 32, tohum: int = 0) -> str:
    o = sozlesmeyi_olc(n_satir, chi, tohum)
    s = ["=== SADAKAT SÖZLEŞMESİ (Dosya 2) -- yüzleştirme ===",
         "",
         "Her meleke dokunacağı bölgeleri İLAN eder; ölçüm dalganın",
         "kendisine bakıp fiilen dokunduğunu bulur. İkisi ayrı düşerse",
         "sözleşme ihlâl edilmiştir. Eşik = %.0e." % ESIK,
         "",
         "  𝒪   meleke              ihlâl / kullanılmayan"]
    ihlal_sayisi = 0
    bos_sayisi = 0
    sic = qsicil()
    for r in o:
        no = int(r["no"])
        ih, ku = r["ihlâl"], r["kullanılmayan"]
        if ih:
            ihlal_sayisi += 1
        if ku:
            bos_sayisi += 1
        isaret = "İHLÂL: " + ",".join(ih) if ih else ""
        if ku:
            isaret += ("  " if isaret else "") + "boş ilan: " + ",".join(ku)
        s.append("  %-3d %-20s %s" % (no, sic[no].ad, isaret or "✓"))
    s += ["",
          "%d melekede hudut ihlâli, %d melekede kullanılmayan ilan."
          % (ihlal_sayisi, bos_sayisi),
          "",
          "İHLÂL: meleke ilan etmediği bir bölgeye dokunmuş -- ya şerhi",
          "yanlış ya kapısı. KULLANILMAYAN İLAN: meleke ilan ettiği bir",
          "bölgeye HİÇ dokunmamış; sözleşme olduğundan geniş, yani",
          "denetlemiyor. İkincisi ihlâl kadar ağır değildir fakat bir",
          "gevşekliktir ve sayılır."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
