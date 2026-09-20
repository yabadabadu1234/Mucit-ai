from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from matematik.sonsuz_mertebeler_teorisi import (
    cins_turet, dikey_asansor, kaide_imzasi, turetim_beyani)

__all__ = ["HendeseAyari", "gecis_dizeyi", "karsilikli_haber",
           "gromov_delta", "mertebe_sec", "dikey_asansor",
           "hendese_teshisi", "hendese_beyani", "hendese_yukle",
           "hendese_sifirla", "kaide_imzasi", "hendese_metni"]


_SAYI: Dict[str, int] = {}


_NISPET: Dict[str, float] = {}


_ASKIN: Dict[str, int] = {}


def hendese_sifirla() -> None:
    _SAYI.clear()
    _SAYI.update({"çağrı": 0, "dag_mertebesi": -1, "eğrilik": 0,
                  "asansör_katı": 0, "kafes": 0, "boynuz": 0,
                  "dolu_boynuz": 0, "boynuz_sonra": 0,
                  "dolu_boynuz_sonra": 0, "tıkanma": 0, "dörtlü": 0,
                  "üçgen_ihlâli": 0, "yönlü_kenar": 0,
                  "simetrik_kenar": 0, "şelale_uzay": 0,
                  "şelale_kategori": 0, "şelale_operad": 0,
                  "opetop_mertebesi": 0, "serbestlik": 0,
                  "0-hücre": 0, "1-hücre": 0, "2-hücre": 0, "3-hücre": 0})
    _NISPET.clear()
    _NISPET.update({"δ": 0.0, "haber": 0.0, "sapma": 0.0, "denklik": 0.0,
                    "üçgen_nispeti": 0.0,
                    "𝒮_simetrik": 0.0, "𝒜_yönlü": 0.0, "Ω_yırtık": 0.0,
                    "koherans": 0.0, "koherans_evvel": 0.0,
                    "kapanma_nispeti": 0.0, "büzülme": 0.0,
                    "tayf_entropisi": 0.0})
    _ASKIN.clear()
    _ASKIN.update({"log": 0, "exp": 0, "eigh": 0})


hendese_sifirla()


@dataclass
class HendeseAyari:
    azami_alfabe: int = 256
    dortlu_ornek: int = 64
    tohum: int = 0


def _kucuk() -> float:
    return float(np.finfo(float).tiny)


def gecis_dizeyi(w: Sequence[int], n: int) -> np.ndarray:
    y = np.asarray(list(w), np.int64).reshape(-1) % int(n)
    if y.size < 2:
        return np.zeros((int(n), int(n)), float)
    T = np.zeros((int(n), int(n)), float)
    np.add.at(T, (y[:-1], y[1:]), 1.0)
    sat = T.sum(axis=1, keepdims=True)
    return T / np.maximum(sat, 1.0)


def karsilikli_haber(w: Sequence[int], n: int) -> Dict[str, float]:
    y = np.asarray(list(w), np.int64).reshape(-1) % int(n)
    if y.size < 2:
        return {"haber": 0.0, "şart_sapması": 0.0, "haber_haddi": 0.0}
    ortak = np.zeros((int(n), int(n)), float)
    np.add.at(ortak, (y[:-1], y[1:]), 1.0)
    top = max(float(ortak.sum()), 1.0)
    P = ortak / top
    Pi = P.sum(axis=1, keepdims=True)
    Pj = P.sum(axis=0, keepdims=True)
    kucuk = _kucuk()
    sec = P > 0.0
    payda = np.maximum(Pi * Pj, kucuk)
    haber = float(np.sum(P[sec] * np.log(P[sec] / payda[sec])))
    sart = P / np.maximum(Pi, kucuk)
    dolu = np.asarray(Pi).reshape(-1) > 0.0
    sapma = (float(np.mean(np.var(sart[dolu], axis=1)))
             if bool(dolu.any()) else 0.0)
    dolu_n = max(1, int(np.count_nonzero(dolu)))
    return {"haber": haber, "şart_sapması": sapma,
            "haber_haddi": float(np.log(float(dolu_n)))}


def _mesafe(w: Sequence[int], n: int) -> np.ndarray:
    T = gecis_dizeyi(w, n)
    S = T + T.T
    var = S > 0.0
    en_az = float(S[var].min()) if bool(var.any()) else 1.0
    ic = -np.log(np.where(var, S, en_az)) + np.where(var, 0.0, 1.0)
    np.fill_diagonal(ic, 0.0)
    D = ic.copy()
    for k in range(int(n)):
        D = np.minimum(D, D[:, k:k + 1] + D[k:k + 1, :])
    return D


