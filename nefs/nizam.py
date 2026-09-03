"""
DOLAŞIKLIK NİZAMI -- sınıf ilanının ölçümle yüzleştirilmesi.

===================================================================
NİÇİN VAR: İKİ BORÇ VE BİR YANLIŞ ŞERH
===================================================================

**1. borç (H148).** 𝒪₅ Tecrit'in şerhi şöyle diyordu:

> *"MERA'nın ``U``su gibi çalışır fakat ters yönde… Fırça katmanının
> tersi (``Gᵀ``) uygulanır; dik olduğu için bu tam tersidir ve bilgi
> kaybetmez."*

İddia **iki cihetten de yanlıştı** ve okunarak tespit edildi:

* ``G``, 𝒪₅'in **kendi** açılarından kuruluyor (``aci`` anahtarı
  ``q5.Tecrit/6``), 𝒪₁'inkinden değil. Yani başka bir kapının
  devriği; tersi değil.
* 𝒪₁ Müşahede **iki** fırça katmanı vuruyor (ofset 0 ve 1); 𝒪₅
  yalnız birine dokunuyor. Tersi olsaydı ikisini ters sırayla
  geri alması gerekirdi.

Ölçüm de bunu doğruladı: χ tavanı kalkınca 𝒪₅ entropiyi 3,357'den
yalnız 3,346'ya indiriyor -- yani **hiç çözmüyor**. "Çözücülüğü"
tamamen kesmeden geliyormuş (H148).

**2. borç (H149).** χ tavanını icradan kaldırırken şöyle yazmıştım:
*"``CHI`` kaldırılmadı: sınıf ilanı manalı bir taahhüttür ve
``nizam_yuzlestir()`` onu ölçümle yüzleştirir."* **O fonksiyonu hiç
yazmamıştım.** Şerhte adı geçen, kodda olmayan bir yüzleştirme, tam da
H88'in dersinin tekrarıdır: denetlenmeyen iddia, iddia değildir.

===================================================================
İŞİN KÜNHÜ: SABİT BİR ÜNİTER ÇÖZÜCÜ OLAMAZ
===================================================================

𝒪₅'i "hakikî tersi" yapmak da doğru cevap **değildir**. Zira:

    Parametresi sabit bir üniter, keyfî bir durumun dolaşıklığını
    azaltamaz. Çözmek **duruma bağlıdır**; melekeler ise durumu
    okuyamaz (kütük H31).

MERA'nın çözücüsü (disentangler) işe yarar çünkü **durum topluluğu
için eniyilenmiştir** -- yani öğrenilmiştir. O hâlde 𝒪₅ ancak
*eğitilerek* çözücü olur, *iddia edilerek* değil.

Bu dosya o eğitimi mümkün kılar: her melekenin sınıf ilanı
(``kurucu``/``koruyucu``/``çözücü``) bir **taahhüt**tür, ölçülür, ve
ihlâli **öğrenilebilir kayba** girer (`nefs/kulli_kayip.py`). Böylece
𝒪₅ "çözücüyüm" dediği için değil, **fiilen çözdüğü için** çözücü olur.

===================================================================
ÖLÇÜT: ΔS -- melekenin dolaşıklığa tesiri
===================================================================

Her melekeden önce ve sonra yarım-zincir von Neumann entropisi ``S``
okunur; ``ΔS = S_sonra − S_önce``. Taahhüt bir **bölge**dir::

    kurucu    : ΔS ≥ +B   (dolaşıklık kurar)
    çözücü    : ΔS ≤ −B   (dolaşıklık çözer)
    koruyucu  : |ΔS| ≤ B  (ne kurar ne bozar)

**Bölge, çünkü işaret körmüş (H157).** İlk yazdığımda ölçüt yalnız
işarete bakıyordu: "cihete ters düşmüyorsa ihlâl yok". İlk koşuda
41 melekenin yarıdan fazlası ``±0,0000`` okudu -- ve sıfır hiçbir
cihete ters düşmediği için hepsi "tam uydu" çıktı. 𝒪₅ Tecrit, hiç
çözmediği hâlde, tam not aldı. Bu **tam da H148'in borcunu ölçünün
körlüğünde saklamak** olurdu. Taahhüt bir iş taahhüdüdür: işi
yapmamak da ihlâldir, ve eksiklik ölçüsü sıfırda düz değil eğimli
olduğu için eğitim ona yol bulabilir.

``yuzlestir()`` her melekenin ölçülen ΔS'ini ilanıyla beraber
döker, uyanı da uymayanı da sayar.

===================================================================
HUDUT -- açıkça
===================================================================

* ``ΔS`` yarım zincir kesitinden okunur; başka bir kesitte başka
  çıkabilir. Tek bir sayı dolaşıklığın tamamını tarif etmez.
* Entropi okumak melekeye başına bir SVD'ye mal olur. Bedel
  gizlenmiyor ve ``sinif_olcumu=False`` ile kapatılabilir --
  kapatılamayan bir tedbirin faydası ölçülemez (kütük H90).
* Bu ölçüm **eğitim ölçütündedir**, akışta değil: hiçbir meleke onu
  okumaz, akışın kararları değişmez (H31 yerinde durur).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["SINIF_CIHETI", "NIZAM_BANDI", "KORUYUCU_BANDI",
           "sinif_ihlali", "yuzlestir", "rapor"]


#: Sınıfın taahhüt ettiği **cihet**: ``ΔS``in işareti ne olmalı.
#: ``+1`` artmalı, ``−1`` azalmalı, ``0`` değişmemeli.
SINIF_CIHETI: Dict[str, int] = {
    "kurucu": +1,
    "çözücü": -1,
    "koruyucu": 0,
}

#: Taahhüdün **bandı**: bir melekenin "yaptım" diyebilmesi için
#: ``ΔS``i en az bu kadar oynatması gerekir; ``koruyucu`` için de
#: "değişmedi" sayılan hudut budur. Sıfır olamaz: kesme üniter
#: değildir ve dokunulmayan bölgeleri de bir parça oynatır (aynı
#: gerekçe `nefs/sozlesme.py`nin ``ESIK``inde de yazılı).
NIZAM_BANDI: float = 0.05

#: Eski ad; H157'den evvel yalnız ``koruyucu``ya bakıyordu.
KORUYUCU_BANDI: float = NIZAM_BANDI


def sinif_ihlali(sinif: str, dS: float) -> float:
    """Taahhüde uymayan kısım, ``[0,1]``de. ``0`` = tam uydu.

    Her sınıf ``ΔS`` için bir **bölge** taahhüt eder; ihlâl, o bölgeye
    olan **eksiklik**tir::

        kurucu    : ΔS ≥ +B      ihlâl = tanh(max(0, B − ΔS))
        çözücü    : ΔS ≤ −B      ihlâl = tanh(max(0, B + ΔS))
        koruyucu  : |ΔS| ≤ B     ihlâl = tanh(max(0, |ΔS| − B))

    **Niçin bölge, yalnız işaret değil (H157).** İlk hâli "cihet
    tutuyorsa ihlâl yok" diyordu. Ölçünce görüldü ki 41 melekenin
    çoğu ``±0,0000`` okuyor -- ve sıfır, hiçbir cihete ters
    düşmediği için **her taahhüde uyuyor** sayılıyordu. Yani hiç
    çözmeyen 𝒪₅ Tecrit "tam uydu" notu alıyordu: tam da H148'in
    kapatmaya çalıştığı borç, ölçünün körlüğünde saklanıyordu.
    Taahhüt bir **iş** taahhüdüdür; işi yapmamak da ihlâldir.

    ``tanh`` ile sıkıştırılır ki tek bir uçuk ölçüm bütün kaybı ele
    geçirmesin -- H145'te ölçülen "doymuş uzuv" kusuru tekrarlanmasın.
    Eksiklik ölçüsü bölge dışında her yerde **eğimlidir**; işaret
    ölçüsü ise sıfırda düz olduğu için eğitime yol göstermiyordu.
    """
    c = SINIF_CIHETI.get(str(sinif), 0)
    d = float(dS)
    if c == 0:
        eksik = abs(d) - NIZAM_BANDI
    else:
        # ``c*d`` cihet doğruysa müsbet; bölgeye girmek için ≥ bant.
        eksik = NIZAM_BANDI - c * d
    return float(np.tanh(max(0.0, eksik)))


def yuzlestir(nefs=None, E: Optional[np.ndarray] = None,
              ayar=None) -> List[Dict[str, object]]:
    """41 melekenin ilanını ölçülen ``ΔS`` ile yüzleştir.

    Dönen her satır: ``no, ad, sınıf, ΔS, ihlâl, uydu_mu``.
    """
    from .kulli_kayip import olcumlu_idrak
    from .qmeleke import qsicil

    if nefs is None:
        from idrak import arc

        from main.egitim import KISA_CPU
        from .qakis import QNefs
        from .qegitim import belirtecleri_kodla, ornekler
        a = ayar or KISA_CPU
        nefs = QNefs(a.tohum, a.qayar())
        nefs.idrak_et(np.zeros((2, a.satir_kubiti)))
        veri = ornekler(arc.yukle_hepsi("training")[:6], azami=2,
                        pencere=a.pencere, sozluk=a.sozluk)
        E = np.stack([belirtecleri_kodla(b, a.satir_kubiti, a.sozluk)
                      for b, _ in veri])
    _q, _ok, dS = olcumlu_idrak(nefs, E, meleke_olcumu=False,
                                sinif_olcumu=True)
    sic = qsicil()
    out: List[Dict[str, object]] = []
    for no in sorted(dS):
        m = sic[no]
        d = float(dS[no])
        ih = sinif_ihlali(m.SINIF, d)
        out.append({"no": no, "ad": m.ad, "sınıf": m.SINIF,
                    "ΔS": d, "ihlâl": ih, "uydu_mu": ih <= 1e-9})
    return out


def rapor() -> str:
    s = ["=== DOLAŞIKLIK NİZAMI -- ilan ile ölçümün yüzleştirilmesi ===",
         "",
         "Her meleke bir SINIF ilan eder; taahhüdü ΔS'in bölgesidir:",
         "  kurucu ΔS≥+%.2f   çözücü ΔS≤−%.2f   koruyucu |ΔS|≤%.2f"
         % (NIZAM_BANDI, NIZAM_BANDI, NIZAM_BANDI),
         "",
         "  𝒪   meleke               sınıf      ΔS       ihlâl"]
    satir = yuzlestir()
    uyan = 0
    for r in satir:
        uyan += bool(r["uydu_mu"])
        s.append("  %-3d %-20s %-10s %+8.4f  %.4f%s"
                 % (r["no"], r["ad"], r["sınıf"], r["ΔS"], r["ihlâl"],
                    "" if r["uydu_mu"] else "   ← İHLÂL"))
    s += ["",
          "%d/%d meleke ilanına uyuyor." % (uyan, len(satir)),
          "",
          "İhlâl bir kusur değil bir **eğitim işareti**dir: ölçü",
          "`nefs/kulli_kayip.py`nin öğrenilebilir kaybına girer, yani",
          "meleke 'çözücüyüm' dediği için değil FİİLEN çözdüğü için",
          "çözücü olur. 𝒪₅ Tecrit'in H148'de açık kalan borcu budur:",
          "sabit bir üniter keyfî bir durumu çözemez; çözücülük ancak",
          "eğitilerek kazanılır, iddia edilerek değil."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
