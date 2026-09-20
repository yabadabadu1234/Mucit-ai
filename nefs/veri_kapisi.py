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
    "parça": 0.0, "parça_haddi": 0.0, "açık": 1.0}


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
        "    KAPI KODLAMADAN SONRA, PARÇA PARÇA KOŞAR: %d parça ×"
        " %d hadd, %d idrak"
        % (int(d.get("parça", 0)), int(d.get("parça_haddi", 0)),
           int(d.get("idrak", 0))),
        "    ŞAHİT YOKTUR: hüküm çiftin BÜTÜN VECİHLERDEKİ ayniyet ve",
        "    ihtilafından okunur; melekesi tayin eder, hafızaya yazar.",
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
    from kuantum.qegitim import belirtecleri_kodla
    dizi = [int(x) for x in bag] + [int(hedef)]
    E = belirtecleri_kodla(dizi, int(taban), int(taban))
    q = nefs.idrak_et(E)
    _KAPI["idrak"] += 1.0
    return np.asarray(q.y.psi[0], complex).reshape(-1)


def _bos_hukum() -> Dict[str, Any]:
    return {"kabul": True, "hudut": "", "terfi": False,
            "kayıt": TASDIK, "sayı": 0.0, "kutup": (), "sebep": ""}


def _hukum(i: int, bag: Sequence[int], hedef: int, H: List[np.ndarray],
           gorulen: Dict[Tuple[int, ...], int], vecihler,
           hafiza, ayar: VeriKapisiAyari) -> Dict[str, Any]:
    tasan = _tasma(bag, int(hedef), int(ayar.taban))
    if tasan:
        return {"kabul": False, "hudut": "mantıksızlık", "terfi": False,
                "kayıt": CERH, "sayı": float(tasan), "kutup": (),
                "sebep": "%d basamak taşıyıcının kod uzayı [0,%d) dışında"
                         % (tasan, max(2, int(ayar.taban)))}
    es = gorulen.get(tuple(int(x) for x in bag))
    if es is None or int(es) == i:
        es = i - 1
    if int(es) < 0:
        return _bos_hukum()
    from .mukayese import ayniyet_ihtilaf
    a = ayniyet_ihtilaf(H[i], H[int(es)], vecihler, hafiza=hafiza)
    kutup = (H[i], H[int(es)])
    if bool(a["tenakuz"]):
        return {"kabul": True, "hudut": "tenakuz", "terfi": True,
                "kayıt": float(a["kayıt"]), "sayı": float(a["ihtilaf"]),
                "kutup": kutup,
                "sebep": "çift %r vechinde örtüşme %.4f, %r vechinde "
                         "%.4f -- ihtilaf nispeti %.4f > ittifak %.4f: "
                         "bir âlemde aynı, başkasında zıt"
                         % (a["en_ayrık"],
                            a["örtüşme"].get(a["en_ayrık"], 0.0),
                            a["en_yakın"],
                            a["örtüşme"].get(a["en_yakın"], 0.0),
                            float(a["ihtilaf"]), float(a["ittifak"]))}
    if bool(a["kısır"]):
        return {"kabul": True, "hudut": "kısırdöngü", "terfi": False,
                "kayıt": float(a["kayıt"]), "sayı": float(a["ittifak"]),
                "kutup": (),
                "sebep": "çift bütün vecihlerde örtüşüyor (asgarî %.4f, "
                         "ittifak %.4f) -- yeni bir şey söylemiyor"
                         % (float(a["asgarî_örtüşme"]),
                            float(a["ittifak"]))}
    return _bos_hukum()


def parca_haddi(taban: int) -> int:
    from .donanim import bellek_haddi
    had = bellek_haddi()
    bayt = max(1, int(taban)) * 16
    kac = int(max(2, int(float(had) * 0.05) // max(bayt, 1)))
    _KAPI["parça_haddi"] = float(kac)
    return kac


def veri_kapisi(veri: Sequence[Any],
                ayar: Optional[VeriKapisiAyari] = None,
                nefs=None, hafiza=None) -> Dict[str, Any]:
    from kuantum.qegitim import ornek_bol
    from .mukayese import vecihleri_istihrac
    a = ayar or VeriKapisiAyari()
    gelen = list(veri)
    assert gelen, "veri kapısına BOŞ yığın geldi -- yoklanacak şey yok"
    if not int(a.acik):
        _KAPI["gelen"] += float(len(gelen))
        _KAPI["kabul"] += float(len(gelen))
        return {"kabul": gelen, "gelen": len(gelen), "reddedilen": 0,
                "kayıt": [TASDIK] * len(gelen), "sebep": "kapı KAPALI",
                "hüküm": [_bos_hukum()] * len(gelen)}
    assert nefs is not None, (
        "veri kapısı MOTORSUZ çağrıldı -- üç hudut hâl üstünde ölçülür, "
        "ham metnin zâhirinden değil (ferman 2-Ú)")
    parca = parca_haddi(int(a.taban))
    kabul: List[Any] = []
    hukumler: List[Dict[str, Any]] = []
    red_sebebi: List[str] = []
    for bas in range(0, len(gelen), parca):
        dilim = gelen[bas:bas + parca]
        gorulen: Dict[Tuple[int, ...], int] = {}
        H: List[np.ndarray] = []
        baglar: List[Sequence[int]] = []
        hedefler: List[int] = []
        for o in dilim:
            bag, hedef, _cins, _makam = ornek_bol(o)
            baglar.append(bag)
            hedefler.append(int(hedef))
            H.append(_idrak(nefs, bag, int(hedef), int(a.taban)))
        vecihler = vecihleri_istihrac(H) if len(H) >= 2 else ()
        _KAPI["parça"] += 1.0
        for i, o in enumerate(dilim):
            h = (_hukum(i, baglar[i], hedefler[i], H, gorulen,
                        vecihler, hafiza, a)
                 if vecihler else _bos_hukum())
            gorulen[tuple(int(x) for x in baglar[i])] = i
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


def kapi_tertibi(kapi_hukmu: Optional[Dict[str, Any]], hafiza,
                 mahalli=None) -> int:
    if not kapi_hukmu or hafiza is None:
        return 0
    tertip = 0
    for h in list(kapi_hukmu.get("hüküm") or ()):
        if str(h.get("hudut")) != "tenakuz":
            continue
        kutup = tuple(h.get("kutup") or ())
        if len(kutup) != 2:
            continue
        hafiza.yeniden_tertiple((kutup[0], kutup[1]), sahit=None,
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
