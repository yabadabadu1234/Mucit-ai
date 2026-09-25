from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["SadakatAyari", "parite_maskesi", "parite_dizini",
           "tenakuz_alarmi", "mantiki_degil", "sadakat_uygula",
           "sadakat_beyani", "sadakat_sifirla",
           "BILINEN_SUPERPOZISYONLAR", "sadakat_devresi",
           "sadakat_devre_beyani", "sadakat_devre_metni"]


@dataclass
class SadakatAyari:

    acik: int = 1
    parite_lifi: int = 2
    lif_yapisi: Tuple[int, ...] = (16, 16, 16)
    sozluk: int = 0

    def __post_init__(self) -> None:
        assert len(self.lif_yapisi) >= 1, "lif yapısı BOŞ olamaz"
        assert 0 <= int(self.parite_lifi) < len(self.lif_yapisi), (
            "parite lifi %d, lif yapısı %r -- aralık dışı"
            % (self.parite_lifi, self.lif_yapisi))


_SAYAC: Dict[str, float] = {"çağrı": 0.0, "yoklanan": 0.0, "alarm": 0.0,
                            "sıfırlanan": 0.0, "ağırlık": 0.0,
                            "artık": 0.0,
                            "kapalı_çağrı": 0.0}

_DIZIN: Dict[Tuple[int, int], np.ndarray] = {}


def parite_maskesi(ayar: Optional[SadakatAyari] = None) -> int:
    a = ayar or SadakatAyari()
    lif = tuple(int(x) for x in a.lif_yapisi)
    for n in lif:
        assert n >= 1 and (n & (n - 1)) == 0, (
            "lif boyu ikinin kuvveti olmalı (parite maskesi bit aralığıdır); "
            "verilen: %r" % (lif,))
    j = int(a.parite_lifi)
    kaydir = 1
    for n in lif[j + 1:]:
        kaydir *= n
    genislik = lif[j]
    return (genislik - 1) * kaydir if kaydir > 1 else (genislik - 1)


def parite_dizini(d: int, ayar: Optional[SadakatAyari] = None) -> np.ndarray:
    a = ayar or SadakatAyari()
    maske = parite_maskesi(a)
    anahtar = (int(d), int(maske))
    hazir = _DIZIN.get(anahtar)
    if hazir is not None:
        return hazir
    k = np.arange(int(d), dtype=np.int64)
    v = (k & np.int64(maske)).astype(np.uint64)
    say = np.zeros(v.shape, np.uint8)
    for _ in range(64):
        if not v.any():
            break
        say ^= (v & np.uint64(1)).astype(np.uint8)
        v >>= np.uint64(1)
    dizin = say.astype(bool)
    _DIZIN[anahtar] = dizin
    return dizin


def tenakuz_alarmi(psi: np.ndarray,
                   ayar: Optional[SadakatAyari] = None
                   ) -> Tuple[float, int]:
    P = np.asarray(psi)
    if P.ndim == 1:
        P = P.reshape(1, -1)
    d = P.shape[-1]
    dizin = parite_dizini(d, ayar)
    guc = np.abs(P) ** 2
    yirtik = guc[..., dizin].sum(axis=-1)
    toplam = guc.sum(axis=-1)
    nispet = float(np.sum(yirtik) / max(float(np.sum(toplam)), 1e-300))
    return nispet, int(np.count_nonzero(yirtik > 1e-30))


