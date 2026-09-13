from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from matematik.mizan import ardisiklik_kaidesi, tam_istikra_mi
from matematik.mizan import MERTEBELER, mertebe_adi, yakin_gazali

__all__ = ["MAKAM_MERTEBE", "GRAY_SIRA", "ESKI_SIRA", "komsuluk_denetimi",
           "eksik_mertebeler", "istikra_mertebesi", "yakin_yuzlestirmesi",
           "rapor"]


def istikra_mertebesi(n_gorev: int = 200) -> Dict[str, object]:
    from .musahede import gorevleri_getir
    g = gorevleri_getir("training")[:int(n_gorev)]
    k = np.array([len(x.egitim) for x in g], dtype=int)
    y = np.array([ardisiklik_kaidesi(int(v), int(v)) for v in k], float)
    adlar = sorted({mertebe_adi(float(v)) for v in y})
    return {"görev": int(k.size), "çift_ortalama": float(k.mean()),
            "yakîn_ortalama": float(y.mean()),
            "mertebe_ortalama": mertebe_adi(float(y.mean())),
            "düşülen_mertebeler": adlar,
            "tam_istikrâ_olan": int(sum(tam_istikra_mi(int(v), int(v))
                                        for v in k))}

MAKAM_MERTEBE: Dict[str, float] = {
    "Vehim": 0.0, "Şek": 0.25, "Zan": 0.5,
    "Zann-ı gālib": 0.75, "Yakîn": 1.0,
}

ESKI_SIRA: Tuple[str, ...] = ("Şek", "Zan", "Yakîn", "Vehim")

GRAY_SIRA: Tuple[str, ...] = ("Vehim", "Şek", "Yakîn", "Zan")


def _kod(sira: Sequence[str], bit: int) -> Dict[str, Tuple[int, ...]]:
    return {ad: tuple((i >> (bit - 1 - b)) & 1 for b in range(bit))
            for i, ad in enumerate(sira)}


def komsuluk_denetimi(sira: Optional[Sequence[str]] = None,
                      bit: Optional[int] = None) -> Dict[str, object]:
    from .zihin_durumu import (MAKAM_ADLARI, QAyar, makam_derecesi,
                          makam_kubit_manasi, makam_merdiveni,
                          makam_mertebeleri)

    if sira is None:
        kac = int(bit if bit is not None
                  else dict(QAyar().kulli_alanlar)["makam"])
        merd = makam_merdiveni(kac)
        adlar = list(makam_mertebeleri(kac))
        derece = list(makam_derecesi(kac))
        ust_kolu = sorted({adlar[k] for k in makam_kubit_manasi(kac)[0]})
        ad_kod = None
    else:
        adlar = list(sira)
        kac = int(bit if bit is not None
                  else max(1, (len(adlar) - 1).bit_length()))
        ad_kod = _kod(adlar, kac)
        duzen = sorted((a for a in adlar if a in MAKAM_MERTEBE),
                       key=lambda a: MAKAM_MERTEBE[a])
        adlar = duzen
        derece = [MAKAM_MERTEBE[a] for a in duzen]
        merd = [int("".join(str(x) for x in ad_kod[a]), 2) for a in duzen]
        ust_kolu = sorted(a for a in ad_kod if ad_kod[a][0] == 1)

    gecis = []
    for i in range(len(merd) - 1):
        h = bin(int(merd[i]) ^ int(merd[i + 1])).count("1")
        gecis.append((adlar[i], adlar[i + 1], h))
    ust_derece = [d for k, d in enumerate(derece)
                  if (sira is None and k in makam_kubit_manasi(kac)[0])
                  or (sira is not None and ad_kod[adlar[k]][0] == 1)]
    monoton = all(derece[i] <= derece[i + 1] + 1e-12
                  for i in range(len(derece) - 1))
    return {
        "geçişler": gecis,
        "kırık_geçiş": sum(1 for _, _, h in gecis if h != 1),
        "makam0_1_kolu": ust_kolu,
        "kol_tutarlı": bool(ust_derece) and bool(
            min(ust_derece) > min(derece) + 1e-12),
        "monoton": bool(monoton),
        "basamak": len(merd),
        "mertebe_sayısı": len(set(adlar)),
    }


def eksik_mertebeler(bit: Optional[int] = None) -> List[Tuple[float, str]]:
    from .zihin_durumu import QAyar, makam_mertebeleri

    kac = int(bit if bit is not None
              else dict(QAyar().kulli_alanlar)["makam"])
    var = {a.lower() for a in makam_mertebeleri(kac)}
    return [(d, ad) for d, ad in MERTEBELER if ad.lower() not in var]


def yakin_yuzlestirmesi(gorev, tohum: int = 0, chi: int = 8
                        ) -> Dict[str, float]:
    from .musahede import ortu
    from .musahede import iki_olcegin_acisi
    from .melekeler import QNefs
    from .zihin_durumu import MAKAM_ADLARI, QAyar

    c = ortu(gorev)
    Y = ortu(gorev, ne="yama")
    oncul = [1.0 if k is not None else 0.0 for k in Y]
    klasik = float(yakin_gazali(oncul, bool(c["kurulabilir"])))

    X, Yz = iki_olcegin_acisi(gorev, ne="öznitelik")
    E = np.concatenate([X, Yz], axis=1)
    q = QNefs(tohum, QAyar(tohum=tohum)).idrak_et(
        E, tikaniklik=float(c["H1"]))
    P = np.atleast_1d(np.asarray(q.makam_dagilimi(), float)).ravel()
    akis = float(P @ q.makam_derece_vektoru())
    return {"klasik_yakin": klasik, "akis_yakin": akis,
            "klasik_ad": mertebe_adi(klasik), "H1": float(c["H1"])}


