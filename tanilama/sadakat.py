from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from nefs.melekeler import QNefs
from nefs.qegitim import belirtecleri_kodla
from nefs.melekeler import QAKIS, qsicil
from nefs.zihin_durumu import QAyar, QYazmac
from nefs.zirh import vicdan

__all__ = ["sadakat_olcusu", "haritala", "rapor"]


def _blok_bitleri(kac: int) -> np.ndarray:
    n = 1 << kac
    x = np.arange(n)
    return np.stack([(x >> (kac - 1 - j)) & 1 for j in range(kac)], axis=1)


def _duzeni_dogrula() -> bool:
    from nefs.zihin_durumu import donme

    ayar = QAyar()
    q = QYazmac(1, ayar)
    bas = q.kulli("tasdik", 0)
    q.tek(bas, donme(0.5 * np.pi))
    P = np.asarray(q.blok_dagilimi(bas, 3), float).ravel()
    return bool(np.argmax(P) == 4)


def _kutleler(q: QYazmac) -> Dict[str, float]:
    bas = q.kulli("tasdik", 0)
    kac = 5
    P = np.asarray(q.blok_dagilimi(bas, kac), float).ravel()
    b = _blok_bitleri(kac)
    tas0, tas1, nak0 = b[:, 0], b[:, 1], b[:, 3]

    tenakuz = float(P[(tas0 == 1) & (nak0 == 1)].sum())
    ayniyet = float(P[tas0 != tas1].sum())

    p_tas0 = float(P[tas0 == 1].sum())
    p_tas1 = float(P[tas1 == 1].sum())
    p_nak0 = float(P[nak0 == 1].sum())
    tenakuz_taban = p_tas0 * p_nak0
    ayniyet_taban = p_tas0 * (1.0 - p_tas1) + (1.0 - p_tas0) * p_tas1

    mb = q.kulli("mizan", 0)
    _, mk = q._alan["mizan"]
    Pm = np.asarray(q.blok_dagilimi(mb, mk), float).ravel()
    mizan_uyku = float(Pm[0])
    tasdik_uyanik = float(P[tas0 == 1].sum())
    kafi_sebep = tasdik_uyanik * mizan_uyku

    return {"tenakuz": tenakuz, "ayniyet": ayniyet,
            "kâfi_sebep": kafi_sebep,
            "tenakuz_fazla": tenakuz - tenakuz_taban,
            "ayniyet_fazla": ayniyet - ayniyet_taban,
            "toplam": tenakuz + ayniyet + kafi_sebep,
            "fazla": abs(tenakuz - tenakuz_taban)
                     + abs(ayniyet - ayniyet_taban)}