def sadakat_uygula(hedef: Any, ayar: Optional[SadakatAyari] = None
                   ) -> Dict[str, Any]:
    a = ayar or SadakatAyari()
    _SAYAC["çağrı"] += 1.0

    yazmac = None
    if isinstance(hedef, np.ndarray):
        psi = hedef
    elif isinstance(getattr(hedef, "genlik", None), np.ndarray) \
            and isinstance(getattr(hedef, "faz", None), np.ndarray):
        m = 16.0
        psi = (np.asarray(hedef.genlik, float)
               * np.exp(2j * math.pi * np.asarray(hedef.faz, float) / m))
        psi = psi.reshape(1, -1)
    else:
        y = getattr(hedef, "y", hedef)
        assert hasattr(y, "psi"), (
            "sadakat_uygula: hedefin genliği bulunamadı (%r)" % type(hedef))
        yazmac = y
        psi = np.asarray(y.psi)

    P = psi if psi.ndim == 2 else psi.reshape(1, -1)
    d = P.shape[-1]
    dizin = parite_dizini(d, a)
    _SAYAC["yoklanan"] += float(int(np.count_nonzero(dizin)))

    once, satir = tenakuz_alarmi(P, a)
    _SAYAC["ağırlık"] += once
    if once > 1e-12:
        _SAYAC["alarm"] += 1.0

    if not int(a.acik):
        _SAYAC["kapalı_çağrı"] += 1.0
        _SAYAC["artık"] += once
        return {"alarm_önce": _bit(once), "alarm_sonra": _bit(once),
                "ağırlık_önce": once, "ağırlık_sonra": once,
                "sıfırlanan": 0, "satır": satir, "açık": False}

    sifirlanan = 0
    if once > 1e-12:
        Q = P.copy()
        Q[..., dizin] = 0.0
        nrm = np.linalg.norm(Q, axis=-1, keepdims=True)
        assert float(np.min(nrm)) > 1e-300, (
            "durumun TAMAMI mantık yırtığı sektöründe -- kod uzayına "
            "izdüşümü sıfır. Bu bir sayı hatası değil, mimarî bir "
            "çöküştür: parite lifi yanlış seçilmiş olmalı.")
        _iz = getattr(yazmac, "iz", None) if yazmac is not None else None
        if (_iz is not None and _iz.senet_acik and psi.ndim == 2
                and np.asarray(nrm, float).reshape(-1).size == P.shape[0]):
            _iz.kapi_yaz("durum", (), np.asarray(P, complex).copy())
            _iz.kapi_yaz("maske", (), np.asarray(dizin, bool).copy())
            _iz.kapi_yaz("ölçek", (),
                         np.asarray(nrm, float).reshape(-1, 1).copy())
        Q = Q / nrm
        sifirlanan = int(np.count_nonzero(dizin))
        _SAYAC["sıfırlanan"] += float(sifirlanan)
        if yazmac is not None:
            yazmac.psi = Q if psi.ndim == 2 else Q.reshape(-1)
        elif isinstance(hedef, np.ndarray) and hedef.ndim == P.ndim:
            hedef[...] = Q.reshape(hedef.shape)
        P = Q

    sonra, _ = tenakuz_alarmi(P, a)
    _SAYAC["artık"] += sonra
    return {"alarm_önce": _bit(once), "alarm_sonra": _bit(sonra),
            "ağırlık_önce": once, "ağırlık_sonra": sonra,
            "sıfırlanan": sifirlanan, "satır": satir, "açık": True}


def mantiki_degil(psi: np.ndarray,
                  ayar: Optional[SadakatAyari] = None) -> np.ndarray:
    a = ayar or SadakatAyari()
    P = np.asarray(psi)
    tek = P.ndim == 1
    Q = P.reshape(1, -1) if tek else P
    d = Q.shape[-1]
    maske = parite_maskesi(a)
    if bin(int(maske)).count("1") % 2 == 1:
        maske = int(maske) & (int(maske) - 1)
    assert maske != 0, (
        "mantıkî olumsuzlama için en az iki basamaklı bir parite lifi "
        "lâzım -- tek basamakta ¬P kod uzayının dışına düşer")
    k = np.arange(d, dtype=np.int64)
    return Q[..., k ^ np.int64(maske)].reshape(P.shape)


def _bit(agirlik: float) -> int:
    return int(float(agirlik) > 1e-12)


