"""
SAĞÎR ve KEBÎR -- iki ölçekli mimari (Dosya 5).

===================================================================
MESELE: ARC'de tek ölçek NİÇİN yetmez
===================================================================

Bir ARC görevinde **iki ilâ dört** gösterim çifti vardır. Bu iki şeyi
aynı anda imkânsız kılar:

* **Yalnız kebîr (küllî) ölçek** -- bütün görevlerde paylaşılan 41
  melekenin açıları. Genelleşir, fakat üç örneklik bir göreve
  **ihtisas edemez**: parametreler bütün görevlerin ortalamasıdır.
* **Yalnız sağîr (cüz'î) ölçek** -- yalnız o görevin üç çiftinden
  öğrenmek. İhtisas eder, fakat üç noktadan genelleme çıkmaz.

Dosya 5'in teklifi ikisini **beraber** tutmaktır ve bu mimaride
karşılığı tamdır:

    KEBÎR : ``QParametre`` -- bütün görevlerde ortak, yavaş, üniter.
    SAĞÎR : görev başına, **kapalı formda**, o görevin kendi
            çiftlerinden (`ogrenme/rkhs.py`).

===================================================================
NİÇİN KAPALI FORM -- ve niçin H31 çiğnenmiyor
===================================================================

Kütük H3: *"öğrenme kapalı formdadır, gradyan yok."* `ogrenme/rkhs.py`
tam olarak onu verir: temsil teoremi gereği en iyi ``f``, veri
noktalarındaki çekirdeklerin gerdiği sonlu altuzaydadır ve

    ``(K + λI) α = y``

**çözülür** (ters alınmaz -- o modülün kendi ısrarı). Üç noktalık bir
görevde bu, ``3×3`` bir sistemdir: mikrosaniye.

**H31 (hiçbir meleke okumaz) burada çiğnenmez** çünkü sağîr ölçek
akışın **içinde** değildir. Akış (``idrak_et``) üniterdir ve hiçbir
şey okumaz; sağîr uydurma **eğitim/çözüm** hattındadır, yani dalganın
dışında. Öğrenmenin okumasında bir beis yoktur; yasak olan, melekenin
kendi girdisine bakıp karar vermesidir.

===================================================================
İKİ ÖLÇEK BİRBİRİNİN AYNI MI? -- ölçülür
===================================================================

İki ölçekli bir mimarinin **bedeli** vardır; o hâlde kazancı
ispatlanmalıdır. Sual şudur: *sağîr ölçek, kebîrin zaten bildiğini mi
söylüyor?*

Bunun ölçüsü Grassmann geometrisidir (`ogrenme/grassmann.py`): iki
ölçeğin ürettiği öznitelik alt uzayları arasındaki **asal açılar**.

* Bütün açılar ``≈ 0`` → alt uzaylar örtüşüyor; sağîr **fazladan
  hiçbir şey** taşımıyor ve ikinci ölçek gereksizdir.
* Açılar büyük → sağîr, kebîrin göremediği bir yön taşıyor; iki ölçek
  hakikaten ikidir.

Bu, "iki ölçek iyidir" diye bir iddia DEĞİLDİR; iddiayı kırmızı
yakabilen bir ölçüttür (kütük H90).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from idrak import arc
from ogrenme.grassmann import asal_acilar, dik_taban, grassmann_mesafesi
from ogrenme.rkhs import RKHS, gauss_cekirdegi, medyan_genislik, psd_mi

__all__ = ["gorev_ozellikleri", "sagir_uydur", "kebir_ozellik",
           "olcek_acilari", "rapor"]


def _izgara_tarifi(g: np.ndarray) -> np.ndarray:
    """Bir ızgaranın **sabit uzunlukta** tarifi -- 14 sayı.

    ARC ızgaraları farklı ölçüdedir; RKHS sabit boyutlu bir vektör
    ister. Tarif kasten **kaba** tutulur (şekil + renk histogramı):
    maksat çözmek değil, iki ölçeğin **aynı** öznitelik uzayında
    kıyaslanabilmesidir. İnce tarif işi `idrak/cozucu.py`nindir.
    """
    g = np.asarray(g, int)
    h, w = g.shape
    hist = np.bincount(g.ravel(), minlength=10)[:10] / max(g.size, 1)
    return np.concatenate([[h / 30.0, w / 30.0, (g != 0).mean(),
                            float(g.max()) / 9.0], hist])


def gorev_ozellikleri(gorev) -> Tuple[np.ndarray, np.ndarray]:
    """Bir görevin gösterim çiftlerinden ``(X, Y)`` öznitelikleri."""
    X, Y = [], []
    for a, b in gorev.egitim:
        X.append(_izgara_tarifi(a))
        Y.append(_izgara_tarifi(b))
    if not X:
        return np.zeros((0, 14)), np.zeros((0, 14))
    return np.asarray(X, float), np.asarray(Y, float)


def sagir_uydur(gorev, lam: float = 1e-6) -> Dict[str, object]:
    """SAĞÎR ölçek: **yalnız bu görevin** çiftlerinden, kapalı formda.

    Çekirdek Gauss'tur ve genişliği medyan sezgisiyle konur (elle
    ayarlanmış bir sabit değil, verinin kendi ölçeği). PSD'lik
    **denetlenir**: `ogrenme/rkhs.py`nin ısrarı budur ve burada da
    raporlanır -- PSD olmayan bir çekirdekte temsil teoremi geçersizdir.
    """
    X, Y = gorev_ozellikleri(gorev)
    if len(X) < 2:
        return {"kuruldu": False, "sebep": "iki çiftten az"}
    gen = medyan_genislik(X)
    K = gauss_cekirdegi(1.0 / max(2.0 * gen ** 2, 1e-9))
    # ``psd_mi`` çekirdeği RASTGELE noktalarda sınar (nokta kümesi
    # almaz); boyut olarak özniteliğin boyutu verilir.
    psd = bool(psd_mi(K, boyut=int(X.shape[1]))["psd_görünüyor"])
    # **Tek** kapalı form çözüm: ``uydur`` çok sütunlu hedefi olduğu
    # gibi alır ve ``(K+λI)`` bir kere Cholesky'lenir -- 14 ayrı sistem
    # kurmak aynı dizeyi 14 kere ayrıştırmak olurdu.
    m = RKHS(K, lam=lam)
    m.uydur(X, Y)
    artik = float(np.abs(np.asarray(m(X), float) - Y).max())
    # **ÇAKIŞAN TARİF -- ölçülen hudut, gizlenmiyor.**
    # 14 sayılık tarif kabadır; bazı görevlerde iki AYRI çiftin tarifi
    # birbirinin aynı çıkar. O zaman Gram dizeyinin iki satırı eşitlenir,
    # ``K+λI``nın koşul sayısı ``1/λ`` mertebesine fırlar (ölçüldü: 5e6)
    # ve kapalı form artık **enterpolasyon yapamaz** -- düzenlileştirme
    # iki çakışan noktanın ortalamasına düşer.
    #
    # Bu, `ogrenme/rkhs.py`nin kusuru DEĞİLDİR; o modül zaten koşul
    # sayısını raporlamakta ısrar ediyor ve haklı çıkıyor. Kusur benim
    # kaba tarifimdedir ve bir borçtur: ince tarif işi
    # `idrak/cozucu.py`nindir.
    d = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2)
    n = len(X)
    cakisan = int((d[np.triu_indices(n, 1)] < 1e-9).sum()) if n > 1 else 0
    return {"kuruldu": True, "psd": psd, "genişlik": float(gen),
            "model": m, "X": X, "Y": Y, "koşul": float(m.kosul),
            "çakışan_çift": cakisan, "azamî_artık": artik}


def kebir_ozellik(gorev, tohum: int = 0, chi: int = 8) -> np.ndarray:
    """KEBÎR ölçek: ana akışın (41 meleke) bu göreve dair beyanı.

    Görevin gösterim çiftleri satır olarak kodlanır, akış koşar ve
    ``kelam`` alanından okunan dağılım öznitelik sayılır. Bu, **bütün
    görevlerde ortak** parametrelerle üretilir -- ihtisas yoktur, ve
    ölçülecek olan da odur.
    """
    from .melekeler import QNefs
    from .zihin_durumu import QAyar

    X, Y = gorev_ozellikleri(gorev)
    if len(X) == 0:
        return np.zeros(16)
    E = np.concatenate([X, Y], axis=1)              # (çift, 28)
    q = QNefs(tohum, QAyar(bag=int(chi), tohum=tohum)).idrak_et(E)
    return np.asarray(q.beyan(16), float)


def olcek_acilari(gorevler: Sequence, tohum: int = 0, chi: int = 8,
                  k: int = 3) -> Dict[str, object]:
    """İki ölçek **aynı** alt uzayı mı geriyor? -- Grassmann asal açıları.

    Her görev için iki öznitelik vektörü toplanır (sağîr tahmini ile
    kebîr beyanı), ikisinden birer alt uzay kurulur ve aralarındaki
    asal açılar ölçülür.

    Açılar sıfıra yakınsa **ikinci ölçek gereksizdir** ve bu netice
    dürüstçe yazılır; büyükse iki ölçek hakikaten ikidir.
    """
    S, K = [], []
    kurulan = 0
    for gv in gorevler:
        r = sagir_uydur(gv)
        if not r.get("kuruldu"):
            continue
        X = r["X"]
        # Sağîr ölçeğin tahmini: kendi kapalı formundan, görev başına
        # tek vektör (çiftler üzerinden ortalama).
        tah = np.asarray(r["model"](X), float).mean(axis=0)
        S.append(tah)
        K.append(kebir_ozellik(gv, tohum, chi)[:len(tah)])
        kurulan += 1
    if kurulan < k + 1:
        return {"görev": kurulan, "yeterli_mi": False}
    S = np.asarray(S, float)
    Kb = np.asarray(K, float)
    # Ortak boy: her iki matris de (görev × boyut)
    d = min(S.shape[1], Kb.shape[1])
    S, Kb = S[:, :d], Kb[:, :d]
    kk = min(k, d, S.shape[0])
    Ys = dik_taban(S.T[:, :kk] if S.T.shape[1] >= kk else S.T)
    Yk = dik_taban(Kb.T[:, :kk] if Kb.T.shape[1] >= kk else Kb.T)
    kk = min(Ys.shape[1], Yk.shape[1])
    Ys, Yk = Ys[:, :kk], Yk[:, :kk]
    aci = np.asarray(asal_acilar(Ys, Yk), float)
    return {
        "görev": kurulan,
        "yeterli_mi": True,
        "asal_açılar": aci,
        "azamî_açı": float(aci.max()) if aci.size else 0.0,
        "grassmann_mesafesi": float(grassmann_mesafesi(Ys, Yk)),
        "boyut": int(kk),
    }


def rapor(n_gorev: int = 24, tohum: int = 0, chi: int = 8) -> str:
    gorevler = arc.yukle_hepsi("training")[:int(n_gorev)]
    s = ["=== SAĞÎR ve KEBÎR -- iki ölçekli mimari (Dosya 5) ===",
         "",
         "KEBÎR: 41 melekenin bütün görevlerde ORTAK açıları.",
         "SAĞÎR: görev başına, o görevin kendi çiftlerinden, KAPALI",
         "       formda (H3: gradyan yok) -- `ogrenme/rkhs.py`.",
         ""]

    kuruldu = psd_ok = 0
    artiklar = []
    for gv in gorevler:
        r = sagir_uydur(gv)
        if r.get("kuruldu"):
            kuruldu += 1
            psd_ok += int(bool(r["psd"]))
            artiklar.append(r["azamî_artık"])
    s += ["SAĞÎR ÖLÇEK (%d görev):" % len(gorevler),
          "  kurulan            : %d" % kuruldu,
          "  çekirdeği PSD olan : %d  (PSD değilse temsil teoremi geçersiz)"
          % psd_ok,
          "  âzamî uydurma artığı (ortanca): %.2e"
          % (float(np.median(artiklar)) if artiklar else float("nan")),
          ""]

    o = olcek_acilari(gorevler, tohum, chi)
    s.append("İKİ ÖLÇEK AYNI ŞEYİ Mİ SÖYLÜYOR? (Grassmann asal açıları)")
    if not o.get("yeterli_mi"):
        s.append("  yeterli görev yok (%d)" % o.get("görev", 0))
    else:
        s += ["  alt uzay boyutu    : %d" % o["boyut"],
              "  asal açılar (rad)  : %s"
              % np.array2string(o["asal_açılar"], precision=4),
              "  âzamî açı          : %.4f rad  (π/2 = 1,5708 tam dik)"
              % o["azamî_açı"],
              "  Grassmann mesafesi : %.4f" % o["grassmann_mesafesi"],
              ""]
        if o["azamî_açı"] < 0.1:
            s.append("  HÜKÜM: açılar sıfıra yakın -- sağîr ölçek kebîrin")
            s.append("  zaten bildiğini söylüyor. İKİNCİ ÖLÇEK GEREKSİZ.")
        else:
            s.append("  HÜKÜM: açılar büyük -- sağîr, kebîrin göremediği bir")
            s.append("  yön taşıyor. İki ölçek hakikaten ikidir.")
    s += ["",
          "Bu bir iddia değil ölçüttür ve kırmızı yanabilir (H90):",
          "açılar sıfıra yakın çıksaydı, iki ölçekli mimarinin bu",
          "hâliyle bedeli var faydası yok demektir ve öyle yazılırdı."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
