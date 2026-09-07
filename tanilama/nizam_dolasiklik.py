from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from nefs import melekeler as qmeleke
from nefs.melekeler import QNefs
from nefs.zihin_durumu import QAyar

__all__ = ["nizam_olcumu", "rapor"]


def _sapma(P: np.ndarray) -> float:
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
        nefs = QNefs(tohum, QAyar(tohum=tohum))
        q = nefs.idrak_et(E)
        kesit = q.taksimat.kesitler().get("veri|hukum", q.n // 2)
        e = q.y.dolasiklik_entropisi(kesit=int(kesit), pencere=int(kesit))
        P = _beyan(q)

        beyanlar = [P]
        for t in range(1, girdi_sayisi):
            r2 = np.random.default_rng(tohum + 1000 * t)
            q2 = QNefs(tohum, QAyar(tohum=tohum)).idrak_et(
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


if __name__ == "__main__":
    print(rapor())
