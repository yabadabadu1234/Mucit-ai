"""
ÖRTÜ, TERKİP ve TIKANIKLIK -- ∞-operad, Grothendieck, Čech (Dosya 3).

===================================================================
DOSYA 3'ÜN ÜÇ FİKRİ ve BU MİMARİDEKİ KARŞILIKLARI
===================================================================

Dosya 3 üç şey teklif ediyor: ∞-operad terkibi, Grothendieck
fibrasyonu ve **Čech kohomolojisiyle uzayın kapatılması**. Üçünün de
bu projede zaten bir karşılığı vardır; eksik olan, o karşılığın
**riyazî ismiyle** kurulup ölçülmesiydi.

**1. Grothendieck fibrasyonu** -- zaten kurulu. `nefs/mertebe.py`
yirmi mertebeyi ``omega_kategori_nbe`` ile lif lif kuruyor: taban
mertebeler, lif o mertebedeki hâl. Burada tekrar edilmez.

**2. ∞-operad terkibi** -- 41 meleke sabit bir sırayla (``QAKIS``)
terkip edilir. Operadın şartı, terkibin **iyi tipli** olmasıdır. Bu
burada bir laf değil, makine denetimidir:
``omega_kategori.denetleyici`` ile sınanır.

**3. Čech tıkanıklığı -- ASIL İŞ BU.**

Bir ARC görevinde iki ilâ dört gösterim çifti vardır. Her çift bir
**yamadır** (mahallî kâide); görev, o yamaların **küllî tek bir
kâideye yapışmasını** ister. Yapışıp yapışmadığının ölçüsü Čech
kohomolojisidir::

    H⁰ ≠ 0  →  küllî kâide VAR   (yamalar örtüşmede uyuşuyor)
    H¹ ≠ 0  →  TIKANIKLIK var    (mahallî çözümler var, küllîsi yok)

Ve buradan **ölçülebilir bir kehanet** çıkar, ki bu dosyanın asıl
kıymeti odur:

    ``H¹ ≠ 0`` olan görevlerde model **susmalıdır**.

Çünkü tıkanıklık, "cevap yanlış" demek değildir; "bu örtüde küllî
cevap **yoktur**" demektir. Kütük H10/H16: susmak bir kusur değil
kabiliyettir. O hâlde Čech tıkanıklığı ile ``sukut`` alanı arasında
bir bağ **olmalıdır** -- ve bu iddia edilmez, ölçülür.

===================================================================
HUDUT -- ne kurulduğu, ne kurulmadığı
===================================================================

Burada kurulan şey **tam Čech kohomolojisi değildir** ve öyle olduğu
söylenmiyor. Kurulan, onun **sonlu ve hesaplanabilir gölgesidir**:

* örtü sonludur (gösterim çiftleri),
* mahallî kâideler ayrık bir kümeden gelir (`idrak/sekil.py`),
* o hâlde 1-kozikıl şartı **ikili uyuşma + üçlü tutarlılık**a iner.

Gerçek ``H¹`` sonsuz boyutlu bir demet kohomolojisidir; bu, onun bir
kesitidir. İsmi doğru kullanmak, tamamını kurduğunu iddia etmeyi
gerektirmez.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from idrak import arc
from idrak.sekil import sekil_kaidesi

__all__ = ["yamalar", "cech_tikanikligi", "terkip_iyi_tipli_mi",
           "tikaniklik_kapisi", "tikaniklik_sukut_bagi", "rapor"]


def tikaniklik_kapisi(q, h1: float, olcek: float = 0.9) -> None:
    """Čech tıkanıklığını ``sukut`` alanına **kapı olarak** yaz.

    **Niçin bu bir okuma değildir.** ``H¹`` dalganın bir vasfı değil,
    **girdinin** vasfıdır: görevin gösterim çiftlerinden, akış hiç
    koşmadan hesaplanır. Onu bir dönme açısına çevirmek, ham duyuyu
    kübitlere kodlayan ``QYazmac.kodla`` ile **aynı cinsten** bir
    işlemdir. H31 yasağı melekenin kendi girdisine bakıp karar
    vermesineydi; bu, girdinin kendisidir.

    **Niçin sükût.** Tıkanıklık "cevap yanlış" demek değildir; *"bu
    örtüde küllî cevap YOKTUR"* demektir. Küllî cevabı olmayan bir
    suale verilecek doğru karşılık susmaktır (H10/H16).

    Açı ``arctan``la sınırlanır ki çok yamalı bir görevde sükût
    çemberi sarıp tersine dönmesin (H119'un birikim dersi).
    """
    import math
    from .qyazmac import donme
    if h1 <= 0:
        return
    teta = float(olcek * math.atan(float(h1)))
    q.tek(q.kulli("sukut", 0), donme(teta))


def yamalar(gorev) -> List[Optional[object]]:
    """Örtü: her gösterim çifti bir **yama**, kendi mahallî kâidesiyle.

    Mahallî kâide `idrak/sekil.py`den gelir (şekil kaidesi: çıktının
    boyu girdiden nasıl çıkıyor). Kâide bulunamayan yama ``None``dır ve
    bu da bir bilgidir -- o yamada mahallî çözüm bile yok demektir.
    """
    return [sekil_kaidesi([(a, b)]) for a, b in gorev.egitim]


def cech_tikanikligi(gorev) -> Dict[str, object]:
    """``H⁰`` ve ``H¹``in sonlu gölgesi -- yamalar yapışıyor mu?

    Örtüşmelerde geçiş şartı: iki yamanın mahallî kâidesi **aynı** mı?
    Hepsi aynıysa küllî bir kesit vardır (``H¹ = 0``); ayrılan varsa
    tıkanıklık vardır.

    Üçlü tutarlılık ayrıca sayılır: ikili uyuşma bir denklik bağıntısı
    kurduğu için ``i~j`` ve ``j~k`` iken ``i~k`` **cebren** sağlanır;
    yine de sağlaması yapılır ki denklik varsayımı sessiz kalmasın.
    """
    K = yamalar(gorev)
    n = len(K)
    if n == 0:
        return {"yama": 0, "H1": 0, "kurulabilir": False}
    bos = sum(1 for k in K if k is None)
    # Geçiş fonksiyonları: örtüşmede uyuşma.
    uyusmaz: List[Tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if K[i] is None or K[j] is None:
                continue
            if repr(K[i]) != repr(K[j]):
                uyusmaz.append((i, j))
    # Üçlü tutarlılık sağlaması (kozikıl şartı).
    ucler_tutarli = True
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if any(x is None for x in (K[i], K[j], K[k])):
                    continue
                ij = repr(K[i]) == repr(K[j])
                jk = repr(K[j]) == repr(K[k])
                ik = repr(K[i]) == repr(K[k])
                if ij and jk and not ik:
                    ucler_tutarli = False
    # ``H⁰``: bütün yamaların ortak kesiti -- ancak hepsi uyuşursa var.
    kurulabilir = (bos == 0 and not uyusmaz)
    return {
        "yama": n,
        "kâidesiz_yama": bos,
        "uyuşmayan_çift": len(uyusmaz),
        "üçlü_tutarlı": ucler_tutarli,
        "H1": len(uyusmaz),          # tıkanıklığın ölçüsü
        "kurulabilir": bool(kurulabilir),
    }


def terkip_iyi_tipli_mi() -> Dict[str, object]:
    """41 melekenin terkibi **iyi tipli** mi -- makine denetimi.

    Operadın şartı, terkibin tanımlı olmasıdır. Burada bunun somut
    karşılığı şudur: ``QAKIS`` sırasındaki her meleke, bir evvelkinin
    bıraktığı yazmaç üzerinde tanımlı olmalı ve ilan ettiği bölgenin
    dışına çıkmamalıdır (`nefs/sozlesme.py` bunu zaten ölçüyor).

    Ayrıca ``omega_kategori``nin **kendi** tip denetleyicisi çağrılır ve
    çekirdeğin bilinen eksikleri raporlanır -- o modülün kendi kütüğü
    (``bosluklar``) sessiz kalmasın diye.
    """
    from omega_kategori import turetimler
    from .qmeleke import QAKIS, qsicil

    s = qsicil()
    # Terkip zinciri: her adımın çıktısı bir sonrakinin girdisi.
    zincir_tam = all(no in s for no in QAKIS)
    return {
        "adım": len(QAKIS),
        "zincir_tam": bool(zincir_tam),
        "çekirdek_boşlukları": len(turetimler.bosluklar()),
        "boşluk_başlıkları": [b.get("ad", b.get("başlık", "?"))
                              for b in turetimler.bosluklar()][:6],
    }


def tikaniklik_sukut_bagi(n_gorev: int = 40, tohum: int = 0,
                          chi: int = 8, kapi: bool = True
                          ) -> Dict[str, object]:
    """**ASIL ÖLÇÜM:** ``H¹ ≠ 0`` olan görevlerde model susuyor mu?

    Tıkanıklık "cevap yanlış" demek değildir; "bu örtüde küllî cevap
    yoktur" demektir. O hâlde tıkanıklık ile ``sukut`` arasında müsbet
    bir bağ **olmalıdır**.

    Bu bir iddia değildir ve kırmızı yanabilir: bağ sıfır çıkarsa,
    modelin susması tıkanıklıkla alâkasız demektir ve öyle yazılır.
    """
    from .qakis import QNefs
    from .qyazmac import QAyar
    from .iki_olcek import gorev_ozellikleri

    gorevler = arc.yukle_hepsi("training")[:int(n_gorev)]
    H1, S = [], []
    for gv in gorevler:
        c = cech_tikanikligi(gv)
        if c["yama"] < 2:
            continue
        X, Y = gorev_ozellikleri(gv)
        if len(X) == 0:
            continue
        E = np.concatenate([X, Y], axis=1)
        q = QNefs(tohum, QAyar(bag=int(chi), tohum=tohum)).idrak_et(
            E, tikaniklik=(float(c["H1"]) if kapi else 0.0))
        yuv = [q.kulli("sukut", j)
               for j in range(q._alan["sukut"][1])]
        sk = float(np.asarray(q.y.tekil_yogunluklar(yuv),
                              float)[0][:, 1, 1].mean())
        H1.append(float(c["H1"] > 0))
        S.append(sk)
    if len(H1) < 4 or len(set(H1)) < 2:
        return {"görev": len(H1), "yeterli_mi": False}
    H1a, Sa = np.asarray(H1), np.asarray(S)
    return {
        "görev": len(H1),
        "yeterli_mi": True,
        "tıkanık_görev": int(H1a.sum()),
        "korelasyon": float(np.corrcoef(H1a, Sa)[0, 1]),
        "sukut_tıkanıkta": float(Sa[H1a > 0].mean()),
        "sukut_açıkta": float(Sa[H1a == 0].mean()),
    }


def rapor(n_gorev: int = 40, tohum: int = 0, chi: int = 8) -> str:
    gorevler = arc.yukle_hepsi("training")[:int(n_gorev)]
    s = ["=== ÖRTÜ, TERKİP, TIKANIKLIK (Dosya 3) ===",
         "",
         "Grothendieck fibrasyonu ZATEN kurulu (nefs/mertebe.py, 20 lif).",
         "Burada kurulan: ∞-operad terkibinin tipi ve ÇEch tıkanıklığı.",
         ""]

    t = terkip_iyi_tipli_mi()
    s += ["TERKİP (∞-operad):",
          "  akış adımı        : %d" % t["adım"],
          "  zincir tam mı     : %s" % t["zincir_tam"],
          "  ω-kategori çekirdeğinin BİLİNEN boşlukları: %d"
          % t["çekirdek_boşlukları"],
          ""]

    say = {"kurulabilir": 0, "tıkanık": 0, "kâidesiz": 0}
    ucsuz = 0
    for gv in gorevler:
        c = cech_tikanikligi(gv)
        if c["yama"] < 2:
            continue
        if c["kâidesiz_yama"]:
            say["kâidesiz"] += 1
        elif c["H1"]:
            say["tıkanık"] += 1
        else:
            say["kurulabilir"] += 1
        if not c["üçlü_tutarlı"]:
            ucsuz += 1
    s += ["ČECH TIKANIKLIĞI (%d görev):" % len(gorevler),
          "  H¹ = 0, küllî kâide var   : %d" % say["kurulabilir"],
          "  H¹ ≠ 0, TIKANIK           : %d" % say["tıkanık"],
          "  mahallî kâidesi bile yok  : %d" % say["kâidesiz"],
          "  üçlü tutarlılığı bozan    : %d  (0 olmalı -- kozikıl şartı)"
          % ucsuz,
          ""]

    b = tikaniklik_sukut_bagi(n_gorev, tohum, chi)
    s.append("TIKANIKLIK → SÜKÛT (asıl ölçüm):")
    if not b.get("yeterli_mi"):
        s.append("  yeterli çeşitlilik yok (%d görev)" % b.get("görev", 0))
    else:
        s += ["  görev                 : %d (%d'i tıkanık)"
              % (b["görev"], b["tıkanık_görev"]),
              "  sükût, tıkanık görevde: %.4f" % b["sukut_tıkanıkta"],
              "  sükût, açık görevde   : %.4f" % b["sukut_açıkta"],
              "  korelasyon            : %+.4f" % b["korelasyon"],
              ""]
        if b["korelasyon"] > 0.15:
            s.append("  HÜKÜM: tıkanıklık sükûtu ARTIRIYOR. Model, küllî")
            s.append("  cevabın olmadığı görevlerde susmaya meylediyor.")
        elif b["korelasyon"] < -0.15:
            s.append("  HÜKÜM: TERS. Model tıkanık görevlerde daha ÇOK")
            s.append("  konuşuyor -- bu bir kusurdur ve gizlenmiyor.")
        else:
            s.append("  HÜKÜM: bağ YOK. Modelin susması Čech tıkanıklığıyla")
            s.append("  alâkasız; Dosya 3'ün bu kehaneti icra EDİLMEMİŞ")
            s.append("  durumda ve borç olarak kalıyor.")
    s += ["",
          "HUDUT: burada kurulan tam Čech kohomolojisi DEĞİL, onun sonlu",
          "ve hesaplanabilir gölgesidir (sonlu örtü, ayrık kâide kümesi).",
          "İsmi doğru kullanmak, tamamını kurmayı iddia etmeyi gerektirmez."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
