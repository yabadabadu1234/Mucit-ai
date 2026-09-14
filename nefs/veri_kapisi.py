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
    "kirlilik": 0.0, "uyumsuzluk": 0.0, "terfi": 0.0, "açık": 1.0}


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
        "    ret sebebi üç hudda göre: tenakuz %d · kısırdöngü %d"
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


def _kisirdongu(dizi: Sequence[int]) -> int:
    u = [int(x) for x in dizi]
    for boy in range(1, len(u) // 2 + 1):
        if u[-boy:] == u[-2 * boy:-boy]:
            return int(boy)
    return 0


def _hukum(bag: Sequence[int], hedef: int, gorulen: Dict[Tuple[int, ...],
           int], ayar: VeriKapisiAyari) -> Dict[str, Any]:
    anahtar = tuple(int(x) for x in bag)
    evvelki = gorulen.get(anahtar)
    if evvelki is not None and int(evvelki) != int(hedef):
        return {"kabul": True, "hudut": "tenakuz", "terfi": True,
                "kayıt": TEVAKKUF, "sayı": float(abs(evvelki - hedef)),
                "sebep": "aynı bağlam evvelce %d hedefiyle geldi, şimdi "
                         "%d ile geliyor -- veri kendi kendini nakzediyor"
                         % (int(evvelki), int(hedef))}
    boy = _kisirdongu(list(bag) + [int(hedef)])
    if boy:
        return {"kabul": True, "hudut": "kısırdöngü", "terfi": False,
                "kayıt": TEVAKKUF, "sayı": float(boy),
                "sebep": "dizinin son %d basamağı kendinden evvelki %d "
                         "basamağın aynısı -- veri kendi üstüne kapanıyor"
                         % (boy, boy)}
    taban = max(2, int(ayar.taban))
    tasan = sum(1 for x in list(bag) + [int(hedef)]
                if not (0 <= int(x) < taban))
    if tasan:
        return {"kabul": False, "hudut": "mantıksızlık", "terfi": False,
                "kayıt": CERH, "sayı": float(tasan),
                "sebep": "%d basamak taşıyıcının kod uzayı [0,%d) dışında"
                         % (tasan, taban)}
    return {"kabul": True, "hudut": "", "terfi": False,
            "kayıt": TASDIK, "sayı": 0.0, "sebep": ""}


def veri_kapisi(veri: Sequence[Any],
                ayar: Optional[VeriKapisiAyari] = None
                ) -> Dict[str, Any]:
    from .qegitim import ornek_bol
    a = ayar or VeriKapisiAyari()
    gelen = list(veri)
    assert gelen, "veri kapısına BOŞ yığın geldi -- yoklanacak şey yok"
    if not int(a.acik):
        _KAPI["gelen"] += float(len(gelen))
        _KAPI["kabul"] += float(len(gelen))
        return {"kabul": gelen, "gelen": len(gelen), "reddedilen": [],
                "kayıt": [TASDIK] * len(gelen), "sebep": "kapı KAPALI",
                "hüküm": [{"kabul": True, "hudut": "", "kayıt": TASDIK,
                           "sayı": 0.0, "sebep": ""}] * len(gelen)}
    gorulen: Dict[Tuple[int, ...], int] = {}
    kabul: List[Any] = []
    hukumler: List[Dict[str, Any]] = []
    red_sebebi: List[str] = []
    for o in gelen:
        bag, hedef, _cins, _makam = ornek_bol(o)
        h = _hukum(bag, int(hedef), gorulen, a)
        gorulen[tuple(int(x) for x in bag)] = int(hedef)
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
            "hüküm": hukumler, "sebep": red_sebebi}


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


def kapi_tertibi(kapi_hukmu: Optional[Dict[str, Any]],
                 haller: Sequence[Any], hafiza,
                 mahalli=None) -> int:
    if not kapi_hukmu or hafiza is None:
        return 0
    hukumler = list(kapi_hukmu.get("hüküm") or ())
    H = [np.asarray(h, complex).reshape(-1) for h in haller]
    if len(H) < 3:
        return 0
    tertip = 0
    for i, h in enumerate(hukumler):
        if str(h.get("hudut")) != "tenakuz":
            continue
        if not bool(h.get("terfi")):
            continue
        a = i % len(H)
        hafiza.yeniden_tertiple(
            (H[a], H[(a + 1) % len(H)]), sahit=H[(a + 2) % len(H)],
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