def rapor(n_gorev: int = 30, tohum: int = 0) -> str:
    from .musahede import gorevleri_getir
    from .zihin_durumu import MAKAM_ADLARI

    s = ["=== MANTIK -- mizan/ ana akışa bağlanıyor ===", ""]
    s.append("MAKAM KODLAMASI (epistemik komşuluk tek kübitle geçilmeli):")
    for ad, sira, bit in (("ESKİ (kusurlu)", ESKI_SIRA, 2),
                          ("GRAY 2 kübit", GRAY_SIRA, 2),
                          ("YÜRÜRLÜKTEKİ", None, None)):
        d = komsuluk_denetimi(sira, bit)
        g = "  ".join("%s→%s:%d" % (a, b, h) for a, b, h in d["geçişler"])
        s.append("  %-15s kırık geçiş=%d  basamak=%d  monoton=%s"
                 % (ad, d["kırık_geçiş"], d["basamak"], d["monoton"]))
        s.append("  %-15s %s" % ("", g))
        s.append("  %-15s makam₀=1 kolu: %s  (tutarlı: %s)"
                 % ("", ", ".join(d["makam0_1_kolu"]), d["kol_tutarlı"]))
    s += ["",
          "EKSİK MERTEBE (klasik mîzânda var, akışın yazmacında yok):"]
    eks = eksik_mertebeler()
    for d, ad in eks:
        s.append("  %.2f  %s" % (d, ad))
    if not eks:
        s.append("  (yok -- H129'un borcu kapandı, makam 3 kübit)")
        s.append("  Kör değil: 2 kübitte hâlâ eksik çıkıyor → %s"
                 % ", ".join(a for _, a in eksik_mertebeler(2)))
    i = istikra_mertebesi()
    s += ["",
          "  VE BU EKSİK ZARARSIZ DEĞİL (kütük H129):",
          "    ARC %d görev, ortalama %.2f gösterim çifti"
          % (i["görev"], i["çift_ortalama"]),
          "    istikrâ yakîni ortalaması : %.4f  →  %s"
          % (i["yakîn_ortalama"], i["mertebe_ortalama"]),
          "    düşülen mertebeler        : %s" % ", ".join(i["düşülen_mertebeler"]),
          "    tam istikrâ olan görev    : %d  (eksik istikrâ yakîn vermez)"
          % i["tam_istikrâ_olan"],
          "    → ARC'nin HER görevi, makamın taşıyamadığı mertebeye",
          "      düşüyor. Akış ya Yakîn deyip fazla iddia ediyor, ya",
          "      Zan deyip eksik. Bütçe sınırı değil, YAPISAL yanlışlık."]

    s += ["", "YAKÎN YÜZLEŞTİRMESİ (klasik hesap ↔ akışın makamı):"]
    gorevler = gorevleri_getir("training")[:int(n_gorev)]
    K, A = [], []
    dusen: Dict[str, str] = {}
    for gv in gorevler:
        try:
            r = yakin_yuzlestirmesi(gv, tohum)
        except (NameError, AttributeError, ImportError) as e:
            raise AssertionError(
                "yakîn yüzleştirmesi eksik AD ile düştü (%s: %s) -- kod "
                "kusuru sessizce atlanamaz (ferman 5)" % (type(e).__name__, e))
        except Exception as e:
            dusen[getattr(gv, "ad", "?")] = "%s: %s" % (type(e).__name__,
                                                        str(e)[:60])
            continue
        K.append(r["klasik_yakin"])
        A.append(r["akis_yakin"])
    if dusen:
        s.append("  düşen görev %d/%d: %s"
                 % (len(dusen), len(gorevler),
                    ", ".join("%s(%s)" % (k, v)
                              for k, v in sorted(dusen.items())[:4])))
    if len(K) >= 4 and len(set(K)) > 1:
        kor = float(np.corrcoef(K, A)[0, 1])
        s += ["  görev              : %d" % len(K),
              "  klasik yakîn ort.  : %.4f" % float(np.mean(K)),
              "  akış yakîni ort.   : %.4f" % float(np.mean(A)),
              "  korelasyon         : %+.4f" % kor,
              ""]
        if kor > 0.15:
            s.append("  HÜKÜM: aynı yöne bakıyorlar.")
        elif kor < -0.15:
            s.append("  HÜKÜM: TERS yöne bakıyorlar -- kusurdur, gizlenmiyor.")
        else:
            s.append("  HÜKÜM: bağ yok. Akışın makamı klasik yakîn hesabıyla")
            s.append("  alâkasız; akış eğitilmemiştir ve bu borç yazılır.")
    else:
        s.append("  yeterli çeşitlilik yok (%d görev)" % len(K))
    return "\n".join(s)