def sadakat_beyani() -> Dict[str, Any]:
    c = max(1.0, _SAYAC["çağrı"])
    return {"çağrı": int(_SAYAC["çağrı"]),
            "yoklanan": int(_SAYAC["yoklanan"]),
            "alarm": int(_SAYAC["alarm"]),
            "sıfırlanan": int(_SAYAC["sıfırlanan"]),
            "alarm_nispeti": float(_SAYAC["ağırlık"] / c),
            "artık_nispeti": float(_SAYAC["artık"] / c),
            "kapalı_çağrı": int(_SAYAC["kapalı_çağrı"])}


BILINEN_SUPERPOZISYONLAR: Tuple[str, ...] = (
    "veri", "parametre", "mahallî", "hafıza", "uzunluk", "çözüm", "mesele")


_DEVRE: Dict[str, float] = {
    "çağrı": 0.0, "süperpozisyon": 0.0, "imha": 0.0, "meçhul": 0.0,
    "dal": 0.0, "tashih": 0.0, "saniye": 0.0, "açık": 1.0}

_KAPSANAN: Dict[str, float] = {}
_MUAF: List[str] = []
_BAGLANMAMIS: List[str] = []


def _uc_kume(guc: np.ndarray, mantiksiz: np.ndarray
             ) -> Tuple[np.ndarray, np.ndarray, int]:
    g = np.asarray(guc, float).reshape(-1)
    m = np.asarray(mantiksiz, bool).reshape(-1)
    assert g.size == m.size, (
        "sadakat devresi: güç %d, mantıksızlık maskesi %d -- ölçü ile "
        "hüküm aynı uzayda olmalı" % (g.size, m.size))
    ic = (~m) & (g > 0.0)
    if not bool(ic.any()):
        return m, ic, 0
    esik = float(np.median(g[ic]))
    mechul = ic & (g < esik)
    return m, mechul, int(np.count_nonzero(mechul))


def _dali_ele(ad: str, genlik: np.ndarray, mantiksiz: np.ndarray
              ) -> np.ndarray:
    G = np.asarray(genlik)
    duz = G.reshape(-1)
    guc = np.abs(duz) ** 2
    imha, _mechul, n_mechul = _uc_kume(guc, mantiksiz)
    n_imha = int(np.count_nonzero(imha & (guc > 0.0)))
    if n_imha:
        duz = duz.copy()
        duz[imha] = 0
        nrm = float(np.linalg.norm(duz))
        assert nrm > 0.0, (
            "SADAKAT DEVRESİ %r SÜPERPOZİSYONUNU TAMAMEN SÖNDÜRDÜ -- "
            "mantıksız sayılan küme durumun tamamıymış. Bu bir sayı "
            "hatası değil, maskenin yanlış kurulduğunun delilidir "
            "(ferman 2-Đ: yalnız mantıksız olan imha edilir)." % ad)
        duz = duz / nrm
        G = duz.reshape(G.shape)
    _DEVRE["imha"] += float(n_imha)
    _DEVRE["meçhul"] += float(n_mechul)
    _DEVRE["dal"] += float(guc.size)
    _DEVRE["süperpozisyon"] += 1.0
    _KAPSANAN[ad] = _KAPSANAN.get(ad, 0.0) + 1.0
    return G


def _sonlu_degil(x: np.ndarray) -> np.ndarray:
    return ~np.isfinite(np.asarray(x).reshape(-1))


def _veri(nefs, a: SadakatAyari) -> bool:
    y = getattr(nefs, "y", None)
    psi = getattr(y, "psi", None) if y is not None else None
    if not isinstance(psi, np.ndarray):
        return False
    P = psi if psi.ndim == 2 else psi.reshape(1, -1)
    d = int(P.shape[-1])
    parite = parite_dizini(d, a)
    mantiksiz = np.tile(parite, P.shape[0]) | _sonlu_degil(P)
    Q = _dali_ele("veri", P, mantiksiz)
    y.psi = Q if psi.ndim == 2 else Q.reshape(-1)
    return True