def _dortlular(n: int, kac: int) -> np.ndarray:
    m = int(n)
    assert m >= 4, "Gromov dörtlüsü için en az dört harf lâzım"
    cikan: List[Tuple[int, int, int, int]] = []
    for i in range(m):
        for a in (1, 2, 3):
            j, k, l = (i + a) % m, (i + 2 * a) % m, (i + 3 * a) % m
            if len({i, j, k, l}) == 4:
                cikan.append((i, j, k, l))
            if len(cikan) >= int(kac):
                return np.asarray(cikan, np.int64)
    assert cikan, "determinist dörtlü taraması boş döndü"
    return np.asarray(cikan, np.int64)


def gromov_delta(w: Sequence[int], ayar: Optional[HendeseAyari] = None
                 ) -> Dict[str, float]:
    a = ayar or HendeseAyari()
    y = np.asarray(list(w), np.int64).reshape(-1)
    n = int(min(int(a.azami_alfabe), max(2, int(y.max()) + 1)))
    if n < 4:
        _NISPET["δ"] = 0.0
        _NISPET["üçgen_nispeti"] = 0.0
        _SAYI["üçgen_ihlâli"] = 0
        _SAYI["dörtlü"] = 0
        return {"δ": 0.0, "üçgen_ihlâli": 0.0, "dörtlü": 0, "alfabe": n}
    D = _mesafe(y, n)
    Q = _dortlular(n, int(a.dortlu_ornek))
    i, j, k, l = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]
    s1 = D[i, j] + D[k, l]
    s2 = D[i, k] + D[j, l]
    s3 = D[i, l] + D[j, k]
    en_buyuk = float(np.max(np.abs(s1 - np.maximum(s2, s3))))
    ihlal = int(np.count_nonzero(D[i, k] > D[i, j] + D[j, k]))
    nispet = float(ihlal) / float(Q.shape[0])
    _NISPET["δ"] = en_buyuk
    _NISPET["üçgen_nispeti"] = nispet
    _SAYI["üçgen_ihlâli"] = int(ihlal)
    _SAYI["dörtlü"] = int(Q.shape[0])
    return {"δ": en_buyuk, "üçgen_ihlâli": nispet,
            "dörtlü": int(Q.shape[0]), "alfabe": n}


def _dag_mertebesi(kenar: np.ndarray) -> int:
    E = np.asarray(kenar, bool)
    kuvvet = E.copy()
    for k in range(1, int(E.shape[0]) + 1):
        if not bool(kuvvet.any()):
            return k
        kuvvet = (kuvvet.astype(np.int64) @ E.astype(np.int64)) > 0
    return -1


def mertebe_sec(w: Sequence[int], ayar: Optional[HendeseAyari] = None
                ) -> Dict[str, Any]:
    a = ayar or HendeseAyari()
    y = np.asarray(list(w), np.int64).reshape(-1)
    n = int(min(int(a.azami_alfabe), max(2, int(y.max()) + 1)))
    hb = karsilikli_haber(y, n)
    T = gecis_dizeyi(y, n)
    m = cins_turet(y, n, T)
    selale = m["şelale"]
    gr = gromov_delta(y, a)
    egrilik = ("hiperbolik" if gr["δ"] > 0.0 and gr["üçgen_ihlâli"] < 0.5
               else ("düz" if gr["δ"] <= 0.0 else "pozitif"))
    dag = _dag_mertebesi(m["kenar"])
    _SAYI["çağrı"] += 1
    _SAYI["dag_mertebesi"] = int(dag)
    _SAYI["eğrilik"] = int({"düz": 0, "hiperbolik": 1,
                            "pozitif": 2}[egrilik])
    _SAYI["kafes"] = int(len(m["kafes"]))
    _SAYI["serbestlik"] = int(len(m["serbestlik"]))
    _SAYI["opetop_mertebesi"] = int(m["hücre_mertebesi"])
    _SAYI["boynuz"] = int(m["boynuz"])
    _SAYI["dolu_boynuz"] = int(m["dolu_boynuz"])
    _SAYI["boynuz_sonra"] = int(m["boynuz_sonra"])
    _SAYI["dolu_boynuz_sonra"] = int(m["dolu_boynuz_sonra"])
    _SAYI["tıkanma"] = int(selale["tıkanma"])
    _SAYI["şelale_uzay"] = int(selale["uzay"])
    _SAYI["şelale_kategori"] = int(selale["kategori"])
    _SAYI["şelale_operad"] = int(selale["operad"])
    _SAYI["yönlü_kenar"] = int(m["yönlü_kenar"])
    _SAYI["simetrik_kenar"] = int(m["simetrik_kenar"])
    for ad in ("0-hücre", "1-hücre", "2-hücre", "3-hücre"):
        _SAYI[ad] = int(m["hücre"][ad])
    _NISPET["haber"] = float(hb["haber"])
    _NISPET["sapma"] = float(np.linalg.norm(T - T.T))
    _NISPET["𝒮_simetrik"] = float(m["hodge"]["𝒮_simetrik"])
    _NISPET["𝒜_yönlü"] = float(m["hodge"]["𝒜_yönlü"])
    _NISPET["Ω_yırtık"] = float(m["hodge"]["Ω_yırtık"])
    _NISPET["tayf_entropisi"] = float(m["tayf_entropisi"])
    _NISPET["koherans_evvel"] = float(m["koherans_evvel"])
    _NISPET["koherans"] = float(m["koherans"])
    _NISPET["kapanma_nispeti"] = float(selale["kapanma_nispeti"])
    _ASKIN["log"] += 2
    for ad in m["serbestlik"]:
        _NISPET[str(ad)] = float(m["koordinat"][ad])
    cikti = dict(m)
    cikti.update({"haber": hb["haber"], "haber_haddi": hb["haber_haddi"],
                  "şart_sapması": hb["şart_sapması"],
                  "sapma": float(np.linalg.norm(T - T.T)),
                  "dag_mertebesi": int(dag),
                  "δ_Gromov": gr["δ"], "üçgen_ihlâli": gr["üçgen_ihlâli"],
                  "eğrilik": egrilik, "alfabe": n})
    return cikti


