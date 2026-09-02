"""22 milyon kübitin Hilbert yazmaç taksimatı -- **tek zincirde**.

Ceridenin (``docs/ceride/TERKIP_LAYIHASI.md``, VI. Bölüm) hükmü şudur::

    |Ψ⟩ = |x⟩ ⊗ |D⟩ ⊗ |m⟩ ⊗ |a⟩

    parametre |x⟩   2.097.152 kübit   (2²¹)
    veri      |D⟩   8.388.608 kübit   (2²³)
    meleke    |m⟩     524.288 kübit   (2¹⁹)
    ancilla   |a⟩  10.989.952 kübit   (artan)
    ───────────────────────────────────────
    toplam         22.000.000 kübit

**Ceridenin bu şemasına dair ilk tenkidim** (H100: her söylediğini
kontrol et). Üç bölge tam ikinin kuvvetidir; dördüncüsü değildir:
``10.989.952 = 22.000.000 − 2²¹ − 2²³ − 2¹⁹``. Yani ancilla bir hesabın
neticesi değil, **yuvarlak 22 milyona tamamlayan artıktır**. Şemanın
keyfî olan tarafı ancilla değil **22 milyon sayısının kendisidir**; bu
bir kusur değildir fakat "ancilla şu kadar olmalı" diye bir riyazî
hüküm de yoktur. ``ANCILLA_ARTIK`` bunu koda yazar ve sınama denetler.

**Bu dosyanın asıl hükmü: paralel değil, eklemli.** Kullanıcı hükmü
açıktır -- *"tek ve paralel olmayan, yek vücut çok uzuvlu bir model"*.
Dört bölge dört ayrı model olsaydı, aralarındaki kesitte dolaşıklık
entropisi **tam sıfır** olurdu (çarpım durumu). Bu dosya bölgeleri aynı
MPS zincirine yerleştirir ve ``eklem_olcusu`` her bölge sınırındaki
entropiyi ölçer: sınır ölü ise (S ≈ 0) o eklem **yoktur** ve ölçü
KIRMIZI yanar (H90: her ölçü kırmızıya da dönebilmeli).

Zincir sırası ``veri → hüküm → meleke → parametre → ancilla``dır ve
sebebi yerelliktir: Ĥ_Dimağ(θ) = Σ_m … [Σ_a θ_m^a T^a] … formülünde θ
hem ``m`` (mertebe) hem ``a`` (üreteç) ile indislidir; yani meleke ile
parametre **komşu** olmalıdır ki aralarındaki kapı ucuz olsun. Meleke
de hükmü seçtiği için hükmün bitişiğindedir. Ancilla en sağdadır: iş
alanıdır, kimse onunla uzaktan konuşmaz.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["CERIDE_TAKSIMAT", "CERIDE_TOPLAM", "ANCILLA_ARTIK",
           "BOLGE_SIRASI", "taksim", "Taksimat", "eklem_olcusu"]


#: Ceridenin tescil ettiği kübit adetleri, harfiyen.
CERIDE_TAKSIMAT: Dict[str, int] = {
    "parametre": 2_097_152,      # 2²¹  -- θ, model ağırlıkları
    "veri": 8_388_608,           # 2²³  -- B=2048 dizi × L=4096 bağlam
    "meleke": 524_288,           # 2¹⁹  -- hangi uzuv uyanık
    "ancilla": 10_989_952,       # artık -- QSVT/FPAA iş alanı
}

#: Ceridenin ilan ettiği toplam.
CERIDE_TOPLAM: int = 22_000_000


def ANCILLA_ARTIK() -> int:
    """Ancilla'nın hesabı: toplamdan üç ikinin kuvvetini çıkar.

    Ceride ancillayı müstakil bir riyazî hükümle vermez; bu fonksiyon
    onun **artık** olduğunu ispat eder ve sınama bunu denetler.
    """
    return CERIDE_TOPLAM - (CERIDE_TAKSIMAT["parametre"]
                            + CERIDE_TAKSIMAT["veri"]
                            + CERIDE_TAKSIMAT["meleke"])


#: Zincirdeki soldan sağa sıra (yerellik gerekçesi dosya şerhindedir).
BOLGE_SIRASI: Tuple[str, ...] = ("veri", "hukum", "meleke", "parametre",
                                 "ancilla")


def taksim(toplam: int, asgari: int = 1,
           veri_sabit: Optional[int] = None,
           hukum_sabit: int = 0) -> Dict[str, int]:
    """``toplam`` kübiti ceridenin **nispetleriyle** böl -- ölçekten bağımsız.

    ``toplam = CERIDE_TOPLAM`` iken netice ceridenin cetveliyle
    **birebir** aynıdır (sınama denetler). Küçük toplamlarda nispet
    korunur, artan kübitler en büyük kalanlara verilir (largest
    remainder), her bölgeye en az ``asgari`` düşer.

    ``veri_sabit`` verilirse veri bölgesi o adede sabitlenir ve geri
    kalan üç bölge kendi aralarında ceride nispetiyle paylaşır -- mevcut
    padişahın veri kübitleri zaten mevcut olduğu için eklemleme bu yolla
    yapılır. ``hukum_sabit`` küllî hüküm bloğudur; ceridede karşılığı
    yoktur, olduğu gibi ayrılır ve nispet hesabına **girmez**.
    """
    toplam = int(toplam)
    ad = [a for a in BOLGE_SIRASI if a != "hukum"]
    out: Dict[str, int] = {"hukum": int(hukum_sabit)}
    kalan = toplam - int(hukum_sabit)
    if veri_sabit is not None:
        out["veri"] = int(veri_sabit)
        kalan -= int(veri_sabit)
        ad = [a for a in ad if a != "veri"]
    if kalan < asgari * len(ad):
        raise ValueError("taksim için kübit yetmiyor: %d kaldı, %d lâzım"
                         % (kalan, asgari * len(ad)))
    nispet = np.array([CERIDE_TAKSIMAT[a] for a in ad], float)
    nispet = nispet / nispet.sum()
    # **ÖLÇÜLEN VE DÜZELTİLEN HATA.** Evvelce her bölgeden ``asgari``
    # kadarı baştan ayrılıp kalan nispetle bölünüyordu. O usul ceridenin
    # kendi toplamında bile şaşıyordu: ``taksim(22.000.000)`` bölgeleri
    # ±1 kaydırıyor, yani şemayı **kendi sayısında doğrulayamıyordu**.
    # Doğrusu, önce saf nispetle bölmek; ``asgari`` ancak bir bölge
    # onun altına düşerse devreye girer. Büyük toplamda hiç girmez ve
    # netice ceridenin cetveliyle birebir çıkar (sınama denetler).
    ham = nispet * kalan
    tam = np.floor(ham).astype(int)
    artik = int(kalan - tam.sum())
    for k in np.argsort(-(ham - tam))[:max(artik, 0)]:
        tam[k] += 1
    if int(tam.min()) < asgari:
        # küçük ölçekte nispet sıfıra yuvarlanır; asgariyi tesis edip
        # farkı en büyük bölgeden düş.
        tam = np.maximum(tam, asgari)
        while int(tam.sum()) > kalan:
            tam[int(np.argmax(tam))] -= 1
    for a, v in zip(ad, tam):
        out[a] = int(v)
    return out


@dataclass
class Taksimat:
    """Bir zincirin bölge haritası: ad → (başlangıç, adet).

    ``kesitler`` bölge sınırlarının zincirdeki yeridir; ``eklem_olcusu``
    tam oralarda entropi ölçer. Sınırlar **iddia değil adres**tir.
    """
    bolge: Dict[str, Tuple[int, int]]
    sira: Tuple[str, ...] = BOLGE_SIRASI

    @classmethod
    def kur(cls, olculer: Dict[str, int],
            sira: Sequence[str] = BOLGE_SIRASI) -> "Taksimat":
        b: Dict[str, Tuple[int, int]] = {}
        k = 0
        for ad in sira:
            n = int(olculer.get(ad, 0))
            b[ad] = (k, n)
            k += n
        return cls(bolge=b, sira=tuple(sira))

    @property
    def n(self) -> int:
        return sum(n for _, n in self.bolge.values())

    def yer(self, ad: str, j: int = 0) -> int:
        """``ad`` bölgesinin ``j``inci kübitinin zincir adresi."""
        bas, kac = self.bolge[ad]
        if kac <= 0:
            raise KeyError("bölge boş: %s" % ad)
        return bas + (int(j) % kac)

    def araligi(self, ad: str) -> List[int]:
        bas, kac = self.bolge[ad]
        return list(range(bas, bas + kac))

    def kesitler(self) -> Dict[str, int]:
        """Komşu bölgeler arasındaki kesit yerleri: ``"veri|hukum"`` → k.

        Boş bölgeler atlanır: sıfır kübitlik bir bölgenin sınırı yoktur,
        onu ölçmek sahte bir kesit uydurmak olurdu.
        """
        dolu = [a for a in self.sira if self.bolge[a][1] > 0]
        out: Dict[str, int] = {}
        for sol, sag in zip(dolu, dolu[1:]):
            bas, kac = self.bolge[sol]
            out["%s|%s" % (sol, sag)] = bas + kac
        return out

    def cetvel(self) -> str:
        satir = ["  %-10s %8s  %8s  %s" % ("BÖLGE", "KÜBİT", "%", "ADRES")]
        top = max(self.n, 1)
        for ad in self.sira:
            bas, kac = self.bolge[ad]
            satir.append("  %-10s %8d  %7.2f%%  [%d, %d)"
                         % (ad, kac, 100.0 * kac / top, bas, bas + kac))
        satir.append("  %-10s %8d" % ("TOPLAM", self.n))
        return "\n".join(satir)


def eklem_olcusu(yazmac, taksimat: Taksimat, pencere: Optional[int] = None,
                 esik: float = 1e-9) -> Dict[str, object]:
    """Her bölge sınırındaki dolaşıklık -- **eklem var mı, yok mu**.

    Kullanıcının hükmü ``paralel olmayan, yek vücut``tur. Bu ölçü tam
    onu denetler ve **kırmızıya dönebilir** (H90):

    * ``S(kesit) > esik``  → o sınırda iki uzuv birbirine bağlıdır.
    * ``S(kesit) ≤ esik``  → o sınır bir **çarpım durumudur**; iki taraf
      fiilen iki ayrı modeldir, yani paraleldir. KIRMIZI.

    Dönen ``kopuk`` boş değilse iddia edilemez; iddia edilirse yalandır.
    """
    kes = taksimat.kesitler()
    S: Dict[str, float] = {}
    for ad, k in kes.items():
        # **Pencere zincirin BAŞINA kadar açılır** ve bu bir tashihtir.
        # ``dolasiklik_entropisi`` pencerenin ilk yuvasını sol uçmuş gibi
        # (``A[:,bas][:,0]``) alır; bu ancak pencere zincirin başından
        # başlarsa doğrudur. Varsayılan ``pencere=24`` ile iç kesitlerde
        # yanlış bir dizey çıkıyor ve entropi **sahte sıfır** okunuyordu:
        # ilk ölçümde ``hukum|meleke`` sınırı 0,000 göründü, halbuki o
        # sınırı kesen kapı fiilen vardı. Ölü eklem ile ölçülemeyen
        # eklem aynı şey değildir; ölçü aleti düzeltilmeden hüküm
        # verilemez (kütük H159 zeyli, H167).
        p = int(k) if pencere is None else int(pencere)
        e = yazmac.dolasiklik_entropisi(kesit=int(k), pencere=p)
        S[ad] = float(e["entropi"])
    kopuk = [ad for ad, v in S.items() if v <= float(esik)]
    # **DOYMA FRENİ -- yalancı yeşilin panzehiri.** Bir MPS kesitinde
    # entropi ``ln χ``yi aşamaz. Ölçüldü: χ=8'de dört sınırın dördü de,
    # dimağ açısı 0,05 ile 0,785 arasında ne olursa olsun, **tam
    # 2,0794 = ln 8** okuyor; χ=16'da tam ``ln 16``. Yani o iki bağda
    # ölçü açıdan bağımsızdır: eklemin kuvvetini değil, yalnız bağın
    # tavanını gösterir. Ancak χ=32'de sayı ayrışıyor (1,384 → 3,083).
    #
    # Bundan çıkan hüküm: ``eklemli`` (sıfır mı değil mi) her χ'de
    # geçerlidir; fakat "eklem şu kadar KUVVETLİ" iddiası ancak
    # ``doymus`` boşken edilebilir. Doymuş bir okumadan kuvvet
    # devşirmek, ölçüyü yalanlamaktır (kütük H167'nin dersi).
    tavan = float(np.log(max(int(getattr(yazmac, "bag", 2)), 2)))
    doymus = [ad for ad, v in S.items() if v >= tavan - 1e-6]
    return {"entropi": S,
            "kopuk": kopuk,
            "doymus": doymus,
            "tavan": tavan,
            "eklemli": len(kopuk) == 0 and len(S) > 0,
            "kuvvet_okunur": len(doymus) == 0 and len(S) > 0,
            "asgari": (min(S.values()) if S else 0.0),
            "kesit": kes}


def _rapor() -> str:                                    # pragma: no cover
    """Kendi kendini gösterme (kütük H126): şema ve ölçü, iddiasız."""
    sat = ["22 MİLYON KÜBİTİN TAKSİMATI -- ceridenin cetveli",
           Taksimat.kur(taksim(CERIDE_TOPLAM)).cetvel(),
           "",
           "ancilla artık mıdır: %d == %d  →  %s"
           % (ANCILLA_ARTIK(), CERIDE_TAKSIMAT["ancilla"],
              ANCILLA_ARTIK() == CERIDE_TAKSIMAT["ancilla"]),
           "",
           "AYNI NİSPET, KÜÇÜK ÖLÇEKTE (padişahın fiilî zinciri):",
           ]
    from nefs.qyazmac import QAyar, QYazmac
    q = QYazmac(5, QAyar(bolge_ac=True))
    sat.append(q.taksimat.cetvel())
    v = np.random.default_rng(0).normal(size=(5, 8))
    q.kodla(v); q.superpozisyon(); q.mera()
    o1 = q.eklem_olcusu()
    q.dimag()
    o2 = q.eklem_olcusu()
    sat.append("")
    sat.append("  %-22s %10s %10s" % ("SINIR", "dimağ önce", "dimağ sonra"))
    for ad in o1["entropi"]:
        sat.append("  %-22s %10.4f %10.4f"
                   % (ad, o1["entropi"][ad], o2["entropi"][ad]))
    sat.append("  eklemli: %s → %s   (tavan ln χ = %.4f, doymuş: %s)"
               % (o1["eklemli"], o2["eklemli"], o2["tavan"], o2["doymus"]))
    return "\n".join(sat)


if __name__ == "__main__":   # pragma: no cover
    print(_rapor())