def sadakat_olcusu(tohum: int = 0, satir: int = 6, sozluk: int = 16,
                   ayar: Optional[QAyar] = None, kalp: bool = True
                   ) -> List[Dict[str, object]]:
    ayar = ayar or QAyar(tohum=tohum)
    rng = np.random.default_rng(tohum)
    belirtec = [int(x) for x in rng.integers(0, sozluk, size=satir)]
    E = belirtecleri_kodla(belirtec, ayar.veri_lifi, ayar.veri_lifi)

    nefs = QNefs(tohum, ayar, sadakat=kalp)
    q = QYazmac(satir, ayar)
    q.kodla(E)
    q.superpozisyon()
    q.harman()

    sicil = qsicil()
    onceki = _kutleler(q)
    satirlar: List[Dict[str, object]] = []
    for adim, no in enumerate(QAKIS):
        t0 = time.perf_counter()
        sicil[no].kosu(q, nefs.p)
        if kalp:
            vicdan(q, nefs.p, ne="işaret")
        simdi = _kutleler(q)
        satirlar.append({
            "adım": adim, "no": no, "ad": sicil[no].ad,
            "tenakuz": simdi["tenakuz"], "ayniyet": simdi["ayniyet"],
            "kâfi_sebep": simdi["kâfi_sebep"],
            "Δtenakuz": simdi["tenakuz"] - onceki["tenakuz"],
            "Δayniyet": simdi["ayniyet"] - onceki["ayniyet"],
            "Δkâfi": simdi["kâfi_sebep"] - onceki["kâfi_sebep"],
            "Δtoplam": simdi["toplam"] - onceki["toplam"],
            "fazla": simdi["fazla"],
            "tenakuz_fazla": simdi["tenakuz_fazla"],
            "ayniyet_fazla": simdi["ayniyet_fazla"],
            "süre_sn": time.perf_counter() - t0,
        })
        onceki = simdi
    if kalp:
        vicdan(q, ne="intaç")
        son = _kutleler(q)
        satirlar.append({"adım": len(satirlar), "no": 0, "ad": "«sadakat intâcı»",
                         "tenakuz": son["tenakuz"], "ayniyet": son["ayniyet"],
                         "kâfi_sebep": son["kâfi_sebep"],
                         "Δtenakuz": son["tenakuz"] - onceki["tenakuz"],
                         "Δayniyet": son["ayniyet"] - onceki["ayniyet"],
                         "Δkâfi": son["kâfi_sebep"] - onceki["kâfi_sebep"],
                         "Δtoplam": son["toplam"] - onceki["toplam"],
                         "fazla": son["fazla"],
                         "tenakuz_fazla": son["tenakuz_fazla"],
                         "ayniyet_fazla": son["ayniyet_fazla"],
                         "süre_sn": 0.0})
    return satirlar


def haritala(satirlar: Sequence[Dict[str, object]], esik: float = 1e-9
             ) -> Dict[str, object]:
    sadik = [r for r in satirlar if float(r["Δtoplam"]) <= esik]
    sadakatsiz = sorted((r for r in satirlar if float(r["Δtoplam"]) > esik),
                        key=lambda r: -float(r["Δtoplam"]))
    return {"sadık": sadik, "sadakatsiz": sadakatsiz,
            "sadık_sayısı": len(sadik), "toplam": len(satirlar)}