def hendese_teshisi(baglamlar: Sequence[Sequence[int]], lif: Sequence[int],
                    ayar: Optional[HendeseAyari] = None) -> Dict[str, Any]:
    assert baglamlar, "hendese teşhisi için bağlam BOŞ olamaz"
    duz: List[int] = []
    for b in baglamlar:
        duz.extend(int(x) for x in np.asarray(list(b), np.int64).reshape(-1)
                   if int(x) >= 0)
    assert duz, "bağlamların hepsi boş -- teşhis edilecek dizi yok"
    m = mertebe_sec(duz, ayar)
    m["asansör"] = dikey_asansor(m, lif)
    _SAYI["asansör_katı"] = int(m["asansör"]["kat"])
    _NISPET["büzülme"] = float(m["asansör"]["büzülme"])
    m["basamak"] = len(duz)
    m["türetim_beyanı"] = turetim_beyani()
    return m


def hendese_beyani() -> Dict[str, Any]:
    b: Dict[str, Any] = {k: int(v) for k, v in _SAYI.items()}
    b.update({"aşkın_%s" % k: int(v) for k, v in _ASKIN.items()})
    b["aşkın_toplam"] = int(sum(_ASKIN.values()))
    b.update({k: float(v) for k, v in _NISPET.items()})
    b.update({"türetim_%s" % k: v for k, v in turetim_beyani().items()})
    return b


def hendese_yukle(d: Dict[str, Any]) -> None:
    for k, v in dict(d).items():
        a = str(k)
        if a.startswith("türetim_") or a.startswith("aşkın_"):
            continue
        if a in _SAYI:
            _SAYI[a] = int(v)
        elif a in _NISPET:
            _NISPET[a] = float(v)


def _serbestlik_satirlari(b: Dict[str, Any]) -> List[str]:
    kat: Dict[int, List[str]] = {}
    for k, v in b.items():
        a = str(k)
        for kok in ("morfizm_", "arite_", "yön_"):
            if a.startswith(kok) and a[len(kok):].isdigit():
                j = int(a[len(kok):])
                kat.setdefault(j, []).append("%s %.4f" % (a, float(v)))
    return ["      " + " · ".join(sorted(kat[j])) for j in sorted(kat)]