def _mahalli(nefs, mahalli) -> bool:
    mh = mahalli if mahalli is not None else getattr(nefs, "mahalli", None)
    hal = getattr(mh, "hal", None) if mh is not None else None
    if not isinstance(hal, np.ndarray) or hal.size == 0:
        return False
    n = max(1, min(int(getattr(mh, "pencere", 0) or 0), hal.shape[1]))
    aktif = hal[:, :n, :]
    mh.hal[:, :n, :] = _dali_ele("mahallî", aktif, _sonlu_degil(aktif))
    return True


def _parametre(nefs, parametre) -> bool:
    pq = parametre if parametre is not None else getattr(nefs, "pq", None)
    g = getattr(pq, "genlik", None) if pq is not None else None
    if not isinstance(g, np.ndarray) or g.size == 0:
        return False
    mantiksiz = _sonlu_degil(g) | (np.asarray(g, float).reshape(-1) < 0.0)
    pq.genlik = np.asarray(_dali_ele("parametre", g, mantiksiz), float)
    f = np.asarray(getattr(pq, "faz", np.zeros(0)), float)
    tashih = int(np.count_nonzero(np.abs(f) > math.pi))
    if tashih:
        pq.faz = np.vectorize(math.remainder)(f, 2.0 * math.pi)
        _DEVRE["tashih"] += float(tashih)
    return True


def _hafiza(hafiza) -> bool:
    kayitlar = getattr(hafiza, "kayitlar", None)
    if not kayitlar:
        return False
    for k in list(kayitlar):
        x = np.asarray(getattr(k, "x", np.zeros(0)))
        if x.size == 0:
            continue
        suzulmus = _dali_ele("hafıza", x, _sonlu_degil(x))
        k.x = (np.asarray(suzulmus, complex) if np.iscomplexobj(x)
               else np.asarray(np.real(suzulmus), float))
    return True


def _mesele(fock) -> bool:
    modlar = getattr(fock, "modlar", None)
    if not modlar:
        return False
    ad = sorted(modlar)
    dol = np.array([float(modlar[k].doluluk) for k in ad], float)
    mantiksiz = _sonlu_degil(dol) | (dol < 1.0)
    for k, olmaz in zip(ad, mantiksiz):
        if bool(olmaz):
            fock.yok_et(k)
    _dali_ele("mesele", np.sqrt(np.maximum(dol, 0.0)), mantiksiz)
    return True


def _cozum_ve_uzunluk(netice, a: SadakatAyari
                      ) -> Tuple[Optional[bool], Optional[bool]]:
    if not isinstance(netice, dict):
        return None, None
    psi = netice.get("hal")
    c: Optional[bool] = None
    if isinstance(psi, np.ndarray) and psi.size:
        netice["hal"] = _dali_ele("çözüm", psi, _sonlu_degil(psi))
        c = True
    boy = netice.get("uzunluk_genliği")
    u: Optional[bool] = None
    if isinstance(boy, np.ndarray) and boy.size:
        n = int(netice.get("pencere", 0) or 0)
        sira = np.arange(boy.size, dtype=float)
        mantiksiz = (_sonlu_degil(boy) | (sira < 1.0)
                     | ((sira > float(n)) if n > 0 else False))
        netice["uzunluk_genliği"] = _dali_ele("uzunluk", boy, mantiksiz)
        u = True
    return c, u