def rapor(tohum: int = 0, satir: int = 6) -> str:
    s = ["=== MANTIĞA SADAKAT: 41 meleke şartı bozuyor mu? ===", ""]
    s.append("bit düzeni sınaması: %s"
             % ("GEÇTİ" if _duzeni_dogrula() else "**KALDI -- ölçüm geçersiz**"))
    s += ["",
          "tenakuz   : P(tasdik=1 ∧ nakz=1)      -- hem mühür hem nakz",
          "ayniyet   : P(tasdik₀ ≠ tasdik₁)      -- hüküm kendi içinde bölük",
          "kâfi sebep: P(tasdik=1) · P(mîzân=0)  -- delilsiz mühür",
          "",
          "  %-3s %-22s %10s %10s %10s %11s"
          % ("𝒪", "ad", "tenakuz", "ayniyet", "kâfi", "Δtoplam")]
    r = sadakat_olcusu(tohum=tohum, satir=satir, kalp=True)
    for x in r:
        s.append("  %-3d %-22s %10.3e %10.3e %10.3e %+11.3e"
                 % (x["no"], x["ad"], x["tenakuz"], x["ayniyet"],
                    x["kâfi_sebep"], x["Δtoplam"]))

    h = haritala(r)
    s += ["", "--- SADAKAT HÜKMÜ ---",
          "şartı BOZMAYAN meleke : %d / %d"
          % (h["sadık_sayısı"], h["toplam"])]
    if h["sadakatsiz"]:
        s.append("en çok bozanlar:")
        for x in h["sadakatsiz"][:6]:
            s.append("   𝒪%-3d %-22s Δ=%+.3e (tenakuz %+.2e, ayniyet %+.2e,"
                     " kâfi %+.2e)"
                     % (x["no"], x["ad"], x["Δtoplam"], x["Δtenakuz"],
                        x["Δayniyet"], x["Δkâfi"]))
    try:
        from nefs.zirh import muhru_stabilizerle_yuzlestir
        from nefs.melekeler import QNefs as _QN
        from nefs.qegitim import belirtecleri_kodla as _bk
        _ay = QAyar(tohum=tohum)
        _E = _bk([1, 2, 3, 4, 5, 6], _ay.veri_lifi, 16)
        _q = _QN(tohum, _ay).idrak_et(_E)
        yz = muhru_stabilizerle_yuzlestir(_q)
        s += ["", "STABİLİZER YÜZLEŞTİRMESİ (kuantum/stabilizer.py):",
              "  hüküm bloğu %d kübit, MPS ile Clifford temsili arası"
              " tvd = %.4f" % (yz["kübit"], yz["tvd"]),
              "  kapsanan şart: %d   kapsanmayan: %s"
              % (yz["kapsanan_şart"], yz["kapsanmayan"])]
    except Exception as e:
        s += ["", "STABİLİZER YÜZLEŞTİRMESİ kurulamadı: %s" % e]

    try:
        from nefs.musahede import kopru
        kk = kopru()
        s += ["", "FUNKTÖR KÖPRÜSÜ (token_uzaylari/morfizm.py):",
              "  tersinir=%s  çarpışma=%d  izometri=%s  mesafe kor.=%.4f"
              % (kk["tersinir"], kk["çarpışma"], kk["izometri"],
                 kk["mesafe_korelasyonu"]),
              "  " + str(kk["hüküm"])]
    except Exception as e:
        s += ["", "FUNKTÖR KÖPRÜSÜ kurulamadı: %s" % e]

    son = r[-1] if r else None
    if son:
        s += ["",
              "akış sonunda ihlâl kütlesi: tenakuz=%.4f  ayniyet=%.4f  "
              "kâfi_sebep=%.4f"
              % (son["tenakuz"], son["ayniyet"], son["kâfi_sebep"]),
              "",
              "TESADÜF TABANININ ÜSTÜNDEKİ FAZLALIK (asıl hüküm budur):",
              "  tenakuz fazlası = %+.4f   ayniyet fazlası = %+.4f"
              % (son["tenakuz_fazla"], son["ayniyet_fazla"]),
              "",
              "Fazlalık sıfıra yakınsa mana şudur: küllî hüküm alanları",
              "mantıkî şartı ne çiğniyor ne gözetiyor -- YAPISIZLAR.",
              "Bu, H94'teki 'kalp yok' hükmünün ikinci bir delilidir."]
    ry = sadakat_olcusu(tohum=tohum, satir=satir, kalp=False)
    sy, sk = ry[-1], r[-1]
    s += ["", "=" * 62,
          "KALP SÖKÜLÜNCE NE OLUYOR? (haraplama, sadakat kapısı kapalı)",
          "",
          "  %-22s %12s %12s %10s" % ("ölçü", "KALPSİZ", "KALPLİ", "kazanç"),
          "  %-22s %12.4f %12.4f %9.1f×"
          % ("tenakuz kütlesi", sy["tenakuz"], sk["tenakuz"],
             sy["tenakuz"] / max(sk["tenakuz"], 1e-12)),
          "  %-22s %12.4f %12.4f %9.1f×"
          % ("ayniyet ihlâli", sy["ayniyet"], sk["ayniyet"],
             sy["ayniyet"] / max(sk["ayniyet"], 1e-12)),
          "  %-22s %+12.4f %+12.4f %10s"
          % ("tenakuz FAZLASI", sy["tenakuz_fazla"], sk["tenakuz_fazla"], "-"),
          "  %-22s %+12.4f %+12.4f %10s"
          % ("ayniyet FAZLASI", sy["ayniyet_fazla"], sk["ayniyet_fazla"], "-"),
          "",
          "Kalp bir uzuvsa: söküldüğünde vücut BOZULMALI. Kazanç 1'e",
          "yakınsa kapı bir şey yapmıyor demektir ve öyle yazılır."]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
