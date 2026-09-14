from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .hafiza import CERH, TASDIK, TEVAKKUF

__all__ = ["VeriKapisiAyari", "veri_kapisi", "kapi_beyani",
           "kapi_metni", "hafiza_hukmu", "kapi_tetabuku",
           "kapi_tertibi"]


@dataclass
class VeriKapisiAyari:
    acik: int = 1
    sozluk: int = 0
    taban: int = 0
    basamak: int = 0


_KAPI: Dict[str, float] = {
    "gelen": 0.0, "kabul": 0.0, "ret": 0.0,
    "tenakuz": 0.0, "kısırdöngü": 0.0, "mantıksızlık": 0.0,
    "tasdik": 0.0, "tevakkuf": 0.0, "cerh": 0.0,
    "kirlilik": 0.0, "uyumsuzluk": 0.0, "terfi": 0.0, "idrak": 0.0,
    "açık": 1.0}


def kapi_beyani() -> Dict[str, float]:
    b = dict(_KAPI)
    b["ret_nispeti"] = (b["ret"] / b["gelen"]) if b["gelen"] else 0.0
    return b


def kapi_metni(b: Optional[Dict[str, float]] = None) -> str:
    d = dict(b or kapi_beyani())
    if not d.get("gelen"):
        return "  VERİ KAPISI: HİÇ YOKLANMADI -- kırmızı (ferman 2-Ó)"
    return "\n".join([
        "  VERİ KAPISI -- RET GİRENE BAKAR (ferman 2-Ó)",
        "    gelen %d   kabul %d   ret %d   (%.4f)"
        % (int(d["gelen"]), int(d["kabul"]), int(d["ret"]),
           d["ret_nispeti"]),
        "    KAPI KODLAMADAN SONRA KOŞAR: %d örnek idrak edildi, üç"
        " hudut" % int(d.get("idrak", 0)),
        "    ham metnin zâhirinden değil HÂL ÜÇGENİNDEN (Δ₃) okundu.",
        "    hudut dökümü: tenakuz %d · kısırdöngü %d"
        " · mantıksızlık %d"
        % (int(d["tenakuz"]), int(d["kısırdöngü"]),
           int(d["mantıksızlık"])),
        "    hafıza kaydının cinsi: tasdik %d · tevakkuf %d · cerh %d"
        % (int(d["tasdik"]), int(d["tevakkuf"]), int(d["cerh"])),
        "    kapı kirliliği %.6f ↔ ret nispeti %.6f, uyumsuzluk %.6f"
        % (d.get("kirlilik", 0.0), d["ret_nispeti"],
           d.get("uyumsuzluk", 0.0)),
        "    KAPI BİR ELEK DEĞİL TASNİF MERCİİDİR: tenakuzlu %d örnek"
        " ELENMEDİ," % int(d.get("terfi", 0.0)),
        "    modalite lifiyle TERFİ etti; ret yalnız mantıksızlıkta"
        " kaldı.",
        "    Model KONUŞMAYI reddetmez; tasnif edilen şey içeri girecek",
        "    VERİDİR, ve kabul edilenin hafızaya nasıl yazılacağını da",
        "    bu kapı tayin eder.   (ölçü %s)"
        % ("açık" if d.get("açık") else "KAPALI"),
    ])


def _tasma(bag: Sequence[int], hedef: int, taban: int) -> int:
    t = max(2, int(taban))
    return sum(1 for x in list(bag) + [int(hedef)]
               if not (0 <= int(x) < t))


def _idrak(nefs, bag: Sequence[int], hedef: int,
           taban: int) -> np.ndarray:
    from .qegitim import belirtecleri_kodla
    dizi = [int(x) for x in bag] + [int(hedef)]
    E = belirtecleri_kodla(dizi, int(taban), int(taban))
    q = nefs.idrak_et(E)
    _KAPI["idrak"] += 1.0
    return np.asarray(q.y.psi[0], complex).reshape(-1)


def _hukum(i: int, bag: Sequence[int], hedef: int, H: List[np.ndarray],
           gorulen: Dict[Tuple[int, ...], int],
           ayar: VeriKapisiAyari) -> Dict[str, Any]:
    tasan = _tasma(bag, int(hedef), int(ayar.taban))
    if tasan:
        return {"kabul": False, "hudut": "mantıksızlık", "terfi": False,
                "kayıt": CERH, "sayı": float(tasan), "üçgen": (),
                "sebep": "%d basamak taşıyıcının kod uzayı [0,%d) dışında"
                         % (tasan, max(2, int(ayar.taban)))}
    es = gorulen.get(tuple(int(x) for x in bag))
    if es is None or int(es) == i:
        es = i - 1
    sahit = next((j for j in range(i - 1, -1, -1)
                  if j != i and j != int(es)), -1)
    if i < 2 or int(es) < 0 or sahit < 0:
        return {"kabul": True, "hudut": "", "terfi": False,
                "kayıt": TASDIK, "sayı": 0.0, "üçgen": (),
                "sebep": ""}
    from .mukayese import bargmann
    ucgen = (int(i), int(es), int(sahit))
    b = bargmann([H[i], H[int(es)], H[sahit]])
    if bool(b["tenakuz"]):
        return {"kabul": True, "hudut": "tenakuz", "terfi": True,
                "kayıt": TEVAKKUF, "sayı": float(b["takla_nispeti"]),
                "üçgen": ucgen,
                "sebep": "hâl üçgeni Φ₃=%+.4f rad ile Möbius taklası "
                         "veriyor (takla nispeti %.4f > kapanış %.4f) -- "
                         "veri kendi kendini nakzediyor"
                         % (float(b["Φ"]), float(b["takla_nispeti"]),
                            float(b["kapanış_nispeti"]))}
    if bool(b["kısır"]):
        return {"kabul": True, "hudut": "kısırdöngü", "terfi": False,
                "kayıt": TEVAKKUF, "sayı": float(b["kapanış_nispeti"]),
                "üçgen": ucgen,
                "sebep": "hâl halkası Φ₃=%+.4f rad ile kendi üstüne "
                         "kapanıyor (koherans %.4f) -- yeni bir şey "
                         "söylemiyor" % (float(b["Φ"]), float(b["r"]))}
    return {"kabul": True, "hudut": "", "terfi": False,
            "kayıt": TASDIK, "sayı": 0.0, "üçgen": ucgen, "sebep": ""}