def sadakat_devresi(nefs=None, hafiza=None, fock=None, netice=None,
                    mahalli=None, parametre=None,
                    ayar: Optional[SadakatAyari] = None) -> Dict[str, Any]:
    a = ayar or SadakatAyari()
    t0 = time.perf_counter()
    _DEVRE["çağrı"] += 1.0
    _MUAF.clear()
    _BAGLANMAMIS.clear()
    if not int(a.acik):
        _DEVRE["açık"] = 0.0
        _MUAF.extend(BILINEN_SUPERPOZISYONLAR)
        _DEVRE["saniye"] += time.perf_counter() - t0
        return sadakat_devre_beyani()
    _DEVRE["açık"] = 1.0

    def _var(deger: bool) -> Optional[bool]:
        return True if deger else None

    kosan: Dict[str, Optional[bool]] = {
        "veri": _var(_veri(nefs, a)) if nefs is not None else None,
        "mahallî": _var(_mahalli(nefs, mahalli)),
        "parametre": _var(_parametre(nefs, parametre)),
        "hafıza": _var(_hafiza(hafiza)) if hafiza is not None else None,
        "mesele": _var(_mesele(fock)) if fock is not None else None,
    }
    c, u = _cozum_ve_uzunluk(netice, a)
    kosan["çözüm"] = c
    kosan["uzunluk"] = u

    for ad in BILINEN_SUPERPOZISYONLAR:
        h = kosan.get(ad)
        if h is None:
            _BAGLANMAMIS.append(ad)
        elif not h:
            _MUAF.append(ad)
    _DEVRE["saniye"] += time.perf_counter() - t0
    return sadakat_devre_beyani()


def sadakat_devre_beyani() -> Dict[str, Any]:
    b: Dict[str, Any] = dict(_DEVRE)
    dal = max(1.0, _DEVRE["dal"])
    b["imha_nispeti"] = float(_DEVRE["imha"] / dal)
    b["meçhul_nispeti"] = float(_DEVRE["meçhul"] / dal)
    b["muaf"] = list(_MUAF)
    b["bağlanmamış"] = list(_BAGLANMAMIS)
    b["kapsanan"] = dict(_KAPSANAN)
    b["bilinen"] = len(BILINEN_SUPERPOZISYONLAR)
    b["kapsama"] = float(len(_KAPSANAN)) / float(
        len(BILINEN_SUPERPOZISYONLAR))
    return b


def sadakat_devre_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = b if b is not None else sadakat_devre_beyani()
    if not int(d.get("çağrı", 0)):
        return ("  SADAKAT DEVRESİ: HİÇ KOŞMADI -- kırmızı (ferman 2-Đ)")
    return "\n".join([
        "  SADAKAT DEVRESİ -- İSTİSNASIZ HER SÜPERPOZİSYONDA (ferman 2-Đ)",
        "    çağrı %d   dokunulan süperpozisyon %d   %.4f sn"
        % (int(d["çağrı"]), int(d["süperpozisyon"]), float(d["saniye"])),
        "    kapsama %d/%d  (%s)"
        % (len(d.get("kapsanan") or {}), int(d["bilinen"]),
           ", ".join(sorted(d.get("kapsanan") or {})) or "yok"),
        "    MUAF KALAN      : %s   (boş olmalı -- invaryant I8)"
        % (", ".join(d.get("muaf") or []) or "yok"),
        "    BAĞLANMAMIŞ     : %s   (tahttan geçirilmeyen süperpozisyon)"
        % (", ".join(d.get("bağlanmamış") or []) or "yok"),
        "    dal %d   İMHA %d (%.6f)   MEÇHUL BIRAKILAN %d (%.6f)"
        % (int(d["dal"]), int(d["imha"]), float(d["imha_nispeti"]),
           int(d["meçhul"]), float(d["meçhul_nispeti"])),
        "    Meçhul SIFIR ise devre fazla eliyor demektir: mantığı henüz",
        "    görünmeyen ihtimal elenmez, yalnız MANTIKSIZ olan imha edilir.",
        "    faz tashihi %d   (ölçü %s)"
        % (int(d["tashih"]), "açık" if d.get("açık") else "KAPALI"),
    ])


def sadakat_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
    for k in _DEVRE:
        _DEVRE[k] = 0.0 if k != "açık" else 1.0
    _KAPSANAN.clear()
    _MUAF.clear()
    _BAGLANMAMIS.clear()
