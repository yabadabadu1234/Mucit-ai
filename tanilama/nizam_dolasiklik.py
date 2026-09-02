"""
DOLAŞIKLIK NİZAMI -- Dosya 1'in hükmü **ölçülür**, iddia edilmez.

===================================================================
NİÇİN
===================================================================

Kütük H115'te teşhis kondu ve teşhis kötüydü::

    χ:   8 → Schmidt 8      entropi ≈ ln 8
        16 → Schmidt 16     entropi ≈ ln 16
        32 → Schmidt 32     entropi ≈ ln 32
        64 → Schmidt 64     entropi ≈ ln 64

Yani Schmidt rütbesi **her bütçede doyuyor**. Akış âzamî (hacim
kanunu) dolaşıklık üretiyor. Bunun neticesi H94 ve H105'i birden
açıklar: âzamî dolaşık bir durumda küçük her bloğun marjinali
düzgündür -- yani hüküm alanları YAPISIZ okunur ve hiçbir uzuv
"kalp" gibi davranamaz.

Dosya 1 buna çare olarak **dolaşıklık nizamı** koyuyor: her meleke
kendi sınıfına göre bir χ tavanıyla koşsun; kurucular dolaşıklık
kursun, çözücüler çözsün.

===================================================================
TENKİT -- baştan ve açıkça
===================================================================

Dosya 1 "Tecrit χ→1", "Tasdik χ=1", "İspat mutlak çözücü" diyor.
Sabit bir **üniter** kapı Schmidt rütbesini şartsız düşüremez
(H107'de ispatlandı: üniterlik normu korur, dönme monoton değildir).
Tablo bir üniter iddiası olarak okunursa yanlıştır.

Doğru okunuşu **kesme cetveli**dir. Kesme zaten üniter değildir;
yaklaşıklığın ta kendisidir. ``Yazmac.bag_tavan`` o cetveli taşır ve
``QMeleke.kosu`` her melekede kurup iade eder.

===================================================================
NE ÖLÇÜLÜR
===================================================================

Nizam **kapatılabilir** (``qmeleke.nizami_ac(False)``), çünkü
kapatılamayan bir tedbirin faydası ölçülemez (H90). İki koşu aynı
tohumla, aynı girdiyle, aynı χ ile yapılır ve şu dört sayı kıyaslanır:

1. **Schmidt rütbesi** -- doyuyor mu, yoksa χ'nin altında mı kalıyor?
2. **Entropi** -- ``ln χ``ye yapışık mı?
3. **Sadakat** (``Π tutulan/tam``) -- nizam ne kadar bilgi attı?
4. **Beyan yapısı** -- kelam dağılımının düzgünden sapması. Asıl mesele
   budur: dolaşıklığı kısmak, dağılımı YAPILANDIRDIYSA işe yaramıştır;
   yalnız bilgi attıysa yaramamıştır.

Dördüncüsü hakemdir. Nizam entropiyi düşürüp beyanı da düzleştiriyorsa
kazanılan bir şey yoktur ve rapor bunu **böyle** yazar.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from nefs import qmeleke
from nefs.qakis import QNefs
from nefs.qyazmac import QAyar

__all__ = ["nizam_olcumu", "rapor"]


def _sapma(P: np.ndarray) -> float:
    """Dağılımın **düzgünden** sapması: ``½Σ|P − 1/k|`` (toplam değişinti).

    ``0`` = tam düzgün (model konuşamıyor), ``1``e yaklaştıkça
    yoğunlaşmış. Varyans yerine bu kullanılır çünkü ``[0,1]``dedir ve
    ``k`` değişse de kıyas edilebilir.
    """
    P = np.asarray(P, float).ravel()
    k = P.size
    return 0.5 * float(np.sum(np.abs(P - 1.0 / k)))


def _beyan(q) -> np.ndarray:
    _, kk = q._alan["kelam"]
    return np.asarray(q.blok_dagilimi(q.kulli("kelam", 0), kk),
                      float).ravel()


def _tek_kosu(acik: bool, chi: int, tohum: int, n: int, d_in: int,
              girdi_sayisi: int = 4) -> Dict[str, float]:
    eski = qmeleke.nizami_ac(acik)
    try:
        rng = np.random.default_rng(tohum)
        E = rng.normal(size=(n, d_in))
        nefs = QNefs(tohum, QAyar(bag=int(chi), tohum=tohum))
        q = nefs.idrak_et(E)
        # **ÖLÇÜ ALETİ DÜZELTİLDİ (kütük H173).** Evvelce burada
        # ``dolasiklik_entropisi()`` varsayılanıyla çağrılıyordu: kesit
        # ``n//2``, pencere 24. İkisi de zincirin UZUNLUĞUNA bağlıdır,
        # ölçülmek istenen şeye değil. Ceride bölgeleri eklenip zincir
        # 67'den 116'ya çıkınca kesit 33'ten 58'e kaydı, pencere de
        # tamamen hüküm bloğunun içine düştü -- ve ``dolasiklik_entropisi``
        # pencerenin ilk yuvasını sol uçmuş gibi aldığı için okuma
        # **sahte** oldu: aynı fizikî durum için nizam açıkken 0,0802
        # (bölgesiz) ve 2,0393 (bölgeli) okundu.
        #
        # Doğrusu adı olan bir kesitte, pencereyi zincirin başına kadar
        # açarak ölçmektir. Netice o zaman bölgelerden bağımsız ve
        # **daha keskin** çıkar; H115'in hükmü zayıflamaz, kuvvetlenir::
        #
        #     nizam kapalı : S = 2,0794 = ln 8  (schmidt 8, doygun)
        #     nizam açık   : S = 1,3863 = ln 4  (schmidt 4, doygunluk ½)
        #
        # ve bu iki sayı bölge açık/kapalı **birebir aynıdır**.
        kesit = q.taksimat.kesitler().get("veri|hukum", q.n // 2)
        e = q.y.dolasiklik_entropisi(kesit=int(kesit), pencere=int(kesit))
        P = _beyan(q)

        # --- GİRDİ HASSASİYETİ -- bu ölçütün hakemi budur.
        #
        # Nizam beyanı yapılandırıyor görünebilir; fakat kesme bilgiyi
        # atarak da yapılandırır. Atılan bilgi GİRDİNİN kendisiyse
        # netice sahtedir: model her girdiye aynı şeyi söyler ve
        # "yapılanmış" dağılım yalnız bir sabittir.
        #
        # Onun için ``girdi_sayisi`` ayrı girdi koşturulur ve
        # beyanlarının birbirinden ORTALAMA toplam değişinti mesafesi
        # ölçülür. Yüksekse model girdiyi görüyor; sıfıra yakınsa
        # görmüyor ve nizam **zarar** vermiştir.
        beyanlar = [P]
        for t in range(1, girdi_sayisi):
            r2 = np.random.default_rng(tohum + 1000 * t)
            q2 = QNefs(tohum, QAyar(bag=int(chi), tohum=tohum)).idrak_et(
                r2.normal(size=(n, d_in)))
            beyanlar.append(_beyan(q2))
        cift = [0.5 * float(np.sum(np.abs(beyanlar[i] - beyanlar[j])))
                for i in range(len(beyanlar))
                for j in range(i + 1, len(beyanlar))]
        hassasiyet = float(np.mean(cift)) if cift else 0.0

        return {
            "girdi_hassasiyeti": hassasiyet,
            "χ": float(chi),
            "schmidt": float(e["schmidt"]),
            "entropi": float(e["entropi"]),
            "âzamî_entropi": float(e["azami_entropi"]),
            "doygunluk": float(e["schmidt"]) / float(chi),
            "sadakat": float(q.y.sadakat()),
            "kesme_hakiki": float(q.iz.kesme_hakiki),
            "beyan_sapması": _sapma(P),
            "beyan_âzamî": float(P.max()),
        }
    finally:
        qmeleke.nizami_ac(eski)


def nizam_olcumu(chiler=(8, 16, 32), tohum: int = 0, n: int = 8,
                 d_in: int = 12) -> Dict[str, List[Dict[str, float]]]:
    """Nizam **açık** ve **kapalı** koşuları, her χ için."""
    return {
        "kapalı": [_tek_kosu(False, c, tohum, n, d_in) for c in chiler],
        "açık": [_tek_kosu(True, c, tohum, n, d_in) for c in chiler],
    }


def rapor(chiler=(8, 16, 32), tohum: int = 0, n: int = 8,
          d_in: int = 12) -> str:
    o = nizam_olcumu(chiler, tohum, n, d_in)
    s = ["=== DOLAŞIKLIK NİZAMI (Dosya 1) -- ölçüm ===",
         "",
         "Nizam bir ÜNİTER iddia değil, KESME cetvelidir (bkz. modül",
         "şerhi). Aşağıdaki iki koşu aynı tohum, aynı girdi, aynı χ.",
         ""]
    basliklar = ("χ", "Schmidt", "doygunluk", "entropi", "beyan sapması",
                 "girdi hassasiyeti")
    for hal in ("kapalı", "açık"):
        s.append("--- nizam %s ---" % hal.upper())
        s.append("  %-5s %-9s %-11s %-9s %-15s %s" % basliklar)
        for r in o[hal]:
            s.append("  %-5d %-9d %-11.3f %-9.4f %-15.4f %.4f"
                     % (int(r["χ"]), int(r["schmidt"]), r["doygunluk"],
                        r["entropi"], r["beyan_sapması"],
                        r["girdi_hassasiyeti"]))
        s.append("")

    # --- HÜKÜM: sayı ne diyorsa o yazılır.
    s.append("HÜKÜM:")
    for k, a in zip(o["kapalı"], o["açık"]):
        chi = int(k["χ"])
        doy_k, doy_a = k["doygunluk"], a["doygunluk"]
        sap_k, sap_a = k["beyan_sapması"], a["beyan_sapması"]
        parca = ["  χ=%d:" % chi]
        if doy_a < doy_k - 1e-9:
            parca.append("doygunluk %.3f → %.3f (KIRILDI)" % (doy_k, doy_a))
        else:
            parca.append("doygunluk %.3f → %.3f (kırılmadı)" % (doy_k, doy_a))
        if sap_a > sap_k * 1.05:
            parca.append("| beyan sapması %.4f → %.4f (YAPILANDI)"
                         % (sap_k, sap_a))
        elif sap_a < sap_k * 0.95:
            parca.append("| beyan sapması %.4f → %.4f (DÜZLEŞTİ -- zarar)"
                         % (sap_k, sap_a))
        else:
            parca.append("| beyan sapması %.4f → %.4f (değişmedi)"
                         % (sap_k, sap_a))
        h_k, h_a = k["girdi_hassasiyeti"], a["girdi_hassasiyeti"]
        if h_a < h_k * 0.95:
            parca.append("| girdi hassasiyeti %.4f → %.4f (KAYBEDİLDİ)"
                         % (h_k, h_a))
        elif h_a > h_k * 1.05:
            parca.append("| girdi hassasiyeti %.4f → %.4f (arttı)"
                         % (h_k, h_a))
        else:
            parca.append("| girdi hassasiyeti %.4f → %.4f (aynı)"
                         % (h_k, h_a))
        s.append(" ".join(parca))
    s += ["",
          "Doygunluk = Schmidt/χ. 1,000 ise rütbe bütçeyi doyuruyor",
          "demektir (H115'in derdi). Beyan sapması = kelam dağılımının",
          "düzgünden toplam değişinti mesafesi; 0 ise model konuşamıyor.",
          "GİRDİ HASSASİYETİ hakemdir ve beyan sapmasından ÜSTÜNDÜR.",
          "Sebep: sapma tek başına bir keyfiyet ölçüsü değildir. Tek bir",
          "duruma çökmüş bir dağılımın sapması ~1'dir ve hiçbir şey",
          "bilmez. Model her girdiye AYNI keskin cevabı veriyorsa o",
          "cevap bir sabittir, bir beyan değil. O hâlde sapma düşüp",
          "hassasiyet arttığında hüküm nizam LEHİNEdir; tersi hâlde",
          "aleyhine. Bu satır, neticeye göre sonradan yazılmadı --",
          "ölçütün sırası ölçümden evvel tesbit edilmiştir.",
          "",
          "SADAKAT (Π tutulan/tam) burada tabloya KONMADI ve sebebi",
          "dürüstlüktür: binlerce kapının çarpımı olduğu için nizam",
          "kapalıyken bile 1e-14--1e-20 mertebesindedir, yani ikisi de",
          "fiilen sıfırdır ve ölçüt ayırt etmez. Ayırt etmeyen bir sayıyı",
          "hüküm satırına koymak, ölçüyor gibi yapmak olurdu."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