def veri_kapisi(veri: Sequence[Any],
                ayar: Optional[VeriKapisiAyari] = None,
                nefs=None) -> Dict[str, Any]:
    from .qegitim import ornek_bol
    a = ayar or VeriKapisiAyari()
    gelen = list(veri)
    assert gelen, "veri kapısına BOŞ yığın geldi -- yoklanacak şey yok"
    if not int(a.acik):
        _KAPI["gelen"] += float(len(gelen))
        _KAPI["kabul"] += float(len(gelen))
        return {"kabul": gelen, "gelen": len(gelen), "reddedilen": 0,
                "kayıt": [TASDIK] * len(gelen), "sebep": "kapı KAPALI",
                "hâl": [], "hüküm": [
                    {"kabul": True, "hudut": "", "kayıt": TASDIK,
                     "sayı": 0.0, "üçgen": (), "sebep": ""}] * len(gelen)}
    assert nefs is not None, (
        "veri kapısı MOTORSUZ çağrıldı -- üç hudut hâl üstünde ölçülür, "
        "ham metnin zâhirinden değil (ferman 2-Ú)")
    gorulen: Dict[Tuple[int, ...], int] = {}
    H: List[np.ndarray] = []
    kabul: List[Any] = []
    hukumler: List[Dict[str, Any]] = []
    red_sebebi: List[str] = []
    for i, o in enumerate(gelen):
        bag, hedef, _cins, _makam = ornek_bol(o)
        H.append(_idrak(nefs, bag, int(hedef), int(a.taban)))
        h = _hukum(i, bag, int(hedef), H, gorulen, a)
        gorulen[tuple(int(x) for x in bag)] = i
        _KAPI["gelen"] += 1.0
        if h["hudut"]:
            _KAPI[str(h["hudut"])] += 1.0
        if h["kabul"]:
            _KAPI["kabul"] += 1.0
            _KAPI["terfi"] += float(bool(h.get("terfi")))
            kabul.append(o)
            hukumler.append(h)
        else:
            _KAPI["ret"] += 1.0
            if len(red_sebebi) < 3:
                red_sebebi.append(str(h["sebep"]))
        _KAPI[{TASDIK: "tasdik", TEVAKKUF: "tevakkuf",
               CERH: "cerh"}[float(h["kayıt"])]] += 1.0
    return {"kabul": kabul, "gelen": len(gelen),
            "reddedilen": len(gelen) - len(kabul),
            "kayıt": [float(h["kayıt"]) for h in hukumler],
            "hâl": H, "hüküm": hukumler, "sebep": red_sebebi}


def kapi_tetabuku(tenakuz: float, kisirdongu: float,
                  mantiksizlik: float) -> Dict[str, float]:
    kir = float(tenakuz) + float(kisirdongu) + float(mantiksizlik)
    kirlilik = float(kir / (1.0 + kir))
    b = kapi_beyani()
    if not b.get("gelen"):
        return {"kayıp": 0.0, "kirlilik": kirlilik, "ret_nispeti": 0.0,
                "gelen": 0.0, "uyumsuzluk": 0.0}
    uyumsuzluk = float(abs(float(b["ret_nispeti"]) - kirlilik))
    _KAPI["kirlilik"] = kirlilik
    _KAPI["uyumsuzluk"] = uyumsuzluk
    return {"kayıp": uyumsuzluk, "kirlilik": kirlilik,
            "ret_nispeti": float(b["ret_nispeti"]),
            "gelen": float(b["gelen"]), "uyumsuzluk": uyumsuzluk}


def kapi_tertibi(kapi_hukmu: Optional[Dict[str, Any]], hafiza,
                 mahalli=None) -> int:
    if not kapi_hukmu or hafiza is None:
        return 0
    H = list(kapi_hukmu.get("hâl") or ())
    if not H:
        return 0
    tertip = 0
    for h in list(kapi_hukmu.get("hüküm") or ()):
        if str(h.get("hudut")) != "tenakuz":
            continue
        ucgen = tuple(h.get("üçgen") or ())
        if len(ucgen) != 3:
            continue
        i, es, sahit = (int(x) for x in ucgen)
        hafiza.yeniden_tertiple((H[i], H[es]), sahit=H[sahit],
                                mahalli=mahalli, kapi="kapı")
        tertip += 1
    return tertip


def hafiza_hukmu(kapi_hukmu: Optional[Dict[str, Any]],
                 indis: int) -> float:
    if not kapi_hukmu:
        return TASDIK
    kayit = list(kapi_hukmu.get("kayıt") or ())
    if not kayit:
        return TASDIK
    return float(kayit[int(indis) % len(kayit)])