def hendese_metni(teshis: Optional[Dict[str, Any]] = None,
                  beyan: Optional[Dict[str, Any]] = None) -> str:
    b = dict(beyan or hendese_beyani())
    if not int(b.get("çağrı", 0)):
        return ("  D2 HENDESE: HİÇ KOŞMADI -- türetim yapılmadı "
                "(ferman 2-Ā-B)")
    s = ["  D2 HENDESE -- CİNS LİSTELENMEZ, TÜRETİLİR (ferman 2-Ā-B/C)",
         "    çağrı %d   opetop mertebesi %d   serbestlik %d (ÖLÇÜLDÜ)"
         % (int(b["çağrı"]), int(b["opetop_mertebesi"]),
            int(b["serbestlik"])),
         "    hücre: 0-h %d · 1-h %d · 2-h %d · 3-h %d"
         % (int(b["0-hücre"]), int(b["1-hücre"]), int(b["2-hücre"]),
            int(b["3-hücre"])),
         "    SERBESTLİK (yapıştırma ağacından, seviye seviye, [0,1]):"]
    s.extend(_serbestlik_satirlari(b))
    s.extend([
        "      koherans %.4f" % float(b.get("koherans", 0.0)),
        "    Hodge: 𝒮 %.4f ⊕ 𝒜 %.4f ⊕ Ω_yırtık %.4f"
        % (b["𝒮_simetrik"], b["𝒜_yönlü"], b["Ω_yırtık"]),
        "    kenar: yönlü %d · simetrik %d"
        % (int(b["yönlü_kenar"]), int(b["simetrik_kenar"])),
        "    boynuz şelaleden EVVEL %d (dolu %d) · SONRA %d (dolu %d)"
        % (int(b["boynuz"]), int(b["dolu_boynuz"]),
           int(b["boynuz_sonra"]), int(b["dolu_boynuz_sonra"])),
        "    ŞELALE -- ÇEKİRDEĞİN KAN TERKİBİ (HKomp) İLE:",
        "      uzay %d · kategori %d · operad %d · TIKANMA %d"
        " (kapanma %.4f)"
        % (int(b["şelale_uzay"]), int(b["şelale_kategori"]),
           int(b["şelale_operad"]), int(b["tıkanma"]),
           b["kapanma_nispeti"]),
        "      Kan doldurması çekirdekte koştu: %d boynuz"
        " (denetim %d · terkip tuttu %d/düştü %d · ters tuttu %d/düştü %d)"
        % (int(b.get("türetim_kan_doldurma", 0)),
           int(b.get("türetim_kan_denetimi", 0)),
           int(b.get("türetim_kan_terkip_tuttu", 0)),
           int(b.get("türetim_kan_terkip_düştü", 0)),
           int(b.get("türetim_kan_ters_tuttu", 0)),
           int(b.get("türetim_kan_ters_düştü", 0))),
        "      operad dolgusu (ikili terkip DEĞİL): %d"
        % int(b.get("türetim_operad_dolgu", 0)),
        "      koherans şelaleden evvel %.4f, sonra %.4f"
        % (b["koherans_evvel"], b.get("koherans", 0.0)),
        "    KAFES ÇEKİRDEĞİN TİP DENETÇİSİNDEN ÜRETİLİR:",
        "      denenen %d · tutan %d · düşen %d → kafes %d düğüm"
        % (int(b.get("türetim_denenen", 0)),
           int(b.get("türetim_tutan", 0)),
           int(b.get("türetim_düşen", 0)), int(b["kafes"])),
        "      YÖNLÜ KANAT (ferman 113-A/B): teşkil eden %d · düşen %d"
        % (int(b.get("türetim_yönlü_tutan", 0)),
           int(b.get("türetim_yönlü_düşen", 0))),
        "      tersi KURULDU %d (⇒ grupoid) · REDDEDİLDİ %d (yönlü kanat);"
        " ad \"kategori\" ancak n ≥ 1'de yazılır (ferman 113-B)"
        % (int(b.get("türetim_ters_kuruldu", 0)),
           int(b.get("türetim_ters_reddedildi", 0))),
        "      kafes evren tavanı U%d"
        % int(b.get("türetim_evren_tavanı", 0)),
        "      yönlü hom teşkil kuralı çekirdekte koştu: %d kere"
        % int(b.get("türetim_yönlü_teşkil", 0)),
        "    tayf entropisi %.4f nat   bağımsızlık artığı %.4e"
        % (b["tayf_entropisi"],
           b.get("türetim_bağımsızlık_artığı", 0.0)),
        "    Ω: tümleyen bulundu %d · bulunamadı %d"
        % (int(b.get("türetim_tümleyen_bulundu", 0)),
           int(b.get("türetim_tümleyen_yok", 0))),
        "    aşkın çağrı: log %d · exp %d · eigh %d (toplam %d)"
        % (int(b.get("aşkın_log", 0)), int(b.get("aşkın_exp", 0)),
           int(b.get("aşkın_eigh", 0)), int(b.get("aşkın_toplam", 0))),
        "    dikey asansör: büzülme %.4f → parite lifi %d"
        % (b["büzülme"], int(b["asansör_katı"]))])
    if teshis:
        s.append("    KAFES DÜĞÜMLERİ (ad · ρ · kısıtlama):")
        for dug, ro in zip(teshis["kafes"], teshis["tayf"]):
            s.append("      %-22s ρ %.4f   kısıtlama %d   yönlü %s"
                     % (dug["ad"], float(ro), int(dug["kısıtlama"]),
                        "evet" if dug.get("yönlü") else "hayır"))
        om = teshis["Ω_cebiri"]
        s.append("    Ω CEBİRİ: %s   (tümleyen %s · unsur %s)"
                 % (om["cebir"], om.get("tümleyen"), om.get("unsur")))
    return "\n".join(s)
